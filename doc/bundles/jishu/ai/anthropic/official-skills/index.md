---
okf_version: "0.2"
type: index
title: "Anthropic 官方 Skills 库 Wiki"
description: "Anthropic官方Skills库中文文档——19个官方Skills索引、SKILL.md格式规范、skill-creator元技能详解、claude-api多语言API参考、文档处理/设计/开发/沟通类Skills分类导航。"
tags: [skills, claude-code, skill-creator, claude-api, docx, pdf, pptx, xlsx, frontend-design, mcp]
generated: { by: "process:content-structuring", at: "2026-08-27" }
status: stable
stale_after: 2027-08-27
---

# Anthropic 官方 Skills 库 Wiki

**Skills（技能包）** 是 Claude Code 和 Claude Agent 生态中的可复用能力包，通过标准化的 `SKILL.md` 文件封装特定领域的专业知识、工作流程和工具集。Skills 由 AI 代理根据用户请求语义**自动触发**，无需用户显式调用，就能在合适的场景下注入专业能力。

Anthropic 官方提供了 **19 个开箱即用的 Skills**，覆盖 API 开发、文档处理、设计创意、沟通写作四大类场景。本 bundle 是这些官方 Skills 的中文文档索引和使用指南。

## Skills 核心概念

| 特性 | 说明 |
|------|------|
| **自动触发** | 基于 `description` 中的触发条件语义匹配，无需用户记忆命令 |
| **自包含目录** | 每个 Skill 是独立目录，含 SKILL.md + scripts/references/agents/examples 等资源 |
| **标准格式** | YAML frontmatter（name + description）+ Markdown 指令正文 |
| **按需加载** | 只在需要时加载，不污染通用上下文 |
| **可分发** | 支持本地安装、Git 分发、插件打包三种方式 |

四大扩展机制对比：Commands（用户显式斜杠命令）、Agents（子代理）、**Skills（自动触发能力包）**、Hooks（生命周期事件）。

## 文档导航

### 📚 概念文档（4 篇）

| 主题 | 说明 |
|------|------|
| [Skills生态概览](concepts/00-overview.md) | Skills 是什么、与 Commands/Agents/Hooks 的关系、触发机制、19 个 Skills 分类总览、安装使用方法、与 SDK Beta Skills API 和插件体系的关系 |
| [SKILL.md格式规范](concepts/01-skill-format.md) | Skill 目录结构、YAML frontmatter 字段详解、description 编写最佳实践（"pushy"风格）、Markdown body 组织方式、资源引用约定、打包分发指南 |
| [Skill Creator工具详解](concepts/02-skill-creator.md) | 元技能 skill-creator 的 5 步创建流程、3 个专业评估代理（analyzer/comparator/grader）、eval-viewer 报告、description improver、quick_validate/run_eval/run_loop 脚本、定量+定性评估方法论 |
| [Claude API Skill详解](concepts/03-claude-api-skill.md) | claude-api Skill 多语言覆盖（8 种语言）、核心文档内容、2025-2026 API 漂移警告（adaptive thinking、camelCase PHP、模型 ID 更新等）、默认配置建议、"Never guess SDK usage"原则 |

### 📖 参考文档（1 篇）

| 参考 | 说明 |
|------|------|
| [全部Skills索引](references/skills-index.md) | 19 个官方 Skills 完整清单表格：API与开发工具(4)、文档处理(5)、设计与创意(7)、沟通与写作(3)，含功能描述、主要资源、触发关键词，另附 theme-factory 10 个预设主题说明 |

## 19 个官方 Skills 速查

| 分类 | Skills |
|------|--------|
| **API 与开发工具** | `claude-api`、`mcp-builder`、`skill-creator`、`webapp-testing` |
| **文档处理** | `docx`、`pdf`、`pptx`、`xlsx`、`doc-coauthoring` |
| **设计与创意** | `algorithmic-art`、`canvas-design`、`theme-factory`、`frontend-design`、`brand-guidelines`、`slack-gif-creator`、`web-artifacts-builder` |
| **沟通与写作** | `internal-comms`、`academy-guide`、`discernment-nudge` |

## 与其他子 bundle 的交叉链接

| 相关 bundle | 链接 | 关系说明 |
|------------|------|---------|
| **Claude Code Wiki** | [/claude-code/concepts/01-plugin-system.md](../claude-code/concepts/01-plugin-system.md) | Skills 是 Claude Code 插件体系四大扩展机制之一，插件可以打包分发 Skills |
| **Python SDK Wiki** | [/python-sdk/concepts/08-beta-agents.md](../python-sdk/concepts/08-beta-agents.md) | SDK Beta Skills API 是云端 API 层面的技能封装，与本地文件系统级的 Claude Code Skills 是不同概念 |
| **Python SDK 概览** | [/python-sdk/concepts/00-overview.md](../python-sdk/concepts/00-overview.md) | claude-api Skill 中 Python 部分的详细文档在 Python SDK bundle 中 |

> ⚠️ **注意区分**：本 bundle（`official-skills`）是 Anthropic **官方 Skills 库的文档索引**；另一个 bundle `ai/ai-agent/anthropics-skills/`（如存在）是 Skills 格式规范的通用说明，两者不冲突——本 bundle 聚焦官方库索引和具体 Skills 的使用，前者聚焦格式规范本身。

## 更新日志

完整变更记录见 [log.md](log.md)。

```{toctree}
:maxdepth: 3

concepts/index
references/index
log
```
