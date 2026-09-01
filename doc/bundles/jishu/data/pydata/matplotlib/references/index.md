# 信源登记簿（References）

本目录登记 matplotlib 知识包所有内容的信源出处，包括源码文件位置、模块职责和溯源事实编号。

## 源码信源清单

| 信源 ID | 文件路径（相对于 matplotlib/lib/） | 模块 | 核心类/函数 | 溯源内容 |
|---------|-----------------------------------|------|------------|---------|
| S-ARTIST | `matplotlib/artist.py` | artist | `Artist`（第111行） | Artist 基类定义、属性系统、回调机制、光栅化装饰器 |
| S-FIGURE | `matplotlib/figure.py` | figure | `FigureBase`（第183行）、`Figure`（第2511行）、`SubFigure`、`_AxesStack`（第71行） | Figure 容器、子图管理、savefig、布局引擎 |
| S-AXES-BASE | `matplotlib/axes/_base.py` | axes._base | `_AxesBase`（第558行）、`_axis_method_wrapper`（第36行）、`_process_plot_format`（第122行） | Axes 基类、坐标变换、spines、轴对象、格式字符串解析 |
| S-AXES | `matplotlib/axes/_axes.py` | axes._axes | `Axes`（第89行） | plot/scatter/bar/hist/imshow/contour/pie 等所有绘图方法 |
| S-PYPLOT | `matplotlib/pyplot.py` | pyplot | `gcf`（第1150行）、`gca`（第2933行）、`figure`（第904行）、`subplots`（第1679行）、`plot`（第4041行）、`show`（第602行）、`savefig`（第1343行）、`switch_backend`（第395行） | 状态机接口、gcf/gca 隐式获取、当前 Figure/Axes 管理 |
| S-BACKEND-BASES | `matplotlib/backend_bases.py` | backend_bases | `RendererBase`（第134行）、`FigureCanvasBase`（第1709行）、`GraphicsContextBase`（第701行）、`FigureManagerBase`（第2704行）、`Event`（第1178行）、`ShowBase`（第3737行） | 后端抽象基类、渲染器接口、事件系统、文件格式注册表 |
| S-BACKENDS | `matplotlib/backends/` | backends | `backend_agg.py`、`backend_svg.py`、`backend_pdf.py`、`backend_ps.py`、`backend_cairo.py`、`backend_tkagg.py`、`backend_qtagg.py`、`backend_webagg.py`、`backend_wxagg.py`、`backend_gtk*agg.py` 等 | 渲染后端（AGG/Cairo/SVG/PDF/PS）和交互后端（Tk/Qt/Wx/WebAgg/GTK）实现 |
| S-LINES | `matplotlib/lines.py` | lines | `Line2D`（第265行）、`AxLine`（第1517行）、`VertexSelector`（第1678行） | 折线、标记、无限直线（axhline/axvline） |
| S-PATCHES | `matplotlib/patches.py` | patches | `Patch`（第35行）、`Rectangle`（第802行）、`Polygon`（第1209行）、`Circle`（第2044行）、`Arc`（第2086行）、`Arrow`（第1395行）、`FancyArrow`（第1478行）、`FancyArrowPatch`（第4257行）、`StepPatch`（第1100行）、`ArrowStyle`（第3290行） | 2D 几何图形补丁、箭头样式 |
| S-TEXT | `matplotlib/text.py` | text | `Text`（第149行）、`Annotation`（第1893行） | 文本渲染、带箭头注释 |
| S-IMAGE | `matplotlib/image.py` | image | `AxesImage`（第880行）、`FigureImage`（第1381行）、`BboxImage`（第1447行） | 图像显示、colormap 映射、插值 |
| S-COLLECTIONS | `matplotlib/collections.py` | collections | `LineCollection`、`PolyCollection`、`PathCollection`、`QuadMesh`、`EventCollection` | 高效批量绘制（散点、等值线填充、网格） |
| S-COLORS | `matplotlib/colors.py` | colors | `Colormap`（第713行）、`LinearSegmentedColormap`（第1087行）、`ListedColormap`（第1299行）、`Normalize`（第2405行） | 颜色规范、色图、归一化、颜色映射 |
| S-CM | `matplotlib/cm.py` | cm | `ScalarMappable`（mixin）、`_colormaps` 注册表 | 色图注册与访问、ScalarMappable 混入类 |
| S-CONTAINER | `matplotlib/container.py` | container | `Container`（第5行）、`BarContainer`（第42行）、`ErrorbarContainer`（第119行）、`PieContainer`（第151行）、`StemContainer`（第223行） | 复合绘图元素容器（元组子类） |
| S-INIT | `matplotlib/__init__.py` | matplotlib | `use()`、`rcParams`、`get_backend()` | 包入口、后端选择、配置系统 |
| S-AXIS | `matplotlib/axis.py` | axis | `Axis`、`XAxis`、`YAxis`、`Tick` | 坐标轴、刻度、标签管理 |

## 文件格式与后端映射

根据 `backend_bases.py` 中 `_default_backends` 和 `_default_filetypes` 注册表（第63-98行）：

| 格式扩展名 | MIME 类型描述 | 默认后端模块 |
|-----------|-------------|-------------|
| eps | Encapsulated Postscript | `backend_ps` |
| pdf | Portable Document Format | `backend_pdf` |
| pgf | PGF code for LaTeX | `backend_pgf` |
| png | Portble Network Graphics | `backend_agg` |
| ps | Postscript | `backend_ps` |
| svg/svgz | Scalable Vector Graphics | `backend_svg` |
| raw/rgba | Raw RGBA bitmap | `backend_agg` |
| jpg/jpeg | JPEG | `backend_agg` |
| gif | GIF | `backend_agg` |
| tif/tiff | TIFF | `backend_agg` |
| webp | WebP | `backend_agg` |
| avif | AVIF | `backend_agg` |

## 信源核验方法

本文档中所有类名、方法名、行号均通过以下方式核验：

1. **Grep 定位**：使用正则 `^class ClassName` 和 `^def funcName` 在源码中精确定义行
2. **源码阅读**：对核心类（Artist、FigureBase、_AxesBase、Axes、Figure、Line2D、Patch 等）读取类定义头部和 `__init__` 方法，确认属性和参数
3. **交叉验证**：交叉检查 pyplot 函数与 Axes 方法的对应关系（如 `plt.plot` → `Axes.plot`）

```{toctree}
:hidden:
:maxdepth: 7

artist-hierarchy
```
