---
type: example
title: "GitHub Trending 每日推送"
bundle: /datawhale/handy-n8n
description: "C06 案例：通过 Schedule Trigger 定时获取 GitHub Trending 数据，并通过邮件发送给指定用户"
sources: https://github.com/datawhalechina/handy-n8n/blob/main/c06/README.md
related:
  - /datawhale/handy-n8n/concepts/workflow-design
tags: [schedule, github, email, automation]
status: stable
---

# GitHub Trending 每日推送

## 概述

本示例对应 handy-n8n 第六章案例一，工作流 JSON 位于 `workflows/c06/github-trending.json`。通过定时任务每天自动获取 GitHub Trending 数据，并通过邮件发送给指定用户。该模式可推广至其他信息源（如 RSS）和其他通知渠道。

## 工作流结构

```
Schedule Trigger（定时触发）
  → HTTP Request（获取 GitHub Trending 页面/API）
  → 数据处理（解析/格式化 Trending 信息）
  → Email Send（发送邮件日报）
```

## 关键节点

### Schedule Trigger
- 配置每日固定时间触发（如每天早上 9:00）
- 注意时区配置：私有化部署通过 `GENERIC_TIMEZONE`/`TZ` 环境变量，或在工作流 Settings 中单独设置时区

### 数据获取与处理
- 通过 HTTP Request 节点获取 GitHub Trending 数据
- 可使用 Code 节点解析 HTML/JSON 格式，提取仓库名、描述、星标数等信息
- 使用表达式或 Edit Fields 节点格式化邮件内容

### 邮件发送
- 配置 SMTP 凭据（如网易邮箱 smtp.163.com:465，需使用授权码）
- 邮件正文使用 HTML 格式，包含 Trending 仓库列表链接

## 扩展思路

- **信息源替换**：将 GitHub Trending 替换为 RSS 订阅、Hacker News、Product Hunt 等
- **通知渠道替换**：邮件 → 飞书机器人 / 企业微信 / Slack / Telegram
- **内容增强**：增加 AI 摘要节点，对 Trending 项目进行分类和总结
- **频率调整**：每日推送 → 每周周报，或根据关键词实时监控

## 学习要点

1. Schedule Trigger 的时区配置是定时任务的常见坑点
2. HTTP Request + Code 节点组合可处理任意网页数据抓取
3. 工作流激活后定时触发器才会按计划执行（测试时用 Manual Trigger）

## 延伸阅读

- [工作流设计](../concepts/workflow-design.md)——触发器与核心节点
- [GitHub Issue 飞书通知](github-issue-notify.md)——另一个 C06 案例，使用 Webhook 触发
- [C06 n8n 案例分享](../references/c06-case-studies.md)——完整信源
