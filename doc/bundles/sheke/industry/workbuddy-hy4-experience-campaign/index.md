---
okf_version: "0.2"
type: bundle
title: "WorkBuddy × 混元 Hy4「体验官」征集活动：规则解构 Wiki 教程与参赛方案"
description: "混元 Hy4 真实体验官征集活动的完整规则知识包——72 条编号事实、70/20/10 评分公式与 521 名奖项算术、8 项投稿表单字段全解、8 类资格取消情形、四条机制洞察，以及基于 awesome-okf-xs 真实资产、按七概念方法论编排的定制参赛方案；flagged：全部事实为活动页单源、13 条官方口径缺口、1 项口径张力待确认。"
tags: ["workbuddy-hy4", "hunyuan-hy4", "体验官", "活动规则", "参赛方案", "七概念", "OKF"]
generated: { by: "process:seven-concepts-cmd", at: "2026-11-09T01:18:04Z" }
verified: [{ by: "process:seven-concepts-v", at: "2026-11-09T01:18:04Z" }]
status: flagged
stale_after: "2026-11-25"
sources:
  - id: activity-page
    resource: "https://www.workbuddy.link/p/tmLIChKEjyBNv8UQXxD29c?source=2"
    title: "WorkBuddy × 混元 Hy4「体验官」征集活动（活动公开页）"
  - id: artifact-html
    resource: "https://workbuddy-space-static.codebuddy.work/page/tmLIChKEjyBNv8UQXxD29c/axS-bAKLmFby/WorkBuddy混元Hy4真实体验官征集活动.html"
    title: "活动页正文静态产物（186,585 字节）"
  - id: state-tree
    resource: "https://workbuddy-space-static.codebuddy.work/page/tmLIChKEjyBNv8UQXxD29c/axS-bAKLmFby/janus.data.json"
    title: "页面状态树（235,566 字节，含 ruleHTML() 与 openForm() 定义）"
---

# WorkBuddy × 混元 Hy4「体验官」征集活动：规则解构 Wiki 教程与参赛方案

> **⚠️ flagged：全部事实为活动页单源。** 本包 72 条事实全部取自活动公开页自身的四个载体——页面首屏、`ruleHTML()` 返回的细则弹层全文、`openForm()` 定义的投稿表单、状态树内的时间轴常量与前端逻辑。无独立媒体信源、无可复核的官方 PDF 直链。另有 **13 条官方口径缺口（G-01~G-13）** 与 **1 项口径张力（C-03）**。引用本包任何规则、评分或表单细节时，须一并转述这一证据等级。
>
> **复核触发条件是「活动页公告变更」，而非日历到期**：细则两处写明「如有调整，以活动页公告为准」（F-005、F-006）。`stale_after: 2026-11-25` 仅为结果公示后的保守重新评估节点，不构成规则失效判定。

本知识包把一次「读完活动页 → 生成 Wiki 教程 → 给出参赛方案」的任务，拆成**可引用、可核验、可执行**五层：

| 层 | 承载 | 内容 |
|---|---|---|
| **事实层** | [01](concepts/01-campaign-facts.md)、[02](concepts/02-scoring-and-awards.md)、[03](concepts/03-submission-and-compliance.md)、[事实底账](references/facts.md) | 72 条编号事实逐条登记（F-001~F-072），覆盖主体与时间轴、70/20/10 评分与四档奖项、8 项表单字段、8 类资格取消情形、内容与知识产权条款 |
| **机制层** | [04 · 机制洞察](concepts/04-mechanism-insights.md) | 四条洞察，每条含**陈述 / 证据 / 反常识 / 行动**四元组；推断显式标注，不伪装成主办方口径 |
| **方案层** | [05 · 参赛方案](concepts/05-participation-plan.md) | 判型、资产盘点、三个选题候选、形态决策、材料依赖链、合规四层自查、七日倒排、阻塞决策点、待核清单 |
| **核验层** | [核验报告](references/verification.md) | 10 项核验结论、口径张力登记、单源清单、缺口影响评估、复核触发检测表 |
| **方法层** | [00 · 总览](concepts/00-overview.md) | 七概念 R→F→I→E→V→A→C 编排记录、编号图例、3 分钟上手卡 |

| 类别 | 数量 |
|---|---|
| 概念文档 | 6 |
| 信源参考 | 2 |
| 索引与日志 | 4 |
| **合计** | **12** |

## 内容导航

- [00 · 总览与阅读地图](concepts/00-overview.md) —— 七概念编排链路、编号图例、关键数字速查、3 分钟上手卡
- [01 · 活动事实与采集链路](concepts/01-campaign-facts.md) —— 主体、时间轴、五步流程、六类建议方向、SPA 四级取证链（F-001~F-025）
- [02 · 评分机制与奖项](concepts/02-scoring-and-awards.md) —— 70 分归一化公式、30 分绝对项、521 名算术、刷量红线（F-026~F-040）
- [03 · 投稿表单与合规条款](concepts/03-submission-and-compliance.md) —— 8 项字段逐条拆解、有效投稿门槛、8 类资格取消、内容与知识产权（F-041~F-072）
- [04 · 机制洞察](concepts/04-mechanism-insights.md) —— I-01 相对分与绝对分 / I-02 排除项清单 / I-03 窗口后核验 / I-04 过程证据的隐私成本
- [05 · 定制参赛方案](concepts/05-participation-plan.md) —— 判型结论、资产盘点、选题对位、形态决策、材料依赖链、合规四层、七日倒排、阻塞兜底、待核清单
- [事实底账 F-001~F-072](references/facts.md) —— 本包唯一事实来源；72 条事实 + 13 条缺口 + 8 条采集元数据
- [核验报告 C-01~C-10](references/verification.md) —— 核验结论、口径张力、勘误留痕、复核触发表

## 四条核心洞察速览

| 编号 | 洞察 | 落点 |
|---|---|---|
| I-01 | 70 分是**相对量**（分母由全场最高者定义），30 分才是**绝对量**；努力能直接控制的是后者 | 投入分配 |
| I-02 | 有效投稿是「排除项清单」而非「做完就有效」——社媒发布、标签、可见性、模型取证等并列全避 | 资格 |
| I-03 | 核验在投稿窗口**之后**且是快照，提交即定生死；发布到截止之间是唯一能影响 70 分的窗口 | 时序 |
| I-04 | 创作对话记录链接同时是过程证据与隐私成本，取证与脱敏必须成对完成 | 合规 |

## 主题关联互链

| 关联 bundle | 互链方向 |
|---|---|
| [workbuddy-1024-contest](../workbuddy-1024-contest/index.md) | **同型赛事直接对照**：同平台、同为活动页单源、同走「事实→机制→路径→方案」四层；可横向比对评分权重迁移（35/40/25 + 社媒 30 → 70/20/10）、有效作品口径与表单字段 |
| [zhihu-ai-science-workshop](../zhihu-ai-science-workshop/index.md) | **跨赛事对照**：双阶段预审型与本包单阶段投稿型的时序结构差异 |
| [ai-project-submission-and-content-publishing-guide](../ai-project-submission-and-content-publishing-guide/index.md) | **发布纪律对照**：版权时序、差异化写作、待核项登记 |
| [workbuddy-opc-whitepaper](../workbuddy-opc-whitepaper/index.md) | **平台层对照**：该束解 WorkBuddy 的产品定位，本包聚焦平台上的具体征集活动规则 |

## 已知边界

- **无 `examples/`**——信源为规则文本与前端表单定义，不含可复现的命令、版本与实际输出，未满足「操作可复现」两问；表单字段以概念页 [03](concepts/03-submission-and-compliance.md) 承载。
- **无获奖作品实证章节**——采集时点（2026-11-09）投稿计数为 0、作品墙停用（F-052、M-07）。
- **不含名次预测、获奖概率与评审口味**——评审机制与分数分布官方未披露（G-02），参赛方案严格遵守参赛作战手册的三条硬边界。
- **不把推断写成规则**——凡官方未给出的口径一律进 G 族，机制解读显式标注「洞察/推断」。
- **规则原文与推断分离**——本包未逐字读到的东西一律标「未读到 / 缺口」。
- **登记时点 2026-11-09**，处于征集期内，距 11-15 23:59 截止约 6 天 15 小时（M-01）。页面计数为快照，会漂移。
- **V 阶段对抗审查已落地修正**——首轮 7 条意见中 6 条采纳、1 条部分采纳，含「把社媒 70 分误读为传播打法」「把归一化分母当作可控变量」两项方向性纠偏，留痕见 [核验报告](references/verification.md)。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```
