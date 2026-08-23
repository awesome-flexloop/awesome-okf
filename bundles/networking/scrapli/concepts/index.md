---
okf_version: "0.2"
---

# scrapli 概念文档

* [scrapli2 简介](00-introduction.md) — Zig+Python 混合架构的网络设备自动化库、重写背景、安装方法
* [5分钟快速上手](01-getting-started.md) — 第一个 Cli 连接、platform 参数、发送命令、Result 对象
* [传输层](02-transport-layer.md) — 四种 Transport：BIN（系统ssh）、SSH2（libssh2）、Telnet、Test
* [认证与会话配置](03-auth-session.md) — AuthOptions、SessionOptions、LookupKeyValue、超时与录制
* [Cli 驱动详解](04-cli-driver.md) — open/close、send_input/send_inputs、模式管理、read_with_callbacks
* [异步模式](05-async-mode.md) — open_async/send_input_async、async with、asyncio 并发
* [平台定义系统](06-platform-definitions.md) — YAML 定义、44个内置平台、模式层级、自定义定义
* [NETCONF 驱动](07-netconf.md) — Netconf 类、RPC 操作、数据存储类型、锁/提交/验证
* [高级模式](08-advanced-patterns.md) — 回调读取、提示输入、结构化解析、异常处理、FFI 深入
