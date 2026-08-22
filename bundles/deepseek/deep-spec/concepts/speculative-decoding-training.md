---
type: concept
scope: deep-spec
name: 投机解码训练方法论
version: "1.0.0"
source: deepspec/eval/base_evaluator.py, deepspec/modeling/dspark/loss.py, deepspec/modeling/eagle3/loss.py
description: 投机解码（Speculative Decoding）的基本原理、草稿模型训练范式、拒绝采样验证机制与置信度校准
---

# 投机解码训练方法论

投机解码（Speculative Decoding）是一种无损加速大语言模型自回归生成的技术。其核心思想是利用一个小的草稿模型（Draft Model）快速生成候选 token 序列，再用大模型（Target Model）并行验证这些候选，通过拒绝采样保证生成分布与原模型完全一致，从而实现推理加速。

---

## 一、投机解码基本原理

### 1.1 核心动机

自回归 LLM 生成是严格串行的过程：每生成一个 token，都需要执行一次完整的模型前向传播。对于大模型，单次前向计算量大、延迟高，导致生成速度受限。投机解码利用两个观察：

1. **简单 token 容易预测**：很多 token（如常见词、语法结构）小模型就能正确预测
2. **并行验证便宜**：现代 GPU 可以一次前向计算多个位置的 logits，验证多个 token 的成本与验证一个 token 相近

### 1.2 基本流程

投机解码的推理循环如下：

```
给定前缀 prompt P，草稿模型 M_draft，目标模型 M_target

1. 草稿阶段：用 M_draft 自回归生成 γ 个候选 token x_1, ..., x_γ
   同时记录每个 token 的草稿概率 p_draft(x_i | context)

2. 验证阶段：用 M_target 一次前向计算所有位置的目标概率
   p_target(x_i | P, x_1, ..., x_{i-1})

3. 拒绝采样：对于每个位置 i = 1..γ：
   - 采样 r ~ Uniform(0,1)
   - 若 r < min(1, p_target(x_i) / p_draft(x_i))，接受 x_i
   - 否则拒绝，从残差分布 resample，停止验证后续 token

4. 如果所有 γ 个 token 都被接受，额外从 p_target(x_{γ+1}) 采样一个 bonus token

5. 将接受的 token（加 bonus 或 resample token）追加到输出，回到步骤 1
```

### 1.3 关键性质

- **无损性**：生成结果的分布与直接从目标模型采样完全一致
- **加速比**：取决于草稿模型的接受率 α，理想加速比约为 1/(1-α)（当草稿模型计算成本可忽略时）
- **接受率**：草稿模型质量越高，接受率越高，加速越好
- **草稿成本**：草稿模型必须足够小，否则其自身计算时间会抵消并行验证带来的收益

---

## 二、草稿模型训练范式

DeepSpec 支持两种主要的草稿模型训练范式，以及一种简化变体。

### 2.1 范式对比

| 方面 | DSpark（块级训练） | Eagle3（TTT 自回归训练） | DFlash（纯 CE 训练） |
|---|---|---|---|
| 训练单位 | Block（块） | TTT 步序列 | Block（块） |
| 特征来源 | 多层目标隐状态拼接 | 5层目标隐状态拼接 | 多层目标隐状态拼接 |
| 自回归方式 | Markov 头修正 | TTT 步自回归（1层draft） | 无（直接预测） |
| 损失函数 | CE + L1 分布对齐 + 置信度 BCE | TTT 多步 soft CE（指数衰减） | 纯 CE |
| 并行度 | 高（多 block 并行前向） | 中（KV cache 复用加速） | 高 |

### 2.2 目标隐状态蒸馏

两种范式都使用**目标隐状态缓存**（Offline Hidden State Caching）作为训练数据：

1. 离线运行目标模型，缓存指定层的 hidden states 到磁盘（BF16 格式，mmap 读取）
2. 训练时直接加载缓存的 hidden states，**无需前向目标模型**
3. 草稿模型将目标隐状态作为输入特征，学习预测下一个 token

这种方式有几个优势：
- **显存高效**：训练时不需要在 GPU 上保留目标模型
- **计算高效**：预计算一次，多次复用
- **训练稳定**：特征是固定的，不会因目标模型参数变化而波动

### 2.3 DSpark 块级训练

DSpark 的核心创新是**块级锚点采样**（Block-level Anchor Sampling）：

1. 从序列中随机选择锚点位置（要求前后 token 都在 loss mask 内）
2. 构造噪声嵌入：block 起始位置使用真实的锚点 token embedding，其余位置使用 `[MASK]` token embedding
3. 将所有 block 的噪声嵌入输入草稿 Transformer，一次性得到所有位置的 base logits
4. Markov 头利用前一 token 的低维嵌入，自回归修正每个位置的 logits
5. 损失函数：
   - **CE Loss**：标准交叉熵，位置越靠近锚点权重越高（指数衰减 `exp(-pos/γ)`）
   - **L1 Loss**：draft 概率分布与 target 概率分布的 L1 距离，鼓励分布对齐
   - **Confidence BCE Loss**：置信度头预测每个 token 是否被接受，用于推理早停

### 2.4 Eagle3 TTT 自回归训练

Eagle3 的核心创新是 **TTT（Test-Time Training）自回归训练**：

1. 将目标隐状态（5层拼接投影后）与 token embedding 拼接作为输入（维度 = hidden_size × 2）
2. 使用单层 Transformer 作为草稿模型
3. 训练时模拟推理过程：在 block 内执行 `ttt_length` 步自回归
   - 每步用草稿模型预测下一个 token logits
   - 将预测的 token embedding 作为下一步输入
   - 使用 KV cache 复用前面步的 KV，减少重复计算
4. 创建特殊的 BlockMask 注意力掩码，支持 TTT 自回归
5. 使用 FusedLogSoftmaxLoss（Triton 融合）计算每步 soft CE 损失
6. 按 `step_loss_decay^step_idx` 对各步损失加权求和（越靠后权重越低）

---

## 三、拒绝采样验证机制

### 3.1 标准拒绝采样

DeepSpec 的 `verify_draft_tokens` 实现了标准投机解码拒绝采样：

```python
# 伪代码
for i in range(len(draft_tokens)):
    target_prob = target_probs[i, draft_tokens[i]]
    draft_prob = draft_probs[i, draft_tokens[i]]
    
    # 接受概率
    accept_prob = min(1.0, target_prob / draft_prob)
    
    if random() < accept_prob:
        accept(draft_tokens[i])  # 接受该 token
    else:
        # 从残差分布采样
        residual = normalize(max(0, target_probs[i] - draft_probs[i]))
        next_token = sample(residual)
        reject()  # 停止验证
        break
else:
    # 所有 draft token 被接受，采样 bonus token
    next_token = sample(target_probs[-1])
```

### 3.2 温度调节

当 temperature > 0 时，使用调整后的概率：
- `p_adjusted = softmax(logits / temperature)`
- 当 temperature = 0 时，使用贪婪解码（argmax）

### 3.3 Stop Token 处理

如果在验证过程中遇到 stop token（如 EOS），则：
- 接受该 stop token
- 设置 `terminated_by_stop_token = True`
- 截断后续生成

---

## 四、置信度校准

### 4.1 置信度头

DSpark 支持训练一个置信度头（AcceptRatePredictor），输入为隐状态特征，输出为每个 token 被接受的预测概率：

```python
class AcceptRatePredictor(nn.Module):
    def __init__(self, input_dim):
        self.proj = nn.Linear(input_dim, 1)
    
    def forward(self, features):
        return self.proj(features).squeeze(-1)
```

### 4.2 推理时早停

在推理（评估）时，可以设置 `confidence_threshold > 0`：
- 当置信度预测值低于阈值时，提前截断 draft 生成
- 避免在低置信度位置生成更多后续 token（它们大概率被拒绝，浪费计算）
- 阈值越高，draft 生成越保守，每次提议 token 数越少但接受率越高

### 4.3 校准指标收集

当 `confidence_threshold = 0`（默认值）时，评估器收集置信度校准数据：
- 记录每个位置的置信度预测值和实际接受/拒绝结果
- 可用于分析 ECE（Expected Calibration Error）等指标
- 帮助确定最佳置信度阈值

---

## 五、通用投机解码框架

DeepSpec 的 `generate_decoding_sample` 提供了一个与模型无关的通用投机解码框架：

```python
def generate_decoding_sample(
    *,
    target_model,           # 目标模型
    input_ids,              # 输入 token
    max_new_tokens,         # 最大生成长度
    max_proposal_tokens,    # 每次最多提议的 token 数
    temperature,            # 采样温度
    stop_token_ids,         # Stop token 列表
    init_context,           # 回调：初始化状态
    propose,                # 回调：生成提议
    update,                 # 回调：更新状态
    post_verify=None,       # 回调：诊断钩子
):
```

回调设计使得添加新的草稿模型架构非常简单——只需实现三个核心回调：
1. **init_context**：初始化 KV cache、隐状态缓存等
2. **propose**：根据当前状态生成 DraftProposal
3. **update**：根据验证结果更新状态（裁剪 KV cache、追加新 token 的信息）

---

## 六、相关链接

- [/deepseek/deep-spec/concepts/overview](/deepseek/deep-spec/concepts/overview) — DeepSpec 整体概述
- [/deepseek/deep-spec/concepts/dspark-model](/deepseek/deep-spec/concepts/dspark-model) — DSpark 模型架构详解
- [/deepseek/deep-spec/concepts/eagle3-model](/deepseek/deep-spec/concepts/eagle3-model) — Eagle3 模型架构详解
- [/deepseek/deep-spec/concepts/training-pipeline](/deepseek/deep-spec/concepts/training-pipeline) — 训练管线详解
- [/deepseek/deep-spec/references/eval-api](/deepseek/deep-spec/references/eval-api) — 评估 API 参考
- [/deepseek/deep-spec/examples/evaluation](/deepseek/deep-spec/examples/evaluation) — 评估使用示例
