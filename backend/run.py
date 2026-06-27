#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""玄镜易后端应用启动脚本"""

import os
from app import create_app, db

if __name__ == '__main__':
    app = create_app()
    
    # 应用上下文中创建数据库表
    with app.app_context():
        db.create_all()
    
    # 运行应用
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=debug
    )
