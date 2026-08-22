---
type: Reference
title: JupyterLab 插件解剖结构
description: JupyterLab 扩展的标准文件结构、构建配置和插件对象定义，基于28个官方示例的共性提取
tags: [jupyterlab, extension, anatomy, structure, build]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: "2027-02-22"
sources:
  - id: hello-world-pkg
    resource: /references/plugin-anatomy.md
    title: hello-world/package.json 标准模板
  - id: hello-world-pyproject
    resource: /references/plugin-anatomy.md
    title: hello-world/pyproject.toml Python构建配置
  - id: hello-world-init
    resource: /references/plugin-anatomy.md
    title: hello-world __init__.py 入口点
  - id: commands-src
    resource: /references/plugin-anatomy.md
    title: commands/src/index.ts 基础命令插件
---

## 标准目录结构

每个 JupyterLab 扩展示例遵循统一的 Copier 模板结构：

```
<extension-name>/
├── src/                          # TypeScript 源码
│   └── index.ts                  # 插件入口（默认导出 JupyterFrontEndPlugin）
├── style/                        # CSS 样式
│   ├── base.css                  # 基础样式
│   ├── index.css                 # 样式入口
│   └── index.js                  # 样式模块加载器
├── schema/                       # JSON Schema 设置（可选）
│   └── plugin.json               # 插件设置 schema
├── <python_package>/             # Python 包目录（snake_case命名）
│   └── __init__.py               # labextension 路径声明
├── ui-tests/                     # Playwright 集成测试
│   ├── tests/
│   └── jupyter_server_test_config.py
├── package.json                  # npm 包配置 + jupyterlab 元数据
├── pyproject.toml                # Python 构建配置（hatchling）
├── tsconfig.json                 # TypeScript 编译配置
├── install.json                  # 扩展安装元数据
└── README.md                     # 示例说明文档
```

## package.json 关键字段

```json
{
  "name": "@jupyterlab-examples/<extension-name>",
  "version": "0.1.0",
  "main": "lib/index.js",
  "types": "lib/index.d.ts",
  "style": "style/index.css",
  "styleModule": "style/index.js",
  "jupyterlab": {
    "extension": true,
    "outputDir": "<python_package>/labextension"
  },
  "scripts": {
    "build": "jlpm build:lib && jlpm build:labextension:dev",
    "build:lib": "tsc --sourceMap",
    "build:labextension": "jupyter labextension build .",
    "watch": "run-p watch:src watch:labextension",
    "watch:src": "tsc -w --sourceMap",
    "watch:labextension": "jupyter labextension watch ."
  },
  "dependencies": {
    "@jupyterlab/application": "^4.0.0"
  },
  "devDependencies": {
    "@jupyterlab/builder": "^4.0.0",
    "typescript": "~5.8.0"
  }
}
```

关键事实：
- `jupyterlab.extension: true` 标记此 npm 包为 JupyterLab 扩展
- `outputDir` 指定编译产物输出到 Python 包的 labextension 目录
- 构建工具链：TypeScript 编译 → JupyterLab Builder 打包
- 核心依赖只有 `@jupyterlab/application`，其他按需引入

## pyproject.toml 构建配置

```toml
[build-system]
requires = ["hatchling>=1.5.0", "jupyterlab>=4.0.0,<5", "hatch-nodejs-version>=0.3.2"]
build-backend = "hatchling.build"

[project]
name = "jupyterlab_examples_<extension_name>"
requires-python = ">=3.9"

[tool.hatch.build.targets.wheel.shared-data]
"<python_package>/labextension" = "share/jupyter/labextensions/@jupyterlab-examples/<extension-name>"
"install.json" = "share/jupyter/labextensions/@jupyterlab-examples/<extension-name>/install.json"

[tool.hatch.build.hooks.jupyter-builder]
dependencies = ["hatch-jupyter-builder>=0.5"]
build-function = "hatch_jupyter_builder.npm_builder"
build_cmd = "build:prod"
npm = ["jlpm"]
```

关键事实：
- 构建后端使用 **hatchling**（非 setuptools）
- hatch-jupyter-builder 钩子负责调用 npm/jlpm 构建前端
- wheel 包将 labextension 静态文件安装到 `share/jupyter/labextensions/`
- 版本号从 package.json 的 nodejs 字段动态读取（`[tool.hatch.version] source = "nodejs"`）

## Python __init__.py 入口点

```python
try:
    from ._version import __version__
except ImportError:
    __version__ = "dev"

def _jupyter_labextension_paths():
    return [{
        "src": "labextension",
        "dest": "@jupyterlab-examples/<extension-name>"
    }]
```

关键事实：
- `_jupyter_labextension_paths()` 返回 labextension 静态文件路径映射
- 服务端扩展额外需要 `_jupyter_server_extension_points()` 和 `_load_jupyter_server_extension()`
- `_version.py` 由构建过程自动生成

## JupyterFrontEndPlugin 插件对象

```typescript
import { JupyterFrontEnd, JupyterFrontEndPlugin } from '@jupyterlab/application';

const plugin: JupyterFrontEndPlugin<void> = {
  id: '<unique-plugin-id>',
  description: '插件描述',
  autoStart: true,
  requires: [/* 必需的依赖 Token */],
  optional: [/* 可选的依赖 Token */],
  provides: /* 导出的 Token（供其他插件使用） */,
  activate: (app: JupyterFrontEnd, ...deps) => {
    // 插件激活逻辑
  }
};

export default plugin;
```

关键字段：
- `id`：全局唯一插件标识符，格式通常为 `@scope/name:plugin-name`
- `autoStart: true`：JupyterLab 启动时自动激活
- `requires`：必需依赖数组，缺失则插件不加载
- `optional`：可选依赖数组，缺失时传入 `null`
- `provides`：导出 Token，允许其他插件依赖此插件
- `activate`：激活函数，接收 app 实例和依赖注入的对象

**多插件导出**：某些示例（clap-button、metadata-form）导出插件数组 `export default [plugin1, plugin2]`，实现 JupyterLab/Notebook 双兼容。

## install.json

```json
{
  "packageManager": "python",
  "packageName": "<python_package_name>",
  "uninstallInstructions": "Use your Python package manager to uninstall"
}
```

标记此扩展通过 Python 包管理器安装/卸载。

## 相关概念

- [插件基础与依赖注入](/concepts/03-plugin-basics.md)
- [命令系统](/concepts/04-commands.md)
- [项目搭建与开发工作流](/concepts/02-project-setup.md)
