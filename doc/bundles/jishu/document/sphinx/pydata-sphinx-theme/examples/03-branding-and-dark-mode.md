---
type: Example
title: 品牌化与暗色模式
description: 双 logo、CSS 变量、Pygments 主题、字体覆盖与模式专用图片的完整示例
tags: [sphinx, theme, pydata, example, branding, dark-mode]
generated: { by: "reference_agent/deepseek-flash", at: "2026-11-24T03:30:00Z" }
status: stable
stale_after: 2027-11-24
sources:
  - id: pst-source-map
    resource: /references/source-map.md
    title: 源码路径映射
---

# 品牌化与暗色模式

## 目标

把默认的 PyData 蓝橙配色改成品牌色，提供两种模式的 logo，代码高亮使用 `tango`/`monokai`，并让一张示意图只出现在暗色模式。

## 1. 双 logo

```python
html_theme_options = {
    "logo": {
        "text": "Acme",
        "image_light": "_static/brand/logo-light.svg",
        "image_dark": "_static/brand/logo-dark.svg",
        "alt_text": "Acme - Home",
        "link": "https://acme.example",
    },
}
```

构建后：两张图被复制到 `_build/html/_static/`，模板根据 `data-theme` 选择 `image_relative.light` 或 `.dark`。

## 2. 品牌色

`_static/css/brand.css`：

```css
html[data-theme] {
  --pst-color-primary: light-dark(#0b5cad, #6cb6ff);
  --pst-color-secondary: light-dark(#c2410c, #fb923c);
  --pst-color-accent: light-dark(#0f766e, #5eead4);
  --pst-color-link: var(--pst-color-primary);
  --pst-color-link-hover: var(--pst-color-secondary);
}
```

接入：

```python
html_static_path = ["_static"]
html_css_files = ["css/brand.css"]
```

要点：

- 必须用 `html[data-theme]`，不要用 `:root`。
- 同时给 light 与 dark 两个值，避免暗色下对比度不足。
- 不要覆盖 `--pst-color-success/warning/danger`，除非你确认语义色仍可区分。

## 3. 代码高亮

```python
html_theme_options = {
    "pygments_light_style": "tango",
    "pygments_dark_style": "monokai",
}
```

构建后 `_static/pygments.css` 会包含：

```css
html[data-theme="light"] .highlight .k { ... }
html[data-theme="dark"]  .highlight .k { ... }
```

若样式名拼错，构建日志会告警并回退到 `tango` / `monokai`。

## 4. 字体

```css
html {
  --pst-font-family-base: "Source Sans 3", var(--pst-font-family-base-system);
  --pst-font-family-heading: "Source Serif 4", var(--pst-font-family-base-system);
  --pst-font-family-monospace: "JetBrains Mono", var(--pst-font-family-monospace-system);
}
```

自托管字体：

```html+jinja
{# _templates/layout.html #}
{% extends "pydata_sphinx_theme/layout.html" %}

{% block fonts %}
  <link rel="stylesheet" href="{{ pathto('_static/vendor/fonts/fonts.css', 1) }}">
{% endblock %}
```

```python
templates_path = ["_templates"]
```

## 5. 模式专用内容

````markdown
```{image} _static/diagram-dark.png
:class: only-dark
:alt: 架构图（暗色）
```

```{image} _static/diagram-light.png
:class: only-light
:alt: 架构图（亮色）
```

```{image} _static/photo.jpg
:class: dark-light
:alt: 两种模式都可直接使用的图片
```
````

- `only-dark` / `only-light`：只在一个模式显示。
- `dark-light`：告诉主题“这张图不需要白底/降亮度处理”。

## 6. 自定义组件跟随主题

```css
.my-card {
  background: var(--pst-color-surface);
  color: var(--pst-color-on-surface);
  border: 1px solid var(--pst-color-border);
  border-radius: 0.5rem;
  padding: 1rem;
}
```

避免写死 `#fff` / `#000`；使用 `--pst-color-*` 让组件自动适配两种模式。

## 7. JavaScript 响应切换

```javascript
// _static/js/theme-hook.js
new MutationObserver(() => {
  const dark = document.documentElement.dataset.theme === "dark";
  document.querySelectorAll(".brand-hero").forEach((el) => {
    el.dataset.mode = dark ? "dark" : "light";
  });
}).observe(document.documentElement, {
  attributes: true,
  attributeFilter: ["data-theme"],
});
```

```python
html_js_files = [("js/theme-hook.js", {"defer": "defer"})]
```

## 8. 验收

- [ ] light/dark 切换时 logo 自动更换。
- [ ] 主色在两种模式下对比度足够（用 Axe 或对比度工具检查）。
- [ ] 代码块颜色随主题变化。
- [ ] 字体在无网络时回退到系统字体。
- [ ] 模式专用图片只在一个模式出现。
- [ ] 自定义卡片在暗色下没有白底残留。

## 相关概念

- [品牌、样式与暗色模式](../concepts/07-branding-styling-and-dark-mode.md)
- [主题配置项](../concepts/06-theme-options.md)
- [可访问性、性能与 FAQ](../concepts/10-accessibility-performance-faq.md)
