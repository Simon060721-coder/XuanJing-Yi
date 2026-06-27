# 玄镜易项目设置指南

## 前置条件

### 必须按装

- **Python 3.9+** - 后端运行环境
- **Node.js 16+** - 前端构建工具
- **npm/yarn** - JavaScript 依赖管理晨器
- **Git** - 版本控制

### 可选安装

- **Docker & Docker Compose** - 容器化部署
- **PostgreSQL** - 模型数据库
- **Redis** - 缓存处理

## 快速开始

### 方画一: 使用 Docker Compose

```bash
cd e:\\玄镜易
docker-compose up --build

# 前端: http://localhost:3000
# 后端: http://localhost:5000/api/v1
```

### 方画二: 本地开发环境

#### 后端设置

```bash
cd backend
python -m venv venv
venv\\Scripts\\activate  # Windows
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
cp .env.example .env
python run.py
```

#### 前端设置

```bash
cd frontend
npm install
npm run dev
```

## 项目结构

```
玄镜易/
├── backend/                # Flask 后端
│   ├── app/
│   │   ├── models/
│   │   ├── services/
│   │   └── routes/
│   ├── tests/
│   ├── run.py
│   └── requirements.txt
├── frontend/               # React 前端
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── styles/
│   ├── index.html
│   └── package.json
├── docs/
├── docker-compose.yml
└── README.md
```

## 常见问题

**Q: API 地址是什么?**

A: http://localhost:5000/api/v1

**Q: 不懂 TypeScript?**

A: 阅读 https://www.typescriptlang.org/docs/

**Q: 不懂易学?**

A: 阅读 [ALGORITHM.md](./ALGORITHM.md)
