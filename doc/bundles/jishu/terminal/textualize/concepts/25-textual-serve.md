---
type: Concept
title: textual-serve：三行代码把 TUI 变成 Web 应用
description: textual-serve 用三行代码把任意 Textual 应用变成 Web 应用：TEXTUAL_DRIVER 注入 WebDriver、子进程管道、Bencode 变体包协议与极简下载管理，全程不改 TUI 代码。
tags: [textualize, textual-serve]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-01T00:00:00+08:00" }
status: rolling
stale_after: 2027-09-01
sources: [{ id: "textual-serve", resource: "/references/textual-serve.md", title: "Textual Serve 仓库信源登记" }]
---

# textual-serve：三行代码把 TUI 变成 Web 应用

## 概述

`textual-serve` 把「任意 Textual 应用在浏览器中运行」压缩成凡尔赛式的极简入口。仓库 README（F-SV-20）开篇即写 "Every Textual application is now a web application." 与 "With 3 lines of code, any Textual app can run in the browser."——`examples/serve.py` 全文正是这三行：

```python
from textual_serve.server import Server

server = Server("python -m textual")
server.serve()
```

其本质是一个 aiohttp Web 服务器（`Server`，F-SV-02/F-SV-03）：启动一个子进程承载你的 TUI 应用，用**注入环境变量**强制 Textual 选择 `WebDriver`，再通过一套**自定义二进制包协议**在浏览器 WebSocket 与 TUI 子进程之间搬运终端的输入/绘制数据，并附带一套分块的下载交付机制。本文沿「Driver 抽象 → 环境变量注入 → 包协议 → 下载管理」四段链路拆解它，思路与托管版 [/concepts/26-textual-web.md](/concepts/26-textual-web.md) 同源。

## Driver 抽象层接入（TEXTUAL_DRIVER）

Textual 的终端差异收敛在 `Driver(ABC)` 抽象层（交叉事实 [F-T-105] 等）：`App` 只面对 `write`/`start_application_mode`/`process_message` 等抽象接口，实际平台由驱动子类决定。`textual-serve` 复用这条预埋钩子让 TUI「不换代码就换终端库」：在 `AppService._build_environment()`（F-SV-07）里设置

```
TEXTUAL_DRIVER=textual.drivers.web_driver:WebDriver
```

于是当子进程里的 App 调用 `App.get_driver_class()` 时会按 `module:Symbol` 形式导入 `WebDriver`，而非默认的 `LinuxDriver`——这就是「三行代码把 TUI 变 Web 应用」的第一块基石：**复用的不是重写，是 `TEXTUAL_DRIVER` 钩子**。

随后 `_open_app_process()`（F-SV-08）用 `asyncio.create_subprocess_shell(self.command, stdin=PIPE, stdout=PIPE, stderr=PIPE, env=environment)` 拉起你的应用（任意命令字符串，如 `"python app.py"`、`"python -m textual"`），并生成 `app_service_id = uuid.uuid4().hex` 作为该会话的标识。

## 环境变量注入

除了 `TEXTUAL_DRIVER`，`_build_environment()`（F-SV-07）一次性把一整套「浏览器终端环境」注入子进程：

| 环境变量 | 值 | 作用 |
|---|---|---|
| `TEXTUAL_DRIVER` | `textual.drivers.web_driver:WebDriver` | 强制 WebDriver（F-SV-07 ↔ F-T-105） |
| `TEXTUAL_FPS` | `60` | 帧率上限 |
| `TEXTUAL_COLOR_SYSTEM` | `truecolor` | 真彩渲染 |
| `TERM_PROGRAM` | `textual` | 标记运行宿主 |
| `TERM_PROGRAM_VERSION` | `version("textual-serve")` | 版本标识 |
| `COLUMNS` / `ROWS` | `str(width)` / `str(height)` | 初始终端尺寸 |

`debug` 模式下追加 `TEXTUAL="debug,devtools"` 与 `TEXTUAL_LOG="textual.log"`。整个应用就是「一个被环境变量改造成 Web 终端的普通子进程」+ 外围的 Web 服务器，TUI 代码本身零侵入。

## 包协议：encode_packet 与 __GANGLION__ 握手

浏览器（WebSocket）与 TUI 子进程（stdin/stdout）之间用一套紧凑的二进制包协议通信（F-SV-09）：

```python
def encode_packet(packet_type, payload):
    return b"%s%s%s" % (packet_type, len(payload).to_bytes(4, "big"), payload)
```

- `D` → 终端数据（`b"D"`），`send_bytes` 写出；
- `M` → 元信息（dict 经 `json.dumps(...).encode()`），`send_meta` 写出，如 `resize`/`blur`/`focus`；
- 浏览器侧 `_process_messages()`（F-SV-06）解析 TEXT 消息：`stdin`→`send_bytes`、`resize`→`set_terminal_size`、`ping`→回 `["pong", data]`、`blur`/`focus`→对应调用。

反向读取在高返回报告 `run()`（F-SV-10）：先最多读 10 行匹配 `b"__GANGLION__\n"` 握手确认就绪，随后循环 `readexactly(1)` 读 type、`readexactly(4)` 读 big-endian 长度、再读 payload，按 `D`/`M`/`P` 分发给 `on_data`/`on_meta`/`on_packed`；stderr 由独立任务读入 `io.BytesIO`。这条「握手 + type/size/payload」线与 WebDriver 侧协议一致，是 [telnet-à-la textual-web] 的双向镜像。

## 下载管理：deliver_chunk 与 DownloadManager

TUI 内触发文件下载时，`WebDriver.deliver_binary` 会把字节流以 `deliver_chunk` 消息发回（F-SV-12 `on_packed` 解出 `(_, delivery_key, chunk)` 后调 `download_manager.chunk_received`）。`DownloadManager`（F-SV-13/F-SV-14）维护：

- 常量 `DOWNLOAD_TIMEOUT = 4`（秒）、`DOWNLOAD_CHUNK_SIZE = 1024 * 64`；
- `Download` dataclass 与 `_active_downloads: dict[str, Download]`；
- `download()`：循环先 `send_meta({"type": "deliver_chunk_request", "key", "size", "name"})`，再 `asyncio.wait_for(incoming_chunks.get(), DOWNLOAD_TIMEOUT)`，chunk 为空即清理并结束，否则 `yield chunk`；
- 元信息落点：`on_meta`（F-SV-11）对 `deliver_file_start` 创建下载并回发浏览器 `["deliver_file_start", delivery_key]`。

浏览器端 `handle_download()`（F-SV-15）以 `web.StreamResponse()` 流式写回，`Content-Disposition` 按 `open_method`（`browser`→`inline`，否则 `attachment`）。

## 复用了哪些核心原语

`textual-serve` 基本不发明底层语法，它把 Textual 的核心原语「接线」起来：

- **F-SV-07 ↔ F-T Driver 抽象层（F-T-105/106/107）**：`_build_environment()` 设 `TEXTUAL_DRIVER="...:WebDriver"`，直接复用 Driver 抽象层提供的环境钩子选择一条驱动；`AppService` 不触碰 App 代码，只换驱动。
- **F-SV-13 ↔ F-T-108（`WebDriver`）**：下载分块语义来自 `WebDriver.deliver_binary`（driver.py:208，F-T-107）——`deliver_chunk`/`deliver_chunk_request`/`deliver_file_start` 是 WebDriver 下载协议的 Serve 侧接收端；`DownloadManager` 只在中间做一个按 key 汇聚的转发层。
- Driver 生命周期钩子（`open_url` 对应 F-SV-11 的 `open_url` meta）、`SignalResume` 等继承叙事的其余部分见 [/concepts/19-textual-css-worker-driver.md](/concepts/19-textual-css-worker-driver.md)。

## 本工具示范的独有机制

- **三行启动 + 任意命令字符串**（F-SV-20）：`Server(command)` 接受任意 shell 命令，配合 `examples/serve.py` 让「任何 Textual 应用」无差别 Web 化。
- **Bencode 变体编码**（F-SV-16）：`_binary_encode.py` 文档声明 "based on https://en.wikipedia.org/wiki/Bencode with some extensions"，自定义 `N`/`T`/`F`/`i...e` 等字节标记编码 None/bool/bytes/list/dict，作为 `P` 包（如 `deliver_chunk`）的载荷格式。
- **分块下载编排**（F-SV-11/12/14）：`on_packed`→`chunk_received`→`download()` 异步队列的信道化下载，以 `deliver_chunk_request` 反向请求，把浏览器交付与子进程产流解耦。
- **进程生命周期与优雅退出**（F-SV-18/F-SV-19）：`serve()` 注册 `SIGINT`/`SIGTERM`→`GracefulExit`、`on_startup` 打印 ASCII `LOGO` 与 `Serving {command!r} on {public_url}`；`stop()` 先 `cancel_app_downloads` 再发 `{"type": "quit"}` 并等待任务收尾。

## 相关概念

- [/concepts/19-textual-css-worker-driver.md](/concepts/19-textual-css-worker-driver.md) — `Driver` 抽象层与 `WebDriver`、`TEXTUAL_DRIVER` 钩子的出处（F-T-105..108）
- [/concepts/26-textual-web.md](/concepts/26-textual-web.md) — 托管版：同样复用 WebDriver/握手，但走 ganglion 网关与托管发布
- [/concepts/00-ecosystem-overview.md](/concepts/00-ecosystem-overview.md) — Textualize 生态全景与 Serve/Web 的定位
- [/references/textual-serve.md](/references/textual-serve.md) — textual-serve 仓库信源登记