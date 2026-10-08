---
type: Concept
title: 快速开始
description: 安装GodeAgents、创建第一个Agent、运行简单任务
tags: [入门, 安装, HelloWorld]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T12:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: F-014
    resource: /references/agents-api.md
    title: Agents API 参考
  - id: F-063
    resource: /references/models-api.md
    title: Models API 参考
  - id: F-047
    resource: /references/tools-api.md
    title: Tools API 参考
---

# 快速开始

## 概述

本文将引导你完成 GodeAgents 的安装、环境配置，并运行你的第一个 ToolCallingAgent 和 CodeAgent。完成本文后，你将能够创建智能体并执行简单的推理任务。

> 事实溯源：F-001、F-143~F-145

## 核心概念

在开始之前，快速了解三个核心概念：

- **Agent（智能体）**：驱动推理循环的主体，有两种类型——`ToolCallingAgent`（JSON 工具调用）和 `CodeAgent`（Python 代码执行）
- **Model（模型）**：LLM 后端实例，负责生成行动。`HfApiModel` 使用 HuggingFace Inference API（免费，适合快速上手），`OpenAIServerModel` 等使用付费 API
- **Tool（工具）**：Agent 与外部世界交互的接口，如搜索、访问网页、执行代码等

## 安装

### pip 安装

GodeAgents 包名为 `codified-smolagents`，使用 pip 安装：

```bash
pip install codified-smolagents
```

核心依赖包括：`torch`、`transformers`、`jinja2`、`huggingface_hub`、`Pillow`、`requests` 等。

### 可选依赖

根据使用的模型后端和执行器，安装对应的 extras：

```bash
# LiteLLM 支持（接入 OpenAI/Anthropic/Azure 等数百个 LLM 提供商）
pip install "codified-smolagents[litellm]"

# 本地 Transformers 模型（离线运行）
pip install "codified-smolagents[transformers]"

# OpenAI 官方 SDK
pip install "codified-smolagents[openai]"

# E2B 云沙箱执行器
pip install "codified-smolagents[e2b]"

# Docker 执行器
pip install "codified-smolagents[docker]"

# vLLM 本地高吞吐量推理
pip install "codified-smolagents[vllm]"

# MLX（Apple Silicon 本地推理）
pip install "codified-smolagents[mlx-lm]"
```

> 事实溯源：F-143

## 环境准备

### API Key 配置

GodeAgents 通过环境变量读取 API 密钥。常用环境变量：

| 环境变量 | 用途 | 对应模型类 |
|---------|------|-----------|
| `HF_TOKEN` | HuggingFace API 令牌 | `HfApiModel` |
| `OPENAI_API_KEY` | OpenAI API 密钥 | `OpenAIServerModel`、`LiteLLMModel` |
| `E2B_API_KEY` | E2B 云沙箱密钥 | `E2BExecutor` |

建议创建 `.env` 文件管理，使用 `python-dotenv` 加载：

```python
from dotenv import load_dotenv
load_dotenv()  # 从 .env 文件加载环境变量
```

### 模型选择

- **快速上手（免费）**：`HfApiModel()` — 默认使用 `Qwen/Qwen2.5-Coder-32B-Instruct`
- **生产环境**：`LiteLLMModel(model_id="gpt-4o")` 或 `OpenAIServerModel(model_id="gpt-4o")`
- **离线/隐私**：`TransformersModel(model_id="HuggingFaceTB/SmolLM2-1.7B-Instruct")`（需要 GPU）
- **Mac 本地**：`MLXModel(model_id="mlx-community/SmolLM2-1.7B-Instruct-4bit")`

> 事实溯源：F-067~F-078

## API 要点

### 导入核心类

```python
from codified_smolagents import ToolCallingAgent, CodeAgent, HfApiModel
```

### 统一入口：run()

所有 Agent 共享同一个 `run()` 方法签名：

```python
agent.run(
    task: str,                          # 任务描述
    stream: bool = False,               # 流式模式（返回生成器）
    reset: bool = False,                # 是否重置记忆
    images: Optional[List] = None,      # 图片输入（多模态）
    additional_args: Optional[Dict] = None,
    max_steps: Optional[int] = None,    # 临时覆盖最大步数
)
```

- `stream=False`（默认）：阻塞直到完成，返回最终答案
- `stream=True`：返回生成器，逐步 yield 每个 ActionStep

> 事实溯源：F-020

## 代码示例

### 第一个 ToolCallingAgent

```python
from codified_smolagents import ToolCallingAgent, HfApiModel

# 1. 创建模型实例（使用 HuggingFace Inference API）
model = HfApiModel()

# 2. 创建 Agent（无额外工具，框架自动注入 final_answer）
agent = ToolCallingAgent(tools=[], model=model)

# 3. 运行任务
result = agent.run("你好，请介绍一下你自己")
print(result)
```

> 事实溯源：F-032~F-038

### 第一个 CodeAgent

```python
from codified_smolagents import CodeAgent, HfApiModel

# 1. 创建模型
model = HfApiModel()

# 2. 创建 CodeAgent，授权 math 模块
agent = CodeAgent(
    tools=[],
    model=model,
    additional_authorized_imports=['math']
)

# 3. 运行计算任务
result = agent.run("计算 2 的 10 次方是多少？请编写Python代码计算并输出结果。")
print(result)
```

> 事实溯源：F-039~F-046

### 添加默认工具

使用 `add_base_tools=True` 一键添加搜索三件套（`web_search`、`visit_webpage`、`search_wikipedia`）：

```python
from codified_smolagents import CodeAgent, HfApiModel

model = HfApiModel()
agent = CodeAgent(
    tools=[],
    model=model,
    add_base_tools=True,  # 自动添加 DuckDuckGoSearchTool、VisitWebpageTool、WikipediaSearchTool
)
result = agent.run("搜索 Python 3.12 的新特性，并总结主要改进")
print(result)
```

手动添加特定工具：

```python
from codified_smolagents import ToolCallingAgent, DuckDuckGoSearchTool, HfApiModel

model = HfApiModel()
agent = ToolCallingAgent(
    tools=[DuckDuckGoSearchTool()],
    model=model,
)
result = agent.run("2024年诺贝尔物理学奖授予了谁？")
print(result)
```

> 事实溯源：F-018、F-120~F-125

### 使用 Gradio UI 快速演示

一行代码启动交互式 Web 界面：

```python
from codified_smolagents import CodeAgent, HfApiModel, GradioUI

model = HfApiModel()
agent = CodeAgent(tools=[], model=model, add_base_tools=True)

# 启动 Gradio 聊天界面
GradioUI(agent).launch()
```

`GradioUI` 内部使用 `stream_to_gradio` 生成器函数，调用 `agent.run(stream=True)` 逐步 yield `gr.ChatMessage` 实现流式输出。

> 事实溯源：F-146~F-147

### 使用 CLI 快速运行

```bash
# 通过命令行直接运行 CodeAgent
smolagents "计算 2**20 的值" --model-type HfApiModel
```

CLI 支持 `--model-type`、`--model-id`、`--tools`、`--imports`、`--api-base`、`--api-key` 等参数。

> 事实溯源：F-143~F-145

## 常见问题/注意事项

### 模型 API Key 配置

- **HfApiModel 报 401/403**：需要设置 `HF_TOKEN` 环境变量，或在构造时传入 `token="hf_xxx"`。免费 token 可在 https://huggingface.co/settings/tokens 获取
- **OpenAI 模型认证错误**：确认 `OPENAI_API_KEY` 已设置。使用第三方兼容 API 时，用 `OpenAIServerModel(api_base="https://your-endpoint/v1", api_key="...")` 指定端点

### 依赖安装问题

- **`ModuleNotFoundError`**：确认 pip 对应的 Python 环境与运行代码的环境一致。使用 `pip --version` 和 `where python`（Windows）检查
- **可选依赖缺失**：使用 `TransformersModel` 需安装 transformers，使用 `E2BExecutor` 需安装 e2b-code-interpreter。安装对应 extras 即可

### CodeAgent 导入授权

- 默认已授权大部分 Python 标准库模块（`BASE_BUILTIN_MODULES`），但 `os`、`sys`、`subprocess`、`shutil` 等危险模块被禁止
- 需要额外模块时通过 `additional_authorized_imports=['numpy', 'pandas']` 授权
- 设置 `additional_authorized_imports=['*']` 会输出警告日志，表示授权所有导入（不推荐）

> 事实溯源：F-041、F-105~F-107

### max_steps 默认值

- 默认 `max_steps=20`，简单问答足够；复杂调研任务建议设为 30-50
- 步数耗尽时 Agent 不会崩溃，而是调用 `provide_final_answer()` 做兜底总结

## 相关链接

- [简介：编码式多智能体推理](00-introduction.md) — 框架核心理念与设计哲学
- [架构总览](02-architecture-overview.md) — 模块依赖与核心组件
- [MultiStepAgent：核心推理循环](03-multi-step-agent.md) — run 循环机制详解
- [Agents API 参考](../references/agents-api.md) — 完整构造参数和方法签名
- [Models API 参考](../references/models-api.md) — 各模型后端配置
- [Tools API 参考](../references/tools-api.md) — 工具定义与内置工具
