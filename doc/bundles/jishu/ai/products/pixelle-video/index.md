---
okf_version: "0.2"
type: bundle
title: Pixelle-Video——输入一个主题自动出片的开源 AI 短视频引擎
description: 阿里 AIDC-AI（GitHub 组织现名 ATH-MaaS）开源 Pixelle-Video 教程（赛博煎蛋 134 期截图短帖核验转化）——28.7k star、五步流水线、ComfyUI/RunningHub/直连 API 三路径、25 模板、数字人/动作迁移、整合包与零成本本地方案实操
tags: [pixelle-video, ai视频, 短视频生成, comfyui, runninghub, tts, 数字人, 阿里AIDC, apache-2.0]
generated:
  by: trae-solo-agent
  at: "2026-10-08T20:30:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-08T21:10:00+08:00"
status: stable
stale_after: "2026-12-31"
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/U1EwSpjYmq4oKrsikWTsIw
  - id: github
    url: https://github.com/AIDC-AI/Pixelle-Video
  - id: github-api
    url: https://api.github.com/repos/AIDC-AI/Pixelle-Video
  - id: docs-site
    url: https://aidc-ai.github.io/Pixelle-Video/zh
---

# Pixelle-Video——输入一个主题自动出片的开源 AI 短视频引擎

> **类型**：开源产品教程（第三方推荐短帖 + 官方源逐项核验转化）
> **信源**：微信公众号「赛博煎蛋」第 134 期《【134期】阿里居然把它开源了！》（2026-09-25，正文 478 字截图型短帖，**全文未点名项目**）+ GitHub API / 官方中文 README / pyproject.toml / 仓库目录实测（核验日 2026-10-08）
> **P0 核验**：13 项声明 ✅ 10 / ⚠️ 2 / 🚩 身份推断 1（高置信 flagged）/ ❌ 0

## 本文概要

Pixelle-Video 是阿里国际数字商业 AIDC-AI 团队（GitHub 组织已更名 **ATH-MaaS**，旧名 AIDC-AI 仍可重定向）开源的 **AI 全自动短视频引擎**（Apache-2.0，2026-10-08 实测 28,745 star）：输入一个主题，自动完成**写文案 → AI 配图/视频 → 语音解说（可克隆音色）→ BGM → 合成 MP4** 全链路。其工程核心是把 LLM、ComfyUI 工作流、TTS、FFmpeg 编排成可插拔流水线，提供本地 ComfyUI / RunningHub 云端 / 直连模型 API 三条能力路径，辅以竖屏/横屏/方形 25+ HTML 模板、数字人口播、动作迁移、自定义素材与批量任务；Windows 有一键整合包。

> 🚩 **先读**：源推文**自始至终没有写出项目名、也没给仓库地址**（截图驱动 + 私信领取），"所指即 Pixelle-Video"是五特征唯一合取的核验推断（flagged 高置信）。帖文只提供功能存在性证据，安装与架构细节全部来自官方源，见 [verification.md](references/verification.md)。
>
> ⚠️ **"免费"有前提**：0 元方案 = Ollama + 本地 ComfyUI，官方明确要求**本地有 GPU**；整合包只免 Python/ffmpeg 安装，免不了显卡。

## 文档结构

### concepts/ — 概念解析

| 文档 | 主题 |
|------|------|
| [00-identity-and-positioning.md](concepts/00-identity-and-positioning.md) | 不点名短帖的身份推断链、AIDC-AI→ATH-MaaS 迁移、28.7k star 时点快照、与 MoneyPrinterTurbo 辨析 |
| [01-pipeline-and-pluggable-architecture.md](concepts/01-pipeline-and-pluggable-architecture.md) | 五步/四阶段流水线、selfhost 8 个与 runninghub 21 个工作流、直连 API、模板命名体系、扩展时间线 |
| [02-usage-modes-and-boundaries.md](concepts/02-usage-modes-and-boundaries.md) | AI 生成/固定文案/自定义素材/数字人模式对照、批量、零成本的 GPU 账单、平台 AI 内容限流与证据边界 |

### examples/ — 实操示例

| 文档 | 主题 |
|------|------|
| [00-install-and-first-video.md](examples/00-install-and-first-video.md) | Windows 整合包 start.bat→8501 与 uv 源码安装、三组系统配置、三栏 WebUI 出片、output/ 取片与 FAQ |
| [01-zero-cost-local-stack.md](examples/01-zero-cost-local-stack.md) | Ollama + 本地 ComfyUI 零现金成本组合、selfhost 工作流模型对照、Edge/Index-TTS 区别、无 GPU 替代 |

### references/ — 信源登记

| 文档 | 说明 |
|------|------|
| [article-source.md](references/article-source.md) | F-001~F-040 事实清单（页面事实/作者主张/官方补充/方法边界四层，观点条目标注） |
| [verification.md](references/verification.md) | 13 项 P0（10✅/2⚠️/1 flagged/0❌）、身份推断链、模式名与"免费"两处口径、组织迁移时效 |

## 已知边界

- **身份推断**：推文未点名，结论 flagged 高置信，引用本帖须保留该前提；截图未留存为文字证据
- **未真机实测**：examples 步骤依官方 README（中文，约 1.4 万字符）与仓库文件实测逐字比对，整合包行为、出图质量与速度未验证
- **强时效**：最新 release v0.1.15（2026-01-27），main pyproject 已标 0.2.0 未发版；README 最新条目 2026-06-01；star 28,745 为 2026-10-08 快照，stale_after 2026-12-31
- **归属为间接证据**：GitHub 组织页未自报公司全称，"阿里"据多家独立媒体 + 合作论文链互证
- **营销数字隔离**：第三方"日更 5 条/成本 2500→5 元/月费 69 元"等无具名来源，不登记不转述；平台对 AI 批量内容可能限流/要求标识，工具不承诺分发效果

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
log
```
