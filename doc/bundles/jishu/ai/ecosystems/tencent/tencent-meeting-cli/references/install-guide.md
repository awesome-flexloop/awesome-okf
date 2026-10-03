---
type: Reference
title: "腾讯会议 CLI 安装指南信源"
description: "面向 AI Agent 的官方安装指南页：CLI 与 Skill 两步安装、Node.js 版本要求、安装后重启与 auth status 验证、一句话提示词。"
tags: [tencent-meeting, tmeet, reference, install-guide, skill-setup]
generated: { by: "reference_agent/trae-solo", at: "2026-10-03T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-03T00:00:00Z" }
status: stable
stale_after: 2027-04-03
sources:
  - id: install-guide
    resource: https://meeting.tencent.com/wemeet-tapi/v2/oauth2/oauth/cli-install-guide?ch=web
    title: 腾讯会议 CLI 安装指南（面向 AI Agent）
---

# 腾讯会议 CLI 安装指南信源

## 信源元信息

| 项目 | 内容 |
|------|------|
| 信源 ID | install-guide |
| URL | https://meeting.tencent.com/wemeet-tapi/v2/oauth2/oauth/cli-install-guide?ch=web |
| 类型 | 官方安装指南（带 `ch=web` 渠道参数） |
| 抓取日期 | 2026-10-03 |
| 对应事实 | F-012、F-013、F-019、F-020 |

## 安装步骤（页面口径）

1. **安装 CLI**：`npm install -g @tencentcloud/tmeet`；
2. **安装 Skill（标注为必需）**：`npx skills add TencentCloud/tencentmeeting-cli -y -g`（F-012）；
3. **重启 AI 工具**：配置完成后重启，确保 SKILL 完整加载；随后运行 `tmeet auth status` 验证（F-019）。

## 环境要求

- Node.js >= 14（F-013）。

> 口径差异：腾讯云文档正文写 Node.js ≥ 16（F-015），package.json engines 为 `>=14`（F-014）。三处并列登记，建议用 LTS。

## 一句话安装提示词

页面提供可复制的引导语，让用户直接发给 AI 助手完成安装（F-020）：

> 帮我安装腾讯会议CLI，链接地址：https://meeting.tencent.com/wemeet-tapi/v2/oauth2/oauth/cli-install-guide?ch=web

该页面本身的设计用途就是「AI 可读的安装说明书」——Agent 访问该页后按步骤执行安装与验证。
