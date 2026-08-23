---
type: concept
title: "前端通信协议与Custom Messages"
description: "Comm 通道建立、消息类型体系（update/request_state/custom）、ESM 模块导出格式、CSS 加载、model proxy、Custom Messages 与 invoke RPC 模式"
prerequisites: ["02-trait-sync.md"]
sources:
  - "../references/esm-protocol.md"
  - "../references/widget-base.md"
  - "../references/framework-bridges.md"
generated: "2026-08-23"
verified: false
tags: ["anywidget", "jupyter", "communication", "comm", "custom-messages", "rpc"]
---

# 前端通信协议与 Custom Messages

trait 同步是数据绑定的基础，但真实应用还需要事件通知、命令调用、跨 Widget 引用等灵活通信模式。本文档讲解 Comm 通道、消息协议、ESM 导出格式、CSS 加载、Custom Messages 和 invoke RPC 模式。

## Comm 通道建立

Comm 是 Python Kernel 和浏览器之间的双向通信通道。anywidget 使用 Jupyter Widgets 标准的 `"jupyter.widget"` comm target。

Comm 在 `ReprMimeBundle` 首次实例化时创建（即 Jupyter 首次显示 Widget 时）：

```python
def open_comm(initial_state, version="2.1.0"):
    state = _replace_widget_refs(initial_state)
    state, buffer_paths, buffers = remove_buffers(state)
    return comm.create_comm(
        target_name="jupyter.widget",
        metadata={"version": version},
        data={
            "state": {
                "_model_module": "anywidget", "_model_name": "AnyModel",
                "_view_module": "anywidget", "_view_name": "AnyView",
                "_view_count": None, **state,
            },
            "buffer_paths": buffer_paths,
        },
        buffers=buffers,
    )
```

Comm 以 `id(obj)` 为键缓存，`weakref.finalize` 在对象 GC 时自动清理。JS 端 `_handle_comm_msg` 等待 Runtime ready 后才处理消息，确保 ESM 加载完成。

## 消息类型体系

| method | 方向 | 用途 | 载荷 |
|--------|------|------|------|
| `"update"` | Python ↔ JS | 同步状态变更 | `state`, `buffer_paths`, `buffers` |
| `"request_state"` | JS → Python | 请求完整状态 | 无 |
| `"custom"` | Python ↔ JS | 自定义消息/命令 | `content`（任意结构） |

### update 消息

双向状态同步的核心消息。Python → JS 通过 `comm.send()` 发送，JS 端 ipywidgets 框架自动更新 model 属性并触发 `change:` 事件。JS → Python 通过 `model.save_changes()` 发送，Python 端 `_handle_msg` 接收后还原 buffers 并设置状态。

### request_state 消息

JS 端在 reconnect 等场景发送 `{"method": "request_state"}`，Python 端响应 `send_state()` 发送完整状态。

### custom 消息

trait 同步之外的通用通信通道：

```javascript
// JS → Python
model.send({ kind: "button-clicked", timestamp: Date.now() });
model.on("msg:custom", (msg, buffers) => {
  if (msg.kind === "notification") console.log(msg.message);
});
```

```python
# Python → JS
widget.on_msg(lambda w, content, buffers: handle(content))
widget.send({"kind": "notification", "message": "Done"})
```

| 特性 | trait 同步 | custom messages |
|------|-----------|----------------|
| 模式 | 声明式属性绑定 | 命令式消息传递 |
| 自动同步 | ✅ | ❌ 手动 send/on_msg |
| 状态持久化 | ✅ 保存在 model state | ❌ 一次性消息 |

## ESM 模块导出格式

ESM 模块是前后端唯一契约，必须 `export default` 一个满足 `WidgetDef` 接口的值：

```typescript
interface WidgetDef<T> {
  initialize?: Initialize<T>;
  render?: Render<T>;
}
type AnyWidget<T> = WidgetDef<T> | (() => Awaitable<WidgetDef<T>>);
```

### 三种导出格式

**格式 1（推荐）：直接导出对象**

```javascript
export default {
  async initialize({ model, signal, experimental }) {
    return () => { /* cleanup */ };
  },
  async render({ model, el, signal, host, experimental }) {
    el.innerHTML = "<div>Hello</div>";
    return () => { /* cleanup */ };
  }
}
```

**格式 2：导出异步函数（支持异步导入）**

```javascript
export default async function() {
  const { Chart } = await import("chart.js/auto");
  return { render({ model, el }) { /* 使用 Chart */ } };
}
```

**格式 3（已弃用）：直接导出 render**——框架自动包装但发出弃用警告。

### initialize 与 render 参数差异

| 参数 | initialize | render | 说明 |
|------|:----------:|:------:|------|
| `model` | ✅ | ✅ | AnyModel 代理对象 |
| `signal` | ✅ | ✅ | AbortSignal 清理信号 |
| `experimental` | ✅ | ✅ | invoke 命令调用 API |
| `el` | ❌ | ✅ | DOM 容器元素 |
| `host` | ❌ | ✅ | 跨 Widget 引用 API |

initialize 无 `el`/`host` 是因为它在 Model 级别运行——一个 Model 可对应多个 View。

## CSS 加载机制

CSS 通过 `_css` trait 同步到前端，两种注入方式：

- **CSS 文本**：通过 `<style id="anywidget-{id}">` 注入 `document.head`，热更新时直接替换 textContent
- **CSS URL**：通过 `<link rel="stylesheet">` 注入，热更新时先创建新 link 等待加载完成，再移除旧 link，避免 FOUC（样式闪烁）

```python
class StyledWidget(anywidget.AnyWidget):
    _css = ".my-widget { color: red; }"               # 内联
    _css = pathlib.Path(__file__).parent / "w.css"    # 外部文件
```

## model proxy：上下文感知监听器

传递给 initialize/render 的 `model` 是 `modelProxy()` 创建的 Proxy，将 `on`/`off` 方法绑定到特定 context 标记：

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

- initialize 阶段使用 `INITIALIZE_MARKER` Symbol 作为 context
- render 阶段使用 view 实例作为 context
- ESM 重载时 `model.off(null, null, INITIALIZE_MARKER)` 批量清除 initialize 监听器
- View 销毁时 `model.off(null, null, view)` 批量清除 render 监听器

这避免了手动追踪每个监听器的清理。

## invoke 模式：基于 UUID 的 RPC

`experimental.invoke()` 实现 JS → Python 请求-响应模式，基于 custom messages 和 UUID 匹配：

1. JS 生成 UUID，发送 `{id, kind: "anywidget-command", name, msg}`
2. Python 匹配 kind 后调用 `@command` 标记的方法
3. Python 发回 `{id, kind: "anywidget-command-response", response}`
4. JS 通过 id 匹配响应，resolve Promise；默认 3 秒超时

### Python 端：@command 装饰器

```python
from anywidget.experimental import command

class CalculatorWidget(anywidget.AnyWidget):
    _esm = """
    export default {
      async render({ model, el, experimental }) {
        const btn = document.createElement("button");
        btn.textContent = "Compute";
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
        return {"sum": msg["a"] + msg["b"]}, []  # (response, buffers)
```

命令在 `__init_subclass__` 时自动收集（遍历 MRO），在 `__init__` 时注册 on_msg 回调。

### 带二进制数据的命令

```javascript
const buffer = new Uint8Array([1,2,3]).buffer;
const [result, respBufs] = await experimental.invoke(
  "process", { width: 100 }, { buffers: [new DataView(buffer)] }
);
```

```python
@command
def process(self, msg, buffers):
    data = bytes(buffers[0])
    return {"status": "ok"}, [b"result"]
```

## Host API：跨 Widget 引用

Host API 允许 Widget 引用其他 Widget，实现组合嵌套：

```typescript
interface Host {
  getModel<T>(ref: string): Promise<AnyModel<T>>;  // 获取子 model
  getWidget<T>(ref: string): Promise<ResolvedWidget<T>>;  // 获取完整视图+exports
}
```

```javascript
// 父 Widget 渲染子 Widget
async render({ model, el, host }) {
  const childRef = model.get("child");  // "anywidget:<model_id>"
  const child = await host.getWidget(childRef);
  const container = document.createElement("div");
  el.appendChild(container);
  await child.render({ el: container });
  console.log(child.exports);  // 访问子 Widget 的 initialize 返回值
}
```

Widget 引用字符串格式为 `"anywidget:<model_id>"`，Python 端 `WidgetTrait` 自动序列化，JS 端 `parseWidgetRef` 解析后通过 `widget_manager.get_model()` 获取子 model。

## 相关示例

- [双向绑定高级用法](../examples/two-way-binding.md) — custom messages、@command、invoke RPC、二进制传输
- [Counter Widget 入门示例](../examples/counter-widget.md) — model.get/set/save_changes 基础通信
