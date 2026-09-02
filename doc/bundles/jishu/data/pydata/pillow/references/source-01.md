---
type: Reference
title: 信源登记：Pillow 绘制图形（简书 5c094689481e）
description: 简书文章《Pillow 绘制图形》信源登记：URL、标题、时点与 F-120~F-127 事实清单（ImageDraw 绘制）
tags: [pillow, imagedraw, drawing, source, jianshu]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-5c094689481e
    url: https://www.jianshu.com/p/5c094689481e
    title: Pillow 绘制图形（水之心，2020 年前后）
---

# 信源登记：Pillow 绘制图形

本文登记简书文章《Pillow 绘制图形》的信源信息与编号事实，供本束概念与示例文档溯源使用。

## 文章信息

| 项目 | 内容 |
|------|------|
| 标题 | Pillow 绘制图形 |
| URL | https://www.jianshu.com/p/5c094689481e |
| 作者 | 水之心 |
| 时点 | 2020 年前后（发布于 2020-05-25，最后编辑 2020-08-11） |
| 所属连载 | matplotlib & pillow & networkx 手册（停止维护），nb/46194813 |

## 事实清单（F-120 ~ F-127）

- **F-120**：绘制前需获取 `ImageDraw.Draw` 对象，代码为 `drawer = ImageDraw.Draw(im)`；并创建空白图片 `im = Image.new("RGB", (300, 300), "white")`。
- **F-121**：`line(xy, fill=None, width=0, joint=None)` 方法，`xy` 为起点与终点坐标 (x1, y1, x2, y2)，示例 `drawer.line((50, 50, 150, 150), fill='green', width=2)`。
- **F-122**：`rectangle(xy, fill=None, outline=None, width=0)`、`arc(xy, start, end, fill=None, width=0)`、`ellipse(xy, fill=None, outline=None, width=0)`、`chord(xy, start, end, fill=None, outline=None, width=0)`、`pieslice(xy, start, end, fill=None, outline=None, width=0)`、`polygon(xy, fill=None, outline=None)`、`point(xy, fill=None)` 等绘制方法。
- **F-123**：`text(...)` 方法签名，参数包括 `xy`、`text`、`fill`、`font`、`anchor`、`spacing=4`、`align='left'`、`direction`、`features`、`language`、`stroke_width=0`、`stroke_fill=None`。
- **F-124**：绘制中文时默认编码不支持中文会报错，代码使用 `ImageFont.truetype('simkai.ttf', 30)` 获取字体对象。
- **F-125**：使用 `ImageFont.truetype('simsun.ttc', 700)` 加载 .ttc 格式宋体字体绘制中文。
- **F-126**：使用 `ttf.getsize(chars)` 得到整个字串的宽度和高度，并用 `img_draw.rectangle(coords, outline='blue')` 框选文字区域。
- **F-127**：`drawer.text((50, 100), text="t", font=imFont, fill="red", stroke_width=5, stroke_fill='yellow')` 设置文本笔画宽度与颜色。

## 文档引用

- 本束概念 [ImageDraw 绘制](../concepts/02-imagedraw-drawing.md) 引用本文信源。
