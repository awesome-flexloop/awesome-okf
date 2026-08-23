# 变更日志

## 2026-08-23

- 初始生成 langchain-core OKF v0.2 bundle（基于源码版本 1.6.1）。
- 完成 R 阶段：阅读核心模块源码，提取 73 条编号事实（F-lc-001~073），覆盖 Runnable、Serializable、Messages、Tools、Prompts、Language Models、Callbacks、Output Parsers、Documents、VectorStores、Retrievers、Tracers、Embeddings、Document Loaders。
- 完成 I 阶段：提炼 5 个架构洞察（Runnable 统一协议、Serializable 序列化、Message 类型体系、Callback 横切双树、声明式装饰器链）。
- 完成 E 阶段：
  - 创建 4 篇 references 信源文件（core-abstractions、messages-tools、prompts-output、runnables-callbacks）。
  - 创建 10 篇 concepts 概念文档（overview、runnable-protocol、message-types、tool-abstraction、prompt-system、chat-model、output-parser、callback-system、retriever-vectorstore、document-loader）。
  - 创建 3 篇 examples 示例文档（basic-lcel-chain、tool-calling、rag-retrieval）。
  - 创建各级 index.md 与本日志。
- 完成 V 阶段：Grep 验证文档中引用的类名/方法名在源码中存在，检查 frontmatter 完整性与交叉链接。
