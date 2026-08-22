---
type: concept
scope: engram
name: overview
description: Engram 总览——通过可扩展查找实现条件记忆，为大语言模型引入新的稀疏性轴
---

# Engram 总览

## 什么是 Engram

**Engram**（论文标题：*Conditional Memory via Scalable Lookup: A New Axis of Sparsity for Large Language Models*）是 DeepSeek 提出的新型模型架构模块，为 Transformer 引入了**条件记忆（Conditional Memory）**作为与 MoE 互补的稀疏性轴。Engram 将经典 N-gram 嵌入现代化，实现 O(1) 复杂度的知识查找。

- **核心思想**：MoE 通过条件计算扩展模型容量，但 Transformer 缺乏原生的知识查找原语。Engram 填补了这一空白。
- **论文**：Conditional Memory via Scalable Lookup
- **许可证**：Apache 2.0

## 核心创新

### 新的稀疏性轴：条件记忆

传统 Transformer/MoE 的稀疏性体现在**计算**维度——每个 token 只激活部分专家（MoE）或部分注意力头。Engram 引入了**记忆**维度的稀疏性：

| 维度 | MoE（条件计算） | Engram（条件记忆） |
|---|---|---|
| 稀疏对象 | 计算（哪些参数参与计算） | 记忆（哪些知识被检索） |
| 机制 | 路由器动态选择专家 | N-gram 哈希确定性寻址 |
| 复杂度 | O(n) 路由计算 | **O(1)** 哈希查找 |
| 适合存储 | 动态推理能力 | 静态事实/模式 |
| 类比 | "大脑的不同功能区" | "海马体的记忆印迹" |

### 现代化的 N-gram 嵌入

经典 N-gram 语言模型直接存储 n-gram 频率，Engram 对其进行了现代化改造：

1. **多头哈希嵌入**：每个 n-gram 通过多个独立哈希函数（不同质数模）映射到多个嵌入头，减少哈希碰撞
2. **压缩分词器**：通过 NFKC 归一化、小写化等预处理，将等价 token 映射到同一 ID，提高命中率
3. **门控融合**：通过 learned gate 将 n-gram 记忆与动态隐藏状态融合，而非简单替换
4. **短卷积**：使用膨胀深度可分离卷积融合局部上下文，扩展感受野
5. **层特定哈希**：不同插入层使用不同哈希乘数，实现层特定的记忆表

### 确定性 O(1) 查找

Engram 的核心操作是哈希表查找：
- 给定 token 序列 `(t_{k-n+1}, ..., t_k)`，计算确定性哈希值
- 哈希值直接作为嵌入表的行索引
- 无需路由网络、无需注意力计算
- 支持大规模嵌入表卸载到 CPU 内存

## 关键贡献

1. **稀疏性分配理论**：提出神经计算（MoE）与静态记忆（Engram）之间的 U 型缩放定律，指导最优容量分配
2. **等参数等 FLOPs 验证**：Engram-27B 在知识、推理、代码、数学等领域均一致优于 MoE 基线
3. **机制分析**：Engram 减轻了早期层重建静态模式的负担，保留更多有效深度用于复杂推理
4. **系统效率**：确定性寻址支持大规模嵌入表 Host 内存卸载，推理开销极小

## 评测结果

Engram 在多个维度上展现一致提升：

- **知识任务**：静态事实记忆能力增强（直接受益于 n-gram 查找）
- **推理任务**：有效深度保留，复杂推理能力提升
- **代码任务**：代码模式（常见 n-gram）快速检索，减轻注意力负担
- **数学任务**：更多网络深度用于数学推导
- **长上下文**：局部 n-gram 信息不依赖长距离注意力传播

## Engram 在 Transformer 中的位置

Engram 模块插入 Transformer 的浅层（如第 1 层和第 15 层），在 Attention 和 MoE 之前以残差方式工作：

```
输入 Token IDs
    ↓
Token Embedding
    ↓
[Layer 1] → Engram（浅层插入）→ Attention → MoE
    ↓
[Layer 2-14] → Attention → MoE
    ↓
[Layer 15] → Engram（中层插入）→ Attention → MoE
    ↓
[Layer 16-29] → Attention → MoE
    ↓
LM Head → 输出
```

浅层插入的设计直觉：早期层负责识别局部模式，Engram 直接提供这些模式的记忆表示，让更深层专注于高层次推理。
