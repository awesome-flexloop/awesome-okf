---
type: Reference
title: 事实核验报告
description: Cua博文18项P0声明核验结论（12通过6时点/口径差异0失败），6项时点勘误详解（Stars/Forks/Issues/主语言/日增/Trending/开发主体），权威来源URL汇总
tags: [核验, P0, 勘误, Cua, Computer-Use, GitHub, trycua, MIT]
generated: { by: "blog-article-to-okf-bundle", at: "2026-10-10T10:50:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: wechat-article-finops-cua
    resource: https://mp.weixin.qq.com/s/6FaVJOhGomsSn43RdFMRlg
    title: 《开源精选 | Cua》（FinOps实战，2026-09-26）
  - id: github-api-cua
    resource: https://api.github.com/repos/trycua/cua
    title: GitHub API：trycua/cua 仓库元数据（2026-10-10）
  - id: newreleases-cua
    resource: https://newreleases.io/project/github/trycua/cua
    title: newreleases.io：trycua/cua Releases
  - id: piwheels-cua-sandbox
    resource: https://www.piwheels.org/project/cua-sandbox/
    title: piwheels：cua-sandbox 版本历史
  - id: cua-driver-pypi
    resource: https://libraries.io/pypi/cua-driver
    title: Libraries.io：cua-driver PyPI 页（含官方 README 摘要）
  - id: openai-hub-cua-s1
    resource: https://www.openai-hub.com/news/2096/
    title: OpenAI Hub：CUA-S1 开源报道（2026-09-19）
  - id: wechat-article-2-cua
    resource: https://mp.weixin.qq.com/s/vEGTwWZ8Mws2fwAQyvm0Yg
    title: 《别再让 Agent 用你的电脑了「Cua：2.8 万 Star 的开源项目」》（极限编程驿站，2026-10-08）
  - id: github-api-cua-20261016
    resource: https://api.github.com/repos/trycua/cua
    title: GitHub API：trycua/cua 仓库元数据（2026-10-16）
  - id: cua-readme-main
    resource: https://cdn.jsdelivr.net/gh/trycua/cua@main/README.md
    title: 官方 README（trycua/cua main 分支，经 jsDelivr 镜像）
  - id: cuabench-leaderboard
    resource: https://cua.ai/cuabench/leaderboard
    title: Cua-Bench EDA Leaderboard（v1）
  - id: cua-home
    resource: https://cua.ai/
    title: Cua 官网首页（Cua Spaces 许可与定价）
  - id: cua-docs
    resource: https://cua.ai/docs
    title: Cua 官方文档中心
  - id: cua-docs-deprecated
    resource: https://cua.ai/docs/cua-sdk/guides/migrate-from-deprecated-packages
    title: 官方文档：从废弃包迁移
  - id: cua-docs-lifecycle
    resource: https://cua.ai/docs/concepts/sandbox-lifecycle
    title: 官方文档：Sandbox lifecycle（Fleet 池容量与费用）
---

# 事实核验报告

> 对博文《开源精选 | Cua》中 18 项 P0/P1（最高优先级）声明进行权威核验。
> 核验日期：2026-10-10。
> 结果：**12 项通过（✅）、6 项时点/口径差异（⚠️）、0 项失败（❌）**。

## 1. 核验结论总览

| # | 声明 | 结论 | 对应事实 |
|---|------|------|---------|
| 1 | 仓库存在/创建时间 2025-01-31 | ✅ 通过 | F-019 / F-054 |
| 2 | MIT 协议 | ✅ 通过 | F-004 / F-056 |
| 3 | README 副标题引语 | ✅ 通过 | F-008 / F-056 |
| 4 | 开发主体 Cua AI, Inc. | ⚠️ 部分通过 | F-004 / F-054 |
| 5 | sandbox v0.8.0 于 2026-09-15 发布 | ✅ 通过 | F-024 / F-058 |
| 6 | Stars 24,432（2026-09-20 快照） | ⚠️ 时点差异 | F-016 / F-055 |
| 7 | Forks 1,681 | ⚠️ 时点差异 | F-017 / F-055 |
| 8 | 开放 Issues 1,032 | ⚠️ 时点差异 | F-020 / F-055 |
| 9 | 主语言 HTML | ⚠️ 时点差异 | F-026 / F-057 |
| 10 | 每日 nightly 发布 | ✅ 通过 | F-023 / F-060 |
| 11 | 安装命令（Driver/Lume/Bench） | ✅ 通过 | F-027~F-034 / F-062 |
| 12 | 6×7 计算器教程 | ✅ 通过 | F-029 / F-061 |
| 13 | CUA-S1 开源/source-only | ✅ 通过 | F-013/F-049 / F-063 |
| 14 | 第三方组件许可证 | ✅ 通过 | F-015 / F-064 |
| 15 | 日增 +859 / Trending 第 2 | ⚠️ 时点数据 | F-018 |
| 16 | 五大核心模块 | ✅ 通过 | F-010~F-014 / F-062 |
| 17 | Computer-Use 2.0 定义 | ✅ 通过 | F-007 / F-062 |
| 18 | run.cua.ai / cua.ai/docs 存在 | ✅ 通过 | F-036/F-040 |

## 2. 通过项详情

### ✅ 仓库存在与创建时间（F-054）
- **博文声明**：仓库 github.com/trycua/cua，创建于 2025-01-31。
- **核验**：GitHub API `repos/trycua/cua` 返回 id 925270205，`created_at: 2025-01-31T15:02:49Z`，与博文完全一致。owner 为 Organization `trycua`（id 191107687），homepage=https://cua.ai。
- **来源**：[GitHub API](https://api.github.com/repos/trycua/cua)

### ✅ MIT 协议（F-056）
- **博文声明**：项目采用 MIT 协议。
- **核验**：GitHub API `license` 字段 = `MIT License`（spdx_id MIT），官方材料一致。
- **来源**：GitHub API

### ✅ README 副标题逐字一致（F-056）
- **博文声明**：官方 README 副标题 "Scale computer-use 2.0 with open-source drivers, cross-OS fleets, and benchmarks for training, evaluation, and data generation."
- **核验**：GitHub API `description` 字段与博文引语**逐字一致**。
- **来源**：GitHub API

### ✅ sandbox v0.8.0 发布日期（F-058）
- **博文声明**：最近正式版为 2026-09-15 发布的 sandbox v0.8.0。
- **核验**：双重确认——newreleases.io 记录 GitHub release `sandbox-v0.8.0`（"0.8.0 (2026-09-15)"）；piwheels 记录 cua-sandbox 0.8.0 于 2026-09-15 16:49:04 UTC 发布。
- **来源**：[newreleases.io](https://newreleases.io/project/github/trycua/cua/release/sandbox-v0.8.0)、[piwheels](https://www.piwheels.org/project/cua-sandbox/)

### ✅ 每日 nightly 发布（F-060）
- **博文声明**：cua-driver-rs 保持每日 nightly 发布（2026-09-14 到 09-19 一天不落）。
- **核验**：newreleases.io 显示 `nightly-cua-driver-rs-v0.28.3-nightly.20260917`、`20260918`、`20260919` 连续发布，与博文描述一致。
- **来源**：[newreleases.io](https://newreleases.io/project/github/trycua/cua)

### ✅ 安装命令（F-062）
- **博文声明**：Driver（macOS/Linux + Windows）、Lume 安装脚本 URL 与命令。
- **核验**：官方文档摘要（libraries.io PyPI 页）逐字一致：
  - macOS/Linux：`/bin/bash -c "$(curl -fsSL https://cua.ai/driver/install.sh)"`
  - Windows（PowerShell）：`irm https://cua.ai/driver/install.ps1 | iex`
  - Lume：`/bin/bash -c "$(curl -fsSL https://cua.ai/lume/install.sh)"`
- **来源**：[Libraries.io cua-driver 页](https://libraries.io/pypi/cua-driver)

### ✅ 6×7 计算器教程（F-061）
- **博文声明**：首个任务为连接 Agent，打开计算器算 6×7，验证显示 42。
- **核验**：官方教程逐字一致："Your first result: connect your agent, ask it to compute 6 × 7 in Calculator, and have it verify that the app displays 42."
- **来源**：官方文档摘要（libraries.io）

### ✅ CUA-S1 开源/source-only（F-063）
- **博文声明**：CUA-S1 为 System 1 决策模型家族，源码 MIT 开源、权重在 Hugging Face，早期研究性发布（source-only）。
- **核验**：OpenAI Hub 2026-09-19 报道"Cua 开源 CUA-S1"，确认其为 System 1 决策模型、面向高频桌面操作；权重托管 Hugging Face 按各自卡片条款授权。source-only 口径一致。
- **来源**：[OpenAI Hub 报道](https://www.openai-hub.com/news/2096/)

### ✅ 第三方组件许可证（F-064）
- **博文声明**：主项目 MIT；Kasm MIT、OmniParser CC-BY-4.0、可选 cua-agent[omni] 含 AGPL-3.0 ultralytics。
- **核验**：多方报道确认"可选的感知扩展（OmniParser 套件）是 AGPL 系"；Kasm MIT、OmniParser CC-BY-4.0 为官方 README 明确声明，无矛盾来源。
- **来源**：腾讯云开发者社区、闲人野鹤等 2026-09 报道

### ✅ 五大核心模块 / Computer-Use 2.0 定义（F-062）
- **博文声明**：Driver/Fleets/Lume/CUA-S1/Bench 五模块；Computer-Use 2.0 = Agent 在同一任务中穿梭代码/API/图形界面。
- **核验**：官方材料确认五模块架构；官方定义 "an agent moving between code, APIs, and graphical interfaces within the same task" 与博文表述一致。
- **来源**：官方 README/文档页

## 3. 勘误与时点差异详解

### ⚠️ 差异1：开发主体名称（F-054）
- **博文表述**："由 Cua AI, Inc. 开发"。
- **实际情况**：GitHub owner 为 Organization `trycua`；官网（cua.ai）以 Cua 品牌运营。博文所称"Cua AI, Inc."应为公司法律实体名称，GitHub API 无法直接证实该法律实体注册名。属于口径问题，非事实错误。

### ⚠️ 差异2：Stars 快照（F-055）
- **博文表述**：总 Stars 24,432（采集于 2026-09-20）。
- **实际情况**：2026-10-10 GitHub API 实测 **29,189**。博文快照为时点数据，引用时须带时点。多方 2026-09-19~21 报道（25.2k）佐证博文快照合理。
- **处理**：正文标注"博文 2026-09-20 快照"，同时给出官方 2026-10-10 时点值。

### ⚠️ 差异3：Forks 快照（F-055）
- **博文表述**：Forks 1,681。
- **实际情况**：2026-10-10 实测 **2,061**。时点差异。

### ⚠️ 差异4：开放 Issues 快照（F-055）
- **博文表述**：1,032 个。
- **实际情况**：2026-10-10 实测 **1,149**。时点差异。

### ⚠️ 差异5：主语言 HTML vs Rust（F-057）
- **博文表述**：主语言标记为 HTML（文档站与演示页）。
- **实际情况**：2026-10-10 GitHub API `language` 字段为 **Rust**。GitHub 主语言字段由仓库字节占比决定，随时间点变动；博文快照（2026-09-20）当时可能确为 HTML。属于时点差异。
- **处理**：正文呈现两种口径并标注时点。

### ⚠️ 差异6：日增 +859 / Trending 第 2（F-018）
- **博文表述**：今日新增 +859，GitHub Trending 日榜第 2。
- **实际情况**：该数据为 2026-09-20 当日快照，无法事后精确复核。多方报道确认 2026-09-19~21 期间 Cua 在 GitHub Trending 前列（如 9 月 21 日 +1018、25.2k 星），博文快照合理。Trendshift 徽章为第三方趋势产品，与 GitHub Trending 不同源。
- **处理**：作为时点数据呈现，附多方佐证。

## 4. 快照后演进（博文未覆盖）

以下为 2026-09-26 博文发布后的官方演进，bundle 正文以"快照后演进"标注，不混入博文事实：

| 演进 | 说明 | 来源 |
|------|------|------|
| cua-sandbox 0.9.0 | 2026-10-01 发布 | piwheels |
| Cua Spaces 桌面应用 0.1.0 | 新增 Cua Spaces 桌面应用产品线，source-available 于 FSL-1.1-MIT | 官方材料 |

## 5. 权威来源汇总

| 来源 | URL | 用途 |
|------|-----|------|
| GitHub API：trycua/cua | https://api.github.com/repos/trycua/cua | 仓库身份/创建时间/许可证/stars/forks/issues/语言 |
| newreleases.io：trycua/cua | https://newreleases.io/project/github/trycua/cua | sandbox-v0.8.0 日期、nightly 发布节奏 |
| piwheels：cua-sandbox | https://www.piwheels.org/project/cua-sandbox/ | cua-sandbox 版本历史（0.8.0/0.9.0 日期） |
| Libraries.io：cua-driver | https://libraries.io/pypi/cua-driver | 官方 README 摘要、安装命令、6×7 教程、Computer-Use 2.0 定义 |
| OpenAI Hub：CUA-S1 报道 | https://www.openai-hub.com/news/2096/ | CUA-S1 开源事件与定位 |
| 腾讯云开发者社区 | https://cloud.tencent.com/developer/article/2746885 | 五模块架构、AGPL 系组件交叉验证 |
| 今日头条（闲人野鹤） | http://m.toutiao.com/group/7691121640284897834/ | 五模块、安装命令、CUA-S1 权重授权交叉验证 |
| 博文原文 | https://mp.weixin.qq.com/s/6FaVJOhGomsSn43RdFMRlg | 主信源事实与观点 |

## 6. 第二轮核验（第二篇文章 P0）

> 核验对象：第二篇文章《别再让 Agent 用你的电脑了「Cua：2.8 万 Star 的开源项目」》（极限编程驿站，2026-10-08，对应事实 F-066~F-154，见 [second-article-facts.md](second-article-facts.md)）。
> 核验日期：2026-10-16。
> 结论口径：`✅ 通过`=与权威源一致 / `⚠️ 时点或口径差异`（含「未获官方页核验，仅第二篇单源」）/ `❌ 失败`。
> 结果：**14 项通过（✅）、6 项时点/口径差异或未核验（⚠️）、0 项失败（❌）**。

| # | 声明 | 结论 | 对应事实 | 来源 |
|---|------|------|---------|------|
| 1 | 仓库 github.com/trycua/cua、MIT、2025 年 1 月建仓 | ✅ 通过 | F-070/F-074/F-075 → F-141 | https://api.github.com/repos/trycua/cua |
| 2 | Star 超 2.8 万 | ⚠️ 时点/口径差异（约数偏低：2026-10-16 实测 29,926） | F-071 → F-140 | https://api.github.com/repos/trycua/cua |
| 3 | Fork 超 2,000 | ✅ 通过（2,142） | F-072 → F-140 | https://api.github.com/repos/trycua/cua |
| 4 | Rust 约占仓库代码量 47% | ⚠️ 口径差异（languages API 实测 42.31%） | F-073 → F-142 | https://api.github.com/repos/trycua/cua/languages |
| 5 | 130+ 位贡献者 | ✅ 通过（149/155） | F-076 → F-143 | https://api.github.com/repos/trycua/cua/contributors |
| 6 | 六组件（Driver/Spaces/Lume/SDK-CLI/CUA-S1/Bench） | ✅ 通过 | F-077~F-086 → F-144/F-148/F-152 | https://cdn.jsdelivr.net/gh/trycua/cua@main/README.md、https://cua.ai/docs |
| 7 | Cua Spaces：macOS 26+、个人免费 | ✅ 通过 | F-079 → F-151 | https://cua.ai/ |
| 8 | SDK 提供 Python/TypeScript/Swift/Kotlin 四语言 | ✅ 通过 | F-081 → F-148 | https://cdn.jsdelivr.net/gh/trycua/cua@main/README.md |
| 9 | CUA-S1 System 1、源码 MIT、权重在 Hugging Face | ✅ 通过 | F-082 → F-148（官方 README） | https://cdn.jsdelivr.net/gh/trycua/cua@main/README.md |
| 10 | 权限三档 standard/bounded/unrestricted 与 `--dangerously-bypass-approvals` | ⚠️ 未获官方页核验（仅第二篇单源） | F-089~F-091 | — |
| 11 | 安装/沙箱/Lume/Driver 命令族 | ✅ 通过 | F-112~F-120 → F-148 | https://cdn.jsdelivr.net/gh/trycua/cua@main/README.md |
| 12 | `cua sb create ubuntu` 起 gVisor 容器而非虚拟机 | ✅ 通过 | F-113 → F-148 | https://cdn.jsdelivr.net/gh/trycua/cua@main/README.md |
| 13 | 榜单 v1：25 个 KiCad 任务、200 次操作、netlist 比对 | ✅ 通过 | F-097~F-100 → F-149 | https://cua.ai/cuabench/leaderboard |
| 14 | 名次与通过数 6/6/5/5/5/1（前五名与第 10 名） | ✅ 通过 | F-101~F-106 → F-149 | https://cua.ai/cuabench/leaderboard |
| 15 | `*`=function-calling；Claude 经 Bedrock；「每个完全通过的任务都是对已有原理图的修改」 | ✅ 通过 | F-107~F-109 → F-150 | https://cua.ai/cuabench/leaderboard |
| 16 | 许可分层 MIT / FSL-1.1-MIT / cua-perception AGPL-3.0-only | ⚠️ 口径差异（FSL 范围文中「音视频流」对应官方 streaming client/codecs/viewers，官方 wire protocol 仍 MIT；文中漏 Cua Driver Bench 亦为 FSL） | F-121~F-125 → F-144/F-145/F-146 | https://cdn.jsdelivr.net/gh/trycua/cua@main/README.md、https://cua.ai/ |
| 17 | 废弃包与 cuabot 安全警告措辞 | ✅ 通过 | F-126/F-127 → F-147 | https://cdn.jsdelivr.net/gh/trycua/cua@main/README.md、https://cua.ai/docs/cua-sdk/guides/migrate-from-deprecated-packages |
| 18 | Cua Fleets 单价 CPU $0.044625/vCPU/小时、内存 $0.0223125/GiB/小时 | ⚠️ 未获官方页核验（仅第二篇单源） | F-132 → F-153 | https://cua.ai/docs/concepts/sandbox-lifecycle（间接） |
| 19 | 采用者 Hermes、Clicky、H Company、Factory Droid | ⚠️ 未获官方页核验（仅第二篇单源） | F-131 | — |
| 20 | Cua Spaces 个人免费 | ✅ 通过 | F-133 → F-151 | https://cua.ai/ |

**计数：✅ 通过 14 项，⚠️ 时点/口径差异或未核验 6 项，❌ 失败 0 项。**

> **未核验项如实呈现**：第 10、18、19 项（F-089~F-091 权限三档命名与 `--dangerously-bypass-approvals`、F-132 Cua Fleets 单价、F-131 采用者名单）在可达官方页**未检出逐字依据**，仅为第二篇单源，按原样呈现，不作提升；F-154 另记「第二篇正文无法经 WebFetch 提取、以 PowerShell 抓取 HTML 替代」这一提取限制。

## 7. 跨信源对账（第一篇 vs 第二篇）

> 对账对象：第一篇（[article-source.md](article-source.md) F-001~F-065，2026-09-26）与第二篇（[second-article-facts.md](second-article-facts.md) F-066~F-154，2026-10-08）在同一知识束内的表述差异。共 **4 条**，每条按「现象—差异—影响—处置」四元组登记。

### 对账 ①：模块命名 —— 第一篇「Fleets」vs 第二篇「Cua Spaces / sandbox」

- **现象**：第一篇五模块含 `Cua Fleets`（隔离云桌面集群，F-011）；第二篇六组件把对应位置写作 `Cua Spaces`，并在命令族中使用 `cua sb`（sandbox 沙箱）。
- **差异**：三个名称指向不同对象——`Cua Spaces` = macOS 桌面 App / 共享桌面产品线（source-available，FSL-1.1-MIT）；`Cua Fleets` = 托管云桌面集群付费服务（按用量计费，官方 SDK 中的 `Pool`/`@trycua/fleet`）；`sandbox`（`cua sb`）= gVisor 沙箱本地运行时。
- **影响**：若沿用单一名词，会把「本地沙箱 / 自有机器 Space / 托管 Fleet 池」三类资源混为一谈，F-011 与 F-079 有被误读为同一组件的风险；成本与许可结论随之错位（Fleets 付费、Spaces 个人免费、sandbox 开源 MIT）。
- **处置**：在正文与概念页按「三类资源」并列呈现，标注各自许可与计费；保留第一篇 F-011 原编号，不改写，仅补注第二篇对应名称为 Cua Spaces / sandbox。

### 对账 ②：接口命名 —— 第一篇「Sandbox SDK」vs 第二篇「Cua SDK 与 CLI（四语言）」

- **现象**：第一篇称云端与本地区共享 `Sandbox SDK`（F-011/F-036/F-037）；第二篇称 `Cua SDK 与 CLI`，提供 Python/TypeScript/Swift/Kotlin 四种语言接口（F-081）。
- **差异**：`Sandbox SDK` 是 `cua` SDK 中面向沙箱生命周期的高层子集（官方文档 `Sandbox SDK reference` 仍在使用该标题，见 F-152）；`Cua SDK 与 CLI` 是整体产品名，其 Rust 核心 + 四语言绑定由官方 README 的 Packages 表确认（F-148）。
- **影响**：两名称并非替代关系而是包含关系；若视作改名，会遗漏「同一 API 在本地与 Fleet 之间迁移」这一第一篇核心结论（F-037）。
- **处置**：正文采用「Cua SDK（含 Sandbox SDK 子集与四语言绑定）」的总分表述，两篇编号各自保留。

### 对账 ③：主语言 —— 第一篇快照 HTML vs 第二篇 Rust（约 47%）vs GitHub API 当前值

- **现象**：第一篇 2026-09-20 快照称主语言标记 HTML（F-026）；第二篇称以 Rust 为主、约占代码量 47%（F-073）；本轮 2026-10-16 GitHub API `language` 字段为 Rust，languages API 计算 Rust 字节占比 42.31%（F-141/F-142）。
- **差异**：GitHub 主语言字段按仓库字节占比动态变化，属时点口径；两篇文章的百分比口径（47%）与当前实测（42.31%）存在差距。
- **影响**：主语言与占比不能作为稳定事实引用，缺少时点会误导读者。
- **处置**：三版数值并列并标注各自时点与口径；正文以「Rust 为当前主语言」表述，占比仅作时点参考。

### 对账 ④：Stars 四版快照 —— 24,432 / 29,189 / 「2.8 万」/ 29,926

- **现象**：第一篇 2026-09-20 快照 24,432（F-016）；2026-10-10 API 29,189（F-055）；第二篇本文称「超过 2.8 万」（F-071）；本轮 2026-10-16 API 29,926（F-140）。
- **差异**：均为同一仓库不同时点的快照；第二篇「2.8 万」是作者约数，相对其发布日（2026-10-08）前后的实测水平偏低。
- **影响**：若把任一行销数当现值，会低估项目动量；跨文档引用易产生陈旧数据。
- **处置**：正文统一采用「时点 + 数值」格式，给出 2026-10-16 现值 29,926 作为当前口径，其余三版作为历史时点登记。

## 8. 新增权威来源（第二轮）

| 来源 | URL | 用途 |
|------|-----|------|
| 第二篇文章 | https://mp.weixin.qq.com/s/vEGTwWZ8Mws2fwAQyvm0Yg | 第二信源事实与观点（F-066~F-139） |
| 官方 README（main，jsDelivr 镜像） | https://cdn.jsdelivr.net/gh/trycua/cua@main/README.md | 六组件、四语言 SDK、gVisor 语义、许可分层、废弃包与 cuabot 警告 |
| Cua-Bench EDA Leaderboard | https://cua.ai/cuabench/leaderboard | 榜单 v1 任务数/步数/netlist 判分、名次与 `*` 口径 |
| Cua 官网首页 | https://cua.ai/ | Cua Spaces 许可（FSL-1.1-MIT）、macOS 26+、个人免费 |
| Cua 官方文档中心 | https://cua.ai/docs | 文档导航与 Sandbox SDK reference（F-152） |
| 官方文档：从废弃包迁移 | https://cua.ai/docs/cua-sdk/guides/migrate-from-deprecated-packages | 废弃清单（含 cuabot）与措辞 |
| 官方文档：Sandbox lifecycle | https://cua.ai/docs/concepts/sandbox-lifecycle | Fleet 池 warm capacity 与费用（F-153 间接） |