# 源码信源索引

本目录登记 pytest-jupyter 所有核心模块的源码信源文档，提供API级别的事实参考。

## 信源文档列表

| 文档 | 源码文件 | 行数 | 核心内容 |
|------|---------|------|---------|
| [入口与版本](init-source.md) | `__init__.py`, `_version.py`, `pyproject.toml` | ~25 | 包导出结构、版本定义、依赖声明、插件入口 |
| [工具函数](utils-source.md) | `utils.py` | ~13 | `mkdir` 临时目录创建函数 |
| [Core插件](jupyter-core-source.md) | `jupyter_core.py` | ~179 | 异步测试钩子、事件循环fixture、临时目录fixtures、环境隔离monkeypatch |
| [Echo内核](echo-kernel-source.md) | `echo_kernel.py` | ~70 | EchoKernel回显内核、EchoKernelApp启动类、do_execute方法 |
| [Client插件](jupyter-client-source.md) | `jupyter_client.py` | ~57 | ZMQ上下文fixture、内核启动工厂、资源自动清理 |
| [Tornado异步测试](pytest-tornasync-source.md) | `pytest_tornasync.py` | ~101 | IOLoop管理、HTTP服务器/客户端fixtures、AsyncHTTPServerClient类 |
| [Server插件](jupyter-server-source.md) | `jupyter_server.py` | ~543 | ServerApp生命周期、HTTP/WebSocket请求工厂、Notebook创建、认证授权测试工具 |

## 模块依赖关系

```
pytest_jupyter/__init__.py (导入jupyter_core的所有内容)
└── pytest_jupyter/jupyter_core.py (基础插件)
    ├── pytest_jupyter/utils.py (工具函数)
    ├── pytest_jupyter/pytest_tornasync.py (导入jupyter_core)
    ├── pytest_jupyter/jupyter_client.py (导入jupyter_core)
    │   └── pytest_jupyter/echo_kernel.py (被client和server插件使用的内核)
    └── pytest_jupyter/jupyter_server.py (导入jupyter_core + pytest_tornasync，间接获得client)
```

## 阅读顺序建议

1. 先读 [入口与版本](init-source.md) 了解包结构和插件入口
2. 再读 [Core插件](jupyter-core-source.md) 理解基础fixtures和异步支持
3. 按兴趣方向阅读：
   - 内核测试方向：[Echo内核](echo-kernel-source.md) → [Client插件](jupyter-client-source.md)
   - Server测试方向：[Tornado异步测试](pytest-tornasync-source.md) → [Server插件](jupyter-server-source.md)

```{toctree}
:maxdepth: 7

echo-kernel-source
init-source
jupyter-client-source
jupyter-core-source
jupyter-server-source
pytest-tornasync-source
utils-source
```
