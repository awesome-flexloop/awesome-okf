---
type: Concept
title: Sphinx 集成机制
description: sphinx_setup 注册流程、Parser 继承链、Post-Transforms、CSS/JS 资源加载、NbMetadataCollector
tags: [myst-nb, sphinx, integration, setup, post-transform]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:30:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: mystnb-source
    resource: /references/mystnb-source.md
    title: MyST-NB 源码路径映射
---

## Sphinx 集成机制

MyST-NB 通过 `sphinx_setup()` 函数注册为 Sphinx 扩展，在 MyST-Parser 基础上叠加 Notebook 处理能力。

## setup 注册流程

`sphinx_ext.py` 中的 `sphinx_setup(app)` 按以下顺序注册：

1. **初始化 MyST-Parser**：调用 `setup_myst_parser(app)`，注册 MyST 的配置和 transforms（但不注册 parser）
2. **注册配置值**：遍历 `NbParserConfig` 字段，通过 `app.add_config_value("nb_<name>", default, "env")` 注册所有 `nb_*` 配置
3. **注册遗留配置名**：为有 `legacy_name` 的字段注册旧版配置名，并发出弃用警告
4. **连接事件**：
   - `builder-inited` → `create_mystnb_config()`：验证配置、创建 NbParserConfig 实例存入 `app.env.mystnb_config`
   - `config-inited` → `add_nb_custom_formats()`：注册自定义文件后缀
   - `config-inited` → `add_exclude_patterns()`：排除 `.ipynb_checkpoints`
   - `build-finished` → `add_global_html_resources()`：复制 CSS 文件
   - `html-page-context` → `add_per_page_html_resources()`：按页添加 JS 文件
5. **注册源解析器**：`app.add_source_parser(Parser)`，添加 `.md`（override）和 `.ipynb` 为 `myst-nb`
6. **注册环境收集器**：`app.add_env_collector(NbMetadataCollector)`
7. **注册指令/角色**：
   - `code-cell`、`raw-cell` → UnexpectedCellDirective（警告指令，正常情况下不应触发）
   - `{nb-download}` → NbDownloadRole
   - Glue 扩展：`{glue}` 指令/角色、NbGlueDomain
   - Eval 扩展：eval 指令/角色
8. **注册 Post-Transforms**：SelectMimeType、ReplacePendingGlueReferences、HideInputCells
9. **注册节点**：HideCodeCellNode（可折叠代码块节点）
10. **注册 CSS**：带 content hash 的 `mystnb.<hash>.css`
11. **加载统计表扩展**：setup_exec_table_extension(app)

## Parser 继承链

```
myst_parser.parsers.sphinx_.MystParser
    └── myst_nb.sphinx_.Parser
          ├── supported = ("myst-nb",)
          ├── 重写 parse() 方法：读取→执行→转Token→渲染
          └── 使用 SphinxRenderer（混入 MditRenderMixin）
```

## 关键 Post-Transforms

### SelectMimeType

在所有文档解析完成后，遍历文档树中的 MIME bundle 节点，根据当前 builder 的 MIME 优先级列表选择最终渲染的 MIME 类型。这保证了不同 builder（html/latex/text）选择各自最优的输出格式。

### ReplacePendingGlueReferences

将 glue 引用的 pending 节点替换为实际渲染的内容。由于 glue 数据可能来自其他文档（跨页面引用），这个替换必须在所有文档读取完成后进行。

### HideInputCells

处理 `hide-input`/`hide-output` 标签，将代码块包装为可折叠的 `HideCodeCellNode` 节点。

## NbMetadataCollector

`NbMetadataCollector` 是 Sphinx EnvironmentCollector，在文档解析过程中收集每页需要的元数据：
- 每页需要的 JS 文件（如 ipywidgets 的 RequireJS 和 Widget Manager）
- 其他 notebook 级元数据

这些数据在 `html-page-context` 事件中用于按页添加 JS 资源。

## CSS 资源

默认 CSS 文件 `mystnb.css` 提供：
- 代码 cell 样式
- 输出区域样式
- stderr 样式（红色边框）
- 可折叠代码块样式
- 输出滚动样式
- ANSI 颜色样式

CSS 文件名包含 content hash（如 `mystnb.abc123.css`），确保缓存更新正确。

## JS 资源（ipywidgets）

当页面包含 ipywidgets 输出时，自动添加：
1. RequireJS（CDN）
2. Jupyter Widgets HTML Manager（CDN）

JS 文件在 `html-page-context` 事件中按页添加，避免无 widget 页面不必要的加载。

## 输出路径

- **执行输出文件夹**：`<outdir>/../jupyter_execute/`（Sphinx 自动设置）
- **缓存路径**：`<outdir>/../.jupyter_cache/`（默认）
- 图片等外部输出文件保存在执行输出文件夹中

## 并行构建

MyST-NB 声明 `parallel_read_safe=True` 和 `parallel_write_safe=True`，支持 Sphinx 并行构建。但注意：
- Notebook 执行本身可能不是并行安全的（取决于 kernel）
- jupyter-cache 提供并发安全

## 双模式初始化

关键设计：`setup(app)` 函数中延迟导入 `sphinx_setup`：

```python
def setup(app):
    from .sphinx_ext import sphinx_setup
    return sphinx_setup(app)
```

同样，`glue()` 函数延迟导入 IPython：

```python
def glue(name, variable, display=True):
    from myst_nb.ext.glue import glue
    return glue(name, variable, display)
```

这种延迟导入确保在 Docutils 独立模式下不导入 Sphinx/IPython。

## 相关概念

- [Docutils 独立使用](11-docutils-standalone.md)
- [配置系统](04-config-system.md)
- [四阶段处理管线](03-processing-pipeline.md)
- [代码隐藏与输出控制](09-hiding-code.md)
- [基础配置示例](/examples/01-basic-setup.md)
