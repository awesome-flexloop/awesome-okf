# 概念文档（Concepts）

本目录包含多模态视觉模型选型知识包的核心概念文档，按"单一模型 → 全景维度 → 场景矩阵 → 协作架构"的学习路径排列。

## 模型篇

| 文档 | 简介 |
|------|------|
| [00 DeepSeek-V4-Flash-Vision-Exp 模型详解](00-deepseek-vision-exp.md) | 实验性质定位、官方发布信息（单图 384 tokens、按 V4-Flash 费率）、API 传图方式、能力边界与模型家族关系 |

## 选型篇

| 文档 | 简介 |
|------|------|
| [01 视觉模型全景与选型维度](01-selection-landscape.md) | 7 组候选模型清单、五个选型维度（成本 / 地域合规 / 模态覆盖 / 隐私部署 / 文档复杂度）、双模型整体思路 |
| [02 按场景选型矩阵](02-scenario-matrix.md) | 零成本尝鲜、国内生产、多图长视频海外、简单抽取、文档 OCR 五类场景的推荐模型、价格与注意事项，附总结口诀 |

## 架构篇

| 文档 | 简介 |
|------|------|
| [03 视觉-推理双模型协作架构](03-vision-reasoning-pipeline.md) | 分工原则（五类感知结果）、三大收益（输出 tokens 更少 / 结果可缓存 / 避免重复推理）与成本意识 |

## 学习路径建议

```
模型篇（00）→ 选型篇（01-02）→ 架构篇（03）
   ↓              ↓               ↓
 认识切入点    确定候选与场景     设计落地管线
```

```{toctree}
:hidden:
:maxdepth: 7

00-deepseek-vision-exp
01-selection-landscape
02-scenario-matrix
03-vision-reasoning-pipeline
```
