---
type: concept
title: "00 - IPython 简介"
description: IPython 是什么——增强的交互式 Python REPL，核心特性、与 Jupyter 的关系、生态系统
tags: [introduction, overview, ipython, repl, jupyter]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: ipython-init
    title: IPython/__init__.py
  - id: ipython-release
    title: IPython/core/release.py
---

## 什么是 IPython

IPython（Interactive Python）是一个**功能增强的交互式 Python 解释器（REPL）**，由 Fernando Perez 于 2001 年创建，采用 BSD-3-Clause 开源许可证发布 [F-002]。当前版本为 9.17.0.dev（开发版），由 "The IPython Development Team" 维护，官方主页为 https://ipython.org [F-001][F-003][F-004]。

IPython 在标准 Python REPL 的基础上提供了大量生产力增强功能，是 Python 生态中最广泛使用的交互式计算环境。它不仅是一个独立的终端工具，更是 Jupyter 项目的核心组件——Jupyter Notebook/Lab 使用的 Python 内核（ipykernel）就建立在 IPython 的执行引擎之上。

### 与标准 Python REPL 的对比

| 特性 | 标准 Python REPL | IPython |
|------|-----------------|---------|
| **Tab 补全** | 基础关键字/变量补全 | Jedi 智能补全、字典键补全、模块属性补全 |
| **对象内省** | `dir()`/`help()` | `?`/`??` 快速内省、`pdef`/`pdoc`/`psource`/`pfile` |
| **魔法命令** | 无 | `%` 行魔法、`%%` 单元魔法，80+ 内置魔法 |
| **历史记录** | readline 基础历史 | SQLite 持久化历史、跨会话搜索、`%history`/`%recall`/`%rerun` |
| **富显示** | `__repr__()` 纯文本 | MIME 多模态显示（HTML/Markdown/SVG/图片/LaTeX） |
| **Shell 集成** | 无 | `!command` 系统命令、`%cd`/`%pwd`/别名系统 |
| **异步支持** | Python 3.8+ 顶层 await 受限 | 原生 async/await、asyncio/trio/curio 事件循环集成 |
| **调试** | `pdb` 基础调试 | `%debug`/`%pdb`、增强 traceback（xmode） |
| **扩展机制** | 无 | 扩展插件系统、事件钩子、自定义魔法 |

## 核心特性

### 增强的交互式 REPL

IPython 的核心是一个增强的交互式 Shell，提供优于标准 Python REPL 的交互体验 [F-200][F-216]。它支持多行编辑、语法高亮、自动缩进、提示符自定义等功能，在终端中通过 prompt_toolkit 库实现富交互 [F-530]。

### 魔法命令系统

IPython 最具特色的功能是魔法命令（Magic Commands）[F-300][F-330]。魔法命令以 `%`（行魔法）或 `%%`（单元魔法）为前缀，提供了大量超出 Python 语法的便捷功能：

- **行魔法**（`%magic`）：作用于单行输入，如 `%timeit`（性能测试）、`%run`（运行脚本）、`%pwd`（查看目录）、`%cd`（切换目录）、`%load_ext`（加载扩展）
- **单元魔法**（`%%magic`）：作用于整个代码单元，如 `%%timeit`、`%%html`、`%%javascript`、`%%capture`

默认情况下 automagic 模式开启 [F-304]，行魔法可以省略 `%` 前缀直接输入命令名（如直接输入 `pwd` 等价于 `%pwd`）。

### MIME 富显示体系

IPython 实现了基于 MIME 类型的多模态显示系统 [F-380][F-410]，允许对象以多种格式呈现：

- **文本**：Pretty 格式化输出
- **HTML/Markdown**：富文本渲染（在 Jupyter 中）
- **SVG/PNG/JPEG**：图形和图像
- **LaTeX/Math**：数学公式
- **JSON/GeoJSON**：结构化数据
- **Javascript**：交互式脚本
- **Video/ProgressBar**：多媒体和进度指示

对象通过实现 `_repr_html_`、`_repr_svg_`、`_repr_png_` 等方法（富显示协议）声明自己的显示能力 [F-384]。

### Tab 智能补全

IPython 提供强大的 Tab 补全系统 [F-440][F-446]，基于 Jedi 库实现语义级补全，支持：

- 模块属性和方法补全
- 字典键补全
- 文件路径补全
- 魔法命令补全
- 自定义匹配器扩展（MatcherAPIv2 协议）

### 对象内省

通过 `?` 和 `??` 语法，IPython 提供快速对象内省能力 [F-500][F-502]：

- `obj?`：显示对象文档字符串（等价于 `pinfo`）
- `obj??`：显示对象源代码（等价于 `pinfo2`）
- `%pdef obj`：显示函数签名
- `%pdoc obj`：显示文档字符串
- `%psource obj`：显示源代码
- `%pfile obj`：显示定义所在文件

### 历史记录管理

IPython 使用 SQLite 数据库持久化存储命令历史 [F-422][F-423]，支持：

- 跨会话历史访问
- 历史搜索（`%history`、`%recall`、`%rerun`）
- 后台异步保存（HistorySavingThread）[F-424]
- In/Out 历史变量（`_ih`、`_oh`、`In`、`Out`、`_`、`__`、`___`）[F-232]

### 原生异步支持

IPython 7.0+ 原生支持 Python 的 async/await 语法 [F-480][F-481]：

- 顶层 `await` 直接可用（无需包装在 async 函数中）
- 支持 asyncio（默认）、trio、curio 三种异步运行器
- `%autoawait` 魔法控制异步行为
- `_pseudo_sync_runner` 兼容无事件循环环境

### 可扩展架构

IPython 提供多层次的扩展机制 [F-430][F-360][F-370]：

- **扩展插件**（Extensions）：通过 `load_ipython_extension()` 入口点安装模块级扩展
- **魔法命令**（Magics）：注册自定义 `%`/`%%` 命令
- **事件系统**（Events）：监听 pre/post_execute 等生命周期事件
- **钩子系统**（Hooks）：覆盖 editor、pager、clipboard 等默认行为
- **输入转换**：自定义输入预处理管线

## 版本与许可

| 属性 | 值 |
|------|-----|
| 版本 | 9.17.0.dev [F-001] |
| version_info | (9, 17, 0, '.dev') [F-010] |
| 许可证 | BSD-3-Clause [F-002] |
| 作者 | The IPython Development Team [F-003] |
| 邮箱 | ipython-dev@python.org [F-003] |
| 主页 | https://ipython.org [F-004] |

## 与 Jupyter 的关系

IPython 和 Jupyter 的关系是理解整个生态的关键：

1. **IPython 是 Jupyter 的 Python 内核**：Jupyter Notebook/JupyterLab 通过 ipykernel 包与 IPython 交互，ipykernel 将 IPython 的执行引擎（InteractiveShell）包装为 ZeroMQ 消息协议的内核服务。终端 IPython 和 Jupyter Python 内核共享同一个核心执行引擎 [F-200][F-012]。

2. **历史演进**：IPython 最初包含 Notebook 功能（IPython Notebook），2014 年项目拆分，语言无关的 Notebook 部分演变为 Jupyter 项目（支持 Julia、Python、R 等多种语言），IPython 专注于 Python 交互式计算。`embed_kernel()` 函数已标记为弃用，直接委托给 `ipykernel.embed.embed_kernel()` [F-012]。

3. **核心复用**：IPython 的 `InteractiveShell` 类被设计为与前端无关的核心引擎 [F-201]。终端前端通过 `TerminalInteractiveShell` 子类接入（使用 stdin/stdout），Jupyter 内核通过 ipykernel 的 `IPythonKernel` 接入（使用 ZeroMQ 消息）。

```
IPython 项目
├── IPython 核心包（本 Wiki 覆盖范围）
│   ├── core/           ← InteractiveShell 执行引擎（终端和 Jupyter 共享）
│   ├── terminal/       ← 终端前端适配（prompt_toolkit、pt_inputhooks）
│   ├── extensions/     ← 内置扩展（autoreload、storemagic）
│   └── lib/、utils/    ← 工具库
│
└── Jupyter 生态（相关项目，非本 Wiki 范围）
    ├── ipykernel       ← Jupyter Python 内核（包装 IPython 核心）
    ├── ipywidgets      ← 交互式 Widget
    ├── jupyter_client  ← Jupyter 客户端协议
    ├── jupyter_server  ← Jupyter 服务端
    └── notebook/lab    ← Jupyter Notebook/Lab 前端
```

## 顶层包结构

IPython 包的目录结构清晰地反映了其架构分层 [F-020][F-021]：

```
IPython/
├── __init__.py         ← 公共 API 入口：start_ipython、embed、embed_kernel [F-007]
├── __main__.py         ← python -m IPython 入口，调用 start_ipython() [F-005]
├── display.py          ← 顶层 display API 重导出 [F-415]
├── paths.py            ← IPython 目录路径工具 [F-514]
│
├── core/               ← 核心引擎（50+ 模块）
│   ├── interactiveshell.py  ← InteractiveShell 核心类 [F-200]
│   ├── magic.py             ← 魔法命令系统 [F-300]
│   ├── magics/              ← 内置魔法类（15 个模块）[F-023]
│   ├── inputtransformer2.py ← 输入转换管线 [F-350]
│   ├── compilerop.py        ← CachingCompiler [F-450]
│   ├── display.py           ← DisplayObject 层次 [F-410]
│   ├── formatters.py        ← 12 种 MIME formatter [F-384]
│   ├── displaypub.py        ← DisplayPublisher [F-390]
│   ├── displayhook.py       ← DisplayHook [F-400]
│   ├── events.py            ← EventManager 事件系统 [F-360]
│   ├── hooks.py             ← Hooks 钩子系统 [F-370]
│   ├── history.py           ← HistoryManager SQLite 历史 [F-422]
│   ├── extensions.py        ← ExtensionManager [F-430]
│   ├── completer.py         ← IPCompleter 补全 [F-440]
│   ├── prefilter.py         ← PrefilterManager [F-460]
│   ├── alias.py             ← AliasManager 别名 [F-470]
│   ├── async_helpers.py     ← 异步运行器 [F-480]
│   └── oinspect.py          ← Inspector 对象内省 [F-500]
│
├── terminal/           ← 终端前端适配 [F-024]
│   ├── ipapp.py             ← TerminalIPythonApp 应用入口 [F-100]
│   ├── interactiveshell.py  ← TerminalInteractiveShell [F-240]
│   ├── prompts.py           ← 提示符类（Prompts/ClassicPrompts）
│   ├── pt_inputhooks/       ← GUI 事件循环集成（8 种框架）[F-025]
│   └── shortcuts/           ← prompt_toolkit 快捷键 [F-025]
│
├── extensions/         ← 内置扩展 [F-026]
│   ├── autoreload.py        ← %autoreload 自动重载 [F-520]
│   ├── storemagic.py        ← %store 变量持久化 [F-521]
│   └── deduperreload/       ← 去重重载 [F-522]
│
├── utils/              ← 30+ 工具模块 [F-027]
├── lib/                ← 附加库（backgroundjobs、clipboard、deepreload 等）[F-029]
├── testing/            ← 测试工具 [F-030]
├── external/           ← 外部依赖捆绑 [F-028]
└── sphinxext/          ← Sphinx 文档扩展
```

## 公共 API 入口

IPython 顶层 `__init__.py` 暴露了三个核心公共 API [F-007]：

```python
# 启动一个完整的 IPython 实例（加载配置、startup 文件）
from IPython import start_ipython
start_ipython(argv=None, **kwargs)  # [F-011]

# 在当前作用域嵌入 IPython（调试用，跳过完整初始化）
from IPython import embed  # 延迟导入 [F-008]
embed()

# 嵌入 Jupyter 内核（已弃用，应直接用 ipykernel）
from IPython import embed_kernel  # [F-012]
```

`InteractiveShell`、`sys_info`、`extract_module_locals` 也在顶层导出 [F-006]。`embed` 和 `get_ipython` 通过 `__getattr__` 延迟导入以加速 `import IPython` [F-008]。

## 相关概念

- [快速开始](01-getting-started.md)
- [架构总览](02-architecture-overview.md)
- [魔法命令系统](04-magic-system.md)
- [信源参考索引](../references/index.md)
