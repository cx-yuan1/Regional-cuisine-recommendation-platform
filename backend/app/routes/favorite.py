"""
收藏相关路由
处理美食收藏功能
"""
from flask import Blueprint, request, session
from sqlalchemy.exc import IntegrityError
from app import db
from app.models.favorite import Favorite
from app.models.food import Food
from app.utils.response import success, error, paginate_response

bp = Blueprint('favorite', __name__, url_prefix='/api/favorites')


@bp.route('', methods=['POST'])
def add_favorite():
    """
    收藏美食（需要登录）
    
    请求参数:
        food_id: 美食ID（必填）
    
    返回:
        收藏成功信息
    """
    # 检查登录状态
    user_id = session.get('user_id')
    if not user_id:
        return error('请先登录', code=401)
    
    data = request.get_json()
    
    # 验证必填字段
    if not data or not data.get('food_id'):
        return error('美食ID不能为空')
    
    food_id = data.get('food_id')
    
    # 检查美食是否存在
    food = Food.query.get(food_id)
    if not food:
        return error('美食不存在', code=404)
    
    # 检查是否已经收藏
    existing_favorite = Favorite.query.filter_by(user_id=user_id, food_id=food_id).first()
    if existing_favorite:
        return error('已经收藏过该美食了')
    
    # 创建收藏
    new_favorite = Favorite(
        user_id=user_id,
        food_id=food_id
    )
    
    try:
        db.session.add(new_favorite)
        db.session.commit()
        return success(new_favorite.to_dict(), '收藏成功')
    except IntegrityError:
        db.session.rollback()
        return error('已经收藏过该美食了')
    except Exception as e:
        db.session.rollback()
        return error(f'收藏失败: {str(e)}')


@bp.route('/food/<int:food_id>', methods=['DELETE'])
def delete_favorite_by_food(food_id):
    """
    通过美食ID取消收藏（需要登录）
    
    路径参数:
        food_id: 美食ID
    
    返回:
        取消收藏成功信息
    """
    # 检查登录状态
    user_id = session.get('user_id')
    if not user_id:
        return error('请先登录', code=401)
    
    # 查询收藏
    favorite = Favorite.query.filter_by(user_id=user_id, food_id=food_id).first()
    if not favorite:
        # 已取消或从未收藏，直接返回成功（幂等）
        return success(message='取消收藏成功')
    
    try:
        db.session.delete(favorite)
        db.session.commit()
        return success(message='取消收藏成功')
    except Exception as e:
        db.session.rollback()
        return error(f'取消收藏失败: {str(e)}')


@bp.route('/<int:favorite_id>', methods=['DELETE'])
def delete_favorite(favorite_id):
    """
    取消收藏（需要登录，只能取消自己的收藏）
    
    路径参数:
        favorite_id: 收藏ID
    
    返回:
        取消收藏成功信息
    """
    # 检查登录状态
    user_id = session.get('user_id')
    if not user_id:
        return error('请先登录', code=401)
    
    # 查询收藏
    favorite = Favorite.query.get(favorite_id)
    if not favorite:
        return error('收藏记录不存在', code=404)
    
    # 检查权限（只能取消自己的收藏）
    if favorite.user_id != user_id:
        return error('无权取消此收藏', code=403)
    
    try:
        db.session.delete(favorite)
        db.session.commit()
        return success(message='取消收藏成功')
    except Exception as e:
        db.session.rollback()
        return error(f'取消收藏失败: {str(e)}')


@bp.route('/my', methods=['GET'])
def get_my_favorites():
    """
    获取当前用户的收藏列表（需要登录）
    
    查询参数:
        page: 页码（默认1）
        per_page: 每页数量（默认12）
    
    返回:
        当前用户的收藏列表
    """
    # 检查登录状态
    user_id = session.get('user_id')
    if not user_id:
        return error('请先登录', code=401)
    
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    
    # 查询当前用户的收藏
    query = Favorite.query.filter_by(user_id=user_id)\
        .order_by(Favorite.created_at.desc())
    
    # 分页查询
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # 转换为字典（包含美食信息）
    favorites = [favorite.to_dict(include_food=True) for favorite in pagination.items]
    
    # 返回分页数据
    return success(paginate_response(
        items=favorites,
        total=pagination.total,
        page=page,
        per_page=per_page
    ))


@bp.route('/check/<int:food_id>', methods=['GET'])
def check_favorite(food_id):
    """
    检查是否已收藏某个美食（需要登录）
    
    路径参数:
        food_id: 美食ID
    
    返回:
        是否已收藏
    """
    # 检查登录状态
    user_id = session.get('user_id')
    if not user_id:
        return error('请先登录', code=401)
    
    # 查询是否已收藏
    favorite = Favorite.query.filter_by(user_id=user_id, food_id=food_id).first()
    
    return success({
        'is_favorited': favorite is not None,
        'favorite_id': favorite.id if favorite else None
    })


@bp.route('/test', methods=['GET'])
def test():
    """测试接口"""
    return {'message': '收藏模块正常'}
