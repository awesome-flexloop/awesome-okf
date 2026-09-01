---
type: Concept
title: 快速开始
description: 从环境准备到构建部署xeus内核的JupyterLite站点的完整入门指南
tags: [getting-started, install, build, deploy, environment]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: readme
    resource: /concepts/01-getting-started.md
    title: README.md installation section
  - id: addon
    resource: /references/python-addon-source.md
    title: XeusAddon构建参考
  - id: meta
    resource: /references/metasource.md
    title: 项目元数据
---

## 前置条件

| 依赖 | 版本要求 | 说明 |
|------|---------|------|
| Python | >= 3.10 | 构建端运行环境（支持3.10-3.14） |
| JupyterLab | >= 4.0.0 | JupyterLite 基于 JupyterLab |
| jupyterlite-core | 0.7.0 ~ 0.9.0 | JupyterLite 核心框架 |
| micromamba | 最新版 | conda 环境管理工具（需预安装） |
| Node.js | 待确认 | 构建 JupyterLab 扩展需要 |

> **注意**：micromamba 必须预先安装在系统 PATH 中（通过 `conda install micromamba -c conda-forge` 或从 [官方文档](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html) 下载安装），构建过程不会自动下载。

## 安装

### 方式一：pip 安装

```bash
pip install jupyterlite-xeus
```

这会安装 Python 包和 JupyterLite 扩展（通过 `hatch-nodejs-version` + `jupyter-builder` 自动处理前端资源）。

### 方式二：从源码开发

```bash
# 克隆仓库
git clone https://github.com/jupyterlite/xeus.git
cd xeus

# 安装Python包（开发模式）
python -m pip install -e .

# 安装前端依赖并构建
yarn install
yarn build
```

## 创建 JupyterLite 站点

### 步骤1：准备环境配置

创建 `environment.yml`（可选，默认已包含 xeus-python）：

```yaml
name: xeus-python-kernel
channels:
  - https://prefix.dev/emscripten-forge-4x
  - https://prefix.dev/conda-forge
dependencies:
  - xeus-python
  - numpy
  - pandas
  - pip:
    - some-pure-python-package
```

> pip 部分**只能安装纯Python包**——任何包含C扩展（.so/.pyd等）的包会被拒绝，必须通过conda安装。详见 [包管理](06-package-management.md)。

### 步骤2：构建 JupyterLite

```bash
jupyter lite build
```

构建过程中 XeusAddon 会自动执行：

1. 下载/定位 micromamba
2. 创建 `emscripten-wasm32` 平台的 conda 环境
3. 安装 environment.yml 中指定的包
4. 用 empack 将 conda 环境打包为浏览器可用的 tar.gz
5. 复制 xeus 内核二进制文件到输出目录
6. 生成 kernels.json 和 kernel.json

构建产出位于 `_output/`（默认）目录。

### 步骤3：预览站点

```bash
jupyter lite serve
```

默认在 `http://localhost:8000` 启动本地服务器。

> **重要**：要获得最佳体验（coincident模式同步文件系统），服务器需要发送 COOP/COEP 响应头。简单开发服务器可能不支持，此时会自动降级到comlink模式。

## 配置选项

在 `jupyter_lite_config.json` 中配置 xeus addon：

```json
{
  "XeusAddon": {
    "log_level": "INFO",
    "environment_file": "environment.yml",
    "default_channels": [
      "https://prefix.dev/emscripten-forge-4x",
      "https://prefix.dev/conda-forge"
    ],
    "mount_jupyterlite_content": false,
    "empack_config": null
  }
}
```

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `log_level` | string | "INFO" | 日志级别（DEBUG/INFO/WARNING/ERROR） |
| `environment_file` | string | "" | 自定义environment.yml路径 |
| `default_channels` | string[] | prefix.dev两个频道 | conda channels列表 |
| `mount_jupyterlite_content` | bool | 仅voici模式为true | 将JupyterLite文件目录打包挂载到/files |
| `empack_config` | string/dict | null | empack打包配置 |

## 部署到生产

构建产出的 `_output/` 目录是纯静态文件，可以部署到任意静态文件服务器：

- **GitHub Pages**：直接push `_output/` 到gh-pages分支
- **Vercel/Netlify**：将构建目录设为 `_output/`
- **Nginx/Apache**：配置静态文件服务

**生产部署强烈建议**配置 COOP/COEP 响应头以启用 crossOriginIsolated 模式：

```nginx
# Nginx 配置
add_header Cross-Origin-Opener-Policy "same-origin" always;
add_header Cross-Origin-Embedder-Policy "require-corp" always;
add_header Cross-Origin-Resource-Policy "cross-origin" always;
```

不配置这些头时，xeus仍然可以工作（自动降级到comlink模式），但文件系统性能较差且stdin依赖Service Worker。

## 验证安装

打开浏览器访问部署的JupyterLite站点：

1. 点击 Launcher 中应该看到 xeus 内核图标（如"Python (XPython)"）
2. 创建新 Notebook，选择 xeus 内核
3. 在单元格中输入 `print("Hello from xeus!")` 并执行
4. 尝试 `import numpy; numpy.array([1,2,3])` 验证包可用

## 常见问题

### Q: 构建时 micromamba 下载失败？
A: 手动下载 micromamba 2.0.5 并设置环境变量 `JUPYTERLITE_MICROMAMBA_PATH` 指向可执行文件路径。

### Q: pip 安装的包报错"cannot be installed with pip in emscripten-wasm32"？
A: 该包含有C扩展，不能通过pip安装到WASM环境。改用conda从emscripten-forge频道安装。

### Q: Notebook 中文件操作很慢？
A: 检查页面是否启用了crossOriginIsolated（DevTools控制台输入`crossOriginIsolated`）。如果为false，配置COOP/COEP响应头。

## 下一步

- 理解架构设计：→ [双语言分层架构](02-architecture.md)
- 了解内核启动过程：→ [内核生命周期](04-kernel-lifecycle.md)
- 自定义环境包：→ [构建系统详解](05-build-system.md)
- 完整部署示例：→ [基础部署示例](../examples/basic-deploy.md)
