---
type: Reference
title: 信源登记：Pillow 模拟电子显示屏（简书 f6b0a43023b3）
description: 简书文章《Pillow 模拟电子显示屏》信源登记：URL、标题、时点与 F-198~F-200 事实清单（网格绘制）
tags: [pillow, imagedraw, electronic-display, grid, source, jianshu]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-f6b0a43023b3
    url: https://www.jianshu.com/p/f6b0a43023b3
    title: Pillow 模拟电子显示屏（水之心，2020 年前后）
---

# 信源登记：Pillow 模拟电子显示屏

本文登记简书文章《Pillow 模拟电子显示屏》的信源信息与编号事实，供本束概念与示例文档溯源使用。

## 文章信息

| 项目 | 内容 |
|------|------|
| 标题 | Pillow 模拟电子显示屏 |
| URL | https://www.jianshu.com/p/f6b0a43023b3 |
| 作者 | 水之心 |
| 时点 | 2020 年前后（发布于 2020-05-26，最后编辑 2020-05-26） |
| 所属连载 | matplotlib & pillow & networkx 手册（停止维护），nb/46194813 |

## 事实清单（F-198 ~ F-200）

- **F-198**：代码定义 `gen_text()` 函数，使用 `Image.open('70.png')` 打开图片，`ImageDraw.Draw(im)` 创建绘图对象。
- **F-199**：代码读取 `W, H = im.size`，设置 `spacing = 20`，计算 `row, colum = int(W / spacing), int(H / spacing)`。
- **F-200**：代码嵌套循环调用 `img_draw.rectangle([i*spacing, j*spacing, (1+i)*spacing, (1+j)*spacing], outline='gray', width=2)` 绘制网格，并以 `im.save('d.png')` 保存图像。

## 文档引用

- 本束概念 [图像特效](../concepts/03-image-effects.md) 与示例 [模拟电子显示屏](../examples/01-electronic-display.md) 引用本文信源。
