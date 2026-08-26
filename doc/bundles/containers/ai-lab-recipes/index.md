---
okf_version: "0.2"
type: Bundle
title: ai-lab-recipes 容器化AI配方仓库
description: 使用Podman构建和运行容器化AI/LLM应用的配方集合，包含模型服务器、Chatbot、RAG、Agent等示例
tags: [AI, LLM, Podman, 容器, Chatbot, RAG, 模型服务器, llamacpp]
generated: { by: "trae-ai", at: "2026-08-26T08:13:00Z" }
verified: { by: "process:source-code-to-okf-wiki", at: "2026-08-26T08:13:00Z" }
status: stable
stale_after: 2027-08-26
sources:
  - id: S-001
    resource: /references/readme-source.md
    title: 项目根目录 README.md
---

# ai-lab-recipes 容器化AI配方仓库

ai-lab-recipes 是由 Containers 项目维护的容器化 AI/LLM 应用配方仓库，提供了一套使用 Podman 在本地构建和运行 AI 应用的完整示例。项目采用**模型服务器 + AI 应用**双容器架构，帮助开发者无需依赖云服务即可在本地快速原型化 AI 应用，并支持平滑过渡到生产环境。

## 核心特性

- 🏗️ **双容器架构**：模型服务与应用逻辑分离，支持灵活组件替换
- 🤖 **多模型服务器**：支持 llamacpp_python、Ollama、Whisper.cpp 等多种推理后端
- 💬 **丰富配方**：Chatbot、RAG、Agent、代码生成、语音转文字、目标检测等
- 🔧 **多部署方式**：Quadlet本地systemd、Bootc可启动容器、Ansible自动化
- 🌍 **多语言支持**：Python、Node.js、Java Quarkus 等多语言应用实现
- 📦 **本地优先**：所有组件可离线运行，保护数据隐私

## 快速开始

最快的体验方式是使用 Podman Desktop AI Lab 扩展一键启动。如果偏好命令行：

```bash
# 1. 下载模型
cd models
curl -sLO https://huggingface.co/instructlab/granite-7b-lab-GGUF/resolve/main/granite-7b-lab-Q4_K_M.gguf

# 2. 启动Chatbot
cd ../recipes/natural_language_processing/chatbot
make quadlet
podman kube play build/chatbot.yaml

# 3. 访问 http://localhost:8501
```

更详细的步骤请参考 [Chatbot示例](examples/01-chatbot.md)。

## Bundle 结构

```
ai-lab-recipes/
├── index.md              # 本文件 - Bundle入口
├── log.md                # 变更日志
├── concepts/             # 核心概念文档
│   ├── index.md
│   ├── 00-introduction.md    # 双容器架构概览
│   ├── 01-model-servers.md   # 模型服务器选型
│   ├── 02-nlp-recipes.md     # NLP配方详解
│   └── 03-deployment.md      # 部署方式说明
├── examples/             # 实战示例
│   ├── index.md
│   ├── 01-chatbot.md         # Chatbot部署示例
│   └── 02-rag.md             # RAG应用部署示例
└── references/           # 信源参考
    ├── index.md
    └── readme-source.md      # 项目README整理
```

## 学习路径

### 新手入门（推荐顺序）

1. **[概念：配方架构概览](concepts/00-introduction.md)** - 理解双容器设计
2. **[示例：启动Chatbot](examples/01-chatbot.md)** - 动手跑通第一个应用
3. **[概念：模型服务器选型](concepts/01-model-servers.md)** - 了解后端选项
4. **[示例：RAG应用部署](examples/02-rag.md)** - 进阶：文档问答
5. **[概念：NLP配方概览](concepts/02-nlp-recipes.md)** - 探索更多应用类型
6. **[概念：部署方式](concepts/03-deployment.md)** - 生产部署选项

### 按场景导航

| 场景 | 推荐文档 |
|------|---------|
| 想快速跑起来看看 | [Chatbot示例](examples/01-chatbot.md) |
| 想基于自己的文档做问答 | [RAG示例](examples/02-rag.md) |
| 想了解架构设计 | [配方架构概览](concepts/00-introduction.md) |
| 不知道选哪个模型服务器 | [模型服务器选型](concepts/01-model-servers.md) |
| 要部署到生产/边缘设备 | [部署方式](concepts/03-deployment.md) |
| 想开发自己的AI应用 | [NLP配方概览](concepts/02-nlp-recipes.md) |

## 项目资源

- **源码仓库**：https://github.com/containers/ai-lab-recipes
- **预构建镜像**：quay.io/ai-lab/ （镜像清单见 ailab-images.md）
- **Podman Desktop**：https://podman-desktop.io （推荐GUI工具）
- **AI Lab扩展**：Podman Desktop 的 AI Lab 扩展提供图形化界面

## 支持的应用类型

| 类别 | 应用 |
|------|------|
| **自然语言处理** | Chatbot、RAG、Graph RAG、Agents、Codegen、Function Calling、Summarizer |
| **音频** | Audio to Text（语音转文字） |
| **计算机视觉** | Object Detection（目标检测） |
| **多模态** | Image Understanding（图像理解） |

## 相关 Bundle

- containers/podman：容器运行时基础
- 更多容器相关Bundle待补充

## 文档导航

- [概念文档入口](concepts/index.md)
- [示例文档入口](examples/index.md)
- [信源参考入口](references/index.md)
- [变更日志](log.md)

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
