# 玄镜易设计规范

> 本文档描述**当前实现**，不是设想。所有色值、字体、断点均与代码一一对应。
> 最后核对：与 `frontend/src/index.css`、`frontend/tailwind.config.js` 同步。

---

## 一、设计原则

1. **克制的用色**：全站只有「墨底 + 暗金 + 朱砂 + 青玉 + 三级文字」五组颜色，不引入体系外的颜色。
2. **令牌先行**：任何色值只在 `src/index.css` 定义一次，组件只引用令牌类名，不写字面色值。
3. **古风在字体，不在装饰**：气质由楷体标题与松紧得当的留白承担，不靠花纹与浮雕堆砌。
4. **动效服务于叙事**：卦象生成的等待感、结果逐层展开，用动效表达「推演」的节奏。

---

## 二、色彩体系（玄墨金）

冷黑墨底配暗金强调，取故宫拓片与线装书的质感。

### 2.1 令牌表

| 令牌 | 类名示例 | 色值 | 用途 |
|------|----------|------|------|
| `--xj-ink` | `bg-xuanjing-ink` | `#0E0F12` | 主背景 |
| `--xj-ink-2` | `bg-xuanjing-ink-2` | `#14161B` | 导航栏、页脚 |
| `--xj-ink-3` | `bg-xuanjing-ink-3/60` | `#1C1E24` | 输入框、内凹面 |
| `--xj-ink-deep` | — | `#0B0C0F` | 背景渐变收尾（仅 CSS） |
| `--xj-gold` | `bg-xuanjing-gold` | `#C6A567` | 强调：主按钮底色、标题、当前导航项 |
| `--xj-gold-bright` | `hover:bg-xuanjing-gold-bright` | `#D8BC85` | 悬停态 |
| `--xj-gold-deep` | `text-xuanjing-gold-deep` | `#967644` | 弱强调、副标题 |
| `--xj-cinnabar` | `bg-xuanjing-cinnabar/15` | `#9E3B32` | 朱砂**填充**：警示底色、凶标签底 |
| `--xj-cinnabar-text` | `text-xuanjing-cinnabar-text` | `#C8604E` | 朱砂**文字**：错误、凶、下降趋势 |
| `--xj-jade` | `text-xuanjing-jade` | `#6E9E82` | 青玉：吉 |
| `--xj-jade-bright` | `text-xuanjing-jade-bright` | `#8FBF9F` | 青玉亮：大吉 |
| `--xj-paper` | `text-xuanjing-paper` | `#ECE7DD` | 主文字 |
| `--xj-paper-dim` | `text-xuanjing-paper-dim` | `#A5A099` | 次文字：正文说明 |
| `--xj-paper-faint` | `text-xuanjing-paper-faint` | `#8A857E` | 弱文字：提示、placeholder |
| `--xj-line` | `border-xuanjing-line` | `#26272D` | 描边 |

### 2.2 使用规则

- **朱砂分填充与文字两档**。`#9E3B32` 在深底上作为文字只有约 2.9:1，不可读，因此文字一律用 `cinnabar-text`。
- **按钮**：金底配 `text-xuanjing-ink`（深色文字），对比度 8.19:1。不要用米白字配金底。
- **吉凶五档**（`DivinationResult` / `HistoryPage` 共用同一映射）：

  | 评级 | 颜色 |
  |------|------|
  | 大吉 | `jade-bright` |
  | 吉 | `jade` |
  | 平吉 | `jade/80` |
  | 平 | `gold` |
  | 凶 | `cinnabar-text` |

### 2.3 对比度实测（WCAG 2.1）

| 组合 | 比值 | 等级 |
|------|------|------|
| 主文字 / 主背景 | 15.55:1 | AAA |
| 次文字 / 主背景 | 7.38:1 | AAA |
| 弱文字 / 主背景 | 5.24:1 | AA |
| 弱文字 / 输入框面 | 4.55:1 | AA |
| 强调金 / 主背景 | 8.19:1 | AAA |
| 强调金 / 导航底 | 7.74:1 | AAA |
| 大吉 / 主背景 | 9.24:1 | AAA |
| 吉 / 主背景 | 6.28:1 | AA |
| 凶（文字档）/ 主背景 | 4.78:1 | AA |
| 按钮文字 / 按钮金底 | 8.19:1 | AAA |

全部文字组合均达到 AA（小字 4.5:1）。弱文字原先为 `#6E6A64`（3.57:1，不达标），已上调为 `#8A857E`。

---

## 三、字体与排版

### 3.1 字体栈

**纯系统字体，不依赖外网**，离线可用，回退链同时覆盖 Windows 与 macOS。

```
标题 font-heading:
  STKaiti → KaiTi → 华文楷体 → 楷体 → Songti SC → STSong
  → STZhongsong → 华文中宋 → SimSun → 宋体 → serif

正文 font-body:
  PingFang SC → Microsoft YaHei → 微软雅黑 → Hiragino Sans GB
  → Heiti SC → SimHei → 黑体 → sans-serif

等宽 font-mono:
  Fira Code → Consolas → Monaco → monospace
```

**为什么是楷体做标题**：楷体保留手书笔意，在「玄镜易」这类大字上呈现典籍气质；正文则用无衬线中文，长段解读更易读。

> 注意：此前配置写的是 `Noto Serif SC` / `Noto Sans SC`，但项目从未加载任何字体文件，而目标机器多数也未安装 Noto，导致标题实际回落到 SimSun、正文回落到系统默认无衬线——**古风排版并未生效**。现已改为真实存在的字体栈。

### 3.2 字号层级

| 场景 | 类名 | 使用位置 |
|------|------|----------|
| 首页主标 | `text-6xl md:text-7xl` | HomePage |
| 页面标题 | `text-5xl` / `text-5xl md:text-6xl` | 占卜页、历史页、关于页 |
| 区块标题 | `text-2xl` | 表单、关于页分节 |
| 卡片小标题 | `text-lg` | 首页三特征卡 |
| 正文 | `text-sm` ~ `text-lg` | 解读文案、说明 |
| 辅助 | `text-xs` | 提示、时间戳、关键词 |

### 3.3 间距

- 内容块之间 `mb-4` ~ `mb-8`（16–32px）。
- 卡片内边距：`p-6`（24px，结果卡）／`p-8`（32px，表单与关于页）。
- 列表项间距 `space-y-4`。
- 页面容器 `.content`：`max-width: 1200px`，内边距随断点收缩（见第六节）。

---

## 四、玻璃拟态

全站只有一处定义，位于 `src/index.css` 的 `.glass-card` / `.glass-panel`。

```css
background: rgba(255, 255, 255, 0.045);
border: 1px solid rgba(255, 255, 255, 0.1);
backdrop-filter: blur(20px);
box-shadow: 0 24px 70px rgba(0, 0, 0, 0.45);
```

- `.glass-card`：圆角 28px，用于区块容器、表单、结果卡。
- `.glass-panel`：圆角 22px。
- 玻璃层需要真实透明度，因此这几项保留 `rgba`，不转为令牌通道值。

---

## 五、交互与动效

基于 Framer Motion。

| 场景 | 参数 |
|------|------|
| 首页入场 | 容器 `staggerChildren: 0.2`、`delayChildren: 0.3`；子项 `y: 20 → 0`，`0.8s easeOut` |
| 页面标题入场 | `opacity 0 → 1`、`y: 20 → 0`，`0.6s` |
| 结果分层展开 | 四层各延迟 `0.1 / 0.2 / 0.3 / 0.4s`，配 `scale 0.95 → 1` |
| 维度条目 | 左右交替入场（`x: ±10 → 0`），每条延迟 `+0.08s` |
| 进度条 | 宽度 `0 → score%`，`0.6s easeOut` |
| 加载态 | `opacity [0.75, 1, 0.75]` 循环 2s，表达「卦象生成中」 |
| 历史卡展开 | 高度 `0 → auto`，`0.3s` |

**焦点可见性**：`index.css` 中全局 `:focus-visible` 提供暗金描边（`rgb(var(--xj-gold) / 0.7)`，offset 2px）；表单控件另加 `focus:ring-2 ring-xuanjing-gold/25`。

---

## 六、响应式

### 断点

| 设备 | 宽度 | 主要变化 |
|------|------|----------|
| 手机 | < 768px | 导航折叠为汉堡菜单；占卜页单列；`.content` 内边距 16px |
| 平板 | 768 – 1023px | 导航展开（`md:flex`）；内容仍为单列 |
| 桌面 | ≥ 1024px | 占卜页双列（`lg:grid-cols-2`）；`.content` 内边距 40px |

最小支持宽度 320px。

### 实现方式

- 布局用 Tailwind 断点（`md:` = 768px，`lg:` = 1024px）。
- `.content` 的容器内边距用 `App.css` 媒体查询：1024px / 768px / 480px 三档收缩。

---

## 七、令牌维护规则

1. **改配色只改 `src/index.css` 的 `:root` 区块**。Tailwind 配置通过
   `rgb(var(--xj-*) / <alpha-value>)` 读取这些变量，因此 `bg-xuanjing-gold/20`
   这类透明度写法依然有效。
2. **组件禁止出现字面色值**。不写 `#C6A567`、不写 `rgba(...)`、不使用
   `emerald-400` / `amber-400` / `white/10` 等体系外颜色。
3. **不要用内联 `style` 传颜色**，也不要靠 `onMouseEnter` 手写悬停——用
   `hover:` 变体类。
4. 新增颜色前先确认现有五组颜色是否够用。

### 自查命令

```bash
# 旧令牌残留（应为空）
grep -rE "xuanjing-(black|cream|gray-light|cyan|red|wood|tea|accent)" frontend/src

# 硬编码色值与体系外颜色（应为空）
grep -rE "#[0-9a-fA-F]{3,8}\b|rgba?\(" frontend/src --include=*.tsx
grep -rE "(emerald|amber|red|zinc|slate)-[0-9]{2,3}|text-white|bg-white" frontend/src
```

---

## 八、变更记录

### 本次调整（玄墨金）

- **配色换代为玄墨金**：原 `DESIGN.md` 记载的「深墨黑 `#0F0E0E` / 墨青 `#1C3A47` / 深朱红 `#8B2323` / 米白 `#E8E6E1` / 浅灰 `#9E9C98`」从未在代码中实现（代码实际是另一套木质棕褐系 `#2B1C16` / `#936142`）。文档与代码长期互相矛盾，现统一为单一方案。
- **消除双套主题系统**：原先 `index.css` 定义了 `--color-*` 变量但组件全部直接用 Tailwind 硬编码类名，改变量毫无效果。现在 CSS 变量成为唯一来源，Tailwind 反向读取。
- **接入真实字体**：配置里的 Noto 字体从未加载且本机不存在，改为系统字体栈。
- **清除硬编码色值**：`Header` 的 `#936142`、`DivinationResult` 的 `onMouseEnter` 换色、`HistoryPage` 的 `#f87171` 等全部令牌化。
- **修复失效类名**：页脚 `text-xuanjing-text-muted` 在配置中不存在，该样式一直静默失效。
- **补齐 favicon**：原先指向不存在的 `/vite.svg`（404），现为 `public/favicon.svg`（暗金圆环 + 乾卦三爻）。
- **无障碍**：弱文字由 3.57:1 提升至 5.24:1；按钮改用深色文字配金底（8.19:1）；新增全局 `:focus-visible` 焦点环。
- **按钮对比修正**：原先金底 `#936142` 配米白字 `#F5E7D0` 为 4.27:1，低于 AA 小字标准 4.5:1；现改为金底 `#C6A567` 配墨色字 `#0E0F12`，8.19:1。
