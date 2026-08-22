---
type: Concept
title: "工作区布局与交互体验设计"
description: "解析 JupyterLab 的 Dock Panel 布局系统、工作区保存/导入机制、workspace.json 配置，以及如何为演示场景设计最优的界面布局"
tags: [workspace, layout, dock-panel, lumino, workspaces, single-document-mode, UX]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:25:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: binder, resource: "/references/binder-config-source.md", title: "Binder配置信源" }
  - { id: narrative, resource: "/references/narrative-source.md", title: "Narrative演示脚本信源" }
---

# 工作区布局与交互体验设计

JupyterLab 的界面布局系统基于 [Lumino](https://github.com/jupyterlab/lumino)（前身为 PhosphorJS）的 Dock Panel 组件，提供了类似桌面 IDE 的灵活面板管理能力。jupyterlab-demo 通过 workspace.json 预设演示布局，让用户点击 Binder 链接即可看到精心设计的界面。

## Lumino Dock Panel 布局模型

JupyterLab 的主工作区是一个 Dock Panel，采用递归分割的布局模型：

### 核心概念

| 概念 | 说明 |
|------|------|
| **Widget** | 面板中的一个可显示组件（Notebook、Console、编辑器、终端等） |
| **Tab Area** | 标签页区域，包含一组可切换的 Widget |
| **Split Area** | 分割区域，将空间分为多个子区域（水平/垂直方向） |
| **Dock Panel** | 根容器，包含整个标签/分割布局树 |

### 布局树结构

workspace.json 中的布局定义采用嵌套的树形结构：

```json
{
  "main": {
    "dock": {
      "type": "split-area",
      "orientation": "horizontal",
      "sizes": [0.5, 0.5],
      "children": [
        {
          "type": "tab-area",
          "currentIndex": 0,
          "widgets": ["notebook:demo/Lorenz.ipynb"]
        },
        {
          "type": "tab-area",
          "widgets": ["help-doc:https://jupyterlab.readthedocs.io/en/stable/"]
        }
      ],
      "current": "help-doc:https://jupyterlab.readthedocs.io/en/stable/"
    }
  }
}
```

这表示：主区域水平分割为两半（50%/50%），左侧是 Lorenz Notebook，右侧是 JupyterLab 文档。

### 边栏布局

```json
{
  "left": {
    "collapsed": false,
    "current": "filebrowser",
    "widgets": ["filebrowser", "running-sessions", "@jupyterlab/toc:plugin", "extensionmanager.main-view"]
  },
  "right": {
    "collapsed": true,
    "widgets": ["jp-property-inspector", "debugger-sidebar"]
  },
  "down": {
    "size": 0,
    "widgets": []
  }
}
```

| 边栏 | 状态 | 包含面板 |
|------|------|---------|
| 左侧 | 展开 | 文件浏览器、运行会话、目录（TOC）、扩展管理器 |
| 右侧 | 折叠 | 属性检查器、调试器侧边栏 |
| 底部 | 隐藏（size=0） | 无（通常用于日志/终端） |

## workspace.json 配置详解

### 整体布局

jupyterlab-demo 的 workspace.json 预设了以下布局：

```
┌─────────────────────────────────────────────────────────┐
│ 菜单/工具栏                                               │
├──────┬──────────────────────────────────────────────────┤
│      │  ┌───────────────────┬───────────────────────┐   │
│ 文件  │  │                   │                       │   │
│ 浏览器 │  │   Lorenz.ipynb   │  JupyterLab 文档       │   │
│      │  │   (Notebook)      │  (帮助文档)            │   │
│ 运行  │  │                   │                       │   │
│ 会话  │  │      50%          │         50%           │   │
│      │  │                   │                       │   │
│ 目录  │  └───────────────────┴───────────────────────┘   │
│      │                                                   │
│ 扩展  │                                                   │
│ 管理器 │                                                   │
├──────┴──────────────────────────────────────────────────┤
│ 状态栏                                                   │
└─────────────────────────────────────────────────────────┘
```

### 各面板的相对尺寸

```json
"relativeSizes": [0.1519, 0.8481, 0]
```

这对应：
- 左侧边栏：约15.2%
- 主区域：约84.8%
- 底部区域：0%（隐藏）

### Widget ID 命名规则

workspace.json 中的 widgets 使用特定的 ID 格式引用：

| 格式 | 示例 | 说明 |
|------|------|------|
| `notebook:<path>` | `notebook:demo/Lorenz.ipynb` | 指定路径的 Notebook |
| `help-doc:<url>` | `help-doc:https://...` | 帮助文档面板 |
| `filebrowser` | `filebrowser` | 内置面板的固定ID |
| `running-sessions` | `running-sessions` | 运行会话面板 |
| `@jupyterlab/toc:plugin` | `@jupyterlab/toc:plugin` | 扩展面板（插件ID） |
| `extensionmanager.main-view` | `extensionmanager.main-view` | 扩展管理器 |

### 文件浏览器初始路径

```json
"file-browser-filebrowser:cwd": {
  "path": "demo"
}
```

这确保用户打开 JupyterLab 时，文件浏览器自动定位到 `demo/` 目录，所有演示材料立即可见。

### Notebook 的工厂配置

```json
"notebook:demo/Lorenz.ipynb": {
  "data": {
    "path": "demo/Lorenz.ipynb",
    "factory": "Notebook"
  }
}
```

`factory: "Notebook"` 指定使用 Notebook 工厂（而非 JSON 编辑器或文本编辑器）打开这个文件。这确保 .ipynb 文件以 Notebook 形式打开。

## 演示布局的设计考量

为什么选择"Notebook + 文档"左右分屏？

### 1. 边学边练模式

- 左侧：可以运行和修改代码（动手实践）
- 右侧：可以查阅文档（获取知识）
- 不需要在标签页间切换，降低认知负担

### 2. 视觉焦点明确

- Lorenz 吸引子的 3D 图形视觉冲击力强，第一印象好
- 官方文档提供权威参考，演示者可以随时展示功能说明

### 3. 面板选择的理由

**左侧面板展开**：
- 文件浏览器是演示中最频繁使用的（打开不同文件）
- TOC（目录）展示文档导航能力
- 扩展管理器展示 JupyterLab 的可扩展性
- 运行会话面板展示内核/终端管理

**右侧面板折叠**：
- 属性检查器和调试器在演示中不常用
- 折叠它们给主区域更多空间
- 需要时可以展开

**底部面板隐藏**：
- 底部通常放日志，演示场景不需要

## 交互模式

### 单文档模式（Single Document Mode）

演示脚本中多次提到"单文档模式"：
- 快捷键：Shift+Cmd+Enter（Mac）或通过 View 菜单切换
- 效果：聚焦当前活动标签页，隐藏其他面板
- 用途：当需要专注于一个 Notebook 或文档时

单文档模式在工作区布局中的切换是即时的，不会丢失布局状态——切回后恢复原来的分屏。

### 标签页管理

- 标签页拖拽重排
- 拖拽标签到边缘可创建新的分屏区域
- 右键标签页菜单：
  - "Create New View for Output"：为输出创建新视图（dashboard 原型）
  - "Open With"：选择其他查看器打开
  - 关闭标签页

### 拖放布局

Dock Panel 支持通过鼠标拖拽自由调整布局：
- 拖拽标签到面板边缘（上/下/左/右）可分割区域
- 拖拽标签到其他标签区域可合并
- 拖拽分割线可调整各区域大小比例

这种灵活性让高级用户可以自定义工作空间，但对演示来说，预设好布局避免了现场调整的尴尬。

## 工作区的保存与导入

### 导出工作区

在 JupyterLab 中，通过命令导出当前布局：

```bash
jupyter lab workspaces export default > workspace.json
```

这会将当前工作区的完整布局（包括打开的文件、面板位置、边栏状态）导出为 JSON 文件。

### 导入工作区

postBuild 中使用的命令：

```bash
conda run -n notebook jupyter lab workspaces import .binder/workspace.json
```

**注意事项**：
- 必须在正确的 Conda 环境中运行（`conda run -n notebook`）
- 否则工作区会导入到用户的 home 目录而非环境路径
- 这也是 postBuild 中使用 `conda run` 的原因

### 工作区的存储位置

JupyterLab 工作区存储在：
- 非Binder环境：`~/.jupyter/lab/workspaces/`
- Binder环境：在 Conda 环境的 Jupyter 配置目录中

工作区通过 URL 参数访问：
- 默认工作区：`/lab`
- 命名工作区：`/lab/workspaces/<name>`

## 创建你自己的演示布局

如果你想为自己的项目创建类似的预设布局：

1. **手动布局**：在 JupyterLab 中打开需要的文件，排列好布局
2. **导出配置**：运行 `jupyter lab workspaces export default > my-workspace.json`
3. **清理无关项**：删除不需要的 widget 条目，保留核心布局
4. **放入 Binder**：将文件放在 `.binder/workspace.json`
5. **添加导入步骤**：在 `postBuild` 中添加 `jupyter lab workspaces import` 命令
6. **测试验证**：通过 Binder 链接打开，确认布局正确

## 相关概念

- [Binder 环境配置三要素](/concepts/02-binder-config.md)
- [演示能力维度与多内核支持](/concepts/04-demo-capabilities.md)
- [插件架构与扩展生态](/concepts/08-extension-demo.md)
- [实战：添加自己的演示内容](/examples/04-add-demo-content.md)
