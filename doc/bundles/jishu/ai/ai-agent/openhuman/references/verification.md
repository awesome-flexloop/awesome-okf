---
okf_version: "0.2"
type: Reference
title: "P0 核验报告：OpenHuman 博文（开源先驱）"
description: "12项P0声明核验——GPLv3/9天Trending/Memory Tree机制/TokenJuice 80%/四会议平台/安装命令6项通过，集成数渠道数容量星标提交数等6项口径漂移或单源，0硬证伪，勘误六条"
tags: [核验报告, OpenHuman, P0核验, 勘误, 口径漂移, GitHub]
generated: { by: "blog-article-to-okf-bundle", at: "2026-09-16T20:30:00+08:00" }
status: stable
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/pdH1ZB3yPfDdA7Ay72hjGQ
    title: 开源先驱博文（2026-07-28）
  - id: github
    url: https://github.com/tinyhumansai/openhuman
    title: OpenHuman 官方 GitHub 仓库（页面+Contents/Releases/Tags API，2026-09-16 实测）
  - id: gitbook-memory
    url: https://tinyhumans.gitbook.io/openhuman/features/memory-tree
    title: 官方文档：Memory Tree
  - id: gitbook-compression
    url: https://tinyhumans.gitbook.io/openhuman/features/token-compression
    title: 官方文档：Smart Token Compression（TokenJuice）
  - id: official-guide
    url: https://www.openhuman.dev/
    title: OpenHuman Guide（2026-05-17 快照的第三方官方指南）
---

# P0 核验报告（verification）

> 核验时间：2026-09-16 ｜ 核验方式：browser_use 直取 GitHub 渲染页 + GitHub Contents/Releases/Tags API + 官方 GitBook WebFetch + WebSearch 交叉
> 信源距离预判：**第三方自媒体推广文**（作者未声明一手实测，营销叙事浓度中高）
>
> **结论：12 项 P0 = 6 ✅ + 6 ⚠️（口径漂移/单源），0 ❌ 硬证伪。博文主结论（本地优先的有记忆 agent harness 真实存在且发布初期爆火）成立；但博文口径数字成组老化，正文一律呈现 2026-09-16 官方现值并标注博文口径。status: stable。**

## 一、勘误四张清单逐项过筛

### 清单① 日期/版本表

| 博文口径 | 权威源现值（2026-09-16） | 结论 |
|---------|------------------------|------|
| v0.63.3，"迭代了六十多个版本"（F-005） | 最新 release v0.63.12（2026-08-07）；**release 共 56 个**（最早 v0.49.32，2026-03-31）；**tag 共 106 个**（F-046） | ⚠️ **勘误 1**：v0.63.3 与博文时点相容，但"六十多个版本"按 releases 口径不成立（56<60），按 tags 口径则远超（106）；博文未注明口径 |
| "发布一周内连续 9 天 Trending 第一"（F-004） | README 原文自认发布后一周内连续 9 天全站第一（F-048） | ✅ 通过（博文标题省略"发布后一周内"时间锚点，已在正文补回） |
| 仓库时间线 | 创建 2026-02-18；最早 release 2026-03-31；"2026-05-13 beta 上线"仅见 AI 生成知识库（F-060，弱源不采） | ✅ 主线时间以 GitHub 元数据为准 |

### 清单② 成效数字溯源表

| 博文口径 | 权威源 | 结论 |
|---------|--------|------|
| TokenJuice 最高省 80% token（F-016） | README "up to 80% fewer tokens" + GitBook 专页双证（F-053） | ✅ 通过 |
| 省幅细分（HTML→MD 40-60% 等）+ 金额（$0.04→$0.008、月 $60→$12，F-020/F-021） | 官方文档无对应数字——为博文基于 GPT-4o 价格与假设输入的**自行测算** | ⚠️ **勘误 2**：正文标"博文测算"，80% 上限可引、细分数字不得当作官方规格 |
| Memory Tree "容量可达 10 亿 token"（F-011/F-019） | 官方 README 与 GitBook Memory Tree 页**无任何容量/速率数字**；仅第三方 AI 生成知识库（agentic-ai.readthedocs.io）写 "1 billion tokens / 10M tokens @4,000 t/s / NeoCortex"（F-052） | ⚠️ **勘误 3**：主打卖点数字官方未背书，"NeoCortex"命名亦不见于官方文档；正文呈现官方机制，数字标注"第三方弱源单源" |
| 7,800+ Star（标题，F-006）、3,926 commits（F-005） | 2026-09-16 实测 **39,814 stars / 20,551 commits**（F-044/F-047）；历史值无法经官方渠道回溯；第三方弱源称 5 月已 27k stars，与博文 7 月 7,800 数量级冲突（F-064） | ⚠️ **勘误 4**：两个历史数字均不可证实；正文只给权威时点值，博文数字作历史口径保留并明示不可回溯 |

### 清单③ 口径对照表

| 博文口径 | 官方现值 | 结论 |
|---------|---------|------|
| 118+ OAuth 集成（F-015 等，全文 3 处） | 2026-09 README：**100+** OAuth + 5,000+ MCP + 90,000+ Skills；2026-05 openhuman.dev 快照确为 118+（F-049） | ⚠️ **勘误 5**：博文在 7-28 时点可能准确（5 月快照旁证），但当前官方口径已收缩为 100+；正文使用现值并注口径漂移 |
| 17 个消息渠道（F-022） | README 现列 **15 个**（Telegram/Discord/Slack/WhatsApp/Signal/iMessage…）+ 原生邮件 IMAP/SMTP（F-050） | ⚠️ **勘误 6**：现口径 15；正文用现值 |
| 建议 8GB+ 内存、4GB 会卡（F-035） | 官方指南：基线 **4GB+**（Getting Started 口径），大邮箱/代码库+本地模型建议 16GB+（F-059） | ⚠️ 两口径并存呈现：官方 4GB+ 可跑，博文 8GB+ 为体验建议 |
| 竞品三款（Claude Cowork/OpenClaw/OpenHuman，F-022） | openhuman.dev 官方表为四款，另含 Hermes Agent（MIT/Terminal-first）（F-061） | ✅ 三款描述与官方一致（闭源/MIT 口径吻合），正文补列 Hermes Agent |

### 清单④ 引文/功能声明逐字核对

| 博文声明 | 核验 | 结论 |
|---------|------|------|
| "Every model…stateless." 定位语（F-008） | 本次核验未在 README 渲染页定位到该句逐字原文（可能出自官网/GitBook/早期 README） | ⚠️ 标"博文转述引文，未逐字定位"，引号内容按博文原文呈现 |
| Meet/Zoom/Teams/Webex 真人参会+转录（F-025） | README 对比行逐字证实 "Joins Meet/Zoom/Teams/Webex, speaks, live transcript"（F-054） | ✅ |
| Signal 加密 A2A + x402 支付（F-028 部分） | README 逐字证实 Signal-protocol E2E + x402 payments（F-055） | ✅（部分） |
| tiny.place @handle、x402 **USDC 赏金**、Agent 互相雇佣（F-028） | README 未见 tiny.place/USDC/bounty 字样（F-055） | ⚠️ 归并勘误 3 同段处理：仅 x402 payments 有据，支付币种与赏金机制单源 |
| ChaCha20-Poly1305（F-029） | README 未见（F-056） | ⚠️ 单源，正文技术栈表不列或标注 |
| React 前端、Claude/GPT/Gemini 模型（F-029） | README 无 React（TS 前端）；模型以"自有 provider key + Ollama"表述，G PT/Gemini 未具名（F-057） | ⚠️ 正文按官方口径修正 |
| 一键隐私模式/本地推理（F-027） | Ollama 本地模型与本地 Memory Tree 有据；"所有推理不离开设备"为博文强化表述（托管模型仍是官方选项之一） | ⚠️ 正文注明"可选本地，非默认全离线" |
| 内置完整 Linux 沙箱（导语） | README/GitBook 未见（F-062） | ⚠️ 单源存疑，正文不收为主干事实 |
| 安装脚本/brew/源码构建（F-030/F-032） | install.sh、install.ps1 HTTP 200 存在；brew cask 见 INSTALL.md（.deb/AUR 同页）；pnpm/Node 24+ 工具链与博文一致（F-058） | ✅ |
| GPLv3（F-007） | 侧栏 GPL-3.0 + API SPDX 确认（F-045） | ✅ |

## 二、P0 核验结论矩阵

| # | 核验对象 | 覆盖事实 | 结论 |
|---|---------|---------|------|
| V1 | 仓库存在性、定位与许可证 | F-007/F-042/F-043/F-045 | ✅ |
| V2 | "9 天 Trending 第一" | F-004/F-048 | ✅（补时间锚点） |
| V3 | 版本序列（v0.63.3/六十多版本） | F-005/F-046 | ⚠️ 勘误 1 |
| V4 | Star/commit 历史数字 | F-005/F-006/F-044/F-047/F-064 | ⚠️ 勘误 4 |
| V5 | Memory Tree 机制与 10 亿 token | F-011/F-014/F-018/F-019/F-051/F-052 | 机制 ✅ ／ 容量数字 ⚠️ 勘误 3 |
| V6 | TokenJuice 80% 与测算金额 | F-016/F-020/F-021/F-053 | 上限 ✅ ／ 测算 ⚠️ 勘误 2 |
| V7 | 集成数 118+ 与渠道数 17 | F-015/F-022/F-049/F-050 | ⚠️ 勘误 5、6 |
| V8 | 四平台会议 Agent | F-025/F-054 | ✅ |
| V9 | Agent Economy（Signal/x402/USDC/tiny.place） | F-028/F-055 | ⚠️ 部分有据 |
| V10 | 技术栈（React/模型/ChaCha20/Linux 沙箱/隐私） | F-027/F-029/F-056/F-057/F-062 | ⚠️ 多处博文口径 |
| V11 | 安装与构建路径 | F-030/F-032/F-058 | ✅ |
| V12 | 竞品对照与硬件口径 | F-022/F-035/F-059/F-061 | ✅（补 Hermes Agent）+ ⚠️ 内存双口径 |

## 三、勘误落实记录

六条勘误（版本口径 / 金额测算 / 10 亿 token / 历史 star·commits / 118→100+ / 17→15）已在 concepts 正文逐项落实：呈现官方现值、博文口径降级为引文，并集中在 [03-landscape-and-tradeoffs](../concepts/03-landscape-and-tradeoffs.md) 的"数字口径速查"表。无任何博文错误数字以事实身份流入正文主干。

## 四、权威信源清单

| 信源 | URL | 信源距离 | 用途 |
|------|-----|---------|------|
| GitHub 仓库 | https://github.com/tinyhumansai/openhuman | 官方一手 | 星标/提交/release/tag/license/README 引文 |
| 官方文档 Memory Tree | https://tinyhumans.gitbook.io/openhuman/features/memory-tree | 官方一手 | 记忆管线机制（反证 10 亿数字） |
| 官方文档 TokenJuice | https://tinyhumans.gitbook.io/openhuman/features/token-compression | 官方一手 | 80% 上限与压缩管线 |
| OpenHuman Guide | https://www.openhuman.dev/ | 第三方转录官方（2026-05 快照） | 118+ 旧口径、硬件基线、四款竞品表 |
| agentic-ai.readthedocs.io | https://agentic-ai.readthedocs.io/en/latest/AgentPlatforms/openhuman/ | AI 生成知识库（弱源） | 10 亿 token/NeoCortex 唯一出处，标弱源 |
| honbul.tistory.com/266 | https://honbul.tistory.com/m/266 | 第三方独立长评（2026-05-19） | 主干功能旁证 |
