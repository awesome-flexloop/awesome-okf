---
type: Concept
title: MCP 开发入门
description: MCP 服务器开发需选择 SDK、实现服务器骨架、注册 Tool 处理函数，遵循 Transport-Protocol-Capability 三层架构进行开发和排错。
tags: [trae-mcp, trae, mcp, development, sdk, tool-registration]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/mcp-source.md
    title: "Trae MCP 源码信源"
---

# MCP 开发入门

本文档介绍如何开发一个简单的 MCP 服务器，包括 SDK 选择、服务器骨架和 Tool 注册。

## 学习资源

在开始开发之前，建议先阅读以下资源：

| 资源 | 链接 | 用途 |
|------|------|------|
| MCP 官方文档 | <https://modelcontextprotocol.io/> | 理解协议规范和 SDK 使用方式 |
| MCP 中文快速入门指南 | <https://github.com/liaokongVFX/MCP-Chinese-Getting-Started-Guide> | 中文入门教程 |
| CloudBase MCP 源码 | <https://github.com/TencentCloudBase/CloudBase-AI-Toolkit> | 参考生产级 MCP 服务器实现 |

## SDK 选择

MCP 服务器可以用多种语言开发，选择对应语言的 SDK：

| 语言 | SDK/方式 | 启动命令示例 |
|------|---------|-------------|
| Node.js/TypeScript | `@modelcontextprotocol/sdk` | `node /path/to/build/index.js` |
| Python | `mcp` Python 包 | `python -m your_mcp_server` 或 `uvx your-mcp-package` |
| Go | MCP Go SDK | 编译为独立二进制文件 |

对于 Node.js 开发者，最常见的方式是使用 TypeScript + `@modelcontextprotocol/sdk`，构建后通过 node 命令启动。

## 仓库目录结构

trae-mcp 仓库中，每个 MCP 服务器存放在 `mcp/` 目录下的独立子目录中：

```
mcp/
├── _template/          # MCP 配套 SKILL.md 模板
│   └── SKILL.md
├── cloudbase/          # CloudBase MCP 配置与文档
│   └── README.md
└── git-commit-generator/  # （误放的 Skill，非 MCP）
```

## MCP 模板结构

`mcp/_template/SKILL.md` 为 MCP 服务器配套使用说明的标准模板，frontmatter 包含 `name` 和 `description` 字段：

```markdown
---
name: your-mcp-name
description: MCP 服务器开发需选择 SDK、实现服务器骨架、注册 Tool 处理函数，遵循 Transport-Protocol-Capability 三层架构进行开发和排错。
---

# Your MCP Name

## Description
详细描述 MCP 服务器提供的能力。

## Usage Scenario
说明在什么场景下应该使用此 MCP。

## Instructions
1. 第一步操作
2. 第二步操作
3. ...

## Examples (Optional)
使用示例。
```

该模板结构与 trae-skills 的 _template 结构完全一致，因为 SKILL.md 本质上是指导 Agent 如何使用 MCP 的自然语言 SOP。

## MCP 服务器基本骨架（概念性介绍）

一个标准的 MCP 服务器通常包含以下核心要素：

### 1. Transport 层启动

服务器需要通过 stdio（标准输入/输出）与 TRAE 通信。Node.js SDK 通常提供 `StdioServerTransport` 类来处理这一层。

### 2. Server 实例创建

创建 MCP Server 实例，指定服务器名称和版本。Server 实例是注册所有能力的入口。

### 3. Tool 注册

通过 Server 实例注册工具。每个 Tool 需要定义：

- **name**：工具名称（Agent 调用时使用的标识符）
- **description**：工具功能描述（帮助 Agent 判断何时使用该工具）
- **inputSchema**：输入参数的 JSON Schema 定义（Agent 构造参数时的依据）
- **handler**：工具执行的处理函数（接收参数，返回结果）

### 4. 能力分类

MCP 定义了三种能力类型，对应 Protocol 层的三种交互模式：

| 能力类型 | 说明 | 使用频率 |
|---------|------|---------|
| **Tools** | 可执行的函数，Agent 调用后产生副作用或返回计算结果 | ⭐⭐⭐ 最常用 |
| **Resources** | 可读取的数据源，Agent 通过 URI 读取资源内容 | ⭐⭐ 较常用 |
| **Prompts** | 预定义的提示词模板 | ⭐ 较少用 |

## 配置本地构建的 MCP

开发完成后，构建 MCP 服务器，在 TRAE 中通过以下配置加载：

```json
{
  "mcpServers": {
    "your-mcp-name": {
      "command": "node",
      "args": ["/absolute/path/to/your/mcp/build/index.js"],
      "env": {
        "API_KEY": "your-api-key-if-needed"
      }
    }
  }
}
```

注意 `args` 中的路径必须是**绝对路径**。保存配置后返回聊天界面，使用 Builder with MCP 即可调用。

## 排错要点

开发过程中遇到问题时，按照三层模型逐层排查：

1. **Transport 层**：确认 command 路径正确、依赖已安装、环境变量齐全——服务器能否正常启动？
2. **Protocol 层**：确认 SDK 版本与 TRAE 兼容、JSON-RPC 握手成功——服务器启动后工具列表是否显示？
3. **Capability 层**：确认 Tool 的 inputSchema 正确、handler 逻辑无误——具体工具调用是否返回预期结果？

## 相关链接

- [MCP 三层模型](/concepts/01-mcp-architecture.md)
- [MCP 配置格式](/concepts/02-mcp-configuration.md)
- [MCP 与 Skill 的本质区别](/concepts/04-mcp-vs-skill.md)
- [构建简单 MCP 服务器示例](/examples/build-simple-mcp.md)
- [配置 MCP 服务器示例](/examples/configure-mcp.md)
- [MCP 协议文档与 CloudBase MCP 索引](/references/mcp-source.md)
