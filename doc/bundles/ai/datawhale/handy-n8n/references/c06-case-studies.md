---
type: reference
title: "C06 n8n 案例分享"
bundle: /datawhale/handy-n8n
description: "两个实战案例：GitHub Trending 每日邮件推送、GitHub Issue 飞书机器人通知"
source: https://github.com/datawhalechina/handy-n8n/blob/main/c06/README.md
path: c06/README.md
tags: [cases, github, webhook, schedule, notification]
status: stable
---

# C06 n8n 案例分享

## 信源信息

- **文件路径**：`c06/README.md`
- **GitHub**：https://github.com/datawhalechina/handy-n8n/blob/main/c06/README.md
- **sidebar 标题**：C06 - n8n 案例分享

## 内容概要

本章提供两个实战案例，将前面章节所学的触发器、核心节点、通知集成等知识综合应用。

## 案例一：GitHub Trending 每日推送

- **工作流文件**：`workflows/c06/github-trending.json`
- **触发方式**：Schedule Trigger（定时任务）
- **流程**：每天定时获取 GitHub Trending 数据 → 通过邮件发送给指定用户
- **可推广性**：
  - 信息源可替换为 RSS 等
  - 通知渠道可替换为飞书、企业微信、Slack 等

## 案例二：GitHub Issue 通知

- **工作流文件**：`workflows/c06/github-issue-notify.json`
- **触发方式**：GitHub Webhook 事件
- **流程**：监听 GitHub Issue 事件 → 新 Issue 创建时 → 通过飞书机器人发送通知
- **关键点**：GitHub 仓库 Webhook 配置指向 n8n Webhook URL，工作流需 Active 状态

## 学习价值

这两个案例分别代表了 n8n 最常见的两种自动化模式：

1. **定时拉取型（Schedule + HTTP Request）**：主动定期获取数据并推送，适用于日报、监控、数据同步
2. **事件驱动型（Webhook + 通知）**：被动接收外部事件并响应，适用于告警、通知、实时集成

## 对应概念

- [工作流设计](../concepts/workflow-design.md)——Schedule Trigger 和 Webhook Trigger
- [高级实战](../concepts/advanced-practice.md)——案例整合
- [GitHub Trending 每日推送示例](../examples/github-trending-digest.md)
- [GitHub Issue 飞书通知示例](../examples/github-issue-notify.md)
