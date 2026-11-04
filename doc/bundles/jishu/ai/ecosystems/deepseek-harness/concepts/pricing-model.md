---
type: concept
title: "历史价格快照：开源与模型计费"
description: "保留 2026-10-05 文章的开源与峰谷价格单源口径，本次未复验许可或费用，不用于当前采购。"
tags: [DeepSeek, Harness, 定价, V4.1, Token]
generated: { by: "process:seven-concepts-cmd+wechat-public-okf", at: "2026-11-04T10:15:04+08:00" }
status: draft
stale_after: 2026-12-05
sources:
  - id: wx-pjfnnu
    title: DeepSeek Harness 2.0 来了，Codex 该退休
    resource: https://mp.weixin.qq.com/s/PjfnnuDXPo6204CmDggIUw
---

# 历史价格快照：开源与模型计费

本页是 2026-10-05 文章的历史价格快照，本次未复验价格、许可或计费规则。下列口径均按作者主张阅读，不用于当前采购；费用和数据流向以实际配置的模型服务为准，操作前读[当前练习的安全条件](creator-safety-and-lifecycle.md)。

## 1. 一句话

> 旧文章称 Harness 本身 **MIT 开源免费**，模型调用**单独计费**。[^wx-pjfnnu] [F-012](../references/facts.md)

## 2. 定价明细（V4.1 Flash）

| 时段 | 输入 token | 输出 token |
|------|-----------|-----------|
| **非高峰** | 15 美分 / 百万 | 60 美分 / 百万 |
| **高峰** | 翻倍（推断约 30 美分 / 百万） | 翻倍（推断约 120 美分 / 百万） |

> ⚠️ 原文表述高峰价格为"翻倍"，上述绝对值为**单源推断**，未独立验证。[F-013、F-014](../references/facts.md)

## 3. 关键误解

> 跑在你电脑上 ≠ 模型在本地跑。[^wx-pjfnnu][F-015]

- 旧文章描述的是本机执行、远端推理的使用方式，不据此排除其他模型配置。
- 网络依赖和费用应核对实际服务端点及计费规则，不能从 App 所在位置推断。

## 4. 成本建议

- 原文峰谷价格只作历史记录，不承诺当前非高峰使用可使成本减半。
- 用"自己知道答案的项目"起步，减少反复试错浪费。

[^wx-pjfnnu]: [DeepSeek Harness 2.0 来了，Codex 该退休](https://mp.weixin.qq.com/s/PjfnnuDXPo6204CmDggIUw)，有限进步Seven，2026-10-05。
