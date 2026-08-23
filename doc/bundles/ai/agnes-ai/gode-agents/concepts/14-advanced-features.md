---
type: Concept
title: 高级特性
description: Managed Agents多智能体协作、Hub集成（save/from_hub/push_to_hub）、CLI命令行、GradioUI界面
tags: [高级, 多智能体, Hub, CLI, Gradio, 托管智能体]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T12:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: F-017
    resource: /references/agents-api.md
    title: Agents API 参考
  - id: F-143
    resource: /references/utils-api.md
    title: Utils API 参考
---

# 高级特性

## 概述

GodeAgents 框架提供了多项高级特性，支持从单智能体原型到多智能体协作系统、从本地开发到云端部署的完整工作流。Managed Agents（托管智能体）允许多个专业化 Agent 协同工作；Hub 集成让 Agent 可以保存为完整项目、从 HuggingFace Hub 加载、或上传为 HF Space 分享；CLI 命令行工具支持无需编写代码即可运行 Agent；GradioUI 提供开箱即用的 Web 聊天界面。这些特性使得框架不仅适合研究和原型开发，也支持团队协作和生产部署。

> 事实溯源：F-017、F-019、F-026、F-027、F-029~F-031、F-143~F-147

## 核心概念

### Managed Agents：托管智能体协作

Managed Agents 是多智能体协作的核心机制。一个主 Agent（CodeAgent 或 ToolCallingAgent）可以将其他 Agent 作为"托管智能体"纳入管理，在运行时将子任务委托给专业化的 Agent 执行。每个托管 Agent 必须具备 `name` 和 `description` 属性，主 Agent 根据 description 决定何时调用哪个托管 Agent。

协作流程：
1. **任务分配**：渲染 `managed_agent.task` 模板，将任务描述传递给被调用的托管 Agent
2. **子 Agent 执行**：托管 Agent 调用自身的 `run()` 方法完成子任务
3. **报告返回**：渲染 `managed_agent.report` 模板，将执行结果返回给主 Agent
4. **摘要追加**（可选）：当 `provide_run_summary=True` 时，追加运行摘要

`_setup_managed_agents()` 在初始化时构建 `{agent.name: agent}` 字典，`_validate_tools_and_managed_agents()` 检测 tools 和 managed_agents 之间的名称冲突。

> 事实溯源：F-017、F-019、F-026

### Hub 集成：Agent 的保存与分享

框架提供了完整的 Agent 生命周期管理，支持将 Agent 保存为可移植的项目目录，并与 HuggingFace Hub 集成：

| 方法 | 功能 |
|------|------|
| `save(output_dir, relative_path=None)` | 递归保存 Agent 及其 managed_agents、工具、提示词、配置 |
| `from_hub(repo_id, ...)` | 从 HuggingFace Hub 下载 Space 仓库并加载 Agent |
| `from_folder(folder)` | 从本地文件夹加载 Agent（递归加载 managed_agents/tools/model） |
| `push_to_hub(repo_id, ...)` | 创建 HF Space 仓库 → save() 到临时目录 → upload_folder 上传 |

`save()` 方法保存的完整项目结构：
- `tools/{name}.py`：每个工具单独保存为 Python 文件
- `prompts.yaml`：自定义提示词模板
- `agent.json`：Agent 配置（类型、参数、模型信息等）
- `requirements.txt`：Python 依赖列表
- `app.py`：Gradio 演示应用（Jinja2 模板生成）
- 递归保存 managed_agents 到子目录

> 事实溯源：F-027、F-029~F-031

### CLI 命令行工具

框架提供命令行入口 `smolagents`，支持无需编写 Python 代码即可运行 Agent：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `prompt` | — | 任务提示（位置参数） |
| `--model-type` | `HfApiModel` | 模型类型 |
| `--model-id` | `Qwen/Qwen2.5-Coder-32B-Instruct` | 模型ID |
| `--imports` | — | 授权导入的模块列表 |
| `--tools` | `["web_search"]` | 可用工具列表 |
| `--verbosity-level` | — | 日志级别 |
| `--api-base` | — | API 基础 URL（兼容 OpenAI 接口） |
| `--api-key` | — | API 密钥 |

CLI 内部通过 `load_model()` 根据 model_type 创建模型实例，再通过 `run_smolagent()` 创建 CodeAgent 并运行。

> 事实溯源：F-143~F-145

### GradioUI：Web 聊天界面

框架内置 Gradio Web 界面支持：

- **`stream_to_gradio(agent, task, ...)`**：生成器函数，调用 `agent.run(stream=True)` 逐步 yield `gr.ChatMessage` 对象，实现流式输出
- **`GradioUI` 类**：构造接收一个 `MultiStepAgent` 实例，提供 `launch()` 和 `create_app()` 方法创建 Gradio 聊天界面

`GradioUI(agent).launch()` 一键启动 Web UI，用户可以通过浏览器与 Agent 交互。

> 事实溯源：F-146~F-147

## API 要点

### Managed Agents 设置与调用

```python
def _setup_managed_agents(managed_agents: List[Agent]) -> Dict[str, Agent]:
    """
    初始化托管智能体：
    - 验证每个agent有name和description属性
    - 构建 {agent.name: agent} 字典
    """
    ...

def _validate_tools_and_managed_agents(tools: Dict, managed_agents: Dict):
    """
    检测tools和managed_agents之间的名称冲突，
    发现重复名称时抛出异常。
    """
    ...

# Agent.__call__ 中托管智能体的调用流程
def __call__(self, task: str, **kwargs):
    """
    1. 渲染 managed_agent.task 模板 → 构造任务消息
    2. 调用 self.run() 执行（内部可能调用managed_agents）
    3. 渲染 managed_agent.report 模板 → 构造报告消息
    4. provide_run_summary=True 时追加运行摘要
    """
    ...
```

> 事实溯源：F-017、F-019、F-026

### Hub 集成方法

```python
def save(self, output_dir: str, relative_path: Optional[str] = None):
    """
    递归保存Agent到指定目录：
    - 递归保存managed_agents
    - 工具保存为 tools/{name}.py
    - 保存prompts.yaml
    - 保存agent.json（Agent配置）
    - 保存requirements.txt
    - 生成app.py（Jinja2模板渲染Gradio应用）
    """
    ...

@classmethod
def from_hub(cls, repo_id: str, **kwargs) -> "MultiStepAgent":
    """
    从HuggingFace Hub下载Space仓库 → from_folder()加载
    """
    ...

@classmethod
def from_folder(cls, folder: str) -> "MultiStepAgent":
    """
    从本地文件夹加载Agent：
    - 读取agent.json
    - 递归加载managed_agents
    - 加载tools
    - 加载model
    """
    ...

def push_to_hub(self, repo_id: str, **kwargs):
    """
    上传Agent到HuggingFace Hub：
    1. 创建HF Space仓库
    2. save()到临时目录
    3. upload_folder上传到Hub
    """
    ...
```

> 事实溯源：F-027、F-029~F-031

### CLI 函数

```python
def parse_arguments() -> argparse.Namespace:
    """
    解析命令行参数：
    - prompt: 任务提示（位置参数）
    - --model-type: 模型类型，默认HfApiModel
    - --model-id: 模型ID，默认Qwen/Qwen2.5-Coder-32B-Instruct
    - --imports: 授权导入模块
    - --tools: 工具列表，默认["web_search"]
    - --verbosity-level: 日志级别
    - --api-base: API基础URL
    - --api-key: API密钥
    """
    ...

def load_model(model_type: str, model_id: str, api_base: Optional[str] = None,
               api_key: Optional[str] = None, **kwargs) -> Model:
    """根据model_type字符串动态创建并返回Model实例"""
    ...

def run_smolagent(prompt: str, tools: List[str], model_type: str, model_id: str,
                  **kwargs) -> str:
    """创建CodeAgent并run(prompt)，返回结果字符串"""
    ...
```

> 事实溯源：F-143~F-145

### GradioUI

```python
def stream_to_gradio(agent: MultiStepAgent, task: str, **kwargs) -> Iterator:
    """
    生成器函数，用于Gradio流式输出：
    调用 agent.run(stream=True)，逐步yield gr.ChatMessage对象
    """
    ...

class GradioUI:
    """Gradio Web聊天界面"""

    def __init__(self, agent: MultiStepAgent):
        """接收一个MultiStepAgent实例"""
        ...

    def create_app(self):
        """创建Gradio App实例"""
        ...

    def launch(self, **kwargs):
        """创建并启动Gradio Web界面（调用gr.launch()）"""
        ...
```

> 事实溯源：F-146~F-147

## 代码示例

### 创建多智能体协作系统

```python
from codified_smolagents import (
    CodeAgent, ToolCallingAgent, HfApiModel,
    DuckDuckGoSearchTool,
)

model = HfApiModel()

# 创建专业化的搜索Agent
search_agent = ToolCallingAgent(
    tools=[DuckDuckGoSearchTool()],
    model=model,
    max_steps=3,
    name="web_searcher",
    description="""网络搜索专家。擅长在互联网上搜索最新信息、
    查找事实性数据、获取新闻和实时信息。
    当需要查找当前不确定的外部信息时使用此Agent。""",
)

# 创建数学计算Agent
math_agent = CodeAgent(
    tools=[],
    model=model,
    additional_authorized_imports=['math', 'statistics', 'numpy'],
    max_steps=3,
    name="math_expert",
    description="""数学计算专家。擅长进行复杂数学计算、
    统计分析、数值运算。当需要精确数学计算时使用此Agent。""",
)

# 创建主Agent，统筹两个专业Agent
manager_agent = CodeAgent(
    tools=[],
    model=model,
    managed_agents=[search_agent, math_agent],
    additional_authorized_imports=['datetime'],
    max_steps=10,
)

# 主Agent会自动根据任务需求选择调用合适的专业Agent
result = manager_agent.run(
    "搜索2026年全球人口数据，然后计算全球人口密度（假设地球陆地面积1.49亿平方公里）"
)
print(result)
```

### 保存 Agent 到本地

```python
from codified_smolagents import CodeAgent, HfApiModel, DuckDuckGoSearchTool

model = HfApiModel()
agent = CodeAgent(
    tools=[DuckDuckGoSearchTool()],
    model=model,
    additional_authorized_imports=['math', 'datetime'],
    max_steps=5,
)

# 保存Agent到本地目录
output_dir = "./my_agent"
agent.save(output_dir)
print(f"Agent已保存到 {output_dir}/")

# 查看保存的文件结构
import os
for root, dirs, files in os.walk(output_dir):
    level = root.replace(output_dir, '').count(os.sep)
    indent = '  ' * level
    print(f"{indent}{os.path.basename(root)}/")
    for f in files:
        print(f"{indent}  {f}")
# 输出类似：
# my_agent/
#   agent.json
#   requirements.txt
#   prompts.yaml
#   app.py
#   tools/
#     web_search.py
```

### 从本地文件夹加载 Agent

```python
from codified_smolagents import CodeAgent

# 从保存的目录加载Agent
loaded_agent = CodeAgent.from_folder("./my_agent")

# 直接使用加载的Agent
result = loaded_agent.run("今天的日期是多少？距离2027年元旦还有多少天？")
print(result)
```

### 推送 Agent 到 HuggingFace Hub

```python
from codified_smolagents import CodeAgent, HfApiModel

model = HfApiModel()
agent = CodeAgent(
    tools=[],
    model=model,
    additional_authorized_imports=['math'],
    max_steps=3,
)

# 推送到HuggingFace Hub（需要先登录 huggingface-cli login）
# agent.push_to_hub("my-username/math-agent")
# 这会创建一个HF Space，可以在线运行Agent
```

### 从 HuggingFace Hub 加载 Agent

```python
from codified_smolagents import CodeAgent

# 从Hub加载Agent
# agent = CodeAgent.from_hub("sergeipetrov/math-agent")
# result = agent.run("计算 2**20 的值")
# print(result)
```

### CLI 命令行使用

```bash
# 基本用法：默认使用 HfApiModel 和 web_search 工具
smolagents "计算 2**10 的值"

# 指定模型和工具
smolagents "搜索2026年AI最新进展并总结" \
  --model-type HfApiModel \
  --model-id "Qwen/Qwen2.5-Coder-32B-Instruct" \
  --tools web_search \
  --verbosity-level 2

# 使用 OpenAI 兼容 API
smolagents "写一个Python快速排序函数" \
  --model-type OpenAIServerModel \
  --model-id "gpt-4o" \
  --api-base "https://api.openai.com/v1" \
  --api-key "sk-..." \
  --imports math,typing

# 授权额外模块
smolagents "分析一组数据的统计特征" \
  --imports statistics,math,collections
```

### 使用 Python API 模拟 CLI

```python
from codified_smolagents.cli import load_model, run_smolagent

# 通过CLI函数创建模型
model = load_model(
    model_type="OpenAIServerModel",
    model_id="gpt-4o",
    api_base="https://api.openai.com/v1",
    api_key="sk-...",
)

# 直接运行（内部创建CodeAgent）
result = run_smolagent(
    prompt="计算斐波那契数列第20项",
    tools=[],
    model_type="OpenAIServerModel",
    model_id="gpt-4o",
    api_base="https://api.openai.com/v1",
    api_key="sk-...",
    additional_authorized_imports=['math'],
)
print(result)
```

### 启动 GradioUI Web 界面

```python
from codified_smolagents import CodeAgent, HfApiModel, GradioUI

model = HfApiModel()
agent = CodeAgent(
    tools=[],
    model=model,
    additional_authorized_imports=['math', 'datetime'],
    max_steps=5,
)

# 启动Gradio Web界面
# GradioUI(agent).launch()
# 浏览器会自动打开，显示聊天界面
# 用户可以在网页上输入问题，Agent流式回复
```

### 使用 stream_to_gradio 自定义界面

```python
from codified_smolagents import CodeAgent, HfApiModel
from codified_smolagents.utils import stream_to_gradio
import gradio as gr

model = HfApiModel()
agent = CodeAgent(
    tools=[],
    model=model,
    additional_authorized_imports=['math'],
    max_steps=5,
)

# 使用stream_to_gradio生成器实现自定义Gradio界面
def respond(message, history):
    # stream_to_gradio是生成器，逐步yield ChatMessage
    for msg in stream_to_gradio(agent, task=message):
        yield msg.content

# 自定义Gradio Blocks
with gr.Blocks() as demo:
    gr.Markdown("# My Custom Agent UI")
    chatbot = gr.ChatInterface(
        respond,
        title="Math Agent",
        description="一个擅长数学计算的AI助手",
    )

# demo.launch()
```

### 多智能体协作 + 保存 + GradioUI 完整流程

```python
from codified_smolagents import (
    CodeAgent, ToolCallingAgent, HfApiModel,
    DuckDuckGoSearchTool, GradioUI,
)

model = HfApiModel()

# 第一步：创建专业Agent
search_agent = ToolCallingAgent(
    tools=[DuckDuckGoSearchTool()],
    model=model,
    max_steps=3,
    name="searcher",
    description="网络搜索专家，用于查找最新信息",
)

coder_agent = CodeAgent(
    tools=[],
    model=model,
    additional_authorized_imports=['pandas', 'numpy', 'matplotlib'],
    max_steps=3,
    name="coder",
    description="Python编程专家，用于数据分析和可视化",
)

# 第二步：创建主Agent管理专业Agent
manager = CodeAgent(
    tools=[],
    model=model,
    managed_agents=[search_agent, coder_agent],
    additional_authorized_imports=['math'],
    max_steps=10,
)

# 第三步：保存Agent项目
manager.save("./research_assistant")
print("Agent已保存")

# 第四步：从保存的目录加载
loaded = CodeAgent.from_folder("./research_assistant")

# 第五步：启动Web界面
# GradioUI(loaded).launch(server_name="0.0.0.0", server_port=7860)
```

> 事实溯源：F-017、F-019、F-026、F-027、F-029~F-031、F-143~F-147

## 注意事项

### 托管 Agent 必须有 name 和 description

`_setup_managed_agents()` 要求每个托管 Agent 都必须设置 `name`（唯一标识符）和 `description`（功能描述，主 Agent 据此决定何时调用）。缺少任一属性会在初始化时抛出异常。description 应清晰描述 Agent 的专长和适用场景。

### 工具和托管 Agent 名称不能冲突

`_validate_tools_and_managed_agents()` 会检测 tools 和 managed_agents 之间的名称冲突。如果一个工具和一个托管 Agent 同名，初始化会失败。建议给托管 Agent 使用描述性名称（如 `web_searcher`、`math_expert`），避免与工具名冲突。

### save() 递归保存 managed_agents

保存主 Agent 时，其所有 managed_agents 也会被递归保存到子目录中。这意味着保存一个多智能体系统会生成完整的目录树，包含所有子 Agent 的配置和工具。加载时同样递归恢复整个 Agent 层次结构。

### from_hub() 需要网络和 HF Token

从 HuggingFace Hub 加载 Agent 需要网络连接能访问 `huggingface.co`，且通常需要设置 `HF_TOKEN` 环境变量（对于私有仓库）。公开仓库可以匿名访问。

### push_to_hub() 创建 HF Space

`push_to_hub()` 将 Agent 上传为 HuggingFace Space，这意味着上传后会有一个可在线运行的 Gradio 演示。Space 默认是公开的，上传前注意不要包含敏感信息（如 API Key）。

### CLI 默认使用 web_search 工具

CLI 的 `--tools` 参数默认值为 `["web_search"]`，这意味着默认会启用 DuckDuckGo 搜索工具。如果不需要搜索功能，需要显式指定 `--tools ""` 或空列表。CLI 默认模型是 `Qwen/Qwen2.5-Coder-32B-Instruct`，需要 HF Token。

### GradioUI 需要安装 gradio

使用 `GradioUI` 或 `stream_to_gradio` 需要安装 `gradio` 包（`pip install gradio`）。框架在导入时不会强制依赖 gradio，仅在使用 GradioUI 时才需要。

### stream=True 实现流式输出

`agent.run(stream=True)` 支持逐步流式输出，`stream_to_gradio` 利用此特性实现打字机效果的回复。直接调用 `agent.run()`（非stream模式）会等待整个推理过程完成后一次性返回结果。

### app.py 由 Jinja2 模板生成

`save()` 生成的 `app.py` 是通过 Jinja2 模板渲染的 Gradio 应用代码，包含加载 Agent 和启动界面的完整逻辑。生成后可以手动修改 app.py 自定义界面，也可以直接运行 `python app.py` 启动。

### requirements.txt 包含工具依赖

保存时框架会收集所有工具声明的 `requirements` 属性，汇总写入 `requirements.txt`。从 Hub 或文件夹加载 Agent 后，建议先运行 `pip install -r requirements.txt` 安装依赖。

## 相关链接

- [多步推理循环](/concepts/03-multi-step-agent.md) — Agent的run()循环与managed_agents调用
- [提示词模板系统](/concepts/12-prompt-templates.md) — managed_agent.task/report模板
- [工具系统：@tool装饰器与Tool基类](/concepts/07-tool-system.md) — 工具的保存与加载
- [CodeAgent：代码执行范式](/concepts/06-code-agent.md) — CodeAgent作为Manager或Worker
- [模型抽象层与多后端](/concepts/09-model-layer.md) — load_model动态创建模型
- [Agents API 参考](/references/agents-api.md) — save/from_hub/push_to_hub完整API
- [Utils API 参考](/references/utils-api.md) — CLI和GradioUI相关API
