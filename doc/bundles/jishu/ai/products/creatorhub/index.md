---
okf_version: "0.2"
type: bundle
title: "🎬 CreatorHub 多平台内容运营本地面板"
description: "微信博文经 OKF v0.2 七阶段转化——Python/FastAPI 本地面板，统一管理抖音/小红书/快手/视频号：监控·采集·下载·发布·自动回复，Chrome CDP/Patchright 浏览器后端、SQLite + 独立 Profile、conservative 风控与任务队列；含安装/上手实操与 23 项核验（14✅/7⚠️/2❌）"
tags: [creatorhub, self-media, multi-platform, content-operations, douyin, xiaohongshu, kuaishou, channels, fastapi, patchright, playwright, local-first, 博文转化]
generated:
  by: seven-concepts-cmd+blog-article-to-okf-wiki
  at: "2026-10-26T10:40:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-26T10:40:00+08:00"
status: flagged
stale_after: 2027-01-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/Y5AvYGtyj2t9xPJIXuSYBA
  - id: github-repo
    url: https://github.com/3441293738/creatorhub
  - id: github-api
    url: https://api.github.com/repos/3441293738/creatorhub
  - id: official-readme
    url: https://raw.githubusercontent.com/3441293738/creatorhub/main/README.md
  - id: official-requirements
    url: https://raw.githubusercontent.com/3441293738/creatorhub/main/requirements.txt
  - id: official-changelog
    url: https://raw.githubusercontent.com/3441293738/creatorhub/main/CHANGELOG.md
---

# 🎬 CreatorHub 多平台内容运营本地面板

> **类型**：终端产品拆解 + 可照做上手教程（操作可复现性两问皆“是”）
> **信源**：微信公众号「明见如是」博文《发现一个自媒体效率神器：CreatorHub，一个本地面板，把抖音小红书快手视频号全管了》（2026-08-28）→ 2026-10-26 经 GitHub API、README、requirements.txt、CHANGELOG、git tree 逐项核验
> **核验结论**：23 项 P0/P1 声明 **14✅ / 7⚠️ / 2❌**
> **状态**：`flagged`——功能核心（本地运行、四平台接入、监控/采集/下载/发布、本地数据）全部成立；**“开源”许可声明不成立**（仓库无 LICENSE），属使用边界核心声明，故标记 flagged
> **数据时点**：Star/Fork/Issue 为 2026-10-26 快照；功能口径为 main 分支 + 最新 Release v0.2.4（2026-10-16）

## 本文概要

[CreatorHub](https://github.com/3441293738/creatorhub) 是一个用 **Python + FastAPI** 编写的**本地 Web 内容运营面板**，把抖音、小红书、快手、视频号的账号管理、作品/评论监控、关键词批量采集、内容下载、发布与跨平台转发、自动评论/回复与通知收进一个界面。它用**系统 Chrome CDP 或 Patchright**（Playwright 兼容分支）驱动真实浏览器，按账号隔离 Profile；数据落在本地 `data/`（SQLite + 媒体 + 登录态），任务统一进入持久化队列，默认 `conservative` 风控（同账号写操作共享间隔与额度、同出口串行、冷却阶梯、出口组熔断）。项目 2026-07-03 创建，2026-10-26 已 2,562 Star、472 Fork、6 个 Release，并自 v0.2.0 起提供 Windows 安装版。

需要先讲清三个边界：**视频号只支持本账号数据**，不能监控/下载他人作品；仓库**没有 LICENSE 文件**，公开可读不等于可自由分发/商用；**自动评论、私信、发布受平台风控与规则约束**，工具降低操作成本，不豁免平台责任。

## 阅读路径

**先建立概念（约 25 分钟）**

1. [CreatorHub 是什么：项目身份与时间线](concepts/00-what-is-creatorhub.md)——定位、作者仓库、Star/版本、许可状态、博文与官方口径差异
2. [本地优先架构：FastAPI + 浏览器后端 + SQLite](concepts/01-local-first-architecture.md)——四层结构、CDP/Patchright、Profile 隔离、数据目录
3. [四平台能力矩阵与功能边界](concepts/02-platform-capability-matrix.md)——登录/采集/监控/弹幕/下载/发布/自动回复/本账号，视频号限制
4. [任务队列与保守风控模型](concepts/03-task-queue-and-risk-control.md)——统一队列、写操作额度、冷却阶梯、代理与出口组熔断
5. [许可、合规与安全边界](concepts/04-boundaries-license-and-compliance.md)——无 LICENSE 的法律含义、平台 ToS、账号风险、赞助商披露

**再动手实操**

6. [Windows 安装版：双击安装与首次启动](examples/00-windows-install.md)
7. [源码运行：环境、启动与自检](examples/01-source-run.md)
8. [添加账号、作品/评论监控与关键词采集](examples/02-accounts-monitoring-and-collection.md)
9. [下载、发布、跨平台转发与分享链接下载](examples/03-download-publish-and-transfer.md)

## 核心事实速查

| 项 | 值 |
|----|-----|
| 仓库 / 形态 | [3441293738/creatorhub](https://github.com/3441293738/creatorhub)，本地 Web 面板（个人开发者仓库） |
| 创建 / 最近推送 | 2026-07-03 / 2026-10-26（高频迭代） |
| 社区数据 | Star **2,562**、Fork **472**、开放 Issue **14**（**2026-10-26 快照**；博文 08-28 口径 1.7k） |
| 许可 | **无 LICENSE 文件，API license=null** → 默认版权保留（source-available，非 OSI 开源） |
| 技术栈 | Python 3.10+ · FastAPI 0.115.6 · Patchright 1.61.2（Playwright 兼容 API）· SQLite · 原生 JS 前端 |
| 浏览器后端 | 系统 Chrome CDP（小红书默认 auto）/ Patchright；非小红书可选 fingerprint-chromium |
| 支持平台 | 抖音、小红书、快手、视频号（视频号仅本账号数据） |
| 主要能力 | 作品/评论/弹幕监控 · 关键词批量采集 · 内容下载 · 多平台发布与转发 · 自动评论/回复 · 通知 · 任务队列 · 风控中心 |
| 数据位置 | `data/creatorhub.db` + `data/media/` + `data/profiles/`；`config.yaml` 本地生成，默认不入 Git |
| 安装 | Windows 10/11 x64 安装包（v0.2.0+）；源码 `start.cmd` / `start.sh`；首次自动装依赖与 Chromium |
| 版本 | v0.2.4（2026-10-16，最新）；共 6 个 Release |

## ⚠️ 阅读前必知的六条口径勘误

1. **“开源”不成立（核心勘误）**：仓库公开但**无 LICENSE**，GitHub license 字段为 null，默认版权保留；可阅读、可自部署不等于可复制、分发或商用。引用或二次开发前须取得作者授权（F-023/F-065）。
2. **Playwright → Patchright**：源文写“Python + FastAPI + Playwright”；官方依赖为 `patchright==1.61.2`（Playwright 兼容分支），浏览器后端优先系统 Chrome CDP，业务层使用兼容 Playwright 的 API（F-031/F-062）。
3. **视频号不是“全管”**：仅支持创作者助手本账号的作品/数据/评论，**不支持监控或下载他人作品**，无关键词采集、无自动评论；标题的“全管了”属夸大（F-045/F-064）。
4. **Windows 已可双击安装**：源文 08-28 称“不是双击就完事”；v0.2.0（09-14）起提供安装包，Win10/11 x64 双击即装。源码运行仍需 Python 与浏览器组件（F-054/F-063）。
5. **“统一发到多个平台”应收窄**：官方是各平台分别发布（抖音/快手/视频号走对应创作平台，小红书面板内发布）+ 已下载内容跨平台转发，README 未声明一次提交自动分发全平台（F-042/F-066）。
6. **Star 是动态值**：源文 1.7k（08-28）与官方 2,562（10-26）不矛盾，但引用必须带时点（F-021/F-061）。

## 采用提示与已知边界

- **本知识包未实机复跑**：examples 的步骤逐字来自官方 README，环境要求与命令可核验；但真实登录、采集、发布依赖账号、网络、平台风控与实机桌面环境，未在本地复现。首次使用请用小号、小规模验证。
- **合规红线**：项目 README 明确“用于技术学习和个人内容管理”，不提供账号/Cookie/代理/平台数据；使用者须自行遵守平台规则与所在地法律，尊重版权与隐私（F-059）。自动评论、私信、批量采集可能触发平台风控或违规，风险由使用者承担。
- **凭据安全**：登录态保存在本机 `data/profiles/`，仍属高敏数据；备份、迁移、共享设备时须按凭据处理。项目未提供独立安全审计（F-067）。
- **商业披露**：README 含住宅代理赞助商 IPWO（含推广码）。赞助关系不改变功能事实，但选型时应注意“中立性”边界（F-060）。
- **供应风险**：个人维护项目、平台页面/接口高频变化，脚本可能随平台改版失效；升级前备份 `config.yaml` 与 `data/`（F-059）。

## 主题关联

- [🎬 OpenCreator 本地优先创作者 AI 工作台](../opencreator/index.md)——同为本地优先创作者工具：OpenCreator 偏 AI 生成与 Codex 执行，CreatorHub 偏多平台账号运营与分发。
- [VidBee 视频下载与本地转录](../vidbee/index.md)——同属“内容获取/本地处理”工具；VidBee 聚焦下载与转录，CreatorHub 聚焦多平台监控与发布。
- [🔎 wigolo 本地 Web 情报层](../wigolo/index.md)——同为本地 Web 工具 + 博文核验先例，可对照“本地优先”的架构与边界写法。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
log
```
