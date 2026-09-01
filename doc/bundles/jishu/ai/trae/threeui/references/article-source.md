# 完整事实登记

> 主信源：微信公众号"前端开发爱好者"《ThreeUI 爆火！一个基于 Three.js 的160+ 3D 组件全开源！》，2026-08-25 08:33
> URL：https://mp.weixin.qq.com/s/Gtmstp6HyXSqdK5h-3GcNQ

## 元信息

| 编号 | 事实 | 核验 |
|------|------|------|
| F-001 | 标题《ThreeUI 爆火！一个基于 Three.js 的160+ 3D 组件全开源！》，"前端开发爱好者"，2026-08-25 08:33 | — |

## 项目概述

| 编号 | 事实 | 核验 |
|------|------|------|
| F-002 | ThreeUI由Meng To开源，是专门给Three.js/WebGL做的视觉组件库 | ✅ |
| F-003 | 官网threeui.com，GitHub github.com/MengTo/threeui，MIT许可证，基于React+Three.js | ✅ |
| F-004 | 项目上线后突破1000+ GitHub Star（博文发布时）；核验时已达4.1k | ✅ |
| F-005 | npm包名@designcodeio/threeui | ✅ |
| F-006 | Meng To是Design+Code创始人，20余年设计编程经验，著书35000读者，近年创建DreamCut和MengTo/Skills | ✅ |
| F-007 | 使用方式：找到效果→在线预览→调参数→查看源码→拿到项目里改，类似shadcn/ui | ✅ |
| F-008 | Community版本源码和资源一起开放，非黑盒npm包 | ✅ |
| F-009 | Community版本：50父组件、111 Routes、141免费Variant、23独立组件=164可浏览效果 | ✅ README |

## 组件数据

| 编号 | 事实 | 核验 |
|------|------|------|
| F-010 | 官方划分10个分类：Landing Pages/Hero/Three.js/Motion Design/Sections/Backgrounds/Buttons/Text Animation/UI Elements/CSS | ⚠️ 官网9个，Sections为空 |

## 六大核心组件类型

| 编号 | 事实 | 核验 |
|------|------|------|
| F-011 | Landing Page/Hero：完整页面含布局/滚动/交互/Three.js场景；代表Kage/Complete Shelf/Bestsellers Book Showcase | ✅ |
| F-012 | Three.js 3D场景：Temple Night/Japanese Tower/Bookshelf/Globe/Orbital Sphere/Landscape；Camera/Light/Material/Animation已封装 | ✅ |
| F-013 | 适用AI官网/SaaS/作品集/Web3/开发者工具Hero区域 | ✅ |
| F-014 | Shader/动态背景：Liquid Form/Dot Matrix/Warp Field/Nebula Background/Particle Network/Flux Vortex | ✅ |
| F-015 | Buttons：Liquid Metal/Plasma/Thinking/Glassmorphism CTA/Gradient Beam CTA等Shader按钮 | ✅ |
| F-016 | Text Animation：Typography Vortex/Morphing Glyph Cloud/Particle Wordmark/Neon Typography；粒子化/变形/沿路径 | ✅ |
| F-017 | 📝 以前文字动画需GSAP+Canvas+Shader手搓，现在可直接用现成实现 | 📝 |
| F-018 | UI Elements：Genie Dock/Animated Top Dock/Gallery/Uplink Loader/Performance Gauges/Skeuomorphic Toggle | ✅ |
| F-019 | 📝 整体覆盖完整页面/3D场景/背景/按钮/文字/UI元素一整套视觉开发场景 | 📝 |
| F-020 | Kage日式寺庙主题含夜景/灯笼/樱花/3D场景/鼠标键盘滚动导航交互 | ✅ |
| F-021 | 📝 很多效果直接放首屏背景就能明显提升页面质感 | 📝 |
| F-022 | 官网显示总计373 components（含Pro组件） | ✅ |

## AI Coding 集成

| 编号 | 事实 | 核验 |
|------|------|------|
| F-023 | ThreeUI支持将源码或Prompt给Codex/Claude Code/Cursor等AI Agent | ✅ |
| F-024 | 示例指令：深蓝色科技风/减少粒子/灯光柔和/动画速度降30% | ✅ |
| F-025 | 📝 痛点：看得懂效果但改不动，Three.js的Camera/Material/Shader参数容易劝退 | 📝 |
| F-026 | 📝 新流程：先找接近目标效果→再让AI改 | 📝 |
| F-027 | 组件自带agent skills，兼容Claude Code/Cursor/Codex/OpenCode/Kiro | ✅ |

> **编号注记（2026-08-29 V 阶段补记）**：F-028、F-029 为事实登记过程中的跳用编号，无对应事实行；编号保留不复用，本节实际范围为 F-023~F-027，后续事实自 F-030 起续编。

## MCP 支持

| 编号 | 事实 | 核验 |
|------|------|------|
| F-030 | ThreeUI提供MCP Server让AI Coding Client访问Catalog | ✅ |
| F-031 | MCP 4工具：search_catalog/get_catalog_item/get_item_source/get_item_prompt | ⚠️ MCP Pro确认，工具名未公开验证 |
| F-032 | MCP属于Pro能力 | ✅ 定价页 |
| F-033 | 📝 MCP工作流：需求→AI Agent→ThreeUI→组件源码→页面 | 📝 |
| F-034 | Pro含50+额外组件、MCP和skills | ✅ |

## 行业趋势

| 编号 | 事实 | 核验 |
|------|------|------|
| F-035 | Canvas UI此前火了，把WebGL Shader带进真实DOM（DavidHDev，2026-07-23发布） | ⚠️ 项目存在性质吻合 |
| F-036 | 📝 前端组件库已开始卷到WebGL层 | 📝 |
| F-037 | 📝 从按钮/文字/背景到完整3D场景/Landing Page，手搓效果变成可直接用的组件 | 📝 |
| F-038 | 📝 加AI Agent后：找效果→拿源码→描述需求→AI修改 | 📝 |
| F-039 | 📝 Three.js门槛正在快速下降 | 📝 |
| F-040 | 📝 以后想做看起来很贵的3D官网可能没以前难 | 📝 |

## 核验补充

| 编号 | 事实 | 来源 |
|------|------|------|
| F-041 | 官网当前9分类（非10），Sections返回"No components match" | threeui.com/browse |
| F-042 | MCP 4工具名无法从公开网页验证，需Pro权限 | threeui.com/pricing |
| F-043 | Canvas UI由DavidHDev创建，html-in-canvas API，支持React/Vue/Svelte/vanilla TS，24→33组件 | GitHub/cssscript |

## 事实统计

| 类别 | 数量 |
|------|------|
| 元信息 | 1 |
| 项目概述 | 8 |
| 组件数据 | 1 |
| 六大组件类型 | 12 |
| AI Coding集成 | 5 |
| MCP支持 | 5 |
| 行业趋势 | 6 |
| 核验补充 | 3 |
| **合计** | **41** |
