---
okf_version: "0.2"
type: concept
title: Matplotlib 简介
description: Matplotlib 是 Python 生态最广泛使用的面向对象绑图库，提供 pyplot 过程式接口、多后端渲染支持、PSF/BSD 兼容许可证，是整个 Python 可视化生态的基础
tags: [matplotlib, plotting, visualization, introduction, pyplot]
generated: { by: reference_agent/trae-glm, at: 2026-08-22T15:00:00Z }
verified: { by: "process:seven-concepts-v", at: 2026-08-22T15:30:00Z }
status: stable
stale_after: 2027-12-31
sources:
  - id: mpl-init
    resource: external/libs/python/matplotlib/matplotlib/lib/matplotlib/__init__.py
    title: matplotlib 包入口
  - id: mpl-artist-hierarchy
    resource: /references/artist-hierarchy.md
    title: Artist 层级体系源码参考
---

# Matplotlib 简介

Matplotlib 是 Python 生态中最广泛使用的**2D绑图库**，由 John D. Hunter（1968-2012）于2003年创建，采用 PSF（Python Software Foundation）兼容的 BSD 风格许可证开源发布。它提供了一套面向对象的绑图 API，以及一个模仿 MATLAB 的过程式接口 `pyplot`，能够生成出版质量的折线图、散点图、柱状图、直方图、等高线图、3D图形等几乎所有常见统计图表类型。

## 核心定位

Matplotlib 的核心设计哲学是：

1. **面向对象（OO）为核心**：所有可见元素都是 `Artist` 对象，Figure→Axes→Primitive 形成清晰的容器-图元层次结构。用户可以直接操作对象属性，完全控制绑图的每一个细节。

2. **pyplot 过程式接口为便捷入口**：`matplotlib.pyplot` 模块提供 MATLAB 风格的隐式状态机接口，通过 `gcf()`/`gca()` 自动追踪当前 Figure 和 Axes，适合交互式探索和快速绑图。

3. **多后端抽象**：通过 `backend_bases.py` 定义统一抽象层，同一套绑图代码可以输出到 AGG 栅格图像、PDF/SVG 矢量文件，或嵌入 Tk/Qt/Wx/GTK/WebAgg 等 GUI 界面。

## 许可证

Matplotlib 采用基于 PSF 的 BSD 兼容许可证发布。这意味着：
- ✅ 可自由使用、修改、分发
- ✅ 可用于商业软件
- ✅ 可闭源使用
- ❗ 必须保留版权声明和许可证文本
- ❗ 不得使用原作者名字进行推广

## 两种接口风格

### 1. 面向对象接口（推荐用于脚本/应用）

显式创建 Figure 和 Axes 对象，直接调用 Axes 方法：

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot([1, 2, 3], [4, 5, 1])
ax.set_xlabel('X轴')
ax.set_ylabel('Y轴')
ax.set_title('面向对象接口')
plt.show()
```

### 2. pyplot 状态机接口（适合交互式使用）

依赖隐式的当前 Figure/Axes 状态，调用 `plt.xxx()` 函数：

```python
import matplotlib.pyplot as plt

plt.figure(figsize=(8, 4))
plt.plot([1, 2, 3], [4, 5, 1])
plt.xlabel('X轴')
plt.ylabel('Y轴')
plt.title('pyplot 接口')
plt.show()
```

> **建议**：根据 `__init__.py` 模块文档，官方鼓励在编程时使用显式面向对象接口，pyplot 隐式接口主要用于交互式工作。`plt.figure`、`plt.subplot`、`plt.subplots`、`plt.savefig` 等少数函数在脚本中也可以简化代码。

## 多后端支持

Matplotlib 的后端系统将「绑图逻辑」与「渲染输出」完全分离。后端分为两大类：

### 渲染后端（非交互，输出到文件/内存）

| 后端 | 类型 | 输出格式 | 特点 |
|------|------|---------|------|
| AGG | 栅格 | PNG/JPG/TIFF/WebP/AVIF | 高质量 Anti-Grain Geometry 引擎，默认后端 |
| Cairo | 栅格+矢量 | PNG/PDF/SVG/PS | 需安装 pycairo，渲染效果不同 |
| SVG | 矢量 | SVG/SVGZ | 纯 Python 生成 SVG，适合Web |
| PDF | 矢量 | PDF | 适合出版印刷 |
| PS | 矢量 | PS/EPS | PostScript 输出 |
| PGF | 矢量 | PDF/PGF | LaTeX PGF/TikZ 输出 |

### 交互后端（GUI 窗口）

| 后端 | GUI 框架 | 说明 |
|------|---------|------|
| TkAgg | Tkinter | Python 内置，零依赖 |
| QtAgg/Qt5Agg | PyQt/PySide | 功能最丰富的 GUI |
| QtCairo | Qt + Cairo | 使用 Cairo 渲染 |
| WxAgg | wxPython | 原生跨平台 GUI |
| GTK3Agg/GTK4Agg | GTK 3/4 | Linux 桌面环境 |
| GTK3Cairo/GTK4Cairo | GTK + Cairo | Cairo 渲染 |
| WebAgg | 浏览器 | 内置 Web 服务器，浏览器交互 |
| nbAgg/ipympl | Jupyter | Notebook 内联交互 |
| macOSX | Cocoa | macOS 原生后端 |

### 后端切换机制

后端可以通过以下方式设置（必须在创建 Figure 之前）：

1. **rcParams/matplotlibrc 文件**：`backend : Agg`
2. **环境变量**：`MPLBACKEND=Agg`
3. **`matplotlib.use()` 函数**：`mpl.use('QtAgg')`
4. **`plt.switch_backend()`**：`plt.switch_backend('Agg')`
5. **IPython 魔法**：`%matplotlib qt`

## 核心模块架构

```
matplotlib/
├── artist.py          # Artist 基类 — 所有可见元素的抽象
├── figure.py          # Figure/FigureBase — 顶层容器
├── axes/
│   ├── _base.py       # _AxesBase — Axes 基类
│   └── _axes.py       # Axes — 所有绘图方法实现
├── pyplot.py          # pyplot — 状态机接口
├── lines.py           # Line2D — 折线/标记
├── patches.py         # Patch/Rectangle/Circle/Polygon — 几何图形
├── text.py            # Text/Annotation — 文本与注释
├── image.py           # AxesImage/FigureImage — 图像显示
├── collections.py     # LineCollection/PathCollection — 批量图元
├── colors.py          # Colormap/Normalize — 颜色系统
├── cm.py              # ScalarMappable/色图注册表
├── backend_bases.py   # RendererBase/FigureCanvasBase — 后端抽象
├── backends/          # 各后端实现
│   ├── backend_agg.py
│   ├── backend_svg.py
│   ├── backend_pdf.py
│   ├── backend_tkagg.py
│   ├── backend_qtagg.py
│   └── backend_webagg.py
├── axis.py            # XAxis/YAxis/Tick — 坐标轴与刻度
├── container.py       # BarContainer/ErrorbarContainer — 复合元素
├── transforms.py      # 坐标变换系统
└── rcsetup.py         # rcParams 配置系统
```

## Matplotlib 在可视化生态中的位置

Matplotlib 是 Python 可视化生态的**基础底座**：

```
Python 解释器
    ↓
NumPy（ndarray 数据结构）
    ↓
Matplotlib（Artist + Renderer + Backend 架构）
    ├── Seaborn（统计绑图，基于 Matplotlib Axes）
    ├── pandas.DataFrame.plot()（内置 Matplotlib 后端）
    ├── scipy（绑图工具函数）
    ├── scikit-learn（部分绑图函数）
    ├── Cartopy/GeoPandas（地理绑图扩展）
    ├── networkx（网络绑图）
    └── plotly/bokeh/altair（独立的交互式绑图库，但常借鉴API风格）
```

Matplotlib 专注于**静态出版质量绑图**，以精细控制和灵活性著称。Seaborn 等高级库在其之上封装了统计绑图的便捷接口，但底层仍然使用 Matplotlib 的 Artist 对象和 Axes 系统。

## 相关概念

- [Artist 体系](01-artist-hierarchy.md)
- [后端系统](02-backend-system.md)
- [pyplot 状态机](03-pyplot-state-machine.md)
- [基础绑图示例](../examples/basic-plotting.md)
- [Artist 层级源码参考](../references/artist-hierarchy.md)
