"""
轮播图相关路由
处理轮播图展示
"""
from flask import Blueprint
from app.models.banner import Banner
from app.utils.response import success, error

bp = Blueprint('banner', __name__, url_prefix='/api/banners')


@bp.route('', methods=['GET'])
def get_banners():
    """
    获取启用的轮播图列表（前台展示）
    
    返回:
        启用的轮播图列表（按排序字段排序）
    """
    # 查询所有启用的轮播图
    banners = Banner.query.filter_by(status=1)\
        .order_by(Banner.sort_order.asc(), Banner.id.asc())\
        .all()
    
    # 转换为字典
    banners_data = [banner.to_dict() for banner in banners]
    
    return success(banners_data)


@bp.route('/<int:banner_id>', methods=['GET'])
def get_banner(banner_id):
    """
    获取单个轮播图详情
    
    路径参数:
        banner_id: 轮播图ID
    
    返回:
        轮播图详情
    """
    banner = Banner.query.get(banner_id)
    if not banner:
        return error('轮播图不存在', code=404)
    
    return success(banner.to_dict())


@bp.route('/test', methods=['GET'])
def test():
    """测试接口"""
    return {'message': '轮播图模块正常'}
