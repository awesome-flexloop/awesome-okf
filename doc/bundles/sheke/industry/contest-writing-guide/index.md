---
okf_version: "0.2"
type: Playbook
title: "知乎、WorkBuddy与头条参赛和写作综合指南"
description: "先核工具、权利与时序，再选作品和独立写作；83条事实、24条缺口、三条洞察与两项L1-draft候选方法。"
status: draft
date: "2026-10-27"
security_level: public
sources:
  - id: source-inventory
    resource: references/source-inventory.md
  - id: facts
    resource: references/facts.md
---

# 知乎、WorkBuddy与头条参赛和写作综合指南

**先核资格与权利，再做可体验成果，最后按不同读者问题写文章。** 本包整合2026-10-27三路公开研究，不开发参赛应用、不生成真实投稿成稿、不代报名或接受协议。知乎、WorkBuddy是有征集期的活动；头条实际入口身份与个人权益未确认，只能使用关联规则研究。

全包按批准清单为**15个Markdown文件**。事实底账唯一登记**83F、24G、7C、6E**；接收覆盖ZH25/WB35/TT22，加Task8当前公开来源补核F-083。三条洞察与两项候选方法均不冒称官方结论、获奖经验或收益验证。状态保持`draft`，独立R2为`blocked`：内容评分4/5、无遗留内容缺陷，CP1/3/4/5/6 pass；CP2/7因历史原文及首次三索引写前快照缺失blocked，不宣告完整验收。

## 最短阅读路径

| 当前任务 | 从这里开始 | 读完做什么 |
|---|---|---|
| 判断哪条路径有意义 | [入口性质与状态](concepts/00-platforms-and-current-status.md) | 分活动/权益入口，列权限与未知 |
| 找工具、材料和条款依据 | [规则与证据地图](concepts/01-rules-and-evidence-map.md) | 用F/G核动作，不用未知填许可 |
| 选题并做真实成果 | [三类候选选题](concepts/02-topic-and-work-selection.md) → [材料](concepts/03-entry-and-materials.md) | 选小而可核的核心任务，保留真实证据 |
| 写各平台介绍和分析 | [差异化写作](concepts/04-writing-by-platform.md) | 私有稿填真实槽位，不换词洗稿 |
| 决定跨投、先发或同步 | [版权与顺序](concepts/05-rights-and-publication-order.md) → [倒排](concepts/06-timeline-and-fallbacks.md) | 核作品/文章/宣传三对象，冲突保留退路 |
| 复用方法而非复制规则数字 | [洞察与方法](concepts/07-insights-and-reusable-methods.md) | 使用候选方法，重新核目标域规则 |
| 回验来源和检查范围 | [事实](references/facts.md)、[来源](references/source-inventory.md)、[验证](references/verification.md) | 分来源事实、实施自验与独立审查 |

## 三条洞察与两项方法

- **I-001 工具资格先于内容包装**：真实工具链不满足时，改文章声明不能补资格。
- **I-002 公开表达有独立时间成本**：先发表的历史不靠等待、换词或删重发消除；Wiki边界仍待确认。
- **I-003 核验范围决定结论范围**：细则字符串一致、百科全文取得、文档构建通过各自只证明其检查对象。
- **M-001 三对象分账**：作品、文章、宣传分别记录工具、许可和发表历史。
- **M-002 证据时序门**：公开前同时核证据、资格、许可和时间；未知不升级为承诺。

两方法各6步、4反模式，成熟度均为**L1-draft**；科研Demo、资助申请仅桌面迁移，没有真实跨域提交验证。详细证据、解释假设与升级条件只在洞察页展开。

## 边界与缺口

知乎官方CLI是片段非全文，10月31日钟点/时区和关联协议未知。WorkBuddy当前54与旧49细则比对一致不覆盖新表单提示、后端或未读服务协议；主办IP限制不可泛化到所有自有作品。头条百科和公告同平台互引不是独立多源，`exclusive`入口身份、本人资格、独家合同及关联同步豁免仍缺。

实际投稿正文、核心待投论证、私人对话、联系方式、收益、合同与未授权截图不落公开包。任何真实或测试密钥不进入公开源码、图片、对话或构建产物；优先无密钥演示或服务端秘密管理。不默认同代码三路跨投，不用固定AIGC比例、相似阈值、截图最佳张数、固定审核工期或收益倍数作保证。

## 实施状态

| 项目 | 状态与证据边界 |
|---|---|
| Task4事实工程 | 作者机械自验完成：F/G/C/E连续唯一，输入82/82，旧显式编号和算术回验；[记录](references/verification.md) |
| Task5写作与方法 | 作者自验综合4/5，三洞察六元素、两方法结构齐；非独立评分 |
| Task6工程收尾 | 范围检查结果以[验证记录](references/verification.md)为准，不代表全库或跨包全面验收 |
| Task7独立V及AC最终验收 | **R2 blocked**；审查者`guide_independent_recheck`，独立内容评分4/5、无遗留内容缺陷；CP1/3/4/5/6 pass，CP2/7历史证据blocked，详见[记录](references/verification.md#独立task7-vr2-blocked)；本次仅回记主代理已有结果，不登记`verified`或宣告完整验收 |
| Task8修补 | 完整13字段/11必填、代维权F-083、当前G1–G3及工程复验见[记录](references/verification.md#task8-修补与当前证据)；不修改旧包或规格 |
| 提交、推送、发布、报名、安装 | **未执行**，不在本次授权范围 |

采集时点、缺口处置和复查触发见信源台账；活动日期之后须重新确认征集状态，不自行延期。历史变更见[更新记录](log.md)。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```
