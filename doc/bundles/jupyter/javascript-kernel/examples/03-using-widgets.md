---
type: Tutorial
title: 使用 Widgets
description: 创建交互式滑块、按钮、进度条和容器控件
tags: [widgets, ui, interactive, slider, button, controls, ipywidgets]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
prerequisites: ["01-first-notebook"]
sources:
  - id: jk-widget
    title: widgets/widget.ts
  - id: jk-widget-int
    title: widgets/widget_int.ts
  - id: jk-widget-btn
    title: widgets/widget_button.ts
  - id: jk-widget-out
    title: widgets/widget_output.ts
---

# 使用 Widgets

JavaScript Kernel 内置了完整的 ipywidgets 兼容控件集，通过 `Jupyter.widgets` 命名空间访问。本教程展示常用 Widget 的使用方法。

## 获取控件类

所有控件通过 `Jupyter.widgets` 获取：

```javascript
const { IntSlider, Button, Output, HBox, VBox, jslink } = Jupyter.widgets;
```

## 基础控件

### IntSlider — 整数滑块

```javascript
const { IntSlider } = Jupyter.widgets;

const slider = new IntSlider({
  value: 50,
  min: 0,
  max: 100,
  step: 5,
  description: '数值:',
  continuous_update: true
});

display(slider);
```

```javascript
// 读取当前值
console.log("当前值:", slider.value);

// 监听变化
slider.observe(({ new: value }) => {
  console.log("值变为:", value);
}, 'value');
```

### FloatSlider — 浮点数滑块

```javascript
const { FloatSlider } = Jupyter.widgets;

const fslider = new FloatSlider({
  value: 3.14,
  min: 0,
  max: 10,
  step: 0.01,
  description: '浮点数:',
  readout_format: '.2f'
});

display(fslider);
```

### IntRangeSlider — 范围滑块

```javascript
const { IntRangeSlider } = Jupyter.widgets;

const range = new IntRangeSlider({
  value: [20, 80],
  min: 0,
  max: 100,
  step: 1,
  description: '范围:'
});

display(range);
```

```javascript
// 读取范围
console.log("范围:", range.value);  // [20, 80]

range.observe(({ new: val }) => {
  console.log(`范围: ${val[0]} ~ ${val[1]}`);
}, 'value');
```

### Checkbox — 复选框

```javascript
const { Checkbox } = Jupyter.widgets;

const cb = new Checkbox({
  value: false,
  description: '启用高级选项'
});

display(cb);

cb.observe(({ new: val }) => {
  console.log("复选框:", val ? "已勾选" : "未勾选");
}, 'value');
```

### Dropdown — 下拉选择

```javascript
const { Dropdown } = Jupyter.widgets;

const dropdown = new Dropdown({
  options: ['北京', '上海', '广州', '深圳'],
  value: '北京',
  description: '城市:'
});

display(dropdown);

dropdown.observe(({ new: val }) => {
  console.log("选择了:", val);
}, 'value');
```

带值的 options（label-value 对）：

```javascript
const { Dropdown } = Jupyter.widgets;

const colorPicker = new Dropdown({
  options: [
    ['红色', '#ff0000'],
    ['绿色', '#00ff00'],
    ['蓝色', '#0000ff']
  ],
  value: '#ff0000',
  description: '颜色:'
});

display(colorPicker);
```

### RadioButtons — 单选按钮

```javascript
const { RadioButtons } = Jupyter.widgets;

const radio = new RadioButtons({
  options: ['小', '中', '大'],
  value: '中',
  description: '尺寸:'
});

display(radio);
```

### Text / Textarea — 文本输入

```javascript
const { Text, Textarea } = Jupyter.widgets;

const nameInput = new Text({
  value: '',
  placeholder: '输入你的名字',
  description: '姓名:'
});

const bioInput = new Textarea({
  value: '',
  placeholder: '介绍一下你自己...',
  description: '简介:',
  rows: 4
});

display(nameInput);
display(bioInput);
```

### ColorPicker — 颜色选择器

```javascript
const { ColorPicker } = Jupyter.widgets;

const picker = new ColorPicker({
  value: '#4A90D9',
  description: '选择颜色:',
  concise: false
});

display(picker);

picker.observe(({ new: color }) => {
  console.log("颜色:", color);
}, 'value');
```

## Button — 按钮

```javascript
const { Button, Output } = Jupyter.widgets;

const btn = new Button({
  description: '点击我',
  button_style: 'success',  // 'primary', 'success', 'info', 'warning', 'danger', ''
  icon: 'check',
  tooltip: '点击查看效果'
});

const out = new Output();
display(btn);
display(out);

let count = 0;
btn.onClick(() => {
  count++;
  out.appendStdout(`点击了 ${count} 次\n`);
});
```

### 按钮样式

| button_style | 颜色 |
|-------------|------|
| `'primary'` | 蓝色 |
| `'success'` | 绿色 |
| `'info'` | 浅蓝 |
| `'warning'` | 橙色 |
| `'danger'` | 红色 |
| `''` | 默认灰色 |

## IntProgress — 进度条

```javascript
const { IntProgress, Button } = Jupyter.widgets;

const progress = new IntProgress({
  value: 0,
  min: 0,
  max: 100,
  description: '加载中:',
  bar_style: 'info'
});

const startBtn = new Button({ description: '开始', button_style: 'primary' });

display(progress);
display(startBtn);

startBtn.onClick(async () => {
  for (let i = 0; i <= 100; i += 5) {
    progress.value = i;
    await new Promise(r => setTimeout(r, 100));
  }
  progress.bar_style = 'success';
  progress.description = '完成!';
});
```

## Output — 输出区域

Output widget 用于捕获和显示程序化输出：

```javascript
const { Button, Output } = Jupyter.widgets;

const out = new Output();
const logBtn = new Button({ description: '记录日志', button_style: 'primary' });
const clearBtn = new Button({ description: '清除', button_style: 'warning' });

display(logBtn);
display(clearBtn);
display(out);

logBtn.onClick(() => {
  const time = new Date().toLocaleTimeString();
  out.appendStdout(`[${time}] 日志消息\n`);
  if (Math.random() > 0.7) {
    out.appendStderr(`[${time}] 警告：随机错误\n`);
  }
});

clearBtn.onClick(() => {
  out.clearOutput();
});
```

### capture — 捕获输出

```javascript
const { Button, Output } = Jupyter.widgets;

const out = new Output();
const btn = new Button({ description: '执行计算', button_style: 'success' });

display(btn);
display(out);

const calculate = out.capture(() => {
  console.log("开始计算...");
  for (let i = 0; i < 5; i++) {
    console.log(`步骤 ${i + 1}: ${Math.random().toFixed(4)}`);
  }
  console.log("计算完成！");
});

btn.onClick(calculate);
```

### appendDisplayData — 追加富内容

```javascript
const { Output } = Jupyter.widgets;

const out = new Output();
display(out);

out.appendDisplayData({
  'text/html': '<h3 style="color:green">✓ 成功</h3>',
  'text/plain': '✓ 成功'
});
```

## 容器控件

### HBox — 水平布局

```javascript
const { IntSlider, HBox, Label } = Jupyter.widgets;

const rSlider = new IntSlider({ value: 128, min: 0, max: 255 });
const gSlider = new IntSlider({ value: 128, min: 0, max: 255 });
const bSlider = new IntSlider({ value: 128, min: 0, max: 255 });

const controls = new HBox({
  children: [
    new Label({ value: 'R:' }), rSlider,
    new Label({ value: 'G:' }), gSlider,
    new Label({ value: 'B:' }), bSlider
  ]
});

display(controls);
```

### VBox — 垂直布局

```javascript
const { IntSlider, VBox, Label } = Jupyter.widgets;

const sliders = [
  { name: '红色', slider: new IntSlider({ value: 255, max: 255 }) },
  { name: '绿色', slider: new IntSlider({ value: 128, max: 255 }) },
  { name: '蓝色', slider: new IntSlider({ value: 64, max: 255 }) }
];

const form = new VBox({
  children: sliders.map(({ name, slider }) =>
    new HBox({ children: [new Label({ value: name + ':' }), slider] })
  )
});

display(form);
```

### Accordion — 折叠面板

```javascript
const { IntSlider, Text, Accordion } = Jupyter.widgets;

const panel1 = new IntSlider({ description: '设置1' });
const panel2 = new Text({ description: '设置2', value: '默认值' });

const accordion = new Accordion({
  children: [panel1, panel2],
  selected_index: 0,
  titles: ['数值设置', '文本设置']
});

display(accordion);
```

### Tab — 标签页

```javascript
const { IntSlider, Text, Tab } = Jupyter.widgets;

const tab1 = new IntSlider({ description: '参数A', value: 50 });
const tab2 = new Text({ description: '参数B', value: 'hello' });

const tabs = new Tab({
  children: [tab1, tab2],
  selected_index: 0,
  titles: ['数值', '文本']
});

display(tabs);
```

## jslink — 双向绑定

将两个控件的属性双向绑定：

```javascript
const { IntSlider, IntText, jslink, HBox, Label } = Jupyter.widgets;

const slider = new IntSlider({ value: 50, min: 0, max: 100 });
const text = new IntText({ value: 50 });

jslink([slider, 'value'], [text, 'value']);

display(new HBox({ children: [new Label({ value: '滑块:' }), slider, new Label({ value: '输入:' }), text] }));
```

拖动滑块时文本框自动更新，修改文本框时滑块也自动更新。

### jsdlink — 单向绑定

```javascript
const { jsdlink } = Jupyter.widgets;

// source 变化时更新 target，但 target 变化不影响 source
jsdlink([slider, 'value'], [progress, 'value']);
```

## 综合示例：RGB 调色板

```javascript
const { IntSlider, ColorPicker, VBox, HBox, Label, Output } = Jupyter.widgets;

const r = new IntSlider({ value: 74, min: 0, max: 255, description: 'R:' });
const g = new IntSlider({ value: 144, min: 0, max: 255, description: 'G:' });
const b = new IntSlider({ value: 217, min: 0, max: 255, description: 'B:' });
const preview = new ColorPicker({ value: '#4A90D9', description: '颜色:' });
const out = new Output();

function updateColor() {
  const hex = '#' + [r.value, g.value, b.value]
    .map(v => v.toString(16).padStart(2, '0'))
    .join('');
  preview.value = hex;
  out.clearOutput();
  out.appendDisplayData({
    'text/html': `<div style="width:100%;height:60px;background:${hex};border-radius:8px;border:1px solid #ccc"></div>`,
    'text/plain': `RGB(${r.value}, ${g.value}, ${b.value}) = ${hex}`
  });
}

r.observe(updateColor, 'value');
g.observe(updateColor, 'value');
b.observe(updateColor, 'value');
updateColor();

display(new VBox({ children: [
  new HBox({ children: [new Label({ value: '调色板' })] }),
  r, g, b, preview, out
]}));
```

## 属性参考

所有 DOMWidget 共享的属性：

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `description` | string | `''` | 控件描述标签 |
| `disabled` | boolean | `false` | 是否禁用 |
| `visible` | boolean | `true` | 是否可见 |
| `layout` | Layout | — | 布局配置 |
| `style` | Style | — | 样式配置 |
| `tooltip` | string | `''` | 鼠标悬停提示 |

## 相关文档

- [05-Widget系统](../concepts/05-widget-system.md) — Widget 类层次和完整 API
- [06-Comm 协议](../concepts/06-comm-protocol.md) — Widget 底层通信
- [04-富媒体输出](04-rich-output.md) — Output widget 高级用法
