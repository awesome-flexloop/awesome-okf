---
okf_version: "0.2"
type: bundle
title: "企业微信智能机器人 Python SDK（wecom-aibot-python-sdk）"
description: "企业微信智能机器人 Python SDK 源码教程——WebSocket 长连接与 bot_id/secret 认证、帧协议与事件分发、流式回复与模板卡片、媒体文件下载与 AES 解密；含 5 概念 + 3 示例 + 3 篇参考文档与 59 条编号事实（基线 commit 6bcb59a，打包 1.0.1 / 运行期 1.0.0）"
tags: [企业微信, WeCom, aibot, Python SDK, WebSocket, 智能机器人, 源码教程]
generated: { by: "okf-wiki/0.2", at: 2026-11-09 }
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - { id: S, resource: "vendor/WecomTeam/wecom-aibot-python-sdk/" }
---

# 企业微信智能机器人 Python SDK（wecom-aibot-python-sdk）

> **性质：源码教程（固定 commit `6bcb59a` 截面），非官方文档翻译。** 所有技术断言以该 commit 的工作树为准，逐条登记在[源码事实登记](references/facts.md)的 `F-001 ~ F-059`；推断性结论集中在[四元组洞察](references/insights.md)。
>
> **未在本机实跑：** 示例文档按源码阅读整理，命令与输出只表示字段与格式形态，不构成运行结果承诺。

## 这束知识包讲什么

在企业微信的三套接入形态中，`wecom-aibot-python-sdk` 负责**机器人通道**：开发者用 `bot_id` 与 `secret` 建立 WebSocket 长连接，接收事件帧并回发消息帧，支持流式回复、模板卡片与媒体文件下载解密。上游为 MIT 许可的纯 Python 包（要求 Python >= 3.8，打包版本 `1.0.1`、运行期 `__version__` 为 `1.0.0`），仓库共 19 个文件、对外导出 17 项能力。

与其他两束的分工：

| 束 | 覆盖 |
|---|---|
| 本束 | 机器人 WebSocket SDK：连接、帧协议、流式与卡片、媒体下载解密 |
| [wecom-cli](../wecom-cli/index.md) | 命令行工具：13 类业务服务、Rust workspace 与 npm 分发 |
| [wecom-unified](../wecom-unified/index.md) | 套件 Skill：统一入口、脚本工具链与文档域操作 |

## 文档导航

| 顺序 | 文档 | 读者要回答的问题 |
|---|---|---|
| 1 | [概览与快速开始](concepts/00-overview.md) | 它是什么、怎么装、最小骨架长什么样、与 CLI/Skill 的边界在哪？ |
| 2 | [连接生命周期](concepts/01-connection-lifecycle.md) | 如何建连、认证、心跳保活？断连后为何必须重跑一遍？ |
| 3 | [帧协议与事件分发](concepts/02-frame-protocol.md) | 帧长什么样、`req_id` 如何路由、事件帧为何也要 `msgtype`？ |
| 4 | [流式回复与模板卡片](concepts/03-streaming-and-card.md) | 100 条队列上限与 5 秒回执窗口如何影响延迟？ |
| 5 | [文件下载与解密](concepts/04-file-download-decrypt.md) | 媒体文件如何下载、AES 解密有哪些私有约定？ |
| 示例 | [最小回声机器人](examples/01-minimal-echo-bot.md) · [多阶段流式回复](examples/02-streaming-reply.md) · [模板卡片回复与文件下载解密](examples/03-template-card-and-file-download.md) | 最小可运行骨架、流式交互与卡片 + 附件链路 |
| 查证 | [源码事实登记](references/facts.md) · [四元组洞察](references/insights.md) · [信源登记](references/sources.md) | 每条说法的取值、行号、可复现命令与工程含义 |

> **状态**：`stable`。2026-11-09 通过 V 阶段独立复核（Grep 级实体核验 + F 编号一致性 + 结构/链接检查）。

## 已知边界

- **版本双口径**：打包元数据为 `1.0.1`，运行期 `__version__` 为 `1.0.0`，正文与事实登记均双写，不择一。
- **仅源码截面**：未做多版本比对，未验证官方文档与实现是否一致；上游若有新版本，需重新采集。
- **未实跑**：所有示例未经真实企业微信租户验证，凭据、回调地址与网络环境均需自行准备。

## 相关企业微信知识包

- [企业微信 5.0.10 版本说明](../wecom-5-0-10-release/index.md)
- [企业微信 5.0.12 版本说明](../wecom-5-0-12-release/index.md)
- [企业微信专题场景](../wecom-topic-scenarios/index.md)

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```