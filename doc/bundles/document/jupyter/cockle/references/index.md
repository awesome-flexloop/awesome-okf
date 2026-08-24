# Cockle 信源参考索引

本目录包含 Cockle 浏览器 Shell 的源码级 API 参考文档，按模块组织。

## 核心 API

| 参考 | 说明 |
|------|------|
| [shell-api.md](shell-api.md) | IShell 接口、Shell 构造选项、Shell/BaseShell 公共方法完整 API |

## 系统模块

| 参考 | 说明 |
|------|------|
| [command-source.md](command-source.md) | CommandRegistry、ICommandRunner、CommandType、CommandModule 等命令系统 API |
| [parser-source.md](parser-source.md) | Tokenizer、Parser、AST 节点类型（CommandNode/PipeNode/RedirectNode）源码参考 |
| [io-source.md](io-source.md) | IInput/IOutput 接口族、TerminalInput/Output、FileInput/Output、Pipe 等 IO 类 API |
| [worker-source.md](worker-source.md) | BaseShellWorker、ComlinkShellWorker、CoincidentShellWorker 和 Worker 入口文件 API |

## 子系统

| 参考 | 说明 |
|------|------|
| [builtin-source.md](builtin-source.md) | 12 个内置命令的类结构和命令清单 |
| [buffered-io-source.md](buffered-io-source.md) | SharedArrayBuffer 和 Service Worker 两种缓冲 IO 实现 API |
| [config-source.md](config-source.md) | Environment、Aliases、History、Termios、cockle-config.json 格式参考 |

```{toctree}
:hidden:

buffered-io-source
builtin-source
command-source
config-source
io-source
parser-source
shell-api
worker-source
```
