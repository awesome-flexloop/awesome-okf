---
type: reference
scope: engram
name: configuration-and-efficiency
description: Engram 配置策略、显存优化、U 型缩放定律与系统效率
---

# 配置策略与系统效率

## 显存优化：Host 内存卸载

Engram 模块的一个关键系统优势是**确定性寻址**——n-gram 哈希地址在推理前即可确定，不需要动态计算路由（不同于 MoE 的专家路由）。这使得巨大的嵌入表可以卸载到 **CPU 主机内存**，推理时仅按需加载所需行，开销极小。

### 为什么可以卸载

| 特性 | MoE（专家路由） | Engram（N-gram 查找） |
|---|---|---|
| 寻址方式 | 动态（token → router → 专家） | 确定性（n-gram → 哈希 → 行） |
| 路由计算 | 需要前向传播计算路由权重 | 哈希可在 CPU 上预计算 |
| 内存访问模式 | 不可预测 | 可预取（prefetchable） |
| 卸载可行性 | 低（延迟高） | **高**（确定性访问） |

### 配置要点

- Engram 嵌入表存储在 CPU 内存中
- 推理前在 CPU 上计算 n-gram 哈希，确定需要访问的嵌入行
- 只将当前批次所需的嵌入行传输到 GPU
- 由于 O(1) 查找特性，数据传输量可控，推理开销最小

## U 型缩放定律

论文提出了神经计算（MoE）与静态记忆（Engram）之间的**U 型缩放定律**：

```
性能
 ↑
 │   ╲                                    ╱
 │    ╲                                  ╱
 │     ╲                                ╱
 │      ╲                              ╱
 │       ╲            最优区域         ╱
 │        ╲          ╭──────╮        ╱
 │         ╲────────╯      ╰────────╱
 │          纯 Engram    纯 MoE
 └──────────────────────────────────→ 计算/记忆分配
          （记忆主导）  （计算主导）
```

核心发现：
- **纯 MoE（计算主导）**：所有知识都需要参数化记忆，训练和推理成本高
- **纯 Engram（记忆主导）**：n-gram 表存储静态知识，但缺乏组合泛化能力
- **最优配置**：两者的混合——Engram 处理静态模式记忆，MoE/Attention 处理动态推理
- U 型曲线指导了在给定参数预算下，MoE 参数和 Engram 嵌入表之间的最优分配

## Engram-27B 配置

在 27B 参数规模下的实验配置：

| 组件 | 配置 |
|---|---|
| 骨干网络 | DeepSeek-V3 风格 MoE 架构 |
| Engram 插入层 | 第 1 层、第 15 层（浅层） |
| N-gram 阶数 | bigram (n=2) + trigram (n=3) |
| 每 n-gram 嵌入维度 | 512 |
| 哈希头数 | 8（每 n-gram） |
| 词表大小 | 每阶约 5 倍原始词表（~646K） |
| ShortConv | kernel_size=4, dilation=3 |

## 长上下文训练

Engram 在长上下文场景下的优势：
- N-gram 记忆天然提供局部上下文信息，不依赖注意力的长距离传播
- ShortConv 以膨胀卷积方式扩展局部感受野
- 浅层 Engram 提前处理静态模式，节省深层的有效深度用于复杂推理
- 在长上下文评测中表现一致提升

## 作用机制分析

论文的机制分析（Mechanistic Analysis）表明：

1. **早期层减负**：Engram 减轻了早期 Transformer 层重建静态模式的负担
   - 没有 Engram 时，早期层需要通过注意力"记住"常见 n-gram 模式
   - Engram 通过查表直接提供这些静态信息，释放早期层的计算能力

2. **有效深度保留**：
   - 早期层不再"浪费"在简单模式记忆上
   - 更多的有效网络深度可用于复杂推理任务
   - 这解释了为什么 Engram 在推理、代码、数学等需要深度推理的任务上也有提升

3. **记忆-计算分离**：
   - Engram 负责"是什么"（静态事实、常见模式）
   - Attention/MoE 负责"怎么推理"（组合泛化、逻辑推演）

## 环境依赖

```bash
pip install torch numpy transformers sympy
```

- Python 3.8+
- PyTorch
- Transformers（用于加载 DeepSeek-V3 tokenizer）
- SymPy（用于查找质数模）
- NumPy

## 集成到现有模型

要将 Engram 集成到自定义 Transformer 模型中：

1. 创建 `EngramConfig`，指定插入层 ID、n-gram 配置
2. 在目标层的 TransformerBlock 中初始化 `Engram(layer_id)` 模块
3. 在 `forward` 中，在 Attention 和 MoE 之前添加 Engram 残差连接
4. 输入需要 `input_ids`（用于 n-gram 哈希）和 `hidden_states`（用于门控计算）
5. 生产环境中，将 Embedding 表放置在 CPU 内存，按需预取到 GPU
