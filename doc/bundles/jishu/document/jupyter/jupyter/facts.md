---
type: Facts
okf_version: '0.2'
title: jupyter 源码事实清单
sources:
- ../../../../../external/libs/jupyter/jupyter/setup.py
- ../../../../../external/libs/jupyter/jupyter/tbump.toml
- ../../../../../external/libs/jupyter/jupyter/setup.cfg
- ../../../../../external/libs/jupyter/jupyter/noxfile.py
- ../../../../../external/libs/jupyter/jupyter/long_description.md
- ../../../../../external/libs/jupyter/jupyter/docs/source/use/jupyter-command.rst
- ../../../../../external/libs/jupyter/jupyter/docs/source/conf.py
- ../../../../../external/libs/jupyter/jupyter/docs/source/use/advanced/migrating.rst
- ../../../../../external/libs/jupyter/jupyter/docs/source/projects/core.rst
- ../../../../../external/libs/jupyter/jupyter/README.md
- ../../../../../external/libs/jupyter/jupyter/SECURITY.md
- ../../../../../external/libs/jupyter/jupyter/.readthedocs.yaml
- ../../../../../external/libs/jupyter/jupyter/.github/workflows/release.yaml
- ../../../../../external/libs/jupyter/jupyter/.travis.yml
generated: '2026-08-22'
tags:
- facts
---

## 项目元数据

- F-001: setup.py:19 — 包名（name）为 `jupyter`，即 PyPI 上的 `jupyter` 包。
- F-002: setup.py:20 — 当前版本为 `1.2.0.dev0`，处于开发预发布状态。
- F-003: setup.py:21 — 包描述（description）为 "Jupyter metapackage. Install all the Jupyter components in one go."。
- F-004: setup.py:24 — 作者为 "Jupyter Development Team"。
- F-005: setup.py:25 — 作者邮箱为 `jupyter@googlegroups.org`。
- F-006: setup.py:34 — 项目 URL 为 `https://jupyter.org`。
- F-007: setup.py:35 — 许可证为 BSD（BSD 3-Clause License）。
- F-008: LICENSE:3 — 版权起始年份为 2017，版权归属 Project Jupyter Contributors。
- F-009: setup.py:36 — 最低 Python 版本要求为 `>=3.6`。
- F-010: setup.py:37-52 — classifiers 声明支持 Python 3.6 至 3.13。
- F-011: tbump.toml:5 — tbump 版本管理工具追踪的当前版本号与 setup.py 一致，为 `1.2.0.dev0`。
- F-012: tbump.toml:20-21 — Git 标签模板为 `v{new_version}`，提交信息模板为 "Bump to {new_version}"。
- F-013: tbump.toml:26-27 — tbump 配置中唯一需要更新版本号的文件是 `setup.py`。

## 目录结构

- F-014: （仓库根） — 仓库根目录下不存在 Python 包子目录（无 `jupyter/` 包目录），不存在 `__init__.py`，不存在 `__main__.py`，不存在根目录级别的 `jupyter.py` shim 文件。
- F-015: setup.py:26 — `py_modules = []`，即不打包任何 Python 模块文件，这是一个零代码的纯元包。
- F-016: setup.py — setup.py 中未定义 `entry_points`、`console_scripts` 或 `scripts`，即此包本身不提供任何命令行入口点。
- F-017: MANIFEST.in:1 — sdist 打包时包含整个 `docs` 目录。
- F-018: MANIFEST.in:2-3 — sdist 打包时排除 `docs/build`、`build`、`dist` 目录。
- F-019: MANIFEST.in:6-7 — sdist 打包时包含 LICENSE 文件和所有 `*.md` 文件。
- F-020: .gitignore:55 — Sphinx 文档构建输出目录 `docs/_build/` 被 Git 忽略。
- F-021: .readthedocs.yaml:1-17 — Read the Docs 构建配置使用 Ubuntu 22.04 + Python 3.11，Sphinx 配置文件为 `docs/source/conf.py`。
- F-022: setup.cfg:1-2 — bdist_wheel 配置为 `universal=1`，即构建通用 wheel（纯 Python、无平台限制）。
- F-023: noxfile.py:7-10 — 定义了 `docs` nox session（Python 3.11），安装 doc-requirements.txt 后运行 sphinx-build 构建 HTML 文档。
- F-024: noxfile.py:12-23 — 定义了 `docs-live` nox session，使用 sphinx-autobuild 提供实时预览服务器，忽略 `docs/build` 目录。
- F-025: .github/workflows/release.yaml:11-33 — CI 在 push 和 PR 时构建 sdist 和 wheel（`python -m build --sdist --wheel .`），上传为 artifact。
- F-026: .github/workflows/release.yaml:36-40 — 仅在 Git tag 推送时通过 `pypa/gh-action-pypi-publish` 发布到 PyPI，使用 PyPI token 认证。
- F-027: .travis.yml:1-44 — Travis CI 配置（历史遗留），用于测试文档构建和推送翻译模板到 Transifex。

## 依赖声明（兼容性 shim 的本质）

- F-028: setup.py:27-33 — install_requires 声明了五个直接依赖：`notebook`、`nbconvert`、`ipykernel`、`ipywidgets`、`jupyterlab`。
- F-029: long_description.md:7 — 安装此包即安装 Jupyter Notebook、JupyterLab 和 IPython Kernel。
- F-030: long_description.md:9-11 — 明确声明 "This is an empty metapackage for user convenience, only expressing dependencies on multiple Jupyter packages. `jupyter` should not be used as a dependency for any packages."。
- F-031: long_description.md:18 — `jupyterlab` 在元包 v1.1 版本中被加入依赖。
- F-032: long_description.md:25-27 — `qtconsole` 在元包 v1.1 版本中被移除，但仍然受支持。
- F-033: long_description.md:13-23 — 文档建议用户按需单独安装各组件，而非依赖元包：列出了 notebook、jupyterlab、ipython、ipykernel、jupyter-console、nbconvert、ipywidgets 的各自包名。

## 命令委托机制（在本包中不存在）

- F-034: setup.py:26 — 本包 py_modules 为空列表，不包含任何可执行 Python 代码。
- F-035: setup.py — 本包未定义任何 console_scripts 入口点，`jupyter` 命令行工具并非由此包提供。
- F-036: docs/source/use/jupyter-command.rst:19-21 — 文档说明 `jupyter` 命令本质上是一个 subcommand 命名空间，PATH 上的 `jupyter-foo` 命令可作为 `jupyter foo` 子命令使用。
- F-037: docs/source/use/jupyter-command.rst:29-50 — `jupyter` 命令支持 --config-dir、--data-dir、--runtime-dir、--paths、--json 等路径查询选项。
- F-038: docs/source/conf.py:175-189 — Sphinx intersphinx 映射引用了 jupytercore、jupyterclient、notebook、lab、nbconvert、nbformat、ipywidgets、ipython、qtconsole、traitlets、ipyparallel、hub 等子项目文档，确认 `jupyter` 命令由 `jupyter_core` 提供。

## 历史背景（Big Split）

- F-039: docs/source/use/advanced/migrating.rst:11-15 — 文档明确引用 "The Big Split"（https://blog.jupyter.org/the-big-split-9d7b88a031a7），说明 IPython 的语言无关组件迁移到 Jupyter 伞下。
- F-040: docs/source/use/advanced/migrating.rst:13-15 — Big Split 后 Jupyter 包含语言无关项目，IPython 继续专注于 Python。
- F-041: docs/source/use/advanced/migrating.rst:236-246 — 文档列出了 IPython 3 到 Jupyter 的模块迁移映射：`IPython.html` → `notebook`；`IPython.html.widgets` → `ipywidgets`；`IPython.kernel` → `jupyter_client` + `ipykernel`；`IPython.parallel` → `ipyparallel`；`IPython.qt.console` → `qtconsole`；`IPython.utils.traitlets` → `traitlets`；`IPython.config` → `traitlets.config`。
- F-042: docs/source/use/advanced/migrating.rst:252-255 — `IPython.kernel` 拆分为两个包：`jupyter_client`（客户端 API 和消息协议）和 `ipykernel`（IPython 内核实现）。
- F-043: docs/source/use/advanced/migrating.rst:105-109 — Big Split 后 Jupyter 不再有 IPython 的 profiles 概念。
- F-044: docs/source/use/advanced/migrating.rst:27-34 — 首次运行任何 `jupyter` 命令时，系统会自动将 IPython 配置文件**复制**（非移动）到 Jupyter 目录，可通过 `jupyter migrate` 手动重跑。
- F-045: docs/source/projects/core.rst:10-19 — 文档定义了两个核心构建块：`jupyter_client`（消息协议规范和 Python 客户端库）和 `jupyter_core`（核心功能和杂项工具）。
- F-046: docs/source/conf.py:62-64 — 文档版本标记为 4.1 / 4.1.1 alpha，反映了 Jupyter 4.x 时代（Big Split 后的版本号跳跃）。
- F-047: docs/source/conf.py:53 — Sphinx 文档项目名称为 "Jupyter Documentation"，而非某个具体子项目，说明此仓库同时承担 Jupyter 生态文档聚合的角色。
- F-048: README.md:90-93 — 元包发布频率极低（"this happens very rarely"），因为它只需要在依赖组合变化时更新。
- F-049: docs/source/conf.py:212-214 — 文档配置了 gettext 国际化支持，locale 目录为 `locale/`，支持多语言翻译（en、es、pt_BR）。
- F-050: SECURITY.md:3 — 安全策略指向 https://jupyter.org/security，不在此仓库内处理安全问题。
