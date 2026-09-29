---
type: Concept
title: 多模态生成与电脑操作
description: Seedance视频生成+Seedream图像生成接入、GitHub插画Skill安装、统一主视觉多媒体传播方案、手机遥控电脑本地操作
tags: [Seedance, Seedream, 多模态, 视频生成, 图像生成, Skill, 远程控制, 电脑操作]
generated: { by: "blog-article-to-okf-bundle", at: "2026-08-28T23:55:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: appso-article
    resource: https://mp.weixin.qq.com/s/dqvRKQoH45cXL2F8z0ZHYw
    title: APPSO 豆包工作实测
  - id: seed-byteDance
    resource: https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2.5
    title: 字节跳动Seed团队官方博客
---

# 多模态生成与电脑操作

> **事实基础**：本文所有具体数据与声明均带 F 编号，完整事实清单见 [references/article-source.md](../references/article-source.md)，核验报告见 [references/verification.md](../references/verification.md)。

## 1. Seedance 与 Seedream 模型接入

豆包工作接入了字节跳动Seed团队的两个生成模型（F-006）：

| 模型 | 类型 | 核验时最新版本 | 用途 |
|------|------|--------------|------|
| **Seedance** | 视频生成 | 2.5（2026-07-31发布） | 宣传视频、动态内容生成 |
| **Seedream** | 图像生成 | 5.0 | 海报、插画、图片素材生成 |

博文评价："得益于Seedance和Seedream的接入，豆包工作交付的内容也比其他Agent要更丰富"（F-006）。

> 两个模型均为字节跳动自研，豆包官网下载页明确标注"专业版Seedream 5.0生图，专业版Seedance 2.5生视频核心模型"。

## 2. GitHub Skill 生态

豆包工作支持直接安装GitHub上的Skill扩展能力（F-015）：

- 博文实测安装了一个**插画Skill**
- 安装后发图即可直接调用该Skill进行处理
- 这意味着多模态能力不局限于内置模型，可通过Skill生态扩展

## 3. 统一主视觉的多媒体传播方案

博文展示了一个典型的多模态协同场景（F-016）：

**输入**：一份活动Brief + 品牌使用规范
**输出**：一整套多媒体传播方案，包含：
- 统一主视觉的图片海报
- 统一主视觉的宣传视频

关键价值：图片和视频的主视觉保持一致——这在传统工作流中需要设计师分别处理图片和视频，且很难保证风格统一。豆包工作通过同一Brief和品牌规范驱动两种模态生成，天然保证视觉一致性。

## 4. 手机遥控电脑

豆包工作支持**跨设备远程操作**（F-017）：

```
手机端豆包工作
  │  远程指令
  ▼
电脑端豆包工作
  │  操作
  ▼
本地电脑文件/应用
```

具体能力：
- 在手机上遥控电脑上的豆包工作
- 操作本地电脑（文件、应用）
- 远程把文件发给手机端用户
- 执行其他电脑端任务

这一能力解决了"人不在电脑前但需要电脑上的文件/操作"的场景，与飞书集成结合后，可以在手机上完成完整的工作闭环。

## 5. 多模态在工作流中的定位

博文将多模态生成定位为豆包工作的"自留地"——在文档/网页等基础能力高度同质化的办公Agent赛道，Seedance+Seedream的原生多模态能力是差异化优势之一：

| 层次 | 能力 | 同质化程度 |
|------|------|-----------|
| 基础层 | 文档/PPT/表格/网页生成 | 高（各家都有） |
| 协同层 | AI编辑、飞书云文档 | 中 |
| **多模态层** | **Seedance视频+Seedream图像+Skill生态** | **低（字节自研模型优势）** |
| 集成层 | 飞书深度打通 | 低（见[02](02-feishu-integration.md)） |

---

## 参考

- 完整事实清单：[references/article-source.md](../references/article-source.md)
- Seedance 2.5 官方博客：https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2.5
- 产品概览：[00-product-overview.md](00-product-overview.md)
- 飞书深度集成：[02-feishu-integration.md](02-feishu-integration.md)
