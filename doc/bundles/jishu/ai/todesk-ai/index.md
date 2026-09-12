---
okf_version: "0.2"
type: bundle
title: ToDesk AI 跨设备 AI 助手产品教程
description: ToDesk 旗下跨设备 AI 助手——Computer Use 可视化操控、多智能体与技能体系、自定义模型接入的官方文档 OKF 教程化重组（含可照做实操流程）
tags: [todesk-ai, computer-use, gui-agent, remote-execution, skills, custom-model]
generated:
  by: codearts/glm-5.3-flash
  at: "2026-09-12T11:30:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-09-12T11:30:00+08:00"
status: stable
stale_after: "2027-03-12"
sources:
  - id: tencent-doc
    url: https://doc.weixin.qq.com/doc/w3_Ae4AJgaPAJMCNi7xCQuo2SaelthS2?scode=AFcAOAfiAAYfXS6XpeARIAFAZkABY
  - id: todesk-official
    url: https://www.todesk.com/
  - id: todesk-ai-site
    url: https://www.todeskai.com
---

# ToDesk AI 跨设备 AI 助手产品教程

> **类型**：产品使用教程（官方文档教程化重组，含可照做实操流程）
> **信源**：官方产品文档（企业微信文档，9184 字，23 页 canvas 渲染页 OCR 逐字转录）+ todeskai.com 官网（2026-09-12 二次采集，补充浏览器插件等新功能）
> **P0 核验**：7 类 P0 声明 ✅ 4 / ⚠️ 3 / ❌ 0（⚠️ 均为单源或时效项，无 ❌）

## 本文概要

ToDesk AI 是 ToDesk（远程控制软件）旗下的跨设备 AI 助手：以一句话指令驱动，AI 自主规划执行任务并交付可验收结果。产品核心是 **Computer Use 可视化操控**——通过屏幕视觉感知模拟真人键鼠，直接操作第三方软件与网页；配合多端远程执行（手机指挥电脑）、技能插件体系（SKILL.md 结构）与自定义模型接入，构成"智能体—技能—模型"三层解耦的 Agent 产品形态。

## 文档结构

### concepts/ — 概念解析

| 文档 | 主题 |
|------|------|
| [00-intro.md](concepts/00-intro.md) | 产品定位、与远控母体关系、版本演进时间线（ToClaw → ToDesk AI） |
| [01-core-capabilities.md](concepts/01-core-capabilities.md) | 三大核心能力：多端远程执行 / Computer Use / 过程可追溯，IM 集成 |
| [02-computer-use.md](concepts/02-computer-use.md) | 五阶段感知-规划-执行循环、适用与不适用场景、系统级安全约束 |
| [03-agent-skill-model.md](concepts/03-agent-skill-model.md) | 智能体与 AI 记忆、Skill 工具箱结构、内置与自定义模型体系 |
| [04-browser-extension.md](concepts/04-browser-extension.md) | 浏览器插件——Chrome 扩展，免安装客户端，四大网页任务能力 |

### examples/ — 实操演练

| 文档 | 主题 |
|------|------|
| [00-install-and-first-run.md](examples/00-install-and-first-run.md) | 环境自检、三平台安装、登录、首次会话与任务建议 |
| [01-daily-workflows.md](examples/01-daily-workflows.md) | 定时任务创建验证、设备权限管理、聊天工具绑定、文件上传两方式 |
| [02-custom-model-and-skills.md](examples/02-custom-model-and-skills.md) | 第三方模型 API 五步接入、Key 类型约束、技能安装与显式调用 |
| [03-browser-extension.md](examples/03-browser-extension.md) | Chrome 商店安装插件、一键唤起与四类网页任务实操 |

### references/ — 信源登记

| 文档 | 说明 |
|------|------|
| [article-source.md](references/article-source.md) | 原文事实清单（F-001 至 F-070），含页码溯源与疑点登记 |
| [verification.md](references/verification.md) | P0 核验报告：官网可达性核验、内部一致性核对、勘误登记 |

## 主题关联

- [EchoBird 百灵鸟 AI Agent 桌面管理工具](../../echobird/index.md)：同为桌面端 AI Agent 工具（模型枢纽 vs 远程操控视角互补）
- [Matt Pocock Skills 生态解读](../../mattpocock-skills/index.md)：SKILL.md 技能目录约定的生态对标（Anthropic Agent Skills 范式）
- [mobile-use 移动自动化框架](../../mobile-use/index.md)：移动端 GUI 自动化的开源框架对照
- [BrowserAct 浏览器自动化 Agent](../../browseract/index.md)：网页端自动化场景的能力对照

## 已知边界

- **单源声明**：内置模型列表（F-049）、积分数额（F-057）为官方文档单源，官网仅佐证机制存在性
- **时效项**：模型列表、积分规则、版本时间线属快速迭代内容（月度级发布节奏），stale_after 前须复核
- **年份口径**：更新日志原文未注年份，版本时间线年份为推断（见 verification.md 勘误-2）
- **OCR 口径**：两处章节标题（跨设备使用/文件上传）因 canvas 分页截断取自目录侧转录；链接 URL 在 canvas 中不可提取，正文以链接标题呈现

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
log
```