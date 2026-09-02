# Pillow Bundle 变更日志

## 2026-09-02 — 初始版本（基于 2020 年前后简书连载教程）

- 基于简书连载《matplotlib & pillow & networkx 手册(停止维护)》中 5 篇 Pillow 文章生成
- 覆盖 4 个概念文档 + 2 个示例文档 + 5 个信源登记文档
- 全部内容引用编号事实（spec:jianshu-blogs-to-okf-wiki 的 facts.md，F-120~F-127、F-128~F-140、F-154~F-161、F-170~F-176、F-198~F-200），无 facts 之外的事实
- 信源：source-01（绘制图形，F-120~F-127）、source-02（处理图像，F-128~F-140）、source-03（缩放与合成，F-154~F-161）、source-04（手绘石雕油画，F-170~F-176）、source-05（电子显示屏，F-198~F-200）
- 过时 API 处理：文档标注「本文基于 2020 年前后教程」（对应 Pillow 7.x 时代），对 `ttf.getsize()` 自 8.0 弃用、`Image.blend` 模式限制放宽等给出「现状」说明
- 本批次文档 `stale_after` 设为 2026-12-31（旧教程时效性保守节点）
