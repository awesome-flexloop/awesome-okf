---
type: Reference
title: 信源登记：使用 Pillow 处理图像（简书 610cd4f0b77e）
description: 简书文章《使用 Pillow 处理图像》信源登记：URL、标题、时点与 F-128~F-140 事实清单（Image 基础与处理）
tags: [pillow, image, processing, source, jianshu]
generated: { by: "spec:jianshu-blogs-to-okf-wiki", at: "2026-09-02T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T00:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: jianshu-610cd4f0b77e
    url: https://www.jianshu.com/p/610cd4f0b77e
    title: 使用 Pillow 处理图像（水之心，2020 年前后）
---

# 信源登记：使用 Pillow 处理图像

本文登记简书文章《使用 Pillow 处理图像》的信源信息与编号事实，供本束概念与示例文档溯源使用。

## 文章信息

| 项目 | 内容 |
|------|------|
| 标题 | 使用 Pillow 处理图像 |
| URL | https://www.jianshu.com/p/610cd4f0b77e |
| 作者 | 水之心 |
| 时点 | 2020 年前后（发布于 2020-05-25，最后编辑 2020-05-25） |
| 所属连载 | matplotlib & pillow & networkx 手册（停止维护），nb/46194813 |
| 原始出处 | 翻译自 Pillow (PIL Fork) 官方文档 |

## 事实清单（F-128 ~ F-140）

- **F-128**：`Image.open('images/cat3.jpg')` 打开图片，打开成功返回 `Image` 对象，失败触发 `OSError` 异常。
- **F-129**：通过 `im.format`、`im.size`、`im.mode`、`im.width`、`im.height`、`im.getpixel((100, 100))` 获取图像信息，输出示例为 format=JPEG、size=(474, 315)、mode=RGB、getpixel((100,100))=(193, 175, 113)。
- **F-130**：`save()` 保存文件时使用文件扩展名决定存储格式，`im.save(outfile, "JPEG")` 为显式指定格式的示例。
- **F-131**：`im.thumbnail(size)` 创建缩略图，`size = (128, 128)`。
- **F-132**：`region = im.crop(box)` 提取子矩形，区域由 (左, 上, 右, 下) 四元组定义，坐标左上角为 (0, 0)。
- **F-133**：`region.transpose(Image.ROTATE_180)` 与 `im.paste(region, box)` 处理并粘贴区域。
- **F-134**：`r, g, b = im.split()` 拆分频段、`Image.merge("RGB", (b, g, r))` 合并频段。
- **F-135**：`im.resize((128, 128))` 调整大小、`im.rotate(45)` 旋转图像，rotate 参数为逆时针角度；并展示 `im.transpose(Image.FLIP_LEFT_RIGHT)`、`Image.FLIP_TOP_BOTTOM`、`Image.ROTATE_90`、`Image.ROTATE_180`、`Image.ROTATE_270` 等转置操作。
- **F-136**：`im.convert("L")` 转换模式，库支持每种受支持模式与 "L" 和 "RGB" 模式之间的转换。
- **F-137**：`im.filter(ImageFilter.DETAIL)` 应用滤波器，列出 BLUR、CONTOUR、DETAIL、EDGE_ENHANCE、EDGE_ENHANCE_MORE、EMBOSS、FIND_EDGES、SMOOTH、GaussianBlur 等滤镜。
- **F-138**：`im.point(lambda i: i * 1.2)` 对每个像素应用函数变换，并使用 `ImageEnhance.Contrast(im)` 创建调整器后调用 `enh.enhance(1.3)`。
- **F-139**：`im.seek(1)`、`im.seek(im.tell()+1)` 读取动画序列帧，序列结束时触发 `EOFError` 异常，并使用 `ImageSequence.Iterator(im)` 遍历序列。
- **F-140**：`im.draft("L", (100, 100))` 控制解码器，仅适用于 JPEG 和 MPO 文件。

## 文档引用

- 本束概念 [图像基础与处理](../concepts/00-image-basics.md) 引用本文信源。
