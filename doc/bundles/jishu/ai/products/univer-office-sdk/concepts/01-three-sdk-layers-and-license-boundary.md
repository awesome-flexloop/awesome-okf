---
okf_version: "0.2"
type: Concept
title: "三 SDK 分层与授权边界（洞察层）"
description: "洞察四元组分析：为什么开源版够用只在特定范围成立；Web/Server/AI 三层 SDK 与 Apache-2.0 覆盖范围、商业扩展清单、选型三问"
tags: [univer, licensing, sdk-architecture, insight, open-source-boundary]
generated: { by: "seven-concepts:I", at: "2026-11-20T10:05:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/7WCDC4R7mxqFRHMP0Zf9hA
  - id: official-readme
    url: https://github.com/dream-num/univer/blob/dev/README.md
  - id: official-compare
    url: https://univer.ai/compare/
---

# 三 SDK 分层与授权边界（洞察层）

> 本文是 **I 阶段洞察产物**，按「现象 → 根因 → 影响 → 建议」四元组组织（G2）。事实出处为 F 编号，见 [信源清单](../references/article-source.md)。

## 四元组：为什么"开源版基本够了"这句话需要加限定词

**现象**：博文一边说"十几行代码就能得到一个完整表格编辑器"，一边提醒"官方在线演示里不少是商业版能力，别看完演示就以为全都开源"（F-011/F-044）。两句话看起来矛盾。

**根因**：Univer 不是"一个开源项目 + 几个付费插件"，而是**按产品职责切成三套 SDK**（F-060），Apache-2.0 只覆盖其中最底层：

| SDK | 职责 | 授权 |
|-----|------|------|
| **Web SDK** | 内容模型、编辑、渲染、公式计算、Facade API、UI 基础、Sheets/Docs 编辑 | 本仓库 **Apache-2.0**，含开源 Headless 内容能力（F-061） |
| **Server SDK** | 实时协同、版本历史、Office 文件导入导出（Exchange） | 单独分发与授权（F-062） |
| **AI SDK** | 把 Office 能力接给既有 agent / 工作流，含 Worktree 审阅集成 | 开源基础之外的扩展单独授权（F-060/F-062） |

**影响**："开源版够用"成立于「纯前端编辑 + 公式 + 用 JSON 快照自己持久化」这一组合；一旦需求触及**文件互通（xlsx 上传下载）、多人协同、版本历史、图表/透视表、打印与 PDF**，就跨过了 Apache-2.0 的边界（F-042/F-045/F-046）。风险不在技术，而在**PoC 阶段用开源版跑通、交付阶段才发现授权预算没算**——这是选型类项目最典型的返工来源。

**建议**：立项时先答「选型三问」，再动手跑 demo：

1. 用户要不要**上传/下载 Excel/Word/PPT**？要 → 需要 Server SDK 的 Exchange 能力，先确认授权。
2. 要不要**多人实时协同 / 版本历史 / 图表 / 透视表 / PDF**？要 → 属商业扩展。
3. 数据能否以**内部 JSON 快照**落到自己的存储？能 → 开源核心即可闭环，无需商业许可（官方明示 "needs no commercial Univer license or Server SDK"，F-064）。

## 开源 / 商业能力分界（官方口径）

| 范围 | 具体能力 | 依据 |
|------|---------|------|
| ✅ Apache-2.0 开源 | 单元格样式、合并单元格、单元格内富文本、冻结窗格、浮动图片、撤销重做；公式、定义名称、筛选排序、数据验证、条件格式、超链接、批注、查找替换；Docs 富文本/段落/列表/批注；Facade API；Headless | F-063（官方 Open-source capabilities 表） |
| 💰 商业 Web SDK 插件 | charts、shapes、pivot tables、SmartArt 等；对比页部分项标 `v1.3.0+ · Pro` | F-062/F-072 |
| 💰 Server SDK | 实时协同、revision history、Office file conversion（XLSX/DOCX/PPTX ↔ Unit 快照） | F-062/F-072 |
| 💰 试用限制 | Freemium 评估含**水印与功能限制**（官方逐字 "watermarks and feature limits"） | F-043/F-062 |

## 博文未披露、但影响选型的三条官方边界

1. **开源版不含服务端组件**，且**开源版公式引擎性能低于商业版**（官方对比页，信息更新 2026-10，F-072）。大表格 / 高公式密度场景需压测后再定档。
2. **快照 ≠ 文件**：`workbook.save()` 产出的是内部 JSON 快照，与 XLSX 导入导出是两条独立能力，后者走 Server SDK（F-067/F-072）。把"能保存"误读成"能导出 Excel"是最常见的需求误判。
3. **官方 demos 展示的是完整 Office SDK**（含商业能力），README 自注 "show more than the default open-source setup"（F-072）。演示可看，但不能当作开源版功能清单。

## 对抗审查记录（V 阶段视角）

| 视角 | 攻击点 | 处置 |
|------|-------|------|
| 魔鬼代言人 | "Apache-2.0 商用没问题"是否等于全功能免费？ | 否。已在本文用三 SDK 分层拆开，并落到分界表 |
| 新人 | 照着官方 demo 选型会不会超预算？ | 已标注 demos 含商业能力，附选型三问 |
| 老板 | 什么时候必须花钱？ | 收敛为三问中的第 1、2 问，可直接进立项清单 |
| 未来 | 功能矩阵会变 | `stale_after: 2026-12-31`，compare 页本身标注 2026-10 口径 |

## 阅读下一篇

- [02 · 嵌入表格与 Facade API](02-embed-and-facade-api.md)——开源核心怎么用起来
- [05 · 选型与可迁移模式](05-selection-and-transferable-patterns.md)——把上面三问抽象成可复用模式
