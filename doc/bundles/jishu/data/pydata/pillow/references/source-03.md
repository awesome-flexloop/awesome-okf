---
type: Reference
title: 信源登记：Pillow 之图像的缩放与合成（简书 8d5ff4ce2052）
description: 简书文章《Pillow 之图像的缩放与合成》信源登记：URL、标题、时点与 F-154~F-161 事实清单（创建/混合/缩放/合成）
tags: [pillow, resize, composite, imagechops, source, jianshu]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-8d5ff4ce2052
    url: https://www.jianshu.com/p/8d5ff4ce2052
    title: Pillow 之图像的缩放与合成（水之心，2020 年前后）
---

# 信源登记：Pillow 之图像的缩放与合成

本文登记简书文章《Pillow 之图像的缩放与合成》的信源信息与编号事实，供本束概念与示例文档溯源使用。

## 文章信息

| 项目 | 内容 |
|------|------|
| 标题 | Pillow 之图像的缩放与合成 |
| URL | https://www.jianshu.com/p/8d5ff4ce2052 |
| 作者 | 水之心 |
| 时点 | 2020 年前后（发布于 2020-05-25，最后编辑 2020-05-25） |
| 所属连载 | matplotlib & pillow & networkx 手册（停止维护），nb/46194813 |

## 事实清单（F-154 ~ F-161）

- **F-154**：通过 `Image.new(mode, size, color)` 创建图像，三个参数分别为 mode、size（width, height）、color。
- **F-155**：示例 `im = Image.new('RGB', (100, 100), 'red')`、`im.save('red.png')`。
- **F-156**：`Image.blend(im1, im2, alpha)` 透明度混合，`alpha` 为 0 时显示 im1、为 1 时显示 im2，并要求 im1 与 im2 大小相同且 mode 均为 RGB。
- **F-157**：`Image.composite(im1, im2, mask)` 遮罩混合，三个参数均为 Image 对象，示例 `im3 = Image.composite(im1, im2, b)`。
- **F-158**：`Image.eval(im, lambda x:x*2)` 对每个像素点进行函数操作。
- **F-159**：`im2.thumbnail((100, 100))` 按尺寸缩放，示例输出 `im1的大小 (474, 315)`、`im2的大小 (100, 66)`。
- **F-160**：`ImageChops.add(image1, image2, scale=1.0, offset=0)` 与 `ImageChops.subtract(image1, image2, scale=1.0, offset=0)` 运算。
- **F-161**：ImageChops 的 darker、lighter、invert、multiply、screen、difference 函数及各自计算公式：darker 为 `min(im1, im2)`、lighter 为 `max(im1, im2)`、invert 为 `max-image`、multiply 为 `im1*im2/max`、screen 为 `max-((max-im1)*(max-im2)/max)`、difference 为 `abs(im1-im2)`。

## 文档引用

- 本束概念 [缩放与合成](../concepts/01-resize-and-composite.md) 引用本文信源。
