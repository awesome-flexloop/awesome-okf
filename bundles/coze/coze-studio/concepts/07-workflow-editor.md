---
type: concept
title: "工作流与智能体编辑器"
description: "Coze Studio 前端基于 FlowGram 引擎的工作流编辑器与 agent-ide 智能体 IDE 的包结构、模块职责与协作机制"
tags: [工作流, FlowGram, 编辑器, Agent IDE, 前端包]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T02:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T02:30:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cs-010
    resource: /references/frontend-architecture.md
    title: "FlowGram 工作流编辑器引擎"
  - id: F-cs-060
    resource: /references/frontend-architecture.md
    title: "workflow/ 8 个子包"
  - id: F-cs-061
    resource: /references/frontend-architecture.md
    title: "agent-ide/ 8 个子包"
---

# 工作流与智能体编辑器

Coze Studio 前端提供两个核心可视化编辑器：工作流编辑器（Workflow Editor）和智能体 IDE（Agent IDE）。工作流编辑器基于 FlowGram 引擎（@flowgram.ai）构建，提供节点拖拽、连线、属性编辑等可视化编排能力；智能体 IDE 提供智能体的人设、提示词、工具、知识库等配置界面。两者在 Rush.js monorepo 中分别以 `packages/workflow/` 和 `packages/agent-ide/` 独立包组存在，通过 level-1 的 arch/ 基础包共享底层能力。

## 两大编辑器定位

```
┌─────────────────────────────────────────────────────────────┐
│                    @coze-studio/app (level-4)               │
│                   主应用路由与页面组装                        │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        ▼                                 ▼
┌───────────────────┐         ┌───────────────────────┐
│  packages/workflow│         │  packages/agent-ide   │
│  (level-3)        │         │  (level-3)            │
│  工作流可视化编辑器│         │  智能体配置 IDE       │
│  FlowGram 引擎    │         │  人设/提示词/工具配置  │
│  8个子包          │         │  8个子包              │
└───────┬───────────┘         └───────────┬───────────┘
        │                                 │
        └────────────────┬────────────────┘
                         ▼
              ┌─────────────────────┐
              │  packages/arch/     │
              │  (level-1 核心包)   │
              │  bot-api/bot-store  │
              │  bot-hooks/i18n/idl │
              │  fetch-stream/...   │
              └─────────────────────┘
```

## 工作流编辑器（workflow/）

`packages/workflow/` 是基于 FlowGram 引擎构建的可视化工作流编辑系统，包含 8 个子包：

| 子包 | 职责 |
|------|------|
| **base** | 工作流基础类型定义、常量、节点 Schema |
| **nodes** | 各类工作流节点的定义（LLM 节点、条件节点、代码节点等） |
| **render** | 基于 FlowGram 的画布渲染引擎，负责节点/连线的可视化绘制 |
| **sdk** | 工作流操作 SDK，提供创建/编辑/执行工作流的编程接口 |
| **history** | 历史记录管理，实现撤销（Undo）/重做（Redo）能力 |
| **test-run** | 工作流测试运行，在编辑器中调试执行工作流 |
| **variable** | 变量管理，工作流内的变量定义、引用和传递 |
| **setters** | 属性设置器，节点选中后的属性面板配置组件 |

### 工作流编辑器工作流程

```
┌────────────┐    ┌────────────┐    ┌────────────┐    ┌────────────┐
│  节点面板  │───▶│  画布渲染  │───▶│  连线编辑  │───▶│ 属性设置器 │
│ (nodes/)   │    │ (render/)  │    │ (render/)  │    │ (setters/) │
└────────────┘    └──────┬─────┘    └──────┬─────┘    └──────┬─────┘
                         │                 │                 │
                         ▼                 ▼                 ▼
                   ┌─────────────────────────────────────────────┐
                   │              workflow/sdk                    │
                   │     统一的工作流数据模型与操作 API            │
                   └──────────────────────┬──────────────────────┘
                                          │
                              ┌───────────┴───────────┐
                              ▼                       ▼
                    ┌──────────────────┐    ┌──────────────────┐
                    │ workflow/history │    │workflow/variable │
                    │ 撤销/重做栈管理  │    │  变量引用追踪    │
                    └──────────────────┘    └──────────────────┘
                                          │
                                          ▼
                              ┌──────────────────┐
                              │workflow/test-run │
                              │  调试运行时      │
                              └──────────────────┘
```

后端通过 Eino 框架执行工作流，前端通过 test-run 包与后端 `/api/workflow` 接口通信，在编辑器中实时展示工作流的执行过程和结果。

## 智能体 IDE（agent-ide/）

`packages/agent-ide/` 是智能体的配置和开发环境，包含 8 个子包：

| 子包 | 职责 |
|------|------|
| **context** | 智能体编辑上下文管理，维护当前编辑智能体的状态 |
| **entry** | 智能体 IDE 入口模块，页面注册和初始化 |
| **layout** | 布局组件，智能体编辑页面的整体布局（侧边栏、主区域、属性面板） |
| **navigate** | 导航管理，智能体各配置页面间的路由切换 |
| **prompt` | 提示词编辑器，智能体人设（Persona）和提示词的可视化编辑 |
| **tool** | 工具配置面板，为智能体添加/配置插件工具 |
| **workflow** | 工作流关联配置，将工作流绑定到智能体 |
| **commons** | 公共组件，智能体 IDE 各模块共享的 UI 组件和工具函数 |

### 智能体 IDE 功能模块

智能体 IDE 围绕 SingleAgent 的配置展开，对应后端 `crossdomain/agent/contract.go` 定义的接口：

- **StreamExecute**：IDE 中可测试运行智能体，查看流式对话效果
- **ObtainAgentByIdentity**：按身份加载已有智能体配置
- **GetSingleAgentDraft**：加载智能体草稿进行编辑

智能体配置涵盖：
- 基本信息（名称、描述、头像）
- 人设与提示词（prompt 包）
- 插件工具选择（tool 包）
- 知识库关联
- 工作流绑定（workflow 包）
- 记忆配置
- 模型选择

## FlowGram 引擎

FlowGram（@flowgram.ai）是工作流编辑器的底层渲染引擎，提供：

- **画布渲染**：无限画布、缩放、平移
- **节点系统**：自定义节点注册、节点端口、节点状态
- **连线系统**：贝塞尔曲线连线、连线校验
- **交互能力**：拖拽、框选、快捷键
- **撤销重做**：基于命令模式的操作历史

workflow/render 包在 FlowGram 之上封装了 Coze Studio 特定的节点渲染逻辑和交互行为。

## 与后端的交互

前端编辑器通过以下 API 与后端交互：

| API 路径 | 功能 |
|----------|------|
| `/api/workflow` | 工作流 CRUD、执行 |
| `/api/draftbot` | 智能体草稿管理 |
| `/api/knowledge` | 知识库关联 |
| `/api/plugin` | 插件工具配置 |
| `/api/playground` | 调试运行 |
| `/api/conversation` | 对话测试 |

所有 API 客户端由 arch/bot-api 和 arch/bot-http 包统一封装，流式响应通过 arch/fetch-stream 包处理。

## 相关概念

- [整体架构概览](/concepts/00-overview-ddd-architecture.md)
- [Rush.js Monorepo 前端架构](/concepts/06-rushjs-monorepo.md)
- [Thrift IDL 与代码生成](/concepts/02-thrift-idl-codegen.md)
- [前端架构参考](/references/frontend-architecture.md)
