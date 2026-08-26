# References — 源码参考

References 是概念文档和示例文档的信源文件，提供源码级索引和速查表。所有 Concepts 和 Examples 文档的 sources 字段均引用这些文件。

## 源码索引

| 信源 | 内容 |
|------|------|
| [main-source](main-source.md) | 核心模块 jupyterlite_sphinx.py 源码索引：节点类、指令类、工具函数、事件处理、setup 函数 |
| [try-examples-source](try-examples-source.md) | _try_examples.py 模块源码索引：doctest 解析、examples_to_notebook 转换管线、autodoc 注入逻辑 |
| [js-source](js-source.md) | jupyterlite_sphinx.js 前端源码索引：全局函数、懒加载机制、移动端检测、ConfigLoader |

## 配置速查

| 信源 | 内容 |
|------|------|
| [config-reference](config-reference.md) | 所有 conf.py 配置项速查表：默认值、类型、功能说明、源码行号引用 |

```{toctree}
:hidden:
:maxdepth: 7

config-reference
js-source
main-source
try-examples-source
```
