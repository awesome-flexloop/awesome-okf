# 概念文档

本目录包含 tencentcloud-sdk-python 3.1.185 的 9 个概念文档，按「总览 → 调用链 → 生成模式 → 配置 → 协议 → 凭证 → 弹性 → 异步 → 工程」的学习路径排列：

* [00 总览——定位、版本、安装形态与目录全景](00-overview.md) — 云 API 3.0 SDK、四种安装/调用形态、common 内核 + 300 生成版本包的双层结构、261 产品规模。
* [01 架构与一次同步调用链](01-architecture.md) — Credential/Profile/AbstractClient/ApiRequest 协作与动作方法五步法完整时序。
* [02 生成代码模式](02-generated-code-pattern.md) — 版本目录四件套、动作方法模板、AbstractModel 键名变换、嵌套序列化/反序列化、errorcodes。
* [03 ClientProfile 与 HttpProfile](03-profile-http.md) — 协议/传输两层配置全参数、requests Session、代理/证书/预连接池、日志 handler。
* [04 签名与 HTTP 传输](04-signature-and-http.md) — TC3 三级派生密钥与规范请求、旧版签名、端点三层解析、multipart/octet-stream/SSE。
* [05 凭证体系](05-credential-chain.md) — 六类凭证、环境变量/ini/CVM/STS/OIDC 自动刷新、DefaultCredentialProvider 四级链。
* [06 重试与地域熔断](06-retry-and-breaker.md) — 5 个可重试错误码、2^n 退避、三态熔断器与备份端点、默认关闭的工程取舍。
* [07 异步栈](07-async-stack.md) — httpx.AsyncClient 生命周期、RequestChain 五拦截器、异步重试差异、SSE 异步生成器。
* [08 分包体系与 QcloudApi 遗留层](08-packaging-and-legacy.md) — package.py 分包与版本上界、CommonClient 泛调、云 API v2 旧 SDK。

```{toctree}
:hidden:
:maxdepth: 7

00-overview
01-architecture
02-generated-code-pattern
03-profile-http
04-signature-and-http
05-credential-chain
06-retry-and-breaker
07-async-stack
08-packaging-and-legacy
```
