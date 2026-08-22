---
type: example
title: "双向绑定高级用法"
description: "深入掌握 anywidget 的多类型 Trait 同步、自定义消息、@observe 回调、@command 命令和二进制数据传输。"
prerequisites: ["02-trait-sync.md", "03-frontend-communication.md"]
sources:
  - "../references/traits.md"
  - "../references/framework-bridges.md"
  - "../concepts/02-trait-sync.md"
  - "../concepts/03-frontend-communication.md"
generated: "2026-08-23"
verified: false
tags: ["anywidget", "jupyter", "example", "two-way-binding", "observe", "custom-messages"]
---

# 双向绑定高级用法

本示例深入演示多类型 Trait 同步、Python `@observe` 监听、JS `model.on` 响应、自定义消息、`@command` RPC 调用和二进制数据传输。

## 前置条件

- 已完成 [Counter Widget 入门](counter-widget.md)
- 理解 Trait 同步基本概念（见 [Trait同步与双向绑定](../concepts/02-trait-sync.md)）

## 步骤 1：多类型 Trait

```python
import anywidget, traitlets, pathlib

class DataWidget(anywidget.AnyWidget):
    count = traitlets.Int(0).tag(sync=True)
    ratio = traitlets.Float(0.5).tag(sync=True)
    name = traitlets.Unicode("世界").tag(sync=True)
    enabled = traitlets.Bool(True).tag(sync=True)
    items = traitlets.List(traitlets.Unicode(), default_value=["苹果", "香蕉"]).tag(sync=True)
    _esm = pathlib.Path(__file__).parent / "data_widget.js"
```

前端 `data_widget.js` 核心模式（以 ratio 滑块为例）：

```javascript
export default {
  render({ model, el }) {
    // JS → Python：输入事件触发同步
    const ratioIn = document.createElement("input");
    ratioIn.type = "range"; ratioIn.min = 0; ratioIn.max = 1; ratioIn.step = 0.01;
    ratioIn.value = model.get("ratio");
    ratioIn.addEventListener("input", () => {
      model.set("ratio", parseFloat(ratioIn.value));
      model.save_changes();
    });

    // Python → JS：监听 change 事件更新 DOM
    model.on("change:ratio", () => { ratioIn.value = model.get("ratio"); });

    // 其他类型同理：Unicode→input[type=text], Bool→checkbox, List→ul/li
    el.appendChild(ratioIn);
  }
}
```

## 步骤 2：Python 端 @observe

使用 `@observe` 监听 trait 变化执行副作用：

```python
from traitlets import observe

class FormWidget(anywidget.AnyWidget):
    username = traitlets.Unicode("").tag(sync=True)
    email = traitlets.Unicode("").tag(sync=True)
    age = traitlets.Int(0).tag(sync=True)
    _message = traitlets.Unicode("").tag(sync=True)  # 同步验证消息到前端
    _esm = pathlib.Path(__file__).parent / "form.js"

    @observe("username", "email", "age")
    def _validate(self, change):
        errors = []
        if len(self.username) < 2: errors.append("用户名至少2字符")
        if "@" not in self.email: errors.append("邮箱格式不正确")
        if self.age < 0 or self.age > 150: errors.append("年龄不合法")
        self._message = "✓ 有效" if not errors else "⚠ " + "; ".join(errors)
```

前端监听 `_message` 变化即可实时显示验证结果。

## 步骤 3：自定义消息（Custom Messages）

Trait 同步适合状态数据，事件型消息使用 `model.send()`（JS→Python）和 `self.send()`（Python→JS）：

```python
class TodoWidget(anywidget.AnyWidget):
    todos = traitlets.List(traitlets.Dict(), default_value=[]).tag(sync=True)
    _esm = pathlib.Path(__file__).parent / "todo.js"

    def __init__(self, **kw):
        super().__init__(**kw)
        self.on_msg(self._handle_msg)

    def _handle_msg(self, msg, buffers):
        if msg.get("type") == "add":
            text = msg.get("text", "").strip()
            if text:
                self.todos = list(self.todos) + [{"text": text, "done": False}]
        elif msg.get("type") == "toggle":
            i = msg["index"]
            if 0 <= i < len(self.todos):
                ts = list(self.todos)
                ts[i] = {**ts[i], "done": not ts[i]["done"]}
                self.todos = ts
        elif msg.get("type") == "clear-done":
            self.todos = [t for t in self.todos if not t["done"]]

    def notify(self, text):
        """Python 主动通知前端"""
        self.send({"type": "notify", "text": text})
```

前端 `todo.js`：

```javascript
export default {
  render({ model, el }) {
    el.innerHTML = `
      <input id="inp" placeholder="添加待办..."> <button id="add">+</button>
      <ul id="list"></ul> <button id="clear">清除已完成</button>
      <div id="notif"></div>`;
    const inp = el.querySelector("#inp"), addBtn = el.querySelector("#add");
    const list = el.querySelector("#list"), clearBtn = el.querySelector("#clear");
    const notif = el.querySelector("#notif");

    // JS → Python 自定义消息
    addBtn.addEventListener("click", () => {
      if (inp.value.trim()) { model.send({ type: "add", text: inp.value }); inp.value = ""; }
    });
    clearBtn.addEventListener("click", () => model.send({ type: "clear-done" }));

    // 渲染列表
    function render() {
      list.innerHTML = "";
      model.get("todos").forEach((t, i) => {
        const li = document.createElement("li");
        li.innerHTML = `<input type="checkbox" ${t.done?"checked":""}> ${t.text}`;
        li.style.textDecoration = t.done ? "line-through" : "none";
        li.querySelector("input").addEventListener("change", () => model.send({ type: "toggle", index: i }));
        list.appendChild(li);
      });
    }
    render();
    model.on("change:todos", render);

    // Python → JS 自定义消息
    model.on("msg:custom", (msg) => {
      if (msg.type === "notify") {
        notif.textContent = msg.text;
        notif.style.opacity = "1";
        setTimeout(() => notif.style.opacity = "0", 2000);
      }
    });
  }
}
```

## 步骤 4：@command + experimental.invoke()（RPC 模式）

`@command` 装饰器将 Python 方法暴露为 JS 可调用的 RPC 命令，支持请求-响应和自动超时：

```python
from anywidget.experimental import command

class MathWidget(anywidget.AnyWidget):
    _esm = pathlib.Path(__file__).parent / "math.js"

    @command
    def fibonacci(self, n, buffers):
        """计算斐波那契第 n 项"""
        if n <= 0: return 0
        a, b = 1, 1
        for _ in range(n - 2): a, b = b, a + b
        return b if n > 2 else 1

    @command
    def stats(self, numbers, buffers):
        """计算统计值"""
        if not numbers: return {"count": 0, "mean": 0}
        return {"count": len(numbers), "sum": sum(numbers),
                "mean": sum(numbers)/len(numbers), "min": min(numbers), "max": max(numbers)}
```

前端通过 `experimental.invoke(name, msg)` 调用：

```javascript
export default {
  render({ model, el, experimental }) {
    el.innerHTML = `
      <label>n=<input id="n" type="number" value="10"></label>
      <button id="fib">计算斐波那契</button> <span id="fib-r"></span><br>
      <label>数字<input id="nums" value="1,2,3,4,5"></label>
      <button id="stat">统计</button> <pre id="stat-r"></pre>`;

    el.querySelector("#fib").addEventListener("click", async () => {
      const n = parseInt(el.querySelector("#n").value);
      el.querySelector("#fib-r").textContent = "...";
      try {
        const [result] = await experimental.invoke("fibonacci", n);
        el.querySelector("#fib-r").textContent = "= " + result;
      } catch(e) { el.querySelector("#fib-r").textContent = "错误"; }
    });

    el.querySelector("#stat").addEventListener("click", async () => {
      const nums = el.querySelector("#nums").value.split(",").map(s=>parseFloat(s.trim()));
      const [result] = await experimental.invoke("stats", nums);
      el.querySelector("#stat-r").textContent = JSON.stringify(result, null, 2);
    });
  }
}
```

`experimental.invoke()` 默认 3 秒超时，内部用 uuid 匹配请求/响应，返回 `[response, buffers]` 元组。

## 步骤 5：二进制数据传输

bytes/bytearray/memoryview 类型的数据自动分离为独立 buffers 传输，不经过 JSON 序列化：

```python
class ImageWidget(anywidget.AnyWidget):
    width = traitlets.Int(128).tag(sync=True)
    height = traitlets.Int(128).tag(sync=True)
    _esm = pathlib.Path(__file__).parent / "image.js"

    def __init__(self, **kw):
        super().__init__(**kw)
        self.on_msg(self._handle_msg)
        self._send_image()

    def _send_image(self):
        import random
        pixels = bytearray(self.width * self.height)
        for i in range(len(pixels)):
            pixels[i] = random.randint(0, 255)
        self.send({"type": "image", "w": self.width, "h": self.height},
                  buffers=[bytes(pixels)])

    def _handle_msg(self, msg, buffers):
        if msg.get("type") == "regen":
            self._send_image()
```

前端通过 `buffers` 参数接收二进制数据：

```javascript
export default {
  render({ model, el }) {
    el.innerHTML = `<canvas id="cv"></canvas> <button id="regen">重新生成</button>`;
    const cv = el.querySelector("#cv"), ctx = cv.getContext("2d");

    el.querySelector("#regen").addEventListener("click", () => model.send({ type: "regen" }));

    model.on("msg:custom", (msg, buffers) => {
      if (msg.type === "image" && buffers.length > 0) {
        cv.width = msg.w; cv.height = msg.h;
        const img = ctx.createImageData(msg.w, msg.h);
        const src = new Uint8Array(buffers[0].buffer, buffers[0].byteOffset, buffers[0].byteLength);
        for (let i = 0; i < src.length; i++) {
          img.data[i*4] = src[i]; img.data[i*4+1] = src[i];
          img.data[i*4+2] = src[i]; img.data[i*4+3] = 255;
        }
        ctx.putImageData(img, 0, 0);
      }
    });
  }
}
```

## 通信模式对比

| 模式 | 方向 | 场景 | API |
|------|------|------|-----|
| Trait sync | 双向 | 状态数据 | `.tag(sync=True)` + `model.get/set/save_changes` |
| Custom msg | 双向 | 事件/操作 | `model.send()` / `self.send()` / `on_msg` |
| @command | JS→Python→JS | RPC 请求-响应 | `@command` + `experimental.invoke()` |
| Binary buffers | 双向 | 图像/大数据 | `send(msg, buffers=[...])` / buffers 参数 |

## 相关概念

- [Trait同步与双向绑定](../concepts/02-trait-sync.md) — 双向绑定原理、多态状态适配和二进制传输
- [前端通信协议](../concepts/03-frontend-communication.md) — Comm 消息类型、Custom Messages 和命令调用
- [多框架桥接与命令调用](../references/framework-bridges.md) — @command、experimental.invoke 和 Host API 参考
