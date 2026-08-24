---
type: OKF
title: JupyterLite Sphinx Demo 教程
description: jupyterlite-sphinx 官方演示项目的系统化教程，涵盖Sphinx配置、Pyodide/Xeus双内核、TryExamples交互按钮、Notebook嵌入、CI/CD部署
tags: [jupyterlite-sphinx, sphinx, jupyterlite, documentation, pyodide, xeus, try-examples, notebooklite, github-pages]
okf_version: "0.2"
version: "0.1.0"
source: https://github.com/jupyterlite/sphinx-demo
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
status: stable
stale_after: 2027-08-22
---

# JupyterLite Sphinx Demo 教程

sphinx-demo 是 `jupyterlite-sphinx` 扩展的官方演示项目，展示了如何将 JupyterLite（浏览器内 Jupyter 环境）完整集成到 Sphinx 文档站点中。它同时示范了 Pyodide 和 Xeus 两种内核的配置方式，覆盖 TryExamples 交互按钮、Notebook 嵌入、四层 JSON 配置、自定义样式和 GitHub Actions 自动部署的最佳实践。

本教程基于 sphinx-demo 源码深度分析，系统讲解从最小站点搭建到双内核 CI/CD 部署的完整流程。

## 📚 快速导航

### [概念文档](concepts/index.md)

**入门篇**
- [00-项目简介](concepts/00-introduction.md) — sphinx-demo 是什么、jupyterlite-sphinx 提供的核心指令、学习路径
- [01-项目目录结构](concepts/01-project-structure.md) — 双示例目录组织、文件职责速查、构建输出
- [02-快速开始](concepts/02-quick-start.md) — 从零搭建第一个交互文档站点

**核心篇**
- [03-conf.py 配置详解](concepts/03-sphinx-conf.md) — 扩展列表、JupyterLite 核心配置、TryExamples、主题选项
- [04-Pyodide 与 Xeus 内核对比](concepts/04-kernel-comparison.md) — 双内核差异、包管理方式、选型指南
- [05-四层配置文件体系](concepts/05-config-files.md) — jupyter_lite_config/jupyter-lite/overrides/try_examples 分层模型
- [06-TryExamples 交互示例](concepts/06-try-examples.md) — 工作原理、三级控制、按钮定制、热加载特性
- [07-NotebookLite 嵌入](concepts/07-notebook-embedding.md) — notebooklite 指令、strip_tagged_cells 机制、code-cell 标签

**高级篇**
- [08-样式定制与主题扩展](concepts/08-customization.md) — 自定义 CSS/JS、PyData 主题配置、版本切换器
- [09-CI/CD 与 GitHub Pages 部署](concepts/09-ci-deployment.md) — 矩阵并行构建、artifact 聚合、gh-pages 部署
- [10-禁用交互示例三级控制](concepts/10-disabling-examples.md) — 全局/页面/函数级禁用策略与最佳实践

### [实践示例](examples/index.md)
- [01-最小可运行站点](examples/01-minimal-site.md) — 从安装依赖到构建预览的6步教程
- [02-Pyodide 内核完整配置](examples/02-pyodide-setup.md) — 含CSS定制、四层JSON、示例模块的完整站点
- [03-Xeus 内核完整配置](examples/03-xeus-setup.md) — environment.yml 包管理、micromamba 构建、与Pyodide差异
- [04-嵌入可交互 Matplotlib 笔记本](examples/04-matplotlib-notebook.md) — NotebookLite+Matplotlib可视化、strip标签实战

### [信源参考](references/index.md)
- [conf.py 配置项速查](references/conf-py-source.md) — 所有配置项的类型、默认值、取值说明
- [JSON 配置文件字段速查](references/json-config-source.md) — 四个JSON文件的完整字段登记
- [GitHub Actions 工作流解析](references/ci-workflow-source.md) — CI工作流的步骤、矩阵、部署配置

## 🚀 快速体验

```bash
# 克隆项目
git clone https://github.com/jupyterlite/sphinx-demo.git
cd sphinx-demo/pyodide-kernel-example

# 安装依赖
pip install -r requirements.txt

# 构建文档
cd docs
make html

# 预览
cd build/html && python -m http.server 8000
# 访问 http://localhost:8000
```

打开浏览器后，你将看到嵌入了 JupyterLab 的文档站点，每个代码示例旁都有 "Try it online" 按钮。

## 🎯 核心特性

| 特性 | 说明 |
|------|------|
| 📝 双内核示范 | Pyodide 和 Xeus 并行示例，95%配置相同，差异仅5处 |
| 🔘 TryExamples | 自动为 docstring 示例添加"在线运行"按钮，三级控制粒度 |
| 📓 NotebookLite | 嵌入可交互 Notebook，strip_tagged_cells 实现文档/Notebook内容分离 |
| ⚙️ 四层配置 | 构建时/运行时/插件/交互行为分层管理，try_examples.json支持热更新 |
| 🎨 样式定制 | 自定义CSS美化按钮、PyData主题图标链接、版本切换器 |
| 🚀 CI/CD | GitHub Actions矩阵并行构建双站点，自动部署到GitHub Pages |

## 🏗️ 架构概览

```
┌─────────────────────────────────────────────────────────┐
│                   Sphinx 文档构建层                       │
│  conf.py → extensions (jupyterlite_sphinx, myst_nb)     │
│  ├─ global_enable_try_examples → 自动插入按钮             │
│  ├─ strip_tagged_cells → Notebook单元格剥离              │
│  └─ jupyterlite_contents → 预装内容复制                   │
├─────────────────────────────────────────────────────────┤
│                 四层 JSON 配置层                          │
│  jupyter_lite_config.json (构建时) → no_sourcemaps       │
│  jupyter-lite.json (运行时) → appName, defaultKernel    │
│  overrides.json (插件) → 工具栏按钮                      │
│  try_examples.json (热更新) → iframe高度, 页面排除        │
├─────────────────────────────────────────────────────────┤
│               JupyterLite 浏览器运行时                     │
│  ┌─────────────┐  ┌──────────────┐                       │
│  │  Pyodide     │  │  Xeus        │                       │
│  │  piplite     │  │  environment │                       │
│  │  (运行时装包) │  │  (构建时预装) │                       │
│  └─────────────┘  └──────────────┘                       │
├─────────────────────────────────────────────────────────┤
│                 CI/CD 部署层                              │
│  GitHub Actions: matrix(pyodide, xeus) → build → deploy  │
│  gh-pages: /pyodide/ + /xeus/ + index.html              │
└─────────────────────────────────────────────────────────┘
```

## 📖 推荐学习路径

1. **快速上手**：[02-快速开始](concepts/02-quick-start.md) → [01-最小站点示例](examples/01-minimal-site.md)，10分钟搭建第一个交互文档
2. **理解配置**：[03-conf.py配置](concepts/03-sphinx-conf.md) → [05-四层配置文件](concepts/05-config-files.md)，掌握所有配置项
3. **选择内核**：[04-内核对比](concepts/04-kernel-comparison.md)，决定使用Pyodide还是Xeus
4. **添加交互**：[06-TryExamples](concepts/06-try-examples.md) → [07-Notebook嵌入](concepts/07-notebook-embedding.md)，让文档活起来
5. **定制外观**：[08-样式定制](concepts/08-customization.md)，打造品牌化文档
6. **自动部署**：[09-CI/CD部署](concepts/09-ci-deployment.md)，配置GitHub Actions自动发布

```{toctree}
:hidden:

concepts/index
examples/index
references/index
spec/facts
spec/insights
facts
insights
```
