# 概念文档

本束的概念层按「事实 → 洞察 → 机制 → 治理 → 萃取」递进组织，对应七概念链路的 R/I/E 阶段产物。

| 文档 | 内容 |
|------|------|
| [00 · 身份、谱系与信源距离](00-identity-and-provenance.md) | 项目身份、Luckysheet 谱系、Apache-2.0、Star 时点勘误、信源距离 |
| [01 · 三 SDK 分层与授权边界（洞察层）](01-three-sdk-layers-and-license-boundary.md) | 洞察四元组：为什么"开源版够用"要加限定词；开源/商业分界表与选型三问 |
| [02 · 嵌入表格与 Facade API](02-embed-and-facade-api.md) | preset 嵌入、Facade 三层对象、Steady 生命周期、JSON 快照、Headless 同构 |
| [03 · 命令系统与插件架构](03-command-system-and-plugin-architecture.md) | Command/Mutation/Operation、撤销合成、changesets+OT、插件分层与扩展点 |
| [04 · AI agent 治理与生态](04-agent-governance-and-ecosystem.md) | 命令事件闸门、CLI/Worktree 审阅流程、五个生态集成、CLI 命令口径勘误 |
| [05 · 选型矩阵与三个可迁移模式（萃取层）](05-selection-and-transferable-patterns.md) | 选型对照 + P-1 授权边界前置 / P-2 命令层治理 / P-3 快照优先（含反模式与迁移验证） |

```{toctree}
:hidden:
:maxdepth: 2

00-identity-and-provenance
01-three-sdk-layers-and-license-boundary
02-embed-and-facade-api
03-command-system-and-plugin-architecture
04-agent-governance-and-ecosystem
05-selection-and-transferable-patterns
```
