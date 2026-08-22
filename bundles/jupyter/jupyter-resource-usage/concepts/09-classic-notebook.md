---
type: Concept
title: 经典Notebook支持
description: _jupyter_nbextension_paths扩展钩子、nbextension静态资源目录结构、RequireJS加载机制、MemoryUsage模块注册、与JupyterLab前端的兼容性
tags: [jupyter-resource-usage, nbextension, classic-notebook, requirejs, nbclassic]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T14:40:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T14:40:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: source-code
    resource: /references/source-code.md
---

# 经典Notebook支持

jupyter-resource-usage 同时支持 JupyterLab 和经典 Jupyter Notebook（Notebook 7.x、nbclassic）。经典Notebook使用不同的前端扩展机制（nbextension），与JupyterLab的labextension完全分离。

## 扩展钩子

`__init__.py` 中定义了经典Notebook的入口点：

```python
def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'static',
        'dest': 'jupyter-resource-usage',
        'require': 'jupyter-resource-usage/index'
    }]
```

| 字段 | 值 | 说明 |
|------|-----|------|
| `section` | `'notebook'` | 注册到notebook区域（而非tree/edit） |
| `src` | `'static'` | Python包内的静态资源目录 |
| `dest` | `'jupyter-resource-usage'` | 目标nbextension目录名 |
| `require` | `'jupyter-resource-usage/index'` | RequireJS模块路径，指向主入口JS |

## 静态资源目录结构

nbextension资源位于Python包的 `static/` 目录（`jupyter_resource_usage/static/`）：

```
jupyter_resource_usage/static/
├── base.css           # 内存指示器CSS样式
├── d3.v3.min.js       # D3.js v3（用于SVG图标渲染）
├── memoryusagetext.js # 主模块：文本显示+轮询
└── memoryusage.js     # 备用模块：SVG图表版本
```

## memoryusagetext.js：文本显示模块

这是默认的nbextension模块，以纯文本形式在经典Notebook页面右上角显示内存使用量：

### RequireJS模块定义

```javascript
define([
    'base/js/namespace',
    'base/js/events',
    'base/js/utils',
    'require',
], function(Jupyter, events, utils, require) {
    'use strict';
    let displayMetrics = false;
    let metricPrefix;
    
    const load_ipython_extension = () => {
        $('<div/>')
            .attr('id', 'notification_memory')
            .css({'padding': '2px 5px'})
            .addClass('label')
            .appendTo('#header_container');
        updateMemoryUsage();
    };
    
    const mib = 1024 * 1024;
    const gib = mib * 1024;
    const tib = gib * 1024;
    
    function updateMemoryUsage() {
        // 调用/api/metrics/v1
        // 格式化显示为XX.XX GiB/MiB
    }
    
    return {
        load_ipython_extension: load_ipython_extension,
    };
});
```

### 显示逻辑

- 在页面顶部 `#header_container` 添加 `#notification_memory` div
- 每5秒轮询一次 `/api/metrics/v1`
- 使用 `setTimeout` 递归实现轮询（非setInterval）
- 单位转换：MiB/GiB/TiB 自动选择
- 警告时添加红色标签样式

### CSS样式（base.css）

```css
/* 内存指示器标签样式 */
#notification_memory {
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 13px;
    color: #777;
}
#notification_memory.label {
    color: #fff;
}
#notification_memory.label-warning {
    background-color: #f0ad4e;
}
```

警告时使用Bootstrap的 `label-warning` 橙色标签（而非JupyterLab的红底红字）。

## memoryusage.js：SVG图表版本

这是一个使用D3.js v3绘制SVG内存使用图表的替代模块，功能更丰富但默认不启用。需要修改 `require` 字段指向此模块才能使用。

它会在Notebook页脚绘制一个小型SVG内存使用趋势图。

## 与JupyterLab前端的关系

| 特性 | labextension (JupyterLab/Notebook7) | nbextension (经典Notebook) |
|------|-------------------------------------|---------------------------|
| 位置 | `packages/labextension/` | `jupyter_resource_usage/static/` |
| 技术栈 | TypeScript + React + Lumino | JavaScript + jQuery + RequireJS |
| 构建工具 | jupyter labextension build (webpack) | 无构建（直接部署JS/CSS） |
| 功能 | 状态栏+顶栏+内核侧边栏 | 仅内存文本显示 |
| CPU/磁盘 | 支持（需配置） | 不支持 |
| 图标库 | JupyterLab Icon Registry | D3.js v3 SVG |
| 启用方式 | pip install自动启用 | `nbextension enable` |
| 依赖 | @jupyterlab/* npm包 | base/js/* RequireJS模块 |

## 自动启用机制

安装时通过 `explicit-install` 标记自动启用，用户无需手动执行 `jupyter nbextension enable`：

```python
# pyproject.toml
[tool.hatch.build.targets.wheel.shared-data]
"jupyter-config/nbconfig/notebook.d/jupyter-resource-usage.json" = "etc/jupyter/nbconfig/notebook.d/jupyter-resource-usage.json"
```

配置文件（`jupyter-config/nbconfig/notebook.d/jupyter-resource-usage.json`）中声明nbextension加载：

```json
{
    "load_extensions": {
        "jupyter-resource-usage/index": true
    }
}
```

## Notebook 7兼容

Notebook 7基于JupyterLab 4.x构建，因此自动使用labextension（TypeScript/React前端），不需要nbextension。`_jupyter_nbextension_paths()` 仅对经典Notebook（nbclassic）和Notebook <7生效。

代码中的兼容性检测：

```typescript
if (labShell) {
    // JupyterLab或Notebook7环境，使用ILabShell
} else {
    // 经典Notebook环境，使用INotebookTracker+IConsoleTracker
}
```

labextension的三个插件（status/topbar/kernel-panel）都包含了对notebookTracker/consoleTracker的可选依赖，确保在没有ILabShell时也能工作。

## 相关概念

- [简介与功能概述](00-introduction.md) — 支持的Jupyter版本
- [安装与启用](01-installation.md) — nbextension启用命令
- [架构总览](02-architecture.md) — 前后端扩展钩子
