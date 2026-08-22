---
type: reference
title: "多框架桥接与高级模式"
description: "TypeScript 类型定义、Host API 跨 Widget 引用、experimental.invoke 命令调用、@command 装饰器、modelProxy 与 Widget 引用解析"
sources:
  - "external/libs/ai/Anything/anywidget/packages/types/index.ts"
  - "external/libs/ai/Anything/anywidget/packages/anywidget/src/host.ts"
  - "external/libs/ai/Anything/anywidget/packages/anywidget/src/invoke.ts"
  - "external/libs/ai/Anything/anywidget/packages/anywidget/src/widget-ref.ts"
  - "external/libs/ai/Anything/anywidget/packages/anywidget/src/model-proxy.ts"
  - "external/libs/ai/Anything/anywidget/packages/anywidget/src/binding.ts"
  - "external/libs/ai/Anything/anywidget/anywidget/experimental.py"
generated: "2026-08-23"
verified: false
tags: ["anywidget", "jupyter", "framework-bridges", "typescript", "host-api", "commands"]
---

# 多框架桥接与高级模式

本文档描述 anywidget 的 TypeScript 类型系统、Host API 跨 Widget 引用机制、experimental.invoke 命令调用模式、@command 装饰器、modelProxy 代理层、Widget 引用解析以及框架适配器模式。

> **说明**：anywidget 提供独立的框架适配 npm 包（如 `@anywidget/react`、`@anywidget/svelte`、`@anywidget/vue`、`@anywidget/signals`），这些包基于本文档描述的核心类型和 Host API 构建。核心包（`anywidget`）本身不依赖任何前端框架，框架适配包作为可选扩展存在。本文档覆盖核心包中已验证的桥接 API。

## TypeScript 类型定义

`packages/types/index.ts` 是 anywidget 的公共类型定义入口，定义了前端 ESM 代码与框架交互所需的全部类型。

### 基础类型别名

[F-301] 基础类型：

```typescript
type Awaitable<T> = T | Promise<T>;
type ObjectHash = Record<string, any>;
type EventHandler = (...args: any[]) => void;
```

[F-302] `LiteralUnion` 类型工具——提供字面量自动补全同时允许任意字符串：

```typescript
type LiteralUnion<T, U = string> = T | (U & {});
```

### AnyModel 接口

[F-304] `AnyModel` 是前端与 model 交互的核心接口：

```typescript
interface AnyModel<T extends ObjectHash = ObjectHash> {
  get<K extends keyof T>(key: K): T[K];
  set<K extends keyof T>(key: K, value: T[K]): void;
  off<K>(eventName?: string, callback?: EventHandler): void;
  on(eventName: "msg:custom", callback: (msg: any, buffers: DataView[]) => void): void;
  on(eventName: `change:${string}`, callback: () => void): void;
  on(eventName: string, callback: EventHandler): void;
  save_changes(): void;
  send(content: any, callbacks?: any, buffers?: ArrayBuffer[] | ArrayBufferView[]): void;
  widget_manager: WidgetManager;
}
```

### WidgetManager 接口

[F-303] `WidgetManager` 用于获取其他 widget 的 model：

```typescript
interface WidgetManager {
  get_model<T extends ObjectHash>(model_id: string): Promise<AnyModel<T>>;
}
```

### 生命周期 Props 接口

[F-308] `RenderProps`——render 函数接收的参数：

```typescript
interface RenderProps<T extends ObjectHash = ObjectHash> {
  model: AnyModel<T>;
  el: HTMLElement;
  signal: AbortSignal;
  host: Host;
  experimental: Experimental;
}
```

[F-310] `InitializeProps`——initialize 函数接收的参数（无 el 和 host）：

```typescript
interface InitializeProps<T extends ObjectHash = ObjectHash> {
  model: AnyModel<T>;
  signal: AbortSignal;
  experimental: Experimental;
}
```

### 生命周期函数类型

[F-309] `Render` 类型：

```typescript
type Render<T extends ObjectHash = ObjectHash> = (
  props: RenderProps<T>
) => Awaitable<void | (() => Awaitable<void>)>;
```

返回值可选为 cleanup 函数。

[F-311] `Initialize` 类型：

```typescript
type Initialize<T extends ObjectHash = ObjectHash> = (
  props: InitializeProps<T>
) => Awaitable<void | (() => Awaitable<void>) | object>;
```

返回值可以是 cleanup 函数或 exports 对象（通过 host.getWidget 访问）。

### WidgetDef 与 AnyWidget 类型

[F-312][F-313] ESM 默认导出类型：

```typescript
interface WidgetDef<T extends ObjectHash = ObjectHash> {
  initialize?: Initialize<T>;
  render?: Render<T>;
}

type AnyWidget<T extends ObjectHash = ObjectHash> =
  | WidgetDef<T>
  | (() => Awaitable<WidgetDef<T>>);
```

### Experimental API

[F-305] `Experimental` 类型包含 invoke 命令调用方法：

```typescript
type Experimental = {
  invoke: <T>(
    name: string,
    msg?: any,
    options?: {
      buffers?: DataView[];
      signal?: AbortSignal;
    }
  ) => Promise<[T, DataView[]]>;
};
```

### Host API 类型

[F-306][F-307] Host 接口与 ResolvedWidget：

```typescript
interface ResolvedWidget<T = unknown> {
  exports: T;
  render(opts: { el: HTMLElement; signal?: AbortSignal }): Promise<void>;
}

interface Host {
  getWidget<T = unknown>(ref: string): Promise<ResolvedWidget<T>>;
  getModel<T extends ObjectHash = ObjectHash>(ref: string): Promise<AnyModel<T>>;
}
```

## Host API——跨 Widget 引用

Host API 允许一个 Widget 引用和操作其他 Widget，实现 Widget 组合与嵌套。

### createHost 实现

[F-413] `createHost` 函数创建 Host 对象：

```typescript
function createHost(
  model: DOMWidgetModel,
  { signal }: { signal: AbortSignal }
): Host {
  return {
    async getModel<T>(ref: string): Promise<AnyModel<T>> {
      const modelId = parseWidgetRef(ref);
      const childModel = await model.widget_manager.get_model(modelId);
      // 包装为 modelProxy，signal abort 时清理监听器
      return modelProxy(childModel, signal) as AnyModel<T>;
    },
    
    async getWidget<T>(ref: string): Promise<ResolvedWidget<T>> {
      const modelId = parseWidgetRef(ref);
      const childModel = await model.widget_manager.get_model(modelId);
      const childBinding = BINDINGS.getOrCreate(childModel);
      
      // 10秒超时等待 childBinding ready
      const timeout = AbortSignal.timeout(10000);
      const exports = await Promise.race([
        childBinding.ready,
        new Promise((_, reject) => {
          timeout.addEventListener("abort", () =>
            reject(new Error("Timeout waiting for widget"))
          );
        }),
      ]) as T;
      
      return {
        exports,
        async render({ el, signal: renderSignal }) {
          const combined = AbortSignal.any([signal, renderSignal, timeout]);
          // 创建 AnyView 并调用 childBinding.createView
          const view = await childModel.widget_manager.create_view(childModel, { el });
          await childBinding.createView(view, {
            signal: combined,
            experimental: { invoke: createInvoke(childModel) },
            host: createHost(childModel, { signal: combined }),
          });
        },
      };
    },
  };
}
```

### Widget 引用解析

[F-414] `parseWidgetRef` 解析引用字符串：

```typescript
const WIDGET_REF_PREFIX = "anywidget:";

function parseWidgetRef(ref: unknown): string {
  if (typeof ref === "string" && ref.startsWith(WIDGET_REF_PREFIX)) {
    return ref.slice(WIDGET_REF_PREFIX.length);
  }
  throw new Error(`Invalid widget reference: ${ref}`);
}
```

Python 端 `WidgetTrait` 将 Widget 值序列化为 `"anywidget:<model_id>"` 格式（[F-251]），JS 端通过 `parseWidgetRef` 解析后用 `widget_manager.get_model()` 获取子 model。

### 使用示例

跨 Widget 引用的典型模式：

```javascript
// 父 Widget
export default {
  async render({ model, el, host }) {
    // 获取子 Widget 的 model
    const childModel = await host.getModel("anywidget:child-model-id");
    childModel.on("change:value", () => {
      console.log("Child value:", childModel.get("value"));
    });
    
    // 获取子 Widget 的完整视图（含 exports 和 render）
    const child = await host.getWidget("anywidget:child-model-id");
    const container = document.createElement("div");
    el.appendChild(container);
    await child.render({ el: container });
    
    // 访问子 Widget 的 exports
    console.log("Child exports:", child.exports);
  }
}
```

## modelProxy——监听器上下文管理

[F-401][F-402] `modelProxy` 创建 model 的代理对象，将 on/off 监听器绑定到特定 context，便于按上下文批量清理：

```typescript
let INITIALIZE_MARKER = Symbol("anywidget.initialize");

function modelProxy(
  model: DOMWidgetModel,
  context: unknown
): AnyModel {
  return new Proxy(model, {
    get(target, prop) {
      if (prop === "on") {
        return (eventName, callback) => target.on(eventName, callback, context);
      }
      if (prop === "off") {
        return (eventName?, callback?) => target.off(eventName, callback, context);
      }
      // get/set/save_changes/send 直接委托到原始 model
      const value = target[prop];
      return typeof value === "function" ? value.bind(target) : value;
    },
  });
}
```

关键设计：
- `INITIALIZE_MARKER` Symbol 用作 initialize 阶段监听器的上下文标记
- ESM 重新绑定时，通过 `model.off(null, null, INITIALIZE_MARKER)` 一次性清除 initialize 阶段注册的所有监听器
- render 阶段使用 view 实例或 AbortSignal 作为 context

## 命令调用模式（experimental.invoke）

anywidget 提供基于 UUID 匹配的 RPC（远程过程调用）模式，允许 JS 端调用 Python 端函数并获取返回值。

### Python 端：@command 装饰器

[F-279][F-280] `@command` 装饰器标记函数为 anywidget 命令：

```python
_ANYWIDGET_COMMAND = "_anywidget_command"

def command(cmd: T) -> T:
    """装饰器，标记函数为 anywidget 可调用命令"""
    setattr(cmd, _ANYWIDGET_COMMAND, True)
    return cmd
```

使用方式：

```python
from anywidget import AnyWidget
from anywidget.experimental import command

class CalculatorWidget(AnyWidget):
    value = t.Int(0).tag(sync=True)
    
    @command
    def add(self, msg, buffers):
        a = msg["a"]
        b = msg["b"]
        result = a + b
        return {"result": result}, []  # (response, buffers)
```

### 命令收集

[F-281] `_collect_anywidget_commands` 在 `__init_subclass__` 中自动收集命令：

```python
def _collect_anywidget_commands(widget_cls: type) -> None:
    cmds: dict[str, _AnyWidgetCommand] = {}
    for base_cls in widget_cls.__mro__:
        for attr_name, attr_value in base_cls.__dict__.items():
            if callable(attr_value) and getattr(attr_value, _ANYWIDGET_COMMAND, False):
                cmds[attr_name] = attr_value
    setattr(widget_cls, _ANYWIDGET_COMMANDS, cmds)
```

### 命令注册

[F-282] `_register_anywidget_commands` 在 `__init__` 中注册 on_msg 回调：

```python
def _register_anywidget_commands(widget: WidgetBase) -> None:
    cmds = getattr(type(widget), _ANYWIDGET_COMMANDS, {})
    if not cmds:
        return
    
    def _handle_command(widget, msg, buffers):
        if msg.get("kind") != "anywidget-command":
            return
        cmd_name = msg["name"]
        if cmd_name not in cmds:
            return
        # 调用命令函数
        response, response_buffers = cmds[cmd_name](widget, msg["msg"], buffers)
        # 发回响应
        widget.send(
            {"id": msg["id"], "kind": "anywidget-command-response", "response": response},
            buffers=response_buffers,
        )
    
    widget.on_msg(_handle_command)
```

### JS 端：experimental.invoke

[F-415] `invoke` 函数实现 JS 端命令调用：

```typescript
import { uuid } from "@lukeed/uuid";

async function invoke<T>(
  model: DOMWidgetModel,
  name: string,
  msg?: any,
  options?: { buffers?: DataView[]; signal?: AbortSignal }
): Promise<[T, DataView[]]> {
  const id = uuid();
  const timeout = AbortSignal.timeout(3000);  // 默认 3 秒超时
  const signal = options?.signal
    ? AbortSignal.any([options.signal, timeout])
    : timeout;
  
  return new Promise((resolve, reject) => {
    function onMsg(customMsg: any, buffers: DataView[]) {
      if (customMsg.kind === "anywidget-command-response" && customMsg.id === id) {
        model.off("msg:custom", onMsg);
        resolve([customMsg.response, buffers]);
      }
    }
    
    signal.addEventListener("abort", () => {
      model.off("msg:custom", onMsg);
      reject(new Error(`Command '${name}' ${signal.reason || "timed out"}`));
    });
    
    model.on("msg:custom", onMsg);
    model.send(
      { id, kind: "anywidget-command", name, msg },
      undefined,
      options?.buffers as ArrayBufferView[]
    );
  });
}
```

关键特性：
- 使用 `@lukeed/uuid` 生成唯一请求 ID
- 默认 3 秒超时（`AbortSignal.timeout(3000)`）
- 支持自定义 AbortSignal
- 支持传递二进制 buffers
- 通过 `msg:custom` 事件监听响应，匹配 id 后 resolve

### 命令调用示例

```javascript
// JS 端
export default {
  async render({ model, el, experimental }) {
    const button = document.createElement("button");
    button.textContent = "Add 1+2";
    button.onclick = async () => {
      try {
        const [result] = await experimental.invoke("add", { a: 1, b: 2 });
        console.log("1 + 2 =", result.result);  // 3
      } catch (e) {
        console.error("Command failed:", e);
      }
    };
    el.appendChild(button);
  }
}
```

## WidgetBinding——框架适配器核心

[F-393] `WidgetBinding` 是框架适配器模式的核心抽象，管理 widget 定义与 model 的绑定生命周期：

```typescript
class WidgetBinding {
  #widgetDef: WidgetDef | null = null;
  #controller: AbortController | null = null;
  #cleanup: (() => Awaitable<void>) | undefined;
  #exports: unknown = undefined;
  #ready: Promise<unknown>;
  
  ready: Promise<unknown>;
  get exports(): unknown { return this.#exports; }
  
  async bind(widgetDef: WidgetDef, { signal, experimental }) {
    if (this.#widgetDef === widgetDef) return;
    
    // 中止旧 binding
    this.#controller?.abort();
    this.#readyReject?.(new Error("Widget reloaded"));
    
    // 清除 initialize 阶段监听器
    model.off(null, null, INITIALIZE_MARKER);
    
    const controller = new AbortController();
    this.#controller = controller;
    this.#widgetDef = widgetDef;
    
    // 创建 ready promise
    const { resolve, reject, promise } = promiseWithResolvers();
    this.#ready = promise;
    
    // 执行 initialize
    const result = await widgetDef.initialize?.({
      model: modelProxy(model, INITIALIZE_MARKER),
      signal: controller.signal,
      experimental,
    });
    
    if (typeof result === "function") {
      this.#cleanup = result;
      this.#exports = undefined;
    } else if (result && typeof result === "object") {
      this.#exports = result;
    }
    resolve(this.#exports);
  }
  
  async createView(target, { signal, experimental, host }) {
    await this.ready;
    if (!this.#widgetDef?.render) return;
    
    const controller = new AbortController();
    const combined = AbortSignal.any([signal, controller.signal]);
    
    const cleanup = await this.#widgetDef.render({
      model: modelProxy(model, target),
      el: target.el,
      signal: combined,
      host,
      experimental,
    });
    
    combined.addEventListener("abort", () => {
      safeCleanup(cleanup, "render cleanup");
      safeCleanup(this.#cleanup, "initialize cleanup");
    });
  }
  
  destroy() {
    this.#controller?.abort();
    this.#widgetDef = null;
    this.#controller = null;
  }
}
```

[F-399][F-400] `BindingManager` 和 `BINDINGS` 单例：

```typescript
class BindingManager {
  #bindings = new Map<DOMWidgetModel, WidgetBinding>();
  
  getOrCreate(model: DOMWidgetModel): WidgetBinding {
    let binding = this.#bindings.get(model);
    if (!binding) {
      binding = new WidgetBinding(model);
      this.#bindings.set(model, binding);
    }
    return binding;
  }
  
  get(model: DOMWidgetModel): WidgetBinding | undefined {
    return this.#bindings.get(model);
  }
  
  destroy(model: DOMWidgetModel): void {
    this.#bindings.get(model)?.destroy();
    this.#bindings.delete(model);
  }
}

export let BINDINGS = new BindingManager();
```

## 框架适配包概述

anywidget 生态系统包含以下框架适配 npm 包（基于上述核心 API 构建）：

| 包名 | 用途 | 核心依赖 |
|------|------|---------|
| `@anywidget/types` | TypeScript 类型定义（本文档已覆盖） | 无 |
| `@anywidget/react` | React Hooks 适配 | React, anywidget 核心 |
| `@anywidget/svelte` | Svelte Store 适配 | Svelte, anywidget 核心 |
| `@anywidget/vue` | Vue Composition API 适配 | Vue, anywidget 核心 |
| `@anywidget/signals` | 通用 Signals 集成 | SolidJS 信号概念 |

这些框架适配包的共同模式是：
1. 封装 `model.get()`/`model.set()`/`model.on("change:")` 为框架原生的响应式 API（React state、Svelte store、Vue ref 等）
2. 使用 `AbortSignal` 或框架生命周期自动清理事件监听器
3. 提供 `useModelState()` 类钩子/Hook，简化双向绑定

> **注意**：上述框架适配包的具体 API 不在当前源码分析范围内，开发者应参考各包的官方文档获取最新 API。

## experimental 模块导出

[F-276] `anywidget.experimental` 模块导出：

```python
__all__ = ["MimeBundleDescriptor", "dataclass", "widget"]
```

注意：`MimeBundleDescriptor` 从 `_descriptor` 重新导出，`command` 也在此模块中定义。

### @widget 装饰器

[F-277] 将任意类变为 Widget：

```python
def widget(*, esm: str | pathlib.Path, css: None | str | pathlib.Path = None, **kwargs):
    kwargs["_esm"] = esm
    if css is not None:
        kwargs["_css"] = css
    def decorator(cls):
        cls._repr_mimebundle_ = MimeBundleDescriptor(**kwargs)
        return cls
    return decorator
```

### @dataclass 装饰器

[F-278] 将标准 Python dataclass 变为响应式 Widget：

```python
def dataclass(cls=None, *, esm, css=None, **dataclass_kwargs):
    def wrap(cls):
        cls = dataclasses.dataclass(cls, **dataclass_kwargs)
        cls = psygnal.evented(cls)  # 注入事件信号
        cls = widget(esm=esm, css=css)(cls)
        return cls
    if cls is None:
        return wrap
    return wrap(cls)
```

## 相关文档

- ESM 前端协议与通信：[esm-protocol](esm-protocol.md)
- Trait 同步与数据绑定：[traits](traits.md)
- 描述符协议：[descriptor](descriptor.md)
- AnyWidget 基类与生命周期：[widget-base](widget-base.md)
- HMR 热更新：[hmr](hmr.md)
