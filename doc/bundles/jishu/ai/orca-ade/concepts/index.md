# 概念解析（Concepts）

本目录拆为事实层、机制层、生态适用层三篇，逐层回答"Orca 是什么、怎么运转、是否适合我"。

| 文档 | 主题 |
|------|------|
| [00-orca-overview.md](00-orca-overview.md) | Orca 定位与 ADE 口径边界、厂商 Stably AI（YC W22）、MIT 开源免费与账号双口径、星标与版本三方数字、平台与分发 |
| [01-fleet-worktree-mechanism.md](01-fleet-worktree-mechanism.md) | 一 prompt 扇出多 Agent、独立 git worktree 隔离与择优合并、终端分屏通知、Design Mode/diff 批注/任务直开 worktree、SSH 远程与移动端、Orca CLI |
| [02-ecosystem-and-fit.md](02-ecosystem-and-fit.md) | 支持 Agent 清单三处口径差异、不含模型复用订阅、五 Agent 即五份 token、适用/不适用决策表、同分组生态位对比与品类质疑 |

```{toctree}
:hidden:
:maxdepth: 1

00-orca-overview
01-fleet-worktree-mechanism
02-ecosystem-and-fit
```