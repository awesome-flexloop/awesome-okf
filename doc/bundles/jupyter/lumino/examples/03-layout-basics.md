---
type: Example
title: 使用布局排列 Widget
description: BoxPanel水平垂直布局、SplitPanel拖拽分割、TabPanel标签页、DockPanel停靠面板的使用
tags: [lumino, layout, boxpanel, splitpanel, tabpanel, dockpanel, ui]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T14:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: boxlayout-source
    resource: /external/libs/jupyter/lumino/packages/widgets/src/boxlayout.ts
    title: @lumino/widgets BoxLayout 源码
  - id: docklayout-source
    resource: /external/libs/jupyter/lumino/packages/widgets/src/docklayout.ts
    title: @lumino/widgets DockLayout 源码
prerequisites:
  - /lumino/concepts/06-layout-system
  - /lumino/concepts/05-widget-lifecycle
---

# 示例：使用布局排列 Widget

本示例演示 Lumino 内置布局系统的使用，包括 BoxPanel、SplitPanel、TabPanel 和 DockPanel。

## 目标

创建一个多面板应用，分别演示四种常用布局方式。

## 示例1：BoxPanel 水平/垂直布局

```typescript
import { BoxPanel, Widget } from '@lumino/widgets';
import '@lumino/default-theme/style/index.css';

// 创建彩色面板作为内容
function createColorPanel(color: string, label: string): Widget {
  const widget = new Widget();
  widget.addClass('color-panel');
  widget.node.style.backgroundColor = color;
  widget.node.style.padding = '20px';
  widget.node.innerHTML = `<h3>${label}</h3>`;
  widget.title.label = label;
  return widget;
}

// 水平布局
const hBox = new BoxPanel({ direction: 'left-to-right', spacing: 4 });
hBox.id = 'hbox-demo';
hBox.addWidget(createColorPanel('#e74c3c', '左侧'));
hBox.addWidget(createColorPanel('#3498db', '中间'));
hBox.addWidget(createColorPanel('#2ecc71', '右侧'));

// 设置拉伸因子
BoxPanel.setStretch(hBox.widgets[0], 0);  // 左侧不拉伸
BoxPanel.setStretch(hBox.widgets[1], 1);  // 中间占1份
BoxPanel.setStretch(hBox.widgets[2], 2);  // 右侧占2份

// 垂直布局
const vBox = new BoxPanel({ direction: 'top-to-bottom', spacing: 4 });
vBox.addWidget(createColorPanel('#f39c12', '顶部'));
vBox.addWidget(createColorPanel('#9b59b6', '中部'));
vBox.addWidget(createColorPanel('#1abc9c', '底部'));
BoxPanel.setStretch(vBox.widgets[0], 0);
BoxPanel.setStretch(vBox.widgets[1], 1);
BoxPanel.setStretch(vBox.widgets[2], 0);

// 嵌套布局：vBox包含hBox
const rootPanel = new BoxPanel({ direction: 'top-to-bottom', spacing: 8 });
const header = createColorPanel('#34495e', '头部');
header.node.style.height = '48px';
const footer = createColorPanel('#34495e', '底部');
footer.node.style.height = '32px';

rootPanel.addWidget(header);
BoxPanel.setStretch(header, 0);
rootPanel.addWidget(hBox);
BoxPanel.setStretch(hBox, 1);
rootPanel.addWidget(footer);
BoxPanel.setStretch(footer, 0);

Widget.attach(rootPanel, document.body);
```

## 示例2：SplitPanel 可拖拽分割

```typescript
import { SplitPanel } from '@lumino/widgets';

const split = new SplitPanel({
  orientation: 'horizontal',
  spacing: 2,
});

split.id = 'split-demo';
split.addWidget(createColorPanel('#e74c3c', '左侧面板'));
split.addWidget(createColorPanel('#3498db', '中间面板'));
split.addWidget(createColorPanel('#2ecc71', '右侧面板'));

// 设置相对尺寸比例
split.setRelativeSizes([1, 2, 1]);

// SplitPanel需要容器提供明确的高度
split.node.style.height = '400px';

Widget.attach(split, document.body);
```

用户可以通过拖拽分割条调整各面板大小。

## 示例3：TabPanel 标签页

```typescript
import { TabPanel } from '@lumino/widgets';

const tabPanel = new TabPanel({
  tabPlacement: 'top',  // 标签位置: top/bottom/left/right
  tabsMovable: true,    // 允许拖拽重排标签
});

// 创建不同内容的标签
const editor = new Widget();
editor.addClass('tab-content');
editor.title.label = '编辑器';
editor.title.iconClass = 'fa fa-code';  // 支持FontAwesome图标类
editor.title.closable = true;
editor.node.innerHTML = '<p>编辑器内容区域</p>';

const preview = new Widget();
preview.title.label = '预览';
preview.title.closable = true;
preview.node.innerHTML = '<p>预览内容区域</p>';

const terminal = new Widget();
terminal.title.label = '终端';
terminal.title.closable = true;
terminal.node.innerHTML = '<p>终端内容区域</p>';

tabPanel.addWidget(editor);
tabPanel.addWidget(preview);
tabPanel.addWidget(terminal);

// 切换标签
tabPanel.currentIndex = 0;

// 监听标签切换
tabPanel.currentChanged.connect((sender, args) => {
  console.log('切换到标签:', args.title.label);
});

tabPanel.node.style.height = '400px';
Widget.attach(tabPanel, document.body);
```

## 示例4：DockPanel IDE风格停靠布局

```typescript
import { DockPanel } from '@lumino/widgets';

const dock = new DockPanel({
  mode: 'multiple-document',  // 'multiple-document' 或 'single-document'
  spacing: 4,
});
dock.id = 'dock-demo';

// 创建多个面板
const explorer = new Widget();
explorer.title.label = '文件浏览器';
explorer.title.closable = true;
explorer.node.innerHTML = '<ul><li>📁 src/</li><li>📄 index.ts</li></ul>';

const editor1 = new Widget();
editor1.title.label = 'main.ts';
editor1.title.closable = true;
editor1.node.innerHTML = '<pre>console.log("Hello");</pre>';

const editor2 = new Widget();
editor2.title.label = 'utils.ts';
editor2.title.closable = true;
editor2.node.innerHTML = '<pre>export function add(a, b) { return a + b; }</pre>';

const terminal = new Widget();
terminal.title.label = '终端';
terminal.title.closable = true;
terminal.node.innerHTML = '<p>$ _</p>';

const console_ = new Widget();
console_.title.label = '控制台';
console_.title.closable = true;
console_.node.innerHTML = '<p>控制台输出</p>';

// 添加第一个面板（自动占据中心）
dock.addWidget(editor1);

// 在右侧分割添加explorer
dock.addWidget(explorer, { mode: 'split-left', ref: editor1 });

// 在下方分割添加terminal
dock.addWidget(terminal, { mode: 'split-bottom', ref: editor1 });

// 以标签方式添加editor2（和editor1同组）
dock.addWidget(editor2, { mode: 'tab-after', ref: editor1 });

// 在右侧添加console
dock.addWidget(console_, { mode: 'tab-after', ref: explorer });

dock.node.style.height = '600px';
Widget.attach(dock, document.body);

// 保存和恢复布局
const savedLayout = dock.saveLayout();
// ...保存到localStorage或服务器...
// dock.restoreLayout(savedLayout);
```

## 关键点说明

### 拉伸因子（Stretch）

BoxLayout 的 stretch 因子决定了多余空间的分配比例：

```
总可用空间 = 容器尺寸 - 固定尺寸widget的自然尺寸
分配比例 = 每个widget的stretch / 所有stretch之和
```

stretch=0 的 Widget 保持其自然尺寸（由内容决定），stretch>0 的 Widget 按比例分配剩余空间。

### 布局的一次性原则

Widget 的 layout 只能设置一次（Panel 内部自动设置），不能在运行时更换布局类型。如果需要切换布局模式，应该创建新的父 Widget 并迁移子 Widget。

### Spacing 属性

布局的 `spacing` 设置子 Widget 之间的间距（像素），不同布局的 spacing 表现略有不同：
- BoxPanel/SplitPanel：子元素之间的间隔
- DockPanel：分割条的宽度
- TabPanel：标签与内容之间的间距

### 尺寸要求

基于 Layout 的 Widget 需要父容器有明确的尺寸约束。如果父容器高度为 0，布局将不可见。使用 BoxPanel 作为根容器可以自动占满可用空间。

## CSS 样式补充

```css
.color-panel {
  color: white;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60px;
}

.tab-content {
  padding: 16px;
}

.lm-DockPanel-widget {
  background: #fff;
  padding: 8px;
}
```

## 扩展练习

1. 嵌套组合 BoxPanel 和 SplitPanel 创建更复杂的布局
2. 监听 DockPanel 的 activeWidget 变化，实现"当前激活面板"状态跟踪
3. 使用 layout.saveLayout/restoreLayout 实现布局持久化到 localStorage
4. 在 DockPanel 中添加右键菜单关闭标签
