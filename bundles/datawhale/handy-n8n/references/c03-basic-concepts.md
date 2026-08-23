---
type: reference
title: "C03 n8n 基本概念"
bundle: /datawhale/handy-n8n
description: "平台介绍、触发器节点（Manual/Schedule/Webhook/Chat）、核心节点（数据处理/控制流/HTTP）、代码节点（表达式与 Code）"
source: https://github.com/datawhalechina/handy-n8n/blob/main/c03/README.md
path: c03/
tags: [workspace, triggers, core-nodes, code, expressions]
status: stable
---

# C03 n8n 基本概念

## 信源信息

- **文件路径**：`c03/README.md`（含 4 个子文档）
- **GitHub**：https://github.com/datawhalechina/handy-n8n/blob/main/c03/
- **sidebar 标题**：C03 - n8n 基本概念

## 内容概要

本章系统介绍 n8n 的基本概念，是全书的核心基础章节，涵盖四个主题。

## 子文档

### n8n 平台介绍（`n8n-workspace.md`）
- 注册账户（本地/云主机/HF Space 部署后首次访问需注册）
- 界面介绍：工作流运行统计、工作流列表、凭据列表、执行列表
- 工作流导入：复制 JSON 粘贴（Ctrl+V）/ Import from URL
- 工作流不会自动保存，需手动 Save
- **数据结构**：节点间使用对象数组传递，每项含 `json`（文本）和 `binary`（Base64 二进制）字段，n8n 自动逐项处理

### n8n 触发器节点（`n8n-trigger-nodes.md`）
- **Manual Trigger**：手动触发，用于测试
- **Schedule Trigger**：定时触发，支持间隔和 Cron，时区配置（全局/工作流级），输出时间信息
- **Webhook Trigger**：接收 HTTP 请求，支持路径参数和查询参数，三种响应模式（Immediately/When Last Node Finishes/Respond to Webhook），测试 URL 与正式 URL 区别
- **Chat Trigger**：聊天触发器，需连接 Agent/集群节点，支持 Hosted Chat 公开访问模式

### n8n 核心节点（`n8n-core-nodes.md`）
- **数据处理节点**：Edit Fields（变量赋值，Manual Mapping/JSON Output）、Split Out（数组拆分）
- **控制流节点**：If（条件判断，多条件 AND/OR）、Merge（合并：Append/Combine/SQL Query/Choose Branch）、Loop（批次循环）
- **HTTP 请求节点**：通用 REST API 连接器，可附加到 AI Agent 作为工具

### n8n 中的代码（`n8n-code.md`）
- **Expressions 表达式**：`{{ }}` 包裹的 JavaScript，tournament 模板引擎，单语句限制
- **Code 节点**：JavaScript/Python 双语，两种模式（Run Once for All Items / Each Item），Python 通过 pyodide 执行
- **内置变量**：`$input`/`$json`/`$now`（JS），`_input`/`_json`/`_now`（Python）
- **外部库**：JS 需配置 `NODE_FUNCTION_ALLOW_EXTERNAL`，Python 通过 pyodide 内置库自动下载
- **安全限制**：Code 节点禁止文件系统访问和 HTTP 请求

## 配套工作流

`workflows/c03/` 目录下 7 个 JSON 文件：test.json、node_manual_trigger.json、node_schedule_trigger.json、node_webhook_trigger.json、node_chat_trigger.json、n8n_node_demo.json、n8n_code_node.json。

## 对应概念

- [工作流设计](../concepts/workflow-design.md)——触发器与核心节点编排
- [数据处理与转换](../concepts/data-processing.md)——表达式、Code 节点、数据结构
