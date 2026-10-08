---
type: concept
scope: deepseek-math-v2
name: overview
description: DeepSeekMath-V2 总览——面向自验证数学推理的大语言模型
---

# DeepSeekMath-V2 总览

## 什么是 DeepSeekMath-V2

**DeepSeekMath-V2**（论文标题：*DeepSeekMath-V2: Towards Self-Verifiable Mathematical Reasoning*）是 DeepSeek 推出的数学推理大模型，核心目标是实现**自验证的数学推理**——模型不仅能生成数学证明，还能验证自身推理的正确性和严谨性。

- **基础模型**：DeepSeek-V3.2-Exp-Base
- **HuggingFace 模型**：`deepseek-ai/DeepSeek-Math-V2`
- **推理支持**：参考 [DeepSeek-V3.2-Exp 仓库](https://github.com/deepseek-ai/DeepSeek-V3.2-Exp)
- **许可证**：Apache 2.0（详见 LICENSE）
- **论文作者**：Zhihong Shao, Yuxiang Luo, Chengda Lu, Z.Z. Ren, Jiewen Hu, Tian Ye, Zhibin Gou, Shirong Ma, Xiaokang Zhang

## 核心动机

传统数学推理 LLM 通过 RL 奖励最终答案正确来提升性能，但这存在根本局限：

1. **正确答案 ≠ 正确推理**：最终答案正确不保证推导过程正确
2. **最终答案奖励不适用于证明**：定理证明需要严谨的逐步推导，而非数值答案
3. **开放问题无法验证**：对于没有已知答案的开放问题，需要模型自己验证推理

DeepSeekMath-V2 的核心主张是：**必须验证数学推理的全面性和严谨性，自验证是扩展测试时计算（test-time compute）的关键，尤其对于没有已知解的开放问题**。

## 方法论：自验证训练

### 1. 训练准确的验证器

首先训练一个基于 LLM 的准确、忠实的验证器，用于评估定理证明的质量。验证器需要：
- 识别证明中的错误步骤
- 判断证明的整体严谨性
- 给出 0/0.5/1 三级评分

### 2. 使用验证器作为奖励模型训练生成器

将验证器作为奖励信号，训练证明生成器。生成器被激励在最终确定证明之前，主动识别并修复自身证明中的问题。

### 3. 扩展验证计算维持生成-验证差距

随着生成器变强，验证器可能无法准确评估更优的证明。解决方案：**扩展验证计算**，自动标注新的"难验证"证明，生成训练数据进一步改进验证器，形成闭环。

## 评测成绩

DeepSeekMath-V2 在数学竞赛和证明基准上取得了顶尖成绩：

| 基准 | 成绩 |
|---|---|
| **IMO 2025** | 金牌级别（Gold-level） |
| **CMO 2024** | 金牌级别（Gold-level） |
| **Putnam 2024** | 118/120（接近满分，配合扩展测试时计算） |
| **IMO-ProofBench** | 强力表现（DeepMind 团队开发的证明基准） |

评测预测结果公开在仓库 `outputs/` 目录。

## 与 DeepSeekMath V1 的关系

DeepSeekMath V1 主要关注数学解题（数值答案），通过 GRPO 等 RL 方法提升答案准确率。V2 则转向更根本的方向：
- V1：追求最终答案正确 → 但可能存在"伪推理"
- V2：追求可验证的严谨证明 → 每步推导都可被验证

## 核心能力

1. **证明生成**：生成严格、全面的数学证明
2. **自验证**：评估自身证明的正确性，识别错误步骤
3. **迭代精炼**：基于验证反馈改进证明
4. **多轮推理**：支持 test-time compute 扩展（最多 16 轮精炼+验证）
