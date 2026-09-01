---
type: Concept
title: textual-dev：devtools 控制台、CLI 子命令与输出重定向
description: textual-dev 用 WebSocket 开发控制台承载调试日志，DevtoolsConsole 导出 segments 并经 CLI 重定向串联。
tags: [textualize, textual-dev]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-09-01T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-01T00:00:00+08:00" }
status: rolling
stale_after: 2027-09-01
sources: [{ id: "textual-dev", resource: "/references/textual-dev.md", title: "Textual Dev 仓库信源登记" }]
---

# textual-dev：devtools 控制台、CLI 子命令与输出重定向

## 概述

textual-dev 是 Textual 的开发者工具包，为 Textual 应用提供实时调试能力。它以 `textual` 命令（F-SD-02/F-SD-03）暴露 8 个子命令——`console`、`run`、`serve`、`borders`、`easing`、`colors`、`keys`、`diagnose`，其中 `console` 启动一个基于 aiohttp 的 WebSocket 开发控制台，`run --dev` 以 `TEXTUAL` 环境变量把调试特性注入被运行的应用，同时把应用的 stdout/print 输出重定向到该控制台。本文覆盖事实 **F-SD-01..18**，类名/方法名均可在 `external/dao/action/Textualize/textual-dev/src/textual_dev/` 下直接验证。

整体链路（F-SD-09..14/F-SD-14）：

1. `console` 子命令调用 `server._run_devtools()`，建起 aiohttp 服务器与 WebSocket 路由（F-SD-04/F-SD-09）。
2. `DevtoolsService` 持有 `ClientHandler` 列表，向每个连接推送 `server_info` 并周期性探测终端尺寸（F-SD-10）。
3. 应用到 `DevtoolsClient.log()` 把一批 renderable segments 用 `pickle.dumps` 打包进 `msgpack` 信封发到服务端（F-SD-12）。
4. `ClientHandler._consume_incoming()` 收到 `client_log` 后 `pickle.loads` 还原 segments，用自定义 renderable 打印到本机控制台（F-SD-11）。

## 复用了哪些核心原语

textual-dev 的开发控制台建立在 Textual 生态的渲染与终端原语之上，最典型的一处：

- **F-SD-13 ↔ F-R Console**：`DevtoolsConsole(Console)` 继承 Rich 的 `Console`，`__init__` 里只做一件事——设 `self.record = True`；随后 `export_segments()` 在 `_record_buffer_lock` 下返回并清空 `_record_buffer`。这正是 Rich `Console` 的录制/导出能力（`Console.__init__` 的 `record=False` 默认参数见 `/concepts/01-rich-console-and-protocol.md`，导出类方法见 F-R-048）。textual-dev 直接继承 Rich `Console` 来获得分段录制原语，而不是自己实现控制台缓冲区。

- **Rich renderable 体系**（F-SD-11/F-SD-16）：`ClientHandler` 打印 `DevConsoleLog` / `DevConsoleNotice`（均为 `renderables.py` 定义的自定义 renderable，`DevConsoleHeader` 用 `textual` 版本信息构建）；`DevConsoleNotice` 的 `level→style` 映射 `{"info": "dim", "warning": "yellow", "error": "red"}` 直接沿用 Rich 的 style 语法。
- **Textual/命令行状态注入**（F-SD-05/F-SD-18）：`run --dev` 向 `environment["TEXTUAL"]` 追加 `"debug,devtools"` 特性，再写入 `TEXTUAL_DEVTOOLS_HOST/PORT`、`TEXTUAL_PRESS`、`TEXTUAL_SCREENSHOT` 等环境变量；`KeysApp` 以 `App[None]` 定制 `TITLE`/`ENABLE_COMMAND_PALETTE`/`inherit_bindings` 并监听 `on_key()`。这些是 Textual 既有的 driver/特性开关入口。

## 本工具示范的独有机制

textual-dev 的差异化价值在于"**外部进程 + 调试管道**"，这是单进程 TUI 框架所没有的开发期机制：

- **WebSocket 开发控制台**（F-SD-09/F-SD-10）：`_make_devtools_aiohttp_app()` 创建 aiohttp `Application`，把 `DevtoolsService` 挂到 `app["service"]`，注册 `get("/textual-devtools-websocket", websocket_handler)`；`_run_devtools()` 在 `run_app` 上以 `DEVTOOLS_PORT` 兜底，OSError 时打印 "Couldn't start server"。
- **分段采集与打包协议**（F-SD-12）：`DevtoolsClient._encode_segments()` 返回 `pickle.dumps(segments, protocol=4)`，`log()` 以 `msgpack.packb` 打包 `{"type": "client_log", "payload": {group, verbosity, timestamp, path, line_number, segments}}`；QueueFull 时 `self.spillover += 1`（以 `QUEUEABLE_TYPES = {"client_log", "client_spillover"}` 分流，F-SD-10→F-SD-11）。
- **输出重定向**（F-SD-14）：`StdoutRedirector.write()` 把 `DevtoolsLog(string, caller)` 追加到 `_buffer`，含 `"\n"` 时 `flush()`；`_write_to_devtools()` 按 caller 的 filename/lineno 切分批次，`_log_devtools_batched()` 以 `"".join(...)` 合并、`rstrip()` 后 `self.devtools.log(..., LogGroup.PRINT, LogVerbosity.NORMAL)`。这让普通 `print` 走的 stdout 也被收进 devtools 管道。
- **终端尺寸轮询**（F-SD-10）：`_console_size_poller()` 监听 `console.width/height` 变化，变化即 `_send_server_info_to_all()`，实现窗口 resize 同步。
- **多命令工具箱**（F-SD-03/F-SD-07/SD-15）：`click.group()` 聚合 8 个子命令；`previews/__init__.py` 的 `__all__` 导出 4 个预览 App（`BorderApp`/`EasingApp`/`ColorsApp`/`KeysApp`）；`run` 子命令区分 `.py` 文件模式（`exec_python`：Windows 用 `subprocess.call([sys.executable, ...])`，否则 `os.execve`）与 `module:app` 导入模式（`exec_import` 用 `EXEC_SCRIPT` 模板编译执行）。
- **诊断报告**（F-SD-08）：`diagnose()` 用 `_section()` 输出 Markdown 表格（`| Name | Value |`）并打印可直接贴进 GitHub issue 的 HTML 注释头。

## 相关概念

- `/concepts/01-rich-console-and-protocol.md` — F-SD-13 复用的 Rich `Console` 录制/导出原语来源
- `/concepts/00-ecosystem-overview.md` — textual-dev 在 Textualize 生态中的定位与其他仓库的依赖图谱