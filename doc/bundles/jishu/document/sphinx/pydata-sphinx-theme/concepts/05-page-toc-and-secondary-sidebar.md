---
type: Concept
title: 页内目录与次级侧栏
description: 右侧 TOC 的生成、按页配置、滚动高亮以及编辑/源码链接
tags: [sphinx, theme, pydata, toc, sidebar, edit-page]
generated: { by: "reference_agent/deepseek-flash", at: "2026-11-24T03:05:00Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: pst-source-map
    resource: /references/source-map.md
    title: 源码路径映射
---

# 页内目录与次级侧栏

右侧栏（secondary sidebar）不是"第二个导航"，而是**当前页面的工具区**：页内目录、编辑此页、查看源码，以及你放进去的任何模板。

## 1. 默认组成

`theme.conf` 默认：

```ini
secondary_sidebar_items = page-toc, edit-this-page, sourcelink
```

对应 `components/` 下三个模板。它们由 `utils.set_secondary_sidebar_items` 解析后写入 `context["secondary_sidebar_items"]`，再由 `sections/sidebar-secondary.html` 逐个 include。

## 2. 页内 TOC 的生成

`toctree.generate_toc_html` 读取 Sphinx 已生成的 `context["toc"]`，做四件事：

1. 为每个 `<li>` 加 `nav-item toc-entry`，为 `<a>` 加 `nav-link`。
2. 为不同层级加 `toc-h1`、`toc-h2`… 类。
3. 对层级 ≤ `show_toc_level + 1` 的 `<ul>` 加 `pst-show_toc_level`，使其默认可见。
4. 若页面只有一个 `h1`，把它当作标题：没有 `h2` 时返回空 TOC；有 `h2` 时只输出标题下的 `<ul>`。

```python
html_theme_options = {
    "show_toc_level": 2,   # 默认展开到 h2；更深层级滚动时再显示
}
```

### 2.1 移除某页 TOC

在页面元数据中加：

```yaml
---
html_theme.sidebar_secondary.remove: true
---
```

`layout.html` 检测到该键后不渲染整个次级侧栏。也可以给该页配置空的 `secondary_sidebar_items`。

### 2.2 按页配置次级侧栏

`secondary_sidebar_items` 支持两种形态：

```python
# 全站统一
html_theme_options = {
    "secondary_sidebar_items": ["page-toc", "sourcelink"],
}

# 按页面模式
html_theme_options = {
    "secondary_sidebar_items": {
        "**": ["page-toc", "edit-this-page", "sourcelink"],
        "reference/api/*": ["page-toc"],
        "index": [],
    },
}
```

匹配使用 Sphinx 的 `patmatch`，支持 `*`、`?`、`[`。同一页匹配两个通配模式时会告警，并采用**最后一个**匹配项。

## 3. 滚动高亮

前端 `setupArticleTocSyncing` 负责：

1. 找出 `#pst-page-toc-nav` 下的所有 `.toc-entry` 与链接。
2. 把每个 TOC 链接映射到正文中对应的标题元素。
3. 用 `IntersectionObserver` 监听标题进入视口顶部 30% 区域。
4. 高亮对应 TOC 项及其祖先链，并设置 `aria-current="true"`。
5. 点击页内链接或 hash 变化时，先高亮目标项，并在 1 秒内禁用观察器，避免滚动过程反复切换。

这意味着：

- 页内标题必须有稳定 `id`（MyST 的 `myst_heading_anchors` 或 rST 自动生成）。
- 自定义 TOC 模板若改变了 `.toc-entry` 结构，滚动高亮会失效。
- 页面若没有 `#pst-page-toc-nav`，脚本直接返回。

## 4. 编辑此页

```python
html_theme_options = {"use_edit_page_button": True}

html_context = {
    "github_user": "my-org",
    "github_repo": "my-repo",
    "github_version": "main",
    "doc_path": "docs",
}
```

`edit_this_page.setup_edit_url` 会：

1. 用 `pagename + page_source_suffix` 得到文件名。
2. 拼接 `doc_path`（保证末尾有 `/`）。
3. 按 provider 模板生成 URL：

```text
GitHub : {github_url}/{user}/{repo}/edit/{version}/{doc_path}{file}
GitLab : {gitlab_url}/{user}/{repo}/-/edit/{version}/{doc_path}{file}
Bitbucket: {bitbucket_url}/{user}/{repo}/src/{version}/{doc_path}{file}?mode=edit
```

4. 预置 provider 的链接文案为 “Edit on GitHub/GitLab/Bitbucket”。

自定义 provider：

```python
html_context = {
    "edit_page_url_template": "https://git.example.com/edit/{{ file_name }}?ref=main",
    "edit_page_provider_name": "GitLab Self-Hosted",
}
```

模板必须包含 `file_name`，否则抛 `ExtensionError`。

## 5. 查看源码

`sourcelink` 依赖 Sphinx 的 `html_show_sourcelink`（默认 True）。要禁用：

```python
html_show_sourcelink = False
```

`html_sourcelink_suffix` 可控制链接后缀（例如设为 `""` 以去掉 `.txt`）。

## 6. 底部按钮

`prev-next` 默认渲染在正文之后，由 `show_prev_next` 控制：

```python
html_theme_options = {"show_prev_next": False}
```

它读取 Sphinx 的 `prev` / `next` 关系，因此同样依赖页面在 toctree 中的顺序。

## 7. 常见问题

| 现象 | 原因 | 处理 |
|---|---|---|
| 右侧空白 | 页面只有一个 `h1`，或 `secondary_sidebar_items` 为空 | 增加 `h2`，或恢复默认列表 |
| TOC 不随滚动高亮 | 标题缺少 `id`，或自定义模板破坏 `.toc-entry` | 开启 heading anchors，保留默认结构 |
| 编辑链接 404 | `doc_path` 或 `github_version` 错误 | 用浏览器打开生成 URL 逐段核对 |
| 编辑按钮不出现 | `use_edit_page_button` 未开，或 provider 字段缺失 | 检查 `html_context` 三件套 |
| 某页 TOC 去不掉 | 只改了 `secondary_sidebar_items` 但被字典通配覆盖 | 用页面元数据 `sidebar_secondary.remove` |
| 移动端右侧栏打不开 | 页面未渲染 `secondary_sidebar_items` | 检查该页是否被配置为空 |

## 相关概念

- [导航与 toctree](04-navigation-and-toctree.md)
- [布局与模板区段](03-layout-and-sections.md)
- [内部实现与扩展点](09-internals-and-extension-points.md)
- [Sphinx 交叉引用指南](../../sphinx/concepts/20-cross-references-guide.md)
