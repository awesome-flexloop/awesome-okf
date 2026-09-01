# 变更日志

## 2026-08-28

- 基于 rust-lang/cargo master @ 75d17360928f57ff2a7d2f2da1c753f5fe1926d1（2026-08-26 采集）源码深度阅读生成
- 采用 source-code-to-okf-wiki 五阶段工作流（R→I→E→V→C）
- 覆盖 10 个概念文档 + 2 个示例文档 + 1 个信源登记文档，主覆盖事实 144 条（F-cargo-001~144，覆盖率 100%）
- 核心子系统覆盖：CLI 分发决策树、Workspace/Package 数据模型、GlobalContext 配置系统、依赖解析 resolver、五种包源、ops 命令业务、编译调度 unit 图、认证 credential 协议、util 基础设施
- 结构基线要点：主 crate 源码位于 `src/`（重组后布局）、`Config` 已更名 `GlobalContext`、SourceId/PackageId 位于 `src/workspace/`、版本双轨制（包 0.101.0 / CLI 1.100.0）
