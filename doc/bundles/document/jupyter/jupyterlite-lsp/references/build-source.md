---
type: Reference
title: 构建系统源码引用（dodo.py + package.json）
description: doit 构建脚本、根 package.json、lerna.json、webpack 配置等构建系统源码引用
tags: [source, build, doit, lerna, webpack]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: dodo-py
    resource: ../../../../../../external/libs/jupyter/jupyterlite-lsp/dodo.py
    title: dodo.py
  - id: root-package
    resource: ../../../../../../external/libs/jupyter/jupyterlite-lsp/package.json
    title: package.json（根）
  - id: lerna-json
    resource: ../../../../../../external/libs/jupyter/jupyterlite-lsp/lerna.json
    title: lerna.json
  - id: lsp-webpack
    resource: ../../../../../../external/libs/jupyter/jupyterlite-lsp/packages/lsp/webpack.config.js
    title: packages/lsp/webpack.config.js
  - id: binder-env
    resource: ../../../../../../external/libs/jupyter/jupyterlite-lsp/.binder/environment.yml
    title: .binder/environment.yml
---

## 构建工具链

| 工具 | 版本/用途 |
|------|----------|
| **doit** | Python 任务运行器，dodo.py 定义所有构建任务 |
| **lerna 6.0.3** | JS monorepo 管理，npmClient 为 jlpm（JupyterLab 包管理器） |
| **yarn workspaces** | workspaces 模式，packages/* 为工作区 |
| **flit_core** | Python 包构建后端 |
| **jupyter labextension build** | JS 扩展构建（基于 webpack 5） |
| **prettier** | JS/Python 代码格式化 |
| **sphinx** | 文档构建（pydata-sphinx-theme + myst-nb） |

## 根 package.json 脚本

| 脚本 | 命令 | 用途 |
|------|------|------|
| `build:ext` | `lerna run labextension:build` | 构建 JupyterLab 扩展 |
| `build:lib` | `lerna run build` | 构建 TypeScript 库 |
| `dist:npm` | `lerna run dist:npm` | 打包 npm 包 |
| `dist:py` | `flit build` | 构建 Python wheel/sdist |
| `docs:sphinx` | `sphinx-build -b html docs build/docs` | 构建文档 |
| `lite:build` | `cd examples && jupyter lite build` | 构建 JupyterLite 示例站点 |
| `setup:js` | `jlpm --prefer-offline ...` | 安装 JS 依赖 |
| `setup:py:ext` | `jupyter labextension develop . --overwrite` | 开发模式安装扩展 |
| `setup:py:pip` | `pip install -e .` | 可编辑模式安装 Python 包 |
| `watch` | `lerna run --parallel --stream watch` | 并行监听所有包的变更 |

## dodo.py 关键任务

### task_copy
- 将 LICENSE.txt 复制到每个 package 目录
- 将 README.md 复制到 packages/lsp/ 目录

### task_hack:connection.js
- **前置依赖**：lite:build 产物（jupyter-lite 构建完成后）
- **操作**：将 jupyterlab-lsp 的 connection.js 中 `new WebSocket` 替换为 `new window.MockWebSocket`
- **目标文件**：`build/lite/extensions/@krassowski/jupyterlab-lsp/static/321.0176abf53bb1a24b854d.js`

### task_binder
- 执行 setup 后输出就绪信息
- 开发命令：`jupyter lab --no-browser --debug`
- 监听命令：`jlpm watch`（另一终端）

### task_dist:hash
- 计算 dist/ 下所有产物的 SHA256 哈希

## doit 任务自动加载

`globals().update(U.load_package_json_tasks())` 将 package.json#/doit/tasks 中定义的任务自动转换为 doit 任务。任务命名规则：`<prefix>:<name>`，如 `build:ext`、`setup:js` 等。

## webpack 配置（两包相同）

```javascript
module.exports = {
  output: { clean: true },
  devtool: 'source-map',
  module: {
    rules: [{ test: /\.js$/, use: ['source-map-loader'] }],
  },
};
```

## 开发环境依赖（.binder/environment.yml）

| 类别 | 包 |
|------|-----|
| 构建 | nodejs >=18,<19; python >=3.8,<3.12; doit-with-toml; flit |
| JupyterLab | jupyterlab >=3.5,<4.0; jupyterlab-lsp >=3.10.2 |
| 格式化 | black; docformatter; isort; pydocstyle; ssort |
| 文档 | pydata-sphinx-theme; myst-nb; sphinx-copybutton |
| JupyterLite | jupyterlite ==0.1.0b15（pip安装） |

## 构建流程顺序

```
setup:js → setup:py:pip → setup:py:ext → build:lib → build:ext → lite:build → hack:connection.js → dist:py + dist:npm
```

## 相关概念

- [构建系统详解](/concepts/07-build-system.md)
- [本地开发环境搭建](/examples/local-dev-setup.md)
- [Python包与Labextension注册](/concepts/08-python-package.md)
