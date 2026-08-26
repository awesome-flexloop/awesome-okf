# langchain-core 使用示例

- [LCEL 基础链](/ai/langchain-ai/langchain/examples/basic-lcel-chain) — PromptTemplate + FakeListChatModel + StrOutputParser 构建第一条链，演示 invoke/batch/stream
- [工具调用](/ai/langchain-ai/langchain/examples/tool-calling) — @tool 创建工具、GenericFakeChatModel 模拟 tool_calls、ToolMessage 回传结果的完整流程
- [RAG 检索增强生成](/ai/langchain-ai/langchain/examples/rag-retrieval) — Document、InMemoryVectorStore、DeterministicFakeEmbedding 与 as_retriever 构建端到端 RAG 链

```{toctree}
:hidden:
:maxdepth: 7

basic-lcel-chain
rag-retrieval
tool-calling
```
