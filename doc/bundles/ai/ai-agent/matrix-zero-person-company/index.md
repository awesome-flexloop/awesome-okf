---
okf_version: "0.2"
type: bundle
title: "Matrix：让 Agent 帮你开一家 0 人公司"
description: "智潮笔记解析Matrix（matrix.build）Agent公司操作系统——CEO Office统筹+部门化分工+durable memory+proof机制+Stripe商业基建，九模型接入矩阵，GDPval 95.45%厂商自述证据边界，AI从造到卖的三阶段论"
tags: [Matrix, 0人公司, Agent公司, AI Agent, CEO Office, Agential OKR, durable memory, proof机制, Stripe, 多模型编排, 厂商自述]
generated: { by: "blog-article-to-okf-bundle", at: "2026-09-01T17:30:00+08:00" }
verified: { by: "process:blog-article-to-okf-wiki-v", at: "2026-09-01T17:30:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/C5clrnoai50eneYvgP1nLw
    title: 《这个AI工具真的疯了！它可以帮你开一家"0人公司"，只需要一个想法，Agent就能自己去赚钱》（智潮笔记，2026-07-04）
  - id: official-1
    url: https://www.aitoolnet.com/matrix
    title: AI Toolnet 收录页（转录 Matrix 官方文案）
  - id: official-2
    url: https://hotools.com/item/matrix
    title: Hotools 收录页（2026-06-23）
  - id: official-3
    url: https://aigjdh.com/sites/2669.html
    title: AI工具集（aigjdh）收录页
---

# Matrix：让 Agent 帮你开一家 0 人公司

> **⚠️ 厂商自述数据提示**：本知识包所有成效数字（GDPval-Bench 95.45%、100+ 定制视频、700k+ 播放、$3,000+ 收入）均转述自 Matrix 官网宣称，**无独立第三方验证**，引用前请阅读[证据边界文档](concepts/02-case-evidence-boundary.md)。

> **性质声明**：本知识包基于智潮笔记 2026-07-04 发布的产品介绍/评论文章转化。博文为第三方自媒体对 Matrix 官网信息与案例的转述，非官方文档或技术教程。**本包无 examples/ 目录**——博文不含任何读者可照做的安装/配置/代码/实测流程（操作可复现性两问皆否）。作者观点已用"作者观点"显式标注。

## 信源说明

| 信源 | 类型 | 用途 |
|------|------|------|
| [智潮笔记博文](https://mp.weixin.qq.com/s/C5clrnoai50eneYvgP1nLw) | 主信源（第三方自媒体转述） | F-001~F-038 全部事实与观点 |
| AI Toolnet / Hotools / AI工具集收录页 | 第三方转录官方文案 | 产品存在性、架构、模型列表、商业基建交叉核验 |
| danilchenko.dev GPT-5.5 评测 | 第三方评测 | GDPval 84.9% 口径参照 |
| OpenAI × Hebbia 官方页 | 同名排除依据 | 区分金融 AI 平台 "Matrix" |

## 知识结构

本知识包含 **3 篇概念文档**和 **2 篇信源参考**：

```
matrix-zero-person-company/
├── index.md（本文件）
├── concepts/
│   ├── index.md
│   ├── 00-product-overview.md           产品概览与接入体系
│   ├── 01-agent-company-architecture.md Agent 公司架构机制
│   └── 02-case-evidence-boundary.md     案例成效与证据边界
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
| [00-product-overview](concepts/00-product-overview.md) | 0人公司叙事、九模型接入矩阵（Neo/Claude Code/Codex/ChatGPT/Gemini/GLM/DeepSeek/Kimi/Qwen）、OpenRouter/自有账号接入、macOS 单平台单源声明 |
| [01-agent-company-architecture](concepts/01-agent-company-architecture.md) | CEO Office 统筹、部门化与领队路由、durable work memory、统一文件系统、proof 机制、商业基建（Stripe/域名/钱包）、VPTD 经济指标、Mermaid 架构图 |
| [02-case-evidence-boundary](concepts/02-case-evidence-boundary.md) | aivideopro.io 案例、GDPval 95.45% 口径风险（Elo vs 百分比）、证据分级总表、作者"冷水"清单、同名产品防混淆 |

### 信源参考（references/）

| 文档 | 内容 |
|------|------|
| [article-source](references/article-source.md) | F-001~F-046 完整事实登记（46条） |
| [verification](references/verification.md) | 6项P0核验报告（2✅ 3⚠️ 1单源，0❌无勘误） |

## 信任与生命周期

- **P0核验**：6 项 = 2✅ + 3⚠️ + 1 单源，**0 ❌ 无硬错误，无勘误**（status: stable）
- **事实总数**：46条（F-001~F-046），其中核验补充 8 条、作者观点 13 条（显式标注）
- **内容敏感度**：公开（微信公开文章）
- **失效日期**：2026-12-31（产品早期阶段快速迭代，平台形态/接入列表可能变更）

## 已知边界

1. **厂商自宣性质**：成效数字全部为厂商/客户自述（GDPval 95.45%、案例数字），无独立验证，index 顶部已设提示块
2. **GDPval 口径未验证**：95.45% 的任务集与分母无法确认；Anthropic 官方 GDPval-AA 为 Elo 制，与百分比口径不可混比——该数字不得用于横向模型比较
3. **单源声明**：macOS 桌面应用、Web 端未上线仅博文提及，以官网实时信息为准
4. **无代码/API**：本包无 examples/——产品为闭源商业平台，无可复现技术步骤
5. **作者观点分层**：F-005/F-008/F-017/F-026/F-028~F-038 为智潮笔记分析判断（含"AI 三阶段论"），非客观事实
6. **同名产品**：Hebbia "Matrix"（金融AI）、matrix-agent-neo 仓库、NeoLabs NeoAgent 均非本产品

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```
