---
type: reference
title: "jupyter-book CLI 事实清单"
description: "Jupyter Book v2 CLI 双层架构源码事实采集，编号 F-001 起，零推测"
tags: [jupyter-book, facts, spec]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "py/jupyter_book/__main__.py"
    facts: [F-001, F-002, F-003, F-004]
  - path: "py/jupyter_book/nodeenv.py"
    facts: [F-005, F-006, F-007, F-008, F-009, F-010]
  - path: "ts/index.ts"
    facts: [F-011, F-012, F-013]
  - path: "ts/clirun.ts"
    facts: [F-014, F-015]
  - path: "ts/build.ts"
    facts: [F-016]
  - path: "ts/init.ts"
    facts: [F-017, F-018]
  - path: "ts/clean.ts"
    facts: [F-019]
  - path: "ts/site.ts"
    facts: [F-020]
  - path: "ts/templates.ts"
    facts: [F-021, F-022, F-023, F-024]
  - path: "ts/options.ts"
    facts: [F-025]
---

# jupyter-book CLI 事实清单

> 本文档记录 Jupyter Book v2 CLI 的源码级事实，编号 F-001 起。所有事实均经过 Grep 级源码验证，不含推断性表述。

## F-001: Python 入口 main() 函数

- 路径：`py/jupyter_book/__main__.py` L30-72
- `main()` 函数是 Python 包入口（`python -m jupyter_book` 调用）
- 版本常量：`__version__ = "2.1.6"`，`NODEENV_VERSION = "22.17.0"`
- 执行流程：
  1. 调用 `find_valid_node(binary_path, test_version=test_node_version, nodeenv_version=NODEENV_VERSION)` 查找/安装 Node.js
  2. 构建新 PATH 环境变量（`os_path`）
  3. 定位编译后的 JS 文件：`dist/jupyter-book.cjs`（相对于 `__file__`）
  4. 构建参数：`[js_path, *sys.argv[1:]]`
  5. 设置环境变量 `MYST_LANG=PYTHON`
  6. Windows 使用 `subprocess.run([node_path, *jb_node_args], env=jb_env)`，非 Windows 使用 `os.execve(node_path, [node_path.name, *jb_node_args], jb_env)`

## F-002: Node.js 版本检查

- 路径：`py/jupyter_book/__main__.py` L20-27
- `test_node_version(triple_version)` 函数检查主版本号
- 允许的 Node.js 版本：18、20、22+（即 18.x, 20.x, 22.x 及以上）
- 不满足时抛出 `NodeVersionError`，提示用户从 https://nodejs.org/en/download 安装 LTS 版本

## F-003: Node.js 查找/安装错误处理

- `NodeEnvCreationError`: nodeenv 创建失败，输出安装失败提示和底层错误
- `PermissionDeniedError`: 用户拒绝安装 Node.js，输出提示信息
- 两种错误均通过 `SystemExit` 退出，返回非零状态码

## F-004: Python 包 __init__.py 为空

- 路径：`py/jupyter_book/__init__.py`
- 文件内容为空，无包级导出

## F-005: nodeenv 管理模块

- 路径：`py/jupyter_book/nodeenv.py`
- 三个自定义异常类：`PermissionDeniedError`、`NodeEnvCreationError`、`NodeVersionError`
- 环境变量控制键：`INSTALL_NODEENV_KEY = "JB_ALLOW_NODEENV"`
- 平台检测：`is_windows()` 通过 `platform.system() == "Windows"` 判断

## F-006: Node.js 版本获取

- `get_triple_node_version(node_path)`: 执行 `node -v`，通过正则 `^v(\d+)\.(\d+)\.(\d+)` 解析版本号，返回 `[major, minor, patch]` 整数列表

## F-007: Node.js 查找逻辑

- `find_installed_node()`: 使用 `shutil.which` 查找已安装的 node（Windows 查找 `node.exe`，其他平台查找 `node`）
- `find_nodeenv_path(version)`: 使用 `platformdirs.user_data_path(appname="jupyter-book", appauthor=False, version=version)` 获取 nodeenv 安装路径

## F-008: Node.js 安装提示

- `ask_to_install_node(path)`: 检查环境变量 `JB_ALLOW_NODEENV`（值为 yes/true/1/y 时自动确认），否则交互询问 `Install Node.js in '{path}'? (y/N):`

## F-009: nodeenv 环境创建

- `create_nodeenv(env_path, version)`: 调用 `python -m nodeenv -v --node={version} --prebuilt --clean-src {env_path}` 创建隔离 Node.js 环境
- 创建失败时 `shutil.rmtree(env_path)` 清理，抛出 `NodeEnvCreationError`
- 使用 `--prebuilt` 标志下载预编译二进制（非源码编译）

## F-010: find_valid_node 查找策略

- 路径：`py/jupyter_book/nodeenv.py` L75-113
- 两阶段查找：
  1. 先查找系统已安装的 Node.js（`find_installed_node()`），检查版本是否满足 `test_version()`；满足则直接返回路径
  2. 系统 Node 不可用或版本不符时，查找/创建 nodeenv 管理的 Node.js
- nodeenv 路径不存在时，打印提示信息并询问是否安装
- Windows nodeenv 可执行文件路径：`{nodeenv_path}/Scripts/node.exe`
- 非 Windows：`{nodeenv_path}/bin/node`
- 返回值：`(new_node_path, new_path)` 二元组，new_path 将 node 目录追加到 PATH

## F-011: TS CLI 入口程序

- 路径：`ts/index.ts`
- Shebang：`#!/usr/bin/env node`
- 导入 `core-js/actual` 提供旧版 Node.js 兼容
- 抑制 punycode 弃用警告（通过覆盖 `process.emit` 过滤 `DeprecationWarning`）
- 使用 `commander` 的 `Command` 创建 CLI 程序

## F-012: 白标（White-labelling）环境变量

- 路径：`ts/index.ts` L27-32
- 启动时设置 5 个环境变量实现白标定制：
  - `MYSTMD_READABLE_NAME = "Jupyter Book"`
  - `MYSTMD_BINARY_NAME = "jupyter book"`
  - `MYSTMD_HOME_URL = "https://jupyterbook.org/stable"`
  - `MYSTMD_NPM_BINARY_NAME = "jupyter-book"`
  - `MYSTMD_NPM_PACKAGE_NAME = "jupyter-book"`

## F-013: CLI 命令注册

- 路径：`ts/index.ts` L40-51
- 注册 5 个子命令：
  - `makeInitCLI(program)` → init 命令
  - `makeBuildCLI(program)` → build 命令
  - `makeStartCLI(program)` → start 命令
  - `makeCleanCLI(program)` → clean 命令
  - `makeTemplatesCLI(program)` → templates 命令（含 list/download 子命令）
- 全局选项：`-d, --debug`（输出错误日志）
- `addDefaultCommand(program)` 设置无参数时默认执行 init
- 版本通过 `-v, --version` 输出

## F-014: clirun 通用命令执行器

- 路径：`ts/clirun.ts` L10-37
- 函数签名：`clirun(sessionClass, func, program, nArgs?)`
- 返回一个 async 函数，接收 commander 解析的 args
- 执行流程：
  1. 从 program.opts() 获取 debug 选项
  2. 创建 chalkLogger（debug 模式用 LogLevel.debug，否则 LogLevel.info）
  3. 创建 session 实例：`new sessionClass({ logger })`
  4. 调用 `session.reload()`
  5. 获取并记录 Node 版本（`getNodeVersion`/`logVersions`）
  6. 检查 Node 版本（`checkNodeVersion`），不满足则 `process.exit(1)`
  7. 在 try/catch 中执行 `func(session, ...args.slice(0, nArgs))`
  8. 错误时输出 debug 栈追踪、错误消息、版本信息，`process.exit(1)`
  9. 执行 `session.showUpgradeNotice?.()` 显示升级提示

## F-015: clirun 依赖 myst-cli

- `clirun` 从 `myst-cli` 导入：`Session` 类、`checkNodeVersion`、`getNodeVersion`、`logVersions`、`ISession` 接口
- 从 `myst-cli-utils` 导入：`chalkLogger`、`LogLevel`

## F-016: build 命令委托

- 路径：`ts/build.ts`
- `makeBuildCLI(program)` 直接调用 myst-cli 的 `makeBuildCommand()`，action 使用 `clirun(Session, build, program)`
- `build` 函数和 `Session` 类完全从 `myst-cli` 导入
- build 命令本身没有 Jupyter Book 自定义逻辑，纯委托

## F-017: init 命令

- 路径：`ts/init.ts`
- `makeInitCLI(program)` 创建 `init` 子命令
- 描述：`Initialize a mystmd project in the current directory`
- 选项：
  - `--project`：初始化 mystmd 项目配置
  - `--site`：初始化 mystmd 站点配置（来自 myst-cli 的 `makeSiteOption`）
  - `--write-toc`：在 myst.yml 中生成目录
  - `--gh-pages`：创建 GitHub Pages 部署 Action
  - `--gh-curvenote`：创建 Curvenote 部署 Action
- Action 委托 myst-cli 的 `init` 函数：`clirun(Session, init, program)`

## F-018: 默认命令执行 init

- 路径：`ts/init.ts` L33-44
- `addDefaultCommand(program)`: 当 program.args.length === 0 时，执行 `clirun(Session, init, program)(args)`，即无参数运行 jupyter-book 等同于 `jupyter-book init`
- 有无效参数时输出错误信息和帮助文本，退出码 1

## F-019: clean 命令委托

- 路径：`ts/clean.ts`
- `makeCleanCLI(program)` 直接调用 myst-cli 的 `makeCleanCommand()`，action 使用 `clirun(Session, clean, program)`
- 纯委托，无自定义逻辑

## F-020: start 命令委托

- 路径：`ts/site.ts`
- `makeStartCLI(program)` 直接调用 myst-cli 的 `makeStartCommand()`，action 使用 `clirun(Session, startServer, program)`
- 纯委托，无自定义逻辑（startServer 来自 myst-cli）

## F-021: templates 命令系统

- 路径：`ts/templates.ts`
- `makeTemplatesCLI(program)` 创建 `templates` 命令，含两个子命令：
  - `list`: 列出/筛选/查看模板详情
  - `download`: 下载公共模板到本地
- 模板类型：`TemplateKind.tex`、`TemplateKind.typst`、`TemplateKind.docx`、`TemplateKind.site`（`allTemplates` 常量）
- 支持的格式选项：`--pdf`、`--tex`、`--typst`、`--docx`、`--site`、`--force`、`--tag`

## F-022: templates list 子命令

- `listTemplatesCLI(session, name?, opts?)`:
  - 提供 name 参数时，获取单个模板详情（支持本地 .yml 文件或远程公共模板），输出 ID、Version、Authors、Description、Tags、Parts、Options
  - 不提供 name 时，调用 `listPublicTemplates(session, kinds)` 列出所有公共模板
  - 支持 `--tag` 按标签过滤（逗号分隔多标签）
- 从 `myst-templates` 导入：`listPublicTemplates`、`fetchPublicTemplate`

## F-023: templates download 子命令

- `downloadTemplateCLI(session, template, path?, opts?)`:
  - 通过 `getKindFromName(template)` 从模板名前缀（tex//typst/docx/site）推断类型
  - 调用 `resolveInputs(session, { template, kind, buildDir })` 解析模板路径和 URL
  - 目标路径已存在时，除非 `--force` 否则报错退出
  - 调用 `downloadTemplate(session, { templatePath, templateUrl })` 下载

## F-024: templates 依赖 myst-templates

- 从 myst-templates 导入：`downloadTemplate`、`fetchPublicTemplate`、`listPublicTemplates`、`resolveInputs`、`TEMPLATE_YML`、`TemplateYmlResponse`
- 从 myst-common 导入：`TemplateKind`

## F-025: Jupyter Book 自定义 CLI 选项

- 路径：`ts/options.ts`
- 定义 4 个选项工厂函数：
  - `makeProjectOption(description)`: `--project` 布尔选项，默认 false
  - `makeWriteTOCOption()`: `--write-toc` 选项，implies({ writeTOC: true })
  - `makeGithubPagesOption()`: `--gh-pages` 布尔选项，创建 GitHub Pages Action
  - `makeGithubCurvenoteOption()`: `--gh-curvenote` 布尔选项，创建 Curvenote Action
- 这些是 jupyter-book 相对于 myst-cli 新增的选项（myst-cli 自身也有 --project/--site 等选项）
