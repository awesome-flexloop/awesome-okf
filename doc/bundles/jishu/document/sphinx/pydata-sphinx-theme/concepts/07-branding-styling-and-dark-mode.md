---
type: Concept
title: 品牌、样式与暗色模式
description: logo 双版本、CSS 变量、light-dark()、Pygments 双主题、字体与主题专用内容
tags: [sphinx, theme, pydata, branding, css, dark-mode]
generated: { by: "reference_agent/deepseek-flash", at: "2026-11-24T03:12:00Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: pst-source-map
    resource: /references/source-map.md
    title: 源码路径映射
---

# 品牌、样式与暗色模式

## 1. Logo 的两套解析路径

PST 支持 light/dark 两个 logo。优先级：

```text
logo.image_light / logo.image_dark
    > html_logo
    > 无 logo（显示项目名）
```

配置：

```python
html_theme_options = {
    "logo": {
        "text": "My Project",
        "alt_text": "My Project - Home",
        "image_light": "_static/logo-light.svg",
        "image_dark": "_static/logo-dark.svg",
        "link": "https://example.com",
    },
}
```

构建期发生三件事：

1. `logo.copy_logo_images` 把本地图片复制到输出 `_static/`（目标已存在则跳过）。
2. `logo.setup_logo_path` 为每个模式计算 `image_relative`；远程 URL 原样使用，本地文件经 `pathto("_static/<name>")`。
3. 模板读取 `theme_logo.image_relative[light|dark]` 输出 `<img>`。

安全细节：路径以 `_t` 结尾会被判定为模板文件并抛 `ExtensionError`，防止把 Jinja 模板当图片路径注入。

### 1.1 只给一个模式

未提供的模式回退到 `html_logo`。如果两个模式都不提供且 `html_logo` 存在，则两者都用 `html_logo`。若只有 logo 没有可见文字，务必提供 `alt_text`。

## 2. 暗色模式的实现

### 2.1 状态机

```text
localStorage.mode  = "auto" | "light" | "dark"
localStorage.theme = "light" | "dark"          # auto 时由系统偏好决定
<html data-mode="..." data-theme="...">
```

- 首屏在 `<head>` 的内联脚本中读取 `localStorage`，避免闪烁。
- `setTheme(mode)` 校验值，写入 `data-mode` 与 `data-theme`，保存到 `localStorage`。
- `auto` 模式监听 `prefers-color-scheme` 变化。
- 主题同时设置 `color-scheme: light dark`，让滚动条/表单控件跟随。

### 2.2 CSS 变量

颜色变量定义在 `html[data-theme="light"]` 与 `html[data-theme="dark"]` 上：

```css
html[data-theme] {
  --pst-color-primary: light-dark(#0a7d91, #7fd6e8);
  --pst-color-secondary: light-dark(#e76f51, #f4a261);
}
```

自定义时用 `html[data-theme]`，不要用 `:root`——后者特异性不足，会被主题规则覆盖。

完整颜色族：

| 变量 | 用途 |
|---|---|
| `--pst-color-primary` | 主色（链接、按钮、强调） |
| `--pst-color-secondary` | 辅色（强调、次级按钮） |
| `--pst-color-accent` | 点缀色 |
| `--pst-color-success/info/warning/danger` | 语义状态 |
| `--pst-color-background` / `on-background` | 页面最底层与之上元素 |
| `--pst-color-surface` / `on-surface` | 卡片/代码块等表面层 |
| `--pst-color-target` | 搜索高亮/锚点目标 |

### 2.3 主题专用内容

| 类 | 行为 |
|---|---|
| `only-light` | 仅 light 模式显示 |
| `only-dark` | 仅 dark 模式显示 |
| `dark-light` | 声明图片在两种模式下都可直接使用，避免主题给图片加白底/降亮度 |

图片在 dark 模式下默认会被加白底并降低亮度；如果图片本身适合暗色，加 `dark-light` 可关闭该处理。

### 2.4 运行时响应主题变化

```javascript
const observer = new MutationObserver(() => {
  const dark = document.documentElement.dataset.theme === "dark";
  document.querySelector(".mainlogo").src =
    dark ? "_static/logo-dark.svg" : "_static/logo-light.svg";
});
observer.observe(document.documentElement, {
  attributes: true,
  attributeFilter: ["data-theme"],
});
```

## 3. 代码高亮双主题

```python
html_theme_options = {
    "pygments_light_style": "tango",
    "pygments_dark_style": "monokai",
}
```

`pygments.get_pygments_stylesheet` 生成：

```css
html[data-theme="light"] .highlight ... { ... }
html[data-theme="dark"]  .highlight ... { ... }
```

`overwrite_pygments_css` 在 `build-finished` 覆盖 `_static/pygments.css`。若样式名不存在，会告警并回退到 `tango` / `monokai`。默认样式来自 `accessible-pygments`，满足 WCAG AA/AAA 对比度。

## 4. 字体

主题只内置 FontAwesome 7 Free；正文与标题默认用系统字体。字体变量：

```css
html {
  --pst-font-family-base: Verdana, var(--pst-font-family-base-system);
  --pst-font-family-display: "Funnel Display", var(--pst-font-family-display-system);
  --pst-font-family-heading: Cambria, Georgia, var(--pst-font-family-base-system);
  --pst-font-family-monospace: Courier, var(--pst-font-family-monospace-system);
}
```

`*-system` 变量是默认字体栈，适合作为回退。若使用系统没有的字体，需要自行托管并覆盖 `fonts` 块：

```html+jinja
{% extends "pydata_sphinx_theme/layout.html" %}

{% block fonts %}
  <link rel="stylesheet" href="{{ pathto('_static/vendor/myfont/index.css', 1) }}">
{% endblock %}
```

FontAwesome 版本升级不受支持；主题的类名与图标集绑定在 7.x。v0.24.0 起普通 FontAwesome `<i>` 不再转成 `<svg>`，自定义图标仍是 `<svg>`。

## 5. 自定义 CSS/JS 的四种方式

1. **`html_css_files` / `html_js_files`**：最简单，路径相对 `html_static_path`。
2. **`app.add_css_file` / `app.add_js_file`**：在扩展 `setup()` 中注册，可加 `body=` 内联脚本。
3. **`html-page-context` 事件**：只对特定页面注入资源。
4. **页面内 `<style>` / `<script>` 或 rST `.. raw:: html`**：适合一次性实验，不利于维护。

```python
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]
html_js_files = [("js/custom.js", {"defer": "defer"})]
```

`html_static_path` 中的目录会保留相对结构复制到输出的 `_static/`。`html_css_files` / `html_js_files` 的路径相对 `html_static_path` 的**输出根**，例如 `_static/css/custom.css` 写作 `css/custom.css`；模板中引用时用 `pathto('_static/css/custom.css', 1)` 更稳妥。

## 6. 设计系统约束

- 颜色需满足 WCAG 2 AA/AAA；不要只靠色相区分状态。
- 交互元素需要可见焦点（WCAG 2.4.7）与键盘可达（WCAG 2.1.1）。
- 自定义组件应复用 `--pst-color-*` 与 `--pst-font-*`，避免硬编码颜色导致暗色模式失效。
- 暗色模式下图片默认加白底/降亮度；用 `dark-light` 显式声明例外。

## 7. 常见问题

| 现象 | 原因 | 处理 |
|---|---|---|
| 自定义颜色不生效 | 用了 `:root` | 改用 `html[data-theme]` |
| 暗色模式首屏闪白 | 自定义脚本延迟设置 `data-theme` | 依赖主题的内联脚本，不要重复实现 |
| logo 在暗色下看不清 | 只提供了一张深色 logo | 提供 `image_dark` 或换用两种模式都可见的图 |
| 代码块高亮不随主题变 | 自定义 CSS 覆盖了 `pygments.css` | 用 `html[data-theme="..."] .highlight` 前缀 |
| 字体没加载 | 只改了变量，没有托管字体 | 覆盖 `fonts` 块并自托管 |
| 图片在暗色下被加白底 | 未声明 `dark-light` | 给适合暗色的图片加该类 |

## 相关概念

- [主题配置项](06-theme-options.md)
- [布局与模板区段](03-layout-and-sections.md)
- [品牌化与暗色模式示例](../examples/03-branding-and-dark-mode.md)
- [社区设计系统（上游）](https://pydata-sphinx-theme.readthedocs.io/en/stable/community/design-system.html)
