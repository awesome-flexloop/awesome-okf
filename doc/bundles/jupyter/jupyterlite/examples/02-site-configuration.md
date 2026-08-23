---
type: Example
title: 站点配置（jupyter-lite.json）
description: 配置应用名称、默认内核、禁用扩展、设置覆盖等
tags: [config, jupyter-lite-json, settings, customization]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T15:32:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: app-source
    resource: /references/app-source.md
    title: 应用框架信源
---

## 基础配置

在项目根目录创建 `jupyter-lite.json` 文件，这是JupyterLite的站点级配置文件：

```json
{
  "jupyter-lite-schema-version": 0,
  "jupyter-config-data": {
    "appName": "My JupyterLite",
    "appUrl": "/lab",
    "baseUrl": "/",
    "defaultKernelName": "python"
  }
}
```

构建时，此文件会被复制到 `_output/jupyter-lite.json`，并被前端读取。

## 配置选项

### 应用设置

```json
{
  "jupyter-config-data": {
    "appName": "Data Science Playground",
    "appVersion": "1.0.0",
    "appUrl": "/lab",
    "baseUrl": "/",
    "faviconUrl": "/favicon.ico",
    "terminalsAvailable": false
  }
}
```

### 内核配置

```json
{
  "jupyter-config-data": {
    "defaultKernelName": "python",
    "kernelspecs": {
      "python": {
        "name": "python",
        "display_name": "Python (Pyodide)",
        "language": "python"
      }
    }
  }
}
```

### 禁用扩展

```json
{
  "jupyter-config-data": {
    "disabledExtensions": [
      "@jupyterlab/extensionmanager-extension",
      "@jupyterlab/help-extension"
    ]
  }
}
```

### 设置覆盖（settingsOverrides）

覆盖JupyterLab扩展的设置：

```json
{
  "jupyter-config-data": {
    "settingsOverrides": {
      "@jupyterlab/apputils-extension:themes": {
        "theme": "JupyterLab Dark",
        "preferred-dark-theme": "JupyterLab Dark",
        "scrollbarMode": "simple"
      },
      "@jupyterlab/notebook-extension:tracker": {
        "codeCellConfig": {
          "autoClosingBrackets": true,
          "lineNumbers": true
        }
      }
    }
  }
}
```

### 联邦扩展（federated_extensions）

加载预编译的JupyterLab扩展：

```json
{
  "jupyter-config-data": {
    "federated_extensions": [
      {
        "name": "@jupyter-widgets/jupyterlab-manager",
        "load": "static/ipywidgets.js",
        "extension": true
      }
    ]
  }
}
```

## 完整配置示例

```json
{
  "jupyter-lite-schema-version": 0,
  "jupyter-config-data": {
    "appName": "My Python Sandbox",
    "appUrl": "/lab",
    "baseUrl": "/",
    "defaultKernelName": "python",
    "disabledExtensions": [
      "@jupyterlab/extensionmanager-extension"
    ],
    "settingsOverrides": {
      "@jupyterlab/apputils-extension:themes": {
        "theme": "JupyterLab Light"
      },
      "@jupyterlab/codemirror-extension:commands": {
        "keyMap": "sublime"
      }
    },
    "languagePreference": "zh-CN"
  }
}
```

## Python端配置（LiteBuildConfig）

构建时也可通过CLI参数或 `jupyter_lite_config.json` 配置构建系统：

```json
{
  "LiteBuildConfig": {
    "strict": true,
    "disable_addons": ["serve"],
    "ignore_sys_prefix": true,
    "output_dir": "dist"
  }
}
```

## 不同应用的独立配置

可以为不同应用（lab/notebook/repl）提供不同配置，通过在 `overrides/` 目录放置配置文件：

```
my-jupyterlite/
├── jupyter-lite.json       # 默认配置
├── overrides/
│   ├── lab/
│   │   └── jupyter-lite.json  # Lab专用配置
│   └── repl/
│       └── jupyter-lite.json  # REPL专用配置
└── content/
    └── welcome.ipynb
```

## 相关概念

- [扩展架构](/concepts/08-extension-architecture.md)
- [Python构建系统](/concepts/06-build-system.md)
