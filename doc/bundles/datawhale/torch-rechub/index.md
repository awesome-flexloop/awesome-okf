---
title: Torch-RecHub 知识束
type: index
bundle: torch-rechub
version: 0.8.0
description: >
  Torch-RecHub 是一个基于 PyTorch 的轻量级推荐系统框架，覆盖排序（CTR）、召回匹配、
  多任务学习和生成式推荐四大任务范式，提供特征描述符体系、可插拔 Trainer、
  ONNX 非侵入式导出、向量检索服务等全链路能力。
sources:
  - https://github.com/datawhalechina/torch-rechub
concepts:
  - /datawhale/torch-rechub/concepts/model-architecture
  - /datawhale/torch-rechub/concepts/feature-engineering
  - /datawhale/torch-rechub/concepts/trainer-system
  - /datawhale/torch-rechub/concepts/data-pipeline
  - /datawhale/torch-rechub/concepts/onnx-export
  - /datawhale/torch-rechub/concepts/multi-task-learning
  - /datawhale/torch-rechub/concepts/tracking-and-visualization
references:
  - /datawhale/torch-rechub/references/models-module
  - /datawhale/torch-rechub/references/trainers-module
  - /datawhale/torch-rechub/references/basic-layers-module
  - /datawhale/torch-rechub/references/data-and-utils-module
  - /datawhale/torch-rechub/references/serving-and-onnx-module
examples:
  - /datawhale/torch-rechub/examples/deepfm-ctr-training
  - /datawhale/torch-rechub/examples/dssm-matching-export
---

# Torch-RecHub

Torch-RecHub 是 Datawhale 开源的 PyTorch 推荐系统工具箱（v0.8.0），旨在以统一、简洁的 API 提供主流推荐模型的实现与训练能力。

## 核心能力

- **排序模型**：DeepFM、WideDeep、DCN/DCNv2、DIN、DIEN、AutoInt、FiBiNet、BST 等 13 种
- **召回模型**：DSSM、YoutubeDNN、MIND、GRU4Rec、SASRec、ComiRec、SINE、STAMP 等 12 种
- **多任务模型**：SharedBottom、MMOE、PLE、ESMM、AITM
- **生成式模型**：HSTU、HLLM、RQVAE、TIGER（需 transformers）
- **统一 Trainer**：CTRTrainer / MatchTrainer / MTLTrainer / SeqTrainer
- **ONNX 导出与量化**：非侵入式导出，支持双塔分塔导出、INT8/FP16 量化
- **向量检索服务**：Annoy / FAISS / Milvus 三种后端
- **实验跟踪**：Weights & Biases / SwanLab / TensorBoardX

## 快速导航

### 概念文档

| 文档 | 内容 |
|------|------|
| [模型体系](/datawhale/torch-rechub/concepts/model-architecture) | 四大类模型的组织方式、基类约定、代表性模型 |
| [特征工程](/datawhale/torch-rechub/concepts/feature-engineering) | SparseFeature/SequenceFeature/DenseFeature、EmbeddingLayer、池化 |
| [Trainer 系统](/datawhale/torch-rechub/concepts/trainer-system) | 四类 Trainer 的职责、训练循环、损失模式、早停与正则化 |
| [数据管道](/datawhale/torch-rechub/concepts/data-pipeline) | Dataset、DataGenerator、序列特征生成、Parquet 流式读取 |
| [ONNX 导出与部署](/datawhale/torch-rechub/concepts/onnx-export) | ONNXExporter、ONNXWrapper、动态轴、量化、向量检索 |
| [多任务学习](/datawhale/torch-rechub/concepts/multi-task-learning) | MMOE/PLE/ESMM 架构、uwl/metabalance/gradnorm 加权 |
| [实验跟踪与可视化](/datawhale/torch-rechub/concepts/tracking-and-visualization) | BaseLogger、torchview 模型可视化、评估指标 |

### 参考文档

- [模型模块源码登记](/datawhale/torch-rechub/references/models-module)
- [Trainer 模块源码登记](/datawhale/torch-rechub/references/trainers-module)
- [基础层模块源码登记](/datawhale/torch-rechub/references/basic-layers-module)
- [数据与工具模块源码登记](/datawhale/torch-rechub/references/data-and-utils-module)
- [服务与 ONNX 模块源码登记](/datawhale/torch-rechub/references/serving-and-onnx-module)

### 示例

- [DeepFM CTR 训练示例](/datawhale/torch-rechub/examples/deepfm-ctr-training)
- [DSSM 召回训练与 ONNX 导出](/datawhale/torch-rechub/examples/dssm-matching-export)

## 安装

```bash
pip install torch-rechub
# 含全部可选依赖
pip install torch-rechub[all]
```

要求 Python >= 3.9，PyTorch >= 1.10.0。

## 源码

- GitHub：https://github.com/datawhalechina/torch-rechub
- 文档：https://datawhalechina.github.io/torch-rechub/
- 许可证：MIT
