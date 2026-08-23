---
type: Concept
title: 构建系统
description: doit 任务运行器、lerna monorepo 管理、flit Python 打包、构建时 WebSocket patch 与完整构建流程
tags: [build, doit, lerna, flit, webpack, monorepo]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-verification", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: 2027-02-22
sources:
  - id: build
    resource: /references/build-source.md
    title: 构建系统源码引用
  - id: hacks
    resource: /references/hacks-source.md
    title: Monkey-patch 源码引用
  - id: python
    resource: /references/python-source.md
    title: Python包源码引用
---

## 构建工具概览

jupyterlite-lsp 采用多工具协作的构建系统，不同语言和任务使用最适合的工具：

| 工具 | 用途 | 配置文件 |
|------|------|---------|
| **doit** | 任务编排（Python 任务运行器） | dodo.py |
| **lerna 6.0.3** | JS monorepo 管理 | lerna.json |
| **yarn workspaces** | JS 包依赖管理 | package.json workspaces |
| **flit_core** | Python 包构建 | pyproject.toml |
| **jupyter labextension build** | JS 扩展 webpack 构建 | 各包 package.json jupyterlab 字段 |
| **TypeScript tsc** | TS→JS 编译 | tsconfig.json |
| **prettier** | JS/Python 代码格式化 | package.json prettier 字段 |
| **sphinx** | 文档构建 | docs/conf.py |

## doit 任务系统

doit 是 Python 的任务自动化工具，类似 make 但使用 Python 脚本定义任务。dodo.py 中的任务分为几类：

### JS 任务（自动从 package.json 加载）

`U.load_package_json_tasks()` 解析 package.json#/doit/tasks 中的任务定义，自动生成 doit 任务。任务名格式为 `task_<prefix>`，如 `task_build`、`task_setup` 等。

package.json 中定义的 JS 任务：

| 任务前缀 | 子任务 | 说明 |
|---------|--------|------|
| build | ext, lib | lib: TypeScript 编译；ext: labextension webpack 构建 |
| setup | js, py:ext, py:pip | js: yarn install；py:ext: labextension develop；py:pip: pip install -e |
| dist | npm, py | npm: lerna run dist:npm；py: flit build |
| docs | sphinx | sphinx-build 构建文档 |
| fix | js:package, js:prettier, py:black, py:isort, py:ssort | 代码格式化 |
| lite | build | jupyter lite build 示例站点 |

执行单个任务：

```bash
doit build:lib      # 仅构建 TS 库
doit setup:js       # 仅安装 JS 依赖
```

### Python 自定义任务

dodo.py 中直接定义的任务：

#### task_copy

将 LICENSE.txt 复制到每个 package 目录，将 README.md 复制到 packages/lsp/ 目录。npm 包发布需要这些文件在包目录中。

#### task_binder

开发环境就绪任务。执行 setup 后输出提示信息，告知开发者如何启动 JupyterLab 和 watch 模式。

```bash
doit binder
# 输出：ready to start work with: jupyter lab --no-browser --debug
#       to rebuild: jlpm watch
```

#### task_hack:connection.js

构建流程中最关键的 Python 任务——在 jupyter lite build 完成后，对 jupyterlab-lsp 的 connection.js 进行 WebSocket 字符串替换：

```python
class C:
    NATIVE_WEBSOCKET = "new WebSocket"
    HACKED_WEBSOCKET = "new window.MockWebSocket"

B.CONNECTION_JS = B.JLLSP / "321.0176abf53bb1a24b854d.js"

def task_hack():
    yield dict(
        name="connection.js",
        file_dep=file_dep,  # 依赖 lite:build 产物
        targets=[B.CONNECTION_JS],
        actions=[(U.patch_one, [C.NATIVE_WEBSOCKET, C.HACKED_WEBSOCKET, B.CONNECTION_JS])],
    )
```

patch_one 使用简单的 str.replace()：

```python
def patch_one(pattern: str, replacement: str, path: Path):
    text = path.read_text(encoding="utf-8")
    text = text.replace(pattern, replacement)
    path.write_text(text, encoding="utf-8")
```

#### task_dist:hash

计算 dist/ 目录下所有发布产物的 SHA256 哈希，生成 SHA256SUMS 文件。

### doit 工具类

dodo.py 中定义了几个工具类组织常量和路径：

| 类 | 作用 | 示例 |
|----|------|------|
| C（Constants） | 字符串常量 | NATIVE_WEBSOCKET, HACKED_WEBSOCKET, UTF8 |
| P（Paths） | 项目路径 | ROOT, PACKAGES, EXAMPLES, DOCS |
| D（Data） | 从配置文件加载的数据 | PY_VERSION, JS_VERSION, JS_TASKS |
| B（Build） | 构建输出路径 | BUILD, DIST, CONNECTION_JS |
| U（Utilities） | 工具函数 | expand_paths, fetch_one, patch_one, hash_files, copy_one |

## lerna Monorepo 配置

lerna.json：

```json
{
  "lerna": "6.0.3",
  "npmClient": "jlpm",
  "useWorkspaces": true,
  "version": "independent"
}
```

- **npmClient: jlpm**：使用 JupyterLab 包管理器（yarn 的 JupyterLab 定制版）
- **useWorkspaces: true**：使用 yarn workspaces 管理依赖提升
- **version: independent**：每个包独立版本号（当前均为 0.1.0-alpha0）

packages/ 目录下三个包：

| 包 | 私有 | 职责 |
|----|------|------|
| lsp | 否 | 核心 LSP 框架 |
| lsp-yaml | 否 | YAML/JSON 语言服务器 |
| _meta | 是 | 元包，重新导出 @jupyterlite/lsp |

## JupyterLab Extension 构建

每个 JS 包的 package.json 中包含 `jupyterlab` 字段，定义 labextension 构建配置：

```json
{
  "jupyterlab": {
    "extension": "lib/plugin.js",
    "outputDir": "../../src/jupyterlite_lsp/_d/share/jupyter/labextensions/@jupyterlite/lsp",
    "webpackConfig": "./webpack.config.js",
    "sharedPackages": {
      "@krassowski/jupyterlab-lsp": {
        "bundled": false,
        "singleton": true
      }
    }
  },
  "jupyterlite": {
    "liteExtension": true
  }
}
```

- **extension**：插件入口文件（编译后）
- **outputDir**：构建产物输出目录，直接输出到 Python 包的 _d/ 目录中
- **sharedPackages**：与 JupyterLab 共享的包，不打包进自身 bundle，singleton 确保单例
- **liteExtension: true**：标记为 JupyterLite 扩展（非传统 JupyterLab 扩展）

`jupyter labextension build .` 命令内部使用 webpack 5 构建，读取各包的 webpack.config.js 进行自定义配置。

## Python 包构建（flit）

pyproject.toml 使用 flit_core 作为构建后端：

```toml
[build-system]
requires = ["flit_core >=3.7.1,<4"]
build-backend = "flit_core.buildapi"

[tool.flit.module]
name = "jupyterlite_lsp"

[tool.flit.sdist]
include = ["src/jupyterlite_lsp/_d"]

[tool.flit.external-data]
directory = "src/jupyterlite_lsp/_d"
```

关键点：
- JS 构建产物输出到 `src/jupyterlite_lsp/_d/` 目录
- `_d/` 被配置为 external-data，随 wheel 一起分发
- sdist 也包含 `_d/` 目录

## 完整构建流程

从源码到可发布产物的完整流程：

```
1. setup:js
   └─ jlpm install → 安装所有 JS 依赖到 node_modules/

2. setup:py:pip
   └─ pip install -e . → 可编辑模式安装 Python 包

3. setup:py:ext
   └─ jupyter labextension develop . --overwrite → 开发模式链接扩展

4. build:lib
   └─ lerna run build → tsc -b src → 编译 TypeScript 到 lib/

5. build:ext
   └─ lerna run labextension:build → webpack 构建
   └─ 产物输出到 src/jupyterlite_lsp/_d/share/...

6. lite:build
   └─ cd examples && jupyter lite build → 构建 JupyterLite 示例站点
   └─ 输出到 build/lite/

7. hack:connection.js
   └─ 字符串替换 connection.js 中 new WebSocket → new window.MockWebSocket

8. dist:py
   └─ flit build → 生成 .tar.gz sdist 和 .whl wheel

9. dist:npm
   └─ lerna run dist:npm → npm pack → 生成 .tgz 包

10. dist:hash
    └─ 计算所有 dist/ 产物的 SHA256 → SHA256SUMS
```

一键执行完整构建：

```bash
doit        # 运行所有任务
doit dist   # 仅构建发布产物
```

## 并行构建

doit 支持并行执行：

```bash
doit -n8 binder   # 8 并行线程执行 binder 任务链
```

lerna 在 watch 模式下也支持并行：

```bash
jlpm watch        # lerna run --parallel --stream watch
```

## 版本管理

JS 版本和 Python 版本保持同步，由 dodo.py 中的 D 类自动转换：

```python
D.JS_VERSION = PY_VERSION.replace("a", "-alpha").replace("b", "-beta")
```

例如：Python 版本 `0.1.0a0` → JS 版本 `0.1.0-alpha0`。

## 相关概念

- [Python包与Labextension注册](/concepts/08-python-package.md)
- [Mock-Socket 桥接机制](/concepts/05-mock-socket-bridge.md)
- [快速开始](/concepts/01-getting-started.md)
- [构建系统源码引用](/references/build-source.md)
- [本地开发环境搭建](/examples/local-dev-setup.md)
