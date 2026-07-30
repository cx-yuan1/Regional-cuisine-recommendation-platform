"""
美食分类相关路由
处理分类列表、分类下的美食等
"""
from flask import Blueprint, request
from app import db
from app.models.food_category import FoodCategory
from app.models.food import Food
from app.utils.response import success, error, paginate_response

bp = Blueprint('food_category', __name__, url_prefix='/api/food-categories')


@bp.route('', methods=['GET'])
def get_categories():
    """
    获取美食分类列表
    
    查询参数:
        status: 状态筛选（0禁用/1启用），不传则返回所有
        page: 页码（默认1）
        per_page: 每页数量（默认20）
    
    返回:
        分类列表
    """
    # 获取查询参数
    status = request.args.get('status', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # 构建查询
    query = FoodCategory.query
    
    # 状态筛选
    if status is not None:
        query = query.filter_by(status=status)
    
    # 按排序字段和ID排序
    query = query.order_by(FoodCategory.sort_order.asc(), FoodCategory.id.asc())
    
    # 分页查询
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # 转换为字典
    categories = [category.to_dict() for category in pagination.items]
    
    # 返回分页数据
    return success(paginate_response(
        items=categories,
        total=pagination.total,
        page=page,
        per_page=per_page
    ))


@bp.route('/<int:category_id>/foods', methods=['GET'])
def get_category_foods(category_id):
    """
    获取指定分类下的美食列表
    
    路径参数:
        category_id: 分类ID
    
    查询参数:
        page: 页码（默认1）
        per_page: 每页数量（默认12）
        sort: 排序方式（rating评分/view_count浏览量/created_at时间，默认created_at）
        order: 排序顺序（asc升序/desc降序，默认desc）
    
    返回:
        该分类下的美食列表
    """
    # 检查分类是否存在
    category = FoodCategory.query.get(category_id)
    if not category:
        return error('分类不存在', code=404)
    
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    sort_by = request.args.get('sort', 'created_at')
    order = request.args.get('order', 'desc')
    
    # 构建查询（只查询该分类下的美食）
    query = Food.query.filter_by(category_id=category_id)
    
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
    
    # 返回数据
    return success({
        'category': category.to_dict(),
        'foods': paginate_response(
            items=foods,
            total=pagination.total,
            page=page,
            per_page=per_page
        )
    })


@bp.route('/active', methods=['GET'])
def get_active_categories():
    """
    获取所有启用的分类（用于前台展示）
    
    返回:
        启用的分类列表（按排序字段排序）
    """
    # 查询所有启用的分类
    categories = FoodCategory.query.filter_by(status=1)\
        .order_by(FoodCategory.sort_order.asc(), FoodCategory.id.asc())\
        .all()
    
    # 转换为字典
    categories_data = [category.to_dict() for category in categories]
    
    return success(categories_data)


@bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """
    获取单个分类详情
    
    路径参数:
        category_id: 分类ID
    
    返回:
        分类详情
    """
    category = FoodCategory.query.get(category_id)
    if not category:
        return error('分类不存在', code=404)
    
    return success(category.to_dict())


@bp.route('/test', methods=['GET'])
def test():
    """测试接口"""
    return {'message': '美食分类模块正常'}
