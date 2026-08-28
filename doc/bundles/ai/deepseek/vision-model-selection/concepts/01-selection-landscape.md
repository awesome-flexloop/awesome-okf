---
type: Concept
title: 视觉模型全景与选型维度
description: 跨厂商视觉模型候选清单（7 组模型）与五个选型维度，确立"视觉模型做感知 + DeepSeek 做推理"的整体思路
tags: [模型选型, 视觉模型, 多模态, 成本, 合规, 本地部署]
generated: { by: "seven-concepts-cmd", at: "2026-08-28T23:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T23:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: wechat-article-hubei
    resource: https://mp.weixin.qq.com/s/iqoikK7m7arGSHnso-q9hQ
    title: 《DeepSeek 多模态视觉实验模型发布！》
---

# 视觉模型全景与选型维度

DeepSeek-V4-Flash-Vision-Exp（F-002）的发布解决了"DeepSeek 能不能看图"的问题，但真实业务中的视觉任务远不止一个候选。本页建立两个坐标系：**有哪些模型可选**，以及**按什么维度比较**。

## 候选模型清单

博文覆盖了 7 组候选模型，从免费尝鲜到文档 OCR 形成完整光谱：

| # | 模型 | 模态/能力 | 价格信号 | 事实编号 |
|---|------|----------|---------|---------|
| 1 | DeepSeek-V4-Flash-Vision-Exp | 图片理解，支持 JPEG/PNG/GIF/WebP（F-005） | 按 V4-Flash 费率，单图最多 384 tokens（F-034） | F-002、F-005、F-034 |
| 2 | GLM-4.6V-Flash / FlashX | 视觉理解 | Flash 免费（F-010）；FlashX 输入 $0.04、输出 $0.40/百万 tokens（F-013） | F-010、F-013 |
| 3 | Doubao-Seed-2.0-mini（豆包） | 图像、视频、音频和文本（F-014） | 输入 ¥0.2、输出 ¥2/百万 tokens 起（F-015） | F-014、F-015 |
| 4 | Gemini 2.5 Flash-Lite | 图像、视频和文本输入（F-018） | 输入 $0.10、输出 $0.40/百万 tokens（F-019） | F-018、F-019 |
| 5 | GPT-5 nano | 图片分类、简单截图识别和结构化抽取（F-021） | 便宜（F-021） | F-021 |
| 6 | MiniCPM-V 4.6 | 本地视觉理解 | 本地部署；约 1.3B 参数，可通过 Ollama 运行（F-023） | F-022、F-023 |
| 7 | DeepSeek-OCR-2 / GLM-OCR | 文档 OCR | OCR 专用模型（F-025） | F-025 |

> 表中价格均为 2026-08 时点信息，边界说明见 [bundle 根索引](../index.md) 的"已知边界"一节。

> 事实溯源：F-002、F-005、F-010、F-013 ~ F-015、F-018、F-019、F-021 ~ F-023、F-025、F-034

## 五个选型维度

### 维度一：成本

成本是最直接的过滤条件（F-010、F-013、F-015、F-019、F-021）：免费额度（GLM-4.6V-Flash，F-010）与便宜模型（GPT-5 nano，F-021）适合验证期；量产后按输入/输出单价精细测算（F-013、F-015、F-019）。成本意识还包括"任务难度与模型档位匹配"——识别报错弹窗不必上旗舰（F-032，作者观点）。

### 维度二：地域合规与结算

面向国内用户时，豆包的国内接入和人民币结算比较方便（F-016）；多图、长视频或海外业务则可考虑 Gemini 2.5 Flash-Lite（F-018）。结算货币、数据出境合规与网络可达性共同构成地域维度。

### 维度三：模态覆盖

任务只吃静态图，还是涉及视频、音频？豆包支持图像、视频、音频和文本（F-014）；Gemini 2.5 Flash-Lite 支持图像、视频和文本输入（F-018）；DeepSeek-V4-Flash-Vision-Exp 当前面向图片理解、不负责生成图片（F-005、F-007）。模态覆盖决定单模型能否闭环。

### 维度四：隐私与本地部署

图片不能上传云端时，可以本地部署 MiniCPM-V 4.6（F-022），约 1.3B 参数也能通过 Ollama 运行（F-023）。相比之下，DeepSeek 视觉模型权重未开放（F-008），走不了本地路线。

### 维度五：文档复杂度

PDF、扫描件、票据和表格应优先评估 DeepSeek-OCR-2 或 GLM-OCR（F-025）：对于几十页文档，OCR 专用模型通常更便于保留布局、控制成本和生成 Markdown（F-026）。

## 整体思路：视觉模型做感知 + DeepSeek 做推理

五个维度之外，博文的整体思路可以压缩成一句话：**视觉模型做感知，DeepSeek 做推理**。

- 视觉侧按场景选一个够用的模型（F-010 ~ F-027）；
- 落地时让视觉模型只返回 OCR 文本、物体、位置关系、表格和不确定项，再交给 DeepSeek 判断（F-028）；
- 本地隐私场景同理：MiniCPM-V 负责提取图片信息，DeepSeek 负责后续分析（F-024）。

分工细节与收益见 [视觉-推理双模型协作架构](03-vision-reasoning-pipeline.md)。

> 事实溯源：F-008、F-010 ~ F-028

## 相关概念

- [DeepSeek-V4-Flash-Vision-Exp 模型详解](00-deepseek-vision-exp.md) — 切入点模型的定位与边界
- [按场景选型矩阵](02-scenario-matrix.md) — 五类场景的推荐模型与价格
- [视觉-推理双模型协作架构](03-vision-reasoning-pipeline.md) — 分工原则与三大收益
