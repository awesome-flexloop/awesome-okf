---
type: Reference
title: "JupyterLite 配置文件源码"
description: "jupyter-lite.json、jupyter_lite_config.json、cockle-config-in.json、repl/jupyter-lite.json 四个配置文件的完整结构解析"
tags: [jupyter-lite, configuration, jupyter-config-data, lite-build-config, xeus-addon, cockle, terminal]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T10:50:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - id: jupyter-lite-json
    resource: "../../../../../external/libs/jupyter/try-jupyter/jupyter-lite.json"
    title: "try-jupyter/jupyter-lite.json"
  - id: jupyter-lite-config-json
    resource: "../../../../../external/libs/jupyter/try-jupyter/jupyter_lite_config.json"
    title: "try-jupyter/jupyter_lite_config.json"
  - id: cockle-config
    resource: "../../../../../external/libs/jupyter/try-jupyter/cockle-config-in.json"
    title: "try-jupyter/cockle-config-in.json"
  - id: repl-jupyter-lite
    resource: "../../../../../external/libs/jupyter/try-jupyter/repl/jupyter-lite.json"
    title: "try-jupyter/repl/jupyter-lite.json"
---

# JupyterLite 配置文件源码

本信源登记项目中4个JSON配置文件的结构与字段含义。

## 1. jupyter-lite.json（站点主配置）

文件路径：`jupyter-lite.json`（项目根目录）

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

### 字段说明

| 字段 | 类型 | 值 | 说明 |
|------|------|---|------|
| `jupyter-lite-schema-version` | integer | `0` | JupyterLite配置Schema版本 |
| `jupyter-config-data.appName` | string | `"Try Jupyter!"` | 站点显示名称 |
| `jupyter-config-data.disabledExtensions` | string[] | 3个扩展 | 禁用的JupyterLab扩展列表 |
| `jupyter-config-data.terminalsAvailable` | boolean | `true` | 是否启用终端功能 |

### 被禁用的扩展

| 扩展ID | 禁用原因 |
|--------|---------|
| `@jupyterlab/server-proxy` | 服务代理（浏览器端无后端服务可代理） |
| `jupyterlab-server-proxy` | 服务代理（同上） |
| `nbdime-jupyterlab` | Notebook diff/merge（需要后端Git支持） |

## 2. jupyter_lite_config.json（构建配置）

文件路径：`jupyter_lite_config.json`（项目根目录）

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

### 字段说明

| 字段 | 类型 | 值 | 说明 |
|------|------|---|------|
| `LiteBuildConfig.output_dir` | string | `"dist"` | 构建输出目录 |
| `LiteBuildConfig.contents` | string[] | `["content"]` | 包含的用户内容目录 |
| `XeusAddon.environment_file` | string[] | 4个yml文件 | Xeus内核环境定义文件列表 |

## 3. cockle-config-in.json（终端配置模板）

文件路径：`cockle-config-in.json`（项目根目录）

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

> **注意**：`cockle-config.json`（输出文件）在 `.gitignore` 中排除，`cockle-config-in.json` 是输入模板。

### 终端预安装包（5个）

| 包名 | 用途 |
|------|------|
| `git2cpp` | Git版本控制（WASM编译版本） |
| `lua` | Lua脚本语言 |
| `nano` | Nano文本编辑器 |
| `tree` | 目录树查看工具 |
| `vim` | Vim文本编辑器 |

### 命令别名

| 别名 | 目标命令 |
|------|---------|
| `git` | `git2cpp` |
| `vi` | `vim` |

### 预设环境变量

| 变量 | 值 | 用途 |
|------|---|------|
| `GIT_AUTHOR_NAME` | `Jane Doe` | Git提交作者名 |
| `GIT_AUTHOR_EMAIL` | `jane.doe@somewhere.com` | Git提交作者邮箱 |
| `GIT_COMMITTER_NAME` | `Jane Doe` | Git提交者名 |
| `GIT_COMMITTER_EMAIL` | `jane.doe@somewhere.com` | Git提交者邮箱 |

## 4. repl/jupyter-lite.json（REPL模式配置）

文件路径：`repl/jupyter-lite.json`

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

REPL（交互式解释器）模式下额外禁用3个扩展：

| 扩展ID | 禁用原因 |
|--------|---------|
| `@jupyterlab/drawio-extension` | DrawIO图表（REPL不需要图表编辑） |
| `jupyterlab-kernel-spy` | 内核监视器（REPL模式不需要） |
| `jupyterlab-tour` | 新手引导（REPL用户不需要引导） |

## 配置层级关系

```
jupyter-lite.json (站点级配置)
├── appName: "Try Jupyter!"
├── disabledExtensions: [server-proxy, nbdime]
└── terminalsAvailable: true
    └── repl/jupyter-lite.json (REPL子目录覆盖)
        └── disabledExtensions: 额外禁用 [drawio, kernel-spy, tour]
```

## 相关信源

- [pyproject.toml 配置信源](pyproject-source.md)
- [内核环境文件信源](config-source.md#xeus内核环境文件)
