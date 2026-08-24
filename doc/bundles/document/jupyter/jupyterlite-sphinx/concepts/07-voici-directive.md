---
type: Concept
title: voici 指令——嵌入 Voici 仪表板
description: "使用 .. voici:: 指令嵌入 Voici 仪表板（基于 Voilà 的静态仪表板渲染），需要安装 voici 包"
tags: [directive, voici, dashboard, voila]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T20:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:00:00+08:00" }
status: stable
stale_after: 2027-02-22
sources:
  - id: main
    resource: /references/main-source.md
    title: 核心模块源码
---

`voici` 指令用于在 Sphinx 文档中嵌入 Voici 仪表板（dashboard）。Voici 是基于 JupyterLite 和 Voilà 技术的静态仪表板渲染工具，可以将 Jupyter Notebook 转换为只包含 Markdown 文本、交互式 widgets（控件）和输出结果的仪表板页面，隐藏代码单元格，为读者提供专注于数据和可视化的应用体验。

## 前置依赖

使用 `voici` 指令需要额外安装 `voici` 包。与 `jupytext` 不同，`voici` 不是 `jupyterlite-sphinx` 的可选依赖项（extras），需要独立安装：

```bash
pip install voici
```

在源码中，`voici` 的导入采用 try-except 模式：

```python
try:
    import voici as _voici
    voici = _voici
except ImportError:
    voici = None
```

如果 `voici` 未安装（`voici is None`），`VoiciDirective.run()` 方法会抛出 `RuntimeError`，提示用户执行 `pip install voici`。因此，使用 `voici` 指令前必须确保 voici 包已正确安装在构建环境中。

构建时，`jupyter lite build` 命令会自动检测 voici 包是否存在，如果存在则将 voici 应用纳入构建的 apps 列表。

## 类继承关系

`voici` 指令由 `VoiciDirective` 类实现，其继承链为：

```
SphinxDirective
  └─ _LiteDirective
       └─ BaseJupyterViewDirective
            └─ VoiciDirective （voici 指令实现类）
```

尽管继承了 `BaseJupyterViewDirective`，但 voici 的 iframe 和 tab 类有独特的实现：

- **iframe_cls** = `VoiciIframe`，继承自 `_PromptedIframe`（注意：**不是** `_LiteIframe`），使用 `VoiciBase` 类的路径逻辑构造 URL
- **newtab_cls** = `VoiciTab`，**不继承** `BaseNotebookTab`，有独立的 URL 构造实现

## VoiciBase 路径逻辑

`VoiciBase` 是一个独立的辅助类（第 348-360 行），定义了 voici 应用的路径构造规则：

- `lite_app` 属性为 `"voici/"`
- `get_full_path()` 方法根据是否指定 notebook 返回不同路径：
  - **指定 notebook 时**：返回 `voici/render/{notebook_name}.html`
  - **未指定 notebook 时**：返回 `voici/tree`

这与其他指令有显著区别：其他指令直接在 URL 中使用查询参数（如 `?path=xxx`），而 Voici 为每个 Notebook 预渲染独立的 HTML 文件，URL 路径直接指向渲染后的页面。

## 基本用法

### 嵌入指定 Notebook 的仪表板

```rst
.. voici:: my_dashboard.ipynb
   :width: 100%
   :height: 800px
   :prompt: 查看交互式仪表板
```

当指定 notebook 参数时：

1. Notebook 文件被复制到 `_contents/` 目录（与其他指令一致）
2. JupyterLite 构建时，voici 会为该 Notebook 生成渲染后的 HTML 页面：`voici/render/my_dashboard.html`
3. iframe 加载的 URL 为 `{prefix}/voici/render/my_dashboard.html`

渲染后的仪表板页面会隐藏代码单元格，只显示 Markdown 内容、代码输出和 ipywidgets 等交互控件。读者可以通过滑动条、下拉框、按钮等 widgets 与数据进行交互，但无法直接编辑代码。

### 嵌入 Voici 文件浏览器

不指定 notebook 参数时，显示 Voici 的文件浏览器视图（tree view），读者可以从列表中选择要查看的仪表板：

```rst
.. voici::
   :width: 100%
   :height: 600px
```

此时 iframe 加载的 URL 为 `{prefix}/voici/tree`。

### 新标签页模式

```rst
.. voici:: my_dashboard.ipynb
   :new_tab: True
   :new_tab_button_text: 在新标签页打开仪表板
```

`VoiciTab` 独立构造新标签页 URL，不依赖 `BaseNotebookTab` 的逻辑，确保路径格式与 Voici 的渲染页面路径一致。

## 指令选项

`voici` 支持与其他指令相同的通用选项：

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `:width:` | CSS 长度 | `100%` | iframe 宽度 |
| `:height:` | CSS 长度 | `1000px` | iframe 高度 |
| `:prompt:` | 字符串 | 无 | 懒加载按钮文本 |
| `:prompt_color:` | CSS 颜色 | `#f7dc1e` | 懒加载按钮背景色 |
| `:search_params:` | bool/list | `False` | 传递页面 URL 搜索参数 |
| `:new_tab:` | bool | `False` | 新标签页模式 |
| `:new_tab_button_text:` | 字符串 | `"Open with Voici"` | 新标签页按钮文本 |
| `:theme:` | 字符串 | 默认主题 | 仪表板主题 |

新标签页按钮的全局配置项为 `voici_new_tab_button_text`，默认值为 `"Open with Voici"`。

## VoiciIframe 的特殊实现

`VoiciIframe` 继承自 `_PromptedIframe` 而非 `_LiteIframe`，这意味着它不使用 `_LiteIframe` 中的通用路径拼接逻辑，而是通过 `VoiciBase.get_full_path()` 方法独立构造 URL。这样做的原因是 Voici 的 URL 结构与其他应用不同：

- 其他应用：`{prefix}/{lite_app}/index.html?path={notebook}`
- Voici：`{prefix}/voici/render/{notebook}.html`（指定 notebook）或 `{prefix}/voici/tree`（未指定）

这种静态 HTML 预渲染方式也是 Voici 仪表板加载速度较快的原因之一——页面是预先生成的，不需要在浏览器端实时转换 Notebook。

## 使用场景

Voici 仪表板适合以下场景：

- **数据可视化应用**：将带有 ipywidgets 交互控件的 Notebook 转为仪表板，读者通过滑块、下拉框等控件实时调整参数查看可视化结果
- **教学演示**：隐藏代码实现细节，让读者专注于概念理解和参数交互
- **数据报告**：将数据分析 Notebook 转为可交互的报告页面，非技术用户也能操作
- **模型演示**：嵌入机器学习模型的交互式演示，读者可以调整输入参数观察预测结果

注意事项：

- Voici 渲染依赖 ipywidgets 等控件库在 JupyterLite 环境中的支持，确保 Notebook 中使用的 widgets 已正确安装
- 仪表板模式下代码单元格被隐藏，不适合需要读者阅读和修改代码的场景——这种场景应使用 [jupyterlite 指令](/concepts/04-jupyterlite-directive.md) 或 [notebooklite 指令](/concepts/05-notebooklite-directive.md)
- 必须安装 voici 包才能使用，否则构建时会报错

## 相关概念

- [指令系统总览](/concepts/03-directive-overview.md)
- [jupyterlite 指令——嵌入 JupyterLab](/concepts/04-jupyterlite-directive.md)
- [notebooklite 指令——嵌入经典 Notebook](/concepts/05-notebooklite-directive.md)
- [配置参考](/concepts/09-configuration.md)
- [核心模块源码](/references/main-source.md)
