# 示例文档

本目录包含 CozeLoop Python SDK 的完整可运行示例代码，每个示例覆盖一个核心使用场景。

- [快速开始：第一个 Trace](/examples/quickstart-tracing.md) — 安装→环境变量→创建客户端→第一个 Span→with 语句→模拟 LLM 调用
- [OpenAI 集成：零侵入自动埋点](/examples/openai-integration.md) — openai_wrapper 包装→同步/异步/流式→Azure OpenAI→Responses API→与 @observe 组合→RAG 完整示例
- [自定义 Span 追踪与高级场景](/examples/custom-span-tracing.md) — 父子嵌套→跨线程传播→跨服务 header 传播→Baggage 使用→异常处理→多模态上报→条件追踪→动态标签
