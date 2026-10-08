---
type: concept
title: "插件体系"
tags: [claude-code, plugin, commands, agents, skills, hooks, mcp]
---

# 插件体系

Claude Code 提供了完善的**插件系统**（Plugin System），允许开发者扩展其核心能力。插件可以添加斜杠命令（Commands）、专项代理（Agents）、可复用技能（Skills）、事件钩子（Hooks）以及 MCP（Model Context Protocol）服务器。

## 什么是插件

插件是一个标准目录结构的扩展包，包含以下一种或多种扩展内容：

| 扩展类型 | 说明 |
|---------|------|
| **Commands（斜杠命令）** | 自定义 `/` 开头的斜杠命令，触发预定义工作流 |
| **Agents（专项代理）** | 专注于特定任务的专用 AI 代理，可并行执行 |
| **Skills（技能）** | 可复用的提示词模板和工作流程，供 Claude 按需加载 |
| **Hooks（事件钩子）** | 在特定事件（如会话开始、工具调用前/后）自动执行的逻辑 |
| **MCP Servers** | Model Context Protocol 服务器，提供外部工具和数据源集成 |

通过插件机制，你可以将团队的最佳实践、工作流程、编码规范固化下来，让所有成员共享。

## 插件标准目录结构

一个 Claude Code 插件遵循标准目录布局：

```
your-plugin/
├── .claude-plugin/
│   └── plugin.json          # 插件元数据配置文件（必需）
├── commands/                # 斜杠命令定义
│   ├── my-command.md        # 单个命令定义
│   └── ...
├── agents/                  # 专项代理定义
│   ├── my-agent.md          # 单个代理定义
│   └── ...
├── skills/                  # 技能定义
│   ├── my-skill/
│   │   └── SKILL.md         # 技能主文件
│   └── ...
├── hooks/                   # 事件钩子脚本
│   ├── SessionStart.sh      # 会话开始钩子
│   └── PreToolUse.py        # 工具调用前钩子
└── .mcp.json                # MCP 服务器配置（可选）
```

### plugin.json 配置文件

`.claude-plugin/plugin.json` 是插件的入口文件，定义插件的基本信息：

```json
{
  "name": "your-plugin-name",
  "version": "1.0.0",
  "description": "插件的简短描述",
  "author": "作者名",
  "commands": [
    {
      "name": "my-command",
      "description": "命令描述",
      "file": "commands/my-command.md"
    }
  ],
  "agents": [
    {
      "name": "my-agent",
      "description": "代理描述",
      "file": "agents/my-agent.md"
    }
  ],
  "skills": ["skills/my-skill/"],
  "hooks": [
    {
      "event": "SessionStart",
      "command": "hooks/SessionStart.sh"
    }
  ],
  "mcpConfig": ".mcp.json"
}
```

## 插件安装

### 通过 /plugin 命令安装

在 Claude Code 交互界面中使用内置的 `/plugin` 命令管理插件：

```
/plugin install <plugin-source>
/plugin list
/plugin update <plugin-name>
/plugin uninstall <plugin-name>
```

插件源可以是：
- 本地目录路径
- Git 仓库 URL
- 官方插件名称

### 通过配置文件安装

编辑 `~/.claude/settings.json`（全局）或项目级 `.claude/settings.json`，添加插件配置：

```json
{
  "plugins": [
    "path/to/local/plugin",
    "https://github.com/user/claude-code-plugin",
    "official-plugin-name"
  ]
}
```

## 四大扩展点详解

### 1. Commands（斜杠命令）

Commands 是最直观的扩展方式，通过 `/command-name` 触发预定义的工作流程。

**特点**：
- 用户主动触发，明确执行某个特定任务
- 通常封装一个完整的工作流（如代码审查、提交代码）
- 可以包含多步骤指令、参数、预期输出格式

**示例结构**：`commands/my-command.md`

```markdown
---
description: 命令描述
---

# 我的自定义命令

执行以下步骤：
1. 第一步：做某事
2. 第二步：做另一件事
...
```

**典型应用场景**：
- `/commit`：自动化 Git 提交流程
- `/code-review`：发起代码审查
- `/feature-dev`：启动功能开发工作流

### 2. Agents（专项代理）

Agents 是专注于特定领域任务的专用 AI 代理，可以独立或并行执行任务。

**特点**：
- 拥有专门定制的系统提示词，针对特定任务优化
- 可以被命令或其他代理调用
- 支持多代理并行协作（如 code-review 插件使用 5 个并行 Sonnet agents 从不同维度审查代码）
- 每个 agent 可以使用不同的模型或配置

**示例结构**：`agents/my-agent.md`

```markdown
---
model: sonnet
description: 代理职责描述
---

你是一个专门负责 XYZ 的代理。
你的职责是：
- ...
- ...
```

**典型应用场景**：
- 代码审查代理（专门检查安全问题、性能问题、风格问题）
- 架构师代理（负责设计决策和架构评审）
- 代码探索代理（快速理解代码库结构）

### 3. Skills（技能）

Skills 是可复用的提示词模板和知识库片段，Claude 会根据任务上下文自动判断是否需要加载某个 skill。

**特点**：
- 被动触发，由 Claude 根据当前任务自动选择加载
- 封装特定领域的专业知识和操作流程
- 比命令更轻量，更像是"可被调用的知识模块"

**示例结构**：`skills/my-skill/SKILL.md`

```markdown
---
name: my-skill
description: 何时使用此技能的描述
---

# 技能名称

## 适用场景
当遇到...情况时使用本技能。

## 操作步骤
1. ...
2. ...
```

**典型应用场景**：
- 前端设计最佳实践
- 迁移指南（如模型版本迁移）
- 安全编码规范
- 插件开发技能

### 4. Hooks（事件钩子）

Hooks 在特定事件发生时自动执行，允许你注入自定义逻辑来监控或修改 Claude Code 的行为。

**支持的钩子事件**：

| 钩子事件 | 触发时机 | 典型用途 |
|---------|---------|---------|
| `SessionStart` | 会话开始时 | 注入自定义指令、设置输出风格、加载上下文 |
| `Stop` | Claude 完成响应时 | 清理资源、记录日志、触发后续操作 |
| `PreToolUse` | 工具调用前 | 安全检查、权限验证、参数修改 |
| `PostToolUse` | 工具调用后 | 结果验证、日志记录、错误处理 |
| `UserPromptSubmit` | 用户提交消息前 | 输入预处理、敏感信息过滤 |

**示例：SessionStart 钩子**（Shell 脚本）：

```bash
#!/bin/bash
echo "注意：请以教育性风格输出，解释你的实现选择。"
```

**示例：PreToolUse 安全钩子**（Python 脚本）：

```python
import sys
import json

tool_call = json.loads(sys.stdin.read())
# 检查是否为危险操作（如 rm -rf /）
if is_dangerous(tool_call):
    print(json.dumps({"block": True, "reason": "检测到危险操作"}))
else:
    print(json.dumps({"block": False}))
```

**典型应用场景**：
- 安全监控：拦截危险命令
- 风格控制：自动切换输出风格（教育模式/简洁模式）
- 审计日志：记录所有工具调用
- 上下文注入：会话开始时自动加载项目特定指令

### MCP Servers

除了上述四个核心扩展点，插件还可以包含 `.mcp.json` 配置文件来集成 MCP（Model Context Protocol）服务器。MCP 是一个开放协议，允许 Claude Code 连接外部数据源和工具：

- 数据库查询
- API 集成
- 内部系统访问
- 自定义工具扩展

## 官方插件 vs 社区插件

### 官方插件

Anthropic 官方维护了 13 个插件，覆盖开发工作流、安全质量、学习风格、开发工具等场景。这些插件经过官方测试和维护，质量有保障。

完整清单见 [官方插件索引](../references/plugins-index.md)。

### 社区插件

社区开发者可以创建和分享自己的插件。安装社区插件时请注意：

- 审查插件代码，特别是 hooks 和 MCP 配置部分（可能执行任意代码）
- 优先选择星标数高、维护活跃的插件
- 注意插件的许可证和兼容性

## 相关概念

- [Claude Code 概览](00-overview.md) — 了解 Claude Code 基础
- [官方插件索引](../references/plugins-index.md) — 13 个官方插件完整清单
- [基本使用示例：安装插件](../examples/basic-usage.md#安装插件) — 插件安装操作示例
