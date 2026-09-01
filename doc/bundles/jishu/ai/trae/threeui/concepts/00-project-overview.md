# 00 项目概述

> ThreeUI 是什么、谁创建的、包含多少内容、如何使用。

## 项目定位

**ThreeUI** 是一套专门给 Three.js / WebGL 做的视觉组件库，由 **Meng To** 开源（F-002）。它按照常规 UI 组件库的方式，将各种 3D 和 WebGL 效果整理成完整目录，开发者可以找到效果、在线预览、调参数、查看源码、拿到项目里改（F-007）。

> 📝 博文将其类比为 shadcn/ui——只不过组件从普通 UI 升级成了 Three.js + WebGL（F-007）。

## 创始人背景

Meng To 是 **Design+Code**（designcode.io）创始人，自学成才的设计师/开发者，有 20 余年设计与编程经验，著有 Design+Code 书籍（35,000 读者）。近年还创建了 DreamCut（dreamcut.ai）和开源的 MengTo/Skills 项目（F-006）。

## 基本信息

| 项目 | 信息 |
|------|------|
| 官网 | https://threeui.com |
| GitHub | https://github.com/MengTo/threeui |
| 许可证 | MIT |
| 技术栈 | React + Three.js/WebGL |
| npm 包名 | `@designcodeio/threeui` |
| CLI | `npx @designcodeio/threeui-cli add <component>` |

来源：F-003、F-005

## Community 版本数据

GitHub README "Included" 部分逐字记载（F-009）：

| 指标 | 数量 |
|------|------|
| Community 父组件 | 50 |
| Community Routes | 111 |
| 免费 Variant | 141 |
| 独立组件 | 23 |
| **可浏览效果总计** | **164**（141 + 23） |

官网显示含 Pro 在内总计 **373 components**（F-022）。

## 开源方式

ThreeUI 并没有把效果封成黑盒 npm 包只暴露几个 API。Community 组件的**实现源码和相关资源都一起开放**（F-008），开发者可以直接拿到完整 Three.js 代码进行修改。

## 使用流程

```
找到效果 → 在线预览 → 调参数 → 查看源码 → 拿到项目里改
```

这个流程与 shadcn/ui 一致，但组件内容从按钮/卡片等传统 UI，变成了 3D 场景、Shader 背景、粒子动画等 WebGL 效果（F-007）。

## GitHub 热度

项目上线后很快突破 1000+ GitHub Star（博文发布时数据，F-004）。核验时（2026-08-28）已达约 **4.1k stars**，增长迅速。

## 关键事实索引

- F-002：ThreeUI 由 Meng To 开源，Three.js/WebGL 视觉组件库
- F-003：官网/GitHub/MIT/React+Three.js
- F-004：1000+ Star（博文时），核验时 4.1k
- F-005：npm 包名 @designcodeio/threeui
- F-006：Meng To = Design+Code 创始人
- F-007：shadcn/ui 式使用流程
- F-008：源码开放，非黑盒
- F-009：50/111/141/23=164 数据
