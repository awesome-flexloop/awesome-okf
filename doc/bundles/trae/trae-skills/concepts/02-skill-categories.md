---
type: Concept
title: 技能分类与模板模式
description: 社区 12 个技能可归纳为三种结构模式：纯 Prompt 型（仅 Markdown 指令）、脚本辅助型（Markdown + Python/JS 脚本）、Workflow 编排型（多 Phase + subskills + 多脚本协同），复杂度递增但核心始终是 SKILL.md。
tags: [trae-skills, categories, patterns, pure-prompt, script-assisted, workflow]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/skills-source.md
    title: Trae Skills 源码信源
---

## 三种模式概览

社区技能按复杂度递增可归纳为三种结构模式：

| 模式 | 核心构成 | 脚本 | subskills | 典型技能 | 复杂度 |
|------|----------|------|-----------|----------|--------|
| **纯 Prompt 型** | SKILL.md + 可选文本资源 | 无 | 无 | git-commit-generator、cn-punctuation-checker、web-design-teroop、wechat-mini-program-development、cloudbase | ★☆☆ |
| **脚本辅助型** | SKILL.md + resources/scripts/ 脚本 | 有 | 无 | daily-hot-news、video-to-keyframes、zopia_ai_skills | ★★☆ |
| **Workflow 编排型** | SKILL.md 多 Phase + subskills/ + 多脚本/模板 | 有 | 有 | daily-trend-writer、kz-article-deep-analysis、trae-claw-install | ★★★ |

三种模式并非"高级/低级"之分——最简单的纯 Prompt 型技能（如 `git-commit-generator`）可能使用频率最高，而最复杂的 Workflow 型技能因为依赖链路较长反而更脆弱。

## 纯 Prompt 型模式

纯 Prompt 型技能仅依靠 `SKILL.md` 中的自然语言指令指导 Agent 行为，不依赖任何可执行脚本。Agent 利用自身的内置能力（文件读写、Shell 执行、代码编辑、WebFetch 等）来完成任务。

**特征**：
- 技能目录中无 `resources/scripts/` 目录
- 可能包含 `examples/`、`templates/`、`resources/` 中的文本文件作为参考
- 指令通常是"分析→生成→输出"的线性流程
- 核心价值在于触发条件精确性和输出格式规范

**社区实例**：

| 技能 | 核心机制 | 内置能力依赖 |
|------|----------|-------------|
| `git-commit-generator` | 分析 git diff → 按 Conventional Commits 模板生成提交信息 | Shell（git diff）、文件读取 |
| `cn-punctuation-checker` | 扫描文件 → 按 12 组标点映射规则检测错误 → 输出位置报告 | 文件读写、正则匹配 |
| `web-design-teroop` | 5 步设计流程：预检→发现→生成规范→布局调整→技术合成 | 文件写入（.design-spec.md）、AskUserQuestion 交互 |
| `wechat-mini-program-development` | 8 步项目搭建：目录结构→config.js→api.js→request.js→util.js→app.js→tabBar | 文件创建、代码生成 |
| `cloudbase` | 7 步云开发流程：确认场景→MCP 检查→环境绑定→MCP 工具操作→部署→收尾 | CloudBase MCP 工具调用 |

详见 [纯 Prompt 型技能](/concepts/03-prompt-only-skills.md)。

## 脚本辅助型模式

脚本辅助型技能在 SKILL.md 指令基础上，通过 `resources/scripts/` 目录下的 Python/JS 脚本执行具体操作。脚本通常用于 Agent 无法仅靠自然语言推理完成的任务：外部数据获取、复杂计算、二进制数据处理。

**特征**：
- 包含 `resources/scripts/` 目录，内含一个或多个可执行脚本
- SKILL.md 中明确指示 Agent 执行脚本命令
- 脚本尽量极简，优先使用标准库，减少依赖安装需求
- 脚本负责"做事"，SKILL.md 负责"指挥"——决定何时调用脚本、如何传参、如何处理输出

**社区实例**：

| 技能 | 脚本语言 | 脚本功能 | 依赖 |
|------|----------|----------|------|
| `daily-hot-news` | Python | `fetch_news.py`（4 层数据源热榜抓取）、`generate_report.py`（JSON→Markdown/HTML 报告） | Python 标准库 |
| `video-to-keyframes` | Python | 4 个脚本：抽帧（extract_frames_and_describe.py）、关键帧选择（select_keyframes.py，dHash 转场检测）、一键编排（run_video_workflow.py）、日期目录生成（generate_daily_folder.py） | numpy、opencv-python |
| `zopia_ai_skills` | HTTP API | REST API 调用（创建项目/Agent 对话/查询状态），SKILL.md 定义 API 端点和认证流程 | 无（Agent 直接 HTTP 请求） |

**设计原则**：
1. 脚本应尽可能使用标准库（如 `fetch_news.py` 仅用 Python 标准库，无需 pip install）
2. SKILL.md 中明确给出一键运行命令，Agent 只需复制执行
3. 脚本输出结构化数据（JSON/CSV），SKILL.md 指导 Agent 格式化最终输出
4. 复杂脚本流水线提供一键编排脚本（如 `run_video_workflow.py`）

详见 [脚本辅助型技能](/concepts/04-script-assisted-skills.md)。

## Workflow 编排型模式

Workflow 编排型技能通过 SKILL.md 定义多阶段（Phase/步骤）的复杂工作流，调用 subskills（子技能）和多个脚本/模板协同完成任务。这类技能处理的是"一个技能无法在单一线性指令中完成"的复杂场景。

**特征**：
- SKILL.md 按 Phase 或编号步骤划分工作流阶段
- 包含 `subskills/` 目录，存放可复用的子技能指令文件
- 可能同时包含脚本、模板、参考文件等多种资源
- 每个 Phase 有明确的输入/输出契约
- 可能定义归档路径、文件命名约定等流程规范

**社区实例**：

| 技能 | Phase/步骤数 | subskills | 工作流特征 |
|------|-------------|-----------|-----------|
| `daily-trend-writer` | 6 个 Phase | doc-coauthoring、mimeng-writing、wechat-article-writer | 时间同步→热点发现→选题深挖→内容打磨→双风格写作→归档交付 |
| `kz-article-deep-analysis` | 4 个步骤 | 无（但有 assets/template.md 和 references/methodology.md） | 文章获取→深度解构（议题/主张/论证骨架）→认知增量→报告生成，使用 @动作/@类型/@优先级 结构化标签 |
| `trae-claw-install` | 5 个步骤 | 无 | 平台检测路由→基线验证→setup/start/check→验收检查→故障排除，跨平台脚本路由 |

**Workflow 设计要点**：
1. **Phase 划分**：每个 Phase 应有明确的目标和产出物
2. **subskills 复用**：将重复使用的指令片段抽取到 `subskills/` 目录
3. **输入输出契约**：明确每个 Phase 从哪里获取输入、产出到哪里
4. **归档约定**：定义输出文件的路径格式和命名规则
5. **错误处理**：明确失败时的故障排除流程（如 `trae-claw-install` 的约束条款）

详见 [Workflow 编排型技能](/concepts/05-workflow-skills.md)。

## 模式选择决策树

设计新技能时，应从最简模式起步：

```
需要执行外部数据获取/复杂计算/二进制处理吗？
├── 否 → 纯 Prompt 型（从 _template 开始）
│         ↓ 验证触发逻辑和指令有效性
└── 是 → 需要多阶段复杂流程和子技能复用吗？
          ├── 否 → 脚本辅助型（写一个极简脚本 + SKILL.md 指令）
          └── 是 → Workflow 编排型（划分 Phase、提取 subskills、编排脚本）
```

关键原则：
- **优先用 Markdown 指令体描述完整工作流**，仅在纯 prompt 无法完成时才引入脚本
- 脚本优先使用标准库，减少依赖
- Workflow 型技能需在 SKILL.md 中明确每个 Phase 的输入/输出契约
- 遵循 `_template` 的规范结构，扩展字段（如 version、metadata.author）可按需添加

## _template 模板结构

所有技能应基于 `skills/_template/SKILL.md` 创建。模板定义了标准章节结构和必填 frontmatter 字段，是技能编写的起点。

模板定义的章节：
1. YAML frontmatter（name + description 必填）
2. `# Skill Name` 标题
3. `## Description` 功能描述
4. `## Usage Scenario` 使用场景（触发条件）
5. `## Instructions` 步骤化指令
6. `## Examples (Optional)` 示例

## 相关概念

- [Trae Skills 简介](/concepts/00-introduction.md)
- [SKILL.md 格式规范](/concepts/01-skill-format.md)
- [纯 Prompt 型技能](/concepts/03-prompt-only-skills.md)
- [脚本辅助型技能](/concepts/04-script-assisted-skills.md)
- [Workflow 编排型技能](/concepts/05-workflow-skills.md)
- [编写自定义 Skill](/concepts/07-write-skill.md)

## 相关内容

- [源码信源索引](/references/skills-source.md)
- [创建第一个 Skill](/examples/create-first-skill.md)
- [带 Python 脚本的 Skill 示例](/examples/skill-with-python-script.md)
