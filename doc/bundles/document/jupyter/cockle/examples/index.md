# Cockle 实践示例索引

本目录包含 Cockle 浏览器 Shell 的可运行实践示例，建议从基础示例开始逐步深入。

## 基础示例

| 示例 | 说明 |
|------|------|
| [01-basic-shell.md](01-basic-shell.md) | 从零创建 Shell 实例、连接终端输出、发送命令并获取结果 |
| [02-using-commands.md](02-using-commands.md) | 管道（|）、重定向（>/>>/<）、别名定义和环境变量的实际用法 |

## 扩展开发

| 示例 | 说明 |
|------|------|
| [03-external-command.md](03-external-command.md) | 注册主线程外部命令，访问浏览器 API 并返回结果到 Shell |
| [04-custom-config.md](04-custom-config.md) | 自定义 cockle-config.json，配置默认别名、环境变量和 WASM 命令包 |

## 交互增强

| 示例 | 说明 |
|------|------|
| [05-tab-completion.md](05-tab-completion.md) | 自定义 Tab 补全、命令状态监听、终端尺寸同步和主题切换 |

```{toctree}
:hidden:
:maxdepth: 7

01-basic-shell
02-using-commands
03-external-command
04-custom-config
05-tab-completion
```
