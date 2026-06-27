# 玄镜易系统架构设计文档

## 1. 系统概览

玄镜易是一个三层架构的易学命理解读系统。

## 2. 后端架构（The Brain）

### 2.1 核心模块

```
Backend
├── Divination Engine（占卜引擎）
├── Mapping Matrix（映射矩阵）
├── Analysis Engine（分析引擎）
└── Data Layer（数据层）
```

### 2.2 数据流

用户输入 → 数据验证 → 占卜算法 → 卦象生成 → 映射查询 → 分析计算 → JSON响应

### 2.3 API接口

POST /api/v1/divination/query

请求体：
```json
{
  "query_type": "梅花易数",
  "input_method": "时间",
  "timestamp": "2026-06-27T10:30:00Z",
  "query_topic": "事业"
}
```

## 3. 前端架构（The Face）

### 3.1 色彩体系

- 主色：#0F0E0E（深墨黑）
- 辅色：#1C3A47（墨青色）
- 强调色：#8B2323（深朱红）
- 文字：#E8E6E1（米白）

### 3.2 交互模式

加载动画：Idle → Loading → Processing → Complete

## 4. 数据结构

### 三层结构

1. 卦象层（The Raw Data）- 原始输入和卦象信息
2. 分析层（The Interpretation）- 数学解读和评分
3. 建议层（The Actionable Advice）- 可执行的行动建议
