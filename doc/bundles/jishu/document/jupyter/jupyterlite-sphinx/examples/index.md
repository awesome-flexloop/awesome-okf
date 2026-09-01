# Examples — 示例文档

Examples 提供可直接复制使用的完整代码示例，每个示例包含 conf.py 配置和 RST 指令代码，可直接在项目中运行。

## 基础示例

| 示例 | 内容 |
|------|------|
| [basic-embed](basic-embed.md) | 最简嵌入：空白 JupyterLab 环境，带点击加载按钮 |
| [notebook-embed](notebook-embed.md) | 嵌入 .ipynb 和 .md Notebook 文件，新标签页打开，标记单元格去除 |

## 进阶示例

| 示例 | 内容 |
|------|------|
| [repl-embed](repl-embed.md) | 嵌入带预填代码的 REPL，内核选择，自动执行控制 |
| [try-examples-basic](try-examples-basic.md) | 手动使用 try_examples 指令为 doctest 代码添加交互按钮 |

## 集成示例

| 示例 | 内容 |
|------|------|
| [autodoc-integration](autodoc-integration.md) | 与 sphinx.ext.autodoc 集成，全局自动为 Examples 段添加交互按钮，运行时配置 |

```{toctree}
:hidden:
:maxdepth: 7

autodoc-integration
basic-embed
notebook-embed
repl-embed
try-examples-basic
```
