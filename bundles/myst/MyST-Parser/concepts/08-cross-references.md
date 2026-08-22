---
type: Concept
title: 交叉引用
description: MyST 的 Markdown 风格交叉引用、MystReferenceResolver 解析流程、intersphinx 集成
tags: [myst, sphinx, cross-reference, intersphinx, pending-xref, myst-parser]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:00:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: myst-parser-source
    resource: /references/myst-parser-source.md
    title: MyST-Parser 源码路径映射
---

## 交叉引用

MyST-Parser 实现了 Markdown 风格的交叉引用语法，通过 `MystReferenceResolver` Post-Transform 统一解析，支持文档内引用、文档间引用、域对象引用和 intersphinx 外部引用。

## Markdown 风格引用语法

### 文档间引用

```markdown
[链接文本](other-doc.md)
[链接文本](./path/to/doc.md)
[链接文本](../parent/doc.md#anchor)
```

### 文档内锚点引用

```markdown
[链接文本](#my-section)
[链接文本](#my-label)
```

### 隐式引用（无扩展名）

```markdown
[链接文本](reference-target)
```

此类引用会尝试通过 Sphinx 域系统解析（类似 RST 的 `:any:` 角色）。

### 显式标签定义

```markdown
(my-label)=
## 我的章节

可以通过 [点击这里](#my-label) 跳转。
```

### 自动标题锚点

启用 `myst_heading_anchors = 3`（深度为 3 级标题），标题自动生成 GitHub 风格的 slug 锚点：

```markdown
## 我的标题 → #我的标题
```

## MystReferenceResolver 工作机制

`MystReferenceResolver` 继承 Sphinx 的 `ReferencesResolver`，优先级为 9（高于默认 10），专门处理 `reftype == "myst"` 的 `pending_xref` 节点。

### 解析优先级链

对于每个 ``[text](target)`` 生成的 `pending_xref` 节点：

1. **doc 域引用**（`refdomain == "doc"`）：
   - 调用 `resolve_myst_ref_doc()` 解析
   - 支持 `doc.md#anchor` 格式（文档 + 锚点）
   - 从 `env.metadata[docname].get("myst_slugs", {})` 查找锚点
   - 也检查 std domain labels
   - 通过 `make_refnode()` 生成引用节点

2. **本地域解析**（`resolve_myst_ref_any()`）：
   - 尝试 `std:ref`（标签引用）
   - 尝试 `std:doc`（文档引用）
   - 遍历 std domain 的所有 object types
   - 遍历所有已注册 domain 的 `resolve_any_xref()`
   - 多结果时发出 `XREF_AMBIGUOUS` 警告

3. **Intersphinx 解析**（`_resolve_myst_ref_intersphinx()`）：
   - 使用 `inventory.filter_sphinx_inventories()` 在 intersphinx inventory 中查找
   - 多结果时发出 `IREF_AMBIGUOUS` 警告
   - 生成外部链接节点

4. **本地锚点回退**：
   - 如果存在 `reflocalid`，创建内部引用指向该锚点

5. **最终降级**：
   - 全部失败 → 发出 `XREF_MISSING` 警告
   - 将引用降级为外部链接（`normalizeLink(target)`）

### 嵌套语法支持

与 RST 的 `:any:` 角色不同，MyST 的引用支持 Markdown 嵌套语法：

```markdown
`[**粗体**和*斜体*](target)`
```

这通过 `_resolve_ref_nested()` 和 `_resolve_doc_nested()` 方法实现，它们保留子节点的内联格式而不是转换为纯文本。

## 引用域控制

通过 `myst_ref_domains` 配置限制引用搜索的域：

```python
# 仅在 std 和 py 域中搜索引用
myst_ref_domains = ["std", "py"]
```

默认值 `None` 表示搜索所有域。

## Intersphinx 集成

MyST 的 Markdown 链接自动支持 intersphinx 外部引用。配置 intersphinx 后：

```python
extensions = ["myst_parser", "sphinx.ext.intersphinx"]
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master", None),
}
```

可以直接在 Markdown 链接中引用外部项目的对象（通过隐式引用）：

```markdown
参见 `dict` 和 `sphinx.application.Sphinx`。
```

## nitpick 模式兼容

MyST 引用支持 Sphinx 的 nitpick 模式和警告抑制：

```python
nitpicky = True
nitpick_ignore = [
    ("myst", "some-target"),  # 忽略特定未解析引用
]
nitpick_ignore_regex = [
    ("myst", r"temp-.*"),      # 正则忽略
]
```

未解析的引用默认会警告，但不会中断构建。

## URL Scheme 识别

`myst_url_schemes` 配置控制哪些链接被识别为外部 URL：

```python
# 默认
myst_url_schemes = {
    "http": None,
    "https": None,
    "mailto": None,
    "ftp": None,
}

# 自定义 scheme（可带 URL 模板和样式）
myst_url_schemes = {
    "http": None,
    "https": None,
    "mailto": None,
    "jupyter": {
        "url": "https://jupyter.org/search?q={path}",
        "title": "Jupyter: {path}",
        "classes": ["jupyter-link"],
    },
}
```

自定义 scheme 支持 URL 模板，使用 `{uri}`、`{scheme}`、`{netloc}`、`{path}`、`{params}`、`{query}`、`{fragment}` 占位符。

## 相关概念

- [MyST 语法概览](/concepts/02-myst-syntax-overview.md)
- [解析器与渲染器](/concepts/06-parser-and-renderer.md)
- [配置系统](/concepts/04-config-system.md)
- [Sphinx 集成机制](/concepts/11-sphinx-integration.md)
- [交叉引用实战](/examples/04-cross-references.md)
