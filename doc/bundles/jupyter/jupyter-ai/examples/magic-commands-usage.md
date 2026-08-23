---
type: Example
title: Magic Commands 使用
description: 在 Jupyter Notebook 中使用 %ai 和 %%ai Magic 命令与 AI 交互的实用示例
tags: [example, magic-commands, ipython, notebook, cell-magic]
sources:
  - id: magics
    resource: external/libs/jupyter/jupyter-ai/docs/source/users/magics.md
    title: magics.md
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2026-08-22
---

# Magic Commands 使用

本示例展示如何在 Notebook 单元格中使用 `%ai` 和 `%%ai` Magic 命令快速与 AI 交互，无需打开聊天面板。

## 前提条件

- Jupyter AI 已安装
- Magic Commands 扩展已安装：`pip install jupyter-ai-magic-commands`
- Jupyternaut 已安装（推荐）：`pip install 'jupyter-ai[jupyternaut]'`
- 已配置至少一个模型的 API Key

## 快速开始

### 加载扩展

在 Notebook 的第一个单元格运行：

```python
%load_ext jupyter_ai_magic_commands
```

看到 `jupyter_ai_magic_commands` 已加载的提示即可。

### 第一个 Magic 提问

```python
%ai "用一句话解释什么是机器学习"
```

AI 会直接在单元格下方返回回答。

## %ai 行命令

行命令 `%ai` 用于简短问答，命令在一行内完成。

### 基本提问

```python
%ai "Python 中 list 和 tuple 的区别是什么？"
```

### 指定模型

使用 `--model` 参数选择模型（格式遵循 LiteLLM 的 provider:model）：

```python
%ai --model anthropic:claude-sonnet-4 "解释快速排序的原理"
```

```python
%ai --model openai:gpt-4 "什么是 Python 的 GIL？"
```

### 代码生成

```python
%ai "写一个 Python 函数，检查字符串是否是回文"
```

返回的代码可以复制到新单元格运行。

## %%ai 单元格命令

单元格命令 `%%ai` 将整个单元格内容作为提示，适合长文本、代码解释等场景。

### 解释代码

```python
%%ai
请解释以下代码的作用，并指出可能的问题：

```python
def process_items(items):
    result = []
    for i in range(len(items)):
        if items[i] > 0:
            result.append(items[i] * 2)
    return result
```
```

### 代码生成

```python
%%ai
请写一个 Python 类实现一个简单的缓存，要求：
1. 支持 get/set/delete 操作
2. 有最大容量限制，超出时使用 LRU 策略淘汰
3. 线程安全
```

## 引用变量和单元格

Magic Commands 最强大的功能之一是可以引用 Notebook 中的变量和之前的单元格。

### 引用变量

使用花括号 `{var_name}` 引用当前内核中的变量：

```python
# 先定义一些数据
import pandas as pd
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie'],
    'score': [85, 92, 78]
})
summary = df.describe().to_string()
```

```python
%ai f"分析这个数据集的统计结果：{summary}"
```

### 引用 In[] 单元格

引用之前执行过的单元格代码：

```python
# 假设 In[3] 是你写的一段代码
%ai "In[3] 中的代码有什么可以优化的地方？"
```

### 引用 Out[] 输出

引用之前单元格的输出：

```python
# 假设 Out[5] 是某个计算结果
%ai f"Out[5] 的结果意味着什么？"
```

### 引用 Err[] 错误

```python
# 当代码报错后
%ai "Err[7] 这个错误怎么解决？"
```

## 配置 Magic Commands

### 设置默认模型

```python
%config AiMagics.default_language_model = "anthropic:claude-sonnet-4"
```

之后使用 `%ai` 时默认使用该模型，无需每次指定 `--model`。

### 调整上下文窗口

```python
# 保留最近5轮对话作为上下文（默认2轮）
%config AiMagics.max_history = 5
```

### 查看当前配置

```python
%config AiMagics
```

### 重置对话历史

```python
%ai reset
```

这会清除 Magic Commands 的对话记忆，相当于开始新的对话。

## 实用场景

### 场景 1：快速解释错误

```python
# 运行代码遇到错误
result = 1 / 0  # ZeroDivisionError
```

```python
%ai "Err[] 这个错误是什么原因？怎么修复？"
```

### 场景 2：代码审查

```python
%%ai
请审查以下代码的性能和安全性：

```python
import sqlite3
def get_user(user_id):
    conn = sqlite3.connect('app.db')
    cursor = conn.execute(f"SELECT * FROM users WHERE id = {user_id}")
    return cursor.fetchone()
```
```

### 场景 3：数据解读

```python
# 先做计算
correlation = df[['total_bill', 'tip', 'size']].corr()
print(correlation)
```

```python
%ai f"解释这个相关系数矩阵的结果：{correlation.to_string()}"
```

### 场景 4：编写测试

```python
# 你写了一个函数
def calculate_factorial(n):
    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0:
        return 1
    return n * calculate_factorial(n - 1)
```

```python
%%ai
为以下函数编写 pytest 测试用例，包括正常情况、边界情况和异常情况：

```python
{In[-2]}
```
```

## Magic Commands vs 聊天面板

| 场景 | 推荐方式 |
|---|---|
| 快速问一个简单问题 | %ai |
| 解释当前单元格代码 | %%ai |
| 长对话/多轮协作 | 聊天面板 |
| 需要 AI 编辑/运行 Notebook | 聊天面板（MCP 工具） |
| 需要拖拽文件/单元格作为上下文 | 聊天面板 |
| 实时协作 | 聊天面板 |
| 引用变量/输出快速分析 | %ai/%%ai |

## 注意事项

1. **对话上下文独立**：Magic Commands 的对话历史与聊天面板互不影响
2. **%ai reset**：切换话题时记得重置对话，避免不相关的上下文干扰
3. **模型格式**：模型 ID 必须是 LiteLLM 支持的格式（`provider:model`）
4. **API Key**：确保对应的 API Key 已设置为环境变量
5. **变量引用**：使用 `{var}` 时变量必须在当前内核中已定义

## 相关示例

- [首次聊天快速上手](first-chat.md)
- [Notebook AI 辅助工作流](notebook-ai-assistant.md)
- [Magic Commands 概念](../concepts/10-magic-commands.md)
