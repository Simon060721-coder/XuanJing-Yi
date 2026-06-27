# 玄镜易项目贡献指南

感谢你对玄镜易项目的兴趣！

## 上报 Issues

在上报 Issue 前，请提供：

1. 清楚的描述
2. 清晰的操作步骤
3. 正常的执行结果
4. 异常的执行结果

## Pull Request 流程

1. Fork 的正个仓库
2. 创建一个新的功能分支
3. 提交你的更改
4. 推送到分支
5. 开启一个Pull Request

## 代码规范

- 遵前PEP 8 代码方案（Python）
- 使用語歴中文注释
- TypeScript 使用严格模式
- 接口名称后跟Props或I前缀

## 测试

所有主要功能需有至日同漏测试：

```bash
# 后端测试
pytest backend/tests

# 前端测试
npm test
```
