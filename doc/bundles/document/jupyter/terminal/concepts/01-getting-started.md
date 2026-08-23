---
type: Concept
title: 安装与快速开始
description: 安装jupyterlite-terminal、配置JupyterLite站点、构建部署以及基础使用方法
tags: [install, configuration, jupyter-lite.json, build, deploy, quickstart]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: metasource
    resource: /references/metasource.md
    title: 项目元信源
  - id: python-source
    resource: /references/python-source.md
    title: Python端源码信源
  - id: readme
    resource: /../../../../../../external/libs/jupyter/terminal/README.md
    title: README.md
---

# 安装与快速开始

## 前置条件

- Python >= 3.10
- Node.js（构建时需要，用于编译TypeScript和WASM资源复制）
- JupyterLite >= 0.7.0, < 0.9.0

## 安装

### 1. 安装扩展和JupyterLite CLI

```bash
pip install jupyterlite-terminal jupyterlite-core
```

`jupyterlite-terminal` 包含了预构建的 labextension 静态资源，安装后即可在 JupyterLite 构建时被自动发现。

### 2. 创建配置文件

在项目根目录创建 `jupyter-lite.json`，启用终端功能：

```json
{
  "jupyter-lite-schema-version": 0,
  "jupyter-config-data": {
    "terminalsAvailable": true
  }
}
```

> **关键配置**：`terminalsAvailable: true` 是启用终端的必要条件。LiteTerminalAPIClient 的 `isAvailable` getter 会读取此配置，如果不为 `true`，终端功能不会激活。

### 3. 构建JupyterLite站点

```bash
jupyter lite build
```

构建过程中，TerminalAddon 的 `post_build` 钩子会自动执行：
1. 检查 cockle WASM 工具是否可用
2. 如不可用，临时 npm 安装 `@jupyterlite/cockle` 到 `.cockle_temp/`
3. 运行 `prepare_wasm.js --list` 获取所需WASM文件列表
4. 将WASM文件复制到输出目录的 `extensions/@jupyterlite/terminal/static/wasm/`

### 4. 启动预览服务器

```bash
jupyter lite serve
```

或者使用任意静态文件服务器。默认访问 http://localhost:8000。

### 5. 打开终端

在 JupyterLab 界面中：
1. 点击菜单 **File → New → Terminal**
2. 一个新的终端标签页打开，显示 shell 提示符
3. 现在可以输入命令，如 `ls`、`pwd`、`cd /drive` 等

## SharedArrayBuffer 模式配置（可选但推荐）

默认情况下，终端使用 Service Worker 模式处理 stdin 和文件系统。如果服务器支持设置 COOP/COEP 响应头，可以启用 SharedArrayBuffer（SAB）模式获得更好的性能：

### 使用 static-handler

```bash
npx static-handler --coi _output/
```

### 使用 jupyter lite serve

```bash
jupyter lite serve \
  --LiteBuildConfig.extra_http_headers=Cross-Origin-Embedder-Policy=require-corp \
  --LiteBuildConfig.extra_http_headers=Cross-Origin-Opener-Policy=same-origin
```

SAB模式下，文件IO通过Atomics实现同步调用，不需要Service Worker中转，延迟更低。终端会自动检测环境并选择最佳模式。

## 基础使用

### 常用命令

终端启动后可以执行cockle内置命令：

```bash
# 查看当前目录
pwd

# 列出文件
ls

# 切换到DriveFS（JupyterLite文件系统）
cd /drive

# 文件操作
cp months.txt other.txt
rm other.txt

# 查看stdin模式
cockle-config stdin

# 切换stdin模式（sab/sw）
cockle-config stdin sab
cockle-config stdin sw
```

### Tab补全

- 输入命令名的前几个字符后按 `Tab` 自动补全（如 `una` → `uname`）
- 输入文件名的前几个字符后按 `Tab` 自动补全（如 `grep ember mon` → `grep ember months.txt`）
- 按 `Tab` 两次列出所有可用命令

### 交互式命令

支持需要stdin输入的交互式命令，如 `grep`：

```bash
grep o
# 然后输入文本行，按 Ctrl+D 结束输入
```

## 开发模式安装

如果需要修改源码并实时调试：

```bash
# 克隆仓库
git clone https://github.com/jupyterlite/terminal.git
cd terminal

# 以可编辑模式安装Python包
pip install -e "."

# 链接开发版本到JupyterLab
jupyter labextension develop . --overwrite

# 监听TypeScript变化自动重建
jlpm watch

# 另一个终端运行JupyterLab
jupyter lab
```

构建产物输出到 `jupyterlite_terminal/labextension/` 目录。

## 部署目录准备

创建 `deploy/` 目录用于自定义部署：

```bash
mkdir -p deploy/contents
# 将要在终端中访问的文件放入 contents/ 目录
echo "Hello from JupyterLite Terminal!" > deploy/contents/hello.txt
```

构建时使用 `--contents` 指定内容目录：

```bash
cd deploy
jupyter lite build --contents contents
```

## 常见问题

### Q: 终端菜单不出现？
确认 `jupyter-lite.json` 中 `terminalsAvailable` 设置为 `true`，并重新执行 `jupyter lite build`。

### Q: 文件系统不可用？
检查是否正确挂载了DriveFS。终端默认挂载到 `/drive`，使用 `ls /drive` 查看文件。

### Q: git命令需要CORS代理？
`git2cpp clone` 远程仓库需要本地CORS代理。在ui-tests目录运行：
```bash
cd ui-tests
jlpm
jlpm serve:cors-proxy
```
然后在终端中设置环境变量：
```bash
export GIT_CORS_PROXY=http://localhost:8881/
git clone https://github.com/jupyterlite/terminal
```

### Q: SAB模式不生效？
确认服务器正确发送了COOP/COEP头。可以在浏览器开发者工具的Console中查看"Service worker supports terminal stdin"消息，或使用 `cockle-config stdin` 检查当前模式。

## 相关概念

- [架构概览](02-architecture-overview.md)：理解六插件如何协作实现终端
- [插件系统](03-plugin-system.md)：了解各插件的详细职责
- [无头命令执行](05-headless-exec.md)：编程式API使用方法
