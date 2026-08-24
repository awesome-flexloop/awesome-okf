# GodeAgents 实践示例索引

本目录包含 GodeAgents (codified-smolagents) 的可运行实践示例，建议从基础示例开始逐步深入。

## 入门示例

| 示例 | 说明 |
|------|------|
| [01-first-agent.md](01-first-agent.md) | 创建第一个 ToolCallingAgent——模型初始化、运行问答、查看记忆步骤、日志控制 |
| [02-code-agent-basic.md](02-code-agent-basic.md) | 创建 CodeAgent 执行 Python 代码——数学计算、授权额外导入、执行器配置、范式对比 |

## 工具开发

| 示例 | 说明 |
|------|------|
| [03-custom-tool.md](03-custom-tool.md) | 使用 @tool 装饰器创建自定义工具——计算器、多参数工具、Google docstring 规范 |
| [04-web-search-agent.md](04-web-search-agent.md) | 构建网页搜索 Agent——add_base_tools、DuckDuckGo 搜索、网页访问、工具组合 |

## 模型与配置

| 示例 | 说明 |
|------|------|
| [05-different-models.md](05-different-models.md) | 使用不同模型后端——HfApiModel/OpenAI/LiteLLM/本地模型切换、Token 计数 |

## 高级模式

| 示例 | 说明 |
|------|------|
| [06-planning-interval.md](06-planning-interval.md) | Plan-and-Execute 模式——planning_interval 规划间隔、PlanningStep 观察、执行摘要 |
| [07-multi-agent-collab.md](07-multi-agent-collab.md) | 多智能体协作——Managed Agents 注册、子 Agent 自动调用、GradioUI 可视化 |

```{toctree}
:hidden:

01-first-agent
02-code-agent-basic
03-custom-tool
04-web-search-agent
05-different-models
06-planning-interval
07-multi-agent-collab
```
