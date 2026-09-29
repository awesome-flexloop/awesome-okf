---
type: Concept
title: SKILL.md 格式规范
description: SKILL.md 是 Skill 的核心文件，采用 YAML frontmatter 声明元数据（name/description/author/version/tags 等），Markdown 正文定义触发条件、使用场景和步骤化指令，是 Agent 识别和执行技能的唯一入口。
tags: [trae-skills, skill-format, SKILL.md, frontmatter, yaml]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/skills-source.md
    title: Trae Skills 源码信源
---

## SKILL.md 的核心地位

每个技能必须包含 `SKILL.md` 文件作为核心指令文件。SKILL.md 是 Agent 识别和加载技能的唯一入口——Agent 通过 frontmatter 中的 `name` 和 `description` 判断何时加载，通过正文中的指令决定如何执行。脚本、模板等资源都是可选的附属品。

## YAML Frontmatter 字段规范

SKILL.md 以 YAML frontmatter 开头，用 `---` 分隔。

### 必填字段

| 字段 | 类型 | 规则 | 说明 |
|------|------|------|------|
| `name` | string | 小写字母、连字符代替空格、命名保持稳定 | 技能的唯一标识符，也是目录名 |
| `description` | string | 明确说明"做什么"以及"何时使用" | Agent 决定是否加载该技能的依据 |

`name` 字段命名规则：
- 使用小写英文字母
- 单词间用连字符（`-`）连接，如 `git-commit-generator`
- 一旦发布不应随意更改，否则会破坏已有引用

`description` 字段是最关键的元数据，应包含双重信息：
1. **功能描述**：该技能能做什么
2. **触发场景**：什么时候应该加载这个技能

示例（`daily-hot-news`）：
> 在 Trae 中构建/部署/调试腾讯云开发（TCB）应用时使用...

示例（`video-to-keyframes`）：
> 视频抽帧、关键帧提取、镜头拆分、转场检测...当用户提供视频并说抽帧/拆帧/关键帧时触发...

### 可选扩展字段

社区技能中常见的扩展字段包括：

| 字段 | 示例值 | 使用技能 |
|------|--------|----------|
| `version` | `1.0.3` | kz-article-deep-analysis |
| `metadata.author` | `K叔` | kz-article-deep-analysis |
| `compatible` | （预留） | 用于声明兼容的 TRAE 版本范围 |
| `tags` | 数组 | 用于技能分类和搜索 |

部分技能的 name 字段带双引号（如 `"cn-punctuation-checker"`、`"video-to-keyframes"`、`"wechat-mini-program-development"`），这在 YAML 中与不带引号效果相同，但可避免特殊字符解析问题。

## 标准章节结构

模板 `skills/_template/SKILL.md` 定义的标准章节结构为：

```markdown
# Skill Name

## Description

描述技能的核心功能和能力边界。

## Usage Scenario

明确列出：
- 正面触发词：用户说什么关键词时触发
- 反面排除条件：什么场景不适用
- 能力边界声明：能做什么/不能做什么

## Instructions

步骤化的执行指令，按编号或分点列出。
每步应包含明确的动作描述和预期产出。

## Examples (Optional)

输入输出示例，帮助 Agent 理解期望的输出格式。
```

### Description 章节

Description 章节应简明扼要地说明技能的核心功能。建议包含：
- 技能的角色定位（如"首席设计架构师"）
- 核心能力范围
- 关键约束或前置条件

### Usage Scenario 章节

这是触发条件设计的关键章节（详见 [触发条件设计示例](../examples/trigger-condition-design.md)）。好的触发条件包含三个要素：

1. **正面触发词**：穷举用户可能使用的关键词
   - `daily-hot-news`："今日热搜""新闻热榜""今天有什么热点""全网热搜""热门新闻""今日新闻""热榜"
   - `git-commit-generator`：用户要求"写 commit message"/"生成 commit"、用户问"我改了什么"
   - `video-to-keyframes`："抽帧""拆帧""关键帧""候选关键帧""镜头拆分""转场点""分段""分镜初筛"

2. **反面排除条件**：明确不适用的场景
   - `daily-hot-news`："不适用于历史新闻或特定领域深度分析"
   - `kz-article-deep-analysis`："不适用于学术论文或书籍"

3. **能力边界声明**：约束条款防止越界操作
   - `cloudbase`："不得编造 CloudBase API 路径或 MCP 工具参数""不得在前端代码中暴露 API key"
   - `trae-claw-install`："不写入真实密钥""复用仓库脚本和文档，不创建并行流程"

### Instructions 章节

步骤化指令是技能的执行核心。建议遵循：
- 按执行顺序编号
- 每步包含明确的动作动词（确认、执行、调用、生成、输出等）
- 复杂步骤可分子步骤
- Workflow 型技能可用 Phase 划分大阶段
- 明确每步的输入来源和输出去向

### Examples 章节（可选）

Examples 章节提供输入输出的参考样例，帮助 Agent 理解期望的输出格式。技能目录下的 `examples/input.md` 和 `examples/output.md` 可作为更详细的示例文件。

## 非标准结构的包容

并非所有社区技能都严格遵循标准章节结构。例如 `cn-punctuation-checker` 采用了 Features/Supported Punctuation Marks/Usage/Execution Flow/Smart Detection Rules 的自定义结构，但凭借精确的功能描述仍能正常工作。这说明：

- **章节结构是建议而非强制**——Agent 能理解不同的 Markdown 组织方式
- **触发条件的精确性比章节结构更重要**——description 字段和触发关键词决定技能是否被加载
- 但遵循标准结构有助于技能的可维护性和可发现性

## 技能目录资源文件

除了 SKILL.md，技能目录可包含以下资源文件来增强指令效果：

| 文件类型 | 路径模式 | 用途 | 示例技能 |
|----------|----------|------|----------|
| 示例文件 | `examples/input.md`、`examples/output.md` | 提供输入输出参考 | daily-trend-writer、git-commit-generator、trae-claw-install |
| 模板文件 | `templates/*.txt`、`templates/*.md` | 可复用的输出模板 | git-commit-generator（commit-message.txt）、daily-trend-writer（topic-brief.md、trend-board.md） |
| 参考文件 | `resources/*.md` | 规范参考、数据源配置 | git-commit-generator（conventional-commits-types.md）、daily-hot-news（trend-sources.md） |
| 辅助脚本 | `resources/scripts/*.py` | Python/JS 脚本执行具体操作 | daily-hot-news（fetch_news.py）、video-to-keyframes（4 个脚本） |
| 子技能 | `subskills/*.md` | 可复用的子指令模块 | daily-trend-writer（doc-coauthoring、mimeng-writing、wechat-article-writer） |
| 验证脚本 | `scripts/verify.py` | 技能结构自检 | kz-article-deep-analysis |
| 方法论 | `references/methodology.md` | 深度分析方法论 | kz-article-deep-analysis |
| 资产模板 | `assets/template.md` | 输出报告模板 | kz-article-deep-analysis |

## 版本管理

kz-article-deep-analysis 提供了技能版本管理的范例：
- frontmatter 中声明 `version: 1.0.3`
- 正文末尾包含「版本历史」章节，记录每次变更
- 版本号遵循语义化版本（SemVer）：主版本.次版本.修订号

版本历史记录：
- v1.0.3：增加使用示例
- v1.0.2：术语专业化
- v1.0.1：添加作者元数据
- v1.0.0：初始版本

## 相关概念

- [Trae Skills 简介](00-introduction.md)
- [技能分类与模板模式](02-skill-categories.md)
- [纯 Prompt 型技能](03-prompt-only-skills.md)
- [脚本辅助型技能](04-script-assisted-skills.md)
- [Workflow 编排型技能](05-workflow-skills.md)
- [编写自定义 Skill](07-write-skill.md)

## 相关内容

- [源码信源索引](../references/skills-source.md)
- [触发条件设计示例](../examples/trigger-condition-design.md)
- [创建第一个 Skill](../examples/create-first-skill.md)
