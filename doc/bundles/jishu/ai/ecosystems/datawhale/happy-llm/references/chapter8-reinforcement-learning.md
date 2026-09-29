---
type: reference
title: "第八章 大模型强化学习"
bundle: /datawhale/happy-llm
description: "GRPO、OPD、Search-R1、ReTool——从偏好对齐到 Agentic RL 的强化学习实践"
source: https://github.com/datawhalechina/happy-llm/blob/main/docs/chapter8/第八章%20大模型强化学习.md
path: docs/chapter8/第八章 大模型强化学习.md
code: docs/chapter8/
tags: [grpo, opd, search-r1, retool, rl, agentic-rl, pytrio]
status: stable
---

# 第八章 大模型强化学习

## 信源信息

- **文件路径**：`docs/chapter8/第八章 大模型强化学习.md`
- **代码目录**：`docs/chapter8/`
- **公共依赖**：`docs/chapter8/requirements.txt`（Python 3.13 + PyTRIO 0.2.6）
- **GitHub**：https://github.com/datawhalechina/happy-llm/blob/main/docs/chapter8/第八章%20大模型强化学习.md

## 内容概要

本章围绕四个主题展开，从基础强化学习算法到 Agentic RL 工程实践：

### 8.1 GRPO（Group Relative Policy Optimization）

- 最早在 DeepSeekMath 中系统提出
- 保留 PPO 的 on-policy 更新思想，使用组内采样估计相对优势
- 省去单独训练 Value Model，降低显存和工程成本
- 组内标准化：`A_i = (r_i - mean(r)) / (std(r) + ε)`
- RLVR（可验证奖励）：数学/代码任务使用规则判题器（如 GSM8K 的 `\boxed{}` 答案提取）
- 退化情形：全对或全错组 advantage=0，不产生梯度
- 代码：`grpo/01-demo-sync.py`（同步版）、`grpo/02-demo-async.py`（异步版）

### 8.2 OPD（On-Policy Distillation）

- Student 在自身状态分布上持续获得 Teacher 的逐 token 指导
- 区别于传统离线蒸馏：Student 生成轨迹，Teacher 在 Student 的轨迹上提供指导
- 代码：`opd/01-demo-sync.py`、`opd/02-demo-async.py`

### 8.3 Search-R1

- 搜索引擎作为 RL 环境
- 模型学习多轮搜索→推理→回答的策略
- 工程结构：`data.py`（数据）、`protocol.py`（协议）、`reward.py`（奖励）、`rollout.py`（采样）、`search.py`（搜索后端）、`train.py`（训练）、`eval.py`（评测）
- 支持无需 API Key 的 Wikipedia 后端验证链路

### 8.4 ReTool

- 代码解释器作为 RL 环境
- 模型生成并执行 Python 代码解决问题
- 需隔离执行环境（`sandbox.py`，建议使用一次性容器/低权限虚拟机）
- 安全提示：移除环境中的 API Key、SSH 配置和云服务凭证
- 工程结构：`data.py`、`protocol.py`、`reward.py`、`rollout.py`、`sandbox.py`、`train.py`、`eval.py`、`analysis.py`、`prepare_data.py`

## PyTRIO 工程架构

- 本地：数据处理、环境交互（搜索/代码执行）、训练调度
- 远端：模型采样、前向/反向传播、LoRA 参数更新（按使用量计费）
- 核心链路：rollout → reward/advantage 计算 → Datum 对齐 → forward_backward() → optim_step() → 刷新采样
- 无需本地 GPU，CPU + 稳定网络即可学习

## 扩展资源

- 作者维护的 [agentic-rl-lab](https://github.com/KMnO4-zx/agentic-rl-lab)：更新频率更高，包含 OPSD、DAPO、GSPO、ALFWorld 等更多算法

## 对应概念

- [GRPO 强化学习](../concepts/grpo-reinforcement-learning.md)
- [Agent 智能体](../concepts/agent-intelligent-agent.md)
- [模型训练](../concepts/model-training.md)
