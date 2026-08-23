---
type: Concept
title: "架构总览：双内核体系与静态站点生成"
description: "Try Jupyter的核心架构：Pyodide+Xeus双内核并存、声明式配置驱动、Pixi编排构建管线、静态站点生成到GitHub Pages部署的完整链路。"
tags: [architecture, jupyterlite, pyodide, xeus, kernel, static-site, build-pipeline]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:50:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: pyproject
    resource: "/references/pyproject-source.md"
    title: "pyproject.toml 项目配置"
  - id: config
    resource: "/references/config-source.md"
    title: "配置文件信源"
  - id: scripts
    resource: "/references/scripts-source.md"
    title: "构建脚本信源"
  - id: ci
    resource: "/references/ci-source.md"
    title: "CI/CD工作流信源"
---

# 架构总览：双内核体系与静态站点生成

Try Jupyter 的架构围绕一个核心设计：**将完整的Jupyter环境编译为纯静态文件**，通过GitHub Pages分发，用户在浏览器中通过WASM（WebAssembly）执行代码。

## 核心架构分层

```
┌─────────────────────────────────────────────────────────┐
│                    用户浏览器                             │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │  JupyterLab  │  │   Notebook7  │  │   Terminal    │  │
│  │   (主界面)    │  │   (经典界面)  │  │  (Cockle)     │  │
│  └──────┬───────┘  └──────┬───────┘  └───────┬───────┘  │
│         │                 │                  │          │
│  ┌──────┴─────────────────┴──────────────────┴───────┐  │
│  │           JupyterLite Core (浏览器端Jupyter框架)     │  │
│  └──┬──────────┬──────────┬──────────┬──────────────┬─┘  │
│     ↓          ↓          ↓          ↓              ↓    │
│  ┌──────┐ ┌────────┐ ┌────────┐ ┌────────┐  ┌─────────┐ │
│  │Pyodide│ │Xeus-   │ │Xeus-Cpp│ │Xeus-R  │  │Xeus-    │ │
│  │Python│ │Python  │ │ (C++23)│ │  (R)   │  │SQLite   │ │
│  │内核  │ │内核    │ │        │ │        │  │         │ │
│  └──────┘ └────────┘ └────────┘ └────────┘  └─────────┘ │
│     ↓          ↓          ↓          ↓              ↓    │
│  ┌──────────────────────────────────────────────────┐    │
│  │        WASM 运行时 (浏览器WebAssembly)             │    │
│  └──────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                          ↑
                          │ 静态文件 (HTML/JS/WASM/数据)
                          │
┌─────────────────────────────────────────────────────────┐
│              GitHub Pages (静态文件托管)                  │
└─────────────────────────────────────────────────────────┘
                          ↑
                          │ jupyter lite build
┌─────────────────────────────────────────────────────────┐
│                    构建管线 (CI/本地)                     │
│  Pixi → JupyterLite CLI → 后处理脚本 → dist/            │
└─────────────────────────────────────────────────────────┘
```

## 双内核体系：Pyodide + Xeus

Try Jupyter 同时搭载两套独立的Python内核体系，并通过Xeus框架支持C++/R/SQLite等多语言内核：

### Pyodide 内核

- **包名**：`jupyterlite-pyodide-kernel`（≥0.8.0,<0.9）
- **技术基础**：CPython编译为WASM，由Pyodide项目维护
- **特点**：对Python科学计算生态兼容性最好，预装大量包
- **包来源**：Pyodide包仓库（pyodide.org）

### Xeus 内核框架

- **包名**：`jupyterlite-xeus`（≥5.0.0,<6）
- **技术基础**：Xeus是一个C++实现的Jupyter内核协议库，可编译为WASM
- **特点**：支持多语言内核，通过conda-forge emscripten-forge通道分发WASM包
- **支持的内核**：

| 内核 | 环境文件 | 预装包 |
|------|---------|--------|
| Xeus-Python | environment-python.yml | numpy, matplotlib, pillow, ipywidgets, ipyleaflet, scipy |
| Xeus-Cpp (C++23) | environment-cpp.yml | symengine, xtensor-blas, xsimd |
| Xeus-R | environment-r.yml | r-ggplot2 |
| Xeus-SQLite | environment-sqlite.yml | xeus-sqlite |

### 内核过滤机制

构建后通过 `scripts/filter_xeus_kernels.py` 脚本过滤，最终只保留5个内核ID：
- `xpython`（Xeus-Python）
- `xcpp23`、`xc23`（C++23，两个ID均保留）
- `xr`（R）
- `xsqlite`（SQLite）

> Pyodide内核不经过此过滤，它由jupyterlite-pyodide-kernel包直接提供。

## 静态站点生成流程

JupyterLite 将整个Jupyter环境编译为纯静态文件（HTML + JavaScript + WASM + 数据）：

```
content/              → 用户notebook和数据文件
environment-*.yml     → Xeus内核环境定义
jupyter-lite.json     → 站点配置
jupyter_lite_config.json → 构建配置
                        ↓ jupyter lite build
dist/                 → 完整静态站点
  ├── lab/            → JupyterLab界面
  ├── repl/           → REPL控制台
  ├── xeus/           → Xeus内核文件
  │   └── kernels.json → 内核列表（被后处理过滤）
  ├── pyodide/        → Pyodide内核文件
  ├── notebooks/      → 打包后的notebook
  └── index.html      → 入口页面
```

## 构建管线

构建和部署由Pixi任务编排，分为三个阶段：

### 阶段1：构建（`pixi run build`）

执行 `jupyter lite build`，完成：
- 安装JupyterLab和扩展
- 打包content/目录
- 编译Xeus内核环境（下载emscripten-forge的WASM包）
- 生成静态站点到dist/

### 阶段2：后处理（两个脚本）

1. **过滤内核**（`pixi run filter-kernels`）：修改 `dist/xeus/kernels.json`，只保留5个精选内核
2. **注入分析**（`pixi run add-plausible`）：用BeautifulSoup解析dist/下所有HTML，在`<head>`中注入Plausible分析脚本

### 阶段3：测试与部署

- **测试**：Playwright自动打开每个notebook，执行所有cell，验证无错误
- **部署**：main分支通过GitHub Actions部署到GitHub Pages

## 配置驱动架构

整个站点的行为由JSON/YAML声明式配置控制，无需编写应用代码：

| 配置文件 | 控制层面 | 核心配置项 |
|---------|---------|-----------|
| `jupyter-lite.json` | 站点运行时 | appName、禁用扩展、终端可用性 |
| `jupyter_lite_config.json` | 构建时 | 输出目录、内容目录、Xeus环境文件 |
| `environment-*.yml` | 内核环境 | 每个内核的包依赖 |
| `cockle-config-in.json` | 终端 | 预安装包、命令别名、环境变量 |
| `repl/jupyter-lite.json` | REPL模式 | REPL专属禁用扩展 |

## 禁用扩展策略

浏览器端Jupyter环境无法使用需要后端服务的扩展，因此显式禁用了：

### 主站禁用（jupyter-lite.json）

| 扩展 | 原因 |
|------|------|
| `@jupyterlab/server-proxy` | 需要后端服务器代理 |
| `jupyterlab-server-proxy` | 同上 |
| `nbdime-jupyterlab` | 需要后端Git支持 |

### REPL额外禁用（repl/jupyter-lite.json）

| 扩展 | 原因 |
|------|------|
| `@jupyterlab/drawio-extension` | REPL不需要图表编辑 |
| `jupyterlab-kernel-spy` | REPL模式不需要内核监控 |
| `jupyterlab-tour` | REPL用户不需要新手引导 |

## 预装扩展与库

除了核心JupyterLab/Notebook，站点还预装了丰富的扩展：

| 类别 | 包 |
|------|---|
| 交互式Widget | ipywidgets 8.x, bqplot, ipycanvas, ipyleaflet, ipympl |
| 可视化 | matplotlib, plotly |
| 文件查看器 | jupyterlab-fasta（FASTA序列）、jupyterlab-geojson（地理数据） |
| 主题 | jupyterlab-night（暗色主题） |
| 语言包 | 法语（fr-FR）、中文（zh-CN） |
| 终端 | jupyterlite-terminal（Cockle WASM终端） |
| URL参数 | jupyterlab-open-url-parameter（支持`?path=`参数打开notebook） |

## 相关概念

- [配置系统](03-configuration-system.md)
- [内核生态](04-kernel-ecosystem.md)
- [构建管线](05-build-pipeline.md)
- [Notebook内容与数据](06-notebooks-and-content.md)
- [部署](08-deployment.md)
