---
okf_version: "0.2"
type: bundles-index
title: "3Blue1Brown 生态"
description: "3Blue1Brown完整开源生态源码中文教程——ManimGL数学动画引擎、视频场景源码、字幕自动化工具链、React现代官网架构"
total_bundles: 4
---

# 3Blue1Brown 生态（3Blue1Brown Ecosystem）

3Blue1Brown（Grant Sanderson）是全球知名的数学教育YouTube频道，以精美的数学可视化动画闻名。本分组提供3Blue1Brown四个核心开源仓库的源码级中文教程，覆盖动画引擎、视频制作、字幕处理、官网构建的完整技术栈。

## 生态关系概览

```
┌──────────────────────────────────────────────────────────────┐
│                  🔵 3Blue1Brown 生态栈                         │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                  内容发布层                              │  │
│  │              3blue1brown-com (官网前端)                  │  │
│  │     React Router v7 SSG · Tailwind v4 · MDX · MathJax   │  │
│  └───────────────────────▲────────────────────────────────┘  │
│                          │ 内容承载                            │
│  ┌───────────────────────┴────────────────────────────────┐  │
│  │                  工具链层                               │  │
│  │              caption-ops (字幕自动化)                   │  │
│  │  faster-whisper转录 · 多后端翻译 · Levenshtein对齐 · SRT │  │
│  └───────────────────────▲────────────────────────────────┘  │
│                          │ 字幕生成                            │
│  ┌───────────────────────┴────────────────────────────────┐  │
│  │                  内容制作层                              │  │
│  │                  videos (视频场景)                      │  │
│  │  PiCreature · checkpoint_paste · 叙事化Scene · 系列解析  │  │
│  └───────────────────────▲────────────────────────────────┘  │
│                          │ 动画渲染                            │
│  ┌───────────────────────┴────────────────────────────────┐  │
│  │                  底层引擎层                              │  │
│  │                  manim (ManimGL动画引擎)                 │  │
│  │     Mobject · Animation · Scene · Camera · OpenGL GPU   │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

## 知识包导航

### 底层引擎

| 知识包 | 简介 |
|--------|------|
| [manim](manim/index.md) | ManimGL数学动画引擎——Mobject对象模型、Animation动画系统、Scene场景管理、Camera摄像机、OpenGL GPU渲染管线 |

### 内容制作

| 知识包 | 简介 |
|--------|------|
| [videos](videos/index.md) | 视频场景源码——PiCreature角色系统、checkpoint_paste交互工作流、叙事化Scene设计、线性代数/微积分/神经网络等经典系列解析 |

### 工具链

| 知识包 | 简介 |
|--------|------|
| [caption-ops](caption-ops/index.md) | 字幕自动化工具集——faster-whisper语音转录、多后端翻译接口、Levenshtein文本对齐、SRT智能分段与时间轴校正 |

### 内容发布

| 知识包 | 简介 |
|--------|------|
| [3blue1brown-com](3blue1brown-com/index.md) | 官网前端架构——React Router v7 SSG静态站点生成、Tailwind v4原子化CSS、MDX双阶段数学渲染、Custom Elements视频播放器、Jotai原子状态管理 |

## 推荐学习路径

```
manim (先学引擎API：Mobject/Animation/Scene/Camera核心抽象)
    → videos (再学叙事技巧：场景组织、角色设计、动画编排，注意老版本API差异)
    → caption-ops (字幕工具链按需学习：转录、翻译、对齐、分段)
    → 3blue1brown-com (前端架构独立学习：React现代栈、MDX、数学渲染)
```

## 版本信息

- **文档生成日期**：2026-08-26
- **源码来源**：https://github.com/3b1b
- **许可证**：各项目采用 MIT 或其他开源许可（详见各 bundle）

```{toctree}
:hidden:
:maxdepth: 7

manim/index
videos/index
caption-ops/index
3blue1brown-com/index
```
