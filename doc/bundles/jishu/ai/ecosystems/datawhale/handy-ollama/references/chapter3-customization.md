---
okf_version: "0.2"
type: reference
title: "第三章 自定义使用 Ollama"
bundle: /datawhale/handy-ollama
sources:
  - https://github.com/datawhalechina/handy-ollama/blob/main/docs/C3/
tags: [chapter3, modelfile, gguf, safetensors, gpu, storage, customization]
status: stable
---

# 第三章 自定义使用 Ollama

## 信源定位

- **源码路径**：`docs/C3/`（3 节）+ `notebook/C3/`（4 个实践 notebook）
- **在线阅读**：[第三章](https://datawhalechina.github.io/handy-ollama/#/C3/)
- **内容性质**：进阶配置，模型导入、存储和 GPU 自定义

## 章节结构

| 节 | 文件 | 核心内容 |
|----|------|----------|
| 3.1 | `1. 自定义导入模型.md` | 从 GGUF 导入、从 Safetensors 导入、模型直接导入、自定义 Prompt、Modelfile 创建 |
| 3.2 | `2. 自定义模型存储位置.md` | OLLAMA_MODELS 环境变量、Windows/Linux/macOS 路径配置、模型迁移 |
| 3.3 | `3. 自定义在 GPU 中运行.md` | OLLAMA_GPU_LAYER=cuda、CUDA_VISIBLE_DEVICES、NVIDIA/AMD GPU 配置、Linux GPU 选择脚本 |

## 关键事实

- GGUF（GPT-Generated Unified Format）是 Ollama 原生支持的模型格式
- 支持直接导入的 Safetensors 架构：LlamaForCausalLM、MistralForCausalLM、GemmaForCausalLM
- `ollama create <name> -f Modelfile` 从 Modelfile 创建模型
- Modelfile 的 FROM 指令支持 GGUF 文件路径、Safetensors 目录、已有模型名
- OLLAMA_MODELS 环境变量控制模型存储路径
- Windows 默认路径：`C:\Users\<用户名>\.ollama\models`
- macOS 默认路径：`~/.ollama/models/`
- Linux 默认路径：`/usr/share/ollama/.ollama/models`
- OLLAMA_GPU_LAYER=cuda 启用 NVIDIA GPU 加速
- `nvidia-smi -L` 查看 GPU UUID（推荐使用 UUID 而非编号）
- OpenAI 兼容性参考：https://ollama.com/blog/openai-compatibility

## 代码资产

- `notebook/C3/1.从GGUF直接导入/`：GGUF 导入 Modelfile 和 notebook
- `notebook/C3/2.safetensors导入/`：Safetensors 导入实践
- `notebook/C3/3.模型直接导入/`：模型直接导入实践
- `notebook/C3/4.自定义Prompt实践/`：自定义 Prompt 角色实践

## 关联概念

- [模型管理与 Modelfile](../concepts/model-management-modelfile.md) — 本章内容的概念化整理
- [使用 Modelfile 自定义模型](../examples/custom-model-modelfile.md) — 三种导入方式的实战示例
