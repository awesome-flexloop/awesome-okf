---
type: Reference
title: 信源登记：Pillow 模拟图像的手绘和石雕、油画效果（简书 a30a6e07102b）
description: 简书文章《Pillow 模拟图像的手绘和石雕、油画效果》信源登记：URL、标题、时点与 F-170~F-176 事实清单（手绘/石雕/油画特效）
tags: [pillow, hand-drawn, engraving, oil-painting, effect, source, jianshu]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-a30a6e07102b
    url: https://www.jianshu.com/p/a30a6e07102b
    title: Pillow 模拟图像的手绘和石雕、油画效果（水之心，2020 年前后）
---

# 信源登记：Pillow 模拟图像的手绘和石雕、油画效果

本文登记简书文章《Pillow 模拟图像的手绘和石雕、油画效果》的信源信息与编号事实，供本束概念与示例文档溯源使用。

## 文章信息

| 项目 | 内容 |
|------|------|
| 标题 | Pillow 模拟图像的手绘和石雕、油画效果 |
| URL | https://www.jianshu.com/p/a30a6e07102b |
| 作者 | 水之心 |
| 时点 | 2020 年前后（发布于 2020-05-26，最后编辑 2020-05-26） |
| 所属连载 | matplotlib & pillow & networkx 手册（停止维护），nb/46194813 |

## 事实清单（F-170 ~ F-176）

- **F-170**：手绘效果特征为黑白灰色、边界线条较重、相同或相近色彩趋于白色、略有光源效果。
- **F-171**：手绘代码使用 `im.convert('L')` 转为灰度图，`grad_x, grad_y = np.gradient(gray)` 取灰度梯度值，`depth = 10.` 预设深度，梯度值乘以 `depth/100.`。
- **F-172**：手绘代码设置光源参数 `vec_el = np.pi/2.2`、`vec_ez = np.pi/4`，`dx = np.cos(vec_el)*np.cos(vec_ez)`、`dy = np.cos(vec_el)*np.sin(vec_ez)`、`dz = np.sin(vec_el)`。
- **F-173**：手绘代码做梯度归一化 `A = np.sqrt(grad_x**2+grad_y**2+1.)`、`uni_x = grad_x/A`、`uni_y = grad_y/A`、`uni_z = 1./A`。
- **F-174**：手绘代码计算 `e = 255*(dx*uni_x + dy*uni_y + dz*uni_z)`，执行 `e = e.clip(0, 255)`，用 `Image.fromarray(e.astype('uint8'))` 重构图像并 `im.save("e.png")`。
- **F-175**：石雕/油画代码使用 `grad_x, grad_y, grad_z = np.gradient(im)` 对 RGB 三通道取梯度，归一化使用 `A = np.sqrt(grad_x**2+grad_y**2+grad_z**2) + 1e-7`，光源参数 `vec_el = np.pi/7.2`、`vec_ez = np.pi/7`。
- **F-176**：文章展示修改光源影响因素的代码：`dx = 2**(np.cos(vec_el)*np.cos(vec_ez))`、`dy = np.exp(np.cos(vec_el))*np.sin(vec_ez)`、`dz = np.log(np.sin(vec_el))`。

## 文档引用

- 本束概念 [图像特效](../concepts/03-image-effects.md) 与示例 [手绘石雕油画](../examples/00-hand-drawn-effects.md) 引用本文信源。
