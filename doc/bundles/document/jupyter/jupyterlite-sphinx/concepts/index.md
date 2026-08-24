# Concepts — 概念文档

Concepts 是 jupyterlite-sphinx 的系统性知识文档，按学习路径分三个篇章：入门篇→核心篇→高级篇。每个概念文档基于源码事实，提供原理讲解、API 参考和用法示例。

## 入门篇

| 文档 | 内容 |
|------|------|
| [00-introduction](00-introduction.md) | jupyterlite-sphinx 核心功能、架构概览、适用场景 |
| [01-installation](01-installation.md) | 安装方法、依赖说明、conf.py 最小配置 |
| [02-quick-start](02-quick-start.md) | 从零开始：安装→配置→构建→嵌入第一个 JupyterLab |
| [03-directive-overview](03-directive-overview.md) | 五个指令对比、通用选项说明（width/height/prompt/new_tab/theme等） |

## 核心篇

| 文档 | 内容 |
|------|------|
| [04-jupyterlite-directive](04-jupyterlite-directive.md) | `.. jupyterlite::` 嵌入完整 JupyterLab，支持 Notebook 文件打开 |
| [05-notebooklite-directive](05-notebooklite-directive.md) | `.. notebooklite::` 嵌入经典 Notebook（retrolite 别名），.ipynb 文件自动解析 |
| [06-replite-directive](06-replite-directive.md) | `.. replite::` 嵌入交互式 REPL，预填代码、内核选择、REPL 行为定制 |
| [07-voici-directive](07-voici-directive.md) | `.. voici::` 嵌入 Voici 仪表板，voici 包依赖检查 |
| [08-try-examples-directive](08-try-examples-directive.md) | `.. try_examples::` doctest 转交互式 Notebook，autodoc 自动注入，移动端适配 |
| [09-configuration](09-configuration.md) | 所有 conf.py 配置项详解：JupyterLite构建、TryExamples全局配置、REPL行为、运行时配置 |

## 高级篇

| 文档 | 内容 |
|------|------|
| [10-build-process](10-build-process.md) | Sphinx 构建生命周期钩子、jupyter lite build 命令行构造、文件复制流程 |
| [11-node-hierarchy](11-node-hierarchy.md) | docutils 自定义节点继承体系、HTML 生成方法、访问器注册机制 |
| [12-frontend-js](12-frontend-js.md) | 前端 JavaScript 函数、iframe 懒加载、移动端检测、ConfigLoader 运行时热配置 |

```{toctree}
:hidden:

00-introduction
01-installation
02-quick-start
03-directive-overview
04-jupyterlite-directive
05-notebooklite-directive
06-replite-directive
07-voici-directive
08-try-examples-directive
09-configuration
10-build-process
11-node-hierarchy
12-frontend-js
```
