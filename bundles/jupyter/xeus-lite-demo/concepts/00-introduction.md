---
type: Concept
title: xeus-lite-demo 简介
description: xeus-lite-demo 是什么、解决什么问题、核心特性一览
tags: [introduction, xeus-lite, jupyterlite, overview, getting-started]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:05:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: readme
    resource: /references/readme-source.md
    title: README 使用说明信源
---

## 什么是 xeus-lite-demo

xeus-lite-demo 是一个 GitHub 模板仓库，用于快速创建带有自定义 conda 包集合的 [JupyterLite](https://jupyterlite.readthedocs.io/) 部署。它将 JupyterLite 的静态站点能力与 [xeus](https://xeus.readthedocs.io/) 原生内核结合，让你可以在浏览器中运行 Python、R、C++ 等编程语言的 Notebook，无需任何后端服务器。

简单来说：点几下鼠标，你就能获得一个完全运行在浏览器中的 Jupyter Notebook 站点，并且可以预装 numpy、matplotlib 等科学计算包。

## 它解决什么问题

传统的 Jupyter 部署需要：
- 一台服务器（本地或云端）
- 安装 Python/R/C++ 环境
- 配置 Jupyter Server
- 管理用户访问和安全

xeus-lite-demo 将这些全部消除：
- **零后端**：所有代码在用户浏览器的 WebAssembly (WASM) 虚拟机中运行
- **零安装**：用户打开网页即可使用，无需本地安装任何东西
- **零运维**：部署到 GitHub Pages 等静态托管服务，自动 HTTPS、全球 CDN
- **可定制**：通过 `environment.yml` 声明需要的包，GitHub Actions 自动构建

## 核心特性

| 特性 | 说明 |
|------|------|
| 🔧 GitHub 模板 | 点击 "Use this template" 即可创建自己的部署仓库 |
| 🚀 自动部署 | push 到 main 分支自动构建并部署到 GitHub Pages |
| 🐍 多语言内核 | 支持 Python（xeus-python）、R（xeus-r）、C++（xeus-cpp） |
| 📦 conda 包生态 | 通过 emscripten-forge 访问数百个预编译为 WASM 的 conda 包 |
| 📓 Notebook 兼容 | 支持标准 .ipynb 格式，放入 `content/` 目录即可访问 |
| 🔌 插件扩展 | 支持安装 jupyterlite-terminal 等 JupyterLite 插件 |
| 🌐 纯静态 | 构建产物为 HTML/JS/WASM 文件，可托管在任意静态服务器 |

## 与其他 JupyterLite 方案的区别

| 方案 | 内核 | 包管理 | 部署方式 |
|------|------|--------|---------|
| JupyterLite 官方 (Pyodide) | Pyodide Python | micropip (PyPI WASM) | CLI 手动构建 |
| **xeus-lite-demo** | **xeus 原生内核** | **conda (emscripten-forge)** | **GitHub Actions 全自动** |

xeus-lite 的核心优势是使用 conda 包管理——这意味着你可以用熟悉的 `environment.yml` 声明依赖，而不是手动管理 PyPI 的 WASM 包列表。

## 谁应该使用

- **教学场景**：快速创建一个包含特定包（如 numpy、matplotlib）的在线 Notebook 环境，学生无需安装即可使用
- **演示/分享**：将数据分析 Notebook 分享给他人，对方打开链接即可交互运行
- **轻量计算**：不需要 GPU 或大量内存的计算任务，可以直接在浏览器中完成
- **原型验证**：快速搭建一个可交互的数据分析环境，验证想法

## 相关概念

- [xeus 与 JupyterLite 生态](01-xeus-jupyterlite.md) — 理解 xeus、JupyterLite、emscripten-forge 之间的关系
- [GitHub 模板三步部署](03-github-template-deploy.md) — 手把手创建第一个部署
- [双环境模型](02-dual-environment.md) — 理解两个 environment.yml 文件的区别
