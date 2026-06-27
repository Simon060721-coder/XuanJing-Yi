"""玄镜易后端应用工厂"""
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from app.config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    """应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    CORS(app)
    
    # 注册蓝图
    from app.routes import divination_bp
    app.register_blueprint(divination_bp, url_prefix='/api/v1')
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app
