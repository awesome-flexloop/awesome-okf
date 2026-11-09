# 概念篇

本组文档从「它是什么」逐步下钻到「字节怎么解」，共 5 篇。建议按顺序阅读，因为后一篇会直接复用前一篇的概念：不理解 `req_id` 的前缀路由，就无法理解流式队列为何以 `req_id` 为键；不理解连接生命周期，就看不懂断连时待回执消息为何被清空。

## 推荐学习路径

1. **建立全局（约 10 分钟）**：读 [概览与快速开始](/concepts/00-overview.md)，确认定位、依赖与最小骨架，能回答「它和 wecom-cli / wecom-unified 各管什么」。
2. **理解连接（约 15 分钟）**：读 [连接生命周期](/concepts/01-connection-lifecycle.md)，掌握 connect → 认证 → 心跳 → 断连 → 重连的时序，记住「重连等于重跑一遍」。
3. **掌握协议（约 20 分钟）**：读 [帧协议与事件分发](/concepts/02-frame-protocol.md)，能手工构造一帧回复，并解释为什么事件帧也必须带 `msgtype`。
4. **深入交互（约 20 分钟）**：读 [流式回复与模板卡片](/concepts/03-streaming-and-card.md)，理解 100 条队列上限与 5 秒回执窗口对延迟的影响。
5. **按需查阅（约 15 分钟）**：读 [文件下载与解密](/concepts/04-file-download-decrypt.md)，掌握补零与 `pad_len ≤ 32` 两处私有约定。

## 文档索引

| 文档 | 核心问题 | 关键事实 | 前置 |
|---|---|---|---|
| [00 概览与快速开始](/concepts/00-overview.md) | 它是什么、怎么装、最小骨架 | F-003、F-006、F-055、F-057 | 无 |
| [01 连接生命周期](/concepts/01-connection-lifecycle.md) | 如何建连、认证、保活、重连 | F-020、F-024、F-025、F-027 | 00 |
| [02 帧协议与事件分发](/concepts/02-frame-protocol.md) | 帧长什么样、事件如何分发 | F-029 ~ F-032、F-047 ~ F-049 | 01 |
| [03 流式回复与模板卡片](/concepts/03-streaming-and-card.md) | 流式与卡片的时序与队列约束 | F-036 ~ F-046 | 01、02 |
| [04 文件下载与解密](/concepts/04-file-download-decrypt.md) | 媒体如何下载、解密、命名 | F-050 ~ F-054 | 01、02 |

## 阅读约定

- 所有 `F-0xx` 均指向 [源码事实登记](/references/facts.md)，可逐条核对行号与取证命令。
- 技术断言只来自固定 commit `6bcb59a` 的工作树；未标注依据的经验性建议不写入正文。
- 需要可运行的代码时，转到 [实战示例](/examples/index.md)；概念篇只保留解释性片段。

```{toctree}
:maxdepth: 2

00-overview
01-connection-lifecycle
02-frame-protocol
03-streaming-and-card
04-file-download-decrypt
```