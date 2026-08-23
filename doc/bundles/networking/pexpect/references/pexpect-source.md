---
type: Reference
title: pexpect 源码信源登记
description: pexpect v4.9.0 源码路径、版本信息、核心模块清单与公开 API
tags: [pexpect, source, reference, v4.9.0]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pexpect-github
    resource: https://github.com/pexpect/pexpect
    title: pexpect GitHub 仓库
    author: human:noahspurrier
  - id: pexpect-docs
    resource: https://pexpect.readthedocs.io
    title: pexpect 官方文档
---

# pexpect 源码信源登记

## 基本信息

| 属性 | 值 |
|------|-----|
| 项目名 | pexpect |
| 版本 | **4.9.0**（commit fc8f062518b4） |
| 描述 | Pure Python Expect-like module for controlling interactive applications（纯 Python Expect 风格交互控制库） |
| 作者 | Noah Spurrier 及贡献者 |
| 许可证 | ISC License（OSI/FSF 认证的 GPL 兼容许可证） |
| Python 要求 | ≥ 2.7 或 ≥ 3.3（依赖 ptyprocess） |
| 官方文档 | <https://pexpect.readthedocs.io> |
| 源码仓库 | <https://github.com/pexpect/pexpect> |

## 源码位置

pexpect 源码位于 SpecWeave 仓库的外部依赖目录：

```
external/libs/pexpect/pexpect/
```

该目录通过 git submodule 引入，本地不做修改。

## 平台限制

pexpect 的核心 `spawn` 类依赖 Unix PTY（`pty` 模块和 `ptyprocess` 库），**仅在 Unix/Linux/macOS 上可用**。在 Windows 上：

- `pexpect.spawn`、`pexpect.run`、`pexpect.spawnu`、`pexpect.runu` 不会被导入到顶层命名空间（`__init__.py` 中 `if sys.platform != 'win32'` 条件守卫）。
- 必须使用 `pexpect.popen_spawn.PopenSpawn`（基于 subprocess.Popen，无 PTY）或 `pexpect.socket_pexpect.SocketSpawn`（基于 socket）。
- `pexpect.fdpexpect.fdspawn` 在 Windows 上对 socket 无效（`socket.fileno()` 在 Windows 上不可用于 select），应改用 SocketSpawn。

## 核心模块清单

| 模块 | 说明 |
|------|------|
| `__init__.py` | 包入口，条件导出 spawn/run（仅 Unix）、异常类、工具函数；定义 `__version__ = '4.9.0'` |
| `spawnbase.py` | `SpawnBase` 抽象基类：实现 expect/expect_list/expect_exact 匹配引擎、compile_pattern_list、read/readline、日志、编码处理、上下文管理器 |
| `pty_spawn.py` | `spawn` 类（Unix PTY 实现）：通过 ptyprocess 启动子进程，实现 send/sendline/sendcontrol/sendeof/sendintr/interact/read_nonblocking/terminate/kill/wait/setwinsize 等；`spawnu` 弃用别名 |
| `popen_spawn.py` | `PopenSpawn` 类（跨平台）：基于 subprocess.Popen，后台线程读取管道到 Queue，无 PTY 能力 |
| `pxssh.py` | `pxssh` 类（继承 spawn）：SSH 登录专用，实现 login/logout/prompt/set_unique_prompt；`ExceptionPxssh` 异常 |
| `fdpexpect.py` | `fdspawn` 类（继承 SpawnBase）：基于任意文件描述符，适用于串口/命名管道 |
| `socket_pexpect.py` | `SocketSpawn` 类（继承 SpawnBase）：基于 socket，跨平台网络交互 |
| `replwrap.py` | `REPLWrapper` 类：REPL 交互封装；`python()`/`bash()`/`zsh()` 工厂函数 |
| `run.py` | `run()` 高层便捷函数：执行命令并返回输出，支持 events 模式响应；`runu` 弃用别名 |
| `expect.py` | `Expecter` 匹配引擎、`searcher_string`（纯字符串搜索）、`searcher_re`（正则搜索） |
| `exceptions.py` | `ExceptionPexpect` 基类、`EOF`、`TIMEOUT` 异常 |
| `FSM.py` | `FSM` 有限状态机、`ExceptionFSM` 异常 |
| `utils.py` | `which`、`is_executable_file`、`split_command_line`、`select_ignore_interrupts`、`poll_ignore_interrupts` |
| `ANSI.py` | ANSI 终端屏幕解析（`ANSI`、`term` 类） |
| `screen.py` | 虚拟屏幕抽象 |
| `_async.py`/`_async_pre_await.py`/`_async_w_await.py` | asyncio 异步支持（expect_async、repl_run_command_async） |

## 公开 API 导出

### Unix 平台顶层导出（`pexpect.*`）

- **核心类**：`spawn`、`spawnu`（弃用）
- **函数**：`run`、`runu`（弃用）、`which`、`split_command_line`
- **异常**：`ExceptionPexpect`、`EOF`、`TIMEOUT`
- **内部引擎**（已导入但非 `__all__` 主要项）：`Expecter`、`searcher_re`、`searcher_string`、`is_executable_file`

### 子模块公开类

- `pexpect.pxssh.pxssh`、`pexpect.pxssh.ExceptionPxssh`
- `pexpect.popen_spawn.PopenSpawn`
- `pexpect.fdpexpect.fdspawn`
- `pexpect.socket_pexpect.SocketSpawn`
- `pexpect.replwrap.REPLWrapper`、`pexpect.replwrap.python`、`pexpect.replwrap.bash`、`pexpect.replwrap.zsh`
- `pexpect.FSM.FSM`、`pexpect.FSM.ExceptionFSM`
- `pexpect.exceptions.ExceptionPexpect`、`pexpect.exceptions.EOF`、`pexpect.exceptions.TIMEOUT`

## 继承层次

```
SpawnBase (spawnbase.py)
├── spawn (pty_spawn.py)          # Unix PTY
│   └── pxssh (pxssh.py)          # SSH 专用
├── PopenSpawn (popen_spawn.py)   # 跨平台 subprocess
├── fdspawn (fdpexpect.py)        # 文件描述符
└── SocketSpawn (socket_pexpect.py)  # socket
```

[^pexpect-github]: pexpect 源码仓库：<https://github.com/pexpect/pexpect>
[^pexpect-docs]: pexpect 官方文档：<https://pexpect.readthedocs.io>
