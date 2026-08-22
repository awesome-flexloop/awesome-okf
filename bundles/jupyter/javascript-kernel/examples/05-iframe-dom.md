---
type: Tutorial
title: IFrame DOM 操作
description: 在 IFrame 模式下操作 DOM、访问主页面、创建可视化
tags: [iframe, dom, canvas, visualization, window, html, main-page]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
prerequisites: ["01-first-notebook"]
sources:
  - id: jk-backends
    title: runtime_backends.ts
  - id: jk-readme
    title: README.md
---

# IFrame DOM 操作

本教程仅适用于 **IFrame 模式**。IFrame 模式在隐藏的同源 iframe 中执行代码，可以访问完整的 DOM API，也可以通过 `window.parent` 操作 JupyterLab 主页面。

## ⚠️ 前置条件

- 内核必须选择 **JavaScript (IFrame)** 模式
- Worker 模式**不支持**任何 DOM 操作

## iframe 内 DOM 操作

代码运行在 iframe 的 `document` 中，可以创建和操作 DOM 元素：

### 创建和显示 DOM 元素

```javascript
// 创建元素
const div = document.createElement('div');
div.style.cssText = 'padding:20px;background:linear-gradient(135deg,#667eea,#764ba2);color:white;border-radius:12px;font-size:18px;text-align:center';
div.textContent = 'Hello from iframe DOM!';

// DOM 元素自动渲染
div
```

### Canvas 绘图

```javascript
const canvas = document.createElement('canvas');
canvas.width = 400;
canvas.height = 300;
const ctx = canvas.getContext('2d');

// 绘制背景
ctx.fillStyle = '#0f0f23';
ctx.fillRect(0, 0, 400, 300);

// 绘制星星
for (let i = 0; i < 100; i++) {
  ctx.beginPath();
  ctx.arc(Math.random() * 400, Math.random() * 300, Math.random() * 2, 0, Math.PI * 2);
  ctx.fillStyle = `rgba(255,255,255,${Math.random()})`;
  ctx.fill();
}

// 绘制文字
ctx.font = 'bold 32px Arial';
ctx.fillStyle = '#00d2ff';
ctx.textAlign = 'center';
ctx.fillText('🌟 Starry Night 🌟', 200, 150);

display(canvas);
```

### 创建交互元素

```javascript
const container = document.createElement('div');
container.style.cssText = 'padding:20px;background:#f8f9fa;border-radius:8px';

const input = document.createElement('input');
input.type = 'text';
input.placeholder = '输入文字...';
input.style.cssText = 'padding:8px 12px;border:1px solid #ddd;border-radius:4px;margin-right:8px;width:200px';

const btn = document.createElement('button');
btn.textContent = '添加';
btn.style.cssText = 'padding:8px 16px;background:#4A90D9;color:white;border:none;border-radius:4px;cursor:pointer';

const list = document.createElement('ul');
list.style.cssText = 'margin-top:12px;padding:0;list-style:none';

btn.onclick = () => {
  if (input.value.trim()) {
    const li = document.createElement('li');
    li.textContent = input.value;
    li.style.cssText = 'padding:8px;background:white;margin-top:4px;border-radius:4px;border-left:4px solid #4A90D9';
    list.appendChild(li);
    input.value = '';
  }
};

container.appendChild(input);
container.appendChild(btn);
container.appendChild(list);
display(container);
```

## 访问主页面 (window.parent)

IFrame 与主页面同源，可以通过 `window.parent` 访问 JupyterLab 的 window 对象：

### 在主页面创建浮动元素

```javascript
// 在主页面右上角创建一个浮动通知
const floatDiv = window.parent.document.createElement('div');
floatDiv.textContent = '来自 JavaScript Kernel 的通知！';
floatDiv.style.cssText = `
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 16px 24px;
  background: linear-gradient(135deg, #00b894, #00cec9);
  color: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  z-index: 99999;
  font-family: sans-serif;
  font-size: 14px;
  animation: slideIn 0.3s ease;
`;
window.parent.document.body.appendChild(floatDiv);

// 5秒后自动移除
setTimeout(() => floatDiv.remove(), 5000);
```

### 操作主页面 DOM

```javascript
// 修改主页面标题
window.parent.document.title = "JS Kernel Active ✨";

// 获取主页面中的元素
const mainArea = window.parent.document.querySelector('#jp-main-dock-panel');
console.log("主面板存在:", !!mainArea);
```

> ⚠️ 操作主页面 DOM 时要小心，避免破坏 JupyterLab 的 UI 结构。

## 使用外部可视化库（IFrame + Magic Imports）

### p5.js 风格 Canvas 动画

```javascript
// IFrame 模式 - 使用 canvas 创建动画
const canvas = document.createElement('canvas');
canvas.width = 400;
canvas.height = 300;
const ctx = canvas.getContext('2d');
display(canvas);

let t = 0;
function draw() {
  ctx.fillStyle = 'rgba(15, 15, 35, 0.1)';
  ctx.fillRect(0, 0, 400, 300);
  
  for (let i = 0; i < 5; i++) {
    const x = 200 + Math.sin(t + i) * 100 * Math.cos(t * 0.5);
    const y = 150 + Math.cos(t + i) * 80 * Math.sin(t * 0.7);
    const r = 20 + Math.sin(t * 2 + i) * 10;
    
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fillStyle = `hsl(${(t * 30 + i * 60) % 360}, 80%, 60%)`;
    ctx.fill();
  }
  
  t += 0.05;
  requestAnimationFrame(draw);
}
draw();
```

### SVG 动态图形

```javascript
// 创建 SVG 饼图
function createPieChart(data, width = 300, height = 300) {
  const total = data.reduce((s, d) => s + d.value, 0);
  const cx = width / 2, cy = height / 2, r = Math.min(width, height) / 2 - 20;
  
  let angle = -90;
  let paths = '';
  const colors = ['#ff6b6b','#4ecdc4','#45b7d1','#96ceb4','#ffeaa7','#dfe6e9','#fd79a8'];
  
  for (let i = 0; i < data.length; i++) {
    const slice = (data[i].value / total) * 360;
    const x1 = cx + r * Math.cos(angle * Math.PI / 180);
    const y1 = cy + r * Math.sin(angle * Math.PI / 180);
    angle += slice;
    const x2 = cx + r * Math.cos(angle * Math.PI / 180);
    const y2 = cy + r * Math.sin(angle * Math.PI / 180);
    const large = slice > 180 ? 1 : 0;
    
    paths += `<path d="M${cx},${cy} L${x1.toFixed(1)},${y1.toFixed(1)} A${r},${r} 0 ${large},1 ${x2.toFixed(1)},${y2.toFixed(1)} Z" fill="${colors[i % colors.length]}" stroke="white" stroke-width="2"/>`;
    
    // Label
    const midAngle = (angle - slice / 2) * Math.PI / 180;
    const lx = cx + (r * 0.65) * Math.cos(midAngle);
    const ly = cy + (r * 0.65) * Math.sin(midAngle);
    paths += `<text x="${lx.toFixed(1)}" y="${ly.toFixed(1)}" text-anchor="middle" fill="white" font-size="12" font-family="Arial" font-weight="bold">${data[i].label}</text>`;
  }
  
  return `<svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">${paths}</svg>`;
}

display(createPieChart([
  { label: 'A', value: 35 },
  { label: 'B', value: 25 },
  { label: 'C', value: 20 },
  { label: 'D', value: 20 }
]));
```

## 在 iframe 中注入样式

```javascript
// 在 iframe 中创建样式
const style = document.createElement('style');
style.textContent = `
  .card {
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    margin: 8px 0;
    transition: transform 0.2s;
  }
  .card:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,0.15); }
  .card-blue { background: linear-gradient(135deg, #667eea, #764ba2); color: white; }
  .card-green { background: linear-gradient(135deg, #11998e, #38ef7d); color: white; }
  .card-orange { background: linear-gradient(135deg, #f093fb, #f5576c); color: white; }
`;
document.head.appendChild(style);

// 创建卡片
const container = document.createElement('div');
container.innerHTML = `
  <div class="card card-blue"><h3>🚀 快速</h3><p>浏览器端即时执行</p></div>
  <div class="card card-green"><h3>🎨 丰富</h3><p>HTML/SVG/Canvas 全支持</p></div>
  <div class="card card-orange"><h3>🔗 互联</h3><p>window.parent 访问主页</p></div>
`;
display(container);
```

## 注意事项

1. **DOM 元素创建在 iframe 的 document 中**，不在主页面的 document 中
2. **display(canvas/div)** 会将元素移动到 Notebook 输出区域显示
3. **window.parent** 访问主页面时，元素创建在主页面 document 中，需要手动管理生命周期
4. **setInterval/requestAnimationFrame** 在输出区域滚动离开视图时仍会运行，注意清理
5. **Worker 模式**下 `document` 和 `window` 不可用，任何 DOM 操作都会抛出 ReferenceError

## 清理资源

创建动画或定时器时记得清理：

```javascript
// 创建一个简单的动画并返回停止函数
const canvas = document.createElement('canvas');
canvas.width = 200;
canvas.height = 200;
const ctx = canvas.getContext('2d');
display(canvas);

let angle = 0;
let animId;
function animate() {
  ctx.fillStyle = '#1a1a2e';
  ctx.fillRect(0, 0, 200, 200);
  ctx.save();
  ctx.translate(100, 100);
  ctx.rotate(angle);
  ctx.fillStyle = '#00d2ff';
  ctx.fillRect(-30, -30, 60, 60);
  ctx.restore();
  angle += 0.05;
  animId = requestAnimationFrame(animate);
}
animate();

// 停止动画（在新单元格执行）
// cancelAnimationFrame(animId);
```

## 相关文档

- [04-运行时后端](../concepts/04-runtime-backends.md) — IFrame/Worker 架构差异
- [04-富媒体输出](04-rich-output.md) — display() 输出 HTML/SVG
- [02-Magic Imports](02-magic-imports.md) — 导入可视化库
