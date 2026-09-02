---
type: Concept
title: Pillow 图像的缩放与合成
description: Pillow 创建图像与缩放合成：Image.new 创建、blend 透明度混合、composite 遮罩混合、eval 按像素操作、thumbnail 按尺寸缩放、ImageChops 通道运算
tags: [pillow, resize, composite, blend, imagechops, thumbnail, concept]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-8d5ff4ce2052
    resource: /references/source-03.md
    title: 信源登记：Pillow 之图像的缩放与合成（F-154~F-161）
---

# Pillow 图像的缩放与合成

本文基于 2020 年前后教程（简书《Pillow 之图像的缩放与合成》），介绍 Pillow 中创建图像、混合、缩放与合成的常用方法。

## 一、创建图像

用 `Image.new(mode, size, color)` 创建图像，三个参数分别为模式、大小 `(width, height)`、颜色（F-154）：

```python
from PIL import Image
im = Image.new('RGB', (100, 100), 'red')
im.save('red.png')  # 保存这个图像
```

`Image.new` 是创建空白/纯色图像的入口，常作为绘制（见 [ImageDraw 绘制](02-imagedraw-drawing.md)）与合成的起点（F-155）。

## 二、图像混合

### 透明度混合

`Image.blend(im1, im2, alpha)` 按透明度混合两张图像（F-156）：

- `im1`：混合过程中透明度为 `(1-alpha)` 的图像
- `im2`：混合过程中透明度为 `alpha` 的图像
- `alpha`：透明度，取值 0-1。为 0 时显示 `im1`，为 1 时显示 `im2`

注意：`im1` 与 `im2` 的大小必须一致，且 `mode` 均为 RGB（F-156）：

```python
from PIL import Image
im1 = Image.open('images/cat3.jpg')
im2 = Image.new('RGB', im1.size, 'red')  # 创建与 im1 同尺寸的图像
Image.blend(im1, im2, 0.5).show()
```

### 遮罩混合

`Image.composite(im1, im2, mask)` 用 `mask` 混合 `im1` 与 `im2`，三个参数均为 `Image` 对象，大小必须一致（F-157）：

```python
from PIL import Image
im1 = Image.open('images/1.jpg')
im2 = Image.open('images/cat3.jpg')
im2 = im2.resize(im1.size)     # 重新设置 im2 大小
r, g, b = im2.split()          # 将图像 2 的三个色道分离
im3 = Image.composite(im1, im2, b)  # 用 b 频段作为遮罩混合
```

## 三、图像缩放

### 按像素缩放

`Image.eval(im, fun)` 对图像中每个像素点应用函数 `fun` 的操作（F-158）：

```python
from PIL import Image
im = Image.open('images/cat3.jpg')
im1 = Image.eval(im, lambda x: x*2)  # 每个像素点 *2
```

### 按尺寸缩放

`Image` 实例的 `thumbnail(size)` 方法按尺寸缩放，直接作用于实例本身（F-159）：

```python
from PIL import Image
im1 = Image.open('images/cat3.jpg')
im2 = im1.copy()                 # 复制图像
im2.thumbnail((100, 100))        # 缩放，传入元组
print("im1的大小", im1.size)      # (474, 315)
print('im2的大小', im2.size)      # (100, 66)
```

`thumbnail()` 等比缩放，不会使图像变形（F-159）。

## 四、图像合成（ImageChops）

`ImageChops` 模块提供许多图像合成方法，通过计算通道中的像素值实现（F-160）：

### 加法运算

`ImageChops.add(image1, image2, scale=1.0, offset=0)`（F-160）：

```python
from PIL import Image, ImageChops
im = Image.open('images/1.jpg')
im1 = Image.open('images/cat3.jpg')
im1 = im1.resize(im.size)        # 重新设置 im1 大小
im2 = ImageChops.add(im, im1)
```

### 减法运算

`ImageChops.subtract(image1, image2, scale=1.0, offset=0)`，用法与 `add` 一致（F-160）：

```python
from PIL import Image, ImageChops
im = Image.open('images/1.jpg')
im1 = Image.open('images/cat3.jpg')
im1 = im1.resize(im.size)
im2 = ImageChops.subtract(im, im1)
```

### 其它函数

ImageChops 的其余常用函数及各自计算公式（F-161）：

| 函数名 | 参数 | 作用 | 计算公式 |
|--------|------|------|----------|
| darker（变暗） | (image1, image2) | 取两张图对应像素的较小值（去亮留暗） | `min(im1, im2)` |
| lighter（变亮） | (image1, image2) | 取两张图对应像素的较大值（去暗留亮） | `max(im1, im2)` |
| invert（反色） | (image) | 用 max(255) 减去每个像素值 | `max-image` |
| multiply（叠加） | (image1, image2) | 两张图互相叠加；与黑色叠加得到黑图 | `im1*im2/max` |
| screen（屏幕） | (image1, image2) | 先反色后叠加 | `max-((max-im1)*(max-im2)/max)` |
| difference（比较） | (image1, image2) | 各像素做减法取绝对值；像素相同结果为黑色 | `abs(im1-im2)` |

## 现状

本文基于 2020 年前后教程（对应 Pillow 7.x 时代），以上 API 在 Pillow 8.x/9.x 中保持稳定：

- `Image.new/blend/composite/eval`、`ImageChops.add/subtract/darker/lighter/invert/multiply/screen/difference` 均可用。
- 兼容提示：`Image.blend` 在 8.x 起支持更多模式（不止 RGB）；`thumbnail()` 的 `reduce_gfactor` 优化在 8.x 可用，但基础用法不变。

## 相关概念

- /concepts/00-image-basics.md — 图像基础与处理（open/save/convert/filter 等）
- /concepts/02-imagedraw-drawing.md — ImageDraw 绘制图形与文字
- /examples/00-hand-drawn-effects.md — 手绘/石雕/油画特效示例
