"""路由模块"""
from flask import Blueprint

divination_bp = Blueprint('divination', __name__)

from app.routes import divination_routes
