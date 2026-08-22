---
okf_version: "0.2"
type: concept
title: "架构总览"
description: "理解 pytest-jupyter 的三层插件架构、fixture依赖链、插件加载机制、import*继承模式与核心设计哲学。"
tags: [architecture, plugin-hierarchy, fixture-dependencies, import-star, event-loop, lifecycle, design-philosophy]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:45:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T14:45:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: jupyter-core-source
    resource: "/references/jupyter-core-source.md"
    title: "Core插件源码信源"
  - id: jupyter-client-source
    resource: "/references/jupyter-client-source.md"
    title: "Client插件源码信源"
  - id: jupyter-server-source
    resource: "/references/jupyter-server-source.md"
    title: "Server插件源码信源"
  - id: pytest-tornasync-source
    resource: "/references/pytest-tornasync-source.md"
    title: "Tornado异步测试源码信源"
---

# 架构总览

pytest-jupyter 是一个**分层的pytest插件集合**，通过"基础层+增量层"的设计，让使用者按需引入测试能力，同时保证各层fixtures的无缝继承。本文从架构层面解析其设计思路。

## 模块文件结构

```
pytest_jupyter/
├── __init__.py          # 包入口：导入jupyter_core的所有内容
├── _version.py          # 版本号定义
├── utils.py             # 工具函数（mkdir）
├── jupyter_core.py      # Core插件：环境隔离+异步基础
├── echo_kernel.py       # Echo测试内核
├── jupyter_client.py    # Client插件：内核管理
├── pytest_tornasync.py  # Tornado异步HTTP测试（内嵌）
└── jupyter_server.py    # Server插件：完整Server测试栈
```

## 插件加载与继承机制

pytest-jupyter 不使用 setuptools entry points 注册插件，而是要求用户在 `conftest.py` 中通过 `pytest_plugins` 列表显式声明要加载的插件模块。

### import * 继承模式

各插件层之间通过 `from .xxx import *` 实现fixture继承：

```python
# jupyter_client.py
from pytest_jupyter.jupyter_core import *  # 继承core所有fixtures

# pytest_tornasync.py
from pytest_jupyter.jupyter_core import *  # 继承core所有fixtures

# jupyter_server.py
from pytest_jupyter.jupyter_core import *      # 继承core
from pytest_jupyter.pytest_tornasync import *  # 继承tornasync（间接获得core）
from pytest_jupyter.utils import mkdir
```

**这种设计的特点：**
1. **无需pytest插件依赖声明**：通过Python的`import *`机制，高层模块加载时自动将低层模块的fixtures带入pytest的fixture注册表
2. **显式优于隐式**：用户加载`jupyter_server`就能获得所有层的fixtures，无需手动加载多个插件
3. **零额外依赖声明**：不需要在pyproject.toml中配置pytest插件依赖关系

[F-003]

### 插件包含关系矩阵

| 加载的插件 | 获得core fixtures | 获得tornasync fixtures | 获得client fixtures | 获得server fixtures |
|-----------|:---:|:---:|:---:|:---:|
| `pytest_jupyter` / `pytest_jupyter.jupyter_core` | ✅ | ❌ | ❌ | ❌ |
| `pytest_jupyter.jupyter_client` | ✅ | ❌ | ✅ | ❌ |
| `pytest_jupyter.pytest_tornasync` | ✅ | ✅ | ❌ | ❌ |
| `pytest_jupyter.jupyter_server` | ✅ | ✅ | ✅（间接） | ✅ |

## Fixture依赖链（DAG）

理解fixture之间的依赖关系是正确使用pytest-jupyter的关键。以下是核心fixture的依赖有向无环图：

```
tmp_path (pytest内置)
├── jp_home_dir ──────────────────────────────┐
├── jp_data_dir ─────────────────────────┐    │
│   ├── jp_kernel_dir ── echo_kernel_spec│    │
│   └── jp_nbconvert_templates ──────────│────│──── jp_configurable_serverapp
├── jp_config_dir ───────────────────────│────│────┐
├── jp_runtime_dir ──────────────────────│────│────┤
├── jp_system_jupyter_path ──────────────│────│────┤
├── jp_system_config_path ───────────────│────│────┤
├── jp_env_jupyter_path ─────────────────│────│────┤
├── jp_env_config_path ── jp_extension_environ  │    │
│   │                                           │    │
jp_asyncio_loop (autouse) ◄─────────────────────┘    │
├── io_loop (tornasync)                             │
├── http_server_port (tornasync)                    │
│   ├── http_server ◄── jp_web_app ◄── jp_serverapp │
│   │   └── http_server_client                      │
│   └── jp_http_port                                │
├── jp_start_kernel                                 │
└── jp_server_cleanup (autouse)                     │
                                                    │
jp_environ ◄─────────────────────────────────────┘
  (聚合所有目录fixtures + monkeypatch)
    │
    ├── jp_configurable_serverapp ◄── jp_serverapp
    │   ├── jp_web_app ── http_server
    │   ├── jp_auth_header
    │   └── jp_fetch / jp_ws_fetch / send_request
    └── jp_start_kernel (client层)
```

### 关键fixture解析顺序

pytest按DAG拓扑顺序解析fixtures，pytest-jupyter精心设计了fixture的执行顺序：

1. **`jp_nbconvert_templates` 必须在 `jp_environ` 之前执行**：它需要在monkeypatch改变Jupyter路径之前，从真实环境中找到nbconvert模板并复制到临时目录
2. **`jp_environ` 是聚合点**：依赖所有临时目录fixtures，一次性完成所有monkeypatch操作
3. **`jp_configurable_serverapp` 依赖jp_environ**：确保ServerApp启动时环境已隔离
4. **`jp_server_cleanup` 是autouse**：每个测试结束后自动清理ServerApp资源
5. **`jp_asyncio_loop` 是autouse**：每个测试自动获得独立的asyncio事件循环

[F-078]

## 异步测试支持架构

pytest-jupyter 实现了自己的异步测试运行机制（不依赖pytest-asyncio），核心由两个pytest hook和一个fixture构成：

### 钩子层（Hooks）

```
pytest_pycollect_makeitem (tryfirst=True)
    │ 识别async def test_*函数，让pytest正常收集它们
    ▼
pytest_pyfunc_call (tryfirst=True)
    │ 拦截测试函数调用：
    │ - 同步函数：直接调用
    │ - 异步函数：获取事件循环，run_until_complete执行
    ▼
jp_asyncio_loop (autouse=True)
    │ 提供ensure_event_loop(prefer_selector_loop=True)创建的事件循环
    │ 测试结束后loop.close()
```

**为什么不用pytest-asyncio？** pytest-asyncio与tornado的IOLoop存在事件循环冲突。Jupyter Server基于tornado，需要SelectorEventLoop，而pytest-asyncio的默认事件循环策略可能不兼容。pytest-jupyter直接控制事件循环的创建和运行，避免了这类冲突。

[F-011][F-012][F-013]

## ServerApp生命周期管理

`jp_configurable_serverapp`是server层最核心的fixture，它实现了一个完整的工厂模式：

```
调用 jp_configurable_serverapp(**kwargs)
    │
    ├── ServerApp.clear_instance()  # 清除已有单例
    ├── 合并默认config + 用户config
    ├── 注入jupyter_server_terminals扩展（v2默认）
    ├── 设置NotebookNotary.db_file = ":memory:"
    ├── 生成随机token（8字符hex）
    ├── 创建ServerApp.instance(log_level="DEBUG", port=..., ...)
    ├── app.init_signal = lambda: None  # 禁用信号处理
    ├── app.initialize(argv=..., new_httpserver=False)
    ├── 重定向日志StreamHandler到jp_logging_stream
    └── app.start_app() → 返回app实例
        │
        测试使用app...
        │
        ▼ (jp_server_cleanup autouse)
    ├── app._cleanup()
    ├── app.kernel_manager.context.destroy()
    └── ServerApp.clear_instance()
```

**关键设计决策：**
- `new_httpserver=False`：ServerApp不自己创建HTTP服务器，而是由pytest_tornasync的`http_server` fixture统一管理，这样测试客户端能直接连接
- `port_retries=0`：不自动重试端口，端口冲突立即报错（测试环境应使用空闲端口）
- `open_browser=False`：测试中绝不打开浏览器
- `allow_root=True`：允许在Docker/root环境下运行（CI/CD常见场景）

[F-080][F-084]

## 资源管理与清理策略

pytest-jupyter 采用多层资源清理保障：

| 层级 | 机制 | 清理内容 |
|------|------|---------|
| Fixture yield后 | 各fixture的teardown代码 | ZMQ context终止、kernel shutdown、HTTP server stop、socket close |
| autouse fixture | `jp_server_cleanup` | ServerApp._cleanup()、kernel_manager.context.destroy()、clear_instance() |
| autouse fixture | `jp_asyncio_loop` | loop.close() |
| 工厂fixture追踪 | kms/kcs列表 | jp_start_kernel追踪所有启动的内核，yield后逐一shutdown |

**防御性断言：**
- `jp_start_kernel` 清理后断言 `km.context.closed == True`，ZMQ上下文泄漏立即失败
- `jp_server_cleanup` 捕获并忽略清理过程中的RuntimeError和SystemExit（避免因清理错误导致测试失败）

[F-032][F-084]

## 设计哲学

### 1. 环境隔离优先
所有测试运行在由pytest tmp_path提供的临时目录中，通过monkeypatch替换Jupyter的环境变量和路径模块属性，确保测试完全不影响用户真实环境。

### 2. 工厂fixture模式
核心交互fixtures（`jp_configurable_serverapp`、`jp_fetch`、`jp_ws_fetch`、`jp_start_kernel`、`jp_create_notebook`）都采用"返回内部函数"的工厂模式，而非直接返回资源。这允许测试在单个测试用例中灵活创建多个资源实例。

### 3. 合理默认 + 完全可覆盖
每个fixture提供合理的默认值（如`jp_base_url`默认`"/a%40b/"`、`jp_argv`默认`[]`），但所有默认值都可以通过简单覆盖fixture来自定义。

### 4. 测试速度优化
- 提供`EchoKernel`替代重量级IPython内核
- `NotebookNotary.db_file = ":memory:"`使用内存SQLite
- 随机端口分配避免等待
- `port_retries=0`快速失败

### 5. v1/v2双版本兼容
通过`is_v2 = version_info[0] == 2`标志，在同一套代码中兼容Jupyter Server 1.x和2.x的API差异（token位置、默认扩展配置等）。

[F-070]

## 外部依赖关系

```
pytest-jupyter
├── pytest (>=7.0) ──── 插件系统、fixture机制、tmp_path
├── jupyter_core (>=5.7) ── 路径管理、ensure_event_loop
│
├── [client] 可选
│   ├── jupyter_client (>=7.4.0) ── 内核管理、KernelManager
│   ├── nbformat (>=5.3) ── Notebook格式读写
│   └── ipykernel (>=6.14) ── Kernel基类、IPKernelApp
│
├── [server] 可选（含client）
│   ├── jupyter_server (>=1.21) ── ServerApp、Authorizer、API handlers
│   └── tornado ── HTTP服务器/客户端、WebSocket、IOLoop
│
└── [test] 开发依赖
    └── pytest-timeout ── 测试超时保护
```

---

**下一步阅读：**
- [Core插件详解](/concepts/03-core-plugin.md) — 深入环境隔离、异步测试钩子和临时目录fixtures
- [Client插件详解](/concepts/04-client-plugin.md) — 内核管理和ZMQ资源
- [Server插件详解](/concepts/05-server-plugin.md) — ServerApp生命周期和HTTP/WebSocket测试
