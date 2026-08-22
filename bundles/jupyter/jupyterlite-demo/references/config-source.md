---
type: Reference
title: JupyterLite 站点配置信源
description: jupyter-lite.json 配置文件结构、字段含义、可用配置项登记
tags: [config, jupyter-lite.json, configuration, disabledExtensions, schema]
source_type: json-config
source_path: repl/jupyter-lite.json
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T18:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: config
    resource: https://github.com/jupyterlite/demo/blob/main/repl/jupyter-lite.json
    title: jupyter-lite.json
---

## 配置文件位置

配置文件位于 `repl/jupyter-lite.json`，在构建时被 JupyterLite CLI 自动发现并嵌入到生成的静态站点中。

## 配置文件结构

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

## 顶级字段

| 字段 | 类型 | Demo 值 | 说明 |
|------|------|---------|------|
| jupyter-lite-schema-version | number | 0 | 配置 schema 版本号 |
| jupyter-config-data | object | (见下) | Jupyter 前端配置数据 |

## jupyter-config-data 常用配置项

| 配置项 | 类型 | Demo 是否使用 | 说明 |
|--------|------|:---:|------|
| disabledExtensions | string[] | ✅ | 禁用的 JupyterLab 扩展 ID 列表 |
| appName | string | ❌ | 应用名称（默认 "JupyterLite"） |
| appVersion | string | ❌ | 应用版本字符串 |
| baseUrl | string | ❌ | 站点 base URL（部署到子路径时设置） |
| defaultKernel | string | ❌ | 默认内核名称 |
| settingsOverrides | object | ❌ | JupyterLab 插件设置覆盖 |
| enableMemoryStorage | boolean | ❌ | 是否启用内存存储（不持久化） |
| litePluginSettings | object | ❌ | JupyterLite 插件设置 |

## disabledExtensions 配置说明

该数组列出需要在站点加载时禁用的 JupyterLab 扩展 ID。Demo 中禁用三个扩展：

1. **@jupyterlab/drawio-extension**：draw.io 图表编辑器，Demo 不需要此功能
2. **jupyterlab-kernel-spy**：内核间谍/监控工具，面向开发者
3. **jupyterlab-tour**：引导式教程功能，存在已知兼容性问题

## 配置文件放置位置

| 位置 | 用途 |
|------|------|
| `repl/jupyter-lite.json` | REPL 应用（/repl 路径）配置 |
| `lab/jupyter-lite.json` | JupyterLab 应用（/lab 路径）配置 |
| `tree/jupyter-lite.json` | 文件树页面配置 |
| `jupyter-lite.json`（根目录） | 全局默认配置 |

Demo 仅在 `repl/` 子目录放置了配置文件，其他应用使用默认配置。
