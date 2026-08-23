---
type: Concept
title: 聊天界面
description: Jupyter AI 聊天界面的核心功能，包括聊天创建、Persona 选择、附件、代码工具栏和多会话管理
tags: [chat, interface, ui, persona, attachment, notebook, features]
sources:
  - id: user-guide
    resource: external/libs/jupyter/jupyter-ai/docs/source/users/index.md
    title: users/index.md
  - id: getting-started
    resource: external/libs/jupyter/jupyter-ai/docs/source/getting-started.md
    title: getting-started.md
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2026-08-22
---

# 聊天界面

Jupyter AI 的聊天界面是用户与 AI Agent 交互的主要入口，集成在 JupyterLab 侧边栏和主区域中。

## 创建和管理聊天

### 创建新聊天

1. 点击 JupyterLab 左侧边栏的**聊天图标**打开聊天面板
2. 点击 **+ New Chat** 按钮创建新聊天
3. 输入聊天名称（也可以后续重命名）

聊天面板可以拖拽到 JupyterLab 右侧，或右键点击图标选择移动位置。

### 聊天即文件

Jupyter AI 中的聊天以 `.chat` 文件的形式存储在工作区中，每个 `.chat` 文件包含完整的聊天历史：

- **持久化**：聊天保存到磁盘，关闭 JupyterLab 后重新打开 `.chat` 文件即可恢复
- **多会话**：可以同时创建多个聊天管理不同的对话线程
- **删除**：直接删除对应的 `.chat` 文件即可删除聊天
- **版本控制**：`.chat` 文件可纳入 Git 版本控制

### 多聊天并发

可以在聊天面板中通过 `+ New chat` 创建多个并行聊天。现有聊天在面板中列出，点击即可切换。

## AI Persona 选择

### Persona 选择器

聊天输入工具栏中有 Persona 选择菜单，点击可选择当前对话使用的 AI Persona。每个 Persona 对应一个 Agent 或模型集成。

### 模型选择

选中 Persona 后，如果该 Persona 支持多个模型，会出现模型选择菜单。你可以：
- 在同一聊天中切换模型
- 选择不同的模型参数（推理力度、权限模式等）
- 查看 Token 使用量和成本（ACP Agent 支持）

### Persona 智能回复规则

Persona 根据连接的用户数量智能决定是否自动回复：

- **1个用户 + 1个 Persona**：该 Persona 总是自动回复新消息
- **1个用户 + 多个 Persona**：最后被 @提及 的 Persona 自动回复
- **多个用户 + ≥1个 Persona**：Persona 不自动回复，必须 @提及

### 发送消息

在输入框中输入消息，按 <kbd>ENTER</kbd> 发送，<kbd>SHIFT</kbd>+<kbd>ENTER</kbd> 换行。

## 附件系统

### 添加附件的方式

聊天支持将文件和 Notebook 单元格作为附件，为 AI Persona 提供额外上下文：

1. **拖拽**：直接将文件拖入聊天输入框
2. **拖拽单元格**：将 Notebook 单元格拖入聊天输入框
3. **文件选择器**：点击输入框中的回形针图标
4. **@file 命令**：输入 `@file:<file-path>` 打开文件自动补全菜单

AI Persona 会读取附件内容来辅助回答。

## 代码工具栏

AI 返回的代码块提供快捷操作按钮：

| 操作 | 说明 |
|---|---|
| 复制到剪贴板 | 将代码复制到剪贴板 |
| 插入到活动单元格上方 | 在当前活动单元格上方插入新单元格 |
| 插入到活动单元格下方 | 在当前活动单元格下方插入新单元格 |
| 替换活动单元格 | 用生成的代码替换当前活动单元格内容 |

### 包含选中内容

在 Notebook 中选中代码后，可以在发送消息时勾选"包含选中内容"选项，将选中的代码作为上下文发送给 AI。

## 权限控制

Agent 调用工具（写入文件、执行命令、MCP 工具）时会弹出权限请求对话框：

- **允许一次**：仅本次允许
- **始终允许**：本次会话中始终允许该工具
- **拒绝**：拒绝本次工具调用

权限模式可通过输入工具栏中的控制按钮调整。部分 Agent 默认不请求权限，需参考 Agent 文档配置。

## 聊天消息的组件角色

理解聊天中各组件的角色有助于理解消息流：

| 组件 | 角色 |
|---|---|
| 聊天面板 | 收集消息、附件和权限决策，显示流式回复 |
| AI Persona | 接收消息并生成回复，可直接调用模型或转发给外部 Agent |
| ACP 集成 | 通过 Agent Client Protocol 连接外部 Agent，回报可用模型/模式/权限 |
| Jupyter MCP 服务器 | 将 Notebook 和 JupyterLab 操作暴露为 MCP 工具 |
| 自定义 MCP 服务器 | 通过 `.jupyter/mcp_settings.json` 添加额外工具源 |

## 消息流程

```
1. 用户发送消息（可附带 Persona 选择或附件）
       │
       ▼
2. Jupyter AI 将消息路由到选中的 Persona
   ├── ACP Persona → 转发给外部 Agent → 流式传回事件
   └── 直接模型 Persona → 调用配置的模型提供商
       │
       ▼
3. Agent/Persona 决定是否需要工具（模型/Notebook工具/MCP工具）
   └── 工具调用可能需要用户审批
       │
       ▼
4. 结果通过 Persona 流式传回聊天面板
   └── 文件/Notebook 编辑等工作区变更由被调用的工具直接执行
```

## 相关概念

- [安装与配置](01-installation-and-setup.md)
- [AI Persona 系统](05-ai-personas.md)
- [ACP 与 MCP 双协议](04-protocols-acp-mcp.md)
- [MCP 工具与 Notebook 交互](07-mcp-tools-and-notebooks.md)
- [聊天文件与持久化](06-chat-files-and-persistence.md)
- [首次聊天示例](../examples/first-chat.md)
