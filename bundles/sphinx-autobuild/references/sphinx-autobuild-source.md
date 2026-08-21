---
type: Reference
title: sphinx-autobuild 源码信源登记
description: sphinx-autobuild 源码路径、版本、核心模块清单与公开 API 导出列表
tags: [sphinx-autobuild, source, reference]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T14:50:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: sphinx-autobuild-repo
    resource: /references/sphinx-autobuild-source.md
    title: sphinx-autobuild GitHub Repository
---

# sphinx-autobuild 源码信源登记

## 源码位置

- **本地路径**：`external/libs/docs/sphinx-autobuild/`
- **上游仓库**：https://github.com/sphinx-doc/sphinx-autobuild
- **版本**：2025.08.25（`__version__ = "2025.08.25"`）

## 版本与依赖

| 项 | 值 |
|---|---|
| 包名 | `sphinx-autobuild` |
| 版本 | `2025.08.25` |
| Python 要求 | `>=3.11` |
| 构建系统 | `flit-core>=3.7` |
| 许可证 | MIT |

### 运行时依赖

| 包名 | 最低版本 | 用途 |
|------|---------|------|
| `colorama` | >=0.4.6 | Windows 控制台彩色输出 |
| `Sphinx` | （无下限） | 文档构建引擎 |
| `starlette` | >=0.35 | ASGI Web 框架 |
| `uvicorn` | >=0.25 | ASGI 服务器 |
| `watchfiles` | >=0.20 | 文件系统监听 |
| `websockets` | >=11 | WebSocket 支持（starlette 传递依赖） |

### CLI 入口

```
sphinx-autobuild = "sphinx_autobuild.__main__:main"
```

## 核心模块清单

sphinx-autobuild 包结构简洁，共 7 个 Python 文件：

```
sphinx_autobuild/
├── __init__.py       # 版本声明
├── __main__.py       # CLI 入口、参数解析、ASGI 应用创建
├── build.py          # Builder 类：封装 sphinx-build 调用
├── filter.py         # IgnoreFilter 类：文件路径忽略规则
├── middleware.py      # JavascriptInjectorMiddleware：热重载脚本注入
├── server.py         # RebuildServer 类：文件监听 + WebSocket 服务
└── utils.py          # 工具函数（端口查找、浏览器打开、日志输出）
```

### 模块详细说明

#### `__init__.py`

- `__version__ = "2025.08.25"`：版本号常量

#### `__main__.py`

| 符号 | 类型 | 可见性 | 说明 |
|------|------|--------|------|
| `main(argv=())` | 函数 | 公开 | CLI 入口函数 |
| `_create_app(watch_dirs, ignore_handler, builder, out_dir, url_host)` | 函数 | 私有 | 创建 Starlette ASGI 应用 |
| `_parse_args(argv)` | 函数 | 私有 | 双阶段参数解析 |
| `_get_sphinx_build_parser()` | 函数 | 私有 | 获取定制化的 Sphinx 参数解析器 |
| `_get_parser()` | 函数 | 私有 | 获取 autobuild 自有参数解析器 |
| `_add_autobuild_arguments(parser)` | 函数 | 私有 | 添加 autobuild 命令行选项组 |

#### `build.py`

| 符号 | 类型 | 说明 |
|------|------|------|
| `Builder` | 类 | 封装 sphinx-build 子进程调用 |
| `Builder.__init__(sphinx_args, *, url_host, pre_build_commands, post_build_commands)` | 方法 | 初始化，接收 sphinx 参数、服务 URL、前后置命令 |
| `Builder.__call__(*, changed_paths)` | 方法 | 执行构建（可调用对象），接收变更路径列表 |
| `Builder._run_commands(commands, log_context)` | 方法 | 执行前置/后置命令列表 |

#### `filter.py`

| 符号 | 类型 | 说明 |
|------|------|------|
| `IgnoreFilter` | 类 | 文件路径忽略过滤器 |
| `IgnoreFilter.__init__(regular, regex_based)` | 方法 | 初始化，接收 glob 路径列表和正则列表 |
| `IgnoreFilter.__call__(filename)` | 方法 | 判断文件是否应被忽略（可调用对象） |
| `IgnoreFilter.__repr__()` | 方法 | 调试用字符串表示 |

#### `middleware.py`

| 符号 | 类型 | 说明 |
|------|------|------|
| `web_socket_script(ws_url)` | 函数 | 生成 WebSocket 热重载的 JavaScript 代码片段 |
| `JavascriptInjectorMiddleware` | 类 | ASGI 中间件，向 HTML 响应注入重载脚本 |
| `JavascriptInjectorMiddleware.__init__(app, ws_url)` | 方法 | 初始化，包装下游 ASGI 应用 |
| `JavascriptInjectorMiddleware.__call__(scope, receive, send)` | 方法 | ASGI 调用接口 |

#### `server.py`

| 符号 | 类型 | 说明 |
|------|------|------|
| `RebuildServer` | 类 | 文件监听 + WebSocket 广播服务器 |
| `RebuildServer.__init__(paths, ignore_filter, change_callback)` | 方法 | 初始化，接收监听路径、忽略过滤器、变更回调 |
| `RebuildServer.lifespan(app)` | 方法 | Starlette lifespan 上下文管理器 |
| `RebuildServer.main()` | 方法 | 主循环：运行 watch 任务和退出等待 |
| `RebuildServer.watch()` | 方法 | 异步文件监听循环 |
| `RebuildServer.__call__(scope, receive, send)` | 方法 | WebSocket 连接处理 |
| `RebuildServer.watch_reloads(ws)` | 方法 | 向 WebSocket 客户端发送重载信号 |
| `RebuildServer.wait_client_disconnect(ws)` | 静态方法 | 等待客户端断开连接 |

#### `utils.py`

| 符号 | 类型 | 说明 |
|------|------|------|
| `find_free_port()` | 函数 | 查找并返回一个空闲端口号 |
| `open_browser(url_host, delay)` | 函数 | 延迟后在默认浏览器中打开 URL |
| `show_message(context)` | 函数 | 显示青色上下文消息 |
| `show_command(command)` | 函数 | 显示蓝色命令行文本 |

## 测试文件

| 文件 | 覆盖范围 |
|------|---------|
| `tests/test_application.py` | 应用集成测试：Builder 构建 + Starlette TestClient 验证 |
| `tests/test_ignore.py` | IgnoreFilter 单元测试：空过滤、正则、glob、混合、调试模式 |

## 公开 API 说明

sphinx-autobuild **没有正式的公开 Python API**。所有功能通过命令行 `sphinx-autobuild` 入口使用。源码中的类（`Builder`、`IgnoreFilter`、`RebuildServer`、`JavascriptInjectorMiddleware`）虽然可以被 import，但属于内部实现，不保证稳定性。
