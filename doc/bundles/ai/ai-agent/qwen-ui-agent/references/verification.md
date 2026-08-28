---
type: Reference
title: 核验报告
description: 8项P0声明逐项核验——5项通过、2项部分有误、1项有误，含MAI-UI权重混淆、58%步数节省以偏概全、硬件要求有误3项勘误详解及权威来源URL
tags: [核验, 勘误, P0, arXiv, GitHub, 官方来源]
generated: { by: "blog-article-to-okf-bundle", at: "2026-08-28T23:45:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: arxiv-2607-28227
    resource: https://arxiv.org/abs/2607.28227
    title: arXiv 2607.28227 官方技术报告
  - id: arxiv-html
    resource: https://arxiv.org/html/2607.28227v1
    title: arXiv 2607.28227 HTML全文
  - id: github-tongyi-mai
    resource: https://github.com/Tongyi-MAI/MAI-UI
    title: GitHub Tongyi-MAI/MAI-UI
  - id: github-requirements
    resource: https://raw.githubusercontent.com/Tongyi-MAI/MAI-UI/main/MAI-UI/requirements.txt
    title: MAI-UI requirements.txt
  - id: official-project-page
    resource: https://tongyi-mai.github.io/Qwen-UI-Agent/
    title: Qwen-UI-Agent官方项目主页
  - id: aibase-report
    resource: https://www.aibase.com/news/30530
    title: AIbase报道
  - id: gpt-56-stats
    resource: https://llm-stats.com/models/gpt-5.6-sol
    title: GPT-5.6 Sol信息
  - id: claude-opus
    resource: https://www.anthropic.com/claude/opus
    title: Claude Opus官方页
---

# 核验报告

> 核验时间：2026-08-28
> 核验方法：WebSearch 权威来源检索 + arXiv 官方技术报告 + GitHub 仓库文件直读 + 官方项目主页交叉验证

## 核验结论总表

| # | 核验项 | 博文声明（F编号） | 结论 | 说明 |
|---|--------|------------------|------|------|
| 1 | 开源发布 | 2026-08-20阿里通义开源发布（F-002） | ✅ 通过 | arXiv 2607.28227、GitHub、官方页三方确认 |
| 2 | 真机训练数据 | 100+设备/150+App/400+任务（F-006） | ✅ 通过 | 论文原文逐字一致 |
| 3 | 基准测试成绩 | MobileWorld 82.1%等四项（F-007~F-010） | ✅ 通过 | 全部与官方数据吻合，对比模型真实存在 |
| 4 | CLI批量动作 | 近四成批量+58%步数节省（F-012） | ⚠️ 部分有误 | 40%批量通过；58%以偏概全 |
| 5 | 安全机制 | 钱/删数据/隐私停手确认（F-013） | ✅ 通过 | 论文+Pandaily案例确认 |
| 6 | 产品定位 | GUI智能体非聊天机器人（F-003） | ✅ 通过 | 官方副标题和定位描述一致 |
| 7 | 开源权重与仓库 | HF放2B/8B权重+GitHub（F-014） | ⚠️ 部分有误 | 代码开源属实，但权重混淆两代产品 |
| 8 | 硬件要求 | 8B消费级显卡/Python 3.10+/PyTorch 2.0+（F-016/F-017） | ❌ 有误 | 8B是旧版，软件版本无官方依据 |

**总计：5✅ + 2⚠️ + 1❌**

---

## 重点核验项详解

### ⚠️ 勘误 1：模型命名与权重混淆（F-014/F-032/F-042）

**博文说法**："MAI-UI-2B 和 8B 两个版本已在 Hugging Face 放出"，暗示这是 Qwen-UI-Agent 的权重。

**实际情况**：

1. arXiv 论文脚注明确写道："Qwen-UI-Agent is a continuation of our previous work, MAI-UI."——Qwen-UI-Agent 是 MAI-UI 的**续作**，不是同一产品。
2. MAI-UI-2B/8B 于 **2025-12-29** 发布，是基于 Qwen3-VL 的 **1.0 旧版模型**。
3. Qwen-UI-Agent 基于 Qwen 3.5 系列，据 AIbase 等媒体报道提供 4B/27B/35B-A3B 版本（主力 27B），但**截至 2026-08-28，Qwen-UI-Agent 自身权重尚未在 HuggingFace 发布**。
4. GitHub 仓库 `Tongyi-MAI/MAI-UI` 同时含两个子目录：`MAI-UI/`（1.0版）和 `Qwen-UI-Agent/`（新版框架）。Qwen-UI-Agent 子目录目前仅 README、assets 和技术报告 PDF。
5. Apache 2.0 开源协议正确，代码框架确实开源。

**影响**：博文标题"开源"部分属实（代码开源），但读者若按博文指引下载 MAI-UI-2B/8B 权重，得到的是前代模型，不等于博文中报告的 Qwen-UI-Agent 基准成绩。

### ⚠️ 勘误 2：58% 步数节省以偏概全（F-012/F-033）

**博文说法**："整体能省下约58%的操作步骤"。

**实际情况**：

arXiv 论文 §3.3.2 原文：

> "On the more challenging OSWorld-v2... requiring **58.4%** and **21.7%** fewer steps per task."

58.4% 的两个限定条件：
- 仅限 **OSWorld-v2** 这一个基准（非"整体"）
- 仅相对于 **MiniMax M3** 这一个对比模型

相对于 Qwen 3.7 Plus，步数减少仅为 **21.7%**。

"近四成动作批量执行"（over 40% of action outputs are batched）核验通过。

### ❌ 勘误 3：硬件要求与软件版本（F-016/F-017/F-034）

**博文说法**："8B版本能跑在单张消费级显卡上""需Python 3.10+和PyTorch 2.0+"。

**实际情况**：

1. **8B 是旧版模型**：8B 规格属于 MAI-UI 1.0（2025-12-29发布），不是 Qwen-UI-Agent。Qwen-UI-Agent 主力为 27B 稠密模型。
2. **27B 显存需求**：BF16 精度约 54GB 显存；4bit 量化约 17GB，理论上可在 RTX 4090（24GB）运行。但权重尚未发布，实际需求待确认。
3. **requirements.txt 仅 4 项**：
   ```
   Jinja2==3.1.6
   numpy==2.3.5
   openai==2.13.0
   Pillow==12.0.0
   ```
   - 未指定 Python 版本下限
   - 未将 PyTorch 列为直接依赖
   - 无 "Python 3.10+" 或 "PyTorch 2.0+" 的官方依据
4. Qwen-UI-Agent 子目录目前**无安装指南**，仅有 README 和技术报告 PDF。

---

## 已通过项简要说明

### 1. 开源发布（F-002）✅

- arXiv 技术报告 2607.28227 提交于 2026-07-30
- GitHub 仓库 Tongyi-MAI/MAI-UI 存在，Apache 2.0 协议
- 官方项目主页 https://tongyi-mai.github.io/Qwen-UI-Agent/
- 2026-08-20 为对外公开发布日，AIbase 等媒体 8月21-22日报道

### 2. 真机训练数据（F-006）✅

论文原文逐字一致：
- "over 100 physical devices"（100+真机）
- "more than 150 applications"（150+App）
- "more than 400 tasks across over 100 apps"（400+任务）

### 3. 基准测试成绩（F-007~F-010）✅

| 基准 | 博文数据 | 官方数据 | 一致 |
|------|---------|---------|------|
| MobileWorld | 82.1% | 82.1% | ✅ |
| MobileWorld-Real | 92.2% | 92.2% | ✅ |
| AndroidDaily | 97.5% | 97.5% | ✅ |
| WebArena | 73.6% | 73.6% | ✅ |

对比模型：
- GPT-5.6 Sol：2026-07-09 发布，70.1%（差12.0点），真实存在
- Claude Opus 4.8：2026-05-28 发布，67.5%（差14.6点），100万token上下文，真实存在

### 4. CLI 批量动作（部分通过）✅

- CLI 执行能力：论文确认
- 批量动作（batched actions）：论文确认
- "over 40% of action outputs are batched"：与博文"近四成"一致 ✅
- 58% 步数节省：见勘误2 ⚠️

### 5. 安全机制（F-013）✅

- 论文："user takeover for high-risk actions"
- Pandaily 报道：Alipay 500元红包案例——填好金额停在支付步骤
- 涉及资金、删除数据、隐私授权三类高风险操作

### 6. 产品定位（F-003）✅

- 官方副标题："Towards Next-Generation Real-World Centric Foundation GUI Agent"
- 论文定位："general purpose executor over existing digital devices"
- 四类能力：Mobile GUI Use / Computer Use / Browser Use / DeepSearch

---

## 核验来源汇总

| 来源 | URL | 用途 |
|------|-----|------|
| arXiv 技术报告 | https://arxiv.org/abs/2607.28227 | 基准成绩/训练数据/CLI/安全机制/版本关系 |
| arXiv HTML全文 | https://arxiv.org/html/2607.28227v1 | 58%数据原文/脚注续作声明 |
| GitHub 仓库 | https://github.com/Tongyi-MAI/MAI-UI | 目录结构/开源协议/requirements.txt |
| requirements.txt | https://raw.githubusercontent.com/Tongyi-MAI/MAI-UI/main/MAI-UI/requirements.txt | 4项依赖核实 |
| 官方项目主页 | https://tongyi-mai.github.io/Qwen-UI-Agent/ | 产品定位/性能数据/能力范围 |
| AIbase 报道 | https://www.aibase.com/news/30530 | 发布时间/模型规格报道 |
| GPT-5.6 信息 | https://llm-stats.com/models/gpt-5.6-sol | 对比模型版本核实 |
| Claude Opus | https://www.anthropic.com/claude/opus | 对比模型版本核实 |
