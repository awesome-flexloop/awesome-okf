---
type: Facts
okf_version: "0.2"
title: "try-jupyter 源码事实清单"
generated: "2026-08-22"
tags: [jupyter, try-jupyter, jupyterlite, demo, deployment]
sources:
  - ../../../../../external/libs/jupyter/try-jupyter/jupyter_lite_config.json
  - ../../../../../external/libs/jupyter/try-jupyter/jupyter-lite.json
  - ../../../../../external/libs/jupyter/try-jupyter/repl/jupyter-lite.json
  - ../../../../../external/libs/jupyter/try-jupyter/pyproject.toml
  - ../../../../../external/libs/jupyter/try-jupyter/environment-cpp.yml
  - ../../../../../external/libs/jupyter/try-jupyter/environment-python.yml
  - ../../../../../external/libs/jupyter/try-jupyter/environment-r.yml
  - ../../../../../external/libs/jupyter/try-jupyter/environment-sqlite.yml
  - ../../../../../external/libs/jupyter/try-jupyter/scripts/filter_xeus_kernels.py
  - ../../../../../external/libs/jupyter/try-jupyter/scripts/add_plausible.py
  - ../../../../../external/libs/jupyter/try-jupyter/.readthedocs.yml
  - ../../../../../external/libs/jupyter/try-jupyter/.github/workflows/deploy.yml
  - ../../../../../external/libs/jupyter/try-jupyter/content/notebooks/Intro.ipynb
---
# try-jupyter 源码事实清单

## 项目元数据与 pixi 任务（pyproject.toml）

- F-001: pyproject.toml:2 — `authors = [{name = "Project Jupyter", email = "jupyter@googlegroups.com"}]`
- F-002: pyproject.toml:3 — 项目名称为 `try-jupyter`
- F-003: pyproject.toml:7 — `[tool.pixi.workspace]` 的 `channels = ["conda-forge"]`
- F-004: pyproject.toml:11 — pixi `clean` 任务执行 `rm -rf .jupyterlite.doit.db dist`
- F-005: pyproject.toml:12 — pixi `build` 任务执行 `jupyter lite build`
- F-006: pyproject.toml:13 — pixi `filter-kernels` 任务执行 `python scripts/filter_xeus_kernels.py dist`
- F-007: pyproject.toml:14 — pixi `add-plausible` 任务执行 `python scripts/add_plausible.py dist`
- F-008: pyproject.toml:16 — pixi `readthedocs` 任务执行 `rm -rf $READTHEDOCS_OUTPUT/html && cp -r dist $READTHEDOCS_OUTPUT/html`

## JupyterLite 构建与运行时配置（jupyter_lite_config.json / jupyter-lite.json）

- F-009: jupyter_lite_config.json:3 — `LiteBuildConfig.output_dir` 设置为 `"dist"`
- F-010: jupyter_lite_config.json:4-6 — `LiteBuildConfig.contents` 为 `["content"]`，将 `content/` 目录纳入站点内容
- F-011: jupyter_lite_config.json:8-14 — `XeusAddon.environment_file` 列出 4 个内核环境文件：`environment-cpp.yml`、`environment-python.yml`、`environment-r.yml`、`environment-sqlite.yml`
- F-012: jupyter-lite.json:4 — `jupyter-config-data.appName` 为 `"Try Jupyter!"`
- F-013: jupyter-lite.json:5-9 — `disabledExtensions` 包含 `@jupyterlab/server-proxy`、`jupyterlab-server-proxy`、`nbdime-jupyterlab` 三个扩展
- F-014: jupyter-lite.json:10 — `jupyter-config-data.terminalsAvailable` 为 `true`
- F-015: repl/jupyter-lite.json:4-8 — `repl/` 子站点的 `disabledExtensions` 包含 `@jupyterlab/drawio-extension`、`jupyterlab-kernel-spy`、`jupyterlab-tour`

## 多内核 WASM 环境定义（environment-*.yml）

- F-016: environment-cpp.yml:1 — 环境名称为 `xeus-cpp-kernel`
- F-017: environment-cpp.yml:3-4 — channels 为 `https://prefix.dev/emscripten-forge-4x` 与 `https://prefix.dev/conda-forge`
- F-018: environment-cpp.yml:6-9 — dependencies 为 `xeus-cpp`、`symengine`、`xtensor-blas`、`xsimd`
- F-019: environment-python.yml:1 — 环境名称为 `xeus-python-kernel`
- F-020: environment-python.yml:6-12 — dependencies 为 `xeus-python`、`numpy`、`matplotlib`、`pillow`、`ipywidgets>=8.1.6`、`ipyleaflet`、`scipy`
- F-021: environment-r.yml:1 — 环境名称为 `xeus-r-kernel`
- F-022: environment-r.yml:6-7 — dependencies 为 `xeus-r >= 0.7.0`、`r-ggplot2`
- F-023: environment-sqlite.yml:1 — 环境名称为 `xeus-sqlite-kernel`
- F-024: environment-sqlite.yml:6 — dependencies 为 `xeus-sqlite`

## content/ 目录组织（notebooks 与 data）

- F-025: content/notebooks/Intro.ipynb:101-103 — kernelspec `display_name` 为 `"Python (Pyodide)"`、`language` 为 `"python"`、`name` 为 `"python"`
- F-026: content/notebooks/Lorenz.ipynb:230-231 — kernelspec `display_name` 为 `"Python (XPython)"`、`language` 为 `"python"`
- F-027: content/notebooks/r.ipynb:5-6 — kernelspec `display_name` 为 `"R 4.4.3 (xr)"`、`language` 为 `"R"`
- F-028: content/notebooks/sqlite.ipynb:5-6 — kernelspec `display_name` 为 `"xsqlite"`、`language` 为 `"sqlite"`
- F-029: content/notebooks/cpp.ipynb:4-5 — kernelspec `display_name` 为 `"C++23"`、`language` 为 `"cpp"`
- F-030: content/data/bar.vl.json:42 — 顶层 `description` 为 `"A simple bar chart with embedded data."`
- F-031: ui-tests/test_notebooks.py:18 — `NOTEBOOKS = sorted(CONTENT_DIR.glob("*.ipynb"))` 自动发现 `content/notebooks/` 下全部 notebook（CONTENT_DIR 定义于 :17）

## scripts/ 构建部署脚本

- F-032: scripts/filter_xeus_kernels.py:14 — `KERNELS_TO_KEEP = {"xcpp23", "xc23", "xr", "xpython", "xsqlite"}`
- F-033: scripts/filter_xeus_kernels.py:19-20 — 脚本读取 `dist/xeus/kernels.json` 作为待过滤的 kernels 清单
- F-034: scripts/add_plausible.py:14 — `PLAUSIBLE_SRC = "https://plausible.io/js/pa-B75UO5--FNXYQSG7GBWkf.js"`
- F-035: scripts/add_plausible.py:24 — 脚本以 `dist_dir.rglob("*.html")` 遍历构建产物中所有 HTML 文件并注入分析脚本

## 构建部署流水线（.readthedocs.yml 与 .github/workflows）

- F-036: .readthedocs.yml:2-6 — build 配置 `os: ubuntu-22.04`，tools 指定 `python: mambaforge-latest`
- F-037: .readthedocs.yml:7-12 — commands 依次为 `mamba install -c conda-forge -c nodefaults pixi`、`pixi install`、`pixi run build`、`pixi run filter-kernels`、`pixi run readthedocs`
- F-038: .github/workflows/deploy.yml:23-25 — build job 使用 `prefix-dev/setup-pixi@v0.9.3`，`pixi-version: v0.71.0`，`cache: true`
- F-039: .github/workflows/deploy.yml:30-31 — build job 先执行 `cp README.md content`，再执行 `pixi run build`
- F-040: .github/workflows/deploy.yml:105-120 — deploy job 依赖 test job、条件为 `github.ref == 'refs/heads/main'`，environment 为 `github-pages`，使用 `actions/deploy-pages@v4`
