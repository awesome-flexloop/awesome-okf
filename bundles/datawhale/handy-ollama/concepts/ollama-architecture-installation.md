---
type: concept
title: "Ollama 架构与安装"
bundle: /datawhale/handy-ollama
description: "Ollama 的定位、核心特性、自动资源探测机制，以及 macOS/Windows/Linux/Docker 四平台安装配置"
sources: https://github.com/datawhalechina/handy-ollama/tree/main/docs/C1
related:
  - /datawhale/handy-ollama/concepts/model-management-modelfile
  - /datawhale/handy-ollama/concepts/api-openai-compatibility
  - /datawhale/handy-ollama/references/chapter1-introduction
  - /datawhale/handy-ollama/references/chapter2-installation
  - /datawhale/handy-ollama/examples/quickstart-first-model
tags: [ollama, architecture, installation, docker, cli]
status: stable
---

# Ollama 架构与安装

## 核心理解

Ollama 是一个开源的大型语言模型服务工具，其官方定位是"Get up and running with large language models locally"（在本地启动并运行大型语言模型）。它创建于 2023 年 6 月 26 日，通过简洁的命令行界面和服务器，让用户能在消费级 PC 上下载、运行和管理各种开源 LLM。

Ollama 的核心设计哲学是**极简部署**——传统 LLM 部署需要配置 Python 环境、CUDA 工具包、模型权重下载和推理框架，而 Ollama 将这些复杂性全部封装，用户只需一条命令即可运行模型。

## 九大核心特点

| 特点 | 说明 |
|------|------|
| 开源免费 | Ollama 及支持的模型完全开源免费 |
| 简单易用 | 几条命令即可启动运行，无需复杂配置 |
| 支持多平台 | Mac、Linux、Windows 原生安装 + Docker 镜像 |
| 模型丰富 | 支持 DeepSeek-R1、Llama3.x、Gemma2、Qwen2 等数百个模型 |
| 功能齐全 | Modelfile 将权重、配置、数据捆绑成包管理 |
| 支持工具调用 | Llama 3.1 等模型支持 tool calling |
| 资源占用低 | 优化 GPU 使用，资源有限环境也能运行 |
| 隐私保护 | 所有数据处理在本地完成，不上传云端 |
| 社区活跃 | 庞大活跃社区，模型和工具持续增长 |

## 自动资源探测机制

Ollama 启动时会自动监测本地计算资源，这是其"CPU 也能玩转大模型"的关键：

- **有 GPU 时**：优先使用 GPU 资源（NVIDIA CUDA 或 AMD ROCm），推理速度更快
- **无 GPU 时**：直接使用 CPU 资源进行推理
- **量化支持**：通过 GGUF 量化格式，7B 模型仅需约 4.7GB 内存，1.5B 模型仅需约 1GB

> **内存需求参考**：运行 7B 模型至少需 8GB 内存，13B 需 16GB，33B 需 32GB。

## 四平台安装

### macOS

下载安装包或使用 Homebrew：

```bash
# 官网下载安装
# https://ollama.com/download

# 安装后验证
ollama --version
```

macOS 用户还可使用 [Enchanted](https://github.com/AugustDev/enchanted) 等兼容 Ollama 的第三方客户端。

### Windows

Windows 提供原生安装程序（OllamaSetup.exe），同时支持 WSL2 环境。安装后 Ollama 以后台服务方式运行，可通过系统托盘图标管理。

### Linux

使用官方一键安装脚本：

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Linux 安装后自动配置 systemd 服务，可通过 `systemctl status ollama` 查看运行状态。

### Docker（跨平台推荐）

Docker 方式提供最一致的环境隔离：

```bash
# CPU 或 NVIDIA GPU
docker pull ollama/ollama

# AMD GPU
docker pull ollama/ollama:rocm

# 运行容器并映射 API 端口
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama

# 指定版本
docker pull ollama/ollama:0.3.0
```

Docker 部署时模型数据通过 volume（`ollama:/root/.ollama`）持久化，避免容器删除后模型丢失。

## CLI 命令体系

Ollama 提供完整的命令行工具，安装后终端输入 `ollama` 即可查看帮助：

| 命令 | 描述 |
|------|------|
| `ollama serve` | 启动 Ollama 服务 |
| `ollama run <model>` | 运行模型（自动拉取并进入交互） |
| `ollama pull <model>` | 从注册表拉取模型 |
| `ollama push <model>` | 将模型推送到注册表 |
| `ollama create <name> -f Modelfile` | 从 Modelfile 创建模型 |
| `ollama list` | 列出本地所有模型 |
| `ollama ps` | 列出正在运行的模型 |
| `ollama show <model>` | 显示模型详细信息 |
| `ollama cp <source> <target>` | 复制模型 |
| `ollama rm <model>` | 删除模型 |
| `ollama stop <model>` | 停止运行中的模型 |

### 交互模式技巧

运行 `ollama run llama3.1` 进入交互模式后：

- 使用 `"""` 可以进行多行输入，再次输入 `"""` 结束
- 输入 `/bye` 退出模型推理
- 终止所有 Ollama 进程（Windows PowerShell）：

```powershell
Get-Process | Where-Object {$_.ProcessName -like '*ollama*'} | Stop-Process
```

## 服务架构

Ollama 安装后作为后台服务运行，默认监听 `http://localhost:11434`，提供 REST API 接口。这一架构意味着：

1. CLI 命令实际上是与本地 Ollama 服务通信的客户端
2. 任何能发送 HTTP 请求的应用都可以调用 Ollama
3. 服务启动后模型加载到内存，后续请求无需重复加载（默认 keep_alive 5 分钟）

这一客户端-服务器架构为后续的 API 调用、WebUI 集成和多语言 SDK 奠定了基础。

## 交叉阅读

- 模型的自定义导入和生命周期管理详见 [模型管理与 Modelfile](model-management-modelfile.md)
- 通过 HTTP API 与 Ollama 服务交互详见 [API 与 OpenAI 兼容接口](api-openai-compatibility.md)
- 第一个模型的完整启动流程实战详见 [快速启动第一个本地模型](../examples/quickstart-first-model.md)
