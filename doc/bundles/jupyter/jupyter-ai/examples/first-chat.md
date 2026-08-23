---
type: Example
title: 首次聊天快速上手
description: 安装 Jupyter AI 后，创建第一个聊天并与 AI Agent 交互的完整流程
tags: [example, getting-started, first-chat, quickstart]
sources:
  - id: getting-started
    resource: external/libs/jupyter/jupyter-ai/docs/source/getting-started.md
    title: getting-started.md
  - id: user-guide
    resource: external/libs/jupyter/jupyter-ai/docs/source/users/index.md
    title: users/index.md
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2026-08-22
---

# 首次聊天快速上手

本示例带你从零开始，安装 Jupyter AI、配置 AI Agent，创建第一个聊天并与 AI 协作完成一个数据分析任务。

## 前提条件

- Python >= 3.9
- JupyterLab 4.x
- 至少一个 AI Agent 的账号和 API Key（如 OpenAI、Anthropic Claude 等）
- Node.js（如需安装 npm 包的 ACP 适配器）

## 步骤 1：安装 Jupyter AI

```bash
# 安装 Jupyter AI 核心
pip install jupyter-ai

# 安装 Jupyternaut（默认 Persona，通过 LiteLLM 支持多模型）
pip install 'jupyter-ai[jupyternaut]'
```

如果你想用 Claude Code 或 Codex 等外部 Agent，还需要安装对应的 Agent CLI 和 ACP 适配器。本示例使用 Jupyternaut + OpenAI 模型，最快速上手。

## 步骤 2：配置 API Key

设置环境变量（推荐方式）：

```bash
# Linux/macOS
export OPENAI_API_KEY="sk-your-api-key-here"

# Windows PowerShell
$env:OPENAI_API_KEY = "sk-your-api-key-here"
```

或者创建 `.env` 文件（不推荐提交到版本控制）：
```bash
OPENAI_API_KEY=sk-your-api-key-here
```

## 步骤 3：启动 JupyterLab

```bash
jupyter lab
```

浏览器会自动打开 JupyterLab。如果没有自动打开，访问终端中显示的 URL（通常是 `http://localhost:8888/lab`）。

## 步骤 4：打开聊天面板

Jupyter AI 有两种打开聊天的方式：

### 方式 A：侧边栏聊天面板
1. 点击 JupyterLab 左侧边栏的**聊天图标**（💬 气泡图标）
2. 点击 **+ New Chat** 创建新聊天
3. 输入聊天名称，如"我的第一个聊天"

### 方式 B：启动页面 Chat 卡片
1. 在 Launcher（启动页面）中找到 **Chat** 卡片
2. 点击创建新聊天文件（`.chat` 文件）

## 步骤 5：选择 AI Persona

1. 在聊天输入框上方的工具栏中，找到 Persona 选择器
2. 点击选择 **Jupyternaut**
3. Jupyternaut 初始化后，会出现模型选择器，选择 `openai:gpt-4` 或 `openai:gpt-3.5-turbo`

> 如果 Jupyternaut 没有出现，检查是否安装了 `jupyter-ai-jupyternaut` 包：
> ```bash
> pip list | grep jupyternaut
> ```

## 步骤 6：发送第一条消息

在输入框中输入：

```
你好！请用中文介绍一下你自己，以及你能帮我做什么？
```

按 <kbd>ENTER</kbd> 发送。Jupyternaut 会流式返回回复。

## 步骤 7：用 AI 辅助数据分析

创建一个新的 Notebook，然后尝试以下对话：

### 场景 1：数据加载

发送消息：
```
帮我写一段代码，加载一个示例 CSV 数据集并展示前5行。使用 pandas。
```

Jupyternaut 会返回类似如下代码：

```python
import pandas as pd

# 加载示例数据集（使用 seaborn 的 tips 数据集）
import seaborn as sns
df = sns.load_dataset('tips')

# 展示前5行
df.head()
```

点击代码块工具栏中的**"插入到单元格下方"**按钮，代码会自动插入到 Notebook 中。运行单元格查看结果。

### 场景 2：数据分析

发送消息：
```
分析这个数据集，告诉我每天不同时间段的平均小费金额，并生成一个柱状图。
```

Jupyternaut 会读取 Notebook 上下文（通过 MCP 工具），生成分析代码：

```python
import matplotlib.pyplot as plt

# 按天和时间分组计算平均小费
avg_tip = df.groupby(['day', 'time'])['tip'].mean().unstack()

# 绘制柱状图
avg_tip.plot(kind='bar', figsize=(10, 6))
plt.title('Average Tip by Day and Time')
plt.xlabel('Day')
plt.ylabel('Average Tip ($)')
plt.legend(title='Time')
plt.tight_layout()
plt.show()
```

**注意**：当 Jupyternaut 需要运行代码时，会弹出权限审批对话框。你可以选择"允许一次"或"始终允许"。

### 场景 3：调试错误

如果代码运行出错，选中错误单元格，发送消息：
```
这段代码报错了，请帮我修复：[附上错误信息]
```

或者直接把错误单元格拖入聊天输入框作为附件。

## 步骤 8：使用附件

Jupyter AI 支持多种附件方式：

| 方式 | 操作 |
|---|---|
| 拖拽文件 | 将文件从文件浏览器拖入输入框 |
| 拖拽单元格 | 将 Notebook 单元格拖入输入框 |
| @file 命令 | 输入 `@file:data.csv` 选择文件 |
| 附件按钮 | 点击输入框的回形针图标选择文件 |

试试：创建一个 CSV 文件，拖入聊天，让 AI 分析数据。

## 步骤 9：保存和恢复聊天

聊天会自动保存为 `.chat` 文件：
- 默认保存在当前工作目录
- 关闭 JupyterLab 后，双击 `.chat` 文件即可恢复聊天
- 可以重命名、移动、删除 `.chat` 文件

## 常见问题

### Jupyternaut 不回复
- 检查 API Key 是否正确设置
- 检查网络连接是否能访问 OpenAI API
- 查看 JupyterLab 终端是否有错误信息
- 尝试重启 JupyterLab

### 工具调用被拒绝
- 权限对话框弹出时，点击"允许一次"即可
- 如果想自动批准，在权限设置中调整
- 注意：Agent 默认在写入文件或运行命令前请求权限，这是安全设计

### 模型选择器不显示
- Jupyternaut 首次加载需要几秒钟初始化
- 发送一条消息后模型选择器通常会出现

## 下一步

- [Notebook AI 辅助工作流](notebook-ai-assistant.md)：更深入的 Notebook AI 协作示例
- [Magic Commands 使用](magic-commands-usage.md)：在单元格中直接使用 AI
- [配置自定义 MCP 服务器](custom-mcp-server.md)：为 AI 添加更多工具
- [创建自定义 Persona](custom-persona.md)：开发自己的 AI 角色
