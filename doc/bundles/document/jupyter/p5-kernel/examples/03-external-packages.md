---
type: Example
title: 外部 npm 包导入
description: 在 p5-kernel 中使用 ES import 语法导入外部 npm 包（canvas-confetti、dayjs 等），组合 p5.js 与第三方库创建丰富的交互效果
tags: [esm, import, npm, external-packages, canvas-confetti, dayjs, interop]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T17:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: ext-pkg-nb
    resource: https://github.com/jupyterlite/p5-kernel/blob/main/examples/external-packages.ipynb
    title: examples/external-packages.ipynb
  - id: kernel
    resource: /references/kernel-source.md
    title: P5Kernel 类 API 信源
---

## 目标

学习如何在 p5-kernel 中通过 ES Module `import` 语法导入外部 npm 包，将第三方库与 p5.js 结合创建更丰富的创意编程效果。

## 支持的 Import 语法

p5-kernel 继承了 JavaScriptKernel 的 import 处理能力，支持多种导入方式：

```javascript
// 默认导入（npm 包名）
import confetti from 'canvas-confetti';

// 命名导入
import { shuffle, debounce } from 'lodash-es';

// 命名空间导入
import * as d3 from 'd3';

// 从 GitHub 导入
import something from 'gh/user/repo/file.js';

// 直接 URL 导入（不做转换）
import lib from 'https://example.com/lib.js';
```

npm 包会自动从 jsDelivr CDN 加载，无需安装。

## 示例 1：canvas-confetti 庆祝特效

### 导入并验证包

```javascript
// 从 npm 导入 canvas-confetti（自动从 jsDelivr 获取）
import confetti from 'canvas-confetti';

// 验证加载成功
typeof confetti
```

执行后应输出 `'function'`。

### 创建交互动画

```javascript
let clicks = 0;

function setup() {
  createCanvas(innerWidth, innerHeight);
  textAlign(CENTER, CENTER);
  textSize(20);
}

function draw() {
  background(30, 30, 50);
  fill(255);
  text('Click anywhere for confetti!', width / 2, height / 2 - 20);
  text('Clicks: ' + clicks, width / 2, height / 2 + 20);
}

function mousePressed() {
  clicks++;

  // 在点击位置发射彩纸
  confetti({
    particleCount: 50,
    spread: 60,
    origin: {
      x: mouseX / width,
      y: mouseY / height
    }
  });
}
```

### 渲染

```javascript
%show
```

点击画布任意位置会触发彩色纸屑爆炸效果，同时显示点击计数。

## 示例 2：Day.js 日期处理

### 导入 Day.js

```javascript
import dayjs from 'dayjs';

const now = dayjs();
console.log('Current time:', now.format('YYYY-MM-DD HH:mm:ss'));
console.log('One week from now:', now.add(7, 'day').format('MMMM D, YYYY'));
```

执行 cell 后，输出区域会显示当前时间和一周后的日期。

### 结合 p5.js 显示时钟

```javascript
import dayjs from 'dayjs';

function setup() {
  createCanvas(400, 200);
  textAlign(CENTER, CENTER);
  textSize(32);
}

function draw() {
  background(20);
  fill(0, 255, 200);
  let now = dayjs().format('HH:mm:ss');
  text(now, width / 2, height / 2);
}
```

```javascript
%show 400 200
```

会显示一个实时更新的数字时钟。

## Import 工作原理

Import 处理发生在两个阶段：

1. **代码注册阶段**：`executeRequest()` 调用 `executor.extractImports(code)` 提取 import 语句，去重存入 `_imports` 数组
2. **渲染阶段**：`%show` 时 `_magics()` 调用 `executor.generateImportCode(this._imports)` 生成实际的 import 加载代码，注入到 iframe 的 script 中

```
Cell 执行（Worker 中）
  ├─ super.executeRequest() → import 在 Worker 中解析（但 npm 包实际在 iframe 中加载）
  ├─ extractImports(code) → 记录到 _imports
  └─ registerCode(code, _codeRegistry)

%show 渲染（生成 iframe srcdoc）
  ├─ generateImportCode(_imports) → 生成 import 加载代码
  ├─ generateCodeFromRegistry(_codeRegistry) → 生成去重后的用户代码
  └─ iframe 中：bootstrap → imports → code → _start()
```

## 常用创意编程库推荐

| 库 | 用途 | Import 语句 |
|----|------|------------|
| [canvas-confetti](https://www.npmjs.com/package/canvas-confetti) | 庆祝彩纸特效 | `import confetti from 'canvas-confetti'` |
| [dayjs](https://www.npmjs.com/package/dayjs) | 轻量日期处理 | `import dayjs from 'dayjs'` |
| [matter-js](https://www.npmjs.com/package/matter-js) | 2D 物理引擎 | `import Matter from 'matter-js'` |
| [tweakpane](https://www.npmjs.com/package/tweakpane) | GUI 参数调优面板 | `import { Pane } from 'tweakpane'` |
| [roughjs](https://www.npmjs.com/package/roughjs) | 手绘风格图形 | `import rough from 'roughjs'` |
| [lodash-es](https://www.npmjs.com/package/lodash-es) | 工具函数库 | `import { shuffle, debounce } from 'lodash-es'` |

## 注意事项

1. **CDN 依赖**：npm 包从 jsDelivr CDN 动态加载，需要网络连接
2. **浏览器兼容**：只支持浏览器兼容的 ES Module 包，不支持 Node.js 内置模块（fs、path 等）
3. **包大小**：大包（如 d3、three.js）首次加载可能需要几秒
4. **Import 位置**：import 语句通常放在 cell 顶部，与普通 JavaScript 一致
5. **iframe 隔离**：import 的包在 iframe 中加载，Worker 侧的代码执行时可能还未加载——但通过 CodeRegistry 累积，`%show` 时所有 import 会在 iframe 中正确加载
6. **去重**：同一模块多次 import 只加载一次（按 source 去重）

## 相关概念

- [%show 魔法命令](../concepts/04-magic-commands.md)
- [P5Kernel 实现详解](../concepts/02-kernel-implementation.md)
- [架构概览](../concepts/01-architecture-overview.md)
- [第一个 p5 Sketch](01-first-sketch.md)
