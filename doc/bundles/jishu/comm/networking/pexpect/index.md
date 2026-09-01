---
okf_version: "0.2"
---

# pexpect 知识库

本知识包是纯 Python Expect 风格交互控制库 [pexpect](https://pexpect.readthedocs.io)（v4.9.0）的系统化中文教程，基于源码深度阅读生成，覆盖从快速上手到跨平台变体、REPL 封装的完整知识体系。所有内容均溯源至 pexpect 源码（`pexpect/` 包核心模块），遵循 [OKF v0.2 规范](concepts/00-introduction.md)。

## 入门与基础（concepts/）

* [pexpect 简介](concepts/00-introduction.md) — Expect 概念、设计哲学、安装方法、平台支持与工具对比。
* [5分钟快速上手](concepts/01-getting-started.md) — 从安装到第一个 spawn+expect 示例、run() 函数、上下文管理器。

## 核心概念（concepts/）

* [spawn 类详解](concepts/02-spawn-class.md) — 构造参数、PTY 伪终端机制、子进程生命周期、回显控制、interact()。
* [expect 模式匹配](concepts/03-expect-patterns.md) — expect/expect_exact/expect_list、模式列表返回索引、EOF/TIMEOUT、before/after/match 三元组。
* [发送与交互](concepts/04-send-interact.md) — send/sendline/sendcontrol/sendeof、interact() 交回终端控制、logfile 日志。
* [pxssh SSH 自动化](concepts/05-pxssh.md) — login/logout/prompt、唯一提示符机制、force_password、SSH 选项与隧道。

## 高级主题（concepts/）

* [跨平台 spawn 变体](concepts/06-cross-platform-spawn.md) — PopenSpawn（跨平台无 PTY）、fdspawn、SocketSpawn、Unix vs Windows 差异。
* [REPLWrapper REPL 封装](concepts/07-replwrap.md) — REPLWrapper 封装 Python/Bash/Zsh REPL、run_command、工厂函数。
* [高级模式](concepts/08-advanced-patterns.md) — FSM 有限状态机、run() 函数、超时处理、非阻塞读取、异步 expect、调试技巧。

## 实战示例（examples/）

* [SSH 自动登录](examples/ssh-login-automation.md) — pxssh 自动登录、密钥认证、主机密钥确认。
* [FTP 交互自动化](examples/ftp-interaction.md) — FTP 登录、文件上传下载、目录操作。
* [密码提示自动响应](examples/password-prompts.md) — sudo/SSH/密钥密码短语、waitnoecho、避免密码回显。
* [REPL 交互控制](examples/repl-control.md) — 使用 REPLWrapper 控制 Python/Bash/数据库 REPL。

## 信源登记簿（references/）

* [pexpect 源码信源登记](references/pexpect-source.md) — pexpect v4.9.0 源码路径、版本、核心模块清单与公开 API 导出。

## 信任与生命周期说明

* **status 判定依据**：全部 14 个内容文档（9 个概念 + 4 个示例 + 1 个信源登记）均 `status: stable`。内容基于对 pexpect 源码（`external/libs/pexpect/pexpect/` 目录）的逐模块阅读与事实提取（77 条源码事实），经 R→I→E→V 四阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-12-31`。pexpect 4.x API 非常稳定，核心类（spawn/pxssh/PopenSpawn/REPLWrapper）自 4.0 以来变化极小；该日期作为针对未来大版本升级的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻（2026-08-23）；`verified.at` 记录 V 阶段 Grep 验证事件（2026-08-23），两者分离、可追溯。

本知识包共收录 14 个内容文档（9 个概念 + 4 个示例 + 1 个信源登记），另含 3 个子目录 index.md 与根 index.md、log.md。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
