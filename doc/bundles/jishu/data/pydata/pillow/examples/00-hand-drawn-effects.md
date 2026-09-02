---
type: Example
title: 手绘/石雕/油画特效完整示例
description: 基于 2020 年前后教程的手绘与石雕/油画特效完整示例：灰度/三通道梯度重构、虚拟光源模拟、归一化与灰度值裁剪重构图像
tags: [pillow, hand-drawn, engraving, oil-painting, gradient, light-source, example]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-a30a6e07102b
    resource: /references/source-04.md
    title: 信源登记：Pillow 模拟图像的手绘和石雕、油画效果（F-170~F-176）
---

# 手绘/石雕/油画特效完整示例

本文基于 2020 年前后教程（简书《Pillow 模拟图像的手绘和石雕、油画效果》），给出把照片转换为手绘效果、以及石雕/油画效果的完整可运行代码。手绘效果的特征是黑白灰、边界线条较重、相同或相近色彩趋于白色、略有光源效果（F-170）。

## 一、手绘效果完整代码

手绘效果分四步：梯度重构（F-171）→ 光源效果（F-172）→ 梯度归一化（F-173）→ 图像生成（F-174）：

```python
import numpy as np
from PIL import Image

# 步骤 1 梯度的重构
im = Image.open('images/cat3.jpg')
gray = im.convert('L')               # 转灰度图

depth = 10.                          # 预设深度为 10，取值范围 (0-100)
grad_x, grad_y = np.gradient(gray)   # 分别取 x 轴、y 轴的梯度值
grad_x = grad_x * depth/100.         # 根据深度调整 x，y 轴的梯度值
grad_y = grad_y * depth/100.

# 步骤 2 构造光源效果
vec_el = np.pi/2.2  # 光源的俯视角度，弧度值
vec_ez = np.pi/4    # 光源的方位角度，弧度值
dx = np.cos(vec_el)*np.cos(vec_ez)  # 光影对 x 轴的影响
dy = np.cos(vec_el)*np.sin(vec_ez)  # 光影对 y 轴的影响
dz = np.sin(vec_el)                 # 光影对 z 轴的影响

# 步骤 3 梯度归一化
A = np.sqrt(grad_x**2+grad_y**2+1.)
uni_x = grad_x/A
uni_y = grad_y/A
uni_z = 1./A

# 步骤 4 图像生成
e = 255*(dx*uni_x + dy*uni_y + dz*uni_z)  # 光源归一化
e = e.clip(0, 255)                        # 裁剪至 0-255 防止溢出

im = Image.fromarray(e.astype('uint8'))   # 重构图像
im.save("e.png")
```

## 二、石雕/油画效果完整代码

石雕/油画效果原理与手绘相同，区别在于对 RGB 三通道取梯度、归一化分母加 `1e-7` 防除零、光源参数不同（F-175）：

```python
import numpy as np
from PIL import Image

im = Image.open('images/cat3.jpg')

depth = 10.                              # 预设深度为 10，取值范围 (0-100)
grad_x, grad_y, grad_z = np.gradient(im)  # 分别取图像的梯度值（三通道）
grad_x = grad_x * depth/100.
grad_y = grad_y * depth/100.
grad_z = grad_z * depth/100.

A = np.sqrt(grad_x**2+grad_y**2+grad_z**2) + 1e-7
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

## 三、修改光源影响因素

修改 `dx`/`dy`/`dz` 的光源影响函数可以得到不同的效果（F-176）：

```python
dx = 2**(np.cos(vec_el)*np.cos(vec_ez))  # 光影对 x 轴的影响
dy = np.exp(np.cos(vec_el))*np.sin(vec_ez)  # 光影对 y 轴的影响
dz = np.log(np.sin(vec_el))  # 光影对 z 轴的影响
```

也可把 `dz` 保持为 `np.sin(vec_el)` 得到浮雕效果（F-176）：

```python
dx = 2**(np.cos(vec_el)*np.cos(vec_ez))
dy = np.exp(np.cos(vec_el))*np.sin(vec_ez)
dz = np.sin(vec_el)  # 光影对 z 轴的影响
```

## 运行要点

- 需要安装 `pillow` 与 `numpy` 两个包。
- 图片路径 `'images/cat3.jpg'` 为原文示例路径，请替换为实际图片路径。
- 输出统一保存为 `e.png`（原文如此），可自行修改文件名。

## 现状

本文基于 2020 年前后教程（对应 Pillow 7.x / NumPy 1.x 时代）：

- `Image.convert('L')`、`np.gradient`、`e.clip(0, 255)`、`e.astype('uint8')`、`Image.fromarray`、`im.save` 在 Pillow 8.x/9.x 与 NumPy 2.x 中均可直接运行。
- 手绘/石雕算法为教程给出的经典实现，参数（`depth`、`vec_el`、`vec_ez`）可按需调节。

## 相关概念

- /concepts/03-image-effects.md — 图像特效原理详解
- /concepts/00-image-basics.md — 图像基础与处理
- /examples/01-electronic-display.md — 模拟电子显示屏完整示例
