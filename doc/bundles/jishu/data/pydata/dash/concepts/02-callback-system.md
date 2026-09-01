---
okf_version: "0.2"
type: concept
title: 回调系统
description: Dash的响应式回调机制——@callback装饰器、Input/Output/State依赖声明、_callback.py执行逻辑、callback_context回调上下文、prevent_update/无输出、多输入多输出、回调链依赖图、background_callback背景回调
tags: [Dash, callback, Input, Output, State, 响应式, callback_context, PreventUpdate, 背景回调, 依赖图]
generated:
  by: reference_agent/trae-glm
  at: 2026-08-22T15:00:00Z
verified:
  by: "process:seven-concepts-v"
  at: 2026-08-22T15:30:00Z
status: stable
stale_after: 2027-12-31
sources:
  - id: dash-callback
    resource: external/libs/python/dash/dash/_callback.py
    title: 回调注册与执行核心模块
  - id: dash-dependencies
    resource: external/libs/python/dash/dash/dependencies.py
    title: Input/Output/State依赖定义
  - id: dash-callback-context
    resource: external/libs/python/dash/dash/_callback_context.py
    title: 回调上下文模块
  - id: dash-class-callback
    resource: external/libs/python/dash/dash/dash.py
    title: Dash类中的callback方法与回调执行
  - id: dash-background
    resource: external/libs/python/dash/dash/background_callback/
    title: 背景回调管理器
---

# 回调系统

回调系统是 Dash 响应式编程模型的核心。开发者通过 `@app.callback` 装饰器声明"当哪些输入组件属性变化时，应该更新哪些输出组件属性"，框架自动管理依赖追踪、请求调度和 UI 更新。

## 回调基础

### 依赖声明三要素

dependencies.py 定义了三种依赖类型，都继承自 `DashDependency` 基类（dependencies.py:40）：

| 类 | 作用 | 是否触发回调 | 支持的通配符 |
|----|------|-------------|-------------|
| `Output(component_id, component_property)` | 声明回调的输出 | — | MATCH, ALL |
| `Input(component_id, component_property)` | 声明触发回调的输入 | ✓ 是 | MATCH, ALL, ALLSMALLER |
| `State(component_id, component_property)` | 读取当前值但不触发 | ✗ 否 | MATCH, ALL, ALLSMALLER |

构造参数：
- `component_id`：组件 ID（字符串、dict 或 Component 实例）
- `component_property`：属性名（如 `"children"`、`"figure"`、`"value"`、`"n_clicks"`）
- `allow_duplicate`（Output）：允许多个回调输出同一属性
- `allow_optional`（Input/State）：标记为可选依赖

### 基本回调示例

```python
from dash import Dash, Input, Output, dcc, html

app = Dash(__name__)
app.layout = html.Div([
    dcc.Input(id="my-input", value="初始值"),
    html.Div(id="my-output"),
])

@app.callback(
    Output("my-output", "children"),  # 输出：更新 my-output 的 children
    Input("my-input", "value"),       # 输入：监听 my-input 的 value 变化
)
def update_output(value):
    return f"你输入了: {value}"
```

当用户在输入框中打字时，`my-input.value` 变化 → 前端自动 POST 请求到后端 → 执行 `update_output` → 返回值更新 `my-output.children` → React 重新渲染 DOM。

### @callback 装饰器

Dash 支持两种装饰器（_callback.py:74）：

1. **`@app.callback(...)`**：绑定到特定 app 实例
2. **`@dash.callback(...)`**（v2.0+）：模块级注册，在首次请求时自动合并到 app

两者签名完全一致，`app.callback` 内部委托给 `_callback.callback()` 函数。

## 回调注册机制

### 参数解析

`handle_grouped_callback_args()`（dependencies.py:332-363）负责解析回调参数：

1. 支持老式语法（`Output(...)` 列表、`Input(...)` 列表、`State(...)` 列表分开传递）
2. 支持新式分组语法（直接按顺序传递，自动区分 Output/Input/State）
3. 支持 dict 形式的命名参数：
   ```python
   @app.callback(
       output=Output("out", "children"),
       inputs=dict(x=Input("x", "value"), y=Input("y", "value")),
   )
   def update(x, y): ...
   ```
4. 最后一个布尔参数 `prevent_initial_call` 可简写为位置参数

### 回调注册数据结构

注册后的回调存储在两个数据结构中（_callback.py:330-374）：

**callback_map（dict）**——后端调度使用：
```python
callback_map["my-output.children"] = {
    "inputs": [{"id": "my-input", "property": "value"}],
    "state": [],
    "outputs_indices": ...,       # 输出分组索引
    "inputs_state_indices": ...,  # 输入/状态分组索引
    "callback": func,             # Python 回调函数
    "raw_inputs": [Input(...)],   # 原始依赖对象
    "no_output": False,           # 是否无输出
    "background": None,           # 背景回调配置
    "manager": None,              # 背景回调管理器
}
```

**_callback_list（list）**——前端依赖图使用：
```python
{
    "output": "my-output.children",
    "inputs": [{"id": "my-input", "property": "value"}],
    "state": [],
    "prevent_initial_call": False,
    "clientside_function": None,
    "no_output": False,
}
```

每个回调通过 `create_callback_id()` 生成唯一 ID（基于 output 和 inputs 的哈希）。

## 回调执行流程

### 请求处理

当组件属性变化时，dash-renderer 向后端发送 POST 请求到 `_dash-update-component`，请求体包含：

```json
{
  "output": "my-output.children",
  "outputs": {"id": "my-output", "property": "children"},
  "inputs": [{"id": "my-input", "property": "value", "value": "hello"}],
  "state": [],
  "changedPropIds": ["my-input.value"]
}
```

后端处理流程（dash.py:1601-1700）：

1. **`_initialize_context(body)`**：初始化全局上下文 `g`，包含 `input_values`、`state_values`、`triggered_inputs` 等
2. **`_prepare_callback(g, body)`**：从 `callback_map` 查找回调函数，准备参数分组
3. **`_execute_callback(func, args, outputs_list, g)`**：构建 `functools.partial`，注入回调上下文
4. 实际调用回调函数，获取返回值
5. 序列化返回值为 JSON 响应

### 回调上下文（callback_context）

_callback_context.py 提供 `CallbackContext` 类，通过 `dash.callback_context`（或别名 `dash.ctx`）访问：

```python
from dash import callback_context, ctx

@app.callback(Output("out", "children"), Input("btn1", "n_clicks"), Input("btn2", "n_clicks"))
def update(btn1, btn2):
    # 哪个输入触发了回调？
    triggered = ctx.triggered  # [{"prop_id": "btn1.n_clicks", "value": 1}]
    if not ctx.triggered:      # 初始加载时 triggered 为空（falsy）
        return "初始状态"

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # 访问所有输入/状态值
    all_inputs = ctx.inputs    # {"btn1.n_clicks": 1, "btn2.n_clicks": 0}
    all_states = ctx.states    # State 的值

    # 访问触发的属性 ID 字典（模式匹配回调）
    triggered_ids = ctx.triggered_prop_ids

    # 访问响应对象（设置 cookies/headers）
    ctx.response.set_cookie("key", "value")
```

上下文使用 Python 的 `contextvars.ContextVar`（_callback_context.py:13-16）实现，支持异步回调中的正确隔离。

### 参数分组

Dash 支持灵活的参数传递方式：

**位置参数**（默认）：按 Input + State 的声明顺序传递
```python
@app.callback(Output("out", "children"), Input("a", "value"), State("b", "value"))
def update(a_val, b_val): ...
```

**字典参数**（命名）：使用 dict 声明 Input/State，回调接收关键字参数
```python
@app.callback(
    Output("out", "children"),
    inputs=dict(x=Input("x", "value"), y=Input("y", "value")),
)
def update(x, y): ...
```

**分组嵌套**：使用 list/tuple 嵌套组织参数，回调接收对应嵌套结构
```python
@app.callback(
    Output("out", "children"),
    [Input("a", "value"), Input("b", "value")],
)
def update(args):  # args 是 [a_value, b_value]
    a_val, b_val = args
```

## 多输入多输出

### 多输入

多个 Input 是"或"关系——任意一个变化都触发回调：

```python
@app.callback(
    Output("graph", "figure"),
    Input("x-dropdown", "value"),
    Input("y-dropdown", "value"),
    Input("size-slider", "value"),
)
def update_graph(x, y, size):
    # 任意输入变化都会执行
    return create_figure(x, y, size)
```

### 多输出

一个回调可以更新多个 Output（Dash 2.0+），返回值顺序必须与 Output 声明顺序一致：

```python
@app.callback(
    Output("graph", "figure"),
    Output("stats", "children"),
    Output("status", "color"),
    Input("dropdown", "value"),
)
def update_all(value):
    fig = create_figure(value)
    stats = f"数据点: {len(data)}"
    color = "green" if valid else "red"
    return fig, stats, color  # 返回元组，顺序对应 Output
```

### 无输出回调

回调可以没有 Output，用于执行副作用（如发送通知、写数据库）：

```python
@app.callback(
    Input("send-btn", "n_clicks"),
    prevent_initial_call=True,
)
def send_email(n_clicks):
    # 执行副作用，不需要返回值
    pass  # 或返回 dash.no_update
```

## 控制回调行为

### prevent_initial_call

默认情况下，页面加载时所有回调都会执行一次（初始调用），以填充输出。使用 `prevent_initial_call=True` 禁用：

```python
@app.callback(
    Output("out", "children"),
    Input("btn", "n_clicks"),
    prevent_initial_call=True,  # 页面加载时不执行
)
def on_click(n):
    return f"点击了 {n} 次"
```

也可以在 app 级别全局设置 `prevent_initial_callbacks=True`。

### PreventUpdate 和 no_update

回调中可以抛出 `PreventUpdate` 异常或返回 `no_update` 来阻止更新：

```python
from dash import PreventUpdate, no_update

@app.callback(Output("out", "children"), Input("input", "value"))
def update(value):
    if not value:
        raise PreventUpdate  # 不更新输出
    return f"值: {value}"

# 多输出中部分不更新
@app.callback(
    Output("a", "children"),
    Output("b", "children"),
    Input("x", "value"),
)
def update(x):
    if x < 0:
        return no_update, "负数"  # a 不更新，b 更新
    return str(x), "正数"
```

`no_update` 是 `NoUpdate` 类的单例实例（dash.py:216），比 `PreventUpdate` 更灵活（支持部分更新）。

### set_props 侧边更新

从回调中直接设置其他组件的属性，无需声明为 Output：

```python
from dash import set_props

@app.callback(Input("btn", "n_clicks"), prevent_initial_call=True)
def on_click(n):
    set_props("alert", {"is_open": True, "children": "操作成功！"})
```

`set_props` 更新的属性会通过响应中的 `sideUpdate` 字段返回给前端（_callback.py:377-382）。

## 回调链与依赖图

多个回调可以串联形成回调链——一个回调的 Output 是另一个回调的 Input：

```python
# 回调1: 下拉框 → 过滤数据
@app.callback(Output("filtered-data", "data"), Input("category", "value"))
def filter_data(category):
    return [d for d in all_data if d["category"] == category]

# 回调2: 过滤后数据 → 更新图表
@app.callback(Output("graph", "figure"), Input("filtered-data", "data"))
def update_graph(data):
    return px.bar(data, x="name", y="value")
```

dash-renderer 在前端构建依赖图（有向无环图），按拓扑顺序执行回调。初始加载时从没有依赖的"叶子"回调开始，逐步传播到下游。

### 循环依赖检测

`_validate.validate_callback()` 在注册时检测循环依赖，防止 A→B→C→A 这样的死循环。

## 模式匹配回调（Pattern-Matching Callbacks）

通过 dict 类型的 ID 和通配符（MATCH/ALL/ALLSMALLER）实现动态数量组件的回调：

```python
from dash import MATCH, ALL, ALLSMALLER

# 动态创建多个输入框，每个都有对应的回调
@app.callback(
    Output({"type": "result", "index": MATCH}, "children"),
    Input({"type": "input", "index": MATCH}, "value"),
)
def update_result(value):
    return f"结果: {value}"

# ALL 匹配所有同类型组件
@app.callback(
    Output("total", "children"),
    Input({"type": "input", "index": ALL}, "value"),
)
def sum_all(values):
    return f"总和: {sum(float(v or 0) for v in values)}"
```

通配符含义（dependencies.py:13-27）：
- `MATCH`：匹配相同 key-value 的组件
- `ALL`：匹配所有满足其他 key 条件的组件，值作为列表传递
- `ALLSMALLER`：匹配 index 小于当前组件的所有同类型组件

## 客户端回调（Clientside Callback）

回调逻辑可以在浏览器端用 JavaScript 执行，避免网络往返：

```python
from dash import ClientsideFunction

app.clientside_callback(
    ClientsideFunction(namespace="my_namespace", function_name="myFunction"),
    Output("out", "children"),
    Input("in", "value"),
)

# 或直接传入 JS 代码字符串
app.clientside_callback(
    """
    function(value) {
        return '客户端: ' + value;
    }
    """,
    Output("out", "children"),
    Input("in", "value"),
)
```

JS 函数需要在 `assets/` 目录的 JS 文件中定义，挂载到 `window.dash_clientside.my_namespace` 下。

## 背景回调（Background Callback）

长时间运行的回调可以使用 `background=True`，在后台进程/worker 中执行，不阻塞前端：

```python
from dash import CeleryManager, DiskcacheManager
import diskcache

cache = diskcache.Cache("./cache")
background_manager = DiskcacheManager(cache)

app = Dash(__name__, background_callback_manager=background_manager)

@app.callback(
    Output("result", "children"),
    Input("run-btn", "n_clicks"),
    background=True,                     # 标记为背景回调
    running=[                            # 运行时状态
        (Output("progress", "style"), {"display": "block"}, {"display": "none"}),
        (Output("run-btn", "disabled"), True, False),
    ],
    progress=[Output("progress-bar", "value"), Output("progress-bar", "max")],
    cancel=[Input("cancel-btn", "n_clicks")],
    prevent_initial_call=True,
)
def update(n_clicks, set_progress):
    for i in range(100):
        time.sleep(0.1)
        set_progress((str(i + 1), "100"))  # 更新进度
    return "完成！"
```

背景回调关键参数（_callback.py:76-93）：

| 参数 | 说明 |
|------|------|
| `background=True` | 启用背景回调 |
| `manager` | 背景回调管理器（DiskcacheManager 或 CeleryManager） |
| `running` | 运行中组件状态列表：`(Output, 运行时值, 完成时值)` |
| `progress` | 进度输出组件，回调接收 `set_progress` 函数作为第一个参数 |
| `progress_default` | 非运行时进度默认值 |
| `cancel` | 取消按钮的 Input，触发时取消运行中的任务 |
| `interval` | 前端轮询进度间隔（毫秒），默认 1000 |

管理器类型：
- **DiskcacheManager**：本地开发，使用 diskcache 库在独立进程中运行
- **CeleryManager**：生产环境，使用 Celery worker + Redis/RabbitMQ 消息队列

## WebSocket 回调

Dash 4.x 支持 WebSocket 长连接回调（`websocket=True`），适用于实时数据推送场景。后端通过 `DashWebsocketCallback`（backends/ws.py）管理 WebSocket 连接。

## API 端点回调

回调可以通过 `api_endpoint` 参数暴露为独立的 HTTP API：

```python
@app.callback(
    Output("result", "children"),
    Input("x", "value"),
    api_endpoint="/api/calculate",
)
def calculate(x):
    return str(eval(x))
```

这使得回调可以被外部系统直接调用，不仅限于 Dash 前端。

## on_error 错误处理

可以为单个回调或整个 app 设置错误处理器：

```python
# app 级别
app = Dash(__name__, on_error=lambda e: str(e))

# 回调级别
@app.callback(
    Output("out", "children"),
    Input("in", "value"),
    on_error=lambda e: f"错误: {e}",
)
def update(value):
    return risky_operation(value)
```

错误处理器接收异常对象，可以通过 `callback_context` 访问原始回调的输入/状态/输出信息。

## 相关概念

- [Dash简介](00-introduction.md)
- [应用架构](01-app-architecture.md)
- [组件系统](03-component-system.md)
- [Dash应用初始化源码分析](../references/dash-app-init.md)
- [第一个Dash应用](../examples/first-dash-app.md)
