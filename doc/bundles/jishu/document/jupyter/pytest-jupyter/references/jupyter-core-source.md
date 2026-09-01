---
okf_version: "0.2"
type: reference
title: "Core插件源码（jupyter_core.py）"
description: "pytest_jupyter/jupyter_core.py 的完整API：临时目录fixtures、asyncio事件循环管理、pytest异步测试钩子、环境隔离monkeypatch"
tags: [core-plugin, fixtures, asyncio, environment-isolation, monkeypatch, tmp-path, resource-limit]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:45:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:45:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: jupyter-core-py
    resource: "../../../../../external/libs/jupyter/pytest-jupyter/pytest_jupyter/jupyter_core.py"
    title: "pytest_jupyter/jupyter_core.py"
---

# Core插件源码（jupyter_core.py）

本信源登记 `pytest_jupyter/jupyter_core.py`（约179行）的核心fixtures、pytest hooks和初始化逻辑。jupyter_core.py 是pytest-jupyter的基础插件，被其他所有插件（client、server）通过`import *`继承。

## 模块级初始化

### 文件描述符限制设置

模块加载时（非fixture内），对Unix系统设置RLIMIT_NOFILE软限制为4096：

1. 尝试`import resource`（Unix专属），Windows下设为None
2. 获取当前软/硬限制：`soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)`
3. 若硬限制 >= DEFAULT_SOFT(4096)，将软限制设为4096
4. 若硬限制 < 软限制，将硬限制调整为等于软限制
5. 调用`resource.setrlimit(resource.RLIMIT_NOFILE, (soft, hard))`应用设置

[F-010]

## Pytest Hooks（异步测试支持）

### pytest_pycollect_makeitem(collector, name, obj) -> list | None

`@pytest.hookimpl(tryfirst=True)` 装饰的收集钩子。

**行为：**
- 若收集器过滤通过且被收集对象是协程函数（`iscoroutinefunction(obj)`返回True）
- 返回`list(collector._genfunctions(name, obj))`让pytest正常收集异步函数
- 否则返回None（不干预）

[F-011]

### pytest_pyfunc_call(pyfuncitem) -> bool

`@pytest.hookimpl(tryfirst=True)` 装饰的测试函数调用钩子。

**行为：**
1. 提取测试函数的fixture参数：`testargs = {arg: funcargs[arg] for arg in pyfuncitem._fixtureinfo.argnames}`
2. 若测试函数不是协程函数：直接同步调用`pyfuncitem.obj(**testargs)`，返回True
3. 若是协程函数：
   - 忽略WindowsSelectorEventLoopPolicy的DeprecationWarning
   - 通过`ensure_event_loop(prefer_selector_loop=True)`获取事件循环
   - 调用`loop.run_until_complete(pyfuncitem.obj(**testargs))`运行协程
   - 返回True（告诉pytest已处理调用）

[F-012]

## 核心Fixtures

### jp_asyncio_loop() (autouse=True)

`@pytest.fixture(autouse=True)` — 每个测试自动使用。

**行为：**
1. 忽略WindowsSelectorEventLoopPolicy的DeprecationWarning
2. 调用`ensure_event_loop(prefer_selector_loop=True)`（来自jupyter_core.utils）获取事件循环
3. yield该事件循环
4. 测试结束后调用`loop.close()`关闭循环

[F-013]

### jp_home_dir(tmp_path) -> Path

返回临时HOME目录路径：`mkdir(tmp_path, "home")`

[F-014]

### jp_data_dir(tmp_path) -> Path

返回临时Jupyter数据目录路径：`mkdir(tmp_path, "data")`

[F-015]

### jp_config_dir(tmp_path) -> Path

返回临时Jupyter配置目录路径：`mkdir(tmp_path, "config")`

[F-016]

### jp_runtime_dir(tmp_path) -> Path

返回临时Jupyter运行时目录路径：`mkdir(tmp_path, "runtime")`

[F-017]

### jp_system_jupyter_path(tmp_path) -> Path

返回临时系统级Jupyter数据路径：`mkdir(tmp_path, "share", "jupyter")`

[F-018]

### jp_env_jupyter_path(tmp_path) -> Path

返回临时环境级Jupyter数据路径：`mkdir(tmp_path, "env", "share", "jupyter")`

[F-019]

### jp_system_config_path(tmp_path) -> Path

返回临时系统级配置路径：`mkdir(tmp_path, "etc", "jupyter")`

[F-020]

### jp_env_config_path(tmp_path) -> Path

返回临时环境级配置路径：`mkdir(tmp_path, "env", "etc", "jupyter")`

[F-021]

### jp_kernel_dir(jp_data_dir) -> Path

返回内核spec目录路径：`mkdir(jp_data_dir, "kernels")`

[F-022]

### echo_kernel_spec(jp_kernel_dir) -> str

安装echo测试内核的kernelspec。

**行为：**
1. 创建目录 `{jp_kernel_dir}/echo/`
2. 构造argv列表：`[sys.executable, "-m", "pytest_jupyter.echo_kernel", "-f", "{connection_file}"]`
3. 构造kernel_data字典：`{"argv": argv, "display_name": "echo", "language": "echo"}`
4. 写入kernel.json文件到该目录
5. 返回目录路径字符串

[F-023]

### jp_environ(monkeypatch, tmp_path, jp_home_dir, jp_data_dir, jp_config_dir, jp_runtime_dir, echo_kernel_spec, jp_system_jupyter_path, jp_system_config_path, jp_env_jupyter_path, jp_env_config_path)

综合环境配置fixture，使用monkeypatch隔离Jupyter环境。

**monkeypatch的环境变量设置：**
1. `HOME` → `str(jp_home_dir)`
2. `PYTHONPATH` → `os.pathsep.join(sys.path)`
3. `JUPYTER_CONFIG_DIR` → `str(jp_config_dir)`
4. `JUPYTER_DATA_DIR` → `str(jp_data_dir)`
5. `JUPYTER_RUNTIME_DIR` → `str(jp_runtime_dir)`

**monkeypatch的模块属性替换（jupyter_core.paths）：**
6. `SYSTEM_JUPYTER_PATH` → `[str(jp_system_jupyter_path)]`
7. `ENV_JUPYTER_PATH` → `[str(jp_env_jupyter_path)]`
8. `SYSTEM_CONFIG_PATH` → `[str(jp_system_config_path)]`
9. `ENV_CONFIG_PATH` → `[str(jp_env_config_path)]`

[F-024]

## 设计要点

1. **三层隔离**：通过monkeypatch同时隔离环境变量和jupyter_core.paths模块属性，确保测试不污染用户真实Jupyter环境
2. **autouse事件循环**：`jp_asyncio_loop`是autouse fixture，每个测试自动获得干净的asyncio事件循环
3. **Selector Loop优先**：`prefer_selector_loop=True`确保在Windows上也使用SelectorEventLoop（与Jupyter的asyncio使用模式兼容）
4. **资源限制预防**：模块级设置RLIMIT_NOFILE防止"Too many open files"错误（Jupyter Server测试会打开大量socket和文件）
5. **依赖链清晰**：所有目录fixtures基于pytest内置的`tmp_path`，`jp_environ`聚合所有目录fixtures进行环境隔离
6. **钩子tryfirst**：两个pytest hooks都用`tryfirst=True`，确保pytest-jupyter的异步处理优先于其他插件
