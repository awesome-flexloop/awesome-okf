---
okf_version: "0.2"
type: Concept
title: "安装与触发：把它装进你的 AI 编程助手"
description: "ub-mode 的两条上手路径——官方三路径安装（grok/claude/cursor 技能目录 + /ub-mode 触发）与博文「上手三步」，以及检查工具需单独安装的断点"
tags: [ub-mode, 安装, 上手, claude-code, cursor, grok, skill-安装]
source: /references/article-source.md#F-031-F-032
status: draft
stale_after: 2027-01-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/vgwzE-3XGKN1VSjaIoZ_BA
  - id: github
    url: https://github.com/unclebob/ub-mode
  - id: skill-md
    url: https://raw.githubusercontent.com/unclebob/ub-mode/master/SKILL.md
---

# 安装与触发：把它装进你的 AI 编程助手

## 官方安装方式（权威源）

ub-mode 的安装本质上是**把 `SKILL.md` 复制进 agent 的技能目录**（F-031）。官方 README 给出了三条示例路径（F-031）——分别对应 Grok、Claude、Cursor：

| Agent | 目标路径 |
|-------|---------|
| Grok | `~/.grok/skills/ub-mode/SKILL.md` |
| Claude | `~/.claude/skills/ub-mode/SKILL.md` |
| Cursor | `~/.cursor/skills/ub-mode/SKILL.md` |

复制完成后，在会话中调用 `/ub-mode` 即可激活（F-031、F-014）。

> **注意**：官方只提供「复制 SKILL.md」这一种方式——**没有** `npm install`、**没有** 插件市场、**没有** 安装脚本。这与它的仓库形态完全一致：整个项目就是一篇文本（见 [项目定位](00-overview-and-philosophy.md)）。获取 `SKILL.md` 本身需先取得仓库副本（克隆或下载原文件）。

## 博文「上手三步」（单源表述）

博文给出的上手流程与官方路径一致，但只列了 Claude 一条路径（F-032）：

| 步 | 动作 | 编号 |
|---|------|------|
| ① | `mkdir -p ~/.claude/skills/ub-mode` 并 `cp SKILL.md ~/.claude/skills/ub-mode/SKILL.md` | F-032 |
| ② | 重启 AI 助手，输入 `/ub-mode` | F-032 |
| ③ | **安装三个检查工具** | F-032 |

> ⚠️ **第三步是断点**：博文要求安装三个检查工具（Crapper / Dryer / Mutator），但**没有给出任何安装方式**（F-034）。这意味着「照做」链路在第三步无法完成——这是本知识包不设 `examples/` 目录的直接原因（骨架判定两问之 Q2 为「否」）。

## ⚠️ 除非你手动接上，否则打分环节不可用

这是理解 ub-mode 使用体验的关键：

| 层次 | 是否随 ub-mode 一起提供 | 说明 |
|------|:---------------------:|------|
| **规则**（`SKILL.md` 三步机制） | ✅ 是 | 复制一个文件即可用 |
| **检查工具**（Crapper / Dryer / Mutator / uml-viewer） | ❌ 否 | 需**单独安装**（F-034） |

所以「第二步：修好还要检验」（F-017）在默认安装下**只能靠 AI 遵守文字规则完成，无法真正跑出分数**。要获得可打分的检查，须另行安装各 companion 工具（四个仓库见 [可打分的检查](02-scoreable-checks.md)）。

## 触发后会发生什么

激活 `/ub-mode` 后，AI 在每次代码改动时会按三步推进（F-014）：

1. **First Make it Work**——先写测试、做最小改动，让代码能跑；
2. **Then Make it Right**——按规则修根因，并用 Crapper / Dryer / Mutator 检查（工具已装时）；
3. **Practice**——记录改动（改了哪些文件、加了哪些测试、检查结果），并按官方规则提交与推送。

> ⚠️ 第 3 步中「自动提交并推送」是被博文作者标注为**保留意见**的一项（F-033）——官方 Practice 节要求 "Push to the main line at the end"，博文表示「不放心」。若你不希望 AI 自动推送到主分支，需自行调整或覆盖该条规则。详见 [边界、勘误与已知限制](04-boundaries-and-gotchas.md)。

## 与上一篇的衔接

检查工具的具体阈值、命令与产物见 [可打分的检查：Crapper、Dryer、Mutator 与 uml-viewer](02-scoreable-checks.md)。下一篇 [边界、勘误与已知限制](04-boundaries-and-gotchas.md) 汇总所有博文与官方源的口径差异与使用前的注意事项。

事实编号全集见 [博文与官方源事实清单](../references/article-source.md)，核验结论见 [P0 核验报告](../references/verification.md)。
