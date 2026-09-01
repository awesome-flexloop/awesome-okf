---
type: Concept
title: "08 构建系统与运行模式"
description: "JupyterLab 三种运行模式（Core/Dev/App）、Rspack 构建管线、singletonPackages 单例约束、staging 目录结构、jlpm 包管理器与 Hatch 构建钩子"
tags: [jupyterlab, build, rspack, webpack, jlpm, yarn, hatch, core-mode, dev-mode, app-mode, staging]
generated:
  by: reference_agent/trae-cn
  at: "2026-08-23"
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: source-map
    resource: /references/source-code-map.md
    title: JupyterLab 源码文件地图
---

JupyterLab 的构建系统负责将 TypeScript/Lumino/React 前端源码打包为浏览器可执行的静态资源，并通过三种运行模式适配不同部署场景。构建系统经历了从 Webpack 到 Rspack 的迁移，使用自定义的 jlpm（Yarn）包管理器，并通过 Hatch 构建钩子集成到 Python 包的安装流程中。

## 三种运行模式

LabApp 定义了三种运行模式（labapp.py:432-445，F-080），通过命令行标志切换，决定静态资源来源、扩展加载策略和 UI 提示：

### Core mode（核心模式）

通过 `--core-mode` 启动（labapp.py:532-541，F-081）。此模式使用 pip 包内置的预构建 JS 资源（`jupyterlab/static/` 目录），**不加载任何第三方扩展**，`labextensions_path` 为空列表（F-088）。构建检查和扩展管理 API 被禁用——`buildAvailable` 和 `buildCheck` 均为 False（F-090），前端不显示构建 UI。

Core mode 适用于最小化部署、受限环境或调试核心功能。它不是"开发模式"，反而最接近"生产最小化部署"——不依赖外部网络，不加载用户安装的扩展。

### Dev mode（开发模式）

通过 `--dev-mode` 启动（labapp.py:543-551，F-082）。此模式使用仓库根目录下 `dev_mode/` 目录中的本地构建资源，面向 JupyterLab 核心开发者。页面顶部显示红色条带提示（通过 `page_config` 中的 `devMode` 标志控制，F-091），明确告知用户当前运行的是未发布的开发版本。

Dev mode 同样禁用构建 UI（`buildAvailable`/`buildCheck` 为 False），但资源来自本地源码构建，支持 watch 模式实现增量编译和热重载。开发者通常使用 `pip install -e .` + `jupyter lab --dev-mode --watch` 工作流。

### App mode（应用模式）

通过 `--app-dir <path>` 启动（F-080），是默认的正常使用模式。App mode 使用用户指定目录（或通过 `get_app_dir()` 按优先级查找的目录）下的静态资源和已安装扩展。该目录包含 `staging/`（构建配置和 node_modules）、`static/`（构建输出）、`extensions/`、`settings/` 等子目录。

App mode 下 `buildAvailable` 为 True，前端显示构建状态和扩展管理 UI。当 source 扩展变更后需要运行 `jupyter lab build` 重新打包。如果静态资源不存在或构建失败，LabApp 注册 `ErrorHandler` 显示错误页面而非退出进程（F-107），服务器仍在运行。

### 应用目录解析

`get_app_dir()` 函数（commands.py:165-208，F-128）按以下优先级确定 app 目录：

1. `JUPYTERLAB_DIR` 环境变量
2. `sys.prefix/share/jupyter/lab`
3. 用户级 site-packages 对应的 share 目录
4. `/usr/local/share/jupyter/lab`
5. 相对路径推导

`ensure_dev()`/`ensure_core()` 函数（commands.py:261-282，F-133）在启动时惰性检查对应模式的静态资源是否存在。

## Rspack 构建

JupyterLab 4.x 使用 Rspack 替代 Webpack 作为前端打包器。Rspack 是用 Rust 编写的高性能 JavaScript 打包器，与 Webpack 生态兼容但构建速度显著提升。

### 构建脚本

`jupyterlab/staging/package.json` 定义了完整的构建脚本（staging/package.json:6-20，F-137）：

| 脚本 | 用途 |
|------|------|
| `build` / `build:dev` | 开发构建（`rspack --config webpack.config.js`） |
| `build:prod` | 生产构建（不压缩） |
| `build:prod:minimize` | 生产构建（压缩） |
| `build:prod:release` | 发布构建 |
| `watch` | 监听模式，增量编译 |
| `build:prod:minimize:doctor` | 使用 Rsdoctor 分析构建产物 |
| `build:prod:minimize:report` | 使用 webpack-bundle-analyzer 生成分析报告 |

构建工具链版本锁定为 `@rspack/cli` 和 `@rspack/core` ^2.0.2（staging/package.json:213-214，F-150）。Node.js 要求 >= 20.0.0（staging/package.json:233，F-018）。

### 构建完成检测

`RSPACK_EXPECT` 正则（commands.py:56，F-125）匹配构建完成的输出，包含 `"theme-light-extension/style/theme.css"` 和 `"Rspack compiled"` 两个标志。`WatchHelper` 使用此正则判断 watch 模式何时首次编译完成。

### 构建流程

`_AppHandler.build()` 方法（commands.py:768-817）执行完整构建：

1. 判断 `production` 模式：当 `production=None` 时，根据是否存在 linked/local 包自动判断（有则为开发模式，F-134）。
2. 若 `splice_source` 为 True，先在仓库根目录运行 `yarn build:packages` 构建 source 包。
3. 调用 `_populate_staging()` 将 core_data 和扩展配置填充到 staging 目录。
4. 在 staging 目录运行 `yarn install` 安装依赖。
5. 调用 `dedupe_yarn()` 使用 `yarn-berry-deduplicate` 的 `fewerHighest` 策略减少重复依赖（F-131）。
6. 运行 `yarn run build:prod[:minimize]` 执行 Rspack 打包。

## singletonPackages 机制

`singletonPackages` 是 JupyterLab 构建系统中最关键的约束之一（staging/package.json:296-365，F-139）。它是一个包名列表，确保这些包在整个应用——包括核心代码和所有 federated 扩展——中只有**一个实例**。

列表包含约 70 个包，分为几类：

- **UI 框架**：`react`、`react-dom`
- **Lumino 组件框架**（15 个包）：`@lumino/widgets`、`@lumino/signaling`、`@lumino/commands`、`@lumino/application` 等
- **CodeMirror 6**（3 个包）：`@codemirror/language`、`@codemirror/state`、`@codemirror/view`
- **CRDT 协作**：`yjs`、`@jupyter/ydoc`
- **JupyterLab 核心包**（40 个）：`@jupyterlab/application`、`@jupyterlab/notebook`、`@jupyterlab/cells`、`@jupyterlab/services`、`@jupyterlab/docregistry`、`@jupyterlab/rendermime` 等
- **Lezer 解析器**（2 个）：`@lezer/common`、`@lezer/highlight`
- **Web Components**（2 个）：`@microsoft/fast-element`、`@microsoft/fast-foundation`

如果没有 singleton 约束，不同扩展可能依赖同一包的不同版本，导致多实例问题。例如，React 多实例会导致 Hook 报错和 Context 丢失；Lumino 多实例会导致 `instanceof` 检查失败和信号槽断连；Yjs 多实例会导致 CRDT 文档无法同步。singletonPackages 通过 Rspack 的 module federation 和共享依赖配置在运行时强制去重。

## staging 目录

`jupyterlab/staging/` 是生产构建的 staging 目录（F-035），包含一个名为 `@jupyterlab/application-top` 的私有 npm 包（staging/package.json:2，F-036）。这个包是构建入口，不发布到 npm，仅用于聚合所有核心扩展和配置。

`package.json` 的 `jupyterlab` 字段定义了构建的核心数据（staging/package.json:235-368，F-138）：

- **name**：`"JupyterLab"`
- **version**：`"4.7.0a1"`
- **extensions**：46 个核心扩展的映射表，键为包名，值为入口路径（空字符串表示默认入口）
- **mimeExtensions**：5 个 MIME 渲染扩展（JavaScript、JSON、Mermaid、PDF、Vega5）
- **singletonPackages**：约 70 个单例包列表
- **buildDir**：`"./build"`（Rspack 中间输出）
- **outputDir**：`".."`（输出到上级目录，即 `static/`）
- **staticDir**：`"../static"`（最终静态资源目录）
- **linkedPackages**：`{}`（本地链接的包，开发时使用）

构建时，`_AppHandler` 深拷贝 core_data（commands.py:694，F-130），合并用户安装的扩展信息后写入 staging 目录的 `package.json`，然后执行 Rspack 构建。深拷贝确保构建过程中的修改不会污染原始的 CoreConfig 数据。

## jlpm 包管理器

jlpm（JupyterLab Package Manager）是 JupyterLab 对 Yarn 的包装。它从 `jupyter_builder.jlpm` 导入 `YARN_PATH`（commands.py:32），指向一个捆绑的 Yarn Berry（Yarn 3）发行版。所有构建相关的 Node.js 命令都通过 `node YARN_PATH` 执行，确保跨平台和跨环境使用一致的 Yarn 版本。

关键 Yarn 操作：

- **安装依赖**：`ensure_node_modules()` 运行 `yarn --immutable --immutable-cache`（commands.py:248，F-132），确保锁文件一致；失败则重新安装。
- **构建包**：`yarn build` 或 `yarn run build:prod`
- **Watch 模式**：`yarn run watch`
- **去重**：`dedupe_yarn()` 调用 `yarn-berry-deduplicate`

根 `package.json` 声明 `packageManager: "yarn@3.5.0"`（F-016），Lerna 配置为 independent 版本模式、npmClient 为 yarn（F-017）。

## AppOptions 配置类

`AppOptions` 定义在 `commands.py:353`（F-129），继承自 traitlets 的 `HasTraits`，是构建系统的配置中心：

| Trait | 类型 | 说明 |
|-------|------|------|
| `app_dir` | Unicode | 应用目录，默认通过 `get_app_dir()` 推导 |
| `use_sys_dir` | Bool | 是否用系统目录遮蔽默认 app_dir（默认 True） |
| `logger` | Instance(logging.Logger) | 日志记录器，默认 `"jupyterlab"` logger |
| `core_config` | Instance(CoreConfig) | 核心包配置，从 staging/package.json 读取 |
| `kill_event` | Instance(Event) | 用于中止构建的事件 |
| `labextensions_path` | List(Unicode) | prebuilt 扩展的搜索路径列表 |
| `registry` | Unicode | npm registry URL，默认从 yarn config 读取 |
| `splice_source` | Bool | 是否将 source 包拼接到应用目录（默认 False） |
| `skip_full_build_check` | Bool | 跳过完整构建检查，仅做快速检查 |
| `verbose` | Bool | 详细输出模式 |

`_ensure_options()` 辅助函数（commands.py:427-434）将 `AppOptions | dict | None` 统一转换为 `AppOptions` 实例，提供灵活的 API 调用方式。

## _AppHandler：构建实际实现

`_AppHandler` 是构建和扩展管理的内部实现类（commands.py:685，F-130），所有模块级公共函数（`build`、`install_extension`、`enable_extension` 等）都委托给它。

构造函数（commands.py:686-715）的关键操作：

1. 调用 `_ensure_options(options)` 规范化配置。
2. **深拷贝 core_data**：`self.core_data = deepcopy(options.core_config._data)`（commands.py:694），避免构建过程中的临时修改污染原始配置。
3. 设置 `app_dir`、`sys_dir`、`labextensions_path`、`registry` 等属性。
4. 调用 `self._get_app_info()` 收集应用信息（已安装扩展、禁用列表、linked 包等）。
5. 执行 4.0 版本迁移：将旧的 `disabledExtensions` 镜像到 `lockedExtensions`，处理 sys_prefix 只读时回退到 user 级别的权限问题。

`_AppHandler` 提供的核心方法包括 `build()`、`watch()`、`install_extension()`、`uninstall_extension()`、`toggle_extension()`、`toggle_extension_lock()`、`list_extensions()`、`build_check()` 等。

## Hatch 构建钩子

JupyterLab 使用 Hatch 作为 Python 构建后端（pyproject.toml:5，F-009），通过自定义构建钩子 `buildapi.py` 将前端构建集成到 Python wheel 的构建流程中。

`builder` 函数（buildapi.py:18-47，F-042）执行以下操作：

1. 调用 `npm_builder(target_name, version, *args, **kwargs)`（来自 `hatch_jupyter_builder`）执行实际的前端构建。
2. **editable 模式**（`version == "editable"`）：从 `packages/` 目录构建到 `dev_mode/static/`，用于 `pip install -e .` 开发安装。构建后直接返回，不执行后续清理。
3. **生产构建**（wheel/sdist）：从 `staging/` 目录构建到 `jupyterlab/static/`。
4. 删除 `jupyterlab/static/*.js.map` source map 文件，减小分发包体积。
5. 验证 NPM 包版本与 Python 包版本一致：读取 `jupyterlab/static/package.json` 中的 `jupyterlab.version`，与 `hatchling version` 输出比较，不一致则抛出错误。

pyproject.toml 中的 wheel 共享数据映射（F-141）将构建产物安装到 Jupyter 的标准共享目录：

| 源目录 | 目标目录 |
|--------|----------|
| `static/` | `share/jupyter/lab/static` |
| `schemas/` | `share/jupyter/lab/schemas` |
| `themes/` | `share/jupyter/lab/themes` |
| `jupyter-config/` | `etc/jupyter` |

这使得 pip 安装后，Jupyter Server 能在标准路径发现静态资源、JSON Schema、主题文件和自动启用配置。

## 清理与维护

`clean()` 函数（commands.py:507-538，F-135）清理 app 目录下的 `extensions`/`settings`/`staging`/`static` 子目录或整个 app_dir，但**禁止清理 dev 和 core 目录**（commands.py:514-519），防止意外删除源码或包内置资源。`jupyter lab clean` 命令支持 `--extensions`、`--settings`、`--static`、`--all` 选择性清理（labapp.py:245-284，F-097）。

## 相关概念

- [07 扩展生态系统](07-extension-ecosystem.md)
- [01 整体架构概览](01-architecture-overview.md)
- [02 应用框架与 Shell 布局](02-application-shell.md)
- [00 概述与知识地图](00-introduction.md)
