---
type: Facts
okf_version: "0.2"
title: "sphinx-demo 源码事实清单"
generated: "2026-08-22"
tags: [jupyter, sphinx, jupyterlite, demo, documentation]
sources:
  - ../../../../../external/libs/jupyter/sphinx-demo/README.md
  - ../../../../../external/libs/jupyter/sphinx-demo/index.html
  - ../../../../../external/libs/jupyter/sphinx-demo/switcher.json
  - ../../../../../external/libs/jupyter/sphinx-demo/pyodide-kernel-example/docs/source/conf.py
  - ../../../../../external/libs/jupyter/sphinx-demo/xeus-kernel-example/docs/source/conf.py
  - ../../../../../external/libs/jupyter/sphinx-demo/pyodide-kernel-example/docs/source/jupyter_lite_config.json
  - ../../../../../external/libs/jupyter/sphinx-demo/pyodide-kernel-example/docs/source/jupyter-lite.json
  - ../../../../../external/libs/jupyter/sphinx-demo/xeus-kernel-example/docs/source/environment.yml
  - ../../../../../external/libs/jupyter/sphinx-demo/.github/workflows/pages.yml
---
# sphinx-demo 源码事实清单

## 项目元数据与总体架构（README.md）

- F-001: README.md:1 — 仓库标题为 `jupyterlite-sphinx-demo`
- F-002: README.md:3 — 展示将 JupyterLite 作为 Sphinx 站点的一部分、经 `jupyterlite-sphinx` 扩展部署为 GitHub Pages 静态站
- F-003: README.md:7-8 — 列出两个独立部署（非 Sphinx 集成）的参考项目：jupyterlite/demo（Pyodide kernel）与 jupyterlite/xeus-lite-demo（Xeus kernel）
- F-004: README.md:26 — `pyodide-kernel-example/` 是使用 Pyodide distribution（WebAssembly 中运行的 Python kernel）的 JupyterLite 部署
- F-005: README.md:27 — `xeus-kernel-example/` 是使用 emscripten-forge channel 的 Xeus kernel 部署
- F-006: README.md:29 — 两个示例均使用 PyData Sphinx Theme（`pydata_sphinx_theme`）
- F-007: README.md:42 — JupyterLite 部署产物存储于 Sphinx 构建输出的 `lite/` 子目录
- F-008: README.md:77 — 项目采用 BSD 3-Clause License

## 根目录 index.html 与 switcher.json

- F-009: index.html:7 — `<meta name="description">` 内容为 `"JupyterLite Sphinx Demo with Pyodide and Xeus kernels"`
- F-010: index.html:8 — favicon 指向 `https://jupyterlite.github.io/sphinx-demo/pyodide/lite/lab/favicon.ico`
- F-011: index.html:352-376 — `<main>` 内嵌"Available JupyterLite kernels"表格，列出 Pyodide 与 Xeus 两个内核及其链接
- F-012: index.html:362-366 — Pyodide 行引用 `jupyterlite-pyodide-kernel`，链接指向 `/pyodide/` 并含 JupyterLite badge 图
- F-013: index.html:369-373 — Xeus 行引用 `xeus-python` kernel，链接指向 `/xeus/` 并含 JupyterLite badge 图
- F-014: switcher.json:1-12 — 两个条目：`{name: "pyodide", url: "https://jupyterlite.github.io/sphinx-demo/pyodide/"}` 与 `{name: "xeus", url: "https://jupyterlite.github.io/sphinx-demo/xeus/"}`

## 双示例目录结构与依赖

- F-015: pyodide-kernel-example/README.md:7-14 — 列出关键文件：conf.py、index.rst、jupyter_lite_config.json、jupyter-lite.json、overrides.json、try_examples.json、button_styling.css、requirements.txt
- F-016: xeus-kernel-example/README.md:13 — 额外包含 `environment.yml`，用于在 Sphinx 构建过程中安装浏览器内 kernel 依赖
- F-017: pyodide-kernel-example/requirements.txt:3 — 依赖 `jupyterlite-sphinx>=0.20.0`
- F-018: pyodide-kernel-example/requirements.txt:8 — 依赖固定版本 `jupyterlite-pyodide-kernel==0.5.2`（固定版本控制部署所用 Pyodide 版本）
- F-019: xeus-kernel-example/requirements.txt:13 — 依赖 `jupyterlite-xeus`（未固定版本）

## conf.py 的 jupyterlite_sphinx 集成（pyodide/xeus 两示例配置相同）

- F-020: conf.py:21-30 — `extensions` 列表含 8 个扩展：sphinx.ext.autodoc、sphinx.ext.mathjax、sphinx.ext.autosummary、sphinx.ext.doctest、jupyterlite_sphinx、sphinx_design、myst_nb、numpydoc
- F-021: conf.py:33-34 — `sys.path.insert` 插入当前目录 `"."` 与 `"disabled_examples"` 两个路径
- F-022: conf.py:43 — `jupyterlite_contents = ["custom_contents/*"]`，将 `custom_contents/` 目录纳入内嵌 JupyterLite 站点
- F-023: conf.py:47 — `jupyterlite_silence = True`，静默 JupyterLite 构建过程输出
- F-024: conf.py:50 — `strip_tagged_cells = True`，从输出 HTML 中剥离带 `jupyterlite_sphinx_strip` 标签的单元格
- F-025: conf.py:54 — `global_enable_try_examples = True`，自动为 numpydoc/sphinx.ext.napoleon 处理的 Examples 节插入 TryExamples 指令
- F-026: conf.py:58 — `try_examples_global_button_text = "Try it online"`，设置所有 TryExamples 按钮的全局文本
- F-027: conf.py:63-68 — `try_examples_global_warning_text` 设置实验性警告消息，Markdown 格式，含指向 issue tracker 的链接

## HTML 输出与主题配置

- F-028: conf.py:78-82 — `html_theme = "pydata_sphinx_theme"`，`html_logo = "_static/icon.svg"`，`html_static_path = ["_static"]`，`html_css_files = ["button_styling.css"]`，`html_js_files = ["pypi.js"]`
- F-029: conf.py:87-99 — `html_theme_options.icon_links` 含两个图标链接：GitHub（fa-brands fa-github）与 PyPI（fa-custom fa-pypi）
- F-030: conf.py:100-103 — `html_theme_options.switcher.json_url` 指向根目录 `switcher.json`；`version_match` 在 pyodide 的 conf.py:102 为 `"pyodide"`、在 xeus 的 conf.py:102 为 `"xeus"`
- F-031: conf.py:113-119 — `html_context` 配置 GitHub 编辑链接，`doc_path` 在 pyodide 的 conf.py:118 为 `"pyodide-kernel-example/docs/source/"`、在 xeus 的 conf.py:118 为 `"xeus-kernel-example/docs/source/"`

## JupyterLite JSON 配置（四层配置）

- F-032: jupyter_lite_config.json:1-5 — `LiteBuildConfig.no_sourcemaps = true`（构建时配置，pyodide/xeus 两示例相同）
- F-033: pyodide-kernel-example/docs/source/jupyter-lite.json:3-7 — 运行时配置 `appName = "jupyterlite-sphinx-demo (Pyodide)"`、`defaultKernelName = "python"`、`faviconUrl = "./lab/favicon.ico"`
- F-034: xeus-kernel-example/docs/source/jupyter-lite.json:3-7 — 运行时配置 `appName = "jupyterlite-sphinx-demo (Xeus)"`、`defaultKernelName = "XPython"`、`faviconUrl = "./lab/favicon.ico"`
- F-035: overrides.json:1-14 — 配置 `@jupyterlab/notebook-extension:panel` 的 toolbar，添加 `name: "download"`、`command: "docmanager:download"` 的下载按钮
- F-036: try_examples.json:1-4 — 配置 `global_min_height: "400px"` 与 `ignore_patterns: ["disabled_examples\/demo.html"]`

## Xeus 环境与示例内容

- F-037: xeus-kernel-example/docs/source/environment.yml:5 — 环境名称为 `jupyterlite-wasm-env`
- F-038: xeus-kernel-example/docs/source/environment.yml:9-11 — channels 为 `https://repo.mamba.pm/emscripten-forge` 与 `conda-forge`
- F-039: xeus-kernel-example/docs/source/environment.yml:16-21 — dependencies 为 `pandas`、`matplotlib`、`xeus-python`
- F-040: pyodide-kernel-example/docs/source/example.py:275-278 — `image_processing` 函数的 Examples 段以 `.. disable_try_examples` 注释开头（每函数级禁用）；其 fibonacci_sequence（:31-51）与 solve_pendulum_ode（:187-243）的 Examples 段含 `>>>` 可执行示例
