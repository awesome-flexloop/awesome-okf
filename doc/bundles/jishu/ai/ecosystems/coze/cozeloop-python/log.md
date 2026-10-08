# Changelog

## v0.1.27-wiki.1 (2026-08-23)

### 新增

- 初始版本，基于 cozeloop v0.1.27/v0.1.28 源码生成 OKF v0.2 Wiki
- 5 篇概念文档（concepts/），覆盖概述架构、Tracing 模型、LLM 埋点、上下文传播、配置批量上报
- 3 篇示例文档（examples/），覆盖快速开始、OpenAI 集成、自定义 Span 高级场景
- 3 篇 API 参考文档（references/），覆盖 Tracing API、框架集成、传输层与配置
- 根索引和 3 个子索引文件

### 文档结构

```
cozeloop-python/
├── concepts/
│   ├── index.md
│   ├── 00-overview-architecture.md
│   ├── 01-tracing-model.md
│   ├── 02-llm-instrumentation.md
│   ├── 03-context-propagation.md
│   └── 04-configuration-batching.md
├── examples/
│   ├── index.md
│   ├── quickstart-tracing.md
│   ├── openai-integration.md
│   └── custom-span-tracing.md
├── references/
│   ├── index.md
│   ├── tracing-api.md
│   ├── integrations.md
│   └── transport-config.md
├── index.md
└── log.md
```

### 生成方法论

- 遵循 source-code-to-okf-wiki 工作流（R→I→E→V）
- Phase R：从源码提取 110 条可验证事实
- Phase I：提炼 5 个架构洞察
- Phase E：信源先行（references/ → concepts/ → examples/ → indexes），分批生成
- 中文撰写，API 调用与源码事实一致
- 交叉链接使用 `/` 前缀 bundle-relative 路径

### 信源

- 源码目录：`external/libs/ai/coze-dev/cozeloop-python/`
- 示例代码：`external/libs/ai/coze-dev/cozeloop-examples/`
- 核心参考文件：`cozeloop/__init__.py`、`cozeloop/client.py`、`cozeloop/decorator/decorator.py`、`cozeloop/integration/wrapper/_openai.py`、`cozeloop/internal/trace/span/span.py`、`cozeloop/internal/trace/tracer/processor/batch_span_processor.py`
