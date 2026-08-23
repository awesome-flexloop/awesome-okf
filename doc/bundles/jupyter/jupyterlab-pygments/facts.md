---
okf_version: '0.2'
generated: '2026-08-22'
tags:
- jupyter
- jupyterlab
- pygments
- syntax-highlighting
- css
- theme
sources:
- ../../../../../external/libs/jupyter/jupyterlab_pygments/README.md
- ../../../../../external/libs/jupyter/jupyterlab_pygments/package.json
- ../../../../../external/libs/jupyter/jupyterlab_pygments/jupyterlab_pygments/__init__.py
- ../../../../../external/libs/jupyter/jupyterlab_pygments/jupyterlab_pygments/style.py
- ../../../../../external/libs/jupyter/jupyterlab_pygments/generate_css.py
- ../../../../../external/libs/jupyter/jupyterlab_pygments/src/index.ts
- ../../../../../external/libs/jupyter/jupyterlab_pygments/style/index.js
- ../../../../../external/libs/jupyter/jupyterlab_pygments/style/index.css
- ../../../../../external/libs/jupyter/jupyterlab_pygments/pyproject.toml
- ../../../../../external/libs/jupyter/jupyterlab_pygments/install.json
- ../../../../../external/libs/jupyter/jupyterlab_pygments/binder/environment.yml
- ../../../../../external/libs/jupyter/jupyterlab_pygments/notebooks/Example.ipynb
- ../../../../../external/libs/jupyter/jupyterlab_pygments/.copier-answers.yml
type: Facts
title: jupyterlab-pygments 源码事实清单
---

# jupyterlab-pygments 事实清单

> 一个 Pygments 语法高亮主题包，使用 JupyterLab CSS 变量实现代码高亮，使 Pygments 生成的 HTML 能够跟随 JupyterLab 主题（亮色/暗色）切换。同时作为 JupyterLab 纯 CSS 扩展（no-op plugin）。

## 包概览

- F-001: README.md:3-6 — 包目的：为 pygments 提供使用 JupyterLab CSS 变量的语法着色主题，使 pygments 生成的 HTML 能够使用 JupyterLab 主题
- F-002: README.md:30 — 依赖 pygments >= 2.4.1
- F-003: README.md:31-32 — 使用的 CSS 变量对应 @jupyterlab/codemirror 包定义的 CodeMirror 语法着色主题，支持 @jupyterlab/codemirror 版本 0.19.1、^1.0、^2.0
- F-004: README.md:36-39 — 已知限制：Pygments 生成的 HTML 和 CSS 类粒度不足以重现 CodeMirror 的所有细节，例如无法区分属性和普通名称
- F-005: README.md:16-26 — 安装方式：conda-forge（conda install -c conda-forge jupyterlab_pygments）或 PyPI（pip install jupyterlab_pygments）
- F-006: package.json:3 — npm 包版本 0.3.0

## Python 包结构

- F-007: jupyterlab_pygments/__init__.py:1-8 — 版本导入 fallback：优先从 _version 导入 __version__，失败则设为 "dev"（开发模式无 editable install 时）
- F-008: jupyterlab_pygments/__init__.py:8 — 从 .style 导入 JupyterStyle 类
- F-009: jupyterlab_pygments/__init__.py:11-15 — _jupyter_labextension_paths() 返回 [{"src": "labextension", "dest": "jupyterlab_pygments"}]，注册 JupyterLab labextension 路径

## JupyterStyle Pygments 主题类

- F-010: jupyterlab_pygments/style.py:4 — 从 pygments.style 导入 Style 基类
- F-011: jupyterlab_pygments/style.py:5-7 — 导入 Pygments token 类型：Comment、Error、Generic、Keyword、Literal、Name、Number、Operator、Other、Punctuation、String、Text、Whitespace
- F-012: jupyterlab_pygments/style.py:10 — JupyterStyle 继承 pygments.style.Style
- F-013: jupyterlab_pygments/style.py:11-48 — 类 docstring 说明：目标是模仿 JupyterLab 的 codemirror 主题，并列出已知局限（点号在 pygments 中为 Operator 而 codemirror 中为普通文本；属性访问中的属性名在 pygments 中为 Name 而 codemirror 中可区分 property）
- F-014: jupyterlab_pygments/style.py:23-47 — docstring 中列出了 24 个可用的 CSS 变量：--jp-mirror-editor-keyword-color、--jp-mirror-editor-atom-color、--jp-mirror-editor-number-color、--jp-mirror-editor-def-color、--jp-mirror-editor-variable-color、--jp-mirror-editor-variable-2-color、--jp-mirror-editor-variable-3-color、--jp-mirror-editor-punctuation-color、--jp-mirror-editor-property-color、--jp-mirror-editor-operator-color、--jp-mirror-editor-comment-color、--jp-mirror-editor-string-color、--jp-mirror-editor-string-2-color、--jp-mirror-editor-meta-color、--jp-mirror-editor-qualifier-color、--jp-mirror-editor-builtin-color、--jp-mirror-editor-bracket-color、--jp-mirror-editor-tag-color、--jp-mirror-editor-attribute-color、--jp-mirror-editor-header-color、--jp-mirror-editor-quote-color、--jp-mirror-editor-link-color、--jp-mirror-editor-error-color
- F-015: jupyterlab_pygments/style.py:50 — default_style = ''（空字符串，不设置默认前景色）
- F-016: jupyterlab_pygments/style.py:51 — background_color = 'var(--jp-cell-editor-background)'（使用 JupyterLab cell 编辑器背景变量）
- F-017: jupyterlab_pygments/style.py:52 — highlight_color = 'var(--jp-cell-editor-active-background)'（高亮背景使用活动编辑器背景变量）
- F-018: jupyterlab_pygments/style.py:54-133 — styles 字典定义各 token 类型到 CSS 值的映射
- F-019: jupyterlab_pygments/style.py:55 — Text → 'var(--jp-mirror-editor-variable-color)'（无 CSS 类）
- F-020: jupyterlab_pygments/style.py:56 — Whitespace → ''（CSS 类 'w'）
- F-021: jupyterlab_pygments/style.py:57 — Error → 'var(--jp-mirror-editor-error-color)'（CSS 类 'err'）
- F-022: jupyterlab_pygments/style.py:60 — Comment → 'italic var(--jp-mirror-editor-comment-color)'（CSS 类 'c'，斜体）
- F-023: jupyterlab_pygments/style.py:66 — Keyword → 'bold var(--jp-mirror-editor-keyword-color)'（CSS 类 'k'，粗体）
- F-024: jupyterlab_pygments/style.py:74 — Operator → 'bold var(--jp-mirror-editor-operator-color)'（CSS 类 'o'，粗体）
- F-025: jupyterlab_pygments/style.py:75 — Operator.Word → ''（CSS 类 'ow'，无特殊样式）
- F-026: jupyterlab_pygments/style.py:80 — String → 'var(--jp-mirror-editor-string-color)'（CSS 类 's'）
- F-027: jupyterlab_pygments/style.py:93 — Number → 'var(--jp-mirror-editor-number-color)'（CSS 类 'm'）
- F-028: jupyterlab_pygments/style.py:100-118 — Name 及其子类型（Attribute/Builtin/Class/Constant/Decorator/Entity/Exception/Function/Property/Label/Namespace/Other/Tag/Variable 等）均映射为空字符串（继承 Text 的变量色），这是已知局限
- F-029: jupyterlab_pygments/style.py:120-130 — Generic 及其子类型（Deleted/Emph/Error/Heading/Inserted/Output/Prompt/Strong/Subheading/Traceback）均为空
- F-030: jupyterlab_pygments/style.py:132 — Punctuation → 'var(--jp-mirror-editor-punctuation-color)'（CSS 类 'p'）
- F-031: jupyterlab_pygments/style.py:61-72,77-78,81-91,94-98,101-117,121-129 — 大量子 token 类型被注释掉（不单独设置样式，继承父类型），保持样式简洁

## CSS 生成脚本

- F-032: generate_css.py:1-3 — 脚本功能：从 jupyterlab-pygments 的 JupyterStyle 生成 pygments 样式表
- F-033: generate_css.py:6 — 从 jupyterlab_pygments 包导入 JupyterStyle
- F-034: generate_css.py:8 — 从 pygments.formatters 导入 HtmlFormatter
- F-035: generate_css.py:11-17 — CSS 文件头部前缀包含版权声明和"This file was auto-generated by generate_css.py"标记
- F-036: generate_css.py:21 — 创建 HtmlFormatter(style=JupyterStyle) 实例，使用 JupyterStyle 格式化
- F-037: generate_css.py:22 — formatter.get_style_defs('.highlight') 生成 .highlight 选择器下的 CSS 规则
- F-038: generate_css.py:23-25 — 过滤仅保留以 '.highlight' 开头的 CSS 行
- F-039: generate_css.py:27-29 — 将生成的 CSS 写入 style/base.css 文件（包含 prefix + 高亮 CSS）

## JupyterLab 前端扩展（纯 CSS 插件）

- F-040: src/index.ts:1-4 — 导入 JupyterFrontEnd 和 JupyterFrontEndPlugin 来自 @jupyterlab/application
- F-041: src/index.ts:9-15 — plugin 定义：id 为 'jupyterlab_pygments:plugin'，autoStart: true，activate 函数体为空（注释 "This plugin only brings CSS style rules"）
- F-042: src/index.ts:17 — export default plugin

## 样式文件

- F-043: style/index.js:1 — 仅导入 './base.css'（由 generate_css.py 生成）
- F-044: style/index.css:1 — @import url('base.css')（导入生成的 base.css）
- F-045: style/base.css — 由 generate_css.py 自动生成，包含 pygments 语法高亮的 CSS 规则（构建产物，不在源码中维护）

## 构建系统

- F-046: pyproject.toml:1-7 — 构建后端使用 hatchling + hatch-nodejs-version + jupyterlab>=4.0.0,<5
- F-047: pyproject.toml:10 — Python 包名：jupyterlab_pygments
- F-048: pyproject.toml:12 — requires-python = ">=3.8"
- F-049: pyproject.toml:28 — dependencies = []（无核心 Python 依赖，运行时依赖 pygments 但未在 dependencies 中声明——由 conda/pip 安装时自动拉取）
- F-050: pyproject.toml:29-35 — 动态字段：version、description、authors、urls、keywords（从 package.json 读取）
- F-051: pyproject.toml:40-41 — Hatch version source 为 nodejs（从 package.json 读取版本号）
- F-052: pyproject.toml:59-61 — Wheel shared-data：labextension 目录映射到 share/jupyter/labextensions/jupyterlab_pygments，install.json 也安装到该目录
- F-053: pyproject.toml:66-77 — hatch-jupyter-builder 钩子：build-function 为 npm_builder，ensured-targets 确保 labextension/static/style.js 和 labextension/package.json 存在，skip-if-exists 避免重复构建
- F-054: pyproject.toml:79-83 — 生产构建命令：build:prod（jlpm 执行）
- F-055: pyproject.toml:85-91 — editable 安装构建命令：install:extension，source_dir=src，build_dir=jupyterlab_pygments/labextension
- F-056: package.json:32 — npm build 脚本：build:css（python generate_css.py）→ build:lib（tsc）→ build:labextension:dev
- F-057: package.json:33 — build:css 调用 python generate_css.py 从 Python JupyterStyle 类生成 CSS
- F-058: package.json:37 — build:prod 流程：clean → build:css → build:lib → build:labextension
- F-059: package.json:41 — clean:lib 清理 lib/、tsconfig.tsbuildinfo、style/base.css（注意 base.css 是构建产物）
- F-060: package.json:58-59 — npm 依赖：@jupyterlab/application ^4.0.8、@types/node ^20.9.0（运行时仅依赖 application 插件框架）
- F-061: package.json:94-97 — jupyterlab 配置：extension: true（标记为 JupyterLab 扩展），outputDir: jupyterlab_pygments/labextension
- F-062: install.json:1-5 — install.json 指定 packageManager 为 python，packageName 为 jupyterlab_pygments

## 项目元数据

- F-063: package.json:4 — npm 描述："Pygments theme using JupyterLab CSS variables"
- F-064: package.json:14 — 许可证：BSD-3-Clause
- F-065: .copier-answers.yml — 由 Copier 模板生成（与 extension-template 一致）
- F-066: binder/environment.yml — Binder 环境配置（用于 mybinder.org 演示）
- F-067: notebooks/Example.ipynb — 示例 Jupyter notebook（演示语法高亮效果）
