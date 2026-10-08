## 项目简介

玄镜易是一套自用易学占断系统，内置**纳甲筮法（六爻）**与**梅花易数**两套完整排盘、断卦引擎，搭配青铜质感古风界面。支持龟壳摇钱成卦、八卦盘取数起卦；每一步占断逻辑均可溯源传统术数典籍依据。

本项目区别于市面上 “随机生成卦象 + 套用模板文案” 的工具：完整还原两套术数底层规则，界面不只是装饰，更是算法规则的可视化展示 —— 你可以直观看到为何此爻为动爻、此卦为体卦，所有判定节点均可追溯。

### 功能总览

#### ✦ 六爻（纳甲筮法）

- 起卦仪式：龟壳震动动画，三枚铜钱旋落，六轮成卦；支持跳过动画直接起卦
- 装卦逻辑：本卦、变卦、宫位、世应、纳甲、六亲、六神、伏神、旬空、进退、六冲六合完整实现
- 断卦引擎：根据所占事项选取用神（占感情可按性别区分妻财 / 官鬼），依托月建、日建判定五行旺衰；逐条输出判定依据与权重，汇总吉凶档位
- 知识库：六十四卦、八卦、四柱干支、二十四节气，支持独立查询

#### ✦ 梅花易数

- 时间起卦：取当下时间起卦，以年支 + 月 + 日定上卦，叠加时支定下卦，遵循古法 “取当下” 的起卦逻辑
- 数字起卦：默认点击八卦盘取数，也支持手动自定义报数起卦
- 成卦动效：八卦盘卦象点亮 → 六爻依次渲染 → 动爻翻转 → 变卦剥离，区分体卦用卦，标注五行生克方向
- 节奏设计：起卦阶段画面静谧低动效，成卦瞬间强动态反馈，形成仪式感

#### ✦ 历史与附加功能

- 占卜记录：列表查看历史卦例，支持单条详情查看、单独删除、一键清空全部记录
- 关于页面：记录起卦规则、解读逻辑构成，如实标注当前实现存在的偏差

## 技术栈

表格

| 分层 | 选型 |
| --- | --- |
| 后端 | Python 3.9+、Flask 2.3、SQLAlchemy 2.0、Flask-SQLAlchemy、Flask-CORS |
| 数据库 | SQLite（默认） / PostgreSQL（修改 DATABASE_URL 即可切换） |
| 前端 | React 18、TypeScript 5.6、Vite 5、Tailwind CSS 3.4、Framer Motion 10 |
| 样式规范 | CSS 变量令牌 + Tailwind；不依赖外部字体、CDN 资源，可完全离线运行 |

## 快速开始

环境前置要求：`Python 3.9+` 与 `Node.js 18+`

### 后端启动

```
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
python run.py
# 服务地址：http://localhost:5000/
# 首次运行自动创建数据表，SQLite数据库文件生成在 backend/ 目录
```

### 前端启动

```
cd frontend
npm install
npm run dev
# 前端地址：http://localhost:3000/
# Vite已配置/api代理转发至后端 5000端口，无需额外修改配置
```

## 自检体系（项目核心特色）

术数开发最隐蔽的 bug，不是程序崩溃，而是卦象看似正常，但纳甲、世应、节气等细节计算出错。
本项目不单单以 “无程序报错” 作为验证标准，而是使用**经典已知卦例回归校验**，保证算法可复现。

执行自检命令：

```
cd backend
py -c "from app.services.liuyao.selftest import main; raise SystemExit(main())"
```

当前：共 1140 项检查，0 失败。
校验覆盖模块：

1. `ganzhi_selftest`：干支推算、节气换算精度，逐项比对参考值，打印时间偏差
2. `judgment_selftest`：用神选取规则、旺衰判定、吉凶分档逻辑校验
3. `api_selftest`：Flask 接口路由、参数校验、JSON 序列化测试；使用内存 SQLite，不写入磁盘
4. `meihua_selftest`：梅花易数起卦、体用生克、变卦生成，内置标准答案用例
5. 统计检验：铜钱摇卦模型校验，三次投掷为独立事件，服从二项分布 B (3, ½)，验证随机模型合理性

> 
> 历史 Bug 案例：前端传递带时区的 ISO 时间串（`toISOString()` 末尾带 Z），早期引擎直接按本地无时间戳时间解析，会造成时间起卦异常。旧测试用例使用不带时区字符串，未能覆盖该场景；现已补充两种格式的测试用例。

## 项目目录结构

```
玄镜易/
├── backend/
│   ├── app/
│   │   ├── __init__.py                 # 应用工厂 create_app()
│   │   ├── config.py                   # 环境配置：开发/测试/生产
│   │   ├── models/
│   │   │   └── hexagram.py             # SQLAlchemy 占卜记录等数据模型
│   │   ├── routes/
│   │   │   ├── liuyao_routes.py        # 六爻接口蓝图
│   │   │   └── divination_routes.py    # 梅花易数 + 历史记录蓝图
│   │   └── services/
│   │       ├── liuyao/                 # 六爻术数内核，纯函数，不绑定Flask
│   │       │   ├── constants.py        # 八卦、六十四卦、纳甲、六亲、六神基础数据表
│   │       │   ├── ganzhi.py           # 干支、四柱、节气计算
│   │       │   ├── casting.py          # 铜钱起爻逻辑
│   │       │   ├── hexagrams.py         # 卦库、装卦处理
│   │       │   ├── paipan.py           # 排盘：纳甲、六亲、世应、六神、伏神、旬空
│   │       │   ├── judgment.py         # 用神、旺衰、吉凶判定
│   │       │   ├── *_selftest.py       # 分层单元自检
│   │       │   └── selftest.py         # 自检统一入口
│   │       ├── divination_engine.py    # 梅花易数核心引擎
│   │       ├── meihua_selftest.py      # 梅花易数自检
│   │       └── mapping_service.py      # 卦象数据→解读文本映射
│   ├── run.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/                      # 首页 / 六爻 / 梅花 / 历史 / 关于
│   │   ├── components/
│   │   │   ├── PageShell.tsx           # 全站页面统一骨架
│   │   │   ├── Header.tsx / Footer.tsx / Layout.tsx
│   │   │   ├── liuyao/                 # 摇卦舞台、龟壳、铜钱、爻组件、解读面板
│   │   │   └── divination/              # 八卦盘、卦画组件
│   │   ├── styles/
│   │   │   ├── index.css               # 全局设计令牌，唯一色值来源
│   │   │   ├── liuyao.css              # 六爻摇卦仪式、铜钱样式
│   │   │   ├── divination.css          # 八卦盘、成卦动画
│   │   │   └── ui.ts                   # 按钮、卡片、输入框等基础UI原语
│   │   ├── services/liuyaoApi.ts
│   │   └── types/liuyao.ts
│   ├── public/assets/                  # 龟甲等静态素材资源
│   └── vite.config.ts
├── docs/                               # 设计文档、算法文档、架构文档
├── docker-compose.yml
└── README.md
```

> 
> 分层约定：`services` 目录下术数内核全部为纯函数，不依赖 Flask，可独立调用与单元测试；路由层仅负责参数校验、调用内核、组装返回 JSON，让自检可以脱离 HTTP 直接验算底层逻辑。

## API 接口一览

统一接口前缀：`/api/v1`

### 六爻

表格

| 请求方式 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/liuyao/toss` | 摇取单爻 |
| POST | `/liuyao/toss-six` | 一次性生成六爻 |
| POST | `/liuyao/paipan` | 装卦排盘 + 断卦计算 |
| GET | `/liuyao/topics` | 占问事项分类 |
| GET/POST | `/liuyao/sizhu` | 四柱干支计算 |
| GET | `/liuyao/hexagrams` | 六十四卦基础信息 |
| GET | `/liuyao/trigrams` | 八卦基础信息 |
| GET | `/liuyao/solar-terms` | 节气数据 |

### 梅花易数 & 历史记录

表格

| 请求方式 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/divination/query` | 起卦（时间起卦 / 数字起卦） |
| GET | `/divination/history` | 历史记录分页列表 |
| GET | `/divination/history/:id` | 单条卦例详情 |
| DELETE | `/divination/history/:id` | 删除单条记录 |
| DELETE | `/divination/history` | 清空全部记录，返回实际删除条数（幂等接口） |
| GET | `/hexagrams` | 卦象基础数据 |
| GET | `/health` | 服务健康检查 |

## 设计系统

色彩与质感统一托管，`frontend/src/index.css` 的 CSS 令牌是全站唯一色值来源；`tailwind.config.js` 读取令牌，组件直接引用令牌类名。更换主题配色无需修改业务组件。

- 通道三元组：例如 `--xj-gold: 198 165 103`，支持 `rgb(var(--xj-gold) / 透明度)` 写法，兼容 Tailwind 透明度修饰符（如`bg-xuanjing-gold/20`）
- 完整色值：例如 `--xj-shell-deep: #17110A`，可直接使用
页面骨架由 `PageShell.tsx` 统一管控内边距、内容最大宽度、纵向间距、页头规范。
按钮、卡片、输入框等基础 UI 原语统一写在 `styles/ui.ts`，页面不再写内联长 class 串，解决同类控件尺寸不一致、页面切换时组件跳动问题。
青铜、铜钱色值均参考实物采样，非主观调参。

## 已知边界与实现偏差

> 
> 全部差异如实标注，方便使用者判断适用范围

1. 时间起卦：当前版本公历月日取数；古法以农历为准。年支、时支干支计算精准，该偏差会在界面与 API 中标注，后续补齐农历换算后修正。
2. 断卦评分：部分评分数值为工程权重设定，并非古籍固定数值，仅用于结果排序、吉凶分档；判定依据清单不受权重影响。六爻结果页、关于页均标注此说明，请优先参考原始判定依据。
3. 用户鉴权：预留 JWT 配置，但尚未接入账号系统，**请勿直接部署在公网**。
4. 缓存：Redis 缓存配置预留，暂未接入，全部计算实时执行。
5. 数据持久化：六爻完整断卦结果暂未入库；历史记录目前仅保存梅花易数起卦信息。
6. Docker：`docker-compose.yml` 已编写，但`Dockerfile.frontend`尚未创建，`docker-compose up`暂时无法拉起完整服务；优先使用本地开发方式运行。

## 文档清单

表格

| 文档 | 内容 |
| --- | --- |
| docs/ARCHITECTURE.md | 系统架构说明 |
| docs/ALGORITHM.md | 术数算法细节 |
| docs/DESIGN.md | 视觉设计规范 |
| docs/SETUP.md | 环境部署指南 |
| docs/CONTRIBUTING.md | 项目开发参与说明 |
| docs/ASSET_SPEC.md | 静态资源规范 |

> 
> 备注：文档初稿写于项目早期，部分模块划分、配色、Docker 部署步骤尚未同步至最新代码，**以 README 和源码为准**，正在持续校正。

## 开源许可

暂未选定开源协议。在确定许可前，本项目代码**禁止用于商业分发**。
