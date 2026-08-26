---
type: Reference
title: ai-lab-recipes 项目 README
description: ai-lab-recipes 项目官方 README，介绍项目定位、模型服务器概念和配方分类
tags: [readme, 项目概述, 入门]
generated: { by: "trae-ai", at: "2026-08-26T08:06:00Z" }
verified: { by: "process:source-code-to-okf-wiki", at: "2026-08-26T08:06:00Z" }
status: stable
stale_after: 2027-08-26
sources:
  - id: S-001
    resource: /references/readme-source.md
    title: 项目根目录 README.md
---

# ai-lab-recipes 项目 README

本文件是 ai-lab-recipes 项目官方 README 的整理摘录，记录项目的核心定位和基本架构。

## 项目定位

ai-lab-recipes 是一个使用 Podman 构建和运行容器化 AI/LLM 应用的配方仓库，帮助开发者：

- 在本地快速原型化 AI/LLM 应用，无需依赖外部托管服务
- 由于已容器化，可快速从原型迁移到生产环境

## 模型服务器概念

**模型服务器（Model Server）** 是提供机器学习模型（如 LLM）服务并通过 API 暴露功能的程序。这使得开发者可以轻松将 AI 能力集成到应用中。

- 默认使用 `llamacpp_python` 模型服务器
- 该服务器支持多种生成式 AI 应用和模型
- 每个示例应用可以搭配多种模型服务器

## 当前配方分类

配方由至少两个组件组成：
1. **模型服务器**：管理模型
2. **AI 应用**：提供特定任务逻辑（聊天、摘要、目标检测等）

配方按类别组织在 `recipes/` 目录下：

| 类别 | 目录 | 说明 |
|------|------|------|
| 音频 | `recipes/audio/` | 语音转文本等音频处理应用 |
| 计算机视觉 | `recipes/computer_vision/` | 目标检测等视觉应用 |
| 多模态 | `recipes/multimodal/` | 图像理解等多模态应用 |
| 自然语言处理 | `recipes/natural_language_processing/` | 聊天机器人、RAG、智能体、代码生成等 NLP 应用 |

## 预构建镜像

许多示例应用和模型的镜像已发布到 `quay.io`，完整镜像列表记录在 `ailab-images.md` 文件中。
