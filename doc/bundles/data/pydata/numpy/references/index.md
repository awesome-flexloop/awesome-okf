# 信源登记簿

本目录包含 NumPy 源码中关键模块的源码摘录与分析，所有概念文档的 `sources` 字段指向本目录。

| 信源 | 对应源码文件 | 说明 |
|------|-------------|------|
| [核心初始化](core-init.md) | `numpy/_core/__init__.py` | C扩展加载、OPENBLAS线程修复、multiarray/umath合并导入、Array API版本 |
| [ndarray与数组创建API源码](ndarray-source.md) | `_core/multiarray.py`、`_core/numeric.py`、`_core/fromnumeric.py` | ndarray类定义、数组创建函数签名、规约包装机制 |
| [ufunc通用函数系统源码](ufunc-source.md) | `_core/umath.py` | ufunc列表、ufunc属性（nin/nout/nargs/identity）、frompyfunc工厂、errstate错误控制 |
| [dtype与数值类型系统源码](dtype-source.md) | `_core/_dtype.py`、`_core/numerictypes.py` | kind字符映射、类型层次树、genericTypeRank、标志位常量、结构化dtype字符串表示 |

```{toctree}
:hidden:

core-init
dtype-source
ndarray-source
ufunc-source
```
