---
type: example
title: "定制 Book 主题"
description: "通过 CSS 变量覆盖、自定义渲染器和主题配置来定制 Book 主题外观"
tags: [myst-theme, book-theme, customization, css-variables]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "themes/book/"
  - path: "styles/index.js"
---

# 定制 Book 主题

本例展示三种层次的 Book 主题定制：颜色品牌化、渲染器替换、布局调整。

## 1. CSS 变量品牌化

最简单的定制方式是在项目的 `myst.yml` 或自定义 CSS 中覆盖 CSS 变量：

```css
/* custom.css — 放在项目目录下 */
:root {
  /* 品牌色 */
  --myst-color-primary: #6366f1;
  --myst-color-primary-hover: #4f46e5;
  --myst-color-link: #6366f1;
  --myst-color-link-hover: #4f46e5;

  /* 字体 */
  --myst-font-body: 'Inter', system-ui, sans-serif;
  --myst-font-heading: 'Inter', system-ui, sans-serif;
  --myst-font-mono: 'JetBrains Mono', monospace;

  /* 内容最大宽度 */
  --myst-content-max-width: 50rem;
}
```

在 `myst.yml` 中引用：

```yaml
site:
  options:
    extra_css:
      - custom.css
```

## 2. 暗色模式定制

```css
/* 默认亮色（可省略，使用内置值） */
:root {
  --myst-color-bg: #ffffff;
  --myst-color-text: #1a1a1a;
}

/* 暗色主题覆盖 */
.dark {
  --myst-color-bg: #0f172a;
  --myst-color-text: #e2e8f0;
  --myst-color-link: #818cf8;
  --myst-color-surface: #1e293b;
  --myst-color-border: #334155;
}
```

## 3. 自定义代码块渲染器

通过 ThemeProvider 的 `renderers` prop 替换代码块组件：

```tsx
import { ThemeProvider } from '@myst-theme/providers';
import { MyST, DEFAULT_RENDERERS } from '@myst-theme/myst-to-react';

// 自定义代码块：添加行号和文件名标签
function CustomCodeBlock({ node, children }) {
  return (
    <div className="custom-code-block">
      {node.filename && (
        <div className="code-filename">{node.filename}</div>
      )}
      <pre data-line-numbers>
        <code className={`language-${node.lang}`}>{children}</code>
      </pre>
    </div>
  );
}

const renderers = {
  ...DEFAULT_RENDERERS,
  code: { base: CustomCodeBlock },
};

export default function MyDocument({ mdast }) {
  return (
    <ThemeProvider renderers={renderers}>
      <MyST ast={mdast} />
    </ThemeProvider>
  );
}
```

## 4. 自定义 Admonition 样式

通过 CSS 类覆盖特定类型的提示框：

```css
/* 自定义 warning 提示框图标 */
.admonition-kind-warning {
  border-left-color: #f59e0b;
  background: linear-gradient(90deg, #fef3c7 0%, transparent 100%);
}

.admonition-kind-warning .admonition-title::before {
  content: '⚠️';
  margin-right: 0.5rem;
}
```

## 5. 站点配置

在 `myst.yml` 中配置 Book 主题选项：

```yaml
site:
  title: "我的技术文档"
  options:
    # 导航栏
    logo: /logo.svg
    logo_text: "My Docs"
    analytics:
      google: G-XXXXXXXX
    # 侧边栏
    sidebar:
      collapse_depth: 2
    # 搜索
    search:
      provider: minisearch
    # 主题切换
    theme:
      default: light
      toggle: true
  nav:
    - title: 指南
      url: /guide
    - title: API
      url: /api
```

## 6. 自定义链接组件

如果嵌入到已有应用中，可以注入自己的路由链接：

```tsx
import { Link as RouterLink } from 'react-router-dom';

<ThemeProvider Link={RouterLink}>
  <MyST ast={mdast} />
</ThemeProvider>
```

所有 MyST 内部链接将使用 `RouterLink` 而非原生 `<a>` 标签。

## 验证

定制完成后，运行以下命令查看效果：

```bash
myst start          # 开发服务器
myst build --html   # 生产构建
```
