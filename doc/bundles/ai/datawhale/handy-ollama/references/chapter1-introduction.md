---
okf_version: "0.2"
type: reference
title: "第一章 Ollama 介绍"
bundle: /datawhale/handy-ollama
sources:
  - https://github.com/datawhalechina/handy-ollama/blob/main/docs/C1/1.%20Ollama%20%E4%BB%8B%E7%BB%8D.md
tags: [chapter1, introduction, overview, cli, models]
status: stable
---

# 第一章 Ollama 介绍

## 信源定位

- **源码路径**：`docs/C1/1. Ollama 介绍.md`
- **在线阅读**：[第一章](https://datawhalechina.github.io/handy-ollama/#/C1/1.%20Ollama%20%E4%BB%8B%E7%BB%8D)
- **内容性质**：概念入门，定义 Ollama 及其核心能力

## 章节结构

1. **Ollama 简介** — "Get up and running with large language models locally"，创建于 2023年6月26日，开源 LLM 服务工具
2. **Ollama 特点** — 开源免费、简单易用、多平台、模型丰富、Modelfile 打包、工具调用、低资源占用、隐私保护、社区活跃
3. **支持的模型** — DeepSeek-R1、Llama3.x、Gemma2、Qwen2、mistral、Phi4、codellama、llava、nomic-embed-text 等数百个模型，含参数量和下载命令
4. **Ollama 常用命令** — serve/run/pull/push/create/show/list/ps/cp/rm/stop/help，多行输入 `"""`，退出 `/bye`

## 关键事实

- Ollama 自动监测本地计算资源，有 GPU 优先 GPU，无 GPU 使用 CPU
- 运行 7B 模型至少需 8GB 内存，13B 需 16GB，33B 需 32GB
- Ollama 将模型权重、配置和数据捆绑为 Modelfile 包
- 支持 Llama 3.1 等模型的工具调用（tool calling）
- 模型库地址：https://ollama.com/library

## 关联概念

- [Ollama 架构与安装](../concepts/ollama-architecture-installation.md) — 本章的特点和命令体系在此概念中展开
- [模型管理与 Modelfile](../concepts/model-management-modelfile.md) — Modelfile 打包机制的深入解析
