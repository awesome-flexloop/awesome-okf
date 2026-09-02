---
type: Concept
title: Pillow 图像特效（手绘/石雕/电子屏）
description: Pillow 图像特效：用灰度梯度重构与光源模拟实现手绘/石雕/油画效果，用 ImageDraw 网格绘制模拟电子显示屏
tags: [pillow, effect, hand-drawn, engraving, oil-painting, gradient, electronic-display, concept]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-a30a6e07102b
    resource: /references/source-04.md
    title: 信源登记：Pillow 模拟图像的手绘和石雕、油画效果（F-170~F-176）
  - id: jianshu-f6b0a43023b3
    resource: /references/source-05.md
    title: 信源登记：Pillow 模拟电子显示屏（F-198~F-200）
---

# Pillow 图像特效（手绘/石雕/电子屏）

本文基于 2020 年前后教程（简书《Pillow 模拟图像的手绘和石雕、油画效果》与《Pillow 模拟电子显示屏》），介绍两类用 Pillow 实现的图像特效：一类通过灰度梯度重构与光源模拟把照片变成手绘/石雕/油画质感，另一类通过 ImageDraw 网格绘制把图片模拟为电子显示屏。

## 一、手绘效果的原理

手绘效果的特征（F-170）：

- 黑白灰色
- 边界线条较重
- 相同或相近色彩趋于白色
- 略有光源效果

实现思路分四步：梯度的重构 → 构造光源效果 → 梯度归一化 → 图像生成（F-171~F-174）。

## 二、手绘效果实现

### 步骤 1：梯度的重构

利用像素间的梯度值与虚拟深度值对图像进行重构，根据灰度变化模拟人类视觉对明暗程度的感知（F-171）：

```python
import numpy as np
from PIL import Image
im = Image.open('images/cat3.jpg')
gray = im.convert('L')              # 转灰度图

depth = 10.                          # 预设深度，取值范围 (0-100)
grad_x, grad_y = np.gradient(gray)   # 分别取 x 轴、y 轴的梯度值
grad_x = grad_x * depth/100.         # 根据深度调整 x 轴梯度值
grad_y = grad_y * depth/100.         # 根据深度调整 y 轴梯度值
```

### 步骤 2：构造光源效果

设计一个位于图像斜上方的虚拟光源，光源相对图像的视角为俯仰角（Elevation）与方位角（Azimuth），据此建立光源对各点梯度值的影响函数（F-172）：

```python
vec_el = np.pi/2.2  # 光源的俯视角度，弧度值
vec_ez = np.pi/4    # 光源的方位角度，弧度值
dx = np.cos(vec_el)*np.cos(vec_ez)  # 光影对 x 轴的影响
dy = np.cos(vec_el)*np.sin(vec_ez)  # 光影对 y 轴的影响
dz = np.sin(vec_el)                 # 光影对 z 轴的影响
```

其中 `np.cos(vec_el)` 为单位光线在地平面上的投射长度，`dx`/`dy`/`dz` 为光源对 x/y/z 三方向的影响程度（F-172）。

### 步骤 3：梯度归一化

构造 x、y 轴梯度的三维归一化单位坐标系，让梯度与光源相互作用、将梯度转化为灰度（F-173）：

```python
A = np.sqrt(grad_x**2+grad_y**2+1.)
uni_x = grad_x/A
uni_y = grad_y/A
uni_z = 1./A
```

### 步骤 4：图像生成

为避免数据溢出，把生成的灰度值裁剪至 0-255 区间，再用 `Image.fromarray` 重构图像并保存（F-174）：

```python
e = 255*(dx*uni_x + dy*uni_y + dz*uni_z)  # 光源归一化
e = e.clip(0, 255)

im = Image.fromarray(e.astype('uint8'))   # 重构图像
im.save("e.png")
```

## 三、石雕/油画效果

石雕/油画效果原理与手绘相同，区别在于对 RGB 三通道同时取梯度、并采用不同的光源参数（F-175）：

```python
import numpy as np
from PIL import Image
im = Image.open('images/cat3.jpg')

depth = 10.                              # 预设深度为 10，取值范围 (0-100)
grad_x, grad_y, grad_z = np.gradient(im)  # 分别取图像的梯度值（三通道）
grad_x = grad_x * depth/100.
grad_y = grad_y * depth/100.
grad_z = grad_z * depth/100.

A = np.sqrt(grad_x**2+grad_y**2+grad_z**2) + 1e-7  # 归一化（加极小量防除零）
uni_x = grad_x/A
uni_y = grad_y/A
uni_z = grad_z/A

vec_el = np.pi/7.2  # 光源的俯视角度，弧度值
vec_ez = np.pi/7    # 光源的方位角度，弧度值
dx = np.cos(vec_el)*np.cos(vec_ez)
dy = np.cos(vec_el)*np.sin(vec_ez)
dz = np.sin(vec_el)

e = 255*(dx*uni_x + dy*uni_y + dz*uni_z)  # 光源归一化
e = e.clip(0, 255)

im = Image.fromarray(e.astype('uint8'))   # 重构图像
im.save("e.png")
```

关键差异（F-175）：

- 手绘对灰度图（单通道）取梯度；石雕/油画对原图（RGB 三通道）取梯度，即 `np.gradient(im)` 得到三个分量 `grad_x`/`grad_y`/`grad_z`。
- 归一化分母加 `1e-7` 防除零；光源参数 `vec_el = np.pi/7.2`、`vec_ez = np.pi/7`，与手绘（`np.pi/2.2`、`np.pi/4`）不同。

修改光源影响因素可得到不同效果（F-176）。例如：

```python
dx = 2**(np.cos(vec_el)*np.cos(vec_ez))  # 光影对 x 轴的影响
dy = np.exp(np.cos(vec_el))*np.sin(vec_ez)  # 光影对 y 轴的影响
dz = np.log(np.sin(vec_el))  # 光影对 z 轴的影响
```

## 四、模拟电子显示屏

将图片以网格形式展示，模拟电子显示屏效果（F-198~F-200）：

```python
def gen_text():
    im = Image.open('70.png')
    img_draw = ImageDraw.Draw(im)

    W, H = im.size        # 读取图像宽高
    spacing = 20          # 网格间距
    row, colum = int(W / spacing), int(H / spacing)  # 网格行列数

    for i in range(row):
        for j in range(colum):
            img_draw.rectangle([i*spacing, j*spacing, (1+i)*spacing, (1+j)*spacing],
                               outline='gray', width=2)
    im.save('d.png')
```

要点（F-198~F-200）：

- `ImageDraw.Draw(im)` 在打开的图像上创建绘图对象（F-198）。
- `W, H = im.size` 读取尺寸，`spacing = 20` 设定网格间距，`row, colum = int(W/spacing), int(H/spacing)` 计算行列数（F-199）。
- 嵌套循环对每个网格用 `rectangle(..., outline='gray', width=2)` 绘制边框，最后 `im.save('d.png')` 保存（F-200）。

## 现状

本文基于 2020 年前后教程（对应 Pillow 7.x 时代），以上方法在 Pillow 8.x/9.x 中保持可用：

- 手绘/石雕效果依赖 NumPy 的 `np.gradient` 与 Pillow 的 `convert('L')`/`Image.fromarray`，二者均可用；`e.clip(0, 255)` 与 `e.astype('uint8')` 写法在 NumPy 2.x 中仍适用。
- 电子屏示例的 `ImageDraw.Draw`/`rectangle`/`save` 均可用，可直接运行。
- 效果公式属于教程给出的经典算法，`dx/dy/dz` 的修改为「光源影响因素」的演示参数，可自行调节。

## 相关概念

- /concepts/00-image-basics.md — 图像基础与处理（convert/filter 等）
- /concepts/02-imagedraw-drawing.md — ImageDraw 绘制图形与文字
- /examples/00-hand-drawn-effects.md — 手绘/石雕/油画完整示例
- /examples/01-electronic-display.md — 模拟电子显示屏完整示例
