---
okf_version: "0.2"
type: Reference
title: "OpenCreator P0 核验报告（verification）"
description: "对博文核心声明的逐项 P0 权威核验——数量/能力/日期/许可等，独立权威信源优先"
tags: [opencreator, verification, p0, authoritative-source]
generated: { by: "wechat-public-okf:P0", at: "2026-10-10T12:10:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: "https://mp.weixin.qq.com/s/oecbF0OUAKYSZfbI6WsKfA"
    title: "1.2万 Star 爆火，来看看这款顶级的一站式 Agent 创作神器"
    account: AI开源无界
  - id: github-api
    url: "https://api.github.com/repos/krillinai/OpenCreator"
    title: "GitHub API 仓库元数据"
  - id: github-repo
    url: "https://github.com/krillinai/OpenCreator"
    title: "OpenCreator README"
---

# OpenCreator P0 核验报告（verification）

> 核验原则：对**数量、百分比、排名、结果主张**、**官方声明/引用研究**、**被表述为普遍或科学的论断**逐条核验。尽量引用独立权威 URL；否则标记 `single-source` 或 `single-source/flagged`。**绝不把信源作者的声明升级为研究事实。**

## P0 核验结论总览

博文核心声明共 **24 项 P0** 核验结果：**18 ✅ / 5 ⚠️ / 1 ❌（作者判断超纲）**，无不实硬伤 ，技术参数高度精准。

## 逐条核验表

| # | 声明（引用事实号） | 类型 | 核验结果 | 权威依据 |
|---|-------------------|------|---------|---------|
| 1 | Star 约 1.2 万（F-001） | 数量 | ✅ | GitHub API 2026-10-10 快照 = 12,671 |
| 2 | 前身 KrillinAI（F-004） | 官方声明 | ✅ | README「OpenCreator was formerly known as KrillinAI」 |
| 3 | 仓库 2024 年底创建（F-005） | 日期 | ✅ | GitHub API created_at = 2024-12-17 |
| 4 | 本地自用无需云服务（F-006） | 结果主张 | ✅ | README「keep creative and development work running locally」 |
| 5 | 视频翻译 14 源 / 101 目标语言（F-008） | 数量 | ✅ | README「14 source languages and 101 target languages」 |
| 6 | 转写支持 Whisper / faster-whisper / WhisperKit（F-009） | 能力声明 | ✅ | README 语音与转写表 + 本地转写补充 |
| 7 | 46 分钟视频一键出完整字幕（F-013） | 结果主张 | ✅ | README「对一段 46 分钟的本地视频进行一键处理…没有字幕遗漏或重叠」 |
| 8 | 视频下载 9 平台（F-014） | 数量/能力 | ✅ | README 视频下载行列出 YouTube/Bilibili/X/TikTok/Instagram/Douyin/Facebook/Xiaohongshu/Pinterest |
| 9 | 视频下载列格式、可只下音频（F-015） | 能力声明 | ✅ | README「inspect available quality and format options, and download video or audio」 |
| 10 | 小红书需完整长链、短链不支持（F-016） | 能力声明 | ⚠️ | 官方仅言「Some sources may require platform cookies」；短链细节为作者补充 |
| 11 | 火柴人动画用 Harbor Hsia 合作原创角色（F-017） | 归属声明 | ⚠️ | 官方称「consistent-character storyboard visuals」；Harbor Hsia 姓名未独立核验（single-source） |
| 12 | 视频生成走 Seedance、版本不覆盖（F-019） | 能力声明 | ✅ | README「Generate videos with Seedance…preview, regenerate, and download each version」 |
| 13 | 配音可接 OpenAI TTS/MiniMax/Edge TTS/阿里云/火山引擎（F-021） | 能力声明 | ✅ | README 语音表逐项对应 |
| 14 | Edge TTS 无需密钥（F-022） | 结果主张 | ⚠️ | Edge TTS 通常免密钥，但"免密钥"为作者判断，未独立核验（single-source） |
| 15 | Agent 用 Codex CLI 执行引擎、未自造循环（F-024） | 官方声明 | ✅ | README「uses Codex CLI as the execution engine instead of reimplementing an Agent loop」 |
| 16 | Agent 复用 Codex 模型/工具调用/Skills/MCP（F-025） | 官方声明 | ✅ | README Codex Native 定义 |
| 17 | 双模式共用状态机、版本化（F-026/F-027） | 能力声明 | ✅ | README Dual-Mode Workflow + Versioning |
| 18 | 记忆全局/项目/对话三层（F-030） | 能力声明 | ✅ | README「global, project, and thread memory」 |
| 19 | 语言模型清单（F-031） | 数量/能力 | ✅ | README 语言模型表（博文遗漏 Grok，本包补充） |
| 20 | 国内模型走 OpenAI 兼容接口接入（F-032） | 能力声明 | ✅ | README「OpenAI-compatible provider」 |
| 21 | 桌面版自带 Codex CLI（F-036） | 能力声明 | ✅ | README「with Codex CLI included」 |
| 22 | Node 22+ / pnpm 9.15.0 / 端口 19861（F-038/F-039） | 技术细节 | ⚠️ | 官方确认 pnpm workspace；Node 22/pnpm 版本/端口须以官方开发文档为准（single-source） |
| 23 | 单 Agent 任务 10-20 万 token（F-040） | 数量估算 | ⚠️/❌ | 社区测试估算，非官方数字（single-source/flagged，作者基调"建议小任务试水"合理但数字不可据此采信） |
| 24 | 本地数据 + SQLite + 127.0.0.1 + token 鉴权（F-041/F-042） | 安全声明 | ⚠️ | 官方 Local Security「keep data local / redacted diagnostics」一致；.runtime 目录、SQLite、逐接口 token 为博文细节（single-source） |

## 勘误与补充（四张清单）

### 硬错误（❌，导致事实失真）
- **无**。博文无核心硬错误。

### 时效勘误（⚠️，动态数字需带时点）
1. Star：博文"1.2 万"为成文口径，本包采用官方现值 **12,671（2026-10-10）**，引用动态数字须带时点。

### 信息补充（博文未提及，官方已确认）
1. **许可**：博文未提，官方为 **Apache-2.0**（F-046）。
2. **技术栈**：TypeScript monorepo（pnpm workspace），顶层含 `apps/`、`packages/`、`skills/`（F-045/F-049）。
3. **两个开发中工具**：Auto Clips、Digital Avatar（博文只说 10 个工具，官方列表另有 2 个 In development）（F-050）。
4. **语言模型 Grok**：博文清单遗漏 Grok（xAI）（F-054）。
5. **图像/视频/语音模型明细**：图像 GPT Image/Seedream 4.0/Kling v2.1/Nano Banana；视频 Seedance 2.5/Kling v2.1 Master/Veo 3.1；本地转写另含 whisper.cpp（F-052/F-053）。
6. **界面多语言**：简中/英文/瑞典语，自动探测或手动选择（F-051）。

### 需复核项（single-source，后续核验）
- Harbor Hsia 合作角色归属（F-017）。
- 端口 19861 / Node 22 / pnpm 9.15.0 / .runtime / SQLite / 逐接口 token（F-039/F-041/F-042）。
- 单 Agent 任务 token 估算（F-040）。

## 核验方法

- 官方一手：GitHub REST API 元数据（Star/Fork/Issues/许可/语言/日期/主页）+ 官方 README.md。
- 采集时点：2026-10-10。
- 不升级声明：凡无独立权威信源的作者判断（Harbor Hsia、token 估算、端口细节），一律标记 single-source/flagged，不写入概念文档为既定事实。