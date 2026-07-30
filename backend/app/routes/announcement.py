"""
公告相关路由
处理公告列表、详情等。
"""
from flask import Blueprint, request
from datetime import datetime
from app import db
from app.models.announcement import Announcement
from app.utils.response import success, error, paginate_response

bp = Blueprint('announcement', __name__, url_prefix='/api/announcements')


@bp.route('', methods=['GET'])
def get_announcements():
    """
    获取公告列表（支持筛选、搜索、分页）
    
    查询参数:
        type: 公告类型筛选（notice/event/system）
        status: 状态筛选（0禁用/1启用）
        keyword: 搜索关键词（搜索标题和内容）
        page: 页码（默认1）
        per_page: 每页数量（默认10）
    
    返回:
        公告列表（只返回有效期内的公告）
    """
    # 获取查询参数
    announcement_type = request.args.get('type', '').strip()
    status = request.args.get('status', type=int)
    keyword = request.args.get('keyword', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 构建查询
    query = Announcement.query
    
    # 只查询启用的公告（如果没有指定status）
    if status is not None:
        query = query.filter_by(status=status)
    else:
        query = query.filter_by(status=1)
    
    # 类型筛选
    if announcement_type:
        query = query.filter_by(type=announcement_type)
    
    # 关键词搜索
    if keyword:
        search_pattern = f'%{keyword}%'
        query = query.filter(
            db.or_(
                Announcement.title.like(search_pattern),
                Announcement.content.like(search_pattern)
            )
        )
    
    # 时间范围筛选（只显示有效期内的公告）
    now = datetime.now()
    query = query.filter(
        db.or_(
            Announcement.start_time.is_(None),
            Announcement.start_time <= now
        )
    ).filter(
        db.or_(
            Announcement.end_time.is_(None),
            Announcement.end_time >= now
        )
    )
    
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


@bp.route('/<int:announcement_id>', methods=['GET'])
def get_announcement_detail(announcement_id):
    """
    获取公告详情
    
    路径参数:
        announcement_id: 公告ID
    
    返回:
        公告详细信息
    """
    # 查询公告
    announcement = Announcement.query.get(announcement_id)
    if not announcement:
        return error('公告不存在', code=404)
    
    # 增加浏览次数
    announcement.view_count += 1
    try:
        db.session.commit()
    except:
        db.session.rollback()
    
    # 返回详情
    return success(announcement.to_dict())


@bp.route('/latest', methods=['GET'])
def get_latest_announcements():
    """
    获取最新公告（用于首页展示）
    
    查询参数:
        limit: 返回数量（默认5）
    
    返回:
        最新公告列表（只返回有效期内的启用公告）
    """
    limit = request.args.get('limit', 5, type=int)
    
    # 当前时间
    now = datetime.now()
    
    # 查询最新的启用公告（在有效期内）
    announcements = Announcement.query\
        .filter_by(status=1)\
        .filter(
            db.or_(
                Announcement.start_time.is_(None),
                Announcement.start_time <= now
            )
        )\
        .filter(
            db.or_(
                Announcement.end_time.is_(None),
                Announcement.end_time >= now
            )
        )\
        .order_by(Announcement.priority.desc(), Announcement.created_at.desc())\
        .limit(limit)\
        .all()
    
    # 转换为字典
    announcements_data = [announcement.to_dict() for announcement in announcements]
    
    return success(announcements_data)


@bp.route('/types', methods=['GET'])
def get_announcement_types():
    """
    获取公告类型列表
    
    返回:
        公告类型列表
    """
    types = [
        {'value': 'notice', 'label': '通知'},
        {'value': 'event', 'label': '活动'},
        {'value': 'system', 'label': '系统'}
    ]
    
    return success(types)


@bp.route('/test', methods=['GET'])
def test():
    """测试接口"""
    return {'message': '公告模块正常'}
