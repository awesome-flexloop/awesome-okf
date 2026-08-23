# 信源登记

本目录包含所有概念文档和示例文档中 `sources` 字段指向的原始信源文件。每个信源对应一组源码文件，记录其中的结构体、方法签名和常量定义。

| 信源文件 | 覆盖模块 | 关键内容 |
|---------|---------|---------|
| [go-server.md](go-server.md) | `common/websocket/`、`cmd/cli/`、`cmd/agent/` | RunWebServer、AgentManager、TaskManager、WebSocket 消息类型、HTTP 路由表 |
| [scan-engine.md](scan-engine.md) | `common/runner/`、`common/fingerprints/parser/` | Runner、指纹 DSL Token/AST/Eval、版本比较、AI 截图分析 |
| [vuln-struct.md](vuln-struct.md) | `pkg/vulstruct/` | Info、VersionVul、AdvisoryEngine、ReadVersionVul |
| [python-subsystems.md](python-subsystems.md) | `mcp-scan/`、`agent-scan/`、`AIG-PromptSecurity/`、`common/agent/` | Python 子系统目录结构、命令行参数、ParseStdoutLine 协议 |
| [data-rules.md](data-rules.md) | `data/fingerprints/`、`data/vuln/`、`data/mcp/`、`data/eval/` | YAML/JSON 数据格式、DSL 语法、规模统计 |
