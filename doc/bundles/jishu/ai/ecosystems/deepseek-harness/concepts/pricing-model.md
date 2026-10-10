---
type: concept
title: "开源免费 + 模型单独计费——钱账"
description: "Harness 的开源与计费机制：MIT 开源免费、模型调用单独计费、V4.1 Flash 峰谷定价（非高峰/高峰翻倍）、以及高峰价格属单源推断的标注。"
tags: [DeepSeek, Harness, 定价, V4.1, Token]
generated: { by: "process:seven-concepts-cmd+wechat-public-okf", at: "2026-10-10T00:00:00Z" }
status: draft
stale_after: 2026-12-05
sources:
  - id: wx-pjfnnu
    title: DeepSeek Harness 2.0 来了，Codex 该退休
    resource: https://mp.weixin.qq.com/s/PjfnnuDXPo6204CmDggIUw
---

# 开源免费 + 模型单独计费：Harness 的钱账

## 1. 一句话

> Harness 本身 **MIT 开源免费**，模型调用**单独计费**。[^wx-pjfnnu][F-011]

## 2. 定价明细（V4.1 Flash）

| 时段 | 输入 token | 输出 token |
|------|-----------|-----------|
| **非高峰** | 15 美分 / 百万 | 60 美分 / 百万 |
| **高峰** | 翻倍（推断约 30 美分 / 百万） | 翻倍（推断约 120 美分 / 百万） |

> ⚠️ 原文表述高峰价格为"翻倍"，上述绝对值为**单源推断**，未独立验证。[F-012][F-015]

## 3. 关键误解

> 跑在你电脑上 ≠ 模型在本地跑。[^wx-pjfnnu][F-015]

- Desktop App 的**执行层**在本机，**模型推理在远端**。
- 因此：有**网络依赖**，且**每次调用都消耗 Token 费用**，即使 App 本身免费。

## 4. 成本建议

- 对价格敏感：优先在**非高峰时段**使用，成本减半（输出 token 是主要成本项）。
- 用"自己知道答案的项目"起步，减少反复试错浪费。

[^wx-pjfnnu]: [DeepSeek Harness 2.0 来了，Codex 该退休](https://mp.weixin.qq.com/s/PjfnnuDXPo6204CmDggIUw)，有限进步Seven，2026-10-05。