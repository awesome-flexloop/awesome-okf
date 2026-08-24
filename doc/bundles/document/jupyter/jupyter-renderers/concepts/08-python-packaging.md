---
type: Concept
title: 预构建扩展与 Python 打包
description: jupyter-renderers 使用 hatch-jupyter-builder 将 TypeScript 编译产物打包为 Python wheel，通过 _jupyter_labextension_paths 入口点注册，支持 pip install 一键安装
tags: [python-packaging, prebuilt-extension, hatch, wheel, labextension, entry-points]
sources:
  - id: fasta-pyproject
    resource: external/libs/jupyter/jupyter-renderers/packages/fasta-extension/pyproject.toml
    title: fasta-extension/pyproject.toml
  - id: fasta-init
    resource: external/libs/jupyter/jupyter-renderers/packages/fasta-extension/jupyterlab_fasta/__init__.py
    title: jupyterlab_fasta/__init__.py
  - id: geojson-pyproject
    resource: external/libs/jupyter/jupyter-renderers/packages/geojson-extension/pyproject.toml
    title: geojson-extension/pyproject.toml
  - id: katex-pyproject
    resource: external/libs/jupyter/jupyter-renderers/packages/katex-extension/pyproject.toml
    title: katex-extension/pyproject.toml
  - id: vega3-pyproject
    resource: external/libs/jupyter/jupyter-renderers/packages/vega3-extension/pyproject.toml
    title: vega3-extension/pyproject.toml
  - id: mathjax2-pyproject
    resource: external/libs/jupyter/jupyter-renderers/packages/mathjax2-extension/pyproject.toml
    title: mathjax2-extension/pyproject.toml
  - id: root-pkg
    resource: external/libs/jupyter/jupyter-renderers/package.json
    title: jupyter-renderers/package.json
status: stable
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-22
---

# 预构建扩展与 Python 打包

jupyter-renderers 采用 JupyterLab 3+ 的**预构建扩展（Prebuilt Extension）**模式，将 TypeScript 编译产物打包为 Python wheel，用户通过 `pip install` 即可安装，无需 Node.js 环境和 `jupyter labextension install` 命令。

## 预构建扩展 vs 源码扩展

| 特性 | 预构建扩展（jupyter-renderers） | 源码扩展（旧模式） |
|------|-------------------------------|-------------------|
| 安装方式 | `pip install xxx` | `jupyter labextension install xxx` |
| 需要 Node.js | ❌ 不需要 | ✅ 必需 |
| 需要编译 | ❌ 已预编译 | ✅ 安装时编译 |
| 安装速度 | 快（wheel 下载） | 慢（需 npm install + webpack） |
| Python 包 | ✅ 有 | ❌ 无（纯 npm 包） |
| 静态资源位置 | Python 包内 `labextension/` 目录 | `$PREFIX/share/jupyter/lab/extensions/` |
| 冲突检测 | 安装时检测 | 编译时检测 |
| JupyterLab 版本要求 | 3.0+ | 1.x-2.x |

## 构建流水线

从 TypeScript 源码到 Python wheel 的完整流程：

```
1. TypeScript 编译
   packages/*/src/**/*.ts → packages/*/lib/**/*.js（CommonJS）
   工具：tsc -b（tsconfig.build.json references）
   输出：lib/*.js + lib/**/*.d.ts

2. CSS 提取
   packages/*/style/**/*.css → packages/*/style/*.css（已存在）
   工具：直接复制（import 在 JS 中）

3. Webpack 打包（由 hatch-jupyter-builder 驱动）
   lib/**/*.js + style/*.css + npm 依赖 → static/labextension/*.bundle.js
   工具：webpack（jupyter labextension build 命令）
   配置：每个包内的 webpack.config.js（@jupyterlab/builder 提供默认配置）
   输出：static/labextension/ 目录（包含打包后的 JS、CSS、package.json）

4. Python wheel 打包
   源文件 + static/labextension/** → *.whl
   工具：hatchling（PEP 517 build backend）
   插件：hatch-jupyter-builder（在 wheel 构建前执行 JS 构建）
   输出：dist/jupyterlab_fasta-X.Y.Z-py3-none-any.whl
```

## pyproject.toml 配置

以 fasta-extension 为例，所有包的 pyproject.toml 结构一致：[^fasta-pyproject]

```toml
[build-system]
requires = ["hatchling>=1.5.0", "hatch-jupyter-builder>=0.5"]
build-backend = "hatchling.build"

[project]
name = "jupyterlab-fasta"
description = "Fasta renderer for JupyterLab"
readme = "README.md"
license = {text = "BSD-3-Clause"}
requires-python = ">=3.7"
dependencies = []  # 空！运行时无 Python 依赖
version = "3.3.0"

[project.optional-dependencies]
test = ["pytest", "pytest-cov", "pytest-jupyter[lab]>=0.4"]

[tool.hatch.build.targets.wheel.shared-options]
# 只打包 labextension 目录和 Python 源文件
exclude = ["**/.gitkeep"]
artifacts = ["jupyterlab_fasta/labextension"]

[tool.hatch.build.hooks.version]
# 版本号来自 hatch-nodejs-version 插件
path = "package.json"

[tool.hatch.build.hooks.jupyter-builder]
# hatch-jupyter-builder 钩子，在构建 wheel 前执行 JS 构建
dependencies = ["hatch-jupyter-builder>=0.5"]
build-function = "hatch_jupyter_builder.npm_builder"
ensured-targets = ["jupyterlab_fasta/labextension"]
skip-if-exists = ["jupyterlab_fasta/labextension/static/style.js"]

[tool.hatch.build.hooks.jupyter-builder.build-kwargs]
build_cmd = "build:prod"          # 执行 npm run build:prod
npm = ["jlpm"]                   # 使用 jlpm（JupyterLab 的 yarn 包装）

[tool.hatch.build.hooks.jupyter-builder.editable-build-kwargs]
# 可编辑安装时执行 build（而非 build:prod）
build_cmd = "build"
npm = ["jlpm"]
source_dir = "src"
build_dir = "jupyterlab_fasta/labextension"
```

### 关键字段解析

| 字段 | 说明 |
|------|------|
| `[build-system].requires` | 构建依赖：hatchling（构建后端）+ hatch-jupyter-builder（JS 构建钩子） |
| `dependencies = []` | **运行时零 Python 依赖**——所有逻辑在编译后的 JS 中 |
| `artifacts` | 声明 labextension 目录为构建产物，需要打包进 wheel |
| `hatch-jupyter-builder` | 构建钩子，在 Python 打包前自动执行 JS 构建命令 |
| `ensured-targets` | 构建完成后必须存在的目录（验证构建成功） |
| `skip-if-exists` | 如果该文件已存在，跳过 JS 构建（加速 pip install） |
| `build_cmd = "build:prod"` | 生产构建命令（`npm run build:prod` → `jupyter labextension build .`） |
| `hatch-nodejs-version` | 从 package.json 读取版本号，保持 JS/Python 版本一致 |

## Python 入口点

每个 Python 包的代码极简，只包含 `__init__.py` 和版本号：

```python
# jupyterlab_fasta/__init__.py
import json
import pathlib

from ._version import __version__

HERE = pathlib.Path(__file__).parent.resolve()

with (HERE / "labextension" / "package.json").open() as fid:
    data = json.load(fid)

def _jupyter_labextension_paths():
    return [{
        "src": "labextension",
        "dest": data["name"]     # "@jupyterlab/fasta-extension"
    }]
```

### _jupyter_labextension_paths 约定

JupyterLab 通过这个特殊函数发现预构建扩展：

1. **函数名约定**：`_jupyter_labextension_paths()`，JupyterLab 自动识别此函数名
2. **返回值**：列表，每个元素是一个字典，包含：
   - `src`：Python 包内静态资源目录的相对路径（相对于 `__init__.py`）
   - `dest`：JupyterLab 扩展安装目标名，通常来自 package.json 的 `name` 字段
3. **资源位置**：静态资源在 Python 包内的 `labextension/` 子目录（即打包产物）
4. **package.json 读取**：从 labextension 目录中读取编译后的 package.json，获取扩展名和版本

JupyterLab 启动时扫描已安装的 Python 包，调用 `_jupyter_labextension_paths()`，将 `src` 指向的目录注册为 labextension。

### 版本文件

`_version.py` 由 hatch 构建时自动生成：

```python
# _version.py（自动生成）
__version__ = "3.3.0"
```

## 包名映射

| npm 包名 | Python 包名 | Python 模块名 | _jupyter_labextension_paths dest |
|---------|------------|-------------|----------------------------------|
| @jupyterlab/fasta-extension | jupyterlab-fasta | jupyterlab_fasta | @jupyterlab/fasta-extension |
| @jupyterlab/geojson-extension | jupyterlab-geojson | jupyterlab_geojson | @jupyterlab/geojson-extension |
| @jupyterlab/katex-extension | jupyterlab-katex | jupyterlab_katex | @jupyterlab/katex-extension |
| @jupyterlab/mathjax2-extension | jupyterlab-mathjax2 | jupyterlab_mathjax2 | @jupyterlab/mathjax2-extension |
| @jupyterlab/vega3-extension | jupyterlab-vega3 | jupyterlab_vega3 | @jupyterlab/vega3-extension |

命名规律：
- npm scope `@jupyterlab/xxx-extension` → Python 包名 `jupyterlab-xxx` → Python 模块名 `jupyterlab_xxx`
- 包名使用连字符（pip 惯例），模块名使用下划线（Python 惯例）

## 根级别构建脚本

根 package.json 定义了整个 monorepo 的构建和发布脚本：[^root-pkg]

```json
"scripts": {
  "build": "node buildutils/lib/lib/ensure-repo.js && lerna run build",
  "build:prod": "node buildutils/lib/lib/ensure-repo.js && lerna run build:prod",
  "clean": "lerna run clean",
  "watch": "lerna run watch --stream --parallel",
  "publish": "npm run clean && npm run build && lerna publish -m \"Publish\"",
  "py": "lerna run py --stream"
}
```

| 脚本 | 命令 | 说明 |
|------|------|------|
| `build` | tsc 编译（CommonJS） | 开发构建，不打 webpack |
| `build:prod` | `jupyter labextension build .`（webpack 打包） | 生产构建，输出 labextension |
| `clean` | 删除 lib/ 和 static/ 目录 | 清理构建产物 |
| `watch` | 并行 watch 所有包 | 开发模式实时编译 |
| `publish` | clean + build + lerna publish | 发布 npm 包和 Python wheel |
| `py` | `hatch build` | 构建 Python wheel |

每个子包也有独立的 pyproject.toml，可单独构建 Python 包。

## hatch-jupyter-builder 工作原理

hatch-jupyter-builder 是一个 hatch 构建钩子插件，工作流程：

1. **wheel 构建触发**：当执行 `pip install` 或 `hatch build` 时，hatch 触发构建钩子
2. **检查 skip-if-exists**：如果指定文件已存在（如预构建的 labextension），跳过 JS 构建
3. **执行 npm 构建**：运行 `jlpm install && jlpm run build:prod`（或配置的命令）
4. **验证 ensured-targets**：确认构建产物存在
5. **复制到 Python 包**：构建产物（static/labextension/）被复制到 Python 模块目录
6. **hatchling 打包**：hatchling 将 Python 源文件 + labextension 目录打包为 wheel

### 开发模式（editable install）

使用 `pip install -e .` 可编辑安装时，使用不同的构建参数：

```toml
editable-build-kwargs = { build_cmd = "build", source_dir = "src", build_dir = "jupyterlab_fasta/labextension" }
```

- 使用 `build`（开发构建，更快）而非 `build:prod`
- 指定 source_dir 和 build_dir，支持热更新

## MANIFEST.in

除了 pyproject.toml，每个包还包含 MANIFEST.in 声明 sdist（源码分发包）应包含的文件：

```
include README.md
include LICENSE
include jupyterlab_fasta/labextension/package.json
graft jupyterlab_fasta/labextension
global-exclude *.tsbuildinfo
```

- `include`：显式包含顶层文件
- `graft`：递归包含整个 labextension 目录
- `global-exclude`：排除 TypeScript 构建信息文件

## 安装流程（用户视角）

```bash
# 用户执行
pip install jupyterlab-fasta

# 1. pip 下载 wheel 文件（.whl）
# 2. wheel 中已包含预编译的 JS/CSS，无需 Node.js
# 3. pip 安装到 site-packages/jupyterlab_fasta/
# 4. JupyterLab 启动时调用 _jupyter_labextension_paths()
# 5. 发现 labextension 目录，注册静态资源路径
# 6. 浏览器加载 jupyterlab_fasta/labextension/static/*.bundle.js
# 7. 扩展激活，注册 MIME 渲染器/应用插件
```

## 自定义预构建扩展的关键要点

1. **pyproject.toml**：使用 hatchling + hatch-jupyter-builder
2. **__init__.py**：实现 `_jupyter_labextension_paths()` 函数
3. **dependencies 为空**：除非需要 Python 服务端逻辑
4. **build:prod**：必须执行 `jupyter labextension build .`（webpack 打包）
5. **labextension 目录**：webpack 输出目录，必须包含 package.json 和 static/
6. **版本同步**：使用 hatch-nodejs-version 从 package.json 读取版本号
7. **_version.py**：由构建系统自动生成，不要手动维护

## 相关概念

- [Monorepo 架构与 Lerna 管理](/concepts/01-monorepo-architecture.md)
- [扩展类型：MIME 渲染器 vs 应用扩展](/concepts/03-extension-types.md)
- [Python 入口点参考](/references/python-entrypoint-reference.md)
- [扩展配置参考](/references/extension-config-reference.md)

[^fasta-pyproject]: fasta-extension/pyproject.toml
[^root-pkg]: root package.json
