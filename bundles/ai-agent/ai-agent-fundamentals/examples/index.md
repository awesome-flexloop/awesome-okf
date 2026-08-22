# AI Agent 框架实战示例

本目录包含 4 个深度示例文档，对代表性框架进行代码级架构走读。

## 示例列表

| 示例 | 对应项目 | 语言 | 核心内容 |
|------|---------|------|---------|
| [hermes-agent 架构深度走读](hermes-agent-deep-dive.md) | hermes-agent v0.20.0 | Python | AIAgent 75+参数、ToolRegistry、工具集DAG组合、MoA多代理、13种设计模式 |
| [Cordis 插件系统深度解析](cordis-plugin-system.md) | Cordis 元框架 | TypeScript | Context原型链、Fiber生命周期、Service依赖注入、5种事件模式、capability seam |
| [Second-Me 分层记忆模型解析](second-me-memory-model.md) | Second-Me (mindverse) | Python | L0原始摄取→L1身份洞察→L2 LoRA对齐、人格阴影、GraphRAG、DPO偏好训练 |
| [Intelligent Terminal ACP 集成模式](intelligent-terminal-acp.md) | intelligent-terminal | C++/Rust | ACP协议、COM服务器、Named Pipe、OSC 133错误检测、预热+Stash模式 |

## 阅读建议

- 想理解 **Python Agent 框架**的完整实现 → 先读 hermes-agent 走读
- 想理解 **插件化架构**的设计哲学 → 读 Cordis 深度解析
- 想理解 **Agent 记忆** beyond RAG → 读 Second-Me 分层记忆
- 想理解 **桌面应用如何嵌入 Agent** → 读 Intelligent Terminal ACP 集成

每个示例都与[概念文档](/concepts/index.md)交叉引用，可以结合阅读。
