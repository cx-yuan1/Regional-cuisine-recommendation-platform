"""
Flask应用初始化模块
创建Flask应用实例，配置数据库、CORS等
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from app.config import Config

# 初始化数据库对象
db = SQLAlchemy()


def create_app(config_class=Config):
    """
    应用工厂函数
    
    参数:
        config_class: 配置类，默认使用Config
    
    返回:
        Flask应用实例
    """
    # 创建Flask应用实例
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    
    # 配置CORS，支持凭证（session）
    CORS(app, supports_credentials=True, origins=app.config['CORS_ORIGINS'])
    
    # 注册蓝图（路由）
    from app.routes import user, food, food_category, comment, favorite, banner, announcement, recommend, ai, admin, upload, merchant
    
    app.register_blueprint(upload.uploads_bp)  # /uploads 静态文件，需先注册
    app.register_blueprint(user.bp)
    app.register_blueprint(food.bp)
    app.register_blueprint(food_category.bp)
    app.register_blueprint(comment.bp)
    app.register_blueprint(favorite.bp)
    app.register_blueprint(banner.bp)
    app.register_blueprint(announcement.bp)
    app.register_blueprint(recommend.bp)
    app.register_blueprint(ai.bp)
    app.register_blueprint(merchant.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(upload.bp)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app
