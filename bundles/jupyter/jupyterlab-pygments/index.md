---
okf_version: "0.2"
type: bundle
title: "jupyterlab_pygments"
description: "连接 Pygments 语法高亮与 JupyterLab 主题系统的轻量双桥组件：Python Style类通过CSS变量桥接CodeMirror主题，构建时生成静态CSS，前端以空插件注入。"
---

# jupyterlab_pygments

> Pygments 语法高亮 × JupyterLab 主题系统——CSS 变量驱动的双语言桥接组件

`jupyterlab_pygments` 是一个轻量级但设计精巧的 JupyterLab 扩展，它解决了一个具体问题：让 Pygments 生成的语法高亮 HTML 自动跟随 JupyterLab 主题（浅色/深色/高对比度）切换颜色。核心方案是 CSS 变量桥接——Python 端定义引用 `var(--jp-mirror-editor-*)` 的 Pygments Style 类，构建时转换为静态 CSS，前端以空插件形式注入页面。

## 快速导航

### 📘 核心概念（6 篇）

**入门**
- [简介](concepts/00-introduction.md) — 项目定位、核心问题、双桥方案概览、生态位置
- [5分钟快速上手](concepts/01-getting-started.md) — 安装、验证、使用 JupyterStyle 生成高亮 HTML

**核心**
- [双桥架构解析](concepts/02-dual-bridge-architecture.md) — Python→CSS→JS 三层桥接设计、构建时vs运行时、CSS变量跨语言契约
- [JupyterStyle 类详解](concepts/03-jupyter-style-class.md) — 继承体系、styles 字典完整映射、22个CSS变量、Pygments vs CodeMirror token差异

**进阶**
- [CSS 生成流水线](concepts/04-css-generation-pipeline.md) — HtmlFormatter.get_style_defs()、.highlight前缀过滤、base.css生成与间接引入
- [构建系统与扩展机制](concepts/05-build-and-extension.md) — hatchling + jupyter-builder双语言构建、预构建扩展加载、wheel数据映射、sideEffects
- [概念文档索引](concepts/index.md) — 概念文档总目录

### 💻 示例代码（2 个）

- [自定义语法高亮样式](examples/01-customize-style.md) — 子类化JupyterStyle扩展token映射、重新生成CSS、构建扩展
- [在Jupyter环境中使用Pygments高亮](examples/02-pygments-highlight.md) — Notebook渲染、完整HTML生成、多语言对比、nbconvert集成
- [示例文档索引](examples/index.md) — 示例总目录

### 📄 源码信源（5 个文件）

- [style.py](references/style-py-source.md) — JupyterStyle 类定义、token→CSS变量映射
- [__init__.py](references/init-py-source.md) — 包入口、版本导入、扩展路径注册
- [generate_css.py](references/generate-css-source.md) — Python→CSS转换器
- [src/index.ts + style/](references/index-ts-source.md) — TypeScript空插件、CSS模块入口
- [构建配置](references/build-config-source.md) — pyproject.toml + package.json 双构建系统配置
- [源码信源索引](references/index.md) — 信源文档总目录

## 版本信息

| 属性 | 值 |
|------|-----|
| 版本 | **0.3.0** |
| Python 版本要求 | ≥ 3.8 |
| JupyterLab 版本 | ≥ 4.0.0, < 5 |
| Pygments 依赖 | ≥ 2.4.1 |
| 构建系统 | Hatchling + hatch-jupyter-builder + hatch-nodejs-version |
| 前端编译 | TypeScript ~5.0.2 + @jupyterlab/builder ^4.0.0 |
| 核心Python代码 | 约 181 行（3个文件） |
| 核心TypeScript代码 | 17 行（1个文件） |
| 许可证 | BSD-3-Clause |
| 源码路径 | `external/libs/jupyter/jupyterlab_pygments/` |

## 核心洞察

jupyterlab_pygments 虽然代码量极小（不到200行Python + 17行TypeScript），但体现了三个值得学习的设计模式：

1. **构建时代码生成桥接跨语言系统**：Python Style类在构建时通过Pygments的HtmlFormatter"编译"为CSS，运行时零开销
2. **CSS变量作为跨语言契约**：`var(--jp-mirror-editor-*)` 变量名是Python端和JS端之间的隐式API，无需任何运行时通信
3. **空插件模式（CSS-only Extension）**：TypeScript插件的activate函数为空，仅通过styleModule注入CSS，实现最小前端足迹

---

**推荐阅读顺序：** [简介](concepts/00-introduction.md) → [快速上手](concepts/01-getting-started.md) → [双桥架构](concepts/02-dual-bridge-architecture.md) → [JupyterStyle类](concepts/03-jupyter-style-class.md) → [CSS生成流水线](concepts/04-css-generation-pipeline.md) → [构建系统](concepts/05-build-and-extension.md)
