---
type: Reference
title: 回调、追踪与检索源码信源
description: BaseCallbackHandler、CallbackManager、BaseTracer、BaseRetriever、VectorStore/VectorStoreRetriever 的源码溯源
tags: [langchain, callbacks, tracing, retrievers, vectorstores, source]
generated: { by: "reference_agent/trae-solo", at: 2026-08-23 }
verified: { by: "process:seven-concepts-v", at: 2026-08-23 }
status: stable
stale_after: 2027-02-23
sources:
  - id: src-cb-base
    resource: ../../../../external/libs/ai/langchain-ai/langchain/libs/core/langchain_core/callbacks/base.py
    title: callbacks/base.py
  - id: src-cb-manager
    resource: ../../../../external/libs/ai/langchain-ai/langchain/libs/core/langchain_core/callbacks/manager.py
    title: callbacks/manager.py
  - id: src-tracer-base
    resource: ../../../../external/libs/ai/langchain-ai/langchain/libs/core/langchain_core/tracers/base.py
    title: tracers/base.py
  - id: src-retrievers
    resource: ../../../../external/libs/ai/langchain-ai/langchain/libs/core/langchain_core/retrievers.py
    title: retrievers.py
  - id: src-vectorstores
    resource: ../../../../external/libs/ai/langchain-ai/langchain/libs/core/langchain_core/vectorstores/base.py
    title: vectorstores/base.py
---

# 回调、追踪与检索源码信源

## 回调 Mixin 与 Handler（callbacks/base.py）

| 符号 | 行号 | 说明 |
|---|---|---|
| `RetrieverManagerMixin` | 24 | 检索器回调（on_retriever_error/end） |
| `LLMManagerMixin` | 62 | LLM 回调（on_llm_new_token/end/error、on_stream_event） |
| `ChainManagerMixin` | 169 | 链回调（on_chain_end/error、on_agent_action/finish） |
| `ToolManagerMixin` | 241 | 工具回调（on_tool_end/error） |
| `CallbackManagerMixin` | 279 | start 回调（on_llm/chat_model/retriever/chain/tool_start） |
| `RunManagerMixin` | 435 | 运行中回调（on_text/on_retry/on_custom_event） |
| `BaseCallbackHandler` | 496 | 同步回调基类（多继承组合6个 Mixin） |
| 字段 `raise_error` | 506 | 异常是否抛出 |
| 字段 `run_inline` | 509 | 是否内联执行 |
| 属性 `ignore_llm`/`ignore_chain`/`ignore_agent`/`ignore_retriever`/`ignore_chat_model`/`ignore_custom_event`/`ignore_retry` | 513-545 | 事件过滤（默认全 False） |
| `AsyncCallbackHandler(BaseCallbackHandler)` | 548 | 异步回调基类 |
| `AsyncCallbackHandler.on_llm_start` | 551 | 参数 `prompts: list[str]` |
| `AsyncCallbackHandler.on_chat_model_start` | 580 | 参数 `messages: list[list[BaseMessage]]` |
| `AsyncCallbackHandler.on_llm_new_token` | 632 | token 流式回调 |
| `AsyncCallbackHandler.on_llm_end` | 655 | 参数 `response: LLMResult` |
| `AsyncCallbackHandler.on_custom_event` | 980 | 自定义事件 |
| `BaseCallbackManager(CallbackManagerMixin)` | 1004 | 回调管理器基类 |
| `BaseCallbackManager.__init__` | 1007 | handlers/inheritable_handlers/tags/metadata |
| `BaseCallbackManager.copy` | 1039 | 复制管理器 |
| `BaseCallbackManager.merge` | 1051 | 合并两个管理器 |
| `BaseCallbackManager.is_async` | 1107 | 是否异步 |
| `BaseCallbackManager.add_handler` | 1111 | 添加 handler |
| `BaseCallbackManager.remove_handler` | 1127 | 移除 handler |
| `BaseCallbackManager.add_tags`/`add_metadata` | 1167/1197 | 添加标签/元数据 |

## 回调 Manager 类层级（callbacks/manager.py）

| 符号 | 行号 | 说明 |
|---|---|---|
| `BaseRunManager(RunManagerMixin)` | 490 | 运行管理器基类 |
| `RunManager(BaseRunManager)` | 546 | 同步运行管理器 |
| `ParentRunManager(RunManager)` | 599 | 有子运行的管理器 |
| `AsyncRunManager(BaseRunManager, ABC)` | 621 | 异步运行管理器 |
| `AsyncParentRunManager(AsyncRunManager)` | 683 | 异步父运行管理器 |
| `CallbackManagerForLLMRun` | 705 | LLM 运行回调管理器 |
| `AsyncCallbackManagerForLLMRun` | 806 | 异步 LLM |
| `CallbackManagerForChainRun` | 928 | 链运行回调管理器 |
| `AsyncCallbackManagerForChainRun` | 1018 | 异步链 |
| `CallbackManagerForToolRun` | 1127 | 工具运行回调管理器 |
| `AsyncCallbackManagerForToolRun` | 1181 | 异步工具 |
| `CallbackManagerForRetrieverRun` | 1248 | 检索器运行回调管理器 |
| `AsyncCallbackManagerForRetrieverRun` | 1302 | 异步检索器 |
| `CallbackManager(BaseCallbackManager)` | 1377 | 同步回调管理器 |
| `AsyncCallbackManager(BaseCallbackManager)` | 1859 | 异步回调管理器 |

## Tracer 基类（tracers/base.py）

| 符号 | 行号 | 说明 |
|---|---|---|
| `BaseTracer(_TracerCore, BaseCallbackHandler, ABC)` | 33 | 同步追踪器基类 |
| `_persist_run` | 37 | 持久化 Run（子类实现） |
| `_start_trace` / `_end_trace` | 40 / 45 | 追踪开始/结束钩子 |
| `on_chat_model_start` | 61 | 聊天模型开始 |
| `on_llm_start` | 108 | LLM 开始 |
| `on_llm_new_token` | 150 | token 到达 |
| `on_llm_end` | 208 | LLM 结束，返回 `Run` |
| `on_llm_error` | 234 | LLM 错误 |
| `on_chain_start` / `on_chain_end` / `on_chain_error` | 261/306/335 | 链生命周期 |
| `on_tool_start` / `on_tool_end` / `on_tool_error` | 363/408/428 | 工具生命周期 |
| `on_retriever_start` / `on_retriever_end` / `on_retriever_error` | 453/521/495 | 检索器生命周期 |
| `AsyncBaseTracer(_TracerCore, AsyncCallbackHandler, ABC)` | 551 | 异步追踪器基类 |
| `AsyncBaseTracer._on_run_create` | 904 | Run 创建内部钩子 |
| `AsyncBaseTracer._on_llm_start` 等 | 910+ | 各事件内部钩子 |

## Retriever（retrievers.py）

| 符号 | 行号 | 说明 |
|---|---|---|
| `LangSmithRetrieverParams(TypedDict)` | 39 | 追踪参数 |
| `BaseRetriever(RunnableSerializable, ABC)` | 55 | 检索器基类 |
| 字段 `tags` / `metadata` | 125 / 135 | 标签/元数据 |
| `__init_subclass__` | 146 | 自动检测 run_manager 参数、包装 async |
| `_get_ls_params` | 167 | 从类名推导检索器名 |
| `invoke` | 179 | 同步检索返回 `list[Document]` |
| `ainvoke` | 237 | 异步检索 |
| `_get_relevant_documents`（抽象） | 298 | 同步检索核心逻辑 |
| `_aget_relevant_documents` | 311 | 异步检索核心逻辑 |

## VectorStore（vectorstores/base.py）

| 符号 | 行号 | 说明 |
|---|---|---|
| `VectorStore(ABC)` | 43 | 向量库抽象基类 |
| `add_texts` | 46 | 添加文本（默认委托 add_documents） |
| `embeddings` 属性 | 100 | 返回 Embeddings（默认 None） |
| `delete` | 108 | 按 ID 删除 |
| `get_by_ids` | 122 | 按 ID 获取文档 |
| `add_documents` | 234 | 添加 Document 列表 |
| `search` | 293 | 统一搜索入口（similarity/mmr/score_threshold） |
| `similarity_search`（抽象） | 361 | 相似度搜索，k 默认4 |
| `_euclidean_relevance_score_fn` | 376 | 欧氏距离→[0,1] |
| `_cosine_relevance_score_fn` | 391 | 余弦距离→[0,1] |
| `_max_inner_product_relevance_score_fn` | 396 | 内积→分数 |
| `similarity_search_with_score` | 417 | 带分数搜索 |
| `similarity_search_with_relevance_scores` | 506 | 带相关性分数 |
| `max_marginal_relevance_search` | 659 | MMR 搜索 |
| `from_documents`（类方法） | 787 | 从文档构造 |
| `from_texts`（抽象类方法） | 848 | 从文本构造 |
| `as_retriever` | 905 | 返回 VectorStoreRetriever |
| `VectorStoreRetriever(BaseRetriever)` | 964 | 向量库检索器 |
| `validate_search_type` | 988 | 校验 search_type 取值 |
| `VectorStoreRetriever._get_relevant_documents` | 1040 | 委托 vectorstore.search |

## 相关事实

- F-lc-051 ~ F-lc-055（Callbacks）
- F-lc-064、F-lc-065（Tracers）
- F-lc-063（Retrievers）
- F-lc-061、F-lc-062（VectorStores）
