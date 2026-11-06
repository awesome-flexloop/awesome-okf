---
okf_version: "0.2"
type: bundle
title: "WeChat Intelligence Hub：把微信聊天变成本地个人情报库"
description: "本地优先、只读的微信个人情报库——只读 Reader + 两个 Codex Skill、旗舰交互式日报与 Markdown/HTML 双报告、定向检索与承诺/待回复/商机信号、全虚构 Demo 与真实接入差距；微信博文经 GitHub API 与官方 README 核验转化（22 项 P0/P1：14✅/8⚠️/0❌）"
tags: [wechat-intelligence-hub, wechat, local-first, read-only, personal-intelligence, codex-skill, python, agpl-3-0, 博文转化, 概念骨架]
generated:
  by: seven-concepts-cmd+blog-article-to-okf-wiki
  at: "2026-11-06T11:48:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-11-06T11:48:00+08:00"
status: stable
stale_after: 2027-03-06
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/LNyKE5lex4qBOmIS4Z-7sg
  - id: github-repo
    url: https://github.com/Rion-Wu-tech/wechat-intelligence-hub
  - id: github-api
    url: https://api.github.com/repos/Rion-Wu-tech/wechat-intelligence-hub
---

# WeChat Intelligence Hub：把微信聊天变成本地个人情报库

> **类型**：产品解析 / 概念综述（**无 `examples/`**——操作可复现性两问皆「否」；官方命令仅作路径说明登记于 concepts/04）
> **信源**：微信公众号「开源食谱」《5 天攒 2000 星！让微信聊天变情报库，相见恨晚！》（原创，豆芽菜小萌，2026-09-24 07:02 北京）→ 2026-11-06 经 GitHub REST API 与官方 README 逐项核验
> **核验结论**：22 项 P0/P1 声明 **14✅ / 8⚠️ / 0❌**，无核心声明被证伪 → `status: stable`
> **数据时点**：Star 等动态数字为 2026-11-06 快照；功能口径为 main 分支 `v0.9.2-preview.2`

## 本文概要

[WeChat Intelligence Hub](https://github.com/Rion-Wu-tech/wechat-intelligence-hub) 是一个 Python 编写、`AGPL-3.0-only` 许可、2026-09-04 创建的本地优先微信个人情报库（F-041、F-055）。它的底层是一个**只读 Reader**，只读取本机已有的聊天记录；上层把消息流转成日报、待回复、承诺、商机与复联线索（F-026、F-044）。官方以「一个产品，两个 Skill」交付：`wechat-cli` 与 `wechat-intelligence-hub`，可在 Codex 里用自然语言调用（F-046、F-051）。

它的差异点不在「搜聊天记录」，而在**输出带时态的状态与行动项**。旗舰交互式日报按博文图注给出四个入口（综合行动 / 群聊日报 / 重点联系人 / 商单信号雷达），报告同时产出 Markdown 与 HTML（F-011、F-014、F-052）。没有真实数据读取条件时，可用**全虚构 Demo** 先把索引、判断与报告链路跑通（F-032、F-049）。

## 阅读路径

**先建立概念（约 15 分钟）**

1. [00 · 项目身份、热度时点与信源距离](concepts/00-what-is-wechat-intelligence-hub.md)——官方身份、三星标口径、四层信源距离
2. [01 · 本地优先只读架构与两个 Skill](concepts/01-local-first-readonly-architecture.md)——Reader/情报产品分层、数据边界、⚠️「不重签名」范围
3. [02 · 旗舰交互式日报、双格式报告与四种视图](concepts/02-flagship-daily-report-and-four-views.md)——上层产物长什么样、哪些是图注单源

**再理解能力与边界**

4. [03 · 定向检索、重点联系人与行动项](concepts/03-search-contacts-and-actions.md)——消息 → 状态 → 行动项
5. [04 · 官方命令路径与全虚构 Demo 的差距](concepts/04-official-workflow-and-demo-gap.md)——五步官方命令（未实机验证）与接入前数据纪律
6. [05 · 洞察、可迁移模式与采用边界](concepts/05-insights-and-adoption-boundaries.md)——三条洞察、M1~M3 模式、AGPL-3.0-only 商业授权

**需要查证时**

- [references/article-source.md](references/article-source.md)（F-001~F-057）· [references/verification.md](references/verification.md)（P0 报告 + 勘误四张清单）

## 核心事实速查

| 项 | 值 | 出处 |
|----|-----|------|
| 主线仓库 | `Rion-Wu-tech/wechat-intelligence-hub` | F-041、F-057 |
| 创建 / 发文 / 核验 | 2026-09-04 / 2026-09-24 / 2026-11-06 | F-041、F-002、F-042 |
| 语言 / 许可 | Python / `AGPL-3.0-only`（闭源·OEM·白标需商业授权） | F-041、F-055 |
| 当前版本 | `v0.9.2-preview.2`（博文未提） | F-045 |
| Star | 博文 1,976（标题取整 2,000）→ **2,764（2026-11-06）** | F-006、F-007、F-042 |
| 分层 | 底层只读 Reader + 上层情报产品；四层目录 | F-026、F-047 |
| 交付 | 一个产品、两个 Skill：`wechat-cli` / `wechat-intelligence-hub` | F-046 |
| 报告产物 | `wechat_daily_full.md`、`wechat-report/`、`wechat_daily_report.html` | F-052 |
| 报告格式 | Markdown + HTML 双格式 | F-014 |
| 日报入口（图注口径） | 综合行动 / 群聊日报 / 重点联系人 / 商单信号雷达 | F-011 |
| 安装 / Demo | `./scripts/install.sh --with-sqlcipher --with-html`；`run_demo.sh` | F-048、F-049 |
| 数据边界 | 本机、不进 Git、不上服务器、样例虚构；只读不保证零封控 | F-028、F-053、F-054 |

## ⚠️ 阅读前必知的四条口径勘误

1. **「5 天」不是「创建后 5 天」**：API 显示仓库创建于 2026-09-04，与发文 2026-09-24 相隔约 20 天；「5 天攒 2000 星」是**博文口径的星标增长窗口，未独立核验**（F-006~F-008、F-041）。标题 2000 与正文 1976 是同一时点的取整与精确值，不是矛盾。
2. **「不重签名」只约束 Reader 核心**：官方确认 Reader 不获取密钥、不重签名、不注入、不 Hook（F-027），但 macOS **候选接入助手**可能重启微信、重签名副本，Windows 首次获取路径尚未合入（F-056）。不可泛化为全项目承诺。
3. **截图不等于验收**：四个入口名、四种视图、移动端、回复草稿、检索五维度均为**博文/图注单源**，官方 README 只有语义对应、未逐字给出名称（F-011~F-024 的 ⚠️ 项）。
4. **全虚构 Demo 证明链路，不证明真实数据可用**：官方 Demo 使用虚构数据（F-032、F-049）；完整历史需本人授权本地数据库，且只覆盖已同步到本机、当前可读的数据（F-034、F-054）。

## 采用提示与已知边界

- **许可证**：`AGPL-3.0-only`，闭源 / OEM / 白标需商业授权；修改后以网络服务对外提供会触发 AGPL 网络开源义务（F-055）。商业内嵌前建议法务确认。
- **成熟度**：`v0.9.2-preview.2`，命令与目录结构可能漂移；本束命令为 2026-11-06 官方 README 文档快照，**未实机验证**（F-045、F-048）。
- **平台风险**：只读不保证零封控、不保证任意微信版本长期兼容；macOS 新机器获取路径官方标注未实测（F-035、F-054、F-056）。
- **数字时效**：Star/功能集为 2026-11-06 核验时点快照，`stale_after: 2027-03-06`，到期前复核。
- **证据强度**：本束无 ❌ 级反证，但标题热度 hook 与 UI 层命名均未独立核验，详见 [references/verification.md](references/verification.md)。

## 信源与可信度

- 事实全集（F-001~F-057，博文 40 + 官方核验 17）：[references/article-source.md](references/article-source.md)
- P0 核验报告与勘误四张清单：[references/verification.md](references/verification.md)
- 信源距离：第三方开源推介号 → 已升级为 GitHub REST API 与官方 README 一手交叉核验；UI 层仍为官方截图经第三方转述。
- 归属歧义：检索中另有 `echoD886/wechat-intelligence-hub` 同名仓库，主线以官方 clone 地址与 API `full_name` 确认（F-057）。
- 同名仓库、`share?code=` 等私域信号均未出现；内容敏感度预检判定 Public，走标准 Spec Mode。

## 主题关联

- [wigolo](../wigolo/index.md)：同属「本地优先情报层」路线，但面向公开 Web（MCP 搜索/抓取）；本束面向本机聊天数据，二者互补。
- [agent-reach](../agent-reach/index.md)：同样以 Skill/CLI 形态给 Agent 装能力，可对照「能力层」与「情报产品」的边界划分。
- [inkos](../inkos/index.md)：同为 `AGPL-3.0` 许可的中文开源项目，可对照许可证采用边界。
- [creatorhub](../creatorhub/index.md)：同样涉及本地数据、隐私合规与「无 LICENSE/边界需勘误」类核验议题。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```
