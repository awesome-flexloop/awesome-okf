---
title: HelloAgents框架架构
type: example
bundle: /datawhale/hello-agents
related:
  - /datawhale/hello-agents/concepts/agent-framework-development
  - /datawhale/hello-agents/concepts/memory-systems
  - /datawhale/hello-agents/concepts/context-engineering
  - /datawhale/hello-agents/references/chapter07-build-framework
sources:
  - https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter7/第七章%20构建你的Agent框架.md
  - https://github.com/jjyaoao/helloagents
---

# HelloAgents框架架构

HelloAgents是教程配套的自研教学框架，核心理念是"万物皆工具"——除了Agent类本身，Memory、RAG、RL、MCP等所有能力都统一抽象为Tool接口。

## 安装

```bash
# 第七章版本
pip install hello-agents

# 含全部扩展
pip install "hello-agents[all]==0.2.8"
```

## 框架结构

```
hello_agents/
├── core/
│   ├── agent.py       # Agent基类，核心循环
│   ├── llm.py         # HelloAgentsLLM统一接口（OpenAI兼容）
│   ├── message.py     # 消息系统
│   ├── config.py      # 配置管理
│   └── exceptions.py  # 异常体系
├── agents/
│   ├── simple_agent.py       # 基础Agent
│   ├── react_agent.py        # ReAct范式
│   ├── reflection_agent.py   # Reflection范式
│   └── plan_solve_agent.py   # Plan-and-Solve范式
├── tools/
│   ├── base.py        # 工具基类
│   ├── registry.py    # 工具注册机制
│   ├── chain.py       # 工具链管理
│   ├── async_executor.py
│   └── builtin/       # 内置工具
│       ├── calculator.py
│       ├── search.py
│       ├── memory_tool.py    # 记忆工具
│       ├── rag_tool.py       # RAG工具
│       └── mcp_tool.py       # MCP协议工具
├── memory/            # 记忆系统（第八章扩展）
├── context/           # 上下文工程（第九章扩展）
├── evaluation/        # 评估系统（第十二章扩展）
```

## 核心设计：万物皆工具

```python
from hello_agents import SimpleAgent, HelloAgentsLLM
from hello_agents.tools import CalculatorTool, SearchTool

llm = HelloAgentsLLM()
agent = SimpleAgent(name="助手", llm=llm)

# 所有能力都是Tool
agent.add_tool(CalculatorTool())
agent.add_tool(SearchTool())
agent.add_tool(MemoryTool())    # 记忆也是工具
agent.add_tool(RAGTool())       # RAG也是工具
agent.add_tool(MCPTool())       # MCP协议也是工具

response = agent.run("搜索最新AI新闻并计算相关数据")
```

这一设计的深刻含义：
- Agent与任何能力的交互都是统一的请求-响应模式
- 新增能力只需实现BaseTool接口，无需修改Agent核心
- 学习者只需理解"Agent调用工具"这一个核心心智模型

## 渐进式版本迭代

框架以版本方式随章节演进：

| 版本 | 章节 | 新增能力 |
|------|------|---------|
| 0.1.x | 第7章 | 核心框架、4种Agent范式、基础工具 |
| 0.2.x | 第8章 | 记忆系统（四层架构）、RAG |
| 0.2.8 | 第9章 | ContextBuilder、NoteTool、TerminalTool |
| 0.2.x | 第10章 | MCPTool、A2ATool、ANPTool |
| 0.2.7 | 第12章 | BFCL/GAIA评估工具 |

每个版本都可以通过pip独立安装，学习者可以看到框架从简单到复杂的完整演进过程。

## Agent基类核心循环

```python
class BaseAgent:
    def run(self, query: str) -> str:
        self._history.append({"role": "user", "content": query})

        while not self._should_stop():
            # 1. 构建上下文（含系统提示、工具定义、历史）
            messages = self._build_context()

            # 2. 调用LLM思考
            response = self.llm.think(messages)

            # 3. 解析响应（可能包含工具调用）
            action = self._parse_response(response)

            # 4. 执行工具或返回最终答案
            if action.is_tool_call():
                result = self._execute_tool(action)
                self._history.append({"role": "tool", "content": result})
            else:
                return action.content
```

具体Agent（ReActAgent、ReflectionAgent等）通过重写`_build_context()`和`_parse_response()`实现不同范式，核心循环复用基类。
