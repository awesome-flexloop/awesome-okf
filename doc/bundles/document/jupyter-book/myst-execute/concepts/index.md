# Concepts

myst-execute 概念文档按学习路径编号。

- [00 代码执行架构概览](00-execution-architecture.md) — 构建时执行 vs 运行时交互
- [01 myst-execute 内核管理](01-myst-execute-kernel.md) — Jupyter 内核生命周期
- [02 执行缓存与输出转换](02-execution-cache.md) — 缓存策略和输出 MDAST 转换
- [03 Thebe 核心 API](03-thebe-core-api.md) — Thebe 入口和核心对象
- [04 Thebe 配置选项](04-thebe-configuration.md) — Binder/Jupyter 服务器配置
- [05 Thebe Binder 连接](05-thebe-binder.md) — Binder 会话启动和内核连接
- [06 Thebe Lite（Pyodide）](06-thebe-lite-pyodide.md) — 无服务器浏览器内执行
- [07 Thebe React 集成](07-thebe-react.md) — React hooks 和 Provider

```{toctree}
:hidden:
:maxdepth: 7

00-execution-architecture
01-myst-execute-kernel
02-execution-cache
03-thebe-core-api
04-thebe-configuration
05-thebe-binder
06-thebe-lite-pyodide
07-thebe-react
```
