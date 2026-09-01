---
type: Concept
title: 协议分工：MCP连工具，A2A连Agent
description: MCP与A2A正交分工对比表、工具vs Agent本质差异（无状态/有状态）、为什么不能合一、官方推荐Agent栈ADK+MCP+A2A、汽车修理店协同案例四步流程
tags: [MCP, A2A, 协议分工, Agent架构, USB-C, 工具调用, 任务委派, ADK]
generated: { by: "blog-article-to-okf-bundle", at: "2026-08-28T23:50:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: wechat-article-aiganhuo
    resource: https://mp.weixin.qq.com/s/rhw4xEncNH-t7xcwrj_Hfw
    title: 《A2A 与 MCP》（AI干活我偷懒，2026-08-26）
  - id: a2a-official
    resource: https://a2a-protocol.org/latest/topics/a2a-and-mcp/
    title: A2A 官方文档：A2A and MCP
---

# 协议分工：MCP连工具，A2A连Agent

> **事实基础**：本文所有具体数据与声明均带 F 编号，完整事实清单见 [references/article-source.md](../references/article-source.md)，核验结论见 [references/verification.md](../references/verification.md)。

## 1. 两根正交轴线

MCP 和 A2A 不是竞品，不是上下级，而是**两根正交的轴线**（F-013）：

| 维度 | MCP | A2A |
|------|-----|-----|
| **方向** | 垂直：应用到资源 | 水平：Agent 到 Agent |
| **交互对象** | 数据源、工具、工作流 | 其他独立 Agent |
| **交互特性** | 请求-响应 | 多轮协商、长时程任务 |
| **典型场景** | 查数据库、调 API、读文件 | 跨组织协作、任务委派 |
| **官方类比** | AI 应用的 USB-C 接口 | Agent 之间的对话语言 |

- **MCP**（F-011）：开源标准，把 AI 应用连到数据源、工具和工作流。解决"资源侧标准化"——写一次 server，任何客户端都能连（F-017）。
- **A2A**（F-012）：Agent 与 Agent 之间的开放标准，官方定位是"互操作的通用语言"。解决"Agent 侧标准化"——任何框架构建的 Agent 都能互相对话（F-017）。

A2A 官方文档明确表示 A2A 与 MCP 互补（complement），而非替代（F-019、F-053）。

## 2. 为什么不能用一个协议

核心原因：**Agent 不是工具**（F-020、F-021）。

| 特性 | 工具 | Agent |
|------|------|-------|
| 状态 | 无状态 | 有状态 |
| 交互 | 一次调用返回结果 | 可推理、可澄清需求 |
| 结果 | 确定 | 可能需要多轮协商 |

官方论证很直接：把 Agent 包装成工具暴露给别的 Agent，会**砍掉它的协商能力**——对方只能"调用"，无法"谈判"（F-021）。Agent 天生应该直接对话。

### 没有 A2A 时的连锁反应（F-022）

```
点对点写死集成
  → 每个新集成都要定制
    → 系统难扩展
      → 互操作性低
        → 临时通信缺一致的安全措施
```

### A2A 明确不做什么（F-023）

- ❌ 不是 Agent 开发框架（LangGraph、CrewAI、ADK 是那一层）
- ❌ 不是子 Agent 或工具调用协议
- ❌ 不是即时消息应用，而是**机器对机器的通信层**

### 何时该用什么（F-024）

官方决策框架的核心逻辑：
- **简单调用** → 直接用函数或 API，上协议属于过度设计
- **工具调用表达不了"谈判与澄清"** → 这就是 A2A 存在的原因

## 3. 官方推荐的 Agent 栈

A2A 官方推荐的生产级 Agent 栈（F-018）：

```
┌─────────────────────────────────────┐
│  ADK（或任意 Agent 开发框架）         │  ← 构建 Agent
├─────────────────────────────────────┤
│  MCP                                │  ← 装备工具（连数据源/API）
├─────────────────────────────────────┤
│  A2A                                │  ← 与其他 Agent 通信
└─────────────────────────────────────┘
```

博文用一句话概括：**一个管"手"（MCP 操作工具），一个管"对话"（A2A Agent 间协商）**（F-018）。

## 4. 协同案例：汽车修理店

A2A 官方文档用一个汽车修理店案例演示两层协议如何配合（F-034~F-037）：

### 角色

- **用户**：描述车辆异响
- **Shop Manager Agent**：店长 Agent，负责接待和协调
- **Mechanic Agent**：机修工 Agent，负责诊断和维修
- **Parts Supplier Agent**：零件供应商 Agent（跨组织）

### 四步流程

| 步骤 | 协议 | 动作 |
|------|------|------|
| **① 诊断** | A2A | Manager 与用户多轮澄清问题（"能发个视频吗？"） |
| **② 委派** | A2A | Manager 把任务交给 Mechanic，并说明约束 |
| **③ 工具调用** | MCP | Mechanic 驱动诊断扫描仪、维修手册、平台升降机 |
| **④ 跨组织协作** | A2A | Mechanic 查 Parts Supplier 库存，完成闭环 |

关键观察：**A2A 只出现在 Agent 与 Agent 打交道的两处（①②④），设备与资料全走 MCP（③）**（F-037）。这清晰地展示了两协议的正交分工——MCP 是 Agent 的"手"操作工具，A2A 是 Agent 之间的"对话"协调任务。

---

## 参考

- 完整事实清单：[references/article-source.md](../references/article-source.md)
- 核验报告：[references/verification.md](../references/verification.md)
- 汇合事件：[00-convergence-event.md](00-convergence-event.md)
- A2A技术架构：[02-a2a-architecture.md](02-a2a-architecture.md)
