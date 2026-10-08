---
type: Reference
title: "Oracle 博文 P0 核验报告"
description: "10 项 P0 声明逐项核验、勘误四张清单、信源清单与时效边界；结论 10✅/0❌，5 项博文缺口由官方源补充"
tags: [Oracle, P0核验, 勘误, 对抗审查, 博文转化]
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/_J1BzyqyoNWuj_998DLo1g
  - id: docs-install
    url: https://raw.githubusercontent.com/steipete/oracle/main/docs/install.md
  - id: docs-browser
    url: https://raw.githubusercontent.com/steipete/oracle/main/docs/browser-mode.md
  - id: docs-agents
    url: https://raw.githubusercontent.com/steipete/oracle/main/docs/agents.md
  - id: skill-md
    url: https://raw.githubusercontent.com/steipete/oracle/main/skills/oracle/SKILL.md
  - id: npm
    url: https://www.npmjs.com/package/@steipete/oracle
---

# P0 核验报告

> 核验时间：2026-09-16 ｜ 核验方法：博文 1684 字全文提取（浏览器 `#js_content` innerText，两次加载一致）后，对全部可执行声明逐项对官方源（GitHub main 分支文档经 Contents API 抓取、npm 官方包页、仓库内置 SKILL.md）。
> 结论：**P0 共 10 项，10 ✅ / 0 ❌**；无勘误型硬错误；5 项博文信息缺口由官方源补充进概念/实战文档并显式标注来源。

## 1. P0 声明逐项核验

| # | 博文声明（F 编号） | 官方源 | 结论 |
|---|---|---|---|
| P0-1 | 项目 Oracle 存在，作者 steipete，开源（F-009） | npm 包页署名 steipete；仓库 docs/skills 路径全部 200；MIT（everydev 索引旁证） | ✅ |
| P0-2 | 功能＝打包 prompt+选中文件给另一模型、取回结果（F-010） | npm README："bundles a prompt with the files you select, sends that context to an AI model … stores the result as a session" | ✅ |
| P0-3 | Browser Mode 可用已登录 ChatGPT 网页会话（F-011） | browser-mode.md：manual-login 持久化 profile、驱动 chatgpt.com Web UI（CDP） | ✅ |
| P0-4 | `brew install steipete/tap/oracle`（F-012） | install.md Homebrew 节原文；tap 另发 oracle-notifier | ✅（平台限定见 GAP-1） |
| P0-5 | `npm install -g @steipete/oracle`（F-013） | install.md npm/pnpm 节原文 | ✅（前置 Node 24+ 见 GAP-1） |
| P0-6 | 首次登录命令三参数 `--engine browser --browser-manual-login --browser-keep-browser -p "HI"`（F-014） | browser-mode.md Manual login mode 示例 `oracle --engine browser --browser-manual-login --browser-keep-browser --model "GPT-5.5 Pro" -p "Say hi"`；三参数 CLI Options 均有定义 | ✅（博文省略 --model，非错误；当前模型口径见 GAP-5） |
| P0-7 | 首次登录后复用浏览器会话（F-015） | `~/.oracle/browser-profile` 持久化，"Reuse the same profile on subsequent runs (no re-login unless the session expires)" | ✅ |
| P0-8 | Codex 接入三行：git clone、mkdir -p ~/.codex/skills、cp -R oracle/skills/oracle（F-016） | agents.md「Codex」节：`mkdir -p ~/.codex/skills` + `cp -R skills/oracle ~/.codex/skills/oracle` | ✅ |
| P0-9 | AGENTS.md 指示 Codex 复杂任务优先走 Oracle（F-017） | agents.md "30-second wiring"：AGENTS.md/CLAUDE.md 放触发场景 bullet（stuck/debugging/architecture review/cross-validating） | ✅ |
| P0-10 | 发布时间 2026-08-30、原创、公众号 Leon学AI（F-001） | 微信页面元数据（两次独立加载一致） | ✅ |

## 2. 勘误四张清单

| 清单 | 结果 |
|---|---|
| ① 日期/版本表 | 博文无版本号、无 GA 日期、无年份归属类声明；发布日期页面自洽。**0 问题** |
| ② 成效数字溯源表 | 博文无任何提效倍数/工时节省/成本数字；"额度更耐用/没那么容易跑完"为无数字的定性体验（F-008），按 📌 作者观点入库，且博文自我限定"不是额度互换"（F-019）。**无需溯源，已分层** |
| ③ 口径对照表 | 无规模/份额/排行数字；第三方索引 everydev 给出 2,597 star（快照时点不明）与"2025-11 创建"，**均不写入正文结论**，创建时间仅在项目档案以 ⚠️ 第三方单源出现（F-023） |
| ④ 引文逐字核对表 | 博文引号内容均为自家口号（"GPT 当大脑，Codex 当双手"），无伪造官方/高管引语；对官方机制的转述与 npm README、agents.md 原意一致 |

**源文硬错误：0 项**（本组 13 篇历史转化曾拦截 4 项，本篇为命令型推荐文，可执行部分全部属实）。

## 3. 博文缺口与口径补充（非错误，入库时显式补齐）

| # | 缺口 | 官方事实 | 入库处理 |
|---|---|---|---|
| GAP-1 | 未提运行前提与平台 | Node.js **24+** 硬要求；brew 包仅 macOS/Linux；Windows 走 npm/npx（install.md） | examples/00 前置条件小节显著标注（F-024/F-025） |
| GAP-2 | "另一模型"被窄化为网页 ChatGPT | 另有 Render 路径（不调模型）；API 路径支持 OpenAI/Azure/Anthropic/Gemini/xAI/OpenRouter 六家；Browser 还支持 Gemini Web（F-026~F-028） | concepts/00 引擎矩阵完整呈现 |
| GAP-3 | 未提会话可重连/可续聊 | sessions 持久化、status/session/restart/--followup；超时应 reattach 而非重跑（F-029/F-033） | concepts/02 + examples/01 |
| GAP-4 | 未提 MCP 形态 | oracle-mcp stdio server 可直挂 Codex/Claude Code/Cursor（F-035） | examples/01 "备选接入" |
| GAP-5 | 模型口径具强时效性 | 核验时官方文档已为 GPT-5.5 Pro / GPT-5.6 Sol / GPT-6 Astra 选择器口径，CLI 月度级发版（npm 0.20.2，60 版本），0.15.2 曾有标签 normalize 缺陷（F-036） | 全篇版本快照提示 + stale_after 2026-12-31 |
| GAP-6 | 未提安全边界 | 默认不附 secrets、单文件 1MB、API 模式真实计费、Pro fail-closed（F-032/F-036/F-038） | examples/01 安全卫生清单 |

## 4. 作者观点/主张分层（防止观点固化为事实）

- 📌 F-002"两边各用各的"、F-004"大脑/双手"比喻、F-006"重推理最吃额度"、F-007 分工表、F-008"配额更耐用"、F-020 推荐人群——均为作者归纳/体验，正文以"博文作者主张"措辞呈现，不写成 Oracle 官方能力或承诺
- F-019 是博文自己给出的反向限定（非额度互换），与官方机制一致，正文并列呈现以校正标题党预期
- F-041 ⚠️：browser 路径"不花 API token"有第三方转述与官方用量记账段支撑，但**订阅档位门槛（Plus 能否用 Pro 档）官方文档未声明**，正文明确"以 OpenAI 官方账号规则为准"

## 5. 信源清单

| id | 信源 | 距离 | 抓取状态 |
|---|---|---|---|
| blog | 微信公众号原文 | ③/④ | 2026-09-16 浏览器提取全文 1684 字，双次一致 |
| github | https://github.com/steipete/oracle | ① | 主站 WebFetch 被网络层拦截，改由 Contents API/raw 抓取 docs 成功 |
| docs-install | docs/install.md（main） | ① | HTTP 200，2958 bytes |
| docs-browser | docs/browser-mode.md（main） | ① | HTTP 200，57515 bytes |
| docs-agents | docs/agents.md（main） | ① | HTTP 200，5672 bytes |
| skill-md | skills/oracle/SKILL.md（main） | ① | 搜索引擎缓存命中全文 |
| npm | npmjs.com/package/@steipete/oracle | ① | 0.20.2（发布约 20 小时前快照） |
| everydev | everydev.ai 工具索引 | ④ | 仅弱事实旁证，已降级标注 |

## 6. 时效边界

- CLI 与 ChatGPT Web UI 双向快速迭代：CLI 参数、模型选择器标签、订阅档位均可能在数周内变化；本报告所有"✅ 一致"仅对 2026-09-16 所见 main 分支与 npm 0.20.2 负责
- 复核触发：stale_after 2026-12-31；此前若 Oracle 大版本变更或 OpenAI 调整 Codex/ChatGPT 额度体系，应提前复核
- 复核要点：`oracle --help --verbose` 参数集、`skills/oracle` 目录是否仍随仓库分发、ChatGPT 订阅档位与自动化使用条款
