---
type: Example
title: 基础使用
description: 从零开始使用 sphinx-autobuild——安装、初始化 Sphinx 项目、启动实时预览、常用选项
tags: [sphinx-autobuild, basic-usage, quickstart, example]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T14:50:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: sphinx-autobuild-source
    resource: /references/sphinx-autobuild-source.md
    title: sphinx-autobuild 源码信源登记
---

# 基础使用

## 场景

你刚刚创建了一个 Sphinx 文档项目，想要在编写文档时实时预览效果，不需要每次保存后手动运行 `sphinx-build` 和刷新浏览器。

## 步骤

### 1. 安装

```bash
pip install sphinx-autobuild
```

验证安装：

```bash
sphinx-autobuild --version
# sphinx-autobuild 2025.08.25
```

### 2. 准备 Sphinx 项目

如果你还没有 Sphinx 项目，先创建一个：

```bash
pip install sphinx
sphinx-quickstart docs
```

按照向导完成初始化。生成的目录结构大致如下：

```
docs/
├── _build/          # 构建输出目录（自动创建）
├── _static/         # 静态文件
├── _templates/      # 模板
├── conf.py          # Sphinx 配置
├── index.rst        # 主文档
├── make.bat         # Windows Makefile
└── Makefile         # Unix Makefile
```

### 3. 启动实时预览

```bash
sphinx-autobuild docs docs/_build/html
```

终端输出示例：

```
[sphinx-autobuild] Starting initial build
[sphinx-autobuild] > python -m sphinx build docs docs/_build/html
Running Sphinx 7.4.0
making output directory... done
building [mo]: targets for 0 po files that are out of date
writing output...
build succeeded.

The HTML pages are in docs/_build/html.
[sphinx-autobuild] Serving on http://127.0.0.1:8000
[sphinx-autobuild] Waiting to detect changes...
```

### 4. 在浏览器中预览

打开浏览器访问 http://127.0.0.1:8000 ，你将看到 Sphinx 文档的首页。

### 5. 编辑并自动刷新

打开 `docs/index.rst`，修改欢迎标题：

```rst
Welcome to My Project's Documentation!
=======================================

这是我的第一个 Sphinx 文档项目。
```

保存文件后，终端会显示：

```
[sphinx-autobuild] Detected changes (docs/index.rst)
[sphinx-autobuild] Rebuilding...
[sphinx-autobuild] > python -m sphinx build docs docs/_build/html
...
build succeeded.
[sphinx-autobuild] Serving on http://127.0.0.1:8000
```

浏览器页面会自动刷新，显示更新后的内容。

## 常用选项组合

### 自动打开浏览器

```bash
sphinx-autobuild --open-browser docs docs/_build/html
```

### 自动选择端口

当 8000 端口被占用或同时运行多个项目时：

```bash
sphinx-autobuild --port=0 --open-browser docs docs/_build/html
```

终端会显示实际使用的端口。

### 跳过首次构建

如果你已经手动构建过文档，不想等首次构建：

```bash
sphinx-autobuild --no-initial docs docs/_build/html
```

### 允许局域网访问

默认只监听 127.0.0.1（仅本机访问）。如果需要从其他设备访问：

```bash
sphinx-autobuild --host 0.0.0.0 docs docs/_build/html
```

然后通过 `http://<你的IP>:8000` 访问。

### 传递 sphinx-build 选项

所有不被 sphinx-autobuild 识别的参数都会传递给 sphinx-build：

```bash
# -a: 全量重建（不使用增量缓存）
# -E: 不使用保存的环境
# -W: 将警告视为错误
# -t dev: 设置 "dev" 标签（用于 only 指令）
sphinx-autobuild -a -E -W -t dev docs docs/_build/html
```

### 添加忽略规则

```bash
# 忽略所有 .tmp 文件和 drafts 目录
sphinx-autobuild \
  --re-ignore '\.tmp$' \
  --ignore 'drafts' \
  docs docs/_build/html
```

## 调试忽略规则

如果文件修改没有触发重建，启用调试模式查看：

```bash
# Linux/macOS
SPHINX_AUTOBUILD_DEBUG=1 sphinx-autobuild docs docs/_build/html

# Windows PowerShell
$env:SPHINX_AUTOBUILD_DEBUG = "1"
sphinx-autobuild docs docs/_build/html
```

每次文件变化都会打印路径和当前忽略规则，帮助诊断配置问题。

## 停止服务器

按 `Ctrl+C` 停止服务器。

## 相关概念

- [5分钟快速上手](/concepts/01-getting-started.md)
- [CLI 入口与参数解析](/concepts/03-cli-and-entrypoint.md)
- [文件监听与过滤](/concepts/05-file-watching.md)
- [自定义前后置命令](/examples/custom-pre-post-build.md)
