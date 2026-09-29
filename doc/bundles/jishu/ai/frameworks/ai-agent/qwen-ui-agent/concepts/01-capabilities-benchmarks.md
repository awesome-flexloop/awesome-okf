---
type: Concept
title: 技术能力与基准成绩
description: Qwen-UI-Agent真机训练数据(100+设备/150+App/400+任务)、四项基准成绩(MobileWorld 82.1%/真机92.2%/安卓97.5%/WebArena 73.6%)、CLI批量动作(40%批量/58%勘误)、安全确认机制
tags: [Qwen-UI-Agent, 真机训练, MobileWorld, WebArena, 基准测试, CLI, 批量动作, 安全机制]
generated: { by: "blog-article-to-okf-bundle", at: "2026-08-28T23:45:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: wechat-article-renjianpanghuang
    resource: https://mp.weixin.qq.com/s/krPGm4HWX_uJwjQtWIRNCA
    title: 《阿里刚开源的 Qwen-UI-Agent》（人间彷徨，2026-08-26）
  - id: arxiv-2607-28227
    resource: https://arxiv.org/abs/2607.28227
    title: arXiv 2607.28227 官方技术报告
  - id: official-project-page
    resource: https://tongyi-mai.github.io/Qwen-UI-Agent/
    title: Qwen-UI-Agent官方项目主页
---

# 技术能力与基准成绩

> **事实基础**：本文所有具体数据与声明均带 F 编号，完整事实清单见 [references/article-source.md](../references/article-source.md)，核验结论见 [references/verification.md](../references/verification.md)。

## 1. 真机训练：非模拟器

Qwen-UI-Agent 的核心差异化在于**真机训练而非模拟器**（F-006）。官方技术报告和 GitHub README 确认了三项数据：

| 训练资源 | 数量 | 论文原文 |
|---------|------|---------|
| 真实手机 | 100+ 台 | "over 100 physical devices" |
| 真实 App | 150+ 款 | "more than 150 applications" |
| 真机评测任务 | 400+ 个 | "more than 400 tasks across over 100 apps"（MobileWorld-Real 基准） |

博文指出，同类产品"要么在模拟器里成绩好看、一上真机就翻车"，真机训练使 Qwen-UI-Agent 在真实环境中"不像很多同类那样一碰弹窗就懵"（F-005）。

## 2. 四项基准成绩

博文和官方技术报告均报告了四项基准测试成绩（F-007~F-010），经核验全部与官方数据吻合：

| 基准 | 成绩 | 说明 |
|------|------|------|
| **MobileWorld** | **82.1%** | 手机操作基准，比 GPT-5.6 Sol（70.1%）高 12.0 个点，比 Claude Opus 4.8（67.5%）高 14.6 个点 |
| **MobileWorld-Real（真机实测）** | **92.2%** | 真实设备上的实测成绩 |
| **AndroidDaily（安卓日常任务）** | **97.5%** | 接近满分 |
| **WebArena** | **73.6%** | 网页操作基准，官方图表显示在所有对比模型中排名第一 |

> **对比模型真实性已核验**（F-037）：
> - **GPT-5.6 Sol**：OpenAI 于 2026-07-09 全面开放，分 Sol/Terra/Luna 三档，Sol 为旗舰档
> - **Claude Opus 4.8**：Anthropic 于 2026-05-28 发布，100 万 token 上下文

> ⚠️ **分数为官方自报**（F-027）：博文特别提醒"这些分数是阿里自己测、自己报的，第三方独立复现还没出来"。引用时应标注为"阿里官方技术报告数据"。

## 3. CLI 执行与批量动作

Qwen-UI-Agent 不只点击界面，还能直接执行**命令行（CLI）指令**（F-011），且单次模型推理可批量输出多个动作（batched actions in a single model turn）。

### 批量动作比例（核验通过）

博文称"电脑任务里近四成动作是批量执行的"（F-012），核验确认论文原文为 **"over 40% of action outputs are batched"**（F-043），表述准确。

### 58% 步数节省（勘误）

> ⚠️ **F-033 勘误**：博文称"整体能省下约58%的操作步骤"，这一说法**以偏概全**。

arXiv 论文 §3.3.2 原文为：

> "On the more challenging OSWorld-v2... requiring **58.4%** and **21.7%** fewer steps per task."

实际含义：

| 对比基准 | 对比模型 | 步数减少 |
|---------|---------|---------|
| OSWorld-v2 | MiniMax M3 | 58.4% |
| OSWorld-v2 | Qwen 3.7 Plus | 21.7% |

58.4% 有两个限定条件：①仅限 OSWorld-v2 这一个基准；②仅相对于 MiniMax M3 这一个对比模型。博文将其简化为"整体省约58%"，扩大了适用范围。正确表述应为"在 OSWorld-v2 基准上，相比 MiniMax M3 减少约 58% 步数"。

## 4. 安全确认机制

Qwen-UI-Agent 设计了**高风险操作人工确认**机制（F-013），经论文和媒体报道交叉验证：

- **涉及资金操作**：如转账、发红包、支付——填好信息后停在支付步骤等用户确认
- **涉及数据删除**：删除文件、记录等操作前停手
- **涉及隐私授权**：权限申请、数据访问等需用户确认
- **违法/高风险请求**：直接拒绝执行

博文和 Pandaily 报道均引用了同一个案例：

> "给我妈发 500 红包"——它填好金额和备注，然后停在支付阶段等你点头（F-013）

论文描述为 "user takeover for high-risk actions"（高风险动作由用户接管）。博文同时提醒：部署者仍需主动配置确认节点，不可默认全授权（F-024）。

---

## 参考

- 完整事实清单：[references/article-source.md](../references/article-source.md)
- 核验报告：[references/verification.md](../references/verification.md)
- 项目概述与定位：[00-project-overview.md](00-project-overview.md)
- 实测踩坑与部署：[02-practice-and-pitfalls.md](02-practice-and-pitfalls.md)
- 3个内部流程实测：[examples/01-three-internal-workflows.md](../examples/01-three-internal-workflows.md)
