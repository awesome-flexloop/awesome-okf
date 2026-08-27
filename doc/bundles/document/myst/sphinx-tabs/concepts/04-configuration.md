---
type: Concept
title: 配置项参考
description: sphinx-tabs 的全部配置项详解：builder 兼容性、CSS加载控制、标签关闭行为、条件资源加载机制
tags: [sphinx, tabs, configuration, builder, assets, css]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:30:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: tabs-source
    resource: /references/tabs-source.md
    title: sphinx-tabs 源码路径映射
---

# 配置项参考

sphinx-tabs 在 `conf.py` 中提供以下配置项。

## sphinx_tabs_valid_builders

**类型**：`list[str]`  
**默认值**：`[]`

添加自定义兼容 builder 名称。默认兼容 builder 列表包括：`html`、`singlehtml`、`dirhtml`、`readthedocs`、`readthedocsdirhtml`、`readthedocssinglehtml`、`readthedocssinglehtmllocalmedia`、`spelling`。

```python
# 为自定义 builder 添加标签页支持
sphinx_tabs_valid_builders = ['my_custom_builder']
```

对于不在兼容列表中的 builder，标签页会降级为普通顺序输出（不使用 ARIA 标签组件，而是简单的 container 嵌套）。

## sphinx_tabs_disable_css_loading

**类型**：`bool`  
**默认值**：`False`

禁用自动加载 `tabs.css`。当使用自定义主题（如 sphinx-book-theme、pydata-sphinx-theme）已内置 tabs 样式时，设为 `True` 避免样式冲突或重复加载。

```python
sphinx_tabs_disable_css_loading = True
```

## sphinx_tabs_disable_tab_closing

**类型**：`bool`  
**默认值**：`False`

禁用"点击已选中标签取消选中"的行为。

- `False`（默认）：点击当前选中的标签会取消选中（关闭标签内容），tablist 添加 `closeable` CSS 类
- `True`：标签一旦选中就不能通过点击取消（只能切换到其他标签），始终有一个标签处于选中状态

```python
sphinx_tabs_disable_tab_closing = True
```

## 条件资源加载机制

sphinx-tabs 实现了**按需加载**策略：

1. `html-page-context` 事件触发 `update_context()`
2. 使用 `_FindTabsDirectiveVisitor` 遍历 doctree，检测是否存在 `sphinx-tabs` CSS 类
3. 仅当页面包含标签页（或全局策略 `html_assets_policy == "always"`）时才添加 CSS/JS

### 实现细节

```python
class _FindTabsDirectiveVisitor(nodes.NodeVisitor):
    def unknown_visit(self, node):
        if (not self._found
            and isinstance(node, nodes.container)
            and "classes" in node
            and isinstance(node["classes"], list)):
            self._found = "sphinx-tabs" in node["classes"]
```

这种机制的好处：
- 不使用标签页的页面不加载 tabs.css/tabs.js，减少网络请求
- 静态资源只在需要时加载，不影响其他页面性能

### 强制全局加载

如果需要在所有页面加载资源（例如某些主题依赖 tabs JS），可以在 Sphinx 中设置：

```python
# Sphinx 5+ 全局资源策略
html_assets_policy = "always"
```

## 静态路径注册

静态资源路径通过 `builder-inited` 事件插入到 `html_static_path` 的**最前面**（`insert(0, ...)`），确保优先级高于其他静态路径：

```python
app.connect(
    "builder-inited",
    (lambda app: app.config.html_static_path.insert(0, static_dir.as_posix())),
)
```

## 相关概念

- [四个指令详解](02-directives.md)
- [无障碍设计](05-accessibility.md)
- [分组同步配置示例](../examples/group-tabs-sync.md)
