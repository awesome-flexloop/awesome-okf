---
title: TinyLLM 大语言模型
type: concept
bundle: /datawhale/tiny-universe
related:
  - /datawhale/tiny-universe/concepts/white-box-philosophy
  - /datawhale/tiny-universe/concepts/tiny-diffusion
  - /datawhale/tiny-universe/concepts/tiny-rag
  - /datawhale/tiny-universe/concepts/tiny-agent
sources:
  - https://github.com/datawhalechina/tiny-universe
---

# TinyLLM 大语言模型

## 定位

TinyLLM 是 tiny-universe 项目结构中的核心模块，**实现一个简单的大语言模型，从训练 tokenizer 开始，到训练模型，再到使用模型生成文本**。仅使用 NumPy 和 PyTorch，显存占用约 2G，训练时间数小时。

> 注：README 主体部分将该模块称为"TinyLlama3"（描述为"逐步预训练一个手搓大模型"），项目结构中目录名为 `TinyLLM`。二者指向同一项目，News 中"2024.10.28 TinyLlama3，从零上手 Llama 预训练到加载模型推理，2G 显存即可完成"与项目结构中 TinyLLM 的描述一致。

## 解决的问题

大模型预训练通常被认为需要海量算力与复杂工程，普通学习者难以触及。TinyLLM 将预训练流程压缩到单卡 2G 显存、数小时即可完成，使学习者能够端到端体验：

- Tokenizer 训练
- 模型训练
- 文本生成

## 核心技术点

### Tokenizer 训练

从零训练 tokenizer，理解分词、词表构建、编码/解码过程，而非直接使用预训练 tokenizer。

### 模型训练

在 PyTorch 层实现大语言模型的训练循环，包括：

- 模型结构定义
- 损失函数与反向传播
- 优化器配置
- 训练数据流水线

### 文本生成

实现自回归生成逻辑，从训练好的模型采样文本。

### 极简依赖

仅依赖 NumPy 与 PyTorch，不使用 transformers、accelerate 等高层库，确保每个训练环节白盒可见。

## 白盒特征

- **硬件门槛极低**：2G 显存即可运行，使大多数个人电脑可复现
- **全流程覆盖**：tokenizer → 训练 → 生成，无断环
- **依赖最小化**：NumPy + PyTorch，无框架遮蔽

## 在项目中的位置

TinyLLM 位于"模型训练层"，是 TinyTransformer（基础组件）的自然延伸，也是 TinyRAG、TinyAgent 等增强系统的模型底座。Qwen-Blog 模块则从另一个角度——以输入 tensor 视角解剖现有 LLM（Qwen2）内部结构——与 TinyLLM 形成互补：一个是从零搭建，一个是拆解现有模型。

## 相关模块

- 基础组件：TinyTransformer（手工搭建 Transformer）
- 结构解剖：Qwen-Blog（深入 Qwen2 内部，含 GQA、RoPE、Attention Mask）
- 生成模型并列：TinyDiffusion（图像生成）
- 应用层：TinyRAG、TinyAgent

## 延伸

- 方法论根源：白盒构建理念
- 生成模型对照：TinyDiffusion
