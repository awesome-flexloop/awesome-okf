---
type: Concept
title: 构建与打包
description: p5-kernel 的 TypeScript 构建流程、p5-docs 自动生成、Python 包构建、hatch-jupyter-builder 集成、双包（npm + PyPI）发布
tags: [build, typescript, hatch, hatchling, npm, pypi, packaging, lerna, monorepo]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T17:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: meta
    resource: /references/metasource.md
    title: p5-kernel 项目元信源
---

## 构建系统概览

p5-kernel 是一个双语言 monorepo，同时发布 npm 包（TypeScript/JavaScript）和 PyPI 包（Python），使用 Lerna + Yarn workspaces 管理 JS 包，使用 Hatchling 管理 Python 包。

```
p5-kernel/ (monorepo root)
├── packages/p5-kernel/           → npm: @jupyterlite/p5-kernel
├── packages/p5-kernel-extension/ → npm: @jupyterlite/p5-kernel-extension
├── jupyterlite_p5_kernel/        → PyPI: jupyterlite-p5-kernel
└── 构建时自动关联：JS 构建产物 → Python 包 labextension/ 目录
```

## Monorepo 管理

### Lerna 配置

[lerna.json](https://github.com/jupyterlite/p5-kernel/blob/main/lerna.json)：

```json
{
  "npmClient": "jlpm",
  "version": "independent",
  "useWorkspaces": true
}
```

| 配置 | 值 | 说明 |
|------|-----|------|
| npmClient | `jlpm` | 使用 JupyterLab 自带的 yarn（jlpm = JupyterLab Package Manager） |
| version | `independent` | 每个包独立版本号，不统一升级 |
| useWorkspaces | `true` | 使用 yarn workspaces 管理依赖 |

### Yarn Workspaces

根 `package.json` 中配置：

```json
{
  "workspaces": {
    "packages": ["packages/*"]
  },
  "private": true
}
```

根包标记为 `private: true`，不发布到 npm；只作为 workspace 协调器。

### 根脚本命令

| 命令 | 功能 |
|------|------|
| `yarn build` | `lerna run build` — 构建所有子包 |
| `yarn build:prod` | `lerna run build:prod` — 生产构建 |
| `yarn clean` | `lerna run clean` — 清理构建产物 |
| `yarn watch` | `lerna run watch` — TypeScript 监听模式 |
| `yarn lint` | ESLint + Prettier 检查和修复 |
| `yarn test` | `lerna run test` — 运行所有测试 |
| `yarn publish` | 清理→构建→lerna publish |

## TypeScript 包构建

### @jupyterlite/p5-kernel 构建

package.json 脚本：

```json
{
  "scripts": {
    "build": "npm run generate:docs && tsc -b",
    "build:prod": "npm run generate:docs && tsc -b",
    "generate:docs": "node scripts/generate-p5-docs.mjs",
    "clean": "rimraf lib && rimraf tsconfig.tsbuildinfo && rimraf src/p5-docs.ts",
    "watch": "tsc -b --watch"
  }
}
```

构建流程：

1. **generate:docs**：执行 `scripts/generate-p5-docs.mjs`，从 `@types/p5/global.d.ts` 解析 JSDoc，生成 `src/p5-docs.ts`
2. **tsc -b**：TypeScript 增量编译，输出到 `lib/` 目录

构建产物（files 字段声明）：

```
lib/
├── index.js          # 编译后的 JS
├── index.d.ts        # 类型声明
├── index.js.map      # Source map
├── kernel.js/.d.ts/.map
├── executor.js/.d.ts/.map
└── p5-docs.js/.d.ts/.map
style/
├── index.css         # 样式入口
├── base.css          # 基础样式
└── index.js          # 样式 JS 入口（用于 CSS 导入）
```

### @jupyterlite/p5-kernel-extension 构建

package.json 脚本：

```json
{
  "scripts": {
    "build": "jlpm run build:lib && jlpm run build:labextension:dev",
    "build:lib": "tsc",
    "build:labextension": "jupyter labextension build .",
    "build:labextension:dev": "jupyter labextension build --development True .",
    "build:prod": "jlpm run build:lib && jlpm run build:labextension",
    "watch": "run-p watch:src watch:labextension"
  }
}
```

扩展构建分两步：

1. **build:lib**：`tsc` 编译 TypeScript 到 `lib/`
2. **build:labextension**：`jupyter labextension build .` 使用 JupyterLab builder 打包为 labextension 格式，输出到 `../../jupyterlite_p5_kernel/labextension/`

开发模式 (`build:labextension:dev`) 生成 development 版本（含 source map，不压缩）。

### p5-docs 自动生成

`scripts/generate-p5-docs.mjs` 是构建前的预处理步骤：

```
@types/p5/global.d.ts (node_modules)
    │
    ├─ ts.createSourceFile() 解析 AST
    ├─ 提取 FunctionDeclaration → 函数名+JSDoc+参数签名
    ├─ 提取 VariableStatement → 变量名+JSDoc（mouseX, width 等）
    ├─ 重载选择：保留参数最多的版本
    ├─ 字母序排序
    │
    ▼
src/p5-docs.ts (自动生成，不提交到 git)
    └─ export const P5_DOCS: Record<string, string> = { ... };
```

clean 命令会删除 `src/p5-docs.ts`，确保下次构建时重新生成。

## Python 包构建

### 构建后端

使用 [Hatchling](https://hatch.pypa.io/) 作为 PEP 517 构建后端：

```toml
[build-system]
requires = ["hatchling>=1.5.0", "jupyterlab>=4.0.0,<5", "hatch-nodejs-version>=0.3.2"]
build-backend = "hatchling.build"
```

| 构建依赖 | 用途 |
|---------|------|
| hatchling>=1.5.0 | 现代 Python 构建后端 |
| jupyterlab>=4.0.0,<5 | JupyterLab 构建工具（labextension build） |
| hatch-nodejs-version>=0.3.2 | 从 package.json 读取版本号 |

### 版本管理

```toml
[tool.hatch.version]
source = "nodejs"
```

Python 包的版本号直接从根 `package.json` 的 `version` 字段读取，实现 JS 和 Python 版本同步，无需手动维护两处版本号。

元数据（description、authors、urls、keywords）也通过 `hatch-nodejs-version` 钩子从 package.json 自动填充：

```toml
[tool.hatch.metadata.hooks.nodejs]
fields = ["description", "authors", "urls", "keywords"]
```

### Hatch Jupyter Builder

```toml
[tool.hatch.build.hooks.jupyter-builder]
dependencies = ["hatch-jupyter-builder>=0.5"]
build-function = "hatch_jupyter_builder.npm_builder"
ensured-targets = [
    "jupyterlite_p5_kernel/labextension/static/style.js",
    "jupyterlite_p5_kernel/labextension/package.json",
]
skip-if-exists = ["jupyterlite_p5_kernel/labextension/static/style.js"]
```

`hatch-jupyter-builder` 是 Jupyter 生态的标准构建钩子，在 Python 包构建时自动执行 npm 构建：

1. **build-function**：使用 `npm_builder` 函数
2. **build_cmd**：生产构建时执行 `build:prod`（即 `tsc + jupyter labextension build`）
3. **npm**：使用 `jlpm` 作为 npm client
4. **ensured-targets**：构建完成后必须存在的文件（验证构建成功）
5. **skip-if-exists**：如果 `style.js` 已存在（pre-built 场景），跳过 npm 构建

Editable 安装模式：

```toml
[tool.hatch.build.hooks.jupyter-builder.editable-build-kwargs]
build_cmd = "install:extension"
npm = ["jlpm"]
source_dir = "src"
build_dir = "jupyterlite_p5_kernel/labextension"
```

开发安装（`pip install -e .`）时执行 `install:extension`（即 `jupyter labextension develop --overwrite .`），创建符号链接而非复制文件，支持热重载。

### Wheel 数据文件

```toml
[tool.hatch.build.targets.wheel.shared-data]
"jupyterlite_p5_kernel/labextension" = "share/jupyter/labextensions/@jupyterlite/p5-kernel-extension"
"install.json" = "share/jupyter/labextensions/@jupyterlite/p5-kernel-extension/install.json"
```

构建 wheel 时，labextension 静态资源被安装到 JupyterLab 的共享扩展目录：
- `{prefix}/share/jupyter/labextensions/@jupyterlite/p5-kernel-extension/`

这是 JupyterLab 预构建扩展（federated extension）的标准安装路径，JupyterLab 启动时自动扫描该目录发现扩展。

### Python 包入口

[jupyterlite_p5_kernel/__init__.py](https://github.com/jupyterlite/p5-kernel/blob/main/jupyterlite_p5_kernel/__init__.py)：

```python
import json
from pathlib import Path
from ._version import __version__

HERE = Path(__file__).parent.resolve()

with (HERE / "labextension" / "package.json").open() as fid:
    data = json.load(fid)

def _jupyter_labextension_paths():
    return [{"src": "labextension", "dest": data["name"]}]
```

`_jupyter_labextension_paths()` 是 Jupyter 扩展发现机制的标准钩子函数，返回 labextension 目录的路径和目标名称（从 package.json 的 name 字段读取，即 `@jupyterlite/p5-kernel-extension`）。

### install.json

```json
{
  "packageManager": "python",
  "packageName": "jupyterlite_p5_kernel",
  "uninstallInstructions": "Use your Python package manager (pip, conda, etc.) to uninstall the package jupyterlite_p5_kernel"
}
```

提供给 JupyterLab Extension Manager 的元数据，标识扩展由 Python 包管理。

## 开发安装流程

```bash
# 创建环境
mamba create --name jupyterlite-p5-kernel -c conda-forge python=3.9 yarn jupyterlab
mamba activate jupyterlite-p5-kernel

# 安装 Python 包（editable 模式）
python -m pip install -e .

# 链接开发版本到 JupyterLab
jlpm run install:extension

# 监听 TypeScript 变化
jlpm run watch

# 安装 jupyterlite 并构建站点
python -m pip install jupyterlite
jupyter lite build
jupyter lite serve
```

## 构建依赖版本

### npm 依赖

| 包 | 版本约束 | 类型 |
|----|---------|------|
| @jupyterlab/nbformat | ^4.5.0 | dependency |
| @jupyterlite/javascript-kernel | ^0.4.0-alpha.3 | dependency |
| @jupyterlite/services | ^0.7.0 | dependency |
| @jupyterlab/application | ^4.5.0 | dependency (extension) |
| @types/p5 | ^1.7.7 | devDependency |
| typescript | ~5.0.2 | devDependency |

### Python 依赖

- 无运行时依赖（`dependencies = []`）
- 仅构建依赖（hatchling、hatch-jupyter-builder、jupyterlab 等）

## 相关概念

- [扩展注册与 CDN 配置](05-extension-registration.md)
- [P5Executor 与渲染机制](03-executor-and-rendering.md)
- [架构概览](01-architecture-overview.md)
