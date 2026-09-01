---
title: TinyDiffusion 扩散模型
type: concept
bundle: /datawhale/tiny-universe
related:
  - /datawhale/tiny-universe/concepts/white-box-philosophy
  - /datawhale/tiny-universe/concepts/tiny-llm
sources:
  - https://github.com/datawhalechina/tiny-universe
---

# TinyDiffusion 扩散模型

## 定位

TinyDiffusion 是 tiny-universe 主体部分的第一个模块，**手工搭建最简化版本的 DDPM（Denoising Diffusion Probabilistic Models）模型**，从论文公式出发，对应到具体的训练与采样过程代码实现。2024 年 12 月 25 日发布，宣称两小时即可完成图像生成预训练。

## 解决的问题

Diffusion 模型是当下最流行的图像生成方案，生成效果优秀、训练过程稳定，但其公式原理对初学者过于复杂，从公式到代码的映射存在认知鸿沟。TinyDiffusion 旨在帮助学习者：

- 理解 Diffusion 模型的前向加噪与反向去噪原理
- 熟悉训练、推理、评估的整套流程
- 在个人硬件上完成端到端复现

## 核心技术点

### DDPM 前向过程

从原始图像逐步添加高斯噪声，直至图像退化为纯噪声。这一过程对应论文中的噪声调度（noise schedule）公式，代码中体现为按时间步 $t$ 叠加噪声。

### DDPM 反向过程

训练神经网络预测每一步添加的噪声，再从纯噪声出发逐步去噪，最终生成图像。TinyDiffusion 在 PyTorch 层手工实现这一采样循环。

### 训练与采样代码

项目强调"从论文中的公式出发，对应到具体的训练与采样过程代码实现"，不使用扩散模型封装库，使公式与代码一一对应。

## 白盒特征

- **资源极简**：两小时完成图像生成预训练，适合单卡学习者
- **公式可追溯**：每个代码块可对应到 DDPM 论文中的具体公式
- **流程完整**：覆盖训练 → 推理 → 评估全链路，而非仅展示推理

## 在项目中的位置

TinyDiffusion 属于"生成模型"方向，与 TinyLLM（语言模型）并列，共同构成"从零训练模型"层。它不依赖 RAG 或 Agent 模块，可独立学习。

项目 README 中配有 DDPM 架构图（`./content/TinyDiffusion/fig/ddpm.png`），直观展示前向与反向过程。

## 延伸

- 同属生成模型白盒实现：TinyLLM
- 方法论根源：白盒构建理念
