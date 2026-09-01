---
type: Tutorial
title: Magic Imports
description: 使用 ES import 语法导入 npm 包，从 CDN 自动加载第三方库
tags: [import, npm, cdn, esm, modules, dependencies, magic-imports]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
prerequisites: ["01-first-notebook"]
sources:
  - id: jk-executor
    title: executor.ts
  - id: jk-readme
    title: README.md
---

# Magic Imports

Magic Imports 是 JavaScript Kernel 的核心特性，让你可以直接使用 ES `import` 语法导入 npm 包，内核自动通过 jsdelivr CDN 加载 ESM 版本的包。

## 基本用法

### 默认导入

```javascript
import confetti from 'canvas-confetti';
confetti();  // 触发彩纸动画！
```

### 命名导入

```javascript
import { range, random } from 'lodash-es';
console.log(range(1, 10));
console.log("Random:", random(0, 100));
```

### 命名空间导入

```javascript
import * as d3 from 'd3';
console.log("d3 version:", d3.version);
```

### 仅副作用导入

```javascript
import 'canvas-confetti';  // 仅加载模块，不导入任何绑定
```

## 导入流行库示例

### 数据处理

```javascript
import Papa from 'papaparse';

const csv = `name,age,city
Alice,30,Beijing
Bob,25,Shanghai
Charlie,35,Shenzhen`;

const result = Papa.parse(csv, { header: true, dynamicTyping: true });
console.log(result.data);
```

### 日期处理

```javascript
import dayjs from 'dayjs';

console.log("Now:", dayjs().format('YYYY-MM-DD HH:mm:ss'));
console.log("Tomorrow:", dayjs().add(1, 'day').format('YYYY-MM-DD'));
console.log("From now:", dayjs('2026-12-31').fromNow());
```

### 工具函数

```javascript
import _ from 'lodash-es';

const users = [
  { name: 'Alice', age: 30, active: true },
  { name: 'Bob', age: 25, active: false },
  { name: 'Charlie', age: 35, active: true }
];

console.log("Active users:", _.filter(users, 'active').map(u => u.name));
console.log("Average age:", _.meanBy(users, 'age'));
```

### 颜色处理

```javascript
import chroma from 'chroma-js';

const color = chroma('hotpink');
console.log("Hex:", color.hex());
console.log("RGB:", color.rgb());
console.log("Darken:", color.darken(1).hex());
console.log("Brighten:", color.brighten(1).hex());
```

### UUID 生成

```javascript
import { v4 as uuidv4 } from 'uuid';

console.log("UUID:", uuidv4());
console.log("Another:", uuidv4());
```

### Markdown 渲染

```javascript
import { marked } from 'marked';

const md = `
# Hello Markdown

This is **bold** and this is *italic*.

- Item 1
- Item 2
- Item 3
`;

display(marked(md), { raw_mimetype: 'text/html' });
```

## 导入后跨单元格使用

Import 的绑定会自动注入到全局作用域，可以在后续单元格中直接使用：

```javascript
// 单元格1：导入
import confetti from 'canvas-confetti';
import { marked } from 'marked';
```

```javascript
// 单元格2：直接使用，无需再次 import
confetti({ particleCount: 100, spread: 70 });
display(marked("**Already imported!**"), { raw_mimetype: 'text/html' });
```

## 指定包版本

```javascript
import React from 'react@18.2.0';
console.log(React.version);
```

```javascript
import lodash from 'lodash@4.17.21';
console.log(lodash.VERSION);
```

## 从 URL 直接导入

除了 npm 包名，还可以直接从任意 URL 导入 ES Module：

```javascript
// 从 unpkg 导入
import React from 'https://esm.sh/react@18';
console.log("React:", React.version);
```

```javascript
// 从 esm.sh 导入
import _ from 'https://esm.sh/lodash-es';
console.log(_.camelCase('hello world'));
```

```javascript
// 导入自定义模块（需要配置 CORS）
import { myFunction } from 'https://my-cdn.com/my-module.js';
```

## IFrame 模式下的 DOM 库

IFrame 模式可以操作 DOM，适合可视化库：

### Canvas Confetti

```javascript
import confetti from 'canvas-confetti';

// 基础彩纸
confetti();

// 自定义彩纸
confetti({
  particleCount: 150,
  spread: 100,
  origin: { y: 0.6 },
  colors: ['#ff0000', '#00ff00', '#0000ff']
});
```

### 使用 Canvas 绘图

```javascript
// IFrame 模式 - 创建 canvas 并显示
const canvas = document.createElement('canvas');
canvas.width = 400;
canvas.height = 300;
const ctx = canvas.getContext('2d');

// 绘制渐变背景
const gradient = ctx.createLinearGradient(0, 0, 400, 300);
gradient.addColorStop(0, '#667eea');
gradient.addColorStop(1, '#764ba2');
ctx.fillStyle = gradient;
ctx.fillRect(0, 0, 400, 300);

// 绘制圆形
ctx.beginPath();
ctx.arc(200, 150, 80, 0, Math.PI * 2);
ctx.fillStyle = 'white';
ctx.fill();

display(canvas);
```

> ⚠️ DOM 操作仅在 IFrame 模式下可用。Worker 模式下没有 `document` 和 `window`。

## 常见问题

### Q: 为什么 import 语句需要特殊处理？

普通浏览器中的 `import` 只支持 URL 和相对路径，不支持裸模块名（如 `'lodash'`）。JavaScript Kernel 通过 AST 转换将裸模块名重写为 CDN URL，并转换为 `await import()` 动态导入，这就是 "Magic" 的由来。

### Q: 导入的包是哪个版本？

不指定版本时，jsdelivr 返回包的最新版本。建议在重要项目中指定版本号以保证可复现性。

### Q: 为什么有些包导入失败？

1. 包没有提供 ESM 版本（只有 CommonJS）
2. 包有 Node.js 依赖（如 `fs`、`path`），在浏览器中不可用
3. CDN 暂时不可用
4. CORS 问题（自定义 URL 需要 CORS 头）

### Q: 可以导入 TypeScript 包吗？

不能直接导入 `.ts` 文件。需要使用已经编译为 JavaScript 的包。

### Q: 相对路径导入怎么用？

```javascript
// 相对路径相对于内核的 baseUrl（通常是 JupyterLite 站点根目录）
import { myFunc } from './my-module.js';
```

这需要文件部署在 JupyterLite 站点中。

## 相关文档

- [03-执行模型](../concepts/03-execution-model.md#magic-imports-_rewriteimportstatements) — Magic Imports 转换原理
- [09-常见问题](../concepts/09-faq-limitations.md#magic-imports-相关) — Magic Imports 常见问题
- [05-IFrame DOM 操作](05-iframe-dom.md) — IFrame 模式下的 DOM 库使用
