"""
用户相关路由
处理用户注册、登录、信息管理等
"""
from flask import Blueprint, request, session
from app import db
from app.models.user import User
from app.models.merchant import Merchant
from app.models.comment import Comment
from app.models.favorite import Favorite
from app.utils.response import success, error
from app.utils.file_upload import save_upload_file

bp = Blueprint('user', __name__, url_prefix='/api/user')


def _add_merchant_status(data: dict, user_id: int):
    """在用户信息中附加入驻申请状态（merchant_status）"""
    merchant = Merchant.query.filter_by(user_id=user_id).first()
    data['merchant_status'] = merchant.status if merchant else None


@bp.route('/register', methods=['POST'])
def register():
    """
    用户注册（支持普通用户和商家）
    
    请求参数:
        username: 用户名（必填）
        password: 密码（必填）
        email: 邮箱（可选）
        register_type: 注册类型 user/merchant（可选，默认 user）
        shop_name: 店铺名称（register_type=merchant 时必填）
        shop_description: 店铺描述（可选）
        contact_phone: 联系电话（可选）
        address: 店铺地址（可选）
    
    返回:
        注册成功的用户信息
    """
    data = request.get_json()
    
    # 验证必填字段
    if not data or not data.get('username') or not data.get('password'):
        return error('用户名和密码不能为空')
    
    username = data.get('username').strip()
    password = data.get('password')
    email = data.get('email', '').strip()
    register_type = (data.get('register_type') or 'user').strip().lower()
    
    # 验证用户名长度
    if len(username) < 3 or len(username) > 50:
        return error('用户名长度必须在3-50个字符之间')
    
    # 验证密码长度
    if len(password) < 6:
        return error('密码长度不能少于6个字符')
    
    # 商家注册：仅创建用户，入驻申请在商家中心单独提交
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        return error('用户名已存在')
    
    # 检查邮箱是否已存在
    if email and User.query.filter_by(email=email).first():
        return error('邮箱已被注册')
    
    # 创建新用户（商家注册时 role 设为 merchant）
    new_user = User(
        username=username,
        password=password,  # 明文存储（按需求）
        email=email if email else None,
        role='merchant' if register_type == 'merchant' else 'user'
    )
    
    try:
        db.session.add(new_user)
        db.session.commit()
        msg = '注册成功，请登录' if register_type == 'user' else '注册成功，请登录后进入商家中心提交入驻申请'
        return success(new_user.to_dict(), msg)
    except Exception as e:
        db.session.rollback()
        return error(f'注册失败: {str(e)}')


@bp.route('/login', methods=['POST'])
def login():
    """
    用户登录
    
    请求参数:
        username: 用户名（必填）
        password: 密码（必填）
    
    返回:
        登录成功的用户信息
    """
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data or not data.get('username') or not data.get('password'):
            return error('用户名和密码不能为空')
        
        username = data.get('username').strip()
        password = data.get('password')
        
        # 查询用户
        user = User.query.filter_by(username=username).first()
        
        # 验证用户名和密码
        if not user or user.password != password:
            return error('用户名或密码错误')
        
        # 确保 role 为字符串（兼容 SQLAlchemy Enum 序列化）
        role_str = str(user.role) if user.role else 'user'
        
        # 保存登录状态到session
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = role_str
        
        data = user.to_dict()
        _add_merchant_status(data, user.id)
        return success(data, '登录成功')
    except Exception as e:
        import traceback
        traceback.print_exc()
        return error(f'登录失败: {str(e)}', code=500)


@bp.route('/logout', methods=['POST'])
def logout():
    """
    退出登录
    
    返回:
        退出成功信息
    """
    # 清除session
    session.clear()
    
    return success(message='退出登录成功')


@bp.route('/info', methods=['GET'])
def get_user_info():
    """
    获取当前登录用户信息
    
    返回:
        用户信息
    """
    # 检查登录状态
    user_id = session.get('user_id')
    if not user_id:
        return error('未登录', code=401)
    
    # 查询用户
    user = User.query.get(user_id)
    if not user:
        return error('用户不存在', code=404)
    
    data = user.to_dict()
    _add_merchant_status(data, user_id)
    return success(data)


@bp.route('/update', methods=['PUT'])
def update_user():
    """
    更新用户信息
    
    请求参数:
        email: 邮箱（可选）
        avatar: 头像文件（可选）
    
    返回:
        更新后的用户信息
    """
    # 检查登录状态
    user_id = session.get('user_id')
    if not user_id:
        return error('未登录', code=401)
    
    # 查询用户
    user = User.query.get(user_id)
    if not user:
        return error('用户不存在', code=404)
    
    # 处理JSON数据
    if request.is_json:
        data = request.get_json()
        
        # 更新邮箱
        if 'email' in data:
            email = data.get('email', '').strip()
            if email:
                # 检查邮箱是否被其他用户使用
                existing_user = User.query.filter_by(email=email).first()
                if existing_user and existing_user.id != user_id:
                    return error('邮箱已被其他用户使用')
                user.email = email
        
        # 更新头像路径（通过上传接口上传后传入路径）
        if 'avatar' in data and isinstance(data.get('avatar'), str):
            user.avatar = data.get('avatar', '').strip() or None
    
    # 处理文件上传（头像，兼容旧方式）
    if 'avatar' in request.files:
        avatar_file = request.files['avatar']
        if avatar_file:
            # 保存头像文件
            avatar_path = save_upload_file(avatar_file, 'avatar')
            if avatar_path:
                user.avatar = avatar_path
            else:
                return error('头像上传失败，请检查文件格式')
    
    try:
        db.session.commit()
        return success(user.to_dict(), '更新成功')
    except Exception as e:
        db.session.rollback()
        return error(f'更新失败: {str(e)}')


@bp.route('/profile', methods=['GET', 'PUT'])
def profile():
    """
    GET: 获取用户详细资料（包含统计信息）
    PUT: 更新用户资料（邮箱、头像路径等）
    """
    # 检查登录状态
    user_id = session.get('user_id')
    if not user_id:
        return error('未登录', code=401)
    
    # 查询用户
    user = User.query.get(user_id)
    if not user:
        return error('用户不存在', code=404)
    
    if request.method == 'PUT':
        # 更新资料
        data = request.get_json() or {}
        if 'email' in data:
            email = data.get('email', '').strip()
            if email:
                existing = User.query.filter_by(email=email).first()
                if existing and existing.id != user_id:
                    return error('邮箱已被其他用户使用')
                user.email = email
        if 'avatar' in data and isinstance(data.get('avatar'), str):
            user.avatar = data.get('avatar', '').strip() or None
        try:
            db.session.commit()
            return success(user.to_dict(), '更新成功')
        except Exception as e:
            db.session.rollback()
            return error(f'更新失败: {str(e)}')
    
    # GET: 获取资料
    comment_count = Comment.query.filter_by(user_id=user_id).count()
    favorite_count = Favorite.query.filter_by(user_id=user_id).count()
    profile_data = user.to_dict()
    profile_data['statistics'] = {
        'comment_count': comment_count,
        'favorite_count': favorite_count
    }
    return success(profile_data)


@bp.route('/test', methods=['GET'])
def test():
    """测试接口"""
    return {'message': '用户模块正常'}
