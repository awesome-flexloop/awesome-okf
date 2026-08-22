---
type: Example
title: CloudBase MCP 使用示例
description: CloudBase MCP 的配置、登录认证、环境选择和 7 步工作流使用方式，涵盖云函数调用、数据库操作等典型场景。
tags: [trae-mcp, mcp, example, cloudbase, tencent-cloud, workflow]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/mcp-source.md
    title: "Trae MCP 源码信源"
---

# CloudBase MCP 使用示例

本示例演示如何配置和使用 CloudBase MCP 操作腾讯云开发资源。

## 步骤 1：添加配置

Settings → MCP → Add → Manually Add，粘贴：

```json
{
  "mcpServers": {
    "cloudbase-mcp": {
      "command": "npx",
      "args": ["-y", "@cloudbase/cloudbase-mcp@latest"],
      "env": {}
    }
  }
}
```

保存配置。

## 步骤 2：首次登录

1. 新建对话，选择 Builder with MCP 模式
2. 发送云开发相关请求（如"帮我查看云开发环境"）
3. 浏览器自动打开，完成腾讯云登录和环境选择
4. 回到 TRAE 即可使用

## 步骤 3：自然语言触发 MCP 工具

通过自然语言描述需求即可触发对应的 MCP 工具：

| 需求示例 | Agent 调用的能力 |
|---------|----------------|
| "查询当前绑定的云开发环境信息" | 环境查询（envQuery） |
| "创建一个名为 todos 的数据库集合并插入数据" | 数据库操作 |
| "创建一个 helloWorld 云函数" | 云函数管理 |
| "查看云存储中的文件列表" | 存储管理 |

## 步骤 4：遵循 7 步工作流

1. **确认场景**：告诉 Agent 要做什么
2. **确保 MCP 可用**：确认 CloudBase MCP 状态正常
3. **显式绑定环境**：调用 envQuery 确认 EnvId
4. **MCP 工具管理资源**：通过 MCP 创建/配置云端资源
5. **加载 Skill 指导**：获取领域工作流指导
6. **按顺序实现**：资源准备→代码编写→本地验证→部署
7. **收尾审查**：报告 EnvId 和访问 URL

## 能力范围

CloudBase MCP 覆盖 7 类云开发资源：AI 模型、认证（auth）、NoSQL/PostgreSQL 数据库、云函数、存储（storage）、CloudRun、微信小程序工具。

## 使用约束

- 不得编造 API 路径或工具参数
- 不得暴露凭证信息
- 同一路径 2-3 次失败后停止重试
- 始终先绑定环境再操作

## 相关链接

- [CloudBase MCP](/concepts/03-cloudbase-mcp.md)
- [MCP 配置格式](/concepts/02-mcp-configuration.md)
- [配置 MCP 服务器示例](/examples/configure-mcp.md)
