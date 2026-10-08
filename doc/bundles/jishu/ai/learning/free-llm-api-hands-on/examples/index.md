# 实战示例（examples/）

三篇可照做的平台接入演练，均以 2026-09-16 核验后的端点、参数与模型名单为准：

| 演练 | 平台 | 核心内容 | 关键坑 |
|---|---|---|---|
| [Agnes AI 接入演练](00-agnes-walkthrough.md) | Agnes | 注册拿 Key → WorkBuddy 配置 → 文本/文生图/异步文生视频全流程 → Agnes Code | 网关用现行 api.agnes-ai.cn；2.0 已废弃用 3.0；视频 size 仅 "720P" |
| [dots3 接入演练](01-dots3-walkthrough.md) | 小红书 dots3 | 注册 → api-key 头 curl → WorkBuddy 直连 → Trae 经 Bearer 通道 | api-key 非 Bearer；Trae 不能直连；OpenRouter 通道 9-30 关闭 |
| [AMD Token Factory 演练](02-amd-walkthrough.md) | AMD Radeon Cloud | 领 rc-Key → 核验日 5 款模型 → 双协议 curl → 多模态 → 积分制 | Vision-Exp 已下架、1B→2B；Anthropic 端点用 x-api-key；积分不是扣费 |

```{toctree}
:maxdepth: 1
:caption: 实战示例

00-agnes-walkthrough
01-dots3-walkthrough
02-amd-walkthrough
```
