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