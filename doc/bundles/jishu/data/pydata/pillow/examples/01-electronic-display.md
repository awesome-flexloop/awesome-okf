---
type: Example
title: 模拟电子显示屏完整示例
description: 基于 2020 年前后教程的电子显示屏模拟完整示例：ImageDraw 读取图像尺寸、按间距计算行列数、嵌套循环绘制网格并保存
tags: [pillow, imagedraw, electronic-display, grid, rectangle, example]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-f6b0a43023b3
    resource: /references/source-05.md
    title: 信源登记：Pillow 模拟电子显示屏（F-198~F-200）
---

# 模拟电子显示屏完整示例

本文基于 2020 年前后教程（简书《Pillow 模拟电子显示屏》），把图片以网格形式展示，模拟电子显示屏效果。核心思路：读取图片尺寸，按固定间距计算网格行列数，再用 `ImageDraw.rectangle` 对每个网格绘制边框（F-198~F-200）。

## 一、完整代码

```python
def gen_text():
    im = Image.open('70.png')           # 打开图片
    img_draw = ImageDraw.Draw(im)       # 创建绘图对象

    W, H = im.size                      # 读取图像宽高
    spacing = 20                        # 网格间距

    row, colum = int(W / spacing), int(H / spacing)  # 网格行列数

    for i in range(row):
        for j in range(colum):
            img_draw.rectangle([i*spacing, j*spacing, (1+i)*spacing, (1+j)*spacing],
                               outline='gray', width=2)
    im.save('d.png')                    # 保存结果
```

## 二、代码要点

- `Image.open('70.png')` 打开图片，`ImageDraw.Draw(im)` 在图像上创建绘图对象（F-198）。
- `W, H = im.size` 读取宽高；`spacing = 20` 设定网格间距；`row, colum = int(W/spacing), int(H/spacing)` 计算行列数（F-199）。
- 嵌套循环对每个网格调用 `img_draw.rectangle([i*spacing, j*spacing, (1+i)*spacing, (1+j)*spacing], outline='gray', width=2)` 绘制边框，最后 `im.save('d.png')` 保存（F-200）。

## 运行要点

- 需要安装 `pillow` 包。
- 图片路径 `'70.png'` 与网格间距 `spacing = 20` 为原文示例设置，可按需调整；间距越小网格越密、电子屏效果越明显。
- 输出文件名为 `d.png`（原文如此），可自行修改。

## 现状

本文基于 2020 年前后教程（对应 Pillow 7.x 时代）：

- `Image.open`、`ImageDraw.Draw`、`im.size`、`img_draw.rectangle`、`im.save` 在 Pillow 8.x/9.x 中均可直接运行。
- 该示例只用到基础绘制 API，无过时写法，代码可直接复现。

## 相关概念

- /concepts/03-image-effects.md — 图像特效原理详解（含电子屏网格绘制）
- /concepts/02-imagedraw-drawing.md — ImageDraw 绘制图形与文字
- /examples/00-hand-drawn-effects.md — 手绘/石雕/油画特效完整示例
