---
type: Reference
title: "三入口信源、版本与覆盖台账"
status: draft
date: "2026-10-27"
sources:
  - id: zh-a
    resource: https://zhuanlan.zhihu.com/p/2091930347550109878
  - id: wb-p
    resource: https://www.workbuddy.link/p/8QYARuAmZ9RgQty3FSzNUs?source=2
  - id: tt-entry
    resource: https://mp.toutiao.com/gf/exclusive?enter_from=menu
---

# 三入口信源、版本与覆盖台账

本页承接Task1–3研究代理于2026-10-27回传的公开资料；Task8另于当日10:57:17/18 UTC+8实际读取指定W-R/W-H，限于修补13字段与代维权条款。正式编号及缺口见[事实底账](facts.md)，发布决策见[版权与发布顺序](../concepts/05-rights-and-publication-order.md)。本包为实施草稿，作者自验与工程检查见[验证记录](verification.md)，独立R1未通过，待R2；历史原始证据未取得的范围不冒称已逐字复验。

## 来源层级与读取边界

“官方”描述来源身份，不等于完整、最新或独立多源。本轮每个平台仍属各自的官方源族；同页不同载体、同平台互引公告、重复 CLI 查询不计作独立第三方证据。旧包是带历史日期的本地基线，不是本轮第二个独立来源。

| 键 | 来源与定位 | 类型、采集状态 | 时点或版本 | 支撑范围 |
|---|---|---|---|---|
| Z-A | [知乎科学活动文章](https://zhuanlan.zhihu.com/p/2091930347550109878)；活动时间、双赛道、参与方式、内容要求、活动说明、评选规则 | 认证机构号“知乎科学”；官方 CLI 公共搜索取得片段，非全文 | 采集 2026-10-27 10:07:16 UTC+8；CLI `EditTime=1792396307`，换算 2026-10-19 15:51:47 UTC+8 | F-001 至 F-025；ZH01 至 ZH25 |
| Z-B | [AI Works 部署公告](https://zhuanlan.zhihu.com/p/2079176428197603018)；部署及发布尾段 | 本轮尾段未取得；仅保留 CLI 编辑元数据与旧包历史机制，不声称当日全文复核 | 本轮 `EditTime=1788501616`，换算 2026-09-04 14:00:16 UTC+8；旧包页脚记录见 E-001 | G-002、G-006 |
| W-P | [WorkBuddy 活动入口](https://www.workbuddy.link/p/8QYARuAmZ9RgQty3FSzNUs?source=2)；bootstrap | 官方活动页公开引导；当前版本已取得，静态壳不能单独充当规则全文 | 2026-10-27；`publishVersion=54` | F-026 |
| W-R | [当前状态树](https://workbuddy-space-static.codebuddy.work/page/8QYARuAmZ9RgQty3FSzNUs/Carn2iELxRnY/janus.data.json)；`$.igSoGL6VmmPNDERL8yhJU3.content` 内 `ruleHTML()` | 研究代理回传完整细则；Task8另实读HTTP200并提取四/6(3)，单点官方规则，不当旧响应 | 2026-10-27；研究回传54载体秒级未知；Task8实际10:57:17 UTC+8 | F-027 至 F-032、F-034 至 F-039、F-048 至 F-060中回传规则条目；F-083为Task8当前逐字补核 |
| W-H | [当前页面实现](https://workbuddy-space-static.codebuddy.work/page/8QYARuAmZ9RgQty3FSzNUs/Carn2iELxRnY/WorkBuddy1024造物挑战征集活动.html)；`openForm()`、`FORM_OPTIONS`、`fRaw`、`fUrl`、`fConversation`、`renderLinkGuide()`、`pDate`、`SUBMIT_END` | 官方前端实现；Task8另实读HTTP200核13字段、11星号及长度，不升格后端结果 | 2026-10-27；研究回传54载体；Task8实际10:57:18 UTC+8 | F-033、F-040至F-047；本轮逐字段补核F-040及材料页13行 |
| W-B | [旧版状态树](https://workbuddy-space-static.codebuddy.work/page/8QYARuAmZ9RgQty3FSzNUs/jJOM0P6H8uMT/janus.data.json)；`ruleHTML()` | 研究代理回传当前/旧版规则字符串机械完全一致；表单提示不一致 | 旧载体49；旧包采集基线 2026-10-24 | C-002、E-002 |
| W-S | [WorkBuddy 服务协议](https://rule.tencent.com/rule/202603180001) | 关联真实链接；本轮未读正文，非“没有协议要求” | 本轮未取得内容版本 | G-019 |
| W-V | [WorkBuddy 隐私政策](https://privacy.qq.com/document/preview/771d9a58551449e9a7e7445ebfe04966) | 关联真实链接；本轮未读正文 | 本轮未取得内容版本 | G-019 |
| T-ENTRY | [用户提供的头条入口](https://mp.toutiao.com/gf/exclusive?enter_from=menu) | 本轮未取得实际入口正文、适用协议或账号资格；不得用 URL 的 exclusive 字样判定计划 | 2026-10-27 未确认；旧TT F-104 仅为历史基线 | G-020、E-006 |
| T-A | [首发激励官方百科](https://baike.toutiao.com/detail/242/566/0)；正文及 `RENDER_DATA` 完整 FAQ | 研究代理取得全文及 FAQ；关联规则研究，不能自动确认为 T-ENTRY 的适用条款 | 页面更新 2026-05-25 11:14:32（页面标值，时区未提供） | F-061 至 F-080 中首发条目 |
| T-B | [首发规则升级公告](https://www.toutiao.com/article/7540173896595620404/)；补贴与质量段 | 官方公告；与 T-A 同平台且互引，非独立多源 | 公告 2025-08-19 14:24（页面标值，时区未提供） | F-074、F-075 |
| T-C | [头条用户协议](https://www.toutiao.com/user_agreement/)；3.9 | 本轮读取片段自3.9至9.3，不是全文；3.9自动同步与首发禁同步示例须并列 | 当日采集，协议整体版本未取得 | F-081、G-022、G-024 |
| T-D | [文章原创官方百科](https://baike.toutiao.com/detail/242/243/0)；正文及 FAQ | 原创面规则，不能当首发或独家协议 | 当日采集；研究输入未提供更新时刻 | F-082 |
| T-E | [创作者计划历史百科](https://baike.toutiao.com/detail/242/255/0) | 2021历史背景；不替代当前资格页 | 页面日期 2021-10-22 | F-082、G-021 |
| T-F | [收益历史百科](https://baike.toutiao.com/detail/192/198/0) | 历史收益背景；不保证当日权益、基础分成或收益 | 页面日期 2021-10-22 | F-082、G-021 |

T-A 至 T-F 的本轮采集窗口为 **2026-10-27 10:09:17–10:11:39 UTC+8**；窗口是整路研究范围，不冒充每个请求的秒级时刻。W-R 与 W-H 的逐字段分层，以[事实底账](facts.md)每行标注为准。

## 旧包关联与使用纪律

| 映射简称 | 实际底账 | 历史时点 | 本轮用途与禁用项 |
|---|---|---|---|
| 旧ZH | [知乎活动事实表](../../zhihu-ai-science-workshop/references/article-source.md) | 原活动采集 2026-10-22/23；部署页脚记录 2026-10-23 | 对照旧 F 编号；预览/正式链接机制仅历史引用；不沿用“活动已结束” |
| 旧WB | [WorkBuddy事实表](../../workbuddy-1024-contest/references/facts.md)及[历史核验](../../workbuddy-1024-contest/references/verification.md) | 2026-10-24；载体49 | 保留121个历史唯一 F 编号含字母后缀；不沿用旧作品墙0、0–9人气推导或固定提前两天工期 |
| 旧TT | [头条事实表](../../toutiao-monetization/references/article-source.md)及[历史核验](../../toutiao-monetization/references/verification.md) | 2026-10-23 | 对照首发与收益面；旧TT F-104 入口确认本轮未复现；旧2026-08-27资格页不被2021背景页覆盖 |
| 旧内容系统 | [WorkBuddy全媒体内容系统](../../workbuddy-content-system/index.md) | 2026-09-20，个人文章解读 | 仅方法候选关联，不将作者自述收益当规则或实测结果；不承接其产品能力作当前官方口径 |

旧号没有直接对应时写“旧概念概括”或“新增”，不虚构旧 F 编号。旧包的错位、过宽总结及历史状态只在本包留痕，不修改旧文件。

## 条款覆盖矩阵

| 问题域 | 知乎 Z-A | WorkBuddy W-R/W-H | 头条关联公开规则 |
|---|---|---|---|
| 主体与入口性质 | F-001 至 F-003；科学活动双赛道 | F-026、F-027；主体原文保留“拟” | T-ENTRY 未确认，G-020；T-A不是赛事 |
| 资格与工具 | F-006、F-011 至 F-014；G-005、G-007 | F-028、F-029、F-035、F-036、F-042 | F-072、F-073；G-020、G-021 |
| 时间与审核 | F-002、F-021、F-024；G-001、G-002 | F-030 至 F-034、F-038、F-060；G-010 | F-061 至 F-065；G-024 |
| 材料与链接 | F-015 至 F-019；G-002、G-007 | F-039至F-048；F-040含13字段与11必填，材料页完整字段/长度/填写边界；G-013 | F-080；实际声明页未取得，G-020 |
| 评分、激励与处罚 | F-008 至 F-010、F-020 至 F-025；G-005 | F-049 至 F-054、F-059；G-008、G-009、G-011 | F-071 至 F-080；E-005；G-021 |
| 原创、重复与跨投 | F-012 至 F-014、F-022、F-023；G-003 | F-036、F-059；G-016 | F-061 至 F-070、F-079；G-023 |
| 授权、撤回与申诉 | G-004，未取得关联协议 | F-055至F-058、F-060；F-083代维权含监测/维权函/诉讼仲裁/调解和解/决策独立实施/必要配合，本人决定授权；G-014、G-015、G-017至G-019 | F-070、F-078、F-081、F-082；G-022、G-024 |

## Task8 可验证短引与历史局限

W-R四/6(3)当前短引：“主办方有权对维权事宜做出决策并独立实施。”、“您有义务在主办方发起维权时予以必要配合。”；W-H字段11/12当前短引：“不是邮箱、微信、手机号或 UIN”、“联系方式不展示在作品墙”。这些短引在本轮响应中逐字回验，不复制完整细则、表单源码或作品墙记录入公开包。

本轮已留仓库外响应字节、HTTP状态、UTC采集时点与SHA-256，定位和复验结果见[Task8记录](verification.md#task8-修补与当前证据)。它们只证明本轮读取。Task1–3三路原始响应、当前/旧版规则比较原件及Task6写前三索引快照在限定检索中未取得；回传摘要和指纹自述仍保留历史身份，不足以独立证明当时逐字覆盖或索引只加本包。不得生成“历史快照”补这个缺口；不据当前来源冒称全部CP-2/CP-7已通过。

## 复查触发与最低动作

投稿前按各平台当日规则再次确认身份、适用协议、工具绑定与体验链接；本包不代为操作。来源更新、WorkBuddy发布版本变化、实际入口可访问或平台回复缺口时重核对应编号。2026-10-31之后不得继续将知乎活动写作“仍可参赛”，2026-11-01之后重核 WorkBuddy 征集状态；公告延期须有新来源。

公开包不收录实际投稿正文、创作私聊、未授权截图、收入或任何密钥。本页仅指向公开来源，没有镜像全文；Task8仅对指定W-R/W-H定点复核，没有重做三路全面研究，亦未报名、发布或签约。
