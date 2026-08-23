---
type: Reference
title: JSON 配置文件字段速查
description: jupyter-lite.json、jupyter_lite_config.json、overrides.json、try_examples.json 四个 JSON 配置文件的字段完整登记
tags: [json, configuration, jupyter-lite.json, jupyter_lite_config.json, overrides.json, try_examples.json]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: pyodide-configs
    resource: /references/json-config-source.md
    title: Pyodide 示例配置文件
  - id: xeus-configs
    resource: /references/json-config-source.md
    title: Xeus 示例配置文件
---

## JSON 配置文件字段速查

本信源文档登记 sphinx-demo 中使用的四个 JupyterLite JSON 配置文件的所有字段。

## jupyter-lite.json（运行时配置）

此文件在 Sphinx 构建时被复制到 JupyterLite 输出目录，控制浏览器端运行时行为。

```json
{
  "jupyter-lite-schema-version": 0,
  "jupyter-config-data": {
    "appName": "...",
    "defaultKernelName": "...",
    "faviconUrl": "./lab/favicon.ico"
  }
}
```

| 字段路径 | Pyodide 取值 | Xeus 取值 | 说明 |
|----------|-------------|-----------|------|
| `jupyter-lite-schema-version` | `0` | `0` | Schema 版本号 |
| `jupyter-config-data.appName` | `"jupyterlite-sphinx-demo (Pyodide)"` | `"jupyterlite-sphinx-demo (Xeus)"` | JupyterLab 应用标题（显示在浏览器标签页） |
| `jupyter-config-data.defaultKernelName` | `"python"` | `"XPython"` | 默认内核名称（Pyodide 为 "python"，Xeus Python 为 "XPython"） |
| `jupyter-config-data.faviconUrl` | `"./lab/favicon.ico"` | `"./lab/favicon.ico"` | Favicon 路径（相对于 lite 目录） |

## jupyter_lite_config.json（构建时配置）

此文件控制 JupyterLite CLI 构建阶段的行为。

```json
{
  "LiteBuildConfig": {
    "no_sourcemaps": true
  }
}
```

| 字段路径 | 取值 | 说明 |
|----------|------|------|
| `LiteBuildConfig.no_sourcemaps` | `true` | 禁用 source map 生成 |

> **注意**：此文件的配置是构建时的，修改后需要重新执行 `make html` 才能生效。这与 try_examples.json 不同。

## overrides.json（JupyterLab 插件覆盖配置）

此文件用于覆盖 JupyterLab 扩展的默认设置，相当于 JupyterLab 的 `overrides.json`。

```json
{
  "@jupyterlab/notebook-extension:panel": {
    "toolbar": [
      {
        "name": "download",
        "label": "Download",
        "args": {},
        "command": "docmanager:download",
        "icon": "ui-components:download",
        "rank": 50
      }
    ]
  }
}
```

| 字段路径 | 取值 | 说明 |
|----------|------|------|
| `@jupyterlab/notebook-extension:panel.toolbar` | 包含一个 Download 按钮项的数组 | 向 Notebook 面板工具栏添加按钮 |
| `toolbar[].name` | `"download"` | 按钮唯一标识 |
| `toolbar[].label` | `"Download"` | 按钮显示文本 |
| `toolbar[].command` | `"docmanager:download"` | 点击时执行的 JupyterLab 命令 ID |
| `toolbar[].icon` | `"ui-components:download"` | 图标（使用 JupyterLab UI 组件图标） |
| `toolbar[].rank` | `50` | 按钮在工具栏中的排序位置 |

## try_examples.json（TryExamples 交互配置）

此文件控制 TryExamples 按钮和 iframe 的运行时行为，由前端 JS 热加载。

```json
{
  "global_min_height": "400px",
  "ignore_patterns": ["disabled_examples\\/demo.html"]
}
```

| 字段 | 类型 | 取值 | 说明 |
|------|------|------|------|
| `global_min_height` | `string` | `"400px"` | TryExamples iframe 的最小高度（CSS 长度值） |
| `ignore_patterns` | `array[string]` | `["disabled_examples\\/demo.html"]` | 正则表达式数组，匹配的页面不显示 TryExamples 按钮 |

> **热加载特性**：try_examples.json 由前端 JavaScript 在页面加载时通过 fetch 获取（带时间戳参数防缓存），因此部署后修改此文件不需要重新构建 Sphinx 文档。这是四个 JSON 配置中唯一支持热更新的。

## 四个配置文件对比

| 配置文件 | 作用阶段 | 修改后是否需要重建 | 典型配置内容 |
|----------|---------|:---:|------------|
| `jupyter_lite_config.json` | 构建时 | ✅ 是 | sourcemaps、输出目录、app 列表 |
| `jupyter-lite.json` | 运行时 | ✅ 是（构建时复制） | appName、内核名、favicon |
| `overrides.json` | 运行时 | ✅ 是（构建时复制） | JupyterLab 插件设置、工具栏 |
| `try_examples.json` | 运行时 | ❌ 否（前端热加载） | iframe 高度、页面忽略规则 |

## 相关概念

- [05-config-files](/concepts/05-config-files.md)
- [03-sphinx-conf](/concepts/03-sphinx-conf.md)
- [/references/conf-py-source.md](/references/conf-py-source.md)
