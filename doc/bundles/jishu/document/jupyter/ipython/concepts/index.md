# IPython 概念文档索引

本目录包含 IPython 增强型 Python REPL 的核心概念文档，建议按编号顺序阅读。

## 入门

| 文档 | 说明 |
|------|------|
| [00-introduction.md](00-introduction.md) | IPython 是什么——核心特性、版本信息、与 Jupyter 的关系、生态系统 |
| [01-getting-started.md](01-getting-started.md) | 安装 IPython、启动终端、第一个交互会话、命令行参数 |

## 核心架构

| 文档 | 说明 |
|------|------|
| [02-architecture-overview.md](02-architecture-overview.md) | 三层架构：TerminalIPythonApp 应用层 → InteractiveShell 核心引擎 → TerminalInteractiveShell 终端前端 |
| [03-shell-lifecycle.md](03-shell-lifecycle.md) | Shell 生命周期：31 步初始化序列、命名空间管理、Singleton 模式、mainloop 主循环、退出流程 |
| [04-magic-system.md](04-magic-system.md) | 魔法命令系统：装饰器注册、LazyMagic 懒加载、MagicsManager、行/单元魔法、automagic 模式 |
| [05-execution-pipeline.md](05-execution-pipeline.md) | 代码执行六阶段管线：输入转换→预过滤→编译→执行→显示→历史+事件，含异步支持 |

## 核心子系统

| 文档 | 说明 |
|------|------|
| [06-display-system.md](06-display-system.md) | MIME 多模态显示体系：DisplayObject 类层次、DisplayFormatter、DisplayPublisher、display() 公共 API |
| [07-input-transform.md](07-input-transform.md) | 基于 tokenize 的 AST 感知输入转换：魔法前缀、系统命令、帮助语法、Prompt 剥离 |
| [08-completer-history.md](08-completer-history.md) | Tab 补全系统（Jedi 补全/字典键补全/matcher 架构）、SQLite 历史管理、系统命令别名 |

## 扩展与定制

| 文档 | 说明 |
|------|------|
| [09-extension-system.md](09-extension-system.md) | 扩展加载/卸载机制、load_ipython_extension 入口点、内置扩展（autoreload/storemagic） |
| [10-events-hooks.md](10-events-hooks.md) | 事件系统（多回调广播）与钩子系统（单函数/链覆盖）、Events vs Hooks vs Extensions 选择指南 |
| [11-custom-magics.md](11-custom-magics.md) | 自定义魔法开发分步指南：@magics_class、@line_magic/@cell_magic、参数解析、行为装饰器 |

## 高级主题

| 文档 | 说明 |
|------|------|
| [12-async-support.md](12-async-support.md) | 顶层 await 原生支持、should_run_async 检测、asyncio/trio/curio 事件循环集成、%autoawait |
| [13-terminal-frontend.md](13-terminal-frontend.md) | TerminalInteractiveShell 终端增强、prompt_toolkit 集成、pt_inputhooks GUI 事件循环、embed() 嵌入 API |

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-getting-started
02-architecture-overview
03-shell-lifecycle
04-magic-system
05-execution-pipeline
06-display-system
07-input-transform
08-completer-history
09-extension-system
10-events-hooks
11-custom-magics
12-async-support
13-terminal-frontend
```
