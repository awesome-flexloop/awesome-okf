---
type: Concept
title: 5分钟快速上手
description: 从安装到启动第一个实时预览服务器，掌握 sphinx-autobuild 的基本用法和常用命令行选项
tags: [sphinx-autobuild, getting-started, quickstart, CLI]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T14:50:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: sphinx-autobuild-source
    resource: /references/sphinx-autobuild-source.md
    title: sphinx-autobuild 源码信源登记
---

# 5分钟快速上手

## 前置条件

- Python 3.11 或更高版本
- 一个已初始化的 Sphinx 文档项目（即包含 `conf.py` 和源文件的目录）
- pip 包管理器

如果还没有 Sphinx 项目，可以快速创建一个：

```bash
pip install sphinx
sphinx-quickstart docs
```

## 基本用法

sphinx-autobuild 的命令格式与 `sphinx-build` 完全一致：

```bash
sphinx-autobuild <sourcedir> <outputdir> [sphinx-options]
```

最基本的用法：

```bash
sphinx-autobuild docs docs/_build/html
```

这条命令会：

1. 在 `docs/` 目录中查找 Sphinx 源文件
2. 将构建产物输出到 `docs/_build/html/`
3. 启动 HTTP 服务器，默认监听 `http://127.0.0.1:8000`
4. 监听 `docs/` 目录的文件变化
5. 在浏览器中打开该地址即可看到文档预览

启动后终端会显示类似以下输出：

```
[sphinx-autobuild] Starting initial build
[sphinx-autobuild] > python -m sphinx build docs docs/_build/html
... (Sphinx 构建输出) ...
[sphinx-autobuild] Serving on http://127.0.0.1:8000
[sphinx-autobuild] Waiting to detect changes...
```

## 停止服务器

按 `Ctrl+C`（`KeyboardInterrupt`）停止服务器，终端会显示：

```
[sphinx-autobuild] Server ceasing operations. Cheerio!
```

## autobuild 专有选项

除了所有 `sphinx-build` 支持的参数外，sphinx-autobuild 还提供以下选项：

### 服务器配置

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--port PORT` | `8000` | 服务端口，设为 `0` 则自动选择空闲端口 |
| `--host HOST` | `127.0.0.1` | 服务主机名，设为 `0.0.0.0` 允许局域网访问 |

### 文件过滤

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--ignore GLOB` | （多次指定） | 添加 glob 模式匹配要忽略的文件/目录 |
| `--re-ignore REGEX` | （多次指定） | 添加正则表达式匹配要忽略的文件/目录 |
| `--watch DIR` | （多次指定） | 添加额外要监听的目录 |

### 构建行为

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--no-initial` | `false` | 跳过首次构建（直接进入监听模式） |
| `--pre-build COMMAND` | （多次指定） | 构建前执行的命令 |
| `--post-build COMMAND` | （多次指定） | 构建成功后执行的命令 |

### 浏览器控制

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--open-browser` | `false` | 构建完成后自动打开浏览器 |
| `--delay SECONDS` | `5` | 打开浏览器前等待的秒数 |

## 自动选择端口

当同时运行多个文档项目时，可以使用 `--port=0` 让操作系统自动分配空闲端口：

```bash
sphinx-autobuild --port=0 docs docs/_build/html
```

终端会显示实际使用的端口号。

## 自动打开浏览器

```bash
sphinx-autobuild --open-browser docs docs/_build/html
```

首次构建完成后，默认等待 5 秒再打开浏览器（确保服务器已就绪）。可以用 `--delay` 调整等待时间：

```bash
sphinx-autobuild --open-browser --delay 3 docs docs/_build/html
```

## 默认忽略目录

sphinx-autobuild 默认忽略以下目录（不会触发重建）：

- 版本控制：`.git`、`.hg`、`.svn`
- IDE 配置：`.idea`、`.vscode`
- 虚拟环境：`.venv`、`venv`
- 缓存目录：`.mypy_cache`、`.nox`、`.ruff_cache`、`.pytest_cache`、`.pytype`、`.tox`、`node_modules`
- 输出目录：Sphinx 的输出目录（outdir）
- 辅助目录：doctree 目录、warnings 文件

这些默认规则与用户通过 `--ignore` 和 `--re-ignore` 添加的规则合并使用。

## 在 Makefile 中使用

在 Sphinx 生成的 Makefile 末尾添加：

```makefile
livehtml:
	sphinx-autobuild "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
```

然后执行：

```bash
make livehtml
```

即可启动实时预览。

## 相关概念

- [sphinx-autobuild 简介](00-introduction.md)
- [架构概览](02-architecture-overview.md)
- [CLI 入口与参数解析](03-cli-and-entrypoint.md)
- [基础使用示例](../examples/basic-usage.md)
