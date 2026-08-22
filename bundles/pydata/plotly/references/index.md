# 参考资料索引

本目录包含 plotly.py 库的深度参考文档，从源码层面解析核心机制。

## 文档列表

| 文档 | 说明 |
|------|------|
| [图对象模型](graph-obj-model.md) | graph_objs 包结构、Figure/Data/Layout/Trace 层级、basedatatypes.py 基类体系、动态属性访问、代码自动生成机制 |

## 信源登记簿

所有参考文档基于以下源码文件和版本生成：

### 核心源码路径

| 模块 | 文件路径 | 说明 |
|------|----------|------|
| 包入口 | `plotly/__init__.py` | 版本获取、惰性导入、pandas 后端 |
| 基类体系 | `plotly/basedatatypes.py` | BaseFigure、BasePlotlyType、BaseTraceType、BaseLayoutType |
| Figure 类 | `plotly/graph_objs/_figure.py` | Figure 自动生成类（继承 BaseFigure） |
| Layout 类 | `plotly/graph_objs/_layout.py` | Layout 自动生成类（继承 BaseLayoutType） |
| Trace 类 | `plotly/graph_objs/_scatter.py` 等 | 40+ 种 Trace 类型自动生成类 |
| 图对象包 | `plotly/graph_objs/` | 所有 Trace/Layout/Frame 子模块及嵌套属性目录 |
| 别名包 | `plotly/graph_objects/` | PEP8 命名别名，重导出 graph_objs |
| 子图工具 | `plotly/_subplots.py` | make_subplots() 函数、子图类型常量 |
| IO 模块 | `plotly/io/` | 渲染器框架、JSON/HTML 序列化、模板系统 |
| Express 核心 | `plotly/express/_core.py` | make_figure()、PxDefaults、数据映射逻辑 |
| Express 图表 | `plotly/express/_chart_types.py` | scatter/line/bar 等工厂函数 |
| Figure Factory | `plotly/figure_factory/` | create_* 特殊图表工厂函数 |
| 颜色模块 | `plotly/colors/` | 颜色比例尺、颜色转换工具 |
| 工具模块 | `plotly/tools.py` | mpl_to_plotly、FigureFactory 类 |
| 回调系统 | `plotly/callbacks.py` | Points、InputDeviceState、BoxSelector 等 |
| 异常类 | `plotly/exceptions.py` | PlotlyError 及子类 |
| Widget 基类 | `plotly/basewidget.py` | FigureWidget 的事件通信基类 |

### 版本信息

- 版本号通过 `importlib.metadata.version("plotly")` 动态获取
- 代码生成器来自 plotly 项目的 codegen 工具链
- 生成文档基于的源码路径：`d:\spaces\SpecWeave\external\libs\python\plotly.py\plotly\`

### 外部依赖

| 依赖 | 用途 |
|------|------|
| plotly.js | 前端渲染引擎（通过 CDN 加载，嵌入 HTML 输出） |
| numpy | Express 和 figure_factory 必需 |
| narwhals | DataFrame 抽象层，支持 pandas/polars 等 |
| ipywidgets (>=7.0) | FigureWidget Jupyter 交互支持（可选） |
| kaleido | 静态图片导出（PNG/SVG/PDF，可选） |
| packaging | 版本比较 |
