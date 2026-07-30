"""
应用配置模块
包含数据库连接、文件上传等配置
"""
import os
from datetime import timedelta


class Config:
    """应用配置类"""
    
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 数据库配置（明文连接，按需求）
    # 格式：mysql+pymysql://用户名:密码@主机:端口/数据库名
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:123456@localhost:3306/food_recommend?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # 设置为True可以看到SQL语句
    
    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 最大上传16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # 上传子目录配置
    UPLOAD_FOLDERS = {
        'avatar': 'avatars',
        'food': 'foods',
        'category': 'categories',
        'banner': 'banners',
        'announcement': 'announcements',
        'merchant': 'merchants'
    }
    
    # 分页配置
    ITEMS_PER_PAGE = 12  # 每页显示数量
    
    # JWT配置（如果后续需要）
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # CORS配置
    CORS_ORIGINS = ['http://localhost:5173', 'http://127.0.0.1:5173']
    
    # DeepSeek AI 配置（美食推荐对话）
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
    DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions'
