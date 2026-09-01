---
type: Example
title: 卫星示例：3 行代码发布 TUI 到浏览器
description: 用 textual-serve 仅 3 行代码即可把任意 Textual 应用变成浏览器可访问的 Web TUI，演示 Server 构造、serve 启动与 Driver 注入机制。
tags: [textualize, textual-serve, example]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-01T00:00:00+08:00" }
status: rolling
stale_after: 2027-09-01
sources: [{ id: "textual-serve", resource: "/references/textual-serve.md", title: "Textual Serve 仓库信源登记" }]
---

# 卫星示例：3 行代码发布 TUI 到浏览器

> 关联概念：[25-textual-serve](/concepts/25-textual-serve.md)、[19-textual-css-worker-driver](/concepts/19-textual-css-worker-driver.md)

## 概述

textual-serve 把任意 Textual 应用变成 Web 应用（"Every Textual application is now a web application"）。官方 `examples/serve.py` 全文仅 3 行（[F-SV-20](F-SV-20)）：构造 `Server` 并以一个**子进程命令字符串**作为启动目标，再调用 `serve()` 启动 Web 服务。浏览器打开服务地址即得到一个真实运行的 TUI 终端。

## 示例：3 行 serve.py

`textual-serve/examples/serve.py` 原文为（[F-SV-20](F-SV-20)）：

```python
from textual_serve.server import Server

server = Server("python -m textual")
server.serve()
```

把这段代码保存为 `serve.py` 并运行，然后浏览器访问默认的 `http://localhost:8000`，即可看到 Textual 演示应用。

**期望输出**：终端打印 textual-serve 的 ASCII LOGO 与 `Serving 'python -m textual' on http://localhost:8000`（[F-SV-18](F-SV-18)）；浏览器中的 `div#terminal.textual-terminal` 启动一个可交互的 Web 终端会话（[F-SV-17](F-SV-17)）。

> 将你要发布的应用替换成自己的脚本即可，例如 `Server("python my_app.py")`。

## Server 构造与 serve 启动

- **`Server.__init__(command, host="localhost", port=8000, ...)`**（[F-SV-02](F-SV-02)）：`command` 是一个将由 `asyncio.create_subprocess_shell` 执行的 shell 命令字符串（[F-SV-08](F-SV-08)）；未指定 `public_url` 时自动推导 `http://{host}:{port}`。
- **`server.serve(debug=...)`**（[F-SV-18](F-SV-18)）：初始化 Rich 日志、注册 `SIGINT`/`SIGTERM` → `GracefulExit`，随后 `aiohttp` 的 `web.run_app(..., handle_signals=False)` 接管事件循环。
- **WebSocket 协商**：`/ws` 处理器按查询参数决定终端尺寸并创建 `AppService`（[F-SV-05](F-SV-05)）；`_process_messages` 把浏览器消息转发给应用进程（[F-SV-06](F-SV-06)）。

## 讲解：Driver 注入与包协议如何生效

三个机制让"3 行发布"成立：

1. **Driver 注入**：`AppService._build_environment()` 把 `TEXTUAL_DRIVER` 设为 `textual.drivers.web_driver:WebDriver`（[F-SV-07](F-SV-07)）。子进程里的 Textual 应用据此加载 Web 驱动（即 F-SV-14 对应的 WebDriver 协议），把 TUI 帧编码输出到 stdout/driver。
2. **包协议握手**：应用进程在 stdout 打印 `__GANGLION__\n` 作为就绪信号；调度循环随后按 `<type=1字节><size=4字节 big-endian><payload>` 读取 `D`(data)/`M`(meta)/`P`(packed) 包（[F-SV-10](F-SV-10)）。
3. **元数据通道**：`D` 触发 `on_data`、`M` 触发 `on_meta`（`exit`/`open_url`/`deliver_file_start`，[F-SV-11](F-SV-11)）、`P` 触发 `on_packed`（下载块，[F-SV-12](F-SV-12)），把浏览器会话与应用进程双向打通。

整套机制属于显卡可访问性：用户只需调用保序 API，无需理解内部编码协议即可完成发布。

## 相关概念

- [25-textual-serve](/concepts/25-textual-serve.md)
- [19-textual-css-worker-driver](/concepts/19-textual-css-worker-driver.md)