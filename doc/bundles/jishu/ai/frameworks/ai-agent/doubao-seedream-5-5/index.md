---
okf_version: "0.2"
type: bundle
title: 豆包 Seedream 5.5 生图实战教程
description: 把一份产品使用手册转成可学的生图教程——四类能力边界、提示词骨架、多轮编辑的保留与变化分离、文字海报与透明素材，以及六大场景的提示词地图。
status: flagged
stale_after: 2027-05-16
sensitivity: internal
tags: [豆包, Seedream, 文生图, 提示词工程, 多轮编辑, 透明素材]
generated: { by: "agent:lark-doc-to-okf-wiki", at: "2026-11-16T15:40:00+08:00" }
sources:
  - id: guide
    resource: https://bytedance.larkoffice.com/docx/HkvNdjRwIoK4DcxHThicjQS3nig
    title: 豆包 Seedream 5.5 使用指南
    author: team:doubao-product
    last_modified: 2026-11-16
  - id: seedream50
    resource: https://bytedance.larkoffice.com/docx/EvLJdw9n8oX1HExDfllcA22jnLe
    title: 豆包 Seedance 2.5 & Seedream 5.0 Pro 升级介绍
  - id: seedream45
    resource: https://bytedance.larkoffice.com/wiki/P1wyw0TPmiq87BkjvCychEdGnGd
    title: 豆包 Seedream 4.5 使用指南
---

# 豆包 Seedream 5.5 生图实战教程

生图模型的能力清单读起来都像广告，真正决定出图质量的是**提示词的结构**。这份源手册用 197 张示例图演示同一个动作：把"我想要的感觉"翻译成"模型能验收的结构"（F-001、F-006）。本包把手册转成中文原创学习材料，事实逐条登记在[事实台账](references/facts.md)。

**当前状态为 flagged**：所有能力数字（含"小字准确率 95%"）均为厂商单方口径，本次未调用模型实测，示例图亦未逐张核对（F-016）。教程可用于学习提示词结构与场景地图，不能当作能力实测记录或效果保证。

## 从你的问题开始

| 问题 | 入口 | 学完可形成的产物 |
| --- | --- | --- |
| 5.5 到底比上一代强在哪，哪些是宣传哪些要自己验 | [能力地图](concepts/00-capability-map.md) | 四条能力边界与一条自验清单 |
| 我写了一大段形容词，出图还是不对 | [提示词骨架](concepts/01-prompt-anatomy.md) | 按"任务→风格、骨架→细节"重排的提示词 |
| 改一处就把别处也改了，越改越糊 | [多轮编辑](concepts/02-multi-turn-editing.md) | 保留/变化分离表与每轮自包含指令 |
| 图里要写中文，字总是糊 | [文字与结构](concepts/03-text-and-structure.md) | 逐字给全＋层级约束的文字任务书 |
| 要透明底素材、贴纸、周边 | [透明素材](concepts/04-alpha-assets.md) | 触发词与验收口径 |
| 人像、海报、信息图、LOGO 分别该怎么写 | [场景地图](concepts/05-scene-playbooks.md) | 按场景选模板的路线图 |
| 只想立刻上手 | [五分钟速查](examples/quickstart.md) | 骨架表＋五步清单＋五个坑 |
| 想直接抄模板 | [提示词模板](examples/prompt-templates.md) | 带填空槽位的十类模板 |
| 想抄词不抄句 | [风格词与美学词库](examples/keyword-library.md) | 40 组可组合的词组 |

学习顺序按上表向下：先认边界，再学骨架，再练编辑与文字两类最难的任务，最后按场景调用模板与词库。全程不需要调用模型，可以先用纸面改写练手。

## 取证与计数

源文档为企业域飞书 docx，document_id `HkvNdjRwIoK4DcxHThicjQS3nig`，revision_id 3367，采集于 2026-11-16，正文 73,231 字符 / 362 行（F-001、F-002）。文档零画板、零评论（F-007、F-008），因此本包没有画板判读环节，信息全部来自正文文字与示例图的 alt/caption 描述。

本包含 6 篇概念、3 篇示例、3 篇信源、两级子索引与根索引及 log，共 17 个 Markdown 文件；事实 40 条，F-001 至 F-040。197 张示例图未入库——它们是厂商示例，既不构成本仓可复用素材，也不宜整体转载，本包只引用其文字与提示词短句，图片缺口见[来源登记](references/source-manifest.md)。计数与口径核对见[核验](references/verification.md)。

## 三条可复核的结论

**1. 这份手册真正的资产是提示词的结构，不是能力列表。** 四条能力（多轮编辑、RGBA、真实质感、小字渲染）都是"结果描述"，而 9 条技巧才是可迁移的部分：先任务后风格、先骨架后细节、结构优先于形容词（F-012、F-023）。反常识之处在于——手册把"提示词手册"整章交给了 40 张带词组的图集（22 组风格词＋18 组美学关键词，F-036），词组本身没有定义；照抄词组出不来的图，缺的正是技巧里那层结构。行动：任何场景先用技巧 1—3 搭骨架，再用风格词与美学词填色。

**2. 多轮编辑的失败点几乎都在"没写清保留什么"。** 文档把能力写成"非编辑区域像素级保持"（F-013），把操作要求写成"圈定明确对象、说清变化"（F-020），把技巧写成"分清保留和变化"与"每轮自包含"（F-030、F-031）。四句话指向同一件事：编辑指令必须把不变项显式写出来，否则模型只能猜哪些该保持。行动：每轮提示词落地成两栏表（保留栏/变化栏），再写一句"其余保持一致"。

**3. 文字与透明底是两类"条件触发"任务，不是风格任务。** 透明底由固定触发词决定（"透明背景""PNG 透明底""无背景""alpha 通道"，F-021），文字内容由中文引号逐字给全决定（F-022）。这两类任务的成败不在形容词，而在有没有写上触发条件与逐字内容。行动：把这两类任务各做一张固定检查表，每次提交前逐项打勾。

## 主题关联

| 知识包 | 分工 |
| --- | --- |
| [豆包工作产品实测](../doubao-work/index.md) | 产品整体能力、飞书集成与额度模型；其中 Seedream 5.0 为上一代口径 |
| [豆包工作与 Remotion 照片视频制作](../doubao-work-remotion-photo-video/index.md) | 把生成结果接进视频流水线：分镜、静帧审核与交付 |
| [豆包工作 Context Layer 分析](../doubao-work-context-layer/index.md) | 组织上下文层的战略假说，与本包无关但同族 |
| 本包 | 单模型使用法：能力边界、提示词骨架、编辑与文字两类难点、场景地图 |

上一代口径见源手册末尾列出的三篇历史文档（F-038）；历史结论不因本包增补而自动升级。

## 已知边界

- 能力数字全部为厂商口径，95% 小字准确率无独立评测支撑，本包未实测（F-016）。
- 197 张示例图未入库、未逐张核对；图内提示词只能读到 caption 与正文 blockquote 中的短句，完整参数（模型版本、参考图编号、迭代次数）未公开。
- "RAGB 透明素材"为源文标题原文（F-034），正文与能力条目均指 RGBA（F-012、F-019），本包统一按 RGBA 叙述并保留原文标题。
- 手册只覆盖"怎么写提示词"，不覆盖额度、并发、商用授权与内容合规；这些需另行核对官方条款。
- 源文档 revision 会变，frontmatter 已锚定 revision_id 3367；改版后按[核验](references/verification.md)的复核触发条件重取。

```{toctree}
:hidden:
:maxdepth: 3

concepts/index
examples/index
references/index
log
```
