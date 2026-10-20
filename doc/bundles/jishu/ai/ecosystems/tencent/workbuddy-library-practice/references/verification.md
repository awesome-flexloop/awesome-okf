---
type: Reference
title: "WorkBuddy 资料库实践材料 · 核验与证据边界"
description: "记录 11 个 WorkBuddy 空间页面的信源距离、与官方知识包的交叉核对、未核实案例口径及 S11 演示数据/采集缺口。"
tags: [WorkBuddy, 资料库, 核验, 证据边界, 对抗审查]
generated: { by: "process:seven-concepts-r", at: "2026-10-19" }
status: draft
stale_after: "2026-12-31"
sources:
  - { id: S01-S11, resource: "article-source.md", title: "本次来源事实登记" }
  - { id: official-workbuddy-library, resource: "../../workbuddy-official-docs/concepts/06-knowledge-base-and-library.md", title: "WorkBuddy 官方资料库与知识库能力" }
  - { id: official-workbuddy-experts, resource: "../../workbuddy-official-docs/concepts/04-experts-skills-and-plugins.md", title: "WorkBuddy 专家、Skill 与插件能力" }
  - { id: official-workbuddy-example-library, resource: "../../workbuddy-official-docs/examples/05-knowledge-base-workflow.md", title: "WorkBuddy 官方知识库工作流" }
  - { id: official-workbuddy-example-experts, resource: "../../workbuddy-official-docs/examples/04-skills-experts-and-plugins.md", title: "WorkBuddy 官方扩展能力操作示例" }
---

# 核验与证据边界

> 核验时点：2026-10-19。本记录覆盖 Task 1 的产品声明与来源边界核对，以及 Task 2 的逐来源去重矩阵、章节映射和示例可复现性判定；它不替代后续四视角审查或自动门禁。

## 核验结论

- **来源性质**：S01–S11 均为 `workbuddy.cn/space/d/` 托管页面。页面作者身份、发布日期、编辑审校过程及与腾讯/WorkBuddy 的组织或商业关系未从页面台账核实；S10 页面自述原文来自腾讯 WorkBuddy 官方公众号（2026-08-28），该归属未独立核验。托管域名不等于官方文档或官方背书。
- **产品事实参照**：资料库定位、成员空间权限、MD/CSV/HTML 联动、人机修订、专家/Skill 的机制与官方操作路径，以既有 `workbuddy-official-docs` 包为准；新包只沉淀作者页面的实践框架、编排方式和案例边界。
- **独立核验范围**：本轮以官方知识包现有官方页面采集与事实编号作交叉参照，未对 11 个作者页面逐项开展新的外部 WebSearch，也未把来源作者的效果描述升级为官方事实或第三方证据。
- **当前状态建议**：来源作者、时间与大部分实践观点属于单源材料；S10 数字不采用、S11 数值不作为真实数据。当前没有发现足以证伪本包实践主题的证据；最终 `stable`/`flagged` 状态须结合后续内容和 V 阶段复核再定。

## 与官方知识包的声明核对

| 来源 | 来源页面所述主题 | 官方参照 | 处理边界 |
| --- | --- | --- | --- |
| S01 | 资料库定位、内容保存/调用、MD 修订及工作台叙述 | [资料库与知识库](../../workbuddy-official-docs/concepts/06-knowledge-base-and-library.md)：F-159–F-162、F-169–F-176 | 产品能力与编辑器行为引用官方包；实践叙述归因 S01 |
| S02 | 保存成果、Agent 接续协作、团队空间快速流程 | [知识库工作流](../../workbuddy-official-docs/examples/05-knowledge-base-workflow.md)：F-159、F-165、F-171–F-172 | 操作步骤不在新包重复；只保留快速流程的组织方式 |
| S03 | 一分钟快速入门 | [知识库工作流](../../workbuddy-official-docs/examples/05-knowledge-base-workflow.md) | 页面只作为入门路径来源；官方操作边界回链 |
| S04 | Agent 接续读取/修改及成果保存/分享 | [资料库与知识库](../../workbuddy-official-docs/concepts/06-knowledge-base-and-library.md)：F-159–F-172、F-243–F-249 | 产品读写/分享能力以官方包为准；“接续协作”作为实践模式归因 S04 |
| S05 | MD 内容、CSV 数据、HTML 呈现及联动 | [资料库与知识库](../../workbuddy-official-docs/concepts/06-knowledge-base-and-library.md)：F-160–F-162、F-175、F-179 | 产品载体能力不重复确立；将来源的职责划分作为实践框架，标注提出者来源 |
| S06 | AI 提议修订、人审及 MD/HTML 差异 | [资料库与知识库](../../workbuddy-official-docs/concepts/06-knowledge-base-and-library.md)：F-169–F-170、F-243–F-249 | 产品行为引用官方核验口径；协作原则归因 S06 |
| S07 | 团队空间与成员协作 | [资料库与知识库](../../workbuddy-official-docs/concepts/06-knowledge-base-and-library.md)：F-165–F-168、F-171 | 权限档位及 Agent 权限遵循官方包；不在本包复述权限手册 |
| S08 | 保存、任务调用、新成果回存的“知识复利”循环 | [资料库与知识库](../../workbuddy-official-docs/concepts/06-knowledge-base-and-library.md)：F-172、F-264–F-267；[知识库工作流](../../workbuddy-official-docs/examples/05-knowledge-base-workflow.md)：F-267 | 具体保存/回存入口引用官方包；“知识复利”及流程抽象注明是来源作者框架，不声称实测效率提升 |
| S09 | 个人/团队工作台场景、静态/动态展示和提示词模板 | [资料库与知识库](../../workbuddy-official-docs/concepts/06-knowledge-base-and-library.md)：F-159–F-162、F-171–F-179 | 工作台样例和模板归因 S09；不能据此推定每个页面是平台内置能力 |
| S10 | 家庭教育专家八步搭建、Prompt/Skill/知识库分工、风险测试 | [专家、专家团、技能与插件](../../workbuddy-official-docs/concepts/04-experts-skills-and-plugins.md)；[扩展能力示例](../../workbuddy-official-docs/examples/04-skills-experts-and-plugins.md) | 官方包用于辨析产品概念和权限边界；八步编排是来源案例流程，不表示官方推荐或普遍有效 |
| S11 | 面包店团队工作台目录、四个业务看板 | 官方资料库页面只作产品能力参照，不覆盖该案例的业务数据 | 仅描述已取得的页面结构；四个看板数据均为页面声明的虚构演示数据，主工作台正文保持未取得状态 |

## 来源覆盖矩阵与知识地图

| 来源 | 与 `workbuddy-official-docs` 的重叠 | 本包保留的实践增量 | 计划归属 |
| --- | --- | --- | --- |
| S01 | 资料库定位、文件与编辑器能力已由概念 06 及示例 05 覆盖 | 以可复用成果为起点的入门组织方式 | `concepts/00-shared-agent-workspace.md` |
| S02 | 保存、Agent 使用和团队空间的产品路径已由官方包覆盖 | “保存成果→继续协作→放入共享空间”的快速流程编排 | `concepts/00-shared-agent-workspace.md` |
| S03 | 快速操作主题与官方示例高度重叠 | 作为快速入门来源映射；不单独复述产品步骤 | `concepts/00-shared-agent-workspace.md` |
| S04 | Agent 读写与分享能力已由官方包覆盖 | 延续上一任务上下文、修改后保存/分享的协作模式 | `concepts/00-shared-agent-workspace.md` |
| S05 | MD/CSV/HTML 的产品联动与职责描述见官方概念 06（F-160–F-162） | 将内容、数据、呈现分层作为作者提出的工作台设计框架 | `concepts/01-content-data-presentation.md` |
| S06 | MD 待确认修订与 HTML 即时修改见官方概念 06（F-169–F-170） | 将“提出建议—人工审阅—确认写回”整理为协作原则 | `concepts/02-human-ai-review-loop.md` |
| S07 | 团队空间、权限档位和 Agent 同权见官方概念 06（F-165–F-168） | 面向团队的共享上下文与协作约定；不重写权限表 | `concepts/03-team-knowledge-cycle.md` |
| S08 | 保存/回存入口见官方概念 06（F-172、F-264–F-267）及示例 05 | “调用—产出—回存—再调用”作为来源作者的知识流动框架 | `concepts/03-team-knowledge-cycle.md` |
| S09 | 个人/团队空间及页面发布产品能力见官方概念 06 | 静态展示/动态工作台的场景分类与提示词模板资产 | `concepts/04-workbench-composition.md` |
| S10 | 专家、Skill 与知识库机制见官方概念 04/06、示例 04/05 | 家庭教育案例的八步编排、职责拆分和风险测试；效果数字不进入正文结论 | `concepts/05-expert-case-boundaries.md` |
| S11 | 官方包未覆盖该面包店演示资产 | 已取得看板目录结构作为工作台案例；只记录看板主题与虚构数据边界 | `concepts/04-workbench-composition.md` |

### 最终概念页清单

1. `00-shared-agent-workspace.md`：资料如何成为人和 Agent 可共同延续的工作成果；合并 S01–S04。
2. `01-content-data-presentation.md`：内容、数据与呈现分层的适用场景及边界；以 S05 为主，并链接官方产品事实。
3. `02-human-ai-review-loop.md`：AI 修改建议与人工确认的协作分工；以 S06 为主，产品行为回链官方包。
4. `03-team-knowledge-cycle.md`：共享上下文与“调用—产出—回存”的团队循环；合并 S07–S08。
5. `04-workbench-composition.md`：个人/团队工作台的场景组织与演示看板边界；合并 S09、S11。
6. `05-expert-case-boundaries.md`：家庭教育专家案例中的步骤、能力职责和风险测试；以 S10 为主，不推广案例成效。

### `examples/` 两问判定

| 候选材料 | Q1：是否有读者可照做的步骤？ | Q2：步骤是否有足够复现信息？ | 决定 |
| --- | --- | --- | --- |
| S02/S03 快速入门 | 是，页面包含快速使用步骤 | 否；当前登记未确认固定产品版本、完整输入条件及可验证输出/重跑结果 | 不建 `examples/`；在概念页说明流程并链接官方示例 |
| S10 专家搭建 | 是，页面描述八步搭建流程和风险测试 | 否；当前登记未确认固定产品版本、完整提示词/测试输入、预期输出和可复验结果 | 不建 `examples/`；作为有边界的案例分析 |
| S11 四个看板 | 否；取得的是演示资产，不是搭建/复现实验步骤 | 否；数据明确为虚构演示数据，主工作台正文未取得 | 不建 `examples/`；在工作台案例页记录结构和数据边界 |

因此，本包按实践综述与案例分析组织，不创建 `examples/`。官方产品操作若有需要，直接链接 `workbuddy-official-docs/examples/`，不复制成未经复验的教程。

## P0 与争议口径

| 声明 | 级别/结果 | 处理 |
| --- | --- | --- |
| S10“3.4 万个家庭”等案例规模文字（F-027） | P0 数字；仅见于来源案例，本轮未取得独立权威出处 | 标注为未核实的原文口径，不作为用户数、服务规模、成效或因果证据；概念正文不得用它支持结论 |
| S11 四个看板中的数值 | 演示数据；页面明确标注为虚构 | 不登记看板中的业务数值为现实事实，不用于市场、经营或效果判断 |
| S11 主工作台正文 | 采集缺口 | 不从页面目录、子看板或标题反推未取得的主工作台功能 |
| S06 关于 MD/HTML 修订表现的说明 | 产品行为声明；与官方包 F-169–F-170 有对应参照 | 后续正文只采用官方包核实的表述，并注明 S06 是实践来源 |
| S05 的 MD/CSV/HTML 分工 | 作者提出的组织框架；产品联动机制另有官方参照 | 只作为内容建模/工作台设计建议呈现，不称作唯一或官方标准 |

## 采集与信源缺口

1. 原始输入 13 个 URL 去重为 11 个唯一页面；重复项为第 2/3 项（S02）和第 9/13 项（S08），详见 [来源与事实登记](article-source.md)。
2. S11 主工作台只取得加载占位；四个子看板可读且均声明虚构数据。本次不把 HTML 展示值复制为事实。
3. S10 的“3.4 万个家庭”未得到独立核验；来源作者身份和数字的统计对象、时间范围、计量口径均未核实。
4. 来源页面的作者、发布日期、原始发布/转载关系、商业赞助关系与内容审校机制未核实。
5. 产品页面可能随版本变化；使用前复核官方文档。本包拟设 `stale_after: 2026-12-31`，此日期为复查提醒，不代表届时内容必然失效。

## 本阶段 G1 自检

- 事实编号：F-001 至 F-046 连续，共 46 条；Spec `facts.md` 与本包 `article-source.md` 的编号集合相等（46/46），无跳号、无重复。机械复核结果：两集合相同、连续、无重复，事实行因果/判断词扫描零命中。
- F 条目均以页面标题、页面内容摘要、来源主张或采集边界描述；产品真实性判断留在本核验记录，未写入 R 阶段事实。
- 13 个输入 URL 与 S01–S11 对账完成，重复链接已显式登记；S11 主工作台缺口及四个子看板的虚构数据声明均已记录。
