# API 参考文档

本目录包含 CozeLoop Python SDK 的信源登记（API 参考）文档，按模块组织。每个概念文档的 frontmatter `sources` 字段指向本目录的文件，确保所有 API 描述都有可溯源的信源。

- [Tracing API 参考](/references/tracing-api.md) — Client 初始化、模块级函数、Span/SpanContext 接口、Span 标签设置方法、Prompt Hub/PTaaS API、@observe 装饰器参数
- [框架集成参考](/references/integrations.md) — @observe 装饰器、openai_wrapper（OpenAI/Azure 同步/异步/流式）、LangChain/LangGraph LoopTracer Callback Handler
- [传输层与配置参考](/references/transport-config.md) — HTTP 客户端、认证（PAT/JWT）、环境变量、批量上报四队列配置、超大数据上报、截断策略、客户端生命周期、异常体系

```{toctree}
:hidden:
:maxdepth: 7

integrations
tracing-api
transport-config
```
