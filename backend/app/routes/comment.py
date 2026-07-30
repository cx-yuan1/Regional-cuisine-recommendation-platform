"""
评论相关路由
处理评论的增删查改
"""
from flask import Blueprint, request, session
from app import db
from app.models.comment import Comment
from app.models.food import Food
from app.utils.response import success, error, paginate_response

bp = Blueprint('comment', __name__, url_prefix='/api/comments')


@bp.route('', methods=['POST'])
def create_comment():
    """
    发表评论（需要登录）
    
    请求参数:
        food_id: 美食ID（必填）
        content: 评论内容（必填）
        rating: 评分1-5（必填）
    
    返回:
        新创建的评论信息
    """
    # 检查登录状态
    user_id = session.get('user_id')
    if not user_id:
        return error('请先登录', code=401)
    
    data = request.get_json()
    
    # 验证必填字段
    if not data or not data.get('food_id') or not data.get('content') or not data.get('rating'):
        return error('美食ID、评论内容和评分不能为空')
    
    food_id = data.get('food_id')
    content = data.get('content', '').strip()
    rating = data.get('rating')
    
    # 验证评分范围
    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return error('评分必须是1-5之间的整数')
    
    # 验证评论内容长度
    if len(content) < 5:
        return error('评论内容不能少于5个字符')
    
    if len(content) > 500:
        return error('评论内容不能超过500个字符')
    
    # 检查美食是否存在
    food = Food.query.get(food_id)
    if not food:
        return error('美食不存在', code=404)
    
    # 创建评论
    new_comment = Comment(
        user_id=user_id,
        food_id=food_id,
        content=content,
        rating=rating
    )
    
    try:
        db.session.add(new_comment)
        db.session.commit()
        
        # 更新美食的平均评分
        update_food_rating(food_id)
        
        return success(new_comment.to_dict(), '评论发表成功')
    except Exception as e:
        db.session.rollback()
        return error(f'评论发表失败: {str(e)}')


@bp.route('/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    """
    删除评论（需要登录，只能删除自己的评论）
    
    路径参数:
        comment_id: 评论ID
    
    返回:
        删除成功信息
    """
    # 检查登录状态
    user_id = session.get('user_id')
    if not user_id:
        return error('请先登录', code=401)
    
    # 查询评论
    comment = Comment.query.get(comment_id)
    if not comment:
        return error('评论不存在', code=404)
    
    # 检查权限（只能删除自己的评论，或管理员可以删除任何评论）
    user_role = session.get('role')
    if comment.user_id != user_id and user_role != 'admin':
        return error('无权删除此评论', code=403)
    
    food_id = comment.food_id
    
    try:
        db.session.delete(comment)
        db.session.commit()
        
        # 更新美食的平均评分
        update_food_rating(food_id)
        
        return success(message='评论删除成功')
    except Exception as e:
        db.session.rollback()
        return error(f'评论删除失败: {str(e)}')


@bp.route('/food/<int:food_id>', methods=['GET'])
def get_food_comments(food_id):
    """
    获取指定美食的评论列表
    
    路径参数:
        food_id: 美食ID
    
    查询参数:
        page: 页码（默认1）
        per_page: 每页数量（默认10）
        sort: 排序方式（created_at时间/rating评分，默认created_at）
        order: 排序顺序（asc升序/desc降序，默认desc）
    
    返回:
        评论列表
    """
    # 检查美食是否存在
    food = Food.query.get(food_id)
    if not food:
        return error('美食不存在', code=404)
    
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort', 'created_at')
    order = request.args.get('order', 'desc')
    
    # 构建查询
    query = Comment.query.filter_by(food_id=food_id)
    
    # 排序
    if sort_by == 'rating':
        sort_column = Comment.rating
    else:
        sort_column = Comment.created_at
    
    if order == 'asc':
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
    
    # 分页查询
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # 转换为字典（包含用户信息）
    comments = [comment.to_dict(include_user=True) for comment in pagination.items]
    
    # 返回分页数据
    return success(paginate_response(
        items=comments,
        total=pagination.total,
        page=page,
        per_page=per_page
    ))


@bp.route('/my', methods=['GET'])
def get_my_comments():
    """
    获取当前用户的评论列表（需要登录）
    
    查询参数:
        page: 页码（默认1）
        per_page: 每页数量（默认10）
    
    返回:
        当前用户的评论列表
    """
    # 检查登录状态
    user_id = session.get('user_id')
    if not user_id:
        return error('请先登录', code=401)
    
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 查询当前用户的评论
    query = Comment.query.filter_by(user_id=user_id)\
        .order_by(Comment.created_at.desc())
    
    # 分页查询
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # 转换为字典（包含美食信息）
    comments = [comment.to_dict(include_user=False, include_food=True) for comment in pagination.items]
    
    # 返回分页数据
    return success(paginate_response(
        items=comments,
        total=pagination.total,
        page=page,
        per_page=per_page
    ))


def update_food_rating(food_id):
    """
    更新美食的平均评分
    
    参数:
        food_id: 美食ID
    """
    # 计算平均评分
    result = db.session.query(db.func.avg(Comment.rating))\
        .filter(Comment.food_id == food_id)\
        .scalar()
    
    # 更新美食评分
    food = Food.query.get(food_id)
    if food:
        food.rating = round(result, 2) if result else 0.00
        db.session.commit()


@bp.route('/test', methods=['GET'])
def test():
    """测试接口"""
    return {'message': '评论模块正常'}
