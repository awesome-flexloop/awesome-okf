---
okf_version: "0.2"
type: Index
title: Textualize 生态 OKF 知识包
description: 基于 Textualize 组织 12 个源码仓库（rich/textual 及 7 个卫星工具）生成的 OKF Wiki，覆盖渲染协议、消息驱动 TUI、驱动抽象与 Web 化发布。
tags: [textualize, rich, textual, tui, terminal, okf]
generated:
  by: "agent:source-code-to-okf-wiki"
  at: "2026-09-01T00:00:00+08:00"
verified:
  by: "process:seven-concepts-v"
  at: "2026-09-01T00:00:00+08:00"
status: stable
stale_after: "2027-09-01"
sources:
  - id: rich
    resource: /references/rich.md
    title: "Rich 仓库信源登记"
  - id: textual
    resource: /references/textual.md
    title: "Textual 仓库信源登记"
  - id: frogmouth
    resource: /references/frogmouth.md
    title: "Frogmouth 仓库信源登记"
  - id: toolong
    resource: /references/toolong.md
    title: "Toolong 仓库信源登记"
  - id: trogon
    resource: /references/trogon.md
    title: "Trogon 仓库信源登记"
  - id: rich-cli
    resource: /references/rich-cli.md
    title: "Rich CLI 仓库信源登记"
  - id: textual-dev
    resource: /references/textual-dev.md
    title: "Textual Dev 仓库信源登记"
  - id: textual-serve
    resource: /references/textual-serve.md
    title: "Textual Serve 仓库信源登记"
  - id: textual-web
    resource: /references/textual-web.md
    title: "Textual Web 仓库信源登记"
  - id: textual-demo
    resource: /references/textual-demo.md
    title: "Textual Demo 仓库信源登记"
  - id: textual-key-recorder
    resource: /references/textual-key-recorder.md
    title: "Textual Key Recorder 仓库信源登记"
  - id: github-org
    resource: /references/github-org.md
    title: "GitHub 组织元仓库信源登记"
---

# Textualize 生态 OKF 知识包

本知识包以 Textualize 开源组织 12 个源码仓库为信源，讲解从 **rich** 终端富文本渲染库、**textual** TUI 框架，到 7 个卫星工具（rich-cli / frogmouth / toolong / trogon / textual-dev / textual-serve / textual-web）的完整生态。

内容基于编号事实（`F-xxx`）逐条采集、无虚构 API，覆盖渲染协议、消息驱动模型、CSS/Worker/Driver 三大基础设施，以及 TUI 变 Web 应用的驱动替换机制。

## 核心洞察

1. **rich 是"协议驱动的递归归约"**——一切皆 renderable，终点是扁平 Segment 流。
2. **textual = rich 渲染核 + 异步消息泵**——DOM 树本质是"每个节点一台消息泵"的 actor 树。
3. **约定即注册**——`__init_subclass__` 元编程贯穿 textual，类定义本身就是接线。
4. **TUI 变 Web 靠"换驱动 + 二进制管道协议"**，应用代码零改动。
5. **12 个仓库是一个分形**——卫星工具全部复用 rich/textual 原语，且自身就是教学材料。

## 文档导航

### [概念文档 Concepts](concepts/index.md)

按学习路径排列的 27 篇核心概念（生态总览 + rich 12 篇 + textual 7 篇 + 卫星 7 篇）：

| 阶段 | 文档 | 说明 |
|------|------|------|
| 入门 | [00-生态总览](concepts/00-ecosystem-overview.md) → [01-渲染协议](concepts/01-rich-console-and-protocol.md) → [02-Text 与 markup](concepts/02-rich-text-and-markup.md) | 建立生态方位感 + 第一次 rich 输出 |
| rich 核心 | [03-12](concepts/index.md) | Style/高亮/Segment/Table/Panel/Markdown/Progress/Live/Layout/渲染管线 |
| textual 核心 | [13-19](concepts/index.md) | App/消息系统/Reactive/DOM/事件/Screen/CSS-Worker-Driver |
| 卫星工具 | [20-26](concepts/index.md) | 每仓库 1 篇，含"复用的原语 + 独有机制"双节 |

### [示例文档 Examples](examples/index.md)

11 篇可直接运行的示例，覆盖 rich 渲染与 textual TUI 应用及卫星工具接入。

### [信源 References](references/index.md)

12 个仓库的信源登记（含 commit hash 固定快照），全部事实可回溯。

## 来源与验证

- 信源快照：12 个仓库 commit hash 已固定（见 [references/index.md](references/index.md)）
- 事实采集：377 条 `F-xxx` 事实，来源为源码 `external/dao/action/Textualize/<repo>/`
- 验证流程：Grep 级 API 真实性 + 计数断言 + toctree/链接完整性

## 更新日志

完整变更记录见 [log.md](log.md)。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```