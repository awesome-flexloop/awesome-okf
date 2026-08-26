---
type: Example
title: Tailwind v4 主题与自定义变体配置
description: 完整可运行示例：从零开始配置 Tailwind v4 的 CSS-first 主题系统，包括 @theme 设计令牌、@custom-variant 自定义状态变体、暗色模式、@layer base 全局样式、@utility 自定义工具类，以及与 Tailwind v3 配置方式的对比。
tags: [3blue1brown, tailwind, tailwind-v4, css, theme, dark-mode, custom-variant, example]
generated: { by: "source-code-to-okf-wiki/e-phase", at: "2026-08-26" }
verified: { by: "", at: "" }
status: draft
stale_after: 2027-08-26
sources:
  - id: facts
    resource: /spec/facts.md
    title: 3Blue1Brown.com 源码事实采集
  - id: concepts-05
    resource: /concepts/05-styling-with-tailwind4.md
    title: Tailwind v4 CSS-first 样式系统
related:
  - /concepts/05-styling-with-tailwind4.md
  - /concepts/06-build-and-deploy.md
---

# Tailwind v4 主题与自定义变体配置

本示例将完整演示如何在项目中配置 Tailwind CSS v4 的 CSS-first 主题系统，包括品牌颜色定义、字体配置、自定义断点、dark/playing/hocus 等自定义变体、暗色模式适配、全局基础样式、自定义工具类等所有核心特性。你将看到 Tailwind v4 如何**完全抛弃 JS 配置文件**，在纯 CSS 中完成所有主题配置（F-094、洞察 I-02）。

## Tailwind v3 vs v4 配置方式对比

在开始之前，先理解 Tailwind v4 带来的范式转变——这是最重要的概念：

| 配置项 | Tailwind v3 方式 | Tailwind v4 CSS-first 方式 |
|--------|------------------|---------------------------|
| **配置文件** | `tailwind.config.js` (JS/TS) | 不需要，直接在 CSS 中配置 |
| **导入核心** | `@tailwind base/components/utilities;` | `@import "tailwindcss";` |
| **主题定义** | `theme: { colors: {...}, fontFamily: {...} }` | `@theme { --color-*: ...; --font-family-*: ...; }` |
| **自定义变体** | `variants` 配置 + 插件 API | `@custom-variant` CSS 指令 |
| **自定义工具类** | `@layer utilities` + `addUtilities` 插件 | `@utility` CSS 指令 |
| **暗色模式** | `darkMode: "class"` 配置 | `@custom-variant dark (...)` 自定义 |
| **颜色系统** | RGB/HSL 静态值 | CSS 变量 + oklch 色彩空间 |
| **暗模式适配** | 每个组件写 `dark:bg-black` | CSS 变量覆盖，组件零改动 |

3Blue1Brown.com 是 Tailwind v4 CSS-first 架构的教科书级实践，所有配置集中在单个 `app/styles.css` 文件中，约 270 行代码（F-094~F-106）。

## 第一步：Vite 集成 Tailwind v4

首先确保安装了正确的依赖（F-007）：

```bash
# 使用 Bun
bun add tailwindcss @tailwindcss/vite

# 或使用 npm
npm install tailwindcss @tailwindcss/vite
```

在 `vite.config.ts` 中注册插件，注意插件链顺序——Tailwind 插件应在 MDX 插件之后、React Router 插件之前（F-032）：

```typescript
// vite.config.ts
import { defineConfig } from "vite";
import { reactRouter } from "@react-router/dev/vite";
import tailwindcss from "@tailwindcss/vite";
import mdxPlugin from "@mdx-js/rollup";

export default defineConfig({
  plugins: [
    mdxPlugin({ /* ... MDX 配置 ... */ }),
    tailwindcss(),  // ← 注册 Tailwind v4 插件
    reactRouter(),
  ],
});
```

## 第二步：创建 app.css 完整示例

创建 `app/app.css`（或项目约定的全局样式入口文件），以下是包含所有核心特性的完整配置：

```css
/* ==========================================================================
   1. 导入 Tailwind CSS v4 核心
   ========================================================================== */
@import "tailwindcss";

/* ==========================================================================
   2. @theme：定义设计令牌（颜色、字体、断点、阴影等）
   ========================================================================== */
@theme {
  /* 先重置 Tailwind 默认值，避免干扰我们的自定义主题（F-095） */
  --font-weight-*: initial;
  --radius-*: initial;
  --color-*: initial;

  /* ------------------------------------------------------------------------
     2.1 自定义响应式断点（F-096）
     注意：这些值整体比 Tailwind 默认值大，适合阅读为主的内容站点
     ------------------------------------------------------------------------ */
  --breakpoint-sm: 30rem;   /* 480px  — 手机横屏/小平板（Tailwind 默认 640px） */
  --breakpoint-md: 55rem;   /* 880px  — 平板/窄桌面（Tailwind 默认 768px） */
  --breakpoint-lg: 70rem;   /* 1120px — 标准桌面（Tailwind 默认 1024px） */
  --breakpoint-xl: 95rem;   /* 1520px — 宽屏/大屏（Tailwind 默认 1280px） */

  /* ------------------------------------------------------------------------
     2.2 字体族（可变字体）（F-097）
     使用 @fontsource-variable 包导入可变字体
     ------------------------------------------------------------------------ */
  --font-family-serif: "Source Serif 4 Variable", Georgia, serif;
  --font-family-sans: "Figtree Variable", system-ui, -apple-system, sans-serif;
  --font-family-mono: "Sometype Mono Variable", "JetBrains Mono", monospace;

  /* ------------------------------------------------------------------------
     2.3 字重（非标准值，更优雅的排版）（F-098）
     ------------------------------------------------------------------------ */
  --font-weight-normal: 350;  /* Light 和 Regular 之间，长文阅读更舒适（不是默认的 400） */
  --font-weight-medium: 500;
  --font-weight-bold: 600;    /* Semibold，避免太粗（不是默认的 700） */

  /* ------------------------------------------------------------------------
     2.4 阴影系统（使用 CSS 变量实现暗模式自动适配）（F-099）
     ------------------------------------------------------------------------ */
  --shadow-sm: 0 1px 2px var(--color-shadow);
  --shadow-md: 0 4px 6px -1px var(--color-shadow);
  --shadow-lg: 0 10px 15px -3px var(--color-shadow);

  /* ------------------------------------------------------------------------
     2.5 oklch 颜色系统（F-100）
     oklch(L C H): L=明度(0%黑~100%白), C=色度(0灰度~0.37最艳), H=色相(0红→120绿→240蓝)
     ------------------------------------------------------------------------ */

  /* 品牌色 */
  --color-theme: oklch(65% 0.2 250);       /* 3B1B 标志性蓝色 */
  --color-secondary: oklch(75% 0.15 50);   /* 橙色/琥珀色，用于强调和 hover 状态 */

  /* 六级灰度：black → white */
  --color-black: oklch(15% 0 0);
  --color-gray-900: oklch(25% 0 0);
  --color-gray-700: oklch(40% 0 0);
  --color-gray-500: oklch(55% 0 0);
  --color-gray-300: oklch(75% 0 0);
  --color-gray-100: oklch(92% 0 0);
  --color-white: oklch(98% 0 0);

  /* 语义色 */
  --color-success: oklch(60% 0.15 145);  /* 绿色：成功、正确答案 */
  --color-warning: oklch(75% 0.15 85);   /* 黄色：警告状态 */
  --color-error: oklch(60% 0.2 25);      /* 红色：错误、失败状态 */

  /* 阴影颜色（亮模式：黑色半透明；暗模式覆盖为白色半透明） */
  --color-shadow: oklch(0% 0 0 / 0.1);
}

/* ==========================================================================
   3. @custom-variant：定义自定义状态变体（F-101、F-102、F-104）
   ========================================================================== */

/* 3.1 dark 变体：基于 class 的暗色模式
   匹配 html.dark 类及其所有后代元素（F-101） */
@custom-variant dark (&:where(.dark, .dark *));

/* 3.2 playing 变体：视频播放状态
   当有视频播放时，documentElement 会添加 .playing 类，
   此时可以用 playing: 前缀调整 UI（如其他内容淡出）（F-102） */
@custom-variant playing (&:where(.playing *));

/* 3.3 hocus 变体：hover + focus-visible 复合状态
   鼠标悬停和键盘聚焦时使用相同样式，避免写两次（F-104） */
@custom-variant hocus (&:is(:hover, :focus-visible));

/* ==========================================================================
   4. .dark 类：暗色模式颜色变量覆盖（F-103）
   核心策略：不是每个组件写 dark:bg-black，而是直接覆盖 CSS 变量！
   组件只写 bg-white，暗模式下 --color-white 自动指向深色值，零重复。
   ========================================================================== */
.dark {
  /* 灰度反转：黑变白、白变黑 */
  --color-black: oklch(98% 0 0);
  --color-gray-900: oklch(92% 0 0);
  --color-gray-700: oklch(75% 0 0);
  --color-gray-500: oklch(55% 0 0);
  --color-gray-300: oklch(40% 0 0);
  --color-gray-100: oklch(25% 0 0);
  --color-white: oklch(15% 0 0);

  /* 主题色和语义色在暗背景上变浅，保证可读性 */
  --color-theme: oklch(75% 0.18 250);
  --color-secondary: oklch(80% 0.15 50);
  --color-success: oklch(70% 0.15 145);
  --color-warning: oklch(80% 0.15 85);
  --color-error: oklch(70% 0.2 25);

  /* 阴影改为白色半透明（暗背景上黑色阴影不可见） */
  --color-shadow: oklch(100% 0 0 / 0.2);
}

/* ==========================================================================
   5. @layer base：全局原生 HTML 元素样式（F-105）
   不需要工具类即可获得一致的排版
   ========================================================================== */
@layer base {
  /* 根元素：衬线体（长文阅读友好） */
  html {
    font-family: var(--font-family-serif);
    scroll-behavior: smooth;
    /* 平滑切换暗模式颜色 */
    transition: background-color 0.2s ease, color 0.2s ease;
  }

  /* body：flex 纵向布局，footer 固定在底部 */
  body {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    @apply bg-white text-black;
    margin: 0;
    line-height: 1.6;
  }

  /* main：flex-grow 填充剩余空间，footer 不会飘在半空 */
  main {
    flex-grow: 1;
  }

  /* section：统一内边距和最大宽度
     最大宽度通过 --width CSS 变量控制，可被 @utility width-sm/md/lg/xl 覆盖 */
  section {
    @apply mx-auto px-4 py-12;
    max-width: var(--width, 70rem); /* 默认 lg 宽度 */
  }

  /* Striped 背景：奇数 section 交替浅灰背景（课程页使用） */
  main.striped > section:nth-of-type(odd) {
    @apply bg-gray-100 dark:bg-gray-900;
  }

  /* 标题：居中、无衬线体、粗字重 */
  h1, h2, h3, h4 {
    @apply font-sans font-bold text-center;
    line-height: 1.3;
  }
  h1 { @apply text-4xl mt-16 mb-8; }
  h2 { @apply text-3xl mt-12 mb-6; }
  h3 { @apply text-2xl mt-8 mb-4; }
  h4 { @apply text-xl mt-6 mb-3; }

  /* 段落：合适的行高和边距 */
  p {
    margin-bottom: 1em;
  }

  /* 链接：主题色、过渡、hocus（hover/focus）变橙色 */
  a {
    @apply text-theme transition-colors duration-200;
    text-decoration-thickness: 1px;
    text-underline-offset: 2px;
  }
  a:any-link {
    @apply hocus:text-secondary;
  }

  /* 按钮：无衬线体、手型光标、过渡 */
  button {
    @apply font-sans cursor-pointer transition-colors duration-200;
  }

  /* 图片：响应式 */
  img {
    max-width: 100%;
    height: auto;
  }

  /* 代码：等宽字体、浅灰背景 */
  code {
    @apply font-mono text-sm bg-gray-100 dark:bg-gray-900 px-1.5 py-0.5 rounded;
  }
  pre code {
    @apply bg-transparent p-0;
  }
  pre {
    @apply font-mono text-sm bg-gray-100 dark:bg-gray-900 p-4 rounded-lg overflow-x-auto my-4;
  }
}

/* ==========================================================================
   6. @utility：自定义工具类（F-106）
   等价于 Tailwind v3 的 @layer utilities
   ========================================================================== */

/* 6.1 内容宽度控制：设置 --width 变量，由 section 的 max-width 消费
   这是一个非常优雅的 CSS 变量模式——组件不直接设置宽度，只改变量 */
@utility width-sm { --width: 30rem; }
@utility width-md { --width: 55rem; }
@utility width-lg { --width: 70rem; }
@utility width-xl { --width: 95rem; }
@utility width-full { --width: 100%; }

/* 6.2 icon：统一图标尺寸（Phosphor 图标默认应用此类） */
@utility icon {
  width: 1.5rem;
  height: 1.5rem;
  vertical-align: middle;
  flex-shrink: 0;
}

/* 6.3 trim：使用 CSS text-box-trim 裁剪文本上下边距，精确垂直对齐 */
@utility trim {
  text-box: trim-both cap alphabetic;
}

/* 6.4 焦点环：键盘导航可见焦点 */
@utility static-ring {
  @apply outline outline-2 outline-offset-2 outline-theme;
}
@utility change-ring {
  @apply outline outline-2 outline-offset-2 outline-transparent transition-colors hocus:outline-theme;
}

/* 6.5 playing-fade：视频播放时淡出其他内容 */
@utility playing-fade {
  @apply transition-opacity duration-300;
  &:not(:has(video, youtube-video, vimeo-video)) {
    @apply playing:opacity-20;
  }
}

/* 6.6 vignette：径向遮罩效果（视频背光、图片边缘柔化） */
@utility vignette {
  mask-image: radial-gradient(ellipse at center, black 50%, transparent 100%);
}

/* 6.7 print-hidden：打印时隐藏（Header、Footer、TOC、视频等） */
@utility print-hidden {
  @media print {
    display: none !important;
  }
}

/* 6.8 prose-reading：阅读优化排版 */
@utility prose-reading {
  @apply font-serif text-lg leading-relaxed;
  p { margin-bottom: 1.25em; }
}
```

## 第三步：在入口文件导入样式

在应用根组件（React Router 框架模式中是 `app/root.tsx`）的最顶部导入样式文件，同时导入可变字体（F-047）：

```tsx
// app/root.tsx
import "~/app.css";  // 全局样式入口，必须第一行导入
import "@fontsource-variable/figtree";
import "@fontsource-variable/source-serif-4";
import "@fontsource-variable/sometype-mono";
import { Links, Meta, Outlet, Scripts, ScrollRestoration } from "react-router";

export function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        {/* 暗模式 FOUC 预防脚本：在 HTML 解析阶段立即设置 dark 类 */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              if (localStorage.getItem('dark-mode') === 'true') {
                document.documentElement.classList.add('dark');
              }
            `,
          }}
        />
        <Meta />
        <Links />
      </head>
      <body>
        {/* 跳转链接（无障碍） */}
        <a href="#main-content" className="sr-only focus:not-sr-only">
          跳转到主要内容
        </a>
        {children}
        <ScrollRestoration />
        <Scripts />
      </body>
    </html>
  );
}

export default function App() {
  return <Outlet />;
}
```

> ⚠️ **FOUC 预防极其重要**：暗模式检测脚本必须内联在 `<head>` 中、在 CSS 加载之前执行，否则页面会先以亮模式渲染一瞬再切换到暗模式，造成"闪烁"（FOUC，Flash of Unstyled Content）。`suppressHydrationWarning` 属性告诉 React 不要因为服务端和客户端的 `class` 属性不一致而警告。

## 第四步：暗色模式切换组件

创建暗模式切换组件，使用 Jotai 持久化状态到 localStorage（F-073~F-076）：

```tsx
// app/components/DarkModeToggle.tsx
import { useAtom } from "jotai";
import { atomWithStorage } from "jotai/utils";
import { Moon, Sun } from "@phosphor-icons/react";

// 持久化到 localStorage 的原子
const darkModeAtom = atomWithStorage("dark-mode", false);

export function DarkModeToggle() {
  const [dark, setDark] = useAtom(darkModeAtom);

  // 同步 dark 类到 html 元素
  useAtomDarkClass(dark);

  // 开发环境快捷键：Ctrl/Cmd + D 切换暗模式
  useDevHotkey(dark, setDark);

  return (
    <button
      onClick={() => setDark(!dark)}
      className="p-2 rounded-lg change-ring"
      aria-label={dark ? "切换到亮色模式" : "切换到暗色模式"}
    >
      {dark ? <Sun className="icon" /> : <Moon className="icon" />}
    </button>
  );
}

// 同步 dark 类副作用
function useAtomDarkClass(dark: boolean) {
  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
  }, [dark]);
}

// 开发环境快捷键
function useDevHotkey(dark: boolean, setDark: (v: boolean) => void) {
  useEffect(() => {
    if (import.meta.env.PROD) return;
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey || e.altKey || e.shiftKey) && e.key === "d") {
        e.preventDefault();
        setDark(!dark);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [dark, setDark]);
}
```

## 第五步：在组件中使用自定义主题 token

配置完成后，你就可以在 JSX/TSX 中使用这些自定义主题了。以下是使用示例：

### 基础颜色与字体

```tsx
export function BrandHeader() {
  return (
    <header className="bg-white dark:bg-gray-900 border-b border-gray-100 dark:border-gray-800">
      <div className="width-lg mx-auto px-4 py-4 flex items-center justify-between">
        {/* logo 使用主题色 */}
        <h1 className="font-sans font-bold text-2xl text-theme m-0">
          3Blue1Brown
        </h1>
        
        {/* 导航链接使用 hocus 变体 */}
        <nav className="flex gap-6 font-sans">
          <a href="/lessons" className="hocus:text-secondary no-underline">
            课程
          </a>
          <a href="/blog" className="hocus:text-secondary no-underline">
            博客
          </a>
          <DarkModeToggle />
        </nav>
      </div>
    </header>
  );
}
```

注意：你**不需要**写 `dark:text-white`、`dark:bg-black`！因为我们用 CSS 变量覆盖策略，`bg-white` 在暗模式下自动使用 `--color-white` 的暗模式值（近黑色）。这是 Tailwind v4 CSS 变量方案最大的优势——零重复。

### 使用自定义变体

```tsx
export function VideoPlayer({ videoId }: { videoId: string }) {
  return (
    <div className="relative">
      {/* 视频容器 */}
      <div className="aspect-video bg-black rounded-lg overflow-hidden">
        <YouTube id={videoId} />
      </div>
      
      {/* 视频播放时，这个说明文字会淡出到 20% 透明度 */}
      <p className="playing-fade text-center text-gray-500 mt-4">
        点击播放按钮开始观看视频
      </p>
      
      {/* 使用 hocus 变体：悬停和聚焦都显示边框 */}
      <button className="change-ring px-4 py-2 bg-theme text-white rounded-lg hocus:bg-secondary">
        全屏
      </button>
    </div>
  );
}
```

### 使用自定义工具类

```tsx
export function LessonPage({ children }: { children: React.ReactNode }) {
  return (
    <Main className="striped width-full">
      {/* 首页使用 xl 宽度 */}
      <section className="width-xl text-center">
        <h1>欢迎来到 3Blue1Brown</h1>
        <p className="prose-reading">
          通过动画和直观理解，让数学变得平易近人。
        </p>
      </section>
      
      {/* 课程正文使用默认 lg 宽度 */}
      <section>
        {children}
      </section>
      
      {/* 博客文章使用更窄的 md 宽度（适合阅读） */}
      {/* <section className="width-md"> */}
    </Main>
  );
}
```

### 响应式布局示例

```tsx
export function LessonGrid({ lessons }: { lessons: Lesson[] }) {
  return (
    <section>
      <h2>所有课程</h2>
      {/* 手机：1列；md(880px)以上：2列；lg(1120px)以上：3列 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {lessons.map((lesson) => (
          <article
            key={lesson.id}
            className="rounded-lg shadow-md bg-white dark:bg-gray-900 overflow-hidden
                       hocus:shadow-lg transition-shadow"
          >
            <img src={lesson.thumbnail} alt={lesson.title} className="w-full aspect-video object-cover" />
            <div className="p-4">
              <h3 className="text-left text-xl mt-0 mb-2">{lesson.title}</h3>
              <p className="text-gray-500 text-sm m-0">{lesson.description}</p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
```

## 第六步：类型安全的 Tailwind 类名（可选）

使用 `clsx` 库（项目统一使用，F-127）进行条件类名拼接：

```tsx
import clsx from "clsx";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost";
  size?: "sm" | "md" | "lg";
}

export function Button({
  variant = "primary",
  size = "md",
  className,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      className={clsx(
        // 基础样式
        "font-sans font-medium rounded-lg change-ring transition-colors",
        // 尺寸变体
        size === "sm" && "px-3 py-1.5 text-sm",
        size === "md" && "px-4 py-2 text-base",
        size === "lg" && "px-6 py-3 text-lg",
        // 颜色变体（暗模式自动适配！）
        variant === "primary" && "bg-theme text-white hocus:bg-secondary",
        variant === "secondary" && "bg-secondary text-white hocus:bg-theme",
        variant === "ghost" && "bg-transparent text-theme hocus:bg-gray-100 dark:hocus:bg-gray-800",
        // 外部传入的类名
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}
```

> 💡 **项目约定**：使用 `clsx` 而非 `classnames`、`cn`、`cva` 等其他库（F-127）。clsx 轻量、API 直观、性能优秀。

## 运行说明

### 完整配置步骤

```bash
# 1. 安装依赖
bun add tailwindcss @tailwindcss/vite @fontsource-variable/figtree @fontsource-variable/source-serif-4 @fontsource-variable/sometype-mono
bun add -d clsx

# 2. 配置 vite.config.ts（见第二步）
# 3. 创建 app.css（见第二步的完整 CSS）
# 4. 在 root.tsx 导入 CSS 和字体（见第三步）
# 5. 创建 DarkModeToggle 组件（见第四步）
# 6. 在组件中使用主题类名（见第五步）

# 7. 启动开发服务器
bun run dev

# 8. 访问 http://localhost:31415 查看效果
# 9. 按 Ctrl+D（开发环境）或点击切换按钮测试暗模式
```

### 验证 Tailwind 工作正常

创建一个测试页面验证所有功能：

```tsx
// app/routes/test-theme.tsx
export default function TestTheme() {
  return (
    <main className="striped">
      <section className="width-md">
        <h1>Tailwind v4 主题测试</h1>
        
        <h2>颜色测试</h2>
        <div className="flex gap-2 flex-wrap my-4">
          <span className="px-3 py-1 bg-theme text-white rounded">theme</span>
          <span className="px-3 py-1 bg-secondary text-white rounded">secondary</span>
          <span className="px-3 py-1 bg-success text-white rounded">success</span>
          <span className="px-3 py-1 bg-warning text-white rounded">warning</span>
          <span className="px-3 py-1 bg-error text-white rounded">error</span>
        </div>
        
        <h2>灰度测试</h2>
        <div className="flex gap-2 my-4">
          {["black", "gray-900", "gray-700", "gray-500", "gray-300", "gray-100", "white"].map((c) => (
            <span
              key={c}
              className={`px-3 py-1 bg-${c} ${c === "black" || c === "gray-900" || c === "gray-700" ? "text-white" : "text-black"} rounded border border-gray-300`}
            >
              {c}
            </span>
          ))}
        </div>
        
        <h2>自定义工具类</h2>
        <button className="change-ring px-4 py-2 bg-theme text-white rounded-lg hocus:bg-secondary my-2">
          change-ring 焦点环（按 Tab 聚焦测试）
        </button>
        
        <h2>字体测试</h2>
        <p className="font-serif">这是 serif 衬线字体（正文）</p>
        <p className="font-sans">这是 sans 无衬线字体（标题）</p>
        <p className="font-mono">这是 mono 等宽字体（代码）</p>
      </section>
    </main>
  );
}
```

访问 `http://localhost:31415/test-theme`，切换亮/暗模式验证所有颜色正确反转。

## 预期效果

完成配置后，你将获得以下特性：

### 主题系统

1. **品牌色**：3B1B 蓝 `oklch(65% 0.2 250)` 和强调橙 `oklch(75% 0.15 50)` 在全站统一使用
2. **oklch 颜色**：感知均匀的色板，亮/暗模式下都有良好的对比度和可读性
3. **字体系统**：正文 Source Serif 4（衬线）、标题 Figtree（无衬线）、代码 Sometype Mono（等宽）三种可变字体
4. **字重排版**：正文 350 字重、标题 600 字重，长文阅读舒适不刺眼
5. **响应式断点**：sm/md/lg/xl 四个断点，适合内容站点的宽阅读列宽

### 暗色模式

1. **零重复适配**：组件不需要写 `dark:bg-black`，CSS 变量自动适配
2. **无 FOUC**：内联脚本在 HTML 解析阶段就设置 dark 类，页面加载无闪烁
3. **持久化**：用户选择保存在 localStorage，下次访问保持偏好
4. **平滑过渡**：html 元素设置 `transition: background-color 0.2s, color 0.2s`，切换不生硬
5. **开发快捷键**：Ctrl+D 快速切换调试

### 自定义变体

1. **dark:**：暗色模式样式（但我们用 CSS 变量方案，很少需要直接用）
2. **playing:**：视频播放状态，可以让其他内容淡出突出视频
3. **hocus:**：hover + focus-visible 复合，键盘和鼠标交互一致反馈

### 全局基础样式

1. **一致排版**：h1-h4、p、a、button、code、pre 等原生元素有统一的默认样式
2. **Flex 布局**：body flex 纵向布局，footer 自然贴底
3. **Striped 背景**：课程页奇数 section 交替背景色
4. **响应式媒体**：图片、视频、代码块自动响应式

### 自定义工具类

1. **width-sm/md/lg/xl/full**：通过 CSS 变量控制 section 最大宽度
2. **icon**：统一图标尺寸 1.5rem×1.5rem
3. **change-ring/static-ring**：无障碍焦点环
4. **playing-fade**：视频播放时其他内容淡出
5. **vignette**：径向遮罩效果
6. **print-hidden**：打印时隐藏导航、视频等非内容元素

### 构建性能

1. **零运行时开销**：纯 CSS 配置，没有 JS 配置解析
2. **JIT 按需生成**：Tailwind v4 只生成实际使用的 CSS，最终 CSS 体积极小（通常 < 20KB gzipped）
3. **摇树优化**：未使用的工具类自动清除
4. **无配置文件**：不需要维护 `tailwind.config.js`，所有配置在 CSS 中一目了然

## Tailwind v4 vs v3 迁移对照

如果你熟悉 Tailwind v3，下表帮你快速迁移思维：

| 你想做的事 | Tailwind v3 写法 | Tailwind v4 写法 |
|-----------|-----------------|-----------------|
| 定义主色 | `theme: { colors: { primary: '#...' } }` | `@theme { --color-primary: oklch(...); }` |
| 自定义字体 | `theme: { fontFamily: { sans: ['...'] } }` | `@theme { --font-family-sans: '...'; }` |
| 自定义断点 | `theme: { screens: { md: '880px' } }` | `@theme { --breakpoint-md: 55rem; }` |
| 启用 dark 模式 | `darkMode: 'class'` | `@custom-variant dark (&:where(.dark, .dark *));` |
| 自定义工具类 | `addUtilities({...})` 插件 | `@utility name { ... }` |
| 暗色模式适配 | `<div className="bg-white dark:bg-black">` | `<div className="bg-white">` + CSS 变量覆盖 |
| hocus 状态 | `hover:underline focus-visible:underline` | `hocus:underline` |

## 常见问题

### 问题 1：@apply 在组件内不工作

Tailwind v4 的 `@apply` 只能在 CSS 文件（`@layer base`、`@utility`）中使用，不能在 TSX/JSX 的 `<style>` 标签或 CSS-in-JS 中使用。直接在 TSX 的 className 中写工具类即可，这是推荐实践。

### 问题 2：CSS 变量不生效

确保：
1. 变量定义在 `@theme { ... }` 块内
2. 变量名符合 `--color-*`、`--font-family-*`、`--breakpoint-*` 等命名约定
3. 没有拼写错误（`--color-theme` 不是 `--colour-theme`）

### 问题 3：暗模式切换有闪烁

确保内联脚本在 `<head>` 中、在 `<Links />` 和 `<Scripts />` 之前执行，并且 `<html>` 标签有 `suppressHydrationWarning` 属性。

### 问题 4：开发环境 CSS 更新不及时

重启开发服务器，Tailwind v4 的 Vite 插件偶发缓存问题。

### 问题 5：想新增一个颜色怎么办？

只需要在 `@theme` 块加一行，不需要修改任何 JS：

```css
@theme {
  /* 新增紫色主题色 */
  --color-purple: oklch(60% 0.2 300);
}
```

然后直接在 JSX 中使用 `bg-purple`、`text-purple`、`border-purple` 等所有 Tailwind 颜色工具类。

## 扩展建议

基于这个基础配置，你可以轻松扩展：

1. **更多颜色**：在 `@theme` 中添加 `--color-info`、`--color-brand-100` 等色阶
2. **动画**：`@theme { --animate-shake: shake 0.5s ease-in-out; }`
3. **圆角**：先重置 `--radius-*: initial`，再定义 `--radius-sm: 0.25rem; --radius-md: 0.5rem;`
4. **间距**：`@theme { --spacing-section: 8rem; }`，然后用 `p-section`、`gap-section`
5. **更多自定义变体**：`@custom-variant reduced-motion (@media (prefers-reduced-motion: reduce));`
6. **容器查询**：`@custom-variant container-sm (@container (min-width: 40rem));`

Tailwind v4 的 CSS-first 模式的强大之处在于：**你已经知道的所有 CSS 知识都可以直接使用**，不需要学习额外的 JS 配置 API。

## 相关概念

- [05 Tailwind v4 CSS-first 样式系统](/concepts/05-styling-with-tailwind4.md) — Tailwind v4 核心概念、@theme/@custom-variant/@utility 详解、oklch 颜色理论、暗模式策略
- [06 构建系统、包管理与静态部署](/concepts/06-build-and-deploy.md) — Vite 插件链、Tailwind 插件位置、构建配置
- [04 核心组件与状态管理](/concepts/04-components-and-state.md) — Jotai 状态管理、暗模式原子实现
- [创建带数学公式的 MDX 页面](/examples/minimal-mdx-page.md) — 内容创作示例
