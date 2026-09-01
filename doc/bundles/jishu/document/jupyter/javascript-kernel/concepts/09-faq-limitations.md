---
type: Concept
title: 常见问题与限制
description: JavaScript Kernel 使用中的常见问题、浏览器限制、调试技巧和最佳实践
tags: [faq, troubleshooting, limitations, debugging, best-practices, cors]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: jk-readme
    title: README.md
  - id: jk-executor
    title: executor.ts
  - id: jk-backends
    title: runtime_backends.ts
---

# 常见问题与限制

## 运行时模式相关

### Q: IFrame 模式和 Worker 模式该选哪个？

**IFrame 模式**（默认）：
- ✅ 可以访问 DOM（`document`、`window`）
- ✅ 可以通过 `window.parent` 操作主页面
- ✅ 适合可视化、canvas 绘图、DOM 操作
- ⚠️ 主线程执行，长时间计算会阻塞 UI

**Worker 模式**：
- ✅ 独立线程，不阻塞 UI
- ✅ 更强的隔离性
- ❌ 无法访问 DOM（没有 `document`、`window`）
- ❌ 无法操作主页面
- ✅ 适合计算密集型任务

### Q: Worker 模式下如何做可视化？

Worker 模式无法直接操作 DOM，但可以：
1. 使用 `display()` 输出 HTML 字符串（HTML 在主线程渲染）
2. 使用 `display()` 输出 SVG/Canvas 数据 URL
3. 通过 Comm 协议发送数据到前端扩展渲染
4. 使用支持 OffscreenCanvas 的库（如果可用）

### Q: 如何在 IFrame 模式中访问主页面的库？

```javascript
// 获取主页面的全局变量
const mainLodash = window.parent._;

// 在主页面中创建 DOM 元素
const div = window.parent.document.createElement('div');
window.parent.document.body.appendChild(div);

// 注意：这只在 IFrame 模式下有效，Worker 模式会报错
```

> ⚠️ 通过 `window.parent` 访问主页面违反同源策略以外的安全边界，仅用于可信场景。

## Magic Imports 相关

### Q: Magic Imports 是从哪里加载包的？

默认从 jsdelivr CDN 加载：`https://cdn.jsdelivr.net/npm/<package-name>/+esm`

+esm 后缀表示 jsdelivr 的 ESM 转换服务，将 CommonJS/UMD 包转换为 ES Module。

### Q: 可以导入特定版本的包吗？

```javascript
import React from 'react@18.2.0';     // 指定版本
import lodash from 'lodash@4.17.21';
```

### Q: Magic Imports 支持哪些 CDN？

默认使用 jsdelivr。Magic Imports 功能的配置（baseUrl、enableAutoNpm 等）由内核配置决定。也可以直接导入完整 URL 来使用其他 CDN：

```javascript
// 使用 unpkg
import d3 from 'https://unpkg.com/d3?module';

// 使用 esm.sh
import React from 'https://esm.sh/react@18';

// 使用 skypack
import lodash from 'https://cdn.skypack.dev/lodash';
```

### Q: 为什么我的 import 失败了？

常见原因：
1. **包不提供 ESM 版本**：有些 npm 包只有 CommonJS 版本，无法直接作为 ES Module 导入。尝试找 ESM 版本或使用 `await import()` 动态导入
2. **CORS 限制**：CDN 必须返回正确的 CORS 头。jsdelivr 默认支持 CORS
3. **包名错误**：检查包名是否正确，注意大小写
4. **网络问题**：CDN 可能暂时不可用

### Q: 导入的包在下一个单元格还能用吗？

是的。Magic Import 的导入项会被赋值到 `globalThis`，跨单元格保持可用：

```javascript
// 单元格1
import confetti from 'canvas-confetti';
// confetti 被赋值到 globalThis.confetti

// 单元格2
confetti();  // 直接使用，不需要再次 import
```

## 执行环境限制

### Q: 为什么 `var x = 1` 在其他单元格中访问不到？

JavaScript Kernel 使用 async function 包装用户代码，函数内部的 `var` 声明不会自动成为全局变量。但内核通过 AST 分析将顶层的 `var`/`let`/`const`/`function`/`class` 声明注入到 globalScope：

```javascript
// 单元格1
var x = 1;
let y = 2;
const z = 3;
function greet() { return 'hi'; }
class Foo {}

// 单元格2 - 都可以访问
console.log(x, y, z);  // 1 2 3
greet();  // 'hi'
new Foo();  // Foo {}
```

但如果变量在非顶层作用域中声明（如函数内部、if 块内），则不会被提升：

```javascript
// 单元格1
if (true) {
  var insideIf = 'hidden';  // 不会被提升到全局
}

// 单元格2
console.log(insideIf);  // ReferenceError!
```

### Q: 为什么 `require()` 不可用？

JavaScript Kernel 是 ES Module 环境，不提供 CommonJS 的 `require()`。使用 ES `import` 语法代替：

```javascript
// ❌ 不支持
const lodash = require('lodash');

// ✅ 使用 import
import lodash from 'lodash';
```

### Q: 可以使用 `process`、`fs` 等 Node.js API 吗？

不可以。JavaScript Kernel 完全运行在浏览器中，没有 Node.js API：
- ❌ `process`、`require`、`module`、`__dirname`、`__filename`
- ❌ `fs`、`path`、`http`、`net` 等 Node.js 内置模块
- ✅ 所有标准 Web API（fetch、WebSocket、Canvas、WebAudio 等）

### Q: 支持哪些 ES 版本特性？

内核声明语言版本为 ES2017，但实际支持程度取决于浏览器。现代浏览器（Chrome/Edge/Firefox/Safari 最新版）通常支持 ES2020+ 特性：

- ✅ async/await
- ✅ 可选链 `?.`
- ✅ 空值合并 `??`
- ✅ 顶层 await（内核特殊支持）
- ✅ BigInt
- ✅ 动态 `import()`
- ⚠️ 顶层 `await` 在内核中自动支持（通过 async function 包装）

## Widget 相关

### Q: 为什么 Widget 不显示？

1. 确保前端安装了 `@jupyter-widgets/jupyterlab-manager` 扩展
2. Widget 类只能在运行时通过 `Jupyter.widgets` 访问，不能在前端代码中直接导入使用
3. 检查浏览器控制台是否有错误

### Q: 可以创建自定义 Widget 吗？

可以，但需要前端扩展配合。自定义 Widget 需要：
1. 内核端：继承 `DOMWidget` 类，定义 model_name/view_name
2. 前端端：注册对应的 widget model 和 view（通过 JupyterLab 扩展）

参考 ipywidgets 的自定义 Widget 文档。

### Q: Widget 的状态会在刷新后保留吗？

不会。刷新页面后内核重启，所有 Widget 状态丢失。这与 IPython kernel 的行为一致。

### Q: jslink 和 observe 有什么区别？

- `jslink`：双向绑定两个 widget 的属性，一个变化另一个自动更新
- `observe`：监听属性变化并执行回调函数，更灵活但需要手动处理

```javascript
// jslink：简洁的双向绑定
jslink([slider1, 'value'], [slider2, 'value']);

// observe：自定义逻辑
slider1.observe(({ new: val }) => {
  slider2.value = val * 2;  // 可以加转换逻辑
}, 'value');
```

## 输出相关

### Q: 为什么字符串被加上了引号？

单元格最后一个表达式是字符串时，`text/plain` 输出会带引号（类似 Node.js REPL），以区分字符串和数字：

```javascript
"hello"  // 输出: 'hello'（带引号）
42       // 输出: 42（不带引号）
```

如果想不带引号显示字符串，使用 `console.log()` 或 `display()`：

```javascript
console.log("hello");  // stdout 输出: hello（不带引号）
display("hello");      // text/plain 输出: hello（不带引号）
```

### Q: 如何让输出不被截断？

内核默认对大对象和数组生成预览文本，长文本可能被截断。对于大量数据：
- 使用 `console.table()` 以表格形式输出
- 使用 `display()` 配合 `application/json` 输出完整 JSON
- 使用 Output widget 的 `appendStdout` 方法

### Q: 如何清除输出？

```javascript
// 在单元格代码中
// 使用 Jupyter API 清除当前输出（需要前端支持）
```

注意：JavaScript Kernel 本身不提供 `clear_output()` 全局函数，但支持 Output widget 的 `clearOutput()` 方法。

## 调试技巧

### Q: 如何调试内核执行的代码？

**IFrame 模式**：
1. 打开浏览器开发者工具
2. 在 Sources 面板中找到 iframe 的源文件
3. 在代码中添加 `debugger` 语句

```javascript
// 在单元格中插入 debugger
debugger;
console.log("调试中");
```

**Worker 模式**：
1. 打开浏览器开发者工具
2. 在 Sources 面板中找到 Worker 线程
3. Worker 的源文件可以在 `chrome://inspect/#workers`（Chrome）中调试

### Q: 如何查看全局作用域中有哪些变量？

```javascript
// 查看所有用户定义的全局变量
Object.keys(globalThis).filter(k => 
  !k.startsWith('_') && 
  !['console', 'display', 'Jupyter'].includes(k)
);
```

### Q: 如何查看导入的模块？

```javascript
// Magic Import 将模块导出赋值到 globalThis
// 查看最近导入的变量
console.log(Object.keys(globalThis).slice(-10));
```

## 安全考虑

### Q: 在 iframe 中执行代码安全吗？

IFrame 模式使用同源 iframe（srcdoc 创建），这意味着：
- iframe 中的代码可以通过 `window.parent` 访问主页面
- 可以操作主页面 DOM
- 共享同源的 localStorage、cookies 等

这是**设计行为**，因为许多可视化场景需要 DOM 访问。如果需要更强的隔离，请使用 Worker 模式。

### Q: Magic Imports 加载的第三方代码安全吗？

Magic Imports 从 jsdelivr CDN 加载 npm 包，这些代码在内核运行时（iframe/Worker）中执行。与任何第三方代码一样，只导入你信任的包。

### Q: 可以禁用 Magic Imports 吗？

可以通过 JupyterLite 配置或内核选项禁用 Magic Imports。但通常不建议禁用，因为它是内核包管理的核心机制。

## 与 IPython Kernel 的差异

| 特性 | IPython Kernel | JavaScript Kernel |
|------|---------------|------------------|
| 运行环境 | Python 后端进程 | 浏览器 (iframe/Worker) |
| 包管理 | pip/conda | Magic Imports (CDN) |
| 文件系统 | ✅ 完整文件系统 | ❌ 仅浏览器存储 |
| DOM 访问 | ❌ | ✅ (IFrame 模式) |
| 阻塞 UI | ❌ 后端进程 | ⚠️ IFrame 模式会 |
| `print()` / `console.log()` | 同步输出 | 异步输出 |
| `display()` | Python 对象 | JS 值/Widget/DOM |
| Widgets | ipywidgets (Python) | ipywidgets (JS, 内置) |
| 魔法命令 | `%matplotlib` 等 | 无（用 import 替代） |
| 异步支持 | asyncio | 原生 Promise/async-await |

## 相关文档

- [00-JavaScript Kernel 简介](00-introduction.md)
- [01-快速开始](01-getting-started.md)
- [03-执行模型](03-execution-model.md) — 代码执行和 AST 转换细节
- [04-运行时后端](04-runtime-backends.md) — IFrame/Worker 模式架构差异
