---
okf_version: "0.2"
---

# PyInvoke 知识库

本知识包是 Python 任务自动化库 [PyInvoke](https://www.pyinvoke.org/)（又称 invoke，"Pythonic Make"）的系统化中文教程，基于源码深度阅读生成，覆盖从快速上手到高级自定义的完整知识体系。所有内容均溯源至 PyInvoke 源码（`invoke/` 包核心模块），遵循 [OKF v0.2 规范](/concepts/00-introduction.md)。

## 入门与基础（concepts/）

* [PyInvoke 简介](concepts/00-introduction.md) — Pythonic 任务自动化库的设计哲学、安装方法、与 Make/Shell 脚本的对比。
* [5分钟快速上手](concepts/01-getting-started.md) — 创建第一个 tasks.py、使用 @task 装饰器、通过 inv 命令执行任务。
* [Task 基础](concepts/02-task-basics.md) — @task 参数详解、任务名与别名、默认任务、帮助文本、pre/post 钩子、autoprint、参数类型。
* [Context 对象](concepts/03-context-object.md) — c.run()、c.sudo()、c.cd()、c.prefix() 方法与配置访问、MockContext 测试。
* [Collection 与命名空间](concepts/04-collection-namespace.md) — 使用 Collection 组织任务、模块化大型项目、ns.configure() 配置、嵌套集合。

## 配置与执行（concepts/）

* [配置系统](concepts/05-configuration.md) — 9 层配置优先级、配置文件格式（yaml/json/python）、环境变量加载、DataProxy 双模式访问。
* [Runner 系统](concepts/06-runners.md) — Local runner、命令执行流程、Result 对象、pty 模式、echo/warn/hide 选项、异步 Promise。
* [CLI 与 Program 类](concepts/07-cli-program.md) — 构建自定义 CLI 工具、Program 参数、核心选项、Parser 机制、tab 补全。
* [执行模型](concepts/08-execution-model.md) — Executor 执行流程、Call 对象、pre/post 展开、dedupe 去重、异常体系。

## 高级主题（concepts/）

* [StreamWatcher 自动响应](concepts/09-watchers.md) — StreamWatcher、Responder 密码自动输入、FailingResponder 失败检测、自定义 watcher。
* [终端与 IO](concepts/10-terminals-io.md) — 伪终端 PTY、输出控制、字符缓冲模式、平台兼容性。
* [高级模式](concepts/11-advanced-patterns.md) — 自定义 Program/Executor/Runner、MockContext 测试、嵌入使用、大型项目组织。

## 实战示例（examples/）

* [基础任务定义与执行](examples/basic-task.md) — 从安装到定义第一个 @task 任务、执行任务、传递参数的完整示例。
* [命名空间组织大型项目](examples/namespace-organization.md) — 使用 Collection 和嵌套模块组织大型项目的任务，含模块化目录结构。
* [使用 Program 构建自定义 CLI](examples/custom-cli.md) — 通过 Program 类将 invoke 任务集合打包为独立 CLI 工具。
* [Watcher 自动化响应](examples/file-watcher-automation.md) — 使用 Responder 和 FailingResponder 自动响应命令行提示。
* [使用 MockContext 测试任务](examples/testing-tasks.md) — 使用 MockContext 对 invoke 任务进行单元测试，验证命令调用和参数。

## 信源登记簿（references/）

* [PyInvoke 源码信源登记](references/pyinvoke-source.md) — PyInvoke 源码路径、版本、核心模块清单与公开 API 导出列表。

## 信任与生命周期说明

* **status 判定依据**：全部 19 个内容文档（12 个概念 + 5 个示例 + 1 个信源登记 + 1 个信源索引）均 `status: stable`。内容基于对 PyInvoke 源码（`external/libs/pyinvoke/invoke/invoke/` 目录）的逐模块阅读与事实提取（70+ 源码事实），经 seven-concepts 方法论 R→I→E→V 四阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-12-31`。PyInvoke v3.x API 相对稳定，主要核心类（Task/Context/Collection/Config/Runner/Executor/Program）自 1.x 以来变化不大；该日期作为针对未来大版本升级的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻（2026-08-21）；`verified.at` 记录 V 阶段对抗审查核验事件（2026-08-21），两者分离、可追溯。

本知识包共收录 18 个内容文档（12 个概念 + 5 个示例 + 1 个信源登记），另含 3 个子目录 index.md 与根 index.md、log.md。

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
