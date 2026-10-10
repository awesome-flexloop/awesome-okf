---
okf_version: "0.2"
type: bundle
title: "Agent 自我进化评测：LIFT 与 Loaded Impact"
description: "原创中文教程，拆解 LIFT 的配对 Holdout 评测、delta 指标和证据边界；非操作教程，许可证状态尚待确认。"
tags: [Agent, 自我进化, 评测, Holdout, LIFT]
generated: { by: "reference_agent", at: 2026-10-10T12:06:17+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-10-10T12:06:17+08:00 }
status: flagged
stale_after: 2026-12-31
sources:
  - id: blog
    resource: "https://mp.weixin.qq.com/s/2I_eem6KwJ3hKeM9nyHSBg?from=industrynews&color_scheme=light#rd"
    title: "Agent 会越用越聪明吗？这个开源项目开始量化「自我进化」！"
  - id: repo
    resource: "https://github.com/FeiZhuNiU-INFJA/LIFT"
    title: "LIFT"
  - id: repo-snapshot
    resource: "https://github.com/FeiZhuNiU-INFJA/LIFT/tree/9d282e415c5e3b0f65b82c8758a013b269583d93"
    title: "LIFT checked source snapshot"
  - id: paper
    resource: "https://raw.githubusercontent.com/FeiZhuNiU-INFJA/LIFT/9d282e415c5e3b0f65b82c8758a013b269583d93/docs/paper-neurips.md"
  - id: leaderboard
    resource: "https://raw.githubusercontent.com/FeiZhuNiU-INFJA/LIFT/9d282e415c5e3b0f65b82c8758a013b269583d93/docs/leaderboard.json"
  - id: se-bench
    resource: "https://arxiv.org/html/2602.04811v1"
  - id: evoagentbench
    resource: "https://arxiv.org/pdf/2607.05202"
  - id: github-api
    resource: "https://api.github.com/repos/FeiZhuNiU-INFJA/LIFT"
---

# Agent 自我进化评测：LIFT 与 Loaded Impact

> **状态提示**：本包整体为 `flagged`。文章称 LIFT 为开源项目，但截至 2026-10-10，仓库 API 未声明许可证且仓库树未见 LICENSE 文件；在许可证得到确认前，不应据此推断代码可自由复用。各概念页与事实页的 `stable` 仅表示其所述内容已核验，不覆盖本包整体的许可证边界。

这是一份技术综述型知识包，不是安装或复现实验教程。文章页面显示账号「开源星探」、原创标记和发布时间 2026-10-09 07:03，页面未注明时区（F-001–F-004）。正文用原创表述整理 LIFT 评测设计，不复刻文章全文。

## 学习路径

| 读者问题 | 内容 |
|---|---|
| LIFT 具体测量什么 | [LIFT 衡量的是什么](concepts/00-lift-measures-loaded-impact.md) |
| 如何比较加载前后效果 | [配对 Holdout 协议](concepts/01-paired-holdout-protocol.md) |
| 如何理解榜单数字 | [排行榜数字如何解读](concepts/02-reading-leaderboard.md) |
| 结果有哪些限制，能否迁移 | [有效范围与迁移边界](concepts/03-limitations-and-transfer.md) |

## 核心认识

- LIFT 的评测焦点是同一 Holdout 任务下 Base 与 Loaded 的指标差异，不是跨 runtime 的绝对能力排序（F-013、F-014、F-019、F-023）。
- 仓库与论文对 LIFT 缩写的展开略有差异；Holdout requirements 与 Warmup requirements 约有 75% 重合，不能将其描述为要求域完全未见（F-027、F-028）。
- 官方资料中的排行榜 JSON 生成于 2026-08-23，文章页面日期为 2026-10-09；榜单只能作为带时点的快照引用（F-004、F-008）。
- 榜单名义上声明 10 次 repeats，而条目显示 274–280 个配对 task-repeats；聚合点估计与按 repeat 计算的 CI 口径不同，`turns` 具体指任务内 work Agent/Judge 交互轮数（F-019、F-021、F-029、F-030）。
- 官方论文自述为 v1 preprint 和 partial cross-runtime sweep；论文还提示 Judge 与环境保真度限制（F-012、F-022）。
- SE-Bench 与 EvoAgentBench 等相关工作已存在，故不把“此前无人衡量”当作领域事实（F-024、F-025）。

## 质量记录

| 阶段 | 结果 |
|---|---|
| R / G1 | 31 条连续事实；文章页面事实、作者主张、官方材料和相关工作分层。 |
| I / G2 | 4 条洞察均含现象、F 编号证据、反常识点、影响与建议。 |
| E / G3 | “同题配对评测”作为 L1-draft；边界、步骤、检验标准、反模式和跨域迁移见[知识地图](references/knowledge-map.md)。 |
| V | 四视角审查及 11 项事实、统计口径攻击已完成并回归；包级导航、全库计数和定向构建通过。完整 toctree 门仍被另一 bundle 缺失的概念索引拦截。许可证未确认，状态维持 `flagged`。 |
| 验证 | UTF-8 与总索引计数门通过；LIFT 包级 toctree 通过；Sphinx 定向构建成功。全库 toctree 尚有 `deepseek-harness/concepts/index.md` 缺失，详见[变更日志](log.md)。主仓库链接脚本按设计排除 `projects/`，因此未将其 0 文件结果当作本包链接验证。 |
| C | 未执行；用户未要求提交。 |

## 资料与审查

- [来源台账](references/source-manifest.md)
- [文章与项目事实索引](references/article-source.md)
- [知识地图与洞察](references/knowledge-map.md)
- [关键声明核验与 V 审查](references/verification.md)
- [变更日志](log.md)

本包没有 `examples/`：文章未提供仅凭文章即可复现的固定版本、环境准备、完整运行步骤和输入输出剧本。官方仓库的存在不等于文章本身是可复现实验手册。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```

## CMD-LOG

```text
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S0 | event=CMD_START | session=sc-20261010-lift-agent-evolution | msg=方法论编排开始：微信公众号文章转 LIFT Agent 自我进化评测 OKF 知识包 | ctx={"scenario":"knowledge","topic":"lift-agent-evolution","depth":"deep","target":"projects/awesome-okf-xs/doc/bundles"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S2 | event=CHAIN_SELECTED | session=sc-20261010-lift-agent-evolution | msg=选定 R→I→E→V；不启用无关 F/A，用户未要求提交 | ctx={"chain":["R","I","E","V"],"gates":["G1","G2","G3","V"],"source_gate":"public-only"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=R1 | event=CONCEPT_COMPLETED | session=sc-20261010-lift-agent-evolution | msg=文章页面、官方仓库与论文资料完成事实采集 | ctx={"fact_range":"F-001..F-031","sources":["blog","LIFT official repository","related benchmarks"]}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=G1 | event=GATE_PASSED | session=sc-20261010-lift-agent-evolution | msg=页面事实、作者主张与官方事实分层，双份事实表连续一致 | ctx={"facts":31,"continuous":true,"mirrored_tables":["spec/facts.md","references/article-source.md"]}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=I1 | event=CONCEPT_COMPLETED | session=sc-20261010-lift-agent-evolution | msg=形成四条四元组洞察及 L1-draft 配对评测模式 | ctx={"insights":4,"pattern":"同题配对评测","maturity":"L1-draft"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=G2 | event=GATE_PASSED | session=sc-20261010-lift-agent-evolution | msg=四条洞察均有 F 证据、反常识点、影响和建议 | ctx={"insights":4,"four_tuple_complete":true}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=E1 | event=CONCEPT_COMPLETED | session=sc-20261010-lift-agent-evolution | msg=完成四篇概念教程、信源台账及知识地图，未建不可复现的 examples | ctx={"facts":31,"concepts":4,"examples":0,"pattern":"同题配对评测","maturity":"L1-draft"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=G3 | event=GATE_PASSED | session=sc-20261010-lift-agent-evolution | msg=模式边界、步骤、检验标准、反模式和跨域迁移齐备 | ctx={"pattern":"同题配对评测","independent_cases":1,"maturity":"L1-draft"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=V1 | event=CONCEPT_COMPLETED | session=sc-20261010-lift-agent-evolution | msg=完成四视角审查及 11 项补充攻击；许可证未决保留 flagged | ctx={"review_roles":["devils_advocate","newcomer","business","future"],"attacks":11,"unresolved":["license"]}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=V | event=GATE_PASSED | session=sc-20261010-lift-agent-evolution | msg=关键事实、样本层级、CI、turns、Holdout 重合、缩写、时区和快照完成回归；生命周期边界显式保留 | ctx={"review_items":11,"unresolved_core_claims":["open-source license"]}
```
