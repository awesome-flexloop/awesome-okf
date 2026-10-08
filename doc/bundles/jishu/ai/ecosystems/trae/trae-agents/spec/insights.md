---
type: spec
title: "TRAE Agents 核心洞察与知识地图"
---

# TRAE Agents 核心洞察与知识地图

## 核心洞察（四元组）

### 洞察 1：Agent 配置的目录约定与 Markdown 模板规范

**陈述**：项目采用 `agents/<agent-name>/README.md` 的目录约定存储每个智能体配置，通过 `_template/` 目录提供标准化 README 模板。模板使用 YAML frontmatter（name/description）定义元数据，固定 8 个章节结构（基本信息/提示词/工具配置/协作智能体/使用示例/配置建议/相关资源/贡献者），内置工具勾选清单为 5 项复选框，确保每个 Agent 提交的信息完整性和一致性。每个 Agent 是一个独立目录，README 即配置文档。

**证据**：F-005（agents/ 目录结构）、F-007（每个 Agent 4 项配置：名称/提示词/工具/协作）、F-012（agents/_template/ + agents/git-commit-generator/ 两个子目录）、F-013（_template 的 YAML frontmatter + 8 章节结构）、F-014（5 项内置工具复选框）、F-015（推荐模型和温度参数）

**反常识**：Agent 配置通常以 JSON/YAML 等结构化格式存储（便于程序读取），但本项目选择纯 Markdown + YAML frontmatter 的"文档即配置"模式。这种选择牺牲了机器可解析性，却换来了极佳的人类可读性和 Git 友好性（diff 清晰、PR 审查容易、贡献门槛低），适合社区驱动的配置分享场景。

**行动**：理解"文档即配置"的社区分享模式设计取舍；分析 YAML frontmatter + Markdown 正文的混合格式如何平衡元数据结构化和内容自由表达；复刻 `_template/` 目录作为新项目模板的模式；掌握内置工具勾选清单的标准化表达方式。

---

### 洞察 2：最小可行 Agent 示例 + 双 Issue 模板引导社区贡献

**陈述**：项目目前仅有 1 个正式 Agent（git-commit-generator，状态 Stable）和 1 个模板，处于初始化阶段，但已建立完整贡献路径：6 步贡献流程（阅读指南→Fork→创建目录→填模板→更新列表→PR）+ 2 个 Issue 模板（Agent Request 新 Agent 请求 / Bug Report 问题反馈），其中 Agent Request 模板要求提交者提供使用场景、示例输入输出等结构化信息，降低了从"需求"到"实现"的转化摩擦。

**证据**：F-011（仅 1 个正式 Agent + "To be added" 占位）、F-016~F-022（git-commit-generator 完整示例，含 11 种 Conventional Commits 类型、格式规则、4 个示例、工具最小化配置）、F-023~F-024（两个 Issue 模板字段设计）、F-025（6 步贡献流程）

**反常识**：很多社区集合类项目在初始化阶段就追求数量，匆忙收录大量低质量条目。本项目反其道而行——先打磨 1 个高质量参考实现（git-commit-generator 包含完整 Prompt/工具配置/示例/参数建议），再通过模板和 Issue 流程引导社区按统一标准提交，质量优先于数量。

**行动**：分析 git-commit-generator 如何作为"参考实现"展示模板的每个章节该如何填写；理解工具最小化原则（仅勾选必要工具，避免过度授权）；复刻"1 个高质量示例 + 模板 + Issue 模板"的冷启动模式。

## 知识地图

### 学习路径

```
阶段1：Agent 配置规范
  ├─ agent-directory-convention.md → Agent 目录约定与"文档即配置"模式
  └─ agent-readme-template.md → Agent README 模板的 YAML frontmatter 与章节规范

阶段2：社区贡献
  └─ agent-contribution-flow.md → 最小可行示例 + Issue 模板的贡献引导
```

### 概念-事实映射

| 概念文档 | 核心事实 | 关键文件 |
|---------|---------|---------|
| agent-directory-convention.md | F-005, F-007, F-012 | `agents/` 目录结构 |
| agent-readme-template.md | F-013~F-015 | `agents/_template/README.md` |
| agent-contribution-flow.md | F-011, F-016~F-025 | `agents/git-commit-generator/README.md`, `.github/ISSUE_TEMPLATE/` |

### 示例/引用规划

| 示例文件 | 来源 | 说明 |
|---------|------|------|
| Agent 配置模板 | `agents/_template/README.md` | YAML frontmatter + 8 章节标准化模板 |
| Git Commit Generator | `agents/git-commit-generator/README.md` | 完整 Agent 配置参考实现 |
