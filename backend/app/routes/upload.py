"""
文件上传相关路由
处理图片上传功能及静态文件访问
"""
from flask import Blueprint, request, session, send_from_directory, current_app
from app.utils.response import success, error
from app.utils.file_upload import save_upload_file

bp = Blueprint('upload', __name__, url_prefix='/api/upload')


# 静态文件服务：单独注册 /uploads 路由（与 api/upload 同级）
uploads_bp = Blueprint('uploads', __name__)


@uploads_bp.route('/uploads/<path:filename>')
def serve_upload(filename):
    """提供上传文件的静态访问"""
    upload_folder = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(upload_folder, filename)


@bp.route('/image', methods=['POST'])
def upload_image():
    """
    上传图片
    
    请求参数:
        file: 图片文件（必填）
        type: 上传类型（avatar/food/category/banner/announcement，默认food）
    
    返回:
        图片路径
    """
    # 检查登录状态
    user_id = session.get('user_id')
    if not user_id:
        return error('请先登录', code=401)
    
    # 获取上传类型
    upload_type = request.form.get('type', 'food')
    
    # 验证上传类型
    valid_types = ['avatar', 'food', 'category', 'banner', 'announcement', 'merchant']
    if upload_type not in valid_types:
        return error(f'上传类型必须是以下之一: {", ".join(valid_types)}')
    
    # 检查文件
    if 'file' not in request.files:
        return error('请选择要上传的文件')
    
    file = request.files['file']
    if not file or file.filename == '':
        return error('请选择要上传的文件')
    
    # 保存文件
    file_path = save_upload_file(file, upload_type)
    if not file_path:
        return error('文件上传失败，请检查文件格式（支持png、jpg、jpeg、gif、webp）')
    
    return success({
        'path': file_path,
        'url': file_path  # 前端可以拼接完整URL
    }, '上传成功')


@bp.route('/test', methods=['GET'])
def test():
    """测试接口"""
    return {'message': '文件上传模块正常'}
