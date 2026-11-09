# 实战示例

本目录的 3 篇示例均按「适用场景 → 前置条件 → 分步代码 → 预期结果 → 失败排查」组织，基于固定 commit `6bcb59a` 的源码阅读整理，**未在本机实跑**；输出只表示字段与格式形态，不构成运行结果承诺。

| 序号 | 示例 | 覆盖能力 | 前置概念 |
|---|---|---|---|
| 01 | [最小回声机器人](01-minimal-echo-bot.md) | 安装、凭据配置、建连认证、事件回调、回声回复 | [00 概览与快速开始](../concepts/00-overview.md) |
| 02 | [多阶段流式回复](02-streaming-reply.md) | 流式队列、增量帧、结束帧与模板卡片 | [03 流式回复与模板卡片](../concepts/03-streaming-and-card.md) |
| 03 | [模板卡片回复与文件下载解密](03-template-card-and-file-download.md) | 卡片回复、事件帧更新卡片、AES-256-CBC 解密落盘 | [03 流式回复与模板卡片](../concepts/03-streaming-and-card.md)、[04 文件下载与解密](../concepts/04-file-download-decrypt.md) |

建议顺序：先跑 01 建立可用的最小闭环，再读 02 理解流式时序；02、03 均假定 01 的连接与凭据已就绪，03 另需 `cryptography` 与卡片交互事件。

```{toctree}
:hidden:
:maxdepth: 7

01-minimal-echo-bot
02-streaming-reply
03-template-card-and-file-download
```