---
okf_version: "0.2"
type: bundle
title: "多模态视觉模型选型指南"
description: "基于 DeepSeek-V4-Flash-Vision-Exp 发布的跨厂商视觉模型选型中文教程——五类场景选型矩阵、价格对比、视觉-推理双模型协作架构"
tags: [AI, LLM, 多模态, 视觉模型, DeepSeek, 模型选型, OCR, 双模型管线]
generated: { by: "seven-concepts-cmd", at: "2026-08-28T23:00:00+08:00" }
verified:
  - { by: "process:seven-concepts-v", at: "2026-08-28T23:00:00+08:00" }
  - { by: "agent-trae/glm-5.3", at: "2026-08-28T23:59:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: wechat-article-hubei
    resource: https://mp.weixin.qq.com/s/iqoikK7m7arGSHnso-q9hQ
    title: 《DeepSeek 多模态视觉实验模型发布！》（微信公众号"湖北"，2026-08-21，收录于"AI开发笔记"）
  - id: deepseek-official-news-260821
    resource: https://api-docs.deepseek.com/news/news260821/
    title: DeepSeek-V4-Flash-Vision-Exp 官方发布新闻
---

# 多模态视觉模型选型指南知识包

本知识包是一份面向开发者的**跨厂商多模态视觉模型选型中文教程**，以 DeepSeek 原生视觉实验模型 DeepSeek-V4-Flash-Vision-Exp 的发布（F-002）为切入点，系统整理五类典型场景下的视觉模型选型矩阵（F-010 ~ F-027）、价格对比（F-013、F-015、F-019、F-034）与"视觉模型做感知 + DeepSeek 做推理"的双模型协作架构（F-028 ~ F-031），最后收敛为一句便于记忆的总结口诀（F-033）。

## 信源说明

本知识包的事实来源为微信公众号"湖北"于 2026-08-21 发布的博文《DeepSeek 多模态视觉实验模型发布！》（收录于"AI开发笔记"，F-001）。生成时（2026-08-28）对博文三项关键声明完成了官方来源轻量核验，全部通过：

| 核验对象 | 官方核验来源 | 结论 |
|---------|-------------|------|
| DeepSeek-V4-Flash-Vision-Exp 发布信息（F-002 ~ F-008） | [DeepSeek 官方发布新闻](https://api-docs.deepseek.com/news/news260821/) | ✅ 通过，并补充官方细节 F-034 |
| GLM-4.6V-Flash 免费 + FlashX 定价（F-010、F-013） | 智谱官方文档（docs.bigmodel.cn）、z.ai 定价页 | ✅ 通过，价格与博文完全一致 |
| Doubao-Seed-2.0-mini 模态与价格（F-014、F-015） | 火山引擎官方价格文档 | ✅ 通过，含阶梯定价细节 F-036 |

核验详情与单源声明清单见 [references/verification.md](references/verification.md)。

---

## 📚 知识结构总览

```
vision-model-selection/
├── concepts/          # 核心概念文档（4篇：模型详解→选型全景→场景矩阵→协作架构）
├── examples/          # 实战示例（3个：成本演练→输出结构→决策树）
├── references/        # 信源登记簿（博文事实清单 + 核验报告）
└── log.md             # 生成日志
```

---

## 🧭 分层导航

### 概念层（concepts/）

* [DeepSeek-V4-Flash-Vision-Exp 模型详解](concepts/00-deepseek-vision-exp.md) — 实验定位、官方计量口径（单图 384 tokens、按 V4-Flash 费率）、API 传图方式与能力边界。
* [视觉模型全景与选型维度](concepts/01-selection-landscape.md) — 7 组候选模型清单、五个选型维度、"视觉做感知 + DeepSeek 做推理"的整体思路。
* [按场景选型矩阵](concepts/02-scenario-matrix.md) — 零成本尝鲜 / 国内生产 / 多图长视频海外 / 简单抽取 / 文档 OCR 五类场景的推荐模型、价格与注意事项。
* [视觉-推理双模型协作架构](concepts/03-vision-reasoning-pipeline.md) — 分工原则、三大收益（输出 tokens 更少 / 结果可缓存 / 避免重复推理）与成本意识。

### 示例层（examples/）

| 示例 | 难度 | 核心内容 |
|------|------|---------|
| [成本-场景选型演练](examples/cost-scenario-walkthrough.md) | ⭐入门 | 以"识别报错弹窗"为例演示任务档位匹配模型档位，附各场景价格对比表 |
| [视觉模型输出结构设计示例](examples/pipeline-output-structure.md) | ⭐⭐基础 | 五字段结构化返回的 JSON Schema 与 Python 伪代码（基于 F-028 推导） |
| [选型决策树](examples/selection-decision-tree.md) | ⭐⭐基础 | 按 F-033 口诀展开的 Mermaid 决策树，叶节点标注事实编号 |

### 信源层（references/）

* [博文信源事实清单](references/article-source.md) — F-001 ~ F-033 完整登记（信源=微信博文），附官方核验信源与 F-034 ~ F-036
* [核验报告](references/verification.md) — 三项关键声明核验结论、细节差异说明与单源声明清单

事实编号索引说明见 [references/index.md](references/index.md)。

---

## ✅ 信任与生命周期说明

* **文档版本**：基于 2026-08-21 发布的博文（F-001）与 2026-08-28 完成的官方轻量核验生成
* **覆盖事实**：共 36 条事实（F-001 ~ F-036），其中 F-001 ~ F-033 来自博文，F-034 ~ F-036 为核验补充
* **核验情况**：三项关键声明（DeepSeek 视觉模型发布信息、GLM 免费与定价、豆包模态与价格）经官方来源核验通过；博文与官方发布日期同步（均为 2026-08-21），未发现编造或过时信息
* **status**：stable — 选型框架与双模型协作架构属于方法论层，稳定性较高
* **stale_after**：2026-12-31 — 视觉模型与定价迭代较快，约 4 个月后应重新评估
* **方法论链路**：R（事实采集）→ I（洞察提炼）→ E（信源先行成文）→ V（核验），详见 [log.md](log.md)

### 已知边界

* DeepSeek-V4-Flash-Vision-Exp 为**实验性质模型**（F-003），接口与计费可能随实验进度调整，不建议无条件用于生产环境
* 本知识包中所有**价格为 2026-08 时点信息**（F-013、F-015、F-019、F-034），各厂商定价可能随时变化，采购决策前请以官方页面为准
* DeepSeek 视觉模型**权重未开源**（F-008）；官方视觉权重计划 2026 年第三季度发布，截至核验日仍未上架（F-035，弱信源）
* Gemini 2.5 Flash-Lite（F-018 ~ F-020）、GPT-5 nano（F-021）、MiniCPM-V 4.6（F-022 ~ F-024）、DeepSeek-OCR-2/GLM-OCR（F-025 ~ F-027）相关声明**仅博文单源**，未经官方核验，引用时请注意甄别
* 博文内容含作者个人观点（如 F-032 识别报错弹窗上旗舰属成本浪费），非官方立场

---

**本知识包共收录 9 个内容文档（4个概念 + 3个示例 + 2个信源），外加 3 个子目录索引、根索引与生成日志，合计 14 个文件。**

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
