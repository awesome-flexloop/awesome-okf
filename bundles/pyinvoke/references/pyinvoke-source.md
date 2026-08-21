---
type: Reference
title: PyInvoke 源码信源登记
description: PyInvoke v3.0.3 源码路径、版本信息、核心模块清单与公开 API
tags: [pyinvoke, source, reference, v3.0.3]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T10:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T12:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pyinvoke-github
    resource: https://github.com/pyinvoke/invoke
    title: PyInvoke GitHub 仓库
    author: human:bitprophet
  - id: pyinvoke-docs
    resource: https://docs.pyinvoke.org
    title: PyInvoke 官方文档
---

# PyInvoke 源码信源登记

## 基本信息

| 属性 | 值 |
|------|-----|
| 项目名 | invoke（PyInvoke） |
| 版本 | **3.0.3** |
| 描述 | Pythonic task execution（Python 风格的任务执行库） |
| 作者 | Jeff Forcier (jeff@bitprophet.org) |
| 许可证 | BSD-2-Clause |
| Python 要求 | ≥ 3.9 |
| 官方文档 | <https://docs.pyinvoke.org> |
| 源码仓库 | <https://github.com/pyinvoke/invoke> |

## 源码位置

PyInvoke 源码位于 SpecWeave 仓库的外部依赖目录：

```
external/libs/pyinvoke/invoke/invoke/
```

该目录通过 git submodule 引入（vendor 区域），本地不做修改。

## CLI 入口点

`pyproject.toml` 定义了两个等价的命令行入口，均指向 `invoke.main:program.run`：

- `invoke` — 完整命令名
- `inv` — 短别名

入口模块为 `invoke/main.py`，它创建一个默认配置的 `Program` 实例：

```python
# invoke/main.py
from . import __version__, Program

program = Program(
    name="Invoke",
    binary="inv[oke]",
    binary_names=["invoke", "inv"],
    version=__version__,
)
```

`invoke/__main__.py` 支持 `python -m invoke` 方式调用，同样委托给 `program.run()`。

## 核心模块清单

| 模块 | 说明 |
|------|------|
| `__init__.py` | 包入口，导出所有公开 API：Task、Collection、Context、Config、Executor、Program、Runner 等核心类，以及 `run()`/`sudo()` 便捷函数，通过 `importlib.metadata` 获取 `__version__` |
| `main.py` | CLI 入口点，创建默认 `Program` 实例（`binary="inv[oke]"`，`binary_names=["invoke","inv"]`） |
| `__main__.py` | 支持 `python -m invoke` 调用，委托给 `main.program.run()` |
| `tasks.py` | 核心任务定义模块：包含 `Task` 类（任务对象）、`@task` 装饰器（支持 name/aliases/default/help/pre/post/autoprint/positional/optional/iterable/incrementable/auto_shortflags/klass 参数）、`Call` 类（带参数的任务调用）、`call()` 便捷函数 |
| `collection.py` | 任务集合/命名空间模块：`Collection` 类用于组织任务树、支持子集合嵌套、`from_module()` 自动发现、`configure()` 配置合并、`add_task()`/`add_collection()`、`task_names` 属性、名称自动转换（下划线↔连字符） |
| `context.py` | 上下文对象模块：`Context` 类（继承 DataProxy，封装 `run()`/`sudo()`/`cd()`/`prefix()` 方法、`command_cwds` 目录栈、`config` 属性）、`MockContext` 类（测试用模拟上下文，支持 Result/布尔/可迭代/字典四种 run 参数格式） |
| `config.py` | 配置系统模块：`Config` 类实现 9 层配置合并（defaults→collection→system→user→project→env→runtime→overrides→modifications）、`DataProxy` 类提供字典/属性双模式访问（嵌套 dict 自动递归包装）、`Environment` 类处理环境变量加载与类型转换、`merge_dicts()` 递归合并、`global_defaults()` 定义所有默认值 |
| `executor.py` | 任务执行器模块：`Executor` 类负责任务的实际调度执行，执行流程为 normalize→expand_calls→dedupe→execute，处理 pre/post 钩子链展开、Call 对象创建、per-call 配置加载（collection + shell env） |
| `program.py` | 命令行程序模块：`Program` 类是 CLI 顶层管理器，定义 `core_args()`（18 个核心标志）和 `task_args()`（3 个任务选项），处理配置创建→核心解析→集合加载→任务解析→清理→配置更新→执行的完整流程 |
| `runners.py` | 命令运行器模块：`Runner` 抽象基类（子类需实现 start/wait/returncode 等）、`Local` 本地运行器（使用 subprocess.Popen，支持 PTY）、`Result` 结果对象（封装 command/stdout/stderr/exited/return_code、ok/failed 属性、tail() 方法）、`Promise` 异步承诺、三线程 IO 模型（handle_stdout/handle_stderr/handle_stdin） |
| `loader.py` | 任务加载器模块：`FilesystemLoader` 类负责从文件系统发现并加载任务模块，从起始目录向上递归搜索 `tasks.py` 或 `tasks/` 包，支持 `-c/--collection` 指定替代模块名 |
| `exceptions.py` | 异常定义模块：定义所有 Invoke 专属异常类，包括 `Exit`、`ParseError`、`Failure`（含 `UnexpectedExit`、`CommandTimedOut`、`AuthFailure`）、`ThreadException`、`ResponseNotAccepted`、`WatcherError`、`AmbiguousEnvVar`、`UncastableEnvVar`、`UnknownFileType`、`UnpicklableConfigMember`、`CollectionNotFound`、`PlatformError`、`SubprocessPipeError` |
| `parser/` | 命令行解析器子包：`Argument`（参数定义，支持 names/kind/optional/positional/default/help 等属性）、`Parser`（解析器，维护 ParserContext 列表）、`ParserContext`（解析上下文，包含 flag 和 positional args）、`ParseResult`（解析结果），处理短标志自动生成、下划线转短横线、位置参数/可选参数/可迭代参数/可递增参数的解析逻辑 |
| `watchers.py` | 输出监控器模块：`StreamWatcher`（threading.local 基类，submit(stream) 方法）、`Responder`（pattern+response 正则匹配，基于 index 增量扫描累积 buffer）、`FailingResponder`（增加 sentinel 失败检测，检测到失败标记抛 ResponseNotAccepted） |
| `terminals.py` | 终端工具模块：`pty_size()` 获取伪终端尺寸（默认 80x24）、`character_buffered()` cbreak 模式上下文管理器、`ready_for_reading()` 非阻塞 IO 检测、`bytes_to_read()` FIONREAD ioctl、`WINDOWS` 平台常量 |
| `util.py` | 工具函数模块：`Lexicon`（支持别名的属性字典）、`helpline()`（提取文档首行帮助文本）、`debug()` 调试输出、`task_name_sort_key()` 任务排序等通用工具 |
| `env.py` | 环境变量模块：`Environment` 类遍历 Config 键路径生成 `INVOKE_` 前缀环境变量名，支持类型转换（bool/int/list 等） |
| `completion/` | Tab 补全子包：`complete()` 函数实现 Bash/Zsh/Fish 的动态补全逻辑（标志补全、任务名补全），附带三种 shell 的静态补全脚本（bash.completion、zsh.completion、fish.completion） |
| `vendor/` | 内嵌第三方依赖（不分包安装）：`fluidity`（状态机）、`lexicon`（属性字典）、`yaml`（PyYAML 完整副本） |

## 公开 API 导出

`invoke/__init__.py` 通过显式导入导出以下核心符号（`# noqa` 标记表示是有意的重导出）：

- **核心类**：`Collection`、`Config`、`Context`、`MockContext`、`Executor`、`FilesystemLoader`、`Program`、`Task`
- **解析器类**：`Argument`、`Parser`、`ParserContext`、`ParseResult`
- **运行器类**：`Failure`、`Local`、`Promise`、`Result`、`Runner`
- **任务工具**：`Call`、`call`、`task`（装饰器）
- **监控器**：`FailingResponder`、`Responder`、`StreamWatcher`
- **便捷函数**：`run()`（创建匿名 Context 执行命令）、`sudo()`（创建匿名 Context 执行 sudo 命令）、`pty_size()`
- **异常类**：`Exit`、`ParseError`、`AuthFailure`、`CollectionNotFound`、`CommandTimedOut`、`PlatformError`、`ResponseNotAccepted`、`ThreadException`、`UnexpectedExit`、`AmbiguousEnvVar`、`UncastableEnvVar`、`UnknownFileType`、`UnpicklableConfigMember`、`WatcherError`、`SubprocessPipeError`

[^pyinvoke-github]: PyInvoke 源码仓库：<https://github.com/pyinvoke/invoke>
[^pyinvoke-docs]: PyInvoke 官方文档：<https://docs.pyinvoke.org>
