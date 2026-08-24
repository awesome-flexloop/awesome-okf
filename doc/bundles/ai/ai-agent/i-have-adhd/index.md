---
okf_version: "0.2"
title: "I Have ADHD"
description: "ADHD认知辅助AI技能 - 10条输出规则+Session Hooks的注意力友好交互系统"
tags:
  - ai-agent
  - adhd
  - accessibility
  - cognitive-assistant
  - personal-ai
  - skills
generated: true
status: active
stale_after: P3M
sources:
  - https://github.com/i-have-adhd/i-have-adhd
related:
  - "[[ai-agent-fundamentals]]"
  - "[[second-me]]"
  - "[[intelligent-terminal]]"
  - "[[anthropics-skills]]"
---

# I Have ADHD

I Have ADHD 是专为 ADHD（注意力缺陷多动障碍）用户设计的 AI 输出风格技能包，核心是10条ADHD友好输出规则（行动优先、编号步骤、平实语言、短块≤3句、粗体关键词、一次一件事、进展标记、安全默认、提供选择、破坏性确认），通过 Claude Code Session Hooks（SessionStart/SessionStop/PostToolUse）实现偏好持久化和上下文恢复，支持 Claude Code/Codex CLI/Claude Desktop 三平台部署，具备Always-On跨应用模式和自动安装脚本。

## 🧩 概念导航（Concepts）

- [ten-output-rules](concepts/ten-output-rules.md) — 十条输出规则：行动优先、编号步骤、短块≤3句/列表≤5项、粗体关键词、8条例外场景、语气原则（直接/鼓励/不评判）
- [session-hooks-mechanism](concepts/session-hooks-mechanism.md) — Session Hooks机制：SessionStart偏好加载+上下文恢复、SessionStop进展保存+偏好持久化、PostToolUse进度标记、JSON偏好存储
- [multi-platform-integration](concepts/multi-platform-integration.md) — 多平台集成：Claude Code（Settings.json+Slash Commands+Hooks）、Codex CLI（instructions.md）、Claude Desktop、Always-On跨应用模式、auto-detect平台

## 🎯 示例导航（Examples）

- [install-adhd-skill](examples/install-adhd-skill.md) — 安装ADHD友好输出技能：各平台安装步骤、Session Hook激活、10条规则验证、临时关闭方法

## 📚 参考导航（References）

- [i-have-adhd-sources](references/i-have-adhd-sources.md) — i-have-adhd源码结构、10条输出规则、hooks always-on机制、多平台集成配置、评估体系信源清单

## 🔗 关联 Bundle

- [ai-agent-fundamentals](../ai-agent-fundamentals/index.md) — AI Agent基础概念与交互模式
- [second-me](../second-me/index.md) — Second Me个人智能体，个性化交互参考
- [intelligent-terminal](../intelligent-terminal/index.md) — 智能终端，可集成ADHD友好输出
- [anthropics-skills](../anthropics-skills/index.md) — Anthropic Skills规范，本技能遵循SKILL.md格式

---

> **信任声明**：本文档基于 i-have-adhd 源码逐模块分析，经 OKF 五阶段流程生成。本工具不构成医疗建议，ADHD诊断与治疗请咨询专业医疗人员。
> 
> **生成时间**：2026-08-23 | **下次审查**：2026-11-23 | **维护者**：OKF Wiki Bot

```{toctree}
:hidden:

concepts/multi-platform-integration
concepts/session-hooks-mechanism
concepts/ten-output-rules
examples/install-adhd-skill
references/i-have-adhd-sources
.spec/facts
```
