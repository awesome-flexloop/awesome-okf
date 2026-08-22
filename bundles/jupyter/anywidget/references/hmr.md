---
type: reference
title: "HMR 热更新与开发工作流"
description: "热更新机制（内置 watchfiles 路径与 Vite 增强路径）、SolidJS 响应式内核、文件监视、AbortSignal 清理与开发环境配置"
sources:
  - "external/libs/ai/Anything/anywidget/anywidget/_util.py"
  - "external/libs/ai/Anything/anywidget/anywidget/_file_contents.py"
  - "external/libs/ai/Anything/anywidget/packages/anywidget/src/runtime.ts"
  - "external/libs/ai/Anything/anywidget/packages/anywidget/src/observe.ts"
  - "external/libs/ai/Anything/anywidget/packages/anywidget/src/binding.ts"
  - "external/libs/ai/Anything/anywidget/packages/anywidget/src/load.ts"
  - "external/libs/ai/Anything/anywidget/packages/vite/index.js"
  - "external/libs/ai/Anything/anywidget/packages/vite/hmr.js"
generated: "2026-08-23"
verified: false
tags: ["anywidget", "jupyter", "hmr", "hot-reload", "vite", "development"]
---

# HMR 热更新与开发工作流

本文档描述 anywidget 的热模块替换（HMR）机制，包括内置 HMR 路径（watchfiles + comm 更新 + SolidJS 响应式）、Vite 增强 HMR 路径（import.meta.hot + 错误遮罩）、文件监视集成、AbortSignal 统一清理以及开发环境配置。

> **注意**：`anywidget/_serve.py` 文件在当前版本中**不存在**。anywidget 不提供独立的开发服务器，HMR 通过文件监视 + comm 通道实现，Vite 插件仅作为增强开发体验的可选组件。

## HMR 两条路径概述

anywidget 的热更新有两条路径，互不排斥：

| 路径 | 依赖 | 机制 | 特点 |
|------|------|------|------|
| **内置 HMR** | `watchfiles`（可选依赖） | 文件监视 → Python changed 信号 → comm update → JS SolidJS 响应式 → 重新加载 | 零配置、纯 Python 端驱动、无需前端构建工具 |
| **Vite 增强 HMR** | Vite dev server + anywidget Vite 插件 | Vite 中间件拦截 → HMR runtime → `import.meta.hot.accept()` | 错误遮罩、模块缓存、更细粒度更新、支持 npm 包导入 |

两条路径最终在 JS 端汇合：ESM 内容变更触发 Runtime 的 SolidJS createEffect 重新执行加载流程。

## 环境变量配置

### ANYWIDGET_HMR

[F-062] `_is_hmr_enabled()` 检查环境变量：

```python
def _is_hmr_enabled() -> bool:
    return os.environ.get("ANYWIDGET_HMR") == "1"
```

启用方式：

```bash
# Linux/macOS
export ANYWIDGET_HMR=1

# Windows PowerShell
$env:ANYWIDGET_HMR=1

# Jupyter 启动前设置
ANYWIDGET_HMR=1 jupyter lab
```

### _should_start_thread 判断

[F-063] `_should_start_thread(path)` 决定是否启动文件监视线程：

```python
def _should_start_thread(path: pathlib.Path) -> bool:
    # 1. site-packages/dist-packages 中的文件不监视
    if "site-packages" in str(path) or "dist-packages" in str(path):
        return False
    # 2. HMR 未启用
    if not _is_hmr_enabled():
        return False
    # 3. watchfiles 未安装
    try:
        import watchfiles
    except ImportError:
        warnings.warn("watchfiles not installed, HMR disabled")
        return False
    return True
```

[F-003] `watchfiles>=1.1.0` 在可选依赖 `dev` 组中；[F-004] dev dependency-group 中要求 `watchfiles>=0.23.0`。

## 内置 HMR 路径

### Python 端文件监视

[F-264][F-265] `FileContents` 类管理文件系统监视：

```python
class FileContents:
    changed = Signal(str)   # 文件修改时发射新内容
    deleted = Signal()      # 文件删除时发射
```

[F-266][F-267] 初始化与线程启动：

```python
def __init__(self, path, start_thread=True):
    self._path = path.absolute().expanduser().resolve()
    if not self._path.exists():
        raise ValueError(f"File not found: {self._path}")
    self._contents = None
    self._stop_event = threading.Event()
    self._background_thread = None
    if start_thread:
        self.watch_in_thread()

def watch_in_thread(self):
    if self._background_thread is not None:
        return
    self._stop_event.clear()
    self._background_thread = threading.Thread(
        target=lambda: deque(self.watch(), maxlen=0),
        daemon=True,
    )
    self._background_thread.start()
```

[F-269] `watch()` 方法使用 watchfiles 监视变更：

```python
def watch(self) -> Iterator[tuple[int, str]]:
    import watchfiles
    for changes in watchfiles.watch(str(self._path), stop_event=self._stop_event):
        for change_type, path in changes:
            if change_type == watchfiles.Change.deleted:
                self.deleted.emit()
                return
            # modified/added
            self._contents = None  # 清空缓存
            self.changed.emit(str(self))
            yield (change_type, path)
```

[F-270] `__str__` 懒加载文件内容（UTF-8）并缓存，文件变更时清空缓存触发重新读取。

### Signal 连接链

[F-554] 文件变更到前端更新的完整链路：

```text
文件保存
  ↓
watchfiles 检测变更
  ↓
FileContents.changed 信号发射（新内容字符串）
  ↓
__init__ 中连接的 lambda：setattr(self, "_esm", new_val)  [F-125]
  ↓ 或
ReprMimeBundle extra_state 连接：self.send_state(key)  [F-194]
  ↓
trait 值更新（traitlets 触发 observe 回调）
  ↓
ReprMimeBundle.send_state() → comm.send({"method": "update", "state: {"_esm": "..."}})
  ↓
JS 端 ipywidgets 框架接收 → model.set("_esm", ...) → 触发 "change:_esm" 事件
```

### VirtualFileContents——内存文件

[F-259][F-262] `VirtualFileContents` 用于 `%%vfile` cell magic 创建的内存文件：

```python
class VirtualFileContents:
    changed = Signal(str)
    
    def __init__(self, contents: str = ""):
        self._contents = contents
    
    @property
    def contents(self):
        return self._contents
    
    @contents.setter
    def contents(self, value):
        self._contents = value
        self.changed.emit(value)
```

[F-273] `%%vfile` cell magic 创建虚拟文件：

```python
@cell_magic
def vfile(self, line: str, cell: str) -> None:
    file_name = line.strip()
    content = self.shell.transform_cell(cell)
    vf = self._files.get(file_name)
    if vf is None:
        vf = VirtualFileContents(content)
        self._files[file_name] = vf
        _VIRTUAL_FILES[f"vfile:{file_name}"] = vf
    else:
        vf.contents = content
```

使用方式（Notebook 中）：

```python
%%vfile widget.js
export default {
  render({ model, el }) {
    el.textContent = "Hello";
  }
}

class MyWidget(AnyWidget):
    _esm = "vfile:widget.js"
```

## JS 端响应式热更新

### Runtime 响应式内核

[F-391] `Runtime` 使用 SolidJS `createRoot`/`createEffect` 构建响应式系统：

```typescript
class Runtime {
  ready: Promise<void>;
  
  constructor(model: DOMWidgetModel, { signal }: { signal: AbortSignal }) {
    const { resolve, promise } = promiseWithResolvers<void>();
    this.ready = promise;
    
    const binding = BINDINGS.getOrCreate(model);
    const experimental = { invoke: /* ... */ };
    
    solid.createRoot((dispose) => {
      signal.addEventListener("abort", dispose);
      
      // 将 _css 和 _esm 包装为 SolidJS signal
      const css = observe(model, "_css", { signal });
      const esm = observe(model, "_esm", { signal });
      
      // CSS 变更响应
      solid.createEffect(() => {
        const cssValue = css();
        const id = String(model.get(_ANYWIDGET_ID_KEY));
        if (cssValue) loadCss(cssValue, id);
      });
      
      // ESM 变更响应
      solid.createEffect(() => {
        const esmValue = esm();
        const id = String(model.get(_ANYWIDGET_ID_KEY));
        const controller = new AbortController();  // 取消前一次加载
        const ready = loadWidget(esmValue, id).then(widgetDef => {
          binding.bind(widgetDef, { signal: controller.signal, experimental });
          resolve();
        });
      });
    });
  }
}
```

[F-392] `createView` 方法在视图层也使用 createEffect 实现重渲染：

```typescript
async createView(view: DOMWidgetView, { signal }: { signal: AbortSignal }) {
  const binding = BINDINGS.getOrCreate(view.model);
  const combinedSignal = AbortSignal.any([
    signal,
    view.model.signal  // model 销毁 signal
  ]);
  const host = createHost(view.model, { signal: combinedSignal });
  
  solid.createRoot((dispose) => {
    combinedSignal.addEventListener("abort", () => {
      dispose();
      // 清理事件监听
      view.model.off(null, null, view);
      emptyElement(view.el);
    });
    
    solid.createEffect(async () => {
      // 等待 widget ready
      const exports = await binding.ready;
      // 清除旧内容
      emptyElement(view.el);
      // 创建新 controller 并调用 render
      const controller = new AbortController();
      const renderSignal = AbortSignal.any([combinedSignal, controller.signal]);
      await binding.createView(view, {
        signal: renderSignal,
        experimental,
        host,
      });
    });
  });
}
```

### observe——trait 到 Signal 的桥接

[F-403] `observe` 函数将 model trait 变更桥接到 SolidJS 响应式系统：

```typescript
function observe<T, K extends keyof T>(
  model: DOMWidgetModel,
  name: K,
  { signal }: { signal: AbortSignal }
): solid.Accessor<T[K]> {
  const [accessor, setter] = solid.createSignal<T[K]>(model.get(name));
  
  const onChange = () => setter(model.get(name));
  model.on(`change:${String(name)}`, onChange);
  
  signal.addEventListener("abort", () => {
    model.off(`change:${String(name)}`, onChange);
  });
  
  return accessor;
}
```

### WidgetBinding 重新绑定

[F-394] ESM 变更时 `WidgetBinding.bind()` 执行重新绑定：

```typescript
bind(widgetDef: WidgetDef, { signal, experimental }) {
  if (this.#widgetDef === widgetDef) return;
  
  // 中止旧 binding
  this.#controller?.abort();
  this.#readyReject?.(new Error("Widget reloaded"));
  
  // 清除 INITIALIZE_MARKER 上下文的监听器
  model.off(null, null, INITIALIZE_MARKER);
  
  const controller = new AbortController();
  this.#controller = controller;
  this.#widgetDef = widgetDef;
  
  const { resolve, reject, promise } = promiseWithResolvers();
  this.#readyResolve = resolve;
  this.#readyReject = reject;
  this.#ready = promise;
  
  // 执行 initialize
  Promise.resolve(widgetDef.initialize?.({
    model: modelProxy(model, INITIALIZE_MARKER),
    signal: controller.signal,
    experimental,
  })).then(result => {
    // 返回函数 → cleanup；返回对象 → exports
    if (typeof result === "function") {
      this.#cleanup = result;
      this.#exports = undefined;
    } else if (typeof result === "object" && result !== null) {
      this.#exports = result;
    }
    resolve(this.#exports);
  });
}
```

### ESM 热更新完整流程

[F-555] JS 端 ESM 热更新步骤：

1. **AbortController 取消**：ESM 变更时创建新 AbortController，abort 前一次加载
2. **loadWidget 加载新模块**：通过 Blob URL 或直接 import 加载新 ESM
3. **binding.bind 重新 initialize**：中止旧 binding，清除旧监听器，执行新 initialize
4. **createView 重新 render**：清空 DOM（`emptyElement(view.el)`），移除旧视图监听器（`model.off(null, null, view)`），创建新 AbortController，调用新 render
5. **cleanup 执行**：旧的 cleanup 函数通过 AbortSignal abort 自动触发

### CSS 热更新

[F-556] CSS 热更新无闪烁机制：

- **CSS 文本**：[F-409] `loadCssText` 替换 `<style>` 元素的 textContent
- **CSS URL**：[F-408] `loadCssHref` 克隆新 `<link>` 元素，等待加载完成后移除旧 link，避免 FOUC（Flash of Unstyled Content）

```typescript
// CSS URL 热更新（无闪烁）
async function loadCssHref(href: string, id: string) {
  const existing = document.getElementById(id);
  const link = document.createElement("link");
  link.id = id;
  link.rel = "stylesheet";
  link.href = href;
  
  // 等待新样式加载完成
  await new Promise((resolve, reject) => {
    link.onload = resolve;
    link.onerror = reject;
    document.head.appendChild(link);
  });
  
  // 加载成功后移除旧 link
  existing?.remove();
}
```

## Vite 增强 HMR 路径

### Vite 插件配置

[F-417] Vite 插件常量：

```javascript
const query = "?anywidget";
const namespace = "anywidget:";
const resolvedNamespace = "\0anywidget:";
```

[F-418] Vite 插件对象：

```javascript
export default function anywidget() {
  return {
    name: "anywidget",
    apply: "serve",  // 仅在 dev serve 模式下生效
    
    resolveId(id) {
      if (id.startsWith(namespace)) {
        return "\0" + id;  // \0 前缀标记为虚拟模块
      }
    },
    
    load(id) {
      if (id.startsWith(resolvedNamespace)) {
        // 读取 hmr.js 模板，替换源文件路径
        const src = id.slice(resolvedNamespace.length);
        return hmrTemplate.replace("__ANYWIDGET_HMR_SRC__", src);
      }
    },
    
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        // 拦截以 ?anywidget 结尾的 URL
        if (req.url.endsWith(query)) {
          // 转换为 namespace 前缀的 bare identifier
          const bare = namespace + req.url.slice(0, -query.length);
          // 转换为浏览器可解析的路径
          req.url = bare;
        }
        next();
      });
    }
  };
}
```

### Vite HMR Runtime

[F-419] `packages/vite/hmr.js` 是 HMR 运行时模板，核心功能：

```javascript
// 工具函数
function noop() {}
function emptyElement(el) { /* 清空所有子节点 */ }
function showErrorOverlay(err) { /* 显示 Vite 错误遮罩 */ }

// 监听全局错误
window.addEventListener("error", showErrorOverlay);
window.addEventListener("unhandledrejection", showErrorOverlay);

// 标准化 AFM（AnyWidget Function Module）输入
function getAFM(newModule) {
  // 支持多种导出格式，含弃用警告
  if (newModule.render) {
    console.warn("Direct render export is deprecated");
    return { async initialize() {}, render: newModule.render };
  }
  let afm = newModule.default;
  if (typeof afm === "function") afm = afm();
  return afm;
}

// 存储当前上下文（initialize 和 render 的状态）
let contexts = [];

// HMR accept：接受源文件更新
import.meta.hot.accept("__ANYWIDGET_HMR_SRC__", (newModule) => {
  const afm = getAFM(newModule);
  refresh(afm);
});

// 首次渲染
async function render({ model, el, signal, host }) {
  const mod = await import("__ANYWIDGET_HMR_SRC__");
  const afm = getAFM(mod);
  const ctx = { model, el, signal, host, cleanup: noop };
  contexts.push(ctx);
  await initializeAndRender(afm, ctx);
}

// HMR refresh：遍历所有上下文重新执行
async function refresh(afm) {
  for (const ctx of contexts) {
    // 执行旧 cleanup
    safeCleanup(ctx.cleanup);
    // 移除旧监听器
    ctx.model.off(null, null, ctx);
    // 清空 DOM
    emptyElement(ctx.el);
    // 创建新 AbortController
    const controller = new AbortController();
    ctx.signal.addEventListener("abort", () => controller.abort());
    // 重新执行 initialize 和 render
    await initializeAndRender(afm, { ...ctx, controller });
  }
}

async function initializeAndRender(afm, ctx) {
  const experimental = { invoke: createInvoke(ctx.model) };
  const initResult = await afm.initialize?.({
    model: ctx.model,
    signal: ctx.controller.signal,
    experimental,
  });
  if (typeof initResult === "function") {
    ctx.cleanup = initResult;
  }
  await afm.render?.({
    model: ctx.model,
    el: ctx.el,
    signal: ctx.controller.signal,
    host: ctx.host,
    experimental,
  });
}

// 导出 render 函数
export default { render };
```

### Vite 集成使用方式

在 Vite 配置中使用：

```javascript
// vite.config.js
import { defineConfig } from "vite";
import anywidget from "anywidget/vite";

export default defineConfig({
  plugins: [anywidget()],
});
```

Python 端使用 Vite 开发服务器 URL：

```python
class MyWidget(AnyWidget):
    _esm = "http://localhost:5173/widget.js?anywidget"
```

## AbortSignal 清理机制

[F-560] AbortSignal 是 HMR 正确清理资源的关键原语。在以下场景触发 abort：

| 场景 | AbortController 位置 | 清理效果 |
|------|---------------------|---------|
| ESM 重新加载 | Runtime createEffect 中新建 controller | 取消旧 initialize 的 signal，触发 cleanup |
| View 移除 | AnyView.#controller | 取消 render 的 signal，DOM 清理 |
| Model 销毁 | AnyModel initialize 中创建 | 清理 BINDINGS、RUNTIMES |
| HMR refresh | Vite hmr.js 新建 controller | 执行旧 cleanup、移除监听器、清空 DOM |

用户 ESM 代码中的正确清理模式：

```javascript
export default {
  render({ model, el, signal }) {
    const button = document.createElement("button");
    el.appendChild(button);
    
    const onClick = () => { /* ... */ };
    button.addEventListener("click", onClick);
    
    const interval = setInterval(() => { /* ... */ }, 1000);
    
    // 方式 1：返回 cleanup 函数
    return () => {
      button.removeEventListener("click", onClick);
      clearInterval(interval);
    };
    
    // 方式 2：监听 abort 事件（等价）
    // signal.addEventListener("abort", () => {
    //   button.removeEventListener("click", onClick);
    //   clearInterval(interval);
    // });
  }
}
```

## JS 工具函数

[F-416] JS 端工具函数：

```typescript
// 条件断言
function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(message);
}

// 安全执行 cleanup（catch 异常）
function safeCleanup(fn: unknown, kind: string = "cleanup") {
  if (typeof fn === "function") {
    try { fn(); }
    catch (e) { console.warn(`Error in ${kind}:`, e); }
  }
}

// Promise.withResolvers polyfill
function promiseWithResolvers<T>() {
  let resolve, reject;
  const promise = new Promise<T>((res, rej) => {
    resolve = res; reject = rej;
  });
  return { resolve, reject, promise };
}
```

## 相关文档

- ESM 前端协议与通信：[esm-protocol](esm-protocol.md)
- AnyWidget 基类与生命周期：[widget-base](widget-base.md)
- 描述符协议与文件管理：[descriptor](descriptor.md)
- 多框架桥接：[framework-bridges](framework-bridges.md)
