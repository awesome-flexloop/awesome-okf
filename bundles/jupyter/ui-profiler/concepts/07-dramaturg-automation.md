---
type: Concept
title: Dramaturg 浏览器自动化层
description: 深入理解ui-profiler自定义的Dramaturg浏览器自动化层——为什么不用Playwright/Puppeteer，waitForSelector/waitForFunction/waitForLayout/waitForScrollEnd等核心API，以及CM5/CM6兼容处理
tags: [jupyterlab, ui-profiler, dramaturg, automation, playwright, mutation-observer, resize-observer]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T13:40:00Z" }
verified: { by: "process:grep-verify", at: "2026-08-22T13:40:00Z" }
status: stable
stale_after: "2027-02-22"
sources:
  - id: dramaturg-ts
    resource: /references/dramaturg-source.md
    title: src/dramaturg.ts Dramaturg实现
---

## 为什么需要 Dramaturg

JupyterLab UI Profiler需要在**浏览器内部**自动化用户操作（点击菜单、切换标签、输入代码等）并精确等待DOM状态变化。常见的浏览器自动化方案为什么不适用？

| 方案 | 问题 |
|------|------|
| **Playwright/Puppeteer** | 运行在Node.js进程中，通过CDP协议控制浏览器；但ui-profiler需要在**用户的浏览器中直接运行**（作为JupyterLab扩展），无法启动外部进程 |
| **Selenium WebDriver** | 同样需要外部驱动进程，不适合浏览器内扩展 |
| **Cypress** | 测试框架，不是库，且需要特殊启动方式 |
| **直接DOM操作+setTimeout** | setTimeout不可靠，固定等待时间要么浪费时间要么状态未就绪；MutationObserver是正确方式但使用复杂 |

**Dramaturg**（戏剧编剧/剧场导演）就是为解决这个问题而生：一个轻量级的、在浏览器内运行的DOM自动化层，提供Playwright风格的API。

## 核心设计：Observer 模式

Dramaturg的核心是利用两个浏览器Observer API来等待状态变化：

```
MutationObserver ──→ 监听DOM树变化（节点添加/删除/属性变化/文本变化）
ResizeObserver  ──→ 监听元素尺寸变化（布局完成信号）
```

配合 `requestAnimationFrame` 等待渲染帧，实现精确的状态等待。

## 核心API

### waitForSelector - 等待元素出现

**文件**: src/dramaturg.ts:L22-L73

```typescript
async waitForSelector<T extends Element = Element>(
  selector: string,
  options?: WaitForSelectorOptions
): Promise<T>
```

**WaitForSelectorOptions**:
| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `timeout` | number | 5000ms | 超时时间 |
| `visible` | boolean | true | 要求元素可见（offsetParent !== null） |
| `hidden` | boolean | false | 等待元素消失/隐藏 |
| `root` | Element | document | 搜索根节点 |
| `predicate` | (el: T) => boolean | - | 额外过滤条件 |
| `includeSlotted` | boolean | true | 是否包含Shadow DOM中通过<slot>分发的元素 |

**实现原理**：

1. 先检查`root.querySelector(selector)`是否已经匹配（即时满足）
2. 如果不满足，创建MutationObserver监听root的子树变化
3. 每次DOM变化时重新querySelectorAll检查匹配
4. 超时则reject
5. 如果`visible: true`，还要检查元素是否真的可见（`offsetParent !== null`）

**Shadow DOM处理**（includeSlotted）：

Shadow DOM中通过`<slot>`分发的元素物理上在light DOM，但渲染在Shadow DOM的slot位置。Dramaturg在查询时特殊处理：
- 查找所有slot元素，收集assignedElements()（分配到该slot的元素）
- 这些slotted元素即使不在Shadow Root的直接子树中也纳入匹配范围

这对JupyterLab很重要——很多组件使用Shadow DOM，而菜单、工具栏等元素是slotted的。

### waitForFunction - 等待自定义条件

**文件**: src/dramaturg.ts:L75-L102

```typescript
async waitForFunction<T>(
  fn: () => T | null | undefined | false | 0 | '',
  options?: WaitForFunctionOptions
): Promise<T>
```

轮询模式（非Observer驱动）：每16ms（约一帧）执行一次fn，直到返回truthy值。

这是最灵活的等待方式，可以等待任意自定义条件：

```typescript
// 等待notebook kernel idle
await dramaturg.waitForFunction(() => {
  return notebook.model?.kernelStatus === 'idle';
}, { timeout: 10000 });
```

**注意**：轮询间隔16ms约为60fps一帧的时间。对于需要更长等待时间的条件，应配合MutationObserver模式。

### waitForLayout - 等待布局稳定

**文件**: src/dramaturg.ts:L104-L135

```typescript
async waitForLayout(element: Element): Promise<DOMRect>
```

这是Dramaturg最巧妙的API之一，解决了"等DOM变化后的布局完成"问题。

**实现原理**：

1. 取元素的初始`getBoundingClientRect()`
2. 创建ResizeObserver监听元素尺寸变化
3. 等待两个连续的requestAnimationFrame：
   - 第一个rAF：浏览器处理完样式计算和布局，但可能还有后续变化
   - ResizeObserver触发后再次rAF：尺寸稳定，布局完成
4. 循环处理初始状态不稳定的情况（如果尺寸仍在变化，继续等待）

为什么需要两个rAF？浏览器的渲染流水线是：
```
JavaScript → Style → Layout → Paint → Composite → rAF callback
```
一个rAF只能保证"之前的变更已处理"，但某些变更（如CSS transition、Lumino布局算法）会在rAF回调中触发新的布局变化。等待ResizeObserver+第二个rAF确保布局完全稳定。

```typescript
// 简化的核心逻辑
const timeout = setTimeout(reject, 5000);
const observer = new ResizeObserver(() => {
  // 尺寸变化后，再等一个rAF确保稳定
  requestAnimationFrame(() => resolve(rect));
});
observer.observe(element);
// 先等一个rAF
requestAnimationFrame(() => {
  // 如果尺寸已经稳定（与初始相同），直接resolve
  const rect = element.getBoundingClientRect();
  if (rectsEqual(rect, initialRect)) {
    clearTimeout(timeout);
    resolve(rect);
  }
});
```

### waitForScrollEnd - 等待滚动结束

**文件**: src/dramaturg.ts:L137-L156

```typescript
async waitForScrollEnd(target: Element, options?: { interval?: number }): Promise<void>
```

轮询模式：每50ms检查一次scrollTop和scrollLeft，连续两次检查值相同则认为滚动结束。

为什么不用scrollend事件？因为scrollend事件在较新浏览器中才支持，且smooth scroll的结束判定需要轮询确认。

### waitForEvent - 等待DOM事件

**文件**: src/dramaturg.ts:L158-L171

```typescript
async waitForEvent(target: EventTarget, eventName: string): Promise<Event>
```

简单的Promise封装：addEventListener(eventName) → resolve(event) → removeEventListener。

### click - 点击元素

**文件**: src/dramaturg.ts:L173-L191

```typescript
async click(selector: string, options?: ClickOptions): Promise<void>
```

1. waitForSelector等待元素
2. 如果visible: true且元素不可见，尝试`element.scrollIntoView()`
3. 调用`element.click()`触发原生点击事件

click()使用的是原生`HTMLElement.click()`方法，而非模拟mousedown/mouseup序列，这简化了实现但可能不触发某些需要完整鼠标事件序列的交互。

### hover - 悬停元素

**文件**: src/dramaturg.ts:L193-L206

```typescript
async hover(selector: string): Promise<void>
```

创建并派发`mouseover`、`mouseenter`、`mousemove`、`pointerover`、`pointerenter`、`pointermove`事件。比click复杂，因为悬停需要多个事件序列。

注意：没有派发mouseleave/mouseout/pointerleave/pointerout——这是有意的，hover()只模拟"移动到元素上"，不模拟"移开"。

### fill - 填充输入框

**文件**: src/dramaturg.ts:L208-L226

```typescript
async fill(selector: string, text: string): Promise<void>
```

1. 等待元素
2. 如果元素已有value，先清除（设置为''并触发input事件）
3. 聚焦元素（element.focus()）
4. 对text中的每个字符逐个触发keydown事件
5. 设置element.value = text
6. 触发input事件
7. 失焦（blur()）

注意：逐字符触发keydown是为了模拟真实输入，但没有触发keypress/keyup，某些监听keyup的组件可能无法正确响应。

### layoutReady - 等待一帧

**文件**: src/dramaturg.ts:L269-L271

```typescript
export function layoutReady(): Promise<void> {
  return new Promise(resolve => requestAnimationFrame(() => resolve()));
}
```

Dramaturg类外部也导出了独立的`layoutReady()`函数。这是最轻量的等待方式——只等一个requestAnimationFrame。

在CSS Benchmark中大量使用：每次禁用/删除CSS规则后调用layoutReady()确保浏览器处理了变更。

## LuminoWidget - Lumino widget等待辅助

**文件**: src/lumino.ts

```typescript
export class LuminoWidget {
  static async waitForAttached(widget: Widget): Promise<void>;
  static async waitForShow(widget: Widget): Promise<void>;
  static async waitForHide(widget: Widget): Promise<void>;
  static async waitForClose(widget: Widget): Promise<void>;
}
```

JupyterLab基于Lumino组件库（PhosphorJS的后继），Lumino widget有自己的生命周期（attached/show/hide/close），不完全等同于DOM的生命周期。

这些方法通过Lumino的Message机制（而非DOM Observer）等待特定生命周期消息：
- `waitForAttached`：等待`after-attach`消息
- `waitForShow`：等待`after-show`消息
- `waitForHide`：等待`after-hide`消息
- `waitForClose`：等待`close`消息

实现方式是hook widget的processMessage或监听相应信号。

## CodeMirror 兼容处理

JupyterLab从3.x开始逐步从CodeMirror 5迁移到CodeMirror 6。Dramaturg（以及Scenario代码）需要兼容两者。

### 检测当前版本

```typescript
// CM5
const cm5Editor = document.querySelector('.CodeMirror-scroll');
// CM6
const cm6Editor = document.querySelector('.cm-scroller');
```

### 编辑器焦点

CM5和CM6的可聚焦元素不同：
- **CM5**：`.CodeMirror` 元素本身可聚焦
- **CM6**：`.cm-content` 元素（contenteditable div）可聚焦

在CompleterScenario和ScrollScenario中都有版本检测逻辑：
```typescript
if (cm6) {
  // CM6: 聚焦 .cm-content
  (editor.querySelector('.cm-content') as HTMLElement)?.focus();
} else {
  // CM5: 直接聚焦CodeMirror容器
  (editor.querySelector('.CodeMirror') as HTMLElement)?.focus();
}
```

### 滚动容器

- **CM5**：`.CodeMirror-scroll` 是滚动容器
- **CM6**：`.cm-scroller` 是滚动容器

ScrollScenario中根据版本选择不同的元素设置scrollTop。

## 设计模式总结

| 模式 | API | 适用场景 |
|------|-----|---------|
| Observer驱动 | waitForSelector, waitForLayout | 等待DOM变化、布局稳定 |
| 轮询驱动 | waitForFunction, waitForScrollEnd | 等待自定义条件、滚动停止 |
| 事件驱动 | waitForEvent | 等待特定DOM事件 |
| 帧同步 | layoutReady | 轻量级"等下一帧" |
| 组合操作 | click, hover, fill | 复杂交互 = 等待 + 动作 |

## 局限性

1. **click()使用原生click()**：不模拟完整鼠标事件序列（mousedown→mouseup→click），某些依赖mousedown的组件可能需要特殊处理
2. **fill()逐字符keydown**：缺少keypress/keyup事件，对某些编辑器可能不完整
3. **hover()不移出**：hover只模拟移入不移出，连续hover可能残留状态
4. **没有drag-and-drop**：不支持拖拽操作
5. **没有键盘快捷键模拟**：没有提供type()或press()方法模拟复杂键盘操作（Scenario中直接使用`app.commands.execute()`代替）
6. **轮询间隔固定**：waitForFunction的16ms间隔不可配置

这些局限是有意的——Dramaturg只为ui-profiler的内置Scenario服务，不需要完整的E2E测试框架能力。

## 相关概念

- (04-scenarios.md
- (09-ui-and-visualization.md
- (../references/dramaturg-source.md
