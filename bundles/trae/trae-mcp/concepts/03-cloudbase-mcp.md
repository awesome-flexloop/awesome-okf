---
type: Concept
title: CloudBase MCP
description: CloudBase MCP 是腾讯云开发的 MCP 服务器，通过 npx 一键启动，提供 AI 模型调用、数据库操作、云函数、存储管理等 7 类云资源能力。
tags: [trae-mcp, trae, mcp, cloudbase, tencent-cloud, cloud-services]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/mcp-source.md
    title: "Trae MCP 源码信源"
---

# CloudBase MCP

CloudBase MCP 是 trae-mcp 仓库中唯一状态为 **✅ Ready** 的 MCP 服务器，它展示了 MCP 在云开发场景下的典型应用模式。

## 什么是 CloudBase MCP

CloudBase MCP 是腾讯云开发（Tencent CloudBase）提供的 MCP 服务器，以 npm 包形式分发（`@cloudbase/cloudbase-mcp`），让 AI Agent 能够直接操作云开发资源。

> ⚠️ trae-mcp 仓库中 `mcp/cloudbase/` 目录仅包含 `README.md` 一个文件，无实际 MCP 服务器代码。服务器代码在 npm 包和 GitHub 源码仓库中，仓库只收录配置和使用文档。

## 能力范围

CloudBase MCP 覆盖腾讯云开发全栈资源，共 7 大类能力：

| 能力类别 | 说明 |
|---------|------|
| AI 模型 | 调用云开发 AI 能力 |
| 认证（auth） | 用户身份认证管理 |
| NoSQL/PostgreSQL 数据库 | 数据库查询与操作 |
| 云函数 | 云函数的创建、调用、调试 |
| 存储（storage） | 文件存储管理 |
| CloudRun | 容器化服务部署与管理 |
| 微信小程序工具 | 小程序相关开发工具 |

## 配置方式

CloudBase MCP 通过 npx 直接启动，配置 JSON 如下：

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

首次使用时，服务器会自动打开浏览器，引导用户完成**登录**和**环境选择**流程。

## 典型工作流：云开发资源的 AI 编排

CloudBase MCP 的使用遵循"环境绑定 → MCP 工具优先 → Skill 加载 → 顺序实现 → 收尾审查"的 7 步模式：

1. **确认场景**：明确是否为云开发项目（Web/小程序/云函数/CloudRun 等）
2. **确保 MCP 可用**：验证 CloudBase MCP 已正确配置并可被调用
3. **显式绑定环境**：调用 `envQuery` 工具解析并绑定 EnvId，避免操作错误环境
4. **优先使用 MCP 工具做管理工作**：通过 MCP 工具查询环境、创建云函数、操作数据库
5. **加载匹配的 CloudBase Skill**：获取领域工作流指导（7 步工作流指令）
6. **按顺序实现**：
   - 资源准备（创建数据库集合、配置存储等）
   - 前后端代码编写
   - 本地验证
   - 部署上线
7. **收尾审查**：运行 cloudbase-code-review，报告 EnvId 和访问 URL

## MCP 与 SKILL 的协作模式

CloudBase MCP 的 7 步模式揭示了一个关键架构原则：

- **MCP 提供原子能力**（"手"）：实际操作云端资源的工具接口
- **SKILL 编排调用顺序**（"脑"）：指导 Agent 在正确的时机调用正确的工具，避免自由调用导致的混乱

关键使用约束：
- 不得编造 API 路径或 MCP 工具参数
- 不得暴露凭证信息
- 同一路径 2-3 次失败后应停止重试，换用其他方式

## 相关链接

- [MCP 配置格式](/concepts/02-mcp-configuration.md)
- [MCP 与 Skill 的本质区别](/concepts/04-mcp-vs-skill.md)
- [CloudBase MCP 使用示例](/examples/use-cloudbase-mcp.md)
- [MCP 协议文档与 CloudBase MCP 索引](/references/mcp-source.md)
