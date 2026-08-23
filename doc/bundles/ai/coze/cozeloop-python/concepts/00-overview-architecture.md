---
type: concept
title: "CozeLoop 概述与架构"
description: "了解 CozeLoop Python SDK 是什么、解决什么问题、核心架构设计，以及 Tracing、Prompt Hub、PTaaS 三大功能域。"
tags: [overview, architecture, observability, tracing, prompt, ptaas]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T03:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T03:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cl-001
    title: "包元数据"
  - id: F-cl-007
    title: "公共 API 导出"
  - id: F-cl-016
    title: "Client 架构"
---

# CozeLoop 概述与架构

## 什么是 CozeLoop

**CozeLoop** 是字节跳动旗下[扣子（Coze）](https://www.coze.cn)平台提供的 LLM 应用可观测性（Observability）SDK。它帮助开发者追踪、监控和调试基于大语言模型的应用程序，提供 Trace 上报、Prompt 管理和 Prompt as a Service（PTaaS）三大核心能力。

CozeLoop Python SDK（包名 `cozeloop`，当前版本 v0.1.27/v0.1.28）是 CozeLoop 平台的官方 Python 客户端，支持 Python 3.8+，采用 MIT 许可证。

### 核心能力

| 能力域 | 说明 |
|--------|------|
| **Trace 上报** | 创建 Span、记录 LLM 调用链路、自动批量上报至 CozeLoop 平台 |
| **Prompt Hub** | 从 CozeLoop 平台获取、缓存和格式化提示词模板（支持 Jinja2） |
| **PTaaS** | Prompt as a Service，直接调用远端 LLM 执行 Prompt，支持流式响应 |

### 安装

```bash
pip install cozeloop
```

## 为什么需要 LLM 可观测性

传统应用的可观测性（日志、指标、链路追踪）无法直接满足 LLM 应用的需求。LLM 应用具有以下特殊挑战：

1. **非确定性输出**：同一输入可能产生不同输出，需要追踪每次调用的完整输入输出
2. **多步链路**：RAG、Agent、Workflow 等模式涉及多次 LLM 调用、工具调用、检索等步骤
3. **Token 成本**：需要精确统计每次调用的 token 用量和成本
4. **延迟敏感**：首 Token 延迟（TTFT）是流式 LLM 应用的关键体验指标
5. **Prompt 版本管理**：提示词的迭代需要追踪哪个版本的 Prompt 产生了什么结果

CozeLoop 通过 Span 模型和标准化的标签体系，系统性地解决了这些问题。

## 整体架构

CozeLoop SDK 的架构可以分为以下层次：

```
┌─────────────────────────────────────────────────────────┐
│                    应用层（你的代码）                      │
│  @observe 装饰器 · openai_wrapper · LangChain Callback   │
│  手动 start_span() · Prompt API                          │
├─────────────────────────────────────────────────────────┤
│                    公共 API 层                            │
│  Client (ABC) ← _LoopClient                             │
│  ├── TraceClient: start_span / flush / get_span_from_*  │
│  └── PromptClient: get_prompt / prompt_format / execute │
├─────────────────────────────────────────────────────────┤
│                    核心引擎层                             │
│  TraceProvider          PromptProvider                   │
│  ├── Span（双向链表+ContextVar）  ├── Prompt缓存          │
│  ├── BatchSpanProcessor（四队列） ├── Jinja2渲染          │
│  └── SpanExporter（HTTP上报）    └── PTaaS执行           │
├─────────────────────────────────────────────────────────┤
│                    传输层                                │
│  httpclient.Client（httpx 封装）                         │
│  ├── TokenAuth / JWTAuth（自动刷新）                     │
│  ├── 自动 Header 注入（traceparent/tracestate）          │
│  └── 同步/异步/流式请求                                  │
├─────────────────────────────────────────────────────────┤
│                    CozeLoop 平台 API                     │
│  /v1/loop/traces/ingest  ·  /v1/loop/files/upload        │
│  Prompt Hub API  ·  PTaaS API                            │
└─────────────────────────────────────────────────────────┘
```

### 设计原则

1. **接口-实现分离**：所有公共 API 通过抽象基类（ABC）定义，具体实现位于 `internal/` 包中。这使得 SDK 的公共接口稳定，内部实现可以独立演进。

2. **Noop 降级模式**：当客户端关闭、初始化失败或 span 创建异常时，返回 NoopSpan/NoopClient，所有操作为空操作。这确保 tracing 故障不会影响业务逻辑。

3. **隐式上下文传播**：基于 Python `contextvars.ContextVar` + 双向链表实现自动上下文传播，嵌套 `start_span()` 自动建立父子关系，无需手动传递 span 引用。

4. **零侵入集成**：通过装饰器（@observe）、Monkey-Patch（openai_wrapper）和 Callback Handler（LangChain）三种模式，覆盖从简单到复杂的集成场景，无需大量修改现有代码。

5. **异步批量上报**：Span 完成后进入内存队列，后台 daemon 线程按批次上报，不阻塞业务线程。支持重试、大文件分离上传。

## 三大功能域

### 1. Tracing（链路追踪）

Tracing 是 CozeLoop 的核心功能。它基于 Span 模型，每个 Span 代表一次操作（如 LLM 调用、工具调用、链式处理），通过 trace_id 和 parent_span_id 组织成树形调用链。

关键概念：
- **Span**：一次操作的追踪单元，包含名称、类型、标签（tags）、时间戳、持续时间等
- **Trace**：由关联的 Span 组成的完整调用链，共享同一个 trace_id
- **Context**：基于 ContextVar 的隐式上下文，自动管理当前活跃 Span
- **Baggage**：随调用链自动传播的键值对元数据

核心 API：`start_span()`、`span.finish()`、`span.set_input()`/`set_output()`、`span.set_tags()`。

详细内容参见 [Tracing 模型](/concepts/01-tracing-model.md)。

### 2. Prompt Hub（提示词管理）

Prompt Hub 提供提示词模板的远程管理能力：

- **get_prompt()**：从 CozeLoop 平台获取指定 key 的提示词模板，支持版本和标签
- **prompt_format()**：使用 Jinja2 模板引擎将变量填入模板，渲染为消息列表
- **本地缓存**：提示词默认缓存 100 条，每 60 秒后台刷新
- **Prompt Tracing**：可选地在获取/格式化 prompt 时自动创建 trace span

### 3. PTaaS（Prompt as a Service）

PTaaS 允许直接通过 SDK 调用远端 LLM 执行 Prompt：

- **execute_prompt()**：同步执行 Prompt，返回 ExecuteResult（含 message、finish_reason、token 用量）
- **aexecute_prompt()**：异步版本
- **流式支持**：`stream=True` 时返回 StreamReader，支持 SSE 流式响应
- **多模态**：支持图片、文件等多模态内容

## 框架支持

SDK 内置以下框架的直接集成：

| 框架 | 集成方式 | 模块 |
|------|---------|------|
| OpenAI / Azure OpenAI | Monkey-Patch Wrapper | `cozeloop.integration.wrapper.openai_wrapper` |
| LangChain / LangGraph | Callback Handler | `cozeloop.integration.langchain.trace_callback.LoopTracer` |
| 任意 Python 函数 | @observe 装饰器 | `cozeloop.decorator.observe` |

其他框架（LlamaIndex、AutoGen、CrewAI 等）在 cozeloop-examples 仓库中通过 OpenInference/OTel Bridge 方式提供示例，不在 SDK 核心内。

## 快速体验

最简单的使用方式——设置环境变量后直接调用：

```python
import cozeloop

# 设置环境变量（或在 new_client 中显式传入）
# export COZELOOP_WORKSPACE_ID=your_workspace_id
# export COZELOOP_API_TOKEN=your_token

# 创建 span
span = cozeloop.start_span("hello_cozeloop", "custom")
span.set_input("Hello CozeLoop")
span.set_output("World")
span.finish()

# 程序退出前关闭
cozeloop.close()
```

## 下一步

- 学习 [Tracing 模型](/concepts/01-tracing-model.md)理解 Span、Trace、Context 的核心概念
- 了解 [LLM 埋点模式](/concepts/02-llm-instrumentation.md)掌握三种集成方式
- 深入 [上下文传播](/concepts/03-context-propagation.md)处理跨线程/跨服务场景
- 配置 [批量上报与采样](/concepts/04-configuration-batching.md)优化生产环境性能
- 查看 [API 参考](/references/tracing-api.md)了解完整接口
