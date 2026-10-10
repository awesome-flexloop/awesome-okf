---
okf_version: "0.2"
type: bundle
title: "Cua：给 AI Agent 一台能用的电脑，Computer-Use 2.0 开源全栈"
description: "Cua（trycua/cua）Computer-Use 开源基础设施全栈——项目身份、Computer-Use 2.0 理念、五大核心模块（Driver/Fleets/Lume/CUA-S1/Bench）、许可证透明度、Stars 趋势、快速上手路径、适用场景与局限"
tags: [Cua, Computer-Use, AI Agent, trycua, 开源, 桌面自动化, 云桌面, 评测基准]
generated: { by: "blog-article-to-okf-bundle", at: "2026-10-10T10:50:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-10T10:50:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: wechat-article-finops-cua
    resource: https://mp.weixin.qq.com/s/6FaVJOhGomsSn43RdFMRlg
    title: 《开源精选 | Cua：给 AI Agent 一台能用的电脑》（微信公众号"FinOps实战"，2026-09-26）
  - id: github-api-cua
    resource: https://api.github.com/repos/trycua/cua
    title: GitHub API：trycua/cua 仓库元数据
  - id: newreleases-cua
    resource: https://newreleases.io/project/github/trycua/cua
    title: newreleases.io：trycua/cua Releases
---

# Cua：给 AI Agent 一台能用的电脑，Computer-Use 2.0 开源全栈

> **⚠️ 性质声明**：本 bundle 为**产品资讯/技术综述类知识包**，以微信公众号"FinOps实战"博文为事实基础，结合 GitHub API、newreleases.io、piwheels、官方文档页等权威来源核验。博文为第三方开源项目推介，非官方文档；作者明确声明快速上手章节的命令"全部来自官方 README"，**未提供本人实测结果**。核验发现 **0 项硬性事实错误、6 项时点/口径差异**（开发主体名称、Stars/Forks/Issues 快照、主语言、日增/Trending），已在 [references/verification.md](references/verification.md) 中如实记录。

Cua 是最近冲上 GitHub Trending 日榜前列的 AI 基础设施项目（F-018）。一句话概括它的野心：**给 AI Agent 一台它们真正能用的电脑**（F-004）。当大模型开始学会"用电脑"而不是只会"聊天"，这个项目就是那条赛道上最完整的开源工具箱（F-041）。

本知识包梳理 Cua 的项目身份、五大核心模块、许可证透明度、Stars 趋势、快速上手路径，以及作者给出的适用场景、局限与展望。

---

## 信源说明

| 信源 | 类型 | 覆盖范围 |
|------|------|---------|
| 微信公众号"FinOps实战"博文 | 主信源（第三方综述） | F-001 ~ F-053（博文全部事实与观点） |
| GitHub API：trycua/cua | 官方核验 | 仓库身份/创建时间/许可证/README 引语/动态数据（F-054~F-057） |
| newreleases.io + piwheels | 官方核验 | sandbox 版本日期、nightly 发布节奏（F-058~F-060） |
| 官方文档页（libraries.io 摘要） | 官方核验 | 安装命令、6×7 教程、Computer-Use 2.0 定义（F-061~F-062） |
| 第三方报道 | 交叉验证 | CUA-S1 开源事件、第三方组件许可证（F-063~F-064） |

核验发现 **6 项时点/口径差异（⚠️）、0 项硬性错误（❌）**，完整核验报告见 [references/verification.md](references/verification.md)。

---

## 📚 知识结构总览

```
cua/
├── concepts/              # 核心概念文档（6篇）
│   ├── 00-project-overview.md        # 项目身份、Computer-Use 2.0 理念、三大难题
│   ├── 01-five-core-modules.md       # 五大核心模块详解
│   ├── 02-ecosystem-and-licensing.md # 许可证透明度、语言构成、工程化成熟度
│   ├── 03-stars-and-momentum.md      # Stars 趋势、社区活跃度、发布节奏
│   ├── 04-getting-started.md         # 快速上手路径（安装命令、建议顺序）
│   └── 05-scenarios-and-limitations.md  # 适用场景、局限与展望
├── references/            # 信源登记簿（2篇）
│   ├── article-source.md  # F-001~F-065 事实完整登记
│   └── verification.md    # 18 项核验结论与 6 项时点差异说明
├── index.md               # 本文件
└── log.md                 # 生成日志
```

---

## 🧭 分层导航

### 概念层（concepts/）

| 文档 | 核心内容 |
|------|---------|
| [项目概览](concepts/00-project-overview.md) | Cua 身份（Cua AI, Inc./MIT/trycua/cua）、Computer-Use 2.0 理念、三大难题、三类人群、GitHub 官方核验事实 |
| [五大核心模块](concepts/01-five-core-modules.md) | Driver（后台投递）、Fleets（隔离云桌面）、Lume（Apple Silicon VM）、CUA-S1（System 1 模型）、Bench（评测闭环） |
| [生态与许可证](concepts/02-ecosystem-and-licensing.md) | MIT + Kasm MIT + OmniParser CC-BY-4.0 + AGPL 边界、多语言架构、工程化成熟度、快照后演进 |
| [Stars 趋势与社区活跃度](concepts/03-stars-and-momentum.md) | 博文快照 vs 官方时点对比、增长态势解读、每日 nightly 发布节奏 |
| [快速上手](concepts/04-getting-started.md) | Driver/Lume/Bench/Fleets 四条路径安装命令、6×7 任务、作者建议顺序 |
| [适用场景、局限与展望](concepts/05-scenarios-and-limitations.md) | 四类适用场景、四点风险、2026 Computer-Use 展望、"卖水人"逻辑 |

### 信源层（references/）

| 文档 | 核心内容 |
|------|---------|
| [博文信源事实清单](references/article-source.md) | F-001~F-053 博文事实登记 + F-054~F-065 核验补充与时点勘误 |
| [核验报告](references/verification.md) | 18 项核验逐项结论表（12✅ + 6⚠️ + 0❌），6 项时点差异详解，权威来源 URL |

---

## ✅ 信任与生命周期说明

- **文档版本**：基于 2026-09-26 发布的博文与 2026-10-10 完成的核验生成
- **覆盖事实**：共 65 条事实（F-001 ~ F-053 来自博文，F-054 ~ F-065 为核验补充）
- **核验情况**：18 项声明经权威来源核验，12 项通过，6 项时点/口径差异，0 项失败
- **status**：stable — 项目存在且活跃，核心身份/协议/模块事实已确认
- **stale_after**：2026-12-31 — 项目每日 nightly、组件版本高频迭代，年末复核
- **方法论链路**：R（事实采集）→ I（洞察提炼）→ E（信源先行成文）→ V（核验），详见 [log.md](log.md)

### 已知边界

1. **第三方综述性质**：博文为"FinOps实战"公众号的开源项目推介，非官方文档。快速上手命令转述自官方 README，作者未实测。
2. **⚠️ 动态数据为时点快照**：Stars/Forks/Issues/主语言为博文 2026-09-20 快照；官方 2026-10-10 时点值见 verification.md（F-055/F-057）。
3. **⚠️ 开发主体名称**：GitHub owner 为 org `trycua`，博文称"Cua AI, Inc."为官网主体口径，无法由 GitHub API 直接证实（F-054）。
4. **⚠️ 日增 +859 / Trending 第 2**：为当日快照，无法事后精确复核；多方报道佐证当时在 Trending 前列（F-018）。
5. **CUA-S1 为 source-only 早期研究性发布**：生产环境慎用（F-049/F-063）。
6. **Fleets 为付费服务**：池保留容量需按教程清理（F-038/F-048）。
7. **快照后演进**：cua-sandbox 0.9.0（2026-10-01）、Cua Spaces 0.1.0 等为博文未覆盖的新动态（F-059/F-065）。

---

**本知识包共收录 9 个内容文档（6 个概念 + 2 个信源 + 1 个生成日志），外加 2 个子目录索引与根索引，合计 12 个文件。**

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
references/index
log
```