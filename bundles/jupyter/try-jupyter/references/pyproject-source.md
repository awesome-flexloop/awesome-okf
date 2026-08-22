---
type: Reference
title: "pyproject.toml 项目配置源码"
description: "try-jupyter 项目的 pyproject.toml 完整解析：项目元数据、pixi工作区配置、任务定义、依赖清单、pytest配置"
tags: [pyproject, pixi, dependencies, pytest, jupyterlite, build-tasks]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:50:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: pyproject-toml
    resource: "../../../../../external/libs/jupyter/try-jupyter/pyproject.toml"
    title: "try-jupyter/pyproject.toml"
---

# pyproject.toml 项目配置源码

本信源登记 try-jupyter 项目 `pyproject.toml` 的完整配置结构。

## 项目元数据

| 字段 | 值 |
|------|---|
| `[project].name` | `try-jupyter` |
| `[project].authors` | `{name = "Project Jupyter", email = "jupyter@googlegroups.com"}` |
| `[project].dependencies` | `["jupyterlab-open-url-parameter>=0.3.0"]` |

项目唯一运行时Python依赖为 `jupyterlab-open-url-parameter`（版本≥0.3.0），用于支持URL参数打开notebook。

## Pixi 工作区配置

```toml
[tool.pixi.workspace]
channels = ["conda-forge"]
platforms = ["linux-64", "osx-64", "win-64", "osx-arm64"]
```

- 使用 conda-forge 作为唯一channel
- 支持4个平台：Linux x64、macOS x64、Windows x64、macOS ARM64

## Pixi 任务定义（6个任务）

| 任务名 | 命令 | 说明 |
|--------|------|------|
| `clean` | `rm -rf .jupyterlite.doit.db dist` | 清理构建产物和doit数据库 |
| `build` | `jupyter lite build` | 执行JupyterLite站点构建 |
| `filter-kernels` | `python scripts/filter_xeus_kernels.py dist` | 过滤xeus内核列表 |
| `add-plausible` | `python scripts/add_plausible.py dist` | 注入Plausible分析代码 |
| `test` | `pytest` | 运行UI测试 |
| `readthedocs` | `rm -rf $READTHEDOCS_OUTPUT/html && cp -r dist $READTHEDOCS_OUTPUT/html` | RTD部署：复制dist到输出目录 |

## Pixi 依赖分类

### JupyterLite 核心（4个包）

| 包 | 版本约束 | 用途 |
|----|---------|------|
| `jupyterlite-core` | `>=0.8.0,<0.9` | JupyterLite核心框架 |
| `jupyterlite-pyodide-kernel` | `>=0.8.0,<0.9` | Pyodide Python内核（浏览器端CPython） |
| `jupyterlite-xeus` | `>=5.0.0,<6` | Xeus多语言内核框架 |
| `jupyterlite-terminal` | `>=1.5.1,<2` | 浏览器终端支持 |

### JupyterLab 与 Notebook（3个包）

| 包 | 版本约束 | 用途 |
|----|---------|------|
| `jupyterlab` | `>=4.6.0,<5` | JupyterLab界面（主界面） |
| `notebook` | `>=7.6.0,<8` | Notebook 7界面 |
| `jupyterlab-night` | `>=0.5.2,<0.6` | 暗色主题 |

### 交互式可视化库（6个包）

| 包 | 版本约束 | 用途 |
|----|---------|------|
| `ipywidgets` | `>=8.1.7` | 交互式Widget基础 |
| `bqplot` | `>=0.13.1,<0.14` | 交互式2D可视化 |
| `ipycanvas` | `>=0.9.1` | Canvas绑定 |
| `ipyleaflet` | `>=0.20.0,<0.21` | 交互式地图 |
| `ipympl` | `>=0.8.2` | Matplotlib交互式后端 |
| `plotly` | `>=6` | Plotly可视化 |

### 语言包（2个包）

| 包 | 版本约束 |
|----|---------|
| `jupyterlab-language-pack-fr-fr` | `>=4.4.post3,<5` |
| `jupyterlab-language-pack-zh-cn` | `>=4.4.post3,<5` |

### 文件查看器扩展（2个包）

| 包 | 版本约束 | 用途 |
|----|---------|------|
| `jupyterlab-fasta` | `>=3.3.0` | FASTA序列文件查看 |
| `jupyterlab-geojson` | `>=3.4.0` | GeoJSON地理数据查看 |

### 构建工具与文档（4个包）

| 包 | 版本约束 | 用途 |
|----|---------|------|
| `python` | `>=3.12` | Python运行时 |
| `nodejs` | `>=22` | Node.js（JupyterLab构建需要） |
| `mamba` | `>=2.4.0,<3` | 包管理器 |
| `micromamba` | `>=2.0.5` | 轻量包管理器 |
| `pip` | `>=25.3,<26` | pip包管理器 |
| `pydata-sphinx-theme` | `>=0.16.1,<0.17` | Sphinx主题 |
| `myst-parser` | `>=4.0.1,<5` | MyST Markdown解析 |
| `beautifulsoup4` | `>=4.12` | HTML解析（后处理脚本使用） |

### 测试框架（4个包）

| 包 | 版本约束 | 用途 |
|----|---------|------|
| `playwright` | `>=1.61.0` | 浏览器自动化 |
| `pytest-playwright` | `>=0.8.0` | Pytest Playwright集成 |
| `pytest-html` | `>=4.2.0` | HTML测试报告 |
| `pytest-rerunfailures` | `>=15.1,<16` | 失败重试 |

## Pytest 配置

```toml
[tool.pytest.ini_options]
testpaths = ["ui-tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "-v --tb=short --html=ui-tests/report.html --self-contained-html"
```

- 测试目录：`ui-tests/`
- 测试文件匹配：`test_*.py`
- 测试函数匹配：`test_*`
- 默认参数：详细输出、短traceback、生成HTML报告

## 相关信源

- [配置文件信源](config-source.md)
- [构建脚本信源](scripts-source.md)
- [测试框架信源](test-source.md)
- [CI/CD工作流信源](ci-source.md)
