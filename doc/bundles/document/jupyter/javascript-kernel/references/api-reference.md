---
type: Reference
title: 全局 API 参考
description: JavaScript Kernel 运行时注入的全局对象和函数 API
tags: [api, reference, global, display, console, jupyter, globals]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: jk-executor
    title: executor.ts
  - id: jk-evaluator
    title: runtime_evaluator.ts
  - id: jk-display
    title: display.ts
  - id: jk-comm
    title: comm.ts
  - id: jk-widget
    title: widgets/widget.ts
---

# 全局 API 参考

JavaScript Kernel 在运行时全局作用域注入以下对象和函数。

## 全局函数

### display()

显示任意值到 Notebook 输出区域。

```typescript
function display(value: any, metadata?: {
  display_id?: string;
  raw_mimetype?: string;
  [key: string]: any;
}): void;
```

**参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `value` | `any` | 要显示的值 |
| `metadata.display_id` | `string` | 输出 ID，用于 update_display_data |
| `metadata.raw_mimetype` | `string` | 直接指定 MIME 类型 |

**示例：**
```javascript
display("Hello");
display("<b>Bold</b>", { raw_mimetype: 'text/html' });
display("loading...", { display_id: 'status' });
```

---

## 全局 console （重写）

内核重写了 `console` 对象，将输出重定向到 Notebook。

### console.log(...args)
### console.info(...args)
### console.debug(...args)
### console.dir(obj)
### console.trace()
### console.table(data, columns?)

输出到 **stdout** 流。参数通过富格式化处理（对象显示为 JSON）。

### console.error(...args)
### console.warn(...args)

输出到 **stderr** 流（红色/黄色显示）。

**原始 console 方法保存在 `console._original` 中（内部使用，不建议直接访问）。**

---

## 全局对象 Jupyter

`globalThis.Jupyter` 提供 Comm 和 Widget 访问。

### Jupyter.comm

CommManager 实例，用于创建和管理自定义通信通道。

#### Jupyter.comm.open(targetName, data?, metadata?, buffers?)

打开一个 comm 通道（内核主动）。

```typescript
open(
  targetName: string,
  data?: any,
  metadata?: Record<string, any>,
  buffers?: ArrayBuffer[]
): Comm;
```

**返回：** [Comm](#comm-类) 实例

#### Jupyter.comm.registerTarget(targetName, handler)

注册 comm target 处理器（处理前端打开的 comm）。

```typescript
registerTarget(
  targetName: string,
  handler: (comm: Comm, message: { data: any; buffers?: ArrayBuffer[]; parentMessageId?: string }) => void | Promise<void>
): void;
```

**示例：**
```javascript
Jupyter.comm.registerTarget('my-target', (comm, msg) => {
  console.log('Comm opened:', msg.data);
  comm.onMsg = ({ data }) => console.log('Received:', data);
  comm.send({ status: 'ready' });
});
```

#### Jupyter.comm.getComm(commId)

通过 ID 获取已有的 Comm 实例。

```typescript
getComm(commId: string): Comm | undefined;
```

---

### Jupyter.widgets

包含所有内置 Widget 类的对象。在运行时动态绑定，仅在 kernel 内部可用。

**常用类：**

| 类名 | 说明 |
|------|------|
| `IntSlider` | 整数滑块 |
| `FloatSlider` | 浮点数滑块 |
| `IntRangeSlider` | 整数范围滑块 |
| `FloatRangeSlider` | 浮点数范围滑块 |
| `IntProgress` | 整数进度条 |
| `FloatProgress` | 浮点数进度条 |
| `Checkbox` | 复选框 |
| `ToggleButton` | 切换按钮 |
| `Dropdown` | 下拉选择 |
| `RadioButtons` | 单选按钮组 |
| `Select` | 列表选择 |
| `Text` | 单行文本输入 |
| `Textarea` | 多行文本输入 |
| `ColorPicker` | 颜色选择器 |
| `Button` | 按钮 |
| `Output` | 输出区域 |
| `Label` | 文本标签 |
| `HTML` | HTML 显示 |
| `HBox` | 水平布局容器 |
| `VBox` | 垂直布局容器 |
| `Box` | 通用容器 |
| `Accordion` | 折叠面板 |
| `Tab` | 标签页 |
| `Layout` | 布局模型 |
| `jslink` | JavaScript 双向绑定函数 |
| `jsdlink` | JavaScript 单向绑定函数 |

完整列表参见 [05-Widget系统](../concepts/05-widget-system.md#可用控件清单)。

---

## Comm 类

代表一个双向通信通道。

### 属性

| 属性 | 类型 | 只读 | 说明 |
|------|------|------|------|
| `commId` | `string` | ✅ | comm 唯一 ID |
| `targetName` | `string \| undefined` | ✅ | target 名称 |
| `onMsg` | `function \| null` | ❌ | 消息回调 |
| `onClose` | `function \| null` | ❌ | 关闭回调 |
| `isDisposed` | `boolean` | ✅ | 是否已关闭 |

### 方法

#### comm.send(data, options?)

发送消息到前端。

```typescript
send(data: any, options?: {
  buffers?: ArrayBuffer[];
  parentMessageId?: string;
}): void;
```

#### comm.close(data?)

关闭 comm 通道。

```typescript
close(data?: any): void;
```

---

## Widget 基类

所有 Widget 的基类。

### 构造函数

```typescript
new Widget(state?: Record<string, any>);
```

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `commId` | `string` | Widget 的 comm/model ID |

### 方法

#### widget.get(key)

获取属性值。

```typescript
get(key: string): any;
```

#### widget.set(key, value) | widget.set(state)

设置属性值（单个或批量）。值变化时自动同步到前端并触发 change 事件。

```typescript
set(key: string, value: any): void;
set(state: Record<string, any>): void;
```

#### widget.on(event, callback)

监听事件。

```typescript
on(event: string, callback: Function): void;
```

支持的事件：`change:propName`、`change`、`close`、`custom`、`click`（Button）。

#### widget.off(event, callback)

取消事件监听。

```typescript
off(event: string, callback: Function): void;
```

#### widget.observe(callback, names?)

ipywidgets 风格的属性观察。

```typescript
observe(
  callback: (change: { name: string; new: any; old: any; owner: Widget; type: string }) => void,
  names?: string | string[]
): void;
```

`names`：属性名字符串、属性名数组、或 `'*'`（所有属性）。

#### widget.unobserve(callback, names?)

取消观察。

```typescript
unobserve(callback: Function, names?: string | string[]): void;
```

#### widget.close()

关闭 widget，销毁 comm 通道。

```typescript
close(): void;
```

### ES 属性访问

Widget 也支持 ES getter/setter 语法糖：

```javascript
slider.value;           // 等价于 slider.get('value')
slider.value = 42;      // 等价于 slider.set('value', 42)
slider.description;     // 等价于 slider.get('description')
```

---

## DOMWidget 类

继承自 Widget，是所有可见控件的基类。

### 通用属性

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `description` | `string` | `''` | 描述标签 |
| `disabled` | `boolean` | `false` | 是否禁用 |
| `visible` | `boolean` | `true` | 是否可见 |
| `tooltip` | `string` | `''` | 悬停提示 |
| `layout` | `Layout` | — | 布局配置 |
| `style` | `Style` | — | 样式配置 |

---

## Button Widget

### 额外属性

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `description` | `string` | `''` | 按钮文字 |
| `icon` | `string` | `''` | 图标类名（Font Awesome） |
| `button_style` | `string` | `''` | 样式：'primary'/'success'/'info'/'warning'/'danger'/'' |
| `tooltip` | `string` | `''` | 悬停提示 |

### 方法

#### button.onClick(callback)

注册点击回调。

```typescript
onClick(callback: () => void): void;
```

---

## Output Widget

### 方法

#### output.clearOutput(options?)

清除输出区域。

```typescript
clearOutput(options?: { wait?: boolean }): void;
```

#### output.appendStdout(text)

追加标准输出文本。

```typescript
appendStdout(text: string): void;
```

#### output.appendStderr(text)

追加标准错误文本。

```typescript
appendStderr(text: string): void;
```

#### output.appendDisplayData(data, metadata?)

追加富显示数据。

```typescript
appendDisplayData(
  data: Record<string, any>,
  metadata?: Record<string, any>
): void;
```

#### output.capture(callback, options?)

捕获回调中产生的所有输出到 Output widget。

```typescript
capture(
  callback: Function,
  options?: { clearOutput?: boolean }
): Function;  // 返回包装后的函数
```

也可以作为装饰器使用：`out.capture({clearOutput: true})(fn)`。

---

## jslink / jsdlink

### jslink(source, target)

双向绑定两个 widget 的属性。

```typescript
function jslink(
  source: [Widget, string],
  target: [Widget, string]
): Link;
```

### jsdlink(source, target)

单向（方向）绑定：source 变化时更新 target，但 target 变化不影响 source。

```typescript
function jsdlink(
  source: [Widget, string],
  target: [Widget, string]
): DirectionalLink;
```

---

## 自定义 MIME 输出方法

任意对象可以定义以下方法来自定义显示：

| 方法 | 返回类型 | 说明 |
|------|---------|------|
| `_toHtml()` | `string` | 返回 HTML 字符串 |
| `_toSvg()` | `string` | 返回 SVG 字符串 |
| `_toPng()` | `string` | 返回 PNG base64 字符串 |
| `_toJpeg()` | `string` | 返回 JPEG base64 字符串 |
| `_toMime()` | `IMimeBundle` | 返回完整 MIME bundle 对象 |
| `inspect()` | `any` | Node.js 风格检查（text/plain） |

---

## 浏览器 API

IFrame 和 Worker 模式下可用的标准 Web API：

| API | IFrame | Worker |
|-----|--------|--------|
| `fetch` | ✅ | ✅ |
| `WebSocket` | ✅ | ✅ |
| `setTimeout`/`setInterval` | ✅ | ✅ |
| `Promise` | ✅ | ✅ |
| `Map`/`Set`/`WeakMap`/`WeakSet` | ✅ | ✅ |
| `ArrayBuffer`/`TypedArray` | ✅ | ✅ |
| `URL`/`URLSearchParams` | ✅ | ✅ |
| `crypto` | ✅ | ✅ |
| `TextEncoder`/`TextDecoder` | ✅ | ✅ |
| `document` | ✅ | ❌ |
| `window` | ✅ | ❌（只有 `self`） |
| `window.parent` | ✅ | ❌ |
| `navigator` | ✅ | ✅ |
| `localStorage` | ✅ | ✅ |
| Canvas API | ✅ | ⚠️（OffscreenCanvas） |
| `requestAnimationFrame` | ✅ | ❌ |
| DOM Elements | ✅ | ❌ |

## 相关文档

- [07-富媒体输出系统](../concepts/07-display-system.md) — display() 和 MIME 类型
- [06-Comm 协议](../concepts/06-comm-protocol.md) — Comm 通信机制
- [05-Widget系统](../concepts/05-widget-system.md) — Widget 完整指南
