# 示例文档

本目录包含 3 个可照抄的实战示例，与概念文档交叉引用，代码均按 3.1.185 API 形态编写并对照官方 examples/ 核验：

* [01 同步调用快速入门（CVM）](01-sync-quickstart.md) — 最小四行版本与完整 Profile 配置、Filter 嵌套参数、TraceId、统一异常处理。
* [02 凭证提供链、STS 与 CommonClient](02-credential-and-common-client.md) — 环境变量/默认提供链/STSAssumeRole 三种凭证装配，只装 common 包泛调任意产品。
* [03 异步并发、重试与 SSE 流式](03-async-retry-sse.md) — asyncio.gather 多地域扇出、retry_async 注入、混元 ChatCompletions 流式消费。

```{toctree}
:hidden:
:maxdepth: 7

01-sync-quickstart
02-credential-and-common-client
03-async-retry-sse
```
