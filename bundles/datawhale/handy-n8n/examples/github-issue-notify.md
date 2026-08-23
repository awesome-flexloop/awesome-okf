---
type: example
title: "GitHub Issue 飞书通知"
bundle: /datawhale/handy-n8n
description: "C06 案例：通过 Webhook 监听 GitHub Issue 事件，当有新 Issue 创建时通过飞书机器人发送通知"
sources: https://github.com/datawhalechina/handy-n8n/blob/main/c06/README.md
related:
  - /datawhale/handy-n8n/concepts/workflow-design
tags: [webhook, github, feishu, notification]
status: stable
---

# GitHub Issue 飞书通知

## 概述

本示例对应 handy-n8n 第六章案例二，工作流 JSON 位于 `workflows/c06/github-issue-notify.json`。通过监听 GitHub Issue 事件，当有新 Issue 创建时自动通过飞书机器人发送通知。这是典型的**事件驱动型自动化**——外部系统通过 Webhook 触发 n8n 工作流。

## 工作流结构

```
Webhook Trigger（接收 GitHub 事件）
  → If（判断是否为新 Issue 事件）
  → 数据处理（提取 Issue 标题、作者、链接等）
  → HTTP Request（调用飞书机器人 Webhook 发送通知）
```

## 关键节点

### Webhook Trigger
- 配置 HTTP 方法为 POST
- GitHub 仓库 Settings → Webhooks → Add webhook
  - Payload URL 填入 n8n Webhook 的正式 URL（工作流需 Active）
  - Content type 选择 `application/json`
  - 选择 "Let me select individual events" → Issues
- n8n 测试 URL 路径含 `webhook-test`，正式 URL 需工作流激活后使用

### 事件过滤
- GitHub Issues 事件包含 opened、edited、closed 等多种 action
- 使用 If 节点判断 `{{ $json.action }}` 是否等于 `opened`，仅在新 Issue 创建时通知

### 飞书通知
- 在飞书群中添加自定义机器人，获取 Webhook URL
- 使用 HTTP Request 节点 POST 飞书机器人 Webhook
- 请求体格式：
```json
{
  "msg_type": "interactive",
  "card": {
    "header": { "title": { "tag": "plain_text", "content": "New GitHub Issue" } },
    "elements": [
      { "tag": "div", "text": { "tag": "lark_md", "content": "**标题**: {{ $json.issue.title }}\n**作者**: {{ $json.issue.user.login }}\n[查看 Issue]({{ $json.issue.html_url }})" } }
    ]
  }
}
```

## 配置要点

1. **Webhook 响应模式**：建议使用 Immediately 模式，GitHub 不需要等待工作流完成
2. **安全考虑**：可在 Webhook 配置中设置 Secret，n8n 端验证 GitHub 签名
3. **工作流必须 Active**：正式 Webhook URL 仅在工作流激活时响应，否则返回 404

## 扩展思路

- **多平台通知**：同时发送飞书、邮件、Slack 通知
- **智能路由**：根据 Issue 标签/内容自动分配给不同团队成员
- **AI 预处理**：接入 AI Agent 对 Issue 进行自动分类、摘要、优先级判断
- **自动回复**：对常见问题 Issue 自动回复 FAQ

## 学习要点

1. Webhook Trigger 是 n8n 与外部系统事件集成的核心方式
2. 测试 URL 和正式 URL 的区别——测试时 Listen for test event，生产需 Active 工作流
3. 事件驱动架构：n8n 作为事件消费者，外部系统作为事件生产者

## 延伸阅读

- [工作流设计](../concepts/workflow-design.md)——Webhook Trigger 详解
- [GitHub Trending 每日推送](github-trending-digest.md)——定时触发型案例
- [C06 n8n 案例分享](../references/c06-case-studies.md)——完整信源
