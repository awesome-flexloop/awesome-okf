# 示例索引（Examples）

本目录包含 matplotlib 绑图的实战代码示例，所有代码可直接运行。

## 基础示例

| 文档 | 覆盖内容 |
|------|---------|
| [基础绑图](basic-plotting.md) | 折线图（plot）、散点图（scatter）、柱状图（bar/barh）、直方图（hist）、饼图（pie）、子图网格（subplots）、subplot_mosaic 复杂布局、样式与主题（style/rcParams）、注释与箭头（annotate/text）、LaTeX 数学公式、imshow 图像显示、双Y轴（twinx）、savefig 保存图片、中文显示设置 |
| [事件处理](event-handling.md) | mpl_connect 事件回调、可连接事件名与事件属性、可拖拽矩形（DraggableRectangle）、鼠标进出事件、picker 对象拾取（基于 2020 年前后教程） |
| [形状与路径](patches-and-path.md) | patches 形状（Ellipse/Arc/Circle/Wedge/RegularPolygon/Arrow/FancyBboxPatch 等）、PatchCollection 集合、Path 路径与 codes 顶点编码、心形/条形图路径（基于 2020 年前后教程） |
| [分形三角形](fractal.md) | Chaos Game 分形三角形：随机取顶点取中点迭代十万次、plt.scatter 渲染（基于 2020 年前后教程） |

## 示例学习路径

```
1. 折线图 → 2. 散点图 → 3. 柱状图 → 4. 直方图
    ↓
5. 子图布局 → 6. 样式设置 → 7. 注释标注
    ↓
8. imshow/颜色条 → 9. 双Y轴综合示例 → 10. 保存图片
```

## 进阶交互与特殊图形（基于 2020 年前后教程）

```
11. 事件处理（mpl_connect/可拖拽/拾取） → 12. 形状与路径（patches/path） → 13. 分形三角形（Chaos Game）
```

## 运行环境

所有示例在以下环境验证通过：
- Python 3.10+
- Matplotlib 3.8+
- NumPy 1.24+

可选依赖：
- SciPy（用于部分示例的 KDE 曲线）
- Jupyter Notebook（推荐交互式运行）

```{toctree}
:hidden:
:maxdepth: 7

basic-plotting
event-handling
fractal
patches-and-path
```
