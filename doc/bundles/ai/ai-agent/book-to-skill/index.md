---
okf_version: "0.2"
title: "Book to Skill"
description: "书籍转技能框架 - 七概念方法论驱动的文档→Agent Skill知识编译器"
tags:
  - ai-agent
  - skill
  - knowledge-extraction
  - book-processing
  - methodology
  - okf
  - python
generated: true
status: active
stale_after: P3M
sources:
  - https://github.com/xinetzone/book-to-skill
related:
  - "[[ai-agent-fundamentals]]"
  - "[[anthropics-skills]]"
  - "[[second-me]]"
---

# Book to Skill

Book to Skill 是将书籍/文档转化为 AI Agent 可执行技能的知识编译器，基于 OKF 七概念方法论。采用"双半架构"——Python确定性文本提取器（summary层：full_text.txt+metadata.json）+ AI Agent规范驱动生成器（cards→prompts→evaluation三层），支持7种文档格式（PDF/EPUB/DOCX/HTML/RTF/TEXT/MOBI）的四级回退解析，实现10步转换流程、四层产出流水线、per-chapter token预算，具备多层安全防护（零宽字符清洗、prompt注入检测、XXE防护），可实现24-51倍token节省。

## 🧩 概念导航（Concepts）

- [four-layer-pipeline](concepts/four-layer-pipeline.md) — 四层产出流水线：双半架构、四种运行模式（Full/Analyze/Generate/Update）、10步转换流程、token预算矩阵、8条质量规则
- [multi-format-parsers](concepts/multi-format-parsers.md) — 多格式解析器：7种文档格式（PDF四级回退、EPUB/DOCX/HTML/RTF/TEXT+Calibre）、13语言章节检测
- [dependency-management](concepts/dependency-management.md) — 依赖管理系统：三层依赖分组（core/advanced/full）、stdlib零依赖回退、uv run一键安装、4种CLI安装模式
- [security-sanitization](concepts/security-sanitization.md) — 安全清洗机制：6类零宽字符清洗、4类代码混淆消除、7类prompt注入检测、DOCX XXE防护、符号链接拒绝

## 🎯 示例导航（Examples）

- [convert-book-to-skill](examples/convert-book-to-skill.md) — 将书籍转换为Skill：依赖安装、文本提取、模式选择、SKILL.md生成、安全验证完整流程

## 📚 参考导航（References）

- [book-to-skill-sources](references/book-to-skill-sources.md) — book-to-skill源码结构、多格式解析器、章节检测系统、SKILL.md生成流水线与安全扫描信源清单

## 🔗 关联 Bundle

- [anthropics-skills](../anthropics-skills/index.md) — Anthropic Skills规范，Book to Skill输出的SKILL.md遵循此标准
- [ai-agent-fundamentals](../ai-agent-fundamentals/index.md) — AI Agent基础概念，技能系统模式
- [second-me](../second-me/index.md) — Second Me可使用Book to Skill产出的技能扩展知识库
- [hermes-agent](../hermes-agent/index.md) — Hermes Agent可加载Book to Skill生成的技能包

---

> **信任声明**：本文档基于 book-to-skill 源码逐模块分析，经 OKF 五阶段流程生成。
> 
> **生成时间**：2026-08-23 | **下次审查**：2026-11-23 | **维护者**：OKF Wiki Bot

```{toctree}
:hidden:

concepts/dependency-management
concepts/four-layer-pipeline
concepts/multi-format-parsers
concepts/security-sanitization
examples/convert-book-to-skill
references/book-to-skill-sources
.spec/facts
```
