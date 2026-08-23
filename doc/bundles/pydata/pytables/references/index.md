# 信源登记簿（References）

本目录包含 PyTables 库核心模块的 API 参考文档，基于源码静态分析生成。

## 文件列表

| 文档 | 覆盖模块 | 核心内容 |
|------|---------|---------|
| [file-init.md](file-init.md) | `__init__.py`, `file.py`, `registry.py`, `utilsextension.pyx` | Blosc2 加载、HDF5 版本检测、`open_file()` 工厂函数、`File` 类、节点注册表、NodeManager |

## 源码版本

- PyTables 版本：3.12.0.dev0
- 源码路径：`tables/`
- 格式版本：OKF v0.2

## 信源可信度

所有 API 名称、类名、方法签名、参数名均直接来自源码静态分析，未参考第三方文档。类标识符（`_c_classid`）、元类注册机制、Cython 扩展层均通过代码验证。
