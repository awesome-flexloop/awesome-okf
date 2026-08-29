---
type: Concept
title: 技能解剖：目录结构与 SKILL.md 组成
description: Agent Skills 技能的物理形态——一个含 SKILL.md 的目录，可选 scripts/references/assets 三个子目录，frontmatter 元数据加正文指令的结构，以及文件相对路径引用约定。
tags: [agent-skills, skill-format, skill-anatomy, directory-structure, specification]
generated: { by: "process:source-code-to-okf-wiki R→I→E", at: "2026-08-29" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29" }
status: stable
stale_after: 2027-08-29
sources:
  - id: spec-mdx
    resource: /references/spec-sources.md
    title: docs/specification.mdx 权威格式规范
  - id: quickstart-mdx
    resource: /references/spec-sources.md
    title: docs/skill-creation/quickstart.mdx 入门教程
---

# 技能解剖：目录结构与 SKILL.md 组成

Agent Skill（智能体技能）的最小物理单位是一个**目录**，其中必须且只需包含一个 `SKILL.md` 文件。规范（specification.mdx）对格式的全部强制要求都围绕这个目录展开：目录里放什么、SKILL.md 由什么组成、各字段如何约束。规范刻意保持极小——不规定技能目录住在哪里、如何被发现、如何被注册，这些由客户端生态以惯例承接（详见 [/concepts/06-client-integration.md](/concepts/06-client-integration.md)）。

本文覆盖规范本体的目录结构与文件组成；frontmatter 各字段的逐项约束见 [/concepts/02-frontmatter-fields.md](/concepts/02-frontmatter-fields.md)。

## 目录结构

一个技能目录的结构如下（F-002）：

```text
my-skill/
├── SKILL.md          # 必需：唯一的强制文件
├── scripts/          # 可选：智能体可执行的代码
│   └── extract.py
├── references/       # 可选：智能体按需阅读的文档
│   └── REFERENCE.md
├── assets/           # 可选：静态资源（模板、图片、数据）
│   └── report-template.md
└── ...               # 任意附加文件或目录均被允许
```

三个可选目录的定位与约定（F-002、F-011）：

| 目录 | 定位 | 约定要点 |
|---|---|---|
| `scripts/` | 可执行代码（executable code） | 脚本应自包含或清楚声明依赖；包含有用的错误信息；优雅处理边界情况；支持语言取决于 agent 实现（常见 Python、Bash、JavaScript） |
| `references/` | 按需阅读的附加文档 | 命名示例 `REFERENCE.md`、`FORMS.md`、领域文件（`finance.md`、`legal.md`）；"Keep individual reference files focused. Agents load these on demand, so smaller files mean less use of context."（单个文件保持聚焦——智能体按需加载，文件越小上下文消耗越少） |
| `assets/` | 静态资源 | 模板（文档/配置）、图片（图表/示例）、数据文件（查找表、schemas） |

规范明确允许任意附加文件或目录（"Any additional files or directories"），上表只是推荐约定而非封闭清单。

## SKILL.md 的两段式组成

`SKILL.md` 必须包含 YAML frontmatter（YAML 前置元数据块），后接 Markdown 内容（F-003）：

```markdown
---
name: pdf-processing
description: Extracts text and tables from PDF files... Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction.
license: Proprietary. LICENSE.txt has complete terms
---

# PDF Processing

分步指令、输入输出示例、常见边界情况……
```

两段的分工对应渐进式披露的前两层（详见 [/concepts/01-progressive-disclosure.md](/concepts/01-progressive-disclosure.md)）：

1. **Frontmatter（元数据层）**：`name` 与 `description` 在会话启动时对所有技能加载，供智能体决定是否激活（约 100 tokens/技能，F-012）。`description` 是激活决策的首要机制（F-007、F-035）。
2. **正文（指令层）**：智能体**决定激活后**才加载整个文件（"the agent will load this entire file once it's decided to activate a skill"，F-010）。

### 正文（body）的规范约束

- **无格式限制**："There are no format restrictions"（F-010）。
- **推荐章节**：分步指令、输入输出示例、常见边界情况（F-010）。
- **长度指南**："Keep your main `SKILL.md` under 500 lines. Move detailed reference material to separate files."（主文件 500 行以内，详细参考材料外移，F-013）。
- **拆分建议**：把较长的 SKILL.md 内容拆分到被引用的文件中（F-010）。

## 文件引用约定

引用技能内其他文件时使用**相对技能根目录的相对路径**（F-014）：

````markdown
详细错误码说明见 [REFERENCE.md](references/REFERENCE.md)。
运行提取脚本：
```bash
python scripts/extract.py
```
````

两条规则（F-014、F-022）：

1. 引用示例：`references/REFERENCE.md`、`scripts/extract.py`——都从技能根目录算起。
2. "Keep file references one level deep from `SKILL.md`. Avoid deeply nested reference chains."（引用保持一层深，避免深层嵌套引用链）。
3. 告诉智能体**何时**加载每个文件——"Read `references/api-errors.md` if the API returns a non-200 status code" 优于泛泛的 "see references/ for details"（F-022）。

## 格式校验

规范 Validation 一节给出官方校验命令（F-015）：

```bash
skills-ref validate ./my-skill
```

该命令检查 `SKILL.md` frontmatter 有效且遵循全部命名约定，退出码 0 表示有效、1 表示存在校验错误。skills-ref 参考实现的完整校验规则见 [/concepts/07-skills-ref-reference-implementation.md](/concepts/07-skills-ref-reference-implementation.md)，CLI 实战见 [/examples/02-skills-ref-cli.md](/examples/02-skills-ref-cli.md)。

## 与生态惯例的边界

规范只定义"目录内放什么"，不强制目录住在哪里。`.agents/skills/` 等存放路径是跨客户端事实惯例，由客户端实现指南承接（F-044）——这一"格式硬、生态软"的分布是理解整个标准的关键，详见 [/concepts/06-client-integration.md](/concepts/06-client-integration.md)。

## 相关概念

- [/concepts/01-progressive-disclosure.md](/concepts/01-progressive-disclosure.md) —— 目录结构背后的组织性原理
- [/concepts/02-frontmatter-fields.md](/concepts/02-frontmatter-fields.md) —— frontmatter 全字段规范
- [/concepts/03-authoring-principles.md](/concepts/03-authoring-principles.md) —— 在此骨架上填充内容的创作原则
- [/concepts/06-client-integration.md](/concepts/06-client-integration.md) —— 目录在哪里被发现
- [/examples/01-first-skill-roll-dice.md](/examples/01-first-skill-roll-dice.md) —— 从零创建一个最小技能目录
