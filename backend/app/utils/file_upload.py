"""
文件上传处理工具
处理图片上传、验证、保存等功能
"""
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app


def allowed_file(filename):
    """
    检查文件扩展名是否允许
    
    参数:
        filename: 文件名
    
    返回:
        bool: 是否允许
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def generate_filename(original_filename):
    """
    生成唯一的文件名
    格式：日期时间_UUID_原始文件名
    
    参数:
        original_filename: 原始文件名
    
    返回:
        str: 新文件名
    """
    # 获取文件扩展名
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
    
    # 生成时间戳
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 生成短UUID
    unique_id = str(uuid.uuid4())[:8]
    
    # 组合新文件名
    return f"{timestamp}_{unique_id}.{ext}"


def save_upload_file(file, upload_type='food'):
    """
    保存上传的文件
    
    参数:
        file: 上传的文件对象
        upload_type: 上传类型（avatar/food/category/banner/announcement）
    
    返回:
        str: 文件的相对路径，失败返回None
    """
    if not file or file.filename == '':
        return None
    
    if not allowed_file(file.filename):
        return None
    
    # 生成新文件名
    filename = generate_filename(file.filename)
    
    # 获取上传子目录
    subfolder = current_app.config['UPLOAD_FOLDERS'].get(upload_type, 'others')
    
    # 构建完整路径
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    
    # 确保目录存在
    os.makedirs(upload_folder, exist_ok=True)
    
    # 保存文件
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)
    
    # 返回相对路径（用于存储到数据库）
    return f"/uploads/{subfolder}/{filename}"


def delete_upload_file(filepath):
    """
    删除上传的文件
    
    参数:
        filepath: 文件的相对路径
    
    返回:
        bool: 是否删除成功
    """
    if not filepath:
        return False
    
    try:
        # 构建完整路径
        full_path = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            filepath.replace('/uploads/', '')
        )
        
        # 删除文件
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
    except Exception as e:
        current_app.logger.error(f"删除文件失败: {str(e)}")
    
    return False
