---
type: Concept
title: 搜索、版本切换与公告
description: 搜索弹窗与即时搜索、switcher.json 版本切换、警告横幅、公告条与分析统计
tags: [sphinx, theme, pydata, search, version-switcher, announcement, analytics]
generated: { by: "reference_agent/deepseek-flash", at: "2026-11-24T03:16:00Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: pst-source-map
    resource: /references/source-map.md
    title: 源码路径映射
---

# 搜索、版本切换与公告

这三类功能共享一个特征：**配置在 Python 侧，行为在浏览器侧**。Python 负责把参数注入 `DOCUMENTATION_OPTIONS` 或渲染容器，JavaScript 负责异步加载与交互。

## 1. 搜索

### 1.1 三种形态

| 形态 | 模板 | 位置 |
|---|---|---|
| 搜索按钮 + 弹窗 | `search-button-field` | `navbar_persistent`（默认） |
| 仅图标按钮 | `search-button` | 任意区段 |
| 常驻输入框 | `search-field` | 侧栏、页脚、navbar_end |

```python
html_theme_options = {
    "navbar_persistent": ["search-button-field"],
    "search_bar_text": "搜索文档…",
}
```

### 1.2 快捷键

- Windows/Linux：`Ctrl + K`
- macOS：`Cmd + K`
- `Escape`：关闭弹窗并清空即时搜索结果

前端 `toggleSearchField()` 会先找页面上的 `form.bd-search`：

- 若只有弹窗里的隐藏输入框，则打开/关闭 `<dialog id="pst-search-dialog">`。
- 若存在常驻输入框，则聚焦它，而不是打开弹窗。
- 同时存在两者时，优先常驻输入框；官方明确建议**二选一**，避免移动端焦点落到不可见控件。

### 1.3 搜索即输

```python
html_theme_options = {"search_as_you_type": True}
```

实现要点：

1. 主题在每页加载 `searchtools.js`、`language_data.js`、`searchindex.js`（搜索页除外，避免重复）。
2. 监听弹窗输入框 `keyup`，300 ms 防抖后调用 `Search.performSearch(query)`。
3. 结果注入 `#search-results`；用 `data-content_root` 修正相对链接。
4. 在真正的 `search` 页强制关闭该功能，避免与 `searchtools.js` 争用同一容器。

### 1.4 禁用内置搜索

```python
html_theme_options = {"disable_search": True}
```

效果：

- 不渲染 `#pst-search-dialog`，快捷键也不会打开它。
- 用户未显式设置 `navbar_persistent` 时，自动设为 `[]`，移除默认搜索按钮。
- **不会**移除你手动放置的 `search-button` 或 `search-field`，需要自行删除。

## 2. 版本切换器

### 2.1 三个步骤

1. 准备一个稳定的 `switcher.json`。
2. 配置 `switcher.json_url` 与 `version_match`。
3. 把 `version-switcher` 模板放进某个区段。

```python
html_theme_options = {
    "switcher": {
        "json_url": "https://example.org/docs/switcher.json",
        "version_match": version,
    },
    "navbar_center": ["version-switcher", "navbar-nav"],
}
```

`switcher.json`：

```json
[
  {"name": "stable", "version": "2.4", "url": "https://example.org/docs/2.4/", "preferred": true},
  {"name": "latest", "version": "2.5.dev", "url": "https://example.org/docs/latest/"},
  {"version": "2.3", "url": "https://example.org/docs/2.3/"}
]
```

字段：

| 字段 | 必填 | 说明 |
|---|---|---|
| `version` | 是 | 与 `version_match` 比较，决定当前项高亮 |
| `url` | 是 | 该版本文档根 URL |
| `name` | 否 | 下拉中显示的名称；缺省用 `version` |
| `preferred` | 否 | 至多一个；标记“最新稳定版”，供警告横幅使用 |

### 2.2 点击行为

点击条目时前端：

1. 计算当前页在目标版本中的路径。
2. 对目标 URL 发 `HEAD` 请求。
3. 存在则跳转；404 或 CORS 失败则回退到目标版本首页。

这解决了“某页在新版本中不存在”的 404 问题，但也意味着需要目标站点允许 `HEAD`。

### 2.3 构建期校验

`update_config` 会在 `check_switcher=True` 时读取 JSON：

- 缺 `url` 或 `version` → 告警。
- 不是合法 JSON → 报错。
- URL 不可达 → 告警（不阻断构建）。

CI 中若网络不稳定，可设 `"check_switcher": False`。

### 2.4 本地 `file://` 限制

浏览器禁止 `file://` 页面 fetch 本地 JSON，因此直接打开构建产物时切换器为空。用 `python -m http.server` 预览即可。

## 3. 版本警告横幅

```python
html_theme_options = {
    "show_version_warning_banner": True,
    "sticky_banners": True,   # 可选：固定在视口顶部
}
```

规则：

1. JSON 中必须**恰好一个** `preferred: true`，否则不显示。
2. 若 `version_match` 等于 preferred 的 `version`，视为稳定版，不显示。
3. 否则用 `compare-versions` 比较 `release`：
   - 小于 preferred → “an old version (x.y)”，附“切换到稳定版”按钮。
   - 大于 preferred，或版本串含 `dev`/`rc`/`pre` → “an unstable development version”。
4. 用户关闭后写入 `localStorage.pst_banner_pref`，14 天内不再显示。

## 4. 公告条

```python
html_theme_options = {
    "announcement": "这里是一段 <a href='...'>公告 HTML</a>",
}
```

- 值不以 `http` 开头：直接作为原始 HTML 插入。
- 值以 `http` 开头：浏览器异步 `fetch` 该 URL，把返回 HTML 插入。
- 远程文件为空：视为移除公告，且无需重新构建。
- 关闭状态写入 `localStorage.pst_announcement_banner_pref`，保留 14 天。

远程公告适合“多版本共用一个公告源”：改一个文件即可让所有版本文档同步更新。

## 5. 分析统计

```python
html_theme_options = {
    "analytics": {
        "plausible_analytics_domain": "docs.example.org",
        "plausible_analytics_url": "https://plausible.example.org/js/script.js",
    },
}
```

或：

```python
html_theme_options = {
    "analytics": {"google_analytics_id": "G-XXXXXXXXXX"},
}
```

- Plausible：注册 `defer` 脚本，带 `data-domain`。
- Google Analytics：注入 consent 默认拒绝的 gtag 配置，再异步加载 `gtag/js`。
- 官方建议优先 Plausible（隐私与自托管友好）。

## 6. 交互时序

```text
页面加载
├── 内联脚本恢复 mode/theme
├── fetchRevealBannersTogether()
│   ├── fetchAndUseVersions()  → 切换器 + 警告横幅
│   └── setupAnnouncementBanner() → 远程公告
├── addModeListener()
├── scrollToActive()
├── setupSearchButtons()
├── setupSearchAsYouType()
├── setupMobileSidebarKeyboardHandlers()
├── setupArticleTocSyncing()
└── setupCollapseSidebarButton()
```

横幅加载完成后统一展开 `.pst-async-banner-revealer`，避免布局跳动。

## 7. 常见问题

| 现象 | 原因 | 处理 |
|---|---|---|
| 搜索无结果 | `searchindex.js` 未生成/未加载 | 确认使用 HTML builder；检查控制台 404 |
| 即时搜索链接 404 | `data-content_root` 缺失或被覆盖 | 不要自定义 `<html>` 标签 |
| 切换器空白 | `file://` 预览、JSON 不可达、`version_match` 不匹配 | 用 HTTP 预览，检查 JSON 与版本串 |
| 警告横幅不出现 | 没有或有多个 `preferred` | 只保留一个 |
| 公告不更新 | 用的是本地字符串而非 URL | 改为远程 URL，改文件即可 |
| 分析脚本未加载 | CSP 或 `analytics` 键拼写错误 | 检查控制台与 `update_config` 逻辑 |

## 相关概念

- [主题配置项](06-theme-options.md)
- [版本切换与搜索示例](../examples/04-version-switcher-and-search.md)
- [内部实现与扩展点](09-internals-and-extension-points.md)
- [Read the Docs 集成](https://pydata-sphinx-theme.readthedocs.io/en/stable/user_guide/readthedocs.html)
