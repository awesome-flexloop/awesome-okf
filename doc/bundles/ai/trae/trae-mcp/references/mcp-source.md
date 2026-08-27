---
type: Reference
title: MCP 协议文档与 CloudBase MCP 索引
description: trae-mcp 仓库的信源登记簿，包含 MCP 官方协议文档链接、CloudBase MCP 文档与源码索引、仓库目录结构和配置速查表。
tags: [trae-mcp, mcp, mcp-protocol, cloudbase, source-index, reference]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/mcp-source.md
    title: "Trae MCP 源码信源"
---

# MCP 协议文档与 CloudBase MCP 索引

本文档汇总 trae-mcp 仓库涉及的外部资源索引，包括 MCP 官方协议文档、CloudBase MCP 相关链接、以及中文学习资源。

## MCP 官方文档

| 资源 | 链接 | 说明 |
|------|------|------|
| MCP 官方文档 | <https://modelcontextprotocol.io/> | MCP 协议完整规范，包含 Transport/Protocol/Capability 三层架构定义、JSON-RPC 消息格式、Tools/Resources/Prompts 三种交互模式 |
| Anthropic MCP 公告 | <https://www.anthropic.com/news/model-context-protocol> | Anthropic 发布 MCP 的官方公告，阐述设计理念与生态愿景 |
| MCP 中文快速入门指南 | <https://github.com/liaokongVFX/MCP-Chinese-Getting-Started-Guide> | 社区维护的中文入门指南，适合中文开发者快速上手 |
| TRAE MCP 文档 | <https://docs.trae.ai/ide/model-context-protocol> | TRAE IDE 中 MCP 配置与使用的官方文档 |

## CloudBase MCP 资源

| 资源 | 链接 | 说明 |
|------|------|------|
| IDE 设置文档 | <https://docs.cloudbase.net/ai/cloudbase-ai-toolkit/ai-agent-plugins> | CloudBase AI Toolkit 在 IDE 中的配置与使用文档 |
| 源码仓库 | <https://github.com/TencentCloudBase/CloudBase-AI-Toolkit> | CloudBase MCP 服务器源码，包含 AI 模型/认证/数据库/云函数/存储/CloudRun/小程序工具等能力实现 |
| Open Plugin 仓库 | <https://github.com/TencentCloudBase/cloudbase-plugin> | CloudBase 开放插件仓库 |
| npm 包 | `@cloudbase/cloudbase-mcp` | CloudBase MCP 的 npm 发布包，通过 `npx -y @cloudbase/cloudbase-mcp@latest` 启动 |

## trae-mcp 仓库索引

| 路径 | 说明 |
|------|------|
| `mcp/_template/` | MCP 配套 SKILL.md 模板，包含 Description/Usage Scenario/Instructions/Examples 标准章节 |
| `mcp/cloudbase/` | CloudBase MCP 配置与使用文档（仅 README.md，服务器代码在 npm 包中） |
| `mcp/git-commit-generator/` | 误放的 Skill 目录（无 MCP 服务器代码，纯 SKILL.md 指令包） |
| `.github/ISSUE_TEMPLATE/bug_report.md` | Bug 报告 Issue 模板 |
| `.github/ISSUE_TEMPLATE/skill_request.md` | MCP 请求 Issue 模板 |

## 相关链接

- [MCP 简介](../concepts/00-introduction.md)
- [MCP 三层模型](../concepts/01-mcp-architecture.md)
- [CloudBase MCP](../concepts/03-cloudbase-mcp.md)
- [配置 MCP 服务器示例](../examples/configure-mcp.md)
