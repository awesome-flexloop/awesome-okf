---
type: Concept
title: 四大图像类：QPixmap / QImage / QPicture / QBitmap
description: Qt 四种绘图设备的分工：屏幕显示优化、像素级 I/O、绘制命令序列化、单色位图，及选型决策
tags: [QPixmap, QImage, QPicture, QBitmap, 图像处理]
generated: { by: "blog-article-to-okf-wiki", at: "2026-09-02T12:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-02T12:00:00+08:00" }
status: stable
stale_after: 2027-09-02
sources:
  - id: jianshu-qt-article-source
    resource: /references/article-source.md
    title: 简书文集事实登记（F-001 ~ F-111）
  - id: qt-official-docs
    resource: https://doc.qt.io/qtforpython-6/
    title: Qt for Python 官方文档
---

# 四大图像类：QPixmap / QImage / QPicture / QBitmap

Qt 提供四个常用图像/绘图设备类，初学者极易混淆。官方文档对它们的定位有明确分工（F-105）：

## 对比总表

| 类 | 本质 | 平台相关性 | 典型用途 |
|----|------|-----------|----------|
| **QPixmap** | 为**屏幕显示**优化的图像（后台可走 GPU/平台原生） | 相关（后端随平台/Qt 版本变化） | 界面中显示图片、图标、双缓冲绘图 |
| **QImage** | 为 **I/O 与像素级访问**设计的图像 | **无关**（像素数据可直接读写） | 图像加载/保存、逐像素处理、算法处理、跨线程绘制 |
| **QPicture** | **绘制命令的序列化记录**（矢量回放设备） | 无关 | 记录 QPainter 命令并重放，分辨率无关 |
| **QBitmap** | 1-bit 深度的**单色** QPixmap | 相关 | 蒙板、光标、透明遮罩 |

## 选型决策

1. **要在 QLabel/界面上显示图片** → `QPixmap`（`QLabel.setPixmap()`）；
2. **要读像素、改像素、做图像算法**（如抠图、滤镜）→ `QImage`（`pixel()`/`setPixel()`/`bits()`）；
3. **要把一段绘制过程存下来反复回放/缩放不失真** → `QPicture`（`painter.begin(picture)` 记录，`play(painter)` 回放）；
4. **要做形状遮罩/单色图标** → `QBitmap`。

## 常见操作

```python
# QPixmap 显示
pix = QPixmap(":/images/logo.png")   # 资源路径（见资源系统）
label.setPixmap(pix)

# QImage 像素处理
img = QImage("photo.png")
for y in range(img.height()):
    for x in range(img.width()):
        c = img.pixelColor(x, y)     # 读像素
        img.setPixelColor(x, y, c.darker(200))  # 写像素

# QPixmap <-> QImage 可互转
qimg = pix.toImage()
pix2 = QPixmap.fromImage(qimg)
```

> 经验法则：**后台线程里不能碰 QPixmap/GUI 类**，图像加载与像素处理放工作线程时用 `QImage`，回到主线程再转 `QPixmap` 显示。

## 可运行示例

- [示例 21：QT 三大绘图类 QPixmap/QImage/QPicture](../examples/21-7b24c91eaa7a.md)：三类对比总览
- [示例 25：Qt 之 QPixmap](../examples/25-5d3022759b07.md)
- [示例 23：Qt 之 QImage](../examples/23-3bc6fc175403.md)
- [示例 22：Qt 之 QPicture](../examples/22-676d63c24f41.md)
- [示例 24：Qt 之 QBitmap](../examples/24-b1302780e909.md)

## 事实溯源

F-105（Qt 6 绘图系统官方文档核验），详见 [verification](../references/verification.md) 第 6 项。
