---
type: Concept
title: 交互式控件与富显示（ipywidgets）
description: ipywidgets 交互控件架构、Widget 模型-视图分离、同步机制、自定义 Widget 开发、显示协议与富输出
tags: [jupyter, ipywidgets, widgets, interact, display, rich-output, mime, comm]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T11:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T11:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: jupyter-metasource
    resource: /references/jupyter-metasource.md
---

# 交互式控件与富显示（ipywidgets）

Jupyter 的核心体验之一是交互式控件和富媒体输出。这一能力由 [ipywidgets](https://ipywidgets.readthedocs.io) 包提供，它让 Notebook 不仅仅是静态文档，而是可以与用户实时交互的应用界面。

## ipywidgets 架构

ipywidgets 提供了在浏览器中渲染 GUI 控件（滑块、按钮、文本框、图表等）的能力，这些控件与 Kernel 中的 Python 对象双向同步。

### 模型-视图-同步架构

```mermaid
graph TB
    subgraph 浏览器前端
        V1["滑块视图<br/>(HTML/JS)"]
        V2["数值显示视图"]
        WManager["Widget Manager"]
    end
    
    subgraph Kernel (Python)
        M["Widget 模型<br/>(Python 对象)"]
        C["Comm 通道<br/>(WebSocket+ZMQ)"]
    end
    
    V1 <-->|状态同步| WManager
    V2 <-->|状态同步| WManager
    WManager <-->|JSON 消息| C
    C <-->|属性同步| M
    
    style M fill:#e8f5e9,stroke:#2e7d32
    style V1 fill:#e3f2fd,stroke:#1565c0
    style V2 fill:#e3f2fd,stroke:#1565c0
    style C fill:#fff3e0,stroke:#e65100
    style WManager fill:#f3e5f5,stroke:#6a1b9a
```

关键设计：

1. **模型在 Kernel 中**：Widget 的状态（如滑块的值 `value=42`）存储在 Python 对象中
2. **视图在浏览器中**：控件的 HTML/JavaScript 渲染在前端
3. **双向同步**：用户拖动滑块 → 新值同步到 Python → Python 中的回调执行；Python 修改 `.value` → 浏览器滑块自动移动
4. **多视图支持**：同一个模型可以有多个视图同时显示（例如滑块+数值显示框）
5. **同步通过 Comm 通道**：使用 Jupyter Protocol 的 Comm（通信）机制在前端和 Kernel 间传递状态变更

### Comm 通道

Comm 是 Jupyter Protocol 中的通用双向通信机制，用于在前端和 Kernel 之间传递自定义消息：

- 不是请求-响应模式，而是自由的双向消息传递
- 每个 Widget 有一个唯一的 Comm 通道
- 状态同步使用 JSON Patch（RFC 6902）格式，只传输变化的部分，效率高
- 同步协议基于 [jupyter-js-widgets](https://github.com/jupyter-widgets/ipywidgets/tree/master/packages/jupyter-js-widgets) 前端包

## 基础使用

### interact 装饰器

最简单的交互式控件创建方式是使用 `interact`：

```python
from ipywidgets import interact

@interact(x=(0, 100, 1))
def f(x=50):
    print(f"x = {x}, x² = {x**2}")
```

`interact` 自动根据参数类型生成对应的控件：

| Python 类型/格式 | 自动生成的控件 |
|----------------|-------------|
| `int` / `(min, max)` / `(min, max, step)` | IntSlider |
| `float` / `(min, max, step)` | FloatSlider |
| `bool` | Checkbox |
| `str` | Text（文本输入） |
| `['a', 'b', 'c']`（列表） | Dropdown（下拉选择） |
| `{'a': 1, 'b': 2}`（字典） | Dropdown（显示键，传递值） |

### 显式控件创建

更精细的控制需要显式创建控件对象：

```python
from ipywidgets import IntSlider, Button, Output, VBox, HBox
from IPython.display import display

slider = IntSlider(min=0, max=100, value=50, description='值:')
button = Button(description='点击')
output = Output()

def on_click(b):
    with output:
        output.clear_output()
        print(f"滑块值: {slider.value}")

button.on_click(on_click)
display(VBox([slider, button, output]))
```

### 常用控件

| 控件类 | 用途 |
|--------|------|
| `IntSlider` / `FloatSlider` | 数值滑块 |
| `IntRangeSlider` / `FloatRangeSlider` | 范围滑块 |
| `IntText` / `FloatText` / `BoundedIntText` | 数值输入框 |
| `ToggleButton` / `Checkbox` | 布尔开关 |
| `Dropdown` / `RadioButtons` / `Select` | 单选 |
| `SelectMultiple` | 多选 |
| `Text` / `Textarea` / `Password` | 文本输入 |
| `Button` | 按钮 |
| `HTML` / `HTMLMath` / `Markdown` | 富文本显示 |
| `Image` | 图片显示 |
| `Output` | 输出区域（捕获 stdout/display） |
| `Play` | 动画播放控件 |
| `DatePicker` / `ColorPicker` | 日期/颜色选择 |
| `FileUpload` | 文件上传 |
| `Tab` / `Accordion` | 标签页/手风琴折叠 |
| `VBox` / `HBox` / `GridBox` | 布局容器 |

## 富显示系统（Rich Display）

Jupyter 的显示系统允许 Python 对象以丰富的格式呈现，而不只是纯文本。

### display() 函数

```python
from IPython.display import display, HTML, Image, Markdown, Latex

# 显示 HTML
display(HTML("<b>加粗文本</b>"))

# 显示图片
display(Image("chart.png", width=400))

# 显示 Markdown
display(Markdown("# 标题\n\n**加粗** 和 *斜体*"))

# 显示 LaTeX 公式
display(Latex(r"$E = mc^2$"))
```

### MIME 类型映射

每个可显示对象实现 `_repr_*_()` 方法，对应不同的 MIME 类型：

| 方法 | MIME 类型 | 渲染器 |
|------|----------|--------|
| `_repr_html_()` | `text/html` | 浏览器 HTML 渲染 |
| `_repr_markdown_()` | `text/markdown` | Markdown 渲染 |
| `_repr_latex_()` | `text/latex` | MathJax/KaTeX |
| `_repr_svg_()` | `image/svg+xml` | SVG 渲染 |
| `_repr_png_()` | `image/png` | PNG 图片 |
| `_repr_jpeg_()` | `image/jpeg` | JPEG 图片 |
| `_repr_json_()` | `application/json` | JSON 查看器 |
| `_repr_javascript_()` | `application/javascript` | JavaScript 执行 |
| `_repr_mimebundle_()` | 多种 MIME | 自定义 mimebundle |
| `__repr__()` | `text/plain` | 纯文本（回退） |

前端选择它能处理的"最佳"MIME 类型渲染。浏览器优先 HTML 和图片，终端回退到 text/plain。

### 自定义 _repr_html_

```python
class DataFrame:
    def _repr_html_(self):
        rows = "".join(
            f"<tr><td>{r[0]}</td><td>{r[1]}</td></tr>"
            for r in self.rows
        )
        return f"<table>{rows}</table>"
```

这正是 pandas DataFrame 在 Notebook 中显示为漂亮表格的原理。

### display_data 消息

当你调用 `display(obj)` 时，IPython 内核会收集 obj 所有 `_repr_*_()` 方法的输出，打包成 `display_data` 消息通过 IOPub 通道发送：

```json
{
  "output_type": "display_data",
  "data": {
    "text/plain": "<__main__.MyObject at 0x...>",
    "text/html": "<b>富文本显示</b>",
    "image/png": "base64编码..."
  },
  "metadata": {}
}
```

前端收到后，选择最适合当前环境的 MIME 类型渲染。

### clear_output 和更新输出

```python
from IPython.display import clear_output
import time

for i in range(100):
    clear_output(wait=True)  # wait=True 避免闪烁
    print(f"进度: {i}%")
    time.sleep(0.1)
```

`clear_output(wait=True)` 等待新内容就绪再清除，实现平滑更新。`Output` Widget 提供了更灵活的输出区域管理。

## 第三方 Widget 生态

ipywidgets 是一个可扩展框架，社区开发了大量第三方 Widget 包：

| 包名 | 用途 |
|------|------|
| [ipyleaflet](https://ipyleaflet.readthedocs.io) | 交互式地图 |
| [ipympl](https://matplotlib.org/ipympl/) | Matplotlib 交互式图表 |
| [plotly](https://plotly.com/python/) | Plotly 交互式图表（内置 Jupyter 支持） |
| [bqplot](https://bqplot.github.io/bqplot/) | 基于 Grammar of Graphics 的交互式图表 |
| [ipyvolume](https://ipyvolume.readthedocs.io) | 3D 可视化 |
| [ipydatagrid](https://github.com/bloomberg/ipydatagrid) | 高性能数据网格 |
| [ipycanvas](https://ipycanvas.readthedocs.io) | Canvas 绘图 |
| [ipytree](https://github.com/QuantStack/ipytree) | 树形控件 |
| [ipycytoscape](https://github.com/cytoscape/ipycytoscape) | 网络图可视化 |
| [voila](https://voila.readthedocs.io) | 将 Notebook 转为独立 Web 应用（隐藏代码单元格） |

## Voilà：Notebook → 独立应用

[Voilà](https://voila.readthedocs.io) 将包含 ipywidgets 的 Notebook 转换为独立的 Web 应用：

- 只显示输出（Markdown、图表、控件），隐藏代码单元格
- 每个访问者获得独立的 Kernel 实例（互不干扰）
- 基于 Jupyter Server，不需要额外的部署基础设施
- 支持模板自定义和身份认证

```bash
# 将 Notebook 转为独立 Web 应用
voila notebook.ipynb

# 指定端口
voila --port=8866 notebook.ipynb
```

## 相关概念

- [什么是计算笔记本与 Jupyter 核心架构](01-what-is-jupyter.md) — 交互式计算概念
- [Kernel 架构](06-kernel-architecture.md) — Widget 模型在 Kernel 中的位置
- [客户端-服务器架构详解](08-client-server.md) — Comm 通道与消息传递
- [配置基础操作](../examples/02-config-basics.md) — 启用/禁用 Widget 扩展
