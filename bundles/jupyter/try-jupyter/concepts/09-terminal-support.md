---
type: Concept
title: "终端支持：Cockle WASM终端"
description: "详解Try Jupyter的浏览器终端支持：Cockle WASM终端架构、cockle-config-in.json配置、预安装工具包（git/vim/nano等）、命令别名、Git环境变量预设、终端配置文件的gitignore策略。"
tags: [terminal, cockle, wasm-terminal, jupyterlite-terminal, git2cpp, vim, nano, browser-shell]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:50:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: config
    resource: "/references/config-source.md"
    title: "配置文件信源"
  - id: pyproject
    resource: "/references/pyproject-source.md"
    title: "pyproject.toml信源"
---

# 终端支持：Cockle WASM终端

Try Jupyter 支持在浏览器中打开终端，这是通过 **Cockle**（JupyterLite Terminal）实现的——一个编译为WebAssembly的类Unix shell环境。用户可以在JupyterLab中通过 File → New → Terminal 打开终端。

## 终端启用配置

终端功能在 `jupyter-lite.json` 中显式启用：

```json
{
  "jupyter-config-data": {
    "terminalsAvailable": true
  }
}
```

`terminalsAvailable: true` 是终端可用的必要条件。设为 `false` 可禁用终端以减小站点体积。

终端功能由 `jupyterlite-terminal≥1.5.1` 包提供。

## Cockle配置文件

终端行为由 `cockle-config-in.json` 配置。此文件是**输入模板**，构建时由Cockle处理生成运行时配置 `cockle-config.json`（该文件在 `.gitignore` 中排除）。

```json
{
  "packages": {
    "git2cpp": {},
    "lua": {},
    "nano": {},
    "tree": {},
    "vim": {}
  },
  "aliases": {
    "git": "git2cpp",
    "vi": "vim"
  },
  "environment": {
    "GIT_AUTHOR_NAME": "Jane Doe",
    "GIT_AUTHOR_EMAIL": "jane.doe@somewhere.com",
    "GIT_COMMITTER_NAME": "Jane Doe",
    "GIT_COMMITTER_EMAIL": "jane.doe@somewhere.com"
  }
}
```

### 配置分为三部分：packages、aliases、environment

## 预安装包（packages）

终端中预安装了5个WASM编译的Unix工具：

### 1. git2cpp — Git版本控制

Git版本控制系统的WASM编译版本。由于是编译为WASM在浏览器中运行，此Git：
- 操作浏览器文件系统（基于Emscripten的虚拟文件系统）
- 支持基本的Git操作（init、add、commit、log、branch等）
- 在终端中命令名为 `git2cpp`，通过别名映射为 `git`

### 2. lua — Lua脚本语言

Lua编程语言解释器，可用于在终端中运行Lua脚本。

### 3. nano — Nano文本编辑器

一个简单易用的终端文本编辑器，适合快速编辑文件。

常用操作：
- `Ctrl+O`：保存文件
- `Ctrl+X`：退出编辑器
- `Ctrl+W`：搜索

### 4. tree — 目录树查看

以树形结构显示目录内容，方便浏览文件系统。

```bash
tree         # 显示当前目录树
tree -L 2    # 显示2层深度
```

### 5. vim — Vim文本编辑器

强大的模态文本编辑器。通过别名映射，`vi` 命令也指向vim。

## 命令别名（aliases）

```json
{
  "aliases": {
    "git": "git2cpp",
    "vi": "vim"
  }
}
```

| 别名 | 实际命令 | 原因 |
|------|---------|------|
| `git` | `git2cpp` | 用户期望 `git` 命令可用，但WASM包名是git2cpp |
| `vi` | `vim` | Unix系统惯例：`vi` 是系统默认编辑器，通常指向vim |

别名机制让用户可以使用熟悉的命令名，而不需要知道底层WASM包的实际名称。

## 环境变量（environment）

预设4个Git相关的环境变量：

| 变量 | 值 | 用途 |
|------|---|------|
| `GIT_AUTHOR_NAME` | `Jane Doe` | Git提交的作者名称 |
| `GIT_AUTHOR_EMAIL` | `jane.doe@somewhere.com` | Git提交的作者邮箱 |
| `GIT_COMMITTER_NAME` | `Jane Doe` | Git提交的提交者名称 |
| `GIT_COMMITTER_EMAIL` | `jane.doe@somewhere.com` | Git提交的提交者邮箱 |

**为什么需要预设这些变量？**

Git在首次提交时如果没有配置user.name和user.email会报错并阻止提交。预设这些默认值：
1. 避免用户首次使用Git时遇到配置错误
2. 提供合理的默认值（用户可以在终端中 `git config` 覆盖）
3. 确保notebook中的Git演示可以正常运行

> **注意**：这些是公共默认值，用户在使用终端时可以通过 `git config --global user.name "Your Name"` 设置自己的信息。但由于浏览器环境是临时的（刷新后重置），这些配置不会持久化。

## .gitignore中的终端相关文件

```gitignore
# JupyterLite terminal
cockle-config.json
.cockle_temp/
cockle_wasm_env/
```

| 文件/目录 | 说明 |
|----------|------|
| `cockle-config.json` | 构建生成的运行时配置（从cockle-config-in.json生成），不应纳入版本控制 |
| `.cockle_temp/` | Cockle运行时临时目录 |
| `cockle_wasm_env/` | Cockle WASM环境缓存 |

`cockle-config-in.json` 是源配置（纳入版本控制），`cockle-config.json` 是构建产物（排除）。这种 `-in` 后缀命名模式明确区分了输入模板和生成输出。

## 终端使用场景

在Try Jupyter站点中，终端可用于：

1. **文件系统浏览**：用 `ls`、`cd`、`tree` 等命令浏览JupyterLite虚拟文件系统
2. **文本编辑**：用nano或vim编辑notebook关联的文件
3. **Git操作**：在浏览器中体验Git基本操作（demo性质，文件系统为临时）
4. **Lua脚本**：运行Lua脚本进行简单计算
5. **命令行学习**：为学习命令行操作的用户提供零安装环境

## 浏览器终端的限制

Cockle WASM终端与本地终端有重要区别：

| 特性 | 本地终端 | Cockle WASM终端 |
|------|---------|----------------|
| 文件系统持久化 | 磁盘持久存储 | 浏览器内存/IndexedDB（刷新可能丢失） |
| 网络访问 | 完全网络访问 | 受浏览器CORS限制 |
| 系统调用 | 完整Linux syscall | WASM模拟的有限系统调用 |
| 进程模型 | 完整进程管理 | 单线程WASM运行时 |
| 包安装 | apt/pip/conda等 | 仅预装包，不可安装新包 |
| 权限 | 用户/root权限模型 | 浏览器沙箱 |

## 禁用终端

如果不需要终端功能（例如自定义精简站点），修改 `jupyter-lite.json`：

```json
{
  "jupyter-config-data": {
    "terminalsAvailable": false
  }
}
```

同时可以从 `pyproject.toml` 依赖中移除 `jupyterlite-terminal` 包以减小站点体积。

## REPL模式下的终端

`repl/jupyter-lite.json` 只配置了额外禁用的扩展，没有覆盖 `terminalsAvailable` 字段，因此REPL模式下终端仍然可用。如果需要在REPL模式下禁用终端，可以在repl配置中显式设置 `terminalsAvailable: false`。

## 相关概念

- [配置系统](03-configuration-system.md)
- [架构总览](02-architecture-overview.md)
- [构建管线](05-build-pipeline.md)
