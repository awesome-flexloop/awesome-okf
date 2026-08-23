---
type: Reference
title: 构建配置源码信源
description: litegitpuller的pyproject.toml和package.json构建配置、依赖声明、打包规则的源码信源登记
tags: [build, hatchling, jupyter-builder, npm, pyproject, package-json]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:55:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T15:55:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: source-build-config
    resource: /references/build-config-source.md
    title: 构建配置源码信源
---

## 文件位置

- Python构建配置：`pyproject.toml`
- npm/前端构建配置：`package.json`
- setuptools 兼容入口：`setup.py`（仅含 `__import__("setuptools").setup()`）

## pyproject.toml 构建系统

### 构建后端

- **build-backend**: `hatchling.build`
- **requires**: `hatchling>=1.5.0`, `jupyterlab>=4.0.0,<5`, `hatch-nodejs-version>=0.3.2`

### 项目元数据

- name: `litegitpuller`
- requires-python: `>=3.8`
- dependencies: 空列表（无运行时依赖）
- version: 从 package.json 动态获取（`tool.hatch.version.source = "nodejs"`）

### 可选依赖

**docs** 组：
- `jupyterlite-sphinx>=0.9.3`
- `jupyterlite-xeus-python>=0.9.0,<0.10.0`
- `myst-parser`
- `pydata_sphinx_theme`
- `sphinx>=4`

### 构建目标映射（wheel shared-data）

| 源路径 | 安装目标 |
|--------|---------|
| `litegitpuller/labextension` | `share/jupyter/labextensions/@jupyterlite/litegitpuller` |
| `install.json` | `share/jupyter/labextensions/@jupyterlite/litegitpuller/install.json` |

### hatch-jupyter-builder 配置

- **build-function**: `hatch_jupyter_builder.npm_builder`
- **ensured-targets**: `litegitpuller/labextension/static/style.js`, `litegitpuller/labextension/package.json`
- **生产构建命令**: `build:prod`（npm 脚本），使用 `jlpm`
- **开发构建命令**: `install:extension`（npm 脚本），使用 `jlpm`，source_dir 为 `src`，build_dir 为 `litegitpuller/labextension`

### sdist 配置

- artifacts: `litegitpuller/labextension`
- exclude: `.github`, `binder`

## package.json 关键配置

### 包信息

- name: `@jupyterlite/litegitpuller`
- version: `0.3.0`
- main: `lib/index.js`（编译输出）
- types: `lib/index.d.ts`
- style: `style/index.css`
- outputDir: `litegitpuller/labextension`

### 运行时依赖

| 包 | 版本范围 |
|----|---------|
| `@jupyterlab/application` | `^4.0.0` |
| `@jupyterlab/coreutils` | `^6.0.0` |
| `@jupyterlab/filebrowser` | `^4.0.0` |
| `@jupyterlab/services` | `^7.0.0` |

### npm 脚本

| 脚本 | 命令 |
|------|------|
| `build` | `jlpm build:lib && jlpm build:labextension:dev` |
| `build:prod` | `jlpm clean && jlpm build:lib:prod && jlpm build:labextension` |
| `build:lib` | `tsc --sourceMap` |
| `build:lib:prod` | `tsc` |
| `build:labextension` | `jupyter labextension build .` |
| `watch` | `run-p watch:src watch:labextension` |
| `test` | `jest --coverage` |
| `lint` | `jlpm stylelint && jlpm prettier && jlpm eslint` |

### 发布文件

- `lib/**/*.{d.ts,eot,gif,html,jpg,js,js.map,json,png,svg,woff2,ttf}`
- `style/**/*.{css,js,eot,gif,html,jpg,json,png,svg,woff2,ttf}`

### JupyterLab 扩展配置

```json
"jupyterlab": {
  "extension": true,
  "outputDir": "litegitpuller/labextension"
}
```
