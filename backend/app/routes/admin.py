"""
管理后台相关路由
处理后台管理功能
"""
from flask import Blueprint, request, session
from sqlalchemy import func
from app import db
from app.models.user import User
from app.models.food import Food
from app.models.food_category import FoodCategory
from app.models.comment import Comment
from app.models.favorite import Favorite
from app.models.banner import Banner
from app.models.announcement import Announcement
from app.models.merchant import Merchant
from app.utils.response import success, error, paginate_response
from app.utils.file_upload import save_upload_file, delete_upload_file

bp = Blueprint('admin', __name__, url_prefix='/api/admin')


def check_admin():
    """
    检查管理员权限
    
    返回:
        tuple: (是否是管理员, 错误响应)
    """
    user_id = session.get('user_id')
    if not user_id:
        return False, error('请先登录', code=401)
    
    role = session.get('role')
    if role != 'admin':
        return False, error('无权访问', code=403)
    
    return True, None


# ==================== 用户管理 ====================

@bp.route('/users', methods=['GET'])
def get_users():
    """
    获取用户列表
    
    查询参数:
        keyword: 搜索关键词（搜索用户名和邮箱）
        role: 角色筛选（user/admin）
        page: 页码（默认1）
        per_page: 每页数量（默认20）
    
    返回:
        用户列表
    """
    is_admin, err_response = check_admin()
    if not is_admin:
        return err_response
    
    # 获取查询参数
    keyword = request.args.get('keyword', '').strip()
    role = request.args.get('role', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # 构建查询
    query = User.query
    
    # 关键词搜索
    if keyword:
        search_pattern = f'%{keyword}%'
        query = query.filter(
            db.or_(
                User.username.like(search_pattern),
                User.email.like(search_pattern)
            )
        )
    
    # 角色筛选（user/admin/merchant，merchant 为已通过商家）
    if role:
        query = query.filter_by(role=role)
    
    # 按创建时间倒序
    query = query.order_by(User.created_at.desc())
    
    # 分页查询
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # 转换为字典
    users = [user.to_dict() for user in pagination.items]
    
    # 返回分页数据
    return success(paginate_response(
        items=users,
        total=pagination.total,
        page=page,
        per_page=per_page
    ))


@bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """
    更新用户信息
    
    路径参数:
        user_id: 用户ID
    
    请求参数:
        email: 邮箱
        role: 角色
    
    返回:
        更新后的用户信息
    """
    is_admin, err_response = check_admin()
    if not is_admin:
        return err_response
    
    # 查询用户
    user = User.query.get(user_id)
    if not user:
        return error('用户不存在', code=404)
    
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
    
    # 角色不可编辑，忽略 role 参数
    
    try:
        db.session.commit()
        return success(user.to_dict(), '更新成功')
    except Exception as e:
        db.session.rollback()
        return error(f'更新失败: {str(e)}')


@bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    删除用户（需要检查关联数据）
    
    路径参数:
        user_id: 用户ID
    
    返回:
        删除成功信息或友好提示
    """
    is_admin, err_response = check_admin()
    if not is_admin:
        return err_response
    
    # 查询用户
    user = User.query.get(user_id)
    if not user:
        return error('用户不存在', code=404)
    
    # 检查关联数据
    comment_count = Comment.query.filter_by(user_id=user_id).count()
    favorite_count = Favorite.query.filter_by(user_id=user_id).count()
    
    if comment_count > 0 or favorite_count > 0:
        return error(
            f'该用户存在{comment_count}条评论和{favorite_count}个收藏记录，无法直接删除。'
            f'请先删除相关数据或联系技术人员处理。',
            code=400
        )
    
    try:
        db.session.delete(user)
        db.session.commit()
        return success(message='用户删除成功')
    except Exception as e:
        db.session.rollback()
        return error(f'删除失败: {str(e)}')


# ==================== 美食管理 ====================

@bp.route('/foods', methods=['GET'])
def get_admin_foods():
    """
    获取美食列表（管理后台）
    
    查询参数:
        keyword: 搜索关键词
        category_id: 分类ID
        region: 地域
        page: 页码
        per_page: 每页数量
    
    返回:
        美食列表
    """
    is_admin, err_response = check_admin()
    if not is_admin:
        return err_response
    
    # 获取查询参数
    keyword = request.args.get('keyword', '').strip()
    category_id = request.args.get('category_id', type=int)
    region = request.args.get('region', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # 构建查询
    query = Food.query
    
    # 关键词搜索
    if keyword:
        search_pattern = f'%{keyword}%'
        query = query.filter(Food.name.like(search_pattern))
    
    # 分类筛选
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    # 地域筛选
    if region:
        query = query.filter_by(region=region)
    
    # 按创建时间倒序
    query = query.order_by(Food.created_at.desc())
    
    # 分页查询
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # 转换为字典
    foods = [food.to_dict(include_stats=True) for food in pagination.items]
    
    # 返回分页数据
    return success(paginate_response(
        items=foods,
        total=pagination.total,
        page=page,
        per_page=per_page
    ))


@bp.route('/foods', methods=['POST'])
def create_food():
    """
    添加美食
    
    请求参数:
        name: 美食名称（必填）
        region: 地域（必填）
        category_id: 分类ID（必填）
        description: 描述
        price_range: 价格区间
        taste_tags: 口味标签（数组或JSON字符串）
        image: 图片路径
    
    返回:
        新创建的美食信息
    """
    is_admin, err_response = check_admin()
    if not is_admin:
        return err_response
    
    # 支持JSON和FormData两种格式
    if request.is_json:
        data = request.get_json()
        name = data.get('name', '').strip()
        region = data.get('region', '').strip()
        category_id = data.get('category_id')
        description = data.get('description', '').strip()
        price_range = data.get('price_range', '').strip()
        taste_tags = data.get('taste_tags', [])
        image = data.get('image', '').strip()
    else:
        name = request.form.get('name', '').strip()
        region = request.form.get('region', '').strip()
        category_id = request.form.get('category_id', type=int)
        description = request.form.get('description', '').strip()
        price_range = request.form.get('price_range', '').strip()
        taste_tags = request.form.get('taste_tags', '').strip()
        image = request.form.get('image', '').strip()
        # 处理文件上传
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file:
                image = save_upload_file(image_file, 'food')
    
    # 验证必填字段
    if not name or not region or not category_id:
        return error('美食名称、地域和分类不能为空')
    
    # 检查分类是否存在
    category = FoodCategory.query.get(category_id)
    if not category:
        return error('分类不存在', code=404)
    
    # 处理taste_tags（支持数组或字符串）
    import json
    if isinstance(taste_tags, list):
        taste_tags_str = json.dumps(taste_tags, ensure_ascii=False)
    else:
        taste_tags_str = taste_tags if taste_tags else None
    
    # 创建美食
    new_food = Food(
        name=name,
        region=region,
        category_id=category_id,
        description=description if description else None,
        price_range=price_range if price_range else None,
        taste_tags=taste_tags_str,
        image=image if image else None
    )
    
    try:
        db.session.add(new_food)
        db.session.commit()
        return success(new_food.to_dict(), '美食添加成功')
    except Exception as e:
        db.session.rollback()
        return error(f'添加失败: {str(e)}')


@bp.route('/foods/<int:food_id>', methods=['PUT'])
def update_food(food_id):
    """
    更新美食信息
    
    路径参数:
        food_id: 美食ID
    
    请求参数:
        同创建接口
    
    返回:
        更新后的美食信息
    """
    is_admin, err_response = check_admin()
    if not is_admin:
        return err_response
    
    # 查询美食
    food = Food.query.get(food_id)
    if not food:
        return error('美食不存在', code=404)
    
    # 支持JSON和FormData两种格式
    import json
    if request.is_json:
        data = request.get_json()
        name = data.get('name', '').strip()
        region = data.get('region', '').strip()
        category_id = data.get('category_id')
        description = data.get('description', '').strip()
        price_range = data.get('price_range', '').strip()
        taste_tags = data.get('taste_tags')
        image = data.get('image', '').strip()
    else:
        name = request.form.get('name', '').strip()
        region = request.form.get('region', '').strip()
        category_id = request.form.get('category_id', type=int)
        description = request.form.get('description', '').strip()
        price_range = request.form.get('price_range', '').strip()
        taste_tags = request.form.get('taste_tags', '').strip()
        image = request.form.get('image', '').strip()
        # 处理文件上传
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file:
                # 删除旧图片
                if food.image:
                    delete_upload_file(food.image)
                image = save_upload_file(image_file, 'food')
    
    # 更新字段
    if name:
        food.name = name
    if region:
        food.region = region
    if category_id:
        # 检查分类是否存在
        category = FoodCategory.query.get(category_id)
        if not category:
            return error('分类不存在', code=404)
        food.category_id = category_id
    if description is not None:
        food.description = description if description else None
    if price_range is not None:
        food.price_range = price_range if price_range else None
    if taste_tags is not None:
        # 处理taste_tags（支持数组或字符串）
        if isinstance(taste_tags, list):
            food.taste_tags = json.dumps(taste_tags, ensure_ascii=False)
        else:
            food.taste_tags = taste_tags if taste_tags else None
    if image:
        food.image = image
    
    try:
        db.session.commit()
        return success(food.to_dict(), '更新成功')
    except Exception as e:
        db.session.rollback()
        return error(f'更新失败: {str(e)}')


@bp.route('/foods/<int:food_id>', methods=['DELETE'])
def delete_food(food_id):
    """
    删除美食（需要检查关联数据）
    
    路径参数:
        food_id: 美食ID
    
    返回:
        删除成功信息或友好提示
    """
    is_admin, err_response = check_admin()
    if not is_admin:
        return err_response
    
    # 查询美食
    food = Food.query.get(food_id)
    if not food:
        return error('美食不存在', code=404)
    
    # 检查关联数据
    comment_count = Comment.query.filter_by(food_id=food_id).count()
    favorite_count = Favorite.query.filter_by(food_id=food_id).count()
    
    if comment_count > 0 or favorite_count > 0:
        return error(
            f'该美食存在{comment_count}条评论和{favorite_count}个收藏记录，无法直接删除。'
            f'请先删除相关数据或联系技术人员处理。',
            code=400
        )
    
    # 删除图片文件
    if food.image:
        delete_upload_file(food.image)
    
    try:
        db.session.delete(food)
        db.session.commit()
        return success(message='美食删除成功')
    except Exception as e:
        db.session.rollback()
        return error(f'删除失败: {str(e)}')


# ==================== 美食分类管理 ====================

@bp.route('/food-categories', methods=['GET'])
def get_admin_categories():
    """
    获取分类列表（管理后台）
    
    返回:
        所有分类列表
    """
    is_admin, err_response = check_admin()
    if not is_admin:
        return err_response
    
    # 查询所有分类
    categories = FoodCategory.query.order_by(FoodCategory.sort_order.asc()).all()
    
    # 转换为字典
    categories_data = [category.to_dict() for category in categories]
    
    return success(categories_data)


@bp.route('/food-categories', methods=['POST'])
def create_category():
    """
    添加分类
    
    请求参数:
        name: 分类名称（必填）
        description: 分类描述
        sort_order: 排序
        status: 状态
        icon: 图标路径
    
    返回:
        新创建的分类信息
    """
    is_admin, err_response = check_admin()
    if not is_admin:
        return err_response
    
    # 支持JSON和FormData两种格式
    if request.is_json:
        data = request.get_json()
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        sort_order = data.get('sort_order', 0)
        status = data.get('status', 1)
        icon = data.get('icon', '').strip()
    else:
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        sort_order = request.form.get('sort_order', 0, type=int)
        status = request.form.get('status', 1, type=int)
        icon = request.form.get('icon', '').strip()
        # 处理文件上传
        if 'icon' in request.files:
            icon_file = request.files['icon']
            if icon_file:
                icon = save_upload_file(icon_file, 'category')
    
    # 验证必填字段
    if not name:
        return error('分类名称不能为空')
    
    # 检查名称是否已存在
    existing_category = FoodCategory.query.filter_by(name=name).first()
    if existing_category:
        return error('分类名称已存在')
    
    # 创建分类
    new_category = FoodCategory(
        name=name,
        description=description if description else None,
        sort_order=sort_order,
        status=status,
        icon=icon if icon else None
    )
    
    try:
        db.session.add(new_category)
        db.session.commit()
        return success(new_category.to_dict(), '分类添加成功')
    except Exception as e:
        db.session.rollback()
        return error(f'添加失败: {str(e)}')


@bp.route('/food-categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    """
    更新分类信息
    
    路径参数:
        category_id: 分类ID
    
    请求参数:
        同创建接口
    
    返回:
        更新后的分类信息
    """
    is_admin, err_response = check_admin()
    if not is_admin:
        return err_response
    
    # 查询分类
    category = FoodCategory.query.get(category_id)
    if not category:
        return error('分类不存在', code=404)
    
    # 支持JSON和FormData两种格式
    if request.is_json:
        data = request.get_json()
        name = data.get('name', '').strip()
        description = data.get('description')
        sort_order = data.get('sort_order')
        status = data.get('status')
        icon = data.get('icon', '').strip()
    else:
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        sort_order = request.form.get('sort_order', type=int)
        status = request.form.get('status', type=int)
        icon = request.form.get('icon', '').strip()
        # 处理文件上传
        if 'icon' in request.files:
            icon_file = request.files['icon']
            if icon_file:
                # 删除旧图标
                if category.icon:
                    delete_upload_file(category.icon)
                icon = save_upload_file(icon_file, 'category')
    
    # 更新字段
    if name and name != category.name:
        existing_category = FoodCategory.query.filter_by(name=name).first()
        if existing_category:
            return error('分类名称已存在')
        category.name = name
    
    if description is not None:
        category.description = description if description else None
    if sort_order is not None:
        category.sort_order = sort_order
    if status is not None:
        category.status = status
    if icon:
        category.icon = icon
    
    try:
        db.session.commit()
        return success(category.to_dict(), '更新成功')
    except Exception as e:
        db.session.rollback()
        return error(f'更新失败: {str(e)}')


@bp.route('/food-categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """
    删除分类（需要检查关联美食）
    
    路径参数:
        category_id: 分类ID
    
    返回:
        删除成功信息或友好提示
    """
    is_admin, err_response = check_admin()
    if not is_admin:
        return err_response
    
    # 查询分类
    category = FoodCategory.query.get(category_id)
    if not category:
        return error('分类不存在', code=404)
    
    # 检查关联美食
    food_count = Food.query.filter_by(category_id=category_id).count()
    
    if food_count > 0:
        return error(
            f'该分类下存在{food_count}个美食，无法直接删除。'
            f'请先将这些美食移至其他分类或删除后再操作。',
            code=400
        )
    
    # 删除图标文件
    if category.icon:
        delete_upload_file(category.icon)
    
    try:
        db.session.delete(category)
        db.session.commit()
        return success(message='分类删除成功')
    except Exception as e:
        db.session.rollback()
        return error(f'删除失败: {str(e)}')


@bp.route('/test', methods=['GET'])
def test():
    """测试接口"""
    return {'message': '管理后台模块正常'}



# ==================== 轮播图管理 ====================

@bp.route('/banners', methods=['GET'])
def get_admin_banners():
    """
    获取轮播图列表（管理后台）
    
    返回:
        所有轮播图列表
    """
    is_admin, err_response = check_admin()
    if not is_admin:
        return err_response
    
    # 查询所有轮播图
    banners = Banner.query.order_by(Banner.sort_order.asc()).all()
    
    # 转换为字典
    banners_data = [banner.to_dict() for banner in banners]
    
    return success(banners_data)


@bp.route('/banners', methods=['POST'])
def create_banner():
    """
    添加轮播图
    
    请求参数:
        title: 标题（必填）
        link_url: 链接地址
        sort_order: 排序
        status: 状态
        image: 图片文件或图片路径
    
    返回:
        新创建的轮播图信息
    """
    is_admin, err_response = check_admin()
    if not is_admin:
        return err_response
    
    # 支持JSON和FormData两种格式
    if request.is_json:
        data = request.get_json()
        title = data.get('title', '').strip()
        link_url = data.get('link_url', '').strip()
        sort_order = data.get('sort_order', 0)
        status = data.get('status', 1)
        image = data.get('image', '').strip()
    else:
        title = request.form.get('title', '').strip()
        link_url = request.form.get('link_url', '').strip()
        sort_order = request.form.get('sort_order', 0, type=int)
        status = request.form.get('status', 1, type=int)
        image = ''
        # 处理文件上传
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file:
                image = save_upload_file(image_file, 'banner')
    
    # 验证必填字段
    if not title:
        return error('标题不能为空')
    
    # 验证图片（必填）
    if not image:
        return error('请上传轮播图图片')
    
    # 创建轮播图
    new_banner = Banner(
        title=title,
        image=image,
        link_url=link_url if link_url else None,
        sort_order=sort_order,
        status=status
    )
    
    try:
        db.session.add(new_banner)
        db.session.commit()
        return success(new_banner.to_dict(), '轮播图添加成功')
    except Exception as e:
        db.session.rollback()
        return error(f'添加失败: {str(e)}')


@bp.route('/banners/<int:banner_id>', methods=['PUT'])
def update_banner(banner_id):
    """
    更新轮播图信息
    
    路径参数:
        banner_id: 轮播图ID
    
    请求参数:
        同创建接口
    
    返回:
        更新后的轮播图信息
    """
    is_admin, err_response = check_admin()
    if not is_admin:
        return err_response
    
    # 查询轮播图
    banner = Banner.query.get(banner_id)
    if not banner:
        return error('轮播图不存在', code=404)
    
    # 支持JSON和FormData两种格式
    if request.is_json:
        data = request.get_json()
        title = data.get('title', '').strip()
        link_url = data.get('link_url')
        sort_order = data.get('sort_order')
        status = data.get('status')
        image = data.get('image', '').strip()
    else:
        title = request.form.get('title', '').strip()
        link_url = request.form.get('link_url', '').strip()
        sort_order = request.form.get('sort_order', type=int)
        status = request.form.get('status', type=int)
        image = ''
        # 处理文件上传
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file:
                # 删除旧图片
                if banner.image:
                    delete_upload_file(banner.image)
                image = save_upload_file(image_file, 'banner')
    
    # 更新字段
    if title:
        banner.title = title
    if link_url is not None:
        banner.link_url = link_url if link_url else None
    if sort_order is not None:
        banner.sort_order = sort_order
    if status is not None:
        banner.status = status
    if image:
        banner.image = image
    
    try:
        db.session.commit()
        return success(banner.to_dict(), '更新成功')
    except Exception as e:
        db.session.rollback()
        return error(f'更新失败: {str(e)}')


@bp.route('/banners/<int:banner_id>', methods=['DELETE'])
def delete_banner(banner_id):
    """
    删除轮播图
    
    路径参数:
        banner_id: 轮播图ID
    
    返回:
        删除成功信息
    """
    is_admin, err_response = check_admin()
    if not is_admin:
        return err_response
    
    # 查询轮播图
    banner = Banner.query.get(banner_id)
    if not banner:
        return error('轮播图不存在', code=404)
    
    # 删除图片文件
    if banner.image:
        delete_upload_file(banner.image)
    
    try:
        db.session.delete(banner)
        db.session.commit()
        return success(message='轮播图删除成功')
    except Exception as e:
        db.session.rollback()
        return error(f'删除失败: {str(e)}')


# ==================== 公告管理 ====================

@bp.route('/announcements', methods=['GET'])
def get_admin_announcements():
    """
    获取公告列表（管理后台）
    
    查询参数:
        keyword: 搜索关键词
        type: 公告类型
        status: 状态
        page: 页码
        per_page: 每页数量
    
    返回:
        公告列表
    """
    is_admin, err_response = check_admin()
    if not is_admin:
        return err_response
    
    # 获取查询参数
    keyword = request.args.get('keyword', '').strip()
    announcement_type = request.args.get('type', '').strip()
    status = request.args.get('status', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # 构建查询
    query = Announcement.query
    
    # 关键词搜索
    if keyword:
        search_pattern = f'%{keyword}%'
        query = query.filter(Announcement.title.like(search_pattern))
    
    # 类型筛选
    if announcement_type:
        query = query.filter_by(type=announcement_type)
    
    # 状态筛选
    if status is not None:
        query = query.filter_by(status=status)
    
    # 按优先级和创建时间排序
    query = query.order_by(Announcement.priority.desc(), Announcement.created_at.desc())
    
    # 分页查询
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # 转换为字典
    announcements = [announcement.to_dict() for announcement in pagination.items]
    
    # 返回分页数据
    return success(paginate_response(
        items=announcements,
        total=pagination.total,
        page=page,
        per_page=per_page
    ))


@bp.route('/announcements', methods=['POST'])
def create_announcement():
    """
    添加公告
    
    请求参数:
        title: 标题（必填）
        content: 内容（必填）
        type: 类型（notice/event/system）
        priority: 优先级（1-5）
        status: 状态
        start_time: 开始时间
        end_time: 结束时间
        image: 图片文件或图片路径
    
    返回:
        新创建的公告信息
    """
    is_admin, err_response = check_admin()
    if not is_admin:
        return err_response
    
    # 获取当前用户ID
    user_id = session.get('user_id')
    
    # 支持JSON和FormData两种格式
    if request.is_json:
        data = request.get_json()
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        announcement_type = data.get('type', 'notice')
        priority = data.get('priority', 3)
        status = data.get('status', 1)
        start_time = data.get('start_time', '').strip()
        end_time = data.get('end_time', '').strip()
        image = data.get('image', '').strip()
    else:
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        announcement_type = request.form.get('type', 'notice')
        priority = request.form.get('priority', 3, type=int)
        status = request.form.get('status', 1, type=int)
        start_time = request.form.get('start_time', '').strip()
        end_time = request.form.get('end_time', '').strip()
        image = ''
        # 处理文件上传
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file:
                image = save_upload_file(image_file, 'announcement')
    
    # 验证必填字段
    if not title or not content:
        return error('标题和内容不能为空')
    
    # 创建公告
    new_announcement = Announcement(
        title=title,
        content=content,
        type=announcement_type,
        priority=priority,
        status=status,
        start_time=start_time if start_time else None,
        end_time=end_time if end_time else None,
        image=image if image else None,
        created_by=user_id
    )
    
    try:
        db.session.add(new_announcement)
        db.session.commit()
        return success(new_announcement.to_dict(), '公告添加成功')
    except Exception as e:
        db.session.rollback()
        return error(f'添加失败: {str(e)}')


@bp.route('/announcements/<int:announcement_id>', methods=['PUT'])
def update_announcement(announcement_id):
    """
    更新公告信息
    
    路径参数:
        announcement_id: 公告ID
    
    请求参数:
        同创建接口
    
    返回:
        更新后的公告信息
    """
    is_admin, err_response = check_admin()
    if not is_admin:
        return err_response
    
    # 查询公告
    announcement = Announcement.query.get(announcement_id)
    if not announcement:
        return error('公告不存在', code=404)
    
    # 支持JSON和FormData两种格式
    if request.is_json:
        data = request.get_json()
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        announcement_type = data.get('type', '').strip()
        priority = data.get('priority')
        status = data.get('status')
        start_time = data.get('start_time', '').strip()
        end_time = data.get('end_time', '').strip()
        image = data.get('image', '').strip()
    else:
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        announcement_type = request.form.get('type', '').strip()
        priority = request.form.get('priority', type=int)
        status = request.form.get('status', type=int)
        start_time = request.form.get('start_time', '').strip()
        end_time = request.form.get('end_time', '').strip()
        image = ''
        # 处理文件上传
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file:
                # 删除旧图片
                if announcement.image:
                    delete_upload_file(announcement.image)
                image = save_upload_file(image_file, 'announcement')
    
    # 更新字段
    if title:
        announcement.title = title
    if content:
        announcement.content = content
    if announcement_type:
        announcement.type = announcement_type
    if priority is not None:
        announcement.priority = priority
    if status is not None:
        announcement.status = status
    if start_time:
        announcement.start_time = start_time
    if end_time:
        announcement.end_time = end_time
    if image:
        announcement.image = image
    
    try:
        db.session.commit()
        return success(announcement.to_dict(), '更新成功')
    except Exception as e:
        db.session.rollback()
        return error(f'更新失败: {str(e)}')


@bp.route('/announcements/<int:announcement_id>', methods=['DELETE'])
def delete_announcement(announcement_id):
    """
    删除公告
    
    路径参数:
        announcement_id: 公告ID
    
    返回:
        删除成功信息
    """
    is_admin, err_response = check_admin()
    if not is_admin:
        return err_response
    
    # 查询公告
    announcement = Announcement.query.get(announcement_id)
    if not announcement:
        return error('公告不存在', code=404)
    
    # 删除图片文件
    if announcement.image:
        delete_upload_file(announcement.image)
    
    try:
        db.session.delete(announcement)
        db.session.commit()
        return success(message='公告删除成功')
    except Exception as e:
        db.session.rollback()
        return error(f'删除失败: {str(e)}')


# ==================== 评论管理 ====================

@bp.route('/comments', methods=['GET'])
def get_admin_comments():
    """
    获取评论列表（管理后台）
    
    查询参数:
        keyword: 搜索关键词（搜索评论内容）
        food_id: 美食ID筛选
        user_id: 用户ID筛选
        page: 页码
        per_page: 每页数量
    
    返回:
        评论列表
    """
    is_admin, err_response = check_admin()
    if not is_admin:
        return err_response
    
    # 获取查询参数
    keyword = request.args.get('keyword', '').strip()
    food_id = request.args.get('food_id', type=int)
    user_id = request.args.get('user_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # 构建查询
    query = Comment.query
    
    # 关键词搜索
    if keyword:
        search_pattern = f'%{keyword}%'
        query = query.filter(Comment.content.like(search_pattern))
    
    # 美食筛选
    if food_id:
        query = query.filter_by(food_id=food_id)
    
    # 用户筛选
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    # 按创建时间倒序
    query = query.order_by(Comment.created_at.desc())
    
    # 分页查询
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # 转换为字典（包含用户和美食信息）
    comments = [comment.to_dict(include_user=True, include_food=True) for comment in pagination.items]
    
    # 返回分页数据
    return success(paginate_response(
        items=comments,
        total=pagination.total,
        page=page,
        per_page=per_page
    ))


@bp.route('/comments/<int:comment_id>', methods=['DELETE'])
def delete_admin_comment(comment_id):
    """
    删除评论（管理员）
    
    路径参数:
        comment_id: 评论ID
    
    返回:
        删除成功信息
    """
    is_admin, err_response = check_admin()
    if not is_admin:
        return err_response
    
    # 查询评论
    comment = Comment.query.get(comment_id)
    if not comment:
        return error('评论不存在', code=404)
    
    food_id = comment.food_id
    
    try:
        db.session.delete(comment)
        db.session.commit()
        
        # 更新美食的平均评分
        from app.routes.comment import update_food_rating
        update_food_rating(food_id)
        
        return success(message='评论删除成功')
    except Exception as e:
        db.session.rollback()
        return error(f'删除失败: {str(e)}')


# ==================== 数据统计 ====================

@bp.route('/statistics/overview', methods=['GET'])
def get_statistics_overview():
    """
    获取总览统计数据
    
    返回:
        总览统计数据
    """
    is_admin, err_response = check_admin()
    if not is_admin:
        return err_response
    
    # 统计各项数据
    from datetime import datetime, timedelta
    today = datetime.now().date()
    first_day_of_month = today.replace(day=1)
    
    user_count = User.query.count()
    food_count = Food.query.count()
    comment_count = Comment.query.count()
    favorite_count = Favorite.query.count()
    category_count = FoodCategory.query.count()
    
    # 今日新增
    today_user_count = User.query.filter(
        func.date(User.created_at) == today
    ).count()
    today_comment_count = Comment.query.filter(
        func.date(Comment.created_at) == today
    ).count()
    today_favorite_count = Favorite.query.filter(
        func.date(Favorite.created_at) == today
    ).count()
    
    # 本月新增美食
    monthly_food_count = Food.query.filter(
        func.date(Food.created_at) >= first_day_of_month,
        func.date(Food.created_at) <= today
    ).count()
    
    # 返回统计数据
    return success({
        'user_count': user_count,
        'food_count': food_count,
        'comment_count': comment_count,
        'favorite_count': favorite_count,
        'category_count': category_count,
        'today_user_count': today_user_count,
        'today_comment_count': today_comment_count,
        'today_favorite_count': today_favorite_count,
        'monthly_food_count': monthly_food_count
    })


@bp.route('/statistics/foods', methods=['GET'])
def get_food_statistics():
    """
    获取美食统计数据
    
    返回:
        美食统计数据（按分类、按地域）
    """
    is_admin, err_response = check_admin()
    if not is_admin:
        return err_response
    
    # 按分类统计
    category_stats = db.session.query(
        FoodCategory.name,
        func.count(Food.id).label('count')
    ).outerjoin(Food, Food.category_id == FoodCategory.id)\
     .group_by(FoodCategory.id, FoodCategory.name)\
     .all()
    
    # 按地域统计
    region_stats = db.session.query(
        Food.region,
        func.count(Food.id).label('count')
    ).group_by(Food.region).all()
    
    # 转换为字典
    category_data = [{'name': name, 'count': count} for name, count in category_stats]
    region_data = [{'name': region, 'count': count} for region, count in region_stats if region]
    
    return success({
        'by_category': category_data,
        'by_region': region_data
    })


@bp.route('/statistics/users', methods=['GET'])
def get_user_statistics():
    """
    获取用户统计数据
    
    查询参数:
        days: 统计天数（默认7天）
    
    返回:
        用户增长趋势数据
    """
    is_admin, err_response = check_admin()
    if not is_admin:
        return err_response
    
    # 获取查询参数
    days = request.args.get('days', 7, type=int)
    
    # 计算日期范围
    from datetime import datetime, timedelta
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days-1)
    
    # 按日期统计用户注册数
    user_stats = db.session.query(
        func.date(User.created_at).label('date'),
        func.count(User.id).label('count')
    ).filter(
        func.date(User.created_at) >= start_date,
        func.date(User.created_at) <= end_date
    ).group_by(func.date(User.created_at)).all()
    
    # 转换为字典
    stats_dict = {str(date): count for date, count in user_stats}
    
    # 填充缺失的日期（补0）
    result = []
    current_date = start_date
    while current_date <= end_date:
        date_str = str(current_date)
        result.append({
            'date': date_str,
            'count': stats_dict.get(date_str, 0)
        })
        current_date += timedelta(days=1)
    
    return success(result)


# ==================== 商家入驻审核 ====================

@bp.route('/merchants', methods=['GET'])
def get_merchant_applications():
    """
    获取商家入驻申请列表（待审核/已通过/已拒绝）
    查询参数: status, page, per_page
    """
    is_admin, err_response = check_admin()
    if not is_admin:
        return err_response
    
    status = request.args.get('status', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = Merchant.query.order_by(Merchant.created_at.desc())
    if status:
        query = query.filter_by(status=status)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = [m.to_dict(include_user=True) for m in pagination.items]
    
    return success(paginate_response(
        items=items,
        total=pagination.total,
        page=page,
        per_page=per_page
    ))


@bp.route('/merchants/<int:merchant_id>/approve', methods=['PUT'])
def approve_merchant(merchant_id):
    """通过商家入驻申请"""
    is_admin, err_response = check_admin()
    if not is_admin:
        return err_response
    
    merchant = Merchant.query.get(merchant_id)
    if not merchant:
        return error('申请不存在', code=404)
    if merchant.status != 'pending':
        return error('该申请已处理')
    
    merchant.status = 'approved'
    merchant.reject_reason = None
    
    # 将用户角色改为 merchant
    user = User.query.get(merchant.user_id)
    if user:
        user.role = 'merchant'
    
    try:
        db.session.commit()
        return success(merchant.to_dict(include_user=True), '审核通过')
    except Exception as e:
        db.session.rollback()
        return error(f'操作失败: {str(e)}')


@bp.route('/merchants/<int:merchant_id>/reject', methods=['PUT'])
def reject_merchant(merchant_id):
    """拒绝商家入驻申请"""
    is_admin, err_response = check_admin()
    if not is_admin:
        return err_response
    
    merchant = Merchant.query.get(merchant_id)
    if not merchant:
        return error('申请不存在', code=404)
    if merchant.status != 'pending':
        return error('该申请已处理')
    
    data = request.get_json() or {}
    reject_reason = (data.get('reject_reason') or '').strip() or '不符合入驻条件'
    
    merchant.status = 'rejected'
    merchant.reject_reason = reject_reason
    
    try:
        db.session.commit()
        return success(merchant.to_dict(include_user=True), '已拒绝')
    except Exception as e:
        db.session.rollback()
        return error(f'操作失败: {str(e)}')
