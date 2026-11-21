# 概念文档

本层回答「它是什么、为什么这样设计、边界在哪」，四篇按「公告 → 接口 → 路由 → 计费与边界」递进。

| 序号 | 文档 | 覆盖内容 |
|---|---|---|
| 00 | [公告与切换边界](00-announcement-and-switch.md) | 2026-11-16 公告事实、切换前后行为对照、BYOK 破坏性变更、不经过 OpenRouter 的任务 |
| 01 | [三种 API 协议与鉴权](01-three-protocols-and-auth.md) | 三协议基址与端点、fine-grained token 权限、`X-HF-Bill-To` 组织计费 |
| 02 | [路由机制与策略后缀](02-routing-mechanism.md) | Routing Cost 六信号、策略后缀、故障转移、会话缓存粘滞、与 OpenRouter 原生 `provider` 对象对照 |
| 03 | [定价、可观测性与边界](03-pricing-observability-and-boundaries.md) | 无加价计费、月度 credits、Providers / Metrics 页签、用量拆分、供应商开关、时效边界 |

```{toctree}
:hidden:
:maxdepth: 2

00-announcement-and-switch
01-three-protocols-and-auth
02-routing-mechanism
03-pricing-observability-and-boundaries
```
