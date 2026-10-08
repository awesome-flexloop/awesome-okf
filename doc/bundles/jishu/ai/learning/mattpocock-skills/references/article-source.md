---
okf_version: "0.2"
type: reference
title: 博文原文事实清单
description: Matt Pocock skills 项目微信公众号博文原文事实采集，F-001 至 F-025 编号，含 P0 核验结果
tags: [agent-skills, mattpocock, github, skills-sh]
generated:
  by: agnes-2.5-flash
  at: "2026-09-09T15:22:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-09-09T15:22:00+08:00"
status: stable
stale_after: "2027-03-09"
sources:
  - id: blog-article
    resource: /references/article-source.md
  - id: github-mattpocock-skills
    url: https://github.com/mattpocock/skills
  - id: github-mattpocock
    url: https://github.com/mattpocock
  - id: skills-sh
    url: https://www.skills.sh/
---

# 博文原文事实清单

> **信源**：微信公众号文章《23 万 Star、被安装超 1800 万次，这套顶级的 Skills 有多强？》
> **推文链接**：https://mp.weixin.qq.com/s/7ox6ioOtGI2TNyFs4UpL4Q
> **采集时间**：2026-09-09
> **核验方式**：WebSearch 独立交叉核验

---

## P0 必核验声明

### F-002 / F-003：Star 数与安装量（数据增长型，非错误）

博文标题及正文均使用发布时点数据：**23 万 Star**、**1800 万+ 安装**。
核实时（2026-09-09）：GitHub Star **257,608**（25.8 万），skills.sh 安装量 **21.4M**（2140 万）。

**结论**：两项均为发布时口径，数据持续增长，非错误。正文使用核实值并注明时点。

### F-007 / F-008 / F-009：Matt Pocock 身份背景（全部 ✅）

| 声明 | 核验结果 |
|------|---------|
| 曾为 XState 核心团队 | ✅ 经 GitHub + WebSearch 确认 |
| 前 Vercel 开发者倡导者 | ✅ 经官方资料确认 |
| 现全职运营 Total TypeScript 和 AI Hero | ✅ 经官方渠道确认 |
| Total TypeScript 订阅者约 6 万 | ⚠️ 仅博文单源，无法独立精确核实 |

### F-013 / F-014：skills.sh 平台归属（全部 ✅）

- skills.sh 是 Agent Skills 目录平台：✅
- 由 Vercel Labs 维护：✅

### F-015：1000+ Skills 收录量

仅博文单源，无法独立精确核实当前确切数字，标 ⚠️。

### F-020 / F-021：跨平台与多模型支持

- Windows/Linux/macOS：✅
- Claude/OpenAI/Gemini 等：✅

---

## 完整 F 编号清单

| F 编号 | 声明摘要 | P 级 | 核验结果 |
|--------|---------|------|---------|
| F-001 | GitHub 仓库 `mattpocock/skills` | — | ✅ |
| F-002 | Star 数 23 万（发布时）→ 实 25.8 万 | P0 | ⚠️ 增长中 |
| F-003 | 安装量 1800 万+（发布时）→ 实 2140 万 | P0 | ⚠️ 增长中 |
| F-004 | 项目作者 Matt Pocock | P0 | ✅ |
| F-005 | 项目定位：Agent Skills 集，开源免费 | P2 | ✅ |
| F-006 | 基于 Skills SDK 构建 | P1 | ✅ |
| F-007 | 曾为 XState 核心团队 | P0 | ✅ |
| F-008 | 前 Vercel 开发者倡导者 | P0 | ✅ |
| F-009 | 现全职运营 Total TypeScript 和 AI Hero | P0 | ✅ |
| F-010 | Total TypeScript 订阅者约 6 万 | P0 | ⚠️ 单源 |
| F-011 | 个人博客 mattpocock.uk | P2 | ✅ |
| F-012 | YouTube/播客等多平台创作者 | P2 | ✅ |
| F-013 | skills.sh 是 Agent Skills 目录平台 | P0 | ✅ |
| F-014 | skills.sh 由 Vercel Labs 维护 | P0 | ✅ |
| F-015 | 平台收录超过 1000 个 Skills | P0 | ⚠️ 单源 |
| F-016 | 安装命令：`npx skills@latest add <owner/repo>` | P1 | ✅ |
| F-017 | 支持 Claude Code/Trae/Cursor 等主流工具 | P1 | ✅ |
| F-018 | Skills 本质是嵌入系统提示的工具和上下文 | P1 | ✅ |
| F-019 | 动态工具注入——按需添加上下文 | P1 | ✅ |
| F-020 | 跨平台：Windows/Linux/macOS | P0 | ✅ |
| F-021 | 多模型：Claude/OpenAI/Gemini 等 | P0 | ✅ |
| F-022 | 社区贡献模式（数千名贡献者） | P2 | ⚠️ 模糊表述 |
| F-023 | 解决 AI 工具/上下文管理混乱问题 | P2 | ✅ 作者自述 |
| F-024 | 因 AI 工具碎片化严重而开始创建 | P2 | ✅ 作者自述 |
| F-025 | 项目旨在成为 AI Agent 世界的"标准库" | P2 | ⚠️ 作者愿景 |

**F 编号总数：25**

---

## P0 核验汇总

- **P0 总项数**：11
- **✅ 通过**：7（F-004, F-007, F-008, F-009, F-013, F-014, F-020, F-021）
- **⚠️ 单源/增长差异**：4（F-002, F-003, F-010, F-015）
- **❌ 失败**：0

**核心声明全部通过核验，无 ❌ 项，bundle 状态 stable。**
