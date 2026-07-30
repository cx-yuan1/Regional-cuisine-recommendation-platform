"""
商家端相关路由
处理入驻申请、美食发布、评价回复、店铺信息维护
"""
from flask import Blueprint, request, session
from datetime import datetime, timedelta
from sqlalchemy import or_, func
from app import db
from app.models.merchant import Merchant
from app.models.food import Food
from app.models.comment import Comment
from app.models.user import User
from app.models.favorite import Favorite
from app.models.food_category import FoodCategory
from app.utils.response import success, error, paginate_response

bp = Blueprint('merchant', __name__, url_prefix='/api/merchant')


def get_current_merchant():
    """获取当前登录用户的商家信息，需已通过审核"""
    user_id = session.get('user_id')
    if not user_id:
        return None, error('请先登录', code=401)
    merchant = Merchant.query.filter_by(user_id=user_id).first()
    if not merchant:
        return None, error('您还不是商家，请先申请入驻')
    if merchant.status != 'approved':
        return None, error('您的入驻申请尚未通过审核' if merchant.status == 'pending' else '入驻申请已被拒绝')
    return merchant, None


# ========== 入驻申请 ==========
@bp.route('/apply', methods=['POST'])
def apply_merchant():
    """
    商家入驻申请
    请求体: name, description, address, contact_phone, logo(可选)
    """
    user_id = session.get('user_id')
    if not user_id:
        return error('请先登录', code=401)
    
    # 检查是否已申请
    existing = Merchant.query.filter_by(user_id=user_id).first()
    if existing:
        if existing.status == 'approved':
            return error('您已是商家，无需重复申请')
        if existing.status == 'pending':
            return error('您的入驻申请正在审核中，请耐心等待')
        if existing.status == 'rejected':
            # 允许重新申请
            db.session.delete(existing)
            db.session.commit()
    
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    if not name or len(name) < 2:
        return error('店铺名称不能为空且至少2个字符')
    
    merchant = Merchant(
        user_id=user_id,
        name=name,
        description=(data.get('description') or '').strip() or None,
        address=(data.get('address') or '').strip() or None,
        contact_phone=(data.get('contact_phone') or '').strip() or None,
        logo=(data.get('logo') or '').strip() or None,
        status='pending'
    )
    try:
        db.session.add(merchant)
        db.session.commit()
        return success(merchant.to_dict(), '入驻申请已提交，请等待审核')
    except Exception as e:
        db.session.rollback()
        return error(f'申请失败: {str(e)}')


@bp.route('/apply/status', methods=['GET'])
def get_apply_status():
    """获取当前用户的入驻申请状态"""
    user_id = session.get('user_id')
    if not user_id:
        return error('请先登录', code=401)
    
    merchant = Merchant.query.filter_by(user_id=user_id).first()
    if not merchant:
        return success({'has_applied': False, 'merchant': None})
    return success({
        'has_applied': True,
        'merchant': merchant.to_dict(),
        'status': merchant.status
    })


# ========== 店铺信息 ==========
@bp.route('/me', methods=['GET'])
def get_merchant_info():
    """获取我的店铺信息"""
    merchant, err = get_current_merchant()
    if err:
        return err
    return success(merchant.to_dict(include_user=True))


@bp.route('/me', methods=['PUT'])
def update_merchant_info():
    """更新店铺信息"""
    merchant, err = get_current_merchant()
    if err:
        return err
    
    data = request.get_json() or {}
    if 'name' in data:
        name = (data.get('name') or '').strip()
        if name and len(name) >= 2:
            merchant.name = name
    if 'description' in data:
        merchant.description = (data.get('description') or '').strip() or None
    if 'address' in data:
        merchant.address = (data.get('address') or '').strip() or None
    if 'contact_phone' in data:
        merchant.contact_phone = (data.get('contact_phone') or '').strip() or None
    if 'logo' in data:
        merchant.logo = (data.get('logo') or '').strip() or None
    
    try:
        db.session.commit()
        return success(merchant.to_dict(), '更新成功')
    except Exception as e:
        db.session.rollback()
        return error(f'更新失败: {str(e)}')


# ========== 美食管理 ==========
@bp.route('/foods', methods=['GET'])
def get_merchant_foods():
    """获取我的店铺美食列表（分页）"""
    merchant, err = get_current_merchant()
    if err:
        return err
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    keyword = request.args.get('keyword', '').strip()
    category_id = request.args.get('category_id', type=int)
    region = request.args.get('region', '').strip()
    
    query = Food.query.filter_by(merchant_id=merchant.id)
    if keyword:
        query = query.filter(or_(
            Food.name.like(f'%{keyword}%'),
            Food.description.like(f'%{keyword}%')
        ))
    if category_id:
        query = query.filter_by(category_id=category_id)
    if region:
        query = query.filter(Food.region.like(f'%{region}%'))
    query = query.order_by(Food.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = [f.to_dict(include_stats=True) for f in pagination.items]
    
    return success(paginate_response(
        items=items,
        total=pagination.total,
        page=page,
        per_page=per_page
    ))


@bp.route('/foods', methods=['POST'])
def create_merchant_food():
    """发布美食"""
    merchant, err = get_current_merchant()
    if err:
        return err
    
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    if not name or len(name) < 2:
        return error('美食名称不能为空且至少2个字符')
    
    region = (data.get('region') or '').strip()
    if not region:
        return error('地域不能为空')
    
    category_id = data.get('category_id')
    if not category_id:
        return error('请选择分类')
    
    description = (data.get('description') or '').strip() or None
    image = (data.get('image') or '').strip() or None
    price_range = (data.get('price_range') or '').strip() or None
    
    import json
    taste_tags = data.get('taste_tags')
    if isinstance(taste_tags, list):
        taste_tags_str = json.dumps(taste_tags, ensure_ascii=False)
    else:
        taste_tags_str = str(taste_tags) if taste_tags else None
    
    food = Food(
        name=name,
        region=region,
        category_id=category_id,
        merchant_id=merchant.id,
        description=description,
        image=image,
        price_range=price_range,
        taste_tags=taste_tags_str
    )
    try:
        db.session.add(food)
        db.session.commit()
        return success(food.to_dict(), '发布成功')
    except Exception as e:
        db.session.rollback()
        return error(f'发布失败: {str(e)}')


@bp.route('/foods/<int:food_id>', methods=['PUT'])
def update_merchant_food(food_id):
    """编辑美食"""
    merchant, err = get_current_merchant()
    if err:
        return err
    
    food = Food.query.get(food_id)
    if not food:
        return error('美食不存在', code=404)
    if food.merchant_id != merchant.id:
        return error('无权编辑此美食', code=403)
    
    data = request.get_json() or {}
    if 'name' in data:
        name = (data.get('name') or '').strip()
        if name and len(name) >= 2:
            food.name = name
    if 'region' in data:
        region = (data.get('region') or '').strip()
        if region:
            food.region = region
    if 'category_id' in data:
        food.category_id = data.get('category_id')
    if 'description' in data:
        food.description = (data.get('description') or '').strip() or None
    if 'image' in data:
        food.image = (data.get('image') or '').strip() or None
    if 'price_range' in data:
        food.price_range = (data.get('price_range') or '').strip() or None
    if 'taste_tags' in data:
        import json
        tags = data.get('taste_tags')
        food.taste_tags = json.dumps(tags, ensure_ascii=False) if isinstance(tags, list) else str(tags) if tags else None
    
    try:
        db.session.commit()
        return success(food.to_dict(), '更新成功')
    except Exception as e:
        db.session.rollback()
        return error(f'更新失败: {str(e)}')


@bp.route('/foods/<int:food_id>', methods=['DELETE'])
def delete_merchant_food(food_id):
    """删除美食"""
    merchant, err = get_current_merchant()
    if err:
        return err
    
    food = Food.query.get(food_id)
    if not food:
        return error('美食不存在', code=404)
    if food.merchant_id != merchant.id:
        return error('无权删除此美食', code=403)
    
    try:
        db.session.delete(food)
        db.session.commit()
        return success(message='删除成功')
    except Exception as e:
        db.session.rollback()
        return error(f'删除失败: {str(e)}')


# ========== 商家统计 ==========
@bp.route('/statistics', methods=['GET'])
def get_merchant_statistics():
    """获取商家统计数据（仅本店铺可见）"""
    merchant, err = get_current_merchant()
    if err:
        return err
    
    food_ids = [f.id for f in Food.query.filter_by(merchant_id=merchant.id).all()]
    
    # 概览统计
    food_count = len(food_ids)
    comment_count = Comment.query.filter(Comment.food_id.in_(food_ids)).count() if food_ids else 0
    favorite_count = Favorite.query.filter(Favorite.food_id.in_(food_ids)).count() if food_ids else 0
    unreplied_count = Comment.query.filter(
        Comment.food_id.in_(food_ids),
        Comment.reply_content.is_(None)
    ).count() if food_ids else 0
    total_view_count = db.session.query(func.sum(Food.view_count)).filter(
        Food.merchant_id == merchant.id
    ).scalar() or 0
    
    # 评论趋势（近N天每日评论数）
    days = request.args.get('days', 7, type=int)
    days = min(max(days, 7), 30)
    start_date = datetime.now().date() - timedelta(days=days)
    
    comment_trend = []
    if food_ids:
        date_col = func.date(Comment.created_at)
        trend_rows = db.session.query(
            date_col.label('date'),
            func.count(Comment.id).label('count')
        ).filter(
            Comment.food_id.in_(food_ids),
            date_col >= start_date
        ).group_by(date_col).order_by(date_col).all()
        comment_trend = [{'date': str(r.date), 'count': r.count} for r in trend_rows]
    
    # 补全日期（无评论的日期为0）
    all_dates = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days + 1)]
    trend_map = {t['date']: t['count'] for t in comment_trend}
    comment_trend = [{'date': d, 'count': trend_map.get(d, 0)} for d in all_dates]
    
    # 美食分类分布（饼图）
    by_category = []
    if food_ids:
        cat_rows = db.session.query(
            FoodCategory.name,
            func.count(Food.id).label('count')
        ).join(Food, Food.category_id == FoodCategory.id).filter(
            Food.merchant_id == merchant.id
        ).group_by(FoodCategory.name).all()
        by_category = [{'name': r.name, 'count': r.count} for r in cat_rows]
    
    # 评分分布（柱状图 1-5星）
    rating_dist = []
    if food_ids:
        for r in range(1, 6):
            cnt = Comment.query.filter(
                Comment.food_id.in_(food_ids),
                Comment.rating == r
            ).count()
            rating_dist.append({'rating': r, 'count': cnt})
    
    # 各美食浏览量 TOP10（柱状图）
    top_foods = []
    if food_ids:
        foods = Food.query.filter_by(merchant_id=merchant.id).order_by(
            Food.view_count.desc()
        ).limit(10).all()
        top_foods = [{'name': f.name, 'view_count': f.view_count or 0} for f in foods]
    
    return success({
        'overview': {
            'food_count': food_count,
            'comment_count': comment_count,
            'favorite_count': favorite_count,
            'unreplied_count': unreplied_count,
            'total_view_count': int(total_view_count)
        },
        'comment_trend': comment_trend,
        'by_category': by_category,
        'rating_distribution': rating_dist,
        'top_foods_by_view': top_foods
    })


# ========== 评价回复 ==========
@bp.route('/comments', methods=['GET'])
def get_merchant_comments():
    """获取我店铺美食的评论列表"""
    merchant, err = get_current_merchant()
    if err:
        return err
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 获取商家所有美食的ID
    food_ids = [f.id for f in Food.query.filter_by(merchant_id=merchant.id).all()]
    if not food_ids:
        return success(paginate_response(items=[], total=0, page=page, per_page=per_page))
    
    query = Comment.query.filter(Comment.food_id.in_(food_ids)).order_by(Comment.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = [c.to_dict(include_user=True, include_food=True) for c in pagination.items]
    
    return success(paginate_response(
        items=items,
        total=pagination.total,
        page=page,
        per_page=per_page
    ))


@bp.route('/comments/<int:comment_id>/reply', methods=['POST'])
def reply_comment(comment_id):
    """回复评论"""
    merchant, err = get_current_merchant()
    if err:
        return err
    
    comment = Comment.query.get(comment_id)
    if not comment:
        return error('评论不存在', code=404)
    
    # 验证评论属于商家美食
    food = Food.query.get(comment.food_id)
    if not food or food.merchant_id != merchant.id:
        return error('无权回复此评论', code=403)
    
    data = request.get_json() or {}
    reply_content = (data.get('content') or data.get('reply_content') or '').strip()
    if not reply_content or len(reply_content) < 2:
        return error('回复内容不能为空且至少2个字符')
    
    comment.reply_content = reply_content
    comment.reply_at = datetime.now()
    comment.replied_by = session.get('user_id')
    
    try:
        db.session.commit()
        return success(comment.to_dict(include_user=True, include_food=True), '回复成功')
    except Exception as e:
        db.session.rollback()
        return error(f'回复失败: {str(e)}')
