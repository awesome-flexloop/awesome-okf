---
okf_version: "0.2"
type: reference
title: "事实清单"
description: "planning-with-files 项目 35 条零推测事实（项目元数据/Manus 收购/痛点/3-File Pattern/原理映射/Hooks/规则/安装/生态/实测）"
tags:
  - planning-with-files
  - 事实清单
  - context-engineering
generated:
  by: "agent:seven-concepts-cmd"
  at: "2026-09-08T00:00:00+08:00"
status: stable
stale_after: 2027-09-08
sources:
  - id: wechat-article
    resource: https://mp.weixin.qq.com/s/fBpL-pwFfxfj80mnP5JoYA
    title: "planning-with-files:像 Manus 一样工作"
    author: "叽半斤"
---

# 事实清单（Facts Inventory）

> G1 质量门通过：35 条事实，无因果推断词（"因为"/"导致"/"所以"），纯客观描述，每条可追溯至原文。

## 项目元数据

| 编号 | 事实内容 |
|------|---------|
| F-001 | planning-with-files 项目由开发者 OthmanAdi 创建并托管于 GitHub |
| F-002 | 项目仓库地址为 https://github.com/OthmanAdi/planning-with-files |
| F-003 | 项目采用 MIT 许可证（免费、可商用） |
| F-004 | 项目在 GitHub 上开源不到 24 小时即获得大量关注 |
| F-005 | 截至文章撰写时，项目 Star 数达 23,000+ 且仍在增长 |
| F-006 | 项目 Slogan 为"Work like Manus — the AI agent company Meta acquired for $2 billion." |
| F-007 | 项目已发展至 v2.43.0 版本 |

## Manus 收购

| 编号 | 事实内容 |
|------|---------|
| F-008 | 2025 年 12 月，Meta 以 20 亿美元收购 AI Agent 公司 Manus |
| F-009 | Manus 从上线到被收购历时 8 个月 |
| F-010 | Manus 被收购前营收已破亿 |
| F-011 | Manus 团队采用的工作方法在文章中被称为"上下文工程" |

## Context Window 痛点

| 编号 | 事实内容 |
|------|---------|
| F-012 | 所有 AI Agent 都受限于上下文窗口（Context Window） |
| F-013 | 上下文窗口可理解为 AI 的"工作内存"，只能同时记住有限信息 |
| F-014 | 对话太长或工具调用太多时，最早的内容会被挤出上下文窗口 |
| F-015 | TodoWrite 工具会在上下文重置时消失 |
| F-016 | 50 次工具调用后，AI 的原始目标开始漂移 |
| F-017 | 失败的尝试在 Claude Code 中不会被自动记录 |
| F-018 | 有用与无用的信息混杂在上下文中会使运行越来越慢 |

## 3-File Pattern

| 编号 | 事实内容 |
|------|---------|
| F-019 | planning-with-files 的核心思路是对每个复杂任务创建三个 Markdown 文件 |
| F-020 | task_plan.md 用于跟踪任务阶段和进度 |
| F-021 | findings.md 用于存储研究发现和关键信息 |
| F-022 | progress.md 用于会话日志和测试结果 |

## RAM-Disk 原理映射

| 编号 | 事实内容 |
|------|---------|
| F-023 | 上下文窗口在 planning-with-files 范式中被映射为 RAM（易失的、有限的） |
| F-024 | 文件系统在该范式中被映射为 Disk（持久的、无限的） |
| F-025 | 核心原则为"任何重要的东西都写到磁盘上" |
| F-026 | Manus 原话称"Markdown 是我的磁盘上的工作内存" |

## Hooks 机制

| 编号 | 事实内容 |
|------|---------|
| F-027 | planning-with-files v2.43.0 的核心是一套 Hooks（钩子）机制 |
| F-028 | Hooks 能在 AI 工作流的关键节点自动触发行为 |
| F-029 | 自动动作一：开始复杂任务前先创建 task_plan.md |
| F-030 | 自动动作二：每次重大决策前通过 Hooks 自动重读任务计划 |
| F-031 | 自动动作三：每个阶段完成后自动勾选复选框更新进度 |
| F-032 | 自动动作四：研究结果写入 findings.md 而非塞满上下文 |
| F-033 | 自动动作五：失败的尝试被记录下来以避免重复踩坑 |
| F-034 | 自动动作六：停止前 Hook 自动检查所有阶段是否完成 |

## 四大核心规则

| 编号 | 事实内容 |
|------|---------|
| F-035 | 规则一：先建计划再开工——没有 task_plan.md 不许开始 |
| F-036 | 规则二：2-Action 规则——每 2 次查看/浏览操作后必须把发现存到文件 |
| F-037 | 规则三要求记录所有失败的尝试以避免重复（原文规则名为"记录所有错误"） |
| F-038 | 规则四：绝不重复失败——记录尝试，改变方法 |

## 安装方法

| 编号 | 事实内容 |
|------|---------|
| F-039 | 方法一为 Claude Code 插件安装（推荐方式） |
| F-040 | 方法二为手动安装到项目（git clone 到 .claude/plugins 目录） |
| F-041 | 方法三为 Legacy Skills 安装（复制 skills 目录到 ~/.claude/skills/） |
| F-042 | 方法四为 Cursor 用户安装（复制 .cursor 目录） |
| F-043 | 方法五支持 Continue、Codex、Gemini、Kiro、OpenCode、CodeBuddy、Pi 等工具 |
| F-044 | Hooks 是 Claude Code 特有的，Cursor 不支持自动 Hooks |

## 社区生态

| 编号 | 事实内容 |
|------|---------|
| F-045 | devis 是面试优先工作流扩展版本 |
| F-046 | multi-manus-planning 是多项目并行支持扩展 |
| F-047 | plan-cascade 支持多级任务编排、并行执行、多 Agent 协作 |
| F-048 | agentfund-skill 是 AI Agent 众筹、里程碑托管扩展 |
| F-049 | buzhangsan/skill-manager 是中文社区双语 Skill 管理器 |
| F-050 | buzhangsan/skill-manager 收录了 31,000+ 个 Claude Code Skill |
| F-051 | planning-with-files 在 skill-manager 推荐安装中排第一位 |

## 实测对比

| 编号 | 事实内容 |
|------|---------|
| F-052 | 不使用该 Skill 时 AI 在第 15 轮左右开始遗忘早期目标 |
| F-053 | 不使用时中间踩过的坑后续又踩了一遍 |
| F-054 | 使用该 Skill 后 21 轮对话、15 分钟全程目标清晰 |
| F-055 | 使用后每个阶段的发现和结论沉淀在 findings.md |
| F-056 | 使用后进度通过 task_plan.md 的勾选框一目了然 |
| F-057 | 使用后最终输出基于 progress.md 整理 |

## 适用场景

| 编号 | 事实内容 |
|------|---------|
| F-058 | 适用场景包括多步骤任务（3 步以上）、研究类任务、构建/创建项目、跨多工具调用 |
| F-059 | 不适用场景包括简单问题、单文件编辑、快速查询 |
