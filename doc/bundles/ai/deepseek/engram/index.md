---
type: bundle
okf_version: "0.2"
scope: engram
name: engram
version: "1.0.0"
source: https://github.com/deepseek-ai/Engram
description: Engram——通过可扩展 N-gram 查找实现条件记忆，为大语言模型引入新的稀疏性轴
---

# Engram

**Engram**（论文：*Conditional Memory via Scalable Lookup: A New Axis of Sparsity for Large Language Models*）是 DeepSeek 提出的新型模型架构模块，为 Transformer 引入**条件记忆（Conditional Memory）**——将经典 N-gram 嵌入现代化，通过确定性哈希实现 O(1) 复杂度的知识查找，作为 MoE（混合专家）之外的互补稀疏性轴。

- **核心思想**：MoE 通过条件计算扩展容量，Engram 通过条件记忆扩展容量——记忆"是什么"，计算"怎么推理"
- **许可证**：Apache 2.0
- **演示代码**：`engram_demo_v1.py`（展示核心数据流）

## 核心创新

| 特性 | 说明 |
|---|---|
| **O(1) 查找** | N-gram 哈希确定性寻址，无需路由网络 |
| **条件记忆** | 与 MoE 互补的稀疏性轴，专门存储静态知识/模式 |
| **多头哈希** | 8 个独立质数模哈希头，显著降低碰撞概率 |
| **门控融合** | 动态 query 与记忆 key 的自适应融合，非简单替换 |
| **Host 内存卸载** | 确定性寻址支持大规模嵌入表卸载到 CPU，推理开销极小 |
| **U 型缩放定律** | 神经计算与静态记忆的最优分配理论 |

## 核心成绩

- Engram-27B 在**等参数、等 FLOPs** 条件下，于知识、推理、代码、数学全领域一致优于 MoE 基线
- 机制分析表明 Engram 减轻了早期层静态模式重建负担，保留有效深度用于复杂推理
- 长上下文训练表现一致提升

## 架构概览

Engram 插入 Transformer 浅层（第 1 层、第 15 层），通过 N-gram 哈希表检索静态记忆，经门控融合和短卷积后以残差方式注入隐藏状态：

```
Token IDs → 压缩分词器 → N-gram 哈希 → 多头嵌入检索
    ↓
门控融合（query 来自动态隐藏状态，key 来自记忆嵌入）
    ↓
短卷积（局部上下文扩展）
    ↓
残差连接 → Attention → MoE
```

## 快速开始

```bash
pip install torch numpy transformers sympy
python engram_demo_v1.py
# ✅ Forward Complete!
```

## 文档导航

### 核心概念

- [总览](/ai/deepseek/engram/concepts/overview) — Engram 定位、条件记忆理念、与 MoE 的关系、U 型缩放定律
- [N-gram 哈希与门控融合机制](/ai/deepseek/engram/concepts/ngram-hashing-and-gating) — 哈希函数设计、多头嵌入、门控机制、短卷积、完整数据流

### API 参考

- [模块 API 参考](/ai/deepseek/engram/references/module-api) — EngramConfig、核心组件类、前向传播接口、TransformerBlock 集成
- [配置策略与系统效率](/ai/deepseek/engram/references/configuration-and-efficiency) — Host 内存卸载、27B 配置、作用机制分析

### 使用示例

- [运行演示](/ai/deepseek/engram/examples/run-demo) — 运行官方 Demo、独立测试 Engram、观察哈希行为

## 目录结构

```
engram/
├── concepts/              # 核心概念（2 篇）
├── references/            # API/配置参考（2 篇）
├── examples/              # 使用示例（1 篇）
└── index.md               # 本文件
```

```{toctree}
:hidden:

concepts/index
examples/index
references/index
```
