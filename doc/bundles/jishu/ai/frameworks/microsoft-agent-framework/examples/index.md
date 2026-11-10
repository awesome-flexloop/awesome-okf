# 实战示例

本目录收录 6 个示例：5 个可演练示例 + 1 个源码阅读路径，均从官方文档片段做最小化改写，用于验证环境与理解关键 API。命令、包名与代码结构以 2026-10 文档为准；运行前请替换模型部署名与终结点。

| 示例 | 目标 | 关键能力 |
|------|------|---------|
| [00 Hello Agent](00-hello-agent.md) | 跑通第一个代理与多轮会话 | 安装、凭据、`run`、`AgentSession` |
| [01 函数工具与审批](01-tool-and-approval.md) | 区分只读与写入工具 | `@tool`、`approval_mode`、参数校验 |
| [02 Harness 与会话](02-harness-session.md) | 用 Harness 做长任务 | `create_harness_agent`、会话复用、压缩预算 |
| [03 工作流与检查点](03-workflow-checkpoint.md) | 图工作流、检查点、HITL | `WorkflowBuilder`、`CheckpointStorage`、`request_info` |
| [04 托管与 Handoff](04-hosted-and-handoff.md) | 上线与多代理分诊 | Foundry Hosting、`HandoffBuilder` |
| [05 源码阅读路径](05-source-reading-map.md) | 用检索命令走通请求链 | `Agent.run`、middleware、SessionContext、CheckpointStorage |

## 示例使用约定

1. 所有示例都需要一个可用的模型部署；本文不提供共享凭据。
2. 示例中的 `client` 变量指向已配置的模型客户端；完整构造见 00 示例。
3. 生产使用前，把 `approval_mode` 从 `never_require` 改为 `always_require`，并接入审计。
4. 示例代码不是官方原文，版本升级后请对照最新文档。

```{toctree}
:hidden:
:maxdepth: 2

00-hello-agent
01-tool-and-approval
02-harness-session
03-workflow-checkpoint
04-hosted-and-handoff
05-source-reading-map
```
