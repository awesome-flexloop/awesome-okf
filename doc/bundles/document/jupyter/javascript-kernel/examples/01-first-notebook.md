---
type: Tutorial
title: 第一个 Notebook
description: 从创建 Notebook 到运行 JavaScript 代码的完整入门教程
tags: [tutorial, getting-started, hello-world, notebook, basics]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
prerequisites: []
sources:
  - id: jk-readme
    title: README.md
---

# 第一个 Notebook

本教程带你从零开始创建第一个 JavaScript Kernel Notebook。

## 前置条件

- 已安装 JupyterLite 和 `jupyterlite-javascript-kernel`
- 使用现代浏览器（Chrome/Edge/Firefox/Safari 最新版）

## 步骤 1：打开 JupyterLite

启动 JupyterLite 站点后，你会看到文件浏览器界面。

## 步骤 2：创建新 Notebook

1. 点击工具栏的 **"+"** 按钮，或选择 **File → New → Notebook**
2. 在弹出的内核选择器中，选择 **JavaScript (IFrame)**
3. 一个新的空 Notebook 会打开

## 步骤 3：运行第一行代码

在第一个单元格中输入：

```javascript
console.log("Hello, JavaScript Kernel!");
```

按 **Shift+Enter** 执行。你应该看到输出：
```
Hello, JavaScript Kernel!
```

## 步骤 4：表达式求值

JavaScript Kernel 会自动输出单元格中最后一个表达式的值：

```javascript
1 + 2
```

执行后输出：`3`

尝试更多表达式：

```javascript
// 字符串拼接
"Hello" + ", " + "World!"
```

```javascript
// 数组操作
[1, 2, 3, 4, 5].filter(n => n % 2 === 0)
```

```javascript
// 对象
{ name: "JavaScript", version: "ES2017" }
```

## 步骤 5：使用变量

变量在单元格之间保持：

```javascript
// 单元格1
const name = "World";
const greeting = `Hello, ${name}!`;
```

```javascript
// 单元格2（新建单元格）
console.log(greeting);
greeting.length
```

## 步骤 6：使用顶层 await

```javascript
// 获取 GitHub API 数据
const response = await fetch('https://api.github.com/repos/jupyterlite/javascript-kernel');
const data = await response.json();
console.log(`仓库: ${data.full_name}`);
console.log(`Stars: ${data.stargazers_count}`);
```

## 步骤 7：显示 HTML

```javascript
display("<h2 style='color: #4A90D9'>HTML 输出</h2>");
display("<p>这是一段 <b>富文本</b> 输出</p>");
```

## 步骤 8：切换运行时模式

1. 点击工具栏右上角的内核名称
2. 选择 **JavaScript (Web Worker)**
3. 注意：Worker 模式下无法访问 DOM，但计算不阻塞 UI

```javascript
// Worker 模式下测试计算
function fibonacci(n) {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
}
console.log("fib(30) =", fibonacci(30));
```

## 常见问题排查

| 问题 | 解决方案 |
|------|---------|
| 代码不执行 | 检查内核是否连接（内核名称旁无空心圆） |
| 输出空白 | 尝试 `console.log()` 替代直接返回值 |
| import 失败 | 检查网络连接和包名拼写 |
| DOM 操作报错 | 切换到 IFrame 模式 |

## 下一步

- 学习 [Magic Imports](02-magic-imports.md) — 导入 npm 包
- 学习 [使用 Widgets](03-using-widgets.md) — 创建交互式控件
- 阅读 [内核架构](../concepts/02-kernel-architecture.md) — 了解内核工作原理
