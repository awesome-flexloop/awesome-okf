---
type: spec
title: "pydata-sphinx-theme 对抗审查记录（V 阶段）"
---

# 对抗审查记录（V 阶段）

> 对象：本知识包 `concepts/`、`examples/`、`references/` 初稿。
> 方法：逐条声明回查源码与官方文档；每条质疑必须给出证据与处置。
> 结论：发现 9 处需要修正的问题，已全部回改；另有 4 处确认无需修改。

## 一、已修正问题

### V-01 示例中的嵌套代码围栏失效

- **质疑**：`01-getting-started.md` 用三个反引号包裹含 `{toctree}` 的 Markdown 示例，内层围栏会提前闭合。
- **证据**：Markdown 围栏规则；Sphinx/MyST 解析行为。
- **处置**：外层改为四个反引号，内层保留三个。同类检查覆盖 `examples/01-basic-site.md`、`examples/02-navigation-and-layout.md`。

### V-02 静态资源“扁平化复制”表述错误

- **质疑**：初稿称 `html_static_path` 中的目录会被扁平化，与示例中 `css/custom.css` 的用法自相矛盾。
- **证据**：Sphinx 复制静态资源时保留相对目录；`html_css_files` 路径相对输出 `_static` 根。
- **处置**：改为“保留相对结构”，并补充 `pathto` 的稳妥写法。影响 `07-branding-styling-and-dark-mode.md`、`examples/05-custom-components.md`。

### V-03 `app.add_js_file(..., defer=True)` 参数错误

- **质疑**：Sphinx 的 `add_js_file` 不把 `defer` 作为布尔关键字处理。
- **证据**：主题自身使用 `app.add_js_file(path, loading_method="defer")`；Sphinx API 使用 `loading_method`。
- **处置**：示例改为 `loading_method="defer"`。

### V-04 顶部导航默认组成与旧文档不一致

- **质疑**：上游 `layout.rst` 写默认 `navbar_end = ["navbar-icon-links"]`，但 `theme.conf` 实际为 `theme-switcher, navbar-icon-links`。
- **证据**：`theme.conf` 第 `navbar_end` 行；`layout.rst` 为旧版说明。
- **处置**：以 `theme.conf` 为准，教程明确写“默认含 theme-switcher”。同时提醒读者升级后以 `theme.conf` 核对。

### V-05 “禁用搜索会移除默认搜索按钮”表述过宽

- **质疑**：`disable_search` 只在用户未显式设置 `navbar_persistent` 时清空它，且不移除手动放置的 `search-button` / `search-field`。
- **证据**：`__init__.py` 中 `disable_search` 分支使用 `setdefault`；`search.rst` 明确说明只控制 `search-button-field`。
- **处置**：在 `08-search-versioning-and-announcements.md` 增加两条限定，避免读者误以为全站搜索 UI 一定消失。

### V-06 版本警告横幅的比较对象不精确

- **质疑**：初稿只写“比较版本”，未说明先比较 `version_match`、再比较 `release`。
- **证据**：`showVersionWarningBanner` 先判断 `preferredVersion === theme_switcher_version_match`，再用 `compare(version, preferredVersion)`。
- **处置**：补充“先 version_match 精确匹配，再 compare-versions 比较 release”的顺序。

### V-07 侧栏缓存条件表述缺少 `dirhtml` 例外

- **质疑**：初稿只说“同祖先同目录共享缓存”，未说明 `dirhtml` 的 URI 以 `/` 结尾而不缓存。
- **证据**：`_sidebar_cache_key` 中 `if not page_uri or page_uri.endswith("/"): return None`。
- **处置**：在 `04-navigation-and-toctree.md` 明确写出 `dirhtml` 不缓存及其原因。

### V-08 组件数量与默认模板列表需以源码为准

- **质疑**：初稿凭印象写“20+ 组件”，未给出准确数量。
- **证据**：`components/` 目录实际 23 个 `.html` 文件。
- **处置**：统一写“23 个可插拔组件”，并在 `references/source-map.md` 列出目录职责。

### V-09 跨 bundle 相对链接层级错误

- **质疑**：`00-introduction.md` 中“Alabaster 默认主题”写作 `../alabaster/index.md`，从 `concepts/` 出发只上升到 bundle 根，无法到达同组的 alabaster。
- **证据**：相对路径解析 + 实际目录树；应上升两级到 `sphinx/` 组目录。
- **处置**：改为 `../../alabaster/index.md`；并用脚本对全包 20 个内容文档的所有相对 `.md` 链接做存在性检查，结果 0 断链。

## 二、质疑后确认无需修改

### C-01 `theme_version` 是否真的可用

- **质疑**：模板中 `theme_version` 可能不存在。
- **核查**：`update_and_remove_templates` 末尾执行 `context["theme_version"] = __version__`。
- **结论**：可用，保留示例。

### C-02 `generate_toc_html` 对单 `h1` 页面的行为

- **质疑**：是否所有页面都有 TOC。
- **核查**：只有一个 `h1` 且无 `h2` 时返回空字符串；`page-toc.html` 会因此渲染为空并被移除。
- **结论**：教程已写“单 h1 无 h2 时 TOC 为空”，无需改。

### C-03 `icon_links` 的三种类型

- **质疑**：是否支持本地图片。
- **核查**：`header-links.rst` 明确 `fontawesome`、`url`、`local` 三种；`local` 路径相对文档根。
- **结论**：保留。

### C-04 公告条关闭时长

- **质疑**：初稿写“永久关闭”。
- **核查**：`setupAnnouncementBanner` 与版本横幅均使用 14 天窗口。
- **结论**：已改为“14 天内不再显示”。

## 三、剩余风险

1. 上游默认值与模板结构可能随版本变化；本包以 `0.25.0dev0` 为基准，`stale_after` 设为 2027-11-24。
2. 未在真实站点上做浏览器矩阵验证；交互行为结论来自源码与官方文档。
3. 可访问性只做了源码级核对，未执行 Axe/读屏实测。
4. 示例配置未全部在空项目中逐条构建；建议读者按“验收清单”逐项确认。

## 四、审查结论

- 事实性：通过（所有关键声明可回查 `spec/facts.md` 与源码路径）。
- 行为性：通过（事件时序、缓存条件、前端分支已核对）。
- 边界：已覆盖 `dirhtml`、非 HTML builder、`file://`、无祖先页面、空模板。
- 可操作性：示例具备完整 `conf.py` 与目录结构，可按步骤复现。
- 处置：9 处修正已落地；4 处质疑确认无需修改。
