---
type: example
title: "Counter Widget 入门示例"
description: "从零构建一个简单的计数器 Widget，演示 AnyWidget 继承、ESM 绑定、Trait 同步和点击事件处理的完整流程。"
prerequisites: ["00-overall-architecture.md", "01-widget-lifecycle.md"]
sources:
  - "../references/widget-base.md"
  - "../references/esm-protocol.md"
  - "../concepts/00-overall-architecture.md"
  - "../concepts/01-widget-lifecycle.md"
generated: "2026-08-23"
verified: false
tags: ["anywidget", "jupyter", "example", "counter", "getting-started"]
---

# Counter Widget 入门示例

从零构建一个最小可运行的 anywidget 计数器。你将掌握：定义 AnyWidget 子类、声明同步 Trait、编写内联 ESM 前端代码、处理点击事件实现双向绑定。

## 前置条件

- Python ≥ 3.10，已安装 `anywidget`（`pip install anywidget`）
- Jupyter Lab 或 Jupyter Notebook

## 步骤 1：最简版本——内联 ESM 字符串

创建 `counter.py`：

```python
import anywidget
import traitlets

class CounterWidget(anywidget.AnyWidget):
    # 声明 Int trait，sync=True 表示与前端双向同步
    value = traitlets.Int(0).tag(sync=True)

    # 内联 ESM：前端代码字符串，零构建
    _esm = """
    export default {
      render({ model, el }) {
        const btn = document.createElement("button");
        btn.className = "counter-btn";

        const update = () => btn.textContent = `count is ${model.get("value")}`;
        update();

        // Python → JS：监听 trait 变化自动更新
        model.on("change:value", update);

        // JS → Python：点击按钮修改值并同步
        btn.addEventListener("click", () => {
          model.set("value", model.get("value") + 1);
          model.save_changes();
        });

        el.appendChild(btn);
      }
    }
    """

    # 内联 CSS
    _css = """
    .counter-btn {
      background: #4f46e5; color: #fff; border: none;
      border-radius: 8px; padding: 10px 20px;
      font-size: 16px; cursor: pointer;
    }
    .counter-btn:hover { background: #4338ca; }
    """
```

### 关键代码解读

- **继承 `AnyWidget`**：基类处理 comm 通道、ESM 加载等底层逻辑（见 [Widget基类与生命周期](../concepts/01-widget-lifecycle.md)）
- **`value = Int(0).tag(sync=True)`**：标记 trait 需要在 Python↔JS 间双向同步
- **`_esm`**：ESM 模块字符串，必须 `export default { render }`，render 接收 `{ model, el }`
- **`model.get/set/save_changes`**：读取/修改/同步前端状态到 Python
- **`model.on("change:key", cb)`**：监听 Python 端 trait 变化
- **`_css`**：内联样式，自动注入页面

## 步骤 2：在 Jupyter 中使用

```python
from counter import CounterWidget
w = CounterWidget()
w          # 显示 widget，点击按钮计数增加
w.value    # 读取当前值
w.value = 42  # Python 端直接修改，前端自动更新
```

## 步骤 3：外部 ESM 文件 + 热更新

当前端代码变复杂时，使用外部文件路径更易维护。

创建 `counter.js`（与 counter.py 同目录）：

```javascript
export default {
  render({ model, el }) {
    const btn = document.createElement("button");
    btn.className = "counter-btn";
    const update = () => btn.textContent = `count is ${model.get("value")}`;
    update();
    model.on("change:value", update);
    btn.addEventListener("click", () => {
      model.set("value", model.get("value") + 1);
      model.save_changes();
    });
    el.appendChild(btn);
  }
}
```

修改 `counter.py` 使用 pathlib.Path 引用外部文件：

```python
import pathlib, anywidget, traitlets

class CounterWidget(anywidget.AnyWidget):
    value = traitlets.Int(0).tag(sync=True)
    _esm = pathlib.Path(__file__).parent / "counter.js"
    _css = ".counter-btn { background: #4f46e5; color: #fff; ... }"
```

类定义时 `__init_subclass__` 自动将路径转为 `FileContents` 实例（F-553）。设置环境变量启用热更新：

```python
import os; os.environ["ANYWIDGET_HMR"] = "1"  # 需 pip install watchfiles
from counter import CounterWidget
w = CounterWidget()
w  # 修改 counter.js 保存后，浏览器自动重新渲染
```

## 步骤 4：initialize 生命周期与 AbortSignal

`initialize` 在 model 绑定时调用（早于 render），适合一次性初始化。返回的 cleanup 函数在 widget 销毁/热更新时通过 AbortSignal 自动执行：

```javascript
export default {
  initialize({ model, signal }) {
    const onKey = (e) => {
      if (e.key === "+") { model.set("value", model.get("value") + 1); model.save_changes(); }
      if (e.key === "-") { model.set("value", model.get("value") - 1); model.save_changes(); }
    };
    document.addEventListener("keydown", onKey);
    // signal 在销毁时 abort，自动清理
    signal.addEventListener("abort", () => document.removeEventListener("keydown", onKey));
  },
  render({ model, el }) {
    const btn = document.createElement("button");
    btn.className = "counter-btn";
    const update = () => btn.textContent = `count is ${model.get("value")}`;
    update();
    model.on("change:value", update);
    btn.addEventListener("click", () => {
      model.set("value", model.get("value") + 1);
      model.save_changes();
    });
    el.appendChild(btn);
  }
}
```

initialize 阶段没有 `el` 和 `host`，仅接收 `{ model, signal, experimental }`（F-558）。

## 步骤 5：加减按钮 + 重置

```javascript
export default {
  render({ model, el }) {
    el.className = "counter-wrap";

    const dec = document.createElement("button"); dec.textContent = "−"; dec.className = "btn dec";
    const span = document.createElement("span"); span.className = "val";
    const inc = document.createElement("button"); inc.textContent = "+"; inc.className = "btn inc";
    const reset = document.createElement("button"); reset.textContent = "Reset"; reset.className = "btn reset";

    const update = () => span.textContent = model.get("value");
    update();
    model.on("change:value", update);

    dec.addEventListener("click", () => { model.set("value", model.get("value") - 1); model.save_changes(); });
    inc.addEventListener("click", () => { model.set("value", model.get("value") + 1); model.save_changes(); });
    reset.addEventListener("click", () => { model.set("value", 0); model.save_changes(); });

    el.append(dec, span, inc, reset);
  }
}
```

```css
.counter-wrap { display: flex; align-items: center; gap: 10px; font-family: system-ui; }
.btn { border: none; border-radius: 6px; padding: 6px 14px; font-size: 16px; cursor: pointer; font-weight: bold; }
.dec { background: #ef4444; color: #fff; } .inc { background: #22c55e; color: #fff; }
.reset { background: #6b7280; color: #fff; font-size: 13px; }
.val { font-size: 24px; font-weight: bold; min-width: 40px; text-align: center; }
```

## API 速查

| API | 用途 |
|-----|------|
| `model.get("key")` | 读取 trait 值 |
| `model.set("key", value)` | 设置值（需 save_changes 才同步） |
| `model.save_changes()` | 发送变更到 Python |
| `model.on("change:key", cb)` | 监听 trait 变化 |
| `model.on("msg:custom", cb)` | 监听自定义消息 |
| `model.send(content, null, buffers)` | 发送自定义消息 |
| `signal.addEventListener("abort", cb)` | 注册清理回调 |

## 相关概念

- [整体架构与ESM协议](../concepts/00-overall-architecture.md) — Python-JS 双层架构和 ESM 零构建理念
- [Widget基类与生命周期](../concepts/01-widget-lifecycle.md) — initialize/render 两阶段和 AbortSignal 清理模式
- [Trait同步与双向绑定](../concepts/02-trait-sync.md) — 多类型 trait 和双向绑定原理
- [ESM前端协议与通信](../references/esm-protocol.md) — ESM 格式和加载机制完整参考
