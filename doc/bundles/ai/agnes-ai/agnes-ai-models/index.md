---
okf_version: "0.2"
type: bundle
title: "AgnesAI 模型API网关"
description: "AgnesAI多模态大模型API网关系统化中文教程——OpenAI兼容接口、对话/图像/视频生成、工具调用、生产环境最佳实践"
tags: [AI, LLM, 多模态, OpenAI兼容, API网关, 图像生成, 视频生成, Agent, Function Calling]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T21:40:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T21:40:00+08:00" }
status: stable
stale_after: 2027-06-30
sources:
  - id: agnes-ai-models-repo
    resource: ../../../../external/libs/models/AgnesAI/AgnesAI-Models/
    title: AgnesAI-Models 官方仓库
---

# AgnesAI 模型API网关知识库

本知识包是 [Agnes AI](https://agnes-ai.com/) 多模态大模型API网关的系统化中文教程，基于官方公开文档（版本 `2026.07.30`）和官方示例代码生成，覆盖从快速入门到生产环境部署的完整知识体系。所有内容均溯源至AgnesAI官方文档与示例，遵循 [OKF v0.2 规范](/concepts/00-introduction.md)。

> AgnesAI是一家专注于全模态基础模型的AI公司，通过统一的OpenAI兼容API网关提供文本对话、图像生成、视频生成、Agent工具调用等能力。

---

## 📚 知识结构总览

```
agnes-ai-models/
├── concepts/          # 核心概念文档（8篇，从入门到生产）
├── examples/          # 可运行实战示例（5个，覆盖核心API）
└── references/        # 信源登记簿（事实溯源）
```

---

## 🚀 入门篇（concepts/）

* [Agnes AI 简介](/concepts/00-introduction.md) — 平台定位、模型家族概览、核心能力、区域站点、版本说明。
* [5分钟快速开始](/concepts/01-getting-started.md) — 环境准备、依赖安装、第一个API调用（Python + curl双版本）、模型选择建议。
* [API认证与安全](/concepts/02-api-authentication.md) — Bearer Token认证机制、API密钥管理最佳实践、安全红线、401错误排查。

## 🎯 核心API篇（concepts/）

* [对话补全 API](/concepts/03-chat-completions.md) — `/v1/chat/completions`接口完整说明：消息格式、流式输出、工具调用、图像理解、关键参数。
* [图像生成 API](/concepts/04-image-generation.md) — 文生图、图生图、尺寸选择、URL/Base64输出、提示词最佳实践。
* [视频生成 API](/concepts/05-video-generation.md) — 异步任务机制、文生视频、图生视频、轮询策略、配额说明。

## ⚙️ 生产环境篇（concepts/）

* [速率限制与配额](/concepts/06-rate-limits.md) — RPM速率限制详解、订阅计划对比、429错误处理、指数退避重试、令牌桶限流实现。
* [错误处理与调试](/concepts/07-error-handling.md) — HTTP状态码速查表、4xx/5xx错误排查、通用重试装饰器、调试技巧、常见问题诊断表。

---

## 💻 实战示例（examples/）

| 示例 | 难度 | 核心能力 |
|------|------|---------|
| [OpenAI兼容客户端配置](/examples/openai-compatible.md) | ⭐入门 | 最小配置、无缝迁移、多服务商切换封装 |
| [Python对话补全示例](/examples/chat-completion.md) | ⭐入门 | 非流式调用、响应结构解析、多轮对话、System Prompt |
| [图像生成示例](/examples/image-generation.md) | ⭐⭐基础 | 文生图、URL/Base64输出、图片下载、批量生成 |
| [视频生成示例](/examples/video-generation.md) | ⭐⭐⭐进阶 | 异步任务提交、轮询等待、健壮重试、视频下载 |
| [Agent工具调用工作流](/examples/agent-workflow.md) | ⭐⭐⭐⭐高级 | Function Calling完整流程、多工具、并行调用、生产级注意事项 |

---

## 📋 信源登记簿（references/）

* [README信源](/references/readme.md) — 官方README中提取的F-001~F-015事实清单
* [模型目录信源](/references/model-catalog.md) — MODEL_CATALOG中提取的F-016~F-038事实清单

所有事实编号索引见 [references/index.md](/references/index.md)。

---

## ✅ 信任与生命周期说明

* **文档版本**：基于AgnesAI官方文档 `2026.07.30` 版本（更新日期 2026-07-30）
* **覆盖事实**：共提取38条可验证事实（F-001~F-038），所有API说明、参数、端点、限流值均有信源溯源
* **status**：stable — 核心API（对话/图像/视频）遵循OpenAI兼容规范，接口稳定性高
* **stale_after**：2027-06-30 — AI模型API迭代较快，设置约10个月后重新评估
* **核验链路**：所有示例代码基于官方examples/目录代码验证；API端点、参数与官方文档一致

### 已知边界

* 本知识包仅覆盖公开API层，核心模型实现和服务端源码未开源
* 速率限制、配额、定价可能随官方调整变化，生产环境请以官方平台控制台为准
* Embeddings、Audio等API文档待官方公开后补充

---

**本知识包共收录 17 个内容文档（8个概念 + 5个示例 + 2个信源 + 2个子目录索引 + 根索引）。**

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
