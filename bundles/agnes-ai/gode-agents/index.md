---
type: OKF
title: GodeAgents (codified-smolagents) 教程
description: GodeAgents (codified-smolagents v1.14.0.dev0) 编码式多智能体推理框架的完整教程——双智能体范式、工具系统、模型抽象层、安全代码执行器和多智能体协作
tags: [godeagents, codified-smolagents, multi-agent, codeact, tool-calling, llm, agent-framework, python]
version: 1.14.0.dev0
source: https://github.com/xinetzone/SpecWeave/tree/main/external/libs/models/AgnesAI/GodeAgents
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T12:50:00+08:00" }
status: stable
stale_after: 2027-08-22
---

# GodeAgents 编码式多智能体推理框架教程

GodeAgents（codified-smolagents）是基于 [smolagents](https://github.com/huggingface/smolagents) fork 的编码式（Codified）多智能体推理框架。它将 LLM 智能体的提示词、工具、行为模式编码化，提供两种推理范式——JSON 函数调用（ToolCallingAgent）和 Python 代码执行（CodeAgent/CodeAct），在统一的 `MultiStepAgent` 基类下实现完整的多步推理循环。

框架的核心创新在于 **Codified Prompting** 方法论：不是用自然语言"告诉"模型该做什么，而是通过编码化的提示模板、类型安全的工具定义、AST 级别的安全代码执行器，让模型的推理过程变得可预测、可验证、可组合。

## 📚 快速导航

### [概念文档](concepts/index.md)
- [00-简介](concepts/00-introduction.md) — 框架概述、Codified Prompting 理念、双智能体范式、核心特性
- [01-快速开始](concepts/01-getting-started.md) — 安装、环境配置、第一个 Agent、Gradio UI 体验
- [02-架构总览](concepts/02-architecture-overview.md) — 六层架构、模块依赖、数据流、核心组件
- [03-MultiStepAgent 核心循环](concepts/03-multi-step-agent.md) — run 循环、step 抽象、规划机制、持久化
- [04-记忆系统](concepts/04-memory-system.md) — MemoryStep 序列、ActionStep/PlanningStep 消息序列化
- [05-ToolCallingAgent 函数调用范式](concepts/05-tool-calling-agent.md) — JSON function calling 机制、step 流程
- [06-CodeAgent 代码执行范式](concepts/06-code-agent.md) — CodeAct 范式、Python 执行器、导入授权
- [07-工具系统](concepts/07-tool-system.md) — @tool 装饰器、Tool 基类、JSON Schema 自动生成
- [08-内置工具详解](concepts/08-builtin-tools.md) — 搜索/网页访问/Python 解释器/最终答案工具
- [09-模型抽象层](concepts/09-model-layer.md) — Model 基类、8 种后端对比、消息处理
- [10-AgentType 多模态类型](concepts/10-agent-types.md) — AgentText/AgentImage/AgentAudio、类型自动转换
- [11-Python 执行器与安全沙箱](concepts/11-python-executor.md) — AST 安全执行、危险模块黑名单、远程执行器
- [12-提示词模板系统](concepts/12-prompt-templates.md) — YAML 模板、Jinja2 渲染、规划/托管/最终答案子模板
- [13-监控与日志](concepts/13-monitoring-logging.md) — AgentLogger、Monitor Token 计数、异常体系
- [14-高级特性](concepts/14-advanced-features.md) — Managed Agents、Hub 集成、CLI、GradioUI

### [实践示例](examples/index.md)
- [01-第一个 ToolCallingAgent](examples/01-first-agent.md) — 创建模型、运行问答、查看记忆、日志控制
- [02-CodeAgent 执行 Python](examples/02-code-agent-basic.md) — 数学计算、额外导入授权、执行器配置
- [03-自定义工具](examples/03-custom-tool.md) — @tool 装饰器、计算器/多参数工具、docstring 规范
- [04-网页搜索 Agent](examples/04-web-search-agent.md) — add_base_tools、搜索+网页访问工具组合
- [05-不同模型后端](examples/05-different-models.md) — HfApiModel/OpenAI/LiteLLM/本地模型切换
- [06-Plan-and-Execute](examples/06-planning-interval.md) — planning_interval 规划间隔、执行摘要
- [07-多智能体协作](examples/07-multi-agent-collab.md) — Managed Agents、子 Agent 注册与自动调用

### [信源参考](references/index.md)
- [Agent API 参考](references/agents-api.md) — MultiStepAgent/ToolCallingAgent/CodeAgent 完整 API
- [工具 API 参考](references/tools-api.md) — Tool 基类、@tool、内置工具、Schema 生成
- [模型 API 参考](references/models-api.md) — Model 基类及 8 种后端 API
- [记忆 API 参考](references/memory-api.md) — AgentMemory/MemoryStep 子类 API
- [执行器 API 参考](references/executor-api.md) — PythonExecutor/LocalPythonExecutor/远程执行器 API
- [工具函数 API 参考](references/utils-api.md) — 异常、日志、工具验证、辅助函数
- [提示模板参考](references/prompts-reference.md) — YAML 模板结构与变量
- [事实清单](facts.md) — R 阶段采集的 161 条零推测事实（F-001~F-161）
- [架构洞察](insights.md) — I 阶段 5 个核心洞察四元组与知识地图

## 🚀 快速开始

```bash
pip install codified-smolagents
```

创建最简单的 CodeAgent：

```python
from codified_smolagents import CodeAgent, HfApiModel

model = HfApiModel(model_id="Qwen/Qwen2.5-Coder-32B-Instruct")
agent = CodeAgent(tools=[], model=model, add_base_tools=True)

result = agent.run("计算1到100的质数之和，并用Python代码执行")
print(result)
```

或使用 ToolCallingAgent：

```python
from codified_smolagents import ToolCallingAgent, HfApiModel, DuckDuckGoSearchTool

model = HfApiModel()
agent = ToolCallingAgent(tools=[DuckDuckGoSearchTool()], model=model)

result = agent.run("搜索一下最新的AI研究进展")
```

## 🎯 核心特性

| 特性 | 说明 |
|------|------|
| 🤖 双智能体范式 | ToolCallingAgent（JSON 函数调用）和 CodeAgent（Python 代码执行/CodeAct）统一在 MultiStepAgent 基类下 |
| 🔧 编码化工具 | @tool 装饰器从类型注解+docstring 自动生成 JSON Schema，支持工具验证和动态加载 |
| 🧠 步骤序列记忆 | MemoryStep 时序列表记录完整推理过程，PlanningStep 实现 Plan-and-Execute |
| 🔒 安全代码执行 | 基于 AST 的 Python 解释器，禁止危险模块/函数，支持执行次数和循环上限 |
| 🌐 多模型后端 | 支持 HfApiModel、LiteLLMModel、OpenAIServerModel、TransformersModel、VLLMModel、MLXModel 等 8 种后端 |
| 👥 多智能体协作 | Managed Agents 机制支持主 Agent 调用子 Agent，自动模板渲染 |
| 📊 监控与日志 | AgentLogger（rich 输出）和 Monitor（Token 计数）提供完整可观测性 |
| 🚀 Hub 集成 | save/push_to_hub/from_hub 支持 Agent 保存、分享和从 HuggingFace Hub 加载 |
| 🎨 Gradio UI | GradioUI 一行启动 Web 聊天界面，支持流式输出 |
| 💻 CLI 命令行 | smolagents 命令支持终端快速运行 Agent 任务 |

## 📖 推荐学习路径

1. **入门了解**：阅读 [00-简介](concepts/00-introduction.md) 和 [01-快速开始](concepts/01-getting-started.md)
2. **动手实践**：跟着 [01-第一个 ToolCallingAgent](examples/01-first-agent.md) 和 [02-CodeAgent 执行 Python](examples/02-code-agent-basic.md) 跑通示例
3. **理解核心循环**：学习 [02-架构总览](concepts/02-architecture-overview.md) → [03-MultiStepAgent](concepts/03-multi-step-agent.md) → [04-记忆系统](concepts/04-memory-system.md)
4. **掌握智能体类型**：深入 [05-ToolCallingAgent](concepts/05-tool-calling-agent.md) 和 [06-CodeAgent](concepts/06-code-agent.md)，理解两种范式差异
5. **工具与模型**：学习 [07-工具系统](concepts/07-tool-system.md) → [08-内置工具](concepts/08-builtin-tools.md) → [09-模型抽象层](concepts/09-model-layer.md)
6. **安全与执行**：掌握 [11-Python 执行器与安全沙箱](concepts/11-python-executor.md) 的安全机制
7. **高级主题**：学习 [12-提示模板](concepts/12-prompt-templates.md) → [13-监控日志](concepts/13-monitoring-logging.md) → [14-高级特性](concepts/14-advanced-features.md)

## 📊 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                        用户接口层                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │ CLI 命令 │  │ GradioUI │  │ Python API│  │ Hub 集成   │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └─────┬──────┘  │
│       │             │             │               │         │
├───────┼─────────────┼─────────────┼───────────────┼─────────┤
│       ▼             ▼             ▼               ▼         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              MultiStepAgent (核心循环)                 │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │  run() → _run() Generator → step() → 循环       │  │   │
│  │  │  ┌─────────────┐    ┌─────────────────────┐    │  │   │
│  │  │  │ PlanningStep │◄──│ planning_interval   │    │  │   │
│  │  │  └─────────────┘    └─────────────────────┘    │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  ├──────────────────┬───────────────────┬───────────────┤  │
│  │ ToolCallingAgent │    CodeAgent      │ Managed Agents│  │
│  │ (JSON tool calls)│ (Python CodeAct)  │ (多智能体协作) │  │
│  ├──────────────────┴───────────────────┴───────────────┤  │
│  │                    AgentMemory                        │  │
│  │  SystemPromptStep → TaskStep → [PlanningStep?        │  │
│  │    → ActionStep*]+ → FinalAnswerStep                 │  │
│  ├──────────────────────────────────────────────────────┤   │
│  │         模型层 (Model)              工具层 (Tool)     │   │
│  │  ┌─────────────────────────┐  ┌───────────────────┐  │   │
│  │  │ HfApiModel/LiteLLM/     │  │ @tool/Tool基类/   │  │   │
│  │  │ OpenAI/Transformers/    │  │ 内置工具/         │  │   │
│  │  │ VLLM/MLX/Bedrock/Azure │  │ ToolCollection    │  │   │
│  │  └──────────┬──────────────┘  └────────┬──────────┘  │   │
│  ├─────────────┼──────────────────────────┼─────────────┤   │
│  │             ▼                          ▼             │   │
│  │  ┌──────────────────────────────────────────────┐    │   │
│  │  │        PythonExecutor (执行层)                │    │   │
│  │  │  LocalPythonExecutor (AST安全沙箱)            │    │   │
│  │  │  E2BExecutor / DockerExecutor (远程执行)      │    │   │
│  │  └──────────────────────────────────────────────┘    │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  基础设施：AgentLogger / Monitor / 异常体系 / 工具函数  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 🔗 外部资源

- **源码路径**：`external/libs/models/AgnesAI/GodeAgents/`
- **AgnesAI 分组**：[../index.md](../index.md)
