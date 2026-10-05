---
type: Reference
title: "腾讯会议 CLI 产品首页信源"
description: "meeting.tencent.com 官方产品页的事实登记：产品标语、兼容 Agent、业务场景、安装入口与 npm 常见问题。"
tags: [tencent-meeting, tmeet, reference, product-page, official-site]
generated: { by: "reference_agent/trae-solo", at: "2026-10-03T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-03T00:00:00Z" }
status: stable
stale_after: 2027-04-03
sources:
  - id: product-page
    resource: https://meeting.tencent.com/meeting-cli/index.html
    title: 腾讯会议 CLI 产品首页
---

# 腾讯会议 CLI 产品首页信源

## 信源元信息

| 项目 | 内容 |
|------|------|
| 信源 ID | product-page |
| URL | https://meeting.tencent.com/meeting-cli/index.html |
| 类型 | 官方产品首页 |
| 抓取日期 | 2026-10-03 |
| 对应事实 | F-002、F-005、F-006、F-007、F-011、F-016、F-018、F-020、F-031 |

## 产品定位

首页标语为「一行指令，让 AI 为你管理腾讯会议」，定位为让 AI 直接管理会议、覆盖会议核心业务域的命令行工具（F-002）。

## 兼容的 AI Agent

- 首页主体列出：WorkBuddy、DeepSeek Harness、Claude Code、Codex、Cursor、GitHub Copilot（F-005）。
- FAQ 安装章节另称 CLI-Skill 可与 Claude Code、Cursor、Codex、OpenClaw 等 AI 工具集成（F-006）。

## 宣传业务场景

- **教育培训**：批量排课、课程整理、错题溯源；
- **销售面客**：会前对齐要点、会后复盘；
- **办公协作**：会议冲突检查、会议章程管理、纪要待办整理（F-007）。

## 安装入口

首页提供 npm 全局安装命令 `npm install -g @tencentcloud/tmeet`（F-011），并支持 macOS/Linux/Windows（F-018）。

## npm 常见问题（FAQ）

- `npm: command not found`：前往 Node.js 官网安装 LTS 版本（自带 npm）；
- 安装后命令不可用：检查 npm 全局 bin 目录在 PATH 中、安装后重启终端（F-016）。

## 一句话安装提示词

首页与安装指南均提供可直接发给 AI 助手的提示词（F-020）：

> 帮我安装腾讯会议CLI，链接地址：https://meeting.tencent.com/wemeet-tapi/v2/oauth2/oauth/cli-install-guide?ch=web

## 安全提示

首页提示凭证本地加密存储、怀疑泄露时立即登出并到账号安全中心处理（与 F-024、F-031 一致）。
