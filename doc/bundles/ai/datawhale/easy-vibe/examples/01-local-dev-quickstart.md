---
title: 本地运行与构建示例
type: example
bundle: /datawhale/easy-vibe
description: 通过最小步骤在本地启动 Easy-Vibe 文档站，演示依赖安装、开发服务器、多语言生产构建与预览命令，并对比 AI IDE 一键运行与传统命令行两种方式。
related:
  - /datawhale/easy-vibe/concepts/deployment-toolchain
  - /datawhale/easy-vibe/concepts/multilingual-docs-architecture
sources:
  - https://github.com/datawhalechina/easy-vibe
---

## 场景说明

你想在本地阅读 Easy-Vibe 教程或参与文档贡献，需要把 VitePress 站点跑起来。本示例演示两种方式：AI IDE 自然语言一键运行，与传统命令行手动运行。

## 前置条件

- Node.js >= 18.0.0（`package.json` engines 要求）
- npm（仓库提供 `package-lock.json`）
- 约 4GB 可用内存（单 locale 构建默认 4096MB 堆）

## 方式一：AI IDE 一键运行（推荐）

README 明确推荐的"现代方式"。在 VS Code、Cursor 或 Trae 的 AI 对话窗口中直接输入：

```text
Please help me run this project locally.
```

AI 会读取 `package.json`、`AGENTS.md`，自动执行依赖安装与启动命令。这是 Vibe Coding 理念在项目自身的体现——用自然语言描述意图，AI 完成具体实现。

## 方式二：传统命令行

### 1. 安装依赖

```bash
npm install
```

或使用 `npm ci`（CI 环境，严格按 lockfile 安装）。

### 2. 启动开发服务器

```bash
npm run dev
```

该命令执行 `vitepress dev docs`，启动带热重载的本地服务器。访问地址：

```
http://localhost:5173/easy-vibe/
```

注意路径含 `/easy-vibe/` 前缀——本地开发默认 base 为 `/easy-vibe/`（与 GitHub Pages 一致），由 `docs/.vitepress/config.mjs` 的环境判断逻辑决定。

### 3. 生产构建

```bash
npm run build
```

该命令调用 `node scripts/build-locales.mjs`，顺序构建全部 10 个语言。构建产物输出到：

```
docs/.vitepress/dist/
```

构建过程中会看到每个 locale 的分组日志，以及最终合并的 page hash 数量。

#### 只构建部分语言（加速）

```bash
VITEPRESS_BUILD_LOCALES=zh-cn,en npm run build
```

#### 单语言快速构建（跳过 locale 编排）

```bash
npm run build:single
```

该命令直接以 8192MB 堆调用 vitepress build，并先生成 sitemap。

### 4. 预览生产构建

```bash
npm run preview
```

执行 `vitepress preview docs`，默认在 `http://localhost:4173/easy-vibe/` 预览构建产物。

## 代码质量检查

提交前建议运行：

```bash
npm run format     # Prettier 格式化（无分号、单引号、无尾逗号）
npm run lint       # ESLint 检查 docs/.vitepress/theme
npm test           # Node 原生 test runner
```

## 关键配置说明

### Base 路径差异

本地开发与生产部署的 URL 前缀不同，由环境变量自动决定：

| 环境 | 触发条件 | base | 本地访问路径 |
|------|---------|------|-------------|
| 本地 dev/preview | 无 `VERCEL`/`EDGEONE` | `/easy-vibe/` | `http://localhost:5173/easy-vibe/zh-cn/` |
| Vercel | `VERCEL=1` | `/` | `https://xxx.vercel.app/zh-cn/` |
| EdgeOne | `EDGEONE=1` | `/` | 根路径 |
| GitHub Pages | 默认 | `/easy-vibe/` | `https://datawhalechina.github.io/easy-vibe/zh-cn/` |

如需强制指定 base：

```bash
BASE=/ npm run build
```

### 内存调整

若构建遇到 OOM：

```bash
BUILD_HEAP_MB=8192 npm run build
```

### 首次访问的欢迎页

本地启动后首次访问根路径会进入 SVG 描边动画欢迎页，点击任意位置后写入 `localStorage`（键 `easy-vibe-welcome-seen=1`）并按浏览器语言跳转到对应 locale。清除 localStorage 可重新触发。

## 验证清单

- [ ] `npm run dev` 后浏览器能打开 `http://localhost:5173/easy-vibe/`
- [ ] 首次访问显示欢迎页动画，点击后跳转到中文（或浏览器语言）首页
- [ ] 顶部导航可切换 Stage 1/2/3、附录、Vibe 故事
- [ ] 语言切换器可在 10 种语言间切换
- [ ] `npm run build` 成功输出 `docs/.vitepress/dist/`
- [ ] `npm run preview` 可预览构建产物

## 相关概念

- [部署与工具链](../concepts/03-deployment-toolchain.md)：完整的构建脚本、三平台部署、电子书发布流水线。
- [多语言文档站架构](../concepts/02-multilingual-docs-architecture.md)：build-locales.mjs 的顺序构建、文件锁、base 自适应机制。
