---
type: concept
title: 渲染与 IO
description: 详解 plotly.io 渲染器框架（notebook/browser/svg/png 等）、offline 模式、to_json/to_html/fig.show() 流程、默认模板机制与静态图片导出
tags:
  - plotly
  - io
  - 渲染
  - renderers
  - 模板
  - 导出
  - offline
generated:
  by: reference_agent/trae-glm
  at: 2026-08-22T15:00:00Z
verified:
  by: "process:seven-concepts-v"
  at: 2026-08-22T15:30:00Z
status: stable
stale_after: 2027-12-31
sources:
  - io/__init__.py
  - io/_renderers.py (RenderersConfig, show)
  - io/_base_renderers.py (各种 Renderer 类)
  - io/_json.py (to_json/from_json)
  - io/_html.py (to_html)
  - io/_templates.py (templates)
  - io/_kaleido.py (to_image/write_image)
---

# 渲染与 IO

Plotly.py 通过 `plotly.io` 模块（通常缩写为 `pio`）统一管理图表的渲染、序列化、导出和模板系统。理解 IO 模块是在不同环境中正确显示和保存 Plotly 图表的关键。

## io 模块结构

[plotly/io/](file:///d:/spaces/SpecWeave/external/libs/python/plotly.py/plotly/io/) 目录包含以下核心文件：

| 文件 | 功能 |
|------|------|
| `__init__.py` | 模块入口，惰性重导出所有公共 API |
| `_renderers.py` | 渲染器框架核心：`RenderersConfig`、`show()` 函数 |
| `_base_renderers.py` | 所有渲染器类定义（BrowserRenderer、NotebookRenderer、PngRenderer 等） |
| `_json.py` | JSON 序列化/反序列化：`to_json()`、`from_json()`、`read_json()`、`write_json()` |
| `_html.py` | HTML 输出：`to_html()`、`write_html()` |
| `_templates.py` | 模板系统：`templates` 对象、`to_templated()` |
| `_kaleido.py` | Kaleido 静态图片导出：`to_image()`、`write_image()`、`write_images()` |
| `_orca.py` / `orca.py` | Orca 静态导出（已被 Kaleido 取代，保留兼容） |
| `_defaults.py` | 默认配置 |

## 渲染器框架（Renderers）

渲染器决定了调用 `fig.show()` 时图表如何被展示。Plotly.py 支持多种渲染器，可根据运行环境自动选择或手动指定。

### RenderersConfig 配置对象

[_renderers.py](file:///d:/spaces/SpecWeave/external/libs/python/plotly.py/plotly/io/_renderers.py#L65) 中的 `RenderersConfig` 类是一个单例对象 `plotly.io.renderers`，管理所有可用渲染器：

```python
import plotly.io as pio

# 查看当前默认渲染器
print(pio.renderers.default)  # 自动检测环境，如 "plotly_mimetype+notebook"

# 查看所有可用渲染器
print(list(pio.renderers))

# 设置默认渲染器
pio.renderers.default = "browser"       # 在浏览器中打开
pio.renderers.default = "notebook"      # Jupyter Notebook
pio.renderers.default = "svg"           # 静态 SVG
pio.renderers.default = "png"           # 静态 PNG（需要 kaleido）
pio.renderers.default = None            # 不自动渲染
```

可以组合多个渲染器（用 `+` 连接）：
```python
pio.renderers.default = "notebook+browser"  # 同时在 notebook 和浏览器显示
```

### 内置渲染器类型

[_base_renderers.py](file:///d:/spaces/SpecWeave/external/libs/python/plotly.py/plotly/io/_base_renderers.py) 定义了以下渲染器类：

**交互式渲染器（基于 MIME type）：**

| 渲染器名 | 类 | 环境 | 说明 |
|----------|----|------|------|
| `plotly_mimetype` | `PlotlyRenderer` | Jupyter Lab/Notebook | 使用 Plotly MIME type 渲染（推荐） |
| `notebook` | `NotebookRenderer` | Classic Jupyter Notebook | 使用 notebook 专用初始化 |
| `jupyterlab` | - | Jupyter Lab | plotly_mimetype 的别名 |
| `colab` | `ColabRenderer` | Google Colab | Colab 专用渲染 |
| `kaggle` | `KaggleRenderer` | Kaggle Kernels | Kaggle 专用渲染 |
| `azure` | `AzureRenderer` | Azure Notebooks | Azure 专用渲染 |
| `cocalc` | `CoCalcRenderer` | CoCalc | CoCalc 平台 |
| `databricks` | `DatabricksRenderer` | Databricks | Databricks 平台 |

**静态图片渲染器（MimetypeRenderer 子类）：**

| 渲染器名 | 类 | 输出格式 |
|----------|----|----------|
| `png` | `PngRenderer` | PNG 位图 |
| `jpeg` / `jpg` | `JpegRenderer` | JPEG 位图 |
| `svg` | `SvgRenderer` | SVG 矢量图 |
| `pdf` | `PdfRenderer` | PDF 文档 |
| `json` | `JsonRenderer` | JSON 数据 |

静态渲染器通过 Kaleido 将 Figure 渲染为图片，需要安装 kaleido 包。

**外部渲染器（ExternalRenderer 子类）：**

| 渲染器名 | 类 | 说明 |
|----------|----|------|
| `browser` | `BrowserRenderer` | 生成临时 HTML 文件并在默认浏览器中打开 |
| `iframe` | `IFrameRenderer` | 生成 iframe 嵌入的 HTML |
| `firefox` / `chrome` / `chromium` | - | 指定浏览器打开（需要配置） |

**其他：**

| 渲染器名 | 说明 |
|----------|------|
| `sphinx_gallery` | Sphinx-Gallery 集成 |
| `notebook_connected` | 使用 CDN plotly.js（体积更小） |

### fig.show() 流程

调用 `fig.show()` 时的执行路径：

1. [BaseFigure.show()](file:///d:/spaces/SpecWeave/external/libs/python/plotly.py/plotly/basedatatypes.py#L3386) 委托给 `pio.show(self, *args, **kwargs)`
2. `_renderers.show()` 获取默认渲染器（或参数指定的 renderer）
3. 渲染器对象调用自身的 `render(fig)` 方法
4. 交互式渲染器（MimetypeRenderer）：将 Figure 转换为 MIME bundle，通过 IPython display 机制展示
5. 外部渲染器（ExternalRenderer）：生成 HTML/图片文件，调用系统命令打开
6. 静态渲染器：调用 Kaleido 将 Figure 转为图片 MIME data

```python
# 指定渲染器（临时覆盖默认）
fig.show(renderer="browser")
fig.show(renderer="svg")
fig.show(renderer="png", width=800, height=600, scale=2)

# 传递 config 参数
fig.show(config={"displayModeBar": False, "responsive": True})
```

## Offline 模式

Plotly.py 的所有渲染都是 offline 的——图表在本地生成和渲染，不需要连接 Plotly 云服务器（Plotly Chart Studio）。

`plotly.offline` 模块提供早期版本的 API（`iplot()`、`plot()`），这些函数现在只是 `pio.show()` 和 `pio.write_html()` 的兼容封装。推荐直接使用 `fig.show()`。

## JSON 序列化

### to_json()

将 Figure 序列化为 JSON 字符串：

```python
import plotly.io as pio

# 简洁输出
json_str = pio.to_json(fig)

# 格式化输出
json_str = pio.to_json(fig, pretty=True)

# 保留 UID
json_str = pio.to_json(fig, remove_uids=False)

# 使用 orjson 引擎（更快，需要安装 orjson）
json_str = pio.to_json(fig, engine="orjson")
```

内部调用 `fig.to_plotly_json()` 获取纯 dict，然后通过 JSON 编码器处理。编码器特殊处理：
- numpy 数组 → Python list
- numpy 标量 → Python 标量
- datetime 对象 → ISO 格式字符串
- BasePlotlyType 对象 → to_plotly_json() 递归
- `Undefined` 哨兵值 → 不输出

### from_json() / read_json() / write_json()

```python
# 从 JSON 字符串构造 Figure
fig = pio.from_json(json_str)

# 从 JSON 文件读取
fig = pio.read_json("figure.json")

# 写入 JSON 文件
pio.write_json(fig, "figure.json", pretty=True)
```

Figure 对象也有便捷方法：
```python
json_str = fig.to_json(pretty=True)
fig.write_json("figure.json")
```

## HTML 输出

### to_html()

生成包含 plotly.js 的 HTML 字符串：

```python
# 自包含 HTML（inline plotly.js，文件较大但完全离线可用）
html_str = pio.to_html(fig, include_plotlyjs=True, full_html=True)

# 使用 CDN（文件小，需要网络）
html_str = pio.to_html(fig, include_plotlyjs="cdn")

# 不包含 plotly.js（外部引用）
html_str = pio.to_html(fig, include_plotlyjs=False)

# 仅 div 片段（可嵌入已有页面）
div_str = pio.to_html(fig, include_plotlyjs="cdn", full_html=False)

# 自定义 div ID
html_str = pio.to_html(fig, div_id="my-chart", auto_open=False)
```

`include_plotlyjs` 参数：
- `True` 或 `"inline"`：内联 plotly.js 源码（~3MB）
- `"cdn"`：使用 CDN 链接
- `"directory"`：引用目录下的 plotly.min.js
- `False`：不包含（需外部加载）
- 路径字符串：直接使用指定路径

### write_html()

直接写入 HTML 文件：

```python
pio.write_html(fig, "chart.html", auto_open=True)  # 写入并自动打开
fig.write_html("chart.html")  # Figure 方法
```

## 静态图片导出

通过 Kaleido（基于 Chromium 的无头浏览器）将 Figure 导出为静态图片。

### to_image()

返回图片字节数据：

```python
# 返回 PNG 字节
img_bytes = pio.to_image(fig, format="png")  # 也可 fig.to_image()

# 导出 SVG
svg_bytes = pio.to_image(fig, format="svg")

# 指定分辨率
img_bytes = pio.to_image(fig, format="png", width=1200, height=800, scale=2)

# JPEG 质量
img_bytes = pio.to_image(fig, format="jpeg", engine="kaleido")
```

### write_image()

直接写入文件（格式由扩展名推断）：

```python
pio.write_image(fig, "chart.png")
pio.write_image(fig, "chart.svg")
pio.write_image(fig, "chart.pdf")
pio.write_image(fig, "chart.jpeg", scale=3)
fig.write_image("chart.png")  # Figure 方法
```

支持格式：`png`, `jpg`/`jpeg`, `webp`, `svg`, `pdf`, `eps`（部分需要额外 Poppler 依赖）。

### write_images()（批量导出）

对于含 frames 的动画 Figure，可以导出所有帧：

```python
pio.write_images(fig, "frame.png")  # → frame_0.png, frame_1.png, ...
```

### full_figure_for_development()

开发辅助函数，通过 Kaleido 计算 plotly.js 填充的所有默认属性值，返回"完整"Figure：

```python
full_fig = pio.full_figure_for_development(fig, warn=False)
# full_fig 包含所有默认属性，可用于学习 plotly.js 的默认行为
```

## 模板系统（Templates）

模板是预定义的布局和 Trace 样式集合，类似于"主题"。

### templates 对象

`pio.templates` 是一个模板配置对象（来自 `_templates.py`），管理所有内置和用户自定义模板：

```python
import plotly.io as pio

# 查看所有可用模板
print(list(pio.templates))
# ['ggplot2', 'seaborn', 'simple_white', 'plotly', 'plotly_white',
#  'plotly_dark', 'presentation', 'xgridoff', 'ygridoff',
#  'gridon', 'none']

# 使用模板
fig.update_layout(template="plotly_dark")
fig.update_layout(template="ggplot2")

# 设置全局默认模板
pio.templates.default = "plotly_white"
```

### 默认模板机制

包初始化时设置默认模板为 `"plotly"`：

```python
# plotly/__init__.py L61-63
from plotly.io import templates
templates._default = "plotly"
```

模板通过 `to_templated()` 方法将模板的 layout 和 data 属性合并到 Figure 中。合并遵循"用户属性优先"原则——用户显式设置的属性不会被模板覆盖。

### 内置模板

| 模板名 | 风格 |
|--------|------|
| `plotly` | 默认，Plotly 品牌配色 |
| `plotly_white` | 白色背景，浅灰色网格 |
| `plotly_dark` | 深色背景 |
| `ggplot2` | R ggplot2 风格 |
| `seaborn` | Python seaborn 风格 |
| `simple_white` | 极简白色背景 |
| `presentation` | 适合演讲的大字体 |
| `gridon` | 显示网格线 |
| `xgridoff` | 隐藏 X 轴网格 |
| `ygridoff` | 隐藏 Y 轴网格 |
| `none` | 无模板 |

### 自定义模板

```python
# 创建自定义模板
from plotly.graph_objects import Layout

my_template = pio.templates["plotly_white"].update(
    layout=Layout(
        font=dict(family="Arial", size=14),
        title_font=dict(size=20),
        colorway=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
    )
)
pio.templates["my_theme"] = my_template

fig.update_layout(template="my_theme")
```

## JSON 配置（config 参数）

渲染时可通过 `config` 参数传递 plotly.js 配置：

```python
fig.show(config={
    "displayModeBar": True,           # 显示模式栏
    "displaylogo": False,             # 隐藏 Plotly logo
    "modeBarButtonsToRemove": ["sendDataToCloud", "autoScale2d"],
    "responsive": True,               # 响应式
    "editable": True,                 # 可编辑标题/标注
    "toImageButtonOptions": {
        "format": "png",
        "filename": "chart",
        "height": 800,
        "width": 1200,
        "scale": 2
    }
})
```

## 相关概念

- [Figure 数据模型](01-figure-model.md)
- [Plotly.py 简介](00-introduction.md)
- [Plotly Express](02-plotly-express.md)
- [图对象模型](../references/graph-obj-model.md)
- [交互式图表示例](../examples/interactive-charts.md)
