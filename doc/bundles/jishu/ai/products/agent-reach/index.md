---
okf_version: "0.2"
type: bundle
title: "Agent Reach：给 AI Agent 接入多平台的能力层 CLI"
description: "Python/MIT 的 Agent 互联网能力层 CLI：有序后端+active_backend 无感切换、doctor 真跑三态、只读授权与给 Agent 的 SKILL.md；两篇博文交叉核验并校正 v1.6.0 口径，含安装实操"
tags: [agent-reach, ai-agent, capability-layer, cli, channels, doctor, skill-md, opencli, mcp, claude-code, cursor, 博文转化]
generated:
  by: seven-concepts-cmd+blog-article-to-okf-wiki
  at: "2026-10-26T11:25:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-26T11:25:00+08:00"
status: stable
stale_after: 2027-01-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/1JfmyVydF2ZMJe131Kp-3w
  - id: blog2
    url: https://mp.weixin.qq.com/s/kk4iSX6xdk3IsNKO4eVy9w
  - id: github-repo
    url: https://github.com/Panniantong/Agent-Reach
  - id: github-api
    url: https://api.github.com/repos/Panniantong/Agent-Reach
  - id: official-readme
    url: https://raw.githubusercontent.com/Panniantong/agent-reach/main/README.md
  - id: official-install
    url: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
  - id: official-sessions
    url: https://raw.githubusercontent.com/Panniantong/agent-reach/main/agent_reach/skill/references/sessions.md
---

# Agent Reach：给 AI Agent 接入多平台的能力层 CLI

> **类型**：技术教程/产品拆解（含可照做 examples/，操作可复现性两问皆"是"）
> **信源**：两篇微信公众号文章——「AI赋能干货铺」《9.2万星炸场：给AI装上眼睛》（2026-10-06）+「架构文摘」《87.7k Stars！给 Agent 装上全网之眼》（2026-10-17），经 GitHub API、官方 README/install.md/SKILL.md/sessions.md 与 v1.5.0 tag 逐项核验（核验日 2026-10-08 与 2026-10-26 两轮）
> **核验结论**：两批合计 41 项 P0/P1 → **✅ 26 / ⚠️ 11 / ❌ 4**；4 项 ❌ 均为可照做性或安全表述错误，已在正文纠正
> **数据时点**：Star 等动态数字为 **2026-10-26** 快照；功能与命令口径为 main 分支 **v1.6.0**（2026-10-23 发布）

## 本文概要

[Agent Reach](https://github.com/Panniantong/Agent-Reach) 是一个 Python 3.10+、MIT 许可的 **AI Agent 互联网能力层**：它自己不抓取任何平台，而是为多个渠道（网页/YouTube/GitHub/B站/V2EX/小红书/雪球/BOSS/LinkedIn/Reddit/Twitter/小宇宙/Facebook/Instagram）维护"**首选+备选的有序后端列表**"，负责选型、安装、体检与路由——上游工具（yt-dlp、gh、bili-cli、OpenCLI 等）被风控或停更时，调整后端顺序即可让用户零感知切换。配套 `doctor` 真实探测 missing/broken/timeout 三态、v1.6.0 起所有命令输出 JSON；专用浏览器默认无头、首次访问会复制该站 Cookie 一次；并随包交付一份**给 Agent 看的 SKILL.md**，实现"发一句话给 Agent，它自己读文档装好"。

渠道数是这个项目最容易读错的指标：v1.5.0 tag 13 个、main@2026-10-08 16 个、v1.6.0 14 个（5 默认 + 6 可选 + 3 实验），详见 [05](concepts/05-version-drift-and-channel-matrix.md)。

## 阅读路径

**先建立概念（约 20 分钟）**

1. [Agent Reach 是什么：项目身份与发布事实](concepts/00-what-is-agent-reach.md)——定位、作者、MIT、2026-02 发布、v1.6.0、10.2 万 Star（带时点）
2. [能力层架构：有序后端列表与 14 渠道全景](concepts/01-capability-layer-architecture.md)——channels/active_backend、412 故障切换、三级渠道矩阵
3. [doctor 真体检与安全模型](concepts/02-doctor-health-and-security-model.md)——三态诊断、JSON 与人读双通道、--safe/--dry-run、凭据 600、Cookie 复制边界
4. [SKILL.md 与 Agent 时代的分发范式](concepts/03-skill-md-agent-distribution-paradigm.md)——给 Agent 的说明书与五条设计启示（**作者观点，已分层**）
5. [团队落地：能力基线、登录态治理与合规边界](concepts/04-team-rollout-and-compliance.md)——四段落地法、适用场景判定、8 条避坑、最小团队规范
6. [版本漂移与渠道矩阵：从 16 到 14](concepts/05-version-drift-and-channel-matrix.md)——三代口径、退役渠道、1.5→1.6 迁移清单

**再动手实操**

7. [安装 Agent Reach 并完成首次体检](examples/00-install-and-doctor.md)——uv 安装、一句话安装、--safe/--dry-run、doctor、升级与卸载
8. [默认渠道实操](examples/01-zero-config-channels.md)——网页/GitHub/YouTube/B站/V2EX + 已退役的 RSS/Exa 说明
9. [登录态渠道与 Cookie 安全](examples/02-login-channels-and-cookie-safety.md)——专用浏览器、自动复制会话、Twitter token、小号纪律

## 核心事实速查

| 项 | 值 |
|----|-----|
| 仓库 / 作者 | [Panniantong/Agent-Reach](https://github.com/Panniantong/Agent-Reach)（个人开发者，显示名 Pnant） |
| 开源时间 / 许可 | 2026-02-24 / MIT / Python 3.10+ |
| 版本 | 最新 **v1.6.0**（2026-10-23），共 **8 个 release** |
| 社区数据 | Star **102,508**、Fork **9,086**、open issues 242、38 贡献者（**2026-10-26 时点**；两篇博文分别写 92,000+ 与 87,759） |
| 渠道数 | **14**：默认 5（bilibili/v2ex/github/youtube/web）、可选 6（xiaohongshu/xueqiu/boss/xiaoyuzhou/linkedin/reddit）、实验 3（twitter/facebook/instagram）；RSS 与 Exa 已退役 |
| 核心机制 | 有序后端列表 + `active_backend` 探测选主；probe 三态 missing/broken/timeout |
| 输出协议 | v1.6.0 起单条命令输出单个 JSON（`ok`/`result`/`error.hint`）；人读 `doctor --text`、实测 `check <渠道> --text` |
| 安全模型 | install 默认只检查、`--safe` 只列需求、`--dry-run` 预览（**无 `--system`**）；凭据 `~/.agent-reach/config.yaml` 权限 600 |
| 会话模型 | 专用浏览器（优先 CloakBrowser，回退 Chrome）、默认无头、闲置 10 分钟关闭；首次访问复制该站 Cookie 一次，不复制整目录/密码库 |
| Agent 交付 | `agent_reach/skill/SKILL.md`（+ 英文版 + references/ 分类文档） |
| 安装 | `uv tool install <latest release zip>` + `agent-reach setup`；**勿装 PyPI 同名包** |

## ⚠️ 阅读前必知的口径勘误（9 条）

1. **Star 数**：两篇博文分别写 92,000+（10-06）与 87,759（10-17）。后者**低于** 10-08 实测的 93,673，非发布日快照；本包采用 **102,508（2026-10-26）**，动态数字引用须带时点（F-056/F-077/F-102）。
2. **"16 个平台"**：文章标题与正文写 16，但自己的表格只有 13 行，且当前 v1.6.0 是 **14** 渠道（F-086/F-087/F-108）。读法见 [05](concepts/05-version-drift-and-channel-matrix.md)。
3. **`pip install agent-reach` 是错的**：PyPI 上那个同名包不是本项目，官方文档首屏就警告"绝不要从 PyPI 安装"；v1.5 用 pipx + GitHub archive，v1.6 用 uv + release zip（F-095/F-109/F-110）。
4. **`--system` 参数不存在**：首版知识包与第二篇文章都误写；实际只有 `install --env=auto`、`--safe`、`--dry-run`（F-092/F-110）。
5. **"不读取浏览器 Cookie"是错的**：v1.6.0 明确首次使用时把该站 Cookie **复制一次**到专用浏览器（不复制整目录、其他站或密码库，不改原浏览器）。正确说法是"隔离复制"，不是"不读"（F-094/F-113）。
6. **"零 API 费"要打折**：基础读取免费；YouTube/小宇宙的语音转文字需要 Groq 或 OpenAI Key（F-091/F-114）。
7. **SKILL.md 不在仓库根目录**：实际在 `agent_reach/skill/SKILL.md`（F-062）。
8. **6 vs 7 默认渠道已是旧账**：v1.5 时代"默认激活 6 个"、文章"7 个零配置"的内部矛盾，在 v1.6.0 被 5 默认 / 6 可选 / 3 实验取代（F-061/F-108）。
9. **团队落地四段是作者建议**：无官方出处，其中"Cookie-Editor 手工导出"已被自动复制会话取代（F-097/F-113）。

## 采用提示与已知边界

- **登录态渠道有账号风险**：Cookie/登录会话等同该账号权限，项目方与两篇博文都一致要求**专用小号**；出问题的是账号，不是程序（F-118/F-119，见 [examples/02](examples/02-login-channels-and-cookie-safety.md)）。
- **供应链**：官方警告不要从 PyPI 安装同名包；v1.6.0 的 `latest` 下载地址会随版本漂移，团队基线应锁具体版本（F-109）。
- **个人维护项目的供应风险**：owner 为个人开发者（38 位贡献者、核验前一日仍有 push），但渠道可用性系于上游工具与平台风控；采用前建议锁版本、先 `--dry-run` 与 `doctor --text` 自检（F-102/F-100）。
- **"最稳选型"为项目方自述**：README 含 6 家赞助商区块（Bright Data/RapidProxy/BrowserAct/腾讯云 Lighthouse/CoreClaw/优刻得星图），选型叙事存在商业背景（F-116）。
- **未实测**：本包核验了渠道/文件存在性、命令逐字一致性与故障史文字记载，**未在本机安装运行，未逐一实测 14 个渠道的当前可用性**，也未复现 doctor 输出。
- **数字时效**：`stale_after: 2027-01-31`；到期前复核 Star、渠道集、安装器与安全口径。

## 信源与可信度

- 第一批事实清单：[references/article-source.md](references/article-source.md)（F-001~F-072，72 条）
- 第二批事实清单：[references/article-source-02.md](references/article-source-02.md)（F-073~F-120，48 条）
- 第一批核验：[references/verification.md](references/verification.md)（21 项：16✅/5⚠️/0❌）
- 第二批核验与版本漂移：[references/verification-02.md](references/verification-02.md)（20 项：10✅/6⚠️/4❌ + 首版 5 处回改）
- 信源距离：两篇均为第三方公众号综述（第二篇作者自陈未实测）→ 已升级为 GitHub API + 官方文档 + tag 比对的一手交叉核验

## 主题关联

- [wigolo](../wigolo/index.md)：本地优先的 Web 情报层（MCP 搜索/抓取）——Agent Reach 偏"多平台接入路由与体检"，wigolo 偏"本地搜索引擎与证据"，同为 Agent 联网能力设施
- [browseract](../browseract/index.md)：浏览器自动化 Agent——与"登录态渠道/浏览器会话"主题相邻（Agent Reach 只读复用会话，BrowserAct 主动操作浏览器）
- [open-code-review](../open-code-review/index.md)：同样以 CLI/MCP 形态接入 Claude Code 等客户端的开发者工具
- [loopx](../loopx/index.md)：Agent 控制面/任务编排设施，与本包"Agent 基础设施"主题相邻
- [todesk-ai](../todesk-ai/index.md)：跨设备 AI 助手的 Computer Use 工具化实践

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
log
```
