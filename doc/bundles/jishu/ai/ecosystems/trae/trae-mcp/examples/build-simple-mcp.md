---
type: Example
title: 构建简单 MCP 服务器示例
description: 从 SDK 选择、服务器骨架搭建到 Tool 注册的完整 MCP 服务器开发流程示例，包含核心代码和 SKILL.md 编写方法。
tags: [trae-mcp, mcp, example, mcp-development, sdk, tool-server]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/mcp-source.md
    title: "Trae MCP 源码信源"
---

# 构建简单 MCP 服务器示例

本示例介绍构建简单 MCP 服务器的基本流程。

## 核心组成

MCP 服务器需要实现：

1. **Transport 层对接**：通过 stdio 与 TRAE 通信
2. **Capability 层注册**：定义 Tools/Resources/Prompts

Protocol 层（JSON-RPC）由 SDK 自动处理。

## Tool 注册四要素

| 要素 | 说明 |
|------|------|
| `name` | 工具名称标识符 |
| `description` | 功能描述，帮助 Agent 判断何时使用 |
| `inputSchema` | 输入参数的 JSON Schema |
| `handler` | 执行函数，接收参数并返回结果 |

## TRAE 配置

构建完成后在 TRAE 中配置：

```json
{
  "mcpServers": {
    "your-mcp-name": {
      "command": "node",
      "args": ["/absolute/path/to/build/index.js"],
      "env": {"API_KEY": "your-api-key-if-needed"}
    }
  }
}
```

注意：路径必须是绝对路径；敏感信息通过 env 传入；保存后新建对话生效。

## 编写 SKILL.md

参考 `mcp/_template/SKILL.md` 模板编写使用说明，包含 Description、Usage Scenario、Instructions（编号步骤）、Examples 章节。SKILL.md 指导 Agent 正确使用 MCP 工具，包括调用顺序和约束条件。

## 三层验证

| 层级 | 验证方法 |
|------|---------|
| Transport 层 | MCP 是否成功启动（无红色错误） |
| Protocol 层 | 工具列表是否显示注册的 Tool |
| Capability 层 | 对话中调用工具是否返回正确结果 |

## 学习资源

- MCP 官方文档：<https://modelcontextprotocol.io/>
- MCP 中文指南：<https://github.com/liaokongVFX/MCP-Chinese-Getting-Started-Guide>
- CloudBase MCP 源码：<https://github.com/TencentCloudBase/CloudBase-AI-Toolkit>

## 相关链接

- [MCP 开发入门](../concepts/05-mcp-development.md)
- [MCP 三层模型](../concepts/01-mcp-architecture.md)
- [配置 MCP 服务器示例](configure-mcp.md)
