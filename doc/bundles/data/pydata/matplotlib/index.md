---
okf_version: "0.2"
---

# Matplotlib 绑图库知识库

本知识包是 [Matplotlib](https://matplotlib.org)（Python 生态最广泛使用的 2D 绑图库）的系统化中文教程，基于 Matplotlib 3.x 源码（`matplotlib/lib/matplotlib/` 目录）深度阅读生成，覆盖从 Artist 继承体系到后端渲染抽象、从 pyplot 状态机到面向对象接口的完整核心架构。所有内容均溯源至 Matplotlib 源码（`artist.py`、`figure.py`、`axes/_base.py`、`axes/_axes.py`、`pyplot.py`、`backend_bases.py`、`lines.py`、`patches.py`、`text.py`、`image.py`、`colors.py`、`cm.py`、`container.py` 等核心模块），遵循 [OKF v0.2 规范](https://github.com/awesome-flexloop/awesome-okf)。

## 入门基础（concepts/）

* [Matplotlib 简介](concepts/00-introduction.md) — 面向对象绑图库定位、PSF/BSD 兼容许可证、pyplot 过程式接口、多后端支持（AGG/Tk/Qt/WebAgg/PDF/SVG 等）、matplotlib 在 Python 可视化生态中的位置。
* [Artist 体系](concepts/01-artist-hierarchy.md) — Artist 基类→Figure（顶层容器）→Axes（绑图区域）→Primitive（Line2D/Rectangle/Text/Image）→Container 类型；属性系统（setp/getp）、zorder 绘制顺序、stale 重绘机制、事件系统。
* [后端系统](concepts/02-backend-system.md) — 渲染后端（AGG/Cairo/SVG/PDF/PS/PGF）、交互后端（Tk/Qt/Wx/WebAgg/GTK/macOSX/nbAgg）、backend_bases.py 抽象基类（RendererBase/FigureCanvasBase/GraphicsContextBase/FigureManagerBase）、后端切换机制（plt.switch_backend/mpl.use/MPLBACKEND）、无头环境注意事项。
* [pyplot 状态机](concepts/03-pyplot-state-machine.md) — gcf()/gca() 隐式获取当前 Figure/Axes、Gcf 全局 Figure 管理器、_AxesStack、pyplot 函数是 Axes 方法的薄包装、OO 接口 vs pyplot 接口的取舍、状态机常见陷阱、交互模式（ion/ioff）。

## 实战示例（examples/）

* [基础绑图](examples/basic-plotting.md) — 折线图（plot/格式字符串/fill_between）、散点图（scatter/颜色映射/大小映射/颜色条）、柱状图（bar/barh/分组/堆叠/误差棒/数值标签）、直方图（hist/累积/KDE/多分布对比）、饼图（pie/explode）、子图网格（subplots/sharex/sharey）、subplot_mosaic 复杂布局、样式与主题（plt.style/rcParams）、注释与箭头（annotate/text/bbox）、LaTeX 数学公式、imshow 图像显示（contour/colormap）、双 Y 轴（twinx）、savefig 保存图片（PNG/PDF/SVG/DPI/bbox_inches）、中文显示设置，全部代码可直接运行。

## 信源登记簿（references/）

* [Artist 层级体系源码参考](references/artist-hierarchy.md) — 基于源码逐类追踪 Artist 基类（artist.py:111）、FigureBase（figure.py:183）、Figure（figure.py:2511）、_AxesBase（axes/_base.py:558）、Axes（axes/_axes.py:89）、Line2D（lines.py:265）、Patch（patches.py:35）、Text（text.py:149）、AxesImage（image.py:880）、Container（container.py:5）等的完整继承树、核心属性表、方法签名、光栅化装饰器机制、set() 自动生成机制、事件类族（MouseEvent/KeyEvent/PickEvent 等）。
* [信源索引](references/index.md) — 17 个源码信源登记（S-ARTIST 到 S-AXIS）、文件格式与后端映射表、信源核验方法说明。

## 学习路径建议

1. **新手入门**：00-introduction → 01-artist-hierarchy → 运行 examples/basic-plotting.md 中的折线图/散点图/柱状图示例
2. **架构理解**：02-backend-system → 03-pyplot-state-machine → 理解 OO 接口与 pyplot 接口的取舍
3. **深入实践**：examples/basic-plotting.md 完整阅读 → 子图布局/注释/双Y轴/保存图片
4. **源码溯源**：阅读 references/artist-hierarchy.md，结合源码目录理解类层次和方法定义位置

## 核心源码速查表

| 模块 | 核心类/函数 | 用途 |
|------|-----------|------|
| `matplotlib/__init__.py` | `use()`, `rcParams`, `get_backend()` | 包入口、后端选择、配置 |
| `matplotlib/artist.py` | `Artist`（第111行） | 所有可见元素的抽象基类 |
| `matplotlib/figure.py` | `FigureBase`（第183行）、`Figure`（第2511行）、`_AxesStack`（第71行） | 顶层容器、子图管理、savefig |
| `matplotlib/axes/_base.py` | `_AxesBase`（第558行） | Axes 基类、坐标变换、spines |
| `matplotlib/axes/_axes.py` | `Axes`（第89行） | 所有绘图方法（plot/scatter/bar/hist/imshow 等） |
| `matplotlib/pyplot.py` | `gcf`（第1150行）、`gca`（第2933行）、`figure`（第904行）、`subplots`（第1679行）、`plot`（第4041行）、`show`（第602行）、`savefig`（第1343行）、`switch_backend`（第395行） | 状态机接口 |
| `matplotlib/backend_bases.py` | `RendererBase`（第134行）、`FigureCanvasBase`（第1709行）、`GraphicsContextBase`（第701行）、`FigureManagerBase`（第2704行）、`Event`（第1178行）、`ShowBase`（第3737行） | 后端抽象基类、事件系统 |
| `matplotlib/lines.py` | `Line2D`（第265行）、`AxLine`（第1517行） | 折线、标记、无限直线 |
| `matplotlib/patches.py` | `Patch`（第35行）、`Rectangle`（第802行）、`Polygon`（第1209行）、`Circle`（第2044行）、`Arc`（第2086行）、`FancyArrowPatch`（第4257行） | 2D 几何图形 |
| `matplotlib/text.py` | `Text`（第149行）、`Annotation`（第1893行） | 文本渲染、注释 |
| `matplotlib/image.py` | `AxesImage`（第880行）、`FigureImage`（第1381行） | 图像显示 |
| `matplotlib/colors.py` | `Colormap`（第713行）、`LinearSegmentedColormap`（第1087行）、`ListedColormap`（第1299行）、`Normalize`（第2405行） | 颜色系统 |
| `matplotlib/cm.py` | `ScalarMappable`、`_colormaps` | 色图注册与混入类 |
| `matplotlib/container.py` | `Container`（第5行）、`BarContainer`（第42行）、`ErrorbarContainer`（第119行）、`StemContainer`（第223行） | 复合元素容器 |

## 信任与生命周期说明

* **status 判定依据**：全部 10 个内容文档（4 个概念 + 1 个示例 + 2 个信源登记 + 3 个子目录 index + 根 index.md），非 index 文件均 `status: stable`。内容基于对 Matplotlib 3.x 源码（`external/libs/python/matplotlib/matplotlib/lib/matplotlib/` 目录）核心子系统的逐模块阅读与事实提取，所有类名、方法名、行号均通过 Grep 精确定位。
* **stale_after 解释**：统一设置为 `2027-12-31`。Matplotlib 核心架构（Artist 层次、后端抽象、pyplot 状态机）自 1.x 以来保持高度稳定；3.x 系列持续增强但核心 API 没有 Breaking Change，该日期作为对未来大版本变化的保守重新评估节点。
* **核验链路**：`generated.at` 记录原始生成时刻（2026-08-22T15:00:00Z）；`verified.at` 记录过程核验事件（2026-08-22T15:30:00Z），所有类名、函数名、参数名、行号均通过源码 Grep 和类定义头部读取验证。

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
