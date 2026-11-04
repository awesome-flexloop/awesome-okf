---
okf_version: "0.2"
type: Concept
title: "ub-mode 是什么：定位、作者与极轻量仓库"
description: "ub-mode 的项目定位（agent skill）、作者 Robert C. Martin、上游溯源、仓库形态与博文语境——回答「它是什么、谁做的、为什么只有几个文件」"
tags: [ub-mode, agent-skill, unclebob, clean-code, 项目定位]
source: /references/article-source.md#F-001-F-014
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

# ub-mode 是什么：定位、作者与极轻量仓库

## 一句话定位

**ub-mode 是一个 agent skill（智能体技能）**，不是一个独立应用、不是一个网站、也不是一个可安装的框架。它做的事情只有一件：**在 AI 编程助手编写或修改代码时，强制施加一套有纪律的软件工程原则**（F-012）。事实出处见 [博文与官方源事实清单](../references/article-source.md)，下文以 `F-xxx` 标注编号。

它的官方自述是：编写或修改代码时，强制执行有纪律的软件工程原则（F-012）。触发时机有两种——用户显式执行 `/ub-mode`，或者要求使用 "the reduced principles"（精简原则）（F-014）。

> **为什么这个定位重要？** 因为它决定了 ub-mode 的交付形态：**没有代码、没有安装包、没有依赖**。整个仓库就是一篇写给 AI 读的规则文档。所有效果都通过「把规则放进 agent 的技能目录」这一件事实现（见 [安装与触发](03-install-and-usage.md)）。

## 作者与上游溯源

| 项 | 事实 | 编号 |
|----|------|------|
| 作者 | Robert C. Martin（GitHub 登录名 `unclebob`，即《Clean Code》作者） | F-036、F-004 |
| 许可证 | MIT License | F-009 |
| 著作权署名 | `Copyright (c) 2026 Robert C. Martin` | F-009 |
| 上游溯源 | README 声明「loosely based on portions of @poteto's rules（`poteto-mode` / `pstack`）」 | F-013 |
| 仓库地址 | `https://github.com/unclebob/ub-mode` | F-003 |

⚠️ **博文未提及上游溯源**（F-013）：ub-mode 是在 @poteto 的 `poteto-mode` / `pstack` 规则基础上松散衍生的。引用时若只写「unclebob 原创」，会遗漏这段谱系。

## 仓库形态：极轻量到近乎「一篇文档」

这是文章标题「只有一个 Skill 的仓库」的事实基础：

| 项 | 事实 | 编号 |
|----|------|------|
| 文件数 | **3 个**文本文件：`LICENSE`（1,073 B）、`README.md`（2,195 B）、`SKILL.md`（3,958 B），合计 7,226 B | F-008 |
| 语言统计 | GitHub API `language` 字段为 `null`——仓库内**无可执行代码** | F-007 |
| 默认分支 | **`master`**（不是 `main`） | F-006 |
| 创建时间 | `2026-10-25T16:04:09Z`；最后代码推送同日 `16:07:59Z` | F-005 |
| 版本状态 | **无 Release、无 tag**，自初始推送后未再改动 | F-037 |
| Star | 博文发文时点（2026-10-28）口径 **2,900**；核验时点（2026-11-04）API 为 **3,951** | F-010 |
| 其他动态数据 | `forks` 214、`open_issues` 5、`subscribers` 24（核验时点） | F-011 |

> ⚠️ **两个易踩坑的细节**：
> 1. **默认分支是 `master`**（F-006）——按 `main` 拼 `raw.githubusercontent.com` 路径会 404，这是本次核验中实际踩到的坑；
> 2. **Star 是动态数字**（F-010）——文章标题的「2900」是发文时点口径，引用时须重新取数，不要当作稳定事实（详见[勘误 E-3](../references/verification.md)）。

## 博文语境：它要解决什么问题

公众号「开源日记」2026-10-28 的博文《只有一个 Skill 的仓库，竟然斩获 2900 Star！》（署名作者「熊叔」）（F-001、F-002）描述的痛点，是 ub-mode 的存在理由：

> 「AI 编程助手**写规则越写越不听话**」——作者观点（F-015）

这类现象的常见形态是：给 AI 写了长长的规则文件（CLAUDE.md / rules 等），初期有效，但随着规则堆积、上下文被稀释，AI 逐渐「忘记」或选择性忽略规则。ub-mode 的应对思路不是再写更多规则，而是**把规则压缩成一条可执行、可打分的短链路**——先让代码能跑（Make it Work），再让代码变好（Make it Right），最后要求说明改了什么（Practice）。

这一「三步机制」及其详细内容见 [三步机制](01-three-step-mechanism.md)。

## 与其他知识包的关系

- [三步机制：Make it Work → Make it Right → Practice](01-three-step-mechanism.md)——本文回答「是什么」，下一篇回答「怎么运作」；
- [可打分的检查：Crapper / Dryer / Mutator（+ uml-viewer）](02-scoreable-checks.md)——规则如何被量化验证；
- [安装与触发](03-install-and-usage.md)——如何把它装进你的助手；
- [边界、勘误与已知限制](04-boundaries-and-gotchas.md)——哪些说法经过核验、哪些只是博文单源。

事实编号全集见 [博文与官方源事实清单](../references/article-source.md)，核验结论见 [P0 核验报告](../references/verification.md)。
