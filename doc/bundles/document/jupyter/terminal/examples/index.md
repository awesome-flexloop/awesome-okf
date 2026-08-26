# JupyterLite Terminal 实践示例

本文档目录包含 JupyterLite Terminal 的使用示例和编程式API调用教程，从终端基础操作到自定义扩展开发。

## 示例文档列表

| 文档 | 核心内容 | 难度 |
|------|----------|------|
| [基础终端使用](01-basic-terminal-usage.md) | 打开终端、导航命令、文件操作、管道过滤、Tab补全、交互式命令、cockle-config、别名使用 | ⭐ 入门 |
| [通过编程式API执行shell命令](02-execute-shell-command.md) | execute-shell命令调用、返回值解析、错误处理、超时设置、执行结果处理模式 | ⭐⭐ 中级 |
| [复用Shell会话](03-reusable-shell-session.md) | start-shell/execute-shell/shutdown-shell持久会话、状态保持、多shell并行、超时恢复、ShellSession辅助类封装 | ⭐⭐ 中级 |
| [注册自定义命令与环境配置](04-custom-command.md) | ILiteTerminalAPIClient注入、registerAlias、registerEnvironmentVariable、registerExternalCommand、条件配置、完整配置插件 | ⭐⭐⭐ 进阶 |

## 前置知识

在阅读示例前，建议先了解对应概念：

- 终端基础使用 → [Shell与Worker机制](/concepts/04-shell-and-worker.md)、[文件系统与Stdin路由](/concepts/06-drivefs-and-stdin.md)
- 编程式API调用 → [无头命令执行](/concepts/05-headless-exec.md)
- 自定义配置扩展 → [插件系统](/concepts/03-plugin-system.md)、[主题同步与设置](/concepts/07-theme-and-settings.md)、[构建系统与扩展开发](/concepts/08-build-and-extension.md)

```{toctree}
:hidden:
:maxdepth: 7

01-basic-terminal-usage
02-execute-shell-command
03-reusable-shell-session
04-custom-command
```
