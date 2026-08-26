---
type: Concept
title: Tailwind v4 CSS-first 样式系统
description: 3Blue1Brown.com 的 Tailwind CSS v4 零配置架构：@theme 设计令牌、@custom-variant 自定义状态变体、oklch 颜色系统、CSS 变量驱动的暗色模式、@layer base 全局样式、@utility 自定义工具类。
tags: [3blue1brown, tailwind, tailwind-v4, css, css-first, oklch, dark-mode, design-tokens]
generated: { by: "source-code-to-okf-wiki/e-phase", at: "2026-08-26" }
verified: { by: "", at: "" }
status: draft
stale_after: 2027-08-26
sources:
  - id: facts
    resource: /spec/facts.md
    title: 3Blue1Brown.com 源码事实采集
  - id: insights
    resource: /spec/insights.md
    title: 3Blue1Brown.com 前端架构洞察
---

# Tailwind v4 CSS-first 样式系统

3Blue1Brown.com 采用 Tailwind CSS v4 `^4.3.3` 作为样式方案，完全抛弃了 Tailwind v3 时代的 JS 配置文件（`tailwind.config.js`），采用全新的 **CSS-first 零配置**范式（洞察 I-02）。所有设计令牌、状态变体、工具类都在纯 CSS 文件中定义，没有 JS 运行时开销，暗模式通过 CSS 变量覆盖实现，是 Tailwind v4 CSS-first 架构的教科书级实践。

## 核心洞察：抛弃 tailwind.config.js，CSS-first 零配置（I-02）

Tailwind v3 时代，JS 配置文件是正统——你需要在 `tailwind.config.js` 中定义主题、颜色、字体、断点、插件。Tailwind v4 彻底颠覆了这一模式：**所有配置都在 CSS 中完成**，不需要任何 JS 配置文件（洞察 I-02）。

项目中没有 `tailwind.config.js`，所有样式配置都集中在 `app/styles.css` 一个文件中，通过四个核心指令完成：

| 指令 | 作用 | v3 等价物 |
|------|------|-----------|
| `@import "tailwindcss";` | 导入 Tailwind 核心 | `@tailwind base/components/utilities;` |
| `@theme { ... }` | 定义设计令牌（颜色、字体、断点等） | `tailwind.config.js` 中的 `theme` 字段 |
| `@custom-variant` | 定义自定义状态变体 | `tailwind.config.js` 中的 `variants` + 插件 |
| `@utility` | 定义自定义工具类 | `@layer utilities` + `addUtilities` 插件 |
| `@layer base` | 定义原生元素全局样式 | `@layer base` |

这种 CSS-first 模式的优势是显而易见的：
- **更简单**：不用学 Tailwind 的 JS 配置 API，直接写标准 CSS
- **更强大**：`@custom-variant` 可以定义任意 CSS 选择器作为状态变体
- **无运行时开销**：纯 CSS 定义，没有 JS 配置解析的开销
- **与 CSS 生态无缝衔接**：直接使用 CSS 自定义属性、`@media`、`@supports` 等标准特性

项目通过 `@tailwindcss/vite: ^4.3.3` Vite 插件集成 Tailwind（F-007），插件链顺序中 Tailwind 在 MDX 之后、React Router 之前（F-032）。

## 全局样式入口结构

`app/styles.css` 是唯一的全局样式文件，结构清晰分层（F-094~F-106）：

```css
/* app/styles.css 完整结构（F-094~F-106） */

/* 1. 导入 Tailwind 核心 */
@import "tailwindcss";

/* 2. @theme 设计令牌：重置默认值，定义自定义值 */
@theme {
  --font-weight-*: initial;
  --radius-*: initial;
  --color-*: initial;
  
  /* 自定义断点 */
  --breakpoint-sm: 30rem;
  --breakpoint-md: 55rem;
  --breakpoint-lg: 70rem;
  --breakpoint-xl: 95rem;
  
  /* 字体族 */
  --font-family-serif: "Source Serif 4 Variable", serif;
  --font-family-sans: "Figtree Variable", sans-serif;
  --font-family-mono: "Sometype Mono Variable", monospace;
  
  /* 字重（非标准值） */
  --font-weight-normal: 350;
  --font-weight-medium: 500;
  --font-weight-bold: 600;
  
  /* 阴影（使用CSS变量实现暗模式适配） */
  --shadow-sm: 0 1px 2px var(--color-shadow);
  --shadow-md: 0 4px 6px var(--color-shadow);
  --shadow-lg: 0 10px 15px var(--color-shadow);
  
  /* oklch颜色系统 */
  --color-theme: oklch(65% 0.2 250);
  --color-secondary: oklch(75% 0.15 50);
  /* ... black→white六级灰度、语义色 ... */
}

/* 3. @custom-variant 自定义状态变体 */
@custom-variant dark (&:where(.dark, .dark *));
@custom-variant playing (&:where(.playing *));
@custom-variant hocus (&:is(:hover, :focus-visible));

/* 4. .dark 类颜色覆盖（暗模式） */
.dark {
  --color-black: oklch(98% 0 0);
  --color-white: oklch(15% 0 0);
  /* ... 其他颜色变量覆盖 ... */
  --color-shadow: oklch(0% 0 0 / 0.3);
}

/* 5. @layer base 全局原生元素样式 */
@layer base {
  html { font-family: var(--font-serif); }
  body { display: flex; flex-direction: column; min-height: 100vh; }
  main { flex-grow: 1; }
  /* ... h1-h4、a、button等元素样式 ... */
}

/* 6. @utility 自定义工具类 */
@utility width-sm { --width: 30rem; }
@utility width-md { --width: 55rem; }
@utility width-lg { --width: 70rem; }
@utility width-xl { --width: 95rem; }
@utility width-full { --width: 100%; }
@utility icon { /* 图标尺寸 */ }
@utility playing-fade { /* 播放时淡出效果 */ }
/* ... 其他自定义工具类 ... */
```

## @theme 设计令牌系统

`@theme` 块是 Tailwind v4 的核心，用于定义项目的设计令牌。项目首先重置三类默认值，再定义自定义值（F-095）：

```css
@theme {
  /* 先重置，避免Tailwind默认值干扰（F-095） */
  --font-weight-*: initial;
  --radius-*: initial;
  --color-*: initial;
  
  /* 再定义自定义值 */
}
```

### 自定义断点

项目定义了四个响应式断点，与 Tailwind 默认值不同（F-096）：

| 断点 | 值 | 像素 | Tailwind 默认 | 用途 |
|------|----|------|---------------|------|
| `sm` | `30rem` | 480px | 640px | 手机横屏/小平板 |
| `md` | `55rem` | 880px | 768px | 平板/窄桌面 |
| `lg` | `70rem` | 1120px | 1024px | 标准桌面 |
| `xl` | `95rem` | 1520px | 1280px | 宽屏/大屏 |

注意：项目的断点整体比 Tailwind 默认值**更大**——`md` 是 880px 而非 768px，`lg` 是 1120px 而非 1024px。这是因为 3Blue1Brown 的内容以阅读为主，需要更宽的阅读区域才切换多栏布局。

在模板中使用方式与 Tailwind v3 一致：`md:flex`、`lg:grid-cols-3` 等。

### 字体系统

项目使用三种可变字体（Variable Fonts），通过 `@fontsource-variable` 包导入（F-019、F-097）：

```css
@theme {
  --font-family-serif: "Source Serif 4 Variable", serif;   /* 正文衬线体 */
  --font-family-sans: "Figtree Variable", sans-serif;     /* 标题无衬线体 */
  --font-family-mono: "Sometype Mono Variable", monospace; /* 代码等宽体 */
}
```

字体导入在 `root.tsx` 中完成（F-047）：

```tsx
// app/root.tsx 第2-4行（F-047）
import "@fontsource-variable/figtree";
import "@fontsource-variable/source-serif-4";
import "@fontsource-variable/sometype-mono";
```

字体使用规范：
- **正文**：`font-serif`（Source Serif 4），长文阅读友好
- **标题**：`font-sans`（Figtree），h1-h4 自动应用（F-105）
- **代码/数学**：`font-mono`（Sometype Mono）

### 字重：非标准的 350/500/600

Tailwind 默认字重是 400(normal)/500(medium)/700(bold)，项目使用了更轻的字重（F-098）：

```css
@theme {
  --font-weight-normal: 350;  /* 不是400，更轻的正文 */
  --font-weight-medium: 500;
  --font-weight-bold: 600;    /* 不是700，避免太粗 */
}
```

这是 3Blue1Brown 排版风格的关键：正文使用 350 字重（Light 和 Regular 之间），长文阅读更舒适；标题使用 600 字重（Semibold）而非 700（Bold），视觉上更优雅不突兀。

### 阴影系统：CSS 变量驱动的暗模式适配

阴影使用 `var(--color-shadow)` 变量而非固定颜色，这样暗模式下只需要改变量值即可适配（F-099）：

```css
@theme {
  --shadow-sm: 0 1px 2px var(--color-shadow);
  --shadow-md: 0 4px 6px var(--color-shadow);
  --shadow-lg: 0 10px 15px -3px var(--color-shadow);
}
```

### oklch 颜色系统

项目使用 oklch 色彩空间定义所有颜色，这是 Tailwind v4 推荐的现代颜色系统（F-100）。oklch 比 RGB/HSL 更符合人眼感知，明度（L）、色度（C）、色相（H）三个维度独立调整，更容易创建感知均匀的色板。

```css
@theme {
  /* 品牌主题色 */
  --color-theme: oklch(65% 0.2 250);      /* 3B1B标志性蓝色 */
  --color-secondary: oklch(75% 0.15 50);  /* 橙色/琥珀色，用于强调 */
  
  /* 六级灰度：black→white */
  --color-black: oklch(15% 0 0);
  --color-gray-900: oklch(25% 0 0);
  --color-gray-700: oklch(40% 0 0);
  --color-gray-500: oklch(55% 0 0);
  --color-gray-300: oklch(75% 0 0);
  --color-gray-100: oklch(92% 0 0);
  --color-white: oklch(98% 0 0);
  
  /* 语义色 */
  --color-success: oklch(60% 0.15 145);
  --color-warning: oklch(75% 0.15 85);
  --color-error: oklch(60% 0.2 25);
  
  /* 阴影颜色（黑/白透明度不同） */
  --color-shadow: oklch(0% 0 0 / 0.1);
}
```

oklch 语法说明：`oklch(L C H)`
- **L（Lightness）**：明度，0% 黑 ~ 100% 白
- **C（Chroma）**：色度/饱和度，0 灰度 ~ 0.37 最大鲜艳度
- **H（Hue）**：色相，0 红 → 120 绿 → 240 蓝 → 360 红

## @custom-variant 自定义状态变体

`@custom-variant` 是 Tailwind v4 最强大的新特性之一，允许你定义任意 CSS 选择器作为状态变体。项目定义了三个关键自定义变体（F-101、F-102、F-104）。

### dark 变体：基于 class 的暗色模式

```css
@custom-variant dark (&:where(.dark, .dark *));  /* F-101 */
```

这定义了 `dark:` 前缀变体，匹配 `.dark` 类本身及其所有后代元素。用法：

```tsx
<div className="bg-white dark:bg-black text-black dark:text-white">
  暗模式适配内容
</div>
```

注意：项目**没有使用 Tailwind 内置的 dark 模式策略**（`darkMode: "class"` 或 `"media"`），而是通过 `@custom-variant` 自定义实现——这样更灵活，可以控制选择器的特异性和匹配范围。

### playing 变体：视频播放状态

```css
@custom-variant playing (&:where(.playing *));  /* F-102 */
```

这定义了 `playing:` 变体，匹配 `.playing` 类的后代元素。当有视频正在播放时，`videoPlayingAtom` 会在 `document.documentElement` 上添加 `playing` 类（F-070），此时可以用 `playing:` 前缀调整 UI：

```tsx
<div className="transition-opacity playing:opacity-30">
  视频播放时淡出的内容（如其他文字、导航）
</div>
```

`@utility playing-fade` 工具类就是基于这个变体实现的（F-106）。

### hocus 变体：hover + focus-visible 复合状态

```css
@custom-variant hocus (&:is(:hover, :focus-visible));  /* F-104 */
```

这定义了 `hocus:` 复合变体（hover 或 focus-visible），解决了一个常见的 UX 问题：**可交互元素在鼠标悬停和键盘聚焦时应该有相同的视觉反馈**。

传统写法需要重复两次：
```tsx
<a className="hover:underline focus-visible:underline">链接</a>
```

使用 `hocus:` 变体只需要写一次：
```tsx
<a className="hocus:underline">链接</a>
```

`@layer base` 中的全局链接样式就使用了这个变体：

```css
@layer base {
  a {
    @apply text-theme transition-colors;
  }
  a:any-link {
    @apply hocus:text-secondary;  /* hover或focus时变橙色 */
  }
}
```

## 暗色模式：CSS 变量覆盖策略

项目的暗色模式实现极其优雅——**不是 Tailwind 内置的 dark: 前缀分别定义颜色，而是通过 CSS 变量覆盖**（F-103）：

```css
/* 亮模式默认变量（在@theme中定义） */
@theme {
  --color-black: oklch(15% 0 0);
  --color-white: oklch(98% 0 0);
  --color-shadow: oklch(0% 0 0 / 0.1);  /* 黑色半透明阴影 */
}

/* 暗模式覆盖变量（F-103） */
.dark {
  --color-black: oklch(98% 0 0);  /* 反转：黑变白 */
  --color-white: oklch(15% 0 0);  /* 反转：白变黑 */
  --color-gray-900: oklch(92% 0 0);
  --color-gray-700: oklch(75% 0 0);
  --color-gray-500: oklch(55% 0 0);
  --color-gray-300: oklch(40% 0 0);
  --color-gray-100: oklch(25% 0 0);
  
  /* 主题色和语义色变浅（在暗背景上更可读） */
  --color-theme: oklch(75% 0.18 250);
  --color-secondary: oklch(80% 0.15 50);
  
  /* 阴影改为白色半透明 */
  --color-shadow: oklch(100% 0 0 / 0.2);
}
```

这种策略的优势是巨大的：

1. **零重复**：组件不需要写 `bg-white dark:bg-black`，只需要写 `bg-white`，暗模式下 `--color-white` 变量自动指向深色值
2. **一致性**：所有使用 `text-theme`、`bg-white` 等类的地方自动适配暗模式，不需要逐个检查
3. **可维护性**：调整暗模式配色只需要修改 `.dark` 块中的变量，不需要搜索替换所有组件
4. **平滑过渡**：可以给 `html` 添加 `transition: background-color 0.2s, color 0.2s;` 实现亮/暗模式切换的平滑动画

灰度变量是**反转**的：亮模式的 `--color-black`（深灰）在暗模式下变成浅灰，`--color-white`（近白）在暗模式下变成近黑。这意味着语义化的类名（`bg-black`、`text-white`）在两种模式下都符合直觉。

### FOUC 预防的 CSS 配合

暗模式的 `.dark` 类在 HTML 解析阶段就通过内联脚本设置（见 [04 核心组件与状态管理](/concepts/04-components-and-state.md)），这意味着 CSS 加载完成时 `.dark` 类已经存在，不会出现亮/暗闪烁。

## @layer base：全局原生元素样式

`@layer base` 定义原生 HTML 元素的全局样式，不需要工具类即可获得一致的排版（F-105）：

```css
@layer base {
  /* 根元素：衬线体 */
  html {
    font-family: var(--font-family-serif);
  }
  
  /* body：flex纵向布局，footer固定在底部 */
  body {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    @apply bg-white text-black;
  }
  
  /* main：flex-grow填充剩余空间 */
  main {
    flex-grow: 1;
  }
  
  /* section：统一内边距和最大宽度（通过CSS变量控制） */
  section {
    @apply mx-auto px-4 py-12;
    max-width: var(--width, 70rem);  /* 默认lg宽度，可被width-sm/md/lg/xl覆盖 */
  }
  
  /* 标题：居中、无衬线体、字重bold */
  h1, h2, h3, h4 {
    @apply font-sans font-bold text-center;
  }
  h1 { @apply text-4xl mt-16 mb-8; }
  h2 { @apply text-3xl mt-12 mb-6; }
  h3 { @apply text-2xl mt-8 mb-4; }
  h4 { @apply text-xl mt-6 mb-3; }
  
  /* 链接：主题色、过渡、hocus变橙色 */
  a {
    @apply text-theme transition-colors;
  }
  a:any-link {
    @apply hocus:text-secondary;
  }
  
  /* 按钮：无衬线体 */
  button {
    @apply font-sans;
  }
}
```

### 内容宽度控制：--width CSS 变量

section 的 `max-width` 使用 `var(--width, 70rem)`，这是一个巧妙的模式——通过 `@utility width-sm/md/lg/xl/full` 设置 `--width` 变量来控制内容宽度，而不是给每个 section 加不同的 max-width 类（F-106）。

```tsx
{/* 使用默认宽度（lg:70rem） */}
<section>...</section>

{/* 使用md宽度（55rem） */}
<section className="width-md">...</section>

{/* 使用full宽度 */}
<Main className="striped width-full">...</section>
```

`striped` 类（在 Lesson.tsx 中使用）通过 CSS 选择器实现奇数 section 交替背景色：

```css
main.striped > section:nth-of-type(odd) {
  @apply bg-gray-100 dark:bg-gray-900;
}
```

## @utility 自定义工具类

`@utility` 指令定义可复用的自定义工具类（F-106），等价于 Tailwind v3 的 `@layer utilities` + `addUtilities`。

### 宽度控制工具类

```css
@utility width-sm { --width: 30rem; }
@utility width-md { --width: 55rem; }
@utility width-lg { --width: 70rem; }
@utility width-xl { --width: 95rem; }
@utility width-full { --width: 100%; }
```

这些类不直接设置宽度，而是设置 `--width` CSS 变量，由 `section` 的 `max-width: var(--width)` 消费。这是 CSS 变量实现"主题化"控制的经典模式。

### icon 工具类

统一图标尺寸（Phosphor 图标通过 IconContext 默认应用 `icon` 类，F-050）：

```css
@utility icon {
  width: 1.5rem;
  height: 1.5rem;
  vertical-align: middle;
}
```

### trim 工具类

使用 CSS `text-box-trim` 裁剪文本上下边距，实现更精确的垂直对齐：

```css
@utility trim {
  text-box: trim-both text;
}
```

### 焦点环工具类

```css
@utility static-ring {
  @apply outline outline-2 outline-offset-2 outline-theme;
}
@utility change-ring {
  @apply static-ring outline-transparent transition-colors hocus:outline-theme;
}
```

`change-ring` 用于按钮/链接等交互元素：默认无轮廓，hover/focus 时显示主题色轮廓，提供清晰的键盘导航反馈。

### playing-fade 工具类

视频播放时淡出其他内容：

```css
@utility playing-fade {
  @apply transition-opacity;
  &:not(:has(video)) {
    @apply playing:opacity-20;
  }
}
```

配合 `playing:` 变体，当页面有视频播放时，不包含视频的元素透明度降到 20%，突出正在播放的视频。

### vignette 工具类

径向遮罩效果，用于视频背光或图片边缘柔化：

```css
@utility vignette {
  mask-image: radial-gradient(ellipse at center, black 60%, transparent 100%);
}
```

### 打印相关工具类

```css
@utility print-hidden {
  @media print {
    display: none !important;
  }
}
```

Header、Footer、TableOfContents、视频播放器等组件使用 `print-hidden`，打印时自动隐藏。

## 3B1B 品牌配色

项目的配色方案体现了 3Blue1Brown 的品牌识别：

| 颜色 | oklch 值 | 用途 |
|------|----------|------|
| **Theme 蓝** | `oklch(65% 0.2 250)` | 链接、按钮、品牌标识、强调元素 |
| **Secondary 橙** | `oklch(75% 0.15 50)` | hover/focus 状态、二级强调、赞助者区域背景 |
| **灰度级** | black→white 六级 | 文字、背景、边框 |
| **Success 绿** | `oklch(60% 0.15 145)` | 成功状态、正确答案 |
| **Warning 黄** | `oklch(75% 0.15 85)` | 警告状态 |
| **Error 红** | `oklch(60% 0.2 25)` | 错误状态、错误消息 |

品牌蓝 `oklch(65% 0.2 250)` 是 3Blue1Brown 的标志性颜色——明度 65%（中等亮度）、色度 0.2（饱和度适中）、色相 250（蓝色区域），在亮/暗背景上都有良好的可读性。

## 响应式设计模式

项目的响应式设计遵循几个核心模式：

### 1. 移动优先 + 渐进增强

Tailwind 是移动优先的，所有基础样式针对手机，通过 `md:`、`lg:` 断点渐进增强：

```tsx
{/* 手机：单列；md以上：两列；lg以上：三列 */}
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {lessons.map((lesson) => <Card key={lesson.id} {...lesson} />)}
</div>
```

### 2. 导航：移动端汉堡菜单 + 桌面端横向导航

```tsx
{/* 桌面端显示 */}
<nav className="hidden md:flex gap-6">
  {NAV_LINKS.map(/* ... */)}
</nav>

{/* 移动端显示汉堡按钮 */}
<button className="md:hidden" onClick={openMenu}>
  <MenuIcon className="icon" />
</button>
```

移动端菜单通过 `createPortal` 渲染到 `document.body`，包含半透明遮罩和右侧滑入面板（F-079）。

### 3. TOC：宽屏显示、窄屏隐藏

TableOfContents 组件通过 JS 计算 `wideEnough` 条件（窗口宽度减去内容宽度的一半能容纳 TOC 宽度+间距），仅在宽屏时显示（F-082）。

### 4. 内容宽度：断点控制

```tsx
{/* 首页：xl宽度 */}
<Main className="width-xl">...</Main>

{/* 课程页：lg宽度（默认） */}
<Main className="striped">...</Main>

{/* 博客文章：md宽度（更窄的阅读列宽） */}
<Main className="width-md">...</Main>
```

## @apply 指令使用

项目在 `@layer base` 和 `@utility` 中使用 `@apply` 指令组合工具类，但在 TSX 组件中**几乎不使用 `@apply`**——所有样式都直接在 className 中使用工具类，这是 Tailwind 的推荐实践：

```css
/* ✅ 在CSS文件中使用@apply（全局样式、自定义工具类） */
@layer base {
  h1 {
    @apply font-sans font-bold text-center text-4xl mt-16 mb-8;
  }
}

/* ❌ 不在组件中使用@apply（不提取"组件类"） */
/* 不这样做： */
/* .card { @apply rounded-lg shadow-md p-6 bg-white; } */
/* 而是直接在TSX中写： */
/* <div className="rounded-lg shadow-md p-6 bg-white"> */
```

不使用 `@apply` 提取组件类的原因：
1. **工具类就是组件**：`rounded-lg shadow-md p-6` 本身就是可复用的"样式组件"
2. **避免抽象泄漏**：提取 `.card` 类后，不同卡片需要不同 padding/shadow 时又要覆盖，反而增加复杂度
3. **更好的摇树优化**：未使用的工具类自动被 Tailwind 清除，自定义类不会
4. **搜索友好**：直接在 JSX 中看到所有样式，不需要在 CSS 和 JSX 之间跳转

唯一的例外是 `@layer base` 中的全局原生元素样式和 `@utility` 中的真正可复用工具类。

## 样式系统总结

3Blue1Brown.com 的 Tailwind v4 CSS-first 架构展示了现代 CSS 的最佳实践：

1. **CSS 变量为核心**：所有颜色、宽度、字体都通过 CSS 变量定义，暗模式仅修改变量值
2. **零 JS 配置**：`@theme`、`@custom-variant`、`@utility` 在 CSS 中完成所有配置
3. **oklch 色彩空间**：感知均匀的颜色系统，轻松创建亮/暗模式配色
4. **移动优先**：基础样式针对手机，断点渐进增强
5. **实用工具类优先**：不滥用 `@apply` 提取组件类，直接在 JSX 中组合工具类
6. **自定义变体扩展**：`dark:`、`playing:`、`hocus:` 等变体让状态样式表达更简洁

这套样式系统的代码量极小（`app/styles.css` 仅约 270 行），但支撑了整个站点的视觉设计，且维护成本极低——这正是 Tailwind v4 CSS-first 范式的威力。

## 相关概念

- [00 官网技术栈总览](/concepts/00-website-overview.md)
- [03 MDX内容系统与数学渲染](/concepts/03-mdx-content-system.md)
- [04 核心组件与状态管理](/concepts/04-components-and-state.md)
- [完整技术栈清单](/references/tech-stack.md)
