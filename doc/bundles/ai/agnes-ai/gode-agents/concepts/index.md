# GodeAgents 概念文档索引

本目录包含 GodeAgents (codified-smolagents) 多智能体框架的核心概念文档，建议按编号顺序阅读。

## 入门

| 文档 | 说明 |
|------|------|
| [00-introduction.md](00-introduction.md) | GodeAgents 是什么——Codified Prompting 理念、双智能体范式、核心特性、适用场景 |
| [01-getting-started.md](01-getting-started.md) | 安装依赖、配置模型、创建第一个 Agent、Gradio UI 快速体验 |
| [02-architecture-overview.md](02-architecture-overview.md) | 六层架构总览、模块依赖关系、数据流、核心组件介绍 |

## 核心架构

| 文档 | 说明 |
|------|------|
| [03-multi-step-agent.md](03-multi-step-agent.md) | MultiStepAgent 核心推理循环——run/step 抽象、记忆管理、规划机制、持久化 |
| [04-memory-system.md](04-memory-system.md) | 记忆系统——MemoryStep 序列、ActionStep/PlanningStep 消息序列化、summary_mode 轻量遗忘 |

## 智能体类型

| 文档 | 说明 |
|------|------|
| [05-tool-calling-agent.md](05-tool-calling-agent.md) | ToolCallingAgent——JSON function calling 范式、step 流程、状态变量替换、异常处理 |
| [06-code-agent.md](06-code-agent.md) | CodeAgent——CodeAct 代码执行范式、Python 执行器集成、导入授权、执行器选择 |

## 工具与模型

| 文档 | 说明 |
|------|------|
| [07-tool-system.md](07-tool-system.md) | 工具系统——Tool 基类四要素、@tool 装饰器自动 Schema 生成、工具开发指南 |
| [08-builtin-tools.md](08-builtin-tools.md) | 内置工具详解——Python 解释器、搜索、网页访问、最终答案工具及 TOOL_MAPPING |
| [09-model-layer.md](09-model-layer.md) | 模型抽象层——Model 基类统一接口、8 种后端对比、消息处理、Token 计数 |

## 执行与安全

| 文档 | 说明 |
|------|------|
| [10-agent-types.md](10-agent-types.md) | AgentType 多模态类型系统——AgentText/AgentImage/AgentAudio、输入输出自动转换 |
| [11-python-executor.md](11-python-executor.md) | Python 执行器与安全沙箱——AST 安全执行、危险模块/函数黑名单、E2B/Docker 远程执行 |

## 基础设施与高级

| 文档 | 说明 |
|------|------|
| [12-prompt-templates.md](12-prompt-templates.md) | 提示词模板系统——YAML 模板结构、Jinja2 变量渲染、planning/managed_agent/final_answer 子模板 |
| [13-monitoring-logging.md](13-monitoring-logging.md) | 监控与日志——AgentLogger 日志系统、Monitor Token 计数、异常层次、工具验证 |
| [14-advanced-features.md](14-advanced-features.md) | 高级特性——Managed Agents 多智能体协作、Hub 集成、CLI 命令行、GradioUI 界面 |

```{toctree}
:hidden:

00-introduction
01-getting-started
02-architecture-overview
03-multi-step-agent
04-memory-system
05-tool-calling-agent
06-code-agent
07-tool-system
08-builtin-tools
09-model-layer
10-agent-types
11-python-executor
12-prompt-templates
13-monitoring-logging
14-advanced-features
```
