---
okf_version: "0.2"
type: bundle
title: "OpenHuman：有记忆的本地优先个人 AI 助手"
description: "开源先驱博文转化——TinyHumans OpenHuman（GPL-3.0/Rust/Tauri 开源 agent harness）：Memory Tree 三树记忆管线、TokenJuice 80%压缩、四平台会议Agent、Signal+x402；12项P0核验6✅6⚠️0❌，六条数字口径勘误"
tags: [OpenHuman, TinyHumans, 个人AI助手, Agent Harness, Memory Tree, TokenJuice, 桌面Agent, GPL-3.0, Tauri, 厂商口径]
generated: { by: "blog-article-to-okf-bundle", at: "2026-09-16T20:30:00+08:00" }
verified: { by: "process:blog-article-to-okf-wiki-v", at: "2026-09-16T20:30:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/pdH1ZB3yPfDdA7Ay72hjGQ
    title: 《又一个人AI助手炸了。连续9天GitHub Trending第一，3,900次提交，7,800+ Star》（开源先驱/豆芽菜小萌，2026-07-28）
  - id: github
    url: https://github.com/tinyhumansai/openhuman
    title: OpenHuman 官方 GitHub 仓库（2026-09-16 实测：39.8k stars / GPL-3.0 / v0.63.12）
  - id: gitbook-memory
    url: https://tinyhumans.gitbook.io/openhuman/features/memory-tree
    title: 官方文档：Memory Tree
  - id: gitbook-compression
    url: https://tinyhumans.gitbook.io/openhuman/features/token-compression
    title: 官方文档：TokenJuice 智能压缩
---

# OpenHuman：有记忆的本地优先个人 AI 助手

> **⚠️ 数字口径提示（先读）**：本包源自 2026-07-28 第三方推广博文，项目处于 Early Beta 周级发版期。博文的 7,800 Star/3,926 commits/118+ OAuth/17 渠道/10 亿 token 等数字在 2026-09-16 核验时均已漂移或仅见弱源（官方现值 39.8k stars、20,551 commits、100+ OAuth、15 渠道；"10 亿 token"官方文档无数字）。**引用本包任何数字前先看[核验报告](references/verification.md)与 03 篇"数字口径速查"。**

> **性质声明**：本知识包基于公众号「开源先驱」（作者豆芽菜小萌）2026-07-28 产品介绍/推广文转化，作者自陈基于"社区讨论和评测"、未声明一手实测。**本包无 examples/ 目录**——操作可复现性两问第②问（作者实测可复现）为否，按技术综述/产品介绍骨架处理；安装命令虽经官方核验真实存在，仅作事实章节而非演练教程。作者观点已全文显式分层。

## 信源说明

| 信源 | 类型 | 用途 |
|------|------|------|
| [开源先驱博文](https://mp.weixin.qq.com/s/pdH1ZB3yPfDdA7Ay72hjGQ) | 主信源（第三方自媒体，2026-07-28） | F-001~F-042 博文事实与观点 |
| [GitHub 仓库](https://github.com/tinyhumansai/openhuman) | 官方一手（2026-09-16 页面+API 实测） | 星标/提交/版本/license/README 引文核验 |
| [官方 GitBook](https://tinyhumans.gitbook.io/openhuman/) | 官方一手 | Memory Tree 与 TokenJuice 机制 |
| [openhuman.dev](https://www.openhuman.dev/) | 第三方转录官方指南（2026-05 快照） | 旧口径旁证、硬件基线、竞品表 |

## 知识结构

```
openhuman/
├── index.md（本文件）
├── concepts/
│   ├── index.md
│   ├── 00-what-is-openhuman.md            定位/热度/时间线/技术栈/安装
│   ├── 01-memory-tree-and-tokenjuice.md   记忆三树管线 + 压缩路由器（含勘误）
│   ├── 02-runtime-and-agent-design.md     编排/会议/隐私/Agent 间经济
│   └── 03-landscape-and-tradeoffs.md      竞品/短板/口径速查/观点分层
├── references/
│   ├── index.md
│   ├── article-source.md                  F-001~F-064 事实登记（64 条）
│   └── verification.md                    12 项 P0（6✅ 6⚠️ 0❌，勘误六条）
└── log.md
```

## 分层导航

### 概念文档（concepts/）

| 文档 | 核心内容 |
|------|---------|
| [00-what-is-openhuman](concepts/00-what-is-openhuman.md) | 开源 agent harness 定位、stateless 命题、双时点仓库指标、GPL-3.0/Rust/Tauri、四种安装方式与授权三步走 |
| [01-memory-tree-and-tokenjuice](concepts/01-memory-tree-and-tokenjuice.md) | 确定性记忆管线、source/topic/global 三树、作业队列与 leaf 生命周期、SQLite+Obsidian vault；10 亿 token 弱源勘误；TokenJuice 七步管线与博文金额测算边界 |
| [02-runtime-and-agent-design](concepts/02-runtime-and-agent-design.md) | 检查点图/Split Brain、Subconscious、吉祥物、Meet/Zoom/Teams/Webex 参会、本地隐私的真实边界、Signal E2E + x402（USDC/tiny.place 单源） |
| [03-landscape-and-tradeoffs](concepts/03-landscape-and-tradeoffs.md) | 合并后的四款竞品对照、Early Beta 五类短板、数字口径速查表、作者观点与组合使用建议 |

### 信源参考（references/）

| 文档 | 内容 |
|------|------|
| [article-source](references/article-source.md) | F-001~F-064 完整事实登记（64 条：博文 42 + 核验补充 22） |
| [verification](references/verification.md) | 12 项 P0 核验（6✅ 6⚠️ 0 硬证伪）+ 勘误四张清单 + 六条勘误落实 |

## 信任与生命周期

- **P0 核验**：12 项 = 6✅ + 6⚠️，**0 ❌**——主结论成立但成组数字老化/单源，勘误完整（status: stable）
- **事实总数**：64 条（F-001~F-064），其中作者观点 6 条、博文测算 2 条，均显式标注
- **内容敏感度**：公开（微信公开文章 + 公开仓库）
- **失效日期**：2026-12-31（Early Beta、周级发版；星标/集成数/版本号强时效，到期前应复核官方 README）

## 已知边界

1. **博文为第三方推广文**：作者未声明一手实测，功能体验描述多源自社区材料；主干功能经官方证实，但"实际体验"类段落不代表测评结论
2. **历史热度数字不可回溯**：7,800 Star / 3,926 commits 无法证实，与第三方弱源（称 5 月已 27k stars）冲突；唯一权威时点值为 2026-09-16 的 39,814 / 20,551
3. **"10 亿 token / NeoCortex / 4,000 t/s"无官方背书**：仅 AI 生成知识库单源；官方只描述机制不给容量数字
4. **金额测算为博文自算**：80% 上限是官方的，$0.04→$0.008 等具体金额依赖博文自选输入与 GPT-4o 价格假设
5. **本地推理是可选项不是默认**：记忆数据默认本地，embedding/推理可经后端；全离线需显式切 Ollama
6. **无移动端**：仅 Windows/macOS/Linux 桌面；中文体验取决于所选模型
7. **观点非事实**：爆火归因、"不是 ChatGPT 替代品"、人群建议等为作者判断，已逐处标注

## 主题关联

- [second-me](../second-me/index.md)：训练型个人分身（LoRA + 三层记忆 HMM）vs OpenHuman 集成摘要型记忆
- [pi-agent-harness](../pi-agent-harness/index.md)：同为 agent harness 定位的高层综述
- [doubao-work](../doubao-work/index.md)：组织上下文路线的产品实测对照

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```
