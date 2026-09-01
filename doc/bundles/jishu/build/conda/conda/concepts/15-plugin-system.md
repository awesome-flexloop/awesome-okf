---
okf_version: "0.2"
type: "concept"
title: "pluggy插件体系"
sources:
  - "conda/plugins/manager.py"
  - "conda/plugins/hookspec.py"
  - "conda/plugins/config.py"
  - "conda/gateways/connection/session.py"
---

# pluggy插件体系

conda 使用 [pluggy](https://pluggy.readthedocs.io/)（pytest 的同款插件框架）构建了完整的插件体系，允许第三方通过标准入口点扩展求解器、子命令、虚拟包、报告后端、认证处理器等19种扩展点。插件在运行时通过 `importlib.metadata` 自动发现，无需手动注册。

## CondaPluginManager：插件管理器

`CondaPluginManager` 继承自 `pluggy.PluginManager`，是 conda 插件系统的核心 [F-068]：

```python
class CondaPluginManager(pluggy.PluginManager):
    def __init__(self, *args, **kwargs):
        super().__init__(APP_NAME, *args, **kwargs)  # APP_NAME = "conda"
        self.get_cached_solver_backend = functools.cache(self.get_solver_backend)
        self.get_cached_session_headers = functools.cache(self.get_session_headers)
        self.get_cached_request_headers = functools.cache(self.get_request_headers)
```

构造时初始化三个带缓存的方法：
- `get_cached_solver_backend()`：缓存求解器后端查找（高频调用路径）
- `get_cached_session_headers()`：缓存按 host 分组的 session 级 HTTP 头
- `get_cached_request_headers()`：缓存按 host+path 分组的 request 级 HTTP 头

### 单例获取

`get_plugin_manager()` 使用 `@functools.cache` 装饰器实现单例模式 `plugins/manager.py#L1373-L1395`：

```python
@functools.cache
def get_plugin_manager() -> CondaPluginManager:
    plugin_manager = CondaPluginManager()
    plugin_manager.add_hookspecs(CondaSpecs)
    plugin_manager.load_plugins(
        solvers, previews,
        *virtual_packages.plugins, *subcommands.plugins,
        *health_checks.plugins, *post_solves.plugins,
        *reporter_backends.plugins, *package_extractors.plugins,
        *prefix_data_loaders.plugins, *environment_specifiers.plugins,
        *environment_exporters.plugins,
    )
    plugin_manager.load_entrypoints(APP_NAME)  # 发现第三方插件
    return plugin_manager
```

### 插件发现机制

`load_entrypoints(group)` 使用 `importlib.metadata.distributions()` 遍历所有已安装的 Python 分发包，查找 `conda` 入口点组中的插件 [F-068]：

```python
def load_entrypoints(self, group, name=None):
    count = 0
    for dist in distributions():
        for entry_point in dist.entry_points:
            if entry_point.group != group:
                continue
            plugin = entry_point.load()  # 可能失败，优雅降级
            if self.register(plugin):
                self._plugin_distinfo.append((plugin, DistFacade(dist)))
                count += 1
    return count
```

加载失败时仅记录 WARNING 日志（因为 CLI logger 在参数解析后才初始化，此时可能无法输出 traceback），不影响 conda 主流程。

### 禁用外部插件

`disable_external_plugins()` 将所有非 `conda.plugins.` 前缀的插件标记为 blocked，对应 CLI 的 `--no-plugins` 选项或 `CONDA_NO_PLUGINS` 环境变量。这是排查插件导致问题的重要手段。

## hookspec 与 hookimpl

conda 使用 pluggy 的标记装饰器定义钩子规格和实现 [F-069]：

```python
_hookspec = pluggy.HookspecMarker(APP_NAME)  # 标记钩子规格
hookimpl = pluggy.HookimplMarker(APP_NAME)    # 标记钩子实现
```

所有钩子规格定义在 `CondaSpecs` 类中，使用 `@_hookspec` 装饰器标记。插件使用 `@hookimpl` 装饰器标记实现函数。

## 19种钩子类型

`CondaSpecs` 类定义了19种钩子规格，覆盖 conda 的主要扩展点 [F-070]：

| 钩子名 | 返回类型 | 用途 |
|---|---|---|
| `conda_solvers` | `Iterable[CondaSolver]` | 注册自定义求解器后端（如 libmamba） |
| `conda_subcommands` | `Iterable[CondaSubcommand]` | 注册外部 CLI 子命令 |
| `conda_virtual_packages` | `Iterable[CondaVirtualPackage]` | 注册虚拟包（如 `__cuda`、`__archspec`） |
| `conda_reporter_backends` | `Iterable[CondaReporterBackend]` | 注册输出报告后端（console/json） |
| `conda_auth_handlers` | `Iterable[CondaAuthHandler]` | 注册 HTTP 认证处理器 |
| `conda_pre_commands` | `Iterable[CondaPreCommand]` | 命令执行前钩子 |
| `conda_post_commands` | `Iterable[CondaPostCommand]` | 命令执行后钩子 |
| `conda_pre_solves` | `Iterable[CondaPreSolve]` | 求解前钩子 |
| `conda_post_solves` | `Iterable[CondaPostSolve]` | 求解后钩子 |
| `conda_pre_transaction_actions` | `Iterable[CondaPreTransactionAction]` | 事务执行前Action |
| `conda_post_transaction_actions` | `Iterable[CondaPostTransactionAction]` | 事务执行后Action |
| `conda_settings` | `Iterable[CondaSetting]` | 注册自定义配置参数 |
| `conda_session_headers` | `Iterable[CondaRequestHeader]` | 按host注册HTTP头 |
| `conda_request_headers` | `Iterable[CondaRequestHeader]` | 按host+path注册HTTP头 |
| `conda_health_checks` | `Iterable[CondaHealthCheck]` | 注册 conda doctor 健康检查 |
| `conda_error_hints` | `Iterable[CondaErrorHint]` | 为错误提供用户提示 |
| `conda_exception_observers` | `Iterable[CondaExceptionObserver]` | 异常观察器（类sys.excepthook） |
| `conda_prefix_data_loaders` | `Iterable[CondaPrefixDataLoader]` | 扩展已安装包数据加载 |
| `conda_package_extractors` | `Iterable[CondaPackageExtractor]` | 注册包格式提取器 |
| `conda_environment_specifiers` | `Iterable[CondaEnvironmentSpecifier]` | 注册环境文件格式解析器 |
| `conda_environment_exporters` | `Iterable[CondaEnvironmentExporter]` | 注册环境导出格式 |

### 关键钩子详解

**conda_solvers**：求解器完全可插拔。`Solver` API 通过 `context.plugin_manager.get_cached_solver_backend()` 获取后端类（参见 [17-public-api.md](17-public-api.md)），classic 求解器本身也是通过此钩子注册的内置插件。

**conda_virtual_packages**：虚拟包（如 `__cuda`、`__linux`、`__osx`、`__win`、`__archspec`）并非硬编码，而是通过插件钩子注入。每个虚拟包插件检测系统特性（CUDA版本、OS版本、CPU指令集）并返回对应 `PackageRecord`。

**conda_subcommands**：插件可注册新的 CLI 子命令。内置插件注册了 `doctor`、`plugins`、`config` 等子命令。插件子命令不能与内置命令重名（preview 插件除外）。

**conda_session_headers / conda_request_headers**：允许插件为特定 host 或 host+path 添加自定义 HTTP 请求头，但受 FORBIDDEN_HEADERS 安全限制。

**conda_exception_observers**：纯观察性钩子，类似 `sys.excepthook`，用于遥测和日志。任何异常都被 `BaseException` 捕获，绝不影响错误报告流程。

## FORBIDDEN_HEADERS：安全边界

`CondaSession` 定义了20个禁止插件设置的 HTTP 头 [F-075]，防止插件破坏 conda 的核心网络栈：

```python
FORBIDDEN_HEADERS = frozenset([
    "accept-charset", "accept-encoding",
    "access-control-request-headers", "access-control-request-method",
    "connection", "content-length", "cookie", "date", "dnt",
    "expect", "host", "keep-alive", "origin", "referer",
    "set-cookie", "te", "trailer", "transfer-encoding",
    "upgrade", "via",
])
```

此外，以 `proxy-` 或 `sec-` 开头的头也被禁止，`x-http-method-override` 等方法覆盖头不允许设置 CONNECT/TRACE/TRACK 方法。`_validate_plugin_headers()` 函数在设置插件头前逐一检查，违规时抛出 `PluginError`。

## 内置插件目录结构

内置插件位于 `conda/plugins/` 子目录 [F-071]：

```
conda/plugins/
├── solvers/              # classic 求解器（内置默认）
├── subcommands/          # 内置子命令（doctor/plugins/config 等）
├── virtual_packages/     # 虚拟包检测（archspec/cuda/conda/linux/osx/windows/freebsd）
├── reporter_backends/    # 报告后端（console/json）
├── environment_exporters/ # 环境导出格式
├── environment_specifiers/ # 环境文件格式解析
├── package_extractors/   # 包提取器（.conda/.tar.bz2）
├── prefix_data_loaders/  # PrefixData 加载器
├── post_solves/          # 求解后钩子
├── previews/             # 预览功能开关（feature flags）
├── manager.py            # CondaPluginManager
├── hookspec.py           # CondaSpecs（所有钩子规格）
├── config.py             # PluginConfig
└── types.py              # 数据类型定义（CondaSolver/CondaSubcommand等）
```

每个内置插件模块通常包含一个 `plugins` 列表或直接在模块级别用 `@hookimpl` 标记实现函数。

## PluginConfig：插件配置管理

`plugins/config.py` 提供 `PluginConfig` 类，用于管理插件注册的自定义配置参数 [F-072]。插件通过 `conda_settings` 钩子注册 `PrimitiveParameter`、`SequenceParameter` 或 `MapParameter`，`load_settings()` 方法将这些参数添加到全局配置系统中，使其可通过 `.condarc`、环境变量和命令行参数配置。

## _HookImplWrapper：实现包装

`CondaPluginManager._hookexec()` 重写了 pluggy 的钩子执行方法，使用 `_HookImplWrapper` 包装每个 HookImpl `plugins/manager.py#L324-L336`。包装器自动为插件返回的对象设置 `.impl` 属性，便于追溯插件来源（用于 `get_plugin_source()` 等方法），同时正确处理迭代器返回值和 hookwrapper。

## 插件冲突检测

`get_hook_results(name)` 方法在返回插件结果前执行冲突检测 `plugins/manager.py#L432-L488`：

1. **名称验证**：插件必须有小写的 `name` 属性（去除首尾空白）
2. **名称冲突**：同一钩子类型下不允许多个插件使用相同名称
3. **排序**：返回结果按插件名称排序，确保确定性

冲突时抛出 `PluginError`，列出所有冲突的插件及其来源。
