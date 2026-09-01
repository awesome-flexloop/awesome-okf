---
type: Example
title: 第一个 p5 Sketch
description: 从零开始创建第一个 p5.js Notebook，定义变量、setup/draw 函数，使用 %show 渲染画布，实时调参
tags: [getting-started, first-sketch, setup, draw, basics, tutorial]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T17:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: intro-nb
    resource: https://github.com/jupyterlite/p5-kernel/blob/main/examples/intro.ipynb
    title: examples/intro.ipynb
  - id: kernel
    resource: /references/kernel-source.md
    title: P5Kernel 类 API 信源
---

## 目标

创建第一个 p5.js Notebook，实现一个旋转矩形动画，理解 p5-kernel 的基本工作流。

## 前置条件

- 已安装 `jupyterlite-p5-kernel`（`pip install jupyterlite-p5-kernel && jupyter lite build`）
- 在 JupyterLite 中创建新 Notebook，选择 **p5.js** 内核

## 步骤

### 步骤 1：定义变量

在第一个 cell 中定义动画参数：

```javascript
let n = 4;        // 矩形数量
let speed = 1;    // 旋转速度
```

执行该 cell（Shift+Enter）。此时不会有图形输出，但变量已注册到代码累积器中。

### 步骤 2：编写 setup() 函数

创建画布：

```javascript
function setup() {
  createCanvas(innerWidth, innerHeight);
  rectMode(CENTER);
}
```

- `createCanvas(innerWidth, innerHeight)` 创建与输出区域等大的画布
- `rectMode(CENTER)` 设置矩形以中心点为基准绘制

执行该 cell。

### 步骤 3：编写 draw() 函数

编写动画循环：

```javascript
function draw() {
  background('#ddd');
  translate(innerWidth / 2, innerHeight / 2);
  for (let i = 0; i < n; i++) {
    push();
    rotate(frameCount * speed / 1000 * (i + 1));
    fill(i * 5, i * 100, i * 150);
    const s = 200 - i * 10;
    rect(0, 0, s, s);
    pop();
  }
}
```

关键 p5.js 函数：
- `background('#ddd')`：每帧用浅灰色覆盖画布
- `translate(x, y)`：将坐标原点移到画布中心
- `push()/pop()`：保存/恢复坐标系状态（隔离每个矩形的旋转变换）
- `rotate(angle)`：旋转坐标系
- `frameCount`：p5 全局变量，记录已绘制帧数
- `fill(r, g, b)`：设置填充颜色

执行该 cell。

### 步骤 4：渲染动画

使用 `%show` magic 显示动画：

```javascript
%show
```

执行后，输出区域会出现一个 iframe，显示旋转的彩色矩形动画。

### 步骤 5：实时调参

修改变量值并执行 cell，动画会自动更新：

```javascript
speed = 3;
```

```javascript
n = 20;
```

每次执行后，已显示的动画会自动更新为新参数的效果，无需重新执行 `%show`。

### 步骤 6：重新渲染

如果想创建一个新的独立输出（不影响之前的），可以再次执行 `%show`：

```javascript
%show
```

也可以指定尺寸：

```javascript
%show 800 600
```

## 完整代码

如果想一次性写完所有代码：

```javascript
let n = 4;
let speed = 1;

function setup() {
  createCanvas(innerWidth, innerHeight);
  rectMode(CENTER);
}

function draw() {
  background('#ddd');
  translate(innerWidth / 2, innerHeight / 2);
  for (let i = 0; i < n; i++) {
    push();
    rotate(frameCount * speed / 1000 * (i + 1));
    fill(i * 5, i * 100, i * 150);
    const s = 200 - i * 10;
    rect(0, 0, s, s);
    pop();
  }
}
```

然后执行 `%show`。

## 工作流总结

```
┌─────────────────────────────────────────┐
│  1. 定义变量（可分散在多个 cell）         │
│  2. 定义 setup() 函数                    │
│  3. 定义 draw() 函数                     │
│  4. 执行 %show 渲染画布                  │
│  5. 修改变量/函数 → 自动更新已有动画      │
│  6. 再次 %show 创建新的独立输出           │
└─────────────────────────────────────────┘
```

## 关键要点

- 代码可以分散在任意多个 cell 中，内核通过 AST 自动累积和去重
- `%show` 是唯一触发图形渲染的命令
- 普通代码执行后，已有的 `%show` 输出自动更新
- `%show` 默认尺寸为 100% × 400px，可通过参数自定义
- p5.js 全局函数（setup、draw、createCanvas、fill、rect 等）直接可用，无需 import

## 相关概念

- [%show 魔法命令](../concepts/04-magic-commands.md)
- [P5Kernel 实现详解](../concepts/02-kernel-implementation.md)
- [架构概览](../concepts/01-architecture-overview.md)
- [粒子系统示例](02-particle-system.md)
