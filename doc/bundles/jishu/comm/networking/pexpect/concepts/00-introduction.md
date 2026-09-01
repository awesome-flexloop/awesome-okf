---
type: Concept
title: pexpect 简介
description: 纯 Python Expect 风格交互控制库——什么是 pexpect、设计哲学、安装方法、平台支持
tags: [pexpect, introduction, expect]
generated: { by: "reference_agent/trae-glm", at: "2026-08-23T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pexpect-source
    resource: /references/pexpect-source.md
---

# pexpect 简介

## 什么是 pexpect

pexpect 是一个纯 Python 实现的 Expect 风格库，用于启动子应用程序并自动控制它们。它的灵感来自 Don Libes 的 Expect（Tcl 扩展），但 pexpect 不依赖 TCL、Expect 或 C 扩展，完全使用 Python 标准库实现。

pexpect 的典型用途包括：

- 自动化交互式应用（ssh、ftp、passwd、telnet 等）
- 自动化软件安装脚本（在不同服务器上复制安装流程）
- 自动化软件测试
- 控制需要密码输入的命令行工具（密码提示直接从 TTY 读取，绕过 stdin）

pexpect 提供两个主要接口：

1. **`run()` 函数**：简单接口，执行命令并返回输出，是 `os.system()` 的便捷替代。
2. **`spawn` 类**：强大接口，启动子程序后可以发送输入、期望（expect）响应模式，实现复杂的交互控制。

## 设计哲学

pexpect 遵循以下设计原则：

- **纯 Python 实现**：不依赖 C 扩展或系统 Expect 程序，只要平台支持 Python `pty` 模块即可工作
- **终端感知**：通过伪终端（PTY）与子进程交互，子进程认为自己连接到真实终端，会正常显示密码提示、颜色输出等
- **模式匹配驱动**：核心编程模型是"发送输入→等待输出模式→根据匹配结果分支"，类似 Expect 的 `expect`/`send` 范式
- **渐进式抽象**：`SpawnBase` 提供统一匹配引擎，`spawn`/`PopenSpawn`/`fdspawn`/`SocketSpawn` 针对不同 I/O 机制提供实现
- **Pythonic**：支持上下文管理器（`with` 语句）、迭代器、文件对象接口（read/readline）

## 安装方法

pexpect 通过 pip 安装：

```bash
pip install pexpect
```

pexpect v4.9.0 的唯一运行时依赖是 [ptyprocess](https://pypi.org/project/ptyprocess/)，它封装了 PTY 的底层系统调用。

验证安装：

```bash
python -c "import pexpect; print(pexpect.__version__)"
```

## 平台支持

| 平台 | spawn（PTY） | PopenSpawn | fdspawn | SocketSpawn |
|------|-------------|------------|---------|-------------|
| Linux | ✅ | ✅ | ✅ | ✅ |
| macOS | ✅ | ✅ | ✅ | ✅ |
| FreeBSD | ✅ | ✅ | ✅ | ✅ |
| Windows | ❌ | ✅ | ⚠️ 有限 | ✅ |
| Solaris | ✅ | ✅ | ✅ | ✅ |

**Windows 用户注意**：`pexpect.spawn` 和 `pexpect.run` 在 Windows 上不可用，因为 Windows 没有 Unix 风格的 PTY。Windows 上应使用 `PopenSpawn`（基于 `subprocess.Popen`）或 `SocketSpawn`（基于 socket）。

```python
# Unix/Linux/macOS
import pexpect
child = pexpect.spawn('ssh user@host')

# Windows（跨平台）
from pexpect.popen_spawn import PopenSpawn
child = PopenSpawn('ssh user@host')
```

## 与其他工具的对比

| 特性 | pexpect | subprocess | paramiko | Fabric |
|------|---------|-----------|----------|--------|
| 定位 | 交互式进程控制 | 子进程管理 | SSH 协议库 | 远程执行框架 |
| 交互模式 | PTY 实时交互 | 管道通信 | SSH 通道 | 基于 paramiko |
| 密码提示 | ✅ 原生支持 | ❌ 需 PTY 参数 | ✅ 编程式认证 | ✅ 封装 |
| 跨平台 | Unix PTY + PopenSpawn | ✅ 全平台 | ✅ 全平台 | ✅ 全平台 |
| 异步支持 | asyncio（async_=True） | asyncio.create_subprocess | 线程模型 | 同步 |
| 学习曲线 | 低 | 低 | 中 | 低 |

### 与 subprocess 的对比

`subprocess.Popen` 通过管道与子进程通信，适合非交互场景：

```python
import subprocess
result = subprocess.run(['ls', '-l'], capture_output=True, text=True)
```

但当程序直接从 TTY 读取（如 ssh 密码提示）时，管道方式无法工作。pexpect 通过 PTY 解决了这个问题：

```python
import pexpect
child = pexpect.spawn('ssh user@host')
child.expect('password:')
child.sendline('mypassword')
```

## 核心模块一览

- **spawn 层**：`spawn`（Unix PTY）、`PopenSpawn`（跨平台管道）、`fdspawn`（文件描述符）、`SocketSpawn`（网络套接字）
- **匹配引擎**：`SpawnBase.expect`/`expect_list`/`expect_exact`、`Expecter`、`searcher_re`/`searcher_string`
- **SSH 专用**：`pxssh`（登录/登出/提示符同步）
- **REPL 封装**：`REPLWrapper`、`python()`/`bash()`/`zsh()` 工厂函数
- **便捷函数**：`run()`（一次性执行+模式响应）
- **异常体系**：`ExceptionPexpect`、`EOF`、`TIMEOUT`、`ExceptionPxssh`

## 相关概念

- [5分钟快速上手](01-getting-started.md)
- [spawn 类详解](02-spawn-class.md)
- [expect 模式匹配](03-expect-patterns.md)
- [pxssh SSH 自动化](05-pxssh.md)
- [跨平台 spawn 变体](06-cross-platform-spawn.md)
- [pexpect 源码信源登记](../references/pexpect-source.md)

[^pexpect-source]: pexpect 源码信源，见 [pexpect-source.md](../references/pexpect-source.md)。
