---
type: Concept
title: 可访问性、性能与常见问题
description: 键盘与读屏支持、Axe 回归测试、构建性能优化与高频故障排查
tags: [sphinx, theme, pydata, accessibility, performance, troubleshooting]
generated: { by: "reference_agent/deepseek-flash", at: "2026-11-24T03:24:00Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: pst-source-map
    resource: /references/source-map.md
    title: 源码路径映射
---

# 可访问性、性能与常见问题

## 1. 可访问性

### 1.1 主题已做的

| 层面 | 措施 |
|---|---|
| 语义 | `role="heading"` 补 `aria-level`；表格加可滚动容器；skip link 直达 `#main-content` |
| 当前状态 | 侧栏 `aria-current="page"`；TOC `aria-current="true"` |
| 键盘 | 搜索 `Ctrl/Cmd+K`、Escape 关闭；抽屉可用键盘开关；可滚动区域 `tabIndex=0` |
| 焦点 | 可见焦点环；打开移动抽屉后聚焦抽屉本身而不是首个控件（规避 WebKit 焦点环） |
| 颜色 | 默认高亮用 `accessible-pygments`；颜色族按 WCAG AA/AAA 调整 |
| 动效 | 遵循 `prefers-reduced-motion`，侧栏折叠/抽屉动画可被禁用 |
| 文案 | 内置字符串可翻译；图标链接有 `icon_links_label` |

### 1.2 站点侧建议

```python
language = "zh_CN"          # 让 <html lang> 正确
html_baseurl = "https://docs.example.org/"
extensions += ["sphinx_sitemap"]
sitemap_locales = [None]
sitemap_url_scheme = "{link}"
```

- 为纯 logo 提供 `alt_text`；有可见文字时可不重复。
- 图片在暗色下若本身适配，加 `dark-light`。
- 自定义交互组件必须支持键盘与焦点可见。
- 用浏览器 DevTools 的 Accessibility Inspector、Axe DevTools、WAVE 做抽查。

### 1.3 自动化测试的边界

主题用 Playwright + Axe-core 扫描 Kitchen Sink 页面，测试文件为 `tests/test_a11y.py`。官方明确说明：自动化最多发现约 30–40% 的问题，**通过 Axe 不等于可访问**。仍需人工键盘走查与读屏测试。

## 2. 构建性能

PST 的主要性能成本来自侧栏 toctree 的解析与渲染。

### 2.1 先调深度

```python
html_theme_options = {
    "navigation_depth": 2,
    "show_nav_level": 1,
}
```

### 2.2 排除生成页

API 文档常用 `autosummary` 生成大量 stub 页。用 `sphinx-remove-toctrees` 把它们从导航中移除：

```python
extensions += ["sphinx_remove_toctrees"]
remove_from_toctrees = ["reference/generated/*"]
```

### 2.3 缓存机制

- 侧栏缓存在 `collapse_navigation=False` 时生效，按“祖先 + 输出目录 + 展开层级 + kwargs”复用。
- `dirhtml` 每页一个目录，无法共享，构建更慢但链接更干净。
- 若你自定义了 `generate_toctree_html` 的调用方式，可能破坏缓存键，导致重复解析。

### 2.4 其他成本

| 成本 | 说明 |
|---|---|
| 搜索索引 | 页面越多，`searchindex.js` 越大；即时搜索会每页加载 |
| 主题 CSS/JS | 通过 webpack 打包，生产模式压缩；开发模式体积更大 |
| Pygments | 双主题 CSS 在 `build-finished` 生成，成本固定 |
| 图片/Notebook | 大输出会显著增大 HTML；优先压缩或外链 |

## 3. 高频问题排查表

### 3.1 主题未生效

| 检查 | 命令/位置 |
|---|---|
| 是否安装 | `python -c "import pydata_sphinx_theme"` |
| 是否配置 | `html_theme = "pydata_sphinx_theme"` |
| 是否被覆盖 | 其他扩展是否改了 `html_theme` |
| 构建日志 | 是否有 `theme pydata_sphinx_theme` 相关报错 |

### 3.2 资源 404

- 检查 `_build/html/_static/styles/pydata-sphinx-theme.css` 是否存在。
- 若使用自定义 `layout.html`，确认没有丢掉 `_webpack.head_pre_assets()` 与 `_webpack.body_post()`。
- `html_static_path` 中的目录会被扁平化复制，引用路径以输出为准。

### 3.3 导航异常

| 现象 | 优先检查 |
|---|---|
| 顶部缺项 | `root_doc` 的 toctree 是否包含该顶层页 |
| 左侧空白 | 当前页是否有祖先；`html_sidebars` 是否为空 |
| 左侧层级过深/过浅 | `show_nav_level`、`navigation_depth` |
| 高亮错页 | 是否自定义缓存；是否用 `dirhtml` |
| More 下拉不出现 | 链接数是否 ≤ `header_links_before_dropdown + 1` |

### 3.4 暗色模式异常

| 现象 | 原因 |
|---|---|
| 首屏闪白 | 自定义脚本晚于主题内联脚本设置 `data-theme` |
| 自定义颜色无效 | 用了 `:root` 而非 `html[data-theme]` |
| 图片被加白底 | 未加 `dark-light` |
| 代码高亮不切换 | 自定义 CSS 覆盖了 `pygments.css` 的双前缀规则 |

### 3.5 版本切换器/公告异常

- `file://` 下无法 fetch：改用 HTTP 预览。
- `switcher.json` 不可达：检查 `json_url` 与 CORS。
- 警告横幅不出现：`preferred` 必须恰好一个。
- 公告不更新：只有 URL 形式才能“改文件即更新”。

### 3.6 构建报错

| 报错 | 处理 |
|---|---|
| `Incorrect logo config type` | `logo` 必须是字典 |
| `icon_links must be a list` | `icon_links` 必须是列表 |
| `Missing required value for use_edit_page_button` | 补齐 `html_context` 的 provider 字段 |
| `Path to ... logo does not exist` | 修正相对 `conf.py` 的路径 |
| `Highlighting style ... not found` | 换用 Pygments 已有样式 |

## 4. 升级策略

1. 先升级 PST，再升级 Sphinx；两者版本约束在 `pyproject.toml` 中声明。
2. 阅读 release notes，重点看默认值变更与废弃键。
3. 在 CI 中保留一次全量构建与链接检查。
4. 用视觉回归（截图）捕捉布局漂移。
5. 若使用自定义模板，升级后重点检查 `sections/` 与 `components/` 的块名是否变化。

## 5. 质量门清单

- [ ] `sphinx-build -W` 无新增警告。
- [ ] 顶部/左侧/右侧导航在三类页面（首页、章节页、API 页）均正确。
- [ ] light/dark/auto 切换与刷新保持。
- [ ] 搜索快捷键、即时搜索、搜索页均可用。
- [ ] 移动端抽屉可开、可关、可 Escape。
- [ ] 键盘 Tab 顺序合理，焦点可见。
- [ ] `switcher.json` 校验通过，警告横幅逻辑正确。
- [ ] 构建产物无 404，`pygments.css` 含双主题前缀。

## 相关概念

- [主题配置项](06-theme-options.md)
- [搜索、版本切换与公告](08-search-versioning-and-announcements.md)
- [内部实现与扩展点](09-internals-and-extension-points.md)
- [上游可访问性指南](https://pydata-sphinx-theme.readthedocs.io/en/stable/user_guide/accessibility.html)
