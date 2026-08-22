---
okf_version: "0.2"
type: references
title: "JupyterLab Pygments 源码信源索引"
description: "jupyterlab_pygments 核心源码的事实采集文档索引，所有API引用均可溯源至这些文件"
tags: [references, source, index, style, pygments, css-generation, build, frontend]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T13:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: style-py
    resource: "../../../../../external/libs/jupyter/jupyterlab_pygments/jupyterlab_pygments/style.py"
    title: "jupyterlab_pygments/style.py"
  - id: init-py
    resource: "../../../../../external/libs/jupyter/jupyterlab_pygments/jupyterlab_pygments/__init__.py"
    title: "jupyterlab_pygments/__init__.py"
  - id: generate-css-py
    resource: "../../../../../external/libs/jupyter/jupyterlab_pygments/generate_css.py"
    title: "generate_css.py"
  - id: index-ts
    resource: "../../../../../external/libs/jupyter/jupyterlab_pygments/src/index.ts"
    title: "src/index.ts"
  - id: pyproject-toml
    resource: "../../../../../external/libs/jupyter/jupyterlab_pygments/pyproject.toml"
    title: "pyproject.toml"
---

# 源码信源索引

本文档索引 jupyterlab_pygments 核心源码的事实采集文档。所有概念文档和示例文档中引用的 API 均溯源至这些信源文件。

## 信源文档清单

| 文档 | 覆盖源码 | 行数 | 核心内容 |
|------|---------|------|---------|
| [style-py-source.md](style-py-source.md) | `jupyterlab_pygments/style.py` | 133行 | JupyterStyle 类定义、Pygments token→CSS变量映射、22个mirror-editor CSS变量、已知限制说明 |
| [init-py-source.md](init-py-source.md) | `jupyterlab_pygments/__init__.py` | 15行 | 版本导入（dev回退）、JupyterStyle导出、_jupyter_labextension_paths()扩展路径注册 |
| [generate-css-source.md](generate-css-source.md) | `generate_css.py` | 33行 | Python→CSS转换器：HtmlFormatter.get_style_defs()、.highlight前缀过滤、base.css自动生成 |
| [index-ts-source.md](index-ts-source.md) | `src/index.ts` + `style/index.css` + `style/index.js` | 17+1+1行 | TypeScript空插件（CSS-only扩展模式）、activate空回调、styleModule CSS注入链路、tsconfig配置 |
| [build-config-source.md](build-config-source.md) | `pyproject.toml` + `package.json` + `install.json` + `setup.py` | 109+200+5+1行 | hatchling构建后端、hatch-nodejs-version版本同步、hatch-jupyter-builder npm构建钩子、wheel shared-data映射、jlpm构建脚本 |

## 源码文件清单

| 源码文件 | 行数 | 核心类/函数/配置 |
|---------|------|-----------------|
| `jupyterlab_pygments/style.py` | 133行 | `JupyterStyle(Style)`、`default_style`、`background_color`、`highlight_color`、`styles` 字典 |
| `jupyterlab_pygments/__init__.py` | 15行 | `__version__`、`JupyterStyle` 导入、`_jupyter_labextension_paths()` |
| `generate_css.py` | 33行 | `main()`、`HtmlFormatter(style=JupyterStyle)`、`get_style_defs('.highlight')`、`base.css` 写入 |
| `src/index.ts` | 17行 | `JupyterFrontEndPlugin<void>`、`plugin` 对象、`activate` 空回调 |
| `style/index.css` | 1行 | `@import url('base.css')` |
| `style/index.js` | 1行 | `import './base.css'` |
| `pyproject.toml` | 109行 | hatchling构建、jupyter-builder钩子、wheel shared-data映射 |
| `package.json` | 200行 | jupyterlab扩展配置、构建脚本、依赖、styleModule声明 |
| `install.json` | 5行 | Python包管理器元数据 |
| `setup.py` | 1行 | setuptools兼容shim |

## 导航

- [概念文档索引](../concepts/index.md)
- [示例文档索引](../examples/index.md)
- [教程首页](../index.md)
