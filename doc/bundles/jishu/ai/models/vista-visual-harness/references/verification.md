---
type: reference
title: "VISTA 博文 P0 核验报告与勘误"
description: "对量子位 VISTA 博文的双轮独立权威核验记录——18 项 P0 声明逐条对照 arXiv 论文、项目页、GitHub 仓库与 ARC Prize 官方方法学，附 8 项勘误（E-1~E-8）。"
tags: [vista, verification, errata, arxiv, arc-prize, provenance]
generated: { by: "opencode/minimax-m3.1-flash-free", at: "2026-10-20" }
verified:
  - { by: "process:seven-concepts-v", at: "2026-10-20" }
status: stable
stale_after: 2027-01-20
sources:
  - id: blog
    url: "https://mp.weixin.qq.com/s/3S5OW6ytgz27zrq4UgCkgQ"
  - id: arxiv
    url: "https://arxiv.org/abs/2610.02200"
  - id: arxiv-html
    url: "https://arxiv.org/html/2610.02200v1"
  - id: project
    url: "https://vista-research.github.io/"
  - id: github
    url: "https://github.com/joshhhhhan/VISTA"
  - id: arc-methodology
    url: "https://docs.arcprize.org/methodology"
  - id: arc-agi3-paper
    url: "https://arxiv.org/abs/2603.24621"
  - id: anthropic-harness
    url: "https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents"
---

# VISTA 博文 P0 核验报告与勘误

> **核验结论摘要**：博文对论文核心声明的转述**准确率高**——ARC-AGI-3 满分 100、动作数少 57.4%、GPT-5.6 Sol 得分 99、三组件机制、双笔记结构等 P0 声明均与论文原文一致。但存在 **1 项重大遗漏（论文自身的局限）、1 项归因越界、6 项口径/上下文省略**，均在本报告逐条落地。
> **状态判定**：`stable`（非 `flagged`）——核心声明全部通过独立核验，无需降级；勘误完整落实。
> **核验方式**：两轮独立上下文子代理分别对照 arXiv HTML 全文 + LaTeX 源码包、官方项目页、GitHub 仓库、ARC Prize 官方方法学与各作者机构主页取证。

## 一、P0 声明核验结果（18 项）

| # | 声明 | 结论 | 权威源证据 |
|---|------|------|-----------|
| P0-01 | 论文为《VISTA: A Visual Harness for Reasoning in an Interactive World》 | ✅ | arXiv:2610.02200，2026-10-01 提交，MIT，CC BY 4.0 |
| P0-02 | 三个核心组件为视觉观测 / 无损视觉记忆 / 视觉检查 | ⚠️ | §3.1 原文：visual observations / lossless visual memory / **visual inspection**。博文第三项作"主动视觉检查"，"主动"非论文用词 → **E-1** |
| P0-03 | 每一帧原样存到上下文之外，含动画中间帧，按回合号与帧号索引 | ✅ | §3.1 + §1："stores every frame returned by the environment, including intermediate animation frames, in its original form… indexed by turn and frame number" |
| P0-04 | Claude Opus 5.0 在 ARC-AGI-3 相对人类动作效率得分 100.00，完成全部 25 个公开游戏 | ✅ | 摘要 + §4.2 + 表1；官方记分卡可独立核验 |
| P0-05 | 所用动作数比首次游玩的人类基线少 57.4% | ✅ | §4.2："uses **7,302 actions** in total, **57.4% fewer** than the human reference of **17,135 actions**" |
| P0-06 | GPT-5.6 Sol 同样全部通关，得分 99 | ✅ | §1 + 表1 + 表2 题注：RHAE **99.00**，max reasoning effort |
| P0-07 | GameWorld 170 项任务成功率 40.0% → 63.3% | ✅ | §5.1（34 个浏览器游戏 / 170 任务 / 5 类题材）+ 图11 |
| P0-08 | AI GameStore 10 个游戏综合得分 47.3 → 140.3，人类中位数归一化为 100 | ✅ | §5.1 + 附录 A.3 公式5/6 + 图11。注：为**逐游戏归一化后的几何平均**，非原始分求和 |
| P0-09 | BabyVision 39 道迷宫与连线题准确率 41.0% → 63.2% | ⚠️ | §5.2 数字正确；但 BabyVision 全集为 **388 项任务 / 22 子类**，39 是所评估子集 → **E-6** |
| P0-10 | 64×64 画面放大为 512×512 PNG | ✅ | §4.3："a **512×512 PNG image**… obtained by **8× nearest-neighbor upscaling of the official 64×64 frame**" |
| P0-11 | inspect 工具可指定历史回合取画面、裁剪放大、多帧对比 | ✅ | 附录 A.4 算法1 + §3.1；另有 read_pixels 返回精确 RGB 值 |
| P0-12 | GUIDE.md 记跨关卡可复用规则，WORKING.md 记当前关卡状态与计划 | ✅ | §3.2 + 附录 A.2；A.4 补充 WORKING.md 跨 RESET 与上下文重启保留、关卡推进后清空 |
| P0-13 | 默认每次动作后只向模型展示最后一帧，中间帧归档待调 | ✅ | 图5 题注 + 附录 A.2 + 算法1 |
| P0-14 | VISTA 不训练任何新模型，只改变视觉信息的获取/保存/使用方式 | ✅ | §3.2："The harness is purely mechanical and **does not involve any trained model**" |
| P0-15 | 论文研究问题表述与"显式注意力"概念 | ✅ | §3.1："an *explicit attention mechanism* over the interaction history"；摘要 "long-horizon vision" |
| P0-16 | 既有做法为文本网格 + 代码世界模型；早期画面会被移出上下文或摘要替代 | ✅ | §4.2 + §4.3 + §1 + §3 |
| P0-17 | 未来方向为更接近物理世界的具身任务 | ✅ | §7："such as embodied tasks in environments that more closely resemble the physical world" |
| P0-18 | 作者名单与共同第一作者标注 | ⚠️ | 论文脚注为 "*Co-first authors.*"，项目页渲染为 "*co-leads*"；同事实两种表述。Qiushi Han 在 MIT ORC 名录登记名 **Josh Han**（邮箱与论文通讯一致） |

**附加核验（非 P0 但影响可信度）**：

- **Anthropic 脉络归因**：Anthropic《Effective harnesses for long-running agents》确实发布于 **2025-11-26**，含特性清单文件、`claude-progress.txt` 进度文件与 git 提交保存已完成工作 → 博文"去年 11 月"表述**成立**。但 **VISTA 论文并未引用该文**（64 条参考文献中唯一 Anthropic 出处是 Claude Opus 5 模型公告）→ **E-2**。
- **基线缺失**：博文只给"满分 100"，未给官方实现基线。论文表1：官方实现 Opus 5.0 RHAE **40.68**、GPT-5.6 Sol RHAE **13.33**（10,619 动作）→ **E-5**。
- **多次运行方差缺失**：附录 B.1 → GameWorld 63.33±2.37%、BabyVision 63.23±3.00%、ARC-AGI-3 Sol 99.04±0.17 → **E-4**。
- **论文局限完全缺失**：§6 数据污染可能性与私有集评估要求 → **E-3**（本报告最重大的遗漏项）。
- **代码已开源未提**：GitHub `joshhhhhan/VISTA`，MIT License → **E-7**。

## 二、勘误清单（E-1 ~ E-8）

| 编号 | 级别 | 类型 | 源文表述 | 权威口径 | 处置 |
|------|------|------|---------|---------|------|
| **E-1** | ⚠️ 轻微 | 术语偏差 | "主动视觉检查" | 论文 §3.1：`visual inspection`（图3c：`model-directed visual inspection`） | 正文按论文原词呈现，并标注博文用词 |
| **E-2** | ⚠️ 需修正 | 归因越界 | 将 Anthropic 2025-11 harness 博文作为 VISTA 直接脉络前史叙述 | 该文存在且日期为 2025-11-26，但论文未引用 | 正文区分"博主叙述的脉络关联"与"论文实际引用" |
| **E-3** | ❌ 重大 | 关键局限缺失 | 未提及数据污染可能性 | §6：模型在公开基准之后发布，无法排除游戏已入训练数据；需私有集评估 | 正文显著位置补入，作为"满分 100"的必要限定 |
| **E-4** | ⚠️ 需补充 | 口径省略 | "63.3%""63.2%""99"无方差 | 附录 B.1：63.33±2.37% / 63.23±3.00% / 99.04±0.17 | 正文补入方差口径 |
| **E-5** | ⚠️ 需补充 | 基线缺失 | 只说"满分 100" | 表1：官方实现 Opus 5.0 = 40.68，GPT-5.6 Sol = 13.33 | 正文补入基线→VISTA 的提升幅度 |
| **E-6** | ⚠️ 需精确 | 范围口径 | "BabyVision 选取的 39 道题" | 全集 388 项任务 / 22 子类；39 为所评估的 20 迷宫 + 19 连线子集 | 正文按论文精确表述 |
| **E-7** | ⚠️ 需补充 | 资产遗漏 | 未提代码 | GitHub `joshhhhhan/VISTA`，MIT License，含运行要求 | 正文补入（读者可行动性最高的信息） |
| **E-8** | ⚠️ 时序 | 版本差异 | 未区分项目页与论文 | 项目页（2026-08-05）数字系统性不同：7,542 动作 / 56% / Sol 98.27 / 基线 30.16；论文：7,302 / 57.4% / 99.00 / 40.68 | 正文一律以论文口径为准并标注项目页差异来源 |

## 三、核心声明与"不可省略的限定"三件套

引用 ARC-AGI-3 满分 100 这一结论时，必须同时给出：

1. **基线**：官方实现 Opus 5.0 RHAE 40.68、GPT-5.6 Sol 13.33 [F-064]
2. **数据污染可能性**：模型在公开基准之后发布，作者无法排除游戏已入训练数据 [F-068]
3. **未见题目上的表现**：需在 ARC-AGI-3 私有集（半私有 55 + 完全私有 55，且刻意与公开集分布外）上评估 [F-074]

## 四、RHAE 计分口径（官方方法学）

- 单关得分 = （人类基线动作数 / AI 动作数）²
- 单关上限：人类基线的 **1.15 倍**
- 未通关关卡计 **0**
- 游戏得分：各关得分的**加权平均**（以关卡序号 1-indexed 为权重）
- 总分：各游戏分的**平均**，最终落在 0%–100%
- 人类基线：每关"动作数最少者"的**上中位数**（upper median human）

> 这意味着"满分 100"要求完成全部 25 个游戏的全部关卡（含最后一关），而非部分关卡的高分累加。

## 五、核验未覆盖的边界

- 未验证 ARC-AGI-3 私有/半私有游戏环境（不在任何公开仓库，需 API key 授权）——本束不收录，仅引用其公开构成数据。
- 未复现论文实验（需付费模型 API + Docker 环境 + 大量算力）；所有实验数字均为**转述论文**，未独立重跑。
- 论文图11 的结果面板在 arXiv HTML 中缺失（仅渲染截图行），数值取自 arXiv LaTeX 源码包的 `figures/fig_results.pdf`，并由 §5.2 与附录 A.6 的人类参考值交叉印证。
- 未独立核验各基准论文本身的方法论质量（GameWorld / AI GameStore / BabyVision），仅核验 VISTA 论文对它们的引用与口径。
- 官方项目页标注 "Aug 5, 2026"，而 Kaiming He 个人主页的论文列表标注该 blogpost 为 "Aug 6, 2026"——日期存在 1 天差异，不影响任何结论，本束统一采用 arXiv Comments 字段的 2026-08-05。

## 六、关联

- 事实登记：[article-source.md](article-source.md)
- 知识地图：[knowledge-map.md](knowledge-map.md)
- 信源边界：[source-manifest.md](source-manifest.md)
