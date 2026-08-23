---
type: Reference
title: Dramaturg 浏览器自动化层源码分析
description: Dramaturg是ui-profiler内置的Playwright-like浏览器自动化工具，基于MutationObserver/ResizeObserver/原生DOM API实现，无需外部E2E框架即可模拟用户交互
tags: [jupyterlab, ui-profiler, dramaturg, automation, mutation-observer, dom, playwright-like]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:40:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T13:40:00Z" }
status: stable
stale_after: "2027-02-22"
sources:
  - id: dramaturg-ts
    resource: /references/dramaturg-source.md
    title: src/dramaturg.ts 浏览器自动化层实现
  - id: lumino-keyboard
    resource: /references/dramaturg-source.md
    title: @lumino/keyboard 键盘布局
---

## 设计定位

**文件**: src/dramaturg.ts:L1-L3（注释）
> Dramaturg implements a subset of Playwright-like API for native web testing.

Dramaturg不依赖Playwright/Puppeteer等外部浏览器自动化框架，而是直接在浏览器中使用原生Web API实现用户交互模拟。这是因为Scenario需要在JupyterLab运行时内部执行（非外部E2E测试），需要直接访问JupyterFrontEnd实例和DOM。

## page 对象

**文件**: src/dramaturg.ts:L332-L362

`page`是Dramaturg的主要入口，提供类Playwright API：

```typescript
export const page = {
  waitForSelector,    // 等待元素达到指定状态
  press,              // 模拟键盘按键
  $,                  // 查询单个元素
  type,               // 在元素中输入文本
  click,              // 点击元素
  focus,              // 聚焦元素
  mouse: { wheel }    // 鼠标滚轮
};
```

## waitForSelector - 元素等待

**文件**: src/dramaturg.ts:L207-L255

支持四种等待状态，使用函数重载区分返回类型：
- `'attached'`: 元素存在于DOM中（不一定可见）→ 返回ElementHandle
- `'detached'`: 元素从DOM中移除 → 返回null
- `'visible'`: 元素可见（宽高均不为0）→ 返回ElementHandle
- `'hidden'`: 元素不可见（宽高为0或display:none）→ 返回null

内部实现使用两个底层等待函数：

### waitForElement - 等待元素出现

**文件**: src/dramaturg.ts:L68-L110

使用MutationObserver监听DOM变化：
- `childList: true, subtree: true` 监听子节点添加
- 如果selector包含属性选择器（`[`）或伪类（`:`），额外监听attributes变化
- 检查addedNodes中的节点及其子节点是否匹配selector
- 5秒超时（可配置）

### waitElementVisible - 等待元素可见

**文件**: src/dramaturg.ts:L25-L61

使用ResizeObserver监听元素尺寸变化：
- 可见条件：`contentRect.width !== 0 && contentRect.height !== 0`
- 隐藏条件：宽或高为0
- 初始检查：如果元素已经可见/隐藏，立即resolve
- ResizeObserver在尺寸满足条件时disconnect并resolve

### waitNoElement - 等待元素消失

**文件**: src/dramaturg.ts:L112-L135

使用MutationObserver监听removedNodes。

### waitUntilDisappears - 轮询等待消失

**文件**: src/dramaturg.ts:L6-L23

使用setInterval轮询（50ms间隔，5秒超时），与waitNoElement不同的是这是一个更简单的轮询版本。

## ElementHandle 类

**文件**: src/dramaturg.ts:L172-L205

类似Playwright的ElementHandle，包装DOM元素提供链式操作：

```typescript
class ElementHandle {
  constructor(public element: Element);
  $(selector): Promise<ElementHandle | null>;     // 在当前元素内查询
  click(): Promise<void>;                         // 点击元素
  focus(): Promise<void>;                         // 聚焦
  press(key, options?): Promise<void>;            // 在元素上按键
  type(text, options?): Promise<void>;            // 在元素上输入文本
  isVisible(): Promise<boolean>;                  // 判断是否可见
  waitForSelector(selector, options): Promise<ElementHandle>;  // 在元素内等待
}
```

注意`waitForSelector`的within选项限制搜索范围在当前元素子树内。

## 用户输入模拟

### click - 鼠标点击

**文件**: src/dramaturg.ts:L306-L317

```typescript
async function click(element: HTMLElement) {
  const rect = element.getBoundingClientRect();
  const initDict = {
    clientX: rect.x + rect.width / 2,
    clientY: rect.x + rect.height / 2,  // 注意：这里可能是rect.y的笔误
    bubbles: true                        // React需要bubbles才能处理事件
  };
  element.dispatchEvent(new MouseEvent('mousedown', initDict));
  element.dispatchEvent(new MouseEvent('mouseup', initDict));
  element.click();
}
```

关键点：
- 计算元素中心点坐标
- 派发mousedown和mouseup事件
- 必须设置`bubbles: true`，React的合成事件系统依赖事件冒泡
- 最后调用原生`.click()`方法

### press - 键盘按键

**文件**: src/dramaturg.ts:L266-L290

使用`@lumino/keyboard`的`getKeyboardLayout()`获取键盘布局，映射key到keyCode：

```typescript
async function press(key, options = { delay: 0 }, element = null) {
  const keys = key.split('+');
  const modifiers = keys.filter(k => keyboardLayout.isModifierKey(k));
  const target = keys.filter(k => !keyboardLayout.isModifierKey(k))[0];
  const eventData: KeyboardEventInit = {
    keyCode: keyToCode[target],
    shiftKey: modifiers.includes('Shift'),
    ctrlKey: modifiers.includes('Ctrl'),
    metaKey: modifiers.includes('Meta'),
    key: target
  };
  element.dispatchEvent(new KeyboardEvent('keydown', eventData));
  element.dispatchEvent(new KeyboardEvent('keypress', eventData));
  if (options.delay) await sleep;
  element.dispatchEvent(new KeyboardEvent('keyup', eventData));
}
```

支持组合键（如'Ctrl+Enter'、'Escape'），通过`+`分割识别修饰键。

### type - 文本输入

**文件**: src/dramaturg.ts:L296-L304

逐字符调用press()模拟打字输入。

### mouse.wheel - 鼠标滚轮

**文件**: src/dramaturg.ts:L353-L362

派发WheelEvent到document。

## 布局等待

### layoutReady - 等待下一帧

**文件**: src/dramaturg.ts:L158-L164

```typescript
export function layoutReady(): Promise<void> {
  return new Promise(resolve => {
    return requestAnimationFrame(() => resolve());
  });
}
```

等待一个requestAnimationFrame，确保浏览器完成布局计算。这是Scenario中最常用的等待函数，在每个DOM操作后调用以确保UI稳定。

### waitForScrollEnd - 等待滚动结束

**文件**: src/dramaturg.ts:L137-L156

使用setInterval轮询scrollTop/scrollLeft，直到连续两次检查值相同（静止requiredRestTime毫秒）。

## 与Playwright的差异

| 特性 | Dramaturg | Playwright |
|------|-----------|------------|
| 运行环境 | 浏览器内（in-process） | Node.js进程（out-of-process） |
| 访问JupyterLab内部 | 直接引用app实例 | 通过CDP/page.evaluate |
| 等待机制 | MutationObserver+ResizeObserver+RAF | 网络空闲+RAF+选择器 |
| 超时 | 默认5秒 | 默认30秒 |
| iframe支持 | 无 | 有 |
| 多页面/多tab | 无 | 有 |
| 截图/录屏 | 无 | 有 |
| 网络拦截 | 无 | 有 |
| 键盘布局 | 依赖@lumino/keyboard | 内置keyboard |

Dramaturg刻意保持轻量——它只实现了Scenario执行所需的最小API集，不追求Playwright的完整功能覆盖。

## 关键设计决策

1. **不使用Playwright/Puppeteer**：因为Profiler需要在JupyterLab运行时中直接执行，外部自动化框架无法访问JupyterFrontEnd实例和命令系统
2. **MutationObserver驱动等待**：比轮询更高效，只在DOM变化时检查
3. **ResizeObserver判断可见性**：比检查offsetHeight/offsetParent更可靠，能处理CSS transform等复杂场景
4. **bubbles: true**：React合成事件系统要求事件冒泡，这是容易遗漏的细节
5. **layoutReady()使用RAF**：确保浏览器完成样式计算和布局后再继续，避免测量抖动

## 相关概念

- (../concepts/07-dramaturg-automation.md
- (../concepts/04-scenarios.md
- (api-tokens.md
