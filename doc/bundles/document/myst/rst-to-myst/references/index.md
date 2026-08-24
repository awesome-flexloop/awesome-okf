# 信源参考

本目录包含源码信源登记文档，为概念文档和示例文档提供可验证的源码引用。

| 文档 | 对应源码文件 | 说明 |
|------|-------------|------|
| [CLI 命令行接口](source-cli.md) | `rst_to_myst/cli.py` | click子命令和CLI选项 |
| [RST 解析器模块](source-parser.md) | `rst_to_myst/parser.py` | LosslessRSTParser、自定义Transforms |
| [MarkdownIt 渲染器](source-markdownit.md) | `rst_to_myst/markdownit.py` | docutils NodeVisitor、token生成 |
| [mdformat 渲染集成](source-mdformat-render.md) | `rst_to_myst/mdformat_render.py` | MDRenderer使用、自定义渲染器 |
| [命名空间 Mock 系统](source-namespace.md) | `rst_to_myst/namespace.py` | ApplicationNamespace、Sphinx扩展加载 |

```{toctree}
:hidden:

source-cli
source-markdownit
source-mdformat-render
source-namespace
source-parser
```
