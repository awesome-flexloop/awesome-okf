---
okf_version: "0.2"
type: bundle
title: "Qwen-UI-Agent：开源GUI智能体技术评测"
description: "阿里通义2026年8月开源的Qwen-UI-Agent GUI智能体技术评测——真机训练、MobileWorld 82.1%基准成绩、CLI批量动作、3个内部流程实测、3个踩坑、部署勘误（MAI-UI权重混淆/58%以偏概全/硬件要求有误）"
tags: [Qwen-UI-Agent, MAI-UI, GUI智能体, Computer Use, Mobile Use, 开源, 阿里通义, 技术评测, RPA]
generated: { by: "blog-article-to-okf-bundle", at: "2026-08-28T23:45:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T23:45:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: wechat-article-renjianpanghuang
    resource: https://mp.weixin.qq.com/s/krPGm4HWX_uJwjQtWIRNCA
    title: 《阿里刚开源的 Qwen-UI-Agent，把"天天点屏幕"的活儿干没了？我们试了 3 个内部流程》（微信公众号"人间彷徨"，作者 wyzw，2026-08-26，原创）
  - id: arxiv-2607-28227
    resource: https://arxiv.org/abs/2607.28227
    title: arXiv技术报告 2607.28227（Qwen-UI-Agent官方论文）
  - id: github-tongyi-mai
    resource: https://github.com/Tongyi-MAI/MAI-UI
    title: GitHub仓库 Tongyi-MAI/MAI-UI（含MAI-UI和Qwen-UI-Agent两个子目录）
  - id: official-project-page
    resource: https://tongyi-mai.github.io/Qwen-UI-Agent/
    title: Qwen-UI-Agent官方项目主页
---

# Qwen-UI-Agent：开源GUI智能体技术评测

> **⚠️ 性质声明**：本 bundle 为**技术评测/选型类知识包**，以微信公众号"人间彷徨"博文的团队实测为事实基础，结合 arXiv 官方技术报告、GitHub 仓库、官方项目主页等权威来源核验。博文为第三方团队体验评测，非官方文档；3 个内部流程为作者团队自述实测（F-038），非官方 benchmark。核验中发现博文存在 **3 处需更正的问题**（MAI-UI 权重与 Qwen-UI-Agent 混淆、58% 步数节省以偏概全、硬件要求有误），已在 [references/verification.md](references/verification.md) 中如实记录，本 bundle 不照搬博文错误。

2026 年 8 月 20 日，阿里通义开源发布 **Qwen-UI-Agent**——一个能像人一样"看屏幕、点按钮、填表单"的 GUI 智能体，直接操作手机和电脑界面，而非通过 API 调用（F-002、F-003）。该项目基于 100 多台真机、150 多款真实 App 训练，在 MobileWorld 基准上达到 82.1%，超过 GPT-5.6 和 Claude Opus 4.8（F-006、F-007）。

本知识包梳理 Qwen-UI-Agent 的项目定位、技术能力、基准成绩、CLI 批量动作机制、安全确认机制，并收录第三方团队的 3 个内部流程实测结果和 3 个踩坑经验。**核验发现博文在开源权重和部署要求上有重要错误**，使用前请务必阅读已知边界。

---

## 信源说明

本知识包采用**博文+官方多源核验**结构：

| 信源 | 类型 | 覆盖范围 |
|------|------|---------|
| 微信公众号"人间彷徨"博文 | 主信源（第三方评测） | F-001 ~ F-031（博文全部事实与作者观点） |
| arXiv 2607.28227 | 官方技术报告 | 基准成绩、训练数据、CLI批量动作、安全机制核验 |
| GitHub Tongyi-MAI/MAI-UI | 官方代码仓库 | 开源协议、目录结构、requirements.txt 核验 |
| 官方项目主页 | 官方产品页 | 性能数据、能力范围、产品定位核验 |

核验中发现博文 3 处问题：①将前代 MAI-UI 1.0 的 2B/8B 权重当作 Qwen-UI-Agent 的权重（F-032、F-042）；②"整体省约58%步骤"实际仅限 OSWorld-v2 对比 MiniMax M3（F-033）；③"8B跑消费级显卡""Python 3.10+/PyTorch 2.0+"无官方依据（F-034）。完整核验报告见 [references/verification.md](references/verification.md)。

---

## 📚 知识结构总览

```
qwen-ui-agent/
├── concepts/              # 核心概念文档（3篇）
│   ├── 00-project-overview.md        # 项目概述与定位
│   ├── 01-capabilities-benchmarks.md # 技术能力与基准成绩
│   └── 02-practice-and-pitfalls.md   # 实测踩坑与部署
├── examples/              # 实战示例（1篇）
│   └── 01-three-internal-workflows.md # 3个内部流程实测
├── references/            # 信源登记簿（2篇）
│   ├── article-source.md  # F-001~F-044 事实完整登记
│   └── verification.md    # 8项核验结论与勘误说明
├── index.md               # 本文件
└── log.md                 # 生成日志
```

---

## 🧭 分层导航

### 概念层（concepts/）

| 文档 | 核心内容 |
|------|---------|
| [项目概述与定位](concepts/00-project-overview.md) | 8.20开源发布、GUI智能体定位、MAI-UI与Qwen-UI-Agent版本关系（含勘误）、四类能力覆盖、官方副标题 |
| [技术能力与基准成绩](concepts/01-capabilities-benchmarks.md) | 真机训练数据(100+设备/150+App/400+任务)、四项基准成绩表(MobileWorld 82.1%/真机92.2%/安卓97.5%/WebArena 73.6%)、CLI批量动作(40%/58%勘误)、安全确认机制 |
| [实测踩坑与部署](concepts/02-practice-and-pitfalls.md) | 3个踩坑(静默点错/长任务迷失/安全边界)、部署方式勘误(权重混淆/硬件要求)、适用人群、分数自报提醒 |

### 实战层（examples/）

| 文档 | 核心内容 |
|------|---------|
| [3个内部流程实测](examples/01-three-internal-workflows.md) | 财务对账导出(40分→5分)、运营日报搬运(85%成功率/弹窗卡点)、老CRM查单回复(无API场景最稳) |

### 信源层（references/）

| 文档 | 核心内容 |
|------|---------|
| [博文信源事实清单](references/article-source.md) | F-001~F-031 博文事实登记（元信息/产品/能力/开源/实测/踩坑/评价/观点8类）+ F-032~F-044 核验补充与勘误 |
| [核验报告](references/verification.md) | 8项核验逐项结论表（5✅ + 2⚠️ + 1❌），3项勘误详解，权威来源URL |

事实编号索引说明见 [references/index.md](references/index.md)。

---

## ✅ 信任与生命周期说明

- **文档版本**：基于 2026-08-26 发布的博文与 2026-08-28 完成的核验生成
- **覆盖事实**：共 44 条事实（F-001 ~ F-031 来自博文，F-032 ~ F-044 为核验补充）
- **核验情况**：8 项声明经 WebSearch + arXiv/GitHub 官方来源核验，5 项通过，2 项部分有误，1 项有误
- **status**：stable — 开源发布为已发生事实，技术规格经官方论文确认
- **stale_after**：2026-12-31 — AI Agent 领域迭代极快，Qwen-UI-Agent 权重尚未发布，后续版本更新可能改变评测结论
- **方法论链路**：R（事实采集）→ I（洞察提炼）→ E（信源先行成文）→ V（核验），详见 [log.md](log.md)

### 已知边界

1. **第三方评测性质**：博文为"人间彷徨"团队自述实测体验（F-038），非官方 benchmark，3 个内部流程无独立第三方验证。博文中的具体耗时（40分钟→5分钟）和成功率（85%）为该团队环境下的数据，不同场景结果可能差异很大。
2. **⚠️ 权重混淆勘误（F-032/F-042）**：博文称"MAI-UI-2B 和 8B 已在 Hugging Face 放出"并暗示这是 Qwen-UI-Agent 的权重。实际：Qwen-UI-Agent 是 MAI-UI 的**续作**（arXiv 脚注"continuation of previous work, MAI-UI"）；MAI-UI-2B/8B 是 2025 年 12 月发布的**前代模型**权重；**Qwen-UI-Agent 自身权重截至 2026-08-28 尚未公开发布**。代码框架 Apache 2.0 开源属实。
3. **⚠️ 58%步数节省以偏概全（F-033）**：博文称"整体能省下约58%的操作步骤"。实际：58.4% 出自 arXiv 论文 §3.3.2，**仅限 OSWorld-v2 基准且仅对比 MiniMax M3 一个模型**；对比 Qwen 3.7 Plus 仅减少 21.7%。"近四成动作批量执行"（over 40%）核验通过（F-043）。
4. **⚠️ 硬件要求有误（F-034）**：博文称"8B版本能跑在单张消费级显卡上""需 Python 3.10+ 和 PyTorch 2.0+"。实际：8B 是前代 MAI-UI 1.0 的版本，Qwen-UI-Agent 主力为 27B 稠密模型（4bit 量化约 17GB 可在 RTX 4090 运行）；requirements.txt 仅 4 项依赖（Jinja2/numpy/openai/Pillow），未指定 Python/PyTorch 版本；Qwen-UI-Agent 子目录尚无安装指南。
5. **分数为官方自报（F-027）**：博文提醒"分数是阿里自己测、自己报的，第三方独立复现还没出来"。MobileWorld 82.1%、真机 92.2%、安卓 97.5%、WebArena 73.6% 均为阿里官方技术报告数据，引用时应标注来源。
6. **产品快速迭代中**：Qwen-UI-Agent 于 2026-08-20 发布，权重尚未放出，API 托管服务也未上线（博文称"等托管"）。本 bundle 反映的是发布初期状态，后续功能、性能、授权方式可能变化。
7. **安全设计**：涉及钱/删数据/隐私授权时主动停手等确认（F-013）经核验属实（Alipay 红包案例），但博文和论文均提醒部署者需主动配置确认节点，不可默认全授权（F-024）。

---

**本知识包共收录 7 个内容文档（3 个概念 + 1 个示例 + 2 个信源 + 根索引），外加 3 个子目录索引与生成日志，合计 11 个文件。**

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
