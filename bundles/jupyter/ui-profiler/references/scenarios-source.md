---
type: Reference
title: Scenario 源码分析参考
description: jupyterlab-ui-profiler 10种内置Scenario的源码实现分析，包含菜单、标签页、侧边栏、补全、滚动、调试器、单元格创建、自定义场景的详细实现
tags: [jupyterlab, ui-profiler, scenario, benchmark, automation, user-interaction]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:40:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T13:40:00Z" }
status: stable
stale_after: "2027-02-22"
sources:
  - id: scenarios-ts
    resource: /references/scenarios-source.md
    title: src/scenarios.ts 所有Scenario实现
  - id: dramaturg-ts
    resource: /references/dramaturg-source.md
    title: src/dramaturg.ts 浏览器自动化层
---

## Scenario 注册机制

**文件**: src/scenarios.ts:L777-L795

所有内置Scenario通过一个独立的JupyterFrontEndPlugin注册：

```typescript
export const plugin: JupyterFrontEndPlugin<void> = {
  id: '@jupyterlab/ui-profiler:default-scenarios',
  autoStart: true,
  requires: [IUIProfiler],
  activate: (app: JupyterFrontEnd, profiler: IUIProfiler) => {
    [
      new MenuOpenScenario(app),
      new MenuSwitchScenario(app),
      new SwitchTabScenario(app),
      new SwitchTabFocusScenario(app),
      new SidebarOpenScenario(app),
      new CompleterScenario(app),
      new ScrollScenario(app),
      new DebuggerScenario(app),
      new CreateCellsScenario(app),
      new CustomScenario(app)
    ].map(scenario => profiler.addScenario(scenario));
  }
};
```

在src/index.ts:L183中作为默认导出的一部分导出：`export default [plugin, scenariosPlugin, interfacePlugin]`。

## MenuOpenScenario - 打开菜单

**文件**: src/scenarios.ts:L76-L93
**ID**: `menuOpen`
**配置**: src/schema/scenario-menu-open.json

构造函数接收JupyterFrontEnd实例，默认打开'file'菜单。通过`setOptions()`可配置`menu`参数（file/edit/view/run/kernel/settings/help）。

执行流程：
- `run()`: 调用 `app.commands.execute('${menu}menu:open')` → 等待 `#jp-mainmenu-${menu}` attached → layoutReady
- `cleanup()`: 等待 `.lm-Menu` attached → 按Escape键 → 等待 `.lm-Menu` detached → layoutReady

## MenuSwitchScenario - 切换菜单

**文件**: src/scenarios.ts:L59-L74
**ID**: `menuSwitch`
**配置**: src/schema/scenario-base.json

依次在已打开的菜单间切换edit/view/run/kernel/settings/help。

执行流程：
- `setup()`: 先打开file菜单（调用openMainMenu）
- `run()`: 循环执行 switchMainMenu，依次打开6个菜单
- `cleanup()`: 同MenuOpenScenario（按Escape关闭菜单）

辅助函数 `openMainMenu()`（L45-L49）和 `switchMainMenu()`（L39-L43）和 `cleanupMenu()`（L51-L57）是共享的。

## SwitchTabScenario - 切换标签页

**文件**: src/scenarios.ts:L700-L769
**ID**: `tabSwitch`
**配置**: src/schema/scenario-tabs.json
**split模式**: `'first'`（仅第一个标签split-right，其余添加到已有区域）

构造函数接收JupyterFrontEnd实例，`setOptions()`接收`tabs`数组（每个tab含path或使用launcher创建）。

执行流程：
- `setupSuite()`: 为每个tab：
  - 如果有path，用 `docmanager:open` 打开
  - 否则用 `launcher:create` 创建launcher widget
  - 第一个（或全部，取决于split模式）以 `split-right` 模式添加到shell
  - 等待widget attached，对于.ipynb文件等待Spinner消失
  - activateTabWidget激活标签
- `run()`: 依次激活每个widget的标签
- `cleanupSuite()`: 关闭所有widget，等待detached

## SwitchTabFocusScenario - 切换标签焦点

**文件**: src/scenarios.ts:L771-L775
**ID**: `tabSwitchFocus`
**split模式**: `'all'`（所有标签都split-right）

继承自SwitchTabScenario，仅修改split模式为`'all'`，模拟多面板并排场景下的标签切换。

## SidebarOpenScenario - 打开侧边栏

**文件**: src/scenarios.ts:L106-L134
**ID**: `sidebarOpen`
**配置**: src/schema/scenario-sidebars.json

测量打开侧边栏面板的性能。默认侧边栏为`['filebrowser']`。

执行流程：
- `setupSuite()`/`setup()`: `closeSidebars()` - 遍历left/right侧边栏，如果面板可见则执行`application:toggle-left/right-area`关闭
- `run()`: 对配置的每个sidebar：
  - `shell.activateById(sidebar)` 激活
  - 等待 `#${sidebar}` visible
  - layoutReady

`closeSidebars()`辅助函数（L95-L104）：查询`#jp-left-stack`/`#jp-right-stack`，如果不包含`lm-mod-hidden`类则toggle关闭。

## SingleEditorScenario 基类

**文件**: src/scenarios.ts:L157-L233

这是CompleterScenario、ScrollScenario、CreateCellsScenario、DebuggerScenario的共同基类，处理编辑器（Notebook或File Editor）的创建和生命周期。

`setupSuite()`流程：
1. 如果未指定path，创建新文件（notebook或.py文件）
2. 使用 `docmanager:open` 打开widget
3. 添加到shell（默认 `split-right` 模式）
4. 激活标签，对于Notebook点击kernel选择对话框的accept按钮
5. 等待 `.jp-Editor` attached和visible
6. 定位editor元素（`.jp-Notebook` 或 `.jp-FileEditorCodeWrapper`）

`cleanupSuite()`: 保存文档 → 关闭widget。

`insertText()`工具函数（L136-L150）: 通过`apputils:run-first-enabled`依次尝试notebook/console/fileeditor的`replace-selection`命令。

## CompleterScenario - 代码补全

**文件**: src/scenarios.ts:L235-L338
**ID**: `completer`
**配置**: src/schema/scenario-completer.json

测量代码补全弹出的性能。继承SingleEditorScenario。

`setupSuite()`额外流程：
1. 插入N个token变量定义（`t0xx = 0`, `t1xx = 1`, ...）
2. 如果有setupCell，先运行setupCell再插入token
3. 在编辑器中输入't'触发补全
4. 预运行一次（first run is flaky），然后cleanup消除影响

`run()`:
1. 聚焦编辑器（处理CM5/CM6兼容）
2. Notebook使用 `completer:invoke-notebook`，File Editor使用 `completer:invoke-file`
3. 等待 `.jp-Completer.jp-HoverBox[style]` attached和visible（带style属性表示是活跃的completer而非残留）

`cleanup()`: 按Escape → 等待completer hidden。

## ScrollScenario - 滚动

**文件**: src/scenarios.ts:L628-L698
**ID**: `scroll`
**配置**: src/schema/scenario-scroll.json

测量编辑器/Notebook滚动性能。继承SingleEditorScenario。

`setupSuite()`额外流程：
1. 插入N个单元格（Notebook）或文本行（File Editor）
2. 每20/50个单元格执行一次layoutReady显示进度
3. 设置 `editor.scrollTop = 0` 回到顶部

`run()`支持两种模式：
- **cellByCell模式**（仅Notebook）：逐单元格执行`notebook:move-cursor-down`，每个cell后layoutReady
- **平滑滚动模式**：调用 `editor.scrollBy({ top: scrollTop, behavior: scrollBehavior })` → waitForScrollEnd → layoutReady

`cleanup()`: 逐单元格move-cursor-up回到顶部，或设置scrollTop=0。

## DebuggerScenario - 调试器

**文件**: src/scenarios.ts:L359-L471
**ID**: `debugger`
**配置**: src/schema/scenario-debugger.json

测量调试器操作性能。继承SingleEditorScenario，固定使用Notebook编辑器。

`setOptions()`覆盖：强制editor='Notebook'，path=null。

`setupSuite()`额外流程：
1. 插入配置的codeCells代码单元格
2. 插入`%reset -f`清理单元格
3. 回到顶部
4. 等待kernel idle
5. 确保工具栏按钮可见（处理响应式工具栏溢出）
6. 点击"Enable Debugger"按钮
7. 等待调试器侧边栏visible，等待Disable Debugger按钮出现
8. 等待 `.jp-DebuggerVariables-body` visible

`run()`: 逐个执行codeCells → 等待kernel idle → 验证变量数符合预期。

`cleanup()`: 执行%reset -f → 等待变量列表清空 → 回到顶部。

## CreateCellsScenario - 创建单元格

**文件**: src/scenarios.ts:L494-L544
**ID**: `create-cells`
**配置**: src/schema/scenario-create-cells.json

测量Notebook中创建单元格的性能。继承SingleEditorScenario。

`run()`: 循环N次：
1. `notebook:insert-cell-below`
2. 可选：改变单元格类型为raw/markdown
3. 可选：插入文本内容
4. layoutReady

`cleanup()`: 循环N次 `notebook:delete-cell` 删除创建的单元格。

## CustomScenario - 自定义场景

**文件**: src/scenarios.ts:L546-L626
**ID**: `custom`
**配置**: src/schema/scenario-custom.json

允许用户通过JSON配置任意命令序列作为场景，无需写代码。

**动态Schema生成**（L553-L589）：构造函数在 `app.restored` 后：
1. 获取所有已注册命令ID `app.commands.listCommands()`
2. 对每个命令调用 `app.commands.describedBy(commandId)` 获取参数schema
3. 动态构建JSON Schema的oneOf，包含setupCommands/commands/cleanupCommands的命令选择

配置结构：
```json
{
  "setupCommands": [{ "id": "command-id", "args": {} }],
  "commands": [{ "id": "command-id", "args": {} }],
  "cleanupCommands": [{ "id": "command-id", "args": {} }]
}
```

`setupSuite()`/`run()`/`cleanup()`分别执行对应命令数组，每个命令后layoutReady。

特殊处理：`fileeditor:change-font-size`命令的title手动覆盖为"Change font size"（因为该命令缺少label）。

## waitForKernelStatus 辅助函数

**文件**: src/scenarios.ts:L473-L478

使用ElementHandle等待Notebook执行指示器到达指定状态：
```typescript
async function waitForKernelStatus(notebookPanel: HTMLElement, status: string) {
  await new ElementHandle(notebookPanel).waitForSelector(
    `.jp-Notebook-ExecutionIndicator[data-status="${status}"]`,
    { state: 'attached' }
  );
}
```

## activateTabWidget 辅助函数

**文件**: src/scenarios.ts:L480-L492

激活指定widget的标签页：
1. 执行 `tabsmenu:activate-by-id` 命令
2. 等待 `li.lm-mod-current[data-id="${widget.id}"]` attached
3. layoutReady

## 相关概念

- (../concepts/04-scenarios.md
- (../concepts/07-dramaturg-automation.md
- (api-tokens.md
