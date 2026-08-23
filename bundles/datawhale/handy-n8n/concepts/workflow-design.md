---
type: concept
title: "工作流设计"
bundle: /datawhale/handy-n8n
description: "触发器节点（Manual/Schedule/Webhook/Chat）、核心节点（数据处理/控制流/HTTP）、节点连接与分支控制"
sources: https://github.com/datawhalechina/handy-n8n/blob/main/c03/README.md
related:
  - /datawhale/handy-n8n/concepts/getting-started
  - /datawhale/handy-n8n/concepts/data-processing
  - /datawhale/handy-n8n/concepts/ai-api-integration
  - /datawhale/handy-n8n/references/c03-basic-concepts
tags: [workflow, trigger, nodes, control-flow]
status: stable
---

# 工作流设计

## 核心理解

n8n 工作流由**节点（nodes）**和**连接（connections）**组成。节点是执行特定任务的小组件，连接定义数据在节点间的流向。任何工作流都需要一个**触发器节点（Trigger Node）**作为起始点，一个工作流可以有多个触发器。

节点分为两类：
- **Trigger 节点**：启动工作流，响应事件（手动、定时、HTTP 请求、聊天消息）
- **Action 节点**：执行具体任务（数据处理、HTTP 请求、条件判断等）

## 触发器节点

### Manual Trigger 手动触发器
最简单的触发器，无输入无输出，点击 Execute workflow 即可触发。主要用于测试和需要手动触发的场景。

### Schedule Trigger 定时触发器
支持多种定时策略：
- 分钟间隔、小时间隔、天间隔
- Cron 表达式配置（灵活的定时规则）

**时区注意事项**：
- 私有化部署通过 `GENERIC_TIMEZONE` 和 `TZ` 环境变量配置
- 官方 SaaS 在管理界面配置
- 单个工作流可在 Settings → Timezone 中覆盖全局时区

输出触发时间信息（timestamp、Readable date、Day of week 等）。

### Webhook Trigger Webhook 触发器
接收 HTTP 请求触发工作流，是 n8n 与外部系统集成的核心方式。

关键配置：
- **HTTP 方法**：GET/POST/PUT/DELETE 等
- **Path**：支持路径参数（`/:variable`、`/path/:variable`）和查询参数（`?p1=a&p2=b`）
- **Authentication**：鉴权方式
- **响应模式**：
  - Immediately：立即返回 `{"message":"Workflow was started"}`
  - When Last Node Finishes：返回最后节点的输出
  - Using Respond to Webhook：自定义响应内容

测试 URL 路径含 `webhook-test`（访问一次后失效，需重新 Listen），正式 URL 无 `test`。

高级配置包括 CORS、IP 白名单、Raw Body、Binary 数据字段等。

### Chat Trigger 聊天触发器
用于聊天机器人和对话式交互工作流，需连接 Agent 节点或集群节点。

- 可视为特殊的 Webhook 触发器
- 支持非公开（工作区内测试）和公开访问（Hosted Chat 模式）
- 公开 URL 仅在工作流 Active 时可用，否则返回 404
- 每次用户发送消息触发一次工作流（SaaS 版本注意配额）

## 核心节点

### 数据处理节点（Data Transformation）

#### Edit Fields 变量赋值节点
更改已有数据或添加新数据，支持两种模式：
- **Manual Mapping**：手动指定字段名和值
- **JSON Output**：通过 JSON 表达式输出

```javascript
// JSON 输出模式示例：生成长度为10的随机数组
{
  "number": {{ Array.from({ length: 10 }, (_) => Math.floor(Math.random() * 100)) }}
}
```

#### Split Out 数据拆分节点
将包含数组字段的数据拆分为多项。Include 配置控制其他字段的保留方式：
- No Other Fields：不保留
- All Other Fields：全部保留
- Selected Other Fields：指定保留

### 控制流节点（Flow）

#### If 条件判断节点
根据比较操作拆分工作流为 True Branch / False Branch。
- 支持 String、Number、Boolean、Array、Object 等数据类型的比较
- 支持多条件组合，AND/OR 逻辑运算

#### Merge 数据合并节点
等待所有上游节点数据可用后合并，四种模式：
1. **Append**：追加，保留所有数据项
2. **Combine**：基于 Combine By 选项决定合并规则
3. **SQL Query**：使用 SQL 语言合并
4. **Choose Branch**：选择输入 1 或输入 2，或输出空项

典型场景：合并多个网页内容后提交 AI 节点总结。

#### Loop 循环节点
默认情况下 n8n 自动逐项处理输入，通常不需要循环节点。特殊场景（如节点只处理第一项的 RSS 节点）可使用 Loop，支持按批次处理（如每批次 2 项）。

### HTTP Request 节点
n8n 中最灵活的节点之一，可向任何 REST API 发起 HTTP 请求。
- 支持请求方法、URL、认证、请求头、请求体等完整配置
- 可作为常规节点使用，也可附加到 AI Agent 作为工具
- 是连接无原生节点支持的第三方服务的通用方案

## 工作流设计要点

1. **触发器选择**：根据事件来源选择——手动测试用 Manual，定时任务用 Schedule，外部回调用 Webhook，对话交互用 Chat
2. **数据流思维**：数据以对象数组在节点间流动，每个节点对数据进行转换或传递
3. **分支与合并**：If 节点拆分分支，Merge 节点汇合分支，形成复杂的流程拓扑
4. **逐项处理**：n8n 自动对数组逐项执行，无需手动循环
5. **激活与测试**：测试 URL 仅用于开发调试，生产环境需激活工作流并使用正式 URL

## 在 handy-n8n 中的位置

C03 的四个子文档系统讲解工作流设计：平台介绍（界面和数据结构）→ 触发器节点（4 种触发器详解）→ 核心节点（数据处理/控制流/HTTP）→ 代码节点（表达式和 Code）。配套 7 个工作流 JSON 文件可直接导入学习。

## 延伸阅读

- [数据处理与转换](data-processing.md)——深入表达式和 Code 节点的代码能力
- [AI 与 API 集成](ai-api-integration.md)——集群节点、Agent、MCP 等高级节点
- [C03 n8n 基本概念](../references/c03-basic-concepts.md)——完整信源
