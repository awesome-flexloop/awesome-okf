---
type: Concept
title: Agnes AI 简介
description: AgnesAI多模态AI平台介绍，包括模型家族、OpenAI兼容API设计、核心能力与适用场景
tags: [简介, 平台概述, 多模态, OpenAI兼容]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T21:40:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T21:40:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: official-readme
    resource: /references/readme.md
    title: Agnes AI 官方README
  - id: model-catalog
    resource: /references/model-catalog.md
    title: Agnes AI 模型目录
---

# Agnes AI 简介

Agnes AI 是一家专注于全模态基础模型的前沿AI公司，通过统一的API网关为开发者提供与OpenAI兼容的多模态模型访问接口，覆盖文本、图像、视频和Agent工作流等场景。

## 核心定位

Agnes AI 的核心设计理念是**OpenAI兼容的统一API网关**，这意味着：

1. 开发者可以直接复用已有的OpenAI SDK和集成代码，只需修改Base URL和API Key即可接入
2. 统一的接口规范覆盖文本对话、图像生成、视频生成等多种模态
3. 支持工具调用（Function Calling）、流式输出、多轮对话等高级特性

> 事实溯源：F-001、F-005

## 模型家族概览

Agnes AI 提供三大类模型，覆盖主流生成式AI场景：

| 模型类别 | 代表模型 | 核心能力 | 推荐场景 |
|---------|---------|---------|---------|
| **文本与视觉语言模型** | agnes-2.5-flash、agnes-2.0-flash、agnes-1.5-flash | 对话补全、流式输出、工具调用、编码、推理、图像理解 | 聊天机器人、编码助手、Agent系统、多模态助手 |
| **图像生成模型** | agnes-image-2.1-flash、agnes-image-2.0-flash | 文生图、图生图、URL/Base64输出、灵活尺寸 | 创意设计、产品视觉、营销素材、图像编辑 |
| **视频生成模型** | agnes-video-v2.0 | 文生视频、图生视频、多图视频、关键帧动画、异步生成 | 短视频制作、产品演示、营销视频、动态素材 |

> 事实溯源：F-008、F-009、F-010、F-011、F-016~F-021

## 区域站点与开发者资源

Agnes AI 提供双站点服务：

- **国际站**：https://agnes-ai.com/
- **中国站**：https://agnes-ai.cn/
- **API平台**：https://platform.agnes-ai.com/ （管理API密钥、查看用量、配置计费）
- **开发者文档**：https://agnes-ai.com/doc/overview

> 事实溯源：F-002~F-004

## 文档版本说明

当前公开文档版本为 `2026.07.30`（最后更新 2026-07-30）。模型可用性、速率限制、定价和配额规则可能随时间调整，生产环境关键值请以官方平台控制台为准。

> 事实溯源：F-006

## 相关概念

- [快速开始](/concepts/01-getting-started.md) — 5分钟完成第一个API调用
- [API认证与安全](/concepts/02-api-authentication.md) — API密钥管理与安全最佳实践
- [对话补全API](/concepts/03-chat-completions.md) — 文本与多模态对话接口详解
