# Changelog

## 2026-08-23

- 初始版本，基于 langchain-ai/helm 仓库源码生成（参考型 bundle）
- R 阶段：完成 85 条源码事实采集（F-001~F-085），覆盖仓库元数据、5 个 Chart 版本信息、模板结构、values 配置、CI/CD、命名约定、探针模式
- I 阶段：提炼 4 个架构洞察（五 Chart 分层矩阵、内置/外部双模式、三入口互斥、文档即代码流水线）
- E 阶段：生成 1 篇信源登记文档（Helm Chart 结构索引），不包含 concepts/ 和 examples/
- 覆盖 Chart：langgraph-cloud 0.3.2、langgraph-dataplane 0.2.22、langsmith 0.17.0-rc.12、langsmith-auth-proxy 0.0.11、langsmith-observability 0.2.0（deprecated）
