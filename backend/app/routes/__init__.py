"""路由模块"""
from flask import Blueprint

divination_bp = Blueprint('divination', __name__)
liuyao_bp = Blueprint('liuyao', __name__)

from app.routes import divination_routes   # noqa: E402,F401
from app.routes import liuyao_routes       # noqa: E402,F401
