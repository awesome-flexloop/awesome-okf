# 概念文档

本目录包含 PyInvoke 的 12 个核心概念文档，按学习路径排列：从入门到高级主题逐步深入。

## 入门与基础

* [00-PyInvoke 简介](00-introduction.md) — Pythonic 任务自动化库的设计哲学、安装方法、与 Make/Shell 脚本的对比。
* [01-5分钟快速上手](01-getting-started.md) — 创建第一个 tasks.py、使用 @task 装饰器、通过 inv 命令执行任务。
* [02-Task 基础](02-task-basics.md) — @task 参数详解、任务名与别名、默认任务、帮助文本、pre/post 钩子、autoprint。
* [03-Context 对象](03-context-object.md) — c.run()、c.sudo()、c.cd()、c.prefix() 方法与配置访问。
* [04-Collection 与命名空间](04-collection-namespace.md) — 使用 Collection 组织任务、模块化大型项目、嵌套集合。

## 配置与执行

* [05-配置系统](05-configuration.md) — 9 层配置优先级、配置文件格式、环境变量加载、DataProxy 双模式访问。
* [06-Runner 系统](06-runners.md) — Local runner、命令执行流程、Result 对象、pty 模式、异步 Promise。
* [07-CLI 与 Program 类](07-cli-program.md) — 构建自定义 CLI 工具、Program 参数、核心选项、tab 补全。
* [08-执行模型](08-execution-model.md) — Executor 执行流程、Call 对象、pre/post 展开、dedupe 去重、异常体系。

## 高级主题

* [09-StreamWatcher 自动响应](09-watchers.md) — Responder 密码自动输入、FailingResponder 失败检测、自定义 watcher。
* [10-终端与 IO](10-terminals-io.md) — 伪终端 PTY、输出控制、字符缓冲模式、平台兼容性。
* [11-高级模式](11-advanced-patterns.md) — 自定义 Program/Executor/Runner、MockContext 测试、嵌入使用。

```{toctree}
:hidden:

00-introduction
01-getting-started
02-task-basics
03-context-object
04-collection-namespace
05-configuration
06-runners
07-cli-program
08-execution-model
09-watchers
10-terminals-io
11-advanced-patterns
```
