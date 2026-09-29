---
okf_version: "0.2"
type: bundle
title: "ThreeUI：Three.js 视觉组件库"
description: "Meng To 开源的 Three.js/WebGL 视觉组件库——164 个 Community 效果、10 大分类、6 大组件类型、AI Coding 集成与 MCP Server，WebGL UI 组件化趋势分析"
tags:
  - three.js
  - webgl
  - ui-components
  - mcp
  - ai-coding
  - frontend
  - open-source
generated: 2026-08-28
verified: web-research-verified
status: stable
stale_after: 2026-12-31
sources:
  - url: https://mp.weixin.qq.com/s/Gtmstp6HyXSqdK5h-3GcNQ
    title: "ThreeUI 爆火！一个基于 Three.js 的160+ 3D 组件全开源！"
    author: "前端开发爱好者"
    date: 2026-08-25
  - url: https://github.com/MengTo/threeui
    title: "ThreeUI GitHub Repository"
    type: repository
  - url: https://threeui.com
    title: "ThreeUI Official Website"
    type: website
  - url: https://threeui.com/pricing
    title: "ThreeUI Pricing (MCP Pro)"
    type: reference
---

# ThreeUI：Three.js 视觉组件库

> **内容性质**：开源工具/技术资讯介绍，基于"前端开发爱好者"2026-08-25 博文，经 GitHub README、官网、定价页等多源核验。博文为作者第一手项目介绍与趋势评论，其中客观技术数据（164 效果、50/111/141/23 统计、MCP Pro）已逐项核验，作者观点与评价以 📝 标注。3 项部分通过已如实记录。

## 信源说明

| 信源 | 类型 | 可信度 | 用途 |
|------|------|--------|------|
| 微信博文（前端开发爱好者） | 主信源 | 中 | 项目介绍、组件分类、AI Coding 工作流 |
| GitHub README | 权威 | 高 | 164 效果数据、MIT 许可证、npm 包名 |
| threeui.com 官网 | 权威 | 高 | 分类导航、组件总数、定价 |
| threeui.com/pricing | 权威 | 高 | MCP Pro 能力确认 |
| Meng To 公告（eond.com） | 一手 | 高 | AI Coding 工作流、Skills 生态 |
| Design+Code / 播客访谈 | 权威 | 高 | Meng To 身份核验 |

## 知识结构总览

```
threeui/
├── index.md                              ← 你在这里
├── concepts/
│   ├── 00-project-overview.md           项目概述（Meng To/Design+Code、开源、164效果、使用流程）
│   ├── 01-component-catalog.md          组件目录（10分类、6大类型、代表效果）
│   ├── 02-ai-coding-mcp.md             AI Coding 与 MCP（Codex/Claude Code/Cursor、MCP 4工具）
│   └── 03-webgl-ui-trend.md            WebGL UI 组件化趋势（Canvas UI 参照、门槛下降）
├── references/
│   ├── article-source.md                完整事实登记 F-001~F-043
│   └── verification.md                  P0 核验报告（4✅ 3⚠️ 0❌）
└── log.md                               生成日志与质量门
```

## 分层导航

### 概念学习（4 篇）

| 序号 | 文档 | 核心内容 |
|------|------|----------|
| 00 | [项目概述](concepts/00-project-overview.md) | Meng To 背景、ThreeUI 定位、164 效果数据、shadcn/ui 式使用流程 |
| 01 | [组件目录](concepts/01-component-catalog.md) | 10 大分类、6 大组件类型、代表效果（Kage/Globe/Liquid Metal 等） |
| 02 | [AI Coding 与 MCP](concepts/02-ai-coding-mcp.md) | 源码+Prompt 交 AI 修改、MCP Server 4 工具、Pro 能力 |
| 03 | [WebGL UI 趋势](concepts/03-webgl-ui-trend.md) | Canvas UI 参照、组件库卷到 WebGL 层、Three.js 门槛下降 |

### 信源参考（2 篇）

| 文档 | 内容 |
|------|------|
| [完整事实登记](references/article-source.md) | F-001~F-043 全部事实，8 类 |
| [P0 核验报告](references/verification.md) | 7 项核验逐项结论、权威来源 URL、3 项勘误 |

## 信任与生命周期

- **P0 核验**：7 项中 4 项完全通过、3 项部分通过、0 项失败
- **勘误记录**：①官网当前 9 分类非 10（Sections 为空）；②MCP 4 个工具名无法从公开来源验证；③Canvas UI 作者为 DavidHDev（博文未误归属，仅补充）
- **事实分级**：客观事实 32 条、作者观点 9 条（📝标注）、核验补充 3 条
- **stale_after**：2026-12-31（开源项目快速迭代中，组件数量和分类可能变化）

## 已知边界

1. ThreeUI 发布于 2026-08-22 左右，本知识包基于发布后第一周信息，后续版本可能新增组件/分类/功能
2. MCP 具体工具名称来自博文描述，需 Pro 账户登录后方可验证
3. GitHub Star 数（博文 1000+，核验时 4.1k）随时间快速增长，不代表稳定值
4. 博文未提供代码示例或 CLI 教程，本知识包不包含 examples/
5. ThreeUI 基于 React，非 React 项目（Vue/Svelte/vanilla）的适用性未验证
6. Pro 版本定价和功能可能调整，以官网为准

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
references/index
log
```
