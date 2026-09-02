---
type: Concept
title: Pillow ImageDraw 绘制图形与文字
description: Pillow ImageDraw 模块 2D 绘制：Draw 对象、line/rectangle/arc/ellipse/chord/pieslice/polygon/point、text 签名与中文字体、文字框选与笔画
tags: [pillow, imagedraw, drawing, text, imagefont, truetype, concept]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-5c094689481e
    resource: /references/source-01.md
    title: 信源登记：Pillow 绘制图形（F-120~F-127）
---

# Pillow ImageDraw 绘制图形与文字

本文基于 2020 年前后教程（简书《Pillow 绘制图形》）。`ImageDraw` 模块提供许多绘制 2D 图像的功能：既可以绘制出全新的图像，也可以在原有图像上绘制。可绘制直线、点、椭圆、矩形、弧、弦、扇形、多边形、形状与文本。

## 一、获取 Draw 对象

绘制前先获取 `ImageDraw.Draw` 对象（F-120）：

```python
from PIL import Image, ImageDraw

im = Image.new("RGB", (300, 300), "white")  # 创建 300*300 白色图片
drawer = ImageDraw.Draw(im)                  # 获取 ImageDraw.Draw 对象
```

后续绘制都使用该 `drawer` 对象完成。

## 二、绘制简单形状

各绘制方法的签名与示例（F-121、F-122）：

### 直线

`line(xy, fill=None, width=0, joint=None)`，`xy` 为起点与终点坐标 `(x1, y1, x2, y2)`（F-121）：

```python
drawer.line((50, 50, 150, 150), fill='green', width=2)
```

### 矩形

`rectangle(xy, fill=None, outline=None, width=0)`，参数同 `line`（F-122）：

```python
drawer.rectangle((50, 50, 150, 150), fill='green', outline='red', width=3)
```

### 圆弧

`arc(xy, start, end, fill=None, width=0)`，`xy` 为圆弧外接矩形的左上/右下坐标，`start`/`end` 为起止角度（F-122）：

```python
drawer.arc((50, 50, 150, 150), start=0, end=90, fill='green', width=3)
```

### 椭圆

`ellipse(xy, fill=None, outline=None, width=0)`（F-122）：

```python
drawer.ellipse((50, 50, 150, 150), fill='green', outline='red', width=3)
```

### 弦

`chord(xy, start, end, fill=None, outline=None, width=0)`（F-122）：

```python
drawer.chord((50, 50, 150, 150), start=0, end=90, fill='green', outline='red', width=3)
```

### 扇形

`pieslice(xy, start, end, fill=None, outline=None, width=0)`，参数同 `chord`（F-122）：

```python
drawer.pieslice((50, 50, 150, 150), start=0, end=90, fill='green', outline='red', width=3)
```

### 多边形

`polygon(xy, fill=None, outline=None)`，参数同 `rectangle`（F-122）：

```python
drawer.polygon((50, 50, 150, 150, 150, 200, 200, 250, 50, 50), fill='green', outline='red')
```

### 点

`point(xy, fill=None)`（F-122）：

```python
drawer.point((100, 100), fill='black')
```

## 三、绘制文字

除简单图形外，`Draw` 还可绘制文字。`text()` 方法签名（F-123）：

```python
text(
    xy,
    text,
    fill=None,
    font=None,
    anchor=None,
    spacing=4,
    align='left',
    direction=None,
    features=None,
    language=None,
    stroke_width=0,
    stroke_fill=None,
    *args,
    **kwargs,
)
```

关键参数：`xy` 为文字区域左上角位置；`text` 为文字内容；`fill` 为文本填充颜色；`font` 为字体；`stroke_width` 为文本笔划宽度；`stroke_fill` 为笔划颜色（F-123）。

```python
drawer.text((100, 100), text='zack', fill='red')
```

### 绘制中文

绘制中文时默认编码不支持中文会报错，需用 `ImageFont.truetype()` 加载中文字体（F-124）：

```python
from PIL import Image, ImageDraw, ImageFont

im = Image.new("RGB", (300, 300), "white")
drawer = ImageDraw.Draw(im)
imFont = ImageFont.truetype('simkai.ttf', 30)  # 'Dengl.ttf' 也是中文字体
drawer.text((50, 100), text="啥", font=imFont, fill="red")
im.show()
```

Windows 上中文字体名称一般是 `.ttc` 格式（如"宋体"），可用 `ImageFont.truetype('simsun.ttc', 700)` 加载（F-125）：

```python
im = Image.new("RGB", (1920, 1080), "white")
drawer = ImageDraw.Draw(im)
imFont = ImageFont.truetype('simsun.ttc', 700)
drawer.text((600, 200), text="80", font=imFont, fill="red")
```

### 将文字区域框选出来

用 `ttf.getsize(chars)` 得到整个字串的宽度与高度，再配合 `rectangle()` 框选文字区域（F-126）：

```python
from PIL import Image, ImageDraw, ImageFont

chars = "你好啊!"
ttf_path = 'simsun.ttc'  # 宋体
chars_x, chars_y = 50, 80

image = Image.new("RGB", (1920, 1080), "white")
ttf = ImageFont.truetype(ttf_path, 50)
chars_w, chars_h = ttf.getsize(chars)  # 得到整个字串的宽度和高度
img_draw = ImageDraw.Draw(image)
coords = (chars_x, chars_y, chars_x+chars_w, chars_y+chars_h)

img_draw.rectangle(coords, outline='blue')
img_draw.text((chars_x, chars_y), chars, font=ttf, fill='red')
```

### 改变文本笔画的大小与颜色

`stroke_width` 与 `stroke_fill` 设置笔划宽度与颜色（F-127）：

```python
im = Image.new("RGBA", (600, 300), (0, 0, 0, 100))
drawer = ImageDraw.Draw(im)
imFont = ImageFont.truetype('simkai.ttf', 100)
drawer.text((50, 100), text="t", font=imFont, fill="red", stroke_width=5, stroke_fill='yellow')
```

## 现状

本文基于 2020 年前后教程（对应 Pillow 7.x 时代），绘制 API 在 Pillow 8.x/9.x 中保持稳定：

- `ImageDraw.Draw` 及 `line/rectangle/arc/ellipse/chord/pieslice/polygon/point/text`、`ImageFont.truetype`、`stroke_width`/`stroke_fill` 均可用。
- 兼容提示：`ImageFont.truetype` 自 8.0 起要求在 `set_variation_by_name` 等特性时注意字体对象；`ttf.getsize()` 自 8.0 起被弃用，改用 `ttf.getlength()`（单行宽度）与 `ttf.getbbox()`（边界框）替代——若需复现原文的框选示例，可把 `chars_w, chars_h = ttf.getsize(chars)` 替换为 `chars_w, chars_h = ttf.getlength(chars), ttf.getbbox(chars)[3]`。
- 中文渲染依赖系统字体（Windows 自带 `simkai.ttf`/`simsun.ttc`）；在 Linux/macOS 环境需替换为相应中文字体路径。

## 相关概念

- /concepts/00-image-basics.md — 图像基础与处理（Image.new 创建画布）
- /examples/01-electronic-display.md — 模拟电子显示屏（网格绘制）
- /examples/00-hand-drawn-effects.md — 手绘/石雕/油画特效示例
