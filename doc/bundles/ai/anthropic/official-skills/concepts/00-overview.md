---
type: concept
title: "Anthropic Skills 生态概览"
tags: [skills, claude-code, claude-agent, capabilities, plugins]
sources:
  - id: anthropic-skills-docs
    title: Anthropic Official Skills Repository
---

# Anthropic Skills 生态概览

**Skills（技能包）** 是 Claude Code 和 Claude Agent 生态中的**可复用能力包**（reusable capability packages），用于封装特定领域的专业知识、工作流程和工具集。每个 Skill 是一个自包含的目录，通过标准化的 `SKILL.md` 文件声明其功能、触发条件和使用指令，使 AI 代理能够在特定场景下自动加载并应用专业能力。

## Skills 是什么

Skills 本质上是**领域专家知识的结构化封装**——它们将某个特定领域的最佳实践、参考文档、脚本工具和操作流程打包成一个可被 AI 代理自动发现和使用的单元。

与通用的系统提示词不同，Skills 具有以下特点：

| 特性 | 说明 |
|------|------|
| **按需触发** | 通过 `description` 中的触发条件自动激活，无需人工指定 |
| **自包含** | 每个 Skill 是独立目录，包含指令、脚本、参考文档等全部资源 |
| **可组合** | 多个 Skills 可以同时加载，协同解决复杂问题 |
| **可分发** | 可以通过文件系统、Git 仓库或插件市场分发共享 |
| **可评估** | 支持通过 evals 定量评估 Skill 的质量和效果 |

## Skills 与其他扩展机制的关系

在 Claude Code 的插件体系中，Skills 是四大扩展机制之一，各机制定位不同：

| 扩展机制 | 定位 | 触发方式 | 典型用途 |
|---------|------|---------|---------|
| **Commands** | 斜杠命令（`/command`） | 用户显式输入 | 交互式工作流、常用操作快捷方式 |
| **Agents** | 子代理（sub-agents） | 主代理显式调用 | 并行任务、专门领域深度处理 |
| **Skills** | 可复用能力包 | 基于描述自动触发 | 领域知识封装、专业能力注入 |
| **Hooks** | 生命周期钩子 | 事件驱动（如 pre-commit、post-edit） | 自动化检查、流程拦截、副作用处理 |

Skills 与 Commands 的关键区别：Commands 需要用户**主动输入**命令名称来触发，而 Skills 由 AI 代理根据用户请求的语义**自动判断**是否需要加载——用户无需知道 Skill 的存在，代理会在合适的场景下自主应用。

> 🔗 扩展阅读：Claude Code 插件体系详见 [/claude-code/concepts/01-plugin-system.md](/claude-code/concepts/01-plugin-system.md)

## SKILL.md 基本结构

每个 Skill 的核心是 `SKILL.md` 文件，采用 **YAML frontmatter + Markdown 指令**的标准格式：

```yaml
---
name: skill-name
description: |
  功能描述
  TRIGGER when: 用户执行X操作、询问Y问题、处理Z文件类型时触发
---
# Skill 标题

这里是 Markdown 格式的指令内容，告诉 AI 代理：
1. 何时使用此 Skill
2. 如何使用相关资源（scripts/、references/ 等）
3. 具体的工作流程和最佳实践
```

### 核心字段说明

- **`name`**：Skill 的唯一标识符，使用 kebab-case 命名
- **`description`**：功能描述 + 触发条件（TRIGGER when...），这是 Skill 自动触发的关键——描述需要足够明确且"有推动力"（pushy），防止在应该触发时未被激活
- **Markdown body**：详细的使用指令、工作流程、资源引用指引

### 可选资源目录

`SKILL.md` 所在目录下可以包含以下可选子目录：

| 目录 | 用途 |
|------|------|
| `scripts/` | 可执行脚本（Python、Shell、Node.js 等） |
| `references/` | 参考文档、API 文档、规范文档 |
| `agents/` | 专门的子代理定义（如 analyzer、comparator、grader） |
| `examples/` | 使用示例、输入输出样例 |
| `evals/` | 评估用例和测试脚本 |

> 🔗 格式规范详见 [SKILL.md 格式规范](01-skill-format.md)

## Skills 触发机制

Skills 的自动触发基于**语义匹配**，流程如下：

1. Claude Code 启动时扫描所有已安装的 Skills 目录，读取每个 `SKILL.md` 的 `name` 和 `description`
2. 当用户发送请求时，代理将请求内容与所有 Skill 的描述进行语义匹配
3. 如果某个 Skill 的描述表明它适用于当前场景，代理会自动加载该 Skill 的完整指令和资源
4. 代理遵循 Skill 中的指导来处理用户请求

### 触发条件编写原则

为了让 Skill 在正确的场景下被触发（避免 undertrigger 或 overtrigger），`description` 需要：

- **明确列出触发场景**：用 "TRIGGER when..." 清晰列出何时应该使用此 Skill
- **包含关键词**：包含用户可能使用的关键词、文件扩展名、技术术语
- **保持具体但不过度宽泛**：描述要足够具体以避免误触发，但也要覆盖合理的使用场景
- **"Pushy" 风格**：宁滥勿缺——在边界情况下倾向于触发，因为加载 Skill 的指令只会增加代理的知识，不会产生副作用

## 19 个官方 Skills 分类总览

Anthropic 官方提供了 19 个开箱即用的 Skills，按功能分为四大类：

### 1. API 与开发工具类（4 个）

| Skill | 核心功能 |
|-------|---------|
| `claude-api` | Claude API/SDK 多语言参考（Python/TypeScript/Java/Go/C#/PHP/Ruby/cURL），含 Managed Agents 文档、模型 ID、流式传输、工具调用、MCP、缓存、token 计数、模型迁移指南 |
| `mcp-builder` | MCP（Model Context Protocol）服务器构建工具，提供 Python/Node.js 参考实现、最佳实践、评估脚本 |
| `skill-creator` | 创建/修改/评估 Skills 的元技能，包含 analyzer/comparator/grader 三个子代理、eval 脚本、描述优化器 |
| `webapp-testing` | Web 应用测试，基于 Playwright 自动化、元素发现、控制台日志捕获、静态 HTML 测试 |

### 2. 文档处理类（5 个）

| Skill | 核心功能 |
|-------|---------|
| `docx` | Word 文档处理（accept_changes、comment、merge_runs、OOXML schema 验证、LibreOffice 集成） |
| `pdf` | PDF 处理（表单字段提取/填充、PDF 转图片、边界框检查、标注填充） |
| `pptx` | PowerPoint 处理（add_slide、clean、thumbnail、图表/主题/幻灯片辅助类） |
| `xlsx` | Excel 电子表格处理 |
| `doc-coauthoring` | 文档协作编写，提供结构化文档工作流 |

### 3. 设计与创意类（7 个）

| Skill | 核心功能 |
|-------|---------|
| `algorithmic-art` | 算法艺术生成，基于 p5.js 模板，提供生成器+查看器模式 |
| `canvas-design` | Canvas 设计系统，内置大量开源字体 |
| `theme-factory` | 主题工厂，提供 10 个预设主题：arctic-frost、botanical-garden、desert-rose、forest-canopy、golden-hour、midnight-galaxy、modern-minimalist、ocean-depths、sunset-boulevard、tech-innovation |
| `frontend-design` | 前端设计指导，帮助创建生产级 UI，避免"AI 美学"陷阱 |
| `brand-guidelines` | Anthropic 官方品牌指南，应用 Anthropic 品牌色彩和排版 |
| `slack-gif-creator` | Slack GIF 创建，包含缓动函数、帧合成、GIF 构建器、验证器 |
| `web-artifacts-builder` | Web 制品构建器，支持 shadcn 组件打包、artifact 初始化/打包脚本 |

### 4. 沟通与写作类（3 个）

| Skill | 核心功能 |
|-------|---------|
| `internal-comms` | 内部沟通模板（3P 更新、公司通讯、FAQ、通用沟通模板） |
| `academy-guide` | 学院指南 |
| `discernment-nudge` | 辨别力提示 |

> 🔗 完整索引详见 [全部 Skills 索引](/official-skills/references/skills-index.md)

## 如何安装与使用 Skills

### Skills 的存放位置

Skills 可以存放在以下位置，Claude Code 会自动扫描：

| 位置 | 作用域 | 说明 |
|------|--------|------|
| `~/.claude/skills/` | 用户全局 | 当前用户的所有项目可用 |
| `<project>/.claude/skills/` | 项目级 | 仅当前项目可用 |
| 插件目录 | 插件分发 | 通过 Claude Code 插件安装的 Skills |

### 安装第三方 Skills

```bash
# 方式 1：复制到全局 skills 目录
cp -r /path/to/skill ~/.claude/skills/

# 方式 2：复制到项目级 skills 目录
cp -r /path/to/skill your-project/.claude/skills/

# 方式 3：通过 Git 克隆（推荐用于版本管理）
git clone https://github.com/someone/skill-repo.git ~/.claude/skills/skill-name
```

安装后重启 Claude Code（或在会话中输入 `/reload`），新 Skill 即可被自动发现和使用。

### 使用 Skills

用户无需显式调用 Skills——只需正常描述你的需求，如果有匹配的 Skill，Claude Code 会自动加载并遵循其中的专业指导。例如：

- 当你说"帮我处理这个 Excel 文件"时，`xlsx` Skill 会自动触发
- 当你说"怎么用 Python SDK 调用 Claude API"时，`claude-api` Skill 会自动加载
- 当你说"帮我写一个 MCP 服务器"时，`mcp-builder` Skill 会提供最佳实践指导

## 与 Python SDK Beta Skills API 的区别

需要注意区分两个不同的"Skills"概念：

| 概念 | 所属 | 用途 |
|------|------|------|
| **Claude Code Skills**（本文档主题） | Claude Code / Claude Agent 插件体系 | 本地文件系统中的能力包，通过 `SKILL.md` 触发，用于指导代理行为 |
| **Python SDK Beta Skills API** | Claude API Python SDK（Beta） | API 层面的技能封装，通过 API 调用管理和执行 Skills |

简单来说：Claude Code Skills 是**本地文件级别的知识封装**，用于增强代理在本地环境中的能力；而 SDK Beta Skills API 是**云端 API 级别的功能抽象**，用于在 API 调用中封装可复用的业务逻辑。

> 🔗 SDK Beta Agents/Skills 详见 [/python-sdk/concepts/08-beta-agents.md](/python-sdk/concepts/08-beta-agents.md)

## 与 Claude Code 插件体系的关系

Skills 是 Claude Code 插件体系的四大组成部分之一。一个 Claude Code 插件可以同时包含 Commands、Agents、Skills 和 Hooks，通过统一的插件结构分发。

插件的典型目录结构：

```
my-plugin/
├── plugin.json          # 插件元数据
├── commands/            # 斜杠命令
├── agents/              # 子代理
├── skills/              # Skills（每个子目录是一个 Skill）
│   ├── my-skill/
│   │   └── SKILL.md
│   └── another-skill/
│       ├── SKILL.md
│       └── scripts/
└── hooks/               # 生命周期钩子
```

> 🔗 插件体系详解详见 [/claude-code/concepts/01-plugin-system.md](/claude-code/concepts/01-plugin-system.md)

## 相关概念

- [SKILL.md 格式规范](01-skill-format.md) — 深入了解 SKILL.md 的完整格式规范和最佳实践
- [Skill Creator 工具详解](02-skill-creator.md) — 学习如何使用 skill-creator 元技能创建和评估自定义 Skills
- [Claude API Skill 详解](03-claude-api-skill.md) — claude-api Skill 的详细使用指南
- [全部 Skills 索引](/official-skills/references/skills-index.md) — 19 个官方 Skills 的完整清单和功能说明
- [Claude Code 插件体系](/claude-code/concepts/01-plugin-system.md) — Skills 在 Claude Code 插件生态中的定位
- [Python SDK Beta Agents](/python-sdk/concepts/08-beta-agents.md) — API 层面的 Skills/Agents 概念（与本地 Skills 区分）
