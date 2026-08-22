---
type: Concept
title: 快速开始
description: 安装 jupyterlite-pyodide-kernel、构建 JupyterLite 站点、基本配置和部署
tags: [getting-started, install, build, deploy, configuration]
prerequisites: ["00-introduction"]
objectives: ["完成 pyodide-kernel 的安装", "能够构建 JupyterLite 站点", "理解基本配置选项"]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00Z" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: pyproject
    resource: /references/addon-source.md
    title: pyproject.toml
  - id: addons
    resource: /references/addon-source.md
    title: addons/
---

# 快速开始

## 为什么需要了解安装和构建流程

pyodide-kernel 不仅是一个浏览器端运行时库，它还包含构建阶段的 Python Addon，负责下载 Pyodide 发行版、准备 wheel 包资源、生成配置文件。正确安装和配置是构建可用的 JupyterLite 站点的前提。

## 安装

### 使用 pip 安装

```bash
pip install jupyterlite-pyodide-kernel
```

安装后，三个 JupyterLite Addon 通过 `[tool.hatch.entry_points.jupyterlite]` 自动注册（F-017）：
- `jupyterlite-pyodide-kernel-pyodide` → `PyodideAddon`
- `jupyterlite-pyodide-kernel-piplite` → `PipliteAddon`
- `jupyterlite-pyodide-kernel-pyodide-lock` → `PyodideLockAddon`

### 从源码安装

```bash
git clone https://github.com/jupyterlite/pyodide-kernel
cd pyodide-kernel
pip install -e ".[dev,test]"
```

开发依赖包括 pytest、jupyterlab、pytest-check-links 等（F-013）。

## 构建 JupyterLite 站点

安装后，使用 `jupyter lite build` 命令构建站点：

```bash
jupyter lite build
```

构建过程中三个 Addon 的生命周期执行顺序：

1. **post_init** 阶段：
   - `PyodideAddon`：如果配置了 `--pyodide` URL，下载并解压 Pyodide 发行版到缓存
   - `PipliteAddon`：下载 `--piplite-wheels` 指定的 wheel 文件
   - `PyodideLockAddon`：如果启用 `--pyodide-lock`，开始 lockfile 定制

2. **build** 阶段：
   - `PyodideAddon`：将 Pyodide 文件复制到输出目录 `static/pyodide/`
   - `PipliteAddon`：从 `lite_dir/pypi/` 复制本地 wheels 到输出目录

3. **post_build** 阶段：
   - `PyodideAddon`：更新 `jupyter-lite.json`，设置 pyodideUrl
   - `PipliteAddon`：生成 `pypi/all.json` 索引，更新 pipliteUrls
   - `PyodideLockAddon`：生成定制的 `pyodide-lock.json`

4. **check** 阶段：
   - 各 Addon 验证配置正确性

构建输出目录默认是 `_output/`，包含：

```
_output/
├── jupyter-lite.json          # 站点配置
├── static/
│   ├── pyodide/               # Pyodide 发行版
│   │   ├── pyodide.mjs        # Pyodide ES 模块入口
│   │   └── pyodide-lock.json  # 包锁文件
│   └── ...
└── pypi/
    └── all.json               # piplite wheel 索引
```

## 基本配置

### 使用 jupyter-lite.json 配置

在构建目录创建 `jupyter-lite.json`，配置 Pyodide Kernel：

```json
{
  "litePluginSettings": {
    "@jupyterlite/pyodide-kernel-extension:kernel": {
      "pyodideUrl": "https://cdn.jsdelivr.net/pyodide/v0.29.3/full/pyodide.mjs",
      "pipliteUrls": [
        "./pypi/all.json?sha256=<checksum>"
      ],
      "disablePyPIFallback": false,
      "mountDrive": false
    }
  }
}
```

### CLI 配置选项

| CLI 选项 | 对应 Addon | 说明 |
|----------|-----------|------|
| `--pyodide <url>` | PyodideAddon | 指定自定义 Pyodide 发行版 URL（F-018） |
| `--piplite-wheels <urls>` | PipliteAddon | 添加额外的 wheel URL（F-022） |
| `--pyodide-lock` | PyodideLockAddon | 启用 lockfile 定制（F-026） |

### 关键配置项

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `pyodideUrl` | CDN URL（F-034） | Pyodide 发行版 URL，默认从 jsdelivr CDN 加载 |
| `pipliteUrls` | `[]` | wheel 索引 URL 列表（F-037） |
| `disablePyPIFallback` | `false`（F-014） | 是否禁用 PyPI 回退 |
| `mountDrive` | `false` | 是否挂载 Emscripten DriveFS（需要 crossOriginIsolated） |
| `loadPyodideOptions` | `{}` | 传递给 `loadPyodide()` 的额外选项 |

### 默认 Pyodide CDN URL

```
https://cdn.jsdelivr.net/pyodide/{PYODIDE_VERSION}/full/pyodide.mjs
```

其中 `PYODIDE_VERSION` 默认为 `0.29.3`（F-014），`PYODIDE_API_INDEX_URL` 指向 jsdelivr CDN（F-034）。

## 启动预览

构建完成后，启动本地服务器预览：

```bash
jupyter lite serve
```

或使用任何静态文件服务器：

```bash
cd _output
python -m http.server 8000
```

然后在浏览器中打开 `http://localhost:8000`。

### 关于 crossOriginIsolated

如果需要 Coincident 模式（同步文件系统和同步 stdin），服务器需要发送以下 HTTP 头：

```
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
```

没有这些头时，kernel 自动降级到 Comlink 模式（F-078 注释说明 Firefox 隐私模式下文件系统不同步）。

## 下一步

- [架构总览](/concepts/02-architecture-overview.md) — 理解双层架构
- [构建时 Addon 系统](/concepts/04-build-addons.md) — 深入了解三个 Addon
- [基本安装与配置示例](/examples/basic-install-config.md) — 完整的配置示例

## 源码参考

- [Python Addon 源码](/references/addon-source.md)
- [JupyterLab Extension 源码](/references/extension-source.md)
