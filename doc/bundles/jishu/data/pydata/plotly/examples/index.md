# 示例索引

本目录包含 Plotly.py 的可运行代码示例。

## 文档列表

| 文档 | 说明 |
|------|------|
| [基础交互式图表](interactive-charts.md) | 散点图、折线图、柱状图、饼图、热力图、3D 表面图、子图的完整代码示例 |

## 使用方式

所有示例代码可直接复制到 Python 环境中运行。前置依赖：

```bash
pip install plotly numpy
```

在 Jupyter Notebook/Lab 中运行时，图表会直接嵌入 Notebook 输出单元。在纯 Python 脚本中运行时，默认会在浏览器中打开临时 HTML 文件（使用 `browser` 渲染器）。

如需更改渲染方式：

```python
import plotly.io as pio
pio.renderers.default = "browser"   # 浏览器
pio.renderers.default = "svg"       # 静态 SVG
pio.renderers.default = "png"       # 静态 PNG（需 kaleido）
```

```{toctree}
:hidden:
:maxdepth: 7

interactive-charts
```
