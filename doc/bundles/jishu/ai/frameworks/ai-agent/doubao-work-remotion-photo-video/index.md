---
okf_version: "0.2"
type: bundle
title: 豆包工作与 Remotion 照片视频制作
description: 从公开案例学习素材、分镜、静帧、声音与项目交付；官方文档核验加原创需求练习，非源码精读或运行复现。
status: flagged
stale_after: 2026-12-04
tags: [豆包工作, Remotion, Agent Skills, 照片视频, 分镜, 静帧审核]
generated: { by: "process:seven-concepts", at: "2026-11-04T10:19:35+08:00" }
sources:
  - id: article
    resource: https://mp.weixin.qq.com/s/P0ImKmk9glQLYipu0iLhZg
    title: 豆包工作+剪辑Skills！人人都是视频大师！
  - id: skills
    resource: https://www.remotion.dev/docs/ai/skills
  - id: coding
    resource: https://www.remotion.dev/docs/ai/coding-agents
  - id: license
    resource: https://www.remotion.dev/license
---

# 豆包工作与 Remotion 照片视频制作

一组照片变成视频，需要决定镜头、文字、运动和声音，也需要检验输出。公众号前端之神的作者林三心不学挖掘机记录了使用豆包工作与 Remotion 制作摩托短片的过程（F-001/F-002/F-013–F-020）。本包把这个公开案例转成中文原创学习材料，并以官方文档校准工具分工和许可边界。[事实登记](references/article-source.md)

**当前状态为 flagged**：核心安装、自动质检和成片结果尚无完整复现证据。教程可以用于学习需求与审核方法，不能当作豆包的稳定功能保证或本次实测记录。

## 从你的问题开始

| 问题 | 入口 | 学完可形成的产物 |
| --- | --- | --- |
| 不懂这些工具的关系 | [工具分工](concepts/00-tool-roles-and-boundaries.md) | 安装范围、权限与费用边界说明 |
| 有照片，但不知道怎么提需求 | [照片与分镜](concepts/01-photo-storyboard-workflow.md) | 素材说明、分镜表与原创需求模板 |
| 静帧好看，视频还是不对 | [渲染与声音](concepts/02-render-audio-and-delivery.md) | 按时间点记录的全片反馈与交付要求 |
| 想提炼一个通用做法 | [先预览后出片](concepts/03-preview-before-render-pattern.md) | 单案例候选模式与适用边界 |
| 想知道文章哪些内容已核实 | [关键核验](references/verification.md) | 官方证据、作者单源与缺口区分 |

学习顺序为工具分工、素材与静帧、渲染与交付、模式迁移。可先在纸面上写需求，不必立即安装、上传照片或运行命令。

## 取材与证据范围

原文章发布于 2026-10-30 08:35，未显示时区；本次采集于 2026-11-04（F-003）。官方技能和 Coding Agents 页标注更新于 2026-11-01（F-036）。取材范围和访问方式见[来源清单](references/source-manifest.md)。

本包含 4 篇概念正文、5 篇信源正文、根与子索引及 log，共 13 个 Markdown 文件。事实登记 36 条，F-001 至 F-036；三条洞察和候选模式均与来源陈述分层。没有 examples 目录，原因是原作版本、输入项目与部分截图不足以支持精确复现。

## 主题关联

| 知识包 | 分工 |
| --- | --- |
| [豆包工作产品实测](../doubao-work/index.md) | 既有媒体功能与飞书集成观察 |
| [Context Layer 分析](../doubao-work-context-layer/index.md) | 组织上下文的战略假说 |
| [组织生产力分析](../doubao-work-org-productivity/index.md) | 组织效率、权限与行业数据 |
| 本包 | 照片视频需求、静帧审核、声音与项目交付 |

这些包来自不同时点，历史结论不因本包增补而自动升级。

## 已知边界

- 12 张图片中只可靠读取第 1 张，2–12 张未完成核对；首尾视频未播放，不验证媒体元数据。
- 一条指令安装、自动画面质检与作者成片结果仍为作者单源；完整提示词与依赖版本未取得。
- Remotion 官方当前技能目录为 1 个聚合入口加 12 个专项，不能反推作者安装集合。
- 命令是已读官方参考；提示模板、分镜时间表与帧数算例是原创建议，本次未运行。
- 本地执行不等于模型处理全部离线；照片、音乐和人物授权需另行核对。
- 免费体验与签到只获部分证据，Remotion 也有主体和用途许可限制，不承诺零成本。

到失效日期前复核技能、许可和豆包入口。未补齐核心证据则保留 flagged；模式持续为 L1-draft。文档门禁和独立审查状态见[更新日志](log.md)与[审查记录](references/adversarial-review.md)。

```{toctree}
:hidden:
:maxdepth: 3

concepts/index
references/index
log
```
