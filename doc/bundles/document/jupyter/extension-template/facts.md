---
okf_version: '0.2'
generated: '2026-08-22'
tags:
- jupyter
- jupyterlab
- extension
- template
sources:
- ../../../../../external/libs/jupyter/extension-template/README.md
- ../../../../../external/libs/jupyter/extension-template/copier.yml
- ../../../../../external/libs/jupyter/extension-template/template/.github/workflows/enforce-label.yml
type: Facts
title: extension-template 源码事实清单
---

# extension-template Facts

## 项目元数据

- F-001: README.md:1 — 项目名称为 "JupyterLab extension template"
- F-002: README.md:5-6 — 基于 copier 模板（非 cookiecutter），用于创建 JupyterLab 扩展
- F-003: README.md:7-10 — 支持四种扩展类型：frontend（纯前端TS）、mimerenderer（MIME渲染器）、frontend-and-server（前后端）、theme（主题）
- F-004: README.md:19-20 — 安装要求：copier~=9.2 + jinja2-time
- F-005: README.md:38 — 使用命令：copier copy --trust https://github.com/jupyterlab/extension-template .
- F-006: README.md:49 — 支持 --vcs-ref 参数指定历史版本
- F-007: README.md:66 — 支持 copier update 命令更新已生成项目的模板

## Copier 配置

- F-008: copier.yml:1 — 最低 copier 版本要求 "7.1.0"
- F-009: copier.yml:2 — _subdirectory: "template"，模板内容在 template/ 子目录
- F-010: copier.yml:3-4 — 启用 jinja2_time.TimeExtension Jinja 扩展
- F-011: copier.yml:6-14 — kind 参数：str 类型，默认 "frontend"，选项为 frontend/mimerenderer/frontend-and-server/theme
- F-012: copier.yml:16-23 — author_name 参数：必填，validator 检查非空且不以空白开头
- F-013: copier.yml:25-34 — author_email 参数：可选，validator 验证邮箱格式
- F-014: copier.yml:36-39 — labextension_name 参数：JS 包名，theme 类型默认 "mytheme"，其他默认 "myextension"
- F-015: copier.yml:41-44 — python_name 参数：Python 包名，由 labextension_name 自动转换（- → _，/ → _，trim @）
- F-016: copier.yml:46-49 — project_short_description 默认 "A JupyterLab extension."
- F-017: copier.yml:51-55 — has_settings 参数：bool 类型，仅非 mimerenderer 类型显示，默认 no
- F-018: copier.yml:57-60 — has_binder 参数：bool 类型，默认 no
- F-019: copier.yml:62-65 — advanced 参数：bool 类型，控制高级选项显示，默认 no
- F-020: copier.yml:67-74 — yarn_linker 参数：仅 advanced 模式显示，选项 node-modules/pnpm，默认 node-modules
- F-021: copier.yml:76-79 — test 参数：bool 类型，默认 yes
- F-022: copier.yml:81-84 — has_ai_rules 参数：是否包含 AI 编程规则 AGENTS.md，默认 no
- F-023: copier.yml:86-96 — AI 规则选项：create_claude_symlink（CLAUDE.md）、create_gemini_symlink（GEMINI.md），均在 has_ai_rules 时显示
- F-024: copier.yml:98-101 — repository 参数：Git 远程仓库 URL
- F-025: copier.yml:103-138 — mimerenderer 专属参数：viewer_name、mimetype、mimetype_name、file_extension、data_format（string/json）
- F-026: copier.yml:140-146 — _tasks：生成后执行 Python 命令创建 CLAUDE.md 和 GEMINI.md 符号链接（条件性执行）

## 模板目录结构

- F-027: template/ 目录包含所有模板文件，使用 .jinja 扩展名
- F-028: template/ 使用 Jinja2 条件语法（{% if %}...{% endif %}）控制文件/代码片段的条件生成，而非 cookiecutter 的 hooks 删除方式
- F-029: template/tsconfig.json.jinja — TypeScript 配置模板
- F-030: template/package.json.jinja — npm 包配置模板
- F-031: template/pyproject.toml.jinja — Python 包配置模板
- F-032: template/install.json.jinja — JupyterLab 扩展安装元数据
- F-033: template/src/index.ts.jinja — 扩展入口点模板（四种类型不同实现）
- F-034: template/style/ 目录包含 CSS 样式模板
- F-035: template/.github/workflows/ 目录包含 CI/CD 工作流模板

## package.json 模板

- F-036: package.json.jinja:2-3 — name 使用 labextension_name，version "0.1.0"
- F-037: package.json.jinja:6-8 — keywords 固定为 jupyter/jupyterlab/jupyterlab-extension
- F-038: package.json.jinja:14 — license 固定为 BSD-3-Clause
- F-039: package.json.jinja:19-24 — files 包含 lib/**、style/**、src/**，has_settings 时额外包含 schema/*.json
- F-040: package.json.jinja:27 — theme 类型无 "style" 字段
- F-041: package.json.jinja:33-57 — scripts 定义：build、build:prod、build:labextension、build:lib、clean、eslint、lint、prettier、stylelint、test（条件）、watch 等
- F-042: package.json.jinja:59-65 — dependencies 根据 kind 变化：非mimerenderer依赖@jupyterlab/application；theme额外依赖@jupyterlab/apputils；frontend-and-server额外依赖@jupyterlab/coreutils和@jupyterlab/services；has_settings额外依赖@jupyterlab/settingregistry；mimerenderer依赖@jupyterlab/rendermime-interfaces和@lumino/widgets
- F-043: package.json.jinja:67-97 — devDependencies 包含 @jupyter/builder、TypeScript、ESLint、Prettier、Stylelint、Jest（条件）、jupyter-builder 等
- F-044: package.json.jinja:112-128 — jupyterlab 配置块：frontend-and-server 类型有 discovery.server 配置；mimerenderer 设置 mimeExtension: true，其他设置 extension: true；outputDir 统一为 {python_name}/labextension；theme 类型设置 themePath
- F-045: package.json.jinja:103-108 — sideEffects 根据 kind 不同配置

## pyproject.toml 模板

- F-046: pyproject.toml.jinja:2-3 — 构建依赖：hatchling>=1.5.0、hatch-nodejs-version>=0.3.2、jupyter-builder>=1.2.0,<2
- F-047: pyproject.toml.jinja:10 — requires-python = ">=3.10"
- F-048: pyproject.toml.jinja:11-26 — classifiers 包含 JupyterLab 4、Extensions、Prebuilt，条件性包含 Mime Renderers/Themes
- F-049: pyproject.toml.jinja:27-29 — dependencies 仅 frontend-and-server 类型包含 jupyter_server>=2.13.0,<3
- F-050: pyproject.toml.jinja:46 — 版本源为 nodejs（从 package.json 读取）
- F-051: pyproject.toml.jinja:55-58 — wheel shared-data 映射：labextension 到 share/jupyter/labextensions/，install.json 到对应目录；frontend-and-server 额外映射 jupyter-config
- F-052: pyproject.toml.jinja:63-80 — hatch-jupyter-builder 构建钩子：build_cmd 为 "build:prod"，使用 jlpm；editable 模式使用 "install:extension"
- F-053: pyproject.toml.jinja:85-91 — jupyter-releaser hooks：before-build-npm 安装依赖并构建，before-build-python 清理

## TypeScript 入口模板

- F-054: src/index.ts.jinja:1-55 — 非 mimerenderer 类型：导出 JupyterFrontEndPlugin，id 为 {labextension_name}:plugin，autoStart: true
- F-055: src/index.ts.jinja:18-21 — theme 类型 requires [IThemeManager]，注册 CSS 主题（isLight: true）
- F-056: src/index.ts.jinja:19-20 — has_settings 类型 optional: [ISettingRegistry]，加载设置并打印
- F-057: src/index.ts.jinja:41-51 — frontend-and-server 类型调用 requestAPI('hello') 与后端通信
- F-058: src/index.ts.jinja:56-132 — mimerenderer 类型：实现 IRenderMime.IExtension，定义 OutputWidget 继承 Widget 实现 IRenderMime.IRenderer，renderModel 方法渲染内容；rendererFactory 定义 mimeTypes 和 createRenderer；fileTypes 定义文件扩展名关联

## Python 包模板

- F-059: {{python_name}}/__init__.py.jinja:1-8 — 从 _version 导入 __version__，导入失败时 fallback 为 "dev" 并警告
- F-060: {{python_name}}/__init__.py.jinja:13-17 — _jupyter_labextension_paths() 返回 labextension 路径配置
- F-061: {{python_name}}/__init__.py.jinja:20-36 — frontend-and-server 类型额外定义 _jupyter_server_extension_points() 和 _load_jupyter_server_extension()，调用 setup_route_handlers()

## 安装元数据

- F-062: install.json.jinja:2-4 — packageManager: "python"，packageName 使用 python_name，提供卸载说明

## 测试与 CI

- F-063: template/{% if test %}ui-tests{% endif %}/ — test 为 yes 时生成 UI 测试目录（Playwright）
- F-064: template/{% if test and kind == 'frontend-and-server' %}tests{% endif %}/ — frontend-and-server + test 时生成 Python 后端测试
- F-065: template/.github/workflows/build.yml.jinja — 构建工作流模板
- F-066: template/.github/workflows/enforce-label.yml、check-release.yml、prep-release.yml、publish-release.yml — 发布相关工作流
