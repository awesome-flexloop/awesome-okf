---
type: Concept
title: Widget 系统
description: 内置 ipywidgets 兼容层、Widget 基类、控件分类、事件系统和双向绑定
tags: [widgets, ipywidgets, ui, interact, events, binding, controls]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: jk-widget
    title: widgets/widget.ts
  - id: jk-widget-index
    title: widgets/index.ts
  - id: jk-widget-int
    title: widgets/widget_int.ts
  - id: jk-widget-btn
    title: widgets/widget_button.ts
  - id: jk-widget-out
    title: widgets/widget_output.ts
---

# Widget 系统

JavaScript Kernel 内置了一套完整的 [Jupyter Widgets](https://ipywidgets.readthedocs.io/)（ipywidgets）兼容实现。所有控件通过 `Jupyter.widgets` 命名空间访问，无需 Python 端支持，纯浏览器端即可创建交互式 UI。

## 获取 Widget 类

Widget 类在运行时动态绑定到 CommManager，通过 `Jupyter.widgets` 访问：

```javascript
const { IntSlider, Button, Output, HBox, jslink } = Jupyter.widgets;
```

> ⚠️ Widget 类**只能在 kernel 运行时内部使用**。在 kernel 外部（如前端扩展代码中）直接导入 Widget 类会抛出 "Widget manager not initialized" 错误。

## Widget 类层次结构

```
Widget (基类)
├── DOMWidget (DOM 控件基类)
│   ├── Layout (布局模型)
│   ├── Style / DescriptionStyle / SliderStyle / ... (样式模型)
│   ├── IntSlider / FloatSlider / FloatLogSlider (滑块)
│   ├── IntRangeSlider / FloatRangeSlider (范围滑块)
│   ├── IntProgress / FloatProgress (进度条)
│   ├── Play (播放控件)
│   ├── IntText / FloatText / BoundedIntText / BoundedFloatText (数值输入)
│   ├── Checkbox / ToggleButton / Valid (布尔控件)
│   ├── Dropdown / RadioButtons / Select / SelectMultiple (选择控件)
│   ├── ToggleButtons / SelectionSlider / SelectionRangeSlider (选择控件)
│   ├── Text / Textarea / Password / Combobox (文本输入)
│   ├── Label / HTML / HTMLMath (显示控件)
│   ├── Output (输出区域)
│   ├── Button (按钮)
│   ├── ColorPicker (颜色选择器)
│   ├── Box / HBox / VBox / GridBox (容器)
│   ├── Accordion / Tab / Stack (选择容器)
│   └── ...
└── Link / DirectionalLink (双向绑定)
```

## 可用控件清单

### 数值控件 (Numeric)

| 控件 | 说明 | 关键属性 |
|------|------|---------|
| `IntSlider` | 整数滑块 | value, min, max, step, description |
| `FloatSlider` | 浮点数滑块 | value, min, max, step, description |
| `FloatLogSlider` | 对数刻度滑块 | value, base, min, max |
| `IntRangeSlider` | 整数范围滑块 | value: [number, number], min, max |
| `FloatRangeSlider` | 浮点数范围滑块 | value: [number, number] |
| `Play` | 播放/动画控件 | value, min, max, step, interval, playing |
| `IntProgress` | 整数进度条 | value, min, max, description, bar_style |
| `FloatProgress` | 浮点数进度条 | value, min, max |
| `IntText` | 整数文本输入 | value, description |
| `FloatText` | 浮点数文本输入 | value, description |
| `BoundedIntText` | 有界整数输入 | value, min, max |
| `BoundedFloatText` | 有界浮点数输入 | value, min, max |

### 布尔控件 (Boolean)

| 控件 | 说明 |
|------|------|
| `Checkbox` | 复选框 |
| `ToggleButton` | 切换按钮 |
| `Valid` | 验证指示器（只读，显示当前值是否有效） |

### 选择控件 (Selection)

| 控件 | 说明 |
|------|------|
| `Dropdown` | 下拉选择 |
| `RadioButtons` | 单选按钮组 |
| `Select` | 列表选择 |
| `SelectMultiple` | 多选列表 |
| `ToggleButtons` | 切换按钮组 |
| `SelectionSlider` | 选择滑块 |
| `SelectionRangeSlider` | 范围选择滑块 |

### 字符串控件 (String)

| 控件 | 说明 |
|------|------|
| `Text` | 单行文本输入 |
| `Textarea` | 多行文本输入 |
| `Password` | 密码输入 |
| `Combobox` | 组合框（可输入+下拉） |

### 显示控件 (Display)

| 控件 | 说明 |
|------|------|
| `Label` | 文本标签 |
| `HTML` | HTML 显示 |
| `HTMLMath` | 数学公式显示 |
| `Output` | 输出捕获区域 |

### 按钮和颜色 (Button & Color)

| 控件 | 说明 |
|------|------|
| `Button` | 按钮（支持 onClick、icon、tooltip、button_style） |
| `ColorPicker` | 颜色选择器（concise 模式可选） |

### 布局与样式 (Layout & Style)

| 控件 | 说明 |
|------|------|
| `Layout` | 布局模型（width、height、margin、padding 等） |
| `Style` | 基础样式 |
| `DescriptionStyle` | 描述文字样式 |
| `SliderStyle` | 滑块样式 |
| `ProgressStyle` | 进度条样式 |
| `ButtonStyle` | 按钮样式 |
| `CheckboxStyle` | 复选框样式 |
| `TextStyle` | 文本控件样式 |
| `HTMLStyle` / `HTMLMathStyle` | HTML 控件样式 |
| `LabelStyle` | 标签样式 |

### 容器控件 (Containers)

| 控件 | 说明 |
|------|------|
| `Box` | 通用容器 |
| `HBox` | 水平布局容器 |
| `VBox` | 垂直布局容器 |
| `GridBox` | 网格布局容器 |
| `Accordion` | 手风琴（折叠面板） |
| `Tab` | 标签页 |
| `Stack` | 栈容器（一次只显示一个子元素） |

### 辅助函数 (Helpers)

| 函数 | 说明 |
|------|------|
| `jslink(source, target)` | JavaScript 双向绑定 |
| `jsdlink(source, target)` | JavaScript 单向（方向）绑定 |

## Widget 基类 API

### 构造函数

```javascript
new Widget(state?: Record<string, unknown>);
```

构造时传入初始状态（属性值），会合并 `_defaults()` 和 `_modelState()` 的默认值。构造函数自动：
1. 打开 `jupyter.widget` comm 通道
2. 发送初始状态到前端
3. 注册消息处理器

### 属性操作

```javascript
// 读取属性
const value = widget.get('value');

// 设置单个属性
widget.set('value', 42);

// 批量设置属性
widget.set({ value: 42, description: 'New Value' });
```

`set()` 检测值变化：值未改变时不发送消息；值改变时：
1. 更新内部状态 `_state`
2. 发送 `comm_msg`（method: 'update'）到前端
3. 触发 `change:propertyName` 事件
4. 触发 `change` 事件

> 💡 Widget 类也提供 ES getter/setter 语法糖（如 `slider.value = 42`），底层调用 `set('value', 42)`。

### 事件系统

```javascript
// 监听事件
widget.on(event, callback);

// 取消监听
widget.off(event, callback);

// 监听属性变化（ipywidgets 风格）
widget.observe(callback, names?);

// 取消观察
widget.unobserve(callback, names?);

// 关闭 widget
widget.close();
```

支持的事件：

| 事件 | 回调参数 | 触发时机 |
|------|---------|---------|
| `change:propName` | `(newValue, oldValue)` | 指定属性变化时 |
| `change` | `(changes: Array<[key, newVal, oldVal]>)` | 任意属性变化时 |
| `close` | `(data)` | comm 通道关闭时 |
| `click`（Button） | `()` | 按钮点击时 |
| `custom` | `(content, buffers)` | 收到自定义 comm 消息时 |

#### observe 回调签名

```javascript
widget.observe((change) => {
  console.log(change.name);   // 属性名
  console.log(change.new);    // 新值
  console.log(change.old);    // 旧值
  console.log(change.owner);  // widget 实例
  console.log(change.type);   // 'change'
}, 'value');
```

`names` 参数：
- 字符串：监听单个属性
- 字符串数组：监听多个属性
- `'*'` 或省略：监听所有属性

### commId

```javascript
widget.commId  // 返回 widget 的 comm/model ID（string）
```

## 显示 Widget

### 自动显示

Widget 作为单元格最后一条表达式时自动显示：

```javascript
const slider = new IntSlider({ value: 50, min: 0, max: 100 });
slider  // 自动显示
```

### 显式显示

使用全局 `display()` 函数：

```javascript
const slider = new IntSlider({ value: 50 });
display(slider);
```

### 不自动显示的情况

```javascript
const slider = new IntSlider({ value: 50 });
// 赋值语句不是表达式，不会自动显示
// 需要显式 display(slider)
```

## 控件示例

### 滑块联动进度条

```javascript
const { IntSlider, IntProgress, jslink } = Jupyter.widgets;

const slider = new IntSlider({ value: 50, min: 0, max: 100, description: 'Value:' });
const progress = new IntProgress({ value: 50, min: 0, max: 100, description: 'Progress:' });

display(slider);
display(progress);

jslink([slider, 'value'], [progress, 'value']);
```

### 按钮点击

```javascript
const { Button, Output } = Jupyter.widgets;

const btn = new Button({ description: 'Click Me!', button_style: 'success' });
const out = new Output();

display(btn);
display(out);

let count = 0;
btn.onClick(() => {
  count++;
  out.appendStdout(`Clicked ${count} times\n`);
});
```

### 容器布局

```javascript
const { IntSlider, HBox, VBox, Label } = Jupyter.widgets;

const slider1 = new IntSlider({ description: 'R' });
const slider2 = new IntSlider({ description: 'G' });
const slider3 = new IntSlider({ description: 'B' });

const controls = new VBox({
  children: [slider1, slider2, slider3]
});

display(controls);
```

### 使用 observe 监听变化

```javascript
const { IntSlider, Output } = Jupyter.widgets;

const slider = new IntSlider({ value: 50, min: 0, max: 100, description: 'Number:' });
const out = new Output();

display(slider);
display(out);

slider.observe(({ new: value }) => {
  out.clearOutput();
  out.appendStdout(`Value changed to: ${value}\n`);
  out.appendStdout(`Square: ${value * value}\n`);
}, 'value');
```

## Output Widget

`Output` widget 提供可编程的输出捕获区域。

### 方法

| 方法 | 说明 |
|------|------|
| `clearOutput(options?)` | 清除输出 |
| `appendStdout(text)` | 追加标准输出文本 |
| `appendStderr(text)` | 追加标准错误文本 |
| `appendDisplayData(data, metadata?)` | 追加富显示数据 |
| `capture(callback, options?)` | 捕获回调中的输出 |

### capture 使用方式

```javascript
// 方式1: 直接包裹函数
const wrapped = out.capture(() => {
  console.log("This goes to Output widget");
});
wrapped();

// 方式2: 作为装饰器
const fn = out.capture({ clearOutput: true })(() => {
  console.log("Cleared first, then this appears");
});
fn();
```

capture 支持嵌套（引用计数 `_captureDepth`），正确处理 Promise 异步操作。

## 自定义 Widget 的 model/view 信息

每个 Widget 子类通过静态属性声明对应的前端 model/view：

```typescript
class IntSlider extends _SliderBase {
  static override modelName = 'IntSliderModel';
  static override viewName = 'IntSliderView';
  static override modelModule = CONTROLS_MODULE;
  static override modelModuleVersion = CONTROLS_MODULE_VERSION;
  // viewModule 和 viewModuleVersion 继承自父类
}
```

前端需要 `@jupyter-widgets/controls` 和 `jupyterlab-widgets` 包来渲染这些 widget。

## 相关文档

- [06-Comm 协议](06-comm-protocol.md) — Widget 底层通信机制
- [03-使用 Widgets](../examples/03-using-widgets.md) — Widget 完整示例
- [04-富媒体输出](../examples/04-rich-output.md) — Output widget 使用
