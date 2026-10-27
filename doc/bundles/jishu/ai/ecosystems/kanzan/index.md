---
okf_version: "0.2"
type: bundle
id: kanzan
title: Kanzan AI 场景与应用工程学习指南
description: 公开中文站点的概念与方法教程，涵盖场景、知识治理、MCP 与 Skills、事件契约、产品边界、成本交付和研究验证；非源码或可直接执行的生产操作教程。
tags: [Kanzan, AI应用, 知识治理, MCP, Skills, 事件协作, 生产交付]
date: 2026-10-27
status: stable
stale_after: 2026-12-31
session: sc-20261027-kanzan
security_level: public
source: Kanzan 公开中文栏目与博客，2026-10-27 采集；权威补充来源见信源台账。
sources:
  - id: site
    resource: https://www.kanzan.top/zh
  - id: inventory
    resource: references/source-inventory.md
  - id: facts
    resource: references/facts.md
  - id: mcp
    resource: https://modelcontextprotocol.io/docs/learn/architecture
  - id: skills
    resource: https://agentskills.io/specification
  - id: interviews
    resource: https://www.anthropic.com/features/81k-interviews
  - id: proof
    resource: https://arxiv.org/html/2605.22763v2
---

# Kanzan AI 场景与应用工程学习指南

从明确业务任务，到治理资料、连接工具、分配权限，再到核算成本与验收交付，Kanzan 公开站点提供了一组相互关联的学习材料。本包将它们按读者问题重组，保留事实、作者观点与教学推导之间的区别。

> **厂商与作者自述边界**：公司登记、产品能力、工业成效和历史商业权益未获独立实测确认。数字不用于采购、盈利或成功率预测。原研究的结论也只适用于其报告的样本与实验。本包是概念与方法教程，不是供应商背书或生产部署承诺。

## 阅读入口

| 想解决的问题 | 页面 |
|---|---|
| 这个站点讲什么，哪些内容已经读过 | [站点画像与学习地图](concepts/00-overview.md) |
| 怎样选业务任务并整理资料 | [场景、知识治理与团队学习](concepts/01-use-cases-and-knowledge.md) |
| MCP、Skills 和事件类型各管什么 | [Agent 与事件契约](concepts/02-agent-and-event-contracts.md) |
| 照片、视频、工作 Feed 与工业场景有何差别 | [产品与工业边界](concepts/03-products-and-industrial-boundaries.md) |
| 怎样比较任务成本并判断交付完成 | [成本与交付](concepts/04-cost-and-delivery.md) |
| 研究有哪些启发，怎样迁移到任务中 | [研究与候选模式](concepts/05-research-and-transfer.md) |
| 每条事实来自哪里 | [唯一事实登记](references/facts.md)与[信源台账](references/source-inventory.md) |
| 哪些内容被校正或保留为未核验 | [核验记录](references/verification.md)与[对抗审查](references/adversarial-review.md) |

首次练习：读[场景篇](concepts/01-use-cases-and-knowledge.md)，填写一张任务卡，人工判断一个正常请求和一个缺资料请求。能说明依据与拒答理由即完成纸面练习，无需接入产品。

## 范围与骨架

采集时点为 2026-10-27：6 个中文栏目页面、博客索引的 21 篇正文、站点地图，以及 7 条权威补充来源。论文为相关章节定点精读，非全部附录通读。三个地图独有 URL 返回 404；英文镜像、后台和关联产品站全量内容不在成功覆盖范围。

本包位于 AI 厂商与社区生态的 `kanzan/`，保持站点级主题完整，不把每篇博客拆成独立束。当前结构为六篇教程、四篇参考、两个子索引、根索引和日志，共 14 个 Markdown 文件。

操作可复现性两问的裁定：

1. 是否存在操作步骤：部署文章有作者自述的代码与顺序，答案为是。
2. 本包是否具有足够前置条件供读者完整复现：目标应用、完整配置、锁文件、秘密注入和恢复条件未取得并验证，答案为否。

因此不设 `examples/`。部署内容保留为流程解读；本包设计的表格与例子均为教学材料，非产品实测。此次按子项目自治规范直接持久化唯一事实台账，不另建公共 Spec 或重复事实副本。

## 七概念产出

采用知识沉淀链路 `R→I→E→V`，session 为 `sc-20261027-kanzan`。C 实际提交等待用户另行授权；不为凑齐七个概念而强加第一性原理或额外拆分。

| 阶段 | 产出 |
|---|---|
| R | [F-001～F-050](references/facts.md)，50 条来源记录；作者主张不升级为独立实测 |
| I | [I-1～I-3](concepts/05-research-and-transfer.md)：任务定义、权限分层、结果成本三条四元组洞察 |
| E | [对象双验](concepts/05-research-and-transfer.md)，含适用边界、六步、反模式、检验标准与财务迁移推演 |
| V | [独立四视角审查记录](references/adversarial-review.md)，9 条 P2 全部采纳，主代理回读确认修改落盘 |
| C | 未提交、未推送；共享索引保留其他会话改动 |

“对象双验”为 L1-draft，尚无两个独立业务部署案例，不宣称 L2 成熟度，也未越界独立登记进方法论模式库。

## 质量与维护

| 检查 | 当前状态与证据 |
|---|---|
| G1 事实 | 50 条编号记录，证据层级与未核验范围见事实表 |
| G2 洞察 | 三条均含陈述、证据、反常识、行动及机制限制 |
| G3 模式 | L1-draft，迁移为教学推演，不冒充实证 |
| V 审查 | 四视角完成，9 条 P2 全部修正；未发现本地证据可确认的 P0/P1 |
| 文档门禁 | 14 文件元数据、85 个本地引用、导航、计数、UTF-8 与 11 项 Python 红线测试通过；全库资产基线未通过，构建结果见日志 |
| Git 提交 | 未授权，不执行 |

价格、权益、主体登记、产品功能和协议版本更新时复核对应事实；到 2026-12-31 重新检查时点性信息。企业使用前另取交付范围、数据协议、SLA、验收样本与退出安排。法律页占位不构成合规披露，也不能证明站点没有其他法律安排。

更新与真实验证证据记录在[日志](log.md)。返回[生态索引](../index.md)。

`stable` 表示本包已审查、可用于限定范围的阅读，不表示产品已实测或全库门禁全部通过。资产基线存在共享工作区与历史规模声明差异；未为消除差异执行提交或 stash。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```
