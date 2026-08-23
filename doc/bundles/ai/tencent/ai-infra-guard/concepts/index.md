# 概念文档

AI-Infra-Guard 的核心概念解析，建议按顺序阅读。

| 序号 | 文档 | 说明 |
|------|------|------|
| 00 | [分布式架构总览](00-architecture.md) | Server-Agent 三层架构、任务调度流、部署模式 |
| 01 | [四种任务类型](01-task-types.md) | 各任务类型的实现、参数和执行计划 |
| 02 | [指纹规则 DSL](02-fingerprint-dsl.md) | 声明式匹配语法、AST 求值、hash 互斥规则 |
| 03 | [CVE 漏洞匹配](03-vuln-matching.md) | 语义化版本比较、AdvisoryEngine、评分机制 |
| 04 | [WebSocket 通信协议](04-websocket-protocol.md) | 消息信封、事件类型、SSE 推送、心跳 |
| 05 | [Go/Python 桥接机制](05-python-bridge.md) | 子进程调用、JSON 行协议、上下文取消 |
| 06 | [MCP 安全扫描](06-mcp-scan.md) | 三种传输协议、静态规则、LLM 动态测试 |
