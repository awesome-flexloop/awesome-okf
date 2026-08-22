---
type: Concept
title: 十种内置 Scenario 场景
description: 详解jupyterlab-ui-profiler的10种内置Scenario场景：菜单操作、标签页切换、侧边栏、代码补全、滚动、调试器、创建单元格、自定义命令序列的配置和使用
tags: [jupyterlab, ui-profiler, scenario, menu, tab, sidebar, completer, scroll, debugger]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:40:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T13:40:00Z" }
status: stable
stale_after: "2027-02-22"
sources:
  - id: scenarios-ts
    resource: /references/scenarios-source.md
    title: src/scenarios.ts 所有Scenario实现
---

## Scenario 概览

Scenario定义了"测什么操作"。ui-profiler内置10种Scenario，覆盖JupyterLab最常见的用户交互：

| ID | 名称 | 类型 | 是否需要Notebook | 配置复杂度 |
|----|------|------|-----------------|-----------|
| `menuOpen` | Open Menu | 菜单操作 | 否 | ⭐ |
| `menuSwitch` | Switch Menu | 菜单操作 | 否 | ⭐ |
| `tabSwitch` | Switch Tabs | 标签页 | 否 | ⭐⭐ |
| `tabSwitchFocus` | Switch Tab Focus | 标签页 | 否 | ⭐⭐ |
| `sidebarOpen` | Open Sidebar | 侧边栏 | 否 | ⭐ |
| `completer` | Completer | 代码补全 | 可选 | ⭐⭐⭐ |
| `scroll` | Scroll | 滚动 | 可选 | ⭐⭐ |
| `debugger` | Debugger | 调试器 | 是 | ⭐⭐⭐ |
| `create-cells` | Create cells | 单元格 | 是 | ⭐⭐ |
| `custom` | Custom Scenario | 自定义 | 按需 | ⭐⭐⭐⭐ |

## MenuOpenScenario - 打开菜单

**ID**: `menuOpen`
**文件**: src/scenarios.ts:L76-L93

测量打开单个主菜单的响应时间。

### 配置选项

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `menu` | string | `'file'` | 菜单名：file/edit/view/run/kernel/settings/help |

### 执行流程

1. `run()`: 执行 `${menu}menu:open` 命令，等待 `#jp-mainmenu-${menu}` 元素attached，等待layoutReady
2. `cleanup()`: 等待 `.lm-Menu` attached → 按Escape键关闭 → 等待菜单detached → layoutReady

### 使用场景

- 测量菜单打开延迟
- 对比不同菜单的打开速度
- CSS Rule Usage场景：发现哪些CSS规则影响菜单渲染

## MenuSwitchScenario - 切换菜单

**ID**: `menuSwitch`
**文件**: src/scenarios.ts:L59-L74

测量在已打开的菜单间切换的性能。

### 执行流程

1. `setup()`: 先打开file菜单
2. `run()`: 依次切换到edit→view→run→kernel→settings→help共6个菜单
3. `cleanup()`: 按Escape关闭最后一个菜单

与MenuOpenScenario的区别：MenuSwitch从已打开的菜单开始，测量菜单切换（横向移动）的性能，而不是从无到有打开菜单。

## SwitchTabScenario - 切换标签页

**ID**: `tabSwitch`
**文件**: src/scenarios.ts:L700-L769

测量在多个标签页间切换的性能。

### 配置选项

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `tabs` | Tab[] | 必填 | 标签页配置数组 |

每个Tab对象：
```typescript
{
  path?: string;  // 文件路径（如notebook.ipynb），不填则创建launcher
}
```

### Split模式

SwitchTabScenario默认 `split: 'first'`，即第一个标签使用split-right模式添加，后续标签添加到已有区域。

### 执行流程

1. `setupSuite()`: 为每个tab：
   - 有path → `docmanager:open` 打开文件
   - 无path → `launcher:create` 创建launcher
   - 第一个（split='first'）以split-right添加到shell
   - 等待widget attached，notebook等待Spinner消失
   - activateTabWidget激活标签
2. `run()`: 依次激活每个widget的标签（通过`tabsmenu:activate-by-id`命令）
3. `cleanupSuite()`: 关闭所有widget

## SwitchTabFocusScenario - 切换标签焦点

**ID**: `tabSwitchFocus`
**文件**: src/scenarios.ts:L771-L775

继承自SwitchTabScenario，唯一区别是 `split: 'all'`——所有标签都以split-right模式并排显示。

这模拟了多面板分屏场景下的标签切换（如Notebook和Console并排），比单区域标签切换更复杂。

## SidebarOpenScenario - 打开侧边栏

**ID**: `sidebarOpen`
**文件**: src/scenarios.ts:L106-L134

测量打开侧边栏面板的性能。

### 配置选项

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `sidebars` | string[] | `['filebrowser']` | 要打开的侧边栏widget ID数组 |

常用侧边栏ID：
- `filebrowser` - 文件浏览器
- `jp-running-sessions` - 运行中的终端和内核
- `jp-property-inspector` - 属性检查器
- `jp-debugger-sidebar` - 调试器面板
- `jp-table-of-contents` - 目录
- `jp-extensionmanager` - 扩展管理器

### 执行流程

1. `setup()`: `closeSidebars()` 关闭所有已打开的侧边栏
2. `run()`: 逐个调用`shell.activateById(sidebar)`，等待对应面板visible
3. 无独立cleanup（下一次setup会关闭）

closeSidebars()辅助函数检查`#jp-left-stack`/`#jp-right-stack`是否有`lm-mod-hidden`类，如果可见则toggle关闭。

## SingleEditorScenario 基类

**文件**: src/scenarios.ts:L157-L233

CompleterScenario、ScrollScenario、CreateCellsScenario、DebuggerScenario都继承自此类，共享编辑器创建和管理逻辑。

### 关键功能

**setupSuite()**：
1. 如果未指定path，创建新文件（notebook或.py文件）
2. `docmanager:open`打开widget
3. 添加到shell（默认split-right模式）
4. 激活标签，Notebook需点击kernel对话框的accept按钮
5. 等待 `.jp-Editor` visible
6. 定位editor元素：`.jp-Notebook`（Notebook模式）或 `.jp-FileEditorCodeWrapper`（文件编辑器模式）

**cleanupSuite()**：保存文档 → 关闭widget

**编辑器兼容**：同时支持CodeMirror 5（`.CodeMirror-scroll`）和CodeMirror 6（`.cm-scroller`、`.cm-content`）。

## CompleterScenario - 代码补全

**ID**: `completer`
**文件**: src/scenarios.ts:L235-L338

测量代码补全（自动完成）弹出的性能。这是最复杂的Scenario之一。

### 配置选项

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `editor` | string | `'Notebook'` | 'Notebook' 或 'Editor'（文件编辑器） |
| `setup.tokenCount` | number | 100 | 预填充的token变量数量 |
| `setup.tokenSize` | number | 10 | 每个token名的长度 |
| `setup.setupText` | string | - | 自定义预填充文本（覆盖tokenCount/tokenSize） |
| `setup.setupCell` | string | - | Notebook模式下预先运行的cell代码 |
| `path` | string | - | 自定义文件路径 |
| `widgetPosition` | string | `'split-right'` | widget添加位置 |

### 执行流程

1. `setupSuite()`（在父类基础上额外）：
   - 插入N个token变量定义（`t0xx = 0`, `t1xx = 1`, ...），变量名padded到tokenSize长度
   - 如果有setupCell，先运行该cell再插入tokens
   - 对于File Editor，需要滚动一点避免out-of-view bug
   - **预运行一次**（first run is flaky）然后cleanup消除warm-up效应
2. `run()`:
   - 聚焦编辑器（CM5/CM6兼容处理）
   - Notebook执行`completer:invoke-notebook`，File Editor执行`completer:invoke-file`
   - 等待 `.jp-Completer.jp-HoverBox[style]` attached和visible（必须有style属性以区分残留的completer）
3. `cleanup()`: 按Escape关闭补全

### 关键细节

- 选择器 `.jp-Completer.jp-HoverBox[style]` 中的 `[style]` 很重要——在JupyterLab 3.x中所有completer都保留在attached状态，只有活跃的completer有程序化设置的style属性（position/top/left/width/height）
- 第一次补全触发通常较慢（JIT编译、缓存填充），setupSuite中预运行一次消除这个偏差

## ScrollScenario - 滚动

**ID**: `scroll`
**文件**: src/scenarios.ts:L628-L698

测量编辑器滚动性能。

### 配置选项

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `editor` | string | `'Notebook'` | 'Notebook' 或 'Editor' |
| `cells` | number | 100 | 预创建的单元格/文本行数 |
| `scrollTop` | number | 5000 | 滚动距离（像素） |
| `scrollBehavior` | string | `'smooth'` | 'smooth' 或 'auto' |
| `cellByCell` | boolean | false | Notebook模式下是否逐cell移动光标（而非连续滚动） |
| `editorContent` | string | - | 自定义每格/每行内容 |

### 执行流程

1. `setupSuite()`（在父类基础上额外）：
   - 插入N个单元格（Notebook）或文本行（File Editor）
   - 每20/50个单元格执行一次layoutReady显示进度
   - 设置 `editor.scrollTop = 0` 回到顶部
2. `run()`:
   - **cellByCell模式**：N次执行`notebook:move-cursor-down`逐cell移动
   - **平滑滚动模式**：`editor.scrollBy({ top: scrollTop, behavior })` → waitForScrollEnd等待滚动停止
3. `cleanup()`: 反向操作回到顶部

### waitForScrollEnd

**文件**: src/dramaturg.ts:L137-L156

使用setInterval轮询（50ms间隔），直到scrollTop和scrollLeft连续两次检查值相同（静止50ms），判定滚动结束。

## DebuggerScenario - 调试器

**ID**: `debugger`
**文件**: src/scenarios.ts:L359-L471

测量调试器操作性能（变量列表更新等）。固定使用Notebook编辑器。

### 配置选项

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `codeCells` | string[] | 必填 | 要执行的代码单元格数组 |
| `expectedNumberOfVariables` | number[] | 必填 | 执行每个cell后期望的变量数 |

### 执行流程

1. `setupSuite()`（在父类基础上额外）：
   - 插入配置的codeCells代码单元格
   - 插入`%reset -f`清理命令作为最后一个cell
   - 回到顶部，等待kernel idle
   - 确保工具栏按钮可见（处理响应式工具栏溢出弹窗）
   - 点击"Enable Debugger"按钮
   - 等待调试器侧边栏和变量列表visible
2. `run()`:
   - 逐个执行codeCells
   - 每个cell后等待kernel idle
   - 如果配置了expectedNumberOfVariables，等待对应数量的变量显示
3. `cleanup()`:
   - 执行`%reset -f`清理变量
   - 等待变量列表清空
   - 回到顶部

### 注意事项

- `setOptions()`强制设置`editor: 'Notebook'`和`path: null`，此Scenario不支持File Editor
- 需要debugger扩展可用且kernel支持调试

## CreateCellsScenario - 创建单元格

**ID**: `create-cells`
**文件**: src/scenarios.ts:L494-L544

测量在Notebook中创建新单元格的性能。

### 配置选项

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `cells` | number | 10 | 创建的单元格数量 |
| `cellType` | string | - | 'code'（默认）/'raw'/'markdown' |
| `editorContent` | string | - | 每个单元格中插入的文本 |

### 执行流程

1. `run()`: 循环N次：
   - `notebook:insert-cell-below` 插入新cell
   - 可选：改变cell类型为raw/markdown
   - 可选：插入editorContent文本
   - layoutReady
2. `cleanup()`: 循环N次`notebook:delete-cell`删除创建的单元格

## CustomScenario - 自定义命令序列

**ID**: `custom`
**文件**: src/scenarios.ts:L546-L626

最灵活的Scenario，允许通过JSON配置任意JupyterLab命令序列，无需写代码。

### 配置选项

| 参数 | 类型 | 说明 |
|------|------|------|
| `setupCommands` | Command[] | 准备阶段执行的命令 |
| `commands` | Command[] | 核心测量操作的命令序列 |
| `cleanupCommands` | Command[] | 清理阶段执行的命令 |

每个Command对象：
```json
{
  "id": "command-id",
  "args": { /* 命令参数 */ }
}
```

### 动态Schema

CustomScenario最强大的特性是**动态生成配置Schema**（L553-L589）：

在`app.restored`后：
1. 获取所有已注册命令ID `app.commands.listCommands()`
2. 对每个命令调用 `app.commands.describedBy(commandId)` 获取参数Schema
3. 动态构建JSON Schema的oneOf，使用户可以从下拉列表选择命令并填写参数
4. 命令的label从`app.commands.label(commandId)`获取

特殊处理：`fileeditor:change-font-size`命令缺少label，手动设置为"Change font size"。

### 执行流程

1. `setupSuite()`: 依次执行setupCommands，每个命令后layoutReady
2. `run()`: 依次执行commands，每个命令后layoutReady
3. `cleanup()`: 依次执行cleanupCommands，每个命令后layoutReady
4. `cleanupSuite()`: 无（cleanupCommands已处理）

### 使用示例

测量切换主题的性能：
```json
{
  "setupCommands": [],
  "commands": [
    { "id": "apputils:change-theme", "args": { "theme": "JupyterLab Dark" } }
  ],
  "cleanupCommands": [
    { "id": "apputils:change-theme", "args": { "theme": "JupyterLab Light" } }
  ]
}
```

## insertText 工具函数

**文件**: src/scenarios.ts:L136-L150

```typescript
export function insertText(jupyterApp: JupyterFrontEnd, text: string): Promise<void> {
  return jupyterApp.commands.execute('apputils:run-first-enabled', {
    commands: [
      'notebook:replace-selection',
      'console:replace-selection',
      'fileeditor:replace-selection'
    ],
    args: { text }
  });
}
```

使用`apputils:run-first-enabled`命令依次尝试三种编辑器的replace-selection，哪个可用就用哪个，自动适配Notebook/Console/File Editor。

## 相关概念

- (01-architecture-overview.md
- (03-benchmarks.md
- (07-dramaturg-automation.md
- (../examples/02-custom-scenario.md
- (../references/scenarios-source.md
