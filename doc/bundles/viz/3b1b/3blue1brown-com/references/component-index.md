---
type: Reference
title: 3Blue1Brown.com 核心组件索引
description: 3Blue1Brown.com app/ 目录下所有核心组件的路径索引，按功能分组，标注核心功能与关键 Props。
tags: [3blue1brown, components, index, react, mdx, video, dark-mode, navigation]
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

# 3Blue1Brown.com 核心组件索引

本文档基于 facts.md F-055 ~ F-093，列出 `app/` 目录下核心组件的路径、功能简述与关键 Props。项目采用"按领域共置"（co-location by domain）原则：通用组件放在 `app/components/`，页面特定组件放在对应页面目录下（如 `app/pages/lessons/`、`app/pages/blog/`）（F-124）。

`app/components/` 包含约 60 个 TSX 组件文件（F-026），以下按功能分组索引。

## 一、布局与导航组件

| 组件路径 | 核心功能 | 关键 Props / 说明 | 事实依据 |
|----------|----------|-------------------|----------|
| `app/root.tsx` | 应用根组件，全局布局入口 | 渲染完整 HTML 文档结构，包含 `<Outlet />` 子路由出口、暗模式 FOUC 预防脚本、错误边界、vite:preloadError 自动刷新 | F-047 ~ F-054 |
| `app/components/Nav.tsx` | 站点主导航 | 导航链接：Home(/)/Talent(/talent)/Patreon/Store/Extras(/extras)/About(/about)；Jotai `openAtom` 管理移动端菜单；createPortal 渲染移动端抽屉；搜索按钮触发 Dialog | F-077 ~ F-080 |
| `app/components/Header.tsx` | 页面头部 | 顶部导航栏，包含 Logo、导航链接、暗色模式切换，打印时隐藏（print:hidden） | F-026、F-123 |
| `app/components/Footer.tsx` | 页面底部 | 页脚信息、社交链接、版权声明，打印时隐藏（print:hidden） | F-026、F-123 |
| `app/components/Main.tsx` | 主内容容器 | 统一 main 标签样式与布局约束，配合 `--width`/`--pad` CSS 变量控制宽度 | F-026、F-105 |
| `app/components/Grid.tsx` | 网格布局组件 | 响应式网格布局封装，用于课程列表、赞助者展示等场景 | F-026 |

## 二、媒体播放组件（Custom Elements + 状态管理）

| 组件路径 | 核心功能 | 关键 Props / 说明 | 事实依据 |
|----------|----------|-------------------|----------|
| `app/components/YouTube.tsx` | YouTube 视频播放器 | **Props**: `id`(string, YouTube视频ID)、`time`(number, 起始时间默认0)、`backlight`(boolean, 背光效果默认false)、原生video属性；静态导入 `youtube-video-element` 注册 Custom Element；未启用时显示 maxresdefault 静态缩略图+白色Play按钮；启用后渲染 `<youtube-video>`；SSR 时仅输出占位 div | F-061 ~ F-066 |
| `app/components/Vimeo.tsx` | Vimeo 视频播放器 | 动态 `import("vimeo-video-element")` 避免初始包体积，cancelled 标志防竞态；缩略图通过 oEmbed API 获取；其他逻辑与 YouTube 类似 | F-067 ~ F-068 |
| `app/components/video.ts` | 视频全局状态模块（非组件） | **导出**: `videoPlayingAtom`(Jotai 全局原子，跟踪是否有视频播放)、`play()`/`stop()`(分发自定义事件并更新原子)、`useVideo(ref)` Hook（管理单个视频：enabled 状态、缩略图→播放器切换、自动滚动到视图中心、互斥播放：一个播放时自动停止其他视频）；订阅原子变化同步 `document.documentElement` 的 `playing` 类供 CSS `playing:` 变体使用 | F-069 ~ F-072、I-04 |
| `app/components/Figure.tsx` | 图表/多媒体容器 | 支持图片+视频双模式：`image` 属性使用 `$lesson/figures/...` 路径（构建时替换为 GCP URL），可选 `video` 属性指定 MP4 动画；Tabs 组件提供 Image/Video 切换；打印适配 | F-026、F-119 |
| `app/components/Image.tsx` | 图片组件 | 统一图片渲染，懒加载、响应式处理 | F-026 |
| `app/components/Canvas.tsx` | Canvas 画布组件 | Canvas 2D 渲染封装，用于课程中的自定义可视化 | F-026 |
| `app/components/Shader.tsx` | WebGL 着色器组件 | GLSL 着色器渲染封装，用于高级视觉效果 | F-026 |

## 三、MDX 与内容渲染组件

| 组件路径 | 核心功能 | 关键 Props / 说明 | 事实依据 |
|----------|----------|-------------------|----------|
| `app/components/Markdownify.tsx` | MDX 运行时组件提供者 | 导出 `useMDXComponents` 函数（MDX 约定命名，非 Hook），映射 markdown 元素到自定义组件：h1/h2/h3/h4→Heading、p→span(noParagraph)/p、a→Link(脚注处理)、blockquote→Quote、section(data-footnotes)→视觉隐藏aside；`providerImportSource` 配置指向此组件 | F-037、F-087 |
| `app/components/MathJax.tsx` | 数学公式渲染组件 | **不渲染 DOM**（返回 null），仅客户端副作用；CDN 加载 MathJax 4（`tex-svg.js`）；MutationObserver 监听 DOM 变化；`code.language-math` 选择器匹配 remark-math 标记的公式；display 模式判断（父元素是 `<pre>` 则为块级）；优先同步 `tex2svg`，失败回退异步 `tex2svgPromise`；配置：`svg.fontCache: "local"`、`\degree` 自定义宏、禁用 `noundefined` 包让错误显式抛出；导出 `isMathElement` 工具供 Heading 过滤 TOC | F-055 ~ F-060、I-03 |
| `app/components/Heading.tsx` | 标题组件（自动生成目录） | **全局状态**: `headingsAtom` 存储页面所有标题信息（element/id/level/content）；渲染 h1-h4 标签；id 从 props 传入或 `slugify(onlyText(children))` 自动生成；挂载时按 DOM 位置插入 headingsAtom，卸载时移除；内部包裹 `<Link to={"#" + id}>` 锚点链接；数学元素通过 `isMathElement` 检测保留内容 | F-084 ~ F-086 |
| `app/components/TableOfContents.tsx` | 自动目录组件 | 从 `headingsAtom` 读取标题列表；计算可见性：`downEnough`（滚动超过前一元素）、`wideEnough`（视口宽度足够容纳侧栏）；滚动时通过 `firstInView` 计算当前活动标题，平滑滚动活动项到 TOC 视图中心；打印时隐藏 | F-081 ~ F-083、F-123 |
| `app/components/Footnote.tsx` | 脚注组件 | 脚注引用与回链处理，配合 Markdownify 的 data-footnotes section 映射 | F-026、F-087 |
| `app/components/Quote.tsx` | 引用块组件 | blockquote 自定义样式 | F-026、F-087 |

## 四、暗色模式与主题组件

| 组件路径 | 核心功能 | 关键 Props / 说明 | 事实依据 |
|----------|----------|-------------------|----------|
| `app/components/DarkMode.tsx` | 暗色模式切换 | **状态**: `darkModeAtom = atomWithStorage("dark-mode", false)` 持久化到 localStorage；useEffect 同步 `document.documentElement.dark` 类；开发环境 Ctrl/Cmd/Alt/Shift+D 快捷键切换；导出 `load` 脚本字符串（在 root.tsx 中作为内联 `<script>` 立即执行，读取 localStorage 提前设置 dark 类，防止 FOUC 闪烁） | F-073 ~ F-076 |

## 五、交互与演示组件

| 组件路径 | 核心功能 | 关键 Props / 说明 | 事实依据 |
|----------|----------|-------------------|----------|
| `app/components/Interactive.tsx` | 懒加载交互演示容器 | **Props**: `Component`(LazyExoticComponent，懒加载的交互组件)；自动包裹 Suspense（fallback="Browser-only interactive"）；提供全屏按钮；`useClient()` 检测通过才渲染（SSR 占位） | F-026、F-120 |
| `app/components/Question.tsx` | 问题组件 | 课程中的问答交互封装 | F-026 |
| `app/components/FreeResponse.tsx` | 自由回答组件 | 开放式问题输入与反馈 | F-026 |
| `app/components/Carousel.tsx` | 轮播组件 | 图片/内容轮播展示 | F-026 |
| `app/components/PiCreature.tsx` | Pi 生物表情组件 | **Props**: `emotion`(string，选择不同表情 SVG)；从 `app/assets/pi-creatures/` 加载 50+ 个 Pi 生物 SVG，用于课程对话气泡 | F-025、F-121 |

## 六、UI 基础组件（Base UI 封装）

`app/components/` 下包含约 60 个 TSX 组件，其中 UI 基础组件基于 `@base-ui/react` 无样式组件库自定义样式（F-018、F-026）：

| 组件 | 基于 Base UI | 核心用途 |
|------|-------------|----------|
| `Button.tsx` | Dialog.Trigger 等 | 按钮组件，统一样式与交互 |
| `Card.tsx` | 自定义 | 卡片容器，用于课程前后导航、内容区块 |
| `Dialog.tsx` | Base UI Dialog | 模态对话框，用于搜索、全屏交互等 |
| `Form.tsx` | 自定义 | 表单基础样式 |
| `Tabs.tsx` | Base UI Tabs | 标签页切换，用于 Figure 图片/视频切换 |
| `Tooltip.tsx` | Base UI Tooltip | 工具提示 |
| `Link.tsx` | React Router Link | 路由链接封装，处理外部链接、脚注引用 |
| `ViewCorner.tsx` | 自定义 | 视口角标装饰 |
| `Navigate.tsx` | 自定义 | 导航跳转辅助 |
| `Celebrate.tsx` | 自定义 | 庆祝动画效果 |
| `ShowPartial.tsx` | 自定义 | 折叠/展开控制，用于赞助者名单展示 |
| `LessonLink.tsx` | 自定义 | 课程间链接，位于页面 MDX 中使用 |
| `ScrollRestoration.tsx` | React Router | 滚动位置恢复，getKey 基于 pathname（同路径 hash 变化不恢复滚动） | F-051 |

## 七、页面级组件（pages/ 按领域共置）

页面特定组件不放在 `app/components/`，而是与对应路由页面共置（F-124）：

| 组件路径 | 所属页面 | 核心功能 | 事实依据 |
|----------|----------|----------|----------|
| `app/pages/home/Home.tsx` | 首页 `/` | 根路由首页组件，课程列表、搜索入口 | F-043 |
| `app/pages/home/Lessons.tsx` | 首页 | 课程搜索与列表展示，Fuse.js 模糊搜索 | F-028、F-080 |
| `app/pages/home/Search.tsx` | 首页 | 搜索对话框组件，被 Nav 引用 | F-080 |
| `app/pages/lessons/Lesson.tsx` | 课程详情页 `/lessons/:id` | 课程详情页主组件：使用 React 19 `use(getFullLesson(id))` 消费异步 MDX；Meta 组件设置 SEO + JSON-LD 结构化数据；`<Main className="striped">` 奇数 section 交替背景；YouTube 视频/图片展示；TableOfContents 目录；渲染 MDX Component；前后课程导航 Card；赞助者感谢区 ShowPartial 折叠展示 | F-107 ~ F-115、F-108 |
| `app/pages/lessons/lessons.ts` | 课程数据模块 | 类型：`RawLessonFrontmatter`(id/title/date/description/credits/video/source/chapter等)；`transformLesson()` 转换：解析 date、提取 year、生成 YouTube 缩略图 URL、合并 credits 为 combinedCredits；eager glob 仅导入 frontmatter 用于列表页；懒加载 glob 用于详情页 | F-088 ~ F-091、I-05 |
| `app/pages/lessons/topics.ts` | 课程主题模块 | 课程主题分类、图片资源映射 | F-014 |
| `app/pages/lessons/[year]/[lesson]/` | 单个课程目录 | 每个课程独立文件夹，包含 `index.mdx`（主内容）、可选 `patrons.txt`（赞助者）、可选自定义 TSX/JSX 组件（如 Hilbert.tsx、NeuralNetwork.jsx、Fourier.tsx 等） | F-029 |
| `app/pages/blog/Post.tsx` | 博客详情页 `/blog/:id` | 博客文章详情页，结构类似 Lesson | F-045 |
| `app/pages/blog/Book.tsx` | 博客页特定组件 | 博客页面相关组件（按领域共置示例） | F-124 |
| `app/pages/about/About.mdx` | 关于页 `/about` | MDX 直接作为路由组件，无额外 TSX 包装 | F-045 |
| `app/pages/extras/Extras.tsx` | 额外内容页 `/extras` | 额外资源页面 | F-045 |
| `app/pages/talent/Talent.tsx` | 人才库页 `/talent` | 人才/合作伙伴列表页 | F-045 |
| `app/pages/talent/Partner.tsx` | 合作伙伴详情 `/talent/:id` | 合作伙伴详情页，类似 Lesson 动态路由 | F-045 |
| `app/pages/NotFound.tsx` | 404 页 `*` | 通配符路由匹配，未找到页面展示 | F-046 |
| `app/sitemap.xml.ts` | 站点地图 | 动态生成 sitemap.xml 路由 | F-045 |

## 八、工具 Hooks 与模块（app/util/）

| 模块路径 | 核心功能 | 关键导出 / 说明 | 事实依据 |
|----------|----------|-----------------|----------|
| `app/util/hooks.ts` | 自定义 React Hooks | **`useClient()`**: useState(false) + useEffect 检测客户端渲染，SSR 时返回 false 渲染占位；**`usePrinting()`**: 监听 beforeprint/afterprint，flushSync 同步更新打印状态；其他 Hooks：视口检测、打印状态等 | F-030、F-122、F-123 |
| `app/util/import.ts` | 批量资源导入封装 | **`importAssets`**: 封装 eager import.meta.glob，提取资源名（index 取父目录名）、slugify 标准化，返回 [getOne, all] 元组；**`importAssetsAsync`**: 封装懒加载 glob，维护 cache 对象保证 Promise 稳定性（满足 React `use()` API 要求），返回 getOne | F-092 ~ F-093、I-05 |
| `app/util/atom.ts` | Jotai 原子工具 | Jotai 原子创建与组合辅助函数 | F-030 |
| `app/util/dom.ts` | DOM 工具 | scrollTo、findClosest 等 DOM 操作辅助 | F-030 |
| `app/util/async.ts` | 异步工具 | waitFor、sleep、frame 等异步控制函数 | F-030 |
| `app/util/string.ts` | 字符串工具 | slugify（生成 URL 友好 ID）、parseDate、formatDate 等 | F-030 |
| `app/util/math.ts` | 数学工具 | 数学计算辅助函数 | F-030 |
| `app/util/vector.ts` | 向量工具 | 二维/三维向量运算 | F-030 |
| `app/util/url.ts` | URL 工具 | URL 解析与处理 | F-030 |
| `app/util/download.ts` | 下载工具 | 文件下载触发 | F-030 |
| `app/util/misc.ts` | 杂项工具 | mapEntries 等通用工具 | F-030 |

## 组件命名与编码约定

| 约定项 | 具体规则 | 事实依据 |
|--------|----------|----------|
| 组件声明 | React 组件使用 `function ComponentName() {}` 声明语法 | F-126 |
| 普通函数 | 非组件函数使用箭头函数 `() => {}` 语法 | F-126 |
| className 拼接 | 统一使用 `clsx` 库，禁止 classnames/cn 等 | F-127 |
| 导入路径 | 内部导入使用 `~/` 前缀别名（指向 app/ 目录），同目录共置文件除外 | F-125、F-033 |
| TypeScript | `strict: true` 严格模式，`noUncheckedIndexedAccess: true` 强制索引检查，`erasableSyntaxOnly: true` 类型标注可擦除 | F-128 |

## 相关概念

- [00 官网技术栈总览](/concepts/00-website-overview.md)
- [01 项目结构与目录组织](/concepts/01-project-structure.md)
- [02 路由与 SSG 预渲染](/concepts/02-routing-and-pages.md)
- [完整技术栈清单](/references/tech-stack.md)
