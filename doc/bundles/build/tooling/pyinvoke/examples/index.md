# 实战示例

本目录包含 5 个完整的可运行示例，每个示例对应一个或多个核心概念，提供从简单到复杂的渐进式学习路径。

* [基础任务定义与执行](basic-task.md) — 从安装到定义第一个 @task 任务、执行任务、传递参数的完整 walkthrough。对应概念：[Task 基础](../concepts/02-task-basics.md)、[5分钟快速上手](../concepts/01-getting-started.md)。
* [命名空间组织大型项目](namespace-organization.md) — 使用 Collection 和嵌套模块组织大型项目，含模块化目录结构。对应概念：[Collection 与命名空间](../concepts/04-collection-namespace.md)。
* [使用 Program 构建自定义 CLI](custom-cli.md) — 通过 Program 类将 invoke 任务集合打包为独立 CLI 工具。对应概念：[CLI 与 Program 类](../concepts/07-cli-program.md)。
* [Watcher 自动化响应](file-watcher-automation.md) — 使用 Responder 和 FailingResponder 自动响应命令行提示（如 sudo 密码输入）。对应概念：[StreamWatcher 自动响应](../concepts/09-watchers.md)、[Runner 系统](../concepts/06-runners.md)。
* [使用 MockContext 测试任务](testing-tasks.md) — 使用 MockContext 对 invoke 任务进行单元测试，验证命令调用和参数。对应概念：[Context 对象](../concepts/03-context-object.md)、[Task 基础](../concepts/02-task-basics.md)。

```{toctree}
:maxdepth: 7

basic-task
custom-cli
file-watcher-automation
namespace-organization
testing-tasks
```
