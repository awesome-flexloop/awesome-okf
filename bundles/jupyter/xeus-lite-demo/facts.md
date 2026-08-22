---
type: Facts
okf_version: '0.2'
title: xeus-lite-demo 源码事实清单
generated: '2026-08-22'
tags:
- facts
---

# xeus-lite-demo 源码事实清单

> R阶段（事实采集）产出的零推测事实清单，每个事实均可通过源码路径验证。

## 项目元数据

- **F-001**: 项目名称 `xeus-lite-demo`，GitHub 模板仓库（Template Repository）
- **F-002**: README 徽章指向 `https://jupyterlite.github.io/xeus-lite-demo/notebooks/?path=demo.ipynb`
- **F-003**: 项目许可证文件未在仓库根目录显式声明（GitHub 模板默认继承上游协议）
- **F-004**: 仓库包含 `.nojekyll` 空文件（GitHub Pages 禁用 Jekyll 处理）
- **F-005**: 仓库包含 `deploy.gif` 演示动画文件

## 目录结构

- **F-006**: 根目录文件：`README.md`, `environment.yml`, `.nojekyll`, `deploy.gif`, `.gitignore`
- **F-007**: `content/` 目录包含 `demo.ipynb`（示例 Notebook）
- **F-008**: `.github/workflows/deploy.yml` — GitHub Actions CI/CD 配置
- **F-009**: `.github/build-environment.yml` — 构建环境 conda 配置

## environment.yml（运行时环境）

- **F-010**: `name: xeus-kernel`
- **F-011**: channels 列表包含两个 URL：`https://repo.prefix.dev/emscripten-forge-dev` 和 `https://repo.prefix.dev/conda-forge`
- **F-012**: 默认 dependencies 为 `xeus-python` 和 `ipycanvas`
- **F-013**: 未指定 channels 的 priority 字段

## .github/build-environment.yml（构建环境）

- **F-014**: `name: build-env`
- **F-015**: channels 为 `conda-forge`
- **F-016**: dependencies 包含 `python`, `pip`, `jupyter_server`, `jupyterlite-core >=0.7`, `jupyterlite-xeus >=4.3`, `notebook >=7.5`

## .github/workflows/deploy.yml（CI/CD）

- **F-017**: 工作流名称 `Build and Deploy`
- **F-018**: 触发条件：`push` 到 `main` 分支 + `pull_request` 到所有分支（`'*'`）
- **F-019**: 两个 job：`build` 和 `deploy`
- **F-020**: `build` job 运行在 `ubuntu-latest`
- **F-021**: build steps 顺序：Checkout → Setup Python → Install mamba → Build JupyterLite site → Upload artifact
- **F-022**: Checkout 使用 `actions/checkout@v3`
- **F-023**: Setup Python 使用 `actions/setup-python@v5`，python-version: `'3.12'`
- **F-024**: Install mamba 使用 `mamba-org/setup-micromamba@v1`，micromamba-version: `'1.5.8-0'`
- **F-025**: micromamba 使用 environment-file: `.github/build-environment.yml`，cache-environment: true
- **F-026**: Build 步骤 shell 为 `bash -l {0}`（login shell）
- **F-027**: Build 命令：`cp README.md content` 然后 `jupyter lite build --contents content --output-dir dist`
- **F-028**: Upload artifact 使用 `actions/upload-pages-artifact@v3`，path: `./dist`
- **F-029**: `deploy` job `needs: build`，条件 `github.ref == 'refs/heads/main'`
- **F-030**: deploy 权限：`pages: write`, `id-token: write`
- **F-031**: deploy environment name: `github-pages`，url: `${{ steps.deployment.outputs.page_url }}`
- **F-032**: deploy 步骤使用 `actions/deploy-pages@v4`，id: `deployment`

## content/demo.ipynb（示例 Notebook）

- **F-033**: Notebook 使用简化的 XML-like 格式（非标准 JSON ipynb）
- **F-034**: 包含两个 code cell，language: python，execution_count 均为 null
- **F-035**: cell-0 源码为 `import this`（Python 之禅）
- **F-036**: cell-1 导入 `from math import pi` 和 `from ipycanvas import Canvas`
- **F-037**: cell-1 创建 Canvas(width=1600, height=1200, layout=dict(width="100%"))
- **F-038**: cell-1 使用 fill_style="#8ee05e" 填充矩形背景（绿色）
- **F-039**: cell-1 使用 fill_style="#f5f533"（黄色）fill_circle 绘制直径1000的圆形
- **F-040**: cell-1 使用 stroke_style="black", line_width=30 绘制圆形描边
- **F-041**: cell-1 使用 fill_style="black" fill_circle 绘制两个眼睛（直径200）
- **F-042**: cell-1 使用 stroke_arc 绘制嘴巴和左眼弧
- **F-043**: cell-1 最后一行输出 `canvas` 变量（Jupyter 显示 Canvas 对象）

## .gitignore

- **F-044**: 忽略模式：`*.bundle.*`, `lib/`, `node_modules/`, `.yarn-packages/`, `*.egg-info/`, `.ipynb_checkpoints`, `*.tsbuildinfo`
- **F-045**: 包含 gitignore.io 生成的标准 Python 模板（__pycache__, build/, dist/, *.py[cod], .pytest_cache 等）
- **F-046**: JupyterLite 特定忽略项：`*.doit.db`, `_output`

## README.md（使用说明）

- **F-047**: README 标题 `Xeus-Lite demo`
- **F-048**: 描述："This GitHub template allows you to create deployments of JupyterLite with a custom set of conda packages."
- **F-049**: 创建部署三步流程：(1) Use this template → (2) Enable GitHub Pages from Actions → (3) Customize environment.yml
- **F-050**: 部署 URL 格式：`https://{USERNAME}.github.io/{DEMO_REPO_NAME}`
- **F-051**: 安装 kernels/packages 通过编辑 `environment.yml`
- **F-052**: 文档链接指向 `https://jupyterlite-xeus.readthedocs.io/en/latest/environment.html`
- **F-053**: 示例1（NumPy+Matplotlib）：channels 使用 emscripten-forge-dev + conda-forge（prefix.dev），dependencies 为 xeus-python + numpy + matplotlib
- **F-054**: 示例2（R kernel）：channels 同上，dependencies 为 xeus-r + r-coursekata
- **F-055**: 示例3（C++ kernel）：channels 同上，dependencies 为 xeus-cpp
- **F-056**: JupyterLite 插件（如 jupyterlite-terminal）添加到 `.github/build-environment.yml` 而非 `environment.yml`
