---
type: concept
title: "Harness 核心概念——模型外层执行壳"
description: "Harness（模型外面那层壳）的定义与职责边界（想/干分工）、运行位置、关键能力，以及“App 在本机≠模型在本地”的反直觉边界。"
tags: [DeepSeek, Harness, 执行壳, Agent]
generated: { by: "process:seven-concepts-cmd+wechat-public-okf", at: "2026-11-04T10:15:04+08:00" }
status: draft
stale_after: 2026-12-05
sources:
  - id: wx-pjfnnu
    title: DeepSeek Harness 2.0 来了，Codex 该退休
    resource: https://mp.weixin.qq.com/s/PjfnnuDXPo6204CmDggIUw
---

# Harness 核心概念：模型外层执行壳

本页保留 2026-10-05 文章的概念解读，本次仅补历史边界，不代表当前模型配置或计费契约；最新学习入口见[创造模式](creator-mode.md)。

## 1. 定义

> Harness 是模型外面那层壳。模型负责"想"，它负责"干"——读文件、改代码、跑命令、检查结果。少了这层，聊天的回答变不成电脑上的活。[^wx-pjfnnu][F-001]

- **模型**：负责思考、生成回答。
- **Harness**：位于模型外层的**执行壳**，把自然语言意图翻译成对文件系统、命令行、运行环境的实际操作。

## 2. 关键能力

- **文件操作**：读文件、改代码。
- **命令执行**：跑命令。
- **结果校验**：检查结果（运行测试、核对输出）。

## 3. 反直觉边界

> App 跑在你电脑上 **≠** 模型在本地跑。[^wx-pjfnnu][F-015]

- 旧文章描述本机执行、远端模型服务的使用方式，不代表所有配置都采用远端推理。
- 是否需要网络及如何计费，应核对实际模型端点；[定价页](pricing-model.md)只保留历史快照。

## 4. 一句话定位

Harness 的价值在"能干出活"——把模型的想法落地为真实电脑上的结果，而不是停留在对话。

[^wx-pjfnnu]: [DeepSeek Harness 2.0 来了，Codex 该退休](https://mp.weixin.qq.com/s/PjfnnuDXPo6204CmDggIUw)，有限进步Seven，2026-10-05。
