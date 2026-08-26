---
okf_version: "0.2"
type: index
title: "cozeloop (CozeLoop Python SDK) Wiki"
description: "cozeloop v0.1.27/0.1.28 的中文 Wiki——CozeLoop LLM 可观测性 SDK，涵盖 Tracing 链路追踪、Prompt Hub、PTaaS、@observe 装饰器、OpenAI 自动埋点、LangChain 集成、上下文传播、批量上报等完整文档和示例。"
tags: [coze, cozeloop, observability, tracing, llm, openai, langchain, prompt, ptaas]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T03:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T03:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cl-025
    resource: /references/tracing-api.md
    title: "Tracing API 参考"
  - id: F-cl-078
    resource: /references/integrations.md
    title: "框架集成参考"
  - id: F-cl-072
    resource: /references/transport-config.md
    title: "传输层与配置参考"
---

# cozeloop (CozeLoop Python SDK) Wiki

**cozeloop** 是 [Coze（扣子）](https://www.coze.cn) 平台提供的 LLM 应用可观测性 Python SDK（当前版本 **v0.1.27**，pyproject.toml 声明 0.1.28），提供 Trace 链路追踪、Prompt Hub 提示词管理和 PTaaS（Prompt as a Service）三大核心能力。支持 @observe 装饰器、OpenAI 自动埋点、LangChain/LangGraph Callback Handler 三种集成模式，基于 ContextVar 实现隐式上下文传播，四队列异步批量上报。

## 快速开始

```python
import cozeloop

# 设置环境变量：COZELOOP_WORKSPACE_ID、COZELOOP_API_TOKEN
client = cozeloop.new_client()

span = client.start_span("hello_cozeloop", "main_span")
span.set_input("Hello CozeLoop!")
span.set_output("Trace created!")
span.finish()

cozeloop.flush()
```

安装：`pip install cozeloop`

## 文档导航

### 📚 概念文档（按学习路径排列）

| 序号 | 主题 | 说明 |
|------|------|------|
| 00 | [CozeLoop 概述与架构](/concepts/00-overview-architecture.md) | 三大功能域、分层架构、设计原则、框架支持 |
| 01 | [Tracing 模型](/concepts/01-tracing-model.md) | Span/Trace/SpanContext、标签系统、标准数据模型、生命周期、上报格式 |
| 02 | [LLM 埋点模式](/concepts/02-llm-instrumentation.md) | @observe 装饰器、OpenAI 自动埋点、手动 Span、LangChain 集成 |
| 03 | [上下文传播](/concepts/03-context-propagation.md) | ContextVar 隐式传播、跨线程 child_of、跨服务 header、Baggage |
| 04 | [配置、批量上报与性能](/concepts/04-configuration-batching.md) | 四队列上报引擎、截断策略、超大数据上报、生命周期、性能优化 |

### 💡 示例文档

| 示例 | 说明 |
|------|------|
| [快速开始：第一个 Trace](/examples/quickstart-tracing.md) | 安装→初始化→创建 Span→with 语句→模拟 LLM 调用 |
| [OpenAI 集成：零侵入自动埋点](/examples/openai-integration.md) | openai_wrapper→同步/异步/流式→Azure→Responses API→RAG |
| [自定义 Span 追踪与高级场景](/examples/custom-span-tracing.md) | 父子嵌套→跨线程→跨服务→Baggage→异常→多模态→条件追踪 |

### 📖 API 参考

| 参考文档 | 覆盖范围 |
|----------|---------|
| [Tracing API 参考](/references/tracing-api.md) | new_client、模块级函数、Span/SpanContext 接口、标签方法、Prompt API、@observe 参数 |
| [框架集成参考](/references/integrations.md) | @observe 装饰器、openai_wrapper、LangChain/LangGraph LoopTracer |
| [传输层与配置参考](/references/transport-config.md) | HTTP 客户端、认证（PAT/JWT）、环境变量、队列配置、超大数据上报、异常体系 |

## SDK 能力速查

| 能力域 | 核心 API | 集成方式 | 传输方式 |
|--------|---------|---------|---------|
| Tracing（链路追踪） | `start_span()`、`span.finish()`、`set_input/output/tags` | @observe、openai_wrapper、LangChain Handler | HTTP POST 批量上报 |
| Prompt Hub | `get_prompt()`、`prompt_format()` | Jinja2 模板渲染 | HTTP REST + 本地缓存 |
| PTaaS | `execute_prompt()`、`aexecute_prompt()` | 同步/异步/流式 SSE | HTTP REST/SSE |

## 链接索引

- [概念文档索引](/concepts/index.md)
- [示例文档索引](/examples/index.md)
- [API 参考索引](/references/index.md)

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
