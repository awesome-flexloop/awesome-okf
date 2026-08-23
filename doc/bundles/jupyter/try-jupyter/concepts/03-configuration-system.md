---
type: Concept
title: "配置系统：声明式JSON/YAML配置详解"
description: "详解jupyter-lite.json站点配置、jupyter_lite_config.json构建配置、cockle终端配置、repl子目录覆盖配置，以及XAddon环境文件配置。"
tags: [configuration, jupyter-lite.json, jupyter_lite_config.json, cockle, xeus-addon, disabled-extensions]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:50:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: config-source
    resource: "/references/config-source.md"
    title: "配置文件信源"
---

# 配置系统：声明式JSON/YAML配置详解

Try Jupyter 采用**声明式配置**架构，整个站点的行为由多个JSON和YAML配置文件控制，无需编写应用代码。理解这些配置文件是自定义JupyterLite站点的关键。

## 配置文件总览

| 配置文件 | 位置 | 类型 | 作用阶段 | 功能 |
|---------|------|------|---------|------|
| `jupyter-lite.json` | 项目根目录 | JSON | 运行时 | 站点名称、禁用扩展、终端开关 |
| `jupyter_lite_config.json` | 项目根目录 | JSON | 构建时 | 输出目录、内容目录、内核环境文件 |
| `cockle-config-in.json` | 项目根目录 | JSON | 运行时 | 终端预安装包、别名、环境变量 |
| `repl/jupyter-lite.json` | repl/子目录 | JSON | 运行时 | REPL模式额外配置（覆盖/追加） |
| `environment-*.yml` | 项目根目录 | YAML | 构建时 | Xeus内核的包依赖定义 |

## 1. jupyter-lite.json — 站点主配置

这是JupyterLite站点的核心运行时配置，影响站点加载后的行为。

```json
{
  "jupyter-lite-schema-version": 0,
  "jupyter-config-data": {
    "appName": "Try Jupyter!",
    "disabledExtensions": [
      "@jupyterlab/server-proxy",
      "jupyterlab-server-proxy",
      "nbdime-jupyterlab"
    ],
    "terminalsAvailable": true
  }
}
```

### 字段详解

**`jupyter-lite-schema-version`**（整数）
- 当前固定为 `0`
- JupyterLite配置Schema版本号，未来Schema变更时递增

**`jupyter-config-data.appName`**（字符串）
- 设置站点的显示名称
- 显示在浏览器标签页和JupyterLab标题栏
- 当前值：`"Try Jupyter!"`

**`jupyter-config-data.disabledExtensions`**（字符串数组）
- 列出需要**禁用**的JupyterLab扩展ID
- 浏览器端环境下，依赖后端服务的扩展无法正常工作，必须禁用
- 禁用3个扩展：
  - `@jupyterlab/server-proxy` / `jupyterlab-server-proxy`：服务代理扩展，需要后端服务器
  - `nbdime-jupyterlab`：Notebook diff/merge扩展，需要后端Git

**`jupyter-config-data.terminalsAvailable`**（布尔值）
- 控制是否启用终端功能
- 设为 `true` 时，JupyterLab中可打开终端（通过Cockle WASM终端）
- 设为 `false` 可禁用终端，减小站点体积

### 自定义建议

修改此文件可以：
- 更改 `appName` 为自己的站点名称
- 根据需要禁用/启用扩展
- 不需要终端时设 `terminalsAvailable: false` 减小体积

## 2. jupyter_lite_config.json — 构建配置

此文件控制 `jupyter lite build` 命令的构建行为。

```json
{
  "LiteBuildConfig": {
    "output_dir": "dist",
    "contents": ["content"]
  },
  "XeusAddon": {
    "environment_file": [
      "environment-cpp.yml",
      "environment-python.yml",
      "environment-r.yml",
      "environment-sqlite.yml"
    ]
  }
}
```

### LiteBuildConfig 部分

**`output_dir`**（字符串）
- 构建产物输出目录
- 默认值：`"dist"`
- 构建后所有静态文件将生成到此目录

**`contents`**（字符串数组）
- 指定包含用户内容（notebook、数据文件）的目录列表
- 默认值：`["content"]`
- 构建时这些目录的内容会被打包到站点中
- 可以添加多个内容目录，如 `["content", "extra-notebooks"]`

### XeusAddon 部分

**`environment_file`**（字符串数组）
- 列出Xeus内核的conda环境定义文件
- 每个YAML文件定义一个独立的WASM内核环境
- 构建时JupyterLite会根据这些文件创建对应的Xeus内核
- 当前4个环境文件对应4种语言内核

## 3. cockle-config-in.json — 终端配置

此文件配置JupyterLite终端（Cockle）预装的工具和环境。

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

> **注意**：实际被终端读取的配置文件是 `cockle-config.json`，该文件在 `.gitignore` 中排除（构建时生成）。`cockle-config-in.json` 是输入模板。

### packages（预安装包）

终端中预安装5个WASM编译的Unix工具：

| 包名 | 功能 |
|------|------|
| `git2cpp` | Git版本控制系统（C++编译到WASM的版本） |
| `lua` | Lua脚本语言解释器 |
| `nano` | Nano文本编辑器 |
| `tree` | 目录树显示工具（`tree` 命令） |
| `vim` | Vim文本编辑器 |

### aliases（命令别名）

| 别名 | 实际命令 | 说明 |
|------|---------|------|
| `git` | `git2cpp` | 让 `git` 命令可用（指向git2cpp） |
| `vi` | `vim` | 让 `vi` 命令可用（指向vim） |

### environment（环境变量）

预设Git提交相关的环境变量（避免Git提交时提示配置用户信息）：

| 变量 | 默认值 |
|------|-------|
| `GIT_AUTHOR_NAME` | Jane Doe |
| `GIT_AUTHOR_EMAIL` | jane.doe@somewhere.com |
| `GIT_COMMITTER_NAME` | Jane Doe |
| `GIT_COMMITTER_EMAIL` | jane.doe@somewhere.com |

## 4. repl/jupyter-lite.json — REPL模式配置

repl/子目录下的jupyter-lite.json为REPL（交互式控制台）模式提供额外配置。此配置与根目录配置**合并**，相同字段以子目录为准（覆盖）。

```json
{
  "jupyter-lite-schema-version": 0,
  "jupyter-config-data": {
    "disabledExtensions": [
      "@jupyterlab/drawio-extension",
      "jupyterlab-kernel-spy",
      "jupyterlab-tour"
    ]
  }
}
```

在REPL模式下额外禁用3个扩展：

| 扩展 | 原因 |
|------|------|
| `@jupyterlab/drawio-extension` | DrawIO图表编辑器，REPL模式不需要 |
| `jupyterlab-kernel-spy` | 内核状态监视器，REPL场景不需要 |
| `jupyterlab-tour` | 新手引导浮层，REPL用户不需要 |

> **注意**：repl配置只禁用了扩展，没有设置 `appName` 或 `terminalsAvailable`，这些字段从根目录配置继承。

## 5. 配置继承与覆盖规则

```
根目录 jupyter-lite.json (全局默认)
├── appName: "Try Jupyter!"
├── disabledExtensions: [server-proxy, nbdime]
└── terminalsAvailable: true
    │
    ├── lab/ 模式 → 使用根目录配置
    │
    └── repl/ 模式 → 根目录 + repl/子目录配置合并
        └── disabledExtensions: 追加 [drawio, kernel-spy, tour]
```

- JupyterLite支持按子目录放置配置文件实现**按路径覆盖**
- 子目录配置与父目录配置合并，数组字段通常为追加模式
- 这种机制允许为Lab、Notebook、REPL等不同界面设置不同配置

## 6. 禁用扩展的常见模式

浏览器端Jupyter需要禁用的扩展主要有几类：

| 类别 | 示例扩展 | 原因 |
|------|---------|------|
| 服务代理类 | `@jupyterlab/server-proxy` | 无后端服务可代理 |
| Git集成类 | `nbdime-jupyterlab` | 无后端Git服务 |
| 协作类 | 与JupyterHub/Collaboration相关 | 浏览器端无持久用户 |
| 重型功能类 | drawio、kernel-spy | REPL/轻量场景不需要 |

## 自定义站点配置的常用修改

| 需求 | 修改位置 | 修改内容 |
|------|---------|---------|
| 更改站点名称 | `jupyter-lite.json` | `appName` 字段 |
| 添加内容目录 | `jupyter_lite_config.json` | `LiteBuildConfig.contents` 数组追加目录 |
| 禁用更多扩展 | `jupyter-lite.json` | `disabledExtensions` 数组追加扩展ID |
| 添加新语言内核 | `jupyter_lite_config.json` | `XeusAddon.environment_file` 追加yml文件 |
| 终端添加工具 | `cockle-config-in.json` | `packages` 对象添加包名 |
| 添加命令别名 | `cockle-config-in.json` | `aliases` 对象添加映射 |

## 相关概念

- [架构总览](02-architecture-overview.md)
- [内核生态](04-kernel-ecosystem.md)
- [构建管线](05-build-pipeline.md)
- [终端支持](09-terminal-support.md)
