---
type: Reference
title: Agnes AI 模型目录
description: AgnesAI官方模型目录，包含所有模型家族、端点、能力、速率限制、配额、兼容性说明
tags: [模型目录, API端点, 速率限制, 配额]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T21:40:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T21:40:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: model-catalog
    resource: ../../../external/libs/models/AgnesAI/AgnesAI-Models/MODEL_CATALOG.md
    title: Agnes AI Model Catalog
---

# Agnes AI 模型目录信源

本文件记录MODEL_CATALOG.md中的可验证事实。

## 模型与端点事实（F-016 ~ F-030）

| 事实编号 | 事实内容 | 溯源位置 |
|---------|---------|---------|
| F-016 | 文本模型 `agnes-1.5-flash`: POST /v1/chat/completions，快速对话、低延迟推理，256K上下文 | MODEL_CATALOG.md L32 |
| F-017 | 文本模型 `agnes-2.5-flash`: POST /v1/chat/completions，编码、工具调用、推理、Agent工作流，512K上下文 | MODEL_CATALOG.md L33 |
| F-018 | 文本模型 `agnes-2.0-flash`: POST /v1/chat/completions，开发者Agent、客服、编码、工作流自动化，256K上下文 | MODEL_CATALOG.md L34 |
| F-019 | 图像模型 `agnes-image-2.0-flash`: POST /v1/images/generations，文生图、图生图，URL/Base64输出 | MODEL_CATALOG.md L48 |
| F-020 | 图像模型 `agnes-image-2.1-flash`: POST /v1/images/generations，高密度图像生成、图像编辑，灵活尺寸 | MODEL_CATALOG.md L49 |
| F-021 | 视频模型 `agnes-video-v2.0`: POST /v1/videos，文生视频、图生视频、多图视频、关键帧动画，异步生成 | MODEL_CATALOG.md L55 |
| F-022 | 图像API根URL: `https://apihub.agnes-ai.com` | MODEL_CATALOG.md L20 |
| F-023 | 视频结果查询端点: `GET https://apihub.agnes-ai.com/agnesapi?video_id=<VIDEO_ID>` | MODEL_CATALOG.md L60 |
| F-024 | 遗留任务查询格式（不推荐）: `GET https://apihub.agnes-ai.com/v1/videos/{task_id}` | MODEL_CATALOG.md L72 |
| F-025 | Free用户视频模型实际RPM: 1；Enterprise: 2；Token Plan: 5 | MODEL_CATALOG.md L108-110 |
| F-026 | Free用户1K图像实际RPM: 20；2K: 10；3K/4K: 1 | MODEL_CATALOG.md L91-94 |
| F-027 | Token Plan用户1K图像实际RPM: 100；2K: 80；3K/4K: 1 | MODEL_CATALOG.md L99-102 |
| F-028 | Starter订阅($4): 文本1500请求/5小时，图像4000张/天，视频500秒/天 | MODEL_CATALOG.md L125 |
| F-029 | Plus订阅($10): 文本7500请求/5小时，图像4000张/天，视频500秒/天 | MODEL_CATALOG.md L126 |
| F-030 | Pro订阅($50): 文本30000请求/5小时，图像4000张/天，视频500秒/天 | MODEL_CATALOG.md L127 |

## HTTP状态码处理事实（F-031 ~ F-038）

| 事实编号 | 事实内容 | 溯源位置 |
|---------|---------|---------|
| F-031 | 400: 无效请求，检查必填字段、参数类型、图像URL可访问性、响应格式位置 | MODEL_CATALOG.md L154 |
| F-032 | 401: 认证失败，检查API密钥、Bearer格式、环境变量加载、账户状态 | MODEL_CATALOG.md L155 |
| F-033 | 404: 端点或资源不存在，检查Base URL、端点路径、模型名、资源ID是否存在 | MODEL_CATALOG.md L156 |
| F-034 | 429: 速率限制超限，检查当前用户计划、RPM限制、并发请求、重试退避 | MODEL_CATALOG.md L157 |
| F-035 | 500: 服务器错误，退避重试，简化payload，验证最小请求是否可复现 | MODEL_CATALOG.md L158 |
| F-036 | 502: 上游网关错误，退避重试，检查服务状态 | MODEL_CATALOG.md L159 |
| F-037 | 503: 服务繁忙或不可用，稍后重试，降低并发，避免立即重复轮询 | MODEL_CATALOG.md L160 |
| F-038 | 520: 未知上游错误，退避重试，捕获请求元数据供支持排查 | MODEL_CATALOG.md L161 |
