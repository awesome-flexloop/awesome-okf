---
type: Concept
title: Trae Skills 简介
description: Trae Skills 是 TRAE IDE 的社区技能仓库，SKILL.md 本质是 YAML frontmatter + Markdown 指令体构成的提示词包，通过自然语言指令指导 Agent 行为，区别于传统插件和 MCP 工具。
tags: [trae-skills, introduction, skill, prompt-package]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/skills-source.md
    title: Trae Skills 源码信源
---

## 什么是 Skill

Skill（技能）是 TRAE IDE 中扩展 Agent 能力的基本单元。每个 Skill 的核心是一个名为 `SKILL.md` 的 Markdown 文件，它由两部分组成：

1. **YAML frontmatter**：元数据头部，声明技能名称（`name`）、功能描述（`description`）、作者、版本、标签等信息。其中 `description` 字段是 Agent 决定是否自动加载该技能的唯一依据。
2. **Markdown 指令体**：自然语言编写的步骤化指令，指导 Agent 在特定场景下应该做什么、怎么做。

SKILL.md 的本质是**提示词包（Prompt Package）**，而非传统意义上的代码包或插件。它的核心交付物是自然语言指令，脚本（Python/JS）仅作为可选辅助资源存在。纯 Prompt 型技能（如 `git-commit-generator`、`cn-punctuation-checker`）无需任何脚本即可工作。

## 社区技能仓库定位

trae-skills 是 TRAE IDE 的社区维护 Agent Skills 集合，采用 MIT 许可证开源。仓库当前包含 12 个技能目录（含 `_template` 模板），覆盖以下场景：

- **内容创作**：`daily-trend-writer`（公众号文章流水线）、`daily-hot-news`（热榜聚合）
- **开发效率**：`git-commit-generator`（提交信息生成）、`cn-punctuation-checker`（中文标点检查）
- **深度分析**：`kz-article-deep-analysis`（文章深度解读）
- **视频处理**：`video-to-keyframes`（视频关键帧提取）
- **云服务部署**：`cloudbase`（腾讯云开发）、`trae-claw-install`（OpenClaw 部署）
- **设计规范**：`web-design-teroop`（设计规范文档维护）
- **小程序开发**：`wechat-mini-program-development`（微信小程序脚手架）
- **AI 视频制作**：`zopia_ai_skills`（Zopia API 集成）

### 安装路径

Skill 支持两种安装级别：

| 安装级别 | 路径 | 作用范围 |
|----------|------|----------|
| 项目级 | `.trae/skills/<skill-name>/SKILL.md` | 仅当前项目可用 |
| 全局级 | `~/.trae/skills/<skill-name>/SKILL.md` | 所有项目可用 |

使用方式：将技能目录复制到对应路径下，TRAE 会自动识别 `SKILL.md` 中的 `description` 字段，在匹配场景时自动加载。

## Skill vs 插件 vs MCP

理解 Skill 与其他扩展机制的区别是正确使用 Skills 的前提：

| 维度 | Skill（技能） | VS Code 插件 | MCP（Model Context Protocol） |
|------|--------------|-------------|-------------------------------|
| **核心交付物** | Markdown 指令文件（SKILL.md） | 编译后的代码（VSIX 包） | MCP Server 进程 |
| **扩展方式** | 自然语言指令指导 Agent 行为 | 通过 VS Code API 扩展 IDE 功能 | 提供标准化工具/资源/Prompt 供 Agent 调用 |
| **执行主体** | Agent 按指令执行（Agent 是执行者） | 插件代码直接执行 | MCP Server 执行工具调用 |
| **是否需要编程** | 纯 Prompt 型不需要，脚本辅助型可选 | 必须编程（TypeScript/JS） | 必须编程（实现 MCP Server） |
| **触发机制** | description 字段匹配自动加载 | 用户手动安装/激活 | Agent 按需要调用工具 |
| **能力边界** | 由 Markdown 指令定义（灵活但依赖 Agent 理解） | 由代码 API 定义（精确但固定） | 由工具 Schema 定义（精确且标准化） |
| **典型场景** | 工作流编排、代码生成规范、内容创作模板 | 语法高亮、调试器、主题 | 数据库查询、API 调用、文件系统操作 |

关键区别：
- **Skill 不直接执行代码**——它告诉 Agent "应该怎么做"，Agent 用自身能力（文件操作、Shell 执行、代码编辑等）来完成任务
- **插件直接操作 IDE**——它通过 VS Code 扩展 API 添加按钮、面板、命令等 UI 元素
- **MCP 提供标准化工具**——它通过 JSON-RPC 协议暴露可调用的函数，Agent 按需调用

在实际使用中，三者可以协作：Skill 可以指导 Agent 使用 MCP 工具（如 `cloudbase` 技能明确要求优先使用 CloudBase MCP 工具），也可以生成代码触发插件功能。

## 技能目录结构约定

每个技能目录以 `SKILL.md` 为入口，可选包含以下子目录：

```
skills/<skill-name>/
├── SKILL.md              # 核心指令文件（必需）
├── examples/             # 输入输出示例（可选）
│   ├── input.md
│   └── output.md
├── templates/            # 可复用模板文件（可选）
├── resources/            # 参考文件、脚本、资源（可选）
│   └── scripts/          # Python/JS 辅助脚本
├── subskills/            # 子技能指令（Workflow 型专用）
├── assets/               # 报告模板等资产（可选）
└── references/           # 方法论参考（可选）
```

## 相关概念

- [SKILL.md 格式规范](01-skill-format.md)
- [技能分类与模板模式](02-skill-categories.md)
- [编写自定义 Skill](07-write-skill.md)

## 相关内容

- [源码信源索引](../references/skills-source.md)
- [创建第一个 Skill](../examples/create-first-skill.md)
