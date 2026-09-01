---
type: Concept
title: 站点配置详解
description: jupyter-lite.json 配置文件的结构、字段含义、扩展管理策略，以及如何定制 JupyterLite 站点行为
tags: [configuration, jupyter-lite.json, disabledExtensions, settings, customization]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T18:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: config
    resource: /references/config-source.md
    title: JupyterLite 站点配置信源
---

## 配置文件位置与发现

JupyterLite 构建时会自动查找配置文件。配置文件可以放在不同目录以控制不同应用：

| 文件路径 | 控制范围 |
|----------|----------|
| `jupyter-lite.json`（根目录） | 全局默认配置，所有应用继承 |
| `lab/jupyter-lite.json` | JupyterLab 应用（/lab 路径） |
| `repl/jupyter-lite.json` | REPL 应用（/repl 路径） |
| `tree/jupyter-lite.json` | 文件浏览器（/tree 路径） |
| `retro/jupyter-lite.json` | RetroLab 应用（如果启用） |

Demo 仓库仅在 `repl/` 目录下放置了配置文件。

## Demo 的配置内容

Demo 使用的配置文件非常精简：

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

### 字段说明

**jupyter-lite-schema-version**

配置 schema 的版本号，当前为 `0`。JupyterLite 构建工具使用此字段验证配置格式兼容性。

**jupyter-config-data**

Jupyter 前端配置数据对象，以下是常用配置项：

### disabledExtensions（禁用扩展）

字符串数组，列出需要在站点加载时禁用的 JupyterLab 扩展 ID：

| 扩展 ID | 功能 | 禁用原因 |
|---------|------|----------|
| `@jupyterlab/drawio-extension` | draw.io 图表编辑器 | Demo 不需要图表编辑功能，减少加载体积 |
| `jupyterlab-kernel-spy` | 内核监控工具 | 面向开发者的调试工具，普通用户不需要 |
| `jupyterlab-tour` | 引导式教程 | 存在已知兼容性 bug（见 jupyterlab-contrib/jupyterlab-tour#82） |

> 💡 **设计哲学**：Demo 的配置策略是「最小化配置」——只禁用已知有问题或不需要的扩展，其余全部走默认值。这体现了 JupyterLite 的约定优于配置（convention over configuration）设计理念。

## 常用高级配置

以下是 jupyter-config-data 中可以使用的其他配置项（Demo 中未使用但实用）：

### 应用信息

```json
{
  "jupyter-config-data": {
    "appName": "My JupyterLite",
    "appVersion": "1.0.0"
  }
}
```

### 默认内核

```json
{
  "jupyter-config-data": {
    "defaultKernel": "python"
  }
}
```

### 禁用存储持久化

```json
{
  "jupyter-config-data": {
    "enableMemoryStorage": true
  }
}
```

设置 `enableMemoryStorage: true` 后，所有文件仅存储在内存中，刷新页面即丢失。适合教学演示和公开站点。

### JupyterLab 设置覆盖

通过 `settingsOverrides` 可以覆盖任意 JupyterLab 插件的设置：

```json
{
  "jupyter-config-data": {
    "settingsOverrides": {
      "@jupyterlab/apputils-extension:themes": {
        "theme": "JupyterLab Dark"
      },
      "@jupyterlab/codemirror-extension:commands": {
        "keyMap": "vim"
      }
    }
  }
}
```

### JupyterLite 插件设置

```json
{
  "jupyter-config-data": {
    "litePluginSettings": {
      "@jupyterlite/pyodide-kernel-extension:kernel": {
        "pyodideUrl": "https://cdn.jsdelivr.net/pyodide/v0.28.0/full/pyodide.js"
      }
    }
  }
}
```

## 多应用差异化配置

如果不同应用需要不同配置，可以在各应用子目录放置独立的配置文件。例如：

- 全局禁用某个扩展 → 在根 `jupyter-lite.json` 配置
- 仅 REPL 禁用某个扩展 → 在 `repl/jupyter-lite.json` 配置
- 仅 Lab 使用特定主题 → 在 `lab/jupyter-lite.json` 配置

配置合并规则：子目录配置会与全局配置深度合并，子目录配置优先级更高。

## 配置验证

构建时 JupyterLite 会验证配置文件的 JSON 格式和 schema 版本。配置错误不会导致构建失败，但会在控制台输出警告。建议在本地构建后访问站点检查配置是否生效。

## 相关概念

- [Demo 仓库结构与三件套模式](01-demo-overview.md)
- [三大内核生态对比](03-kernel-ecosystem.md)
- [自定义 Demo 站点指南](07-customization-guide.md)
- [从零部署到 GitHub Pages](../examples/01-first-deployment.md)
