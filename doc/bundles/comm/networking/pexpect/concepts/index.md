# pexpect 概念文档

## 入门

* [pexpect 简介](00-introduction.md) — 纯 Python Expect 风格交互控制库的设计哲学、安装方法、平台支持。
* [5分钟快速上手](01-getting-started.md) — 从安装到第一个 spawn+expect 示例的快速入门。

## 核心

* [spawn 类详解](02-spawn-class.md) — 构造参数、子进程生命周期、PTY 伪终端机制、回显控制、interact。
* [expect 模式匹配](03-expect-patterns.md) — expect/expect_exact/expect_list、模式列表索引、EOF/TIMEOUT、before/after/match 三元组、searchwindowsize。
* [发送与交互](04-send-interact.md) — send/sendline/write/sendcontrol/sendeof、interact() 交回控制、logfile 日志、delaybeforesend。
* [pxssh SSH 自动化](05-pxssh.md) — login/logout/prompt、唯一提示符机制、force_password、SSH 选项与隧道。

## 高级

* [跨平台 spawn 变体](06-cross-platform-spawn.md) — PopenSpawn（跨平台无 PTY）、fdspawn（文件描述符）、SocketSpawn（socket）、Unix vs Windows 差异。
* [REPLWrapper REPL 封装](07-replwrap.md) — REPLWrapper 封装 Python/Bash/Zsh REPL、run_command、续行检测、工厂函数。
* [高级模式](08-advanced-patterns.md) — FSM 有限状态机、run() 函数、超时处理、非阻塞读取、异步 expect、调试技巧。

```{toctree}
:hidden:

00-introduction
01-getting-started
02-spawn-class
03-expect-patterns
04-send-interact
05-pxssh
06-cross-platform-spawn
07-replwrap
08-advanced-patterns
```
