---
type: Example
title: 粒子系统
description: 使用 p5-kernel 创建经典粒子系统动画，学习面向对象编程、边界碰撞、HSB 颜色模式和透明度拖尾效果
tags: [particle-system, animation, oop, hsb, collision, trailing, creative-coding]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T17:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: particle-nb
    resource: https://github.com/jupyterlite/p5-kernel/blob/main/examples/particle-system.ipynb
    title: examples/particle-system.ipynb
---

## 目标

实现一个经典的粒子系统（Particle System），粒子在画布上运动、反弹、变色，半透明背景产生拖尾效果。

## 代码实现

### 初始化粒子数组

```javascript
let particles = [];
```

### setup() 初始化

```javascript
function setup() {
  createCanvas(innerWidth, innerHeight);
  colorMode(HSB, 360, 100, 100, 100);

  // 创建初始粒子
  for (let i = 0; i < 50; i++) {
    particles.push({
      x: random(width),
      y: random(height),
      vx: random(-2, 2),
      vy: random(-2, 2),
      hue: random(360),
      size: random(5, 15)
    });
  }
}
```

要点：
- `colorMode(HSB, 360, 100, 100, 100)` 切换到 HSB 颜色模式，色相范围 0-360，饱和度/亮度/透明度范围 0-100
- 每个粒子是一个简单对象，包含位置(x,y)、速度(vx,vy)、色相(hue)和大小(size)
- `random(min, max)` 生成随机初始值

### draw() 动画循环

```javascript
function draw() {
  // 半透明背景产生拖尾效果
  background(0, 0, 10, 20);

  for (let p of particles) {
    // 更新位置
    p.x += p.vx;
    p.y += p.vy;

    // 边界反弹
    if (p.x < 0 || p.x > width) p.vx *= -1;
    if (p.y < 0 || p.y > height) p.vy *= -1;

    // 绘制粒子
    noStroke();
    fill(p.hue, 80, 90, 70);
    circle(p.x, p.y, p.size);

    // 色相渐变
    p.hue = (p.hue + 0.5) % 360;
  }
}
```

要点：
- `background(0, 0, 10, 20)` 使用低透明度（alpha=20）背景，不覆盖前几帧，产生拖尾效果
- 边界检测：碰到画布边缘时速度取反（`*= -1`）实现反弹
- `fill(hue, saturation, brightness, alpha)` 在 HSB 模式下设置颜色
- `circle(x, y, diameter)` 绘制圆形粒子
- `p.hue = (p.hue + 0.5) % 360` 让色相缓慢循环变化

### 显示动画

```javascript
%show
```

## 效果说明

- 50 个彩色粒子在画布上自由运动
- 碰到边缘时反弹
- 粒子颜色随时间缓慢变化（色相循环）
- 半透明背景产生运动拖尾效果
- 整体呈现出催眠般的流动视觉效果

## 可探索的变体

### 调整粒子数量

```javascript
// 在新 cell 中修改粒子数
// 需要重新定义 setup 或动态添加粒子
for (let i = 0; i < 100; i++) {
  particles.push({
    x: random(width),
    y: random(height),
    vx: random(-3, 3),
    vy: random(-3, 3),
    hue: random(360),
    size: random(3, 10)
  });
}
```

### 添加鼠标交互

```javascript
function mouseMoved() {
  // 鼠标附近添加新粒子
  particles.push({
    x: mouseX,
    y: mouseY,
    vx: random(-2, 2),
    vy: random(-2, 2),
    hue: random(360),
    size: random(5, 15)
  });
  // 限制粒子总数
  if (particles.length > 200) {
    particles.shift();
  }
}
```

### 连线效果

在 draw() 循环中添加粒子间连线：

```javascript
// 在 for 循环外或内添加
for (let i = 0; i < particles.length; i++) {
  for (let j = i + 1; j < particles.length; j++) {
    let d = dist(particles[i].x, particles[i].y, particles[j].x, particles[j].y);
    if (d < 80) {
      stroke(particles[i].hue, 80, 90, map(d, 0, 80, 50, 0));
      line(particles[i].x, particles[i].y, particles[j].x, particles[j].y);
    }
  }
}
```

## 相关概念

- [%show 魔法命令](../concepts/04-magic-commands.md)
- [P5Executor 与渲染机制](../concepts/03-executor-and-rendering.md)
- [外部包导入示例](03-external-packages.md)
