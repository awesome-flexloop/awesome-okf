---
type: Concept
title: 无障碍设计
description: sphinx-tabs 的 WAI-ARIA 标签页模式实现：ARIA 属性、键盘导航、语义化 HTML 元素和屏幕阅读器支持
tags: [sphinx, tabs, accessibility, aria, wai-aria, keyboard-navigation]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:32:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: tabs-source
    resource: /references/tabs-source.md
    title: sphinx-tabs 源码路径映射
---

# 无障碍设计

sphinx-tabs 完全遵循 WAI-ARIA Authoring Practices Guide (APG) 的 Tabs Pattern，输出语义化 HTML，支持键盘导航和屏幕阅读器。

## ARIA 角色与属性

sphinx-tabs 输出的 HTML 结构包含以下 ARIA 属性：

| 元素 | ARIA 角色 | 属性 |
|------|----------|------|
| 标签栏容器 | `role="tablist"` | `aria-label="Tabbed content"` |
| 标签按钮 | `role="tab"` | `id`、`aria-selected`、`aria-controls`、`tabindex`、`name` |
| 面板容器 | `role="tabpanel"` | `id`、`aria-labelledby`、`tabindex`、`hidden` |

### 输出结构示例

```html
<div class="sphinx-tabs docutils container">
  <div role="tablist" aria-label="Tabbed content">
    <button role="tab" id="tab-0-0"
            aria-selected="true" aria-controls="panel-0-0"
            tabindex="0" class="sphinx-tabs-tab">标签一</button>
    <button role="tab" id="tab-0-1"
            aria-selected="false" aria-controls="panel-0-1"
            tabindex="-1" class="sphinx-tabs-tab">标签二</button>
  </div>
  <div role="tabpanel" id="panel-0-0"
       aria-labelledby="tab-0-0" tabindex="0"
       class="sphinx-tabs-panel">
    内容一
  </div>
  <div role="tabpanel" id="panel-0-1"
       aria-labelledby="tab-0-1" tabindex="0"
       hidden="true" class="sphinx-tabs-panel">
    内容二
  </div>
</div>
```

## 语义化 HTML 选择

sphinx-tabs 的标签按钮使用 `<button>` 元素（`SphinxTabsTab.tagname = "button"`），而非 `<div>` 或 `<span>`。这带来三个无障碍优势：

1. **原生可聚焦**：`<button>` 自动参与 Tab 键焦点顺序
2. **键盘可激活**：Enter 和 Space 键原生触发 click 事件
3. **屏幕阅读器识别**：自动播报为"按钮"角色

若使用 `<div role="tab">` 则需要手动添加 `tabindex="0"`、监听 keydown 事件模拟 Enter/Space 激活，增加了无障碍缺陷风险。

## 键盘导航支持

sphinx-tabs 的 JavaScript 实现了完整的标签页键盘交互：

| 按键 | 行为 |
|------|------|
| **Tab** | 焦点移入标签栏时聚焦到当前选中标签（`tabindex="0"`）；焦点移出到面板或下一个元素 |
| **→ (右箭头)** | 移动焦点到下一个标签，最后一个标签循环到第一个 |
| **← (左箭头)** | 移动焦点到上一个标签，第一个标签循环到最后一个 |
| **Enter/Space** | 激活当前聚焦的标签（通过 `<button>` 原生支持） |

### 循环导航实现

```javascript
function keyTabs(e) {
    if (e.keyCode === 39) {  // 右箭头
        nextTab = tab.nextElementSibling || tab.parentNode.firstElementChild;
    } else if (e.keyCode === 37) {  // 左箭头
        nextTab = tab.previousElementSibling || tab.parentNode.lastElementChild;
    }
    // roving tabindex: 当前标签 tabindex=-1，下一标签 tabindex=0
    if (nextTab !== null) {
        nextTab.setAttribute("tabindex", 0);
        nextTab.focus();
    }
}
```

使用**roving tabindex**模式：同一时刻只有一个标签的 `tabindex` 为 0，其余为 -1，确保 Tab 键只会停留在选中的标签上。

## 选中状态管理

- **初始状态**：第一个标签 `aria-selected="true"` 且面板可见；其余 `aria-selected="false"` 且面板 `hidden="true"`
- **选中切换**：先调用 `deselectTabList()` 将所有标签设为未选中（`aria-selected="false"` + 面板 `hidden="true"`），再调用 `selectTab()` 激活目标标签
- **位置补偿**：切换标签时计算 tablist 位置偏移量，调用 `window.scrollTo()` 防止内容高度变化导致页面跳动

```javascript
function changeTabs(e) {
    const positionBefore = this.parentNode.getBoundingClientRect().top;
    deselectTabList(this);
    selectTab(this);
    const positionAfter = this.parentNode.getBoundingClientRect().top;
    window.scrollTo(0, window.scrollY + (positionAfter - positionBefore));
}
```

## 降级处理

对于不兼容的 builder（非 HTML 输出），标签页降级为普通 docutils container 嵌套输出，不使用 ARIA 角色和标签按钮，内容按顺序渲染。这确保在 LaTeX/PDF/ePub 等输出中内容不会丢失。

## 相关概念

- [四个指令详解](02-directives.md)
- [配置项参考](04-configuration.md)
- [基础标签页示例](../examples/basic-tabs.md)
