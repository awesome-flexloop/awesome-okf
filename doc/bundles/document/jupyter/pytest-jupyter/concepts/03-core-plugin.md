---
okf_version: "0.2"
type: concept
title: "Core插件详解"
description: "深入理解 jupyter_core 插件：环境隔离机制、asyncio事件循环管理、异步测试pytest钩子、临时目录fixtures体系、echo_kernel_spec安装。"
tags: [core-plugin, jp-environ, asyncio, event-loop, pytest-hooks, monkeypatch, tmp-path, file-descriptor-limit]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:45:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:45:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: jupyter-core-source
    resource: "/references/jupyter-core-source.md"
    title: "Core插件源码信源"
  - id: utils-source
    resource: "/references/utils-source.md"
    title: "工具函数源码信源"
---

# Core插件详解

Core插件（`pytest_jupyter.jupyter_core`）是pytest-jupyter的基础层，提供环境隔离、asyncio事件循环管理和异步测试钩子三大核心能力。所有其他插件（client、server）都通过`import *`继承Core插件的所有fixtures。

## 模块级初始化：文件描述符限制

Core插件在模块加载时（非fixture内）执行一段初始化代码，调整Unix系统的文件描述符限制：

```python
if resource is not None:
    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    DEFAULT_SOFT = 4096
    if hard >= DEFAULT_SOFT:
        soft = DEFAULT_SOFT
    if hard < soft:
        hard = soft
    resource.setrlimit(resource.RLIMIT_NOFILE, (soft, hard))
```

**为什么需要这个？** Jupyter Server测试会打开大量ZMQ socket、HTTP连接和临时文件，默认的文件描述符软限制（通常1024）可能不够用。这里将软限制提升到4096（前提是硬限制允许），防止"Too many open files"错误。Windows上`resource`模块不可用，设为None跳过。

[F-010]

## 异步测试基础设施

Core插件最核心的贡献是让pytest原生支持`async def test_*`风格的异步测试，无需安装pytest-asyncio。

### jp_asyncio_loop（autouse fixture）

```python
@pytest.fixture(autouse=True)
def jp_asyncio_loop():
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message=".*WindowsSelectorEventLoopPolicy.*", ...)
        loop = ensure_event_loop(prefer_selector_loop=True)
    yield loop
    loop.close()
```

**关键点：**
- `autouse=True`：每个测试自动获得独立的事件循环，无需在测试函数参数中声明
- `prefer_selector_loop=True`：在Windows上优先使用SelectorEventLoop（与Jupyter/tornado的asyncio使用模式兼容），而非ProactorEventLoop
- 测试结束后调用`loop.close()`清理循环
- 忽略WindowsSelectorEventLoopPolicy的DeprecationWarning（Python 3.10+在Windows上发出此警告）

[F-013]

### pytest_pycollect_makeitem 钩子

```python
@pytest.hookimpl(tryfirst=True)
def pytest_pycollect_makeitem(collector, name, obj):
    if collector.funcnamefilter(name) and iscoroutinefunction(obj):
        return list(collector._genfunctions(name, obj))
    return None
```

这个钩子让pytest在测试收集阶段能正确识别`async def test_xxx`协程函数作为测试用例。`tryfirst=True`确保在其他插件之前处理。

[F-011]

### pytest_pyfunc_call 钩子

```python
@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem):
    funcargs = {arg: funcargs[arg] for arg in pyfuncitem._fixtureinfo.argnames}
    if not iscoroutinefunction(pyfuncitem.obj):
        pyfuncitem.obj(**testargs)
        return True
    loop = ensure_event_loop(prefer_selector_loop=True)
    loop.run_until_complete(pyfuncitem.obj(**testargs))
    return True
```

这是异步测试执行的核心钩子：
1. 提取测试函数需要的fixture参数
2. 同步函数：直接调用，返回True（告诉pytest"我已处理"）
3. 异步函数：获取事件循环，用`run_until_complete`运行协程，返回True
4. `return True` 告诉pytest不要再尝试调用该函数

[F-012]

## 临时目录Fixtures体系

Core插件基于pytest内置的`tmp_path` fixture，创建了一套Jupyter专用的临时目录：

| Fixture | 路径结构 | 对应Jupyter概念 |
|---------|---------|----------------|
| `jp_home_dir` | `{tmp_path}/home` | HOME目录（~） |
| `jp_data_dir` | `{tmp_path}/data` | Jupyter用户数据目录 |
| `jp_config_dir` | `{tmp_path}/config` | Jupyter配置目录 |
| `jp_runtime_dir` | `{tmp_path}/runtime` | Jupyter运行时文件目录 |
| `jp_system_jupyter_path` | `{tmp_path}/share/jupyter` | 系统级数据路径（sys.prefix/share/jupyter） |
| `jp_env_jupyter_path` | `{tmp_path}/env/share/jupyter` | 环境级数据路径 |
| `jp_system_config_path` | `{tmp_path}/etc/jupyter` | 系统级配置路径 |
| `jp_env_config_path` | `{tmp_path}/env/etc/jupyter` | 环境级配置路径 |
| `jp_kernel_dir` | `{jp_data_dir}/kernels` | 内核spec目录 |

所有这些fixtures都通过`mkdir(tmp_path, *parts)`工具函数创建，该函数使用`pathlib.Path.mkdir(parents=True)`递归创建目录。

[F-014] ~ [F-022]

## 环境隔离核心：jp_environ

`jp_environ`是Core插件中最重要的fixture，它聚合了所有临时目录fixtures，通过monkeypatch将Jupyter的环境变量和路径模块属性全部重定向到临时目录：

```python
@pytest.fixture
def jp_environ(monkeypatch, tmp_path, jp_home_dir, jp_data_dir,
               jp_config_dir, jp_runtime_dir, echo_kernel_spec,
               jp_system_jupyter_path, jp_system_config_path,
               jp_env_jupyter_path, jp_env_config_path):
```

### monkeypatch操作清单

| monkeypatch目标 | 设置值 | 影响 |
|----------------|-------|------|
| `os.environ["HOME"]` | `str(jp_home_dir)` | 重定向HOME目录 |
| `os.environ["PYTHONPATH"]` | `os.pathsep.join(sys.path)` | 确保临时环境能导入当前Python路径 |
| `os.environ["JUPYTER_CONFIG_DIR"]` | `str(jp_config_dir)` | 重定向配置目录 |
| `os.environ["JUPYTER_DATA_DIR"]` | `str(jp_data_dir)` | 重定向数据目录 |
| `os.environ["JUPYTER_RUNTIME_DIR"]` | `str(jp_runtime_dir)` | 重定向运行时目录 |
| `jupyter_core.paths.SYSTEM_JUPYTER_PATH` | `[str(jp_system_jupyter_path)]` | 替换系统数据路径列表 |
| `jupyter_core.paths.ENV_JUPYTER_PATH` | `[str(jp_env_jupyter_path)]` | 替换环境数据路径列表 |
| `jupyter_core.paths.SYSTEM_CONFIG_PATH` | `[str(jp_system_config_path)]` | 替换系统配置路径列表 |
| `jupyter_core.paths.ENV_CONFIG_PATH` | `[str(jp_env_config_path)]` | 替换环境配置路径列表 |

**为什么同时monkeypatch环境变量和模块属性？** 因为`jupyter_core.paths`中的路径发现函数（如`jupyter_data_dir()`）既读取环境变量，也有自己的默认路径列表（SYSTEM_JUPYTER_PATH等）。只设置环境变量不足以完全隔离——某些路径发现逻辑可能绕过环境变量直接使用模块级列表。

[F-024]

## echo_kernel_spec

`echo_kernel_spec` fixture在`{jp_kernel_dir}/echo/`目录下安装echo测试内核的kernelspec：

```python
argv = [sys.executable, "-m", "pytest_jupyter.echo_kernel", "-f", "{connection_file}"]
kernel_data = {"argv": argv, "display_name": "echo", "language": "echo"}
```

它创建一个`kernel.json`文件，指向`pytest_jupyter.echo_kernel`模块作为内核启动入口。这样在测试环境中可以通过内核名`"echo"`启动一个快速回显内核。

[F-023]

## 隔离效果验证

当你在测试中使用`jp_environ`（或依赖它的任何高层fixture），以下代码验证隔离效果：

```python
def test_environ(jp_environ):
    from jupyter_core import paths
    import os
    # 数据目录存在（在临时路径下）
    assert os.path.exists(paths.jupyter_data_dir())
    # 配置目录在临时路径下
    assert "tmp_path" in paths.jupyter_config_dir() or "tmp" in paths.jupyter_config_dir()
```

## Core插件使用建议

1. **不需要server/client时直接使用core**：测试纯工具函数、路径操作、配置加载等不涉及网络/内核的代码时，加载`pytest_jupyter`即可
2. **jp_environ是入口fixture**：大多数情况下你只需要声明`jp_environ`依赖（或使用依赖它的高层fixture），不需要单独使用各个jp_*_dir fixtures
3. **async test开箱即用**：加载core插件后，直接写`async def test_xxx()`即可，不需要额外装饰器
4. **不要混用pytest-asyncio**：core插件的异步钩子与pytest-asyncio冲突，选择其一
5. **autouse的代价**：`jp_asyncio_loop`是autouse的，意味着每个测试都会创建/销毁事件循环——这对大多数测试是透明的，但如果你有特殊的事件循环需求需注意

---

**下一步阅读：**
- [Client插件详解](04-client-plugin.md) — 内核启动、ZMQ管理、echo kernel使用
- [Tornado异步支持](06-tornasync-plugin.md) — HTTP服务器/客户端测试基础设施
- [Server插件详解](05-server-plugin.md) — 完整的Jupyter Server测试栈
