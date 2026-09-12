---
okf_version: "0.2"
type: concept
title: 产品定位与演进
description: ToDesk AI 的产品定位、与远控母体的关系、版本演进时间线与文档信源说明（F-001 至 F-006）
tags: [todesk-ai, product-overview, computer-use]
generated:
  by: codearts/glm-5.3-flash
  at: "2026-09-12T11:30:00+08:00"
sources:
  - id: tencent-doc
    url: https://doc.weixin.qq.com/doc/w3_Ae4AJgaPAJMCNi7xCQuo2SaelthS2?scode=AFcAOAfiAAYfXS6XpeARIAFAZkABY
  - id: todesk-official
    url: https://www.todesk.com/
---

# 产品定位与演进

## 一句话定位

ToDesk AI 是 ToDesk（远程控制软件）旗下的 AI 助手产品（F-001/F-004），官方定义为"深度融合大模型能力与视觉理解技术的智能 AI 助手"——用户以一句话下达任务，产品自主规划并执行，最终交付可验收的结果（F-001）。官网将其表述为"帮你自动完成工作的 AI 助手"（F-004）。

## 与传统 AI 助手的差异化

原文将差异化锚定在两点（F-002）：

1. **从"对话"到"操控"**：产品搭载 Computer Use 能力，通过屏幕视觉感知、以可视化 GUI 方式模拟真人的键盘与鼠标操作，让目标电脑"被看懂、被操控"——而不是停留在单一设备内的问答。
2. **从"单机"到"跨设备"**：指令发出不受设备限制，用户随时随地用手机或电脑下达任务，AI 自动在目标电脑上跨设备执行。

## 产品演进时间线

更新日志（原文未注年份，按版本号序列推断属 2025—2026 年，见 [verification.md 勘误-2](../references/verification.md)）呈现的关键节点（F-003/F-005）：

| 时点（原文口径） | 版本 | 关键变化 |
|------|------|---------|
| 4月4日 | 2.1.0 | 新增切换模型（Kimi K2.5、Minimax M2.7、Doubao 2.0 pro 等）与企业微信机器人接入 |
| 4月17日 | — | 多智能体上线；模型管理与计费中心（支持自定义接入第三方模型 API）；审计日志优化 |
| 4月28日 | 4.8.8.6 | 智能交互问答弹窗；Node 节点文件搜索增强；长对话稳定性优化 |
| 5月20日 | 3.0.0.0 | **ToClaw 更名 ToDesk AI**，全新 PC 应用发布；批量权限设置 |
| 5月28日 | 3.0.0.2 | 新增 AI 记忆能力（记住用户习惯与偏好）；多任务连接 |
| 6月9日 | 3.0.0.3 | 全新移动应用发布 |
| 6月25日 | 3.0.0.5 | AI 悬浮球消息通知；黑屏/隐私屏模式下仍支持远程操控 |
| 7月6日 | 3.0.0.6 | Mac 系统最低支持版本调整至 macOS 10.15 |

> 演进脉络小结：产品以"模型切换 → 多智能体 → 自定义模型计费 → AI 记忆 → 移动端"的节奏，从单助手工具演进为可编排、可记忆、跨端的 Agent 平台。

## 信源与文档形态说明

本 bundle 的事实源为官方产品文档（企业微信文档分享页，"外部/只能查看"），页面字数标注 9184 字（F-006）。原文属官方一手信源，事实采集与核验过程见 [references/article-source.md](../references/article-source.md) 与 [references/verification.md](../references/verification.md)。

## 主题关联

- [EchoBird 百灵鸟 AI Agent 桌面管理工具](../../echobird/index.md)：同为桌面端 AI Agent 工具，视角互补（模型枢纽 vs 远程操控）
- [MiniTap 官方文档教程](../../minitap/index.md)：同属"官方文档 → OKF 教程"形态的产品学习束