---
okf_version: "0.2"
title: "Agency Agents"
description: "The Agency - 270+专业AI Agent Persona角色库与NEXUS多Agent编排框架"
tags:
  - ai-agent
  - multi-agent
  - persona
  - agency-swarm
  - markdown
  - role-specialization
generated: true
status: active
stale_after: P3M
sources:
  - https://github.com/agency-agents/agency-agents
related:
  - "[[ai-agent-fundamentals]]"
  - "[[hermes-agent]]"
  - "[[agency-agents-app]]"
  - "[[anthropics-skills]]"
---

# Agency Agents

Agency Agents（The Agency）是一个包含约270个专业AI Agent Persona的角色库，按17个部门（Division）分类组织。核心是NEXUS（Network of EXperts, Unified in Strategy）多Agent编排框架，支持3种部署模式（Full/Sprint/Micro）和7阶段流水线（Discovery→Operate）。每个Agent使用标准化Markdown格式定义（YAML frontmatter+10标准章节），配套16种工具集成适配器（Hermes/Codex/Claude Code等）和convert.sh格式转换引擎。

## 🧩 概念导航（Concepts）

- [agent-md-template](concepts/agent-md-template.md) — Agent Markdown模板规范：YAML frontmatter字段（name/description/color等）、10标准章节、Persona/Operations双分组、lint校验规则
- [persona-division-structure](concepts/persona-division-structure.md) — Persona部门分类体系：17个部门（divisions.json SSOT）、约270个Agent按专业领域分类、子目录层级组织
- [nexus-orchestration](concepts/nexus-orchestration.md) — NEXUS多Agent编排框架：3种部署模式、7阶段流水线、质量门控、Playbook/Runbook体系、handoff交接协议
- [integration-adapters](concepts/integration-adapters.md) — 工具集成适配体系：16种AI编码工具元数据、三种安装机制、convert.sh转换引擎、Hermes懒加载路由插件

## 🎯 示例导航（Examples）

- [create-custom-persona](examples/create-custom-persona.md) — 创建自定义Persona：YAML frontmatter填写、正文章节编写、lint检查、convert.sh格式转换

## 📚 参考导航（References）

- [agency-agents-sources](references/agency-agents-sources.md) — The Agency项目目录结构、部门体系、Agent文件格式规范、脚本工具信源清单

## 🔗 关联 Bundle

- [agency-agents-app](../agency-agents-app/index.md) — Agency Agents桌面应用，Tauri+Svelte 5原生应用
- [ai-agent-fundamentals](../ai-agent-fundamentals/index.md) — AI Agent基础概念与多Agent编排模式
- [hermes-agent](../hermes-agent/index.md) — Hermes Agent可加载The Agency的Persona角色
- [anthropics-skills](../anthropics-skills/index.md) — Anthropic Skills，SKILL.md格式规范参考

---

> **信任声明**：本文档基于 The Agency 源码逐模块分析，经 OKF 五阶段流程生成。
> 
> **生成时间**：2026-08-23 | **下次审查**：2026-11-23 | **维护者**：OKF Wiki Bot

```{toctree}
:hidden:
:maxdepth: 7

concepts/agent-md-template
concepts/integration-adapters
concepts/nexus-orchestration
concepts/persona-division-structure
examples/create-custom-persona
references/agency-agents-sources
```
