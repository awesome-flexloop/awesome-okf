---
type: Concept
title: MCP 与 Skill 的本质区别
description: MCP 是程序化工具服务器（扩展 Agent 的"手"），SKILL 是提示词指令包（扩展 Agent 的"脑"），两者在本质、接口和使用方式上有根本区别。
tags: [trae-mcp, trae, mcp, skill, comparison, architecture]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/mcp-source.md
    title: "Trae MCP 源码信源"
---

# MCP 与 Skill 的本质区别

MCP 和 SKILL 是 TRAE Agent 能力扩展的两种根本不同机制。理解两者的区别是正确使用 TRAE 生态的前提。

## 核心对比

| 维度 | MCP | SKILL |
|------|-----|-------|
| **本质** | 工具服务器（Tool Server） | 提示词指令包（Prompt Package） |
| **接口形式** | 程序化 API 接口 | 自然语言工作流指令 |
| **使用方式** | Agent 通过函数调用来使用 | 指导 Agent 如何思考和行动 |
| **返回结果** | 结构化数据（JSON 等） | 不返回数据，而是注入行为模式 |
| **比喻** | 扩展 Agent 的"手"（能做什么操作） | 扩展 Agent 的"脑"（知道怎么做、何时做） |
| **分发形式** | npm 包 / Python 包 / 独立可执行文件 | Markdown 文件（SKILL.md + 资源文件） |
| **配置方式** | JSON 配置（command/args/env）启动服务器进程 | 复制 SKILL.md 到 `.trae/skills/` 目录 |
| **能力发现** | 启动后通过 JSON-RPC 自动注册 | 通过 SKILL.md frontmatter 声明 |

## 调用方式对比

### MCP 调用方式

MCP 配置完成后，Agent 在对话中会**自动发现**服务器提供的工具，并在需要时以函数调用形式执行：

1. 用户描述需求（如"帮我查询 CloudBase 数据库中的用户列表"）
2. Agent 判断需要调用 CloudBase MCP 的数据库查询工具
3. Agent 构造工具调用参数并执行
4. MCP 服务器返回结构化查询结果
5. Agent 基于结果继续对话或执行下一步操作

用户不需要知道具体工具的名称和参数——Agent 会自动处理。

### SKILL 调用方式

SKILL 加载后，Agent 会**遵循** SKILL.md 中定义的自然语言指令来指导自己的行为：

1. SKILL.md 中定义了 Description、Usage Scenario、Instructions（编号步骤）、Examples
2. Agent 匹配到适用场景后，按照 Instructions 中的步骤顺序执行
3. SKILL 不提供可执行接口，而是告诉 Agent"应该怎么做"
4. Agent 在执行过程中可能调用 MCP 工具、读写文件、运行命令等

## 仓库中的混淆案例

trae-mcp 仓库中存在 MCP 和 Skill 混淆的典型案例：

### git-commit-generator 是 Skill 而非 MCP

`mcp/git-commit-generator/` 目录包含：
- `SKILL.md`：自然语言指令（分析 diff → 确定 type/scope → 生成 Conventional Commits 格式信息）
- `examples/input.md`、`examples/output.md`：示例输入输出
- `templates/commit-message.txt`：提交信息模板
- `resources/conventional-commits-types.md`：11 种 commit 类型定义

该目录**没有任何 MCP 服务器实现代码**（无 index.js、无 build/ 目录、无启动命令），完全是从 trae-skills 仓库复制的 Skill 内容。这说明该目录误放在了 trae-mcp 仓库中。

### _template 中的 SKILL.md 是使用说明

`mcp/_template/SKILL.md` 是 MCP 服务器的**配套使用说明文档**模板，结构与 trae-skills 的 _template 完全一致。这意味着每个 MCP 服务器目录下可以放一个 SKILL.md 来说明如何使用该 MCP，但 SKILL.md 本身不等于 MCP 服务器。

## 何时使用 MCP，何时使用 SKILL

| 场景 | 选择 | 原因 |
|------|------|------|
| 需要执行具体操作（查询数据库、调用云函数、发送消息、操作文件系统） | **MCP** | 这些需要程序化 API 接口来实际改变或读取外部状态 |
| 需要遵循工作流 SOP（如何写 commit message、如何做代码审查、如何做安全检查） | **SKILL** | 这些需要自然语言指令来指导 Agent 的思考和行为顺序 |
| 需要原子化的资源操作能力 | **MCP** | MCP 应聚焦于提供原子化的资源操作 |
| 需要复杂的多步骤编排逻辑 | **SKILL** | 编排逻辑放在 SKILL 中，MCP 只提供原子工具 |
| 两者都需要 | **MCP + SKILL 组合** | MCP 提供"手"，SKILL 提供"脑"，如 CloudBase MCP 的 7 步模式 |

## trae-mcp 仓库的定位

由于 MCP 服务器代码通常以 npm/Python 包形式分发，trae-mcp 仓库当前更像是一个 **"MCP 配置注册表"**，收录：
- MCP 配置 JSON（command/args/env）
- SKILL.md 使用说明（配套 SOP）
- 状态标记（Ready/WIP/To be added）

贡献新 MCP 时应提供：配置 JSON、SKILL.md 使用说明、状态标记。

## 相关链接

- [MCP 简介](/concepts/00-introduction.md)
- [MCP 三层模型](/concepts/01-mcp-architecture.md)
- [MCP 配置格式](/concepts/02-mcp-configuration.md)
- [CloudBase MCP](/concepts/03-cloudbase-mcp.md)
- [MCP 开发入门](/concepts/05-mcp-development.md)
