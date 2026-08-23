---
type: Example
title: 自定义主题样式示例
description: 修改品牌色、添加全局 Vue 组件、覆盖默认 CSS 样式和添加动画效果的自定义主题操作示例。
tags: [trae-learning, vitepress, example, custom-theme, vue, css]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/learning-source.md
    title: "Trae Learning 源码信源"
---

# 自定义主题样式示例

本示例演示如何自定义 TRAE Learning 的主题样式和组件。

## 主题扩展机制

TRAE Learning 的主题通过 `.vitepress/theme/index.js` 继承 DefaultTheme 并注册自定义组件：

```js
import DefaultTheme from 'vitepress/theme'
import './custom.css'
import YourComponent from './components/YourComponent.vue'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('YourComponent', YourComponent)
  }
}
```

## 修改品牌色

编辑 `.vitepress/theme/custom.css`，修改 CSS 变量：

```css
:root {
  --brand-color: #0FDC78; /* 修改为你想要的品牌色 */
}
```

同时需要更新所有引用 `#0FDC78` 的地方，包括发光效果、光条、badge 颜色等。

## 添加新的全局组件

1. 在 `.vitepress/theme/components/` 下创建 Vue 组件
2. 在 `index.js` 中导入并通过 `app.component()` 注册
3. 在 Markdown 文件中直接使用组件标签

例如创建一个 `Callout.vue` 提示框组件后，在 Markdown 中使用：

```markdown
<Callout type="tip">
这是一个提示信息。
</Callout>
```

## 覆盖 VitePress 默认样式

在 `custom.css` 中通过更高优先级的选择器覆盖默认样式：

```css
/* 强制暗色背景 */
.VPContent, .VPHome, .VPDoc {
  background: #000000 !important;
}

/* 隐藏不需要的 UI 元素 */
.VPNavBarAppearance {
  display: none;
}
```

## CSS 动画定义

参考项目中的动画模式定义自定义动画：

```css
@keyframes your-animation {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}

.your-class {
  animation: your-animation 0.6s ease-out;
}
```

## 响应式断点

项目使用两个主要响应式断点：

- `@media (max-width: 900px)`：平板布局调整（如隐藏光条）
- `@media (max-width: 768px)`：移动端布局调整（单列布局、调整 padding）

## 相关链接

- [自定义主题开发](/concepts/02-custom-theme.md)
- [VitePress 站点架构](/concepts/01-vitepress-setup.md)
- [本地预览与构建示例](/examples/local-preview.md)
