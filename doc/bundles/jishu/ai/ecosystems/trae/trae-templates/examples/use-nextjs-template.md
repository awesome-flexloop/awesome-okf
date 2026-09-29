---
type: Example
title: 使用 Next.js 模板创建项目
description: 从 nextjs-starter 模板开始，完成复制模板、安装依赖、启动开发服务器、验证运行的完整流程。
tags: [trae-templates, example, nextjs, react, typescript, app-router]
generated: { by: "reference_agent/trae-cn", at: 2026-04-22T00:00:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-04-22T00:00:00+08:00 }
status: stable
stale_after: 2026-10-22
sources:
  - id: src
    resource: /references/templates-source.md
    title: Trae Templates 源码信源
---

## 示例目标

使用 `nextjs-starter` 模板创建一个 Next.js 14 + TypeScript 项目，并启动开发服务器验证运行。

## 步骤 1：复制模板

```bash
# 创建项目目录
mkdir my-nextjs-app
cd my-nextjs-app

# 复制模板文件（从 trae-templates 仓库）
cp -r /path/to/trae-templates/templates/web-frontend/nextjs-starter/* .
```

或者从 GitHub 直接下载：
1. 打开 trae-templates 仓库
2. 进入 `templates/web-frontend/nextjs-starter/` 目录
3. 下载所有文件到你的项目目录

## 步骤 2：查看文件结构

复制完成后，项目结构如下：

```
my-nextjs-app/
├── package.json        # 依赖声明（Next.js 14、React 18、TypeScript）
├── tsconfig.json       # TypeScript 配置（Module Resolution: Bundler）
├── next.config.mjs     # Next.js 配置
├── .gitignore
├── app/
│   ├── layout.tsx      # 根布局（App Router）
│   └── page.tsx        # 首页组件
└── README.md
```

查看 `app/page.tsx` 了解首页结构，`app/layout.tsx` 了解根布局。

## 步骤 3：安装依赖

```bash
# 使用 npm
npm install

# 或使用 pnpm（推荐）
pnpm install

# 或使用 yarn
yarn install
```

模板不包含 lock 文件，首次安装时会根据你使用的包管理器生成对应的 lock 文件（package-lock.json / pnpm-lock.yaml / yarn.lock）。

## 步骤 4：启动开发服务器

```bash
npm run dev
```

启动成功后，终端会显示：

```
  ▲ Next.js 14.x.x
  - Local:        http://localhost:3000
  - Environments: .env
```

## 步骤 5：验证运行

在浏览器中打开 `http://localhost:3000`，确认页面正常显示。

你应该能看到 Next.js 模板提供的默认首页内容。

## 步骤 6：开始开发

### 添加新页面

在 `app/` 目录下创建新目录和 `page.tsx` 文件：

```
app/
├── about/
│   └── page.tsx    # 访问 /about
└── posts/
    └── page.tsx    # 访问 /posts
```

### 添加 API 路由

在 `app/api/` 目录下创建路由：

```
app/api/
└── hello/
    └── route.ts    # GET /api/hello
```

### 添加组件

创建 `components/` 目录存放可复用组件：

```
components/
├── Header.tsx
└── Footer.tsx
```

### 添加样式

可以选择：
- CSS Modules：创建 `*.module.css` 文件
- Tailwind CSS：安装 `tailwindcss` 并配置
- 全局 CSS：在 `app/globals.css` 中添加（需自行创建）

## 步骤 7：构建生产版本

```bash
npm run build
```

构建产物输出到 `.next/` 目录。

预览生产构建：
```bash
npm start
```

## 与其他模板的组合

### 添加 superpowers AI 工作流

```bash
# 复制 .trae/ 目录到项目根
cp -r /path/to/trae-templates/templates/tools-devops/superpowers-trae-init/.trae .
```

这将添加 AI 开发约束（4 条铁律）和 25+ 个技能到项目中。

### 添加 .editorconfig

```bash
cp /path/to/trae-templates/templates/tools-devops/editor-config/.editorconfig .
```

统一团队编辑器行为（缩进、换行符、字符集等）。

### 添加 .gitignore

模板已包含基础 `.gitignore`。如需 Node.js 完整版：
```bash
cp /path/to/trae-templates/templates/tools-devops/gitignore/Node.gitignore .gitignore
```

## 常见问题

**Q: 端口 3000 被占用怎么办？**
A: 使用 `npm run dev -- -p 3001` 指定其他端口。

**Q: 可以使用 JavaScript 而非 TypeScript？**
A: 模板默认 TypeScript。如需 JavaScript，将 `.tsx` 文件改为 `.jsx`，删除 `tsconfig.json`，修改 `next.config.mjs` 禁用 TypeScript 检查。但推荐使用 TypeScript。

**Q: 为什么模板不包含 app/globals.css？**
A: 遵循最小可用原则，不预设样式方案。你可以自行添加 CSS Modules、Tailwind、CSS-in-JS 等方案。

**Q: 模板不包含路由/状态管理/测试？**
A: 是的，最小可用设计。按需添加：
- 路由：App Router 文件系统路由已内置
- 状态管理：Zustand、Jotai、Redux 等自选
- 测试：Jest + React Testing Library 或 Playwright

## 相关概念

- [Web 前端模板](../concepts/02-web-frontend-templates.md)
- [五维分面分类体系](../concepts/01-template-classification.md)
- [AGENTS.md 开发契约](../concepts/07-agents-contract.md)

## 相关内容

- [源码信源索引](../references/templates-source.md)
- [使用 superpowers-trae-init 初始化环境](use-superpowers-init.md)
- [创建自定义模板](create-custom-template.md)
