---
type: concept
title: "模型管理与 Modelfile"
bundle: /datawhale/handy-ollama
description: "Modelfile 模型打包机制、GGUF/Safetensors 导入方式、模型全生命周期命令、存储路径与 GPU 加速配置"
sources: https://github.com/datawhalechina/handy-ollama/tree/main/docs/C3
related:
  - /datawhale/handy-ollama/concepts/ollama-architecture-installation
  - /datawhale/handy-ollama/concepts/api-openai-compatibility
  - /datawhale/handy-ollama/concepts/production-deployment
  - /datawhale/handy-ollama/references/chapter3-customization
  - /datawhale/handy-ollama/examples/custom-model-modelfile
tags: [modelfile, gguf, safetensors, model-management, gpu, storage]
status: stable
---

# 模型管理与 Modelfile

## 核心理解

Ollama 将模型权重、配置和提示词模板捆绑为一个称为 **Modelfile** 的包，这是 Ollama 模型管理的核心抽象。Modelfile 的概念类似于 Dockerfile——它以声明式文本定义模型的来源、系统提示词、推理参数等，使得模型配置可以像代码一样版本化、复现和分享。

模型管理涵盖三个维度：**模型获取**（从注册表拉取或从外部文件导入）、**模型定制**（通过 Modelfile 创建自定义模型）、**模型运维**（存储位置、GPU 调度、生命周期命令）。

## Modelfile 机制

### 基本结构

Modelfile 是一个纯文本文件，通过指令定义模型：

```dockerfile
# 从 GGUF 文件创建
FROM ./Qwen2-0.5B.Q3_K_M.gguf

# 或从已有模型创建
FROM llama3.1

# 系统提示词
SYSTEM """你是一个乐于助人的AI助手，请用简洁的中文回答问题。"""

# 推理参数
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER stop "Human:"
PARAMETER stop "Assistant:"
```

### 核心指令

| 指令 | 作用 | 示例 |
|------|------|------|
| `FROM` | 指定模型来源（GGUF 文件、Safetensors 目录、已有模型名） | `FROM ./model.gguf` |
| `SYSTEM` | 设置系统提示词 | `SYSTEM "You are a helpful assistant."` |
| `PARAMETER` | 设置推理参数（temperature、top_p、stop 等） | `PARAMETER temperature 0.8` |
| `TEMPLATE` | 自定义提示词模板 | `TEMPLATE "{{ .System }}..."` |
| `ADAPTER` | 指定 LoRA 适配器 | `ADAPTER ./adapter.safetensors` |
| `LICENSE` | 模型许可证 | `LICENSE """MIT"""` |

### 创建模型

在 Modelfile 所在目录执行：

```bash
ollama create mymodel -f Modelfile
ollama run mymodel
```

## 三种模型导入方式

### 方式一：从 GGUF 导入

GGUF（GPT-Generated Unified Format）是 Ollama 最原生支持的模型格式，专为 CPU/GPU 推理设计，支持多种量化级别：

```dockerfile
# Modelfile
FROM ./Qwen2-0.5B.Q3_K_M.gguf
```

```bash
ollama create mymodel -f Modelfile
ollama run mymodel
```

GGUF 的优势在于单文件分发、量化压缩（Q3_K_M、Q4_K_M 等），以及跨平台兼容性。

### 方式二：从 Safetensors 导入

Safetensors 是一种安全的模型权重存储格式。Ollama 支持直接导入特定架构的 Safetensors 模型：

- `LlamaForCausalLM`
- `MistralForCausalLM`
- `GemmaForCausalLM`

```dockerfile
FROM ./llama-3-8b-bnb-4bit
```

对于不支持的架构，可先将 Safetensors 转换为 GGUF 格式再导入。

### 方式三：从已有模型导入并定制

基于 Ollama 注册表中的模型，通过 Modelfile 覆盖系统提示词和参数，创建定制化模型：

```dockerfile
FROM llama3.1
SYSTEM """你是马里奥，用马里奥的口吻回答所有问题。"""
PARAMETER temperature 0.9
```

```bash
ollama create mario -f Modelfile
ollama run mario
```

这种方式无需重新下载权重，仅覆盖配置，极其轻量。

## 模型全生命周期命令

```bash
# 拉取模型
ollama pull llama3.1           # 从注册表下载
ollama pull nomic-embed-text   # 拉取嵌入模型

# 查看模型
ollama list                    # 列出本地所有模型
ollama show llama3.1           # 查看模型详细信息（参数、模板、系统提示）
ollama ps                      # 查看正在运行的模型及内存占用

# 运行与停止
ollama run llama3.1            # 运行并进入交互
ollama stop llama3.1           # 停止运行中的模型（释放内存）

# 复制与删除
ollama cp llama3.1 my-llama    # 复制模型
ollama rm my-llama             # 删除本地模型

# 推送
ollama push mymodel            # 推送到注册表（需登录）
```

## 自定义模型存储位置

Ollama 默认将模型存储在系统盘，多模型场景下可能导致空间不足。通过 `OLLAMA_MODELS` 环境变量可自定义存储路径：

| 操作系统 | 默认路径 | 配置方式 |
|----------|----------|----------|
| macOS | `~/.ollama/models/` | `launchctl setenv OLLAMA_MODELS /path/to/models` |
| Linux | `/usr/share/ollama/.ollama/models` | systemd 服务环境变量或 `/etc/systemd/system/ollama.service` |
| Windows | `C:\Users\<用户名>\.ollama\models` | 系统变量新建 `OLLAMA_MODELS=D:\Ollama\Models` |

### Windows 配置要点

1. **首次安装时指定路径**：`.\OllamaSetup.exe /DIR="D:\Ollama\Models"`
2. **安装后修改环境变量（推荐）**：系统变量 → 新建 `OLLAMA_MODELS` → 重启 Ollama 服务
3. **迁移现有模型**：停止 Ollama 进程 → 复制 models 目录到新位置 → 设置环境变量 → 重启

> **注意**：路径不能包含中文或空格。

## GPU 加速配置

Ollama 默认自动检测 GPU，但也支持手动配置：

### NVIDIA GPU

```bash
# 环境变量设置
OLLAMA_GPU_LAYER=cuda          # 启用 CUDA 加速

# 多 GPU 时指定特定 GPU
CUDA_VISIBLE_DEVICES=GPU-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

通过 `nvidia-smi -L` 查看 GPU UUID（推荐使用 UUID 而非编号，因编号可能随驱动更新变化）。

验证 GPU 是否生效：

```bash
ollama run deepseek-r1:1.5b
ollama ps   # 查看 PROCESSOR 列是否显示 GPU
```

### AMD GPU

使用 ROCm 版本的 Docker 镜像：`ollama/ollama:rocm`。

### Linux GPU 选择脚本

Linux 下可通过脚本灵活选择 GPU，设置 `CUDA_VISIBLE_DEVICES` 环境变量控制使用哪些 GPU 设备。

## 模型版本与标签

Ollama 使用 `模型名:标签` 的格式管理模型版本：

```bash
ollama run llama3.1           # 默认 latest 标签
ollama run llama3.1:70b       # 指定 70B 参数版本
ollama run llama3.2:1b        # 指定 1B 轻量版本
ollama run llama3.2-vision    # 多模态版本
ollama run deepseek-r1:671b   # 大参数版本
```

同一模型的不同标签共享模型名前缀，便于切换和管理。

## 交叉阅读

- Ollama 架构和 CLI 命令基础详见 [Ollama 架构与安装](ollama-architecture-installation.md)
- 通过 API 进行模型管理（创建/拉取/删除）详见 [API 与 OpenAI 兼容接口](api-openai-compatibility.md)
- Modelfile 自定义模型的完整实战详见 [使用 Modelfile 自定义模型](../examples/custom-model-modelfile.md)
- 生产环境多模型部署和 GPU 调度详见 [生产部署实践](production-deployment.md)
