---
type: Concept
title: MyST-NB 简介
description: MyST-NB 是什么——定位、核心能力、与 MyST-Parser 的关系、适用场景
tags: [myst-nb, introduction, jupyter, notebook, myst]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:30:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: mystnb-source
    resource: /references/mystnb-source.md
    title: MyST-NB 源码路径映射
---

## MyST-NB 简介

**MyST-NB**（MyST Notebook）是 Executable Books 生态中用于解析和执行 Jupyter Notebook 的 Sphinx 扩展和 docutils 解析器，版本 **v1.5.0.dev**。它建立在 MyST-Parser 之上，使 Sphinx 能够将 `.ipynb` 文件和 MyST 文本格式 Notebook（`.md`，标记为 `file_format: mystnb`）作为文档源文件，自动执行代码 cell 并渲染输出。

## 定位与核心能力

MyST-NB 在 MyST-Parser 的基础上增加了 **Jupyter Notebook 执行与渲染**能力：

- ✅ **双格式输入**：支持标准 `.ipynb` Jupyter Notebook 和 MyST 文本格式 Notebook（Markdown 中嵌入 code-cell）
- ✅ **自动代码执行**：5 种执行模式（off/auto/force/cache/inline），集成 nbclient 和 jupyter-cache
- ✅ **多格式输出渲染**：MIME 类型优先级系统，自动选择 HTML/图片/Markdown/LaTeX/Widget 等输出格式
- ✅ **Glue 变量粘贴**：在代码中「粘贴」变量，文档任意位置引用（跨页面）
- ✅ **Eval 内联求值**：在 Markdown 正文中内联插入代码计算结果
- ✅ **细粒度控制**：全局/文件/Cell 三层配置覆盖，精确控制代码隐藏、输出滚动、错误处理
- ✅ **ipywidgets 支持**：自动加载 RequireJS 和 Jupyter Widgets JS
- ✅ **Sphinx/Docutils 双模式**：既作为 Sphinx 扩展，也可独立通过 CLI 使用
- ✅ **并行构建安全**：parallel_read_safe 和 parallel_write_safe 均为 True

## 与 MyST-Parser 的关系

MyST-NB 不是 MyST-Parser 的替代品，而是其 **超集扩展**：

| 层级 | MyST-Parser | MyST-NB |
|------|-------------|---------|
| 输入格式 | `.md`（MyST Markdown） | `.md`（MyST）+ `.ipynb` + `.md`（mystnb 格式） |
| 代码处理 | 仅作为静态代码块渲染 | 执行代码 cell 并渲染输出 |
| 变量系统 | 无 | Glue 粘贴 + Eval 求值 |
| MIME 渲染 | 无 | MIME 优先级 + 多输出格式 |
| 依赖 | 无 Jupyter 依赖 | myst-parser + nbclient + nbformat + jupyter-cache + ipython |
| 配置 | `myst_*` 前缀 | `nb_*` 前缀（叠加在 `myst_*` 之上） |

架构上，MyST-NB 的 Parser 类继承 MyST-Parser 的 Parser，sphinx_setup() 先调用 `setup_myst_parser(app)` 初始化 MyST-Parser 基础配置，再叠加 MyST-NB 特有配置和扩展。

## 四阶段处理管线

MyST-NB 的核心处理流程为四阶段（对比 MyST-Parser 的三阶段增加了「执行」阶段）：

```
输入文件 (.ipynb / .md[mystnb])
    │
    ▼
[读取层] read.py → NotebookNode (nbformat)
    │
    ▼
[执行层] execute/ → 执行代码 cell，填充 outputs
    │
    ▼
[转换层] nb_to_tokens.py → markdown-it Token 流
    │
    ▼
[渲染层] render.py → docutils AST 节点
    │
    ▼
Sphinx/Docutils 输出（HTML/LaTeX/...）
```

## 适用场景

- **计算型文档**：包含可执行代码的技术文档、教程、报告
- **数据分析报告**：在文档中嵌入代码和可视化输出
- **教学材料**：可执行的 Jupyter Notebook 教程书籍
- **科学论文**：包含公式和可复现计算结果的学术文档
- **快速原型**：在纯 Markdown 中编写可执行 notebook，无需启动 Jupyter

## 相关概念

- [快速开始](01-getting-started.md)
- [MyST Notebook 文件格式](02-notebook-format.md)
- [四阶段解析管线](03-processing-pipeline.md)
- [配置系统](04-config-system.md)
