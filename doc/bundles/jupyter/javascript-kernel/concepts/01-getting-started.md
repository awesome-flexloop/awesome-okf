---
type: Concept
title: 快速开始
description: 安装 JavaScript Kernel、创建第一个 Notebook、基础用法和模式选择
tags: [install, quickstart, notebook, basics]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: jk-readme
    title: README.md
---

# 快速开始

## 安装

使用 pip 安装 JavaScript Kernel 到 JupyterLite 环境：

```bash
pip install jupyterlite-javascript-kernel
```

安装后，构建 JupyterLite 站点时会自动包含 JavaScript 内核。

### 开发模式安装

```bash
git clone https://github.com/jupyterlite/javascript-kernel.git
cd javascript-kernel
pip install -e "."
jupyter labextension develop . --overwrite
jlpm build
```

## 第一个 Notebook

1. 打开 JupyterLite
2. 点击 "New Notebook"
3. 在内核选择器中选择 **JavaScript (IFrame)** 或 **JavaScript (Web Worker)**
4. 在单元格中输入 JavaScript 代码并执行

### Hello World

```javascript
console.log("Hello, JavaScript Kernel!");
```

输出：
```
Hello, JavaScript Kernel!
```

### 基本表达式

单元格中最后一个表达式的值会自动输出：

```javascript
1 + 2
```

输出：`3`

```javascript
const x = 10;
const y = 20;
x + y
```

输出：`30`

```javascript
"Hello, " + "World!"
```

输出：`'Hello, World!'`

### 使用顶层 await

```javascript
const response = await fetch('https://api.github.com/repos/jupyterlite/javascript-kernel');
const data = await response.json();
data.name
```

输出：`'javascript-kernel'`

### 对象和数组

```javascript
const person = { name: "Alice", age: 30 };
person
```

输出会格式化显示对象内容（JSON + 文本预览）。

```javascript
const numbers = [1, 2, 3, 4, 5];
numbers.map(n => n * 2)
```

输出：`[2, 4, 6, 8, 10]`

## 选择运行时模式

### 什么时候用 IFrame 模式？

- 需要操作 DOM（创建元素、canvas 绘图等）
- 需要访问 `window`、`document` 对象
- 使用需要 DOM 的库（如 p5.js、canvas-confetti、D3.js）

```javascript
// IFrame 模式下可以操作主页面 DOM
const div = window.parent.document.createElement('div');
div.textContent = 'Hello from iframe!';
div.style.cssText = 'position:fixed;top:10px;right:10px;background:yellow;padding:10px;z-index:9999;';
window.parent.document.body.appendChild(div);
```

### 什么时候用 Web Worker 模式？

- 执行计算密集型任务（不阻塞 UI）
- 不需要 DOM 访问
- 需要更强的代码隔离

```javascript
// Worker 模式 - 计算密集型任务
function fibonacci(n) {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
}
fibonacci(40)
```

### 禁用特定模式

通过 JupyterLite 配置禁用不需要的模式：

**禁用 Worker 模式**（只保留 IFrame）：

```json
{
  "jupyter-config-data": {
    "disabledExtensions": [
      "@jupyterlite/javascript-kernel-extension:kernel-worker"
    ]
  }
}
```

**禁用 IFrame 模式**（只保留 Worker）：

```json
{
  "jupyter-config-data": {
    "disabledExtensions": [
      "@jupyterlite/javascript-kernel-extension:kernel-iframe"
    ]
  }
}
```

## Console 输出

内核重写了 `console` 对象，将输出重定向到 Notebook：

| 方法 | 输出流 | 用途 |
|------|--------|------|
| `console.log()` | stdout | 普通日志 |
| `console.info()` | stdout | 信息日志 |
| `console.debug()` | stdout | 调试日志 |
| `console.warn()` | stderr | 警告 |
| `console.error()` | stderr | 错误 |
| `console.table()` | stdout | 表格数据 |
| `console.dir()` | stdout | 对象检查 |

```javascript
console.log("普通信息");
console.error("错误信息");
console.table([{a:1,b:2},{a:3,b:4}]);
```

`console.log` 会自动对对象进行富格式化：

```javascript
console.log({ name: "test", value: 42, nested: { a: 1 } });
```

## 下一步

- 学习 [03-执行模型](03-execution-model.md) 了解 Magic Imports 和代码执行原理
- 学习 [05-Widget系统](05-widget-system.md) 使用交互式控件
- 查看 [02-Magic Imports](../examples/02-magic-imports.md) 示例了解 npm 包导入
