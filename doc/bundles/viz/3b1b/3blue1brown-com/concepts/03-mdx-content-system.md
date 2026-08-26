---
type: Concept
title: MDX内容系统与数学渲染
description: 3Blue1Brown.com 的 MDX 内容架构：Vite 插件链配置、frontmatter 元数据系统、两阶段导入性能优化、MathJax 4 双阶段数学渲染、自定义组件映射与课程页面结构。
tags: [3blue1brown, mdx, remark, mathjax, frontmatter, import-meta-glob, performance, react-use]
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

# MDX内容系统与数学渲染

MDX（Markdown + JSX）是 3Blue1Brown.com 的内容核心载体——所有课程视频、博客文章、额外内容都以 `.mdx` 文件形式存储，通过 Vite + Rollup 插件链在构建时转换为 React 组件。项目采用了一套精心设计的**双阶段内容加载**和**双阶段数学渲染**架构，既保证了列表页的极致加载速度，又实现了高质量的数学公式渲染（洞察 I-03、I-05）。

## MDX 在项目中的角色与覆盖范围

3Blue1Brown.com 有三类核心内容使用 MDX 承载（F-028、F-029）：

1. **课程内容（Lessons）**：`app/pages/lessons/20[0-9][0-9]/**/index.mdx`，按年份组织（2015-2019），每个课程是独立文件夹，包含主 MDX 文件、可选的 `patrons.txt` 赞助者名单、以及课程专属的交互式 TSX/JSX 组件（如 Hilbert.tsx、NeuralNetwork.jsx、Fourier.tsx 等）。

2. **博客文章（Blog）**：`app/pages/blog/**/index.mdx`，技术文章、公告等长文内容。

3. **合作伙伴（Talent）**：`app/pages/talent/**/index.mdx`，合作伙伴介绍页面。

此外，部分静态路由直接使用 MDX 文件作为页面组件，如 `/about` 对应 `About.mdx`、`/testbed` 对应 `Testbed.mdx`（F-045）。

## Vite 插件链与 MDX 构建配置

MDX 处理通过 `@mdx-js/rollup` Vite 插件集成，插件链顺序经过精心设计（F-032、F-037）：

```ts
// vite.config.ts 插件链顺序（F-032）
plugins: [
  textReplacePlugin(),    // 自定义前置插件：frontmatter派生属性 + $lesson路径替换
  mdxPlugin(),            // MDX处理：Remark插件链
  tailwindcss(),          // Tailwind v4 Vite插件
  reactRouter(),          // React Router框架模式插件
  svgrPlugin(),           // SVG作为React组件导入
]
```

### Remark 插件链配置

MDX 插件的 Remark 生态插件按以下顺序执行（F-037）：

```ts
// vite.config.ts 第99-109行（F-037）
remarkPlugins: [
  remarkFrontmatter,      // 解析YAML frontmatter
  remarkMdxFrontmatter,   // 将frontmatter导出为MDX组件属性
  remarkMath,             // 解析$...$和$$...$$数学公式标记
  remarkGfm,              // GitHub Flavored Markdown扩展（表格、任务列表等）
  editMDX,                // 自定义插件：修复MDX段落包装问题
],
providerImportSource: "~/components/Markdownify",
```

`providerImportSource` 指定 MDX 运行时使用自定义组件提供者 `~/components/Markdownify`，实现 Markdown 元素到 React 组件的映射（F-087）。

### 自定义插件：editMDX 修复段落包装

MDX 存在一个已知问题（issue #1798）：会为 `<p>`、`<a>`、`<button>`、`<Link>`、`<Button>` 等元素添加多余的段落包装。`editMDX` 插件在构建时遍历 MDX AST 节点，移除这些多余包装（F-036）：

```ts
// vite.config.ts 第85-96行（F-036）
function editMDX() {
  return (tree) => {
    visit(tree, "mdxJsxFlowElement", (node) => {
      // 移除MDX为特定元素添加的多余段落包装
    });
  };
}
```

### 自定义插件：textReplacePlugin 前置处理

`textReplacePlugin` 是一个 `enforce: "pre"` 的前置插件，在 MDX 转换前执行两个关键处理（F-035）：

1. **从 frontmatter 派生属性**：根据 MDX 内容自动计算 `readable`（内容长度 > 500 字符）和 `interactive`（包含 `<Interactive` 标签）两个布尔属性，注入到 frontmatter 中供列表页使用。

2. **`$lesson` 路径替换**：将 MDX 中的 `$lesson` 变量替换为 GCP 存储桶的完整路径（如 `$lesson/figures/linear-transformations.png` → `https://storage.googleapis.com/.../lessons/linear-transformations/figures/...`），实现图片资源的 CDN 加载。

## frontmatter 元数据系统

每个课程 MDX 文件开头必须包含 YAML frontmatter，定义课程元数据（F-116）：

```yaml
---
title: 线性代数的本质
description: 通过几何直观理解线性变换、矩阵、行列式等核心概念
date: 2016-08-13
chapter: 3
video: kjBOsedkmLc
source: _2016/linear-transformations.py
credits:
  - "Manim by Grant Sanderson"
  - "Music by Vincent Rubinetti"
---
```

### frontmatter 类型定义

TypeScript 类型 `RawLessonFrontmatter` 明确定义了所有字段（F-088）：

```ts
// app/pages/lessons/lessons.ts 第8-22行（F-088）
type RawLessonFrontmatter = {
  id: string;
  title: string;
  date: string;           // YYYY-MM-DD格式字符串
  description: string;
  credits: string[];      // "Role by Name"格式字符串数组
  video?: string;         // YouTube视频ID
  source?: string;        // GitHub manim源码路径
  chapter?: number;       // 章序号
  image?: string;
  thumbnail?: string;
  readable?: boolean;     // textReplacePlugin派生：内容长度>500字符
  interactive?: boolean;  // textReplacePlugin派生：包含<Interactive标签
  combinedCredits?: Record<string, string[]>;
};
```

### frontmatter 转换函数

导入后通过 `transformLesson` 函数进行数据标准化（F-089）：

```ts
// app/pages/lessons/lessons.ts 第31-58行（F-089）
function transformLesson(
  path: string,
  { frontmatter }: { frontmatter: RawLessonFrontmatter }
): Lesson {
  return {
    ...frontmatter,
    date: parseDate(frontmatter.date),  // 解析字符串为Date对象
    year: new Date(frontmatter.date).getFullYear(),
    image: frontmatter.video
      ? getThumbnail(frontmatter.video)  // video存在时用YouTube缩略图
      : frontmatter.image,
    combinedCredits: groupCredits(frontmatter.credits),  // 按角色分组
    thumbnail: undefined,  // 清除thumbnail字段
  };
}
```

## 核心洞察：frontmatter 与 MDX 内容分离加载（I-05）

这是项目最关键的性能优化之一。大多数 MDX 站点要么 eager 导入所有 MDX（列表页加载所有内容），要么完全懒加载（列表页需等待所有 MDX 解析）。3Blue1Brown 利用 Vite 的特殊查询参数实现了**两阶段导入**（洞察 I-05）：

### 第一阶段：列表页仅加载 frontmatter

列表页（课程库页面）使用 `query: "frontmatter-only"` 参数，在构建时仅导入所有 MDX 的 frontmatter 元数据，不导入完整内容（F-090）：

```ts
// app/pages/lessons/lessons.ts 第64-71行（F-090）
const lessonModules = import.meta.glob(
  "./20[0-9][0-9]/**/index.mdx",
  { eager: true, query: "frontmatter-only" }  // 关键：仅frontmatter
);

// 转换为Lesson对象数组
export const allLessons = Object.entries(lessonModules)
  .map(([path, module]) => transformLesson(path, module as any))
  .sort((a, b) => b.date.getTime() - a.date.getTime());
```

这一模式的 JS 体积仅几十 KB（元数据），列表页可以瞬间加载完成，不需要等待几 MB 的 MDX 内容解析。

### 第二阶段：详情页懒加载完整 MDX

详情页（课程页面）使用无 `eager` 的 `import.meta.glob` 配合 `importAssetsAsync` 实现按需加载，并通过 React 19 的 `use()` API 消费 Promise（F-091、F-108）：

```ts
// app/pages/lessons/lessons.ts 第42-46行（F-091）
const [getLesson] = importAssetsAsync<{
  default: ComponentType;
  frontmatter: RawLessonFrontmatter;
}>("./20[0-9][0-9]/**/index.mdx");

export function getFullLesson(id: string) {
  return getLesson(id).then((module) => ({
    Component: module.default,
    ...transformLesson(`./${id}/index.mdx`, module),
  }));
}
```

在课程页面组件中直接使用 `use()` 消费（F-108）：

```tsx
// app/pages/lessons/Lesson.tsx 第50行（F-108）
const lesson = use(getFullLesson(id));  // React 19 use() API
```

### importAssets 工具函数封装

`app/util/import.ts` 提供了两个工具函数封装批量导入逻辑（F-092、F-093）：

```ts
// app/util/import.ts（F-092、F-093）

// eager导入：用于frontmatter等元数据
export function importAssets<T>(pattern: string) {
  const modules = import.meta.glob(pattern, { eager: true });
  // 通过nameFromPath提取资源名：index文件取父目录名，否则取文件名
  // slugify标准化名称
  // 返回[getOne函数, all映射]元组
}

// 懒加载导入：用于完整MDX内容
export function importAssetsAsync<T>(pattern: string) {
  const modules = import.meta.glob<T>(pattern);  // 无eager，返回() => Promise
  const cache = new Map<string, Promise<T>>();  // Promise缓存保证稳定性
  
  function getOne(name: string): Promise<T> {
    // 维护cache对象确保Promise引用稳定（React use()要求）
    // 解决import.meta.glob每次调用返回新Promise的问题
  }
  
  return [getOne] as const;
}
```

`importAssetsAsync` 的 Promise 缓存至关重要——React 19 的 `use()` API 要求 Promise 引用稳定，如果每次渲染都传入新 Promise 会导致无限循环。

## 核心洞察：双阶段数学渲染（I-03）

数学公式是 3Blue1Brown 内容的核心。项目没有采用常见的"构建时 KaTeX 渲染为 HTML"方案，而是独创了**"构建时标记 + 运行时 CDN 渲染"**的双阶段策略（洞察 I-03）。

### 构建时：remark-math 仅做标记

构建时 `remark-math` 插件只做一件事：将 `$...$`（行内公式）和 `$$...$$`（块级公式）标记为 `<code class="language-math">` 元素，不做任何实际渲染（F-055）。这带来两个好处：

1. **构建速度极快**：数学公式渲染是 MDX 构建的主要性能瓶颈，跳过这一步可以显著提升构建速度（几十上百个含大量公式的课程页面）。
2. **渲染质量更高**：MathJax 的 SVG 渲染质量优于 KaTeX，尤其是复杂公式（矩阵、积分、分式等）。

### 运行时：MathJax 4 CDN 渲染 SVG

运行时客户端从 CDN 加载 MathJax 4，通过 `MathJax` 组件完成渲染（F-056~F-059）：

```tsx
// app/components/MathJax.tsx（F-055~F-059）
const mathClass = "language-math";
const selector = "code.language-math";  // 匹配remark-math生成的标记

export default function MathJax() {
  // 返回null，不渲染DOM，仅执行副作用
  useEffect(() => {
    // 从CDN加载MathJax 4（F-056）
    // 注释说明：作为npm包导入会导致问题
    const script = document.createElement("script");
    script.src = "https://cdn.jsdelivr.net/npm/mathjax@4/tex-svg.js";
    script.async = true;
    document.head.appendChild(script);
  }, []);
  
  // useMutationObserver监听DOM变化（F-057）
  useMutationObserver(
    document.body,
    () => renderMath(),
    { subtree: true, childList: true }
  );
  
  return null;
}
```

CDN 加载不是"性能倒退"，而是利用浏览器缓存——MathJax 从 jsdelivr CDN 加载后，访问其他同样用 MathJax CDN 的站点会直接命中缓存，首次加载后后续页面无额外开销。

### MathJax 配置

MathJax 初始化时应用了精心调优的配置（F-058）：

```ts
// app/components/MathJax.tsx 第58-83行（F-058）
window.MathJax = {
  svg: { fontCache: "local" },  // 使用本地字体缓存
  loader: { load: ["[tex]/color"] },  // 加载颜色扩展
  tex: {
    macros: {
      degree: "{^\\circ}",  // 自定义\degree宏
    },
    packages: {
      "[+]": ["color"],
      "[-]": ["noundefined"],  // 禁用noundefined包：未定义宏抛出错误而非静默
    },
  },
  startup: {
    typeset: false,  // 禁用自动渲染，手动控制时机
    ready() {
      // 自定义formatError：重命名为MathJaxError并抛出
    },
  },
};
```

禁用 `noundefined` 包是一个重要的质量保障——默认情况下 MathJax 会将未定义的宏（如拼写错误的 `\vecor`）渲染为红色警告文本但不报错，禁用后会直接抛出错误，便于开发时发现问题。

### 渲染函数：同步优先、异步回退

`render` 函数遍历所有数学元素，优先使用同步 `tex2svg`，失败时回退异步 `tex2svgPromise`（F-059）：

```ts
// app/components/MathJax.tsx 第104-137行（F-059）
function render() {
  const elements = document.querySelectorAll(selector);
  for (const el of elements) {
    const isDisplay = el.parentElement?.tagName === "PRE";
    const code = el.textContent || "";
    
    try {
      // 优先同步渲染：性能更好
      const svg = MathJax.tex2svg(code, { display: isDisplay });
      el.replaceWith(svg);
    } catch (e) {
      // 失败回退异步渲染：处理复杂公式
      MathJax.tex2svgPromise(code, { display: isDisplay })
        .then((svg) => el.replaceWith(svg));
    }
  }
}
```

MutationObserver 确保路由切换、懒加载组件等动态内容中的数学公式也能被正确渲染。

### 工具函数：isMathElement

`isMathElement` 工具函数供 Heading 组件过滤 TOC 内容使用——目录中不需要显示数学公式的原始代码（F-060）：

```ts
// app/components/MathJax.tsx 第140-146行（F-060）
export function isMathElement(node: ReactNode): boolean {
  return (
    isElement(node) &&
    typeof node.props.className === "string" &&
    node.props.className.includes(mathClass)
  );
}
```

## MDX 自定义组件映射

`Markdownify.tsx` 通过 `useMDXComponents` 函数定义了 Markdown 元素到自定义 React 组件的映射（F-087）：

```tsx
// app/components/Markdownify.tsx 第38-88行（F-087）
export function useMDXComponents(components: Components) {
  return {
    h1: (props) => <Heading level={1} {...props} />,
    h2: (props) => <Heading level={2} {...props} />,
    h3: (props) => <Heading level={3} {...props} />,
    h4: (props) => <Heading level={4} {...props} />,
    p: (props) => <p {...props} />,  // noParagraph模式下为span
    a: ({ href, children, ...props }) => {
      // 处理脚注引用 → Link组件
      if (href?.startsWith("#fn")) {
        return <Link to={href} {...props}>{children}</Link>;
      }
      return <a href={href} {...props}>{children}</a>;
    },
    blockquote: (props) => <Quote {...props} />,
    section: (props) => {
      // data-footnotes脚注区域 → 视觉隐藏的aside
      if (props["data-footnotes"]) {
        return <aside className="sr-only" {...props} />;
      }
      return <section {...props} />;
    },
    ...components,
  };
}
```

Heading 组件是 MDX 内容的核心——它自动生成 ID、注册到全局 `headingsAtom` 供 TableOfContents 使用，并包裹锚点链接（F-084~F-086）。

## Lesson 课程页面结构

课程详情页 `Lesson.tsx` 是 MDX 内容的渲染容器，结构清晰（F-107~F-115）：

```tsx
// app/pages/lessons/Lesson.tsx 核心结构（F-107~F-115）
export async function loader({ params }: Route.LoaderArgs) {
  return { id: params.id };
}

export default function Lesson({ loaderData }: Route.ComponentProps) {
  const { id } = loaderData;
  const lesson = use(getFullLesson(id));  // React 19 use()消费MDX
  const { Component } = lesson;
  
  return (
    <>
      <Meta />  {/* SEO meta标签 + JSON-LD结构化数据 */}
      <Main className="striped">  {/* 奇数section交替背景色 */}
        <section>
          <h1>{lesson.title}</h1>
          {lesson.video && <YouTube id={lesson.video} />}
          {!lesson.video && lesson.image && <Image image={lesson.image} />}
          <TableOfContents />  {/* 自动目录 */}
        </section>
        <Component />  {/* MDX内容直接渲染 */}
        <section>{/* 前后课程导航 */}</section>
        <section>{/* 赞助者感谢区 */}</section>
      </Main>
    </>
  );
}
```

### MDX 内容编写规范

课程 MDX 文件遵循以下编写规范（F-116~F-121）：

1. **按 section 分段**：内容按 `<section>` 标签分段，每个 section 对应页面中的一个视觉区块，配合 `striped` 类实现奇数/偶数 section 背景交替效果（F-118）。

2. **组件直接导入**：MDX 文件顶部可直接 import TSX 组件，在 Markdown 中以 JSX 方式使用（F-117）：

```mdx
import Figure from "~/components/Figure";
import Question from "~/components/Question";
import PiCreature from "~/components/PiCreature";

## 线性变换的几何意义

<PiCreature emotion="thinking" />

考虑一个二维向量...

<Figure image="$lesson/figures/transform.png" video="$lesson/clips/transform.mp4" />
```

3. **Figure 双模式**：Figure 组件支持图片 + 视频双模式，`image` 属性使用 `$lesson/figures/...` 路径（构建时替换为 GCP 完整 URL），可选 `video` 属性指定 MP4 动画，Tabs 组件提供 Image/Video 切换（F-119）。

4. **Interactive 懒加载**：交互式演示通过 `Interactive` 组件封装，自动懒加载并提供全屏按钮，仅在客户端渲染（F-120）。

5. **PiCreature 表情**：PiCreature 组件通过 `emotion` prop 选择不同的 Pi 生物 SVG 表情（从 `app/assets/pi-creatures/` 加载），用于课程中的对话气泡（F-121）。

### 客户端检测 Hook：useClient()

由于项目禁用 SSR，Custom Elements、MathJax 等浏览器 API 只能在客户端使用。`useClient()` Hook 用于区分 SSR 和客户端渲染（F-122）：

```ts
// app/util/hooks.ts 第115-124行（F-122）
export function useClient() {
  const [client, setClient] = useState(false);
  useEffect(() => setClient(true), []);
  return client;
}
```

YouTube 组件在 SSR 时仅输出占位 div（F-064）：

```tsx
// app/components/YouTube.tsx 第39行（F-064）
if (!useClient()) return <div className={className} />;
```

### 打印适配：usePrinting()

`usePrinting()` Hook 监听打印事件，组件可在打印时调整布局（F-123）：

```ts
// app/util/hooks.ts 第171-177行（F-123）
export function usePrinting() {
  const [printing, setPrinting] = useState(false);
  useEffect(() => {
    const before = () => flushSync(() => setPrinting(true));
    const after = () => flushSync(() => setPrinting(false));
    window.addEventListener("beforeprint", before);
    window.addEventListener("afterprint", after);
    return () => {
      window.removeEventListener("beforeprint", before);
      window.removeEventListener("afterprint", after);
    };
  }, []);
  return printing;
}
```

Header、Footer、TableOfContents、视频播放器等组件均标记为 `print:hidden`，打印时自动隐藏。

## 相关概念

- [00 官网技术栈总览](/concepts/00-website-overview.md)
- [02 路由与 SSG 预渲染](/concepts/02-routing-and-pages.md)
- [04 核心组件与状态管理](/concepts/04-components-and-state.md)
- [05 Tailwind v4 CSS-first 样式系统](/concepts/05-styling-with-tailwind4.md)
- [核心组件路径索引](/references/component-index.md)
