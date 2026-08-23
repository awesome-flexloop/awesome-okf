---
okf_version: "0.2"
type: reference
title: "构建配置源码（pyproject.toml与package.json）"
description: "Python与Node.js双构建系统配置：hatchling后端、jupyter-builder钩子、npm构建脚本与labextension打包"
tags: [build-system, hatchling, pyproject-toml, package-json, jupyter-builder, labextension, wheel, hatch-nodejs-version]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T13:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pyproject-toml
    resource: "../../../../../external/libs/jupyter/jupyterlab_pygments/pyproject.toml"
    title: "pyproject.toml"
  - id: package-json
    resource: "../../../../../external/libs/jupyter/jupyterlab_pygments/package.json"
    title: "package.json"
  - id: install-json
    resource: "../../../../../external/libs/jupyter/jupyterlab_pygments/install.json"
    title: "install.json"
  - id: setup-py
    resource: "../../../../../external/libs/jupyter/jupyterlab_pygments/setup.py"
    title: "setup.py"
---

# 构建配置源码（pyproject.toml 与 package.json）

本信源登记 Python 与 Node.js 双构建系统的配置文件：`pyproject.toml`（Python 包构建）、`package.json`（Node.js/前端构建）、`install.json`（JupyterLab 安装元数据）、`setup.py`（兼容 shim）。jupyterlab_pygments 是一个典型的 JupyterLab 预构建扩展（prebuilt extension），采用双语言构建流水线。

## pyproject.toml — Python 构建配置

### 构建系统声明

```toml
[build-system]
requires = [
    "hatchling>=1.5.0",
    "jupyterlab>=4.0.0,<5",
    "hatch-nodejs-version>=0.3.2",
]
build-backend = "hatchling.build"
```

- 使用 `hatchling` 作为构建后端（现代 Python 包构建工具）
- 构建时依赖 `jupyterlab>=4.0.0,<5`（提供 `jupyter labextension build` 命令）
- 构建时依赖 `hatch-nodejs-version>=0.3.2`（从 package.json 读取版本号）

### 项目元数据

```toml
[project]
name = "jupyterlab_pygments"
readme = "README.md"
requires-python = ">=3.8"
dependencies = []
dynamic = ["version", "description", "authors", "urls", "keywords"]
```

- Python 版本要求：≥ 3.8
- `dependencies = []`: 未声明运行时依赖（实际运行需要 pygments，但未在此显式声明，由 JupyterLab 环境隐含提供）
- 版本、描述、作者等元数据标记为 `dynamic`，由 hatch-nodejs-version 从 package.json 动态读取

### 版本源配置

```toml
[tool.hatch.version]
source = "nodejs"
```

版本号来源于 Node.js 的 `package.json` 文件，确保 Python 包和 npm 包版本一致。

### 元数据钩子

```toml
[tool.hatch.metadata.hooks.nodejs]
fields = ["description", "authors", "urls"]
```

从 package.json 同步 description、authors、urls 字段到 Python 包元数据。

### 源码分发包配置

```toml
[tool.hatch.build.targets.sdist]
artifacts = ["jupyterlab_pygments/labextension"]
exclude = [".github", "binder"]
```

- sdist 中包含预构建的 `labextension/` 目录
- 排除 `.github/` 和 `binder/` 开发目录

### Wheel 包数据映射

```toml
[tool.hatch.build.targets.wheel.shared-data]
"jupyterlab_pygments/labextension" = "share/jupyter/labextensions/jupyterlab_pygments"
"install.json" = "share/jupyter/labextensions/jupyterlab_pygments/install.json"
```

Wheel 包的核心映射关系：
- `jupyterlab_pygments/labextension/` → 安装到 `share/jupyter/labextensions/jupyterlab_pygments/`
- `install.json` → 安装到同一目录下
- 这是 JupyterLab 发现预构建扩展的标准路径

### Jupyter Builder 构建钩子

```toml
[tool.hatch.build.hooks.jupyter-builder]
dependencies = ["hatch-jupyter-builder>=0.5"]
build-function = "hatch_jupyter_builder.npm_builder"
ensured-targets = [
    "jupyterlab_pygments/labextension/static/style.js",
    "jupyterlab_pygments/labextension/package.json",
]
skip-if-exists = ["jupyterlab_pygments/labextension/static/style.js"]
```

- 使用 `hatch-jupyter-builder` 的 `npm_builder` 函数
- 构建时自动执行 npm 构建流水线
- `ensured-targets`: 构建后必须存在的文件列表
- `skip-if-exists`: 如果目标文件已存在则跳过构建（支持可编辑安装）

### 构建参数

```toml
[tool.hatch.build.hooks.jupyter-builder.build-kwargs]
build_cmd = "build:prod"
npm = ["jlpm"]

[tool.hatch.build.hooks.jupyter-builder.editable-build-kwargs]
build_cmd = "install:extension"
npm = ["jlpm"]
source_dir = "src"
build_dir = "jupyterlab_pygments/labextension"
```

- 生产构建使用 `build:prod` 命令
- 可编辑安装使用 `install:extension` 命令
- 使用 `jlpm`（JupyterLab 包管理器，yarn 的封装）作为 npm 客户端

## package.json — Node.js/前端构建配置

### 基本信息

```json
{
    "name": "jupyterlab_pygments",
    "version": "0.3.0",
    "description": "Pygments theme using JupyterLab CSS variables",
    "license": "BSD-3-Clause",
    "main": "lib/index.js",
    "types": "lib/index.d.ts",
    "style": "style/index.css",
    "styleModule": "style/index.js"
}
```

- 版本 0.3.0
- `main`: TypeScript 编译输出入口
- `types`: TypeScript 类型声明入口
- `style`: CSS 入口文件（用于工具消费）
- `styleModule`: JS 样式模块入口（JupyterLab 扩展系统识别此字段加载 CSS）

### JupyterLab 扩展配置

```json
"jupyterlab": {
    "extension": true,
    "outputDir": "jupyterlab_pygments/labextension"
}
```

- `"extension": true`: 标记为 JupyterLab 扩展
- `"outputDir"`: 构建输出目录（与 Python 包映射路径对应）

### 构建脚本

| 脚本 | 命令 | 说明 |
|------|------|------|
| `build` | `jlpm build:css && jlpm build:lib && jlpm build:labextension:dev` | 完整开发构建 |
| `build:css` | `python generate_css.py` | 从 Python Style 生成 CSS |
| `build:lib` | `tsc` | 编译 TypeScript |
| `build:labextension` | `jupyter labextension build .` | 构建 labextension（生产） |
| `build:labextension:dev` | `jupyter labextension build --development True .` | 构建 labextension（开发模式） |
| `build:prod` | `jlpm clean && jlpm build:css && jlpm build:lib && jlpm build:labextension` | 完整生产构建 |
| `clean:lib` | `rimraf lib tsconfig.tsbuildinfo style/base.css` | 清理编译产物 |
| `watch` | `run-p watch:src watch:labextension` | 并行监听 TS 和 labextension |

### 依赖关系

**运行时依赖（dependencies）：**
- `@jupyterlab/application: ^4.0.8` — JupyterLab 应用 API
- `@types/node: ^20.9.0` — Node.js 类型定义

**开发依赖（devDependencies）：**
- `@jupyterlab/builder: ^4.0.0` — JupyterLab 扩展构建工具
- `typescript: ~5.0.2` — TypeScript 编译器
- `eslint`/`prettier`/`stylelint` 等代码质量工具
- `rimraf`/`npm-run-all` 等构建工具

### sideEffects 声明

```json
"sideEffects": ["style/*.css", "style/index.js"]
```

告知 webpack 等打包工具这些文件有副作用（CSS 注入），不应在 tree-shaking 时移除。

## install.json — JupyterLab 安装元数据

```json
{
  "packageManager": "python",
  "packageName": "jupyterlab_pygments",
  "uninstallInstructions": "Use your Python package manager (pip, conda, etc.) to uninstall the package jupyterlab_pygments"
}
```

- `packageManager: "python"`: 标记为 Python 包管理的扩展
- `packageName`: Python 包名
- 提供卸载说明

## setup.py — 兼容 Shim

```python
__import__("setuptools").setup()
```

- 仅一行代码，调用 `setuptools.setup()`
- 存在是为了兼容旧版本 pip（不支持 pyproject.toml-only 的构建）
- 实际构建逻辑完全由 pyproject.toml 中的 hatchling 配置驱动

## 构建流程总览

```
pip install jupyterlab_pygments
    │
    ▼
hatchling 读取 pyproject.toml
    │
    ├── hatch-nodejs-version: 从 package.json 读取版本号
    │
    └── hatch-jupyter-builder (npm_builder)
         │
         ▼
    jlpm install (安装 npm 依赖)
         │
         ▼
    build:prod 流程:
         ├── clean (清理旧产物)
         ├── build:css → python generate_css.py → style/base.css
         ├── build:lib → tsc → lib/index.js
         └── build:labextension → jupyter labextension build .
              │
              ▼
         jupyterlab_pygments/labextension/ (构建产物)
              │
              ▼
    wheel 打包:
    ├── labextension/ → share/jupyter/labextensions/jupyterlab_pygments/
    └── install.json → share/jupyter/labextensions/jupyterlab_pygments/install.json
```
