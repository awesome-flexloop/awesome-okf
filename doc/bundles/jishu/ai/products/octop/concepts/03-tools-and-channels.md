---
okf_version: "0.2"
type: Concept
title: "Octop 工具调用与多渠道接入"
description: "Octop 的 Browser AI+、Terminal AI+、远程桌面、ACP 双向集成，以及 Web/IM/HTTP/SSE/WebSocket 多渠道与定时任务（能力层）"
tags: [octop, browser-automation, terminal, remote-desktop, acp, mcp, im-channel, websocket, apscheduler]
generated: { by: "blog-article-to-okf-wiki:E", at: "2026-10-10T09:45:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: "https://mp.weixin.qq.com/s/kskjE8iQ2AxtI_Skqz5fvg"
  - id: official-home
    url: "https://tencentcloud.github.io/Octop/"
  - id: pypi
    url: "https://pypi.org/project/octop/"
---

# Octop 工具调用与多渠道接入

> 能力层（How to use the tools & channels）。本文介绍 Octop 让 AI「不只回答问题，还能做事」的工具执行能力，以及多渠道接入与定时调度的交互方式。

## 工具调用：让 AI 真正执行操作

Octop 没有把 AI 局限在文本生成，而是集成了浏览器自动化、终端操作、远程桌面与外部工具连接能力——**Agent 在获得相应权限后执行实际操作**（F-020）。

### Browser AI+（浏览器自动化）

基于 Chromium 浏览器自动化（`harness-browser`，F-008/F-037）：

- 操作网页、获取截图、处理表单、执行浏览器任务（F-021）。

### Terminal AI+（终端）

- 把 AI 辅助能力引入终端环境（F-022）。
- 用户可在 Web 控制台使用**交互式 Shell**，让 AI 帮助理解命令、排查问题或辅助执行操作（F-022）。

### 远程桌面

- 通过控制台查看和操作桌面会话（F-023）。
- 覆盖 **Linux、Windows、macOS**（F-023）。

## 对外协作：ACP（Agent Client Protocol）双向集成

对开发者，Octop 提供 **ACP 双向集成**（F-024）：

- **对外**：外部 IDE 或终端工具可经 ACP 使用 Octop Agent；
- **对内**：Octop 可将编程任务委托给 **OpenCode、Claude Code、Codex** 等外部编码 Agent；
- 意义：Octop 可以充当**统一任务入口**，将不同工作交给合适的工具完成，而不必独立实现所有开发能力（F-024，作者转述）。

另有 **MCP 连接器**（官方口径，F-039），对齐 Agent 工具生态主流接入方式。

## 多渠道接入

- **网页**：Web Dashboard（F-027）。
- **桌面客户端**（F-027）。
- **聊天平台**：飞书、钉钉、微信、QQ、企业微信等（F-027）。
- **程序化接口**：HTTP、SSE、WebSocket（F-027）。
- 统一由 `harness-gateway` 归一化处理入站消息（F-006/F-037）。

## 定时调度

- 配合 **APScheduler** 定时调度能力，可配置**周期性任务**，让 AI 在指定时间运行工作流程（F-028）。
- 这让 Octop 更接近「可长期运行的 AI 工作平台」而非「等待提问的聊天窗口」（F-028，作者转述）。

## 反模式与边界

- **工具权限 ≠ 无门槛执行**：Agent 需**获得相应权限**后才执行实际操作（F-020）；远程桌面/终端是敏感能力，应按最小权限原则配置（推断）。
- **多渠道 ≠ 无需平台接入**：飞书/钉钉等 IM 渠道通常需要对应平台的开放平台/机器人配置（推断，博文未展开细节）。
- **定时任务 ≠ 无运维**：长时运行依赖平台可访问性与工作空间持久化（推断）。

## 阅读下一篇

- [04 · 安装与快速上手](04-install-and-run.md)——安装、初始化、启动与首用配置
- [实操示例](../../examples/00-install-and-run.md)——可直接照做的安装启动流程