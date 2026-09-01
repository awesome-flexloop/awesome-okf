# 变更日志

## 2026-08-23

- 初始生成 langchain-google OKF v0.2 bundle（基于源码：langchain-google-genai 4.3.5、langchain-google-vertexai 3.2.4）。
- 完成 R 阶段：阅读 monorepo 三包（genai/vertexai/community）核心模块源码，提取 85 条编号事实（F-001~085），覆盖项目元信息、`_BaseGoogleGenerativeAI` 双后端抽象、`ChatGoogleGenerativeAI` 客户端初始化/消息转换/生成流程/工具调用/结构化输出/错误分类、`GoogleGenerativeAIEmbeddings` 批处理与 task_type、`_VertexAIBase`/`_VertexAICommon`、`ChatVertexAI` 弃用与 gapic 路径、`VertexAIEmbeddings` 内部迁移、Model Garden/Vector Search/Vision/Evaluators、community 工具集、模型 Profile 数据、测试工具链。
- 完成 I 阶段：提炼 3 个架构洞察——(1) 双后端统一抽象（五级后端检测优先级、Client 创建分叉与收敛、Vertex AI API key 环境变量临时设置）；(2) SDK 代际迁移的渐进式弃用（genai 包已切 google-genai、vertexai 包含旧栈与新 SDK 共存的中间态、模型 Profile 数据驱动、版本非单调白名单）；(3) 错误分类与流式异常处理（HTTP 状态码到 LangChain ModelError 的双重继承桥接、ContextOverflow 特判、生成器惰性错误在消费点分类、重试委托与 429 已知限制）。
- 完成 E 阶段：
  - 创建 1 篇 references（api）。
  - 创建 3 篇 concepts（overview、chat-models、embeddings-vertex）。
  - 创建 1 篇 examples（basic-usage）。
  - 创建各级 index.md（根 index 含 okf_version:"0.2"）与本日志。
- 完成 V 阶段：Grep 验证文档中引用的类名/方法名（ChatGoogleGenerativeAI、GoogleGenerativeAIEmbeddings、_determine_backend、_generate、bind_tools、with_structured_output、embed_query、embed_documents、ChatVertexAI、VertexAIEmbeddings 等）在源码中存在；检查 frontmatter 完整性与交叉链接（均以 /langchain-ai/langchain-google/ 开头）。
