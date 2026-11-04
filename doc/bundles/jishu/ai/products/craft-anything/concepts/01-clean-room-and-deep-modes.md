---
okf_version: "0.2"
type: Concept
title: "净室与深度两种模式：理解行为还是原样复刻"
description: "Craft Anything 的默认净室（Clean room）模式与深度（Deep）模式之别，以及强制工具白名单对安全边界的约束"
tags: [craft-anything, clean-room, deep-mode, tool-whitelist, safety]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-11-04T09:32:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-04T09:32:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: "https://mp.weixin.qq.com/s/wB4MHVC4hOWPMobtVidniA"
  - id: github-repo
    url: "https://github.com/storytold/craft-anything"
---

# 净室与深度两种模式：理解行为还是原样复刻

## 为什么会有"两种模式"

Craft Anything 的目标是"看懂他人软件、再造你自己的版本"。但"看懂"的程度可以有深浅：是**只观察外部行为后独立重写**，还是**更贴近原实现去探查与复刻**？项目用两种模式对应这两条路线（F-005）。

## 净室模式（Clean room，默认）

**净室**是项目的默认模式，也是官方对外定位里直接写明的那个词——README 称其为 "an open-source, **clean-room** engine"（F-025）。

净室模式的核心含义是：**先理解行为、再独立实现**，而不是直接搬运原站的设计与资产。对使用者而言，这意味着更清晰的法律与工程边界：产出物是"在你的观察基础上独立造出的版本"，而非原软件的拷贝。

> **口径提示**：官方公开材料明确确认的是"clean-room 引擎"这一取向（F-025）；博文所述"净室为默认模式"与其方向一致，但"默认为净室"的措辞属**博文单源**表述（见 [verification.md](../references/verification.md)）。

## 深度模式（Deep）

博文称项目另提供**深度（Deep）模式**（F-005），与默认净室模式相对——可理解为需要更深入探查目标实现的情形。

> **核验状态**：深度模式的存在与具体行为**仅博文单源**，官方 README / STATUS.md 未在本次核验中给出与之逐字对应的说明。使用该模式前建议以官方文档当前描述为准。

## 工具白名单：强制的安全边界

博文称项目中的**工具白名单是强制机制**（F-006）——即引擎在探查/构建过程中能被调用的工具受白名单约束，而非任意放行。

这与项目"可审计的工程流程"取向一致：把"AI 能做什么"收进显式清单，是让自动化复刻过程可控、可复现的前提。参见 [03 · 工具、四步工作流与运行时](03-tools-workflow-and-runtime.md) 中"每个工具既是 CLI 子命令又是 MCP 工具"的设计——白名单正是在这一工具面上生效。

> **核验状态**："工具白名单强制"**仅博文单源**（F-006），本次未获官方一手逐字确认。

## 模式选择速查

| 维度 | 净室（Clean room，默认） | 深度（Deep） |
|------|------------------------|--------------|
| 取向 | 观察外部行为后独立重写 | 更深入探查目标实现 |
| 官方确认度 | ✅ 官方定位明确为 clean-room 引擎（F-025） | ⚠️ 仅博文单源（F-005） |
| 适用直觉 | 想拥有"你自己的版本"、边界更清晰 | 需要更贴近原实现细节时 |

## 阅读下一篇

- [02 · 相似度检查机制](02-likeness-checking-method.md)：无论哪种模式，收敛判定都走同一套可量化检查。
- [04 · 安装与已知边界](04-install-and-known-limits.md)：早期 alpha 阶段两种模式的成熟度差异。
