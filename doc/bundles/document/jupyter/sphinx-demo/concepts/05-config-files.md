---
type: Concept
title: JupyterLite 四层配置文件体系
description: jupyter_lite_config.json、jupyter-lite.json、overrides.json、try_examples.json 的分层配置模型与使用方式
tags: [configuration, json, jupyter-lite.json, overrides.json, try_examples.json]
difficulty: intermediate
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: json-configs
    resource: /references/json-config-source.md
    title: JSON 配置文件源码
---

## 四层配置模型

JupyterLite Sphinx 集成涉及四个 JSON 配置文件，它们分别管控不同层面的行为。理解这四层配置的分工是正确定制 JupyterLite 站点的关键。

```
┌──────────────────────────────────────────────────────┐
│  Layer 1: conf.py (Sphinx 层)                         │
│  jupyterlite_contents, strip_tagged_cells,           │
│  global_enable_try_examples, ...                     │
├──────────────────────────────────────────────────────┤
│  Layer 2: jupyter_lite_config.json (构建时)           │
│  no_sourcemaps, LiteBuildConfig 设置                  │
├──────────────────────────────────────────────────────┤
│  Layer 3: jupyter-lite.json (运行时基础配置)           │
│  appName, defaultKernelName, faviconUrl              │
├──────────────────────────────────────────────────────┤
│  Layer 4: overrides.json (JupyterLab 插件配置)        │
│  工具栏按钮、插件默认值覆盖                             │
├──────────────────────────────────────────────────────┤
│  Layer 5: try_examples.json (TryExamples 热更新)      │
│  iframe 高度、页面忽略规则                              │
└──────────────────────────────────────────────────────┘
```

conf.py 是 Sphinx 层面的配置，其余四个 JSON 文件控制 JupyterLite 本身的行为。

## 第一层：jupyter_lite_config.json（构建时）

此文件配置 JupyterLite CLI 的构建行为，等价于命令行参数。

```json
{
  "LiteBuildConfig": {
    "no_sourcemaps": true
  }
}
```

**作用时机**：执行 `jupyter lite build`（由 Sphinx 在 `make html` 时自动调用）时读取。

**修改后需要**：重新执行 `make html`。

demo 中仅设置 `no_sourcemaps: true` 来减小产物体积。其他常用选项包括：
- `output_dir`：构建输出目录
- `apps`：要构建的 JupyterLite 应用列表（lab、notebook、repl、retro）
- `source_date_epoch`：可重现构建的时间戳

## 第二层：jupyter-lite.json（运行时基础配置）

此文件配置 JupyterLite 前端应用的基本行为。

```json
{
  "jupyter-lite-schema-version": 0,
  "jupyter-config-data": {
    "appName": "My JupyterLite Docs",
    "defaultKernelName": "python",
    "faviconUrl": "./lab/favicon.ico"
  }
}
```

**作用时机**：浏览器加载 JupyterLite 时读取。

**修改后需要**：重新执行 `make html`（构建时被复制到输出目录）。

### 关键字段

| 字段 | 说明 | Pyodide 示例 | Xeus 示例 |
|------|------|-------------|-----------|
| `appName` | JupyterLab 标题栏和浏览器标签页显示的名称 | "jupyterlite-sphinx-demo (Pyodide)" | "jupyterlite-sphinx-demo (Xeus)" |
| `defaultKernelName` | 默认启动的内核 | `"python"` | `"XPython"` |
| `faviconUrl` | 浏览器标签页图标 | `"./lab/favicon.ico"` | `"./lab/favicon.ico"` |

> **注意**：Pyodide 和 Xeus 的 `defaultKernelName` 不同。使用错误的内核名会导致 JupyterLite 启动失败。

## 第三层：overrides.json（插件配置）

此文件覆盖 JupyterLab 扩展的默认设置，相当于 JupyterLab 中的 Settings → Overrides。

demo 用它在 Notebook 工具栏中添加 Download 按钮：

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

**作用时机**：JupyterLab 加载插件时读取。

**修改后需要**：重新执行 `make html`。

通过 overrides.json，你可以：
- 添加/移除工具栏按钮
- 修改插件默认值
- 配置主题设置
- 自定义命令面板

## 第四层：try_examples.json（热更新配置）

```json
{
  "global_min_height": "400px",
  "ignore_patterns": ["disabled_examples\\/demo.html"]
}
```

**这是四个 JSON 配置中唯一支持热更新的文件**。前端 JavaScript 在每次页面加载时通过 fetch 请求获取此文件（带时间戳参数防缓存），因此：

- **修改后不需要重新构建 Sphinx 文档**
- 部署后可以直接在服务器上修改此文件
- 用户刷新页面即可看到变更

### 配置字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `global_min_height` | string (CSS) | TryExamples iframe 的最小高度，如 `"400px"`、`"50vh"` |
| `ignore_patterns` | string[] | 正则表达式数组，匹配的页面 URL 路径不显示 TryExamples 按钮 |

`ignore_patterns` 使用正则匹配，注意转义特殊字符（如 `/` 需要写成 `\\/`）。

## 配置文件放置位置

默认情况下，所有四个 JSON 文件应放在 Sphinx 源目录（`conf.py` 同级）：

```
docs/source/
├── conf.py
├── jupyter-lite.json          ← 自动发现
├── jupyter_lite_config.json   ← 自动发现
├── overrides.json             ← 自动发现
└── try_examples.json          ← 自动发现
```

也可以在 conf.py 中显式指定路径：

```python
jupyterlite_config = "config/jupyter_lite_config.json"
jupyterlite_overrides = "config/overrides.json"
```

## 完整字段参考

所有 JSON 配置文件的完整字段列表见 [/references/json-config-source.md](/references/json-config-source.md)。

## 相关内容

- [03-sphinx-conf](/concepts/03-sphinx-conf.md)
- [06-try-examples](/concepts/06-try-examples.md)
- [10-disabling-examples](/concepts/10-disabling-examples.md)
- [/references/json-config-source.md](/references/json-config-source.md)
