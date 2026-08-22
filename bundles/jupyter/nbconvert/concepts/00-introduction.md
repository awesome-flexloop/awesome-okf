---
okf_version: "0.2"
type: "concept"
title: "nbconvert 简介"
description: "Jupyter Notebook转换工具：nbconvert是什么、核心能力、项目信息与安装方法"
tags: [introduction, overview, jupyter, notebook-conversion]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: pyproject
    resource: ../references/factory-source.md
    title: "导出器工厂函数源码解析"
  - id: readme
    resource: "../../../../../../external/libs/jupyter/nbconvert/README.md"
    title: "README.md"
  - id: pyproject-toml
    resource: "../../../../../../external/libs/jupyter/nbconvert/pyproject.toml"
    title: "pyproject.toml"
---

# nbconvert 简介

## 什么是 nbconvert

nbconvert 是 [Jupyter](https://jupyter.org/) 项目的 **Notebook 格式转换工具**，通过 Jinja2 模板引擎将 `.ipynb` Notebook 文件转换为多种静态格式 [F-001]。它是 Jupyter 生态中负责"输出"环节的核心组件——Jupyter 负责交互式编写和执行 Notebook，nbconvert 负责将 Notebook 转换为可分享、可发布的静态文档。

nbconvert 提供的核心能力包括：

1. **多格式导出**：支持 HTML、LaTeX、PDF、Reveal.js 幻灯片、Markdown、reStructuredText、可执行脚本、AsciiDoc 等多种输出格式 [F-002]
2. **Notebook 执行**：内置 ExecutePreprocessor，可在转换前自动执行 Notebook 中的代码单元（基于 nbclient）
3. **模板定制**：基于 Jinja2 模板系统，支持自定义模板、模板继承链，通过 conf.json 声明式配置
4. **预处理管道**：11 个内置预处理器，支持按标签/正则移除单元、清空输出、提取图片、清理元数据等
5. **过滤器扩展**：40+ 个内置 Jinja2 过滤器（Markdown转换、代码高亮、ANSI处理等），支持自定义过滤器
6. **Python API 与 CLI**：同时提供命令行工具 `jupyter nbconvert` 和 Python 编程接口
7. **插件化扩展**：通过 entry points 机制支持第三方包注册自定义导出器

## 项目信息

| 属性 | 值 |
|------|-----|
| 包名 | `nbconvert` |
| 描述 | "Convert Jupyter Notebooks (.ipynb files) to other formats." |
| 许可证 | BSD-3-Clause（Modified BSD License） |
| 构建系统 | hatchling（hatchling >=1.5） |
| Python 要求 | ≥ 3.9 [F-003] |
| CLI 入口 | `jupyter-nbconvert` → `nbconvert.nbconvertapp:main` |
| 附加 CLI | `jupyter-dejavu` → `nbconvert.nbconvertapp:dejavu_main` |
| 代码仓库 | https://github.com/jupyter/nbconvert |
| 文档 | https://nbconvert.readthedocs.io/ |

[F-004]

## 核心依赖

```
beautifulsoup4          # HTML解析与处理
bleach[css]!=5.0.0      # HTML清洗（XSS防护）
defusedxml              # 安全XML解析
jinja2>=3.0             # Jinja2模板引擎
jupyter_core>=4.7       # Jupyter核心（路径、配置）
jupyterlab_pygments     # JupyterLab代码高亮样式
MarkupSafe>=2.0         # Markup安全转义
mistune>=2.0.3,<4       # Markdown解析器
nbclient>=0.5.0         # Notebook客户端（代码执行）
nbformat>=5.7           # Notebook格式读写
packaging               # 版本号处理
pandocfilters>=1.4.1    # Pandoc过滤器
pygments>=2.4.1         # 代码高亮
traitlets>=5.1          # 配置系统
```

[F-005]

## 可选依赖

| extras | 依赖 | 功能 |
|--------|------|------|
| `qtpng` | pyqtwebengine>=5.15 | Qt渲染PNG截图导出 |
| `qtpdf` | nbconvert[qtpng] | Qt渲染PDF导出 |
| `webpdf` | playwright | Playwright无头浏览器PDF导出 |
| `serve` | tornado>=6.1 | `--post serve` HTTP预览服务器 |
| `test` | pytest, ipykernel, ipywidgets, flaky | 测试依赖 |
| `docs` | sphinx, myst_parser, pydata_sphinx_theme等 | 文档构建 |
| `all` | 以上全部 | 完整安装 |

[F-006]

## nbconvert 在 Jupyter 生态中的位置

nbconvert 是 Jupyter 生态的**格式转换层**：

- **JupyterLab/Notebook** 在下载/导出菜单中调用 nbconvert 生成不同格式
- **nbclient** 提供 Notebook 执行能力，nbconvert 的 ExecutePreprocessor 基于它
- **nbformat** 提供 .ipynb 文件的读写 API，nbconvert 使用它加载 Notebook
- **nbviewer** 使用 nbconvert 将 Notebook 渲染为 HTML 供在线浏览
- **papermill** 等参数化工具在执行完 Notebook 后可用 nbconvert 导出结果
- **Jupyter Book/Bookbook** 等文档工具底层使用 nbconvert 转换 Notebook

## 安装

### 基础安装

```bash
pip install nbconvert
```

### 完整安装（含所有可选功能）

```bash
pip install nbconvert[all]
```

### 附加系统依赖

某些导出格式需要额外安装系统工具：

- **PDF 导出（LaTeX）**：需要安装 TeX 发行版（TeX Live/MiKTeX）
- **PDF 导出（WebPDF）**：需要安装 playwright（`pip install nbconvert[webpdf] && playwright install`）
- **Pandoc 相关转换**：需要安装 [Pandoc](https://pandoc.org/)（用于 Markdown→LaTeX/RST 等转换）

验证安装：

```bash
jupyter nbconvert --version
```

## 相关概念

- [5分钟快速上手](01-getting-started.md)
- [架构总览](02-architecture-overview.md)
