---
type: Concept
title: "从状态到类型化决策"
description: "Jev定位、三种原语、请求响应契约，以及概率、置信度与类型正确的区别"
tags: [Jev, System One, 类型化决策]
generated: { by: "process:seven-concepts-e", at: "2026-09-20" }
status: draft
stale_after: 2026-10-20
sources:
  - { id: article, resource: "https://mp.weixin.qq.com/s/lnWrTGbsLO59w_7cK_rTqQ" }
  - { id: launch, resource: "https://typesafe.ai/blog/introducing-system-one-models-and-jev" }
  - { id: api, resource: "https://docs.typesafe.ai/api" }
  - { id: models, resource: "https://docs.typesafe.ai/models" }
  - { id: primitives, resource: "https://docs.typesafe.ai/primitives" }
  - { id: confidence, resource: "https://docs.typesafe.ai/confidence" }
---

# 从状态到类型化决策

客服软件收到一段投诉后，常常只需要判断是否紧急、转给哪个部门、情绪处于什么等级。TypeSafe为这种嵌入软件的判断设计了Jev：输入待评价状态，输出预定义类型中的结果和概率。发布文由创始人Diogo Almeida署名；其OpenAI经历属于本人/厂商自述，Jev并非OpenAI发布的产品。[F-003～F-004](../references/article-source.md)

## 先理解接口分工

**state** 是模型这一次能够看到的事实或材料，不是自动读取的电脑状态。当前模型仅接受文本或文本组织成的结构化数据；图像、音频、视频必须先由外围系统转成文本信息。**question** 是针对这些材料的一项判断；**answer** 是按声明类型返回的值，软件再决定怎样使用。[F-023～F-029、F-035](../references/article-source.md)

| 组件 | 责任 | 不应隐含假定的能力 |
| --- | --- | --- |
| 状态提供程序 | 读取授权范围内的数据，整理时间、来源和相关字段 | 模型自动看见屏幕或浏览器 |
| Jev | 按instructions与criteria输出概率化判断 | 自动补全真实世界中缺失的事实 |
| 策略代码 | 组合答案、检查权限、选择拒绝或下一步 | 高置信度自然拥有执行权 |
| 执行程序 | 发送按键、打开页面、渲染像素、更新业务状态 | 返回一个动作名称就等于动作完成 |

表中职责拆分是本教程的工程解释，不是原项目源码还原。

## 三种问题怎样选

| 原语 | 适用问题 | 输入criteria | 输出与解释 |
| --- | --- | --- | --- |
| Noul | 是否出现退款请求 | 可选的true/false含义 | `noul`为yes概率，没有独立`confidence` |
| Choice | 应转到哪个部门 | 选项名到说明的映射 | `choice`是所选项，`probabilities`覆盖各项，另有`confidence` |
| Score | 情绪处于哪个等级 | 至少两个有序等级描述 | `score`为按等级概率加权的值；`legend`解释等级，还有分布与`confidence` |

上述字段来自官方API。[F-025～F-027](../references/article-source.md) 判断问题本身必须清楚：Noul的0.5表示yes/no同等不确定，不能拿来表示“中等技能”。需要评价程度时，应使用有语义锚点的Score。Choice可能漏掉现实输入时，应增加other/none类选项，而不是强迫模型从不适用的类别中选一个。[F-025、F-038](../references/article-source.md)

## 读懂请求契约

官方端点是 `POST https://api.typesafe.ai/v1/systemone`，使用Bearer鉴权。请求包含`state`、`model`、`questions`。[F-023](../references/article-source.md)

以下为**官方API文档中的请求示例**，仅用于读懂结构，本教程没有发送请求，也没有实测响应：

```json
{
  "state": "Help! My payouts have been failing for 3 days.",
  "model": "jev-latest",
  "questions": {
    "is_urgent": {
      "type": "noul",
      "instructions": "Does this convey urgency?"
    }
  }
}
```

`is_urgent`只是代码的映射键，底层模型不会用这个名字推断题意。删去instructions后不能指望模型“看变量名就懂”。响应在`answers`下按原键返回答案，同时包含`model`和`usage.input_tokens/output_tokens`。[F-024、F-030](../references/article-source.md) 本例没有展示响应数值，避免把文档示意值误认为本地执行结果。

多个问题可以放进同一请求，共享state并独立计算。若“是否紧急”和“部门归属”都可从当前材料判断，可同时提问；若第二题需要先按部门去取新政策，则确实需要下一次请求。串行依赖由数据依赖决定，不由界面显示顺序决定。[F-029](../references/article-source.md)

## 概率与正确性的三个层次

**类型合法**意味着返回值位于约定的类型或选项空间。官方发布文据此给出0%类型错误，并说明该零值不是经验测量。合法部门选项中仍可能选错部门，所以不能把它扩写为“决策零错误”。[F-010](../references/article-source.md)

**confidence**是Choice/Score概率分布形状的统计量，分布集中通常对应更高值。它不是“当前答案正确的百分比”的直接同义词；Noul则只返回yes概率。官方所读页面没有给出精确计算公式，本教程不补写公式。[F-025、F-028](../references/article-source.md)

**校准**关注一批预测概率与真实结果的符合程度。TypeSafe把训练路线称为RLCD，强调校准决策，但发布材料不足以复原其训练算法，也不足以证明在任意中文业务数据上都校准良好。模型页明确英语为主训练语言、其他语言表现有差异。用自己的带标签样本检验，才可决定哪些判断适合自动处理。[F-005、F-036](../references/article-source.md)

## 当前产品边界

| 项目 | 2026-09-20读取时的官方口径 |
| --- | --- |
| 版本 | `jev-1.13.0`；`jev-latest`与`jev-preview`当前都指向它，别名会移动 |
| 费用 | 每百万输入token为0.042美元，输出不计费 |
| 限流 | 250,000 tokens/s、1,200 requests/min，官方说明动态调整 |
| 上下文 | 模型页：总请求64k、state加最长题32k；原语页仍写约32k共享预算 |
| 定制 | 不提供按账户fine-tune/LoRA，通过state、instructions和criteria表达领域要求 |
| 可用阶段 | 发布说明为early access；精确发布日期未核实 |

事实依据为[F-006、F-011、F-031～F-037](../references/article-source.md)。两处上下文口径尚未得到官方澄清，参阅[冲突说明](../references/verification.md)，不要把表中容量当作本地已验证值。接口401与422分别提示鉴权和请求校验问题；429与529应退避，官方SDK默认重试，但业务端仍须设置等待上限。[F-030](../references/article-source.md)

## 理解检查

“是否含退款请求”适合Noul，“焦虑程度”适合有清晰等级的Score，“交给哪个部门”适合Choice。若所有部门都不适用，问题出在选项覆盖，不应靠提高confidence阈值解决。能解释这三种差异，再阅读[控制类案例](01-games-and-simulation.md)，就能区分模型输出与实际执行。
