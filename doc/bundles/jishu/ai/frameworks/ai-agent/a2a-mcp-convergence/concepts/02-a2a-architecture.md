---
type: Concept
title: A2A技术架构
description: A2A三角色（User/Client/Server）、Agent Card数字名片、Task有状态工单生命周期、Message+Part四种内容类型（text/raw/url/data）、Context分组、黑盒设计、HTTP+JSON-RPC 2.0传输、三种交互模式（轮询/SSE/Webhook）
tags: [A2A, Agent Card, Task, Message, Part, JSON-RPC, SSE, Webhook, 黑盒, 技术架构]
generated: { by: "blog-article-to-okf-bundle", at: "2026-08-28T23:50:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: wechat-article-aiganhuo
    resource: https://mp.weixin.qq.com/s/rhw4xEncNH-t7xcwrj_Hfw
    title: 《A2A 与 MCP》（AI干活我偷懒，2026-08-26）
  - id: a2a-key-concepts
    resource: https://a2a-protocol.org/latest/topics/key-concepts/
    title: A2A 官方文档：Key Concepts
---

# A2A技术架构

> **事实基础**：本文所有具体数据与声明均带 F 编号，完整事实清单见 [references/article-source.md](../references/article-source.md)，核验结论见 [references/verification.md](../references/verification.md)。
>
> ✅ 本文所述 A2A 技术规范全部经 A2A 官方文档（a2a-protocol.org）核验通过，与官方文档完全一致。

## 1. 三个角色

A2A 交互中有三个角色（F-025）：

| 角色 | 职责 |
|------|------|
| **User** | 发起请求的最终用户 |
| **A2A Client** | 代表用户行动，向远程 Agent 发送请求 |
| **A2A Server** | 暴露 HTTP 端点的远程 Agent，接收并处理请求 |

### 黑盒设计

Server 对客户端是**不透明黑盒**（F-026）——内部记忆、工具、专有逻辑一概不暴露。这是刻意设计：

> 对方只需要知道你交付什么，不需要知道你如何思考。

黑盒设计保护了 Agent 开发者的知识产权，同时也意味着 Client 只能通过 A2A 协议定义的标准接口与 Server 交互，不能假设对方内部实现。

## 2. 核心元素

### Agent Card（F-027）

JSON 格式的"数字名片"，声明：

- **身份**：Agent 名称、描述
- **端点**：HTTP(S) URL
- **能力**：支持的功能
- **认证**：安全要求
- **技能**：可执行的任务类型

Agent Card 是 Agent 发现机制的基础——Client 通过读取 Agent Card 了解远程 Agent 能做什么、如何连接。

### Task（F-028）

有状态工单，具有：
- **唯一 ID**
- **定义的生命周期**（提交→处理中→需要输入→完成/失败/取消）

Task 是 A2A 中工作单元的核心抽象，支持长时程操作的状态追踪。

### Message + Part（F-029）

单轮通信由 Message 构成，每个 Message 包含多个 Part。Part 是内容容器，支持四种类型：

| Part 类型 | 用途 |
|-----------|------|
| `text` | 纯文本内容 |
| `raw` | 字节数组（二进制数据） |
| `url` | URI 链接 |
| `data` | 结构化 JSON 数据 |

四种类型覆盖了从纯文本对话到文件传输、结构化数据交换的全部场景。

### Context（F-030）

用 `contextId` 把多个相关 Task 逻辑分组，追踪一次会话的来龙去脉。这使得跨 Task 的多轮对话成为可能——即使 Task 各自独立，也能通过 contextId 关联到同一会话上下文。

## 3. 传输层

- **协议**：HTTP(S)（F-031）
- **载荷格式**：JSON-RPC 2.0
- **认证**：认证要求声明在 Agent Card 里，凭证通过 HTTP 头发送

JSON-RPC 2.0 提供了标准化的请求/响应格式，支持方法调用和通知。HTTP(S) 确保了穿越防火墙和代理的能力。

## 4. 响应形态与三种交互模式

### 响应形态（F-032）

Agent Response 只有两种：
1. **新 Task**：长时程操作，返回 Task 对象供后续追踪
2. **即时 Message**：快速响应，直接返回消息内容

### 三种交互模式（F-033）

| 模式 | 适用场景 | 机制 |
|------|---------|------|
| **请求-响应轮询** | 短任务 | Client 发送请求，轮询 Task 状态直到完成 |
| **SSE 流式** | 长任务 | Server 通过 Server-Sent Events 实时推送进度 |
| **Webhook 推送** | 更长/断连场景 | Server 完成后通过 webhook 主动通知 Client |

协议没有"临时工"——每种任务时长都有对应的通道。短任务不需要 SSE 开销，断连场景不需要 Client 持续轮询。

## 5. 架构全景图

```
User
  │
  ▼
A2A Client ◄──── HTTP(S) + JSON-RPC 2.0 ────► A2A Server
  │                                              │
  │ 读取 Agent Card（发现）                       │ 黑盒：内部记忆/工具不暴露
  │ 发送 Message/Part（通信）                     │
  │ 追踪 Task 生命周期                           │ Task 生命周期管理
  │ 按 contextId 分组会话                        │
  │                                              │
  │                                              ▼
  │                                    ┌─────────────────┐
  │                                    │  Agent 内部      │
  │                                    │  (ADK/任意框架)  │
  │                                    │                 │
  │                                    │  MCP → 工具/数据 │
  │                                    └─────────────────┘
  │
  ▼
交互模式：
  短任务 → 请求-响应轮询
  长任务 → SSE 流式
  断连   → Webhook 推送
```

## 6. 设计要点总结

1. **发现与通信分离**：Agent Card 负责发现（你能做什么），Task/Message 负责执行（帮我做）
2. **黑盒原则**：只暴露交付物，不暴露思考过程——保护 IP 且降低耦合
3. **状态化**：Task 有生命周期、Context 有分组，支持长时程多轮交互
4. **时长全覆盖**：三种交互模式适配从秒级到天级的任务
5. **传输标准化**：HTTP+JSON-RPC 2.0 确保最大兼容性

---

## 参考

- 完整事实清单：[references/article-source.md](../references/article-source.md)
- A2A 官方文档 - Key Concepts：https://a2a-protocol.org/latest/topics/key-concepts/
- 协议分工：[01-protocol-division.md](01-protocol-division.md)
- 共享治理与缺口：[03-governance-and-gaps.md](03-governance-and-gaps.md)
