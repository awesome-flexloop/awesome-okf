---
type: Concept
title: 模型服务器选型
description: 项目支持的四种模型服务器：llamacpp_python、ollama、whispercpp、object_detection_python
tags: [模型服务器, llamacpp, ollama, whispercpp, 选型]
generated: { by: "trae-ai", at: "2026-08-26T08:08:00Z" }
verified: { by: "process:source-code-to-okf-wiki", at: "2026-08-26T08:08:00Z" }
status: stable
stale_after: 2027-08-26
sources:
  - id: S-001
    resource: /references/readme-source.md
    title: 项目根目录 README.md
---

# 模型服务器选型

ai-lab-recipes 提供四种模型服务器实现，分别针对不同的 AI 任务场景。所有模型服务器均以容器形式提供，通过标准化 API 与 AI 应用交互。

## llamacpp_python（默认推荐）

**定位**：通用 LLM 推理服务器，项目默认选型

**特点**：
- 基于 [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) 库
- 提供 OpenAI 兼容 API 接口
- 支持多种构建变体：
  - `base/`：CPU 版本
  - `cuda/`：NVIDIA GPU 加速版本
  - `vulkan/`：Vulkan 加速（支持 amd64/arm64）
- 包含完整测试套件（`tests/` 目录）
- 通过环境变量配置模型路径和服务端口

**目录结构**：
```
model_servers/llamacpp_python/
├── base/Containerfile      # CPU版构建文件
├── cuda/Containerfile      # CUDA版构建文件
├── vulkan/
│   ├── amd64/Containerfile
│   └── arm64/Containerfile
├── src/
│   ├── run.sh              # 启动脚本
│   └── requirements.txt
├── tests/                  # 测试套件
└── Makefile                # 构建脚本
```

**适用场景**：Chatbot、RAG、Agent、代码生成、摘要等绝大多数 NLP 任务

## Ollama

**定位**：易用的本地 LLM 运行时

**特点**：
- 基于 [Ollama](https://ollama.ai/) 官方镜像
- 简化模型拉取和管理流程
- 提供命令行工具和 API
- 适合快速体验和开发

**适用场景**：快速原型验证、开发者本地体验、不想手动管理 GGUF 文件的场景

## Whisper.cpp

**定位**：语音识别专用服务器

**特点**：
- 基于 [whisper.cpp](https://github.com/ggerganov/whisper.cpp)
- 高效的语音转文本推理
- 支持多种 Whisper 模型尺寸
- 针对音频任务优化

**目录结构**：
```
model_servers/whispercpp/
├── base/Containerfile
├── src/run.sh
├── tests/
└── Makefile
```

**适用场景**：音频转文本、语音助手、会议记录等音频处理任务（对应 `recipes/audio/audio_to_text/`）

## Object Detection Python

**定位**：目标检测专用服务器

**特点**：
- 基于 Python 实现的计算机视觉模型服务
- 提供目标检测 API
- 独立的推理服务实现

**目录结构**：
```
model_servers/object_detection_python/
├── base/Containerfile
├── src/
│   ├── object_detection_server.py
│   ├── run.sh
│   └── requirements.txt
├── tests/
└── Makefile
```

**适用场景**：图像目标检测任务（对应 `recipes/computer_vision/object_detection/`）

## 选型对比表

| 模型服务器 | 任务类型 | API兼容性 | 硬件加速 | 推荐场景 |
|-----------|---------|----------|---------|---------|
| llamacpp_python | NLP通用 | OpenAI兼容 | CPU/CUDA/Vulkan | 生产级NLP应用、自定义开发 |
| Ollama | NLP通用 | Ollama API | CPU/GPU | 快速体验、本地开发 |
| Whisper.cpp | 语音识别 | 专用API | CPU | 音频转文本应用 |
| Object Detection | 计算机视觉 | 专用API | CPU | 目标检测应用 |

## 模型格式要求

- **llamacpp_python / Ollama**：需要 GGUF 格式模型（如 granite-7b-lab-Q4_K_M.gguf）
- **Whisper.cpp**：使用 Whisper 系列模型
- **目标检测**：使用对应视觉模型

模型可通过 `models/download_hf_models.py` 脚本从 HuggingFace 下载，或使用 `convert_models/` 工具进行格式转换。

## 相关概念

- [配方架构概览](00-introduction.md)：理解双容器整体架构
- [NLP配方概览](02-nlp-recipes.md)：了解基于这些模型服务器构建的NLP应用
- [部署方式](03-deployment.md)：学习如何部署模型服务器和应用
