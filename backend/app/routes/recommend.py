"""
AI推荐相关路由
处理个性化推荐、热门推荐等
"""
from flask import Blueprint, request, session
from sqlalchemy import func, desc
from app import db
from app.models.food import Food
from app.models.user_behavior import UserBehavior
from app.models.favorite import Favorite
from app.models.comment import Comment
from app.utils.response import success, error

bp = Blueprint('recommend', __name__, url_prefix='/api/recommend')


@bp.route('/personal', methods=['GET'])
def get_personal_recommend():
    """
    个性化推荐（需要登录）
    基于用户的浏览历史和收藏记录推荐
    
    查询参数:
        limit: 返回数量（默认10）
    
    返回:
        个性化推荐美食列表
    """
    # 检查登录状态
    user_id = session.get('user_id')
    if not user_id:
        return error('请先登录', code=401)
    
    limit = request.args.get('limit', 10, type=int)
    
    # 获取用户收藏的美食分类和地域
    favorite_foods = db.session.query(Food)\
        .join(Favorite, Favorite.food_id == Food.id)\
        .filter(Favorite.user_id == user_id)\
        .all()
    
    # 提取用户偏好的分类和地域
    preferred_categories = set()
    preferred_regions = set()
    
    for food in favorite_foods:
        if food.category_id:
            preferred_categories.add(food.category_id)
        if food.region:
            preferred_regions.add(food.region)
    
    # 获取用户已收藏的美食ID（排除这些）
    favorited_food_ids = [food.id for food in favorite_foods]
    
    # 构建推荐查询
    query = Food.query
    
    # 排除已收藏的美食
    if favorited_food_ids:
        query = query.filter(~Food.id.in_(favorited_food_ids))
    
    # 如果有偏好分类或地域，优先推荐
    if preferred_categories or preferred_regions:
        query = query.filter(
            db.or_(
                Food.category_id.in_(preferred_categories) if preferred_categories else False,
                Food.region.in_(preferred_regions) if preferred_regions else False
            )
        )
    
    # 按评分和浏览量排序
    recommended_foods = query\
        .order_by(Food.rating.desc(), Food.view_count.desc())\
        .limit(limit)\
        .all()
    
    # 如果推荐数量不足，补充热门美食
    if len(recommended_foods) < limit:
        remaining = limit - len(recommended_foods)
        recommended_ids = [food.id for food in recommended_foods]
        exclude_ids = favorited_food_ids + recommended_ids
        
        additional_foods = Food.query\
            .filter(~Food.id.in_(exclude_ids) if exclude_ids else True)\
            .order_by(Food.rating.desc(), Food.view_count.desc())\
            .limit(remaining)\
            .all()
        
        recommended_foods.extend(additional_foods)
    
    # 转换为字典
    foods_data = [food.to_dict() for food in recommended_foods]
    
    return success(foods_data)


@bp.route('/hot', methods=['GET'])
def get_hot_recommend():
    """
    热门推荐（按浏览量和评分综合排序）
    
    查询参数:
        limit: 返回数量（默认10）
        category_id: 分类ID筛选（可选）
        region: 地域筛选（可选）
    
    返回:
        热门美食列表
    """
    limit = request.args.get('limit', 10, type=int)
    category_id = request.args.get('category_id', type=int)
    region = request.args.get('region', '').strip()
    
    # 构建查询
    query = Food.query
    
    # 分类筛选
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    # 地域筛选
    if region:
        query = query.filter_by(region=region)
    
    # 按浏览量和评分排序
    hot_foods = query\
        .order_by(Food.view_count.desc(), Food.rating.desc())\
        .limit(limit)\
        .all()
    
    # 转换为字典
    foods_data = [food.to_dict() for food in hot_foods]
    
    return success(foods_data)


@bp.route('/similar/<int:food_id>', methods=['GET'])
def get_similar_recommend(food_id):
    """
    相似美食推荐（基于分类和地域）
    
    路径参数:
        food_id: 美食ID
    
    查询参数:
        limit: 返回数量（默认10）
    
    返回:
        相似美食列表
    """
    limit = request.args.get('limit', 10, type=int)
    
    # 查询目标美食
    target_food = Food.query.get(food_id)
    if not target_food:
        return error('美食不存在', code=404)
    
    # 查询相似美食（同分类或同地域，排除自己）
    similar_foods = Food.query\
        .filter(Food.id != food_id)\
        .filter(
            db.or_(
                Food.category_id == target_food.category_id,
                Food.region == target_food.region
            )
        )\
        .order_by(Food.rating.desc(), Food.view_count.desc())\
        .limit(limit)\
        .all()
    
    # 转换为字典
    foods_data = [food.to_dict() for food in similar_foods]
    
    return success(foods_data)


@bp.route('/by-category/<int:category_id>', methods=['GET'])
def get_category_recommend(category_id):
    """
    按分类推荐（该分类下的高评分美食）
    
    路径参数:
        category_id: 分类ID
    
    查询参数:
        limit: 返回数量（默认10）
    
    返回:
        该分类下的推荐美食列表
    """
    limit = request.args.get('limit', 10, type=int)
    
    # 查询该分类下的高评分美食
    foods = Food.query\
        .filter_by(category_id=category_id)\
        .filter(Food.rating >= 4.0)\
        .order_by(Food.rating.desc(), Food.view_count.desc())\
        .limit(limit)\
        .all()
    
    # 转换为字典
    foods_data = [food.to_dict() for food in foods]
    
    return success(foods_data)


@bp.route('/by-region', methods=['GET'])
def get_region_recommend():
    """
    按地域推荐（该地域下的高评分美食）
    
    查询参数:
        region: 地域（必填）
        limit: 返回数量（默认10）
    
    返回:
        该地域下的推荐美食列表
    """
    region = request.args.get('region', '').strip()
    limit = request.args.get('limit', 10, type=int)
    
    if not region:
        return error('地域参数不能为空')
    
    # 查询该地域下的高评分美食
    foods = Food.query\
        .filter_by(region=region)\
        .filter(Food.rating >= 4.0)\
        .order_by(Food.rating.desc(), Food.view_count.desc())\
        .limit(limit)\
        .all()
    
    # 转换为字典
    foods_data = [food.to_dict() for food in foods]
    
    return success(foods_data)


@bp.route('/trending', methods=['GET'])
def get_trending_recommend():
    """
    趋势推荐（最近浏览量增长快的美食）
    
    查询参数:
        limit: 返回数量（默认10）
        days: 统计天数（默认7天）
    
    返回:
        趋势美食列表
    """
    limit = request.args.get('limit', 10, type=int)
    days = request.args.get('days', 7, type=int)
    
    # 计算日期范围
    from datetime import datetime, timedelta
    start_date = datetime.now() - timedelta(days=days)
    
    # 统计最近浏览行为最多的美食
    trending_foods = db.session.query(
        Food,
        func.count(UserBehavior.id).label('behavior_count')
    ).outerjoin(
        UserBehavior,
        db.and_(
            UserBehavior.food_id == Food.id,
            UserBehavior.created_at >= start_date,
            UserBehavior.behavior_type == 'view'
        )
    ).group_by(Food.id)\
     .order_by(desc('behavior_count'), Food.rating.desc())\
     .limit(limit)\
     .all()
    
    # 转换为字典
    foods_data = [food.to_dict() for food, count in trending_foods]
    
    return success(foods_data)


@bp.route('/new', methods=['GET'])
def get_new_recommend():
    """
    新品推荐（最新添加的美食）
    
    查询参数:
        limit: 返回数量（默认10）
    
    返回:
        最新美食列表
    """
    limit = request.args.get('limit', 10, type=int)
    
    # 查询最新添加的美食
    new_foods = Food.query\
        .order_by(Food.created_at.desc())\
        .limit(limit)\
        .all()
    
    # 转换为字典
    foods_data = [food.to_dict() for food in new_foods]
    
    return success(foods_data)


@bp.route('/test', methods=['GET'])
def test():
    """测试接口"""
    return {'message': 'AI推荐模块正常'}
