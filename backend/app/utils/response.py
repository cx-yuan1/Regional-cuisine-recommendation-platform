"""
统一响应格式工具
提供标准化的API响应格式
"""
from flask import jsonify


def success(data=None, message='操作成功', code=200):
    """
    成功响应
    
    参数:
        data: 返回的数据
        message: 提示信息
        code: 状态码
    
    返回:
        JSON响应对象
    """
    return jsonify({
        'code': code,
        'message': message,
        'data': data
    }), code


def error(message='操作失败', code=400, data=None):
    """
    错误响应
    
    参数:
        message: 错误信息
        code: 状态码
        data: 附加数据
    
    返回:
        JSON响应对象
    """
    return jsonify({
        'code': code,
        'message': message,
        'data': data
    }), code


def paginate_response(items, total, page, per_page):
    """
    分页响应
    
    参数:
        items: 当前页数据列表
        total: 总记录数
        page: 当前页码
        per_page: 每页数量
    
    返回:
        包含分页信息的数据字典
    """
    return {
        'items': items,
        'pagination': {
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page  # 总页数
        }
    }
