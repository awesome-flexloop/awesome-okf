---
type: concept
title: "局限、口径差异与实践建议：如何正确引用 VISTA"
description: "论文自陈的局限、博文与论文的 8 项口径差异逐条对照、以及给不同读者的可操作建议——从'要不要用'到'引用这条结论时必须附带什么'。"
tags: [vista, limitations, errata, citation, adoption, practical-guide]
generated: { by: "opencode/minimax-m3.1-flash-free", at: "2026-10-20" }
verified:
  - { by: "process:seven-concepts-v", at: "2026-10-20" }
status: stable
stale_after: 2027-01-20
sources:
  - id: article-source
    resource: /references/article-source.md
  - id: verification
    resource: /references/verification.md
  - id: github
    url: "https://github.com/joshhhhhan/VISTA"
  - id: arxiv
    url: "https://arxiv.org/abs/2610.02200"
---

# 05 · 局限、口径差异与实践建议

## 一、论文自陈的局限（勘误 E-3 · 最重大的遗漏）

博文**完全没有提及**论文 §6 的局限。原文：

> "We acknowledge that the models' existing capabilities remain a key factor in this success… Additionally, because the models we use were **released after the public benchmarks**, we cannot rule out the possibility that these games were **included in their training data**. Evaluation on novel games, such as those in the **private set** of ARC-AGI-3, would provide a stronger test of our system's generalization." [F-068]

论文没有独立的 "Threats to Validity" 章节，§6 "Limitations" 是唯一的效度讨论。三条要点：

1. **模型能力仍是关键因素**——VISTA 只是"一种简单但有效的 eliciting 方式"，不是模型能力的替代品；
2. **数据污染不可排除**——所用模型在公开基准之后发布，无法排除这 25 个游戏已在训练数据中；
3. **私有集评估缺失**——真正更强的泛化检验需要 ARC-AGI-3 私有集，而私有集（半私有 55 + 完全私有 55）刻意与公开集分布外 [F-074]，且**不在任何公开仓库中**。

> **这条局限改变结论的读法**：正确的表述是"VISTA 在 ARC-AGI-3 **公开集**上取得了满分"，而不是"多模态模型已能在交互式视觉环境中达到人类水平"。

## 二、8 项口径差异逐条对照

| 编号 | 级别 | 博文表述 | 权威口径 | 本束处置 |
|------|------|---------|---------|---------|
| E-1 | ⚠️ 轻微 | 第三组件叫"主动视觉检查" | 论文 §3.1：visual inspection；图 3c：model-directed visual inspection | 正文按论文原词，并标注博文用词 |
| E-2 | ⚠️ 需修正 | 把 Anthropic 2025-11 harness 博文当作 VISTA 的直接脉络前史 | 该文存在且日期为 2025-11-26，但**论文未引用**；唯一 Anthropic 出处是 Claude Opus 5 模型公告 | 正文区分"博主叙述的脉络"与"论文实际引用" |
| E-3 | ❌ 重大 | 未提数据污染可能性与私有集评估要求 | §6 明确承认无法排除污染 | 正文显著位置补入 |
| E-4 | ⚠️ 需补充 | "63.3%""63.2%""99"无方差 | 附录 B.1：63.33±2.37% / 63.23±3.00% / 99.04±0.17 | 正文补入方差口径 |
| E-5 | ⚠️ 需补充 | 只说"满分 100" | 表1：官方实现 Opus 5.0 = 40.68、Sol = 13.33 | 正文补入基线→VISTA 提升幅度 |
| E-6 | ⚠️ 需精确 | "BabyVision 选取的 39 道题" | 全集 388 项任务 / 22 子类；39 为所评估子集（20 迷宫 + 19 连线） | 正文按论文精确表述 |
| E-7 | ⚠️ 需补充 | 未提代码 | GitHub `joshhhhhan/VISTA`，MIT License，含运行要求 | 正文补入 |
| E-8 | ⚠️ 时序 | 未区分项目页与论文 | 项目页（2026-08-05）数字系统性不同：7,542 动作 / 56% / Sol 98.27 / 基线 30.16；论文：7,302 / 57.4% / 99.00 / 40.68 | 正文一律以论文口径为准并标注差异来源 |

完整证据见 [核验报告 · 勘误清单](../references/verification.md)。

## 三、项目页 vs 论文：不要混用两套数字

| 指标 | 项目页（2026-08-05 blogpost） | 论文（2026-10-01 arXiv v1） | 本束采用 |
|------|---------------------------|---------------------------|---------|
| Opus 5.0 总动作数 | 7,542 | **7,302** | 论文 |
| 比人类基线少 | 56.0% | **57.4%** | 论文 |
| GPT-5.6 Sol RHAE | 98.27 | **99.00** | 论文 |
| 官方实现 Opus 5.0 基线 | 30.16 | **40.68** | 论文 |
| arXiv 链接 | **无**（arXiv 上线晚约 2 个月） | — | — |

两套数字**都自洽**（各自内部一致），差异源于实验迭代。博文引用的是**论文**口径 [F-047][F-049]，与项目页不同——引用时务必标明出处。

此外：arXiv 摘要的 Comments 字段记载"本稿早期版本曾发布于 2026-08-05 的 blogpost"，项目页页眉也标 "Aug 5, 2026"；而 Kaiming He 个人主页的论文列表标为 "Aug 6, 2026"——1 天差异，不影响任何结论。

## 四、给不同读者的行动建议

### 对研究者：怎么用这条结论

1. **引用时必带限定三件套**：基线（40.68 / 13.33）、数据污染不可排除、私有集表现未知 [F-064][F-068][F-074]。
2. **区分能力与编排**：消融阶梯证明同一模型下编排带来 13.33 → 99.00 [F-065]，报数时须固定模型。
3. **别把满分说成唯一**：Tycho 同样 100.00，Retrodict 99.86 [F-065]。
4. **注意方法边界**：3D 重渲染变体降到 84.12、动作数增至 20,640 [F-066]——结论对网格化 2D 环境最稳。

### 对工程师：要不要照着做

**可复制的部分**（不依赖 ARC-AGI-3）：

- 三层记忆结构 + 每层各自的清理策略（原始证据 / 跨任务结论 / 当前状态）[F-030][F-051][F-053]；
- 原始帧全量留存 + 按回合/帧号索引 + 只把最后一帧放进上下文 [F-032][F-051]；
- `inspect` 式工具的两个维度：跨时间取多帧对比 + 跨空间放大局部，外加精确像素读取 [F-052]；
- "预测—执行—对比"的回合闭环 [F-029]。

**需要谨慎的部分**：

- ARC-AGI-3 满分是**特定环境**的结果，不是通用能力证明 [F-068]；
- 官方实现基线本身就有 40.68——**很多场景的瓶颈不在 harness**，先测基线再决定投入。

### 对读者：怎么判断一条"满分"新闻

| 维度 | 问什么 | 本案例的答案 |
|------|-------|------------|
| 基线 | 提升了多少？从多少到多少？ | 40.68 → 100.00（Opus 5.0）[F-064] |
| 污染 | 模型发布时间 vs 基准发布时间？ | 模型更晚，无法排除污染 [F-068] |
| 泛化 | 未见题目上如何？ | 未知，私有集未测 [F-068][F-074] |
| 方差 | 多次运行稳定吗？ | ARC ±0.17；GameWorld ±2.37% [F-067] |
| 竞争者 | 有别的路线同样好吗？ | Tycho 100.00、Retrodict 99.86 [F-065] |
| 可复现 | 代码/数据可得吗？ | 代码 MIT 开源；私有集不可得 [F-075][F-074] |

### 对二手资讯读者：本案例的方法论价值

这个案例本身是一个"**如何读一条高分技术新闻**"的完整样本：

- 博文的**转述质量高**——18 项 P0 声明中 14 项完全准确，核心数字全部与论文一致；
- 但博文的**筛选有偏**——省掉了论文自己写明的局限、基线、方差，以及代码开源这一最具行动价值的信息；
- 因此正确的做法不是"相信博文"或"怀疑博文"，而是**顺藤摸瓜到一手论文**：博文给出的 arXiv 链接就是入口，而项目页与论文的两套数字差异恰好演示了为什么必须回到版本化的一手源。

## 五、开源资产与运行要求

代码已开源，MIT License [F-075]：

| 项 | 要求 |
|----|------|
| 仓库 | `github.com/joshhhhhan/VISTA` |
| 许可 | MIT License |
| 操作系统 | Linux x86_64 |
| Python | 3.12 |
| 容器 | Docker Engine |
| Agent CLI | Codex CLI 0.145.0 或 Claude Code 2.1.220 |
| 批量运行 | 另需 `tmux` |
| 操作模式 | `online` / `competition` / `offline` |
| 公开样例 | `.venv/bin/vista --profile arc3 --backend codex --game-id s5i5 --operation-mode online --model gpt-5.6-sol --effort max`；批量 `./scripts/run_batch.sh --runtime claude --mode online --model opus --effort xhigh -j 2` |
| 其他基准 | 另有 `--profile gameworld` / `aigamestore` / `babyvision` 流程 |

> 上述命令为**仓库 README 原文**引用，非本束改写；实际执行前请以仓库当前 README 为准（CLI 版本号具有时效性）。

## 六、时效性声明

| 项 | 状态 | 复核建议 |
|----|------|---------|
| 论文与项目页数字 | 稳定（版本化） | 无需复核，除非论文出 v2 |
| ARC-AGI-3 公开集成绩 | 随新模型发布变化 | 引用前查 ARC Prize 官方记分卡 [F-076] |
| 模型版本与 CLI 版本号 | **易过期** | `stale_after` 前复核仓库 README |
| 基准排行榜 | 持续变动 | "此前最好成绩"仅代表论文发表时点 |
| 仓库 star 数等瞬时计数 | 不作为稳定事实收录 | — |

## 相关

- [事实登记](../references/article-source.md) · [核验与勘误](../references/verification.md) · [知识地图](../references/knowledge-map.md)
- [AI 工程方法论]](../../../practice/ai-engineering-methodology/index.md)：Harness 工程与 Agent 评测谱系
