---
type: Reference
title: AI Agent 跨项目信源索引
description: 12个AI Agent项目的源码位置与信源登记总表，作为fundamentals跨项目概念文档的信源依据。
tags:
  - ai-agent
  - cross-project
  - sources
  - reference
generated: 2026-08-23T02:00:00+08:00
verified: true
status: stable
stale_after: 2027-08-23
sources:
  - d:\spaces\SpecWeave\external\libs\models\ai\hermes-agent\
  - d:\spaces\SpecWeave\external\libs\models\ai\veadk-python\
  - d:\spaces\SpecWeave\external\libs\models\ai\Zleap-Agent\
  - d:\spaces\SpecWeave\external\libs\models\ai\deepseek-harness\
  - d:\spaces\SpecWeave\external\libs\models\ai\cordis\
  - d:\spaces\SpecWeave\external\libs\models\ai\mindverse\Second-Me\
  - d:\spaces\SpecWeave\external\libs\models\ai\intelligent-terminal\
  - d:\spaces\SpecWeave\external\libs\models\ai\agency-agents\
  - d:\spaces\SpecWeave\external\libs\models\ai\agency-agents-app\
  - d:\spaces\SpecWeave\external\libs\models\ai\anthropics\
  - d:\spaces\SpecWeave\external\libs\models\ai\book-to-skill\
  - d:\spaces\SpecWeave\external\libs\models\ai\i-have-adhd\
---

# AI Agent 跨项目信源索引

本文件登记 ai-agent bundle group 下 12 个项目的源码位置，供跨项目概念文档引用。

## Tier 1：大型框架/运行时

| 项目 | 语言 | 源码位置 | 项目信源 |
|------|------|---------|---------|
| hermes-agent | Python | [hermes-agent/](file:///d:/spaces/SpecWeave/external/libs/models/ai/hermes-agent/) | [hermes-agent-sources.md](../hermes-agent/references/hermes-agent-sources.md) |
| veadk-python | Python | [veadk-python/](file:///d:/spaces/SpecWeave/external/libs/models/ai/veadk-python/) | [veadk-python-sources.md](../veadk-python/references/veadk-python-sources.md) |
| zleap-agent | TypeScript/Rust | [Zleap-Agent/](file:///d:/spaces/SpecWeave/external/libs/models/ai/Zleap-Agent/) | [zleap-agent-sources.md](../zleap-agent/references/zleap-agent-sources.md) |
| deepseek-harness | TypeScript | [deepseek-harness/](file:///d:/spaces/SpecWeave/external/libs/models/ai/deepseek-harness/) | [deepseek-harness-sources.md](../deepseek-harness/references/deepseek-harness-sources.md) |
| intelligent-terminal | C++/Rust | [intelligent-terminal/](file:///d:/spaces/SpecWeave/external/libs/models/ai/intelligent-terminal/) | [intelligent-terminal-sources.md](../intelligent-terminal/references/intelligent-terminal-sources.md) |

## Tier 2：中型框架/库

| 项目 | 语言 | 源码位置 | 项目信源 |
|------|------|---------|---------|
| cordis | TypeScript | [cordis/](file:///d:/spaces/SpecWeave/external/libs/models/ai/cordis/) | [cordis-sources.md](../cordis/references/cordis-sources.md) |
| second-me | Python/TypeScript | [mindverse/Second-Me/](file:///d:/spaces/SpecWeave/external/libs/models/ai/mindverse/Second-Me/) | [second-me-sources.md](../second-me/references/second-me-sources.md) |

## Tier 3：专项工具/应用

| 项目 | 语言 | 源码位置 | 项目信源 |
|------|------|---------|---------|
| agency-agents | Markdown | [agency-agents/](file:///d:/spaces/SpecWeave/external/libs/models/ai/agency-agents/) | [agency-agents-sources.md](../agency-agents/references/agency-agents-sources.md) |
| agency-agents-app | Rust/Svelte | [agency-agents-app/](file:///d:/spaces/SpecWeave/external/libs/models/ai/agency-agents-app/) | [agency-agents-app-sources.md](../agency-agents-app/references/agency-agents-app-sources.md) |
| anthropics-skills | Python/Markdown | [anthropics/](file:///d:/spaces/SpecWeave/external/libs/models/ai/anthropics/) | [anthropics-skills-sources.md](../anthropics-skills/references/anthropics-skills-sources.md) |
| book-to-skill | Python | [book-to-skill/](file:///d:/spaces/SpecWeave/external/libs/models/ai/book-to-skill/) | [book-to-skill-sources.md](../book-to-skill/references/book-to-skill-sources.md) |
| i-have-adhd | Shell/Markdown | [i-have-adhd/](file:///d:/spaces/SpecWeave/external/libs/models/ai/i-have-adhd/) | [i-have-adhd-sources.md](../i-have-adhd/references/i-have-adhd-sources.md) |

## 事实采集文件

每个项目在 `.spec/facts.md` 中存储了 R 阶段采集的零推测事实清单，作为所有文档的信源基础：

| 项目 | 事实数 | facts 文件 |
|------|--------|-----------|
| hermes-agent | 80 | [facts.md](../hermes-agent/.spec/facts.md) |
| veadk-python | 100 | [facts.md](../veadk-python/.spec/facts.md) |
| zleap-agent | 113 | [facts.md](../zleap-agent/.spec/facts.md) |
| deepseek-harness | 118 | [facts.md](../deepseek-harness/.spec/facts.md) |
| cordis | 84 | [facts.md](../cordis/.spec/facts.md) |
| second-me | 40 | [facts.md](../second-me/.spec/facts.md) |
| intelligent-terminal | 79 | [facts.md](../intelligent-terminal/.spec/facts.md) |
| agency-agents | 54 | [facts.md](../agency-agents/.spec/facts.md) |
| agency-agents-app | 50 | [facts.md](../agency-agents-app/.spec/facts.md) |
| anthropics-skills | 30 | [facts.md](../anthropics-skills/.spec/facts.md) |
| book-to-skill | 99 | [facts.md](../book-to-skill/.spec/facts.md) |
| i-have-adhd | 18 | [facts.md](../i-have-adhd/.spec/facts.md) |
| **总计** | **865** | |
