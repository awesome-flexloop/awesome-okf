---
type: Concept
title: "HyperFrames：HTML 即视频工程"
description: "以 HTML/CSS/动画为源文件，逐帧渲染 MP4，把视频制作纳入 Git、CI 和 Agent 工作流"
tags: [HyperFrames, HTML, 视频工程, Agent]
generated: { by: "process:seven-concepts-e", at: "2026-09-20" }
verified: { by: "process:seven-concepts-v", at: "2026-09-20" }
status: flagged
stale_after: 2026-11-30
sources:
  - { id: article, resource: "/references/article-source.md" }
  - { id: github, resource: "https://github.com/heygen-com/hyperframes" }
---

# HyperFrames：HTML 即视频工程

HyperFrames 将 HTML、CSS、媒体和可寻址动画作为视频源，逐帧在浏览器中渲染，再由 FFmpeg 编码 MP4。[F-011][F-013] 这让 Agent 可以用熟悉的网页结构生产可版本管理的视频，而不是依赖不可审查的时间轴工程文件。

## 典型回路

`init` 创建项目，`preview` 浏览器热预览，`lint` 检查合成，`render` 输出 MP4。[F-012] GSAP、Lottie、CSS 和 Three.js 等动画运行时通过适配器接入；确定性是框架目标，但外部媒体、字体和浏览器版本仍可能影响产物。[F-013]

项目采用 Apache-2.0，本地渲染可避免按次托管费；云渲染仍会产生云或厂商成本，4K、60fps 和 HDR 会把 CPU、时间与存储开销推高。[F-014][F-015]

## 适用边界

适合代码化、批量化、可审查的视频内容；不等于 After Effects 的设计师工作流平替，也不保证每次环境变化后生成字节完全相同。
