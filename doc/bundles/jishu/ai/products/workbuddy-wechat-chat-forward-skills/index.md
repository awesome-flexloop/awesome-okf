---
okf_version: "0.2"
type: bundle
title: "微信聊天记录转发 WorkBuddy 与两个 Skill：官方入口、群日报与辟谣卡"
description: "产品功能资讯与操作路径登记：单篇微信博文经七阶段核验转化，含官方入口证据边界、群日报与辟谣卡机制、五个可迁移模式。非可复现实操教程，未在本机实跑。"
tags: [微信, WorkBuddy, Skill, 群聊日报, 辟谣, P0核验, flagged, 博文转化]
generated: { by: "reference_agent/blog-article-to-okf-wiki", at: "2026-11-06T04:02:15Z" }
verified: { by: "process:seven-concepts-v", at: "2026-11-06T04:02:15Z" }
status: flagged
stale_after: "2026-12-31"
sources:
  - id: article
    resource: "/references/article-source.md"
  - id: verification
    resource: "/references/verification.md"
  - id: blog
    resource: https://mp.weixin.qq.com/s/BvTuiZelPTb1ZgLT3NoMHQ
    title: "微信聊天记录终于能正经交给 AI 了，官方开的口子不怕封号（2026-10-10）"
  - id: wecom-help-19221
    resource: https://open.work.weixin.qq.com/help/wap/detail?docid=19221
    title: "企业微信官方帮助中心《如何合并转发会话消息》"
  - id: tmtpost-8129024
    resource: https://www.tmtpost.com/nictation/8129024.html
    title: "钛媒体 2026-09-04 微信聊天记录支持 WorkBuddy 调用"
  - id: gmw-20251125
    resource: https://m.gmw.cn/2025-11/25/content_1304238071.htm
    title: "光明网转载 @健康上海12320 淡盐水辟谣"
  - id: workbuddy-site
    resource: https://workbuddy.tencent.com/
    title: "WorkBuddy 官网"
---

# 微信聊天记录转发 WorkBuddy 与两个 Skill

> **⚠️ flagged：** 文章标题级的两项核心声明核验失败——①「官方开的口子**不怕封号**」是把「微信提供原生入口」推成「腾讯保证不封号」，检索不到任何官方承诺或说明；②「两个 skill **都开源**」**不可验证**（不是已证伪），zip 获取方式仅存于评论区置顶，正文无仓库、许可证、版本或源码。详见 [P0 核验报告](references/verification.md)。
>
> **一句话决策摘要**：**入口路径可以采信**（微信内原生合并转发 → 转发到其他应用 → WorkBuddy，有多源第三方佐证），但**「不怕封号」不可当平台承诺、「都开源」不可当已可获取**；本束提供的是事实边界与可迁移设计思路，**不提供可照做的安装教程**。
>
> **内容性质**：产品功能资讯 + 操作路径登记，**非可复现实操教程，未在本机实跑**。本束按「操作可复现性两问」第二问为否，**不设 `examples/`**。

微信公众号《微信聊天记录终于能正经交给 AI 了，官方开的口子不怕封号》（林月半子聊AI，2026-10-10，F-001~F-004）讲的是同一条路径上的两件事：微信合并转发弹窗新增「转发到其他应用」可选 WorkBuddy（F-013/F-016），作者据此做了「工作群日报」与「家族群辟谣卡」两个 skill（F-035/F-036）。

本束把它转成可溯源知识包：**120 条 F 编号事实**（双份登记）、**20 项 P0 权威核验**、**6 项勘误**（E-1/E-2 命中核心声明，E-3~E-6 为口径与出处差异），并沉淀 **5 个可迁移模式**。

## 阅读路径

1. [原文事实清单](references/article-source.md) → [P0 核验报告](references/verification.md)：先建立事实与可信度边界
2. [官方入口、四步路径与「不怕封号」的证据边界](concepts/00-official-entry-and-path.md)
3. [工作群日报 Skill](concepts/01-daily-report-skill.md) → [家族群辟谣卡](concepts/02-factcheck-card-skill.md)
4. [可迁移模式、操作路径登记与可复现性边界](concepts/03-transferable-patterns-and-boundaries.md)

## 核验摘要

| 结论 | 数量 | 要点 |
|------|------|------|
| ✅ 通过 | 9 项 | 四步路径与第三方实测一致、100 条量级上限有官方帮助支撑、2026-01 DMCA 下架事件有腾讯回应 + 项目 README 直证、WorkBuddy 产品定性、三条辟谣结论方向 |
| ❌ 核心失败 | 2 项 | E-1「不怕封号」无官方依据（F-030/F-111）、E-2「都开源」不可验证（F-037/F-120） |
| ⚠️ 口径 / 出处差异 | 4 项 | E-3 100 条端差异与 2MB 上限、E-4 ETC 引文媒体名不符、E-5 微信收费栏目名与措辞不符、E-6 官方公告缺口 |
| 📝 不可核验但未证伪 | 3 项 | zip 实际内容、「三条硬规矩」具体规则、三个规划 skill 的实现状态 |

三条辟谣依据中，只有「光明网转载的健康上海 12320」**逐字精确对应**（F-115）；另两条结论成立但出处记错（F-117/F-118）。

## 已知边界

- **不可复现**：两个 skill 的 zip 无正文链接、无版本、无源码、无输入输出样例、无运行日志（F-040/F-096~F-099/F-120）；提示词与四步路径是原文照录，不是演练。
- **图片未转录**：整条路径图、日报结构清单、五风格对比、辟谣长图/单条卡、**「三条硬规矩」**、入口生态图共 6 处以上，正文无文字，本束一律留白不补写（F-017/F-050/F-073/F-082/F-095）。
- **作者自述数字**：216 条消息、36 人、27 张图、6 话题、3 链接、14–15 点 56 条等均无独立复核（F-045~F-049/F-097），不得当容量或性能基准。
- **无版本号**：正文未给微信 / WorkBuddy / skill 版本（F-096）；入口能力依赖双端版本，列表中的应用集合与条数上限均可能变化。
- **100 条上限不是全平台硬规则**：企业微信官方帮助为「最多 100 条」并附 **2MB** 消息体积上限；「微信派」2025-03-25 就个人微信答复 **iOS 100 / 安卓 99**（F-101/F-102，勘误 E-3）。文章把它简化为「微信一次最多只能选 100 条」。
- **无官方公告**：目前只有第三方媒体快讯与个人实测文佐证入口（F-103~F-106）；且这些实测文发表于同一时间窗、可能彼此转载，独立性有限。不得表述为「腾讯已发布正式公告并作出承诺」。
- **时效**：`stale_after: 2026-12-31`；复核项见 [核验报告](references/verification.md) §5。

## 主题关联

| 关联知识包 | 分工 |
|-----------|------|
| [wigolo 本地 Web 情报层](../wigolo/index.md) | 同为「微信博文经七阶段转化」的本地情报工具；本束聚焦微信原生入口与两个 skill，wigolo 聚焦搜索/抓取/研究工具链 |
| [Skills Manager 跨 AI 编程工具技能库](../skills-manager/index.md) | 同组 skill 管理主题；本束的两个 skill 是具体用例，Skills Manager 讲集中式管理与 Agent 集成边界 |
| [Knocket 会聊天的个人名片（腾讯 RTC）](../knocket/index.md) | 同组腾讯系产品、同为微信博文核验转化；本束以聊天内容为输入，Knocket 以客户接待为入口 |
| [WorkBuddy 全媒体内容系统](../../../../sheke/industry/workbuddy-content-system/index.md) | 同为 WorkBuddy 主题且同为 flagged 的博文转化束；该束是商业分析/内容流水线，本束是产品入口与工具机制 |
| [腾讯生态 AI 知识包分组](../../ecosystems/tencent/index.md) | 腾讯官方文档与生态资料集合；本束为第三方作者实践，不做官方资料收录 |

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```
