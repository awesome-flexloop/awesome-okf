# 信源参考

本目录包含源码信源登记文档，为概念文档和示例文档提供可验证的源码引用。

| 文档 | 对应源码文件 | 说明 |
|------|-------------|------|
| [插件入口模块](source-init.md) | `mdformat_footnote/__init__.py` | 版本号、插件名和导出 |
| [插件核心实现](source-plugin.md) | `mdformat_footnote/plugin.py` | update_mdit、RENDERERS、CLI参数 |
| [脚注重排序逻辑](source-reorder.md) | `mdformat_footnote/_reorder.py` | 分类、依赖图、排序、ID重分配 |

```{toctree}
:maxdepth: 7

source-init
source-plugin
source-reorder
```
