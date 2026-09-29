---
okf_version: "0.2"
type: bundle
title: "豆包工作：连上飞书后的AI同事"
description: "APPSO实测豆包工作（Doubao Work）——字节跳动生产力Agent产品，深度打通飞书组织架构/文档/消息/任务/多维表格，Seedance+Seedream多模态生成，滚动额度模型，核心论点'组织上下文决定AI能不能成为同事'"
tags: [豆包工作, Doubao Work, 飞书, Feishu, Agent, 字节跳动, Seedance, Seedream, 办公AI, 生产力]
generated: { by: "blog-article-to-okf-bundle", at: "2026-08-28T23:55:00+08:00" }
verified: true
status: stable
stale_after: 2026-12-31
sources:
  - id: appso-article
    resource: https://mp.weixin.qq.com/s/dqvRKQoH45cXL2F8z0ZHYw
    title: 《实测豆包工作：连上飞书后，Agent终于像个同事了》（APPSO，2026-08-25）
  - id: 36kr-review
    resource: https://36kr.com/p/3954390879222917
    title: 36氪/爱范儿豆包工作实测
  - id: caixinglobal
    resource: https://www.caixinglobal.com/2026-08-25/bytedance-consolidates-ai-office-tools-around-doubao-102477744.html
    title: 财新全球：字节跳动整合AI办公工具
  - id: doubao-official
    resource: https://www.doubao.com/work
    title: 豆包工作官网
---

# 豆包工作：连上飞书后的AI同事

> **性质声明**：本知识包基于 APPSO（爱范儿旗下）2026-08-25 发布的产品实测评测文章转化。博文为媒体提前拿到测试资格的 hands-on 体验，非官方文档或技术教程。文中产品功能描述以测试时版本为准，产品快速迭代中（stale_after: 2026-12-31）。作者观点（如"组织上下文决定AI能不能成为同事"）已用 📝 标注，不代表客观事实。

## 信源说明

| 信源 | 类型 | 用途 |
|------|------|------|
| [APPSO 博文](https://mp.weixin.qq.com/s/dqvRKQoH45cXL2F8z0ZHYw) | 主信源（媒体实测） | F-001~F-042 全部事实与观点 |
| 36氪/爱范儿实测 | 交叉验证 | 产品发布、额度、80+风格、"由豆包发送"等 |
| 财新/第一财经/eWeek | 权威媒体 | 产品发布日期、定位、行业背景 |
| 豆包官网 doubao.com/work | 官方来源 | 产品可用性、模型版本 |
| David Senra 播客访谈 | 引语来源 | Sam Altman 引语核验 |

## 主题关联（豆包工作主题簇）

本知识包与同组另外两篇豆包工作博文转化的知识包构成主题簇，建议按"功能实测 → 战略分析 → 组织生产力"顺序阅读：

| 知识包 | 视角与分工 | P0 核验 | 链接 |
|--------|-----------|---------|------|
| **doubao-work（本包）** | APPSO 媒体一手实测：产品功能、多模态生成、额度模型、飞书集成 | 8✅ 零勘误 | — |
| doubao-work-context-layer | AI产品阿颖战略分析：飞书作为组织 Context Layer、个人 vs 组织效率、Context 竞争论 | 4✅ 1⚠️ 1❌ | [进入](../doubao-work-context-layer/index.md) |
| doubao-work-org-productivity | 36氪行业分析：Deloitte/BCG 数据、组织 ROI、权限治理与组织闭环 | 5✅ 1⚠️ 0❌ | [进入](../doubao-work-org-productivity/index.md) |

## 知识结构

本知识包含 **4 篇概念文档**和 **2 篇信源参考**：

```
doubao-work/
├── index.md（本文件）
├── concepts/
│   ├── index.md
│   ├── 00-product-overview.md    产品概览与核心能力
│   ├── 01-multimodal-computer.md 多模态与电脑操作
│   ├── 02-feishu-integration.md  飞书深度集成
│   └── 03-work-context-thesis.md 工作现场论点
├── references/
│   ├── index.md
│   ├── article-source.md
│   └── verification.md
└── log.md
```

## 分层导航

### 概念文档（concepts/）

| 文档 | 核心内容 |
|------|---------|
| [00-product-overview](concepts/00-product-overview.md) | 产品发布、定位、文档/PPT/网页生成、AI协同编辑、额度模型 |
| [01-multimodal-and-computer](concepts/01-multimodal-and-computer.md) | Seedance/Seedream多模态、GitHub Skill、远程电脑操作 |
| [02-feishu-integration](concepts/02-feishu-integration.md) | 飞书组织架构、文档、消息、任务、多维表格、会议纪要、权限继承 |
| [03-work-context-thesis](concepts/03-work-context-thesis.md) | "进入工作现场"论点、Sam Altman引语、模型vs组织上下文 |

### 信源参考（references/）

| 文档 | 内容 |
|------|------|
| [article-source](references/article-source.md) | F-001~F-042 完整事实登记（42条） |
| [verification](references/verification.md) | 8项P0核验报告（全部通过）+ 权威来源URL |

## 信任与生命周期

- **P0核验**：8项关键声明全部通过权威交叉验证（8✅ 0⚠️ 0❌），无勘误
- **事实总数**：42条（F-001~F-042），其中客观事实33条、作者观点9条（📝标注）
- **内容敏感度**：公开（微信公开文章）
- **失效日期**：2026-12-31（产品快速迭代，功能可能变更）

## 已知边界

1. **媒体实测性质**：博文为APPSO提前体验，非官方文档；功能描述以测试时版本为准
2. **无代码/API**：本知识包无examples/目录——产品为闭源SaaS，无可复现技术步骤
3. **作者观点**：F-020/F-027/F-031/F-035~F-042为作者分析判断，非客观事实
4. **额度数据时效性**：5h滚动额度和1%消耗为测试时数据，定价和额度可能调整
5. **飞书依赖边界**：博文明确说明不用飞书也能用全部基础能力，飞书仅解锁深度集成
6. **模型版本**：核验时Seedance最新为2.5、Seedream为5.0，博文未指定具体版本号

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
references/index
log
```
