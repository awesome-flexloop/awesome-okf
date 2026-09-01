---
type: Reference
title: package.json 扩展配置参考
description: JupyterLab 扩展 package.json 中 jupyterlab 字段的完整配置参考，涵盖 mimeExtension/extension/outputDir/schemaDir 等
tags: [config, package.json, jupyterlab, reference]
sources:
  - id: fasta-pkg
    resource: external/libs/jupyter/jupyter-renderers/packages/fasta-extension/package.json
    title: fasta-extension/package.json
  - id: geojson-pkg
    resource: external/libs/jupyter/jupyter-renderers/packages/geojson-extension/package.json
    title: geojson-extension/package.json
  - id: katex-pkg
    resource: external/libs/jupyter/jupyter-renderers/packages/katex-extension/package.json
    title: katex-extension/package.json
  - id: mathjax2-pkg
    resource: external/libs/jupyter/jupyter-renderers/packages/mathjax2-extension/package.json
    title: mathjax2-extension/package.json
  - id: vega3-pkg
    resource: external/libs/jupyter/jupyter-renderers/packages/vega3-extension/package.json
    title: vega3-extension/package.json
  - id: root-pkg
    resource: external/libs/jupyter/jupyter-renderers/package.json
    title: root package.json
  - id: lerna
    resource: external/libs/jupyter/jupyter-renderers/lerna.json
    title: lerna.json
status: stable
generated:
  by: source-code-to-okf-wiki
  at: 2026-08-22
---

# package.json 扩展配置参考

本文档详细说明 JupyterLab 扩展在 `package.json` 中的配置字段，基于 jupyter-renderers 5个扩展包的实际配置整理。

## jupyterlab 字段

`package.json` 中的 `"jupyterlab"` 字段是 JupyterLab 扩展的核心配置。

### MIME 渲染器扩展配置

```json
{
  "jupyterlab": {
    "mimeExtension": true,
    "outputDir": "jupyterlab_<name>/labextension"
  }
}
```

| 字段 | 类型 | 说明 | 使用的包 |
|------|------|------|---------|
| `mimeExtension` | boolean | 标记为 MIME 渲染器扩展（非应用扩展） | fasta, geojson, vega3 |
| `outputDir` | string | 编译产物输出目录（相对于包根目录） | 所有包 |

**示例**（fasta-extension）：[^fasta-pkg]

```json
{
  "jupyterlab": {
    "mimeExtension": true,
    "outputDir": "jupyterlab_fasta/labextension"
  }
}
```

### 应用扩展配置

```json
{
  "jupyterlab": {
    "extension": true,
    "outputDir": "jupyterlab_<name>/labextension",
    "schemaDir": "schema",
    "disabledExtensions": ["其他扩展ID"]
  }
}
```

| 字段 | 类型 | 说明 | 使用的包 |
|------|------|------|---------|
| `extension` | boolean | 标记为应用扩展（提供 Token 服务） | katex, mathjax2 |
| `outputDir` | string | 编译产物输出目录 | 所有包 |
| `schemaDir` | string | JSON Schema 设置文件目录（可选） | katex |
| `disabledExtensions` | string[] | 启用本扩展时自动禁用的扩展 ID 列表 | katex |

**示例**（katex-extension）：[^katex-pkg]

```json
{
  "jupyterlab": {
    "extension": true,
    "outputDir": "jupyterlab_katex/labextension",
    "schemaDir": "schema",
    "disabledExtensions": [
      "@jupyterlab/mathjax-extension:plugin",
      "@jupyterlab/mathjax2-extension:plugin"
    ]
  }
}
```

**注意**：KaTeX 扩展启用时会自动禁用 MathJax 和 MathJax2 扩展，确保同一时间只有一个 LaTeX 排版器生效。

## styleModule 字段

```json
{
  "styleModule": "style/index.js"
}
```

所有5个包都设置了此字段，指向样式入口文件。`style/index.js` 通常导入 CSS 文件：

```javascript
// style/index.js
import './base.css';
import './index.css';
```

## 标准 scripts 字段

所有5个扩展包使用完全一致的构建脚本模式：

| 脚本 | 命令 | 说明 |
|------|------|------|
| `build` | `jlpm build:lib && jlpm build:labextension:dev` | 开发模式构建（含 sourcemap） |
| `build:lib` | `tsc --sourceMap` | 仅编译 TypeScript |
| `build:lib:prod` | `tsc` | 生产模式编译 TS（无 sourcemap） |
| `build:labextension` | `jupyter labextension build .` | 构建 JupyterLab 扩展（生产） |
| `build:labextension:dev` | `jupyter labextension build --development True .` | 构建 JupyterLab 扩展（开发） |
| `build:prod` | `jlpm clean && jlpm build:lib:prod && jlpm build:labextension` | 完整生产构建 |
| `clean` | `jlpm clean:lib` | 清理编译产物 |
| `clean:all` | `jlpm clean:lib && jlpm clean:labextension && jlpm clean:lintcache` | 全量清理 |
| `clean:labextension` | `rimraf <python_pkg>/labextension <python_pkg>/_version.py` | 清理 labextension |
| `clean:lib` | `rimraf lib tsconfig.tsbuildinfo` | 清理 TS 编译输出 |
| `watch` | `run-p watch:src watch:labextension` | 并行监听 TS 和 labextension |
| `watch:src` | `tsc -w [--sourceMap]` | 监听 TS 变化 |
| `watch:labextension` | `jupyter labextension watch .` | 监听 labextension 变化 |
| `install:extension` | `jlpm build` | 安装扩展（=build） |

## 公共依赖

### 运行时依赖（所有 MIME 渲染器共享）

| 包 | 版本范围 | 用途 |
|----|---------|------|
| `@jupyterlab/rendermime-interfaces` | `^3.0.0 \|\| ^3.8.0` | MIME 渲染器接口定义 |
| `@lumino/widgets` | `^1.0.0 \|\| ^2.1.0` | Widget 基类 |
| `@lumino/messaging` | `^1.0.0 \|\| ^2.0.0` | 消息系统（生命周期） |

### 各扩展特有依赖

| 扩展 | 特有依赖 | 用途 |
|------|---------|------|
| fasta | `@jlab-contrib/msa: ^1.1.2` | 多序列比对查看器 |
| geojson | `@jupyterlab/apputils`, `@jupyterlab/ui-components`, `@lumino/algorithm`, `leaflet: ^1.5.0` | 对话框/图标/模糊搜索/Leaflet地图 |
| katex | `@jupyterlab/application`, `@jupyterlab/rendermime`, `@jupyterlab/settingregistry`, `katex: ^0.12.0` | 应用插件/设置系统/KaTeX引擎 |
| mathjax2 | `@jupyterlab/application`, `@jupyterlab/coreutils`, `@jupyterlab/rendermime`, `@jupyterlab/translation`, `@lumino/coreutils` | PageConfig/PromiseDelegate/翻译 |
| vega3 | `@lumino/coreutils`, `vega-embed: 3.9.2` | JSON类型/vega-embed渲染（固定版本） |

## Monorepo 根配置

### package.json（根）[^root-pkg]

```json
{
  "private": true,
  "workspaces": ["packages/*"],
  "scripts": {
    "build": "lerna run --parallel build",
    "build-py": "rimraf dist && mkdir -p dist && lerna run --parallel clean:all && lerna exec --concurrency 4 -- python -m build && lerna exec --concurrency 4 -- mv ./dist/jupyterlab* ../../dist/",
    "build:prod": "lerna run --parallel build:prod",
    "watch": "lerna run --parallel watch",
    "install-ext": "lerna run build:labextension:dev",
    "install-py": "lerna exec --concurrency 4 -- python -m pip install -e ."
  },
  "devDependencies": {
    "lerna": "^6.6.0",
    "@jupyterlab/buildutils": "^4.0.0"
  }
}
```

### lerna.json [^lerna]

```json
{
  "npmClient": "yarn",
  "useWorkspaces": true,
  "version": "independent"
}
```

**关键配置**：
- `"version": "independent"`：每个包独立版本号（非统一版本）
- `"npmClient": "yarn"`：使用 yarn 而非 npm
- `"useWorkspaces": true`：使用 yarn workspaces 管理依赖提升

## install.json（根目录）[^root-pkg]

```json
{
  "packageManager": "python",
  "packageName": "jupyterlab-renderers",
  "uninstallInstructions": "Use your Python package manager (pip, conda, etc.) to uninstall the package jupyterlab-renderers"
}
```

这是 JupyterLab 元包的安装配置文件，标记该包由 Python 包管理器管理。

[^fasta-pkg]: fasta-extension/package.json
[^katex-pkg]: katex-extension/package.json
[^lerna]: lerna.json
[^root-pkg]: root package.json
