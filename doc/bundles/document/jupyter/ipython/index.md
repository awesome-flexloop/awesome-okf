---
type: OKF
title: IPython 教程
description: IPython v9.17.0.dev 增强型 Python REPL 的完整教程——三层架构、魔法命令系统、代码执行管线、MIME 显示系统、扩展机制和集成实践
tags: [ipython, jupyter, repl, python, shell, magic, interactive]
version: 9.17.0.dev
source: https://github.com/ipython/ipython
website: https://ipython.org
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
---

# IPython 增强型 Python REPL 教程

IPython 是 Python 的增强交互式解释器（REPL），提供语法高亮、Tab 补全、对象内省、魔法命令、富文本显示、历史记录、异步支持和可扩展架构等特性。它是 Jupyter Notebook/Lab 的 Python 内核（ipykernel）的基础，也是数据科学和科学计算领域最广泛使用的交互式 Python 环境。

IPython 采用三层分离架构：`TerminalIPythonApp` 负责命令行启动和配置加载，`InteractiveShell` 是与 UI 无关的核心执行引擎，`TerminalInteractiveShell` 提供终端前端适配。同一核心引擎被 Jupyter 内核通过 ZeroMQ 消息协议复用，实现了终端和 Notebook 两种前端的代码执行一致性。

## 📚 快速导航

### [概念文档](concepts/index.md)
- [00-简介](concepts/00-introduction.md) — IPython 是什么、核心特性、与 Jupyter 关系、生态系统
- [01-快速开始](concepts/01-getting-started.md) — 安装、启动、第一个会话、命令行参数
- [02-架构总览](concepts/02-architecture-overview.md) — 三层架构（App→Shell→Frontend）、核心组件、数据流
- [03-Shell 生命周期](concepts/03-shell-lifecycle.md) — 31 步初始化序列、命名空间管理、主循环、退出流程
- [04-魔法命令系统](concepts/04-magic-system.md) — 装饰器注册、LazyMagic 懒加载、MagicsManager、行/单元魔法
- [05-代码执行管线](concepts/05-execution-pipeline.md) — 六阶段管线：转换→预过滤→编译→执行→显示→历史+事件
- [06-显示系统](concepts/06-display-system.md) — MIME 多模态显示、DisplayObject 层次、DisplayFormatter、display()
- [07-输入转换与特殊语法](concepts/07-input-transform.md) — 基于 tokenize 的 AST 感知转换、%/!/ ? 语法
- [08-补全、历史与别名](concepts/08-completer-history.md) — Tab 补全（Jedi/matcher）、SQLite 历史、AliasManager
- [09-扩展系统](concepts/09-extension-system.md) — ExtensionManager、load/unload_extension、内置扩展
- [10-事件与钩子](concepts/10-events-hooks.md) — EventManager 多回调广播、Hooks 单函数覆盖、CommandChainDispatcher
- [11-自定义魔法开发](concepts/11-custom-magics.md) — @magics_class、@line_magic/@cell_magic、参数解析
- [12-异步支持](concepts/12-async-support.md) — 顶层 await、asyncio/trio/curio 运行器、%autoawait
- [13-终端前端与 GUI 集成](concepts/13-terminal-frontend.md) — prompt_toolkit、pt_inputhooks、embed()、快捷键

### [实践示例](examples/index.md)
- [01-IPython 基本使用](examples/01-basic-usage.md) — 安装启动、In/Out 变量、快捷键、帮助系统
- [02-魔法命令实战](examples/02-using-magics.md) — 常用行/单元魔法（%timeit/%run/%%bash/%%writefile）
- [03-富文本输出与 display()](examples/03-display-rich-output.md) — HTML/Markdown/Image 输出、update_display、富显示协议
- [04-创建自定义魔法命令](examples/04-custom-magic.md) — @magics_class 自定义魔法完整步骤、SQL 魔法示例
- [05-IPython 扩展开发](examples/05-extension-basics.md) — 扩展入口点、autoreload、pip 可安装扩展打包
- [06-事件监听与钩子定制](examples/06-event-hooks.md) — 事件回调计时、自定义编辑器钩子、embed() 调试

### [信源参考](references/index.md)
- [InteractiveShell API 参考](references/interactiveshell-source.md) — 核心 Shell 类完整 API（属性/方法/初始化序列）
- [应用层 API 参考](references/app-source.md) — TerminalIPythonApp、BaseIPythonApplication、启动流程
- [魔法系统 API 参考](references/magic-source.md) — MagicsManager、Magics 基类、装饰器、内置魔法清单
- [显示系统 API 参考](references/display-source.md) — DisplayFormatter、DisplayObject 层次、DisplayPublisher
- [输入转换 API 参考](references/inputtransformer-source.md) — TransformerManager、输入转换器、特殊语法处理
- [事件与钩子 API 参考](references/events-hooks-source.md) — EventManager、HookManager、预定义事件列表
- [扩展系统 API 参考](references/extension-source.md) — ExtensionManager、扩展入口点协议
- [历史/补全/别名 API 参考](references/history-completer-source.md) — HistoryManager、IPCompleter、AliasManager
- [事实清单](facts.md) — 从源码采集的 537 条零推测事实
- [架构洞察](insights.md) — 5 个核心洞察四元组（陈述/证据/反常识/行动）与知识地图

## 🚀 快速开始

```bash
pip install ipython
```

启动 IPython 终端：

```bash
ipython
```

最简单的交互体验：

```python
In [1]: 1 + 1
Out[1]: 2

In [2]: %timeit sum(range(1000))
15.1 μs ± 83.3 ns per loop (mean ± std. dev. of 7 runs, 100,000 loops each)

In [3]: from IPython.display import HTML, display
   ...: display(HTML('<b>Hello, <i>IPython</i>!</b>'))
<b>Hello, <i>IPython</i>!</b>

In [4]: import numpy as np
   ...: np.linspace(0, 1, 5)
Out[4]: array([0.  , 0.25, 0.5 , 0.75, 1.  ])
```

## 🎯 核心特性

| 特性 | 说明 |
|------|------|
| 🪄 魔法命令 | 80+ 内置行魔法（%timeit/%run/%pwd）和单元魔法（%%bash/%%writefile/%%html），支持自定义 |
| 🔍 对象内省 | ?/?? 查看文档和源码，%pdef/%pdoc/%psource/%pfile 详细内省 |
| 🎨 富文本显示 | MIME 多模态输出（HTML/Markdown/SVG/PNG/Latex/JSON），display() 统一 API |
| ⌨️ Tab 补全 | Jedi 智能补全、字典键补全、文件路径补全、魔术命令补全 |
| 📜 历史管理 | SQLite 持久化历史、上下箭头导航、%history/%recall/%rerun |
| ⚡ 异步原生 | 顶层 await、asyncio/trio/curio 事件循环集成、%autoawait |
| 🔌 可扩展 | 扩展系统（%load_ext）、事件回调、自定义钩子、自定义魔法 |
| 🐛 增强调试 | %debug/%pdb、Verbose/Context/Plain 异常模式、ultratb 美化 traceback |
| 📦 自动重载 | %autoreload 自动重新加载修改的模块，开发效率利器 |
| 🖥️ 终端增强 | prompt_toolkit 语法高亮、自动缩进、多行编辑、GUI 事件循环集成 |

## 📖 推荐学习路径

1. **入门了解**：阅读 [00-简介](concepts/00-introduction.md) 和 [01-快速开始](concepts/01-getting-started.md)，跟着 [01-基本使用](examples/01-basic-usage.md) 动手操作
2. **理解架构**：学习 [02-架构总览](concepts/02-architecture-overview.md) 理解三层分离设计
3. **掌握核心**：深入 [03-Shell 生命周期](concepts/03-shell-lifecycle.md)、[04-魔法命令系统](concepts/04-magic-system.md)、[05-代码执行管线](concepts/05-execution-pipeline.md)
4. **常用功能**：学习 [06-显示系统](concepts/06-display-system.md)、[07-输入转换](concepts/07-input-transform.md)、[08-补全历史别名](concepts/08-completer-history.md)
5. **实战练习**：跟着 [02-魔法命令实战](examples/02-using-magics.md) 和 [03-富文本输出](examples/03-display-rich-output.md) 练习
6. **扩展定制**：掌握 [09-扩展系统](concepts/09-extension-system.md)、[10-事件与钩子](concepts/10-events-hooks.md)、[11-自定义魔法](concepts/11-custom-magics.md)
7. **高级主题**：学习 [12-异步支持](concepts/12-async-support.md) 和 [13-终端前端](concepts/13-terminal-frontend.md)

## 📊 架构概览

```
┌──────────────────────────────────────────────────────────────────┐
│                    终端启动 (TerminalIPythonApp)                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  TerminalIPythonApp(BaseIPythonApplication, InteractiveShellApp) │
│  │  • 命令行参数解析 (argparse)                                │
│  │  • 配置文件加载 (ipython_config.py)                         │
│  │  • 子命令分发 (profile/kernel/locate/history)               │
│  │  • initialize(): init_path→init_shell→init_banner→...      │
│  │  • start(): shell.mainloop() 启动 REPL                      │
│  └──────────────────────────┬─────────────────────────────────┘  │
│                             │ instance(parent=self, ...)          │
├─────────────────────────────┼────────────────────────────────────┤
│                             ▼                                     │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  InteractiveShell (SingletonConfigurable) ← 核心引擎        │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │  输入处理                                            │  │  │
│  │  │  • input_transformer_manager → TransformerManager    │  │  │
│  │  │  • prefilter_manager → AutoMagic/Alias/ESC           │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │  代码执行                                            │  │  │
│  │  │  • compiler → CachingCompiler (缓存编译)             │  │  │
│  │  │  • run_ast_nodes / run_code (同步/异步)              │  │  │
│  │  │  • should_run_async → 顶层 await 检测               │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │  子系统组件                                          │  │  │
│  │  │  • magics_manager → MagicsManager (80+魔法)         │  │  │
│  │  │  • display_formatter → DisplayFormatter (12 MIME)   │  │  │
│  │  │  • history_manager → HistoryManager (SQLite)        │  │  │
│  │  │  • events → EventManager (5+生命周期事件)            │  │  │
│  │  │  • extension_manager → ExtensionManager             │  │  │
│  │  │  • completer → IPCompleter (Jedi补全)               │  │  │
│  │  │  • alias_manager → AliasManager                     │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │  命名空间                                            │  │  │
│  │  │  • user_ns (用户命名空间: In/Out/_/__/___)           │  │  │
│  │  │  • user_global_ns (全局命名空间)                     │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────┬─────────────────────────────────┘  │
│                             │ 继承                                │
├─────────────────────────────┼────────────────────────────────────┤
│                             ▼                                     │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  TerminalInteractiveShell (InteractiveShell) ← 终端前端     │  │
│  │  • prompt_toolkit 富终端（语法高亮/自动缩进/多行编辑）      │  │
│  │  • Prompts/ClassicPrompts 提示符                           │  │
│  │  • pt_inputhooks GUI 事件循环集成 (Qt/Gtk/Tk/WX/asyncio)  │  │
│  │  • confirm_exit/term_title/autoedit_syntax                │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  IPKernelShell (ipykernel) ← Jupyter 内核前端              │  │
│  │  • ZeroMQ 消息协议替代 stdin/stdout                        │  │
│  │  • 复用 InteractiveShell 核心执行引擎                      │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

## 🔗 外部资源

- **官方网站**：[ipython.org](https://ipython.org)
- **GitHub 仓库**：[ipython/ipython](https://github.com/ipython/ipython)
- **官方文档**：[ipython.readthedocs.io](https://ipython.readthedocs.io)
- **Jupyter 项目**：[jupyter.org](https://jupyter.org)
- **ipykernel**：[ipython/ipykernel](https://github.com/ipython/ipykernel) — IPython 的 Jupyter 内核
- **traitlets**：[ipython/traitlets](https://github.com/ipython/traitlets) — IPython 使用的配置框架
- **prompt_toolkit**：[prompt_toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit) — 终端 UI 库

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
facts
insights
log
```
