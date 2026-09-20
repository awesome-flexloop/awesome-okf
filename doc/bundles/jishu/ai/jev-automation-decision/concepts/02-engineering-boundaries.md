---
type: Concept
title: "工程边界与评测方法"
description: "从置信度、回退、输入限制和端到端成本建立 Jev 的落地评估框架"
tags: [Jev, 评测, 置信度, 回退, 成本]
generated: { by: "process:seven-concepts-e", at: "2026-09-20" }
verified: { by: "process:seven-concepts-v", at: "2026-09-20" }
status: flagged
stale_after: 2026-10-20
sources:
  - { id: article, resource: "/references/article-source.md" }
  - { id: intro, resource: "https://docs.typesafe.ai/introduction" }
  - { id: system-one, resource: "https://docs.typesafe.ai/concepts/system-one" }
  - { id: state, resource: "https://docs.typesafe.ai/concepts/state" }
---

# 工程边界与评测方法

## 1. 置信度只是信号

Choice 和 Score 返回 `confidence`，Noul 返回 yes 概率；这些数值用于表达不确定性，不是自动授权凭证。[F-021](../references/article-source.md)

推荐把动作分成三档：

| 结果 | 处理 |
| --- | --- |
| 高置信度且低风险 | 代码执行，并记录版本和输入摘要 |
| 中间区域或状态缺失 | 请求补充信息，或交给人工 |
| 高风险动作/策略冲突 | 强制人工批准，不因高置信度跳过 |

阈值必须用本领域标注集校准。换语言、换渠道、换版本后重新评测，不能沿用文章中的“几乎不出错”。[F-005、F-018](../references/article-source.md)

## 2. 输入限制决定架构

官方当前描述 Jev 接收字符串、JSON 对象或文本数组，不接受图像、音频和视频。[F-018](../references/article-source.md)

因此“控制游戏”或“操控浏览器”需要额外组件：

1. 感知或采集器把环境转成文本状态。
2. Jev 只回答有限问题。
3. 执行器落实动作并回收新状态。
4. 策略层处理超时、无效答案和人工接管。

如果状态编码丢失了关键上下文，类型安全的结果仍可能稳定地错误。

## 3. 不只看 API 单价

文章把低价和高频调用作为主要卖点，但端到端成本还包括：

- 状态采集、清洗和序列化；
- 辅助模型或 OCR/浏览器工具；
- 网络等待、重试和限流；
- 执行器维护；
- 低置信度人工复核；
- 错误动作的业务损失。

官方价格示例可以作为输入成本的一个变量，不能直接推出完整任务成本。[F-004、F-023](../references/article-source.md)

## 4. 最小评测闭环

在真实业务接入前，至少记录：

1. 版本或模型别名、区域和请求时间。
2. 输入状态快照与问题定义。
3. 结构合法率、业务准确率、拒答/回退率。
4. 端到端 P50/P95 延迟，而不是只测模型响应。
5. 每个成功任务的全成本和人工复核时长。
6. 误触发、漏触发和高风险动作案例。

**本节洞察（I-3）**：模型便宜并不等于系统便宜；真正的比较单位应是“同等业务质量下完成一个任务的全成本”。这是对文章卖点的工程化重述。

## 5. 迁移清单

- 任务能否被拆成一个个独立、可枚举的问题？
- 状态是否包含做判断所需的全部事实？
- 是否存在 `other/none` 或拒答路径？
- 阈值是否由本领域数据校准？
- 高风险动作是否有人工门禁？
- 评测是否含外围组件和失败成本？

若前三项无法满足，优先使用通用推理模型或规则系统补足，而不是强行把开放问题压成 Choice。
