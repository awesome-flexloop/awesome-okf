---
type: Concept
title: jupyterlite 指令——嵌入 JupyterLab
description: 使用 .. jupyterlite:: 指令在文档中嵌入完整的 JupyterLab 界面，支持打开指定 Notebook 和 Markdown 文件
tags: [directive, jupyterlite, jupyterlab, iframe]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T20:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:00:00+08:00" }
status: stable
stale_after: 2027-02-22
sources:
  - id: main
    resource: /references/main-source.md
    title: 核心模块源码
---

`jupyterlite` 指令用于在 Sphinx 文档中嵌入完整的 JupyterLab（Jupyter 实验室）界面。JupyterLab 是 Jupyter 项目的下一代 Web 交互开发环境，提供文件浏览器、多标签页 Notebook 编辑器、终端、命令面板、插件系统等完整功能。通过该指令，读者无需离开文档页面即可获得完整的 Jupyter 编程体验。

## 类继承关系

`jupyterlite` 指令由 `JupyterLiteDirective` 类实现，其继承链为：

```
SphinxDirective
  └─ _LiteDirective            （Notebook 嵌入基类，处理文件路径解析、文件复制、jupytext 转换）
       └─ BaseJupyterViewDirective  （定义 iframe_cls 和 newtab_cls 的中间类）
            └─ JupyterLiteDirective （jupyterlite 指令实现类）
```

`JupyterLiteDirective` 在基类基础上绑定了两个渲染组件：

- **iframe_cls** = `JupyterLiteIframe`，其 `lite_app` 属性为 `"lab/"`，负责 iframe 嵌入模式下的 HTML 节点渲染
- **newtab_cls** = `JupyterLiteTab`，负责新标签页按钮的 HTML 节点渲染

## 基本用法

### 嵌入空白 JupyterLab

不带参数时，指令嵌入一个空白 JupyterLab 环境，显示启动页（Launcher），读者可以自行创建新的 Notebook、Console 或 Terminal：

```rst
.. jupyterlite::
```

读者看到的是完整的 JupyterLab 界面，可以自由创建文件、编写代码、安装包等。

### 在 JupyterLab 中打开指定 Notebook

指定 Notebook 文件路径作为指令参数时，JupyterLab 加载后会自动打开该文件：

```rst
.. jupyterlite:: my_notebook.ipynb
   :width: 100%
   :height: 800px
   :prompt: 点击启动 JupyterLab
```

支持的文件格式：

- **`.ipynb` 文件**：标准 Jupyter Notebook 文件，直接被复制到 JupyterLite 的 `_contents/` 目录
- **`.md` 文件**：Markdown 格式的 Notebook（Jupytext 配对文件），需要安装可选依赖 `jupytext`（安装方式：`pip install jupyterlite-sphinx[markdown]`）。构建时 jupytext 会将 `.md` 文件转换为 `.ipynb` 格式

指定的 Notebook 文件在 Sphinx 构建过程中会被自动复制到输出目录下的 `_contents/` 文件夹中，JupyterLite 构建流程会将其纳入静态站点。

## URL 路径构造

当指定 Notebook 参数时，iframe 加载的 URL 路径构造规则为：

```
{prefix}/lab/index.html?path={notebook_path}
```

其中：

- `prefix` 是当前 RST 文档相对于 JupyterLite 输出目录（`lite/`）的相对路径
- `lab/index.html` 是 JupyterLab 应用的入口
- `path` 查询参数指定要打开的 Notebook 文件路径

例如，当文档位于 `docs/tutorial/` 目录，指定 Notebook 为 `example.ipynb` 时，最终 URL 类似：

```
../../lite/lab/index.html?path=example.ipynb
```

## 指令选项

`jupyterlite` 指令支持全部通用选项，包括：

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `:width:` | CSS 长度 | `100%` | iframe 宽度 |
| `:height:` | CSS 长度 | `1000px` | iframe 高度（JupyterLab 需要较大高度以显示完整 IDE 布局） |
| `:prompt:` | 字符串 | 无 | 设置后显示懒加载按钮，按钮文本为选项值；点击后才创建 iframe |
| `:prompt_color:` | CSS 颜色 | `#f7dc1e`（黄色） | 懒加载按钮背景色 |
| `:search_params:` | bool/list | `False` | 是否传递当前页面 URL 搜索参数到 iframe |
| `:new_tab:` | bool | `False` | 设为 `True` 时使用新标签页模式，不嵌入 iframe |
| `:new_tab_button_text:` | 字符串 | `"Open as a notebook"` | 新标签页按钮文本 |
| `:theme:` | 字符串 | JupyterLite 默认 | 指定 JupyterLab 主题 |

## 新标签页模式

设置 `:new_tab: True` 后，指令渲染为一个按钮而非 iframe。读者点击按钮，JupyterLab 会在浏览器新标签页中打开完整界面，不受 iframe 尺寸限制：

```rst
.. jupyterlite:: my_notebook.ipynb
   :new_tab: True
   :new_tab_button_text: 在 JupyterLab 中打开完整 Notebook
```

新标签页按钮的默认文本为 `"Open as a notebook"`，可以通过 `:new_tab_button_text:` 指令选项覆盖，也可以通过 `conf.py` 中的 `jupyterlite_new_tab_button_text` 全局配置统一设置。

## 懒加载模式（推荐）

当文档页面中包含多个 JupyterLite 嵌入实例时，强烈建议使用 `:prompt:` 选项启用懒加载：

```rst
.. jupyterlite:: analysis.ipynb
   :prompt: 启动交互式分析环境
   :prompt_color: #4CAF50
```

启用懒加载后，页面初始加载时不会创建 iframe，而是显示一个可点击的按钮。读者点击按钮后，前端 JavaScript 才会动态创建 iframe 并加载 JupyterLab。这避免了同时启动多个 JupyterLite 实例导致的内存占用过高和页面加载缓慢问题。

## 使用场景

`jupyterlite` 指令适合以下场景：

- **教学教程**：让读者在阅读教程的同时直接在 JupyterLab 中跟着操作
- **数据探索**：嵌入数据集和 Notebook，读者可以自由修改参数、探索数据
- **完整编程环境**：需要文件浏览器、多文件编辑、终端等完整 IDE 功能
- **Notebook 集合**：不指定参数时，读者可以在 JupyterLab 文件浏览器中访问所有提供的 Notebook 文件

如果只需要展示单个 Notebook 且不需要完整 IDE 功能，可以考虑使用界面更简洁的 [notebooklite 指令](/concepts/05-notebooklite-directive.md)；如果只需要短小的交互式代码片段，[replite 指令](/concepts/06-replite-directive.md) 更轻量。

## 相关概念

- [指令系统总览](/concepts/03-directive-overview.md)
- [notebooklite 指令——嵌入经典 Notebook](/concepts/05-notebooklite-directive.md)
- [replite 指令——嵌入交互式 REPL](/concepts/06-replite-directive.md)
- [voici 指令——嵌入 Voici 仪表板](/concepts/07-voici-directive.md)
- [配置参考](/concepts/09-configuration.md)
- [核心模块源码](/references/main-source.md)
