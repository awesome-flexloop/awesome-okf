---
okf_version: "0.2"
type: bundle
title: "WiFiT3：跨平台 WiFi 安全审计工具"
description: "基于一篇公开公众号文章与官方仓库的 WiFiT3 原创教程与事实索引"
tags: [wifi, security, audit, networking, single-source]
status: draft
stale_after: 2027-10-07
generated:
  by: process:seven-concepts-wifit3-okf
  at: 2026-10-10T12:00:00Z
sources:
  - id: src-001
    resource: https://mp.weixin.qq.com/s/ufDnlN7grRoYzNT5LxY26A
    title: "kali笔记：离了大谱! 这款WiFi工具太强了"
  - id: src-002
    resource: https://github.com/derv82/wifit3
    title: "derv82/wifit3 - A standalone USB Wi-Fi auditor"
---

# WiFiT3：跨平台 WiFi 安全审计工具

本 bundle 将一篇公开公众号文章（`kali笔记`）关于 **WiFiT3** 工具的介绍转化为原创教程与事实索引，并以官方 GitHub 仓库（`derv82/wifit3`）作为独立核验信源。文章中的工具评价属于作者观点；工具能力与特性以官方仓库实测/文档为准分层呈现。

> **合法使用边界**：WiFiT3 官方声明仅用于**自有机或经明确授权审计**的网络与设备。本教程仅用于安全审计学习与研究，不鼓励未经授权的访问行为。

## 内容边界

- 收录范围：已核验的公开文章 `SRC-001` 与公开仓库 `SRC-002`。
- 不收录：文章全文镜像、需登录或受限内容、非公开附件。
- 信源状态：文章归属已核验（kali笔记公众号 2026-10-07 发布）；工具特性以官方仓库为准（该束上线时仓库 version v0.3.3 BETA，供核验锚定）。
- 单源边界：文章对工具的"推荐/评价"为作者观点，非工具能力的确凿证据；能力描述优先挂官方 README（`SRC-002`）。

## 教程导航

- [WiFiT3 原创教程](concepts/wifit3-audit-tool-guide.md)：前期侦察、密码找回与快速上手的原创改写教程。

```{toctree}
:hidden:
:maxdepth: 3

concepts/wifit3-audit-tool-guide
references/facts-and-source-index
log
```