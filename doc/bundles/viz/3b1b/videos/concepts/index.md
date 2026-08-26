# 概念文档

Videos 仓库核心概念，共 6 篇，按学习路径组织。

* [00 Videos 仓库总览与入门](00-videos-overview.md) — Videos 仓库是 3Blue1Brown 2015-2018 年所有数学动画视频的源码集合，基于 Manim 早期版本构建，包含 PiCreature 角色系统、自定义场景基类和按年份组织的完整视频项目源码。
* [01 PiCreature 角色系统详解](01-picreature-characters.md) — PiCreature 是 3Blue1Brown 视频中的标志性π形角色，不是简单SVG图形而是具备表情切换、视线追踪、自然眨眼、对话气泡的完整角色系统，让动画中的角色具备"生命感"。
* [02 自定义 Scene 基类体系](02-custom-scenes.md) — Videos 仓库提供了一系列预定义的 Scene 子类，包括自动眨眼的 PiCreatureScene、教室场景 TeacherStudentsScene、坐标图场景 GraphScene 等，通过继承和组合实现场景逻辑复用，避免每个视频重复编写样板代码。
* [03 视频Scene代码结构与叙事模式](03-video-structure-pattern.md) — 一个视频=一个Scene子类的编码范式，详解construct()叙事分调、CONFIG配置字典、generate_target动画模式、多继承组合、get_*复用构造等3Blue1Brown视频源码的经典代码结构。
* [04 checkpoint_paste 交互式开发工作流](04-checkpoint-paste-workflow.md) — 3Blue1Brown视频制作的核心开发范式——不是"写完→运行→看结果→修改"，而是在运行中的Manim窗口里即时粘贴代码片段看到效果，配合-se/-p标志、Sublime集成、force_skipping跳转实现视觉创意的快速迭代。
* [05 代表性系列项目结构解析](05-series-projects.md) — 深度解析3Blue1Brown四大经典系列源码结构——线性代数本质(eola)、微积分本质(eoc)、神经网络(nn)、概率系列(eop)，理解系列项目的reusables复用模式、章节组织、跨章共享组件的最佳实践。

```{toctree}
:hidden:
:maxdepth: 7

00-videos-overview
01-picreature-characters
02-custom-scenes
03-video-structure-pattern
04-checkpoint-paste-workflow
05-series-projects
```
