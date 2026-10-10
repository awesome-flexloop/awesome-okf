---
okf_version: "0.2"
type: bundle
title: image-blaster——把一张照片变成可漫游 3D 世界的 Claude 技能集
description: 开源「图像→3D世界」工作流教程（微信博文核验转化）——多模型编排管线、8 个 Claude Code skills、三类可进游戏引擎的资产输出、Hunyuan 3D 参数、快速上手实操
tags: [image-blaster, image-to-3d, claude-code, world-labs, marble, hunyuan-3d, fal, elevenlabs, gaussian-splatting, orchestration]
generated:
  by: trae-solo-agent
  at: "2026-10-10T12:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-10T12:30:00+08:00"
status: stable
stale_after: "2026-12-10"
sources:
  - id: wechat
    url: https://mp.weixin.qq.com/s/uANTnBjmirCavBJb9pNytA
    title: 6.9K Star！这个开源项目把图像变3D世界的门槛砸得稀碎！
    access_time: "2026-10-10"
  - id: github
    url: https://github.com/neilsonnn/image-blaster
    title: neilsonnn/image-blaster (README + .claude/skills 目录实测)
    access_time: "2026-10-10"
---

# image-blaster——把一张照片变成可漫游 3D 世界的 Claude 技能集

> **类型**：开源工具教程（第三方推荐博文 + 官方仓库实测，经双源核验转化）
> **信源**：微信公众号公开推文 2026-10-05（标题见上，公众号名未能从页面抓取确认）+ GitHub 仓库 `neilsonnn/image-blaster`（README 与 `.claude/skills/` 目录实测，核验日 2026-10-10）
> **P0 核验**：8 项声明 ✅ 6 / ⚠️ 2 / ❌ 0（Star 数文章"6.9K+"vs 实测 2.7k 差异显著；作者姓名双源不一致；ElevenLabs 是否必需未在 README 确认）

## 本文概要

image-blaster 是一个**开源的、运行在 Claude Code 上的「图像到世界」技能集（image-to-world skillset）**：给定一张图片，它通过串联 World Labs Marble 1.1（环境重建）、腾讯 Hunyuan 3D（物体建模）、FAL Nano Banana / GPT-Image-2（图片编辑）、ElevenLabs SFX（音效生成）等多个专业模型，在约 5 分钟内产出一整套可直接进游戏引擎的 3D 资产包。与"一个大一统模型包打天下"的思路相反，它采用**多模型编排**——每个环节交给领域内最专业的模型，配以 8 个严格排序的 Claude Code skills 流水线与"人类始终在回路里"的逐步确认机制。

> ⚠️ **时效提示（先读）**：博文声称 Star 数为 6.9K+，但核验时（2026-10-10）GitHub 实测为 **2.7k**，差异显著，疑为博文写作时点或夸大，正文以双口径呈现。详见 [verification.md](references/verification.md)。

## 文档结构

### concepts/ — 概念解析

| 文档 | 主题 |
|------|------|
| [00-image-blaster-overview.md](concepts/00-image-blaster-overview.md) | 项目定位、多模型编排核心理念、8 个技能流水线、人类在环机制 |
| [01-output-assets.md](concepts/01-output-assets.md) | 三类输出资产（静态环境 .spz / 动态物体 .glb/.obj / 音效 .mp3）与输出目录结构、结构化输出为何"生产就绪" |
| [02-technical-architecture.md](concepts/02-technical-architecture.md) | 技术架构、动态/静态物体判断标准、Hunyuan 3D 可调参数、图片编辑双模型、三音效输出、Hooks 自动化 |

### examples/ — 实操示例

| 文档 | 主题 |
|------|------|
| [00-getting-started.md](examples/00-getting-started.md) | 环境要求、四步安装（clone / Claude Code / 三 API Key / blast）、目录组织与生命周期 |

### references/ — 信源登记

| 文档 | 说明 |
|------|------|
| [source-manifest.md](references/source-manifest.md) | 信源登记（公众号 URL / GitHub 仓库）、公开性预检记录、采集方式 |
| [facts.md](references/facts.md) | F-001~F-035 事实清单（博文页事实+作者论断+官方核验补充，三析分层） |
| [verification.md](references/verification.md) | P0 核验记录、勘误表、核验方法与未覆盖边界 |

## 主题关联

- [LoopX 长程 Agent 控制面](../.././loopx/index.md)：同为微信博文→OKF 核验转化的产品教程包，其"编排层 vs 单一模型"叙事与 image-blaster 的"多模型编排"形成方法论对照
- 同域 AI 产品终端工具（见 [AI 产品与终端工具组索引](../index.md)）：image-blaster 属"图像→3D 创作管线 Agent 工具"定位，与 LoopX、wigolo、orca-ade 等同属开箱即用的 Agent 驱动工具

> 📌 **注**：本文为单源博文 + 单仓库核验的轻量教程包，未来可在「多模型编排」这一方法论维度与 LoopX 的控制面编排做法做横向对照。

## 已知边界

- **数据强时效**：Star 数、模型命名（marble-1.1 / hunyuan-3d / nano-banana / gpt-image-2 / elevenlabs-sfx）、安装命令均有版本时效，`stale_after`（2026-12-10）前须复核
- **公众号名未确认**：页面抓取未能取得账号名，仅以规范 URL 与标题登记；如需补正可在复核时更新 source-manifest
- **作者姓名双源不一致**：博文称 Neilson Koerner-Safrata；`marble3dai` 第三方博客称 Nicholas Neilson；GitHub 显示 neilsonnn（Neilson K-S）、World Labs 团队，已并记
- **未真机执行**：examples 步骤经官方 README 逐字比对，本包制作中未实际运行 blast 流水线；Three.js 加载 `.spz` 的兼容性未实测
- **观点分层**：文章"把门槛砸得稀碎""最狠的是"等为作者渲染语（P2 单源），已作为 author_claim 归入事实表，不作为独立事实引用

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
log
```