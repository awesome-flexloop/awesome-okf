---
okf_version: "0.2"
type: "concept"
title: "异常体系与错误处理"
sources:
  - "conda/__init__.py"
  - "conda/exceptions.py"
  - "conda/exception_handler.py"
---

# 异常体系与错误处理

conda 建立了以 `CondaError` 为根的完整异常层次体系，配合 `ExceptionHandler` 全局异常处理器，统一处理用户错误、系统错误、信号中断和未预期异常，并支持结构化错误报告和插件错误提示扩展。

## CondaError 基类

`CondaError` 定义在 `conda/__init__.py` 中，是所有 conda 异常的基类 [F-005]：

```python
class CondaError(Exception):
    return_code: int = 1       # 默认退出码
    reportable: bool = False   # 是否可上报给核心维护者

    def __init__(self, message, *args, caused_by=None, guidance=None, **kwargs):
        self.message = message or ""
        self._kwargs = kwargs
        self._caused_by = caused_by
        self._guidance = ErrorGuidance.coerce(guidance) if guidance else None
```

核心属性：
- **return_code**：进程退出码，默认为1。子类可覆盖（如 `CondaExitZero` 为0，`ArgumentError` 为2）
- **reportable**：标记异常是否包含可上报的错误报告信息
- **caused_by**：链式异常，记录导致当前错误的底层异常
- **guidance**：结构化错误指导（`ErrorGuidance` 对象），包含 `cause`、`summary` 和 `hints` 列表，为用户提供可操作的修复建议

### printf 风格消息格式化

`CondaError.__str__()` 使用 Python 的 `%` 运算符做 printf 风格格式化 [F-006]：

```python
def __str__(self):
    if not self._kwargs:
        return str(self.message)
    return str(self.message) % self._kwargs
```

这意味着抛出异常时，`message` 中的 `%(key)s` 占位符会被 `**kwargs` 中的值替换：

```python
# 示例
raise CondaError(
    "Package '%(package)s' not found in channel %(channel)s",
    package="numpy",
    channel="conda-forge"
)
# str() 输出: "Package 'numpy' not found in channel conda-forge"
```

若格式化失败（如占位符不匹配），会在 stderr 打印调试信息后重新抛出异常。

### dump_map() 结构化序列化

`dump_map()` 方法将异常序列化为字典，用于 JSON 输出模式（`--json`）和错误报告，包含：异常类型、异常名、消息、repr、caused_by、所有 kwargs 以及 guidance（若有）[F-005]。

## CondaMultiError：批量异常容器

`CondaMultiError` 用于收集多个错误一并抛出，是典型的控制流产物而非面向用户的单一错误 [F-007]：

```python
class CondaMultiError(CondaError):
    def __init__(self, errors: Iterable[CondaError]):
        self.errors = errors
        super().__init__(None)

    def __str__(self):
        return "\n".join(str(e) for e in self.errors) + "\n"
```

设计要点：
- 自身不携带 `guidance`，指导信息由各叶子错误独立提供
- `contains(exception_class)` 方法检查是否包含特定类型的异常
- `__repr__` 使用 `e.__repr__()` 而非 `repr(e)`，避免 Python 将其转回 `str()` 导致信息丢失
- 在事务操作（如包链接）中，可能遇到多个路径冲突或权限错误，此时收集所有错误一并报告

## CondaExitZero：正常退出异常

`CondaExitZero` 的 `return_code = 0` [F-008]，用于表示"正常但需要退出"的场景。它有两个重要子类：

- **DryRunExit**：`--dry-run` 模式执行完毕后的正常退出
- **CondaSystemExit**：同时继承 `CondaExitZero` 和 `SystemExit`，用于需要触发 SystemExit 语义的场景

以异常方式实现"正常退出"的好处是可以在任意调用栈深度直接退出，而无需逐层传递返回值。

## CondaSignalInterrupt：信号处理

`conda_signal_handler(signum, frame)` 是全局信号处理函数 [F-009]：

```python
ACTIVE_SUBPROCESSES: Iterable[Popen] = set()

def conda_signal_handler(signum, frame):
    for p in ACTIVE_SUBPROCESSES:
        if p.poll() is None:
            p.send_signal(signum)
    raise CondaSignalInterrupt(signum)
```

该函数注册在 `conda/__init__.py` 中（便于下游代码 monkey-patch），行为是：
1. 遍历 `ACTIVE_SUBPROCESSES` 集合，向所有仍在运行的子进程转发信号
2. 抛出 `CondaSignalInterrupt` 异常，由异常处理器统一处理

`CondaSignalInterrupt` 在 `exceptions.py` 中定义，使用 `get_signal_name()` 将信号编号转为可读名称，消息格式为 `"Signal interrupt %(signal_name)s"`。

## Help 异常体系

Help 类异常（`return_code = 0`）用于将帮助信息显示作为控制流：

- **Help**：帮助信息基类
- **ActivateHelp/DeactivateHelp**：activate/deactivate 命令的帮助文本
- **GenericHelp**：通用命令帮助（hook/commands/reactivate）

在 activate.py 的 `_parse_and_set_args()` 中，若检测到 `-h`/`--help`/`/?` 标志，直接抛出对应的 Help 异常，由异常处理器捕获并输出帮助文本（退出码0）。

## 异常层次概览

conda 定义了60+ 种异常类，主要分类如下：

| 类别 | 代表异常 | 说明 |
|---|---|---|
| 参数/命令 | `ArgumentError`, `TooManyArgumentsError`, `CommandNotFoundError` | 命令行参数错误、命令未找到 |
| 通道/网络 | `ChannelError`, `ChannelNotAllowed`, `ChannelDenied`, `UnavailableInvalidChannel`, `CondaHTTPError`, `CondaSSLError`, `AuthenticationError`, `ProxyError` | 通道配置、HTTP、SSL、认证错误 |
| 包/求解 | `PackagesNotFoundError`, `UnsatisfiableError`, `InvalidVersionSpec`, `InvalidMatchSpec` | 包未找到、依赖冲突、规范格式错误 |
| 文件系统 | `PathNotFoundError`, `DirectoryNotFoundError`, `NotWritableError`, `NoWritableEnvsDirError`, `LinkError`, `ClobberError` 系列 | 路径不存在、权限不足、文件冲突 |
| 环境 | `EnvironmentLocationNotFound`, `EnvironmentNameNotFound`, `CorruptedEnvironmentError`, `EnvironmentIsFrozenError` | 环境不存在、损坏、被冻结 |
| 事务 | `RemoveError`, `CyclicalDependencyError`, `PaddingError`, `BinaryPrefixReplacementError` | 卸载错误、循环依赖、二进制补丁错误 |
| IO/内存 | `CondaIOError`, `CondaFileIOError`, `CondaMemoryError`, `ChecksumMismatchError` | IO错误、OOM、校验和不匹配 |
| 插件 | `PluginError` | 插件加载/配置错误 |

`UnsatisfiableError` 是最复杂的异常之一，它接收求解器返回的冲突链 `bad_deps`（按冲突类型分类为 `direct`/`python`/`virtual_package`/`request_conflict_with_history`），格式化输出冲突链，并通过 `_get_guidance()` 生成结构化修复建议。

## ExceptionHandler：全局异常处理器

`ExceptionHandler` 类 `exception_handler.py#L26-L435` 是所有 CLI 入口的统一异常处理入口，通过 `conda_exception_handler()` 函数创建实例并调用：

```python
def conda_exception_handler(func, *args, **kwargs):
    exception_handler = ExceptionHandler()
    return exception_handler(func, *args, **kwargs)
```

`__call__` 方法用 try-except 包裹目标函数，`handle_exception()` 根据异常类型分发处理：

1. **CondaError（非reportable）**→ `handle_application_exception()`：打印异常消息，返回 `exc_val.return_code`
2. **CondaError（reportable）**→ `handle_reportable_application_exception()`：生成完整错误报告（含traceback、conda info、环境变量），格式化输出
3. **EnvironmentError with errno=ENOSPC**：包装为 `NoSpaceLeftError` 处理
4. **MemoryError**：包装为 `CondaMemoryError` 处理
5. **KeyboardInterrupt**：打印 "KeyboardInterrupt"，返回1
6. **SystemExit**：直接返回 `exc_val.code`
7. **其他未预期异常**→ `handle_unexpected_exception()`：生成完整错误报告（含traceback和conda info），提示用户使用 `--no-plugins` 排除插件问题

### 异常观察器插件

在处理异常前，`handle_exception()` 先调用 `context.plugin_manager.invoke_exception_observers(exc_val, exc_tb)` [F-070]，通知注册的 `conda_exception_observers` 插件。这些观察器遵循 CPython `sys.excepthook` 模型：纯粹观察、不能抑制/修改/重定向异常，异常被 `BaseException` 级别捕获并记录 DEBUG 日志，确保有 bug 的插件不会破坏错误报告流程。

### 插件错误提示

`ExceptionHandler` 调用 `context.plugin_manager.get_error_hints(error)` 获取插件提供的 `CondaErrorHint`，附加到错误的 guidance 中。每个插件独立调用，失败被隔离，hint_code 去重时核心 guidance 优先。

### JSON 输出模式

当 `context.json` 为 True（`--json` 选项），错误报告以 JSON 格式输出到 stdout，结构包含 `error`、`exception_name`、`exception_type`、`command`、`traceback`、`conda_info` 和 `conda_error_components` 字段。
