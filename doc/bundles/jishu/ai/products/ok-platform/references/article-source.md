---
okf_version: "0.2"
type: Reference
title: 腾讯 OK 平台「AI 端到端研发流程」文章事实清单（F-001~F-060）
description: 微信公众号文章《别只盯着AI Coding，真正的变化发生在整个研发流程》的可核验事实登记——页面事实与作者主张分级，供 bundle 各概念文档逐声明归因。
sources:
  - id: wx-ok-reprocess
    resource: https://mp.weixin.qq.com/s/s_AmjWIB57b7fQY_3VNkoQ
    title: 别只盯着AI Coding，真正的变化发生在整个研发流程（腾讯技术工程）
    author: author:danteyang (tencent-tech-eng)
    last_modified: 2026-10-09
  - id: netease-mirror
    resource: https://c.m.163.com/news/a/L8QO7DU90518R7MO.html
    title: 网易镜像（同文，2026-10-09 18:37）
    last_modified: 2026-10-09
generated:
  by: trae-solo-agent
  at: 2026-10-10T09:00:00+08:00
status: draft
stale_after: 2026-12-31
---

# 文章事实清单（F-001~F-060）

> 参考 [frontmatter.md](../../../.agents/rules/frontmatter.md)：本文为 `type: Reference` 信源登记。
> `page_fact` = 页面可核验的结构/署名事实；`author_claim` = 作者的观点、因果断言、价值判断或解释。**执行者解读不入本文**（解读统一入 `knowledge-map.md` 机制层）。

## 信源登记

| 字段 | 值 |
|---|---|
| 主来源 `source_id` | `wx-ok-reprocess` |
| 标题 | 别只盯着AI Coding，真正的变化发生在整个研发流程 |
| 账号 | 腾讯技术工程（mp.weixin.qq.com 账号主体） |
| 作者 | danteyang |
| 发布页时间戳 | 2026-10-09 09:36（微信端显示）；网易镜像 2026-10-09 18:37 |
| 访问方式 | 公开 URL，无需登录（public-only 通过） |
| 复制边界 | 未复制全文，仅登记事实与短引；镜像与微信两源文本一致 |

## F 事实表

| F | claim | type | source_id | locator | status |
|---|---|---|---|---|---|
| F-001 | 文章标题为《别只盯着AI Coding，真正的变化发生在整个研发流程》 | page_fact | wx-ok-reprocess | 标题行 | verified |
| F-002 | 文章由「腾讯技术工程」微信公众号账号发布 | page_fact | wx-ok-reprocess | 标题下署名 | verified |
| F-003 | 文章署名作者为 danteyang | page_fact | wx-ok-reprocess | 标题下署名 | verified |
| F-004 | 微信端页面时间戳为 2026-10-09 09:36 | page_fact | wx-ok-reprocess | 标题下时间 | verified |
| F-005 | 网易镜像转载时间戳为 2026-10-09 18:37 | page_fact | netease-mirror | 页面时间 | verified |
| F-006 | 文章主题为「AI 开始自动完成需求评审、技术方案、编码、审查和部署后，研发流程的变化」 | page_fact | wx-ok-reprocess | 导语段 | verified |
| F-007 | 文章基于「OK 平台端到端自动交付的真实运营数据」展开 | page_fact | wx-ok-reprocess | 导语段 | verified |
| F-008 | 作者列举自行熟悉的外部/司内 AI 编程工具：CodeBuddy、Cursor、Claude code | author_claim | wx-ok-reprocess | §一 | single-source |
| F-009 | 作者主张：日常开发任务「基本都能 cover」 | author_claim | wx-ok-reprocess | §一 | single-source |
| F-010 | 作者主张：把原始需求直接丢给 AI，AI 只能反问改哪里/怎么改，或自行按可行想法动手，效果常不及预期 | author_claim | wx-ok-reprocess | §一 | single-source |
| F-011 | 作者举例解释「AI 失忆」：帖子列表优化需求，AI 不知道接口、下游存储（MySQL/ES）、分页逻辑变更、慢查询缺索引等背景 | author_claim | wx-ok-reprocess | §一 | single-source |
| F-012 | 作者主张：开发先把「加载慢」翻译成「关联查询缺索引 + N+1 问题」再喂 AI | author_claim | wx-ok-reprocess | §一 | single-source |
| F-013 | 作者观点：「你是翻译和决策官，AI 是执行者」 | author_claim | wx-ok-reprocess | §一 | single-source |
| F-014 | 作者主张：把「翻译/决策」环节也交给 AI，需求可端到端自我跑完 | author_claim | wx-ok-reprocess | §一 | single-source |
| F-015 | 作者列出研发六阶段人/AI分工表：需求分析、方案设计、编码、测试、部署、线上运维；AI 擅长执行、人擅长判断 | author_claim | wx-ok-reprocess | §一 | single-source |
| F-016 | 作者主张：信息在需求链路（用户→运营→PM→开发）中逐级传递发生「信息衰减」 | author_claim | wx-ok-reprocess | §一 | single-source |
| F-017 | 作者主张：评审会、接口对齐会、联调周「因人的局限而存在，不是因为问题本身需要它们」 | author_claim | wx-ok-reprocess | §一 | single-source |
| F-018 | 作者给出「零基思维核心追问」：这个环节因人的局限而存在，还是因问题本身需要它 | author_claim | wx-ok-reprocess | §一 | single-source |
| F-019 | 作者列举可被消解的摩擦：前后端对协议开会、PM与开发来回拉评审、联调等待 | author_claim | wx-ok-reprocess | §一 | single-source |
| F-020 | 作者观点：真正的问题是流程结构，不是执行速度；「重构」区别于「插件」 | author_claim | wx-ok-reprocess | §一 | single-source |
| F-021 | 作者用历史类比（信使→电话、纸质公文→电邮）论证技术跃迁淘汰旧流程 | author_claim | wx-ok-reprocess | §一 | single-source |
| F-022 | 作者列举「补偿人的局限」的传统环节：前后端分离、接口文档、需求评审会、联调阶段 | author_claim | wx-ok-reprocess | §一 | single-source |
| F-023 | 作者结论：不是在旧流程里插 AI 工具，而是用 AI 重新定义流程本身，端到端重建 | author_claim | wx-ok-reprocess | §一 | single-source |
| F-024 | OK 平台定位为「AI 驱动的端到端研发平台」，核心理念「需求即交付」 | author_claim | wx-ok-reprocess | §二 | single-source |
| F-025 | 作者主张：用户提交需求描述后，AI Agent 自动走完 需求评审→仓库匹配→技术方案→编码→Code Review→部署 全链路 | author_claim | wx-ok-reprocess | §二 | single-source |
| F-026 | OK 平台运营时间窗：2026 年 4 月下旬上线至 6 月 | page_fact | wx-ok-reprocess | §二 | verified |
| F-027 | 安全中心项目空间 4-6 月提交 254 条需求 | author_claim | wx-ok-reprocess | §二 | single-source/flagged |
| F-028 | 254 条需求中 172 条由 AI 端到端完成，占比 68% | author_claim | wx-ok-reprocess | §二 | single-source/flagged |
| F-029 | 其余需求为策略需求/数据需求/超出端到端能力范围，转人工 | author_claim | wx-ok-reprocess | §二 | single-source |
| F-030 | 作者主张传统模式下简单需求从提出到合并代码中位耗时 3~5 个工作日 | author_claim | wx-ok-reprocess | §二 | single-source/flagged |
| F-031 | OK 平台上 51% 的需求在 2 小时内完成 | author_claim | wx-ok-reprocess | §二 | single-source/flagged |
| F-032 | 作者主张：人力不变时团队可承接更多需求，人从重复开发抽身聚焦转人工的复杂/高风险/高价值需求 | author_claim | wx-ok-reprocess | §二 | single-source |
| F-033 | 作者提出「九阶段全链路」，各阶段有 AI 角色、输入、输出和质量门 | page_fact | wx-ok-reprocess | §二 | verified |
| F-034 | 九阶段细节在原文以配图（截图）呈现，正文未展开为文本 | page_fact | wx-ok-reprocess | §二 配图 | verified |
| F-035 | 作者主张 AI 开发最大失败模式是「需求模糊导致大量返工」 | author_claim | wx-ok-reprocess | §三 | single-source |
| F-036 | 作者主张「瓶颈不在开发侧，在需求侧」 | author_claim | wx-ok-reprocess | §三 | single-source |
| F-037 | 作者主张「需求写得多清楚，AI 就做得多准确；需求描述模糊，代码再快也是返工」 | author_claim | wx-ok-reprocess | §三 | single-source |
| F-038 | OK 平台需求评审 AI 采用「访谈式逐层深挖」（复述理解→顺着回答挖→发散收敛→区分必须/建议明确） | author_claim | wx-ok-reprocess | §三 | single-source |
| F-039 | 作者列「放行必要条件」四项：做什么、为谁做、关键业务规则、验收标准 | author_claim | wx-ok-reprocess | §三 | single-source |
| F-040 | OK 平台为 PM 设计独立「需求收集池」，AI 负责把粗想法补全为可开发规格 | author_claim | wx-ok-reprocess | §三 | single-source |
| F-041 | 可行性评估 AI 对 7 个维度打分（0~100）：清晰度20%、仓库匹配20%、改动范围15%、技术复杂度15%、外部依赖10%、风险等级10%、交付形态10% | author_claim | wx-ok-reprocess | §三 | single-source |
| F-042 | 总分 ≥60 才能进入开发流水线；作者称其是「保护机制」非通关游戏 | author_claim | wx-ok-reprocess | §三 | single-source |
| F-043 | 作者主张「方案阶段改方向成本最低，开发阶段发现方向错了代价最高」 | author_claim | wx-ok-reprocess | §四 | single-source |
| F-044 | 技术方案 AI 四条硬纪律：按依赖图排序（非重要性）、垂直切片优先、任务粒度控制（>5文件或跨2子系统要拆分）、插入检查点（每2-3步） | author_claim | wx-ok-reprocess | §四 | single-source |
| F-045 | 技术方案 AI 对关键决策做「找茬式自审」，站在「假设作者过度自信」视角 | author_claim | wx-ok-reprocess | §四 | single-source |
| F-046 | 方案不确定项收进「待确认问题」（产品/技术两类），用户管理端逐题回答 | author_claim | wx-ok-reprocess | §四 | single-source |
| F-047 | 作者主张「不确定的事提前暴露，不让模糊进入开发，是整条链路质量最核心的原则」 | author_claim | wx-ok-reprocess | §四 | single-source |
| F-048 | 开发 AI 结束标志：编译 + 单测 + 创建 MR 通过 | author_claim | wx-ok-reprocess | §五 | single-source |
| F-049 | 编码三条纪律：简单优先（抵抗过度设计）、范围纪律（只碰该碰的文件+「发现但不碰」）、关键路径先写测试再实现 | author_claim | wx-ok-reprocess | §五 | single-source |
| F-050 | 注入「简单优先」约束后，审查中「架构过度复杂类」问题频次下降约一半 | author_claim | wx-ok-reprocess | §五 | single-source/flagged |
| F-051 | 约 49 条需求（约 17%）在自动开发阶段经历超过 1 轮代码审查+修复 | author_claim | wx-ok-reprocess | §五 | single-source/flagged |
| F-052 | OK 平台代码审查 AI 标准为「改善即批准」：关键问题（bug/崩溃/安全/数据损坏/功能缺失/越权）才阻塞；改进建议（命名/注释/风格/可选性能）不阻塞 | author_claim | wx-ok-reprocess | §六 | single-source |
| F-053 | 审查 AI 对六项安全维度强制核对（UID/UIN 登录态、鉴权中间件、SQL 参数化、敏感信息不硬编码、协议边界校验、资源归属校验） | author_claim | wx-ok-reprocess | §六 | single-source |
| F-054 | 作者观点「90 分的代码今天上线优于追求 95 分但多返工两轮明天上线」 | author_claim | wx-ok-reprocess | §六 | single-source |
| F-055 | 作者主张人的角色升级而非消失：决策者与知识供给者 | author_claim | wx-ok-reprocess | §七 | single-source |
| F-056 | 人不可替代的四个节点：决策与方案选型、补充隐性上下文、异常识别与干预、最终价值判断 | author_claim | wx-ok-reprocess | §七 | single-source |
| F-057 | 作者观点「上下文质量决定输出质量，是 AI 研发中最核心的规律」 | author_claim | wx-ok-reprocess | §七 | single-source |
| F-058 | 作者举例：标签拆分需求 AI 遗漏关联巡检 Skill，需人在代码审查时识别补充 | author_claim | wx-ok-reprocess | §七 | single-source |
| F-059 | 作者主张人工 Review 从行级向意图级升级（跨模块交互、边界条件、安全影响面） | author_claim | wx-ok-reprocess | §七 | single-source |
| F-060 | 文章第八节标题「八、知识飞轮」；其正文未在本包采集的两源文本中完整呈现 | page_fact | wx-ok-reprocess | §八 | verified |

## 采集边界

- **未获取「九阶段全链路」逐阶段文本表**：原文以截图呈现（F-034），正文无该表文本。
- **第八节「知识飞轮」正文未获全**：Win/网易两源均止于第七节末、第八节标题处（F-060）；过渡语「八、知识飞轮：」后无正文可登记，采集中止，不臆补。
- 敏感性预检：公开文章、无访问控制，`public` 通过。