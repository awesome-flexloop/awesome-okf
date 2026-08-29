---
okf_version: "0.2"
title: "Agent Skills 开放标准与 skills-ref 参考实现"
description: "Agent Skills 开放标准的格式规范、创作/评估/优化方法学与 skills-ref 参考实现——6 字段 frontmatter 契约、渐进式披露三层加载、46 客户端生态、宽松与严格双校验策略。"
tags:
  - agent-skills
  - skill-format
  - open-standard
  - skills-ref
  - progressive-disclosure
  - anthropic
generated: { by: "process:source-code-to-okf-wiki R→I→E", at: "2026-08-29" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29" }
status: stable
stale_after: 2027-08-29
sources:
  - id: spec-mdx
    resource: /references/spec-sources.md
    title: docs/specification.mdx 权威格式规范
  - id: creation-mdx
    resource: /references/spec-sources.md
    title: docs/skill-creation/ 五篇创作指南
  - id: client-mdx
    resource: /references/spec-sources.md
    title: docs/client-implementation/adding-skills-support.mdx
  - id: skills-ref
    resource: /references/skills-ref-sources.md
    title: skills-ref 源码与测试信源登记
related:
  - "[[anthropics-skills]]"
---

# Agent Skills 开放标准与 skills-ref 参考实现

本知识束解析 **Agent Skills 开放标准**（agent-skills 仓库，最初由 Anthropic 开发的轻量级智能体能力扩展格式，已被 46 家客户端采纳）与官方 Python 参考实现 **skills-ref**。内容覆盖协议层三件事：格式规范（SKILL.md 目录格式、6 个 frontmatter 字段、渐进式披露三层加载契约）、创作与治理方法学（上下文经济学、gotchas/模板/checklist 等模式、eval 驱动迭代、description 防过拟合优化）、以及参考实现的架构样本（8 个公开 API、严格校验器与宽松客户端两种失败策略、CLI 三子命令）。

与同目录既有知识束 anthropics-skills 的分工：anthropics-skills 教你"用别人写好的技能"（资产层），本知识束教你"标准是什么、怎么写、怎么验、怎么集成"（协议层）——两者以 skill-creator 的引用为衔接点，互为上下游。

## 🧭 学习路径

```text
入门              核心                    高级
───────────    ───────────────────    ─────────────────────────────────
技能解剖    →    Frontmatter 字段    →   Eval 驱动迭代
（长什么样）      （逐字段约束）           （质量治理）
   │                │                      │
   ↓                ↓                      ↓
渐进式披露    →    创作原则            →   Description 优化
（为何这样组织）   （怎么写好）             （触发治理）
   │                │                      ↓
   └──────────────────────→   客户端集成 / skills-ref 参考实现
                              （生态如何消费 / 架构样本）
```

1. **入门**：[00 技能解剖](/concepts/00-skill-anatomy.md) 认识物理形态 → [01 渐进式披露](/concepts/01-progressive-disclosure.md) 理解组织原理；
2. **核心**：[02 Frontmatter 字段](/concepts/02-frontmatter-fields.md) 掌握格式契约 → [03 创作原则](/concepts/03-authoring-principles.md) 学会填充内容；
3. **高级**：[04 Eval 驱动迭代](/concepts/04-eval-driven-iteration.md) 与 [05 Description 优化](/concepts/05-description-optimization.md) 构成治理闭环 → [06 客户端集成](/concepts/06-client-integration.md) 与 [07 skills-ref](/concepts/07-skills-ref-reference-implementation.md) 面向实现者；
4. **动手**：[01 roll-dice 实战](/examples/01-first-skill-roll-dice.md) → [02 skills-ref CLI 实战](/examples/02-skills-ref-cli.md)。

## 🧩 概念导航（Concepts）

| 文件 | 标题 | 一句话 |
|---|---|---|
| [00-skill-anatomy](/concepts/00-skill-anatomy.md) | 技能解剖 | 一个含 SKILL.md 的目录 + 三个可选子目录的物理形态 |
| [01-progressive-disclosure](/concepts/01-progressive-disclosure.md) | 渐进式披露 | Metadata ~100 tokens → Instructions <5000 tokens → Resources 按需 |
| [02-frontmatter-fields](/concepts/02-frontmatter-fields.md) | Frontmatter 全字段规范 | 六字段规范约束 × validator 实现规则双栏对照 |
| [03-authoring-principles](/concepts/03-authoring-principles.md) | 创作原则 | add-what-agent-lacks、五种内容模式、脚本工程要点 |
| [04-eval-driven-iteration](/concepts/04-eval-driven-iteration.md) | Eval 驱动迭代 | 双臂对照、断言分级、benchmark delta、迭代闭环 |
| [05-description-optimization](/concepts/05-description-optimization.md) | Description 优化 | 触发率测量、near-miss 负例、60/40 防过拟合切分 |
| [06-client-integration](/concepts/06-client-integration.md) | 客户端集成 | 46 客户端、.agents/skills/ 惯例、宽松校验四规则、双激活路径 |
| [07-skills-ref-reference-implementation](/concepts/07-skills-ref-reference-implementation.md) | skills-ref 参考实现 | 8 个公开 API、两种错误风格分工、CLI 三子命令 |

## 🎯 示例导航（Examples）

| 文件 | 标题 | 一句话 |
|---|---|---|
| [01-first-skill-roll-dice](/examples/01-first-skill-roll-dice.md) | 创建第一个 Skill | quickstart 蓝本：从空目录到发现/激活/校验全流程 |
| [02-skills-ref-cli](/examples/02-skills-ref-cli.md) | skills-ref CLI 实战 | validate / read-properties / to-prompt 三子命令全流程 |

## 📚 参考导航（References）

| 文件 | 标题 | 一句话 |
|---|---|---|
| [spec-sources](/references/spec-sources.md) | 规范文档信源登记 | 12 个规范/指南信源逐文件登记与 F-xxx 追溯 |
| [skills-ref-sources](/references/skills-ref-sources.md) | skills-ref 源码信源登记 | 12 个源码/测试文件逐文件登记与 API 签名 |

## 📊 文档统计

| 目录 | 篇数 | 说明 |
|---|---|---|
| concepts/ | 8 | 按学习路径编号 00-07 |
| examples/ | 2 | 入门实战 + CLI 实战 |
| references/ | 2 | 双信源登记表 |
| 索引与日志 | 5 | 根 index + 3 个子目录 index + log |
| **合计** | **17** | 内容基于 68 条登记事实（F-001 ~ F-068） |

## 🔗 关联 Bundle

- [anthropics-skills](../anthropics-skills/index.md) — Anthropic 官方技能库（资产层，同目录既有知识束 `bundles/ai/ai-agent/anthropics-skills/`）：本束方法论对应的成品技能与 skill-creator 工具

---

> **信任声明**：本文档基于 `external/libs/ai/agentskills/agentskills/` 仓库（Agent Skills 开放标准官方仓库）的规范文档与 skills-ref 源码分析，经 source-code-to-okf-wiki 工作流 R→I→E 三阶段生成，全部技术断言可经 references/ 信源登记表追溯至 68 条登记事实。
>
> **生成时间**：2026-08-29 | **下次审查**：2027-08-29

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
log
```
