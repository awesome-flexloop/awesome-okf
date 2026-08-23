---
type: concept
title: "多前端框架桥接"
description: "框架适配器模式、@anywidget/types TypeScript 类型、React/Svelte/Vue/Signals 集成思路、model proxy 机制、experimental 命令模式与 BindingManager"
prerequisites: ["03-frontend-communication.md"]
sources:
  - "../references/framework-bridges.md"
generated: "2026-08-23"
verified: false
tags: ["anywidget", "jupyter", "framework-bridges", "react", "svelte", "vue", "typescript"]
---

# 多前端框架桥接

anywidget 核心包不依赖任何前端框架，但通过适配器模式提供了与 React、Svelte、Vue 等主流框架的官方桥接包，将 model API 封装为各框架原生的响应式原语。本文档讲解适配器设计模式、TypeScript 类型系统，以及各框架集成的基本思路。

## 框架适配器模式

所有框架桥接包基于同一个核心抽象：**WidgetBinding + modelProxy**。这层抽象将生命周期管理和状态管理与具体 UI 框架解耦。

```text
┌──────────────────────────────────────────┐
│       UI 框架（React/Svelte/Vue）         │
│  ┌──────────────────────────────────┐   │
│  │  框架原生响应式（Hooks/Stores）   │   │
│  └──────────────┬───────────────────┘   │
│                 │ 桥接层                 │
│  ┌──────────────▼───────────────────┐   │
│  │ model proxy + AbortSignal + Host │   │
│  └──────────────┬───────────────────┘   │
└─────────────────┼────────────────────────┘
                  │
┌─────────────────▼────────────────────────┐
│  anywidget 核心：WidgetBinding / Runtime  │
└──────────────────────────────────────────┘
```

各桥接包的共同模式：
1. 将 `model.get/set/on` 封装为框架原生响应式 API（React state、Svelte store、Vue ref）
2. 利用 AbortSignal 或框架生命周期自动清理事件监听器
3. 提供 `useModelState()` 类 Hook/Store，一行代码实现双向绑定
4. 基于 `@anywidget/types` 提供 TypeScript 类型支持

### 官方桥接包

| 包名 | 框架 | 核心原语 |
|------|------|---------|
| `@anywidget/types` | 无（类型） | TypeScript interfaces |
| `@anywidget/react` | React | Hooks |
| `@anywidget/svelte` | Svelte | Stores |
| `@anywidget/vue` | Vue | Composition API |
| `@anywidget/signals` | 通用 Signals | Signal 原语 |

> 框架适配包的具体 API 请参考各包官方文档，本文档覆盖核心包中已验证的桥接 API。

## @anywidget/types TypeScript 类型

`@anywidget/types` 是类型安全 ESM 代码的基础。

### AnyModel 泛型接口

```typescript
import type { AnyModel } from "@anywidget/types";

interface CounterModel {
  value: number;
  label: string;
}

function render({ model, el }: { model: AnyModel<CounterModel>; el: HTMLElement }) {
  const value = model.get("value");  // 类型为 number ✓
  model.set("label", "Count: ");     // 类型检查 ✓
}
```

核心 API：

```typescript
interface AnyModel<T extends ObjectHash = ObjectHash> {
  get<K extends keyof T>(key: K): T[K];
  set<K extends keyof T>(key: K, value: T[K]): void;
  save_changes(): void;
  on(eventName: "msg:custom", cb: (msg: any, buffers: DataView[]) => void): void;
  on(eventName: `change:${string}`, cb: () => void): void;
  on(eventName: string, cb: EventHandler): void;
  off(eventName?: string, cb?: EventHandler): void;
  send(content: any, callbacks?: any, buffers?: ArrayBuffer[] | ArrayBufferView[]): void;
  widget_manager: WidgetManager;
}
```

### 生命周期 Props 类型

```typescript
interface RenderProps<T> {
  model: AnyModel<T>;
  el: HTMLElement;
  signal: AbortSignal;
  host: Host;
  experimental: Experimental;
}
interface InitializeProps<T> {
  model: AnyModel<T>;
  signal: AbortSignal;
  experimental: Experimental;  // 无 el 和 host
}
```

### Experimental 和 Host 类型

```typescript
type Experimental = {
  invoke: <T>(name: string, msg?: any, opts?: {
    buffers?: DataView[]; signal?: AbortSignal;
  }) => Promise<[T, DataView[]]>;
};

interface Host {
  getModel<T>(ref: string): Promise<AnyModel<T>>;
  getWidget<T>(ref: string): Promise<ResolvedWidget<T>>;
}
interface ResolvedWidget<T> {
  exports: T;
  render(opts: { el: HTMLElement; signal?: AbortSignal }): Promise<void>;
}
```

### WidgetDef 类型

```typescript
interface WidgetDef<T> {
  initialize?: Initialize<T>;
  render?: Render<T>;
}
type AnyWidget<T> = WidgetDef<T> | (() => Awaitable<WidgetDef<T>>);
```

## model proxy：监听器上下文管理

传递给 initialize/render 的 `model` 是 `modelProxy()` 创建的 Proxy，这是框架桥接的关键基础设施：

```typescript
function modelProxy(model, context): AnyModel {
  return new Proxy(model, {
    get(target, prop) {
      if (prop === "on")  return (ev, cb) => target.on(ev, cb, context);
      if (prop === "off") return (ev?, cb?) => target.off(ev, cb, context);
      const v = target[prop];
      return typeof v === "function" ? v.bind(target) : v;
    },
  });
}
```

`on`/`off` 的第三个参数（context）实现监听器的批量管理：

| Context | 用途 | 清理时机 |
|---------|------|---------|
| `INITIALIZE_MARKER` (Symbol) | initialize 阶段监听器 | ESM 重新绑定时（HMR） |
| View 实例 | render 阶段监听器 | View 销毁或 HMR refresh 时 |

通过 `model.off(null, null, context)` 可一次性清除指定 context 下的所有监听器，无需追踪 callback 引用。

## React 集成

`@anywidget/react` 提供 React Hooks，用函数组件编写 Widget 视图：

```jsx
import { useModelState } from "@anywidget/react";
import { createRoot } from "react-dom/client";

function Counter({ model }) {
  const [value, setValue] = useModelState(model, "value");
  return (
    <button onClick={() => setValue(value + 1)}>{value}</button>
  );
}

export default {
  render({ model, el }) {
    const root = createRoot(el);
    root.render(<Counter model={model} />);
    return () => root.unmount();
  }
}
```

`useModelState(model, key)` 返回 `[value, setValue]` 元组，类似 `useState`，自动订阅 `change:key` 事件并在 cleanup 时自动移除监听。

## Svelte 集成

`@anywidget/svelte` 将 model 属性转换为 Svelte store，支持 `$` 语法自动订阅：

```svelte
<!-- Counter.svelte -->
<script>
  export let value;
  export let setValue;
</script>
<button on:click={() => setValue($value + 1)}>{$value}</button>
```

```javascript
import { modelStore } from "@anywidget/svelte";
import Counter from "./Counter.svelte";

export default {
  render({ model, el }) {
    const store = modelStore(model);
    const component = new Counter({ target: el, props: { store } });
    return () => component.$destroy();
  }
}
```

Svelte store 契约（`subscribe`/`set`/`update`）与 model API 天然契合，桥接层只需要将 `model.on("change:")` 映射为 store 通知。

## Vue 集成

`@anywidget/vue` 通过 Composition API 将 model 属性转换为 Vue ref：

```vue
<template>
  <button @click="value++">{{ value }}</button>
</template>

<script setup>
import { ref } from "vue";
const props = defineProps(["model"]);
const value = ref(props.model.get("value"));
props.model.on("change:value", () => value.value = props.model.get("value"));
</script>
```

Vue 的响应式系统（ref/reactive）和生命周期钩子（onUnmounted）与 AbortSignal 结合，实现自动清理。

## Signals 集成

`@anywidget/signals` 提供 TC39 Signals 提案兼容的信号原语，框架无关：

```javascript
import { signal, computed, effect } from "@anywidget/signals";

export default {
  render({ model, el }) {
    const count = signal(model.get("value"));
    model.on("change:value", () => count.set(model.get("value")));

    const dispose = effect(() => {
      el.innerHTML = `<button>${count()}</button>`;
    });

    el.querySelector("button").onclick = () => {
      model.set("value", count() + 1);
      model.save_changes();
    };
    return () => dispose();
  }
}
```

## experimental 命令模式

`@command` + `experimental.invoke()` 构成 RPC 命令调用模式，是框架桥接和高级交互的基础。

```python
from anywidget.experimental import command

class DataWidget(anywidget.AnyWidget):
    _esm = """
    export default {
      async render({ model, el, experimental }) {
        const btn = document.createElement("button");
        btn.onclick = async () => {
          const [result] = await experimental.invoke("add", { a: 2, b: 3 });
          btn.textContent = `2+3=${result.sum}`;
        };
        el.appendChild(btn);
      }
    }
    """
    @command
    def add(self, msg, buffers):
        return {"sum": msg["a"] + msg["b"]}, []
```

- Python 端：`@command` 标记方法 → `__init_subclass__` 收集（遍历 MRO）→ `__init__` 注册 on_msg
- JS 端：UUID 生成 → custom 消息发送 → 监听响应匹配 id → resolve Promise
- 默认 3 秒超时（`AbortSignal.timeout(3000)`），支持自定义 signal 和二进制 buffers

## BindingManager：绑定生命周期

`BindingManager` 管理所有 Widget 绑定，确保每个 model 对应一个 WidgetBinding：

```typescript
class BindingManager {
  #bindings = new Map<DOMWidgetModel, WidgetBinding>();
  getOrCreate(model) { /* 创建或返回已有 binding */ }
  destroy(model) { /* 销毁 binding */ }
}
export const BINDINGS = new BindingManager();
```

`WidgetBinding` 是适配器模式的核心，管理 initialize 执行、render 调用、cleanup 存储、exports 对象和 ready Promise。框架桥接包无需关心生命周期细节，只需在 render 中挂载 UI，在 cleanup 中卸载。

## 开发方式选择

| 场景 | 推荐方式 |
|------|---------|
| 快速原型/简单交互 | 原生 JS + 内联 ESM（零依赖） |
| 复杂 UI | 框架桥接包（React/Svelte/Vue） |
| 数据可视化 | 原生 JS + D3/Chart.js |
| 轻量级响应式 | @anywidget/signals |
| Notebook 内探索 | %%vfile + HMR |
| 生产级应用 | Vite + 框架桥接包 |

## 相关示例

- [双向绑定高级用法](../examples/two-way-binding.md) — custom messages 与 invoke 命令调用
- [Vite 集成开发](../examples/vite-integration.md) — Vite + 框架集成开发环境
