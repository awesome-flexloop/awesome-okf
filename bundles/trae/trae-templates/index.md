---
type: Index
title: Trae Templates 文档索引
description: trae-templates 社区模板仓库完整文档，涵盖五维分面分类体系、23个模板详解（Web前端/后端/移动桌面/数据AI/工具DevOps）、AGENTS.md AI开发契约和自定义模板创建指南。
tags: [trae-templates, index, documentation]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/templates-source.md
    title: Trae Templates 源码信源
---

# Trae Templates 文档

Trae Templates 是 TRAE IDE 的社区维护项目模板集合，采用 MIT 许可证。它提供 23 个极简启动模板，按五维分面分类法组织，覆盖 Web 前端、后端服务、移动桌面、数据 AI、工具 DevOps 五大领域。模板遵循"最小可用"设计原则——仅包含必需文件，拒绝多余脚手架。

## 概念文档

| 文档 | 说明 |
|------|------|
| [00-introduction.md](/concepts/00-introduction.md) | Trae Templates 简介：项目定位、五大分类体系、模板与脚手架区别 |
| [01-template-classification.md](/concepts/01-template-classification.md) | 五维分面分类体系：应用形态作为第一维度的分类哲学和选择方法 |
| [02-web-frontend-templates.md](/concepts/02-web-frontend-templates.md) | Web 前端模板（8个）：web-basic、react-starter、vue-starter、nextjs-starter、nuxtjs-starter、svelte-starter、angular-starter、tailwind-starter |
| [03-backend-templates.md](/concepts/03-backend-templates.md) | 后端服务模板（5个）：fastapi-service、nodejs-express、go-gin-service、java-springboot、rust-actix |
| [04-mobile-desktop-templates.md](/concepts/04-mobile-desktop-templates.md) | 移动端和桌面端模板（3个）：react-native、flutter-starter、electron-starter |
| [05-data-ai-templates.md](/concepts/05-data-ai-templates.md) | 数据与 AI 模板（3个）：python-script、jupyter-notebook、pytorch-starter |
| [06-tools-devops-templates.md](/concepts/06-tools-devops-templates.md) | 工具与 DevOps 模板（4个）：docker-compose、editor-config、gitignore、superpowers-trae-init |
| [07-agents-contract.md](/concepts/07-agents-contract.md) | AGENTS.md 开发契约：4条铁律、工具适配映射、触发器字典、Core Memory 集成 |

## 示例文档

| 文档 | 说明 |
|------|------|
| [use-nextjs-template.md](/examples/use-nextjs-template.md) | 使用 Next.js 模板创建项目：复制→安装→启动→开发的完整流程 |
| [use-superpowers-init.md](/examples/use-superpowers-init.md) | 使用 superpowers-trae-init 初始化 AI 辅助开发环境：.trae/ 配置→核心记忆→铁律验证 |
| [create-custom-template.md](/examples/create-custom-template.md) | 创建自定义模板：以 hono-starter 为例的最小可用模板设计全流程 |
| [agents-md-config.md](/examples/agents-md-config.md) | AGENTS.md 配置示例：轻量 AI 开发契约文件编写指南 |

## 参考文档

| 文档 | 说明 |
|------|------|
| [templates-source.md](/references/templates-source.md) | 源码信源索引：23个模板的技术栈、文件结构、启动命令、关键特性完整映射 |

## 快速开始

1. 阅读 [简介](/concepts/00-introduction.md) 理解模板定位和设计哲学
2. 阅读 [五维分面分类体系](/concepts/01-template-classification.md) 了解如何选择模板
3. 按应用形态阅读对应分类文档（Web前端/后端/移动桌面/数据AI/工具DevOps）
4. 参考 [使用 Next.js 模板](/examples/use-nextjs-template.md) 动手实践
5. 如需 AI 辅助开发，阅读 [AGENTS.md 开发契约](/concepts/07-agents-contract.md) 和 [superpowers-init 示例](/examples/use-superpowers-init.md)
6. 想贡献模板，阅读 [创建自定义模板](/examples/create-custom-template.md)
