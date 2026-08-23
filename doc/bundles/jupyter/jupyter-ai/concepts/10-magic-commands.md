---
type: Concept
title: Magic Commands
description: Jupyter AI 的 IPython Magic 命令（%ai 和 %%ai），用于在 Notebook 单元格中直接调用 AI
tags: [magic-commands, ipython, cell-magic, line-magic, notebook, ai-magics]
sources:
  - id: magics
    resource: external/libs/jupyter/jupyter-ai/docs/source/users/magics.md
    title: magics.md
  - id: pyproject
    resource: external/libs/jupyter/jupyter-ai/pyproject.toml
    title: pyproject.toml (magics extra)
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2026-08-22
---

# Magic Commands

Magic Commands 是 Jupyter AI 提供的 IPython 扩展，允许你在 Notebook 单元格中直接使用 `%ai` 和 `%%ai` 命令与 AI 交互，无需打开聊天面板。

## 安装

Magic Commands 是可选功能，需要单独安装：

```bash
pip install jupyter-ai-magic-commands
```

或通过 extras 安装：

```bash
pip install 'jupyter-ai[magics]'
```

## 加载扩展

在 Notebook 中首先加载扩展：

```python
%load_ext jupyter_ai_magic_commands
```

## 基本用法

### 行命令：`%ai`

用于简短的问答：

```python
%ai "解释什么是 pandas DataFrame"
```

### 单元格命令：`%%ai`

在单元格开头使用，将整个单元格内容作为提示：

```python
%%ai
请解释以下代码的作用：
```python
import pandas as pd
df = pd.read_csv('data.csv')
df.groupby('category').mean()
```
```

或者在单元格中写提示，后续单元格提供代码上下文：

```python
%%ai
这段代码有什么问题？
```

## 引用变量和单元格

Magic Commands 支持引用 Notebook 中的变量和之前的单元格输出：

| 语法 | 说明 |
|---|---|
| `In[<n>]` | 引用第 n 个输入单元格的代码 |
| `Out[<n>]` | 引用第 n 个输出单元格的结果 |
| `Err[<n>]` | 引用第 n 个单元格的错误输出 |
| `{variable_name}` | 引用当前内核中的变量值 |

**示例：**

```python
# 让 AI 解释第5个单元格的代码
%ai "解释 In[5] 中的代码做了什么"
```

```python
# 使用变量值作为上下文
data_sample = df.head().to_string()
%ai f"分析这个数据集的前几行：{data_sample}"
```

## 配置模型

Magic Commands 通过 `AiMagics` 配置类管理设置。

### 选择模型

```python
%ai --model openai:gpt-4 "解释量子计算"
```

或通过配置设置默认模型：

```python
%config AiMagics.default_language_model = "openai:gpt-4"
```

模型格式遵循 LiteLLM 的 provider:model 命名规则，支持 1000+ 模型。

### 设置上下文窗口大小

```python
%config AiMagics.max_history = 5  # 保留最近5轮对话
```

### 重置对话历史

```python
%ai reset
```

这会清除 Magic Commands 的对话上下文记忆。

## Magic Commands vs 聊天面板

| 特性 | Magic Commands | 聊天面板 |
|---|---|---|
| 上下文 | Notebook 单元格变量/输出 | 附件、拖拽文件/单元格 |
| 对话历史 | 独立（%ai reset 清除） | .chat 文件持久化 |
| 模型切换 | 每个单元格可选 | Persona 选择器 |
| 工具使用 | 有限（通过 LiteLLM） | 完整 MCP 工具集 |
| 实时协作 | 无 | 支持（Yjs CRDT） |
| 适用场景 | 快速代码问答、单元格内 AI 辅助 | 复杂任务、多轮对话、Agent 工作流 |

## 相关概念

- [AI Persona 系统](05-ai-personas.md)
- [MCP 工具与 Notebook 交互](07-mcp-tools-and-notebooks.md)
- [安装与配置](01-installation-and-setup.md)
- [Magic Commands 示例](../examples/magic-commands-usage.md)
