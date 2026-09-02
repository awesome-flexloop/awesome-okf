# 概念索引（Concepts）

本目录包含 Pillow 核心概念的系统性讲解，共 4 篇概念文档，建议按顺序阅读。

## 概念列表

| 序号 | 文档 | 核心内容 |
|------|------|---------|
| 00 | [图像基础与处理](00-image-basics.md) | `Image` 类基础：open/save/属性查询、crop/paste、split/merge、resize/rotate/transpose、convert、filter/point/ImageEnhance、序列与 draft（F-128~F-140） |
| 01 | [缩放与合成](01-resize-and-composite.md) | `Image.new` 创建、blend 透明度混合、composite 遮罩混合、eval 按像素、thumbnail 按尺寸、ImageChops 通道运算（F-154~F-161） |
| 02 | [ImageDraw 绘制](02-imagedraw-drawing.md) | `ImageDraw.Draw` 与 line/rectangle/arc/ellipse/chord/pieslice/polygon/point、text 签名、中文字体 truetype、文字框选与笔画（F-120~F-127） |
| 03 | [图像特效](03-image-effects.md) | 灰度梯度重构+光源模拟实现手绘/石雕/油画；ImageDraw 网格绘制模拟电子显示屏（F-170~F-176、F-198~F-200） |

## 阅读路径建议

```
00-image-basics（理解 Image 类基础）
    ↓
01-resize-and-composite（创建/缩放/合成）
    ↓
02-imagedraw-drawing（绘制图形与文字）
    ↓
03-image-effects（特效：手绘/石雕/电子屏）
    ↓
examples/00-hand-drawn-effects.md（动手实践）
```

## 概念依赖关系

```
00-image-basics
    ├── 01-resize-and-composite
    ├── 02-imagedraw-drawing
    └── 03-image-effects
          ├── examples/00-hand-drawn-effects.md
          └── examples/01-electronic-display.md
```

```{toctree}
:hidden:
:maxdepth: 7

00-image-basics
01-resize-and-composite
02-imagedraw-drawing
03-image-effects
```
