---
type: Reference
title: 项目元数据信源
description: repo2jupyterlite 项目的版本信息、依赖、构建配置和目录结构登记
tags: [meta, setup, build, dependencies]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T16:00:00+08:00" }
verified: { by: "process:grep-api-verify", at: "2026-08-22T16:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: setup-py
    resource: ../../../../../../external/libs/jupyter/repo2jupyterlite/setup.py
    title: setup.py 包配置
  - id: env-yml
    resource: ../../../../../../external/libs/jupyter/repo2jupyterlite/environment.yml
    title: environment.yml Conda环境
  - id: pkg-json
    resource: ../../../../../../external/libs/jupyter/repo2jupyterlite/package.json
    title: package.json 前端依赖
  - id: webpack-config
    resource: ../../../../../../external/libs/jupyter/repo2jupyterlite/webpack.config.js
    title: webpack.config.js 前端构建配置
---

## 项目基本信息

| 属性 | 值 |
|------|-----|
| 包名 | `repo2jupyterlite` |
| 版本 | `0.2` |
| 描述 | Build JupyterLite bundles from code repositories |
| 作者 | Yuvi Panda (yuvipanda@gmail.com) |
| 许可证 | 3-BSD |
| 仓库 | https://github.com/jupyterlite/repo2jupyterlite/ |
| Python版本要求 | `&gt;=3.10` |

## Python 依赖

核心依赖（setup.py install_requires）：

| 包名 | 说明 |
|------|------|
| `jupyterlite-core[all]` | JupyterLite 核心（含所有可选依赖） |
| `jupyterlite-xeus-python` | Xeus Python 内核（WASM） |
| `jupyter-repo2docker` | 仓库内容提供者框架 |
| `yarl` | URL 处理库 |

BinderLite 额外运行时依赖（environment.yml）：

| 包名 | 说明 |
|------|------|
| `mamba` | 快速包管理器 |
| `fastapi` | Web 框架 |
| `uvicorn` | ASGI 服务器 |
| `nodejs` | JavaScript 运行时（前端构建） |
| `pip` | Python 包管理器 |
| `escapism` | 字符串安全编码（run.py 导入） |
| `tornado` | 异步HTTP客户端（github.py 使用） |
| `traitlets` | 配置系统（github.py 使用） |
| `jinja2` | 模板引擎（FastAPI Jinja2Templates） |
| `python-multipart` | FastAPI 表单处理 |
| `aiofiles` | 异步文件操作 |

## 前端依赖（package.json）

运行时依赖：

| 包名 | 版本 | 说明 |
|------|------|------|
| `bootstrap` | ^5.2.3 | CSS 框架 |
| `react` | ^18.2.0 | React 核心 |
| `react-dom` | ^18.2.0 | React DOM 渲染 |

开发依赖：Babel 7.x、Webpack 5.x、相关 loader 和 html-webpack-plugin。

## 构建流程

1. **Python 包构建**：`setup.py` 中 `setup()` 调用前先执行 `npm i &amp;&amp; npm run build`，即先构建前端资源
2. **前端构建**：`npm run build` 调用 webpack，将 React 应用打包到 `binderlite/static/`，HTML 模板输出到 `binderlite/templates/index.html`
3. **入口点**：`repo2jupyterlite = repo2jupyterlite.app:main`（CLI命令）

## 目录结构

```
repo2jupyterlite/
├── repo2jupyterlite/          # Python CLI 包
│   ├── __init__.py            # 空文件
│   └── app.py                 # CLI 入口（main/fetch/build）
├── repoproviders/             # 仓库提供者模块
│   ├── __init__.py            # 空文件
│   ├── github.py              # GitHubRepoProvider（Tornado+traitlets）
│   └── utils.py               # Cache LRU 缓存类
├── binderlite/                # BinderLite Web 应用
│   ├── __init__.py            # 空文件
│   ├── run.py                 # FastAPI 应用与路由
│   ├── publish.py             # Publisher 抽象与 LocalFilesystemPublisher
│   ├── static/                # 前端静态资源（webpack输出）
│   │   └── wordmark.svg       # Logo
│   └── templates/             # Jinja2 模板（webpack生成index.html）
├── src/                       # 前端源码
│   ├── App.jsx                # React 主组件
│   ├── App.css                # 样式
│   └── detectors.js           # URL 解析检测器
├── setup.py                   # Python 包配置
├── environment.yml            # Conda 环境定义
├── package.json               # Node.js 依赖与脚本
├── webpack.config.js          # Webpack 构建配置
└── README.md                  # 项目说明
```
