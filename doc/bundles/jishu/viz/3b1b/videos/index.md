---
type: bundle
title: 3Blue1Brown 视频源码（videos）
okf_version: "0.2"
description: 3Blue1Brown 2015-2018年数学视频的Manim场景源码深度解析，涵盖PiCreature角色系统、视频Scene结构模式、checkpoint_paste交互式工作流、经典系列（线性代数/微积分/神经网络）项目组织
tags: [3blue1brown, manim, 视频源码, picreature, 数学动画, 线性代数, 微积分, 交互式开发]
generated:
  at: 2026-08-26
  by: source-code-to-okf-wiki skill
verified:
  at: 2026-08-26
  by: grep-api-verification
status: stable
stale_after: 2027-08-26
sources:
  - /references/representative-series.md
  - /spec/facts.md
---

# 3Blue1Brown 视频源码知识库

> ⚠️ **重要提示**：本知识包基于3Blue1Brown 2015-2018年视频源码，代码使用Manim早期版本API（CONFIG字典、OldTex、ShowCreation等），与当前ManimGL有显著差异。建议先学习 [ManimGL 知识包](../manim/index.md) 掌握当前API后，再回来研读videos仓库学习叙事设计和动画技巧。

本知识包是 3Blue1Brown 用于制作数学科普视频的 Videos 仓库（2015-2018年经典时期）系统化中文源码解析，基于 Videos 仓库源码深度阅读生成。覆盖 PiCreature（π生物）角色系统、自定义 Scene 基类体系、视频代码叙事模式、checkpoint_paste 交互式开发工作流、以及线性代数本质/微积分本质/神经网络等经典系列的项目组织。与 [ManimGL 知识包](../manim/index.md) 聚焦"引擎怎么用"不同，本知识包聚焦"用引擎讲好数学故事"的实战方法论——所有内容均溯源至 videos/ Python 源码，遵循 OKF v0.2 规范。

## 概念文档（concepts/）

按学习路径组织的 6 篇核心概念文档：

* [Videos 仓库总览与入门](concepts/00-videos-overview.md) — 仓库定位、目录结构、manim_imports_ext 统一入口、版本兼容性总览
* [PiCreature 角色系统详解](concepts/01-picreature-characters.md) — 表情状态机、视线追踪、自动眨眼、对话气泡、PiCreatureScene 场景基类
* [自定义 Scene 基类体系](concepts/02-custom-scenes.md) — PiCreatureScene、TeacherStudentsScene、GraphScene 等可复用场景基类的继承与组合模式
* [视频Scene代码结构与叙事模式](concepts/03-video-structure-pattern.md) — construct() 叙事分调、CONFIG 配置字典、generate_target 动画模式、get_* 复用构造
* [checkpoint_paste 交互式开发工作流](concepts/04-checkpoint-paste-workflow.md) — 运行中粘贴代码即时反馈、Sublime 集成、embed() 断点、force_skipping 跳转
* [代表性系列项目结构解析](concepts/05-series-projects.md) — eola/eoc/nn/eop 四大经典系列的目录组织、reusables 复用模式演进

## 实战示例（examples/）

2 篇从零开始的实战示例：

* [第一个 PiCreature 场景](examples/hello-picreature.md) — 创建角色、切换表情、对话气泡，含原版 API 说明与纯净 ManimGL 简化方案
* [checkpoint_paste 交互式开发流程](examples/interactive-development.md) — 最小骨架→运行交互→逐段粘贴→embed 断点的完整工作流演示

## 信源登记簿（references/）

2 篇源码溯源文档：

* [Videos 自定义模块索引](references/custom-modules-index.md) — custom/ 扩展模块功能说明、once_useful_constructs 历史组件库、版本兼容性标注
* [代表性视频系列目录导航](references/representative-series.md) — 按年度索引 eola/eoc/nn/eop 等经典系列，含目录结构、运行命令、老代码注意事项

## 信任与生命周期说明

* **status 判定依据**：当前 10 个内容文档（6 个概念 + 2 个示例 + 2 个信源登记）均基于对 Videos 仓库（`custom/`、`once_useful_constructs/`、`_2015/`~`_2018/` 核心目录）的逐模块阅读与事实提取（76 条源码事实 F-001~F-076），经 seven-concepts 方法论 R→I→E 三阶段流程生成，Grep API 验证通过，状态标记为 `stable`。
* **stale_after 解释**：统一设置为 `2027-08-26`。Videos 仓库中 2015-2018 年经典视频的源码结构（PiCreature 角色系统、Scene 基类继承模式、checkpoint_paste 工作流、系列项目 reusables 组织）已固化为历史资产，不会随新版本 Manim 迭代而改变；该日期作为针对仓库结构重大调整的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻；`verified.at` 记录 V 阶段 Grep 对抗验证事件（类名/方法签名/目录结构/文件命名逐一比对源码），两者分离、可追溯。

本知识包共收录 10 个内容文档（6 个概念 + 2 个示例 + 2 个信源登记），另含 3 个子目录 index.md、2 个 spec 文档（facts/insights）与根 index.md、log.md。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
