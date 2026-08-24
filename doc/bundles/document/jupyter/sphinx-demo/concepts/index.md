# sphinx-demo 核心概念

本文档目录包含 JupyterLite Sphinx Demo 的核心概念文档，从项目入门到部署实战系统讲解 jupyterlite-sphinx 集成的各个层面。

## 概念文档列表

### 入门篇

| 序号 | 文档 | 核心内容 |
|------|------|----------|
| 00 | [项目简介](00-introduction.md) | sphinx-demo定位、jupyterlite-sphinx核心指令、双内核示范、学习路径 |
| 01 | [项目目录结构](01-project-structure.md) | 双示例目录组织、各文件职责、Xeus额外文件、构建输出目录 |
| 02 | [快速开始](02-quick-start.md) | 6步搭建最小站点、安装依赖、conf.py最小配置、构建预览、常见问题 |

### 核心篇

| 序号 | 文档 | 核心内容 |
|------|------|----------|
| 03 | [conf.py配置详解](03-sphinx-conf.md) | 扩展列表、JupyterLite核心配置项、TryExamples配置、MyST配置、主题选项 |
| 04 | [Pyodide与Xeus内核对比](04-kernel-comparison.md) | 包管理差异、conf.py差异点、CI构建需求、选型指南 |
| 05 | [四层配置文件体系](05-config-files.md) | jupyter_lite_config/jupyter-lite/overrides/try_examples分层模型、热加载特性 |
| 06 | [TryExamples交互示例](06-try-examples.md) | 工作原理、三级控制粒度（全局/页面/函数）、按钮CSS定制、预导入代码 |
| 07 | [NotebookLite嵌入](07-notebook-embedding.md) | notebooklite指令、strip_tagged_cells机制方向、code-cell标签、外部Notebook引用 |

### 高级篇

| 序号 | 文档 | 核心内容 |
|------|------|----------|
| 08 | [样式定制与主题扩展](08-customization.md) | 自定义CSS/JS、PyData主题图标链接、版本切换器、编辑按钮 |
| 09 | [CI/CD与GitHub Pages部署](09-ci-deployment.md) | 触发条件、矩阵并行构建、artifact聚合、gh-pages部署、本地验证 |
| 10 | [禁用交互示例三级控制](10-disabling-examples.md) | 全局开关/ignore_patterns/disable_try_examples注释、组合策略、手动按钮 |

## 推荐学习路径

1. **入门**：[00-简介](00-introduction.md) → [01-目录结构](01-project-structure.md) → [02-快速开始](02-quick-start.md)
2. **配置**：[03-conf.py配置](03-sphinx-conf.md) → [05-四层配置](05-config-files.md)
3. **内核选型**：[04-Pyodide vs Xeus](04-kernel-comparison.md)
4. **交互功能**：[06-TryExamples](06-try-examples.md) → [07-NotebookLite](07-notebook-embedding.md) → [10-禁用控制](10-disabling-examples.md)
5. **高级主题**：[08-样式定制](08-customization.md) → [09-CI/CD部署](09-ci-deployment.md)
6. **动手实践**：前往[实践示例](/examples/index.md)跟着教程构建完整站点

```{toctree}
:hidden:

00-introduction
01-project-structure
02-quick-start
03-sphinx-conf
04-kernel-comparison
05-config-files
06-try-examples
07-notebook-embedding
08-customization
09-ci-deployment
10-disabling-examples
```
