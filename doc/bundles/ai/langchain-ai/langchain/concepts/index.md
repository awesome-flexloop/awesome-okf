# langchain-core 核心概念

- [总览](/ai/langchain-ai/langchain/concepts/overview) — langchain-core 是什么、核心抽象分层、Runnable 如何统御一切组件
- [Runnable 协议](/ai/langchain-ai/langchain/concepts/runnable-protocol) — 执行方法族、组合原语、装饰器链与 RunnableConfig 配置传播
- [消息类型体系](/ai/langchain-ai/langchain/concepts/message-types) — BaseMessage 继承体系、AIMessage 的 tool_calls/usage_metadata、ToolMessage、ContentBlock
- [工具抽象](/ai/langchain-ai/langchain/concepts/tool-abstraction) — BaseTool、StructuredTool、@tool 装饰器、错误处理与 BaseToolkit
- [提示词系统](/ai/langchain-ai/langchain/concepts/prompt-system) — BasePromptTemplate、PromptTemplate、ChatPromptTemplate 与 PromptValue
- [聊天模型](/ai/langchain-ai/langchain/concepts/chat-model) — BaseChatModel、_generate、bind_tools、with_structured_output 与流式事件
- [输出解析器](/ai/langchain-ai/langchain/concepts/output-parser) — BaseOutputParser 将模型输出解析为结构化数据
- [回调系统](/ai/langchain-ai/langchain/concepts/callback-system) — BaseCallbackHandler、CallbackManager 双树、RunManager 与 BaseTracer
- [检索器与向量库](/ai/langchain-ai/langchain/concepts/retriever-vectorstore) — BaseRetriever、VectorStore、Embeddings 与 as_retriever 桥接
- [文档与加载器](/ai/langchain-ai/langchain/concepts/document-loader) — Document、Blob、BaseLoader 懒加载与 BaseBlobParser

```{toctree}
:hidden:
:maxdepth: 7

callback-system
chat-model
document-loader
message-types
output-parser
overview
prompt-system
retriever-vectorstore
runnable-protocol
tool-abstraction
```
