---
type: OKF
title: p5-kernel 教程
description: JupyterLite p5.js 内核的系统化教程，涵盖内核架构、iframe渲染、代码累积机制、%show魔法命令、P5Executor渲染、扩展注册与构建打包
tags: [p5-kernel, jupyterlite, p5js, creative-coding, iframe, kernel, jupyter, typescript]
okf_version: "0.2"
version: "0.4.0-alpha.2"
source: https://github.com/jupyterlite/p5-kernel
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T17:00:00+08:00" }
status: stable
stale_after: 2027-08-22
---

# p5-kernel 教程

p5-kernel 是 [JupyterLite](https://jupyterlite.readthedocs.io/) 的 p5.js 内核，让你可以在 Jupyter Notebook 中直接编写和运行 [p5.js](https://p5js.org/) 创意编程草图。它构建在 JupyterLite JavaScript 内核之上，通过 iframe 沙箱渲染 p5.js 画布，支持增量式 cell 编程、ES Module 外部包导入和实时动画预览。

本教程基于源码深度分析（v0.4.0-alpha.2），系统讲解 p5-kernel 的核心架构、iframe 渲染机制、代码累积模型、魔法命令、执行器扩展和构建打包。

## 📚 快速导航

### [概念文档](concepts/index.md)
- [00-p5-kernel 简介](concepts/00-introduction.md) — 是什么、核心特性、安装方法、生态位置
- [01-架构概览](concepts/01-architecture-overview.md) — 继承关系、三层线程模型、关键数据流、核心设计决策
- [02-P5Kernel 实现详解](concepts/02-kernel-implementation.md) — 构造函数、bootstrap 机制、executeRequest 流程、生命周期
- [03-P5Executor 与渲染机制](concepts/03-executor-and-rendering.md) — p5.Graphics 自动渲染为 PNG、P5_DOCS 内置文档、构建时文档生成
- [04-%show 魔法命令](concepts/04-magic-commands.md) — 语法参数、iframe srcdoc 生成、AST 代码累积、实时更新机制
- [05-扩展注册与 CDN 配置](concepts/05-extension-registration.md) — JupyterLab 插件注册、KernelSpec、p5Url 配置与覆盖
- [06-构建与打包](concepts/06-build-and-packaging.md) — TypeScript 构建、p5-docs 自动生成、hatchling Python 包、双发布

### [实践示例](examples/index.md)
- [01-第一个 p5 Sketch](examples/01-first-sketch.md) — setup/draw、%show 渲染、实时调参
- [02-粒子系统](examples/02-particle-system.md) — 面向对象、边界碰撞、HSB 颜色、拖尾效果
- [03-外部 npm 包导入](examples/03-external-packages.md) — ES import 语法、canvas-confetti、dayjs、第三方库组合

### [信源参考](references/index.md)
- [项目元信源](references/metasource.md) — 版本、依赖、目录结构、构建配置
- [P5Kernel 类 API 信源](references/kernel-source.md) — 构造函数、方法、私有字段、命名空间接口
- [P5Executor 类 API 信源](references/executor-source.md) — MIME 渲染、P5_DOCS、文档生成脚本
- [扩展注册信源](references/extension-source.md) — 插件定义、CDN 配置、KernelSpec 字段

### [补充材料](../index.md)
- [事实清单](facts.md) — R 阶段采集的 67 条零推测事实
- [架构洞察](insights.md) — I 阶段提炼的 4 个核心洞察

## 🚀 快速开始

### 安装

```bash
pip install jupyterlite-p5-kernel
jupyter lite build
jupyter lite serve
# 访问 http://localhost:8000
```

### 第一个 Sketch

在 Notebook 中选择 **p5.js** 内核，然后：

```javascript
function setup() {
  createCanvas(400, 400);
}

function draw() {
  background(220);
  fill(255, 0, 0);
  ellipse(mouseX, mouseY, 50, 50);
}
```

```javascript
%show 400 400
```

执行后即可看到一个跟随鼠标移动的红色圆形。

## 🎯 核心特性

| 特性 | 说明 |
|------|------|
| 🎨 p5.js 原生支持 | 直接编写 setup()/draw()，使用全部 p5.js API |
| 📝 增量式编程 | 变量和函数可分散在多个 cell，内核自动累积 |
| 🖼️ iframe 沙箱渲染 | `%show` 在独立 iframe 中渲染，与 Notebook UI 隔离 |
| 📦 ES Module 导入 | `import confetti from 'canvas-confetti'` 直接加载 npm 包 |
| 🖼️ Graphics 自动渲染 | p5.Graphics 离屏画布自动转为 PNG 输出 |
| 📖 内置 API 文档 | Shift+Tab 显示 p5.js 函数签名和描述 |
| 🔄 实时更新 | 修改变量后所有 sketch 自动刷新 |
| 🌐 零后端 | 完全浏览器运行，无需服务器进程 |

## 🏗️ 架构概览

```
┌─────────────────────────────────────────────────────────┐
│  主线程 (JupyterLab UI)                                  │
│  内核选择器 → display_data 渲染 iframe                   │
└────────────────────────┬────────────────────────────────┘
                         │ 内核协议消息
┌────────────────────────▼────────────────────────────────┐
│  Web Worker (JS 运行时)                                  │
│  P5Kernel(extends JavaScriptKernel)                     │
│  ├─ 执行用户 JS 代码（Worker 全局作用域）                │
│  ├─ AST 累积代码到 CodeRegistry（去重合并）              │
│  ├─ 追踪 import 语句（去重）                             │
│  └─ 生成 iframe srcdoc → display_data                   │
│                                                          │
│  P5Executor(extends JavaScriptExecutor)                 │
│  ├─ p5.Graphics → PNG base64 渲染                       │
│  └─ P5_DOCS 内置 API 文档（构建时从 @types/p5 生成）     │
└────────────────────────┬────────────────────────────────┘
                         │ srcdoc HTML
┌────────────────────────▼────────────────────────────────┐
│  iframe (p5.js 渲染沙箱)                                 │
│  import(p5.js CDN) → 创建 __globalP5 → 加载imports      │
│  → 执行累积代码 → __globalP5._start() → 动画循环        │
└─────────────────────────────────────────────────────────┘
```

## 📖 推荐学习路径

1. **入门了解**：阅读 [00-简介](concepts/00-introduction.md) 和 [01-架构概览](concepts/01-architecture-overview.md)，理解继承关系和三层模型
2. **动手实践**：跟着 [01-第一个 Sketch](examples/01-first-sketch.md) 创建第一个动画
3. **理解核心**：学习 [02-P5Kernel 实现](concepts/02-kernel-implementation.md) 和 [04-%show 魔法命令](concepts/04-magic-commands.md)
4. **渲染机制**：阅读 [03-P5Executor 与渲染](concepts/03-executor-and-rendering.md) 理解 Graphics 渲染和内置文档
5. **扩展配置**：学习 [05-扩展注册](concepts/05-extension-registration.md) 了解 CDN 配置和内核注册
6. **进阶实践**：尝试 [02-粒子系统](examples/02-particle-system.md) 和 [03-外部包导入](examples/03-external-packages.md)
7. **构建发布**：阅读 [06-构建与打包](concepts/06-build-and-packaging.md) 了解双包发布流程

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
facts
insights
log
```
