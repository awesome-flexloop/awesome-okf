---
type: Concept
title: textual-web：ganglion 客户端、包协议与托管发布
description: textual-web 是 WebDriver 的托管发布侧：ganglion 网关客户端、msgpack 包协议与 packets.yml 生成的 18 种 Packet 类型，把 Textual 应用与终端托管发布到 Web。
tags: [textualize, textual-web]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-01T00:00:00+08:00" }
status: rolling
stale_after: 2027-09-01
sources: [{ id: "textual-web", resource: "/references/textual-web.md", title: "Textual Web 仓库信源登记" }]
---

# textual-web：ganglion 客户端、包协议与托管发布

## 概述

如果说 `textual-serve` 是「本地自托管」的 Web 化（[/concepts/25-textual-serve.md](/concepts/25-textual-serve.md)），`textual-web` 则是把 Textual 应用与终端**发布到托管网关**的客户端侧：通过 `ganglion_client` 连接远端 gateway（ganglion），用 `msgpack` 帧 + 一套由模板生成的 `Packet` 类型声明应用、协商会话、搬运终端数据，并对 `TEXTUAL_DRIVER` 注入的 `WebDriver` 子进程做会话管理。仓库本地实际还包含 `session_manager`/`app_session`/`terminal_session` 三条会话分支与 pydantic 配置模型（F-SW-17）。本文沿「Driver 抽象 → 环境变量注入 → 包协议 → 托管发布」链路，与本地版 Serve 遥相呼应。

## Driver 抽象层接入（TEXTUAL_DRIVER）

与 `textual-serve` 同一手段：`AppSession.open()`（F-SW-14）写入

```
TEXTUAL_DRIVER=textual.drivers.web_driver:WebDriver
```

让子进程内的 Textual 应用启用 `WebDriver`（F-SW-14 ↔ F-T-105，WebDriver 本体见 F-T-108），把终端 I/O 收敛成 WebDriver 的 `write`/meta/二进制消息。这样**同一套 TUI 代码既可跑在本地 Serve，也可发布到托管 Web**，差异只在驱动选择与数据通道。

`open()` 还以 `os.chdir(self.working_directory)` 进入工作目录后 `create_subprocess_shell` 拉起应用，`finally` 恢复原 cwd。

## 环境变量注入

`AppSession.open()`（F-SW-14）打入与 Serve 几乎一致的环境集：`TEXTUAL_FPS="60"`、`TEXTUAL_COLOR_SYSTEM="truecolor"`、`TERM_PROGRAM="textual-web"`、`TERM_PROGRAM_VERSION=version("textual-web")`、`COLUMNS`/`ROWS`；`devtools` 为真时追加 `TEXTUAL="debug,devtools"` 与 `TEXTUAL_LOG="textual.log"`。区别在 `TERM_PROGRAM` 标记为自身版本、并挂在宿主会话体系之下。

## 包协议：packets.py 的 18 个 PacketType 与 msgpack

`textual-web` 的协议会话由 `packets.py`（F-SW-11）定义，文件头注明 "auto-generated from **packets.yml** and packets.py.template" 与 **"Do not hand edit."**——即先从一份 `packets.yml` 单来驱动生成整套类型：

- `PacketType(IntEnum)`：`NULL=0` 至 `REQUEST_DELIVER_CHUNK=17` 共 18 个值；
- `Packet` 继承 `tuple`；`PACKET_MAP` 把 1-17 映射到 17 个 Packet 类（Ping/Pong/Log/Info/DeclareApps/SessionOpen/SessionClose/SessionData/RoutePing/RoutePong/NotifyTerminalSize/Focus/Blur/OpenUrl/BinaryEncodedMessage/DeliverFileStart/RequestDeliverChunk）；
- `Handlers.dispatch_packet()` 执行 `packet._get_handler(self)(packet)`。

收发落地在 `ganglion_client.py`（F-SW-10）：`run_websocket()` 以 `partial(msgpack.unpackb, use_list=True, raw=False)` 解码 BINARY 消息，`decode_envelope()` 以首元素 int 查 `PACKET_MAP` 并 `packet_class.build(*packet_data[: len(packet_class._attributes)])`，`send()` 以 `msgpack.packb(packet, use_bin_type=True)` 发送——**帧用 msgpack，语义用 Packet 类**，比 Serve 的 `encode_packet`（type+length+payload）更高阶的声明式通道。

终端多路复用：`TerminalSession`（F-SW-16）走 `pty.fork()` + `fcntl.ioctl(TIOCSWINSZ)` 的真实伪终端，`AppSession`（F-SW-14/15）则同样识别 `__GANGLION__\n` 握手后按 type(1B)+size(4B BE)+payload 读包（`b"D"`→数据、`b"M"`→meta、`b"P"`→二进制消息）。

## 托管发布：ganglion、会话路由与配置

发布的核心是「声明 + 协商 + 路由」三层（F-SW-03/F-SW-05/F-SW-09/F-SW-12）：

- **环境（托管点）**：`environment.py`（F-SW-05）以 `Environment` dataclass 配三项——`prod`（`https://textual-web.io/...`）、`local`（`ws://127.0.0.1:8080/...`）、`dev`（`https://textualize-dev.io/...`），`get_environment()` 对未知名抛 `RuntimeError`。
- **连接鉴权**：`ganglion_client._connect()`（F-SW-07）api_key 非空时带 `headers = {"GANGLIONAPIKEY": api_key}`，`ws_connect(..., heartbeat=15, compress=12)` 包在 `Retry()`（F-SW-08，指数退避 `retry_count**2`）中，`WSServerHandshakeError` 记录 "check your API Key"。
- **应用声明**：`post_connect()`（F-SW-09）把 `config.apps` 经 `model_dump(include={"name","slug","color","terminal"})` 后 `send(packets.DeclareApps(apps))`；Windows 下过滤 terminal 应用。
- **会话开启**：`on_session_open()`（F-SW-12）→ `session_manager.new_session(app_slug, SessionID, RouteKey, devtools, size)`，随后 `session_process.start(connector)`；`SessionManager`（F-SW-13）以 `sessions: dict[SessionID, Session]` 与 `routes: TwoWayDict[RouteKey, SessionID]` 维护，terminal/app 各建 `TerminalSession`/`AppSession`。
- **配置模型**：`config.py`（F-SW-17）定义 pydantic `Account(api_key)`、`App(name, slug, path, color, command, terminal)`、`Config(account, apps)`；`ExpandVarsStr = Annotated[str, AfterValidator(expandvars)]` 让 `path`/`command` 在解析时展开环境变量。
- **CLI 装配**：`cli.py`（F-SW-02/03/04）`-c/-e/-r/--dev/-t/--welcome/--merlin` 等；`-r` 逐条 `add_app(...)`，无应用时插入 `Welcome`/`Merlin Tribute`。

浏览器端渲染同样交由 `WebDriver`（F-T-108）对应协议完成（托管 UI 由 textual-web.io 载体侧承接，本仓库聚焦客户端）。

## 复用了哪些核心原语

- **F-SW-14 ↔ F-T Driver（F-T-105/106/107/108）**：`TEXTUAL_DRIVER="...:WebDriver"` 复用 Driver 抽象层选择机制；`__GANGLION__` 握手、`D/M/P` 包分发与 `WebDriver` 的 `write`/meta/`deliver_binary` 语义同源（`deliver_binary` 见 F-T-107）。
- **`WebDriver` 生命周期与 `open_url`/下载**：`F-SW-15` 的 meta 回发（`exit`/`blur`/`focus`）与 `OpenUrl`/`DeliverFileStart`/`RequestDeliverChunk` 包，均是 Driver 层既有通道的包化映射。
- **`TEXTUAL` 开发特性注入**：`devtools` 时 `TEXTUAL="debug,devtools"` + `TEXTUAL_LOG`，复用保留的开发开关。

## 本工具示范的独有机制

- **模板生成的包类型**（F-SW-11）：`packets.yml`+`packets.py.template` 自动生成 18 个 `PacketType` 与 `PACKET_MAP`，"Do not hand edit"——协议演进改模板而非手写类。
- **ganglion 网关联邦**（F-SW-05/F-SW-07/F-SW-09/F-SW-12）：通过远端 API/WebSocket 地址声明应用、协商会话、按 `RouteKey` 路由，实现**多应用托管**而非单应用本地服务。
- **伪终端终端托管**（F-SW-16）：`TerminalSession` 用 `pty.fork()` + `fcntl.ioctl(TIOCSWINSZ)` 托管真实终端进程（`TERM_PROGRAM="textual-web"` 后 `os.execlp`），提供非 Textual 应用的 shell 托管。
- **指数退避重连**（F-SW-08）：`Retry` 以 `retry_count**2` 抖动退避，`success()` 归零重试计数。
- **空闲自杀**（F-SW-20）：`ExitPoller`（`EXIT_POLL_RATE=5`）在 `--exit-on-idle` 下监测无会话空闲超时后 `force_exit()`；`Poller(Thread)` 用 `selectors.DefaultSelector()` 做多路 IO。
- **TCP 就绪探针**（F-SW-19）：`web.py`（Stub）注册 `/health-check/`，`wait_for(connected_event.wait(), 5.0)` 后返回 "Hello, world"（TCPSite 0.0.0.0:8080）。
- **身份标识**（F-SW-18）：`IDENTITY_ALPHABET=31` 字符 + `IDENTITY_SIZE=12` 的 `os.urandom` 生成短 ID（用于 slug/路由）。

## 相关概念

- [/concepts/19-textual-css-worker-driver.md](/concepts/19-textual-css-worker-driver.md) — `Driver` 抽象层与 `WebDriver`、`TEXTUAL_DRIVER` 钩子的出处（F-T-105..108）
- [/concepts/25-textual-serve.md](/concepts/25-textual-serve.md) — 本地自托管版：同用 WebDriver/握手，但无网关、直连 WebSocket
- [/concepts/00-ecosystem-overview.md](/concepts/00-ecosystem-overview.md) — Textualize 生态全景与 Web 托管定位
- [/references/textual-web.md](/references/textual-web.md) — textual-web 仓库信源登记