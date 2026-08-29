# 01 组件目录

> ThreeUI 的分类体系、六大核心组件类型与代表效果。

## 分类体系

博文称官方划分 10 个分类（F-010）：

1. Landing Pages
2. Hero
3. Three.js
4. Motion Design
5. Sections
6. Backgrounds
7. Buttons
8. Text Animation
9. UI Elements
10. CSS

> ⚠️ **核验勘误（F-041）**：官网 threeui.com/browse 当前显示 **9 个分类**，"Sections"分类访问返回"No components match this category."。Sections 可能是计划中但尚未上线、已被移除或合并。

## 六大核心组件类型

### 1. Landing Page / Hero

ThreeUI 最吸睛的是完整页面和 Hero 区域组件，已包含完整布局、滚动、交互甚至 Three.js 场景（F-011）。

**代表效果**：

| 效果 | 描述 |
|------|------|
| **Kage** | 日式寺庙主题完整交互页面，含夜景、灯笼、樱花和 3D 场景，保留鼠标、键盘、滚动和导航交互（F-020） |
| Complete Shelf | 完整书架展示页面 |
| Bestsellers Book Showcase | 畅销书展示 |

> 📝 博文评论：以前看到这种网站第一反应是"这得写多久？"，现在可以直接从完整效果开始改（F-011）。

### 2. Three.js 3D 场景

ThreeUI 的核心部分，Camera、Light、Material、Animation 等基础工作很多已封装好（F-012）。

**代表效果**：Temple Night、Japanese Tower、Bookshelf、Globe、Orbital Sphere、Landscape

**适用产品**（F-013）：
- AI 官网
- SaaS 产品
- 作品集
- Web3
- 开发者工具

这些产品的 Hero 区域很多可以直接从这里找灵感。

### 3. Shader / 动态背景

> 📝 "如果你喜欢现在 AI 产品官网那种炫酷背景，这一类基本够玩了。"（F-014）

**代表效果**：

| 效果 | 风格 |
|------|------|
| Liquid Form | 流体变形 |
| Dot Matrix | 点阵 |
| Warp Field | 空间扭曲 |
| Nebula Background | 星云 |
| Particle Network | 粒子网络 |
| Flux Vortex | 通量漩涡 |

流体、粒子、星云、点阵、空间扭曲全覆盖。很多效果直接放首屏背景就能明显提升页面质感（F-021）。

### 4. Buttons

连按钮都开始卷 Shader 了（F-015）。

**代表效果**：Liquid Metal Button、Plasma Button、Thinking Button、Glassmorphism CTA、Gradient Beam CTA

> 📝 已经远远超过传统 CSS Hover 的感觉——流体、金属、玻璃、光效、渐变、粒子全塞进一个按钮里（F-015）。

### 5. Text Animation

文字动画支持粒子化、变形、沿路径运动，特别适合产品 Logo、Hero 标题、品牌展示（F-016）。

**代表效果**：Typography Vortex、Morphing Glyph Cloud、Particle Wordmark、Neon Typography

> 📝 以前这种效果大概率要自己折腾 GSAP + Canvas + Shader，现在可以直接拿现成实现（F-017）。

### 6. UI Elements

更适合直接塞进业务页面的小组件（F-018）：

| 效果 | 类型 |
|------|------|
| Genie Dock | Dock 栏 |
| Animated Top Dock | 顶部 Dock |
| Gallery | 画廊 |
| Uplink Loader | 加载动画 |
| Performance Gauges | 仪表盘 |
| Skeuomorphic Toggle | 拟物开关 |

Dock、Loading、Gallery、Toggle、仪表盘这些常见 UI 也开始加入 Three.js 和 Motion 效果。

## 覆盖范围总结

ThreeUI 已覆盖（F-019）：

```
完整页面 → 3D 场景 → 背景 → 按钮 → 文字 → UI 元素
```

从宏观的整页布局到微观的按钮文字，一整套视觉开发场景。

## 关键事实索引

- F-010：10 个分类（⚠️ 实际 9 个）
- F-011~F-020：六大组件类型详情与代表效果
- F-021：首屏背景提升质感
- F-022：官网总计 373 components（含 Pro）
- F-041：Sections 分类勘误
