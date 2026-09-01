---
okf_version: "0.2"
type: concept
title: "构建系统与 Lab 扩展机制"
description: "解析 jupyterlab_pygments 的双语言构建流水线：hatchling + hatch-jupyter-builder 驱动 npm 构建，预编译前端资源打包进 wheel。"
tags: [build-system, hatchling, jupyter-builder, prebuilt-extension, labextension, wheel, npm-builder, dual-build]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T13:00:00Z" }
verified: { by: "process:source-code-to-okf-wiki-v", at: "2026-08-22T13:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: build-config
    resource: "/references/build-config-source.md"
    title: "构建配置源码信源"
  - id: index-ts
    resource: "/references/index-ts-source.md"
    title: "前端扩展源码信源"
  - id: init-py
    resource: "/references/init-py-source.md"
    title: "__init__.py 源码信源"
---

# 构建系统与 Lab 扩展机制

jupyterlab_pygments 是一个典型的 JupyterLab 4 **预构建扩展（prebuilt extension）**，它的构建系统跨越 Python 和 Node.js 两个生态。本文档解析双语言构建流水线和扩展加载机制。

## 构建系统架构

jupyterlab_pygments 采用 Python 构建工具（hatchling）驱动 Node.js 构建的混合模式：

```
┌─────────────────────────────────────────────────────────┐
│                  pip/conda install                       │
│                          │                              │
│                          ▼                              │
│              hatchling (Python 构建后端)                  │
│                          │                              │
│          ┌───────────────┼───────────────┐              │
│          ▼               ▼               ▼              │
│  hatch-nodejs-version  hatch-jupyter-  标准 wheel       │
│  (版本同步)             builder          打包            │
│                          │                              │
│                          ▼                              │
│              npm_builder 函数                             │
│                          │                              │
│          ┌───────────────┼───────────────┐              │
│          ▼               ▼               ▼              │
│    jlpm install    build:css       build:lib           │
│    (安装npm依赖)    (generate_css    (tsc编译            │
│                     .py → base.css)  → lib/index.js)    │
│                          │                              │
│                          ▼                              │
│              jupyter labextension build                 │
│              (webpack 打包 → labextension/)              │
│                          │                              │
│                          ▼                              │
│              wheel 打包（shared-data映射）                │
│                          │                              │
│                          ▼                              │
│    安装到 share/jupyter/labextensions/jupyterlab_pygments/│
└─────────────────────────────────────────────────────────┘
```

## Python 构建配置详解

### hatchling 构建后端

pyproject.toml 使用 hatchling 作为构建后端：

```toml
[build-system]
requires = ["hatchling>=1.5.0", "jupyterlab>=4.0.0,<5", "hatch-nodejs-version>=0.3.2"]
build-backend = "hatchling.build"
```

选择 hatchling（而非 setuptools）的原因：
- 原生支持 `[tool.hatch.build.hooks]` 构建钩子机制
- hatch-nodejs-version 插件可以直接从 package.json 读取版本号
- hatch-jupyter-builder 插件提供 npm 构建集成
- 现代 Python 打包标准（PEP 517/518）

### 版本同步机制

```toml
[tool.hatch.version]
source = "nodejs"

[tool.hatch.metadata.hooks.nodejs]
fields = ["description", "authors", "urls"]
```

版本号唯一来源是 `package.json` 中的 `"version": "0.3.0"`。hatch-nodejs-version 在构建时：
1. 读取 package.json 的 version 字段
2. 自动生成 `_version.py` 文件（包含 `__version__`）
3. 同步 description、authors、urls 等元数据

这确保 Python 包和 npm 包版本始终一致，避免了手动维护两个版本号的问题。

### hatch-jupyter-builder 钩子

这是构建系统的核心——在 Python 构建过程中自动触发 Node.js 构建：

```toml
[tool.hatch.build.hooks.jupyter-builder]
dependencies = ["hatch-jupyter-builder>=0.5"]
build-function = "hatch_jupyter_builder.npm_builder"
ensured-targets = [
    "jupyterlab_pygments/labextension/static/style.js",
    "jupyterlab_pygments/labextension/package.json",
]
skip-if-exists = ["jupyterlab_pygments/labextension/static/style.js"]
```

| 配置项 | 作用 |
|--------|------|
| `build-function` | 使用 `npm_builder` 函数，它负责调用 npm/yarn 执行构建命令 |
| `ensured-targets` | 构建后必须存在的文件，如果缺失则构建失败 |
| `skip-if-exists` | 如果目标文件已存在则跳过构建（支持增量构建和可编辑安装） |

### 构建命令参数

```toml
[tool.hatch.build.hooks.jupyter-builder.build-kwargs]
build_cmd = "build:prod"
npm = ["jlpm"]

[tool.hatch.build.hooks.jupyter-builder.editable-build-kwargs]
build_cmd = "install:extension"
npm = ["jlpm"]
source_dir = "src"
build_dir = "jupyterlab_pygments/labextension"
```

| 模式 | 构建命令 | 用途 |
|------|---------|------|
| 生产构建（pip install） | `jlpm build:prod` | 完整构建：clean → build:css → build:lib → build:labextension |
| 可编辑安装（pip install -e） | `jlpm install:extension` | 开发构建：build:css → build:lib → build:labextension:dev |

`jlpm` 是 JupyterLab 提供的 yarn 封装，确保使用正确版本的包管理器。

### Wheel 数据映射

```toml
[tool.hatch.build.targets.wheel.shared-data]
"jupyterlab_pygments/labextension" = "share/jupyter/labextensions/jupyterlab_pygments"
"install.json" = "share/jupyter/labextensions/jupyterlab_pygments/install.json"
```

这是 wheel 包中最关键的配置——将构建产物映射到 JupyterLab 的扩展发现路径：

- `labextension/` 目录 → `share/jupyter/labextensions/jupyterlab_pygments/`
- `install.json` → 同样的目标目录

当用户 `pip install` 后，这些文件会被安装到 Python 环境的 `share/jupyter/labextensions/` 目录下，JupyterLab 启动时自动扫描该目录发现预构建扩展。

## Node.js 构建流水线

package.json 中的 scripts 定义了完整的前端构建流程：

### build:css — CSS 生成

```bash
python generate_css.py
```

调用 Python 脚本，将 JupyterStyle 类转换为 style/base.css。这是构建的第一步，因为后续的 webpack 打包需要 CSS 文件存在。

### build:lib — TypeScript 编译

```bash
tsc
```

使用 TypeScript 编译器将 `src/index.ts` 编译为 `lib/index.js` 和 `lib/index.d.ts`。tsconfig.json 配置：
- target: ES2018
- module: ESNext（支持 tree-shaking）
- strict: true（严格类型检查）

### build:labextension — Webpack 打包

```bash
jupyter labextension build .
# 开发模式：
jupyter labextension build --development True .
```

这是 JupyterLab 提供的构建命令，内部使用 webpack：
1. 读取 package.json 中的 `jupyterlab` 配置
2. 从 `style/index.js`（styleModule 入口）开始打包
3. 处理 CSS import（提取 CSS 到单独文件）
4. 输出到 `jupyterlab_pygments/labextension/` 目录

### build:prod — 完整生产构建

```bash
jlpm clean && jlpm build:css && jlpm build:lib && jlpm build:labextension
```

生产构建先清理旧产物（clean:lib 删除 lib/、tsconfig.tsbuildinfo、base.css），然后按顺序执行 CSS 生成→TS 编译→labextension 打包。

## 预构建扩展（Prebuilt Extension）机制

jupyterlab_pygments 是 JupyterLab 4 的预构建扩展，这与 JupyterLab 3 的源码扩展有本质区别：

### 预构建 vs 源码扩展

| 特性 | 预构建扩展（jupyterlab_pygments） | 源码扩展（JupyterLab 3 模式） |
|------|--------------------------------|---------------------------|
| 安装方式 | pip/conda install，无需 Node.js | pip install + jupyter lab build |
| 前端资源 | 预编译在 wheel 包中 | 用户端编译 |
| 安装时间 | 快（直接复制文件） | 慢（需要 webpack 打包） |
| Node.js 依赖 | 仅构建时需要（开发者） | 用户环境也需要 |
| 热重载 | 不支持（开发模式除外） | 支持 |
| JupyterLab 版本 | ≥ 4.0 | 3.x |

### 扩展发现流程

JupyterLab 启动时如何发现 jupyterlab_pygments？

```
JupyterLab 启动
    │
    ▼
1. 扫描 {sys.prefix}/share/jupyter/labextensions/ 目录
    │
    ▼
2. 找到 jupyterlab_pygments/ 子目录
    │
    ▼
3. 读取 package.json（确认这是有效的 JupyterLab 扩展）
    │  "jupyterlab": { "extension": true }
    │
    ▼
4. 加载 static/style.js（webpack 打包产物）
    │
    ▼
5. 执行插件的 activate 函数（空函数，但触发 CSS 注入）
    │
    ▼
6. 应用 .highlight CSS 规则到页面
```

### _jupyter_labextension_paths() 的作用

`__init__.py` 中的 `_jupyter_labextension_paths()` 函数是另一个扩展发现路径的一部分：

```python
def _jupyter_labextension_paths():
    return [{"src": "labextension", "dest": "jupyterlab_pygments"}]
```

这个函数被 JupyterLab 的 Python 端用于：
- 在经典 Notebook 或非预构建模式下发现扩展路径
- 返回包内的 labextension 目录相对于包的位置
- 在开发模式（`jupyter labextension develop`）下创建符号链接

对于预构建扩展，主要发现路径是 `share/jupyter/labextensions/`，但此函数提供了向后兼容。

## install.json 的作用

```json
{
  "packageManager": "python",
  "packageName": "jupyterlab_pygments",
  "uninstallInstructions": "Use your Python package manager (pip, conda, etc.) to uninstall..."
}
```

install.json 是 JupyterLab 扩展的元数据文件：
- `packageManager: "python"`：告知 JupyterLab 这个扩展通过 Python 包管理器安装
- `packageName`：对应的 Python 包名
- `uninstallInstructions`：卸载提示信息

JupyterLab 的扩展管理器界面使用此信息显示扩展的安装来源和卸载方式。

## setup.py 的兼容作用

```python
__import__("setuptools").setup()
```

这一行 shim 的存在是为了兼容不支持 PEP 517 的旧版 pip（< 19.0）。当旧版 pip 遇到没有 setup.py 的项目时，它会回退到运行 `python setup.py install`。这个 shim 确保即使在这种情况下，setuptools 也能被调用（通过 pyproject.toml 中的配置）。现代 pip（≥ 19.0）会直接使用 pyproject.toml 中的 build-backend，完全忽略 setup.py。

## sideEffects 的重要性

package.json 中声明：

```json
"sideEffects": ["style/*.css", "style/index.js"]
```

这对于 CSS 正常加载至关重要。Webpack 的 tree-shaking（死代码消除）会移除没有被使用的导出。如果不声明 sideEffects，webpack 可能认为 `import './base.css'`（在 style/index.js 中）是"无副作用的导入"而将其移除，导致 CSS 不被包含在最终 bundle 中。

通过声明 `style/*.css` 和 `style/index.js` 有副作用（CSS 注入到页面是一种副作用），webpack 会保留这些导入。

---

**相关概念：**
- [双桥架构解析](02-dual-bridge-architecture.md) — 构建系统在整体架构中的位置
- [CSS 生成流水线](04-css-generation-pipeline.md) — build:css 步骤详解
- [自定义样式示例](../examples/01-customize-style.md) — 修改样式后的重新构建
