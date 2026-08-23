---
type: Reference
title: p5-kernel 项目元信源
description: p5-kernel 项目的版本、依赖、目录结构、构建配置等元信息登记
tags: [metasource, p5-kernel, jupyterlite, metadata]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T17:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: root-pkg
    resource: https://github.com/jupyterlite/p5-kernel/blob/main/package.json
    title: 根 package.json
  - id: kernel-pkg
    resource: https://github.com/jupyterlite/p5-kernel/blob/main/packages/p5-kernel/package.json
    title: @jupyterlite/p5-kernel package.json
  - id: ext-pkg
    resource: https://github.com/jupyterlite/p5-kernel/blob/main/packages/p5-kernel-extension/package.json
    title: @jupyterlite/p5-kernel-extension package.json
  - id: pyproject
    resource: https://github.com/jupyterlite/p5-kernel/blob/main/pyproject.toml
    title: pyproject.toml
---

## 项目基本信息

| 属性 | 值 |
|------|-----|
| 项目名 | jupyterlite-p5-kernel |
| GitHub | https://github.com/jupyterlite/p5-kernel |
| 许可证 | BSD-3-Clause |
| 根包版本 | 0.4.0-a2 |
| npm 包版本 | 0.4.0-alpha.2 |
| Python 包名 | jupyterlite-p5-kernel |
| Python 要求 | >=3.10 |
| 包管理 | yarn workspaces + lerna (independent 版本模式) |
| 构建后端 | hatchling + hatch-nodejs-version + hatch-jupyter-builder |

## 目录结构

```
p5-kernel/
├── packages/
│   ├── p5-kernel/                    # npm 包 @jupyterlite/p5-kernel
│   │   ├── src/
│   │   │   ├── index.ts              # 入口：re-export kernel + executor
│   │   │   ├── kernel.ts             # P5Kernel 类实现
│   │   │   ├── executor.ts           # P5Executor 类实现
│   │   │   └── p5-docs.ts            # 自动生成的 p5.js API 文档映射
│   │   ├── scripts/
│   │   │   └── generate-p5-docs.mjs  # 从 @types/p5 生成文档映射
│   │   ├── style/                    # CSS 样式
│   │   └── package.json
│   └── p5-kernel-extension/          # npm 包 @jupyterlite/p5-kernel-extension
│       ├── src/
│       │   ├── index.ts              # JupyterLab 插件注册
│       │   └── declarations.d.ts     # PNG 模块声明
│       ├── style/
│       │   └── icons/p5js.png        # p5.js logo
│       └── package.json
├── jupyterlite_p5_kernel/
│   ├── __init__.py                   # Python 包入口（labextension 路径注册）
│   └── _version.py                   # 版本文件（hatch 自动生成）
├── examples/                         # 示例 notebooks
│   ├── intro.ipynb
│   ├── particle-system.ipynb
│   ├── flow-field.ipynb
│   ├── interactive-circles.ipynb
│   ├── recursive-tree.ipynb
│   ├── spiral-galaxy.ipynb
│   └── external-packages.ipynb
├── install.json                      # JupyterLab 扩展安装元数据
├── pyproject.toml                    # Python 构建配置
├── lerna.json                        # Lerna 配置
└── package.json                      # 根 monorepo 配置
```

## npm 依赖关系

### @jupyterlite/p5-kernel

| 依赖 | 版本 | 用途 |
|------|------|------|
| @jupyterlab/nbformat | ^4.5.0 | Jupyter notebook 格式类型（IMimeBundle） |
| @jupyterlite/javascript-kernel | ^0.4.0-alpha.3 | 基础 JavaScript 内核（P5Kernel 继承自此） |
| @jupyterlite/services | ^0.7.0 | JupyterLite 内核服务（IKernel, IKernelSpecs 等） |
| @types/p5 (dev) | ^1.7.7 | p5.js 类型定义（用于文档生成） |
| typescript (dev) | ~5.0.2 | TypeScript 编译器 |

### @jupyterlite/p5-kernel-extension

| 依赖 | 版本 | 用途 |
|------|------|------|
| @jupyterlab/application | ^4.5.0 | JupyterLab 前端应用插件 API |
| @jupyterlite/p5-kernel | ^0.4.0-alpha.2 | 依赖内核包 |
| @jupyterlite/services | ^0.7.0 | 内核规格注册 API |
| @jupyterlab/builder (dev) | ^4.5.5 | JupyterLab 扩展构建工具 |

### 共享包配置

```json
{
  "@jupyterlite/services": {
    "bundled": false,
    "singleton": true
  }
}
```

`@jupyterlite/services` 标记为 singleton，确保与 JupyterLite 主应用共享同一实例。

## Python 包配置

- 构建后端：hatchling >= 1.5.0
- 版本来源：nodejs（从 package.json 读取）
- 构建钩子：hatch-jupyter-builder（自动执行 npm build:prod）
- 无运行时依赖（`dependencies = []`）
- wheel 数据文件：
  - `jupyterlite_p5_kernel/labextension/` → `share/jupyter/labextensions/@jupyterlite/p5-kernel-extension/`
  - `install.json` → `share/jupyter/labextensions/@jupyterlite/p5-kernel-extension/install.json`

## 默认 CDN 配置

- p5.js 默认 CDN：`https://cdn.jsdelivr.net/npm/p5@1.9.0/lib/p5.js`
- 可通过 JupyterLab PageConfig `p5Url` 选项覆盖
- 本地 URL 自动拼接 origin
