---
okf_version: "0.2"
type: facts
bundle: /datawhale/handy-ollama
sources: https://github.com/datawhalechina/handy-ollama
generated:
  by: okf-wiki-bot
  at: "2026-08-23T00:00:00Z"
status: stable
---

# handy-ollama 事实清单

本文件记录从 handy-ollama 源码文档中提取的章节结构与关键事实，作为知识包派生的事实基础。

## 项目元事实

| 编号 | 事实 | 信源 |
|------|------|------|
| F-001 | handy-ollama 是 Datawhale 开源的动手学 Ollama 教程，定位"从零开始实现 CPU 玩转大模型部署" | README.md |
| F-002 | 2025.11.06 被 Ollama 官方仓库收录，是目前唯一的 Tutorial | README.md:26 |
| F-003 | 开源协议为 CC BY-NC-SA 4.0 | README.md:143 |
| F-004 | 在线阅读地址 https://datawhalechina.github.io/handy-ollama/ | README.md:52 |
| F-005 | 仓库含 docs/（Markdown文档）、notebook/（源代码）、images/（图片）三大目录 | README.md:48 |

## 章节结构事实（与 docs/_sidebar.md 一致）

| 编号 | 章节 | 文件路径 | 关键内容 |
|------|------|----------|----------|
| F-010 | 第1章 Ollama 介绍 | C1/1. Ollama 介绍.md | 基础概念、核心特性、支持模型、常用命令 |
| F-020 | 第2章 Ollama 安装与配置 | C2/ | macOS/Windows/Linux/Docker 四平台安装 |
| F-021 | 2.1 macOS 安装与配置 | C2/1. Ollama 在 macOS 下的安装与配置.md | macOS 安装、Enchanted 客户端 |
| F-022 | 2.2 Windows 安装与配置 | C2/2. Ollama 在 Windows 下的安装与配置.md | Windows 安装、WSL2、环境变量 |
| F-023 | 2.3 Linux 安装与配置 | C2/3. Ollama 在 Linux 下的安装与配置.md | Linux 安装脚本、systemd 服务 |
| F-024 | 2.4 Docker 安装与配置 | C2/4. Ollama 在 Docker 下的安装与配置.md | docker pull ollama/ollama、CPU/GPU 镜像、端口映射 |
| F-030 | 第3章 自定义使用 Ollama | C3/ | 模型导入、存储位置、GPU 运行 |
| F-031 | 3.1 自定义导入模型 | C3/1. 自定义导入模型.md | GGUF 导入、Safetensors 导入、模型直接导入、自定义 Prompt、Modelfile |
| F-032 | 3.2 自定义模型存储位置 | C3/2. 自定义模型存储位置.md | OLLAMA_MODELS 环境变量、Windows/Linux/macOS 路径配置、模型迁移 |
| F-033 | 3.3 自定义在 GPU 中运行 | C3/3. 自定义在 GPU 中运行.md | OLLAMA_GPU_LAYER、CUDA_VISIBLE_DEVICES、NVIDIA/AMD GPU 配置 |
| F-040 | 第4章 Ollama REST API | C4/ | 原生 API、多语言 SDK |
| F-041 | 4.1 Ollama API 使用指南 | C4/1. Ollama API 使用指南.md | /api/generate、/api/chat、/api/embed、模型管理端点、流式/非流式、JSON 模式、多模态 |
| F-042 | 4.2 Python 中使用 Ollama API | C4/2. 在 Python 中使用 Ollama API.md | ollama Python 库、requests 调用、流式响应 |
| F-043 | 4.3 Java 中使用 Ollama API | C4/3. 在 Java 中使用 Ollama API.md | OkHttp、Spring AI 集成 |
| F-044 | 4.4 JavaScript 中使用 Ollama API | C4/4. 在 JavaScript 中使用 Ollama API.md | Node.js fetch、流式处理 |
| F-045 | 4.5 C++ 中使用 Ollama API | C4/5. 在 C++ 中使用 Ollama API.md | libcurl 调用、cpr 库 |
| F-046 | 4.6 Golang 中使用 Ollama API | C4/6. 在 Golang 中使用 Ollama API.md | ollama-go 客户端、chat/generate/structured output |
| F-050 | 第5章 Ollama 在 LangChain 中的使用 | C5/ | Python/JavaScript 双语言集成 |
| F-051 | 5.1 Python 集成 | C5/1. Ollama 在 LangChain 中的使用 - Python 集成.md | langchain-ollama、ChatPromptTemplate、链式调用、多模态、工具调用、RAG |
| F-052 | 5.2 JavaScript 集成 | C5/2. Ollama 在 LangChain 中的使用 - JavaScript 集成.md | langchainjs、base_chat/advanced_prompt/tool/multimodal |
| F-060 | 第6章 Ollama 可视化界面部署 | C6/ | FastAPI/WebUI 两种方案 |
| F-061 | 6.1 FastAPI 部署可视化界面 | C6/1. 使用 FastAPI 部署 Ollama 可视化对话界面.md | FastAPI + WebSocket + 静态前端、流式对话 |
| F-062 | 6.2 WebUI 部署可视化界面 | C6/2. 使用 WebUI 部署 Ollama 可视化对话界面.md | open-webui (ollama-webui-lite)、Node.js 部署、Docker 部署 |
| F-070 | 第7章 应用案例 | C7/ | Copilot/Dify/RAG/Agent 七案例 |
| F-071 | 7.1 搭建本地 AI Copilot 编程助手 | C7/1. 搭建本地的 AI Copilot 编程助手.md | Continue 插件、VS Code/JetBrains、本地模型接入 |
| F-072 | 7.2 Dify 接入 Ollama 本地模型 | C7/2. Dify 接入 Ollama 部署的本地模型.md | Dify 模型供应商配置、LLM/Embedding 接入、Docker 网络 |
| F-073 | 7.3 LangChain 搭建本地 RAG | C7/3. 使用 LangChain 搭建本地 RAG 应用.md | 文档加载、分块、向量检索、Ollama LLM |
| F-074 | 7.4 LlamaIndex 搭建本地 RAG | C7/4. 使用 LlamaIndex 搭建本地 RAG 应用.md | LlamaIndex 查询引擎、react/openai agent 模式 |
| F-075 | 7.5 LangChain 实现本地 Agent | C7/5. 使用 LangChain 实现本地 Agent.md | 工具调用、ReAct、本地 Agent |
| F-076 | 7.6 LlamaIndex 实现本地 Agent | C7/6. 使用 LlamaIndex 实现本地 Agent.md | LlamaIndex Agent、工具注册 |
| F-077 | 7.7 DeepSeek R1 + Ollama 本地 RAG | C7/7. 使用 DeepSeek R1 和 Ollama 实现本地 RAG 应用.md | DeepSeek R1 推理模型、RAG 结合、PDF 解析 |

## Ollama 核心事实

| 编号 | 事实 | 信源 |
|------|------|------|
| F-101 | Ollama 创建于 2023年6月26日，开源大型语言模型服务工具 | C1/1:7 |
| F-102 | Ollama 自动监测本地计算资源，有 GPU 优先用 GPU，无 GPU 用 CPU | C1/1:13 |
| F-103 | Ollama 将模型权重、配置和数据捆绑成 Modelfile 包 | C1/1:23 |
| F-104 | Ollama 支持 Llama 3.1 等模型的工具调用（tool calling） | C1/1:24 |
| F-105 | 运行 7B 模型至少需 8GB 内存，13B 需 16GB，33B 需 32GB | C1/1:248 |
| F-106 | Ollama 默认 API 端口为 11434 | C7/2:18 |
| F-107 | Ollama 常用命令：serve/run/pull/push/create/list/ps/rm/cp/show/stop | C1/1:259-271 |
| F-108 | 模型默认存储路径：macOS ~/.ollama/models/，Linux /usr/share/ollama/.ollama/models，Windows C:\Users\<user>\.ollama\models | C5/1:57-60 |
| F-109 | REST API 端点：POST /api/generate（生成补全）、POST /api/chat（对话补全）、POST /api/embed（嵌入） | C4/1 |
| F-110 | /api/generate 支持 stream/format(json)/images/options(seed,temperature)/keep_alive 参数 | C4/1:32-46 |
| F-111 | /api/chat 支持 messages(role: system/user/assistant/tool)、tools、tool_calls | C4/1:279-288 |
| F-112 | Modelfile 通过 FROM 指令指定模型源（GGUF 文件、Safetensors 目录、已有模型名） | C3/1:52,109 |
| F-113 | ollama create <name> -f Modelfile 从 Modelfile 创建自定义模型 | C3/1:61 |
| F-114 | Docker 镜像：ollama/ollama（CPU/Nvidia GPU）、ollama/ollama:rocm（AMD GPU） | C2/4:30-34 |
| F-115 | Open WebUI Docker 部署命令映射 3000:8080 端口，通过 host.docker.internal 访问宿主机 Ollama | C6/2:57 |
| F-116 | OLLAMA_MODELS 环境变量控制模型存储位置 | C3/2:45 |
| F-117 | OLLAMA_GPU_LAYER=cuda 启用 NVIDIA GPU 加速，CUDA_VISIBLE_DEVICES 指定 GPU | C3/3:30,49 |
| F-118 | Ollama 提供 OpenAI 兼容接口（参考 https://ollama.com/blog/openai-compatibility） | C3/1:346 |

## 代码资产事实

| 编号 | 事实 | 信源 |
|------|------|------|
| F-201 | notebook/C3/ 含4个模型导入实践：GGUF导入、Safetensors导入、模型直接导入、自定义Prompt | notebook/C3/ |
| F-202 | notebook/C4/ 含 Python/C++/Golang/Java(Spring AI) API 示例代码 | notebook/C4/ |
| F-203 | notebook/C5/ 含 LangChain Python(ipynb) 和 JavaScript(base_chat/tool/multimodal/advanced_prompt) 集成代码 | notebook/C5/ |
| F-204 | notebook/C6/fastapi_chat_app/ 含 FastAPI+WebSocket 可视化对话完整应用（app.py + static/index.html） | notebook/C6/ |
| F-205 | notebook/C7/ 含 DeepSeek_R1_RAG、LangChain_Agent、LangChain_RAG、LlamaIndex_Agent、LlamaIndex_RAG 五个应用案例代码 | notebook/C7/ |
