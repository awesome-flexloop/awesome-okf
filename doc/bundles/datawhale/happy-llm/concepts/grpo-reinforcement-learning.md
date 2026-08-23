---
type: concept
title: "GRPO 强化学习"
bundle: /datawhale/happy-llm
description: "Group Relative Policy Optimization——组相对策略优化，使用组内采样估计相对优势，省去 Value Model，是大模型 RLVR 的主流算法"
sources: https://github.com/datawhalechina/happy-llm/blob/main/docs/chapter8/第八章%20大模型强化学习.md
related:
  - /datawhale/happy-llm/concepts/model-training
  - /datawhale/happy-llm/concepts/agent-intelligent-agent
tags: [grpo, rl, rlvr, ppo, agentic-rl, reinforcement-learning]
status: stable
---

# GRPO 强化学习

## 核心理解

GRPO（Group Relative Policy Optimization，组相对策略优化）最早在 DeepSeekMath 中系统提出，是当前大模型强化学习最主流的基础算法之一。它保留了 PPO 的 on-policy 更新思想，但通过**同一问题的一组采样结果估计相对优势**，省去了 PPO 中单独训练 Value Model 的过程，显著降低了训练成本和工程复杂度。

第八章围绕 GRPO 展开，并进一步介绍 OPD、Search-R1 和 ReTool，展示从偏好对齐到 Agentic RL 的演进。

## 从语言模型到强化学习策略

将自回归语言模型放入 RL 框架的对应关系：

| 强化学习概念 | 大语言模型中的含义 |
|---|---|
| 状态 s_t | prompt 与已生成的 token |
| 动作 a_t | 下一个 token |
| 策略 π_θ(a_t\|s_t) | 模型对下一个 token 的概率分布 |
| 轨迹 τ | 一段完整回答或多轮工具交互 |
| 环境 | 判题器、搜索引擎、代码解释器 |
| 奖励 R(τ) | 答案正确性、格式、工具执行结果 |

一次模型生成称为一次 **rollout**。训练目标是提高高奖励轨迹中动作的概率，降低低奖励轨迹中动作的概率。

## 从 PPO 到 GRPO

### PPO 的问题

PPO 使用 Value Model 估计状态价值 V(s)，再结合回报计算优势函数。在大模型场景中：
- Value Model 通常与策略模型规模接近，带来额外显存和训练成本
- 价值估计误差会传递到策略更新
- 需要策略模型和价值模型同步更新，工程复杂度高

### GRPO 的解决方案

对于一个问题 x，从旧策略采样 G 个回答：

```
{y_1, y_2, ..., y_G} ~ π_θ_old(·|x)
```

判题器给出奖励 r_1, ..., r_G，GRPO 使用组内均值和标准差标准化：

```
A_i = (r_i - mean(r)) / (std(r) + ε)
```

- 高分回答获得正 advantage → 被鼓励
- 低分回答获得负 advantage → 被抑制
- 问题难度被组内基线抵消，策略专注学习"相同条件下哪些生成方式更好"

### 退化情形

当一组回答全部正确或全部错误时，每个 A_i = 0，该组不产生有效梯度。若训练日志中退化组比例长期偏高，需调整题目难度、采样温度或 group size。

## RLVR：可验证奖励强化学习

GRPO 只负责将奖励转换为相对优势，**奖励质量决定模型最终学到什么**。对于数学和代码任务，可以使用确定性规则判题器，这类训练称为 **RLVR（Reinforcement Learning with Verifiable Rewards）**。

第八章以 GSM8K 为例，要求模型将答案写在 `\boxed{}` 中，通过正则提取并与标准答案比对。这种奖励信号无需人工标注，可大规模自动化，是 DeepSeek-R1 等推理模型成功的关键。

## PPO-clip 目标

GRPO 使用与 PPO 相同的裁剪目标限制策略更新幅度：

```
L = -E[min(r_t(θ)·A_t, clip(r_t(θ), 1-ε, 1+ε)·A_t)]
```

其中 r_t(θ) = π_θ/π_θ_old 是新旧策略概率比，裁剪防止一次更新破坏模型已有能力。同时加入 KL 散度惩罚项防止策略偏离参考模型过远。

## 训练闭环

第八章所有示例（GRPO/OPD/Search-R1/ReTool）共享同一核心链路：

1. 使用当前策略生成一组轨迹（rollout）
2. 根据结果或 Teacher 反馈计算奖励/训练信号
3. 将 prompt、response、旧策略 logprob 和 advantage 对齐
4. 调用 `forward_backward()` 与 `optim_step()` 更新策略
5. 刷新采样客户端，下一轮 rollout 使用新权重

## PyTRIO 工程架构

第八章使用 PyTRIO 0.2.6 将本地与远端解耦：
- **远端**：模型采样、前向/反向传播、LoRA 参数更新（按使用量计费）
- **本地**：数据处理、搜索环境、代码执行沙箱、训练调度
- 无需本地 GPU，CPU + 稳定网络即可学习，基础实验预算控制在 200 元以内

## 从 GRPO 到 Agentic RL

- **OPD（On-Policy Distillation）**：Student 在自身状态分布上持续获得 Teacher 的逐 token 指导
- **Search-R1**：将搜索引擎作为环境，模型学习多轮搜索→推理→回答
- **ReTool**：将代码解释器作为环境，模型生成并执行 Python 代码解决问题（需沙箱隔离）

Search-R1 和 ReTool 将 RL 从"偏好对齐"推进到"环境交互"——Agent 在真实环境中尝试动作，根据最终结果判断轨迹是否有效，再更新策略。

## 在 Happy-LLM 中的位置

第八章是全书的前沿章节，建立在第四章（RLHF 理论）、第六章（训练工程）和第七章（Agent 基础）之上。GRPO 是理解 DeepSeek-R1 等推理模型和现代 Agentic RL 的关键入口。

## 延伸阅读

- [模型训练](model-training.md)——三阶段训练中的 RL 阶段
- [Agent 智能体](agent-intelligent-agent.md)——Agentic RL 的应用基础
- [TinyAgent 智能体工具调用示例](../examples/agent-tinyagent.md)——Agent 基础实践
