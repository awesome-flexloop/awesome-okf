---
type: Concept
title: 自定义主题开发
description: 通过自定义主题实现强品牌视觉风格，包括 Canvas 3D 地球仪组件 VibeHero、玻璃拟态卡片 HomeFeatures 和 CSS 动画定制。
tags: [trae-learning, trae, vitepress, custom-theme, vue-components, styling]
generated: { by: "reference_agent/trae-cn", at: "2026-04-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-04-22T00:00:00+08:00" }
status: stable
stale_after: "2026-10-22"
sources:
  - id: src
    resource: /references/learning-source.md
    title: "Trae Learning 源码信源"
---

# 自定义主题开发

TRAE Learning 通过继承 VitePress DefaultTheme + 自定义 CSS 覆盖 + 两个 Vue 组件，实现了高度定制化的"赛博朋克学习站"视觉风格。

## 主题入口：.vitepress/theme/index.js

自定义主题继承自 VitePress DefaultTheme，导入样式和组件后通过 `enhanceApp` 注册为全局 Vue 组件：

```js
import DefaultTheme from 'vitepress/theme'
import './custom.css'
import VibeHero from './components/VibeHero.vue'
import HomeFeatures from './components/HomeFeatures.vue'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('VibeHero', VibeHero)
    app.component('HomeFeatures', HomeFeatures)
  }
}
```

这种方式保留了 VitePress 默认主题的侧边栏、导航、搜索等核心能力，仅替换首页和覆盖样式。

## 全局样式：custom.css

### 品牌色彩与字体

- **品牌主色**：`#0FDC78`（绿色）
- **背景色**：强制黑色 `#000000`
- **文字色**：白色
- **字体**：Inter（正文）、JetBrains Mono（代码）

### 强制暗色覆盖

CSS 强制所有 VitePress 布局容器背景为黑色：

- `VPContent`、`VPHome`、`VPDoc`、`VPPage`、`Layout` 均设置 `background: #000000`
- 隐藏外观切换按钮（`.VPNavBarAppearance`、`.VPSwitchAppearance` 设置 `display: none`）

### 动画与发光效果

CSS 定义了三种动画关键帧：

| 动画 | 效果 |
|------|------|
| `pulse-glow` | 脉冲发光 |
| `float` | 漂浮动画 |
| `fade-in-up` | 向上淡入 |

三个发光工具类：`glow-sm`、`glow-md`、`glow-lg`。

### 响应式适配

在 `@media (max-width: 768px)` 断点调整 feature 卡片 padding/border-radius 和 manifesto 区域边距。

## VibeHero 组件：Canvas 3D 地球仪

VibeHero 是首页的 Hero 区域组件，使用 Canvas 2D 绘制程序化 3D 地球仪效果：

### 地球仪渲染

- **位置**：页面右侧（cx = w×0.66, cy = h×0.46）
- **纹理**：140×70 Float32Array 存储，通过 6 层正弦/余弦函数叠加模拟大陆轮廓，使用 `Math.pow(val, 0.75)` 校正
- **网格**：60 纬度 × 100 经度网格，12 条经线 + 7 条纬线（颜色 `rgba(15, 220, 120, 0.04)`）
- **倾角**：`TILT = 0.38` 弧度
- **旋转速度**：每帧 `angle += 0.002`

### 装饰元素

- **18 个漂浮代码符号**：`{}`、`</>`、`AI`、`fn()`、`#`、`vibe`、`=>`、`$`、`%`、`code`、`let`、`[]`、`git`、`<div>`、`npm`、`class`、`&&`、`0xFF`，使用 JetBrains Mono 字体
- **40 个闪烁粒子**：随机分布在球面，根据相位和速度闪烁，仅在 flicker > 0.6 时渲染

### 文字内容

- "AI-Powered Development" 徽章（带闪烁绿点）
- 大标题 "TRAE LEARNING"（LEARNING 使用渐变色）
- 副标题 "The Art of Vibecoding / 探索 AI 辅助开发的无限可能"
- 两个按钮："开始学习"（绿色主按钮→guide/what-is-vibecoding）、"浏览教程"（幽灵按钮→tutorials/）

### 生命周期

- 使用 `requestAnimationFrame` 驱动动画循环
- `onUnmounted` 中取消动画帧并移除 resize 事件监听

## HomeFeatures 组件：玻璃拟态特性卡片

HomeFeatures 展示 4 个功能特性，采用左右交替布局：

### 特性内容

| 特性 | 代码语言 | 描述 |
|------|---------|------|
| 心流编码 | typescript | 展示 TypeScript 代码示例 |
| 极速反馈 | prompt | 展示 Prompt 交互示例 |
| 专家共建 | yaml | 展示 YAML 配置示例 |
| 技术审美 | javascript | 展示 JavaScript 代码示例 |

偶数项使用 `direction: rtl` 实现左右交替布局。

### 视觉效果

- **玻璃拟态代码卡片**：半透明背景 + 模糊效果
- **macOS 风格窗口装饰**：红黄绿三个圆点 + 右上角语言标签
- **自定义语法高亮**：`hl(code, lang)` 函数支持 prompt/yaml/js/ts 四种语言，使用正则匹配关键字、字符串、注释、函数调用、数字
- **鼠标跟随光条**：左侧绿色光条（light-bar），包含 bloom/glow/core/line 四层渐变，通过 CSS 变量 `--light-y` 控制垂直位置
- **Manifesto 区块**：引用"在 AI 时代，编程的门槛正在消失，而审美的价值正在凸显……"

### 响应式

- `@media (max-width: 900px)`：隐藏光条
- `@media (max-width: 768px)`：特性改为单列布局

## 相关链接

- [VitePress 站点架构](/concepts/01-vitepress-setup.md)
- [Trae Learning 学习站简介](/concepts/00-introduction.md)
- [自定义主题样式示例](/examples/customize-theme.md)
- [文档站源码索引](/references/learning-source.md)
