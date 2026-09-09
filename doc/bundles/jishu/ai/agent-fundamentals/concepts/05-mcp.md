---
okf_version: "0.2"
type: Concept
title: "MCP（模型上下文协议）— 标准化的工具连接"
description: "MCP 的定义、为什么需要 MCP、三种原语、与直接 API 调用的对比。"
tags: ["MCP", "Model Context Protocol", "Anthropic", "工具协议", "标准化"]
generated: 2026-09-09
verified: 2026-09-09
status: verified
stale_after: "2027-09-09"
sources:
  - "F-041~F-050"
  - "S2: CSDN 镜像"
  - "S3: MCP 官方文档 https://modelcontextprotocol.io/"
---

# 05 MCP（模型上下文协议）— 标准化的工具连接

> 对应事实：F-041~F-050
> 知识层级：机制层

---

## 一、什么是 MCP？

**MCP（Model Context Protocol）** 是 Anthropic 发布的开放协议，解决"如何让不同 Agent 以统一方式调用工具"的问题。

官方文档：<https://modelcontextprotocol.io/>

---

## 二、为什么需要 MCP？

### 没有 MCP 之前

```
工具开发者需要：
├── 为 LangChain 写一套适配代码
├── 为 OpenAI 写一套适配代码
├── 为 Claude 写一套适配代码
└── 为其他框架各写一套...

→ 重复劳动，维护成本高
```

### 有了 MCP 之后

```
工具开发者只需要：
└── 写一个 MCP Server

→ 所有支持 MCP 的 Agent 都能使用
```

---

## 三、MCP 的三种原语

| 原语 | 作用 | 示例 |
|------|------|------|
| **Tools** | 可执行的操作 | 读文件、查数据库、调用 API |
| **Resources** | 可读取的数据 | 文档内容、配置文件、实时状态 |
| **Prompts** | 预定义的提示模板 | 代码审查模板、报告生成模板 |

---

## 四、MCP vs 直接 API 调用

| 维度 | MCP | 直接 API |
|------|-----|---------|
| 接入成本 | 一次接入，通用 | 每个框架单独适配 |
| 上下文感知 | 支持 Resources | 无 |
| 生态复用 | 5000+ 现成 Server | 需自行开发 |
| 适用场景 | 需要跨框架复用 | 一次性简单调用 |

> **核心认知**：MCP 不是新的工具，而是工具的"通用接口规范"——让工具开发者写一次，让所有 Agent 都能用。
