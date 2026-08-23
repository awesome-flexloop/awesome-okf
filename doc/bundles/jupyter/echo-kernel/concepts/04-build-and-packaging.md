---
type: Concept
title: 构建与打包系统
description: Echo Kernel的双语言构建系统，TypeScript编译、JupyterLab扩展打包、hatchling Python打包、hatch-jupyter-builder桥接
tags: [build, packaging, typescript, hatchling, jupyter-builder, pip, npm, labextension]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T16:18:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: python-src
    resource: /references/python-source.md
    title: Python包与构建配置信源
  - id: plugin-src
    resource: /references/plugin-source.md
    title: 插件注册源码信源
---

## 双语言构建架构

Echo Kernel是一个**双语言包**——前端用TypeScript编写，后端用Python打包分发。构建系统需要串联两个生态系统：

```
TypeScript源码 (src/*.ts)
  ↓ tsc编译
JavaScript文件 (lib/*.js)
  ↓ jupyter labextension build
Labextension静态资源 (labextension/)
  ↓ hatch-jupyter-builder（pip install时自动触发）
Python Wheel包（包含labextension静态文件）
  ↓ pip install
JupyterLab扩展目录 (share/jupyter/labextensions/@jupyterlite/echo-kernel/)
```

## TypeScript 编译

### 编译配置（tsconfig.json）

| 配置项 | 值 | 说明 |
|--------|-----|------|
| `target` | `ES2018` | 编译目标ES版本 |
| `module` | `esnext` | 模块格式（ES模块） |
| `moduleResolution` | `node` | 模块解析策略 |
| `outDir` | `lib` | 输出目录 |
| `rootDir` | `src` | 源码根目录 |
| `strict` | `true` | 严格类型检查 |
| `declaration` | `true` | 生成.d.ts类型声明文件 |
| `sourceMap` | `true`（开发模式） | 生成source map |
| `jsx` | `react` | JSX支持（JupyterLab使用React） |

### 编译命令

```bash
# 开发模式（含sourceMap）
jlpm build:lib    # tsc --sourceMap

# 生产模式（无sourceMap，更小体积）
jlpm build:lib:prod  # tsc
```

编译将 `src/index.ts` 和 `src/kernel.ts` 编译为 `lib/index.js` 和 `lib/kernel.js`。

## JupyterLab 扩展打包

TypeScript编译后的JS文件不能直接使用，需要通过JupyterLab builder打包为labextension格式：

```bash
jupyter labextension build .
```

这个命令：
1. 使用webpack（或其他打包器）将所有JS模块打包为bundle
2. 处理CSS样式文件
3. 生成 `labextension/` 目录，包含：
   - `static/` 目录：打包后的JS/CSS/字体等静态资源
   - `package.json`：扩展元数据
   - `build_log.json`：构建日志

### 开发模式 vs 生产模式

| 模式 | 命令 | 特点 |
|------|------|------|
| 开发 | `jupyter labextension build --development True .` | 含sourceMap，未压缩，构建快 |
| 生产 | `jupyter labextension build .` | 压缩优化，无sourceMap，体积小 |

## npm 脚本体系

package.json中定义了完整的构建脚本：

| 脚本 | 命令 | 用途 |
|------|------|------|
| `build` | `jlpm build:lib && jlpm build:labextension:dev` | 完整开发构建 |
| `build:prod` | `jlpm clean && jlpm build:lib:prod && jlpm build:labextension` | 完整生产构建 |
| `build:lib` | `tsc --sourceMap` | 仅编译TS（开发） |
| `build:lib:prod` | `tsc` | 仅编译TS（生产） |
| `build:labextension` | `jupyter labextension build .` | 打包labextension（生产） |
| `build:labextension:dev` | `jupyter labextension build --development True .` | 打包labextension（开发） |
| `install:extension` | `jlpm build` | 开发安装构建 |
| `clean` | `jlpm clean:lib` | 清理构建产物 |
| `clean:all` | `jlpm clean:lib && jlpm clean:labextension` | 全量清理 |
| `watch` | `run-p watch:src watch:labextension` | 监听模式（自动重建） |

### Watch模式（开发时使用）

```bash
jlpm run watch
```

启动两个并行监听进程：
- `tsc -w --sourceMap`：监听TS文件变化，自动重新编译
- `jupyter labextension watch .`：监听编译输出变化，自动重新打包labextension

开发时运行 `jupyter lab`，修改源码后刷新浏览器即可看到变化。

## Python 包构建

Python端使用hatchling作为构建后端，通过hatch-jupyter-builder桥接前端构建。

### pyproject.toml 关键配置

#### 构建系统

```toml
[build-system]
requires = ["hatchling>=1.5.0", "jupyterlab>=4.0.0,<5", "hatch-nodejs-version>=0.3.2"]
build-backend = "hatchling.build"
```

#### 版本同步

```toml
[tool.hatch.version]
source = "nodejs"
```

版本号从package.json的 `version` 字段自动获取，确保Python包和npm包版本一致。

#### Jupyter Builder Hook

这是最关键的配置——在pip install时自动构建前端：

```toml
[tool.hatch.build.hooks.jupyter-builder]
dependencies = ["hatch-jupyter-builder>=0.5"]
build-function = "hatch_jupyter_builder.npm_builder"
ensured-targets = [
    "jupyterlite_echo_kernel/labextension/static/style.js",
    "jupyterlite_echo_kernel/labextension/package.json",
]
skip-if-exists = ["jupyterlite_echo_kernel/labextension/static/style.js"]

[tool.hatch.build.hooks.jupyter-builder.build-kwargs]
build_cmd = "build:prod"
npm = ["jlpm"]

[tool.hatch.build.hooks.jupyter-builder.editable-build-kwargs]
build_cmd = "install:extension"
npm = ["jlpm"]
source_dir = "src"
build_dir = "jupyterlite_echo_kernel/labextension"
```

| 配置项 | 说明 |
|--------|------|
| `build-function` | 使用npm_builder策略构建前端 |
| `ensured-targets` | 构建完成后必须存在的文件（验证构建成功） |
| `skip-if-exists` | 如果这些文件已存在则跳过构建（避免重复构建） |
| `build_cmd`（生产） | `build:prod`，执行生产构建 |
| `build_cmd`（开发） | `install:extension`，执行开发构建 |
| `npm` | 使用 `jlpm`（JupyterLab绑定的yarn版本） |

#### Wheel数据安装

```toml
[tool.hatch.build.targets.wheel.shared-data]
"jupyterlite_echo_kernel/labextension" = "share/jupyter/labextensions/@jupyterlite/echo-kernel"
"install.json" = "share/jupyter/labextensions/@jupyterlite/echo-kernel/install.json"
```

构建wheel时，将labextension静态文件安装到JupyterLab的扩展目录。

### Python包结构

```
jupyterlite_echo_kernel/
├── __init__.py          # 包入口（版本导入 + _jupyter_labextension_paths）
├── _version.py          # 自动生成的版本文件
└── labextension/        # 构建产物（不纳入git，pip install时生成）
    ├── static/
    │   ├── style.js
    │   ├── bundle.js
    │   └── ...
    └── package.json
```

## 完整安装流程（pip install）

```bash
pip install jupyterlite-echo-kernel
```

执行过程：

1. **下载sdist/wheel**：pip从PyPI下载包
2. **解压源码**（如果是sdist）：解压tar.gz到临时目录
3. **hatchling接管构建**：
   - hatch-jupyter-builder检测是否需要构建前端
   - 如果 `labextension/static/style.js` 不存在，执行前端构建
4. **前端构建**：
   - 执行 `jlpm install`（安装npm依赖）
   - 执行 `jlpm build:prod`（清理→编译TS→打包labextension）
   - 产物输出到 `jupyterlite_echo_kernel/labextension/`
5. **验证构建**：检查ensured-targets文件是否存在
6. **打包wheel**：将Python代码和labextension静态文件一起打包
7. **安装到site-packages**：
   - Python代码 → `site-packages/jupyterlite_echo_kernel/`
   - labextension → `share/jupyter/labextensions/@jupyterlite/echo-kernel/`
8. **JupyterLab发现扩展**：通过 `_jupyter_labextension_paths()` 注册扩展路径

## JupyterLite 站点构建

安装Python包后，需要重新构建JupyterLite站点：

```bash
jupyter lite build
```

这个命令：
1. 收集所有已安装的JupyterLite扩展（包括echo-kernel）
2. 将扩展的静态资源打包到站点中
3. 生成可部署的静态站点目录 `_output/`

## 开发模式安装

开发时使用editable模式：

```bash
# 安装Python包（开发模式）
python -m pip install -e .

# 链接JupyterLab扩展（创建symlink）
jupyter labextension develop . --overwrite

# 启动watch模式
jlpm run watch

# 另一个终端启动JupyterLab
jupyter lab
```

这使你可以修改TypeScript源码后，浏览器刷新即可看到变化，无需重新pip install。

## 发布流程

包同时发布到PyPI和npm：

```bash
# 1. 版本更新
hatch version <new-version>  # 更新package.json中的版本

# 2. 清理
jlpm clean:all

# 3. 构建Python包
python -m build

# 4. 上传到PyPI
twine upload dist/*

# 5. 发布npm包
npm login
npm publish --access public
```

## 相关概念

- [Echo Kernel简介](/concepts/00-introduction.md)
- [JupyterLite内核架构](/concepts/01-kernel-architecture.md)
- [插件注册机制](/concepts/02-plugin-registration.md)
- [EchoKernel实现详解](/concepts/03-echokernel-implementation.md)
- [自定义内核开发](/examples/02-custom-kernel-tutorial.md)
