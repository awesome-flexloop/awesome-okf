---
title: deepagents-in-action GitHub 仓库
type: reference
bundle: /datawhale/deepagents-in-action
description: Datawhale 出品的《Deep Agents 实战》教程仓库，基于 LangChain/LangGraph 生态系统构建生产级 AI Agent，包含14章课程内容与 AgentSeek 模板体系。
sources:
  - id: github-repo
    resource: https://github.com/datawhalechina/deepagents-in-action
    title: datawhalechina/deepagents-in-action GitHub 仓库
---

# deepagents-in-action GitHub 仓库

## 基本信息

- **仓库地址**：https://github.com/datawhalechina/deepagents-in-action
- **课程网站**：https://datawhalechina.github.io/deepagents-in-action/
- **出品方**：沧海九粟（LangChain 官方认证大使）
- **开源社区**：Datawhale
- **视频合集**：[B站](https://space.bilibili.com/28357052/lists/7757577?type=season)
- **图文合集**：小红书
- **开源协议**：CC BY-NC-SA 4.0（课程内容）/ MIT（网站代码）

## 版本要求

- Deep Agents ≥ 0.5
- Node.js ≥ 22.12.0（网站开发）
- 部分功能最低版本：
  - FilesystemBackend virtual_mode：≥0.5.0
  - FilesystemPermission：≥0.5.2
  - interrupt 权限模式：≥0.6.8
  - RubricMiddleware（Beta）：≥0.6.5
  - 第13章验证版本：0.7.1
  - Event Streaming v3：≥0.6

## 章节结构

| 篇章 | 章节 | 主题 |
|------|------|------|
| 准备篇 | pre01-pre02 | AgentSeek 环境搭建与技能安装 |
| 认知篇 | 第1-2章 | Agent Harness 诞生逻辑、快速上手 |
| 核心篇 | 第3-6章 | 虚拟文件系统、任务规划、子Agent、异步子Agent |
| 进阶篇 | 第7-12章 | Skills、长期记忆、HITL、沙箱、文件权限、MCP |
| 前沿预览 | 第13-14章 | Grading Rubrics、Event Streaming v3 |

## AgentSeek 模板体系

模板仓库：https://github.com/agentseek-ai/agentseek-templates

共7种模板：deepagents/default、deepagents/content-builder、deepagents/research、deepagents/mcp、deepagents/sandbox、deepagents/streaming、langchain/rubric。

## 网站技术栈

- Astro 6（静态站点框架）
- Tailwind CSS 4（样式）
- TypeScript
- 内容流水线：content/ 源文件经 scripts/prep-content.mjs 注入 frontmatter 生成到 src/content/chapters/
- 章节元数据：scripts/chapters.json

## 模型算力

由硅基流动（SiliconFlow）提供模型算力支持，支持通过 `MODEL_NAME` 环境变量切换模型。
