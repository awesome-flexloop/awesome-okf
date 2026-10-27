---
type: Reference
title: GPT-6.1 Terra 信源与编号事实
description: 原帖、官方发布文和模型参考的逐声明登记；官方自述不等于独立复测。
status: draft
stale_after: 2026-11-27
source: https://x.com/thsottiaux/status/2114800277677092936
sources:
  - id: tibo
    resource: https://x.com/thsottiaux/status/2114800277677092936
  - id: launch
    resource: https://openai.com/index/introducing-gpt-6-1-terra/
  - id: model
    resource: https://developers.openai.com/api/docs/models/gpt-6.1-terra
---

# GPT-6.1 Terra 信源与编号事实

## 信源层级

| ID | 材料 | 读取方式与覆盖范围 | 证据边界 |
|---|---|---|---|
| S1 / tibo | [Tibo 主帖](https://x.com/thsottiaux/status/2114800277677092936) | Defuddle 正文与浏览器主帖核对 | 发布者自述；页面回复不是主帖 |
| S2 / launch | [OpenAI 发布文](https://openai.com/index/introducing-gpt-6-1-terra/) | Defuddle 403、WebFetch 失败后，浏览器读取完整正文及可访问图表标签 | 厂商一手声明与自报评测 |
| S3 / model | [API 模型参考](https://developers.openai.com/api/docs/models/gpt-6.1-terra) | Defuddle 读取正文，浏览器另核对端点图标状态 | 官方接口声明，未执行 API 请求 |
| S4 / safety | [部署安全系统卡](https://deploymentsafety.openai.com/gpt-6-1-terra) | Defuddle fetch failed；浏览器 ERR_CONNECTION_CLOSED | 未读取，不作为实质结论依据 |
| S5 / quote | [原帖引用的 OpenAI 帖子](https://x.com/OpenAI/status/2114780711664398349) | 在 S1 的引用区读取可见正文 | 同厂商来源，不增加独立证据数量 |

采集日为 2026-10-27。S1 页面显示 `3:24 · 2026年10月27日`，未取得时区；S2 未显示精确发布日期，不能把 S1 时间作为 S2 的出版时间。引用帖包含一个显示时长 00:31 的视频，未转写视频，不从视频推导能力。

## 原帖短引文

> “Day 22/ Terra is back!”
>
> “gives 2X more usage than 6.1 Sol across API and subscriptions.”

其余内容以原创中文概述登记，不复制评论或发布文全文。

## 编号事实

以下共 45 条，F-001 至 F-045 连续。表述“官方称”记录的是声明存在，而非实测证明声明普遍成立。价格均为采集日文档口径。

| 编号 | 声明或观测 | 来源 | 类型 |
|---|---|---|---|
| F-001 | 主帖作者显示为 Tibo，账号为 @thsottiaux。 | S1 | 页面元信息 |
| F-002 | 主帖以 Day 22 和 Terra is back 开头。 | S1 | 发布者叙述 |
| F-003 | 主帖称模型在 writing、personality、nuanced understanding of requests 上提升。 | S1 | 发布者评价，未独立验证 |
| F-004 | 主帖称 computer use 表现很好。 | S1 | 发布者评价，未独立验证 |
| F-005 | 主帖称相较 6.1 Sol，API 与订阅的 usage 为 2X more。 | S1 | 核心额度自述，口径不足 |
| F-006 | 主帖页面显示 2026-10-27 3:24，时区未取得。 | S1 | 时间观测 |
| F-007 | 引用区的 OpenAI 帖子将型号写为 GPT-6.1 Terra，并描述屏幕理解、跨应用行动与自然写作。 | S5 | 官方发布声明 |
| F-008 | 官方发布文将 Terra 定位为兼具视觉推理、精确电脑操作与自然写作的快速高效模型；所举场景为提案、图纸理解、填表、视频编辑和发票录入会计软件。 | S2 | 官方定位与场景举例，未复现 |
| F-009 | 发布文的前代比较对象为 GPT-5.6 Terra。 | S2 | 比较对象 |
| F-010 | 发布文称标准 API 价格比 GPT-5.6 Terra 和 GPT-6.1 Sol 低 50%。 | S2 | 官方相对价格声明 |
| F-011 | 发布文称 ChatGPT Work 和 Codex 的相同 usage allowance 可覆盖更多任务，没有写精确 2X。 | S2 | 官方额度措辞 |
| F-012 | 发布文列出的可用用户为 Plus、Pro、Enterprise、Edu，在 ChatGPT Work 与 Codex 中使用。 | S2 | 官方可用范围 |
| F-013 | 发布文与模型参考给出的 API 名称都是 gpt-6.1-terra。 | S2、S3 | 官方标识交叉核对 |
| F-014 | 标准输入价为每百万 token 1 美元。 | S2、S3 | 官方定价交叉核对 |
| F-015 | 标准缓存输入价为每百万 token 0.05 美元。 | S2、S3 | 官方定价交叉核对 |
| F-016 | 标准输出价为每百万 token 5 美元。 | S2、S3 | 官方定价交叉核对 |
| F-017 | 模型参考列 context window 为 1,050,000，max output tokens 为 128,000。 | S3 | 官方规格 |
| F-018 | 模型参考列文本和图像为输入，文本为输出；音频和视频均不支持。 | S3 | 官方模态边界 |
| F-019 | reasoning.effort 支持 none、low、medium、high、xhigh、max，medium 为默认。 | S3 | 官方参数 |
| F-020 | 模型参考明确写 Tool calling requires the Responses API。 | S3 | 官方接口约束 |
| F-021 | 浏览器核对 Endpoints 图标：Chat Completions、Responses、Batch 支持，Live 与 Realtime 系列不支持。 | S3 | 页面状态核验，非 API 实测 |
| F-022 | 模型参考列 Streaming、Function calling、Structured outputs 为支持，Fine-tuning 不支持。 | S3 | 官方功能矩阵 |
| F-023 | 模型参考在 Responses API 工具区列 Web search、File search、Image generation、Code interpreter 为支持。 | S3 | 官方工具矩阵 |
| F-024 | 模型参考在 Responses API 工具区列 Hosted shell、Apply patch、Skills、Computer use、MCP、Tool search 为支持。 | S3 | 官方工具矩阵 |
| F-025 | 模型参考列缓存写入 30 分钟保留每百万 token 1.25 美元，12 小时保留 2.50 美元，长上下文调整前。 | S3 | 官方缓存价格 |
| F-026 | 输入超过 272K token 时，整个请求的输入和缓存费率为 2 倍，输出费率为 1.5 倍。 | S3 | 官方长上下文计费边界 |
| F-027 | Batch 与 Flex 比 Standard 低 50%；Fast mode 为 Standard 的 2 倍；可用地区的 regional processing 加价 10%。 | S3 | 官方价格修饰项 |
| F-028 | 模型参考称工具特定模型存在按工具调用计费的费用，指向 pricing 页了解详情。 | S3 | 费用边界，具体金额未核验 |
| F-029 | API 限速表列 Free 不支持；Build、Launch、Grow 的 RPM 分别为 5,000、10,000、15,000。 | S3 | 官方 API 限速，非订阅额度 |
| F-030 | API 限速表列 Build、Launch、Grow 的 TPM 分别为 1,000,000、4,000,000、40,000,000。 | S3 | 官方 API 限速 |
| F-031 | 发布文的 Agents' Last Exam v1 图列 Terra medium 为 57.6%，Cost 为 0.29 美元；正文使用 cost per task，未取得成本覆盖范围、失败计入及聚合方法。 | S2 图表与正文 | 厂商自报评测，统计细项缺口 |
| F-032 | 同图列 GPT-5.6 Terra medium 为 42.6%，Cost 为 0.84 美元。 | S2 图表 | 厂商自报评测 |
| F-033 | 同图列 GPT-6 Astra medium 为 57.6%，Cost 为 4.82 美元。 | S2 图表 | 厂商自报评测 |
| F-034 | 同图列 Terra max 为 60.0% / 1.01 美元，Claude Opus 5.5 为 63.2% / 8.82 美元；本次读取未取得 Claude effort 标注。 | S2 图表 | 厂商自报跨厂商评测，设置缺口 |
| F-035 | 发布文称 Terra 在该评测中完成任务比 GPT-6 Astra 和 GPT-6.1 Sol 快三倍以上。 | S2 | 厂商成效自述，缺独立复测 |
| F-036 | 发布文称 MMMU-Pro 每个 reasoning setting 均超过 GPT-5.6 Terra；浏览器未取得具体分数。 | S2 | 厂商自报定性比较 |
| F-037 | 发布文称 OSWorld 2.1 的 medium effort 超过前代最佳分数；浏览器未取得具体分数。 | S2 | 厂商自报定性比较 |
| F-038 | 内部诱错提示评测的 low effort 错误率，官方报前代 53.6%、Terra 16.7%。 | S2 | 内部评测，非通用错误率 |
| F-039 | 同评测 maximum effort 官方报下降 18 个百分点至 4.3%。 | S2 | 内部评测，未取得完整方法 |
| F-040 | Terminal-Bench 4.0 的 maximum effort，官方报 Terra 50.3%，前代已发布分数为 21.5%。 | S2 | 厂商自报编码评测 |
| F-041 | 发布文建议最复杂编码任务仍选择 GPT-6.1 Sol 或 GPT-6 Astra。 | S2 | 官方选型限定 |
| F-042 | Terminal-Bench-Science 0.1 的 max effort，官方称 Terra 超过 Sol、距 Opus 5.5 不到五分，估计成本不足其五分之一。 | S2 | 厂商自报，未取得绝对分数 |
| F-043 | 发布文称 Terra 在 Preparedness Framework 的 cybersecurity 分类达到 Critical threshold，并保持 Astra 的保护措施。 | S2 | 官方安全声明，系统卡未读 |
| F-044 | 发布文称相较前代更能维持任务范围、坦诚披露限制，并在提示注入测试中表现出较强抵抗。 | S2 | 官方对齐评价，非免疫保证 |
| F-045 | 官方系统卡链接在本次提取和浏览器通道均未读取成功；系统卡细项未核验。 | 采集记录 | 取证缺口 |

S1、S2、S3 和 S5 相互印证部分发布口径，但不是独立研究。没有第三方复测加入此事实表；不能将“多页面”写成“三个独立来源证实”。
