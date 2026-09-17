---
okf_version: "0.2"
type: Concept
title: "Agent 运行时与产品设计：编排、会议、隐私与 Agent 间经济"
description: "检查点图编排与Split Brain双脑、研究侦察前置、Subconscious后台循环、桌面吉祥物与语音、Meet/Zoom/Teams/Webex真人参会、本地隐私模式与Ollama、Signal E2E+x402（tiny.place/USDC口径勘误）"
tags: [Agent编排, Split Brain, Subconscious, 会议Agent, 桌面吉祥物, Ollama, Signal Protocol, x402, 隐私]
generated: { by: "blog-article-to-okf-bundle", at: "2026-09-16T20:30:00+08:00" }
verified: { by: "process:blog-article-to-okf-wiki-v", at: "2026-09-16T20:30:00+08:00" }
status: stable
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/pdH1ZB3yPfDdA7Ay72hjGQ
    title: 开源先驱博文（2026-07-28）
  - id: github
    url: https://github.com/tinyhumansai/openhuman
    title: OpenHuman GitHub 仓库
  - id: official-guide
    url: https://www.openhuman.dev/
    title: OpenHuman Guide
---

# Agent 运行时与产品设计：编排、会议、隐私与 Agent 间经济

## 一、编排器：检查点图、双脑与前置侦察

博文把 OpenHuman 的第二、第三大能力概括为"出色的编排器"和"深度研究员"（F-012/F-013）：

- **基于检查点图（checkpoint graph）的 Agent 运行时**管理一支 Agent 舰队：快速反射 Agent 处理入站流量（消息、通知等轻量事件，追求秒回），深度推理核心把复杂工作委派给 Worker Agent——博文称之为 **Split Brain 双脑架构**（F-026，轻事快回、重活慢做）
- **研究侦察兵前置**：在用户问完问题之前先扫记忆库与文件系统，消除冷启动与"让我想想"的等待（F-013）。其工程基础即 Memory Tree 的 20 分钟 auto-fetch 与三树预聚合（见 [01-memory-tree-and-tokenjuice](01-memory-tree-and-tokenjuice.md)）

> 说明：检查点图与 Worker 舰队的**内部实现细节**博文未展开，官方 README 层面可对应的是 "agent orchestration and workflows" 的自我定位（F-043）；具体运行时数据结构以官方文档后续章节为准，本包不替官方补全架构细节。

## 二、Subconscious：不交互时也在运转

博文描述的**潜意识系统（Subconscious）**是一条后台循环：持续对比你的"世界状态"、推进长期目标、撰写晨间简报（F-024）。这与 Memory Tree 官方机制中的后台作业体系相互呼应——embeddings、实体抽取、摘要桶 seal、每日 digest 都在后台 worker 完成，UI 不阻塞（F-051）。"用户不主动交互时 Agent 仍在做维护性工作"是该产品与按需应答式聊天工具的核心体验差异之一。

## 三、桌面吉祥物与会议 Agent

- **桌面吉祥物（Mascot）**：有表情、会说话的常驻形象，承担新邮件摘要、日历提醒、系统通知的主动播报；关闭主窗口后仍在桌面常驻（F-023）。第三方资料显示其语音链路为 STT 输入 + ElevenLabs TTS 输出 + 口型同步（F-063 旁证，具体供应商以官方为准）
- **会议 Agent**——这是 OpenHuman 辨识度最高的功能之一，且获官方 README 对比行逐字证实（F-054 ✅）：

  > "🚀 Joins Meet/Zoom/Teams/Webex, speaks, live transcript"

  即可以真人参与者身份加入 **Google Meet / Zoom / Teams / Webex** 四类会议、会中发言、实时转录；博文另称其能自动从日历加入并生成摘要（F-025，日历联动方向与 20 分钟同步体系相容，具体触发细节以官方文档为准）。

## 四、隐私模式：本地优先的真实边界

博文的"一键隐私模式"说法（F-027）需要拆开读：

| 层面 | 官方事实 |
|------|---------|
| 记忆数据 | Memory Tree 全部落在本机 `~/.openhuman`（chunks.db + wiki/），"Everything is local. Nothing about your raw data leaves your machine unless you explicitly send a chat message that includes it."（F-051） |
| 模型推理 | **可选全本地**：通过 Local AI 走 Ollama，embeddings 与摘要树构建均可 on-device；否则 embeddings 等调用经过 OpenHuman 后端，和普通模型调用一样出设备（F-051/F-057） |
| 接入方式 | "your own provider key or a fully local Ollama model, and mix the three however you like"——托管模型、自有 key、本地模型三类可混用（F-057） |

因此博文"所有推理不离开设备，Rust 核心强制执行"是**强化表述**：本地优先是默认数据姿态、全本地推理是可选模式，而非默认完全离线（F-027 勘误口径）。安全侧官方明确写出的是 Agent 间通信的 Signal Protocol E2E；博文技术栈表中的 ChaCha20-Poly1305 未见于 README（F-056，单源）。

## 五、Agent 间协作与"Agent Economy"

博文描绘的 Agent Economy（F-028）包含三个要素，核验后证据强弱不同：

| 要素 | 核验结论 |
|------|---------|
| Signal 加密的 Agent 间编排 | ✅ README 明确："Agent-to-agent messaging runs over Signal-protocol end-to-end encryption"；"instances orchestrate each other over Signal-protocol E2E sessions with x402 payments. No server ever sees plaintext"（F-055） |
| x402 支付/赏金 | ⚠️ 官方仅有 "x402 payments" 字样；**支付币种为 USDC、存在"赏金/bounty"机制**未获官方证据（F-055） |
| tiny.place 的 @handle | ⚠️ README 未见 "tiny.place" 与 "@handle" 表述（F-055，博文单源） |

**读数指引**："OpenHuman 实例之间可经 Signal E2E 会话互相编排并伴随 x402 支付、服务器看不到明文"是有据的主干；"USDC 赏金、Agent 互相雇佣、tiny.place 身份"是博文对该主干的具体化演绎，引用时需标注单源。

## 六、UI 优先：编排能力的桌面表达

OpenHuman 把自己与终端优先的同类工具明确区分开（F-017/F-061）：UI-first 桌面壳、产品登录后逐连接器 OAuth 授权（登录产品≠自动获得邮箱权限）、桌面内聚合聊天/连接账户/记忆（Intelligence 页）/吉祥物/语音。Intelligence 页提供系统状态、Run ingest 按钮、记忆指标（Storage/Sources/Chunks/Topics/First·latest memory）、实体关系力导向图、Obsidian vault 深链、ingest 活跃热力图与按作用域检索（F-051）。

## 相关文档

- 记忆与压缩机制：[01-memory-tree-and-tokenjuice](01-memory-tree-and-tokenjuice.md)
- 产品概览与安装：[00-what-is-openhuman](00-what-is-openhuman.md)
- 短板与适用边界：[03-landscape-and-tradeoffs](03-landscape-and-tradeoffs.md)
