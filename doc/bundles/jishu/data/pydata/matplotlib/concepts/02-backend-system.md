---
okf_version: "0.2"
type: concept
title: 后端系统
description: Matplotlib 后端系统将绑图逻辑与渲染输出分离，通过 backend_bases.py 抽象基类定义渲染器/画布/管理器接口，支持 AGG/Cairo/SVG/PDF 等渲染后端和 Tk/Qt/Wx/WebAgg 等交互后端
tags: [matplotlib, backend, renderer, AGG, SVG, PDF, Tk, Qt, WebAgg, GUI]
generated: { by: reference_agent/trae-glm, at: 2026-08-22T15:00:00Z }
verified: { by: "process:seven-concepts-v", at: 2026-08-22T15:30:00Z }
status: stable
stale_after: 2027-12-31
sources:
  - id: mpl-backend-bases
    resource: external/libs/python/matplotlib/matplotlib/lib/matplotlib/backend_bases.py
    title: matplotlib.backend_bases 模块 — 后端抽象基类
  - id: mpl-backends
    resource: external/libs/python/matplotlib/matplotlib/lib/matplotlib/backends/
    title: matplotlib.backends 包 — 后端实现
  - id: mpl-init
    resource: external/libs/python/matplotlib/matplotlib/lib/matplotlib/__init__.py
    title: matplotlib 包入口（use 函数）
---

# 后端系统

后端（Backend）是 Matplotlib 架构中最关键的抽象层之一。它将「**绑什么图**」（Artist 对象树构建）与「**怎么渲染**」（输出到屏幕/文件）完全分离。用户的绑图代码（创建 Figure/Axes/Line2D 等）与后端无关，同一套代码只需切换后端即可输出到 PNG 图片、PDF 文件、Tk 窗口、Qt 窗口或浏览器。

## 一、后端的两层含义

Matplotlib 中的"后端"实际上包含两层概念：

1. **渲染后端（Renderer/Non-interactive backend）**：负责将 Artist 对象树绘制为像素或矢量路径。不提供 GUI 窗口。
   - AGG（栅格）、Cairo（栅格+矢量）、SVG（矢量）、PDF（矢量）、PS（矢量）、PGF（矢量）

2. **交互后端（GUI backend）**：在渲染后端基础上，提供 GUI 窗口事件循环、工具栏、用户交互。通常命名为 `<GUI>Agg` 形式，表示使用 GUI 框架做窗口管理，用 AGG 做渲染。
   - TkAgg、Qt5Agg/QtAgg、WxAgg、GTK3Agg/GTK4Agg、WebAgg、macosx、nbAgg

交互后端 = GUI 框架（窗口+事件）+ 渲染引擎（AGG/Cairo）。例如 `TkAgg` = Tkinter 窗口 + AGG 渲染。

## 二、backend_bases.py 抽象基类

`backend_bases.py` 定义了所有后端必须实现的抽象接口。核心类包括：

### RendererBase（第134行）

渲染器抽象基类，负责实际的绘制操作。子类必须实现的方法：

| 方法 | 说明 |
|------|------|
| `draw_path(gc, path, transform, rgbFace)` | 绘制路径（核心方法，必须实现） |
| `draw_image(gc, x, y, im, transform)` | 绘制图像 |
| `draw_gouraud_triangles(gc, points, colors, trans)` | 绘制 Gouraud 着色三角形 |
| `draw_text(gc, x, y, s, prop, angle, ismath)` | 绘制文本（建议实现以优化性能） |
| `draw_markers(gc, marker_path, marker_trans, path, trans, rgbFace)` | 绘制标记（建议实现） |

其他重要方法/属性：
- `open_group()`/`close_group()` — 分组（SVG/PDF 等格式用）
- `flipy` — Y 轴是否翻转（大多数后端 True）
- `get_canvas_width_height()` — 获取画布尺寸
- `get_text_width_height_descent()` — 文本度量

### GraphicsContextBase（第701行）

图形上下文，存储绘制时的样式属性：颜色、线宽、线型、透明度、裁剪路径、抗锯齿、hatch 图案等。后端通过 GC 对象传递这些属性给绘制方法。

核心属性：
- `_linewidth`、`_linestyle`、`_color`、`_alpha`
- `_capstyle`、`_joinstyle`（线头/连接点样式）
- `_antialiased`、`_hatch`、`_fillcolor`
- `_cliprect`/`_clippath`、`_dashes`

### FigureCanvasBase（第1709行）

画布抽象层，是连接 Figure 与 GUI 窗口/输出文件的桥梁。

核心职责：
- **持有 Figure**：`self.figure` 指向绑定的 Figure 对象
- **管理渲染器**：`get_renderer()` 返回 RendererBase 实例
- **触发绘制**：`draw()` 方法启动渲染流程，`draw_idle()` 空闲时重绘
- **事件分发**：通过 `mpl_connect(event, callback)` 注册事件回调
- **输出文件**：`print_figure(filename, *args, **kwargs)` 保存到文件
- **GUI 事件循环**：`start_event_loop()`/`stop_event_loop()`

子类需实现：`switch_backends()` 中的具体 canvas 类、`paint()` 事件处理等。

### FigureManagerBase（第2704行）

GUI 窗口管理器，负责窗口标题、大小调整、工具栏、显示/隐藏等。

### Event 类族（第1178行起）

| 类名 | 行号 | 说明 |
|------|------|------|
| `Event` | 1178 | 事件基类，持有 `name`、`canvas`、`guiEvent` |
| `DrawEvent` | 1206 | 画布重绘事件（`'draw_event'`） |
| `ResizeEvent` | 1233 | 窗口大小改变事件（`'resize_event'`） |
| `CloseEvent` | 1253 | 窗口关闭事件（`'close_event'`） |
| `LocationEvent` | — | 带坐标的事件基类 |
| `MouseEvent` | 1323 | 鼠标事件（按键/移动/滚轮） |
| `KeyEvent` | 1497 | 键盘事件 |
| `PickEvent` | 1448 | Artist 拾取事件 |

### ShowBase（第3737行）

`plt.show()` 的后端实现基类，负责启动 GUI 事件循环并阻塞主线程。每个交互后端都有自己的 `Show` 子类。

## 三、渲染后端详解

### AGG（backend_agg.py）— 默认后端

AGG（Anti-Grain Geometry）是一个高质量的 C++ 2D 栅格渲染引擎，Matplotlib 自带编译好的 `_backend_agg` 扩展模块。

特点：
- **输出格式**：PNG、JPG、TIFF、WebP、AVIF、BMP、RGBA（raw）
- **抗锯齿**：高质量亚像素抗锯齿
- **字体**：通过 FreeType（`ft2font`）渲染文本
- **性能**：纯 C++ 渲染，速度快
- **依赖**：无外部 GUI 依赖，是无头环境（服务器、CI）的首选

AGG 是大多数 GUI 后端的渲染引擎（TkAgg、QtAgg、WxAgg 都使用 AGG 绘制到内存缓冲区，再交给 GUI 框架显示）。

### SVG（backend_svg.py）

纯 Python 实现的 SVG 矢量输出后端。

特点：
- **输出格式**：SVG、SVGZ（gzip 压缩的 SVG）
- **无外部依赖**：纯 Python 生成 SVG XML
- **文本可选路径化**：可选择将文本转为路径（`svg.fonttype` rcParam）
- **适合 Web**：输出可直接嵌入 HTML
- **不支持交互**：纯文件输出后端

### PDF（backend_pdf.py）

纯 Python 实现的 PDF 输出后端。

特点：
- **输出格式**：PDF
- **适合出版**：支持嵌入字体、矢量图形
- **多页支持**：通过 `PdfPages` 类支持多页 PDF
- **Type1/TrueType**：支持多种字体格式嵌入

### PS/EPS（backend_ps.py）

PostScript 输出后端。

特点：
- **输出格式**：PS、EPS（Encapsulated PostScript）
- **适合 LaTeX**：传统学术出版常用格式
- **支持 Level 2 PS**：利用 Level 2 特性优化

### Cairo（backend_cairo.py）

基于 Cairo 图形库的渲染后端，通过 `pycairo` 绑定。

特点：
- **输出格式**：PNG、PDF、SVG、PS
- **渲染质量**：Cairo 渲染效果与 AGG 略有不同
- **依赖**：需要安装 pycairo 和 Cairo 库
- **配对 GUI**：QtCairo、TkCairo、GTK3Cairo、WxCairo

### PGF（backend_pgf.py）

LaTeX PGF/TikZ 输出后端。

特点：
- **输出格式**：PDF（通过 LaTeX 编译）
- **需要 LaTeX**：依赖系统安装 LaTeX（XeLaTeX/LuaLaTeX）
- **高质量排版**：文本完全由 LaTeX 渲染，与文档字体一致
- **适合学术论文**：插入到 LaTeX 文档中无字体不一致问题

## 四、交互后端详解

### TkAgg（backend_tkagg.py）

基于 Tkinter（Python 标准库自带）的 GUI 后端。

- **依赖**：无（Tkinter 是 Python 标配）
- **特点**：零安装即可使用，是 fallback 默认交互后端
- **组成**：Tk Canvas + AGG 渲染（先 AGG 渲染到 PNG 缓冲区，再贴到 Tk Canvas）

### QtAgg/Qt5Agg（backend_qtagg.py/backend_qt5agg.py）

基于 Qt 框架（PyQt5/PySide2/PyQt6/PySide6）的 GUI 后端。

- **依赖**：需要安装 PyQt5/PySide2/PyQt6/PySide6
- **特点**：功能最丰富、外观最现代的交互后端
- **组成**：QWidget 窗口 + AGG 渲染
- **支持**：Qt5Agg（Qt5）、QtAgg（自动选择Qt5/Qt6）
- **工具栏**：内置 NavigationToolbar2QT，提供缩放/平移/保存等功能

### WxAgg（backend_wxagg.py）

基于 wxPython 的 GUI 后端。

- **依赖**：需要安装 wxPython
- **特点**：原生外观的跨平台 GUI

### GTK3Agg/GTK4Agg（backend_gtk3agg.py/backend_gtk4agg.py）

基于 GTK 的 GUI 后端（GTK 3 和 GTK 4 版本）。

- **依赖**：需要安装 PyGObject 和 GTK 开发库
- **特点**：Linux 桌面环境（GNOME）原生

### WebAgg（backend_webagg.py）

基于 Web 浏览器的交互后端。

- **依赖**：无（内置 Tornado Web 服务器）
- **特点**：启动一个本地 Web 服务器，在浏览器中交互绑图
- **组成**：Tornado 后端 + JavaScript 前端（mpl.js）
- **支持**：缩放/平移/调整大小等基本交互
- **访问**：浏览器打开 `http://localhost:8888/`（默认端口）
- **远程使用**：可从远程机器访问（注意安全）

### nbAgg（backend_nbagg.py）/ ipympl

Jupyter Notebook 内联交互后端。

- **依赖**：`ipympl` 包（`pip install ipympl`）
- **特点**：在 Notebook 单元格内显示可交互图形
- **启用**：`%matplotlib widget` 或 `%matplotlib ipympl`
- **对比 inline**：inline 是静态 PNG 嵌入；ipympl 提供完整交互

### macOSX（backend_macosx.py）

macOS 原生 Cocoa 后端。

- **依赖**：仅 macOS 系统可用
- **特点**：原生 Retina 支持，原生外观
- **渲染**：直接使用 CoreGraphics 渲染（不依赖 AGG）

## 五、后端切换机制

后端的选择发生在 Matplotlib 初始化和 Figure 创建时。切换后端有以下几种方式，按优先级从高到低：

### 1. matplotlib.use()（必须在创建 Figure 前调用）

```python
import matplotlib
matplotlib.use('Agg')       # 非交互：只输出到文件
matplotlib.use('TkAgg')     # Tkinter 交互窗口
matplotlib.use('QtAgg')     # Qt 交互窗口
matplotlib.use('WebAgg')    # 浏览器交互
matplotlib.use('module://my_backend')  # 自定义后端
```

> ⚠️ **注意**：`matplotlib.use()` 必须在创建任何 Figure 之前调用，且在导入 pyplot 后立即调用最佳。一旦 Figure 创建完成，GUI 后端之间无法互相切换（但可以切换到非交互后端用于保存文件）。

### 2. plt.switch_backend()

```python
import matplotlib.pyplot as plt
plt.switch_backend('Agg')
```

与 `matplotlib.use()` 类似，但可以关闭已有窗口并切换。

### 3. MPLBACKEND 环境变量

```bash
# Linux/macOS
export MPLBACKEND=Agg
python script.py

# Windows
set MPLBACKEND=Agg
python script.py

# 或临时设置
MPLBACKEND=Agg python script.py
```

### 4. matplotlibrc 配置文件

在 `matplotlibrc` 文件中设置：
```
backend : Agg
```

配置文件位置：
- 当前目录：`./matplotlibrc`
- 用户目录：`~/.config/matplotlib/matplotlibrc`（Linux）/ `~/.matplotlib/matplotlibrc`（其他）
- Matplotlib 安装目录：`mpl-data/matplotlibrc`

### 5. IPython 魔法命令

```python
%matplotlib inline      # Jupyter：静态PNG嵌入
%matplotlib widget      # Jupyter：ipympl交互
%matplotlib qt          # Qt窗口
%matplotlib tk          # Tk窗口
%matplotlib notebook    # 旧版Jupyter交互（等价于nbAgg）
```

## 六、后端选择决策指南

| 场景 | 推荐后端 | 原因 |
|------|---------|------|
| 服务器/CI/无显示器 | Agg | 无依赖，高质量栅格输出 |
| 脚本生成PNG图片 | Agg | 简单直接 |
| 生成PDF/SVG矢量 | PDF/SVG | 纯Python，无LaTeX依赖 |
| 快速交互式探索 | TkAgg | 零安装，Python自带 |
| 桌面应用集成 | QtAgg | 功能最丰富，社区最大 |
| Jupyter Notebook | ipympl/inline | 内联交互或静态图片 |
| 远程/浏览器访问 | WebAgg | 无需本地GUI框架 |
| LaTeX论文出版 | PGF/PDF | LaTeX排版，字体一致 |
| macOS本地开发 | macOSX | 原生Retina体验 |

## 七、文件格式注册表

`backend_bases.py` 维护了两个核心注册表（第63-98行）：

- `_default_filetypes`：文件扩展名 → 格式描述映射
- `_default_backends`：文件扩展名 → 默认后端模块映射

当调用 `fig.savefig('output.pdf')` 时，Matplotlib 会：
1. 根据扩展名 `'pdf'` 查找 `_default_backends['pdf']`
2. 延迟导入 `matplotlib.backends.backend_pdf`
3. 获取其 `FigureCanvas` 类
4. 创建临时 canvas，调用 `print_pdf()` 方法输出

用户可以通过 `register_backend(format, backend, description)` 注册自定义文件格式。

## 八、后端注册与发现机制

`backends/registry.py` 提供了 `backend_registry`，支持：
- 延迟加载后端模块
- 后端兼容性检测
- 内置后端列表查询

查询可用后端：
```python
import matplotlib
print(matplotlib.rcsetup.all_backends)  # 列出所有已知后端名
from matplotlib.backends import backend_registry
print(backend_registry.list_all())  # 列出可解析的后端
```

## 九、无头环境（Headless）注意事项

在无显示器的环境（服务器、Docker、SSH、CI）中使用 Matplotlib 时：

1. **必须选择非交互后端**：通常是 Agg
2. **不要调用 plt.show()**：无头环境没有 GUI 事件循环
3. **启动前设置后端**：
   ```python
   import matplotlib
   matplotlib.use('Agg')
   import matplotlib.pyplot as plt
   # ... 绑图代码 ...
   plt.savefig('output.png')
   ```
4. **或者用环境变量**：`MPLBACKEND=Agg python script.py`

如果遇到 "TclError: no display name and no $DISPLAY environment variable" 错误，说明当前后端（通常是 TkAgg）试图连接显示器，但环境中没有 X11/Wayland 显示服务。切换到 Agg 即可解决。

## 相关概念

- [Artist 体系](01-artist-hierarchy.md)
- [pyplot 状态机](03-pyplot-state-machine.md)
- [Matplotlib 简介](00-introduction.md)
- [Artist 层级源码参考](../references/artist-hierarchy.md)
- [基础绑图示例](../examples/basic-plotting.md)
