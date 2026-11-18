# 实战示例

本层给出可以直接复制修改的操作路径。三篇均可独立完成，建议按序做。

| 序号 | 文档 | 你会得到 |
|---|---|---|
| 01 | [三协议最小可运行示例](01-quickstart-three-protocols.md) | curl / Python / JavaScript 各一份请求，以及响应里读缓存命中的位置 |
| 02 | [编码 Agent 接入](02-coding-agent-setup.md) | Claude Code（手动环境变量 + `hf-claude` 扩展）与 OpenCode 两套配置，含组织计费 |
| 03 | [策略选择与缓存粘滞演练](03-routing-policy-and-cache.md) | `X-HF-Session-Id` 用法、默认 vs `:cheapest` 的对照实验设计、旧用法迁移自查表 |

> 示例中的模型 id 与端点均取自官方文档；运行前请确认该模型当前仍被至少一家供应商服务（可用 `hf models ls --warm` 查询）。

```{toctree}
:hidden:
:maxdepth: 2

01-quickstart-three-protocols
02-coding-agent-setup
03-routing-policy-and-cache
```
