---
type: Reference
title: Agent Skills 规范文档信源登记
description: 登记本知识束引用的 12 个规范/指南类信源文件（含权威规范 specification.mdx、五篇创作指南与客户端名录数据），逐个记录文件路径、内容摘要与对应事实编号段。
tags: [agent-skills, skill-format, sources, specification, provenance]
generated: { by: "process:source-code-to-okf-wiki R→I→E", at: "2026-08-29" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29" }
status: stable
stale_after: 2027-08-29
sources:
  - id: agents-md
    resource: /references/spec-sources.md
    title: 仓库 AGENTS.md 权威性声明
  - id: spec-mdx
    resource: /references/spec-sources.md
    title: docs/specification.mdx 格式规范
  - id: creation-mdx
    resource: /references/spec-sources.md
    title: docs/skill-creation/ 五篇创作指南
  - id: client-mdx
    resource: /references/spec-sources.md
    title: docs/client-implementation/adding-skills-support.mdx 客户端集成指南
---

# Agent Skills 规范文档信源登记

本文件登记 agent-skills-spec 知识束所引用的全部规范文档类信源（共 12 个文件），信源均位于 `external/libs/ai/agentskills/agentskills/` 仓库（Agent Skills 开放标准官方仓库，最初由 Anthropic 开发，见事实 F-042）。每条登记包含：信源文件路径、内容摘要、角色定位（权威规范 / 指南 / 数据），以及该信源支撑的事实编号段（F-xxx 对应 `/trae/specs/agentskills-okf-wiki/facts.md` 中的登记条目）。

权威性裁决规则（F-001）：仓库 AGENTS.md 声明 `docs/specification.mdx` 对格式要求具有唯一权威性（authoritative）；解释性文档、示例、测试与实现均不向格式添加需求；当各表面不一致时，应在权威源处解决差异，而非把现有实现行为当作规范。

## 信源总表

| # | 信源文件（相对仓库根） | 角色 | 支撑事实 |
|---|---|---|---|
| 1 | `AGENTS.md` | 权威性声明 | F-001 |
| 2 | `README.md` | 定位声明 | F-042（互证） |
| 3 | `docs/specification.mdx` | **权威格式规范** | F-002 ~ F-015 |
| 4 | `docs/home.mdx` | 定位声明 | F-042 |
| 5 | `docs/clients.mdx` | 客户端名录入口 | F-041 |
| 6 | `docs/snippets/clients.jsx` | 客户端名录数据 | F-041 |
| 7 | `docs/skill-creation/quickstart.mdx` | 入门教程 | F-016 ~ F-017 |
| 8 | `docs/skill-creation/best-practices.mdx` | 创作指南 | F-018 ~ F-026 |
| 9 | `docs/skill-creation/evaluating-skills.mdx` | 评估指南 | F-027 ~ F-034 |
| 10 | `docs/skill-creation/optimizing-descriptions.mdx` | description 优化指南 | F-035 ~ F-040 |
| 11 | `docs/skill-creation/using-scripts.mdx` | 脚本工程指南 | （互补信源，见 11 号登记） |
| 12 | `docs/client-implementation/adding-skills-support.mdx` | 客户端实现指南 | F-043 ~ F-052 |

## 逐文件登记

### 1. AGENTS.md（仓库根）

仓库级智能体指令文件。关键声明：`docs/specification.mdx` is authoritative for format requirements；解释性文档、示例、测试与实现均不向格式添加需求；不把 `skills-ref/` 视作一般贡献面——它是 demonstration artifact，不是 production SDK，也不是格式需求的来源。本条声明是本知识束"规范 > 实现"裁决次序的依据。→ F-001

### 2. README.md（仓库根）

仓库自述文件，声明 Agent Skills 开放标准定位与许可证（代码 Apache-2.0 / 文档 CC-BY-4.0），与 `docs/home.mdx` 的定位声明同源互证。→ F-042

### 3. docs/specification.mdx（权威格式规范）

**本知识束最重要的信源**。核心章节与内容：

- **Overview / 目录结构**：Skill 是一个目录，最低要求只含一个 `SKILL.md`；可选目录 `scripts/`（executable code）、`references/`（documentation）、`assets/`（templates, resources），且允许任意附加文件或目录（"Any additional files or directories"）。→ F-002
- **SKILL.md 结构**：必须包含 YAML frontmatter 后接 Markdown 内容。→ F-003
- **Frontmatter 字段表**：`name`（必填）、`description`（必填）、`license`、`compatibility`（max 500 字符）、`metadata`（字符串键值映射）、`allowed-tools`（Experimental）。→ F-004
- **name 约束**：1-64 字符；unicode 小写字母数字与连字符；不得以连字符开头/结尾；不得含连续连字符；必须与父目录名一致；合法/非法示例。→ F-005 ~ F-006
- **description 约束**：1-1024 字符；应同时描述 what 与 when；差例 "Helps with PDFs." 与好例对照。→ F-007
- **license / compatibility 字段**：建议保持简短；Note："Most skills do not need the `compatibility` field"。→ F-008
- **metadata / allowed-tools 字段**：键名建议 reasonably unique；`allowed-tools` 为空格分隔的预批准工具列表，Experimental。→ F-009
- **正文（body）**：无格式限制；推荐章节；智能体决定激活后加载整个文件；建议拆分长内容。→ F-010
- **可选目录约定**：`scripts/` 脚本要求、`references/` 按需加载文档（"smaller files mean less use of context"）、`assets/` 静态资源三类。→ F-011
- **渐进式披露**：Metadata（约 100 tokens）→ Instructions（推荐 <5000 tokens）→ Resources（按需）三阶段及 token 预算。→ F-012
- **长度上限**："Keep your main `SKILL.md` under 500 lines." → F-013
- **文件引用约定**：相对技能根目录的路径；引用保持一层深。→ F-014
- **Validation 一节**：给出 `skills-ref validate ./my-skill` 命令并链接参考库。→ F-015

### 4. docs/home.mdx

文档站点首页。定位声明："lightweight, open format for extending AI agent capabilities"；技能核心是含 `SKILL.md` 的文件夹；加载经 Discovery → Activation → Execution 三阶段；"Open development" 一节声明格式最初由 Anthropic 开发、作为开放标准发布并被越来越多智能体产品采纳。→ F-042

### 5. docs/clients.mdx

客户端名录页面，从 `docs/snippets/clients.jsx` 导入 `clients` 数组并渲染 `ClientShowcase` 组件，是 46 家客户端生态信息的展示入口。→ F-041

### 6. docs/snippets/clients.jsx

客户端名录数据文件。`clients` 数组共 **46 个条目**，每条字段为 `name`、`description`、`url`、`lightSrc`、`darkSrc`、可选 `scale`、`instructionsUrl`、可选 `sourceCodeUrl`；名录包含 Claude、Claude Code、ChatGPT & Codex、Gemini CLI、GitHub Copilot、VS Code、Cursor、Goose、OpenHands、Letta、Factory、Kiro、Spring AI、Roo Code、TRAE（sourceCodeUrl 指向 github.com/bytedance/trae-agent）等。→ F-041

### 7. docs/skill-creation/quickstart.mdx

入门教程，创建 `roll-dice` 技能。关键内容：VS Code 默认在 `.agents/skills/` 目录查找技能；示例 SKILL.md 不足 20 行；开放格式声明（同一技能可在 Claude Code 与 OpenAI Codex 等兼容智能体工作）；`name` 必须与文件夹名一致、`description` 是激活依据、正文是激活后指令；"How it works" 三步骤 Discovery → Activation → Execution；"Tool-use reliability varies across models" 提示。→ F-016 ~ F-017

### 8. docs/skill-creation/best-practices.mdx

创作最佳实践指南，本知识束创作原则文档的主要信源。核心章节：两条创建路径（从亲自动手任务提取 / 从既有项目产物合成，F-018）；用真实执行打磨（execute-then-revise，F-019）；上下文经济学（"Add what the agent lacks, omit what it knows"，F-020）；划界与细节度（F-021）；大技能结构化（500 行/5000 tokens，F-022）；控制校准（自由度 vs 规定性，F-023）；默认值与过程倾向（F-024）；Gotchas 模式（F-025）；输出模板/checklist/验证循环/plan-validate-execute 与脚本打包信号（F-026）。

### 9. docs/skill-creation/evaluating-skills.mdx

评估驱动迭代指南。核心内容：测试用例三要素与 `evals/evals.json` 结构（F-027）；双臂对照运行模式与工作区结构（F-028）；干净上下文与旧版快照（F-029）；`timing.json` 字段（F-030）；断言写作原则（F-031）；`grading.json` / `benchmark.json` 结构与 delta 分析（F-032）；模式分析五条规则（F-033）；人工反馈 `feedback.json` 与迭代闭环（F-034）。

### 10. docs/skill-creation/optimizing-descriptions.mdx

description 触发优化指南。核心内容：触发机制定位与能力阈值限定（F-035）；写作四原则（F-036）；`eval_queries.json` 查询集设计（F-037）；near-miss 负例（F-038）；触发率测量（3 次运行、0.5 阈值、jq 检测脚本，F-039）；60/40 防过拟合切分与五步优化循环（F-040）。

### 11. docs/skill-creation/using-scripts.mdx

脚本工程指南（补充信源，facts.md 未单独立条，内容与 F-026、F-043 互补，concepts/03 的附录节直接引用原文）。核心内容：

- **一次性命令**：六个运行器——`uvx`（Python，随 uv 分发、激进缓存）、`pipx`（Python，成熟替代）、`npx`（随 Node.js 分发）、`bunx`（Bun 环境）、`deno run`（需权限标志）、`go run`（内置）；建议钉住版本、在 SKILL.md 声明前置条件。
- **自包含脚本**：Python 用 PEP 723 内联依赖（`# /// script` TOML 块）配 `uv run`；Deno 用 `npm:`/`jsr:` 导入说明符；Bun 自动安装缺失包；Ruby 用 `bundler/inline`。
- **面向智能体的脚本设计**：禁止交互式提示（硬性要求）；用 `--help` 文档化接口；有帮助的错误消息（说清错了什么、期望什么、下一步试什么）；结构化输出（JSON/CSV/TSV）且**数据走 stdout、诊断走 stderr**；幂等性；`--dry-run` 标志；有区分的退出码；安全默认值；可预测的输出规模（许多 harness 在 10-30K 字符阈值截断工具输出，大输出应默认给摘要或支持 `--offset` / `--output`）。

### 12. docs/client-implementation/adding-skills-support.mdx

客户端实现指南，面向智能体产品开发者。核心章节：集成差异两因素与三层加载策略表（Tier 1 Catalog / Tier 2 Instructions / Tier 3 Resources，F-043）；发现位置（project/user 两级作用域 + `.agents/skills/` 惯例 + 附加位置，F-044）；扫描规则与上界（深度 4-6 层、最多 2000 目录，F-045）；命名冲突/信任/云端场景（F-046）；解析与宽松校验四规则（F-047）；技能记录三字段（F-048）；Tier 1 目录披露与放置（F-049 ~ F-050）；Tier 2 激活双路径（F-051）；长会话上下文管理（结构化包裹、压缩豁免、子代理委派，F-052）。

## 使用约定

- 本知识束所有 concepts/examples 文档的 `sources` frontmatter 均指向本登记表或 `/references/skills-ref-sources.md`。
- 事实编号 F-xxx 是唯一追溯键；文档正文中的技术断言若无法对应到事实编号或本登记表所列信源原文，视为无效。
- 信源为只读外部仓库文件，本知识束不修改 `external/` 下任何内容。

## 相关概念

- [/concepts/00-skill-anatomy.md](/concepts/00-skill-anatomy.md) —— 权威规范 specification.mdx 的完整解析
- [/concepts/03-authoring-principles.md](/concepts/03-authoring-principles.md) —— 创作指南组信源的整合应用
- [/concepts/06-client-integration.md](/concepts/06-client-integration.md) —— 客户端实现指南信源的整合应用
- [/concepts/07-skills-ref-reference-implementation.md](/concepts/07-skills-ref-reference-implementation.md) —— 源码类信源登记见 skills-ref 源码登记表
- [/references/skills-ref-sources.md](/references/skills-ref-sources.md) —— skills-ref 源码/测试文件信源登记
