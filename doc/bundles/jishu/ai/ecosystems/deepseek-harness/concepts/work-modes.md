---
type: concept
title: "四种工作模式"
description: "Harness 2.0 的四种模式（Standard/PTC/Minimal/Creator）定位与适用场景，以及 Automation 定时能力，附首次使用建议。"
tags: [DeepSeek, Harness, Standard, PTC, Minimal, Creator]
generated: { by: "process:seven-concepts-cmd+wechat-public-okf", at: "2026-10-10T00:00:00Z" }
status: draft
stale_after: 2026-12-05
sources:
  - id: wx-pjfnnu
    title: DeepSeek Harness 2.0 来了，Codex 该退休
    resource: https://mp.weixin.qq.com/s/PjfnnuDXPo6204CmDggIUw
---

# 四种工作模式

## 1. 模式总览

Harness 2.0 提供四种模式，覆盖从日常编码到插件开发的不同场景：[^wx-pjfnnu][F-010]

| 模式 | 用途 |
|------|------|
| **Standard** | 日常写代码 |
| **PTC** | 写 TS 编排工具 |
| **Minimal** | 极简实验 |
| **Creator** | 造插件 |

## 2. 各模式简述

### Standard（日常写代码）
默认的日常编码场景模式，用于常规的写代码任务。

### PTC（写 TS 编排工具）
面向 TypeScript 编排工具开发。注：原文仅指明用途，未展开技术细节，属单源信息。

### Minimal（极简实验）
轻量实验模式，用于不需要完整能力的简单尝试。

### Creator（造插件）
扩展模式：说一句"要个报告清单面板"，直接生成插件源码，装完**不重启就出现在侧边栏**，状态切走再回来仍在。[^wx-pjfnnu][F-013]

## 3. Automation（定时自动化）

除四种模式外，还支持定时自动化：90 秒后自动读数据、算出核实过的数字、写成文件。[^wx-pjfnnu][F-014]

## 4. 首次使用建议

> 建议第一次用，挑一个**你自己知道正确答案的项目**开始。[^wx-pjfnnu][F-016]

用已知答案的项目，才能判断 Harness 干的活对不对；同时避免在试错中空耗 Token。

[^wx-pjfnnu]: [DeepSeek Harness 2.0 来了，Codex 该退休](https://mp.weixin.qq.com/s/PjfnnuDXPo6204CmDggIUw)，有限进步Seven，2026-10-05。