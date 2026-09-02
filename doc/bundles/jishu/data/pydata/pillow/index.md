---
okf_version: "0.2"
---

# Pillow 图像处理知识库

本知识包是 [Pillow](https://python-pillow.org)（Python Imaging Library，PIL 的分支与后继，Python 生态最常用的图像处理库）的入门知识包，基于 2020 年前后简书连载《matplotlib & pillow & networkx 手册(停止维护)》中 5 篇 Pillow 相关文章生成，覆盖图像基础与处理、图像的缩放与合成、ImageDraw 绘制图形与文字、以及手绘/石雕/电子屏图像特效四部分内容。所有内容均溯源至编号事实（spec:jianshu-blogs-to-okf-wiki 的 facts.md，F-120~F-127、F-128~F-140、F-154~F-161、F-170~F-176、F-198~F-200），遵循 [OKF v0.2 规范](https://github.com/awesome-flexloop/awesome-okf)。

## 入门基础（concepts/）

* [图像基础与处理](concepts/00-image-basics.md) — `Image` 类基础：open/save/属性查询、crop/paste、split/merge、resize/rotate/transpose、convert、filter/point/ImageEnhance、序列读取与 draft 控制解码器。
* [缩放与合成](concepts/01-resize-and-composite.md) — `Image.new` 创建、blend 透明度混合、composite 遮罩混合、eval 按像素操作、thumbnail 按尺寸缩放、ImageChops 通道运算。
* [ImageDraw 绘制](concepts/02-imagedraw-drawing.md) — `ImageDraw.Draw` 与 line/rectangle/arc/ellipse/chord/pieslice/polygon/point、text 签名、中文字体 truetype、文字框选与笔画。
* [图像特效](concepts/03-image-effects.md) — 灰度梯度重构+光源模拟实现手绘/石雕/油画；ImageDraw 网格绘制模拟电子显示屏。

## 实战示例（examples/）

* [手绘/石雕/油画特效](examples/00-hand-drawn-effects.md) — 完整可运行的手绘与石雕/油画特效：灰度/三通道梯度重构、虚拟光源模拟、归一化与灰度值裁剪重构图像。
* [模拟电子显示屏](examples/01-electronic-display.md) — 完整可运行的电子屏模拟：读取图像尺寸、按间距计算行列数、嵌套循环绘制网格并保存。

## 信源登记簿（references/）

* [信源索引](references/index.md) — 5 篇简书文章信源登记概览。
* [source-01](references/source-01.md) — 《Pillow 绘制图形》（F-120~F-127，2020 年前后）。
* [source-02](references/source-02.md) — 《使用 Pillow 处理图像》（F-128~F-140，2020 年前后）。
* [source-03](references/source-03.md) — 《Pillow 之图像的缩放与合成》（F-154~F-161，2020 年前后）。
* [source-04](references/source-04.md) — 《Pillow 模拟图像的手绘和石雕、油画效果》（F-170~F-176，2020 年前后）。
* [source-05](references/source-05.md) — 《Pillow 模拟电子显示屏》（F-198~F-200，2020 年前后）。

## 学习路径建议

1. **入门**：concepts/00-image-basics.md → concepts/01-resize-and-composite.md → concepts/02-imagedraw-drawing.md
2. **特效进阶**：concepts/03-image-effects.md → 运行 examples/00-hand-drawn-effects.md → examples/01-electronic-display.md
3. **溯源**：阅读 references/source-01~05.md，结合编号事实核对 API 用法

## 信任与生命周期说明

* **status 判定依据**：全部内容文档均 `status: stable`，基于 2020 年前后教程，引用编号事实 F-120~F-127、F-128~F-140、F-154~F-161、F-170~F-176、F-198~F-200。
* **stale_after 解释**：统一设置为 `2026-12-31`。教程对应 Pillow 7.x 时代，核心 API（Image 基础、缩放合成、ImageDraw 绘制）在 8.x/9.x 中保持兼容；该日期作为对旧教程时效性的保守重新评估节点。
* **核验链路**：`generated.at` 与 `verified.at` 均记录为 2026-09-02T00:00:00Z（spec:jianshu-blogs-to-okf-wiki 生成、process:seven-concepts-v 核验）；概念/示例文档均给出「现状」标注过时 API（如 `ttf.getsize()` 自 8.0 弃用）。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
