---
type: Concept
title: notebooklite 指令——嵌入经典 Notebook
description: "使用 .. notebooklite:: 指令嵌入经典 Jupyter Notebook 界面（tree视图），retrolite 为其别名"
tags: [directive, notebooklite, classic-notebook, retrolite]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T20:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:00:00+08:00" }
status: stable
stale_after: 2027-02-22
sources:
  - id: main
    resource: /references/main-source.md
    title: 核心模块源码
---

`notebooklite` 指令用于在 Sphinx 文档中嵌入经典 Jupyter Notebook 界面。经典 Notebook 界面是 JupyterLab 出现之前广泛使用的单文档交互界面，相比 JupyterLab 更加简洁轻量，专注于单个 Notebook 的阅读和执行，适合不需要完整 IDE 功能的场景。`retrolite` 是该指令的别名，两者完全等效。

## 类继承关系

`notebooklite` 指令由 `NotebookLiteDirective` 类实现，其继承链为：

```
SphinxDirective
  └─ _LiteDirective
       └─ BaseJupyterViewDirective
            └─ NotebookLiteDirective （notebooklite/retrolite 指令实现类）
```

`NotebookLiteDirective` 绑定的渲染组件：

- **iframe_cls** = `NotebookLiteIframe`，其 `lite_app` 属性为 `"tree/"`，`notebooks_path` 属性为 `"../notebooks/"`
- **newtab_cls** = `NotebookLiteTab`，继承自 `BaseNotebookTab`，负责新标签页按钮渲染

## 别名 retrolite

在 `setup()` 函数中，`retrolite` 被注册为 `notebooklite` 的别名：

```python
app.add_directive("retrolite", NotebookLiteDirective)
```

这意味着以下两种写法完全等价：

```rst
.. notebooklite:: my_notebook.ipynb

.. retrolite:: my_notebook.ipynb
```

`retrolite` 名称来源于 JupyterLite 早期的 RetroLab 项目（后合并为 Jupyter Notebook v7），保留别名是为了向后兼容。新项目建议使用 `notebooklite` 名称。

## 基本用法

### 嵌入 Notebook 文件浏览器

不带参数时，指令嵌入经典 Notebook 的文件浏览器视图（tree view），读者可以浏览 `_contents/` 目录下的所有 Notebook 文件并选择打开：

```rst
.. notebooklite::
   :width: 100%
   :height: 600px
```

### 直接打开指定 Notebook

指定 Notebook 文件路径时，直接在经典 Notebook 界面中打开该文件：

```rst
.. notebooklite:: tutorial.ipynb
   :width: 100%
   :height: 800px
   :prompt: 启动 Notebook
```

与 `jupyterlite` 指令相同，支持 `.ipynb` 和 `.md`（需 jupytext）两种文件格式，文件在构建时被复制到 `_contents/` 目录。

## URL 路径构造

`notebooklite` 的 URL 路径与 `jupyterlite` 有所不同。不指定 Notebook 参数时，URL 为：

```
{prefix}/tree/
```

指定 Notebook 参数时，由于 Notebook 文件存放在 `_contents/notebooks/` 下（相对于 tree 视图的路径），URL 构造为：

```
{prefix}/tree/../notebooks/{notebook_path}
```

这里 `../notebooks/` 就是 `NotebookLiteIframe.notebooks_path` 属性的值，用于从 tree 应用路径导航到 notebooks 目录。例如：

```
../../lite/tree/../notebooks/tutorial.ipynb
```

浏览器会自动解析 `../` 路径段，实际加载的是 `../../lite/notebooks/tutorial.ipynb`。

## NotebookLiteParser：自动将 .ipynb 作为文档源

`notebooklite` 指令体系还包含一个特殊的解析器类 `NotebookLiteParser`，它继承自 Sphinx 的 `RSTParser`。当 `jupyterlite_bind_ipynb_suffix` 配置为 `True`（默认值）时，Sphinx 会将 `.ipynb` 文件后缀绑定到该解析器。

`NotebookLiteParser` 的作用是将直接放置在 Sphinx 源目录中的 `.ipynb` 文件自动解析为包含 `notebooklite` 指令的文档。具体来说，当一个 `.ipynb` 文件被作为 Sphinx 文档源处理时，解析器会自动在生成的 RST 内容中插入 `.. notebooklite::` 指令，将该 Notebook 嵌入到生成的 HTML 页面中。

这意味着你可以直接将 `.ipynb` 文件放入 Sphinx 文档目录，无需手动编写 RST 文件即可在文档站点中展示可运行的 Notebook。

## 指令选项

`notebooklite` 支持与 `jupyterlite` 相同的通用选项：

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `:width:` | CSS 长度 | `100%` | iframe 宽度 |
| `:height:` | CSS 长度 | `1000px` | iframe 高度 |
| `:prompt:` | 字符串 | 无 | 懒加载按钮文本 |
| `:prompt_color:` | CSS 颜色 | `#f7dc1e` | 懒加载按钮背景色 |
| `:search_params:` | bool/list | `False` | 传递页面 URL 搜索参数 |
| `:new_tab:` | bool | `False` | 新标签页模式 |
| `:new_tab_button_text:` | 字符串 | `"Open as a notebook"` | 新标签页按钮文本 |
| `:theme:` | 字符串 | 默认主题 | Notebook 主题 |

新标签页按钮的全局配置项为 `notebooklite_new_tab_button_text`，默认值同样为 `"Open as a notebook"`。

## 与 jupyterlite 的对比

`notebooklite` 和 `jupyterlite` 都可以嵌入 Notebook，但它们面向不同的使用场景：

| 特性 | notebooklite | jupyterlite |
|------|-------------|-------------|
| 界面 | 经典 Notebook 单文档界面 | JupyterLab 完整 IDE |
| 文件浏览器 | tree 视图，仅展示 Notebook 文件 | 完整文件浏览器，支持新建/删除/重命名 |
| 多文件编辑 | 一次只聚焦一个 Notebook | 支持多标签页同时编辑多个文件 |
| 额外功能 | 无终端、无命令面板 | 包含终端、命令面板、插件系统 |
| 加载速度 | 相对较轻量 | 功能完整，加载稍慢 |
| 适用场景 | 展示单个 Notebook 供阅读和运行 | 需要完整交互编程环境 |

选择建议：

- 仅需让读者运行和阅读单个 Notebook → 使用 `notebooklite`
- 需要读者进行自由探索、创建新文件、使用终端 → 使用 `jupyterlite`
- 嵌入短小代码片段即时运行 → 使用 [replite 指令](/concepts/06-replite-directive.md)

## 相关概念

- [指令系统总览](/concepts/03-directive-overview.md)
- [jupyterlite 指令——嵌入 JupyterLab](/concepts/04-jupyterlite-directive.md)
- [replite 指令——嵌入交互式 REPL](/concepts/06-replite-directive.md)
- [配置参考](/concepts/09-configuration.md)
- [核心模块源码](/references/main-source.md)
