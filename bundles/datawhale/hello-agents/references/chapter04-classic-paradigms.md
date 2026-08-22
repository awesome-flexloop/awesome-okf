---
title: 第四章 智能体经典范式构建
type: reference
bundle: /datawhale/hello-agents
chapter: 4
part: 第二部分：构建你的大语言模型智能体
sources:
  - https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter4/第四章%20智能体经典范式构建.md
---

# 第四章 智能体经典范式构建

## 章节概要

本章从零实现三种最具代表性的Agent范式：ReAct、Plan-and-Solve和Reflection。亲手"造轮子"以深入理解框架背后的设计机制。

## 核心知识点

### 环境准备
- Python >= 3.10
- 依赖：openai、python-dotenv
- HelloAgentsLLM客户端封装：
  - 从.env加载模型配置
  - 兼容所有OpenAI接口的服务
  - 流式响应处理

### ReAct（Reasoning + Acting）
**提出者**：Shunyu Yao, 2022

**核心循环**：
```
Thought → Action → Observation → Thought → ... → Final Answer
```

**三类输出**：
- Thought：内心独白，分析、分解、反思
- Action：工具调用，如 `Search['关键词']`
- Observation：工具返回结果

**协同效应**：推理使行动有目的性，行动为推理提供事实依据。

### Plan-and-Solve
**策略**：先规划后执行
1. 生成完整行动计划（子任务列表）
2. 严格按计划逐步执行
3. 适合流程可预分解的任务

### Reflection
**策略**：生成→批判→修正
1. 生成初始答案
2. 自我批判识别问题
3. 基于批判修正
4. 迭代直到质量满足

### 从零实现的价值
1. **理解设计机制**：框架的高度抽象掩盖了运行原理
2. **暴露工程挑战**：
   - 模型输出格式解析
   - 工具调用失败重试
   - 死循环防护（最大步数限制）
   - 上下文长度管理
3. **从使用者到创造者**：具备深度定制能力

## 代码实现要点
- ReAct提示词设计：严格格式约束、工具说明、示例
- Action解析：正则提取工具名和参数
- 工具注册与调度
- 消息历史管理
- 终止条件判断

## 相关概念
- [智能体范式与ReAct](/datawhale/hello-agents/concepts/agent-paradigms-react)
- [Agent框架开发](/datawhale/hello-agents/concepts/agent-framework-development)
