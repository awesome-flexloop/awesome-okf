---
type: Concept
title: 富媒体输出系统
description: display() 函数、DisplayHelper、MIME bundle、display_id 更新机制
tags: [display, mime, rich-output, media, html, visualization, display-id]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: jk-display
    title: display.ts
  - id: jk-executor
    title: executor.ts
---

# 富媒体输出系统

JavaScript Kernel 提供丰富的输出能力，支持 HTML、SVG、图片、Markdown、LaTeX、JSON 等多种 MIME 类型。输出通过全局 `display()` 函数和单元格自动返回值两种方式产生。

## display() 全局函数

内核运行时在 globalScope 上注入全局 `display()` 函数，可以在任何代码中调用以显示内容：

```javascript
display(value, metadata?);
```

### 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `value` | `any` | 要显示的值，可以是字符串、对象、Widget、或自定义 MIME 对象 |
| `metadata` | `object`（可选） | 附加的 metadata，如 `display_id`、MIME 类型特定配置 |

### 基本用法

```javascript
// 显示文本
display("Hello, World!");

// 显示 HTML
display("<h1 style='color:red'>Red Title</h1>");

// 显示对象（自动序列化为 JSON）
display({ name: "Alice", age: 30 });

// 显示 Widget
const { IntSlider } = Jupyter.widgets;
display(new IntSlider({ value: 42 }));
```

## DisplayHelper

`DisplayHelper` 是 `display()` 函数的底层实现，管理输出消息发送和 display_id 更新机制。

### 构造参数

```typescript
interface DisplayHelperOptions {
  baseUrl?: string;
  onOutput?: (message: RuntimeOutputMessage) => void;
}
```

- `baseUrl`：图片等资源的基础 URL
- `onOutput`：输出消息回调（由 evaluator 注入，发送到前端）

### display() 方法流程

```
display(obj, metadata?)
    │
    ├─► obj 是 Widget？
    │   └─► 发送 display_data (application/vnd.jupyter.widget-view+json)
    │
    ├─► obj 是 HTMLElement？
    │   └─► 发送 display_data (DOM MIME bundle)
    │
    ├─► metadata.display_id 存在？
    │   ├─► 首次：发送 display_data（带 transient display_id）
    │   └─► 后续：发送 update_display_data（更新已有输出）
    │
    ├─► metadata.raw_mimetype 指定了 MIME 类型？
    │   └─► obj 作为该 MIME 类型直接发送
    │
    └─► 其他值 → getMimeBundle(obj) 转换
        └─► 发送 display_data
```

## MIME Bundle 格式

所有输出最终转换为 Jupyter 标准的 MIME bundle 格式：

```json
{
  "text/plain": "'Hello'",
  "text/html": "<b>Hello</b>",
  "application/json": { "greeting": "Hello" }
}
```

MIME bundle 是一个对象，key 为 MIME 类型，value 为该类型的表示。前端按优先级选择最佳表示渲染。

### 支持的 MIME 类型

| MIME 类型 | 说明 | 产生方式 |
|----------|------|---------|
| `text/plain` | 纯文本 | 所有值默认产生 |
| `text/html` | HTML 渲染 | HTML 字符串、DOM 元素、`_toHtml()` |
| `text/markdown` | Markdown | 自定义输出 |
| `text/latex` | LaTeX 公式 | 自定义输出 |
| `image/svg+xml` | SVG 图片 | `_toSvg()` |
| `image/png` | PNG 图片（base64） | `_toPng()` |
| `image/jpeg` | JPEG 图片（base64） | `_toJpeg()` |
| `application/json` | JSON | 对象、数组、Map、Set、Date、Error |
| `application/javascript` | JavaScript | 自定义输出 |
| `application/vnd.jupyter.widget-view+json` | Widget 视图 | Widget 实例 |
| `application/vnd.jupyter.widget-state+json` | Widget 状态 | Widget 管理器 |
| DOM 专用 MIME | DOM 元素 | HTMLElement 实例 |

## display_id 更新机制

使用 `metadata.display_id` 可以更新之前显示的内容，实现动态更新效果：

```javascript
// 首次显示
display("Loading...", { display_id: "status" });

// 模拟异步更新
setTimeout(() => {
  display("Done!", { display_id: "status" });  // 更新，不新建输出
}, 1000);
```

### 工作原理

1. 首次 display 时，如果 `display_id` 不存在，发送 `display_data` 消息（transient 中包含 display_id）
2. 后续同一 display_id 调用 display 时，发送 `update_display_data` 消息
3. 前端根据 display_id 找到对应的输出区域并替换内容

### 动态更新示例

```javascript
// 进度更新
for (let i = 0; i <= 100; i += 10) {
  display(`Progress: ${i}%`, { display_id: "progress" });
  await new Promise(r => setTimeout(r, 200));
}
```

```javascript
// HTML 动态更新
display("<div>Step 1</div>", { display_id: "steps" });
await new Promise(r => setTimeout(r, 500));
display("<div>Step 2</div>", { display_id: "steps" });
await new Promise(r => setTimeout(r, 500));
display("<div>Step 3 ✓</div>", { display_id: "steps" });
```

## 自定义 MIME 类型输出

通过 `metadata.raw_mimetype` 可以直接指定 MIME 类型输出：

```javascript
// 直接输出 Markdown
display("# Hello Markdown\n\nThis is **bold** text.", {
  raw_mimetype: "text/markdown"
});

// 直接输出 LaTeX
display("$$E = mc^2$$", {
  raw_mimetype: "text/latex"
});

// 直接输出 SVG
display('<svg width="100" height="100"><circle cx="50" cy="50" r="40" fill="red"/></svg>', {
  raw_mimetype: "image/svg+xml"
});
```

## 对象自定义输出方法

对象可以定义特殊方法来控制自己的显示方式：

| 方法 | 返回类型 | MIME 类型 | 优先级 |
|------|---------|----------|--------|
| `_toMime()` | `IMimeBundle` | 自定义完整 bundle | 最高 |
| `_toHtml()` | `string` | `text/html` | 高 |
| `_toSvg()` | `string` | `image/svg+xml` | 中 |
| `_toPng()` | `string`（base64 data URI 或 raw base64） | `image/png` | 中 |
| `_toJpeg()` | `string`（base64） | `image/jpeg` | 中 |
| `inspect()` | `any` | `text/plain`（Node.js 风格） | 低 |

```javascript
class Circle {
  constructor(radius) {
    this.radius = radius;
  }

  _toHtml() {
    return `<svg width="${this.radius * 2}" height="${this.radius * 2}">
      <circle cx="${this.radius}" cy="${this.radius}" r="${this.radius}" fill="blue"/>
    </svg>`;
  }

  _toMime() {
    return {
      "text/plain": `Circle(radius=${this.radius})`,
      "text/html": this._toHtml(),
      "application/json": { type: "Circle", radius: this.radius }
    };
  }
}

display(new Circle(50));
```

## Widget 输出

Widget 实例的输出使用专用 MIME 类型：

```json
{
  "application/vnd.jupyter.widget-view+json": {
    "version_major": 2,
    "version_minor": 1,
    "model_id": "c-uuid-here"
  },
  "text/plain": "IntSlider(value=50)"
}
```

前端通过 `model_id` 查找 widget model 并渲染对应的 view。

## HTML 输出注意事项

### HTML 自动检测

字符串是否被自动识别为 HTML 取决于：
- 以 `<` 开头，后跟标签名、`<!DOCTYPE` 或 `<!--`
- 以 `>` 结尾
- trim 后内容匹配正则 `/^<(?:[a-zA-Z][a-zA-Z0-9-]*[\s/>]|!(?:DOCTYPE|--))/`

```javascript
// 被识别为 HTML
display("<b>Bold</b>");
display("<div style='color:blue'>Blue</div>");

// 不被识别为 HTML（字符串表达式）
display("<a, b>");  // 不是有效 HTML 标签
display("hello <world>");  // 不以标签开头
```

### DOM 元素输出

HTMLElement 实例会使用专用的 DOM MIME bundle 渲染，保留元素引用而非序列化字符串。

## 输出和单元格返回值

一个单元格可以产生两种输出：

1. **display() 调用**：产生 `display_data` 消息，可以多次调用，每个调用一个输出
2. **单元格最后一个表达式的值**：产生 `execute_result` 消息（包含 execution_count）

```javascript
// 产生 3 个输出：display_data (HTML) + display_data (text) + execute_result (42)
display("<h1>Title</h1>");
display("Some text");
42
```

## Console 输出

Console 输出（`console.log`/`error`/`warn`）产生 `stream` 消息，不属于 display 系统，但在 Notebook 中同样可见：

| console 方法 | 流名称 | 文本颜色 |
|-------------|--------|---------|
| `log`/`info`/`debug`/`dir`/`table` | `stdout` | 白色/默认 |
| `error`/`warn` | `stderr` | 红色/黄色 |

## 相关文档

- [03-执行模型](03-execution-model.md) — getMimeBundle 类型处理规则
- [05-Widget系统](05-widget-system.md) — Widget 显示
- [04-富媒体输出](../examples/04-rich-output.md) — 各种输出类型示例
