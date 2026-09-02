# CPython Bundle 变更日志

## 2026-09-02

**Migration**: 合并 learning 10/python314-cpython-wiki（语言特性/自由线程/JIT/新模块/标准库改进/源码架构/C API/构建平台/迁移指南/实战示例/FAQ/官方文档路线图 + 学习路径）；去重 learning-path.md（保留更完整的 python314-learning-path.md）；舍弃 seven-concepts-report.md 与 log.md；cheatsheet.html 随迁。（任务所述 04 源实测不存在，04 仅有 python314-stdlib-wiki，属另一批次）

**Migration**: 合并 learning 08/cpython-devguide-wiki（贡献者快速上手/开发工作流/治理与社区/最佳实践与反模式/FAQ 资源 6 章）。

## 2026-08-21 — 初始版本

- 基于 CPython 3.16.0a0（main 分支开发版）源码深度阅读生成
- 采用 source-code-to-okf-wiki 五阶段工作流（R→I→E→V→C）
- 覆盖 10 个概念文档 + 3 个示例文档 + 1 个信源登记文档
- 核心子系统覆盖：对象模型、类型系统、引用计数、内存分配、垃圾回收、解释器帧、字节码执行、编译器流水线、模块导入
