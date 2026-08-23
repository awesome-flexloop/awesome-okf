---
title: 部署与工具链
type: concept
bundle: /datawhale/easy-vibe
description: Easy-Vibe 的工具链覆盖本地开发、多语言静态站点构建、三平台部署（Vercel/GitHub Pages/魔搭 Docker）与多语言 PDF/EPUB 电子书发布，并通过 Husky、Prettier、ESLint 保障代码质量。
related:
  - /datawhale/easy-vibe/concepts/vibe-coding-philosophy
  - /datawhale/easy-vibe/concepts/multilingual-docs-architecture
sources:
  - https://github.com/datawhalechina/easy-vibe
---

## 工具链总览

Easy-Vibe 虽然是文档站而非应用，但其工具链覆盖了从本地开发到多形态产物发布的完整链路：

```
本地开发 (npm run dev)
    ↓
代码质量 (Prettier + ESLint + Husky hooks)
    ↓
多语言构建 (build-locales.mjs 顺序构建 + 文件锁)
    ↓
┌───────────────────────────────────────────────┐
│  Web 静态站                                    │
│  ├─ Vercel (vercel.json, base=/)              │
│  ├─ GitHub Pages (deploy.yml, base=/easy-vibe/)│
│  └─ 魔搭创空间 (Dockerfile + Nginx, :7860)     │
├───────────────────────────────────────────────┤
│  电子书 (release-books.yml on tag v*)          │
│  ├─ PDF (XeLaTeX + 10 语言 CJK 字体)           │
│  └─ EPUB (Puppeteer)                           │
│  → 上传到 GitHub Release                       │
└───────────────────────────────────────────────┘
```

## 本地开发

### 环境要求

- Node.js >= 18.0.0（`package.json` engines 字段）
- npm（仓库含 `package-lock.json`）

### 常用命令

| 命令 | 作用 |
|------|------|
| `npm install` | 安装依赖 |
| `npm run dev` | 启动 VitePress 本地开发服务器（热重载），默认 `http://localhost:5173/easy-vibe/` |
| `npm run build` | 生产构建（多语言顺序构建），输出到 `docs/.vitepress/dist` |
| `npm run build:single` | 单语言快速构建（跳过 locale 编排，8GB 堆内存） |
| `npm run preview` | 本地预览生产构建 |
| `npm run format` | Prettier 格式化整个仓库 |
| `npm run lint` | ESLint 检查 `docs/.vitepress/theme` |
| `npm run lint:fix` | ESLint 自动修复 |
| `npm test` | Node 原生 test runner 运行 `docs/` 与 `scripts/` 下的 `*.test.js` |
| `npm run sitemap` | 生成 sitemap.xml 与 robots.txt |

### AI IDE 一键运行

README 特别推荐"现代方式"：在 VS Code、Cursor 或 Trae 的 AI 对话窗口中直接说 "Please help me run this project locally."，由 AI 读取项目配置并完成启动。这是 Vibe Coding 理念在自身项目中的实践。

## 代码质量工具链

### Prettier

`.prettierrc` 配置三项规则：

- `semi: false`（不使用分号）
- `singleQuote: true`（单引号）
- `trailingComma: "none"`（无尾逗号）

`npm run format` 格式化全仓库，`.prettierignore` 排除构建产物与依赖。

### ESLint

`eslint.config.js` 使用 ESLint 9 扁平配置，配合 `eslint-plugin-vue` 与 `vue-eslint-parser` 检查 Vue SFC。检查范围限定在 `docs/.vitepress/theme`。

### Husky Git Hooks

`package.json` 的 `prepare: husky` 在安装时自动注册 Git hooks。仓库含 `.husky/pre-commit` 与 `.husky/pre-push`，在提交/推送前执行格式与检查。

### 提交规范

`AGENTS.md` 要求 Conventional Commits 风格：`feat:`、`fix:`、`docs:`（可选 scope 如 `feat(docs):`）。PR 需包含简短描述、UI/组件变更的截图/GIF、涉及路径。

## 多语言构建脚本

核心脚本 `scripts/build-locales.mjs` 的设计已在[多语言文档站架构](/datawhale/easy-vibe/concepts/02-multilingual-docs-architecture.md)中详述。工具链视角的关键点：

- **文件锁** `build-locales.lock` 防并发，PID 存活检测自动清除僵尸锁。
- **内存控制**：每 locale 默认 4096MB 堆（`BUILD_HEAP_MB` 可调），CI 中 GitHub Actions 用 8192MB。
- **增量能力**：`VITEPRESS_BUILD_LOCALES=zh-cn,en npm run build` 只构建指定语言。
- **确定性渲染**：`buildConcurrency` 默认 1（`VITEPRESS_BUILD_CONCURRENCY` 可调），注释说明 VitePress 2 alpha 可能在并发写入哈希时出问题。

其他脚本：

| 脚本 | 作用 |
|------|------|
| `generate-sitemap.mjs` | 生成 sitemap.xml 与 robots.txt |
| `build-latex-book.mjs` | 调用 XeLaTeX 生成 PDF |
| `build-epub.mjs` | 用 Puppeteer 生成 EPUB |
| `build-books.mjs` | 编排所有语言的 PDF+EPUB（支持 `BOOK_PDF_ONLY`/`BOOK_EPUB_ONLY`/指定 locale） |
| `book-shared.mjs` | 电子书构建共享逻辑 |
| `render-book-asset.mjs` | 渲染电子书资源 |
| `epub-image-conversion.mjs` | EPUB 图片转换 |
| `optimize-stage1-images.mjs` | Stage 1 截图优化 |
| `scan-appendix-component-i18n.mjs` | 附录组件 i18n 翻译缺失扫描 |

## Web 部署

### Vercel

`vercel.json` 声明：

- `buildCommand: npm run build`
- `installCommand: npm install`
- `framework: vitepress`
- `outputDirectory: docs/.vitepress/dist`

缓存策略：
- `/assets/(.*)` → `public, max-age=31536000, immutable`（带哈希的静态资源永久缓存）
- 图片资源（avif/gif/ico/jpeg/jpg/png/svg/webp）→ `public, max-age=604800, stale-while-revalidate=86400`
- `/sitemap.xml`、`/robots.txt` → `public, max-age=86400, s-maxage=86400`

安全头（全站）：
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: camera=(), microphone=(), geolocation=()`

Vercel 部署时自动设置 `VERCEL=1`，config.mjs 据此把 base 设为 `/`。

### GitHub Pages

`.github/workflows/deploy.yml` 在推送到 `main` 时触发：

1. 仅 `github.repository_owner == 'datawhalechina'` 执行（fork 不触发）。
2. Ubuntu 最新 runner，Node 20，npm 缓存。
3. `actions/configure-pages@v4` 配置 Pages。
4. `npm ci` 安装依赖。
5. `NODE_OPTIONS=--max-old-space-size=8192 npm run build` 构建。
6. `actions/upload-pages-artifact@v3` 上传 `docs/.vitepress/dist`。
7. `actions/deploy-pages@v4` 部署。

并发控制 `group: pages` + `cancel-in-progress: false`，排队但不取消正在进行的生产部署。GitHub Pages 环境下 base 为 `/easy-vibe/`。

### 魔搭创空间（ModelScope Studio）

`Dockerfile` 采用多阶段构建：

- **构建阶段** `node:20-alpine`：`npm ci` 后 `npm run build`。
- **运行阶段** `nginx:alpine`：拷贝 `nginx.conf` 到 `/etc/nginx/conf.d/default.conf`，拷贝构建产物到 `/usr/share/nginx/html`，`EXPOSE 7860`（魔搭要求端口），`CMD ["nginx", "-g", "daemon off;"]`。

这是三条 Web 部署路径中唯一自包含镜像方案，不依赖平台的 Node 构建环境。

## 电子书发布

`.github/workflows/release-books.yml` 在推送 `v*` tag 时触发（也支持手动 `workflow_dispatch`）：

1. 安装系统依赖：
   - TeX Live：`texlive-xetex`、`texlive-latex-extra`、`texlive-fonts-recommended`、`texlive-lang-cjk`、`texlive-lang-arabic`、`texlive-lang-korean`、`texlive-lang-japanese`、`texlive-lang-chinese`、`texlive-lang-european`
   - 字体：`fonts-noto-cjk`、`fonts-noto-core`、`fonts-wqy-zenhei`、`fonts-wqy-microhei`、`fonts-nanum` 等
   - 工具：`imagemagick`、`ffmpeg`、`ghostscript`、`librsvg2-bin`
2. `npm ci` 安装依赖。
3. `PDF_VERSION` 与 `EPUB_VERSION` 设为 tag 名，`NODE_OPTIONS=--max-old-space-size=8192`，执行 `npm run book:all`。
4. 列出 `docs/.vitepress/dist/*.pdf` 与 `*.epub`。
5. 用 `softprops/action-gh-release@v2` 把所有 PDF/EPUB 附加到 GitHub Release，并自动生成 release notes。

电子书命令支持细粒度控制：`npm run book:zh`、`npm run book:en`、`BOOK_PDF_ONLY=1 npm run book:all`、`BOOK_EPUB_ONLY=1 npm run book:all`。

## Markdown 扩展与构建钩子

- **KaTeX**：`markdown-it-katex` 插件支持数学公式渲染。
- **图片懒加载**：config.mjs 自定义 image 渲染规则，对 `stage-1` 路径下的图片自动添加 `loading="lazy"` 与 `decoding="async"`（Stage 1 长教程截图多，避免首屏竞争）。
- **build-hooks.mjs**：通过 `createBuildHooks` 工厂注册 VitePress 的 `transformHtml`、`transformHead`、`buildEnd` 钩子，处理 locale 菜单链接重写等。
- **死链宽容**：`ignoreDeadLinks: true`，避免构建因外部链接或未完成页面失败。

## AI Agent 辅助文件

工具链中包含三份面向 AI 的说明文件，它们本身不参与构建，但决定了 AI IDE 如何理解本仓库：

- `llms.txt`：1380 行 AI 导航地图，公开发布于 `docs/public/llms.txt`。
- `CLAUDE.md`：Claude Code 专用，含 bash 权限白名单（`which`、`find`、`mv`、`tree`、`cat`、`curl`、`npm run dev/build/preview/format` 等）。
- `AGENTS.md`：通用 Agent 仓库规范。

## 相关概念

- [Vibe Coding 理念](/datawhale/easy-vibe/concepts/01-vibe-coding-philosophy.md)：工具链所服务的教学理念与三阶段内容。
- [多语言文档站架构](/datawhale/easy-vibe/concepts/02-multilingual-docs-architecture.md)：build-locales.mjs 的顺序构建、base 自适应、SEO 生成等机制的深入解析。
