---
okf_version: "0.2"
type: bundle
title: "Agent Reach：给 AI Agent 接入 16 平台的能力层 CLI"
description: "Python/MIT 的 Agent 互联网能力层 CLI：16 渠道有序后端+active_backend 无感切换、doctor 真跑三态、默认只读授权与给 Agent 的 SKILL.md，含安装实操（博文经官方核验）"
tags: [agent-reach, ai-agent, capability-layer, cli, channels, doctor, skill-md, opencli, mcp, claude-code, cursor, 博文转化]
generated:
  by: seven-concepts-cmd+blog-article-to-okf-wiki
  at: "2026-10-08T13:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-08T13:00:00+08:00"
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/1JfmyVydF2ZMJe131Kp-3w
  - id: github-repo
    url: https://github.com/Panniantong/Agent-Reach
  - id: github-api
    url: https://api.github.com/repos/Panniantong/Agent-Reach
  - id: official-readme
    url: https://raw.githubusercontent.com/Panniantong/agent-reach/main/README.md
  - id: official-install
    url: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
---

# Agent Reach：给 AI Agent 接入 16 平台的能力层 CLI

> **类型**：技术教程/产品拆解（含可照做 examples/，操作可复现性两问皆"是"）
> **信源**：微信公众号「AI赋能干货铺」博文《9.2万星炸场：给AI装上眼睛，16个平台一个CLI全打通》（作者学生小孙，2026-10-06）→ 2026-10-07/08 经 GitHub API、官方 README/install.md、git tree 逐项核验
> **核验结论**：21 项 P0/P1 声明 **16✅ / 5⚠️ / 0❌**，核心声明无失败；安装命令逐字可溯
> **数据时点**：Star 等动态数字为 2026-10-08 快照；功能口径为 main 分支（最新 release v1.5.0）

## 本文概要

[Agent Reach](https://github.com/Panniantong/Agent-Reach) 是一个 Python 3.10+、MIT 许可的 **AI Agent 互联网能力层**：它自己不抓取任何平台，而是为 16 个渠道（网页/YouTube/GitHub/RSS/Exa/V2EX/B站/Twitter/小红书/Reddit/雪球/小宇宙/LinkedIn/Boss/Facebook/Instagram）维护"**首选+备选的有序后端列表**"，负责选型、安装、真跑体检与路由——上游工具（yt-dlp、gh、bili-cli、OpenCLI 等）被风控或停更时，调整后端顺序即可让用户零感知切换。配套 `doctor` 真实探测 missing/broken/timeout 三态、`--json` 供 Agent 读取 `active_backend`；安装器默认只读、需 `--system` 显式授权；并随包交付一份**给 Agent 看的 SKILL.md**，实现"发一句话给 Agent，它自己读文档装好"。

## 阅读路径

**先建立概念（15 分钟）**

1. [Agent Reach 是什么：项目身份与发布事实](concepts/00-what-is-agent-reach.md)——定位、作者、MIT、2026-02 发布、v1.5.0、93.7k 热度（带时点）
2. [能力层架构：有序后端列表与 16 渠道全景](concepts/01-capability-layer-architecture.md)——channels/active_backend、412 故障切换、三档渠道（6/7 口径勘误）
3. [doctor 真体检与安全授权模型](concepts/02-doctor-health-and-security-model.md)——三态诊断、人机双输出、默认只读/dry-run/凭据 600
4. [SKILL.md 与 Agent 时代的分发范式](concepts/03-skill-md-agent-distribution-paradigm.md)——给 Agent 的说明书与五条设计启示（**作者观点，已分层**）

**再动手实操**

5. [安装 Agent Reach 并完成首次体检](examples/00-install-and-doctor.md)——pipx/一句话安装、三档授权、doctor、卸载
6. [零配置渠道实操](examples/01-zero-config-channels.md)——网页/GitHub/YouTube/Exa/RSS/V2EX + B站免登录
7. [登录态渠道与 Cookie 安全](examples/02-login-channels-and-cookie-safety.md)——Twitter/小红书/Reddit 等配置与专用小号纪律

## 核心事实速查

| 项 | 值 |
|----|-----|
| 仓库 / 作者 | [Panniantong/Agent-Reach](https://github.com/Panniantong/Agent-Reach)（个人开发者，显示名 Pnant） |
| 开源时间 / 许可 | 2026-02-24 / MIT / Python 3.10+ |
| 版本 | 最新 v1.5.0「能力层:多后端路由 + 真体检 + OpenCLI」（2026-06-11，共 7 个 release） |
| 社区数据 | Star **93,673**、Fork **8,195**、36 贡献者（**2026-10-08 时点**；博文 10-06 口径为 92,000+/约 8,000） |
| 渠道数 | 对外 **16** 个；git tree 实际 channels/ 20 文件/17 个渠道实现（含 mcporter 等内部映射） |
| 默认激活 | **6** 个零配置渠道（网页/YouTube/GitHub/RSS/Exa/V2EX）；B站免登录但需 bili-cli 装好即用 |
| 核心机制 | 有序后端列表 + `active_backend` 探测选主；probe 三态 missing/broken/timeout；`doctor --json` |
| 安全模型 | install 默认只读、`--dry-run`、`--system` 显式授权；凭据 `~/.agent-reach/config.yaml` 权限 600 |
| Agent 交付 | `agent_reach/skill/SKILL.md`（+ SKILL_en.md、references/ 7 篇）；一句话安装指向 docs/install.md |
| 安装 | `pipx install https://github.com/Panniantong/agent-reach/archive/main.zip`（**勿装 PyPI 同名包**） |

## ⚠️ 阅读前必知的五条口径勘误

1. **Star 数**：博文"92,000+"为 2026-10-06 发文口径，本知识包采用官方现值 **93,673（2026-10-08）**，动态数字引用须带时点（F-056）。
2. **"6 个 vs 7 个开箱即用"**：博文头部写 6、正文零配置列 7（含 B站），系博文内部矛盾。官方**默认激活口径为 6**；B站官方另注"装好即用、无需登录"但不属于默认激活 6 个（F-061，[concepts/01](concepts/01-capability-layer-architecture.md) 有完整对照表）。
3. **SKILL.md 位置**：不在仓库根目录，实际在 `agent_reach/skill/SKILL.md`（另有英文版与 7 篇 references）（F-062）。
4. **channels/ 树图**：博文画 9 文件、README 树画 13 渠道，均为简化示意；git tree 地面真值为 **20 文件/17 个渠道实现**（F-063）。
5. **pipx 命令出处**：博文的 pipx 安装命令逐字出自官方 **docs/install.md**，README 正文无 pipx 字样（主推"一句话发给 Agent"）；命令可照做（F-066）。另有 lobehub 旧镜像"13+ platforms/含抖音微博"系过期快照，不采信（F-070）。

## 采用提示与已知边界

- **登录态渠道有账号风险**：小红书/Reddit/Facebook/Instagram 及 Twitter token 依赖登录凭据，Cookie 等同完整登录权限，项目方与博文都一致要求**专用小号**；官方建议稳定场景走约 $1/月的服务器代理（F-033/F-068，见 [examples/02](examples/02-login-channels-and-cookie-safety.md)）。
- **供应链**：官方警告不要从 PyPI 安装同名包，以 GitHub archive / install.md 为准（F-069）。
- **个人维护项目的供应风险**：owner 为个人开发者（36 位贡献者、核验前一日仍有 commit，维护活跃），但渠道可用性系于上游工具与平台风控，采用前建议锁版本、先 `--dry-run` 与 `doctor` 自检。
- **"最稳选型"为项目方自述**：README 含赞助商区块（BrowserAct/腾讯云 OpenClaw/CoreClaw/UCloud）与作者业务合作信息（F-071）；本包核验了渠道/文件存在性与故障史文字记载，**未逐一实测 17 个渠道实现的当前可用性**，也未复现 doctor 输出。
- **数字时效**：Star/渠道口径为 2026-10-08 快照，`stale_after: 2026-12-31`，到期前复核默认激活数、channels 实现数与选型链。
- 博文末条"五条设计启示"为推介作者**个人观点（V）**，[concepts/03](concepts/03-skill-md-agent-distribution-paradigm.md) 已逐条标注并附适用边界，勿当作客观结论。

## 信源与可信度

- 事实清单与逐条核验状态：[references/article-source.md](references/article-source.md)（F-001~F-072，72 条）
- P0/P1 核验报告与勘误四张清单：[references/verification.md](references/verification.md)（21 项 16✅/5⚠️/0❌）
- 信源距离：第三方公众号综述 → 已升级为 GitHub API + 官方 README/install.md + git tree 一手交叉核验，第三方（neodrop/GitCode/lobehub/deepwiki）仅作旁证

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
