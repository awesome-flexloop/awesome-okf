---
okf_version: "0.2"
type: Concept
title: "两类实证：代码补全与 128K 大海捞针"
description: "DeepSeek-V4 系列的相位敏感性证据——装饰性 docstring 长度触发顶层补全在正确/错误答案间 4-token 周期反转；128K NIAH 检索跨相位最大差距 40.2 个百分点，五组数字均经论文 Figure 1/2 核验。"
tags: [phase-sensitivity, deepseek-v4, niah, code-completion, retrieval]
generated: { by: "reference_agent/deepseek-v4", at: "2026-10-10" }
verified:
  - { by: "process:seven-concepts-v", at: "2026-10-10" }
status: stable
stale_after: 2026-12-31
sources:
  - id: arxiv
    url: "https://arxiv.org/abs/2609.36322"
---

# 两类实证：代码补全与 128K 大海捞针

## 实证一：周期性反转的代码补全

### 构造

测试对象是 **DeepSeek-V4-Flash-Base** [F-005]。实验取自 DeepSeek-V4 官方推理代码中的一段 **FP8 量化函数**，让模型补全最后一个 token [F-005]。正确答案是 "8"——这段代码需要完成 FP8 相关的类型转换（函数量化到 FP8，而外层 cast 已转为 FP32，补 "32" 会重复外层转换并跳过舍入步骤）[F-006]。

为测试预测是否依赖位置，研究人员在代码前加了一段**纯装饰性 docstring**（第二行放重复的 "=" 号），只改变等号数量调整填充长度 `L`。代码本身、要补全的位置、正确答案都未变，唯一变化是前面多了几个实际无意义的 token [F-007]。

### 观察到的周期行为

16 种填充长度 L 下，顶层补全周期性反转 [F-008][F-009]：

- `L mod 4 ∈ {0,1}` → 模型倾向**错误答案 32**
- `L mod 4 ∈ {2,3}` → 模型倾向**正确答案 8**

且在某一组位置，错误答案 32 的平均概率高达 **71.3%**、正确答案 8 仅为 **26.4%**[F-010]；换到另一组位置，正确答案 8 升到 **91.5%**、错误答案 32 仅有 **7.2%**[F-011]。

**`P(8)-P(32)` 范围从 -0.79 到 0.95**（论文正文），仅改变 docstring 长度即可反转首选补全 [F-012]。反转每 4 个 token 重复一次，恰好匹配 DeepSeek-V4 压缩稀疏注意力（CSA）的步长 `S=4` [F-009][F-046]。

> 说明：`P(8)-P(32)` 的 -0.79~0.95 是对**单个代码补全示例**的相位概率差；文章所列的 71.3%/26.4%、91.5%/7.2% 是**按相位分组后的平均概率**。二者口径不同，本束已区分，引用时勿混淆 [F-039]。

该反转不限于单一 filler：四种 filler 家族大多遵循同一四 token 模式；后训练版 DeepSeek-V4-Flash-0731 与 DeepSeek-V4.1-Flash 也表现出周期反转，各自匹配其步长（`S=4` 与 `S=2`）。对照之下，**无分块 KV 压缩的 DeepSeek-V3.1-Base** 仅在 64 个输入中的 4 个把 32 排在 8 之上，且余量很小 [F-048]。

## 实证二：128K 大海捞针（NIAH）检索

### 构造

研究人员构造长达 **128K token** 的上下文，内含约 **1.6 万个键值对**（K1↔V1、K2↔V2……）[F-013]。让模型找出指定 Key 对应的 Value。测试中键值关系、问题、上下文总长度都保持一致，重点是**调整目标信息相对压缩窗口边界的位置** [F-014]。

按目标 key 位置对 8 取余分成 8 组（residue groups），覆盖 DeepSeek-V4 的两个步长周期、DeepSeek-V4.1 的四个周期；各组提示长度、查询位置、键值绑定一致，并保证目标 key 绝对位置的均值/方差在各组相同 [F-013][F-014]。

### 观察到的差距（论文 Figure 2，已核验）

| 模型 | 跨相位最大准确率差距 |
|------|---------------------|
| DeepSeek-V4-Flash-Base | **40.2 个百分点** [F-015] |
| DeepSeek-V4-Pro-Base | **34.8 个百分点** [F-016] |
| DeepSeek-V4-Flash-0731（后训练） | 19.1 个百分点 [F-017] |
| DeepSeek-V4-Pro-0813（后训练） | 14.8 个百分点 [F-017] |
| DeepSeek-V4.1-Flash-0910（后训练） | 6.1 个百分点 [F-017] |

波动周期：**DeepSeek-V4 为 4 个 token、DeepSeek-V4.1 为 2 个 token**，恰好对应两代模型各自的压缩步长 [F-018][F-019][F-020][F-046]。

base 检查点相位敏感最为尖锐；后训练提升准确率并收窄差距但未消除——DeepSeek-V4 后训练版差距仍大；DeepSeek-V4.1-Flash 差距最小，但其四个偶数 residue 组仍全部高于四个奇数组 [F-017]。

> **平均分掩盖差异**：这类周期波动在常规 benchmark 平均分中可能看不出来——某些位置表现很好、另一些明显掉队，汇总平均后成绩依然不错 [F-041][F-045]。

## 延伸阅读

- 相位与相位敏感性定义见 [00-phase-sensitivity-overview](00-phase-sensitivity-overview.md)
- 成因与机理见 [02-mechanism-kernel-and-specialization](02-mechanism-kernel-and-specialization.md)
- 评估建议见 [03-evaluation-implications](03-evaluation-implications.md)