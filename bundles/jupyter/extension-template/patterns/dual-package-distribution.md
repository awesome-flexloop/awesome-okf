---
type: Pattern
title: 双包分发模式
description: 将前端资源打包进 Python wheel 实现单一命令安装，适用于需要同时提供前端 UI 和后端逻辑的 Python 库。
tags: [dual-package, npm, python, wheel, distribution, jupyter-builder]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T12:36:00Z" }
status: stable
source: extension-template
applicability: Jupyter 扩展、含前端 UI 的 Python 库、混合技术栈项目
---

# 双包分发模式（NPM + Python Wheel）

## 问题

扩展同时包含前端（TypeScript/JavaScript）和后端（Python）代码，终端用户需要简单的安装方式。如果要求用户分别安装 NPM 包和 Python 包，安装流程复杂且容易出错。

## 解决方案

将编译后的前端静态资源打包进 Python wheel，通过 `pip install` 一次性安装前端和后端代码。使用构建钩子（hatchling + jupyter-builder）在构建 wheel 时自动编译前端代码。

## 架构

```
开发时（editable install）：
  pip install -e . → hatchling 钩子 → jupyter-builder install:extension
    → tsc --sourceMap（编译 TS）
    → jupyter-builder build --development（生成 labextension）
    → 创建符号链接到 JupyterLab

发布时（pip install / python -m build）：
  python -m build → hatchling 钩子 → jupyter-builder build:prod
    → tsc（生产编译）
    → jupyter-builder build（打包 labextension）
    → 将 labextension/ 复制到 wheel 的 share/jupyter/labextensions/
    → 生成 wheel（含预编译前端资源，无需 NodeJS）
```

## 核心配置

### 1. 构建钩子（pyproject.toml）

```toml
[build-system]
requires = ["hatchling>=1.5.0", "hatch-nodejs-version>=0.3.2", "jupyter-builder>=1.2.0,<2"]
build-backend = "hatchling.build"

[tool.hatch.build.hooks.jupyter-builder]
dependencies = ["hatch-jupyter-builder>=0.5"]
build-function = "hatch_jupyter_builder.npm_builder"

[tool.hatch.build.hooks.jupyter-builder.build-kwargs]
build_cmd = "build:prod"
npm = ["jlpm"]

[tool.hatch.build.hooks.jupyter-builder.editable-build-kwargs]
build_cmd = "install:extension"
npm = ["jlpm"]
source_dir = "src"
build_dir = "mypackage/labextension"
```

### 2. 前端入口（Python __init__.py）

```python
def _jupyter_labextension_paths():
    """告诉 JupyterLab 在哪里找前端资源"""
    return [{"src": "labextension", "dest": "my-extension"}]
```

### 3. shared-data 映射

wheel 通过 `shared-data` 将前端资源安装到 JupyterLab 扫描路径：

```toml
[[tool.hatch.build.targets.wheel.shared-data]]
source = "mypackage/labextension"
target = "share/jupyter/labextensions/my-extension"
```

### 4. 版本同步

使用 `hatch-nodejs-version` 从 package.json 读取版本号，确保 NPM 和 Python 包版本一致：

```toml
[tool.hatch.version]
source = "nodejs"
```

## 关键原则

1. **单一真值**：版本号只在 package.json 中定义，Python 包通过构建钩子自动同步
2. **生产构建自包含**：wheel 包包含预编译的前端资源，终端用户不需要 NodeJS
3. **开发模式快速迭代**：editable install 使用符号链接和 sourcemap，支持 watch 模式自动重载
4. **隔离安装验证**：CI 中在无 NodeJS 环境中安装 wheel，验证自包含性
5. **资源路径约定**：前端资源安装到 `share/jupyter/labextensions/<name>/`，这是 JupyterLab 扫描扩展的标准路径

## 验证模式

CI 中的 `test_isolated` job 是验证双包构建正确性的关键：

1. 删除系统 NodeJS
2. pip install wheel
3. 验证 `jupyter labextension list` 显示 OK
4. 运行 browser_check 确认扩展可加载

## 反模式

- ❌ 让终端用户运行 `npm install` 或 `jlpm build`（wheel 应包含预编译资源）
- ❌ 手动维护两个版本号（应使用自动化版本同步）
- ❌ 在 wheel 中包含 node_modules（应只包含编译产物）
- ❌ 不验证隔离安装（可能遗漏构建配置错误）

## 适用场景

- JupyterLab 扩展（最典型场景）
- Jupyter Server 扩展
- 任何包含 Web UI 但希望用户通过 pip 安装的 Python 库
- 混合语言（Python + JS/TS）项目的分发
