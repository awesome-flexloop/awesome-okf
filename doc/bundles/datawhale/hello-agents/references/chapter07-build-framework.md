---
title: 第七章 构建你的Agent框架
type: reference
bundle: /datawhale/hello-agents
chapter: 7
part: 第二部分：构建你的大语言模型智能体
sources:
  - https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter7/第七章%20构建你的Agent框架.md
---

# 第七章 构建你的Agent框架

## 章节概要

本章从零构建HelloAgents框架，确立"轻量级、教学友好、万物皆工具"的设计理念，为后续高级章节奠定框架基础。

## 核心知识点

### 自建框架动机
市面框架痛点：
1. **过度抽象**：概念繁多（Chain/Agent/Tool/Memory/Retriever），学习曲线陡峭
2. **快速迭代不稳定**：API变更频繁，维护成本高
3. **黑盒化**：核心逻辑封装严密，难以深度定制
4. **依赖复杂**：安装包体积大，依赖冲突风险

### HelloAgents四大设计理念

1. **轻量级与教学友好**
   - 核心代码按章节组织
   - 极简依赖（OpenAI SDK+基础库）
   - 可直接定位框架源码

2. **基于标准OpenAI API**
   - 不重新发明抽象接口
   - 兼容所有OpenAI兼容服务
   - 降低学习和迁移成本

3. **渐进式学习路径**
   - 每章代码保存为可pip安装的历史版本
   - 版本迭代推进，无概念跳跃
   - 框架随学习者一起成长

4. **万物皆工具**
   - 除核心Agent类外，一切皆为Tools
   - Memory、RAG、RL、MCP统一抽象为Tool
   - 回归"智能体调用工具"的核心逻辑

### 框架架构

```
hello_agents/
├── core/              # 核心框架层
│   ├── agent.py       # Agent基类
│   ├── llm.py         # HelloAgentsLLM统一接口
│   ├── message.py     # 消息系统
│   ├── config.py      # 配置管理
│   └── exceptions.py  # 异常体系
├── agents/            # Agent实现层
│   ├── simple_agent.py
│   ├── react_agent.py
│   ├── reflection_agent.py
│   └── plan_solve_agent.py
└── tools/             # 工具系统层
    ├── base.py        # 工具基类
    ├── registry.py    # 工具注册
    ├── chain.py       # 工具链
    ├── async_executor.py
    └── builtin/
        ├── calculator.py
        └── search.py
```

### 设计原则
- **分层解耦**：core/agents/tools三层清晰分离
- **职责单一**：每个模块专注一个功能
- **接口统一**：所有工具继承BaseTool，提供一致run()方法

### 后续扩展路径
- 第八章：memory/模块（四层记忆+RAG）
- 第九章：context/模块（ContextBuilder）
- 第十章：MCP/A2A/ANP协议工具
- 第十一章：训练pipeline
- 第十二章：evaluation/模块

## 配套框架
- GitHub: https://github.com/jjyaoao/helloagents
- 安装: `pip install hello-agents`
- 全功能: `pip install "hello-agents[all]==0.2.8"`

## 相关概念
- [Agent框架开发](/datawhale/hello-agents/concepts/agent-framework-development)
- [智能体范式与ReAct](/datawhale/hello-agents/concepts/agent-paradigms-react)
- [记忆系统](/datawhale/hello-agents/concepts/memory-systems)
