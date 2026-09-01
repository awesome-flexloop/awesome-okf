---
type: Concept
title: DeepSeek-V4-Flash-Vision-Exp 模型详解
description: DeepSeek 原生视觉实验模型的定位、官方发布信息、API 传图方式、能力边界，以及与 V4-Flash/V4-Pro 的关系
tags: [DeepSeek, 视觉模型, 实验模型, 多模态, API]
generated: { by: "seven-concepts-cmd", at: "2026-08-28T23:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T23:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: wechat-article-hubei
    resource: https://mp.weixin.qq.com/s/iqoikK7m7arGSHnso-q9hQ
    title: 《DeepSeek 多模态视觉实验模型发布！》
  - id: deepseek-official-news-260821
    resource: https://api-docs.deepseek.com/news/news260821/
    title: DeepSeek-V4-Flash-Vision-Exp 官方发布新闻
---

# DeepSeek-V4-Flash-Vision-Exp 模型详解

DeepSeek 于 2026-08-21 发布了原生视觉模型 **DeepSeek-V4-Flash-Vision-Exp**（F-002），开发者现在可以通过官方 API 传入图片（F-004）。本页拆解该模型的定位、计量口径、接入方式与能力边界，作为后续选型讨论的切入点。

> 该模型发布信息已通过 DeepSeek 官方新闻核验（详见 [核验报告](../references/verification.md)）。

## 实验性质定位

模型名称中的 **Exp** 后缀表明这是一个**实验性质**的模型（F-003）。这意味着：

- 接口形式、计费规则与能力上限可能随实验进度调整；
- 官方对其稳定性未作生产级承诺，接入前应评估业务容错；
- 实验模型通常是正式版的前奏，值得跟踪，但不建议无条件押注生产链路。

> 事实溯源：F-002、F-003

## 官方发布信息

DeepSeek 官方发布新闻（2026-08-21）给出了两条关键计量信息（F-034）：

| 项目 | 官方口径 | 说明 |
|------|---------|------|
| 单图 token 折算 | 单图最多折算 384 tokens | 图片输入的计量上限（F-034） |
| 计费费率 | 按 V4-Flash 费率计费 | 与 V4-Flash 同价（F-034） |

即：一张图片最多按 384 tokens 计入输入，费率沿用 V4-Flash（F-034）。这条口径让"DeepSeek 侧的视觉任务成本"变得可预估。

> 事实溯源：F-034

## API 传图方式

### 支持的图片格式

| 格式 | 支持 |
|------|------|
| JPEG | ✅（F-005） |
| PNG | ✅（F-005） |
| GIF | ✅（F-005） |
| WebP | ✅（F-005） |

### 图片输入方式

模型可接收三种图片输入（F-006）：

1. **Base64** — 图片内容直接编码进请求体（F-006）；
2. **图片链接** — 传入可公网访问的图片 URL（F-006）；
3. **Files API 文件** — 先通过 Files API 上传文件再引用（F-006）。

开发者现在即可通过官方 API 传图片（F-004），三种输入方式覆盖了绝大多数业务接入形态（F-006）。

> 事实溯源：F-004、F-005、F-006

## 能力边界

使用该模型前，需要清楚三条边界：

1. **只理解、不生成**：模型主打图片理解，不负责生成图片（F-007），生图需求不在其能力范围内。
2. **权重未开源**：发布时未同步开放模型权重（F-008），无法本地部署；官方视觉权重计划于 2026 年第三季度发布，截至核验日（2026-08-28）仍未上架（F-035，弱信源）。
3. **实验性质**：见上文定位一节（F-003）。

> 事实溯源：F-003、F-007、F-008、F-035

## 与 V4-Flash/V4-Pro 的关系

需要注意：DeepSeek 普通的 **V4-Flash** 和 **V4-Pro** 依然不能直接处理图片（不能"直接吃图"）（F-009）。视觉能力是 Vision-Exp 这个独立实验型号才具备的，三者在 API 侧是不同型号：

| 型号 | 能看图 | 定位 |
|------|-------|------|
| V4-Flash | ❌（F-009） | 文本模型；Vision-Exp 的费率基准（F-034） |
| V4-Pro | ❌（F-009） | 文本模型 |
| V4-Flash-Vision-Exp | ✅（F-002、F-004） | 实验性视觉理解模型 |

> 事实溯源：F-002、F-004、F-009、F-034

## 小结

DeepSeek-V4-Flash-Vision-Exp 补齐了 DeepSeek 生态"看图"的空白（F-002、F-004），以单图最多 384 tokens、按 V4-Flash 费率的计量口径提供 API 级图片理解（F-034）。但在跨厂商视角下，它只是视觉任务的候选之一——完整的选型地图见 [视觉模型全景与选型维度](01-selection-landscape.md)。

## 相关概念

- [视觉模型全景与选型维度](01-selection-landscape.md) — 7 组候选模型与五个选型维度
- [按场景选型矩阵](02-scenario-matrix.md) — 五类场景的推荐模型与价格
- [视觉-推理双模型协作架构](03-vision-reasoning-pipeline.md) — 视觉模型与 DeepSeek 的分工
