---
okf_version: "0.2"
type: example
title: Dash第一个应用
description: 从Hello World到交互式散点图回调、多页面应用、dcc.Graph+Plotly图表、输入框与下拉框联动的完整可运行代码示例
tags: [Dash, 入门, Hello World, 回调, Plotly, dcc.Graph, 多页面, 交互]
generated:
  by: reference_agent/trae-glm
  at: 2026-08-22T15:00:00Z
verified:
  by: "process:seven-concepts-v"
  at: 2026-08-22T15:30:00Z
status: stable
stale_after: 2027-12-31
sources:
  - id: dash-class
    resource: external/libs/python/dash/dash/dash.py
    title: Dash主类API
  - id: dash-callback
    resource: external/libs/python/dash/dash/_callback.py
    title: 回调装饰器
  - id: dash-dependencies
    resource: external/libs/python/dash/dash/dependencies.py
    title: Input/Output/State
  - id: dash-pages
    resource: external/libs/python/dash/dash/_pages.py
    title: 多页面路由
---

# Dash第一个应用

本文提供从最简单的 Hello World 到完整交互式应用的渐进式代码示例，所有代码均可直接运行。

## 前置条件

```bash
pip install dash==4.4.1       # 安装Dash（自动包含Flask、plotly等依赖）
pip install pandas            # 部分示例需要pandas
```

运行方式：将代码保存为 `app.py`，执行 `python app.py`，然后在浏览器中打开 `http://127.0.0.1:8050`。

## 示例1：Hello World（最小应用）

```python
from dash import Dash, html

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Hello, Dash!"),
    html.P("这是我的第一个Dash应用。"),
])

if __name__ == "__main__":
    app.run(debug=True)
```

**代码解析**：
- `Dash(__name__)`：创建应用实例，`__name__` 帮助 Dash 查找静态资源
- `app.layout`：设置应用的 UI 布局，是一棵组件树
- `html.Div`、`html.H1`、`html.P`：HTML 组件，对应 `<div>`、`<h1>`、`<p>` 标签
- `app.run(debug=True)`：启动开发服务器，debug 模式支持热重载

## 示例2：交互式散点图回调

这个示例展示 Dash 的核心——响应式回调：选择下拉框中的选项，图表自动更新。

```python
from dash import Dash, html, dcc, Input, Output, callback
import plotly.express as px
import pandas as pd

app = Dash(__name__)

# 准备示例数据
df = pd.DataFrame({
    "水果": ["苹果", "香蕉", "橙子", "葡萄", "西瓜"] * 3,
    "销量": [4, 1, 2, 3, 5, 6, 4, 3, 5, 7, 3, 2, 5, 4, 6],
    "月份": ["1月"]*5 + ["2月"]*5 + ["3月"]*5,
})

app.layout = html.Div([
    html.H1("水果销量分析"),

    html.Label("选择月份："),
    dcc.Dropdown(
        id="month-dropdown",
        options=[{"label": m, "value": m} for m in df["月份"].unique()],
        value="1月",
        clearable=False,
    ),

    dcc.Graph(id="sales-graph"),
])

@callback(
    Output("sales-graph", "figure"),
    Input("month-dropdown", "value"),
)
def update_graph(selected_month):
    """当下拉框值变化时，更新散点图。"""
    filtered = df[df["月份"] == selected_month]
    fig = px.bar(
        filtered,
        x="水果",
        y="销量",
        title=f"{selected_month}水果销量",
        color="水果",
    )
    return fig

if __name__ == "__main__":
    app.run(debug=True)
```

**代码解析**：
- `dcc.Dropdown`：下拉框组件，`id` 为回调绑定标识
- `dcc.Graph`：Plotly 图表容器，`figure` 属性接收 plotly.graph_objects.Figure 对象
- `@callback(Output(...), Input(...))`：声明输出和输入依赖
- 当 `month-dropdown.value` 变化时，dash-renderer 自动调用 `update_graph` 函数
- 函数返回值自动更新 `sales-graph.figure`
- 使用 `plotly.express` 快速创建图表

## 示例3：输入框+下拉框联动（多输入+State）

此示例演示多个输入组件联动，以及 State（读取值但不触发回调）的用法。

```python
from dash import Dash, html, dcc, Input, Output, State, callback

app = Dash(__name__)

app.layout = html.Div([
    html.H1("个人信息卡片生成器"),

    html.Div([
        html.Label("姓名："),
        dcc.Input(id="name-input", type="text", placeholder="输入你的名字"),
    ], style={"margin": "10px 0"}),

    html.Div([
        html.Label("选择颜色："),
        dcc.Dropdown(
            id="color-dropdown",
            options=[
                {"label": "红色", "value": "#ff4444"},
                {"label": "蓝色", "value": "#4444ff"},
                {"label": "绿色", "value": "#44aa44"},
                {"label": "紫色", "value": "#aa44aa"},
            ],
            value="#4444ff",
        ),
    ], style={"margin": "10px 0"}),

    html.Div([
        html.Label("字体大小："),
        dcc.Slider(id="size-slider", min=12, max=48, step=2, value=24,
                   marks={12: "12px", 24: "24px", 36: "36px", 48: "48px"}),
    ], style={"margin": "10px 0"}),

    html.Button("生成卡片", id="generate-btn", n_clicks=0,
                style={"margin": "10px 0", "padding": "8px 16px"}),

    html.Hr(),
    html.Div(id="card-output"),
])

@callback(
    Output("card-output", "children"),
    Input("generate-btn", "n_clicks"),
    State("name-input", "value"),
    State("color-dropdown", "value"),
    State("size-slider", "value"),
    prevent_initial_call=True,
)
def generate_card(n_clicks, name, color, size):
    """点击按钮时，用State读取表单值（输入时不触发）。"""
    if not name:
        return html.P("请输入姓名！", style={"color": "red"})

    return html.Div([
        html.H3("你的卡片", style={"textAlign": "center"}),
        html.Div(
            f"你好，{name}！",
            style={
                "color": color,
                "fontSize": f"{size}px",
                "textAlign": "center",
                "padding": "20px",
                "border": f"3px solid {color}",
                "borderRadius": "10px",
                "margin": "20px auto",
                "width": "300px",
            },
        ),
    ])

if __name__ == "__main__":
    app.run(debug=True)
```

**代码解析**：
- `State`：读取组件当前值，但值变化时不触发回调（适合表单场景）
- `Input("generate-btn", "n_clicks")`：按钮点击次数作为触发器
- `prevent_initial_call=True`：页面加载时不执行回调（避免点击次数为0时生成空卡片）
- `style` 属性使用字典传递 CSS 样式（React 风格，camelCase 属性名如 `fontSize`、`textAlign`）
- 回调可以返回组件树（`html.Div(...)`），不只限于返回简单值

## 示例4：多输出回调

一个回调同时更新多个组件属性：

```python
from dash import Dash, html, dcc, Input, Output, callback
import plotly.express as px
import pandas as pd
import numpy as np

app = Dash(__name__)

app.layout = html.Div([
    html.H1("数据仪表盘"),

    html.Label("数据点数量："),
    dcc.Slider(id="n-slider", min=10, max=500, step=10, value=100,
               marks={10: "10", 100: "100", 250: "250", 500: "500"}),

    dcc.Graph(id="scatter-plot"),
    html.Div(id="stats-output"),
])

@callback(
    Output("scatter-plot", "figure"),
    Output("stats-output", "children"),
    Input("n-slider", "value"),
)
def update_dashboard(n):
    """一个回调同时更新图表和统计信息。"""
    np.random.seed(42)
    x = np.random.randn(n)
    y = 2 * x + np.random.randn(n) * 0.5

    fig = px.scatter(
        x=x, y=y,
        title=f"{n}个随机数据点",
        labels={"x": "X", "y": "Y"},
        trendline="ols",
    )

    stats = html.Div([
        html.H4("统计摘要"),
        html.P(f"数据点数: {n}"),
        html.P(f"X均值: {x.mean():.3f}, X标准差: {x.std():.3f}"),
        html.P(f"Y均值: {y.mean():.3f}, Y标准差: {y.std():.3f}"),
        html.P(f"相关系数: {np.corrcoef(x, y)[0,1]:.3f}"),
    ], style={"margin": "10px", "padding": "10px", "backgroundColor": "#f0f0f0"})

    return fig, stats  # 返回元组，顺序对应Output声明

if __name__ == "__main__":
    app.run(debug=True)
```

**代码解析**：
- 多个 `Output` 声明对应返回值的多个元素（元组顺序）
- 回调可以返回 plotly Figure、组件树、字符串等多种类型
- 使用 `plotly.express.scatter` 的 `trendline="ols"` 添加趋势线

## 示例5：多页面应用

使用 `use_pages=True` 和 `register_page` 创建多页面应用。

**项目结构**：
```
my_app/
├── app.py
└── pages/
    ├── home.py
    ├── about.py
    └── analysis.py
```

**app.py**（主文件）：
```python
from dash import Dash, html, dcc, page_registry, page_container

app = Dash(__name__, use_pages=True)

# 导航栏
nav = html.Nav([
    dcc.Link(page["name"], href=page["relative_path"],
             style={"marginRight": "20px", "textDecoration": "none"})
    for page in page_registry.values()
], style={"padding": "10px", "backgroundColor": "#333"})

app.layout = html.Div([
    nav,
    html.Hr(),
    page_container,  # 页面内容渲染位置
])

if __name__ == "__main__":
    app.run(debug=True)
```

**pages/home.py**（首页）：
```python
from dash import register_page, html

register_page(__name__, path="/", name="首页", title="我的应用 - 首页")

layout = html.Div([
    html.H2("欢迎来到首页"),
    html.P("这是一个多页面Dash应用。"),
    html.P("使用上方导航栏在页面间切换。"),
])
```

**pages/about.py**（关于页）：
```python
from dash import register_page, html

register_page(__name__, name="关于", title="关于我们")

layout = html.Div([
    html.H2("关于我们"),
    html.P("这是一个使用Dash构建的数据可视化应用。"),
    html.P("Dash版本: 4.4.1"),
])
```

**pages/analysis.py**（分析页，动态路径）：
```python
from dash import register_page, html, dcc, Input, Output, callback
import plotly.express as px
import pandas as pd

register_page(
    __name__,
    path_template="/analysis/<category>",
    name="数据分析",
    title="数据分析",
)

def layout(category=None):
    """动态布局函数，接收路径参数。"""
    categories = ["销售", "用户", "产品"]
    return html.Div([
        html.H2(f"数据分析 - {category or '总览'}"),
        dcc.Dropdown(
            id="cat-select",
            options=[{"label": c, "value": c} for c in categories],
            value=category or "销售",
        ),
        dcc.Graph(id="analysis-chart"),
    ])

@callback(
    Output("analysis-chart", "figure"),
    Input("cat-select", "value"),
)
def update_chart(cat):
    # 示例数据
    data = {"销售": [10, 20, 15], "用户": [50, 80, 60], "产品": [5, 8, 12]}
    fig = px.bar(
        x=["Q1", "Q2", "Q3"],
        y=data.get(cat, [0, 0, 0]),
        title=f"{cat}季度数据",
    )
    return fig
```

**代码解析**：
- `use_pages=True`：启用文件系统路由
- `register_page(__name__, path=..., name=...)`：注册页面元数据
- `page_container`：页面内容占位组件（内部包含 `dcc.Location` 和内容容器）
- `page_registry`：有序字典，包含所有已注册页面的元数据
- `dcc.Link`：客户端导航链接（不刷新页面）
- `path_template` 支持动态路径参数，layout 函数接收参数作为关键字参数
- `pages/` 目录下的 `.py` 文件自动导入，触发 `register_page` 调用

## 示例6：回调链与实时更新

多个回调串联，实现数据过滤→可视化→统计的流水线：

```python
from dash import Dash, html, dcc, Input, Output, callback
import plotly.express as px
import pandas as pd
import numpy as np

app = Dash(__name__)

np.random.seed(42)
df = pd.DataFrame({
    "category": np.random.choice(["A", "B", "C"], 200),
    "x": np.random.randn(200),
    "y": np.random.randn(200),
    "size": np.random.randint(10, 100, 200),
})

app.layout = html.Div([
    html.H1("回调链演示：过滤→图表→统计"),

    html.Label("选择类别："),
    dcc.Checklist(
        id="category-checklist",
        options=[{"label": c, "value": c} for c in ["A", "B", "C"]],
        value=["A", "B", "C"],
        inline=True,
    ),

    dcc.Interval(id="timer", interval=2000, n_intervals=0),  # 每2秒触发

    dcc.Graph(id="main-graph"),
    html.Div(id="info-panel"),
])

@callback(
    Output("main-graph", "figure"),
    Input("category-checklist", "value"),
    Input("timer", "n_intervals"),
)
def update_graph(categories, n):
    """第一个回调：根据选择和定时器更新图表。"""
    filtered = df[df["category"].isin(categories)]
    # 添加时间变化效果
    jitter = np.random.randn(len(filtered)) * 0.1

    fig = px.scatter(
        filtered,
        x="x", y=filtered["y"] + jitter,
        color="category", size="size",
        title=f"实时散点图 (刷新次数: {n})",
    )
    return fig

@callback(
    Output("info-panel", "children"),
    Input("main-graph", "figure"),  # 依赖图表更新（回调链）
)
def update_info(figure):
    """第二个回调：图表更新后，自动更新统计面板。"""
    if not figure:
        return html.P("等待数据...")

    traces = figure["data"]
    total_points = sum(len(t["x"]) for t in traces)
    categories = [t["name"] for t in traces]

    return html.Div([
        html.H4("当前图表状态"),
        html.P(f"显示类别: {', '.join(categories)}"),
        html.P(f"总数据点: {total_points}"),
    ], style={"marginTop": "10px", "padding": "10px", "borderLeft": "3px solid blue"})

if __name__ == "__main__":
    app.run(debug=True)
```

**代码解析**：
- `dcc.Interval`：定时器组件，按固定间隔触发 `n_intervals` 递增
- `dcc.Checklist`：多选框，value 为选中值的列表
- 回调链：`update_graph` 的 Output（`main-graph.figure`）是 `update_info` 的 Input——图表更新后自动触发统计更新
- dash-renderer 在前端构建依赖图，确保回调按正确顺序执行

## 运行提示

1. **开发模式**：`app.run(debug=True)` 启用热重载和调试工具栏
2. **指定端口**：`app.run(port=8051)` 更改默认端口
3. **外部访问**：`app.run(host="0.0.0.0")` 允许局域网访问
4. **生产部署**：不使用 `app.run()`，而是使用 Gunicorn/uWSGI（Flask后端）或 Uvicorn（FastAPI后端）：
   ```bash
   # Flask 后端
   gunicorn app:server
   # FastAPI 后端
   uvicorn app:server --host 0.0.0.0 --port 8050
   ```
   注意：生产环境使用 `app.server`（底层Flask/FastAPI实例）而非app本身。

## 相关概念

- [Dash简介](../concepts/00-introduction.md)
- [应用架构](../concepts/01-app-architecture.md)
- [回调系统](../concepts/02-callback-system.md)
- [组件系统](../concepts/03-component-system.md)
- [Dash应用初始化源码分析](../references/dash-app-init.md)
