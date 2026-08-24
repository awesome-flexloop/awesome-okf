---
type: OKF
title: xeus-lite-demo 教程
description: JupyterLite xeus 内核部署模板的系统化教程，涵盖 GitHub 模板部署、双环境配置、多语言内核（Python/R/C++）、CI/CD 流水线和插件扩展
tags: [xeus-lite, jupyterlite, xeus, wasm, conda, github-pages, deployment, python, r, cpp]
okf_version: "0.2"
source: https://github.com/jupyterlite/xeus-lite-demo
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:05:00+08:00" }
status: stable
stale_after: 2027-08-22
---

# xeus-lite-demo 教程

xeus-lite-demo 是一个 GitHub 模板仓库，让你在几分钟内部署一个完全运行在浏览器中的 Jupyter Notebook 站点。它通过 [JupyterLite](https://jupyterlite.readthedocs.io/) + [xeus](https://xeus.readthedocs.io/) 原生内核 + GitHub Actions 自动化，实现零后端、零安装、零运维的 Notebook 部署体验。

本教程基于源码深度分析，系统讲解 xeus-lite-demo 的核心概念、双环境架构、部署流程、多语言内核配置和插件扩展。

## 📚 快速导航

### [概念文档](concepts/index.md)
- [00-xeus-lite-demo 简介](concepts/00-introduction.md) — 是什么、解决什么问题、核心特性一览
- [01-xeus 与 JupyterLite 生态](concepts/01-xeus-jupyterlite.md) — xeus、JupyterLite、emscripten-forge 技术栈关系
- [02-双环境模型](concepts/02-dual-environment.md) — 构建环境 vs 运行时环境，两个 yml 文件的本质区别
- [03-GitHub 模板三步部署](concepts/03-github-template-deploy.md) — 三步创建自己的 JupyterLite 站点
- [04-运行时环境配置](concepts/04-runtime-env-config.md) — environment.yml 详解、channels、dependencies、可用包
- [05-构建环境配置](concepts/05-build-env-config.md) — build-environment.yml 详解、插件安装
- [06-CI/CD 流水线](concepts/06-cicd-pipeline.md) — GitHub Actions 双 job 流程详解
- [07-多语言内核支持](concepts/07-kernel-options.md) — Python/R/C++/Lua 内核配置与选择指南
- [08-内容目录与 Notebook](concepts/08-content-and-notebooks.md) — content/ 目录管理、数据文件组织

### [实践示例](examples/index.md)
- [01-创建第一个部署](examples/01-first-deployment.md) — 10分钟零工具部署第一个站点
- [02-Python 科学计算环境](examples/02-numpy-matplotlib.md) — NumPy/Pandas/Matplotlib 配置
- [03-R 内核统计分析](examples/03-r-kernel.md) — xeus-r + tidyverse 统计教学环境
- [04-C++ 交互式编程](examples/04-cpp-kernel.md) — xeus-cpp 交互式 C++ 编程
- [05-添加 JupyterLite 插件](examples/05-add-jupyterlite-plugins.md) — 终端等插件安装

### [信源参考](references/index.md)
- [README 使用说明](references/readme-source.md) — 三步部署流程原文
- [运行时环境配置](references/environment-source.md) — environment.yml 完整内容
- [构建环境配置](references/build-env-source.md) — build-environment.yml 完整内容
- [CI/CD 流水线](references/deploy-workflow-source.md) — deploy.yml 完整工作流
- [示例 Notebook](references/demo-notebook-source.md) — demo.ipynb 内容解析

### 补充材料
- [事实清单](facts.md) — R 阶段采集的 56 条零推测事实
- [架构洞察](insights.md) — I 阶段提炼的 4 个核心洞察

## 🚀 快速开始

### 三步部署你的站点

1. **Use this template** → 在 [xeus-lite-demo 仓库](https://github.com/jupyterlite/xeus-lite-demo)点击绿色按钮创建你的仓库
2. **Enable GitHub Pages** → Settings → Pages → Source 选 "GitHub Actions"
3. **自定义 environment.yml** → 添加你需要的包（如 numpy、matplotlib），commit 后自动部署

等 3-5 分钟，访问 `https://{用户名}.github.io/{仓库名}/` 即可使用。

### 默认演示

默认配置包含 xeus-python 内核和 ipycanvas，打开 demo.ipynb 可以看到一个笑脸绘制示例，验证环境正常工作。

## 🎯 核心特性

| 特性 | 说明 |
|------|------|
| 🔧 GitHub 模板 | 一键创建部署仓库，无需本地配置 |
| 🚀 自动部署 | push 到 main 自动构建部署到 GitHub Pages |
| 🐍 多语言支持 | Python、R、C++、Lua 内核可选 |
| 📦 conda 包管理 | 通过 emscripten-forge 使用熟悉的 environment.yml |
| 📓 Notebook 兼容 | 标准 .ipynb 格式，放入 content/ 即可 |
| 🔌 插件扩展 | 支持 jupyterlite-terminal 等插件 |
| 🌐 纯静态站点 | HTML/JS/WASM，可托管任意静态服务器 |
| 💰 零成本 | GitHub Pages 免费托管 |

## 🏗️ 架构概览

```
用户浏览器（WASM 运行时）
┌─────────────────────────────────────────┐
│  JupyterLite UI (Notebook/Lab)          │
│  ├─ xeus-python (CPython WASM)          │
│  ├─ xeus-r (R WASM)                     │
│  ├─ xeus-cpp (C++ WASM)                 │
│  └─ 用户包 (numpy/matplotlib/...)        │
└─────────────────────────────────────────┘
         ▲ 静态文件
         │
GitHub Pages (静态托管)
         ▲ dist/ 产物
         │
GitHub Actions (CI 构建)
┌─────────────────────────────────────────┐
│  micromamba → jupyter lite build        │
│  ├─ build-env: jupyterlite-core + xeus  │
│  ├─ 读取 environment.yml → 下载WASM包   │
│  └─ 打包 content/ → 静态站点            │
└─────────────────────────────────────────┘
```

## 📖 推荐学习路径

1. **入门**：阅读 [00-简介](concepts/00-introduction.md) → [01-生态概览](concepts/01-xeus-jupyterlite.md) → 跟着 [01-第一个部署](examples/01-first-deployment.md) 动手
2. **理解核心**：学习 [02-双环境模型](concepts/02-dual-environment.md)（最重要的概念！）→ [04-运行时配置](concepts/04-runtime-env-config.md) → [05-构建配置](concepts/05-build-env-config.md)
3. **自动化**：阅读 [06-CI/CD流水线](concepts/06-cicd-pipeline.md) 理解自动部署原理
4. **多语言**：根据需要阅读 [07-多语言内核](concepts/07-kernel-options.md) → 动手做 [02-Python](examples/02-numpy-matplotlib.md)/[03-R](examples/03-r-kernel.md)/[04-C++](examples/04-cpp-kernel.md) 示例
5. **扩展**：学习 [08-内容管理](concepts/08-content-and-notebooks.md) → [05-插件安装](examples/05-add-jupyterlite-plugins.md)

```{toctree}
:hidden:

concepts/index
examples/index
references/index
facts
insights
log
```
