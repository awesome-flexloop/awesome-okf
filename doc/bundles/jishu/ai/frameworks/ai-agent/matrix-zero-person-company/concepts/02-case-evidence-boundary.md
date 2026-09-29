---
okf_version: "0.2"
type: Concept
title: "案例成效与证据边界：厂商自述 vs 独立验证"
description: "aivideopro.io视频工作室案例、GDPval-Bench 95.45%宣称的证据分级——全部成效数字仅厂商自述无独立验证，含GDPval口径风险与读数指南"
tags: [aivideopro, GDPval, 厂商自述, 证据分级, 效果核验, 风险边界]
generated: { by: "blog-article-to-okf-bundle", at: "2026-09-01T17:30:00+08:00" }
verified: { by: "process:blog-article-to-okf-wiki-v", at: "2026-09-01T17:30:00+08:00" }
status: stable
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/C5clrnoai50eneYvgP1nLw
    title: 智潮笔记博文（2026-07-04）
  - id: official-1
    url: https://www.aitoolnet.com/matrix
    title: AI Toolnet 收录页（转录官方文案）
  - id: official-3
    url: https://www.danilchenko.dev/posts/gpt-5-5-review/
    title: GPT-5.7 评测（GDPval 第三方口径参照）
---

# 案例成效与证据边界：厂商自述 vs 独立验证

> **本章是本 bundle 的风险读数指南**：Matrix 的所有成效证据目前均无法独立验证。这不是说数字是假的，而是说**引用前必须知道它们处在证据链的哪一层**。

## 一、旗舰案例：aivideopro.io AI 视频工作室

博文转述官网案例（F-020~F-022）：

| 环节 | 宣称内容 |
|------|---------|
| 商业链路 | 定位、报价页面、作品展示、创作者流程、Stripe 收款、付费套餐、客户 brief intake 全链路接通 |
| 生产端 | 交付 100+ 条定制视频 |
| 分发端 | 自动化 YouTube 频道，最高短视频 700k+ 播放 |
| 收入（aitoolnet 转录补充） | $3,000+ 收入 |

**证据分级：⚠️ 厂商/客户自述**。三个独立第三方工具站（aitoolnet/hotools/aigjdh）的转述相互一致（F-044），但全部溯源至 Matrix 官方文案，无独立流量/收入验证。

## 二、基准宣称：GDPval-Bench 95.45%

博文称 Matrix 在 GDPval-Bench 跑出 95.45%，超过 Codex CLI 的 84.9% 和 Claude Opus 4.7 的 80.3%（F-025），并将其解读为"harness 工程很强"（F-026，作者解读）。

**证据分级：⚠️ 厂商自述 + 口径未验证**，三个独立读数风险：

1. **95.45% 无独立出处**：仅见于 aitoolnet 转录的 Matrix 官方文案（F-043），未找到任何第三方评测或榜单可溯源
2. **对照数字口径存疑**：Codex CLI 84.9% 与第三方评测中 GPT-5.5 的 GDPval 84.9% 数值吻合（F-043），但无法确认 Matrix 官网对照表的对象与口径；Claude Opus 4.7 的 80.3% 无法独立溯源
3. **GDPval 口径分裂**：Anthropic 官方对 GDPval-AA 采用 **Elo 制**（如 Opus 4.6 = 1606、Opus 4.8 = 1890），而百分比口径见于部分第三方评测——两种口径不可直接混比，95.45% 的分母与任务集无法确认

**正确的读数姿势**：95.45% 可以作为"厂商对其 harness 工程的自信宣称"引用，不能作为"Matrix 比 Claude/GPT 强"的结论引用。

## 三、证据边界总表

| 声明 | 证据层级 | 可信度处理 |
|------|---------|-----------|
| 产品存在、九模型接入、架构机制、商业基建 | ✅ 三方工具站转录交叉一致 | 可正常引用 |
| aivideopro.io 案例（100+ 视频/700k+ 播放/$3k 收入） | ⚠️ 厂商/客户自述 | 引用须标注"厂商自述" |
| GDPval-Bench 95.45% 及对照数字 | ⚠️ 厂商自述 + 口径未验证 | 引用须标注，不得用于横向比较 |
| macOS 桌面应用、Web 未上线 | 单源（仅博文） | 以官网实时信息为准 |
| "0人公司"有效性、"AI 三阶段论" | 📝 作者观点 | 观点，非事实 |

## 四、作者的"冷水"清单（观点，但与证据边界互洽）

博文在展示案例后主动列出四点克制判断（F-030/F-031/F-032/F-035，作者观点）：

1. Matrix 远没到"躺着赚钱"的程度——结果取决于目标是否清晰、懂不懂这门生意
2. 跑通案例的人本身不是小白（懂社区、懂获客、懂客户心理）
3. Matrix 承担的是"费时间但不需要顶级创意"的执行环节
4. 真正的判断、审美在人手里；公司能否赚钱取决于 CEO 位置上的人

这四点与本文档的证据边界互相印证：**即使厂商自述数字全部为真，它们也只证明"执行链路技术上可跑通"，不证明"任何人都能用它赚钱"**。

## 五、同名产品防混淆

核验中发现三个同名干扰项（F-045），检索 Matrix 相关资料时须与本产品区分：

| 名称 | 实际产品 | 区分特征 |
|------|---------|---------|
| Hebbia "Matrix" | 金融/法律多智能体研究平台（OpenAI 官网收录） | o3-mini/o1/GPT-4o，面向投行/律所 |
| matrix-agent-neo/matrix-core | GitHub fork 仓库（fork 自 Sidiora-Labs） | 与 matrix.build 无关 |
| NeoAgent（NeoLabs-Systems） | 自托管开源 AI Agent | npm 安装、Android 控制等，与 Matrix 内置 Neo Agent 无关 |

## 相关文档

- 产品定位：[00-product-overview](00-product-overview.md)
- 架构机制：[01-agent-company-architecture](01-agent-company-architecture.md)
- 核验报告：[references/verification](../references/verification.md)
