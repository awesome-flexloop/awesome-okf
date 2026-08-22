---
title: 项目简介
type: concept
bundle: jupyter-notebook
chapter: "00"
difficulty: beginner
tags: ["overview", "introduction"]
prerequisites: []
sources: ["F-001", "F-002", "F-003"]
---

# 00 | 项目简介

## Jupyter Notebook 是什么

Jupyter Notebook 是一个基于Web的交互式计算环境，允许用户创建和共享包含实时代码、方程式、可视化和叙事文本的文档。它支持超过40种编程语言，广泛应用于数据科学、机器学习、学术研究和教育领域。

> **信源**: [pyproject.toml](/references/00-source-registry.md#S-001) 中description定义为 "Jupyter Notebook - A web-based notebook environment for interactive computing"（F-001）

## v7 的核心变革

Jupyter Notebook 7.x 是一次**架构级重写**，与6.x版本有本质区别：

| 维度 | Notebook 6.x | Notebook 7.x |
|------|-------------|-------------|
| 前端实现 | 独立的JavaScript前端 | 基于JupyterLab前端 |
| 后端 | 独立Tornado应用 | Jupyter Server扩展 + JupyterLab基座 |
| 插件系统 | 自定义nbextension | JupyterLab LabExtension |
| 构建系统 | setuptools + webpack | Hatchling + Lerna + Lumino |
| 兼容层 | 原生 | notebook_shim包桥接 |

### v7 的本质

Notebook v7 的核心定位是 **JupyterLab的"经典模式"发行版**：

1. 它复用JupyterLab的全部核心能力（文档管理、渲染引擎、插件系统）
2. 通过自定义 `NotebookShell` 提供更简洁的单文档布局
3. 通过 `notebook_shim` 兼容层支持v6配置项
4. 通过 `@jupyter-notebook/*` 命名空间的前端包提供Notebook专属UI

## 生态定位

```
┌─────────────────────────────────────────────┐
│         Jupyter Notebook v7                  │
│  ┌─────────────────────────────────────┐    │
│  │   Notebook Shell + Shim Layer       │    │
│  │   (6区域布局 + 配置兼容)             │    │
│  └──────────────┬──────────────────────┘    │
│                 │ 继承/复用                  │
│  ┌──────────────▼──────────────────────┐    │
│  │         JupyterLab 4.x               │    │
│  │  (插件系统/文档管理/渲染引擎/UI组件)  │    │
│  └──────────────┬──────────────────────┘    │
│                 │ 依赖                       │
│  ┌──────────────▼──────────────────────┐    │
│  │       Jupyter Server 2.x             │    │
│  │  (REST API/Kernel管理/认证/静态文件)  │    │
│  └──────────────┬──────────────────────┘    │
│                 │ 依赖                       │
│  ┌──────────────▼──────────────────────┐    │
│  │        Jupyter Client / Core         │    │
│  │  (Kernel协议/配置路径/路径管理)       │    │
│  └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

## 版本与依赖

### 核心依赖版本

| 依赖 | 版本要求 | 作用 |
|------|---------|------|
| Python | >=3.10 | 运行时环境（F-001） |
| jupyter_server | >=2.19.0 | 后端服务器框架（F-003） |
| jupyterlab | >=4.7.0a1 | 前端基座（F-003） |
| notebook_shim | >=0.2.4 | v6配置兼容层（F-003） |
| tornado | >=6.2.0 | Web服务器框架（F-003） |

### 技术栈

- **后端**: Python + Tornado + traitlets（配置系统）
- **前端**: TypeScript + Lumino（Widget框架）+ React
- **构建**: Hatchling（Python包）+ Lerna（前端monorepo）
- **发布**: jupyter-releaser（F-005）

## 为什么要学习源码

1. **插件开发**: 理解Notebook v7的插件机制 = 理解JupyterLab插件开发
2. **定制化**: 企业部署需要自定义认证、UI主题、API端点
3. **排障**: 遇到启动失败、扩展冲突等问题时需要定位到源码
4. **贡献**: 向Jupyter生态提交PR需要理解代码结构

## 下一步

→ [架构总览](./01-architecture-overview.md) 理解前后端分离架构与请求生命周期
