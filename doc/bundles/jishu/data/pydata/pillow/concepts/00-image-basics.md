---
type: Concept
title: Pillow 图像基础与处理
description: Pillow（PIL Fork）Image 类基础：打开/保存/属性查询、剪切粘贴、频段拆分合并、几何与颜色变换、滤波增强、序列读取与控制解码器
tags: [pillow, image, processing, open, save, crop, convert, filter, concept]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-610cd4f0b77e
    resource: /references/source-02.md
    title: 信源登记：使用 Pillow 处理图像（F-128~F-140）
---

# Pillow 图像基础与处理

本文基于 2020 年前后教程（简书《使用 Pillow 处理图像》，原文翻译自 Pillow (PIL Fork) 官方文档）。Pillow 是 Python Imaging Library（PIL）的分支与后继，其中最重要的类是 `Image`，定义在同名模块中。你可以通过从文件加载图像、处理其他图像或从头创建图像等途径获得 `Image` 实例。

## 一、打开图像与属性查询

从文件加载图像使用 `Image.open()`（F-128）。打开成功返回 `Image` 对象，失败触发 `OSError` 异常：

```python
from PIL import Image
im = Image.open('images/cat3.jpg')  # 打开图片
```

获得对象后可查询其信息（F-129）：

```python
print('图像的格式：', im.format)      # JPEG
print('图像的大小：', im.size)        # (474, 315)
print('图像的模式：', im.mode)        # RGB
print('图像的宽度：', im.width)       # 474
print('图像的高度：', im.height)      # 315
print('获取某个像素点的颜色值：', im.getpixel((100, 100)))  # (193, 175, 113)
```

- `format` 标识图像来源；若图像不是从文件读取，该属性为 `None`。
- `size` 是 `(宽度, 高度)` 元组（像素单位）；`mode` 定义频段的数量、名称以及像素类型与深度。常见模式：灰度图 `"L"`（luminance）、真彩色 `"RGB"`、预打印 `"CMYK"`（F-129）。

展示图像用 `im.show()`。标准版本的 `show()` 效率不高——它把图像保存到临时文件再调用外部程序显示，未安装相应程序时甚至无法工作；但它对调试与测试很方便。

## 二、读写图像

从磁盘读取用 `Image.open()`，无需预先知道文件格式，库会根据文件内容自动确定格式。保存用 `Image.save()`，除非显式指定格式，否则库用文件扩展名决定存储格式（F-130）。

转换为 JPEG 的批处理示例（F-130）：

```python
import os, sys
from PIL import Image
for infile in sys.argv[1:]:
    f, e = os.path.splitext(infile)
    outfile = f + ".jpg"
    if infile != outfile:
        try:
            with Image.open(infile) as im:
                im.save(outfile)
        except OSError:
            print("cannot convert", infile)
```

`save()` 的第二个参数可显式指定格式（`im.save(outfile, "JPEG")`）；使用非标准扩展名时必须这样指定。

## 三、剪切、粘贴与频段操作

用 `crop()` 提取子矩形，区域由 `(左, 上, 右, 下)` 四元组定义，坐标系左上角为 `(0, 0)`（F-132）：

```python
box = (100, 100, 200, 200)
region = im.crop(box)
```

处理区域后可用 `paste()` 粘贴回去（F-133）：

```python
region = region.transpose(Image.ROTATE_180)
im.paste(region, box)
```

粘贴时区域大小必须与目标框完全匹配，且不能超出图像边界；原始图像与区域的模式不必一致，不一致时区域会被自动转换（F-133）。

`split()` 把多频段图像拆成一组单频段图像，`Image.merge(mode, bands)` 把一组图像组合成新图像。例如交换 RGB 三个频段（F-134）：

```python
r, g, b = im.split()
im = Image.merge("RGB", (b, g, r))
```

注意单频段图像调用 `split()` 返回图像本身；要使用各频段通常需先转为 RGB 模式（F-134）。

## 四、几何变换

`resize()` 调整大小（参数为指定新尺寸的元组），`rotate()` 旋转（参数为逆时针角度，F-135）：

```python
out = im.resize((128, 128))
out = im.rotate(45)  # 逆时针 45 度
```

以 90 度为单位旋转或翻转用 `transpose()`（F-135）：

```python
out = im.transpose(Image.FLIP_LEFT_RIGHT)
out = im.transpose(Image.FLIP_TOP_BOTTOM)
out = im.transpose(Image.ROTATE_90)
out = im.transpose(Image.ROTATE_180)
out = im.transpose(Image.ROTATE_270)
```

`rotate()` 加 `expand=True` 可达到与 `transpose(ROTATE)` 相同的尺寸调整效果；更通用的变换用 `transform()`（F-135）。

## 五、颜色变换

用 `convert()` 在不同像素表示之间转换（F-136）：

```python
from PIL import Image
im = Image.open("hopper.ppm").convert("L")
```

库支持每种受支持模式与 `"L"`、`"RGB"` 之间的转换；要在其他模式之间转换，必须借助中间图像（通常是 `"RGB"` 模式图像）（F-136）。

## 六、滤波与增强

`ImageFilter` 模块提供可配合 `filter()` 方法使用的预定义滤波器（F-137）：

```python
from PIL import ImageFilter
out = im.filter(ImageFilter.DETAIL)
```

常用滤镜及用途（F-137）：

| 滤镜值 | 用途 |
|--------|------|
| BLUR | 模糊效果 |
| CONTOUR | 轮廓 |
| DETAIL | 细节 |
| EDGE_ENHANCE | 边缘增强 |
| EDGE_ENHANCE_MORE | 边缘增强 plus |
| EMBOSS | 浮雕效果 |
| FIND_EDGES | 寻找边缘 |
| SMOOTH | 平滑 |
| GaussianBlur | 高斯模糊 |

`point()` 可对每个像素应用一个单参数函数（常用于对比度操作，F-138）：

```python
out = im.point(lambda i: i * 1.2)  # 每个像素乘以 1.2
```

更高级的增强用 `ImageEnhance` 中的类：从图像创建调整器，再调用 `enhance()` 调整（F-138）：

```python
from PIL import ImageEnhance
enh = ImageEnhance.Contrast(im)
enh.enhance(1.3).show("30% more contrast")
```

可获取的调整器：`ImageEnhance.Color()`（颜色）、`ImageEnhance.Contrast()`（对比度）、`ImageEnhance.Brightness()`（亮度）、`ImageEnhance.Sharpness()`（清晰度）（F-138）。

## 七、图像序列

PIL 对图像序列（动画格式）提供基础支持，支持的格式含 FLI/FLC、GIF 及部分实验性格式；TIFF 文件也可含多帧。打开序列文件时自动加载第一帧，用 `seek()`/`tell()` 在不同帧间移动（F-139）：

```python
from PIL import Image

im = Image.open("animation.gif")
im.seek(1)  # 跳到第二帧
try:
    while 1:
        im.seek(im.tell()+1)
        # 对每帧做处理
except EOFError:
    pass  # 序列结束
```

序列结束时触发 `EOFError` 异常。用 `ImageSequence.Iterator` 可配合 for 语句遍历（F-139）：

```python
from PIL import ImageSequence
for frame in ImageSequence.Iterator(im):
    # ...对每帧做处理...
```

## 八、控制解码器

`draft()` 处理已打开但尚未加载的图像，使其尽可能匹配给定模式与大小，通过重新配置解码器加速解码（通常用于缩略图创建或单色打印场景）。**仅适用于 JPEG 和 MPO 文件**（F-140）：

```python
from PIL import Image
with Image.open(file) as im:
    print("original =", im.mode, im.size)
    im.draft("L", (100, 100))
    print("draft =", im.mode, im.size)
```

注意生成的图像可能与要求不完全匹配；要确保图像不大于给定尺寸，请用 `thumbnail()`（F-140）。

## 现状

本文基于 2020 年前后教程（对应 Pillow 7.x 时代），以上核心 API 在 Pillow 8.x/9.x 中保持稳定：

- `Image.open/save/crop/paste/split/merge/resize/rotate/transpose/convert/filter/point/seek/tell/draft`、`ImageFilter`、`ImageEnhance`、`ImageSequence` 等均可用。
- 兼容提示：`ttf.getsize()` 在 8.0 起被 `ImageFont.getlength()`/`getbbox()` 取代（见 [ImageDraw 绘制](02-imagedraw-drawing.md)）；`StringIO` 在 Python 3 中改用 `io.BytesIO`；`Image.open(fp)` 从文件对象读取同样可用。

## 相关概念

- /concepts/01-resize-and-composite.md — 创建、缩放与合成图像
- /concepts/02-imagedraw-drawing.md — ImageDraw 绘制图形与文字
- /concepts/03-image-effects.md — 手绘/石雕/电子屏特效
