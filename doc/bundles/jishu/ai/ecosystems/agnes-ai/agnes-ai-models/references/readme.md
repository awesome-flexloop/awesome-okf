---
type: Reference
title: Agnes AI 官方README
description: AgnesAI官方README文档，包含项目介绍、快速开始、模型列表、API端点、基础示例
tags: [官方文档, README, 快速开始]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T21:40:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T21:40:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: official-readme
    resource: ../../../external/libs/models/AgnesAI/AgnesAI-Models/README.md
    title: Agnes AI Official README
---

# Agnes AI 官方README信源

本文件是AgnesAI官方README的信源登记簿，记录从官方README中提取的可验证事实，供concepts文档引用溯源。

## 核心事实清单（F-001 ~ F-015）

| 事实编号 | 事实内容 | 溯源位置 |
|---------|---------|---------|
| F-001 | Agnes AI 提供OpenAI兼容的多模态模型API网关，支持文本、图像、视频和Agent工作流 | README.md L11 |
| F-002 | 国际站URL: https://agnes-ai.com/ ；中国站URL: https://agnes-ai.cn/ | README.md L32-33 |
| F-003 | 开发者文档URL: https://agnes-ai.com/doc/overview | README.md L34 |
| F-004 | API平台URL: https://platform.agnes-ai.com/ | README.md L35 |
| F-005 | API Base URL: `https://apihub.agnes-ai.com/v1` | README.md L36 |
| F-006 | 当前文档版本: `2026.07.30`，最后更新: 2026-07-30 | README.md L23-24 |
| F-007 | Python SDK依赖: `openai>=1.40.0`, `requests>=2.32.0`，要求Python >=3.9 | pyproject.toml L7-9 |
| F-008 | 文本模型 `agnes-2.5-flash`: 支持512K上下文，65.5K最大输出，支持工具调用、编码、推理、图像理解 | README.md L41 |
| F-009 | 文本模型 `agnes-2.0-flash`: 支持256K上下文，64K最大输出，2026年6月从1M上下文回滚以保证稳定性 | README.md L42 |
| F-010 | 图像模型 `agnes-image-2.1-flash`: 支持文生图、图生图、URL/Base64输出，灵活尺寸 | README.md L61 |
| F-011 | 视频模型 `agnes-video-v2.0`: 支持文生视频、图生视频、多图视频、关键帧动画，异步任务API | README.md L62 |
| F-012 | 视频结果查询使用 `video_id`，通过 `GET https://apihub.agnes-ai.com/agnesapi?video_id=<VIDEO_ID>` 轮询 | README.md L179 |
| F-013 | 认证方式: 所有请求使用 `Authorization: Bearer YOUR_API_KEY` 请求头 | README.md L186 |
| F-014 | Free用户文本模型实际RPM: 20；Enterprise: 40；Token Plan: 1000 | README.md L115-117 |
| F-015 | API密钥必须保存在服务端环境变量，禁止暴露在客户端代码或公开仓库中 | README.md L187 |
