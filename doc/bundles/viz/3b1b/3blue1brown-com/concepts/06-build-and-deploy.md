---
type: Concept
title: 构建系统、包管理与静态部署
description: 3Blue1Brown.com 的工程化体系：Bun 包管理器选型、package.json scripts 全解析、Vite 插件链架构、React Router 预渲染（SSG）配置、TypeScript 严格模式、静态托管部署方案。
tags: [3blue1brown, bun, vite, react-router, ssg, build, deploy, typescript, package-manager]
generated: { by: "source-code-to-okf-wiki/e-phase", at: "2026-08-26" }
verified: { by: "", at: "" }
status: draft
stale_after: 2027-08-26
sources:
  - id: facts
    resource: /spec/facts.md
    title: 3Blue1Brown.com 源码事实采集
---

# 构建系统、包管理与静态部署

3Blue1Brown.com 采用现代化前端工程化栈，以 **Bun** 为首选包管理器和运行时，**Vite 8** 为构建工具，**React Router v8 框架模式**为应用框架，通过 **SSG（静态站点生成）** 预渲染所有页面为纯静态 HTML，最终部署到 Netlify 等静态托管平台。整个体系零 Node.js 服务器依赖，构建产物可部署到任意 CDN 或静态文件服务器（F-003、F-039、F-130）。

## 包管理器：为什么选择 Bun

项目使用 Bun 作为首选包管理器和运行时（F-129），但 package.json 脚本保持与 npm/yarn/pnpm 的兼容性，不使用 Bun 专有 API。

### Bun vs npm/pnpm/yarn 对比

| 维度 | Bun | npm/pnpm/yarn |
|------|-----|---------------|
| **安装速度** | 极快（原生实现，比 pnpm 快 3-5 倍） | 较慢（Node.js 单线程瓶颈） |
| **启动速度** | 极快（JavaScriptCore 引擎） | 较慢（V8 冷启动开销） |
| **运行时** | 内置运行时（替代 Node.js） | 需要 Node.js |
| **TypeScript 支持** | 原生支持，无需 ts-node/tsx | 需要额外配置 |
| **脚本执行** | `bun run` 直接执行 TS/JSX | `npm run` 需通过 node 执行 |
| **兼容性** | 兼容 95%+ npm 包，少量边缘差异 | 完全兼容 |

项目选择 Bun 的核心理由：
1. **开发体验**：依赖安装和 dev server 启动速度显著提升
2. **工具链一体化**：Bun 同时是包管理器、运行时、打包器、测试运行器，减少工具依赖
3. **零配置 TypeScript**：直接运行 `.ts` 文件无需额外编译步骤

脚本同时兼容 npm/yarn/pnpm 的原因：降低团队成员的环境门槛，不需要强制所有人切换到 Bun。`bunx` 等价于 `npx`，用于执行项目本地的 CLI 工具（F-003）。

## package.json scripts 全解析

`package.json` 定义了完整的开发、构建、预览、类型检查脚本体系（F-002~F-003）：

```json
{
  "scripts": {
    "dev": "react-router dev --open --port 31415",
    "build": "react-router build",
    "preview": "bunx serve ./build/client -p 31415",
    "typecheck": "react-router typegen && tsc"
  }
}
```

### dev：开发服务器

```bash
bun run dev
```

- 启动 React Router 框架模式的 Vite 开发服务器（F-002）
- `--open`：启动后自动打开浏览器
- `--port 31415`：监听端口 31415（π 的前五位，3Blue1Brown 的标志性数字）
- 支持 HMR（热模块替换），修改代码无需刷新页面
- MDX 文件变更自动触发页面重新渲染

### build：生产构建

```bash
bun run build
```

- 执行 React Router 生产构建（F-003）
- Vite 打包所有资源：TSX → JS、CSS → 压缩 CSS、MDX → JS 模块
- 静态资源（图片、字体、视频）哈希化处理用于缓存
- 产物输出到 `build/client/` 目录（由 preview 命令推断）
- 构建过程自动执行 SSG 预渲染（见下文）

### preview：本地预览构建产物

```bash
bun run preview
```

- 使用 `serve` 启动静态文件服务器，服务 `./build/client` 目录（F-003）
- 端口同样是 31415
- 用于在部署前验证生产构建是否正常工作
- 模拟静态托管环境，可发现仅在 SSG 模式下出现的问题

### typecheck：类型检查

```bash
bun run typecheck
```

- 分两步执行（F-004）：
  1. `react-router typegen`：生成路由类型定义（`+types/Lesson.ts` 等文件，供 `Route.ComponentProps` 使用）
  2. `tsc`：运行 TypeScript 编译器做完整类型检查
- 这是 CI 必须通过的质量门

## Vite 构建配置：插件链架构

`vite.config.ts` 是 Vite 的配置文件，核心是精心设计的插件链顺序（F-032~F-038）。Vite 插件按注册顺序执行，不同顺序会产生不同结果，项目的插件顺序经过仔细考量。

### 插件链顺序（F-032）

```typescript
// vite.config.ts 第16-37行（F-032）
import { defineConfig } from "vite";
import { reactRouter } from "@react-router/dev/vite";
import tailwindcss from "@tailwindcss/vite";
import mdxPlugin from "@mdx-js/rollup";
import svgrPlugin from "@svgr/rollup";

export default defineConfig({
  plugins: [
    textReplacePlugin(),   // 1. 自定义前置插件（enforce: "pre"）
    mdxPlugin({ ... }),    // 2. MDX 处理
    tailwindcss(),         // 3. Tailwind v4 CSS 处理
    reactRouter(),         // 4. React Router 框架模式集成
    svgrPlugin({ ... }),   // 5. SVG 作为 React 组件导入
  ],
  // ... 其他配置
});
```

插件执行顺序说明：

| 顺序 | 插件 | 作用 | 为什么在这个位置 |
|------|------|------|------------------|
| 1 | `textReplacePlugin` | MDX 转换前的文本替换：frontmatter 属性派生、`$lesson` 路径替换 | 需要在 MDX 解析前修改源码，`enforce: "pre"` 确保最先执行（F-035） |
| 2 | `mdxPlugin` | MDX → JSX 转换，处理 Remark 插件链 | 必须在 React Router 之前将 MDX 转为标准 JS 模块（F-037） |
| 3 | `tailwindcss()` | Tailwind v4 CSS 处理：扫描 className、生成 CSS | 在 JSX 转换完成后扫描 className 最准确（F-007） |
| 4 | `reactRouter()` | React Router 框架模式核心：路由处理、SSR/SSG、HMR | 处理路由模块和页面组件，需要在其他 JS 转换之后（F-004） |
| 5 | `svgrPlugin` | SVG → React 组件转换 | 将 `.svg` 导入转为 React 组件，放在最后避免干扰其他插件（F-038） |

### 路径别名配置（F-033~F-034）

```typescript
// vite.config.ts 第33-35行（F-033）
import { fileURLToPath } from "node:url";

export default defineConfig({
  plugins: [ /* ... */ ],
  resolve: {
    tsconfigPaths: true,  // 启用 tsconfig.json 中的路径解析（F-034）
    alias: {
      "~/": fileURLToPath(new URL("./app/", import.meta.url)),
    },
  },
});
```

配合 `tsconfig.json` 第32行的配置：

```json
{
  "compilerOptions": {
    "paths": {
      "~/*": ["./app/*"]
    }
  }
}
```

实现 `~/` 前缀的绝对导入，避免深层嵌套目录的相对路径地狱（F-125）：

```tsx
// ✅ 推荐：使用 ~/ 绝对导入
import { MathJax } from "~/components/MathJax";
import { lessons } from "~/pages/lessons/lessons";

// ❌ 避免：多层相对路径
import { MathJax } from "../../../components/MathJax";
```

### textReplacePlugin：前置文本处理插件

这是项目自定义的 Vite 插件，`enforce: "pre"` 确保在所有其他转换之前执行（F-035）：

```typescript
// vite.config.ts 第40-82行（F-035）
function textReplacePlugin() {
  return {
    name: "text-replace",
    enforce: "pre" as const,
    transform(code: string, id: string) {
      // 只处理 MDX 文件
      if (!id.endsWith(".mdx")) return;
      
      // 处理1：从frontmatter派生readable和interactive属性
      // - readable: 内容长度 > 500字符
      // - interactive: 包含<Interactive标签
      
      // 处理2：将$lesson变量替换为GCP存储桶完整路径
      // $lesson/figures/xxx.png → https://storage.googleapis.com/.../lessons/.../figures/xxx.png
      
      return { code: transformedCode, map: null };
    },
  };
}
```

这个插件解决了两个关键问题：
1. **元数据派生**：在构建时计算课程是否"可读"（长篇内容）和"有交互"，不需要在客户端运行时判断
2. **资源路径替换**：MDX 中使用简洁的 `$lesson/` 前缀，构建时替换为生产环境的 GCP CDN 完整 URL

### MDX 插件配置与 Remark 插件链

```typescript
// vite.config.ts 第99-109行（F-037）
import remarkFrontmatter from "remark-frontmatter";
import remarkMdxFrontmatter from "remark-mdx-frontmatter";
import remarkMath from "remark-math";
import remarkGfm from "remark-gfm";

mdxPlugin({
  remarkPlugins: [
    remarkFrontmatter,      // 1. 解析 YAML frontmatter
    remarkMdxFrontmatter,   // 2. 将 frontmatter 导出为 JS 属性
    remarkMath,             // 3. 解析 $...$ 和 $$...$$ 数学公式
    remarkGfm,              // 4. GFM 扩展（表格、任务列表、删除线等）
    editMDX,                // 5. 自定义插件：修复 MDX 段落包装问题
  ],
  providerImportSource: "~/components/Markdownify",
})
```

Remark 插件顺序至关重要：先解析 frontmatter，再处理数学公式，最后应用自定义修复。

`providerImportSource` 指定 MDX 运行时使用自定义组件提供者 `~/components/Markdownify`，这是项目自定义 Markdown 组件映射的入口（F-087）。

### editMDX：修复 MDX 段落包装问题

MDX 有一个已知问题（issue #1798）：当 `<p>`、`<a>`、`<button>`、`<Link>`、`<Button>` 等元素作为块级元素的直接子元素时，MDX 会错误地用额外的 `<p>` 标签包装它们（F-036）。`editMDX` 插件在构建时遍历 AST 移除这些多余包装：

```typescript
// vite.config.ts 第85-96行（F-036）
function editMDX() {
  return (tree: any) => {
    visit(tree, "mdxJsxFlowElement", (node) => {
      // 移除为特定元素添加的多余段落包装
      const tagNames = ["p", "a", "button", "Link", "Button"];
      if (tagNames.includes(node.name)) {
        // 提升子元素，移除多余包装
      }
    });
  };
}
```

### SVGR 插件配置

```typescript
// vite.config.ts 第112-120行（F-038）
svgrPlugin({
  expandProps: "start",  // props 展开到开头，允许默认 props 被覆盖
  svgProps: {
    className: "icon",   // SVG 默认 className 为 "icon"
  },
})
```

这使得导入 SVG 时默认应用 `icon` 工具类（尺寸 1.5rem×1.5rem），但可以通过 props 覆盖：

```tsx
import Logo from "~/assets/logo.svg";

// 默认：icon 尺寸
<Logo />

// 覆盖：更大尺寸
<Logo className="w-12 h-12" />
```

## react-router.config.ts：SSG 预渲染配置

`react-router.config.ts` 是 React Router 框架模式的核心配置文件，决定了渲染模式和预渲染策略（F-039~F-041）。

### 完全禁用 SSR，采用 SSG 模式

```typescript
// react-router.config.ts 第12行（F-039）
export default {
  ssr: false,  // 完全禁用服务端渲染
  // ...
};
```

这是一个关键的架构决策：项目不使用 Node.js 服务器运行时，而是采用 **SSG（Static Site Generation）** 模式，在构建时预渲染所有页面为静态 HTML（F-130）。

SSG vs SSR vs SPA 对比：

| 模式 | 渲染时机 | 服务器需求 | SEO | 首屏速度 |
|------|----------|-----------|-----|----------|
| **SSG** | 构建时 | 静态文件服务器/CDN | ✅ 优秀 | ✅ 极快（直接返回 HTML） |
| SSR | 每个请求时 | 需要 Node.js 服务器 | ✅ 优秀 | ⚠️ 较快（服务器渲染延迟） |
| SPA | 客户端 | 静态文件服务器 | ❌ 差 | ❌ 慢（需等待 JS 下载执行） |

3Blue1Brown.com 选择 SSG 的原因：
1. **内容是静态的**：课程内容、博客文章发布后很少变动，不需要每次请求动态渲染
2. **部署简单**：构建产物是纯 HTML/CSS/JS，可部署到 Netlify、Vercel、Cloudflare Pages、GitHub Pages 等任意静态托管平台
3. **性能极佳**：CDN 边缘缓存，全球用户都能快速访问
4. **零运维成本**：没有 Node.js 服务器需要维护、监控、扩容

### prerender：动态路由收集与预渲染

`ssr: false` 模式下，React Router 需要知道哪些路径需要预渲染为 HTML。静态路由（`/`、`/about`、`/extras`）自动处理，但动态路由（`/lessons/:id`）需要显式收集（F-040）：

```typescript
// react-router.config.ts 第15-65行（F-040）
export default {
  ssr: false,
  
  async prerender() {
    // 1. 收集所有课程路由（/lessons/:id）
    const lessonModules = import.meta.glob(
      "./app/pages/lessons/20[0-9][0-9]/**/index.mdx",
      { eager: true, query: "frontmatter-only" }
    );
    const lessonRoutes = Object.keys(lessonModules).map((path) => {
      // 从文件路径提取课程 ID
      // ./app/pages/lessons/2016/linear-transformations/index.mdx → /lessons/linear-transformations
      const id = path.split("/").slice(-2, -1)[0];
      return `/lessons/${id}`;
    });
    
    // 2. 收集 talent 页面路由（/talent/:id）
    const talentModules = import.meta.glob("./app/pages/talent/**/index.mdx", { eager: true });
    const talentRoutes = Object.keys(talentModules).map(/* ... */);
    
    // 3. 收集博客文章路由（/blog/:id）
    const blogModules = import.meta.glob("./app/pages/blog/**/index.mdx", { eager: true });
    const blogRoutes = Object.keys(blogModules).map(/* ... */);
    
    // 4. 返回所有需要预渲染的路由
    const routes = [
      ...lessonRoutes,
      ...talentRoutes,
      ...blogRoutes,
      "/404",  // 404 页面也预渲染
    ];
    
    // 5. 将路由列表写入文件供 E2E 测试使用（F-041）
    await fs.writeFile("./tests/routes.json", JSON.stringify(routes, null, 2));
    
    return routes;
  },
};
```

关键技术点：
1. **`import.meta.glob` 构建时收集**：Vite 的 `import.meta.glob` 在构建时扫描文件系统，匹配 glob 模式的所有文件路径，这是静态站点生成器的标准技术
2. **`eager: true`**：构建时立即导入（而非懒加载），因为我们需要在构建阶段访问文件路径列表
3. **`query: "frontmatter-only"`**：仅导入 frontmatter 元数据，不导入完整 MDX 内容，优化构建性能
4. **路径提取**：从文件路径 `./app/pages/lessons/2016/linear-transformations/index.mdx` 提取出课程 ID `linear-transformations`，构建为 `/lessons/linear-transformations` 路由
5. **测试导出**：预渲染路由列表同时写入 `./tests/routes.json`，供 Playwright E2E 测试遍历所有页面（F-041）

### SSG 构建产物结构

执行 `bun run build` 后，`build/client/` 目录包含：

```
build/client/
├── index.html                    # 首页 /
├── about/
│   └── index.html                # /about
├── lessons/
│   ├── index.html                # 课程列表页
│   ├── linear-transformations/
│   │   └── index.html            # /lessons/linear-transformations
│   ├── neural-networks/
│   │   └── index.html            # /lessons/neural-networks
│   └── ...
├── blog/
│   └── ...
├── assets/                       # 哈希化静态资源（JS/CSS/图片/字体）
│   ├── index-abc123.js
│   ├── lessons-def456.js
│   ├── styles-ghi789.css
│   └── ...
├── 404.html                      # 404 页面（Netlify 等平台自动识别）
└── sitemap.xml                   # 自动生成的站点地图
```

每个路由对应一个目录下的 `index.html`，这是静态托管的标准惯例（clean URLs）。

## TypeScript 严格模式配置

项目启用了完整的 TypeScript 严格模式，这是代码质量的重要保障（F-128）：

```json
// tsconfig.json 关键配置（F-128）
{
  "compilerOptions": {
    "strict": true,                    // 启用所有严格类型检查选项
    "noUncheckedIndexedAccess": true,   // 强制索引访问检查
    "erasableSyntaxOnly": true          // 要求类型标注可擦除（不使用 enum/namespace 等运行时语法）
  }
}
```

### strict: true

启用以下所有严格检查：
- `noImplicitAny`：禁止隐式 any 类型
- `noImplicitThis`：禁止 this 隐式 any
- `strictNullChecks`：null/undefined 是独立类型，不能赋值给其他类型
- `strictFunctionTypes`：函数参数类型逆变检查
- `strictPropertyInitialization`：类属性必须初始化或有 undefined 类型
- `useUnknownInCatchVariables`：catch 变量默认为 unknown 而非 any

### noUncheckedIndexedAccess: true

这是一个额外的严格选项：数组或对象索引访问的返回值自动包含 `undefined`：

```typescript
const lessons = ["a", "b", "c"];
const first = lessons[0];  // 类型: string | undefined，不是 string

// 必须显式检查或使用非空断言（谨慎）
if (first) {
  console.log(first.toUpperCase());
}
```

这强制开发者处理数组越界的边界情况，避免运行时 `Cannot read property 'toUpperCase' of undefined` 错误。

### erasableSyntaxOnly: true

TypeScript 有一些语法在编译后会留下运行时代码（如 `enum`、`namespace`、参数属性），`erasableSyntaxOnly: true` 禁止使用这些语法，只允许使用编译后完全擦除的类型标注：

```typescript
// ❌ 禁止：enum 编译后生成 IIFE
enum Direction { Up, Down }

// ✅ 推荐：使用 as const 对象
const Direction = { Up: 0, Down: 1 } as const;
type Direction = typeof Direction[keyof typeof Direction];
```

## 环境配置

项目使用 Vite 的环境变量机制，通过 `.env` 文件管理不同环境的配置。

### 环境变量命名规范

Vite 要求客户端可访问的环境变量必须以 `VITE_` 前缀开头：

```bash
# .env（所有环境共享）
VITE_SITE_NAME=3Blue1Brown

# .env.development（开发环境）
VITE_API_URL=http://localhost:31415/api

# .env.production（生产环境）
VITE_API_URL=https://www.3blue1brown.com/api
```

在代码中通过 `import.meta.env` 访问：

```typescript
const siteName = import.meta.env.VITE_SITE_NAME;
const apiUrl = import.meta.env.VITE_API_URL;
```

### 类型安全的环境变量

项目可以通过 `vite-env.d.ts` 为环境变量添加类型：

```typescript
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_SITE_NAME: string;
  readonly VITE_API_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
```

## 静态托管部署

项目构建产物是纯静态文件，可部署到任意静态托管平台（F-130）。根目录存在 `netlify.toml`，表明 Netlify 是官方部署平台。

### Netlify 部署配置

```toml
# netlify.toml
[build]
  command = "bun run build"
  publish = "build/client"

[[redirects]]
  from = "/*"
  to = "/404.html"
  status = 404
```

关键配置：
- **build.command**：构建命令 `bun run build`（Netlify 原生支持 Bun）
- **build.publish**：发布目录 `build/client`
- **404 重定向**：所有未匹配路径返回 `404.html`，SPA/SSG 站点标准配置

### 部署方式对比

| 平台 | 部署方式 | 优势 |
|------|----------|------|
| **Netlify** | Git 集成，自动部署 | 简单、PR 预览、表单处理、边缘函数 |
| **Vercel** | Git 集成，自动部署 | 优秀的 Next.js 支持、边缘网络、分析 |
| **Cloudflare Pages** | Git 集成/Wrangler CLI | 免费额度大、全球边缘网络、R2 存储集成 |
| **GitHub Pages** | GitHub Actions | 免费、与仓库集成、自定义工作流 |
| **Nginx/Apache** | 手动上传 build/client | 完全控制、自有服务器 |

### 部署检查清单

1. **环境变量**：在托管平台配置所有 `VITE_*` 环境变量
2. **Node/Bun 版本**：指定版本（Netlify 使用 `NODE_VERSION` 环境变量）
3. **构建命令**：`bun run build` 或 `npm run build`
4. **发布目录**：`build/client`（不是项目根目录）
5. **SPA 回退**：配置 404 重定向到 `/404.html`（处理客户端路由）
6. **缓存策略**：静态资源（`assets/` 下带哈希的文件）设置长期缓存，HTML 设置不缓存或短期缓存
7. **HTTPS**：确保启用 HTTPS（所有现代平台默认支持）
8. **压缩**：启用 Gzip/Brotli 压缩（平台默认支持）

### Vite 预加载错误处理

生产部署后有一个常见问题：旧版本的 chunk 文件在新版本部署后被删除，用户正在浏览旧页面时懒加载新 chunk 会 404。项目通过监听 `vite:preloadError` 事件解决（F-054）：

```tsx
// app/root.tsx 第119-129行（F-054）
useEffect(() => {
  const handler = (event: any) => {
    // 使用 sessionStorage 去重，避免无限刷新循环
    const key = "preload-error-refreshed";
    if (sessionStorage.getItem(key)) return;
    sessionStorage.setItem(key, "true");
    
    // 强制刷新页面获取新资源
    window.location.reload();
  };
  
  window.addEventListener("vite:preloadError", handler);
  return () => window.removeEventListener("vite:preloadError", handler);
}, []);
```

这是一个优雅降级方案：预加载失败时自动刷新一次（sessionStorage 标记防止无限刷新），用户体验影响最小。

## bun run vs npm run 对比

项目脚本兼容 Bun 和 npm，日常开发可根据偏好选择：

| 操作 | Bun | npm | pnpm |
|------|-----|-----|------|
| 安装依赖 | `bun install` | `npm install` | `pnpm install` |
| 添加依赖 | `bun add <pkg>` | `npm install <pkg>` | `pnpm add <pkg>` |
| 添加 dev 依赖 | `bun add -d <pkg>` | `npm install -D <pkg>` | `pnpm add -D <pkg>` |
| 运行脚本 | `bun run dev` | `npm run dev` | `pnpm dev` |
| 执行本地 CLI | `bunx serve` | `npx serve` | `pnpm dlx serve` |

Bun 特定优势：
- `bun run` 不创建子 shell，脚本执行更快
- Bun 内置 `dotenv`，自动加载 `.env` 文件
- `bunx` 比 `npx` 快很多，且自动缓存包

注意事项：
- 少量 npm 包可能在 Bun 下有兼容性问题（主要是包含原生 Node.js 插件的包），遇到问题可回退到 npm
- CI 环境建议使用官方 Bun Docker 镜像或 `oven-sh/setup-bun` GitHub Action

## 构建性能优化

项目的构建配置体现了多项性能优化实践：

1. **`query: "frontmatter-only"`**：收集路由时只导入 frontmatter，不导入完整 MDX 内容，大幅减少构建时内存占用
2. **懒加载路由**：课程内容通过无 `eager` 的 `import.meta.glob` 懒加载，构建时拆分为独立 chunk
3. **Tailwind JIT**：Tailwind v4 仅生成实际使用的 CSS，最终 CSS 体积极小
4. **资源哈希**：静态资源文件名包含内容哈希，浏览器可安全地长期缓存
5. **代码分割**：Vite 自动按路由进行代码分割，首屏只加载必要代码
6. **SVG 作为组件**：SVG 通过 SVGR 内联为 React 组件，避免额外网络请求

## 工程化体系总结

3Blue1Brown.com 的工程化体系是现代静态站点的标杆：

1. **Bun 驱动**：极致的开发体验，同时保持 npm 兼容性
2. **Vite 插件链**：精心设计的插件顺序，每个插件职责单一
3. **React Router SSG**：零服务器依赖，构建时预渲染所有页面
4. **TypeScript 严格模式**：`strict` + `noUncheckedIndexedAccess` 保障代码质量
5. **路径别名**：`~/` 前缀避免相对路径地狱
6. **静态部署**：产物可部署到任意 CDN，运维成本为零
7. **错误降级**：预加载失败自动刷新，用户体验无感知

这套体系的代码量极小，但覆盖了现代前端工程化的所有关键环节：开发体验、构建性能、类型安全、部署简单、运行时健壮。

## 相关概念

- [00 官网技术栈总览](/concepts/00-website-overview.md)
- [01 项目结构与目录组织](/concepts/01-project-structure.md)
- [02 路由系统与页面组织](/concepts/02-routing-and-pages.md)
- [03 MDX 内容系统与数学渲染](/concepts/03-mdx-content-system.md)
- [05 Tailwind v4 CSS-first 样式系统](/concepts/05-styling-with-tailwind4.md)
- [完整技术栈清单](/references/tech-stack.md)
- [创建带数学公式的 MDX 页面](/examples/minimal-mdx-page.md)
- [Tailwind v4 主题与自定义变体配置](/examples/tailwind-theme-setup.md)
