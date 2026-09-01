---
type: example
title: "Vite 集成开发与 HMR"
description: "使用 Vite 和 @anywidget/vite 插件搭建 anywidget 开发环境，体验热更新（HMR）、TypeScript 和 React/Svelte 框架集成。"
prerequisites: ["04-hmr-dev.md", "05-framework-bridges.md"]
sources:
  - "../references/hmr.md"
  - "../references/esm-protocol.md"
  - "../references/framework-bridges.md"
  - "../concepts/04-hmr-dev.md"
  - "../concepts/05-framework-bridges.md"
generated: "2026-08-23"
verified: false
tags: ["anywidget", "jupyter", "example", "vite", "hmr", "react"]
---

# Vite 集成开发与 HMR

使用 Vite 搭建专业 anywidget 开发工作流，获得模块热更新（HMR）、TypeScript、CSS 预处理器和 React/Svelte/Vue 框架支持。

## 前置条件

- 已完成 [Counter Widget 入门](counter-widget.md)
- Node.js ≥ 18，Python ≥ 3.10
- `pip install anywidget watchfiles`
- 理解 HMR 概念（见 [HMR热更新](../concepts/04-hmr-dev.md)）

## 步骤 1：项目结构

```text
my_widget/
├── src/
│   ├── index.js        # 前端 ESM 入口（Vite dev 入口）
│   └── style.css
├── my_widget/
│   ├── __init__.py     # Python 包
│   └── static/         # Vite build 输出（生产）
│       └── index.js
├── package.json
└── vite.config.js
```

初始化项目：

```bash
mkdir my_widget && cd my_widget
npm init -y
npm install -D vite @anywidget/vite
```

## 步骤 2：Vite 配置

创建 `vite.config.js`：

```javascript
import { defineConfig } from "vite";
import anywidget from "@anywidget/vite";

export default defineConfig({
  plugins: [anywidget()],
  build: {
    lib: { entry: ["src/index.js"], formats: ["es"], fileName: "index" },
    outDir: "my_widget/static",
    emptyOutDir: true,
  },
});
```

`@anywidget/vite` 插件（F-417/418）通过查询参数 `?anywidget` 拦截请求，在 dev server 模式下注入 HMR 运行时（packages/vite/hmr.js），使用 `import.meta.hot.accept()` 实现热更新。

## 步骤 3：编写前端代码

`src/index.js`：

```javascript
import "./style.css";

export default {
  render({ model, el }) {
    el.className = "counter-vite";

    const heading = document.createElement("h3");
    heading.textContent = "Vite + anywidget";

    const decBtn = document.createElement("button"); decBtn.textContent = "−"; decBtn.className = "btn dec";
    const countSpan = document.createElement("span"); countSpan.className = "count";
    const incBtn = document.createElement("button"); incBtn.textContent = "+"; incBtn.className = "btn inc";

    const update = () => countSpan.textContent = model.get("value");
    update();
    model.on("change:value", update);

    decBtn.addEventListener("click", () => { model.set("value", model.get("value") - 1); model.save_changes(); });
    incBtn.addEventListener("click", () => { model.set("value", model.get("value") + 1); model.save_changes(); });

    el.append(heading, decBtn, countSpan, incBtn);
  },
};
```

`src/style.css`：

```css
.counter-vite {
  font-family: system-ui; padding: 20px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 12px; color: white; text-align: center;
}
.counter-vite .count { font-size: 48px; font-weight: bold; display: inline-block; min-width: 80px; }
.counter-vite .btn { border: none; border-radius: 8px; padding: 10px 20px; font-size: 18px; cursor: pointer; margin: 0 8px; font-weight: bold; }
.counter-vite .dec { background: #ef4444; color: white; }
.counter-vite .inc { background: #22c55e; color: white; }
```

## 步骤 4：Python 包

`my_widget/__init__.py`：

```python
import os, pathlib, anywidget, traitlets

_DEV = os.environ.get("ANYWIDGET_HMR") == "1"

class ViteCounter(anywidget.AnyWidget):
    value = traitlets.Int(0).tag(sync=True)

    if _DEV:
        # 开发模式：指向 Vite dev server（?anywidget 触发 HMR）
        _esm = "http://localhost:5173/src/index.js?anywidget"
    else:
        # 生产模式：使用 Vite build 输出的静态文件
        _esm = pathlib.Path(__file__).parent / "static" / "index.js"
```

关键点：URL 形式的 `_esm` 在 JS 端通过动态 `import()` 直接加载（F-410）；`?anywidget` 查询参数触发 Vite 插件的 HMR 模板注入。

## 步骤 5：启动开发 + 体验 HMR

添加 npm 脚本到 `package.json`：

```json
{
  "scripts": { "dev": "vite", "build": "vite build" },
  "devDependencies": { "@anywidget/vite": "^0.1.0", "vite": "^5.0.0" }
}
```

启动 Vite dev server：

```bash
npm run dev
```

Jupyter 中使用开发模式：

```python
import os; os.environ["ANYWIDGET_HMR"] = "1"
from my_widget import ViteCounter
w = ViteCounter()
w
```

现在修改 `src/index.js` 或 `src/style.css` 保存，浏览器中的 widget **自动更新**，状态（value 值）保留。

### HMR refresh 流程（packages/vite/hmr.js）

1. `import.meta.hot.accept()` 接收模块更新
2. 执行旧模块 cleanup 函数
3. `model.off()` 移除旧事件监听
4. `emptyElement(el)` 清空 DOM
5. 创建新 AbortController
6. 动态 import 新模块
7. 调用 `initialize()` 和 `render()`

```text
编辑源码 → Vite 检测变更 → WebSocket 推送 → HMR accept
→ cleanup + off + 清空 DOM → import 新模块 → 重新 render
→ ✨ 更新完成，model 状态保留
```

## 步骤 6：生产构建

```bash
npm run build
```

输出到 `my_widget/static/index.js`（单文件 ESM，CSS 内联到 JS 中）。不设置 `ANYWIDGET_HMR` 即为生产模式：

```python
# 生产模式：无需运行 Vite dev server
from my_widget import ViteCounter
ViteCounter()
```

## 步骤 7：TypeScript 支持

Vite 原生支持 TS，安装类型定义：`npm install -D @anywidget/types`。将文件改为 `.ts` 后缀：

```typescript
// src/index.ts
import type { AnyWidget } from "@anywidget/types";
import "./style.css";

interface Model { value: number; }

const widget: AnyWidget<Model> = {
  render({ model, el }) {
    const v: number = model.get("value");  // 类型推断
    // ...
  },
};
export default widget;
```

Python dev URL 改为 `http://localhost:5173/src/index.ts?anywidget`。

## 步骤 8：React 集成

安装 React 依赖：`npm install react react-dom`，`npm install -D @vitejs/plugin-react @types/react @types/react-dom`。

`vite.config.js`：

```javascript
import { defineConfig } from "vite";
import anywidget from "@anywidget/vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [anywidget(), react()],
  build: { lib: { entry: ["src/index.jsx"], formats: ["es"], fileName: "index" }, outDir: "my_widget/static", emptyOutDir: true },
});
```

`src/index.jsx`：

```jsx
import React, { useState, useEffect, useCallback } from "react";
import { createRoot } from "react-dom/client";

function Counter({ model }) {
  const [count, setCount] = useState(model.get("value"));

  useEffect(() => {
    const onChange = () => setCount(model.get("value"));
    model.on("change:value", onChange);
    return () => model.off("change:value", onChange);
  }, [model]);

  const inc = useCallback(() => { model.set("value", model.get("value") + 1); model.save_changes(); }, [model]);
  const dec = useCallback(() => { model.set("value", model.get("value") - 1); model.save_changes(); }, [model]);

  return (
    <div style={{ padding: 20, textAlign: "center" }}>
      <h3>React + anywidget</h3>
      <button onClick={dec}>−</button>
      <span style={{ fontSize: 32, margin: "0 16px", fontWeight: "bold" }}>{count}</span>
      <button onClick={inc}>+</button>
    </div>
  );
}

export default {
  render({ model, el }) {
    const root = createRoot(el);
    root.render(<Counter model={model} />);
    return () => root.unmount();  // cleanup：HMR 时卸载 React
  },
};
```

可封装 `useModelState(model, key)` 自定义 Hook 简化 trait 访问，模式与 useEffect cleanup 相同。

## 内置 HMR vs Vite HMR 对比

| 特性 | 内置 HMR（watchfiles） | Vite 增强 HMR |
|------|----------------------|--------------|
| 触发条件 | `ANYWIDGET_HMR=1` + 路径 `_esm` | `ANYWIDGET_HMR=1` + URL `_esm` + Vite server |
| 错误提示 | 控制台 | 浏览器错误遮罩层 |
| 框架支持 | 原生 JS | React/Svelte/Vue/Preact |
| TypeScript | ❌ | ✅ |
| CSS 预处理器 | ❌ | ✅（Sass/Less） |
| 模块拆分 | ❌（单文件） | ✅（import 多模块） |
| 适用场景 | 快速原型 | 复杂前端、团队协作 |

## 开发工作流速查

| 操作 | 命令 | HMR | Python 重启 |
|------|------|:---:|:-----------:|
| 启动 dev server | `npm run dev` | — | — |
| 开发模式 | `os.environ["ANYWIDGET_HMR"]="1"` | ✅ | ❌ |
| 生产构建 | `npm run build` | ❌ | 刷新页面即可 |
| 修改前端（dev） | 保存文件 | ✅ 自动 | ❌ |
| 修改 Python | 重新执行单元格 | — | ✅ 需 re-import |

## 相关概念

- [HMR热更新](../concepts/04-hmr-dev.md) — 热更新机制、SolidJS 响应式内核和 watchfiles 原理
- [多框架桥接](../concepts/05-framework-bridges.md) — Host API、Widget 引用和前端框架集成模式
- [ESM前端协议与通信](../references/esm-protocol.md) — ESM 加载机制、Blob URL 和远程 URL 处理
- [HMR热更新与开发服务器](../references/hmr.md) — HMR 运行时和 Vite 插件详细参考
