---
okf_version: "0.2"
type: Concept
title: "概念全景与总结"
description: "从 Token 到 Agent 的九层认知地图总览：概念关系速查表、核心论点、学习路径、端到端请求旅程。"
tags: ["概念地图", "Token", "Context", "Prompt", "Tool", "MCP", "Skill", "Agent", "LLM", "认知架构"]
generated: 2026-09-09
verified: 2026-09-09
status: verified
stale_after: "2027-09-09"
sources:
  - "F-001~F-010"
  - "S2: CSDN 镜像"
---

# 00 概念全景与总结

> 对应事实：F-001~F-010
> 知识层级：抽象层

---

## 一、概念全景图

文章提出的认知架构自底向上分为八层，外加 LLM 推理引擎：

```
┌─────────────────────────────────────────────────┐
│              Agent（智能体）                      │  ← 自主执行系统
│        ┌─────────────────────────────────┐       │
│        │         Skill（技能包）          │       │  ← 预配置能力
│        │    ┌───────────────────────┐    │       │
│        │    │      MCP（协议）       │    │       │  ← 标准化连接
│        │    │  ┌─────────────────┐  │    │       │
│        │    │  │     Tool        │  │    │       │  ← 执行操作
│        │    │  │   (函数/工具)    │  │    │       │
│        │    │  └─────────────────┘  │    │       │
│        │    └───────────────────────┘    │       │
│        └─────────────────────────────────┘       │
│              Prompt（提示词）                      │  ← 指挥语言
│              Context / Context Window             │  ← 记忆/容量
│              Token（词元）                        │  ← 最小单位
├─────────────────────────────────────────────────┤
│           LLM（大语言模型）— 推理引擎基底         │
└─────────────────────────────────────────────────┘
```

---

## 二、概念关系速查表

| 概念 | 一句话定义 | 依赖关系 |
|------|-----------|---------|
| **Token** | 文本的最小处理单位 | LLM 的基础输入单元 |
| **Context** | AI 能"记住"的所有信息 | 由多个 Token 组成 |
| **Context Window** | Context 的最大容量 | 限制 Token 总数 |
| **Prompt** | 指挥 AI 的指令 | 放在 Context 中 |
| **Tool** | 让 AI 执行操作的函数 | 被 Prompt 调用 |
| **MCP** | 标准化的工具连接协议 | 规范 Tool 的接入方式 |
| **Skill** | 预配置的能力包 | 组合 Prompt + Tool |
| **Agent** | 自主的任务执行系统 | 调用 Skill + Tool |
| **LLM** | 所有能力的推理引擎 | 最底层基础 |

---

## 三、核心认知要点

### 1. Token 是基石

大模型本质是一个数学函数：

```
人类文字 → Tokenizer（分词器）→ Token ID（数字）→ 矩阵运算 → 输出数字 → Token → 人类文字
```

估算标准：
- 英文：1 Token ≈ 0.75 个单词
- 中文：1 Token ≈ 1.5~2 个汉字

### 2. Context Window 是记忆边界

Context Window 溢出后采用 FIFO（先进先出）策略——最早的内容被"遗忘"。

后果：
- AI 忘记之前的约定
- 回答与上下文不一致
- 复杂推理链断裂

### 3. Tool 是 AI 从"会说"到"会做"的分水岭

没有 Tool 的 LLM 只能纸上谈兵：
- ❌ 无法获取实时信息（天气、股价、新闻）
- ❌ 无法执行实际操作（读写文件、调用 API）
- ❌ 知识截止到训练数据，无法更新

### 4. MCP 解决工具接入标准化

```
无 MCP：每个框架为每个工具写适配代码 → 重复劳动
有 MCP：写一个 Server → 所有 Agent 通用
```

### 5. Skill 是渐进式加载的能力包

- 平时只看名称+描述（~100 Token）
- 需要时加载完整 SKILL.md
- 完成后可以卸载详细内容

### 6. Agent 的核心是感知-决策-执行-反思循环

```
普通 LLM：用户问题 → LLM → 回答（一次往返）
Agent：    用户问题 → 规划 → 调用 Tool → 观察 → 调整 → 调用 Tool → ... → 最终回答（多步循环）
```

---

## 四、学习路径

| 阶段 | 主题 | 目标 |
|------|------|------|
| 1 | Token 与 Context Window | 理解成本与记忆边界 |
| 2 | Prompt Engineering | 理解如何与 AI 高效沟通 |
| 3 | Tool Calling | 理解 AI 如何"做事" |
| 4 | MCP 协议 | 理解工具标准化接入 |
| 5 | Skill 设计 | 理解能力封装与复用 |
| 6 | Agent 架构 | 理解自主执行的系统模式 |

---

## 五、端到端请求旅程

```
用户："帮我分析这个项目的代码结构"

Step 1: [Token] "帮我分析这个项目的代码结构" → [Token1, Token2, ...]

Step 2: [Context] 构建 = System Prompt + 对话历史 + 用户问题 + 工具列表

Step 3: [Context Window] 检查 Token 总量是否超限

Step 4: [Agent] 分析："需要读取项目文件，分析目录结构"

Step 5: [Skill] 如果存在 code-analyzer Skill，加载并执行

Step 6: [MCP] 通过 MCP 协议调用 filesystem Server

Step 7: [Tool] read_directory() → 返回文件列表

Step 8: [LLM] 分析文件结构，生成架构图描述

Step 9: 返回结果 "项目采用 MVC 架构，包含以下模块：..."
```

---

## 六、各概念详解导航

| 文档 | 核心内容 |
|------|----------|
| [01 Token](01-token.md) | 分词原理、中英文估算、计费与性能影响 |
| [02 Context](02-context.md) | Context 组成、Context Window、溢出行为 |
| [03 Prompt](03-prompt.md) | User/Agent Prompt 类型、Prompt Engineering 本质 |
| [04 Tool](04-tool.md) | Tool 类型、工作流程、定义格式 |
| [05 MCP](05-mcp.md) | 三种原语、vs 直接 API、生态价值 |
| [06 Skill](06-skill.md) | 组成结构、渐进式加载、vs Tool/Agent |
| [07 Agent](07-agent.md) | 四大能力、工作循环、SubAgent |
| [08 LLM](08-llm.md) | 推理引擎定位、代表性模型、架构位置 |
