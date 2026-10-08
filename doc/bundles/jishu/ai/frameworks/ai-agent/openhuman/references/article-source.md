---
okf_version: "0.2"
type: Reference
title: "博文事实清单：OpenHuman 个人 AI 助手（开源先驱）"
description: "开源先驱博文《又一个人AI助手炸了》全文事实登记 F-001~F-064 共64条——博文42条+2026-09-16 GitHub/官方文档核验补充22条，含作者观点与博文测算分层"
tags: [信源登记, OpenHuman, TinyHumans, 个人AI助手, Memory Tree, TokenJuice, 事实清单]
generated: { by: "blog-article-to-okf-bundle", at: "2026-09-16T20:30:00+08:00" }
status: stable
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/pdH1ZB3yPfDdA7Ay72hjGQ
    title: 《又一个人AI助手炸了。连续9天GitHub Trending第一，3,900次提交，7,800+ Star》（开源先驱/豆芽菜小萌，2026-07-28）
  - id: github
    url: https://github.com/tinyhumansai/openhuman
    title: OpenHuman 官方 GitHub 仓库（2026-09-16 实测）
---

# 博文事实清单（article-source）

> F-001~F-042 出自博文；F-043~F-064 为 2026-09-16 核验补充。本文件与 spec `facts.md` 双份登记，编号集合一致。

## 博文元信息

| 编号 | 事实 | 级别 |
|------|------|------|
| F-001 | 博文标题《又一个人AI助手炸了。连续9天GitHub Trending第一，3,900次提交，7,800+ Star》（"又一个人AI助手"为原文，疑为"又一个个人AI助手"脱字） | P2 |
| F-002 | 公众号「开源先驱」，作者署名「豆芽菜小萌」，2026-07-28 06:48 发布于北京，带微信"原创"标记 | P2 |
| F-003 | 博文性质：第三方自媒体开源项目介绍/推广文；作者自陈"我翻了翻社区讨论和评测"，未声明一手实测；文末"点赞/在看/转发"导流与标题党推荐阅读 | P2 |

## 热度与项目元数据（博文口径）

| 编号 | 事实 | 级别 |
|------|------|------|
| F-004 | 博文称项目"发布一周内连续 9 天霸榜 GitHub Trending 第一" | P0 |
| F-005 | 博文称 3,926 次 commit，已迭代到 v0.63.3、"迭代了六十多个版本" | P0 |
| F-006 | 博文标题称 7,800+ Star | P0 |
| F-007 | 博文称 GPLv3 开源、Rust + Tauri 构建 | P0 |

## 产品定位

| 编号 | 事实 | 级别 |
|------|------|------|
| F-008 | 博文引用项目定位语："Every model in the world shares the same fundamental limitation: they are stateless."（世界上所有模型都有同一个根本缺陷：它们没有状态） | P1 |
| F-009 | 博文称 OpenHuman 解决 stateless 问题——让 AI 真正"认识你"：知道你的项目、日程、昨天和同事聊了什么 | P1 |
| F-010 | 博文归纳：OpenHuman 不是又一个聊天机器人，而是持续运转、知道你是谁、能自己干活的个人数字分身 | 作者归纳 |

## 三大能力与四个痛点

| 编号 | 事实 | 级别 |
|------|------|------|
| F-011 | 能力一"有记忆的大脑"：Memory Tree 层级摘要树，博文称容量可达 10 亿 token，持续更新；存本地 SQLite 并生成 .md 同步 Obsidian | P0 |
| F-012 | 能力二"编排器"：基于检查点图的 Agent 运行时，管理 Agent 舰队；快速反射 Agent 处理入站流量，深度推理核心把复杂工作委派给 Worker | P1 |
| F-013 | 能力三"深度研究员"：研究侦察兵在用户问完之前已扫完记忆库和文件系统，无冷启动 | P1 |
| F-014 | 痛点①无长期记忆：层级摘要树替代线性对话记录，记得"有什么/什么重要/什么关系" | P1 |
| F-015 | 痛点②数据孤岛：118+ OAuth 集成打通 Gmail/Slack/GitHub/Notion/Calendar 等，每 20 分钟自动同步 | P0 |
| F-016 | 痛点③上下文成本：TokenJuice 压缩层最高省 80% token，"一个月能省几百块" | P0 |
| F-017 | 痛点④上手门槛：桌面应用优先、图形界面、OAuth 一键授权 | P1 |

## Memory Tree（博文口径）

| 编号 | 事实 | 级别 |
|------|------|------|
| F-018 | 博文六步：①118+ OAuth 拉取邮件/文档/聊天/代码/日历；②标准化为 ≤3,000 token Markdown 块；③按时效性/相关性/来源权重打分；④折叠 per-source/per-topic/per-day 层级摘要树；⑤SQLite + .md 同步 Obsidian；⑥每 20 分钟增量更新 | P0 |
| F-019 | 博文对比表：容量（几万 token / RAG 百万级 / Memory Tree 10 亿 token）；结构（线性 / 向量检索 / 层级摘要树）；更新（每次对话 / 手动索引 / 20 分钟自动）；可读性（不可读 / 不可读 / Obsidian 可编辑）；隐私（云端 / 可控 / 本地优先） | P1（博文整理口径） |

## TokenJuice（博文测算口径）

| 编号 | 事实 | 级别 |
|------|------|------|
| F-020 | 博文测算：30KB 原始数据约 8,000 token → 压缩后 6KB 约 1,600 token；按 GPT-4o 价格一次深度分析 $0.04→$0.008，每天 50 次月成本 $60→$12 | P0（博文自行测算） |
| F-021 | 博文列压缩省幅：HTML→Markdown 40-60%、长 URL 缩短 5-10%、非 ASCII 清理 5-15%、去重 10-30%，全栈最高省 80% | P0（博文口径） |

## 竞品对照（博文口径）

| 编号 | 事实 | 级别 |
|------|------|------|
| F-022 | 博文对比表：Claude Cowork（闭源/桌面+CLI/对话级记忆/少量集成/无同步/无渠道/不参会）；OpenClaw（MIT/终端优先/插件记忆/需自建/无/少量/不支持）；OpenHuman（GPLv3/UI 优先/Memory Tree+Obsidian/118+ OAuth/20 分钟/17 渠道/Meet·Zoom·Teams·Webex） | P0 |

## 特色设计

| 编号 | 事实 | 级别 |
|------|------|------|
| F-023 | 桌面吉祥物：有表情会说话，主动提醒邮件/日历/通知，关窗后常驻 | P1 |
| F-024 | 潜意识系统 Subconscious：后台循环对比世界状态、推进长期目标、撰写晨间简报 | P1 |
| F-025 | 会议 Agent：真人身份加入 Meet/Zoom/Teams/Webex，自动从日历加入，实时转录摘要 | P0 |
| F-026 | Split Brain 双脑：快速反射 Agent 处理入站消息通知，深度推理核心委派 Worker 舰队 | P1 |
| F-027 | 一键隐私模式：推理不离开设备、Rust 核心强制；记忆存本地 SQLite，可接 Ollama 本地模型 | P1 |
| F-028 | Agent Economy：tiny.place 的 @handle、Signal 加密 Agent 间编排、x402 USDC 赏金交易、Agent 互相雇佣 | P0 |

## 技术栈（博文表）

| 编号 | 事实 | 级别 |
|------|------|------|
| F-029 | Tauri（Rust 后端+Web 前端）；React/TypeScript；Rust runtime；SQLite；Claude/GPT/Gemini/Ollama；ChaCha20-Poly1305 / Signal Protocol E2E；Cargo/CMake/Ninja/pnpm；GPLv3 | P0 |

## 获取与上手

| 编号 | 事实 | 级别 |
|------|------|------|
| F-030 | install.sh（macOS/Linux）、install.ps1（Windows）、`brew install --cask openhuman`、GitHub Releases 四种安装方式 | P0 |
| F-031 | 三步走：OAuth 连接 3-5 个核心服务 → 等 5-10 分钟初始同步 → 直接提问 | P1 |
| F-032 | 源码构建：clone → submodule update --init --recursive → pnpm install → pnpm dev / pnpm --filter openhuman-app dev:app | P1 |

## 短板（博文评测口径）

| 编号 | 事实 | 级别 |
|------|------|------|
| F-033 | Early Beta：迭代快但稳定性打磨中，文档不全，生产慎用 | P1 |
| F-034 | OAuth 连接器良莠不齐：Gmail/GitHub 稳，小众服务 token 偶发过期；20 分钟同步固定、不能手动即时触发 | P1 |
| F-035 | 资源占用不轻：建议 8GB+ 内存，4GB 机器吉祥物动画会卡 | P1 |
| F-036 | 中文体验依赖底层模型，英文最好，纯中文场景建议先试 | P1（作者建议） |
| F-037 | 仅桌面端（Win/macOS/Linux），暂无移动端 | P1 |

## 作者结论

| 编号 | 事实 | 级别 |
|------|------|------|
| F-038 | 作者观点：连霸 Trending 靠踩中"所有 AI 助手都没有记忆"的真实痛点而非营销 | 作者观点 |
| F-039 | 作者观点：10 亿 token/118+ OAuth/省 80%/一键隐私不是噱头；Rust+Tauri 比 Electron 轻，UI 优先免命令行 | 作者观点 |
| F-040 | 作者观点：不替代 ChatGPT/Claude，做"了解你这个人"而非"回答你这个问题"；最佳用法是组合 | 作者观点 |
| F-041 | 作者建议：知识工作者/Obsidian 用户/多工具切换者值得装；纯聊天 ChatGPT 够用 | 作者观点 |
| F-042 | 项目地址 https://github.com/tinyhumansai/openhuman（原文纯文本） | P2 |

## 核验补充事实（2026-09-16）

| 编号 | 事实 | 来源 |
|------|------|------|
| F-043 | 仓库真实存在；About 原文 "open source agent harness with local-first memory, agent orchestration, and workflows"；官网 tinyhumans.ai/openhuman；文档 tinyhumans.gitbook.io/openhuman；仓库创建于 2026-02-18 | GitHub |
| F-044 | 2026-09-16 实况：39.8k stars（39,814）、3.9k forks（3,922）、201 watching、190 issues、183 contributors；Rust 58.6%/TS 37.9%/JS 2%/Shell 1.4% | GitHub 页面+API |
| F-045 | License 为 GPL-3.0（侧栏+API）——博文 F-007 准确 | GitHub |
| F-046 | 最新 release v0.63.12（2026-08-07）；release 共 56 个（最早 v0.49.32，2026-03-31）；tag 共 106 个（最新 v0.63.21，main 已有 v0.63.29 提交）；v0.63.3 处于 7-28 合理时点 | GitHub API |
| F-047 | 提交总数 2026-09-16 为 20,551；博文 3,926 历史值无法回溯，现值约为其 5.2 倍 | GitHub |
| F-048 | README 自认："Within one week of launch, OpenHuman became the number one trending repository on GitHub for nine days in a row."——9 天 Trending 属实但时间锚点为"发布后一周内" | GitHub README |
| F-049 | OAuth 口径漂移：2026-09 README 为 "100+ OAuth integrations, 5,000+ MCP servers, 90,000+ Skills"；2026-05 openhuman.dev 快照为 "118+ OAuth connectors"——博文 118+ 合于 5 月口径，9 月官方为 100+ | README/openhuman.dev |
| F-050 | 消息渠道：README 现为 "15 messaging channels（Telegram/Discord/Slack/WhatsApp/Signal/iMessage…）plus native email (IMAP IDLE + SMTP)"；博文 17 个与现口径 15 不符 | GitHub README |
| F-051 | Memory Tree 官方机制（GitBook）：canonicalize→≤3k 内容寻址分块→fast-score→单事务落盘；source/topic/global 三树（L0 seal 级联/hotness 物化/UTC 每日 digest）；持久作业队列+3 worker+信号量；leaf 状态机 pending_extraction→admitted→buffered→sealed/dropped；`~/.openhuman` 下 chunks.db + wiki/ vault；20 分钟 auto-fetch + 手动 Run ingest + RPC；可选 agentmemory 后端 | GitBook memory-tree |
| F-052 | "10 亿 token / 10M@4,000 t/s / NeoCortex"在官方 README 与 GitBook 均未见；仅第三方 AI 生成知识库（agentic-ai.readthedocs.io，2026-05）单源给出，官方未背书 | 弱源单源 |
| F-053 | TokenJuice "up to 80% fewer tokens" 经 README+GitBook 双证；官方为多阶段压缩路由器（2KB 门限→7 类内容检测→专用压缩器→CCR 缓存+⟦tj:hash⟧ 标记→记账），始于 vincentkoc/tokenjuice 移植；博文细分省幅与美元测算是博文自算，官方无对应数字 | README/GitBook |
| F-054 | README 对比行："🚀 Joins Meet/Zoom/Teams/Webex, speaks, live transcript"——四平台+发言+转录证实 | GitHub README |
| F-055 | README 明确 Signal-protocol E2E 的 A2A 消息与 "x402 payments"、"No server ever sees plaintext"；tiny.place/@handle、USDC、bounty 字样未见 | GitHub README |
| F-056 | Signal Protocol E2E 官方明确；"ChaCha20-Poly1305" README 未见 | GitHub README |
| F-057 | Tauri/Rust（1.96.1）/SQLite/Node 24+/pnpm/TypeScript 证实；README 无 "React"；Ollama 全本地明确，GPT/Gemini 未以模型名出现（泛指自有 provider key） | GitHub |
| F-058 | install.sh（HTTP 200，21,787B）/install.ps1（9,013B）存在；brew cask 命令见 INSTALL.md（另支持 .deb/AUR）；4 枚 Product Hunt 徽章 | GitHub |
| F-059 | openhuman.dev 硬件口径：RAM baseline 4GB+（Getting Started）；大邮箱/代码库+本地模型建议 16GB+；建议 SSD——博文 8GB+ 建议更保守 | openhuman.dev |
| F-060 | Early Beta 官方证实（"Under active development. Expect rough edges."）；仓库 2026-02-18 创建、最早 release 2026-03-31；"2026-05-13 beta 发布"仅见 AI 生成知识库（弱源） | GitHub/弱源 |
| F-061 | openhuman.dev 官方竞品表为四款：Claude Cowork（闭源）/OpenClaw（MIT）/Hermes Agent（MIT）/OpenHuman（GNU）——博文三款与官方口径一致，漏列 Hermes Agent | openhuman.dev |
| F-062 | "内置完整 Linux 沙箱"在官方 README 与 GitBook 公开功能页均未见——仅博文单源，存疑 | 官方未见 |
| F-063 | 第三方独立长评（honbul.tistory.com，2026-05-19，基于 README/manifest/GitBook）旁证：Tauri 定位、Meet Agent、118+ 集成、20 分钟 auto-fetch、Memory Tree+Obsidian | 第三方旁证 |
| F-064 | 第三方 AI 知识库称首日 +1,694 stars/day、两周 27k+ stars——无法回溯且与博文 7,800+ 数量级冲突，两历史值均不采信；唯一权威时点值 2026-09-16 的 39.8k | 弱源冲突 |

## 可信度分层

| 等级 | 事实编号 | 说明 |
|------|---------|------|
| ✅ 官方核验 | F-007/F-045, F-043, F-048, F-051, F-053, F-054, F-058, F-060, F-061 | 许可证/仓库/9 天 Trending/记忆机制/80%/四会议平台/安装/Beta/竞品口径 |
| ⚠️ 口径漂移或单源 | F-004~F-006, F-011, F-015, F-022, F-028, F-029, F-035, F-052, F-056, F-057, F-062, F-064 | 数字漂移、弱源单源、官方未见 |
| 📝 作者观点 | F-010, F-036, F-038~F-041 | 归纳与建议，非客观事实 |
| 📊 博文测算 | F-020, F-021 | 美元金额与细分省幅为博文假设推算 |
