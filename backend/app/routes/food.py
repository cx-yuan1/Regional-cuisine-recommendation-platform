"""
美食相关路由
处理美食列表、详情、搜索等
"""
from flask import Blueprint, request
from sqlalchemy import or_
from app import db
from app.models.food import Food
from app.models.food_category import FoodCategory
from app.utils.response import success, error, paginate_response

bp = Blueprint('food', __name__, url_prefix='/api/foods')


@bp.route('', methods=['GET'])
def get_foods():
    """
    获取美食列表（支持筛选、搜索、分页）
    
    查询参数:
        region: 地域筛选
        category: 分类筛选（分类名称）
        category_id: 分类ID筛选
        keyword: 搜索关键词（搜索名称和描述）
        sort: 排序方式（rating评分/view_count浏览量/created_at时间，默认created_at）
        order: 排序顺序（asc升序/desc降序，默认desc）
        page: 页码（默认1）
        per_page: 每页数量（默认12）
    
    返回:
        美食列表
    """
    # 获取查询参数
    region = request.args.get('region', '').strip()
    category = request.args.get('category', '').strip()
    category_id = request.args.get('category_id', type=int)
    keyword = request.args.get('keyword', '').strip()
    sort_by = request.args.get('sort', 'created_at')
    order = request.args.get('order', 'desc')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    
    # 构建查询
    query = Food.query
    
    # 地域筛选
    if region:
        query = query.filter_by(region=region)
    
    # 分类筛选（支持分类名称或分类ID）
    if category_id:
        query = query.filter_by(category_id=category_id)
    elif category:
        # 通过分类名称查找分类ID
        food_category = FoodCategory.query.filter_by(name=category).first()
        if food_category:
            query = query.filter_by(category_id=food_category.id)
    
    # 关键词搜索（搜索名称和描述）
    if keyword:
        search_pattern = f'%{keyword}%'
        query = query.filter(
            or_(
                Food.name.like(search_pattern),
                Food.description.like(search_pattern)
            )
        )
    
    # 排序
    if sort_by == 'rating':
        sort_column = Food.rating
    elif sort_by == 'view_count':
        sort_column = Food.view_count
    else:
        sort_column = Food.created_at
    
    if order == 'asc':
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
    
    # 分页查询
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # 转换为字典
    foods = [food.to_dict() for food in pagination.items]
    
    # 返回分页数据
    return success(paginate_response(
        items=foods,
        total=pagination.total,
        page=page,
        per_page=per_page
    ))


@bp.route('/<int:food_id>', methods=['GET'])
def get_food_detail(food_id):
    """
    获取美食详情
    
    路径参数:
        food_id: 美食ID
    
    返回:
        美食详细信息（包含统计信息）
    """
    # 查询美食
    food = Food.query.get(food_id)
    if not food:
        return error('美食不存在', code=404)
    
    # 增加浏览次数
    food.view_count += 1
    try:
        db.session.commit()
    except:
        db.session.rollback()
    
    # 返回详情（包含统计信息）
    return success(food.to_dict(include_stats=True))


@bp.route('/regions', methods=['GET'])
def get_regions():
    """
    获取所有地域列表（去重）
    
    返回:
        地域列表
    """
    # 查询所有不重复的地域
    regions = db.session.query(Food.region).distinct().all()
    
    # 转换为列表
    region_list = [region[0] for region in regions if region[0]]
    
    return success(region_list)


@bp.route('/hot', methods=['GET'])
def get_hot_foods():
    """
    获取热门美食（按浏览量和评分综合排序）
    
    查询参数:
        limit: 返回数量（默认10）
    
    返回:
        热门美食列表
    """
    limit = request.args.get('limit', 10, type=int)
    
    # 查询热门美食（按浏览量降序，评分降序）
    foods = Food.query\
        .order_by(Food.view_count.desc(), Food.rating.desc())\
        .limit(limit)\
        .all()
    
    # 转换为字典
    foods_data = [food.to_dict() for food in foods]
    
    return success(foods_data)


@bp.route('/latest', methods=['GET'])
def get_latest_foods():
    """
    获取最新美食
    
    查询参数:
        limit: 返回数量（默认10）
    
    返回:
        最新美食列表
    """
    limit = request.args.get('limit', 10, type=int)
    
    # 查询最新美食
    foods = Food.query\
        .order_by(Food.created_at.desc())\
        .limit(limit)\
        .all()
    
    # 转换为字典
    foods_data = [food.to_dict() for food in foods]
    
    return success(foods_data)


@bp.route('/recommended', methods=['GET'])
def get_recommended_foods():
    """
    获取推荐美食（高评分美食）
    
    查询参数:
        limit: 返回数量（默认10）
        min_rating: 最低评分（默认4.0）
    
    返回:
        推荐美食列表
    """
    limit = request.args.get('limit', 10, type=int)
    min_rating = request.args.get('min_rating', 4.0, type=float)
    
    # 查询高评分美食
    foods = Food.query\
        .filter(Food.rating >= min_rating)\
        .order_by(Food.rating.desc(), Food.view_count.desc())\
        .limit(limit)\
        .all()
    
    # 转换为字典
    foods_data = [food.to_dict() for food in foods]
    
    return success(foods_data)


@bp.route('/test', methods=['GET'])
def test():
    """测试接口"""
    return {'message': '美食模块正常'}
