# 概念索引（Concepts）

本目录包含 matplotlib 核心架构概念的系统性讲解，共 4 篇概念文档，建议按顺序阅读。

## 入门

| 序号 | 文档 | 核心内容 |
|------|------|---------|
| 00 | [Matplotlib 简介](00-introduction.md) | 面向对象绑图库定位、pyplot 过程式接口、PSF/BSD许可证、多后端支持（AGG/Tk/Qt/WebAgg）、matplotlib 在可视化生态的位置 |

## 核心架构

| 序号 | 文档 | 核心内容 |
|------|------|---------|
| 01 | [Artist 体系](01-artist-hierarchy.md) | Artist 基类→Figure(顶层容器)→Axes(绑图区域)→Primitive(Line2D/Rectangle/Text/Image)→Container(Axes容器)；属性系统(setp/getp)、zorder绘制顺序、stale重绘机制、事件系统 |
| 02 | [后端系统](02-backend-system.md) | 渲染后端(AGG/Cairo/SVG/PDF/PS)、交互后端(Tk/Qt/Wx/WebAgg/GTK/macOSX)、backend_bases.py抽象基类(RendererBase/FigureCanvasBase/GraphicsContextBase)、后端切换机制(plt.switch_backend/mpl.use/MPLBACKEND)、无头环境注意事项 |
| 03 | [pyplot 状态机](03-pyplot-state-machine.md) | gcf()/gca()隐式获取当前Figure/Axes、Gcf全局管理器、_AxesStack、pyplot函数是Axes方法的薄包装、OO接口vs pyplot接口取舍、状态机常见陷阱、交互模式 |

## 阅读路径建议

```
00-introduction（了解定位）
    ↓
01-artist-hierarchy（理解对象模型）→ references/artist-hierarchy.md（源码溯源）
    ↓
02-backend-system（理解渲染抽象）
    ↓
03-pyplot-state-machine（理解接口风格）
    ↓
examples/basic-plotting.md（动手实践）
```

## 概念依赖关系

```
00-introduction
    ├── 01-artist-hierarchy ←→ references/artist-hierarchy.md
    │     ├── 02-backend-system
    │     └── 03-pyplot-state-machine
    └── examples/basic-plotting.md
```

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-artist-hierarchy
02-backend-system
03-pyplot-state-machine
```
