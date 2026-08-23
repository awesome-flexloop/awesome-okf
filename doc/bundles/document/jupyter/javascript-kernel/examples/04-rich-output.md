---
type: Tutorial
title: 富媒体输出
description: HTML、SVG、图片、Markdown、LaTeX、JSON 等多种输出格式
tags: [output, mime, html, svg, markdown, latex, display, visualization]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
prerequisites: ["01-first-notebook"]
sources:
  - id: jk-display
    title: display.ts
  - id: jk-executor
    title: executor.ts
---

# 富媒体输出

JavaScript Kernel 支持多种富媒体输出格式。本教程展示各种输出类型的使用方法。

## HTML 输出

### 自动识别 HTML 字符串

以 `<` 开头并以 `>` 结尾的字符串会自动识别为 HTML：

```javascript
"<h1 style='color:#4A90D9'>标题</h1>"
```

```javascript
`<div style='padding:20px;background:linear-gradient(135deg,#667eea,#764ba2);color:white;border-radius:10px'>
  <h2>渐变卡片</h2>
  <p>这是通过 HTML 输出的富内容</p>
</div>`
```

### 使用 display() 输出 HTML

```javascript
display("<b>粗体</b> <i>斜体</i> <u>下划线</u>");
```

### 创建表格

```javascript
const data = [
  { name: 'Alice', score: 95, grade: 'A' },
  { name: 'Bob', score: 87, grade: 'B' },
  { name: 'Charlie', score: 92, grade: 'A' }
];

let html = '<table style="border-collapse:collapse;width:100%">';
html += '<tr style="background:#4A90D9;color:white"><th style="padding:8px;border:1px solid #ddd">Name</th><th style="padding:8px;border:1px solid #ddd">Score</th><th style="padding:8px;border:1px solid #ddd">Grade</th></tr>';
for (const row of data) {
  const bg = row.grade === 'A' ? '#e8f5e9' : '#fff3e0';
  html += `<tr style="background:${bg}"><td style="padding:8px;border:1px solid #ddd">${row.name}</td><td style="padding:8px;border:1px solid #ddd;text-align:center">${row.score}</td><td style="padding:8px;border:1px solid #ddd;text-align:center">${row.grade}</td></tr>`;
}
html += '</table>';
display(html);
```

## Markdown 输出

使用 `raw_mimetype` 指定 Markdown 格式：

```javascript
const md = `
# JavaScript Kernel

## 特性列表

- ✅ 浏览器端执行
- ✅ Magic Imports
- ✅ 内置 Widgets
- ✅ 顶层 await

> 纯浏览器中的 JavaScript Notebook 体验
`;

display(md, { raw_mimetype: 'text/markdown' });
```

## LaTeX 输出

```javascript
display("$$\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}$$", {
  raw_mimetype: 'text/latex'
});
```

```javascript
display("E = mc^2", { raw_mimetype: 'text/latex' });
```

> 注意：LaTeX 渲染需要前端安装 MathJax 或 KaTeX 扩展。

## SVG 输出

### 直接输出 SVG 字符串

```javascript
const svg = `
<svg width="200" height="200" viewBox="0 0 200 200">
  <defs>
    <radialGradient id="grad1" cx="50%" cy="50%" r="50%">
      <stop offset="0%" style="stop-color:#ff6b6b;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#ee5a24;stop-opacity:1" />
    </radialGradient>
  </defs>
  <circle cx="100" cy="100" r="80" fill="url(#grad1)"/>
  <text x="100" y="110" text-anchor="middle" fill="white" font-size="24" font-family="Arial">SVG</text>
</svg>`;
display(svg);
```

### 使用 _toSvg() 方法

```javascript
class PieChart {
  constructor(data) { this.data = data; }
  _toSvg() {
    const total = this.data.reduce((s, d) => s + d.value, 0);
    let angle = 0;
    let paths = '';
    const cx = 100, cy = 100, r = 80;
    const colors = ['#ff6b6b','#4ecdc4','#45b7d1','#96ceb4','#ffeaa7','#dfe6e9'];
    for (let i = 0; i < this.data.length; i++) {
      const slice = (this.data[i].value / total) * 360;
      const x1 = cx + r * Math.cos((angle - 90) * Math.PI / 180);
      const y1 = cy + r * Math.sin((angle - 90) * Math.PI / 180);
      angle += slice;
      const x2 = cx + r * Math.cos((angle - 90) * Math.PI / 180);
      const y2 = cy + r * Math.sin((angle - 90) * Math.PI / 180);
      const large = slice > 180 ? 1 : 0;
      paths += `<path d="M${cx},${cy} L${x1},${y1} A${r},${r} 0 ${large},1 ${x2},${y2} Z" fill="${colors[i % colors.length]}"/>`;
    }
    return `<svg width="200" height="200" viewBox="0 0 200 200">${paths}</svg>`;
  }
}

display(new PieChart([
  { label: 'A', value: 30 },
  { label: 'B', value: 20 },
  { label: 'C', value: 50 }
]));
```

## Canvas 输出（IFrame 模式）

IFrame 模式下创建的 canvas 元素会直接渲染：

```javascript
const canvas = document.createElement('canvas');
canvas.width = 400;
canvas.height = 200;
const ctx = canvas.getContext('2d');

// 背景
ctx.fillStyle = '#1a1a2e';
ctx.fillRect(0, 0, 400, 200);

// 绘制正弦曲线
ctx.beginPath();
ctx.strokeStyle = '#00d2ff';
ctx.lineWidth = 2;
for (let x = 0; x < 400; x++) {
  const y = 100 + 50 * Math.sin(x * 0.03);
  x === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
}
ctx.stroke();

// 绘制余弦曲线
ctx.beginPath();
ctx.strokeStyle = '#ff6b6b';
for (let x = 0; x < 400; x++) {
  const y = 100 + 50 * Math.cos(x * 0.03);
  x === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
}
ctx.stroke();

display(canvas);
```

## JSON 输出

对象和数组自动以 JSON 格式输出：

```javascript
{
  name: "JavaScript Kernel",
  version: "0.1.0",
  features: ["iframe", "worker", "widgets", "magic-imports"],
  runtime: {
    iframe: true,
    worker: true
  }
}
```

## console.table 表格输出

```javascript
const users = [
  { id: 1, name: 'Alice', age: 30, city: 'Beijing' },
  { id: 2, name: 'Bob', age: 25, city: 'Shanghai' },
  { id: 3, name: 'Charlie', age: 35, city: 'Shenzhen' }
];
console.table(users);
```

## display_id 动态更新

使用 `display_id` 更新已有输出：

```javascript
// 动态时钟
for (let i = 0; i < 10; i++) {
  const time = new Date().toLocaleTimeString();
  display(`<div style="font-size:2em;text-align:center;font-family:monospace;color:#4A90D9">${time}</div>`, {
    display_id: 'clock',
    raw_mimetype: 'text/html'
  });
  await new Promise(r => setTimeout(r, 1000));
}
```

```javascript
// 进度条动画
for (let i = 0; i <= 100; i += 2) {
  const width = i;
  const color = i < 30 ? '#ff6b6b' : i < 70 ? '#ffa502' : '#2ed573';
  display(`
    <div style="width:100%;background:#f1f2f6;border-radius:10px;overflow:hidden">
      <div style="width:${width}%;background:${color};padding:8px 0;color:white;text-align:center;font-weight:bold;transition:width 0.1s">${i}%</div>
    </div>
  `, { display_id: 'progress-bar', raw_mimetype: 'text/html' });
  await new Promise(r => setTimeout(r, 50));
}
```

## 自定义 _toMime 输出

对象可以定义 `_toMime()` 方法完全控制输出：

```javascript
class DataFrame {
  constructor(data, columns) {
    this.data = data;
    this.columns = columns || Object.keys(data[0] || {});
  }

  _toHtml() {
    let html = '<table style="border-collapse:collapse;font-size:0.9em">';
    html += '<thead><tr style="background:#2d3436;color:white">';
    for (const col of this.columns) {
      html += `<th style="padding:8px 12px;border:1px solid #ddd">${col}</th>`;
    }
    html += '</tr></thead><tbody>';
    for (let i = 0; i < Math.min(this.data.length, 20); i++) {
      const bg = i % 2 === 0 ? '#f9f9f9' : 'white';
      html += `<tr style="background:${bg}">`;
      for (const col of this.columns) {
        html += `<td style="padding:6px 12px;border:1px solid #ddd">${this.data[i][col]}</td>`;
      }
      html += '</tr>';
    }
    if (this.data.length > 20) {
      html += `<tr><td colspan="${this.columns.length}" style="padding:8px;text-align:center;color:#888">... ${this.data.length - 20} more rows</td></tr>`;
    }
    html += '</tbody></table>';
    return html;
  }

  _toMime() {
    return {
      'text/plain': `DataFrame(${this.data.length} rows × ${this.columns.length} columns)`,
      'text/html': this._toHtml(),
      'application/json': { columns: this.columns, rowCount: this.data.length }
    };
  }
}

const df = new DataFrame([
  { product: 'Widget A', sales: 1200, revenue: 24000 },
  { product: 'Widget B', sales: 800, revenue: 32000 },
  { product: 'Widget C', sales: 1500, revenue: 45000 },
  { product: 'Widget D', sales: 600, revenue: 18000 }
]);
display(df);
```

## 函数源码显示

函数会自动显示语法高亮的源码：

```javascript
function quickSort(arr) {
  if (arr.length <= 1) return arr;
  const pivot = arr[Math.floor(arr.length / 2)];
  const left = arr.filter(x => x < pivot);
  const middle = arr.filter(x => x === pivot);
  const right = arr.filter(x => x > pivot);
  return [...quickSort(left), ...middle, ...quickSort(right)];
}

quickSort  // 自动显示函数源码
```

## 错误输出

```javascript
try {
  throw new Error("示例错误消息");
} catch(e) {
  e  // 显示错误对象（包含堆栈信息）
}
```

## 相关文档

- [07-富媒体输出系统](../concepts/07-display-system.md) — display() 和 MIME 类型详解
- [03-执行模型](../concepts/03-execution-model.md#mime-富输出-getmimebundle) — getMimeBundle 类型处理规则
- [03-使用 Widgets](03-using-widgets.md) — Output widget 输出
