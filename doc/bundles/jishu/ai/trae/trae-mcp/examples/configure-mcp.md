---
type: Example
title: 配置 MCP 服务器示例
description: 在 TRAE IDE 中添加本地 MCP 服务器和 CloudBase MCP 的完整配置步骤，包括 JSON 配置示例和验证方法。
tags: [trae-mcp, mcp, example, configuration, setup, cloudbase]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/mcp-source.md
    title: "Trae MCP 源码信源"
---

# 配置 MCP 服务器示例

本示例演示如何在 TRAE IDE 中配置一个 MCP 服务器。

## 步骤 1：打开 MCP 配置面板

1. 打开 TRAE IDE
2. 进入 **Settings**（设置）
3. 找到 **MCP** 选项
4. 点击 **Add**（添加）
5. 选择 **Manually Add**（手动添加）

## 步骤 2：配置本地构建的 MCP 服务器

假设你有一个本地开发的 MCP 服务器，构建产物入口文件为 `/absolute/path/to/build/index.js`：

```json
{
  "mcpServers": {
    "your-mcp-name": {
      "command": "node",
      "args": ["/absolute/path/to/build/index.js"],
      "env": {
        "API_KEY": "your-api-key"
      }
    }
  }
}
```

**字段说明**：

- `your-mcp-name`：替换为你的 MCP 服务器名称
- `command`：使用 `node` 启动构建产物
- `args`：入口文件的绝对路径（必须是绝对路径）
- `env.API_KEY`：如需 API Key 则在此配置

## 步骤 3：配置 CloudBase MCP

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

- `command`：使用 `npx` 运行 npm 包，无需预安装
- `args[0]`：`-y` 自动确认安装
- `args[1]`：`@cloudbase/cloudbase-mcp@latest` 始终使用最新版本
- 首次使用会打开浏览器进行登录和环境选择

## 步骤 4：保存并验证

1. 保存配置
2. 返回 TRAE 聊天界面
3. 新建对话（确保新 MCP 生效）
4. 选择 **Builder with MCP** 模式
5. 在对话中尝试使用新添加的 MCP 工具

## 常见问题排查

| 问题 | 排查方向 |
|------|---------|
| MCP 无法启动（红色错误） | 检查 command 是否可用、args 路径是否正确（绝对路径） |
| 启动但工具列表为空 | 检查 SDK 版本兼容性、JSON-RPC 握手是否成功 |
| 工具调用失败 | 检查环境变量/API Key 是否配置、认证是否过期 |

## 相关链接

- [MCP 配置格式](../concepts/02-mcp-configuration.md)
- [MCP 三层模型](../concepts/01-mcp-architecture.md)
- [CloudBase MCP 使用示例](use-cloudbase-mcp.md)
- [构建简单 MCP 服务器示例](build-simple-mcp.md)
