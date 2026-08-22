---
type: Example
title: 本地预览与构建示例
description: npm ci、docs:dev 本地预览、docs:build 构建和 docs:preview 预览的命令使用示例及自动部署流程说明。
tags: [trae-learning, vitepress, example, preview, build, npm-scripts]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/learning-source.md
    title: "Trae Learning 源码信源"
---

# 本地预览与构建示例

本示例演示如何在本地启动开发服务器、构建站点和预览生产版本。

## 前置条件

- 已安装 Node.js（推荐 LTS 版本）
- 已克隆项目仓库
- 在项目根目录下执行命令

## 安装依赖

```bash
npm ci
```

使用 `npm ci` 而非 `npm install` 以确保依赖版本与 lock 文件一致。

## 启动开发服务器（本地预览）

```bash
npm run docs:dev
```

VitePress 开发服务器启动后，通常在以下地址访问：

```
http://localhost:5173/trae-learning/
```

注意路径包含 `/trae-learning/`（对应 config.js 中的 `base` 配置）。

开发服务器支持热更新——修改 Markdown 或组件文件后，浏览器会自动刷新。

## 构建生产版本

```bash
npm run docs:build
```

构建产物输出到 `.vitepress/dist` 目录。这是 GitHub Pages 部署时上传的目录。

构建完成后检查：

- 无构建错误
- 所有页面正确生成
- 静态资源（图片、CSS、JS）路径正确

## 预览生产构建

```bash
npm run docs:preview
```

在本地启动静态文件服务器，预览构建后的生产版本。用于在部署前验证构建结果是否正确。

## 部署到 GitHub Pages

项目已配置 GitHub Actions 自动部署。只需将代码 push 到 main 分支：

```bash
git add .
git commit -m "docs: add new tutorial"
git push origin main
```

Push 后自动触发 `.github/workflows/deploy.yml`：

1. **build job**：在 ubuntu-latest 上使用 Node.js 20 安装依赖、构建站点、上传产物
2. **deploy job**：使用 `actions/deploy-pages@v4` 部署到 GitHub Pages

也可以在仓库的 Actions 页面手动触发（workflow_dispatch）。

## 本地开发常用命令总结

| 命令 | 用途 | 场景 |
|------|------|------|
| `npm ci` | 安装依赖 | 首次克隆或依赖更新后 |
| `npm run docs:dev` | 启动开发服务器 | 日常编写文档时 |
| `npm run docs:build` | 构建生产版本 | 提交前验证构建 |
| `npm run docs:preview` | 预览生产构建 | 部署前最终验证 |

## 相关链接

- [GitHub Pages 部署](/concepts/05-deploy-pages.md)
- [VitePress 站点架构](/concepts/01-vitepress-setup.md)
- [自定义主题开发](/concepts/02-custom-theme.md)
- [添加新教程文档示例](/examples/add-tutorial.md)
