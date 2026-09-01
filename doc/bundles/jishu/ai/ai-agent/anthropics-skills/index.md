---
okf_version: "0.2"
title: "Anthropic Skills"
description: "Anthropic官方Agent Skills参考实现 - SKILL.md规范与渐进式加载最佳实践"
tags:
  - ai-agent
  - anthropic
  - claude
  - skills
  - tool-use
  - best-practices
generated: true
status: active
stale_after: P3M
sources:
  - https://github.com/anthropics/skills
related:
  - "[[ai-agent-fundamentals]]"
  - "[[hermes-agent]]"
  - "[[book-to-skill]]"
---

# Anthropic Skills

Anthropic Skills 是 Anthropic 官方发布的 Agent Skills 参考实现，定义了 SKILL.md 文件格式标准（6个YAML frontmatter字段、kebab-case命名、description触发机制、body<500行长度指南）、三级渐进式加载架构（Metadata→Body→Bundled Resources）、.skill分发包格式（ZIP/DEFLATED、自动验证、排除规则），以及内置的评估基准框架（双slave对比运行、A/B盲比、description自动优化循环、三环境适配）。包含17个内置Skill分类。

## 🧩 概念导航（Concepts）

- [skill-md-format-spec](concepts/skill-md-format-spec.md) — SKILL.md格式规范：6个frontmatter字段、kebab-case命名、description触发、body 4种内容模式、<500行指南
- [progressive-loading](concepts/progressive-loading.md) — 渐进式加载机制：三级加载（Metadata~100词→Body<500行→Resources按需）、资源引用约定、大文件分层
- [skill-packaging](concepts/skill-packaging.md) — Skill打包格式：.skill ZIP规范、DEFLATED压缩、排除规则、package_skill.py、17个内置Skill分类
- [eval-benchmark-framework](concepts/eval-benchmark-framework.md) — 评估基准框架：evals.json测试用例、双slave对比、grading.json评分、A/B盲比、三环境适配（Claude Code/Claude.ai/Cowork）

## 🎯 示例导航（Examples）

- [write-custom-skill](examples/write-custom-skill.md) — 编写自定义Skill：SKILL.md frontmatter规范、body指令编写、渐进式加载设计、.skill打包

## 📚 参考导航（References）

- [anthropics-skills-sources](references/anthropics-skills-sources.md) — Anthropic Agent Skills参考实现仓库结构、SKILL.md规范、Progressive Disclosure机制、17个Skill清单与工具脚本信源

## 🔗 关联 Bundle

- [hermes-agent](../hermes-agent/index.md) — Hermes Agent技能框架参考Anthropic Skills设计
- [book-to-skill](../book-to-skill/index.md) — 书籍转技能方法论，输出符合SKILL.md规范
- [ai-agent-fundamentals](../ai-agent-fundamentals/index.md) — AI Agent基础概念与技能系统模式
- [agency-agents](../agency-agents/index.md) — The Agency Persona格式参考SKILL.md规范

---

> **信任声明**：本文档基于 Anthropic Skills 官方仓库源码分析，经 OKF 五阶段流程生成。
> 
> **生成时间**：2026-08-23 | **下次审查**：2026-11-23 | **维护者**：OKF Wiki Bot

```{toctree}
:hidden:
:maxdepth: 7

concepts/eval-benchmark-framework
concepts/progressive-loading
concepts/skill-md-format-spec
concepts/skill-packaging
examples/write-custom-skill
references/anthropics-skills-sources
```
