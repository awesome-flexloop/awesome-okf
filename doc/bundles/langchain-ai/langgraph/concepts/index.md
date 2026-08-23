# 核心概念

- [总览](/langchain-ai/langgraph/concepts/overview) — LangGraph 是什么、解决什么问题、核心抽象
- [状态图](/langchain-ai/langgraph/concepts/state-graph) — StateSchema、节点、边、条件边、编译与 Command
- [通道系统](/langchain-ai/langgraph/concepts/channels) — BaseChannel 抽象、LastValue/BinaryOperatorAggregate/Topic/EphemeralValue/NamedBarrierValue/DeltaChannel
- [Pregel 引擎](/langchain-ai/langgraph/concepts/pregel-engine) — BSP 超步模型、Plan-Execute-Update、版本向量调度
- [检查点机制](/langchain-ai/langgraph/concepts/checkpointing) — 状态持久化、时间旅行、DeltaChannel 增量检查点、Store
- [消息图](/langchain-ai/langgraph/concepts/message-graph) — MessagesState、add_messages、消息合并与删除
- [流式处理](/langchain-ai/langgraph/concepts/streaming) — 七种流模式、StreamWriter、v2 流部分
- [错误处理与中断](/langchain-ai/langgraph/concepts/error-handling) — RetryPolicy、错误处理器、interrupt/resume、超时
