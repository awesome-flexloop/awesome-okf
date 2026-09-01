---
type: concept
title: "CSS 变量与主题切换"
description: "基于 CSS 自定义属性的颜色系统、暗色模式支持和主题定制机制"
bundle: myst-theme
sources:
  - /references/structure-styles-src.md
  - /spec/facts.md
related:
  - 00-theme-architecture.md
  - 02-grid-layout-system.md
tags: [myst-theme, concept]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
---

# CSS 变量与主题切换

## 颜色系统架构

myst-theme 的颜色系统完全建立在 CSS 自定义属性（CSS Variables/Custom Properties）之上。所有颜色值都通过 `--myst-color-*` 命名空间的变量定义，组件中使用 Tailwind 类名间接引用这些变量。

```
CSS 变量定义（styles/*.css）
    ↓
Tailwind themeExtensions 映射（styles/index.js）
    ↓
组件中使用 Tailwind 类名（bg-myst-info-bg、text-myst-link）
    ↓
最终渲染为 CSS 变量引用
```

## 语义色分类

### 功能色

| 类别 | 变量示例 | 用途 |
|------|---------|------|
| 链接 | `--myst-color-link`, `--myst-color-link-hover` | 超链接颜色 |
| 主色 | `--myst-color-primary`, `--myst-color-primary-hover` | 按钮、主操作 |
| 焦点 | `--myst-color-focus-ring`, `--myst-color-focus-outline` | 键盘焦点指示器 |
| 激活 | `--myst-color-active`, `--myst-color-active-bg` | 活动状态（当前标签页等） |

### 中性色

| 类别 | 变量示例 | 用途 |
|------|---------|------|
| 背景 | `--myst-color-bg`, `--myst-color-bg-secondary` | 页面/区域背景 |
| 表面 | `--myst-color-surface`, `--myst-color-surface-hover` | 卡片、面板表面 |
| 文本 | `--myst-color-text`, `--myst-color-text-secondary/tertiary` | 正文、次要、辅助文本 |
| 边框 | `--myst-color-border`, `--myst-color-border-strong` | 分割线、边框 |
| 反色 | `--myst-color-inverse-bg`, `--myst-color-inverse-text` | 深色背景上的浅色 |
| 代码 | `--myst-color-code` | 行内代码颜色 |

### 语义状态色（Admonition/Proof 等）

每个语义色有三个变体（主色/背景/文本）：

| 语义 | 主色 | 背景色 | 文本色 |
|------|------|--------|--------|
| info | `--myst-color-info` | `--myst-color-info-bg` | `--myst-color-info-text` |
| success | `--myst-color-success` | `--myst-color-success-bg` | `--myst-color-success-text` |
| tip | `--myst-color-tip` | `--myst-color-tip-bg` | `--myst-color-tip-text` |
| warning | `--myst-color-warning` | `--myst-color-warning-bg` | `--myst-color-warning-text` |
| danger | `--myst-color-danger` | `--myst-color-danger-bg` |--myst-color-danger-text` |
| error | `--myst-color-error` | `--myst-color-error-bg` | `--myst-color-error-text` |
| theorem | `--myst-color-theorem` | `--myst-color-theorem-bg` | `--myst-color-theorem-text` |
| example | `--myst-color-example` | `--myst-color-example-bg` | `--myst-color-example-text` |
| proof | `--myst-color-proof` | `--myst-color-proof-bg` | `--myst-color-proof-text` |

三变体模式使得 admonition 组件可以统一使用 `bg-myst-{kind}-bg`、`text-myst-{kind}-text`、`border-l-myst-{kind}` 类名，kind 作为变量传入。

## Tailwind 注册

在 `styles/index.js` 的 themeExtensions.colors 中，CSS 变量被注册为 Tailwind 颜色：

```js
colors: {
  myst: {
    link: 'var(--myst-color-link)',
    'link-hover': 'var(--myst-color-link-hover)',
    primary: 'var(--myst-color-primary)',
    // ...
    info: 'var(--myst-color-info)',
    'info-bg': 'var(--myst-color-info-bg)',
    'info-text': 'var(--myst-color-info-text)',
    // ... 所有语义色
  }
}
```

组件中即可使用：
```html
<div class="bg-myst-info-bg text-myst-info-text border-l-4 border-myst-info">
  This is an info admonition
</div>
```

## 暗色模式

暗色模式通过 CSS 类切换实现。当 `<html>` 或根元素添加 `dark` 类时，CSS 变量值被覆盖：

```css
/* 默认（亮色） */
:root {
  --myst-color-bg: #ffffff;
  --myst-color-text: #1a1a1a;
  --myst-color-link: #2563eb;
  /* ... */
}

/* 暗色模式 */
.dark {
  --myst-color-bg: #0f172a;
  --myst-color-text: #e2e8f0;
  --myst-color-link: #60a5fa;
  /* ... */
}
```

**关键优势**：
- 只需切换一个 CSS class 即可完成全站点主题切换
- 组件代码不需要任何修改（始终引用相同的 CSS 变量名）
- 过渡动画只需在 CSS 变量上设置 transition
- 用户可以通过浏览器偏好（prefers-color-scheme）或手动切换

ThemeProvider 提供 `theme` 和 `setTheme` 接口管理暗色/亮色状态。

代码高亮也分两套 CSS：`code-highlight-light.css` 和 `code-highlight-dark.css`，暗色模式下加载 dark 版本。

## 品牌定制

通过覆盖 CSS 变量即可实现品牌定制，无需重新构建组件：

```css
/* 自定义品牌主题 */
:root {
  --myst-color-link: #0066cc;        /* 品牌蓝 */
  --myst-color-primary: #ff6600;     /* 品牌橙 */
  --myst-color-primary-hover: #ff8533;
}
```

定制方式：
1. **CSS 文件覆盖**：在主题的 `styles/app.css` 中重新定义变量
2. **内联样式**：通过 `<style>` 标签动态注入
3. **Tailwind 配置**：如果需要修改 Tailwind 层面的配置，在主题的 `tailwind.config.js` 中扩展

## Typography 集成

`@tailwindcss/typography` 插件的 `prose` 类默认颜色被覆盖为 myst CSS 变量：

```js
typography: (theme) => ({
  DEFAULT: {
    css: {
      '--tw-prose-links': 'var(--myst-color-link)',
      '--tw-prose-body': 'var(--myst-color-prose-body)',
      '--tw-prose-headings': 'var(--myst-color-text)',
      '--tw-prose-code': 'var(--myst-color-code)',
      '--tw-prose-bold': 'var(--myst-color-text)',
      // 移除 code 前后反引号
      'code::before': { content: 'none' },
      'code::after': { content: 'none' },
    }
  }
})
```

这使得 Tailwind typography 的所有排版样式自动适配 myst 颜色主题，包括暗色模式切换。

## 与组件库的关系

CSS 变量是样式系统的**唯一真理源**（single source of truth）：
- myst-to-react 组件不硬编码颜色值，全部使用 `bg-myst-*`/`text-myst-*` Tailwind 类
- themes/book 和 themes/article 通过覆盖 CSS 变量实现不同的视觉风格
- jupyter 包的组件（BinderBadge、Outputs 等）同样使用 myst 颜色变量

这确保了无论在哪个主题、哪个环境（站点/JupyterLab）中使用，组件颜色行为一致且可通过 CSS 变量统一控制。
