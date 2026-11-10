# 概念文档索引

本目录 10 篇概念文档，按“入门 → 核心 → 进阶 → 应用”排列。

```{toctree}
:hidden:
:maxdepth: 2

00-project-overview
01-architecture
02-session-model
03-http-protocol
04-deployments
05-runtimes-and-execution
06-configuration-and-extension
07-failure-modes-and-tests
08-source-map
09-agent-integration
```

| 文档 | 主题 | 关键事实 |
|---|---|---|
| [00 项目总览](00-project-overview.md) | 定位、谱系、规模、适用性 | F-001 ~ F-016 |
| [01 架构分层](01-architecture.md) | Deployment / Runtime / Server 职责 | F-017 ~ F-039 |
| [02 会话模型](02-session-model.md) | pexpect、PS1 哨兵、退出码 | F-041 ~ F-060 |
| [03 HTTP 协议](03-http-protocol.md) | 10 路由、认证、幂等、511 | F-047、F-064 ~ F-083 |
| [04 部署矩阵](04-deployments.md) | 7 种部署的生命周期 | F-019 ~ F-038 |
| [05 运行时与执行语义](05-runtimes-and-execution.md) | Local / Remote / Dummy | F-039 ~ F-071 |
| [06 配置与扩展](06-configuration-and-extension.md) | Pydantic 配置、from_config、hook | F-023 ~ F-038、F-071 |
| [07 失败模式与测试](07-failure-modes-and-tests.md) | 12 类异常、89 个用例 | F-084 ~ F-093、F-109 ~ F-114 |
| [08 源码地图](08-source-map.md) | 符号、调用链、扩展点 | F-001 ~ F-114 |
| [09 作为 Agent 执行后端](09-agent-integration.md) | 接入模式、工具映射、并行 | F-039 ~ F-068、F-094 ~ F-095 |
