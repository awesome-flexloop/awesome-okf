---
type: Concept
title: sphinx-demo 与 jupyterlite-sphinx 简介
description: sphinx-demo 项目是什么、jupyterlite-sphinx 扩展提供什么能力、本 Wiki 的内容定位与学习路径
tags: [introduction, jupyterlite-sphinx, overview]
difficulty: beginner
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: readme
    resource: /references/conf-py-source.md
    title: sphinx-demo README
---

## 项目定位

sphinx-demo 是 `jupyterlite-sphinx` 扩展的官方演示项目。它展示了如何将 JupyterLite（浏览器内 Jupyter 环境）集成到 Sphinx 文档站点中，让读者在阅读文档时可以直接在浏览器中运行 Python 代码，无需本地安装 Python 环境。

### 核心价值

- **零安装交互**：文档读者点击按钮即可在浏览器中运行代码示例
- **双内核示范**：同时展示 Pyodide（纯 WebAssembly CPython）和 Xeus（emscripten-forge 预编译环境）两种内核
- **完整配置参考**：从 conf.py 到 CI/CD 部署，覆盖 JupyterLite 文档站点的所有配置层面
- **最佳实践示范**：TryExamples 按钮、Notebook 嵌入、CSS 定制、版本切换等实际用法

### jupyterlite-sphinx 提供的核心指令

| 指令 | 功能 |
|------|------|
| `.. jupyterlite::` | 嵌入可操作的 JupyterLab 环境 |
| `.. notebooklite::` | 嵌入可交互的 Jupyter Notebook |
| `.. replite::` | 嵌入 REPL（交互式代码执行器） |
| `.. try_examples::` | 在代码示例旁添加"Try it online"按钮 |
| `.. voici::` | 嵌入 Voici 仪表板 |

当 `global_enable_try_examples=True` 时，`autodoc` 自动从 NumPy 风格 docstring 的 Examples 节生成 TryExamples 按钮，无需手动添加指令。

### 双内核并行示范

项目包含两个结构相同但内核不同的示例站点：

- **pyodide-kernel-example**：使用 Pyodide 内核，通过 piplite 在运行时安装包
- **xeus-kernel-example**：使用 Xeus 内核，通过 environment.yml 在构建时预装包

两个示例共享相同的 Sphinx 配置模板，通过根目录的版本切换器（switcher.json）实现一键切换。

## 学习路径

建议按以下顺序学习本 Wiki：

1. **[02-quick-start](/concepts/02-quick-start.md)**：从零搭建一个最小可运行站点
2. **[03-sphinx-conf](/concepts/03-sphinx-conf.md)**：理解 conf.py 中每个配置项的作用
3. **[04-kernel-comparison](/concepts/04-kernel-comparison.md)**：选择适合你项目的内核
4. **[05-config-files](/concepts/05-config-files.md)**：掌握四层 JSON 配置文件体系
5. **[06-try-examples](/concepts/06-try-examples.md)**：为文档添加交互式代码示例
6. **[09-ci-deployment](/concepts/09-ci-deployment.md)**：配置自动构建和部署

## 相关内容

- [02-quick-start](/concepts/02-quick-start.md)：快速开始教程
- [03-sphinx-conf](/concepts/03-sphinx-conf.md)：conf.py 配置详解
- [/examples/01-minimal-site.md](/examples/01-minimal-site.md)：最小站点示例
