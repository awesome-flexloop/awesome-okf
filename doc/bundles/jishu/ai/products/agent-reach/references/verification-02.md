---
okf_version: "0.2"
type: Reference
title: "第二篇博文 P0 核验报告与 v1.6.0 版本漂移"
description: "对「架构文摘」2026-10-17 文章的 20 项 P0/P1 核验（10✅/6⚠️/4❌），勘误四张清单、v1.5→v1.6 漂移对照，以及首版知识包 5 处错误回改登记"
tags: [agent-reach, verification, p0-check, fact-check, errata, version-drift]
generated: { by: "blog-article-to-okf-wiki:R/V", at: "2026-10-26T10:55:00+08:00" }
status: stable
stale_after: 2027-01-31
sources:
  - id: blog2
    url: https://mp.weixin.qq.com/s/kk4iSX6xdk3IsNKO4eVy9w
  - id: github-api
    url: https://api.github.com/repos/Panniantong/Agent-Reach
  - id: official-readme
    url: https://raw.githubusercontent.com/Panniantong/agent-reach/main/README.md
  - id: official-install
    url: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
  - id: official-sessions
    url: https://raw.githubusercontent.com/Panniantong/agent-reach/main/agent_reach/skill/references/sessions.md
  - id: readme-v150
    url: https://raw.githubusercontent.com/Panniantong/agent-reach/v1.5.0/README.md
  - id: install-v150
    url: https://raw.githubusercontent.com/Panniantong/agent-reach/v1.5.0/docs/install.md
---

# 第二篇博文 P0 核验报告与 v1.6.0 版本漂移

> 核验时间：2026-10-26。信源：GitHub REST API（仓库元数据、release 列表、channels 目录树）、main 分支 README / docs/install.md / skill/SKILL.md / skill/references/sessions.md、v1.5.0 tag 的 README 与 install.md。
> 博文信源距离：**第三方公众号综述，且作者自陈未实测**（F-074），低于一手实测，只可作为线索，不可作为结论。
> 对应事实登记：[article-source-02.md](article-source-02.md)（F-073~F-120）。

## 核验总览

| 级别 | 数量 | 结论分布 |
|------|------|---------|
| P0（数字/日期/命令/参数/结构/安全口径） | 14 | ✅ 7 / ⚠️ 4 / ❌ 3 |
| P1（能力声明/引文/观点归属） | 6 | ✅ 3 / ⚠️ 2 / ❌ 1 |
| 合计 | 20 | **✅ 10 / ⚠️ 6 / ❌ 4** |

**总体评估**：项目真实、活跃、机制描述基本准确；但文章有 **4 项与官方材料直接矛盾**（Star 数字、`pip install`、`--system` 参数、"不读取小红书浏览器 Cookie"），另有 6 项口径/时效偏差。4 项 ❌ 中，只有 Star 数字属"核心热度声明"，其余 3 项是**可照做性/安全性误导**——读者若照做会踩坑或误解隐私边界，因此必须在正文显著位置纠正。本包状态维持 **stable**（项目身份、16→14 渠道机制、412 故障史、医生体检、能力层定位均成立），但勘误须逐条落实。

## 勘误四张清单

### ① 数字/日期表

| 声明（F） | 官方核验 | 结论 |
|-----------|---------|------|
| Star 87,759（F-077） | 2026-10-08 已 93,673；2026-10-26 为 102,508（F-102/F-107） | ❌ 数字低于更早时点，非发布日快照；正确写法是"87,759 无出处；10-17 前后应约 9.5万–10万" |
| "16 个平台"（F-086） | main@10-08 有 16 个渠道实现（17 个 py 减 mcporter 承载）；README 表列 13 行；v1.6.0 为 14（F-107/F-108） | ⚠️ 有时间点依据，但必须标注版本；当前口径是 14 |
| 文章平台表 13 行（F-087） | 13 行 = 缺 Exa/Facebook/Instagram 三项 | ⚠️ 与标题的 16 自相矛盾 |
| "上线半年多"（F-076） | created_at 2026-02-24，至发文 7 个半月（F-105） | ✅ |
| "Trendshift 日榜榜首"（F-078） | README 挂 Trendshift #24387 "#1 Repository of the Day" 徽章（F-117） | ✅ 徽章由项目自挂，Trendshift 页面存在；视为项目自述+第三方榜单，非独立审计 |

### ② 命令/参数溯源表

| 声明（F） | 官方核验 | 结论 |
|-----------|---------|------|
| `pip install agent-reach`（F-095） | install.md 首屏即警告"PyPI 上叫 agent-reach 的包不是本项目，绝不要从 PyPI 安装"；v1.5.0 允许 `pip install <GitHub archive URL>`，v1.6.0 改用 `uv tool install <release zip>`（F-109/F-110） | ❌ 装的是别人家的包；且与同段引用的警告自相矛盾 |
| `--system` 显式授权（F-092） | 两个版本的 install.md 与 README 均无该参数；实际为 `install --env=auto`（默认）、`--safe`（只检查）、`--dry-run`（预览）（F-110） | ❌ 参数不存在，照抄会直接报错 |
| 安装器检查 Node.js/gh CLI/mcporter（F-082） | 属 v1.5.0 README 的"它会做什么"第 2 步；v1.6.0 主路径改为 uv + `setup` | ⚠️ 版本口径 |
| `agent-reach doctor` 报当前后端（F-083） | 命令存在；v1.6.0 起所有命令输出单个 JSON，人读用 `doctor --text`（F-111） | ✅ 能力成立，输出形态已变 |
| 一句话安装链接（F-081） | `docs/install.md` 路径存在且可访问 | ✅ |

### ③ 口径对照表（平台/成本）

| 声明（F） | 官方核验 | 结论 |
|-----------|---------|------|
| "零 API 费：所有工具开源、API 免费"（F-091） | v1.6.0 README：YouTube 转文字、小宇宙转文字需 Groq 或 OpenAI Key（F-114）；v1.5.0 称 Whisper 用"免费 Key" | ⚠️ 应写"基础读取零 API 费；语音转文字需第三方 Key（Groq 有免费额度）" |
| 代理约 $1/月（F-079） | v1.5.0 README："本地电脑不需要代理，代理只有部署在服务器上才需要（~$1/月）"（F-115）；v1.6.0 README 未重述 | ✅ 历史口径成立；当前版本未再承诺价格 |
| Cookie 存 `~/.agent-reach/config.yaml`、权限 600（F-090） | v1.5.0 README 明文 600（F-115）；v1.6.0 安装文档确认升级保留该文件，但未重述权限 | ✅ 配置路径成立，权限表述以 v1.5.0 为准 |
| "16 个平台全覆盖"（F-086/F-099） | v1.6.0 为 14 渠道（5 默认/6 可选/3 实验），RSS 与 Exa 已退役（F-108） | ⚠️ 覆盖数下降，属"诚实瘦身"（v1.4.2 起移除失修渠道），不应作为长期卖点 |

### ④ 引文逐字核对表

| 声明（F） | 原文 | 结论 |
|-----------|------|------|
| "README 明说：Twitter 只接受用户通过 Cookie-Editor 手工导出的内容"（F-093） | v1.5.0 README："需要 Cookie 的平台（Twitter、小红书等），**优先使用** Chrome 插件 Cookie-Editor 导出 Cookie" | ⚠️ "优先"被改写成"只接受"；同一版本另提供 OpenCLI 登录态路径 |
| "Agent Reach 不替用户执行小红书登录，也不读取小红书浏览器 Cookie"（F-094） | v1.5.0 README：小红书"桌面装 OpenCLI（刷过小红书即可用）"；v1.6.0 sessions.md：首次会复制该站 Cookie 一次到专用浏览器（F-113） | ❌ 前半句真，后半句假；正确表述见下节 |
| "本人在写稿时未逐条真机复现"（F-074） | 文内原句 | ✅ 如实，且应据此下调信源等级 |
| "README 被赞助商广告占据：BrowserAct、腾讯云 Lighthouse、CoreClaw、优刻得星图等"（F-100） | main README 赞助商 6 家，另有 Bright Data、RapidProxy（F-116） | ✅ 事实成立，列举不全 |
| 团队落地四段（F-097） | 无官方出处 | ⚠️ 作者建议（V），第②段"Cookie-Editor 手工导出"已被 v1.6.0 自动复制会话取代 |

## 安全口径的正确表述（重点）

对"会不会碰我的浏览器和账号"这个问题，官方 v1.6.0 的准确表述是三条，而不是"不读取 Cookie"：

1. 所有浏览器渠道共用一个**专用浏览器**，与日常 Chrome 分开，默认无头、闲置 10 分钟自动关闭（F-112）。
2. 首次使用某站时，若 Chrome 已连 OpenCLI 扩展，程序会**把该站 Cookie 复制一次**到专用浏览器；只复制该站，不复制整个浏览器目录、其他站点或密码库，不改动来源浏览器（F-113）。
3. 需要本人登录时才开窗口，由用户完成；程序不代登、不要密码、不输出 Cookie；退出/移除渠道后不再自动复制（F-119）。

因此，**"不读取浏览器 Cookie"是错误表述**；正确的风险提示是"会复制该站 Cookie 到专用浏览器，等同该账号的登录权限，务必用专用小号"。

## v1.5.0 → v1.6.0 版本漂移对照

| 维度 | v1.5.0（2026-06-11，文章写作期） | v1.6.0（2026-10-23，当前） |
|------|--------------------------------|---------------------------|
| 安装 | pipx + GitHub archive；`install --env=auto [--safe\|--dry-run]` | `uv tool install <release zip>` + `agent-reach setup`；从 1.5 有迁移专章 |
| 渠道数 | README 表 13 行 / tag 内 13 个渠道模块 | 14 渠道：默认 5 / 可选 6 / 实验 3；RSS、Exa 退役 |
| 命令输出 | 人读文本为主，`doctor --json` | 所有命令输出单个 JSON（`ok`/`result`/`error.hint`）；人读用 `doctor --text` |
| 更新 | `check-update` 提醒 | 结果内嵌 `meta.update`；`agent-reach update` |
| 登录/会话 | OpenCLI 复用浏览器登录态；Cookie-Editor 优先 | 专用浏览器 + 首次自动复制该站 Cookie；`login --import-existing` 重取 |
| 密钥 | 小红书/小宇宙按引导配置 | `agent-reach configure groq-key`，Key 不进聊天 |
| 卸载 | `uninstall [--dry-run] [--keep-config]` | `uninstall --dry-run` 先列清单，确认后执行 |
| 平台分级 | "装好即用 / 配置后解锁" | "默认 / 可选 / 实验"（实验档明示可能随时失效） |

> 这张表解释了为什么同一篇介绍在不同时间读会"对不上"：文章写于 1.5 时代，而 1.6 在 6 天后发布，改了安装器、渠道集与输出协议。**引用任何平台数、安装命令前，先确认版本。**

## 首版知识包（2026-10-08）勘误回改登记

首版依据 1.5 时代材料写成，本次复核发现 5 处需要回改，已在正文落实：

| # | 位置 | 原表述 | 回改后 | 依据 |
|---|------|--------|--------|------|
| 1 | 根 index、概念 02、示例 00 | `install --system` 三档授权 | `install --env=auto` + `--safe` + `--dry-run`，无 `--system` | F-110 |
| 2 | 概念 01、概念 02、示例 02 | "不读浏览器 Cookie" | 会复制该站 Cookie 一次；不复制整目录/密码库 | F-113 |
| 3 | 根 index、概念 00/01、示例 01 | 16 渠道、6 个默认激活 | 历史 16 → 现行 14；默认 5 / 可选 6 / 实验 3 | F-107/F-108 |
| 4 | 根 index、概念 00/03、示例 00 | 最新 v1.5.0、93.7k Star | v1.6.0、102,508（2026-10-26） | F-102/F-103 |
| 5 | 概念 03 | `agent-reach check-update` | `meta.update` + `agent-reach update` | F-119 |

> 这不是"推翻首版"，而是**版本漂移的正常维护**：首版对 1.5 的描述在当时是准确的，只是 1.6 改了实现。知识包把两代口径都保留下来，读者才能判断自己装的是哪一代。

## 结论与复核计划

- **可采信**：项目身份、能力层定位、有序后端路由、412 故障切换、doctor 真实探测、只读边界、专用浏览器隔离。
- **不可照抄**：Star 数字、`pip install` 命令、`--system` 参数、"不读取 Cookie"的隐私表述、固定的"16 平台"。
- **复核触发条件**：v1.7.0 发布、README 平台表增删渠道、`docs/install.md` 安装器再次更换、`stale_after` 到期（2027-01-31）。
