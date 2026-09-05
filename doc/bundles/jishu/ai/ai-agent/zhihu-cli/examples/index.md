---
okf_version: "0.2"
type: Example
title: "实战操作指南"
description: "Zhihu CLI 知识包操作层导航，5 篇示例文档从安装到命令使用再到 Agent 接入、MCP 配置与性能验证。"
tags: ["操作层", "实战指南", "示例", "Zhihu CLI", "MCP", "性能测试"]
generated: 2026-09-04
verified: 2026-09-05
status: verified
stale_after: "2026-12-31"
sources:
  - "F-001~F-235"
---

# 实战操作指南

本知识包包含 5 篇操作文档，从注册安装到命令使用再到 Agent 接入、MCP 配置与性能验证，带你一步步上手知乎数据开放平台。

## 学习路径

| 顺序 | 文档 | 核心内容 | 预计阅读 |
|------|------|----------|----------|
| 1 | [01 注册与安装](01-setup-installation.md) | 开放平台注册、实名认证、CLI 安装、Access Secret 配置 | 8 min |
| 2 | [02 核心命令使用](02-core-commands.md) | search/hot/answer/me 四大命令实战示例 | 10 min |
| 3 | [03 Agent 接入配置](03-agent-integration.md) | 以 Claude Code 为例的 Skill/MCP 接入配置流程 | 8 min |
| 4 | [04 MCP 接入实操指南](04-mcp-integration.md) | zhihu_search_mcp / zhida_mcp 详细配置、curl 示例、排错指南 | 12 min |
| 5 | [05 API 性能验证](05-api-latency-benchmark.md) | 响应耗时实测脚本、验证官方 600ms 延迟宣称的方法 [P0-047] | 6 min |

## 路径图

```mermaid
graph LR
    A[01 注册安装<br/>准备工作] --> B[02 核心命令<br/>基础使用]
    B --> C[03 Agent接入<br/>集成使用]
    C --> D[04 MCP 实操<br/>协议级接入]
    D --> E[05 性能验证<br/>独立核验]
    E --> F[concepts/<br/>深入理解原理]
```

建议先阅读 [concepts/](../concepts/index.md) 了解整体架构，再回到 examples 动手实践。

---

```{toctree}
:hidden:
:maxdepth: 2

01-setup-installation
02-core-commands
03-agent-integration
04-mcp-integration
05-api-latency-benchmark
```
