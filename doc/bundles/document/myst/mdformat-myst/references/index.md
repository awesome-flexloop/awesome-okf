# 信源参考

本目录包含源码信源登记文档，为概念文档和示例文档提供可验证的源码引用。

| 文档 | 对应源码文件 | 说明 |
|------|-------------|------|
| [插件入口模块](source-init.md) | `mdformat_myst/__init__.py` | 版本号和包入口 |
| [插件核心实现](source-plugin.md) | `mdformat_myst/plugin.py` | update_mdit、RENDERERS、POSTPROCESSORS |
| [指令格式化模块](source-directives.md) | `mdformat_myst/_directives.py` | fence渲染、YAML格式化、选项解析 |

```{toctree}
:hidden:

source-directives
source-init
source-plugin
```
