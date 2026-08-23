# pandas Bundle 变更日志

## 2026-08-22 — 初始版本

- 基于 pandas 源码（`external/libs/python/pandas/pandas/` 目录）核心模块深度阅读生成
- 覆盖 4 个概念文档 + 1 个示例文档 + 1 个信源登记文档
- 核心子系统覆盖：核心初始化与API导出、DataFrame数据模型(BlockManager)、Series与Index体系、GroupBy split-apply-combine机制
- 所有类名、方法名均通过源码Grep验证
