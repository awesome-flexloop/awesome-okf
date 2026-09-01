---
type: spec
title: "3Blue1Brown.com 源码事实采集（R阶段）"
---

# 3Blue1Brown.com 源码事实采集（R阶段）

## 模块概览表

| 模块 | 文件路径 | 核心内容 |
|------|----------|----------|
| 项目配置 | `package.json` | 依赖管理、脚本命令、技术栈声明 |
| 构建配置 | `vite.config.ts` | Vite插件链、MDX处理、路径别名 |
| 路由配置 | `react-router.config.ts` | SSR关闭、预渲染配置、动态路由收集 |
| 路由清单 | `app/routes.ts` | URL路径到页面组件的映射表 |
| 根组件 | `app/root.tsx` | 应用入口、全局布局、错误边界 |
| 全局样式 | `app/styles.css` | Tailwind v4主题定义、自定义工具类 |
| 课程数据 | `app/pages/lessons/lessons.ts` | MDX课程批量导入、frontmatter转换 |
| 主题分类 | `app/pages/lessons/topics.ts` | 课程主题分类、图片资源映射 |
| 课程页面 | `app/pages/lessons/Lesson.tsx` | 课程详情页布局、视频嵌入、前后导航 |
| 数学渲染 | `app/components/MathJax.tsx` | MathJax CDN加载、TeX→SVG转换 |
| 视频播放 | `app/components/YouTube.tsx` | YouTube视频嵌入、静态缩略图懒加载 |
| Vimeo播放 | `app/components/Vimeo.tsx` | Vimeo视频嵌入、API缩略图获取 |
| 视频状态 | `app/components/video.ts` | 全局视频播放状态管理、自定义事件 |
| 暗模式 | `app/components/DarkMode.tsx` | Jotai持久化状态、FOUC预防脚本 |
| 站点导航 | `app/components/Nav.tsx` | 响应式导航、移动端抽屉、搜索入口 |
| 目录组件 | `app/components/TableOfContents.tsx` | 自动生成目录、滚动高亮、侧栏定位 |
| 标题组件 | `app/components/Heading.tsx` | 自动ID生成、标题原子注册、锚点链接 |
| MDX提供者 | `app/components/Markdownify.tsx` | react-markdown包装、自定义组件映射 |
| 图表组件 | `app/components/Figure.tsx` | 图片/视频切换、Tab面板、打印适配 |
| 交互组件 | `app/components/Interactive.tsx` | 懒加载交互演示、全屏控制 |
| 资源导入 | `app/util/import.ts` | import.meta.glob封装、批量资源加载 |
| 通用Hooks | `app/util/hooks.ts` | 客户端检测、打印状态、视口检测等 |

---

## 一、技术栈（package.json）

F-001：`package.json` 第2行设置 `"type": "module"`，项目使用ES Modules规范。

F-002：`package.json` 第4行开发命令为 `react-router dev --open --port 31415`，使用React Router Dev服务器，端口31415，启动时自动打开浏览器。

F-003：`package.json` 第5行构建命令为 `react-router build`，产物输出到 `build/client` 目录（由第6行preview命令 `bunx serve ./build/client -p 31415` 推断）。

F-004：`package.json` 第27行依赖 `@react-router/node: ^8.2.0`，第45行依赖 `react-router: ^8.2.0`，第58行devDependencies依赖 `@react-router/dev: ^8.2.0`，使用React Router v8（对应v7框架模式的后续版本）。

F-005：`package.json` 第40行依赖 `react: ^19.2.7`，第42行依赖 `react-dom: ^19.2.7`，使用React 19。

F-006：`package.json` 第89行devDependencies依赖 `vite: ^8.1.5`，使用Vite 8作为构建工具。

F-007：`package.json` 第86行devDependencies依赖 `tailwindcss: ^4.3.3`，第59行依赖 `@tailwindcss/vite: ^4.3.3`，使用Tailwind CSS v4零配置模式，通过Vite插件集成。

F-008：`package.json` 第56行devDependencies依赖 `@mdx-js/rollup: ^3.1.1`，MDX通过Rollup/Vite插件在构建时处理。

F-009：`package.json` 第80-83行devDependencies依赖Remark生态：`remark-frontmatter: ^5.0.0`（frontmatter解析）、`remark-gfm: ^4.0.1`（GFM扩展）、`remark-math: ^6.0.0`（数学公式解析）、`remark-mdx-frontmatter: ^5.2.0`（MDX frontmatter导出）。

F-010：`package.json` 第38行依赖 `jotai: ^2.20.2`，使用Jotai作为原子化状态管理库。

F-011：`package.json` 第49-50行依赖 `vimeo-video-element: ^1.7.2` 和 `youtube-video-element: ^1.9.0`，使用Custom Elements封装视频播放器，镜像原生`<video>` API。

F-012：`package.json` 第28行依赖 `@react-three/fiber: 9.6.1`，第47行依赖 `three: 0.185.1`，集成Three.js用于3D交互演示。

F-013：`package.json` 第32行依赖 `d3: ^7.9.0`，使用D3.js进行数据可视化。

F-014：`package.json` 第36行依赖 `gsap: ^3.15.0`，使用GSAP动画库。

F-015：`package.json` 第44行依赖 `react-p5: ^1.4.1`，集成p5.js用于创意编码交互。

F-016：`package.json` 第34行依赖 `fuse.js: ^7.5.0`，使用Fuse.js实现模糊搜索。

F-017：`package.json` 第31行依赖 `comlink: ^4.4.2`，使用Comlink简化Web Worker通信。

F-018：`package.json` 第22行依赖 `@base-ui/react: ^1.6.0`，使用Base UI无样式组件库。

F-019：`package.json` 第23-25行依赖三种可变字体：`@fontsource-variable/figtree`（无衬线）、`@fontsource-variable/source-serif-4`（衬线）、`@fontsource-variable/sometype-mono`（等宽）。

F-020：`package.json` 第26行依赖 `@phosphor-icons/react: ^2.1.10`，使用Phosphor图标库。

F-021：`package.json` 第29行依赖 `@reactuses/core: ^6.4.0`，使用ReactUse Hooks工具库。

F-022：`package.json` 第57行devDependencies依赖 `@playwright/test: ^1.61.1`，第53行依赖 `@axe-core/playwright: ^4.12.1`，使用Playwright进行E2E测试和无障碍检测。

---

## 二、目录结构

F-023：项目采用React Router框架模式的`app/`目录约定，而非Next.js的`app/`或传统SPA的`src/`结构。根目录包含`app/`、配置文件、`.github/`、`.vscode/`等。

F-024：`app/`目录下有7个一级子目录：`api/`（客户端API请求）、`assets/`（静态资源）、`components/`（通用组件）、`data/`（顶层站点数据）、`pages/`（按领域组织的页面和内容）、`util/`（通用工具函数）。

F-025：`app/assets/`包含三类资源：`clips/`（7个MP4视频片段：calculus、clacks、eola、fourier-pi、prime-spirals、sphere-area、sudanese-band-loop）、`misc/`（SVG杂项：bubble-speech、bubble-thought）、`pi-creatures/`（50+个Pi生物表情SVG）。

F-026：`app/components/`包含约60个TSX组件文件，覆盖UI基础（Button、Card、Dialog、Form、Tabs、Tooltip等）、布局（Header、Footer、Nav、Main、Grid等）、媒体（YouTube、Vimeo、Figure、Image、Canvas、Shader等）、内容（MathJax、Markdownify、Heading、TableOfContents、Footnote等）、交互（Interactive、Question、FreeResponse、Carousel等）。

F-027：`app/data/`包含3个JSON数据文件：`site.json`（站点元数据、社交链接、GCP配置）、`team.json`（团队成员信息）、`topics.json`（课程主题分类）。

F-028：`app/pages/`按路由领域组织，包含5个主要页面目录：`home/`（首页）、`about/`（关于页）、`lessons/`（课程库，按年份分2015-2019+子目录）、`blog/`（博客文章）、`extras/`（额外内容），以及`NotFound.tsx`（404页）。

F-029：`app/pages/lessons/`下按年份组织课程目录（2015/、2016/、2017/、2018/、2019/），每个课程是独立文件夹，包含`index.mdx`（主内容）、可选的`patrons.txt`（赞助者名单）、可选的自定义TSX/JSX组件（如Hilbert.tsx、NeuralNetwork.jsx、Fourier.tsx等）和数据文件。

F-030：`app/util/`包含11个工具模块：`async.ts`（异步工具：waitFor、sleep、frame）、`atom.ts`（Jotai原子工具）、`dom.ts`（DOM工具：scrollTo、findClosest等）、`download.ts`（下载工具）、`hooks.ts`（自定义React Hooks）、`import.ts`（批量资源导入）、`math.ts`（数学工具）、`misc.ts`（杂项工具：mapEntries）、`string.ts`（字符串工具：slugify、parseDate、formatDate）、`url.ts`（URL工具）、`vector.ts`（向量工具）。

F-031：项目根目录无`public/`文件夹（React Router框架模式约定），静态资源通过`app/assets/`或Vite的资源处理机制导入。

---

## 三、构建配置（vite.config.ts + react-router.config.ts）

F-032：`vite.config.ts` 第16-37行使用`defineConfig`导出配置，插件链顺序为：textReplacePlugin（自定义前置插件）→ mdxPlugin（MDX处理）→ tailwindcss()（Tailwind v4 Vite插件）→ reactRouter()（React Router框架模式插件）→ svgrPlugin（SVG作为React组件导入）。

F-033：`vite.config.ts` 第33-35行配置路径别名`"~/": fileURLToPath(new URL("./app/", import.meta.url))`，配合`tsconfig.json`第32行`"~/*": ["./app/*"]`实现`~/`前缀绝对导入。

F-034：`vite.config.ts` 第32行设置`tsconfigPaths: true`，启用tsconfig路径解析。

F-035：`vite.config.ts` 第40-82行定义自定义`textReplacePlugin`（enforce: "pre"），在MDX文件转换前执行两个处理：①从frontmatter派生`readable`（内容长度>500字符）和`interactive`（包含`<Interactive`标签）属性；②将`$lesson`变量替换为GCP存储桶完整路径（`site.gcp.bucket/lessons/...`）。

F-036：`vite.config.ts` 第85-96行定义`editMDX` Remark插件，遍历`mdxJsxFlowElement`节点，移除MDX为`<p>`、`<a>`、`<button>`、`<Link>`、`<Button>`元素添加的多余段落包装（解决MDX issue #1798）。

F-037：`vite.config.ts` 第99-109行配置MDX插件，Remark插件顺序为：remarkFrontmatter → remarkMdxFrontmatter → remarkMath → remarkGfm → editMDX；`providerImportSource`设为`"~/components/Markdownify"`，即MDX运行时使用自定义组件提供者。

F-038：`vite.config.ts` 第112-120行配置SVGR插件，`expandProps: "start"`（props展开到开头），SVG默认className为`"icon"`（支持props.className覆盖）。

F-039：`react-router.config.ts` 第12行明确设置`ssr: false`，完全禁用服务端渲染，采用预渲染（SSG）+客户端水合模式。

F-040：`react-router.config.ts` 第15-65行定义`prerender`异步函数，通过`import.meta.glob`（eager: true）收集三类动态路由：`/lessons/:id`（匹配`lessons/20[0-9][0-9]/**/index.mdx`）、`/talent/:id`（匹配`talent/**/index.mdx`）、`/blog/:id`（匹配`blog/**/index.mdx`），加上静态路由和`/404`，全部预渲染为静态HTML。

F-041：`react-router.config.ts` 第59-62行将预渲染路由列表写入`./tests/routes.json`，供E2E测试使用。

---

## 四、路由系统（app/routes.ts）

F-042：`app/routes.ts` 第1行从`@react-router/dev/routes`导入`index`和`route`两个路由定义辅助函数。

F-043：`app/routes.ts` 第7行`index("pages/home/Home.tsx")`定义根路径`/`对应首页组件`pages/home/Home.tsx`。

F-044：`app/routes.ts` 第8行`route("lessons/:id", "pages/lessons/Lesson.tsx")`定义动态路由`/lessons/:id`，参数id通过React Router的`useParams`或`Route.ComponentProps`获取，对应课程详情页。

F-045：`app/routes.ts` 第9-14行定义静态路由：`/about`（About.mdx，MDX直接作为路由组件）、`/extras`（Extras.tsx）、`/talent`（Talent.tsx）、`/talent/:id`（Partner.tsx）、`/blog/:id`（Post.tsx）、`/testbed`（Testbed.mdx）、`/sitemap.xml`（sitemap.xml.ts，动态生成站点地图）。

F-046：`app/routes.ts` 第16行`route("*", "pages/NotFound.tsx")`定义通配符路由，匹配所有未命中路径，显示404页面。

---

## 五、根布局与应用入口（app/root.tsx）

F-047：`app/root.tsx` 第1行导入`"~/styles.css"`作为全局样式入口，第2-4行导入三个可变字体CSS。

F-048：`app/root.tsx` 第26行默认导出`App`函数组件，是应用的根组件。

F-049：`app/root.tsx` 第28-47行使用`useLocation`和`useRef`跟踪路由变化，`useEffect`处理滚动逻辑：新页面加载时等待`document.readyState === 'complete'`后滚动到hash；仅hash变化时平滑滚动。

F-050：`app/root.tsx` 第50行使用`<IconContext.Provider value={{ className: "icon" }}>`为所有Phosphor图标设置默认className为`"icon"`。

F-051：`app/root.tsx` 第52-83行渲染完整HTML文档结构：`<html lang="en" suppressHydrationWarning>`（suppressHydrationWarning用于暗模式类名在水合前已设置）、`<head>`包含Analytics、DarkMode内联脚本、charset/viewport meta、`<Links />`；`<body>`包含跳转链接（a11y）、`<Outlet />`（子路由渲染位置）、ViewCorner、Navigate、MathJax、Celebrate、ScrollRestoration（getKey基于pathname，同路径hash变化不恢复滚动）、`<Scripts />`。

F-052：`app/root.tsx` 第56行使用`<script dangerouslySetInnerHTML={{ __html: loadDarkMode }} />`在HTML解析阶段立即执行暗模式检测脚本，避免FOUC（闪烁）。

F-053：`app/root.tsx` 第89-116行导出`ErrorBoundary`错误边界组件，渲染简单的错误提示页面，包含错误堆栈和GitHub issue链接。

F-054：`app/root.tsx` 第119-129行监听`vite:preloadError`事件，当Vite预加载失败（如部署后旧chunk不存在）时，使用sessionStorage去重后强制刷新页面获取新资源。

---

## 六、核心组件

### 数学渲染（MathJax.tsx）

F-055：`app/components/MathJax.tsx` 第7-8行定义mathClass为`"language-math"`，选择器为`code.language-math`，匹配remark-math在构建时生成的数学代码块。

F-056：`app/components/MathJax.tsx` 第12行MathJax从CDN加载：`https://cdn.jsdelivr.net/npm/mathjax@4/tex-svg.js`，注释说明作为npm包导入会导致问题。

F-057：`app/components/MathJax.tsx` 第15-35行默认导出`MathJax`组件，返回null（不渲染DOM），仅在客户端执行副作用：`useEffect`初始化MathJax，`useMutationObserver`监听DOM变化（subtree: true, childList: true），当新增包含数学元素的节点时重新渲染。

F-058：`app/components/MathJax.tsx` 第58-83行MathJax配置：`svg.fontCache: "local"`，加载`[tex]/color`扩展，自定义`\degree`宏为`{^\circ}`，禁用`noundefined`包（未定义宏抛出错误而非静默），`formatError`将错误重命名为MathJaxError并抛出，`startup.typeset: false`（手动控制渲染时机）。

F-059：`app/components/MathJax.tsx` 第104-137行`render`函数遍历所有`code.language-math`元素，判断display模式（父元素是`<pre>`则为块级公式），优先同步调用`tex2svg`，失败回退异步`tex2svgPromise`，将原`<code>`元素替换为生成的SVG。

F-060：`app/components/MathJax.tsx` 第140-146行导出`isMathElement`工具函数，判断React节点是否为数学元素（检查className包含language-math），供Heading组件过滤TOC内容使用。

### 视频播放器（YouTube.tsx / Vimeo.tsx / video.ts）

F-061：`app/components/YouTube.tsx` 第1行静态导入`"youtube-video-element"`（Custom Elements注册），第30行使用`useRef<HTMLVideoElement>`引用自定义元素`<youtube-video>`。

F-062：`app/components/YouTube.tsx` 第13-20行Props类型：`id`（YouTube视频ID）、`time`（起始时间，默认0）、`backlight`（背光效果，默认false），以及原生video元素属性。

F-063：`app/components/YouTube.tsx` 第32行调用`useVideo(ref)`获取视频状态和控制函数：enabled（是否显示真实播放器）、playing（是否播放中）、play（播放触发）、onPlay/onStop（事件回调）。

F-064：`app/components/YouTube.tsx` 第39行`if (!useClient()) return <div className={className} />;`，服务端渲染时仅输出占位div，避免Custom Elements在SSR中不兼容。

F-065：`app/components/YouTube.tsx` 第44-65行未启用时显示静态缩略图按钮：点击触发play()，显示YouTube maxresdefault缩略图，中间有白色圆形Play按钮。

F-066：`app/components/YouTube.tsx` 第68-83行启用后渲染`<youtube-video>`自定义元素，设置src为`https://www.youtube.com/watch?v=${id}&t=${time}s`，poster为缩略图，backlight为true且播放中时应用SVG滤镜背光效果。

F-067：`app/components/Vimeo.tsx` 第43-57行Vimeo库动态`import("vimeo-video-element")`，使用cancelled标志防止竞态条件。

F-068：`app/components/Vimeo.tsx` 第59-61行Vimeo缩略图通过oEmbed API获取：`https://vimeo.com/api/oembed.json?url=${watch}&width=1920&height=1080`。

F-069：`app/components/video.ts` 第10行定义`videoPlayingAtom = atom(false)`全局原子，跟踪站点是否有任何视频正在播放。

F-070：`app/components/video.ts` 第13-18行订阅videoPlayingAtom变化，同步在document.documentElement上添加/移除`playing`类，供CSS `playing:`变体使用。

F-071：`app/components/video.ts` 第21-30行导出`play()`和`stop()`函数，分发自定义事件`video-play`/`video-stop`并更新全局原子。

F-072：`app/components/video.ts` 第50-88行`useVideo` Hook管理单个视频实例：useState(enabled)控制缩略图/播放器切换，play()启用后等待元素就绪→滚动到视图中心→等待readyState===4→播放；onPlay/onStop更新全局原子；监听全局play/stop事件控制其他视频停止；卸载时调用onStop。

### 暗模式（DarkMode.tsx）

F-073：`app/components/DarkMode.tsx` 第9行`darkModeAtom = atomWithStorage("dark-mode", false)`使用Jotai的atomWithStorage持久化到localStorage，默认false。

F-074：`app/components/DarkMode.tsx` 第19-21行useEffect同步darkMode状态到document.documentElement的dark类。

F-075：`app/components/DarkMode.tsx` 第24-28行开发环境下监听Ctrl/Cmd/Alt/Shift+D快捷键切换暗模式。

F-076：`app/components/DarkMode.tsx` 第49-53行导出`load`脚本字符串：`localStorage.getItem("dark-mode") === "true"`时立即在`<html>`上添加dark类，在root.tsx中作为内联脚本执行防止FOUC。

### 导航与目录（Nav.tsx / Header.tsx / Footer.tsx / TableOfContents.tsx）

F-077：`app/components/Nav.tsx` 第18-43行定义导航链接数组：Home(/)、Talent(/talent)、Patreon（外部链接）、Store（外部链接）、Extras(/extras)、About(/about)。

F-078：`app/components/Nav.tsx` 第46行`openAtom = atom(false)`管理移动端菜单展开状态，使用Jotai而非useState以便跨组件共享（但此处仅组件内使用）。

F-079：`app/components/Nav.tsx` 第77-99行移动端菜单使用`createPortal`渲染到document.body，包含半透明遮罩和右侧滑入面板。

F-080：`app/components/Nav.tsx` 第137-146行搜索按钮使用Dialog组件，触发时渲染`<Search dialog close={close} />`组件（从home/Lessons导入）。

F-081：`app/components/TableOfContents.tsx` 第31行`const headings = useAtomValue(headingsAtom)`从全局原子读取页面标题列表。

F-082：`app/components/TableOfContents.tsx` 第46-57行计算TOC可见性：`downEnough`（滚动超过前一元素底部）、`wideEnough`（窗口宽度减去内容宽度的一半能容纳TOC宽度+间距）。

F-083：`app/components/TableOfContents.tsx` 第84-95行滚动时通过`firstInView`计算当前活动标题，平滑滚动TOC中的活动项到视图中心。

### 标题组件（Heading.tsx）

F-084：`app/components/Heading.tsx` 第32行`headingsAtom = atom<Heading[]>([])`全局存储页面所有标题的信息：element（DOM引用）、id、level（1-4）、content（简化文本，数学元素保留）。

F-085：`app/components/Heading.tsx` 第35-90行Heading组件：根据level渲染h1-h4标签，id从props传入或通过slugify(onlyText(children))自动生成，useEffect在挂载时按DOM文档位置插入headingsAtom，卸载时移除。

F-086：`app/components/Heading.tsx` 第84-88行标题内部包裹`<Link to={"#" + id} className="contents text-current no-underline">`，点击标题可跳转锚点。

### MDX内容系统（Markdownify.tsx + lessons.ts + import.ts）

F-087：`app/components/Markdownify.tsx` 第38-88行导出`useMDXComponents`函数（非Hook，命名以use开头是MDX约定），映射markdown元素到自定义组件：h1/h2/h3/h4→Heading组件、p→span（noParagraph模式）或p、a→Link组件（处理脚注引用）、blockquote→Quote组件、section（data-footnotes）→视觉隐藏的aside。

F-088：`app/pages/lessons/lessons.ts` 第8-22行定义RawLessonFrontmatter类型：id、title、date（字符串）、description、credits（字符串数组，格式"Role by Name"）、video（YouTube ID）、source（GitHub源码路径）、chapter（章序号）、image、thumbnail、combinedCredits、readable、interactive。

F-089：`app/pages/lessons/lessons.ts` 第31-58行transformLesson转换函数：解析date字符串为Date对象、提取year、video存在时用YouTube getThumbnail生成图片URL、合并credits为按角色分组的combinedCredits对象、清除thumbnail字段。

F-090：`app/pages/lessons/lessons.ts` 第64-71行通过`import.meta.glob("./20[0-9][0-9]/**/index.mdx", { eager: true, query: "frontmatter-only" })`在构建时仅导入所有课程的frontmatter（不导入完整MDX内容），用于列表页。

F-091：`app/pages/lessons/lessons.ts` 第42-46行getFullLesson通过`import.meta.glob<RawLesson>("./20[0-9][0-9]/**/index.mdx")`（无eager，懒加载）配合importAssetsAsync实现课程内容按需加载，配合React `use()` API消费Promise。

F-092：`app/util/import.ts` 第5-39行importAssets封装eager import.meta.glob：通过nameFromPath提取资源名（index文件取父目录名，否则取文件名），slugify标准化，返回[getOne函数, all映射]元组。

F-093：`app/util/import.ts` 第42-79行importAssetsAsync封装懒加载import.meta.glob：维护cache对象确保Promise稳定性（React `use()`要求），返回getOne函数。

---

## 七、样式系统（app/styles.css + Tailwind v4）

F-094：`app/styles.css` 第1行`@import "tailwindcss";`导入Tailwind CSS v4，无独立tailwind.config文件，采用CSS-first配置方式。

F-095：`app/styles.css` 第5-42行`@theme`块定义主题令牌，先重置`--font-weight-*: initial`、`--radius-*: initial`、`--color-*: initial`清除默认值，再定义自定义值。

F-096：`app/styles.css` 第6-9行自定义断点：sm=30rem(480px)、md=55rem(880px)、lg=70rem(1120px)、xl=95rem(1520px)。

F-097：`app/styles.css` 第11-13行字体族：serif=Source Serif 4 Variable、sans=Figtree Variable、mono=Sometype Mono Variable。

F-098：`app/styles.css` 第16-18行书重：normal=350、medium=500、bold=600（非标准400/500/700）。

F-099：`app/styles.css` 第23-25行阴影：sm/md/lg三级阴影均使用var(--color-shadow)变量实现暗模式适配。

F-100：`app/styles.css` 第28-41行颜色系统使用oklch色彩空间：theme(蓝)、secondary(橙)、black→white六级灰度、success/warning/error语义色、shadow（黑/白透明度不同）。

F-101：`app/styles.css` 第44行`@custom-variant dark (&:where(.dark, .dark *));`定义dark变体，匹配.dark类及其后代。

F-102：`app/styles.css` 第46行`@custom-variant playing (&:where(.playing *));`定义playing变体，匹配.playing类后代，用于视频播放时的UI调整。

F-103：`app/styles.css` 第48-63行`.dark`类覆盖所有颜色变量为暗模式值：灰度反转（black↔white）、主题色和语义色变浅、shadow改为白色半透明。

F-104：`app/styles.css` 第65行`@custom-variant hocus (&:is(:hover, :focus-visible));`定义hocus复合变体（hover或focus-visible）。

F-105：`app/styles.css` 第69-222行`@layer base`定义原生HTML元素全局样式：html使用衬线体、body使用flex纵向布局、main为flex grow、section有统一内边距和max-width约束（通过CSS变量--width和--pad控制）、h1-h4居中使用无衬线体、a标签使用主题色+hocus过渡、按钮使用无衬线体。

F-106：`app/styles.css` 第226-272行`@utility`定义自定义工具类：width-sm/md/lg/xl/full（控制内容最大宽度，通过--width变量）、icon（图标尺寸）、trim（text-box: trim-both text，文本裁剪）、static-ring/change-ring（焦点环）、playing-fade（播放时淡出）、vignette（径向遮罩）。

---

## 八、课程页面结构（Lesson.tsx）

F-107：`app/pages/lessons/Lesson.tsx` 第3行导入`type { Route } from "./+types/Lesson"`，使用React Router框架模式的类型生成（react-router typegen）。

F-108：`app/pages/lessons/Lesson.tsx` 第50行`const lesson = use(getFullLesson(id))`使用React 19的`use()` API直接消费异步import的Promise。

F-109：`app/pages/lessons/Lesson.tsx` 第91-117行使用Meta组件设置SEO meta标签，并通过react-schemaorg注入Article和VideoObject JSON-LD结构化数据。

F-110：`app/pages/lessons/Lesson.tsx` 第121行`<Main className="striped">`使用striped类实现奇数section交替背景色（通过CSS main.striped > section:nth-of-type(odd)选择器）。

F-111：`app/pages/lessons/Lesson.tsx` 第149-153行视频区域：有video时渲染`<YouTube id={video} />`，否则渲染`<Image image={image} />`，打印时隐藏视频。

F-112：`app/pages/lessons/Lesson.tsx` 第205行`<TableOfContents />`在课程头部之后、内容之前放置目录组件。

F-113：`app/pages/lessons/Lesson.tsx` 第208行`<Component />`直接渲染MDX导入的default组件（即MDX内容转换后的React组件）。

F-114：`app/pages/lessons/Lesson.tsx` 第211-249行前后课程导航：使用Card组件展示previous/next课程卡片，三列布局（prev-empty-next）。

F-115：`app/pages/lessons/Lesson.tsx` 第252-272行赞助者感谢区：bg-secondary/10背景，ShowPartial组件控制折叠/展开，按4/3/2/1列网格响应式展示patrons名单。

---

## 九、MDX内容格式与特殊功能

F-116：课程MDX文件使用YAML frontmatter，字段包括title、description、date(YYYY-MM-DD)、chapter(数字)、video(YouTube ID)、source(manim源码路径)、credits(字符串数组)，示例见`app/pages/lessons/2016/linear-transformations/index.mdx`。

F-117：MDX文件中可直接import TSX组件：如第15-19行导入Figure、FreeResponse、LessonLink、PiCreature、Question等自定义组件，在Markdown中以JSX方式使用。

F-118：MDX内容按`<section>`标签分段，每个section对应页面中的一个视觉区块，配合striped背景交替效果。

F-119：Figure组件支持图片+视频双模式，image属性使用`$lesson/figures/...`路径（构建时替换为GCP完整URL），可选video属性指定MP4动画，Tabs组件提供Image/Video切换。

F-120：`app/components/Interactive.tsx`封装懒加载交互演示：接收LazyExoticComponent作为Component prop，自动包裹Suspense（fallback="Browser-only interactive"），提供全屏按钮，客户端检测useClient()通过才渲染。

F-121：`app/components/PiCreature.tsx`组件通过emotion prop选择不同的Pi生物SVG表情（从app/assets/pi-creatures/加载），用于课程中的对话气泡。

F-122：`app/util/hooks.ts` 第115-124行`useClient()` Hook：useState(false) + useEffect(() => setClient(true), [])，用于区分SSR和客户端渲染，返回false时组件渲染占位内容。

F-123：`app/util/hooks.ts` 第171-177行`usePrinting()` Hook：监听beforeprint/afterprint事件，使用flushSync同步更新状态，组件在打印时返回null或调整布局（如Header、Footer、TableOfContents均为print:hidden）。

---

## 十、其他架构特征

F-124：项目采用"按领域共置"（collocate by domain）组织方式：页面相关的组件、图片、数据都放在pages/下对应目录中（如blog/Book.tsx、lessons/.../Hilbert.tsx），而非集中在components/images目录。

F-125：所有内部导入使用`~/`前缀（除同目录colocated文件外），tsconfig.json和vite.config.ts均配置此别名。

F-126：React组件使用`function ComponentName() {}`声明语法，非组件函数使用箭头函数`() => {}`语法（AGENTS.md明确约定）。

F-127：className条件拼接统一使用clsx库（非cn、classnames等）。

F-128：`tsconfig.json` 第23行启用`strict: true`严格模式，第27行`noUncheckedIndexedAccess: true`强制索引访问检查，第25行`erasableSyntaxOnly: true`要求类型标注可擦除。

F-129：项目使用Bun作为首选运行时（README和AGENTS.md说明），但package.json脚本均兼容npm/yarn/node（如bun run、bunx），避免使用Bun专有API。

F-130：部署目标为Netlify（netlify.toml存在），构建产物为静态文件（build/client/），无Node.js服务器运行时依赖。
