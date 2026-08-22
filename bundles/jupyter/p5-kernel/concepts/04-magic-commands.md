---
type: Concept
title: %show 魔法命令
description: p5-kernel 的 %show magic 命令语法、参数、iframe srcdoc 生成机制、display 更新与增量渲染
tags: [magic, show, iframe, srcdoc, display-data, incremental-rendering]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T17:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: kernel
    resource: /references/kernel-source.md
    title: P5Kernel 类 API 信源
---

## %show 是什么

`%show` 是 p5-kernel 唯一的魔法命令（magic command），用于在 Notebook 输出区域渲染 p5.js sketch。它将累积的所有代码（变量定义、setup()、draw()、import 语句等）组装成完整的 p5 程序，在独立 iframe 中执行并显示画布。

没有 `%show`，用户只能在 cell 输出中看到文本结果和变量值；执行 `%show` 后才会看到可视化的 p5 动画画布。

## 基本语法

```javascript
// 最简形式：默认 100% 宽度，400px 高度
%show

// 指定宽度和高度（像素值）
%show 800 600

// 指定宽度和高度（混合单位）
%show 100% 500px

// 指定百分比宽度和像素高度
%show 50% 300
```

### 参数解析

`%show` 命令使用正则表达式解析：

```typescript
const re = /^%show(?: (.+)\s+(.+))?\s*$/;
const matches = code.match(re);
const width = matches?.[1] ?? '100%';
const height = matches?.[2] ?? '400px';
```

- 第一个捕获组是 width，第二个是 height
- 未提供参数时，width 默认为 `'100%'`，height 默认为 `'400px'`
- 参数直接作为 HTML 属性值使用，支持所有 CSS 长度单位（px、%、em、vw、vh 等）
- 参数之间用空格分隔

## iframe 生成机制

### srcdoc 内容组装

`_magics()` 方法生成完整的 iframe HTML 内容：

```javascript
const importCode = executor.generateImportCode(this._imports);
const combinedCode = executor.generateCodeFromRegistry(this._codeRegistry);

const script = `
  ${this._bootstrap}.then(async () => {
    ${importCode}
    ${combinedCode}
    window.__globalP5._start();
  }).catch(e => console.error(e));
`;

const srcdocContent = [
  '<body style="overflow: hidden; margin: 0; padding: 0;">',
  `<script>${script}</script>`,
  '</body>'
].join('');
```

生成的 iframe 内容结构：

```html
<body style="overflow: hidden; margin: 0; padding: 0;">
<script>
  import('https://cdn.jsdelivr.net/npm/p5@1.9.0/lib/p5.js').then(() => {
    window.__globalP5 = new p5();
    return Promise.resolve();
  }).then(async () => {
    // import 加载代码（来自 ES import 语句）
    // 累积的用户代码（setup/draw/变量/函数）
    window.__globalP5._start();
  }).catch(e => console.error(e));
</script>
</body>
```

### 执行顺序

在 iframe 中，代码按以下顺序执行：

1. **Bootstrap**：动态 import p5.js CDN，创建 `window.__globalP5 = new p5()` 全局实例
2. **Import 加载**：执行 import 加载代码（处理用户的 ES `import` 语句，从 CDN 加载 npm 包）
3. **用户代码**：执行所有累积的非 magic cell 代码（变量定义、setup()、draw() 等）
4. **启动 Sketch**：调用 `window.__globalP5._start()`，p5.js 开始执行 setup() 和 draw() 循环

### HTML 转义

srcdoc 属性值需要进行 HTML 转义以防止注入和语法错误：

```typescript
const escapedSrcdoc = srcdocContent
  .replace(/&/g, '&amp;')
  .replace(/'/g, '&#39;')
  .replace(/"/g, '&quot;');
```

- `&` → `&amp;`（必须最先替换，避免重复转义）
- `'` → `&#39;`
- `"` → `&quot;`

### 最终输出

最终通过 `displayData` 发送的 HTML 内容：

```html
<iframe width="${width}" height="${height}" frameborder="0" srcdoc="${escapedSrcdoc}"></iframe>
```

iframe 设置了 `frameborder="0"` 去除边框，body 样式设置 `overflow: hidden; margin: 0; padding: 0;` 确保画布填满 iframe 无空白。

## 代码累积与去重

### CodeRegistry 工作原理

每次执行非 magic 代码时，代码被注册到 `CodeRegistry`：

```typescript
this._p5Executor?.registerCode(code, this._codeRegistry);
```

CodeRegistry 使用 AST（抽象语法树）分析代码结构，而非简单字符串拼接。这意味着：

- 后定义的同名**变量**会覆盖前面的定义
- 后定义的同名**函数**会替换前面的定义
- 多次执行同一 cell 不会导致重复代码
- 函数引用关系通过 AST 正确解析

例如，用户执行：
```javascript
// Cell 1
let n = 4;
function setup() { createCanvas(400, 400); }
```
然后执行：
```javascript
// Cell 2
n = 20;
```
在 `%show` 时，`generateCodeFromRegistry()` 会生成 `let n = 20;` 而非两个 `let n` 声明。

### Import 去重

```typescript
const imports = executor.extractImports(code);
for (const imp of imports) {
  if (!this._imports.some(existing => existing.source === imp.source)) {
    this._imports.push(imp);
  }
}
```

Import 语句按 `source`（模块路径/URL）去重，同一模块不会重复加载。

## 实时更新机制

### 自动更新已有 Sketch

每次执行非 magic 代码后，p5-kernel 会自动更新所有已显示的 `%show` 输出：

```typescript
const magics = await this._magics();
this._parentHeaders.forEach(h => {
  this.updateDisplayData(
    {
      data: magics.data,
      metadata: magics.metadata,
      transient
    },
    h
  );
});
```

这意味着典型的交互工作流是：

1. 定义 setup() 和 draw() → 执行 `%show` 看到动画
2. 修改某个变量值（如 `speed = 3`）→ 执行该 cell → 所有已显示的动画自动更新
3. 修改 draw() 函数 → 执行该 cell → 动画自动反映新逻辑

无需重新执行 `%show`，所有输出实时同步。

### updateDisplayData 原理

`updateDisplayData` 是 Jupyter 内核协议的一部分，通过 `transient.display_id` 匹配之前的 `display_data` 消息，用新数据替换旧输出。P5Kernel 使用 kernel id 作为固定的 `display_id`，所有 `%show` 输出共享同一 display_id，因此一次更新会刷新所有输出。

### Parent Headers 追踪

每次调用 `%show` 时，当前消息的 header 被存入 `_parentHeaders` 数组。后续更新时，遍历这个数组对每个 parent header 发送 `update_display_data` 消息，确保所有显示的 sketch 都被更新。

## 错误处理

iframe 中的代码通过 Promise chain 执行，错误被 `.catch(e => console.error(e))` 捕获并输出到浏览器控制台。如果 sketch 代码有错误，iframe 中不会显示画布，但错误信息可以通过浏览器开发者工具（F12 → Console）查看。

```javascript
${this._bootstrap}.then(async () => {
  // ... sketch code
  window.__globalP5._start();
}).catch(e => console.error(e));
```

## 典型使用模式

### 模式 1：完整定义后一次性渲染

```javascript
// Cell 1: 变量
let n = 10;
let speed = 1;

// Cell 2: setup
function setup() {
  createCanvas(innerWidth, innerHeight);
}

// Cell 3: draw
function draw() {
  background(220);
  for (let i = 0; i < n; i++) {
    rect(i * 30, 0, 20, height);
  }
}

// Cell 4: 显示
%show
```

### 模式 2：边写边调

```javascript
// 先写最简 setup/draw
function setup() { createCanvas(400, 400); }
function draw() { background(0); }
%show 400 400

// 添加内容
function draw() {
  background(0);
  fill(255);
  ellipse(mouseX, mouseY, 50, 50);
}
// 执行后自动更新

// 调整参数
let size = 80;
// 执行后自动更新
```

### 模式 3：指定尺寸

```javascript
%show 800 600      // 800px × 600px
%show 100% 300    // 全宽 × 300px
%show 50% 50vh    // 半宽 × 视口高度一半
```

## 相关概念

- [P5Kernel 实现详解](/concepts/02-kernel-implementation.md)
- [P5Executor 与渲染机制](/concepts/03-executor-and-rendering.md)
- [架构概览](/concepts/01-architecture-overview.md)
- [第一个 p5 Sketch](/examples/01-first-sketch.md)
