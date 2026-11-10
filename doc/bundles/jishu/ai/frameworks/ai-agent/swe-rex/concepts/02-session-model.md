---
type: Concept
title: "会话模型：pexpect、PS1 哨兵与退出码提取"
description: "BashSession 如何维持持久 shell、判断命令结束、提取退出码、处理交互式程序与中断；check 三态与 bashlex 回退的完整语义"
tags: [swe-rex, session, pexpect, bash, pty, exit-code]
generated: { by: "seven-concepts-cmd/E", at: "2026-11-10T17:40:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T17:50:00+08:00" }
status: stable
stale_after: 2027-03-31
sources:
  - id: repo-facts
    resource: /references/source-code-map.md
    title: "源码事实登记 F-041 ~ F-060"
---

# 会话模型：pexpect、PS1 哨兵与退出码提取

`run_in_session()` 看起来只是“跑一条命令”，实际是一个持续运行的 bash 伪终端加上一套终止判定协议。理解这套协议，才能解释为什么有些命令会超时、为什么交互式程序要单独标记、为什么退出码有时是 `None`。

## 两种执行路径

| 路径 | 方法 | 实现 | 状态 | 适用 |
|---|---|---|---|---|
| 一次性命令 | `execute(Command)` | `subprocess.run` | 无状态 | 独立命令、无需 `cd`/环境变量 |
| 会话命令 | `run_in_session(BashAction)` | `BashSession` + pexpect | 持久 | 需要状态、交互式工具、多步操作 |

`LocalRuntime.execute()` 使用 `subprocess.run`，`stdin=DEVNULL`，可选合并输出流（F-060）。`run_in_session()` 则走 `BashSession`，同一个 session 名共享一个 bash 进程（F-049、F-051）。

## 启动：把 shell 变成可判定的状态机

`BashSession.start()`（`runtime/local.py` 第157-175行，F-052）做了五件事：

1. `pexpect.spawn("/usr/bin/env bash", encoding="utf-8", echo=False)`。
2. 环境变量强制 `PS1=SHELLPS1PREFIX`、`PS2=""`、`PS0=""`。
3. `await asyncio.sleep(0.3)` 等 shell 起来。
4. 如有 `startup_source`，逐个 `source`，再 `sleep 0.3`。
5. 重置 PS1/PS2/PS0，`sendline` 后 `expect(self._ps1, timeout=startup_timeout)`。

```python
self._shell = pexpect.spawn(
    "/usr/bin/env bash",
    encoding="utf-8",
    codec_errors="backslashreplace",
    echo=False,
    env=dict(os.environ.copy(), **{"PS1": self._ps1, "PS2": "", "PS0": ""}),
)
```

固定 PS1 是整套协议的锚点：命令输出里只要出现 `SHELLPS1PREFIX`，就说明 shell 回到了提示符。代价是用户命令若自己打印这个字符串，会被误判为结束——这是设计取舍，不是 bug。

`startup_source` 被特殊处理，是因为这些文件常会覆盖 PS1；所以 source 之后必须重新 `export PS1`（F-041、F-052）。

## 普通命令：三步流程

`_run_normal()`（`runtime/local.py` 第274-351行，F-053）严格三步：

### 第一步：语法检查

```python
_check_bash_command(action.command)
```

用 `/usr/bin/env bash -n << 'SOUNIQUEEOF'` 跑一遍语法检查（F-058）。失败抛 `BashIncorrectSyntaxError`，异常携带 `bash_stdout` 与 `bash_stderr` 到 `extra_info`（F-058、F-085）。这样坏命令不会污染 session。

### 第二步：拆分与发送

用 `bashlex.parse()` 把多行命令拆成独立命令，再用 `" ; "` 连接（F-053、F-057）。原因写在源码注释里：如果直接把带换行的多条命令发进去，会连续收到多个 PS1，无法区分哪一个是最后一条的结束。

bashlex 失败时走回退路径（F-054）：

```bash
<original command>
 TMPEXITCODE=$? ; sleep 0.1; echo -n 'UNIQUESTRING29234' ; (exit $TMPEXITCODE)
```

然后 `expect(["UNIQUESTRING29234"])` 而不是 PS1。源码注释称 bashlex “very buggy”，会抛 `ParsingError`、`NotImplementedError`、`TypeError` 等，所以捕获所有异常。

### 第三步：提取退出码

命令结束后，再发一条旁路命令：

```bash
echo EXITCODESTART$?EXITCODEEND
```

`expect("EXITCODEEND")`，从输出中用正则 `EXITCODESTART([0-9]+)` 提取数字（F-053）。如果匹配数不是 1，抛 `NoExitCodeError`。取完后还要再 `expect(PS1, timeout=0.1)` 清掉多余提示符。

这种“旁路 echo”比 `$?` 直接混在输出里可靠：它把退出码放进独立标记，不会和命令自身输出混淆。

## `check` 三态

`BashAction.check` 控制退出码处理（F-042）：

| 值 | 行为 | 退出码 | 异常 |
|---|---|---|---|
| `"raise"`（默认） | 提取并检查 | `int` | 非零抛 `NonZeroExitCodeError`；提取失败抛 `NoExitCodeError` |
| `"silent"` | 提取但不抛 | `int` 或 `None` | 提取失败吞掉，置 `None` |
| `"ignore"` | 不提取 | `None` | 不抛 |

`error_msg` 会拼进 `NonZeroExitCodeError` 的消息（F-042、F-053）。这让 agent 可以给失败命令附上上下文，而不是只看到退出码。

## 交互式命令

交互式程序（`python`、`gdb`、`less`）不会回到 PS1，因此走 `_run_interactive()`（`runtime/local.py` 第245-272行，F-055）：

```python
await runtime.run_in_session(BashAction(
    command="python",
    is_interactive_command=True,
    expect=[">>> "],
))
```

- `is_interactive_command=True`：发送命令后 `expect(action.expect + [PS1])`，命中任一 expect 字符串即返回。
- `is_interactive_quit=True`：用于退出交互式程序；发送 `stty -echo; echo 'UNIQUESTRING29234'`，等唯一字符串与 PS1，确保 shell 回到可控状态。
- 非 quit 的交互式命令会从输出里剥掉回显的命令本身（F-055）。

`BashObservation.expect_string` 记录实际命中的是哪个 expect 字符串；超时则为空（F-044）。这让调用方知道“命令是正常结束还是被提示符截断”。

## 中断

`BashInterruptAction`（F-043）用于打断卡住的命令：

```python
await runtime.run_in_session(BashInterruptAction())
```

`interrupt()`（`runtime/local.py` 第186-216行，F-056）：

1. 最多 `n_retry=3` 次发送 `SIGINT`，每次 `expect(expect + [PS1], timeout=0.2)`。
2. 全部失败后发送 Ctrl-Z，等 expect，再 `kill -9 %1`。
3. 仍失败则抛 `pexpect.TIMEOUT`。

这是为 `sleep 10`、`less` 这类“不响应 SIGINT 或占据终端”的场景准备的。测试 `test_interrupt_session` 与 `test_interrupt_pager` 覆盖了这两类（F-109）。

## 超时语义

超时发生在两个位置：

1. `expect(..., timeout=action.timeout)` 超时 → `CommandTimeoutError`（F-053、F-055）。
2. 提取退出码时 `expect(EXITCODEEND, timeout=1)` 超时 → `NoExitCodeError`（F-053）。

`timeout=None` 表示不超时。注意 `BashAction.timeout` 默认是 `None`（F-042），而测试里的 `_Action` 子类把默认值改成 5 秒（F-082）。生产代码应显式设置超时，否则卡死命令会永久占用 session。

## 输出清洗

`_strip_control_chars()`（F-059）删除 ANSI 转义序列并把 `\r\n` 归一为 `\n`。这解决两类噪声：彩色输出、PTY 的 CRLF。它不删除进度条的其他控制字符，也不做编码转换——编码由 pexpect 的 `encoding="utf-8"` 与 `codec_errors="backslashreplace"` 处理。

## 多会话隔离

`LocalRuntime` 用 `dict[str, Session]` 保存会话（F-049）：

```python
await runtime.create_session(CreateBashSessionRequest(session="shell1"))
await runtime.create_session(CreateBashSessionRequest(session="shell2"))
```

- 同名重复创建抛 `SessionExistsError`（F-050）。
- 不存在的 session 抛 `SessionDoesNotExistError`（F-051）。
- 两个 session 的环境变量互不可见；测试 `test_multiple_isolated_shells` 验证了这一点（F-109）。

## 已知限制

| 限制 | 事实 | 影响 |
|---|---|---|
| 固定 PS1 可能被命令输出伪造 | F-052 | 极少数输出会提前结束命令 |
| bashlex 解析失败走唯一字符串回退 | F-054 | 回退路径依赖 `sleep 0.1`，高负载下可能不稳 |
| 交互式命令不提取退出码 | F-055 | 交互式路径固定 `exit_code=0` |
| `check="ignore"` 不提取退出码 | F-042 | 适合明知不会正常退出的命令 |
| session 状态只在 runtime 进程内 | F-049 | server 重启即丢失 |

## 相关概念

- [运行时与执行语义](/concepts/05-runtimes-and-execution.md)
- [失败模式与测试](/concepts/07-failure-modes-and-tests.md)
- [Docker 沙箱示例](/examples/02-docker-sandbox.md)
