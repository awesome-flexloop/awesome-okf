---
type: Concept
title: 核心组件与状态管理
description: 3Blue1Brown.com 的组件架构：Web Components 视频播放器、Jotai 原子状态管理、暗色模式 FOUC 预防、自动目录导航、Heading 锚点系统、React 19 use() API 使用。
tags: [3blue1brown, react, components, jotai, web-components, custom-elements, dark-mode, table-of-contents, react-19]
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

# 核心组件与状态管理

3Blue1Brown.com 的组件体系围绕"轻量、原生、可预测"三个原则设计：约 60 个 TSX 组件按领域共置（F-026），使用 Jotai 原子化状态管理替代 Redux/Zustand/Context API，视频播放器采用 Web Components 而非 React 封装，暗色模式通过内联脚本预防 FOUC。整个组件库没有复杂的抽象层，充分利用浏览器原生能力和 React 19 新特性。

## 核心组件概览

`app/components/` 目录包含约 60 个 TSX 组件文件，按功能可分为五大类（F-026）：

| 分类 | 核心组件 | 用途 |
|------|----------|------|
| **UI 基础** | Button、Card、Dialog、Form、Tabs、Tooltip | 无样式交互组件（基于 Base UI，F-018） |
| **布局** | Header、Footer、Nav、Main、Grid、Container | 页面结构与响应式布局 |
| **媒体** | YouTube、Vimeo、Figure、Image、Canvas、Shader | 视频/图片/3D 内容渲染 |
| **内容** | MathJax、Markdownify、Heading、TableOfContents、Footnote | MDX 内容增强 |
| **交互** | Interactive、Question、FreeResponse、Carousel | 课程交互式演示 |

此外，项目使用 `@phosphor-icons/react: ^2.1.10` 作为图标库（F-020），通过 `<IconContext.Provider>` 统一设置默认 className 为 `"icon"`（F-050）；`@reactuses/core: ^6.4.0` 提供常用 Hooks（F-021），如 `useMutationObserver`、`useEventListener` 等。

## 核心洞察：Custom Elements 视频播放器（I-04）

这是项目最具反常识的设计决策之一：YouTube/Vimeo 播放器**不使用 React 组件封装 SDK**，而是直接使用 `youtube-video-element` 和 `vimeo-video-element` 这两个 Custom Elements（自定义元素，Web Components 标准）（洞察 I-04）。

### 为什么选择 Web Components 而非 React 封装？

React 生态的"默认做法"是用 React 组件包装第三方 UI 库，但 3Blue1Brown 故意选择 Web Components，有三个核心理由：

1. **镜像原生 `<video>` API**：`<youtube-video>` 和 `<vimeo-video>` 完全镜像原生 `<video>` 元素的 API——会用原生 `<video>` 就会用它们，不需要学习新的 React 封装层 API（play/pause/currentTime/poster 等属性和事件完全一致）。

2. **生命周期与 React 无关**：Custom Elements 是浏览器原生标准，其生命周期由浏览器管理，不会因为 React 重渲染导致播放器重新加载或状态丢失。

3. **无依赖、框架无关**：Custom Elements 不依赖 React，可以在任何框架或无框架环境中使用。

### YouTube 组件实现

`YouTube.tsx` 组件是 Custom Elements 集成的典范（F-061~F-066）：

```tsx
// app/components/YouTube.tsx（F-061~F-066）
import "youtube-video-element/react";  // 注册Custom Element
import { useRef } from "react";
import { useVideo } from "./video";
import { useClient } from "~/util/hooks";

type Props = {
  id: string;
  time?: number;
  backlight?: boolean;
} & ComponentProps<"video">;

export default function YouTube({
  id,
  time = 0,
  backlight = false,
  className,
  ...props
}: Props) {
  const ref = useRef<HTMLVideoElement>(null);  // 引用<youtube-video>元素
  const { enabled, playing, play, onPlay } = useVideo(ref);
  
  // SSR时仅输出占位div（F-064）
  if (!useClient()) return <div className={className} />;
  
  const watch = `https://www.youtube.com/watch?v=${id}&t=${time}s`;
  const poster = `https://i.ytimg.com/vi/${id}/maxresdefault.jpg`;
  
  // 未启用时：显示静态缩略图+播放按钮（F-065）
  if (!enabled) {
    return (
      <button className={className} onClick={play}>
        <img src={poster} alt="" />
        <PlayIcon className="white circle" />
      </button>
    );
  }
  
  // 启用后：渲染<youtube-video>自定义元素（F-066）
  return (
    <>
      <youtube-video
        ref={ref}
        className={clsx(className, backlight && playing && "backlight")}
        src={watch}
        poster={poster}
        playsInline
        onPlay={onPlay}
        {...props}
      />
      {backlight && playing && <BacklightSVGFilter />}
    </>
  );
}
```

注意 `useRef<HTMLVideoElement>` 的类型标注——因为 `<youtube-video>` 镜像原生 `<video>` API，所以直接使用 `HTMLVideoElement` 类型即可，不需要自定义类型。

### Vimeo 组件：动态导入与竞态预防

Vimeo 播放器使用动态 `import()` 避免增加初始包体积，并通过 `cancelled` 标志防止竞态条件（F-067）：

```tsx
// app/components/Vimeo.tsx 第43-61行（F-067、F-068）
useEffect(() => {
  let cancelled = false;
  
  import("vimeo-video-element/react").then(() => {
    if (cancelled) return;  // 组件已卸载，不更新状态
    setLoaded(true);
  });
  
  // 获取Vimeo缩略图（F-068）
  fetch(`https://vimeo.com/api/oembed.json?url=${watch}&width=1920&height=1080`)
    .then((res) => res.json())
    .then((data) => {
      if (cancelled) return;
      setPoster(data.thumbnail_url);
    });
  
  return () => { cancelled = true; };
}, [id]);
```

## Jotai 原子化状态管理

项目使用 Jotai `^2.20.2` 作为唯一的全局状态管理方案（F-010），替代了传统的 Redux/Zustand/Context API。Jotai 的原子模型完美适配 3Blue1Brown 的需求：单个状态对应单个原子，不需要 reducer/action/selector 这些仪式感代码，按需订阅不会导致无关组件重渲染。

### 全局原子概览

项目定义了 4 个核心全局原子：

| 原子 | 位置 | 用途 |
|------|------|------|
| `videoPlayingAtom` | `app/components/video.ts` | 跟踪是否有视频正在播放，实现全局互斥 |
| `darkModeAtom` | `app/components/DarkMode.tsx` | 持久化暗模式偏好到 localStorage |
| `headingsAtom` | `app/components/Heading.tsx` | 页面标题列表，供 TableOfContents 自动生成目录 |
| `openAtom` | `app/components/Nav.tsx` | 移动端导航菜单开关状态 |

### 全局播放互斥：一个播放，其他暂停

这是 Jotai 原子模型的经典应用场景（F-069~F-072）：

```ts
// app/components/video.ts（F-069~F-072）
import { atom, useAtomValue, useSetAtom } from "jotai";

// 单个布尔原子：站点是否有任何视频正在播放
export const videoPlayingAtom = atom(false);

// 订阅原子变化，同步到document.documentElement的playing类（F-070）
// 供CSS playing:变体使用
const videoPlayingAtomWithEffect = atom(
  (get) => get(videoPlayingAtom),
  (get, set, value: boolean) => {
    set(videoPlayingAtom, value);
    document.documentElement.classList.toggle("playing", value);
  }
);

// 全局play/stop控制函数（F-071）
export function play() {
  window.dispatchEvent(new CustomEvent("video-play"));
  useSetAtom(videoPlayingAtomWithEffect)(true);
}

export function stop() {
  window.dispatchEvent(new CustomEvent("video-stop"));
  useSetAtom(videoPlayingAtomWithEffect)(false);
}
```

### useVideo Hook：单个视频实例管理

`useVideo` Hook 管理单个视频的完整生命周期：缩略图→播放器切换、自动滚动、全局互斥（F-072）：

```ts
// app/components/video.ts 第50-88行（F-072）
export function useVideo(ref: RefObject<HTMLVideoElement>) {
  const [enabled, setEnabled] = useState(false);
  const [playing, setPlaying] = useState(false);
  const setGlobalPlaying = useSetAtom(videoPlayingAtomWithEffect);
  
  // 播放触发：启用播放器→等待就绪→滚动到视图→播放
  const play = useCallback(async () => {
    setEnabled(true);
    await nextFrame();  // 等待DOM更新
    
    const video = ref.current;
    if (!video) return;
    
    // 滚动到视图中心
    video.scrollIntoView({ behavior: "smooth", block: "center" });
    
    // 等待视频readyState === 4（HAVE_ENOUGH_DATA）
    await new Promise<void>((resolve) => {
      if (video.readyState >= 4) return resolve();
      video.addEventListener("canplaythrough", () => resolve(), { once: true });
    });
    
    await video.play();
    setPlaying(true);
    setGlobalPlaying(true);
  }, [ref, setGlobalPlaying]);
  
  const onPlay = useCallback(() => {
    setPlaying(true);
    setGlobalPlaying(true);
  }, [setGlobalPlaying]);
  
  const onStop = useCallback(() => {
    setPlaying(false);
  }, []);
  
  // 监听全局play/stop事件，实现互斥播放
  useEffect(() => {
    const handleOtherPlay = () => {
      if (!enabled) return;
      ref.current?.pause();  // 其他视频播放时暂停自己
      setPlaying(false);
    };
    
    window.addEventListener("video-play", handleOtherPlay);
    return () => window.removeEventListener("video-play", handleOtherPlay);
  }, [enabled, ref]);
  
  // 卸载时停止播放
  useEffect(() => {
    return () => {
      if (playing) setGlobalPlaying(false);
    };
  }, [playing, setGlobalPlaying]);
  
  return { enabled, playing, play, onPlay, onStop };
}
```

### 暗模式实现：atomWithStorage + FOUC 预防

暗色模式是 Jotai + 浏览器原生能力的另一个优雅实现（F-073~F-076）：

```tsx
// app/components/DarkMode.tsx（F-073~F-076）
import { atomWithStorage } from "jotai/utils";

// 持久化到localStorage，默认false（F-073）
export const darkModeAtom = atomWithStorage("dark-mode", false);

export default function DarkMode() {
  const [dark, setDark] = useAtom(darkModeAtom);
  
  // 同步状态到<html>的dark类（F-074）
  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
  }, [dark]);
  
  // 开发环境快捷键：Ctrl/Cmd/Alt/Shift+D切换（F-075）
  useEffect(() => {
    if (import.meta.env.DEV) {
      const handler = (e: KeyboardEvent) => {
        if (e.key === "d" && (e.ctrlKey || e.mateKey || e.altKey || e.shiftKey)) {
          e.preventDefault();
          setDark(!dark);
        }
      };
      window.addEventListener("keydown", handler);
      return () => window.removeEventListener("keydown", handler);
    }
  }, [dark, setDark]);
  
  return (
    <button onClick={() => setDark(!dark)} aria-label="Toggle dark mode">
      {dark ? <SunIcon /> : <MoonIcon />}
    </button>
  );
}

// FOUC预防内联脚本（F-076）：在HTML解析阶段立即执行
export const load = `
  if (localStorage.getItem("dark-mode") === "true") {
    document.documentElement.classList.add("dark");
  }
`;
```

**FOUC（Flash of Unstyled Content）预防**是关键：在 `root.tsx` 中，暗模式脚本作为内联 `<script>` 在 `<head>` 中立即执行（F-052）：

```tsx
// app/root.tsx 第56行（F-052）
<script dangerouslySetInnerHTML={{ __html: loadDarkMode }} />
```

这行脚本在 React 水合之前就执行，直接读取 localStorage 并添加 `dark` 类，避免了页面加载时先亮后暗的闪烁。`<html>` 标签上设置了 `suppressHydrationWarning` 因为服务端渲染时不知道用户的暗模式偏好（F-051）。

### 移动端导航：openAtom + createPortal

移动端导航菜单使用 Jotai 原子管理开关状态，通过 `createPortal` 渲染到 `document.body` 避免布局问题（F-078、F-079）：

```tsx
// app/components/Nav.tsx（F-077~F-080）
const openAtom = atom(false);  // 移动端菜单开关（F-078）

const NAV_LINKS = [
  { to: "/", label: "Home" },
  { to: "/talent", label: "Talent" },
  { to: "https://patreon.com/3blue1brown", label: "Patreon", external: true },
  { to: "https://store.dftba.com/collections/3blue1brown", label: "Store", external: true },
  { to: "/extras", label: "Extras" },
  { to: "/about", label: "About" },
];  // F-077

export default function Nav() {
  const [open, setOpen] = useAtom(openAtom);
  
  return (
    <>
      {/* 桌面端导航 */}
      <nav className="hidden md:flex">
        {NAV_LINKS.map(/* ... */)}
      </nav>
      
      {/* 移动端汉堡按钮 */}
      <button className="md:hidden" onClick={() => setOpen(true)}>
        <MenuIcon />
      </button>
      
      {/* 移动端菜单：Portal渲染到body（F-079） */}
      {open && createPortal(
        <>
          <div className="fixed inset-0 bg-black/50" onClick={() => setOpen(false)} />
          <aside className="fixed right-0 top-0 h-full w-80 bg-white dark:bg-black">
            {/* 菜单内容 */}
            <button onClick={() => setOpen(false)}><XIcon /></button>
            {NAV_LINKS.map(/* ... */)}
          </aside>
        </>,
        document.body
      )}
      
      {/* 搜索按钮：点击打开Dialog（F-080） */}
      <Dialog>
        <Search dialog close={close} />
      </Dialog>
    </>
  );
}
```

虽然 `openAtom` 只在 Nav 组件内使用，但仍用 Jotai 而非 useState——这是为了未来可能的跨组件共享（比如其他组件触发菜单打开）预留的扩展点。

## 目录导航系统：TableOfContents + Heading

自动生成的目录（Table of Contents, TOC）是内容站点的核心 UX 组件，通过 `headingsAtom` 全局原子实现 Heading 组件和 TOC 组件之间的松耦合通信。

### Heading 组件：自动注册标题

`Heading` 组件是 h1-h4 标签的统一封装，自动完成三件事：生成 ID、注册到全局原子、包裹锚点链接（F-084~F-086）：

```tsx
// app/components/Heading.tsx（F-084~F-086）
export type Heading = {
  element: HTMLElement;
  id: string;
  level: 1 | 2 | 3 | 4;
  content: ReactNode;  // 简化文本，数学元素保留
};

export const headingsAtom = atom<Heading[]>([]);  // F-084

type Props = {
  level: 1 | 2 | 3 | 4;
  id?: string;
  children: ReactNode;
};

export default function Heading({ level, id: propId, children }: Props) {
  const ref = useRef<HTMLHeadingElement>(null);
  const [headings, setHeadings] = useAtom(headingsAtom);
  
  // 自动生成ID：从props传入或slugify(children文本)
  const id = propId || slugify(onlyText(children));
  const Tag = `h${level}` as const;
  
  // 挂载时按DOM文档位置插入headingsAtom，卸载时移除
  useEffect(() => {
    const element = ref.current;
    if (!element) return;
    
    const heading: Heading = { element, id, level, content: simplifyContent(children) };
    
    // 按DOM位置插入（不是按React渲染顺序）
    setHeadings((prev) => {
      const index = prev.findIndex((h) => 
        element.compareDocumentPosition(h.element) & Node.DOCUMENT_POSITION_FOLLOWING
      );
      if (index === -1) return [...prev, heading];
      return [...prev.slice(0, index), heading, ...prev.slice(index)];
    });
    
    return () => {
      setHeadings((prev) => prev.filter((h) => h.id !== id));
    };
  }, [id, children, setHeadings]);
  
  return (
    <Tag ref={ref} id={id}>
      {/* 锚点链接：点击标题可跳转（F-086） */}
      <Link to={`#${id}`} className="contents text-current no-underline">
        {children}
      </Link>
    </Tag>
  );
}
```

`headingsAtom` 的插入顺序不是 React 渲染顺序，而是通过 `compareDocumentPosition` 按实际 DOM 文档位置排序——这确保了即使 MDX 内容中有条件渲染或动态加载的标题，TOC 顺序也与页面视觉顺序一致。

`simplifyContent` 函数会过滤掉数学元素（使用 `isMathElement` 工具函数，F-060），避免 TOC 中显示原始的 LaTeX 代码。

### TableOfContents 组件：可见性计算 + 滚动高亮

`TableOfContents` 组件订阅 `headingsAtom`，根据滚动位置和窗口宽度决定是否显示，并高亮当前活动标题（F-081~F-083）：

```tsx
// app/components/TableOfContents.tsx（F-081~F-083）
export default function TableOfContents() {
  const headings = useAtomValue(headingsAtom);  // F-081
  const [activeId, setActiveId] = useState<string>();
  const tocRef = useRef<HTMLElement>(null);
  
  // 计算TOC可见性（F-082）
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const update = () => {
      // downEnough：滚动超过前一元素（如视频）底部
      const downEnough = window.scrollY > tocRef.current?.offsetTop ?? 0;
      // wideEnough：窗口宽度减去内容宽度的一半能容纳TOC+间距
      const contentWidth = 70 * 16;  // lg断点 = 70rem
      const tocWidth = 240;
      const gap = 48;
      const wideEnough = (window.innerWidth - contentWidth) / 2 >= tocWidth + gap;
      
      setVisible(downEnough && wideEnough && headings.length > 1);
    };
    
    update();
    window.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update);
    return () => {
      window.removeEventListener("scroll", update);
      window.removeEventListener("resize", update);
    };
  }, [headings.length]);
  
  // 滚动时计算当前活动标题（F-083）
  useEffect(() => {
    const onScroll = () => {
      // firstInView：找到第一个顶部在视口上方但底部在视口内的标题
      const firstInView = headings.find((h) => {
        const rect = h.element.getBoundingClientRect();
        return rect.top <= 100 && rect.bottom > 0;
      });
      if (firstInView) setActiveId(firstInView.id);
      
      // 平滑滚动TOC中的活动项到视图中心
      const activeEl = tocRef.current?.querySelector(`[data-id="${activeId}"]`);
      activeEl?.scrollIntoView({ block: "center", behavior: "smooth" });
    };
    
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, [headings, activeId]);
  
  if (!visible) return null;
  
  return (
    <nav ref={tocRef} className="fixed toc-position">
      <h4>Contents</h4>
      <ul>
        {headings.filter(h => h.level >= 2).map((h) => (
          <li key={h.id} data-id={h.id} className={clsx(h.level === 3 && "pl-4", h.id === activeId && "active")}>
            <Link to={`#${h.id}`}>{h.content}</Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}
```

TOC 仅在 h2 及以下标题数量大于 1、窗口足够宽、且滚动过了页面顶部区域时才显示——这是一个典型的"渐进式增强"UX：窄屏或短页面不显示 TOC，避免占用宝贵的屏幕空间。

## React 19 use() API 使用

React 19 的 `use()` API 是消费异步资源的革命性特性，项目在两个关键场景中使用：

### 场景1：课程页面消费异步 MDX

课程详情页直接使用 `use()` 消费 `getFullLesson(id)` 返回的 Promise（F-108）：

```tsx
// app/pages/lessons/Lesson.tsx 第50行（F-108）
export default function Lesson({ loaderData }: Route.ComponentProps) {
  const { id } = loaderData;
  const lesson = use(getFullLesson(id));  // 直接use(Promise)
  const { Component, ...metadata } = lesson;
  
  return (
    <Main className="striped">
      <Component />  {/* MDX组件直接渲染 */}
    </Main>
  );
}
```

不需要 `Suspense` 边界包裹（React Router 框架模式在路由层处理），不需要 `useEffect` + `useState` 的手动状态管理，代码极其简洁。

### Promise 稳定性保证

React `use()` API 要求 Promise 引用稳定——如果每次渲染传入新 Promise，会导致无限循环。`importAssetsAsync` 通过内部 cache 保证这一点（F-093）：

```ts
// app/util/import.ts 第42-79行（F-093）
export function importAssetsAsync<T>(pattern: string) {
  const modules = import.meta.glob<T>(pattern);
  const cache = new Map<string, Promise<T>>();
  
  function getOne(name: string): Promise<T> {
    if (cache.has(name)) {
      return cache.get(name)!;  // 返回缓存的同一个Promise
    }
    const loader = modules[findPath(name)];
    if (!loader) throw new Error(`Module not found: ${name}`);
    const promise = loader();
    cache.set(name, promise);
    return promise;
  }
  
  return [getOne] as const;
}
```

### 场景2：路由 loader 数据

React Router 框架模式的 `loader` 函数是异步的，`useLoaderData()` 内部也使用 `use()` 消费 Promise，但框架层已经做了封装，用户代码不需要直接处理。

## 客户端检测与打印适配

两个关键的自定义 Hook 解决 SSR/客户端差异和打印适配问题：

### useClient()：SSR 占位

由于项目设置 `ssr: false`，但 React Router 框架模式仍会在构建时执行一次渲染（SSG），`useClient()` 用于区分构建时渲染和客户端水合（F-122）：

```ts
// app/util/hooks.ts 第115-124行（F-122）
export function useClient() {
  const [client, setClient] = useState(false);
  useEffect(() => setClient(true), []);
  return client;
}
```

Custom Elements（YouTube/Vimeo）、MathJax、Interactive 等依赖浏览器 API 的组件都使用这个 Hook，在构建时渲染占位内容。

### usePrinting()：打印适配

`usePrinting()` 监听 `beforeprint`/`afterprint` 事件，使用 `flushSync` 同步更新状态，组件可在打印时隐藏或调整布局（F-123）：

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

Header、Footer、TableOfContents、视频播放器等组件均标记为 `print:hidden`（通过 Tailwind 自定义工具类实现），打印时自动隐藏，输出干净的内容文档。

## 根组件布局与错误处理

`app/root.tsx` 是应用入口，包含全局布局、滚动逻辑、错误边界等（F-047~F-054）：

```tsx
// app/root.tsx 核心结构（F-047~F-054）
import "~/styles.css";
import "@fontsource-variable/figtree";
import "@fontsource-variable/source-serif-4";
import "@fontsource-variable/sometype-mono";

export default function App() {
  // 路由变化滚动逻辑（F-049）
  // 新页面：等待document.readyState==='complete'后滚动到hash
  // 仅hash变化：平滑滚动
  
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: loadDarkMode }} />
        <Links />
      </head>
      <body>
        <a href="#main" className="skip-link">Skip to content</a>  {/* a11y跳转链接 */}
        <Header />
        <Outlet />  {/* 子路由渲染位置 */}
        <Footer />
        <MathJax />  {/* 数学渲染（返回null，仅副作用） */}
        <ScrollRestoration getKey={(location) => location.pathname} />
        <Scripts />
      </body>
    </html>
  );
}

// 错误边界（F-053）
export function ErrorBoundary() {
  const error = useRouteError();
  return (
    <html>
      <body>
        <h1>Something went wrong</h1>
        <pre>{error.stack}</pre>
        <a href="https://github.com/3b1b/3blue1brown.com/issues/new">Report on GitHub</a>
      </body>
    </html>
  );
}
```

`vite:preloadError` 事件监听处理部署后的旧 chunk 问题——当部署新版本后，用户浏览器中缓存的旧 JS 尝试加载已不存在的 chunk 时，自动强制刷新获取新资源（F-054）。

## 相关概念

- [00 官网技术栈总览](00-website-overview.md)
- [03 MDX内容系统与数学渲染](03-mdx-content-system.md)
- [05 Tailwind v4 CSS-first 样式系统](05-styling-with-tailwind4.md)
- [核心组件路径索引](../references/component-index.md)
