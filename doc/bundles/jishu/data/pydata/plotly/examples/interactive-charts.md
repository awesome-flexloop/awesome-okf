---
type: example
title: Plotly 基础交互式图表
description: 包含散点图、折线图、柱状图、饼图、热力图、3D 表面图、子图的完整可运行代码示例
tags:
  - plotly
  - 示例
  - 散点图
  - 折线图
  - 柱状图
  - 饼图
  - 热力图
  - 3d
  - 子图
generated:
  by: reference_agent/trae-glm
  at: 2026-08-22T15:00:00Z
verified:
  by: "process:seven-concepts-v"
  at: 2026-08-22T15:30:00Z
status: stable
stale_after: 2027-12-31
sources:
  - graph_objects/_scatter.py, _bar.py, _pie.py, _heatmap.py, _surface.py
  - _subplots.py (make_subplots)
  - express/_chart_types.py
---

# Plotly 基础交互式图表

本文提供 Plotly.py 常用图表类型的完整可运行代码示例。所有示例均使用 `plotly.graph_objects` 低级 API 构建（以便理解底层结构），同时在适当处给出 `plotly.express` 高级 API 的等价写法。

## 前置条件

```python
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np

# 可选：设置默认渲染器（根据环境调整）
# pio.renderers.default = "browser"  # 在浏览器中打开
# pio.renderers.default = "notebook"  # Jupyter Notebook
```

---

## 1. 散点图（Scatter Plot）

```python
import plotly.graph_objects as go
import numpy as np

# 生成随机数据
np.random.seed(42)
x = np.random.randn(100)
y = 2 * x + np.random.randn(100) * 0.5

# 使用 graph_objects 创建散点图
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=x, y=y,
    mode='markers',              # 散点模式（'lines', 'markers', 'lines+markers', 'text'）
    marker=dict(
        size=8,                  # 点大小
        color=y,                 # 按 y 值着色
        colorscale='Viridis',    # 颜色比例尺
        showscale=True,          # 显示颜色条
        opacity=0.7,             # 透明度
        line=dict(width=1, color='white')  # 点边框
    ),
    name='数据点',
    hovertemplate='x: %{x:.2f}<br>y: %{y:.2f}<extra></extra>'  # 自定义悬停提示
))

# 添加趋势线
z = np.polyfit(x, y, 1)
p = np.poly1d(z)
x_line = np.linspace(x.min(), x.max(), 100)

fig.add_trace(go.Scatter(
    x=x_line, y=p(x_line),
    mode='lines',
    line=dict(color='red', width=2, dash='dash'),
    name='趋势线'
))

fig.update_layout(
    title='散点图示例',
    xaxis_title='X 值',
    yaxis_title='Y 值',
    template='plotly_white',
    showlegend=True,
    width=700, height=500
)

fig.show()
```

**Plotly Express 等价写法：**
```python
import plotly.express as px
import pandas as pd

df = pd.DataFrame({'x': x, 'y': y})
fig = px.scatter(df, x='x', y='y', trendline='ols',
                 title='散点图示例 (Express)',
                 template='plotly_white')
fig.show()
```

---

## 2. 折线图（Line Chart）

```python
import plotly.graph_objects as go
import numpy as np

# 生成时间序列数据
t = np.linspace(0, 4 * np.pi, 200)
y1 = np.sin(t)
y2 = np.cos(t)
y3 = np.sin(t) * np.cos(t)

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=t, y=y1,
    mode='lines',
    name='sin(t)',
    line=dict(color='royalblue', width=2),
    hovertemplate='t=%{x:.2f}<br>sin(t)=%{y:.3f}<extra></extra>'
))

fig.add_trace(go.Scatter(
    x=t, y=y2,
    mode='lines',
    name='cos(t)',
    line=dict(color='firebrick', width=2, dash='dash'),
    hovertemplate='t=%{x:.2f}<br>cos(t)=%{y:.3f}<extra></extra>'
))

fig.add_trace(go.Scatter(
    x=t, y=y3,
    mode='lines',
    name='sin(t)·cos(t)',
    line=dict(color='green', width=2, dash='dot'),
    fill='tozeroy',             # 填充到零轴
    fillcolor='rgba(0,255,0,0.1)',  # 填充颜色（半透明）
    hovertemplate='t=%{x:.2f}<br>乘积=%{y:.3f}<extra></extra>'
))

fig.update_layout(
    title='三角函数折线图',
    xaxis_title='t',
    yaxis_title='值',
    hovermode='x unified',       # 悬停显示所有曲线在该x位置的值
    template='plotly_white',
    width=700, height=450,
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
)

fig.show()
```

---

## 3. 柱状图（Bar Chart）

```python
import plotly.graph_objects as go

# 数据
categories = ['产品A', '产品B', '产品C', '产品D', '产品E']
values_2024 = [20, 14, 23, 25, 22]
values_2025 = [25, 18, 20, 28, 26]

fig = go.Figure()

fig.add_trace(go.Bar(
    x=categories,
    y=values_2024,
    name='2024年',
    marker_color='royalblue',
    text=values_2024,            # 显示数值标签
    textposition='outside',      # 标签位置
    hovertemplate='%{x}<br>销售额: %{y}万元<extra>2024年</extra>'
))

fig.add_trace(go.Bar(
    x=categories,
    y=values_2025,
    name='2025年',
    marker_color='firebrick',
    text=values_2025,
    textposition='outside',
    hovertemplate='%{x}<br>销售额: %{y}万元<extra>2025年</extra>'
))

fig.update_layout(
    title='年度销售对比',
    xaxis_title='产品',
    yaxis_title='销售额（万元）',
    barmode='group',              # 'group' 分组 / 'stack' 堆叠 / 'overlay' 叠加 / 'relative'
    bargap=0.15,                 # 组间间距
    bargroupgap=0.1,             # 组内间距
    template='plotly_white',
    width=700, height=500,
    yaxis=dict(gridcolor='lightgray')
)

fig.show()
```

**水平柱状图：**
```python
fig = go.Figure(go.Bar(
    x=values_2024,
    y=categories,
    orientation='h',             # 水平方向
    marker_color='teal',
    text=values_2024,
    textposition='outside'
))
fig.update_layout(title='水平柱状图', template='plotly_white')
fig.show()
```

---

## 4. 饼图（Pie Chart）

```python
import plotly.graph_objects as go

labels = ['Chrome', 'Safari', 'Firefox', 'Edge', '其他']
values = [65, 18, 8, 5, 4]
colors = ['#4285F4', '#EA4335', '#FBBC04', '#34A853', '#9AA0A6']

fig = go.Figure()

fig.add_trace(go.Pie(
    labels=labels,
    values=values,
    hole=0.3,                    # 中心挖孔 → 环形图（0为普通饼图）
    marker=dict(colors=colors, line=dict(color='white', width=2)),
    textinfo='label+percent',    # 显示标签和百分比
    textfont=dict(size=12),
    hovertemplate='%{label}<br>占比: %{percent}<br>份额: %{value}%<extra></extra>',
    pull=[0.05, 0, 0, 0, 0],    # 拉出某一片
    rotation=90,                 # 起始角度
    direction='clockwise',       # 方向
))

fig.update_layout(
    title='浏览器市场份额',
    template='plotly_white',
    width=600, height=500,
    showlegend=True,
    legend=dict(orientation='v', x=1.02, y=0.5)
)

fig.show()
```

---

## 5. 热力图（Heatmap）

```python
import plotly.graph_objects as go
import numpy as np

# 生成相关矩阵数据
np.random.seed(42)
n_vars = 8
data = np.random.randn(100, n_vars)
corr_matrix = np.corrcoef(data.T)

labels = [f'变量{i+1}' for i in range(n_vars)]

fig = go.Figure()

fig.add_trace(go.Heatmap(
    z=corr_matrix,
    x=labels,
    y=labels,
    colorscale='RdBu_r',         # 红蓝发散色标（_r 反转）
    zmin=-1, zmax=1,             # 值范围
    showscale=True,
    colorbar=dict(
        title='相关系数',
        titleside='right',
        thickness=15,
        len=0.8
    ),
    text=np.round(corr_matrix, 2),  # 显示数值
    texttemplate='%{text:.2f}',
    textfont=dict(size=10),
    hovertemplate='%{y} vs %{x}<br>相关系数: %{z:.3f}<extra></extra>',
    hoverongaps=False
))

fig.update_layout(
    title='变量相关矩阵热力图',
    width=600, height=550,
    template='plotly_white',
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=False, autorange='reversed')  # y轴翻转（左上为原点）
)

fig.show()
```

---

## 6. 3D 表面图（3D Surface Plot）

```python
import plotly.graph_objects as go
import numpy as np

# 生成曲面数据: z = sin(sqrt(x²+y²)) / (sqrt(x²+y²)) (墨西哥帽)
x = np.linspace(-8, 8, 100)
y = np.linspace(-8, 8, 100)
X, Y = np.meshgrid(x, y)
R = np.sqrt(X**2 + Y**2)
Z = np.sin(R) / (R + 1e-10)  # 避免除以零

fig = go.Figure()

fig.add_trace(go.Surface(
    x=X, y=Y, z=Z,
    colorscale='Viridis',
    contours={
        "x": {"show": True, "color": "gray", "start": -8, "end": 8, "size": 2},
        "y": {"show": True, "color": "gray", "start": -8, "end": 8, "size": 2},
        "z": {"show": True, "color": "white", "start": -1, "end": 1, "size": 0.2}
    },
    lighting=dict(
        ambient=0.6,
        diffuse=0.8,
        specular=0.3,
        roughness=0.5
    ),
    hovertemplate='x=%{x:.2f}<br>y=%{y:.2f}<br>z=%{z:.3f}<extra></extra>'
))

fig.update_layout(
    title='3D 表面图: sinc(r) = sin(r)/r',
    width=700, height=600,
    template='plotly_white',
    scene=dict(
        xaxis_title='X',
        yaxis_title='Y',
        zaxis_title='Z',
        camera=dict(
            eye=dict(x=1.5, y=1.5, z=1.0)  # 相机位置
        )
    ),
    margin=dict(l=0, r=0, t=50, b=0)
)

fig.show()
```

---

## 7. 子图（Subplots）

```python
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np

# 生成数据
np.random.seed(42)
x = np.linspace(0, 10, 100)
y_scatter = np.random.randn(100).cumsum()
y_line = np.sin(x)
categories = ['A', 'B', 'C', 'D']
values = [23, 45, 56, 78]
z_heatmap = np.random.randn(6, 6)

# 创建 2x2 子图
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=('散点趋势', '正弦曲线', '柱状图', '热力图'),
    specs=[
        [{"type": "xy"}, {"type": "xy"}],
        [{"type": "xy"}, {"type": "heatmap"}]  # 第四个子图为热力图类型
    ],
    horizontal_spacing=0.12,
    vertical_spacing=0.15,
    shared_xaxes=False,
    shared_yaxes=False
)

# (1,1) 散点趋势
fig.add_trace(go.Scatter(
    x=x, y=y_scatter,
    mode='markers+lines',
    marker=dict(size=5, color='royalblue'),
    line=dict(width=1, color='royalblue'),
    name='随机游走'
), row=1, col=1)

# (1,2) 正弦曲线
fig.add_trace(go.Scatter(
    x=x, y=y_line,
    mode='lines',
    line=dict(color='firebrick', width=2),
    name='sin(x)'
), row=1, col=2)

# (2,1) 柱状图
fig.add_trace(go.Bar(
    x=categories, y=values,
    marker_color='teal',
    name='数值',
    showlegend=False
), row=2, col=1)

# (2,2) 热力图
fig.add_trace(go.Heatmap(
    z=z_heatmap,
    colorscale='Viridis',
    showscale=False,
    name='热力'
), row=2, col=2)

# 更新全局布局
fig.update_layout(
    title_text='2x2 子图示例',
    template='plotly_white',
    width=800, height=650,
    showlegend=True,
    legend=dict(orientation='h', yanchor='bottom', y=1.02)
)

# 更新特定子图的坐标轴
fig.update_xaxes(title_text='X', row=2, col=1)
fig.update_yaxes(title_text='累计值', row=1, col=1)
fig.update_yaxes(title_text='sin(x)', row=1, col=2)

fig.show()
```

---

## 8. 综合示例：多 Trace + 自定义布局

```python
import plotly.graph_objects as go
import numpy as np

np.random.seed(123)
x = np.linspace(0, 10, 50)
y1 = np.sin(x) + np.random.normal(0, 0.1, 50)
y2 = np.cos(x) + np.random.normal(0, 0.1, 50)
y3 = 0.5 * x + np.random.normal(0, 0.5, 50)

fig = go.Figure()

# 散点
fig.add_trace(go.Scatter(
    x=x, y=y1,
    mode='markers',
    name='sin(x) + 噪声',
    marker=dict(size=8, color='blue', opacity=0.6)
))

# 折线
fig.add_trace(go.Scatter(
    x=x, y=y2,
    mode='lines',
    name='cos(x) + 噪声',
    line=dict(color='red', width=2)
))

# 带填充的折线
fig.add_trace(go.Scatter(
    x=x, y=y3,
    mode='lines+markers',
    name='0.5x + 噪声',
    line=dict(color='green', width=2),
    marker=dict(size=5)
))

# 添加参考线
fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
fig.add_vline(x=5, line_dash="dot", line_color="gray", opacity=0.5)

# 添加标注
fig.add_annotation(
    x=2, y=np.sin(2),
    text="峰值",
    showarrow=True,
    arrowhead=1,
    ax=30, ay=-30
)

fig.update_layout(
    title=dict(
        text='<b>综合图表</b>: 多种 Trace + 自定义布局',
        font=dict(size=18)
    ),
    xaxis=dict(
        title='X 轴',
        showgrid=True,
        gridcolor='lightgray',
        zeroline=True,
        zerolinecolor='gray'
    ),
    yaxis=dict(
        title='Y 轴',
        showgrid=True,
        gridcolor='lightgray'
    ),
    template='plotly_white',
    width=800, height=500,
    hovermode='closest',
    margin=dict(l=60, r=30, t=80, b=60)
)

fig.show()
```

---

## 导出图表

```python
# 导出为 HTML（可在浏览器中交互查看）
fig.write_html("chart.html")

# 导出为静态图片（需要 kaleido: pip install kaleido）
# fig.write_image("chart.png", scale=2)  # 2x 分辨率 PNG
# fig.write_image("chart.svg")
# fig.write_image("chart.pdf")

# 导出 JSON（可重新加载）
fig.write_json("chart.json")
# fig2 = pio.read_json("chart.json")
```

## 相关概念

- [Figure 数据模型](../concepts/01-figure-model.md)
- [Plotly Express](../concepts/02-plotly-express.md)
- [渲染与 IO](../concepts/03-rendering-io.md)
- [图对象模型](../references/graph-obj-model.md)
