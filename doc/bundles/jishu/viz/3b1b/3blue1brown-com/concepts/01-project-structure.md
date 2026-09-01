---
type: Concept
title: 项目结构与目录组织
description: 3Blue1Brown.com 完整目录树解析、app/ 目录 React Router 约定、按领域共置原则、关键配置文件职责详解。
tags: [3blue1brown, project-structure, directory, co-location, app-directory, react-router]
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
  - id: tech-stack
    resource: /references/tech-stack.md
    title: 3Blue1Brown.com 完整技术栈清单
  - id: component-index
    resource: /references/component-index.md
    title: 3Blue1Brown.com 核心组件索引
---

# 项目结构与目录组织

3Blue1Brown.com 采用 React Router 框架模式的目录约定，而非 Next.js 的 `app/` 目录或传统 SPA 的 `src/` 结构（F-023）。理解目录组织是阅读源码的第一步——项目严格遵循"按领域共置"（co-location by domain）原则，组件、工具、资源不是按类型集中放置，而是按业务领域就近组织。

## 根目录结构概览

项目根目录包含以下核心内容（F-023）：

```
3blue1brown.com/
├── app/                    # React Router 框架模式约定的应用源码目录
│   ├── api/                # 客户端 API 请求模块
│   ├── assets/             # 静态资源（视频片段、SVG、Pi 生物表情）
│   ├── components/         # 通用可复用组件（约 60 个 TSX 文件）
│   ├── data/               # 顶层站点数据（JSON 配置）
│   ├── pages/              # 按路由领域组织的页面和内容（核心内容区）
│   ├── util/               # 通用工具函数与 Hooks（11 个模块）
│   ├── root.tsx            # 应用根组件、全局布局、错误边界
│   ├── routes.ts           # 路由定义表（URL → 页面组件映射）
│   └── styles.css          # 全局样式入口（Tailwind v4 CSS-first 配置）
├── .github/                # GitHub Actions CI/CD 配置
├── .vscode/                # VS Code 编辑器配置
├── tests/                  # E2E 测试（Playwright）
├── package.json            # 依赖管理与脚本命令
├── vite.config.ts          # Vite 构建配置（插件链、MDX、路径别名、SVGR）
├── react-router.config.ts  # React Router 框架配置（ssr:false、prerender）
├── tsconfig.json           # TypeScript 配置（strict、路径别名）
├── netlify.toml            # Netlify 部署配置
└── README.md               # 项目说明
```

> **注意**：项目根目录**没有**传统 React 项目常见的 `public/` 文件夹（F-031）——这是 React Router 框架模式的约定。静态资源不是放在 `public/` 下通过 URL 直接访问，而是通过 `app/assets/` 目录导入，由 Vite 的资源处理机制在构建时进行 hash 命名和优化。

## app/ 目录详解：React Router 框架模式约定

`app/` 是 React Router 框架模式的核心约定目录，类似于 Next.js 的 `app/` 但更轻量，所有源码都放在这个目录下（F-023、F-024）。

### app/ 的 7 个一级子目录

| 子目录 | 职责 | 详细说明 | 事实依据 |
|--------|------|----------|----------|
| `api/` | 客户端 API 请求 | 封装外部 API 调用（如 Vimeo oEmbed 缩略图获取等） | F-024 |
| `assets/` | 静态资源 | 视频片段、SVG 杂项、Pi 生物表情，通过 Vite 导入处理 | F-025 |
| `components/` | 通用组件 | 跨页面复用的组件，约 60 个 TSX 文件，按 UI/媒体/内容/交互分类 | F-026 |
| `data/` | 顶层站点数据 | 站点元数据、团队信息、主题分类等 JSON 配置文件 | F-027 |
| `pages/` | 页面与内容 | **按路由领域共置**的页面组件、MDX 课程内容、页面特定组件 | F-028 |
| `util/` | 工具函数 | 通用工具模块、自定义 React Hooks，共 11 个 | F-030 |
| 根文件 | 全局入口 | `root.tsx`（根布局）、`routes.ts`（路由表）、`styles.css`（样式） | F-011、F-042、F-094 |

### app/assets/ 静态资源目录

`app/assets/` 包含三类静态资源（F-025），全部通过 ES Module 导入使用，Vite 在构建时处理：

| 子目录 | 资源类型 | 具体内容 |
|--------|----------|----------|
| `clips/` | MP4 视频片段 | 7 个课程配套短循环视频：calculus、clacks、eola、fourier-pi、prime-spirals、sphere-area、sudanese-band-loop |
| `misc/` | SVG 杂项 | bubble-speech（对话气泡）、bubble-thought（思考气泡）等 SVG 图形 |
| `pi-creatures/` | Pi 生物表情 | 50+ 个 Pi 生物 SVG 表情图，通过 `PiCreature` 组件的 `emotion` prop 选择使用 |

资源导入示例：
```tsx
import piCreatureHappy from "~/assets/pi-creatures/happy.svg";
```

### app/data/ 顶层数据目录

包含 3 个 JSON 数据文件，在构建时导入使用（F-027）：

| 文件 | 内容 |
|------|------|
| `site.json` | 站点元数据：标题、描述、社交链接、GCP 存储桶配置（课程资源 CDN） |
| `team.json` | 团队成员信息：姓名、角色、头像等 |
| `topics.json` | 课程主题分类：线性代数、微积分、神经网络等分类与图标映射 |

### app/util/ 工具函数目录

包含 11 个工具模块（F-030），按功能职责拆分：

| 模块文件 | 核心功能 |
|----------|----------|
| `hooks.ts` | 自定义 React Hooks：`useClient()`（客户端检测）、`usePrinting()`（打印状态）等 |
| `import.ts` | 批量资源导入封装：`importAssets`（eager glob）、`importAssetsAsync`（懒加载 glob + Promise 缓存） |
| `atom.ts` | Jotai 原子创建与组合辅助工具 |
| `async.ts` | 异步控制工具：`waitFor`、`sleep`、`frame` 等 |
| `dom.ts` | DOM 操作工具：`scrollTo`、`findClosest` 等 |
| `string.ts` | 字符串处理：`slugify`（生成 URL 友好 ID）、`parseDate`、`formatDate` |
| `math.ts` | 数学计算辅助函数 |
| `vector.ts` | 二维/三维向量运算工具 |
| `url.ts` | URL 解析与处理工具 |
| `download.ts` | 文件下载触发工具 |
| `misc.ts` | 通用杂项：`mapEntries` 等 |

## 核心设计原则：按领域共置（Co-location by Domain）

3Blue1Brown.com 最值得学习的目录设计原则是"按领域共置"——不按"组件/图片/数据/样式"的文件类型分目录，而是按业务路由领域就近组织所有相关文件（F-124、洞察 I-05）。

### 反例：传统按类型集中的目录

```
传统 SPA 项目（不推荐）：
src/
├── components/     # 所有组件放这里，不管属于哪个页面
│   ├── BlogCard.tsx
│   ├── LessonCard.tsx
│   └── Nav.tsx
├── images/         # 所有图片集中
│   ├── blog/
│   └── lessons/
├── data/           # 所有数据集中
└── pages/          # 页面组件单独放
    ├── Blog.tsx
    └── Lesson.tsx
```

这种方式在项目变大后，修改一个页面功能需要跨越 4-5 个目录寻找相关文件，上下文切换成本极高。

### 正例：3Blue1Brown 按领域共置

```
app/pages/
├── home/                    # 首页领域
│   ├── Home.tsx             # 首页路由组件
│   ├── Lessons.tsx          # 首页课程列表（仅首页使用，不进 components/）
│   ├── Search.tsx           # 首页搜索对话框（被 Nav 引用，但与首页搜索逻辑强相关）
│   └── ...
├── lessons/                 # 课程库领域（最复杂的领域）
│   ├── Lesson.tsx           # 课程详情页路由组件
│   ├── lessons.ts           # 课程数据导入、frontmatter 转换
│   ├── topics.ts            # 课程主题分类
│   ├── 2015/                # 2015 年课程
│   ├── 2016/                # 2016 年课程
│   │   ├── linear-transformations/
│   │   │   ├── index.mdx    # 课程主内容（MDX）
│   │   │   ├── patrons.txt  # 赞助者名单
│   │   │   ├── Hilbert.tsx  # 本课程专用自定义组件
│   │   │   └── figures/     # 本课程图片
│   │   └── ...
│   └── ...
├── blog/                    # 博客领域
│   ├── Post.tsx             # 博客详情页路由组件
│   ├── Book.tsx             # 博客页面专用组件（F-124 反例引用）
│   └── [post-name]/
│       └── index.mdx
├── about/
│   └── About.mdx            # MDX 直接作为路由组件
├── extras/
│   └── Extras.tsx
├── talent/
│   ├── Talent.tsx
│   └── Partner.tsx
└── NotFound.tsx             # 404 页面
```

### 共置原则的判断标准

什么时候组件应该放到 `app/components/`，什么时候应该就近放到 `pages/xxx/` 下？判断标准很简单：

| 场景 | 放置位置 | 示例 |
|------|----------|------|
| 组件被**多个页面/领域**复用 | `app/components/` | `Button`、`Dialog`、`YouTube`、`MathJax`、`Nav`、`DarkMode` |
| 组件**仅在单个页面/领域**使用 | 就近放在对应 `pages/xxx/` 下 | `home/Lessons.tsx`（仅首页课程列表）、`home/Search.tsx`（首页搜索）、`lessons/topics.ts`（仅课程分类） |
| 组件**仅在单个课程**中使用 | 放在该课程目录下 | `lessons/2016/linear-transformations/Hilbert.tsx`、`lessons/2017/neural-networks/NeuralNetwork.jsx` |

> **反常识提示**：即使组件被其他组件引用（如 `Nav.tsx` 引用了 `home/Search.tsx`），只要 Search 本质上是首页搜索功能的一部分，它就应该留在 `home/` 目录而非提升到 `components/`。引用跨目录是正常的，共置优先于"避免跨目录引用"。

## 公共组件 vs 页面内组件区分

`app/components/` 下约 60 个组件都是跨页面复用的通用组件（F-026），按功能可分为五大类：

| 分类 | 组件示例 |
|------|----------|
| **UI 基础** | Button、Card、Dialog、Form、Tabs、Tooltip、Link |
| **布局** | Header、Footer、Nav、Main、Grid、ViewCorner |
| **媒体** | YouTube、Vimeo、Figure、Image、Canvas、Shader |
| **内容** | MathJax、Markdownify、Heading、TableOfContents、Footnote、Quote、PiCreature |
| **交互** | Interactive、Question、FreeResponse、Carousel、ShowPartial、Celebrate |

完整组件索引见 [核心组件路径索引](../references/component-index.md)。

## 关键配置文件职责

根目录下的配置文件是项目的"骨架"，理解它们的职责是掌握架构的关键：

### package.json：项目依赖与脚本

项目清单文件（F-001 ~ F-022），核心内容：
- `"type": "module"`：启用 ES Modules 规范
- 开发命令：`react-router dev --open --port 31415`（端口 31415 是 π 的前几位，3B1B 特色）
- 构建命令：`react-router build`，产物输出到 `build/client/`
- 预览命令：`bunx serve ./build/client -p 31415`

### vite.config.ts：构建配置核心

Vite 构建配置（F-032 ~ F-038），定义了整个构建流水线：

1. **插件链顺序**（F-032，顺序很重要）：
   ```ts
   // 插件执行顺序：pre → normal → post
   textReplacePlugin()  // enforce: "pre"，MDX 转换前处理
     → mdxPlugin()      // MDX 编译 + Remark 插件链
     → tailwindcss()    // Tailwind v4 处理
     → reactRouter()    // React Router 框架模式集成
     → svgrPlugin()     // SVG → React 组件
   ```

2. **自定义 textReplacePlugin**（F-035）：两个关键功能：
   - 从 MDX frontmatter 派生 `readable`（内容长度 > 500 字符）和 `interactive`（包含 `<Interactive` 标签）布尔属性
   - 将 MDX 中的 `$lesson` 变量替换为 GCP 存储桶完整 URL（`site.gcp.bucket/lessons/...`）

3. **editMDX Remark 插件**（F-036）：修复 MDX issue #1798——MDX 会给 `<p>`、`<a>`、`<button>`、`<Link>`、`<Button>` 元素外面包多余的 `<p>` 标签，这个插件遍历 AST 移除多余包装。

4. **路径别名配置**（F-033）：
   ```ts
   resolve: {
     alias: {
       "~/": fileURLToPath(new URL("./app/", import.meta.url))
     }
   }
   ```
   配合 tsconfig.json 第 32 行 `"~/*": ["./app/*"]`，所有内部导入使用 `~/` 前缀（除同目录共置文件外）（F-125）。

5. **SVGR 配置**（F-038）：`expandProps: "start"`，SVG 默认 className 为 `"icon"`（支持 props.className 覆盖）。

### react-router.config.ts：React Router 框架配置

React Router 框架模式的配置文件（F-039 ~ F-041）：

- **`ssr: false`**（F-039）：完全禁用服务端渲染，采用纯预渲染（SSG）模式
- **`prerender` 异步函数**（F-040）：构建时通过 `import.meta.glob` 收集三类动态路由：
  - `/lessons/:id`：匹配 `lessons/20[0-9][0-9]/**/index.mdx`
  - `/talent/:id`：匹配 `talent/**/index.mdx`
  - `/blog/:id`：匹配 `blog/**/index.mdx`
  - 加上静态路由和 `/404`，全部预渲染为静态 HTML
- **路由列表导出**（F-041）：将预渲染路由列表写入 `./tests/routes.json`，供 Playwright E2E 测试遍历所有页面

### tsconfig.json：TypeScript 配置

严格的 TypeScript 配置（F-128）：
- `"strict": true`：启用所有严格类型检查
- `"noUncheckedIndexedAccess": true`：强制索引访问检查（`arr[0]` 类型为 `T | undefined` 而非 `T`）
- `"erasableSyntaxOnly": true`：要求类型标注可擦除（不使用 enum、namespace 等运行时遗留语法）
- 路径别名：`"~/*": ["./app/*"]`（F-033、F-125）

## 编码约定速查

项目有明确的编码风格约定（F-126、F-127）：

| 约定项 | 具体规则 |
|--------|----------|
| 组件声明 | React 组件使用 `function ComponentName() {}` 声明语法 |
| 普通函数 | 非组件函数使用箭头函数 `() => {}` 语法 |
| className 拼接 | 统一使用 `clsx` 库，禁止 classnames/cn 等其他方案 |
| 导入路径 | 内部导入使用 `~/` 前缀别名，同目录共置文件使用相对路径 |
| 包管理器 | Bun 首选，但所有脚本兼容 npm/yarn，不使用 Bun 专有 API（F-129） |

## 目录结构理解 Checklist

- [ ] 知道 `app/` 是 React Router 框架模式的约定目录（而非 Next.js 或 src/）
- [ ] 理解项目**没有** `public/` 目录，静态资源在 `app/assets/` 通过导入使用
- [ ] 掌握"按领域共置"原则：能判断一个组件应该放 `components/` 还是就近放 `pages/`
- [ ] 了解 `vite.config.ts` 插件链顺序和 textReplacePlugin 的两个核心功能
- [ ] 理解 `ssr: false` + `prerender` 的纯 SSG 架构
- [ ] 熟悉 `~/` 路径别名指向 `app/` 目录

## 相关概念

- [00 官网技术栈总览](00-website-overview.md)
- [02 路由与 SSG 预渲染](02-routing-and-pages.md)
- [完整技术栈清单](../references/tech-stack.md)
- [核心组件路径索引](../references/component-index.md)
