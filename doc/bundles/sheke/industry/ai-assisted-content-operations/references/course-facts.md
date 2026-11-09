---
type: Reference
title: "课程事实与主张登记（F-001～F-030）"
route: chaptered-summary
sources:/n  - id: s1-purchased-session
    resource: "session:cdp-purchased-2026-11-09"
status: flagged
stale_after: 2026-12-09
generated: { by: "process:seven-concepts-cmd", at: "2026-11-09T06:23:33Z" }
---

# 课程事实与主张登记

F-001～F-030 共 **30 条**，是本包唯一 F 台账，其它页面只引用编号，不建立第二份。分层：F-001～F-008 采集通道与加工规范，F-009～F-019 六篇教程的方法链与口径冲突登记，F-020～F-030 双包分账、适用边界与模式。**本包编号与同组短故事包互不通用**（F-020）。

`session_fact` 只确认「已购课会话里取到了什么」；`lecture_derived` 记录 ASR 派生稿的原创改写，只回答「课堂讲了什么」，不认证方法有效性、不作逐字引语；`conflict` 与 `unverified_claim` 记录口径差异与待核验主张，不合并抹平、不写成事实；`negative` 记录明确缺席；`scoped` 记录适用边界。逐项裁决见[核验与勘误](verification.md)。

| F | claim | type | source_id | locator | status |
|---|---|---|---|---|---|
| F-001 | 30 节搭售赠课录播合计 17.25 小时、1201.2 MB，均为同一课程已购课会话下可见的最小清晰度原件 | session_fact | s1 | 目录接口 40 节中 idx 10～39 | observed |
| F-002 | 采集沿用第三轮的浏览器进程内 CDP 通道；未导出、复制或保存账号凭据，未写入播放签名地址 | session_fact | s1 | 采集通道 | observed/scoped |
| F-003 | 播放签名地址有有效期；过期后由登录态目录接口重新签发，元数据未变化，无需重新登录 | session_fact | s1 | 签名刷新 | observed |
| F-004 | 30 节全部完成音频转写，产出 30 份带时间戳的 ASR 派生稿；派生稿不是逐字稿，存在同音字与专名误识 | session_fact | s1 | ASR 覆盖 | observed/scoped |
| F-005 | 逐字转写文本、播放签名地址、账号凭据与本地文件路径均不入库；仅保留去品牌化的结构化要点笔记作为加工素材 | scoped | s1 | 入库边界 | observed/scoped |
| F-006 | 登录态目录里 file_list 全空、playlist_v2 全 null、笔记接口空列表；本批赠课同样无讲义、课件附件与官方字幕 | negative | s1 | 字段核查 | observed |
| F-007 | 30 份要点笔记按四小节结构产出（环节顺序／方法要点／案例与举例／边界与负向），每份均做去品牌化自查 | scoped | s1 | 加工规范 | observed/scoped |
| F-008 | 六篇教程按主题聚类：同一主题下的多节内容合并为一条方法链，不按课次流水账复述 | scoped | s1 | 编排决策 | observed/scoped |
| F-009 | 定位方法链：自我盘点 → 赛道收窄 → 人设要素 → 主页承接 → 对标账号校验与差异化 | lecture_derived | s1 | 第 01 篇 | asr-derived/rewritten |
| F-010 | 平台方法链：先按分发机制给平台分类 → 判内容形态与排版约束 → 做冷启动最小验证 → 按机制差异调投放节奏 | lecture_derived | s1 | 第 02 篇 | asr-derived/rewritten |
| F-011 | idx 12 与 idx 36 主题重叠但表述有差异，按「不同场次表述差异，待核验」并列登记，不合并抹平 | conflict | s1 | 第 02 篇 | observed/scoped |
| F-012 | 脚本生产链：选题来源 → 标题候选与筛选 → 输入框架与约束 → 由粗到细结构化脚本 → 人工质量把关与局部润色 → 热点风险控制 | lecture_derived | s1 | 第 03 篇 | asr-derived/rewritten |
| F-013 | 批量生产里人只守判断节点：判断环节只输出分析与风险项、不改原文，决定权归创作者 | lecture_derived | s1 | 第 03 篇 | asr-derived/rewritten |
| F-014 | 视觉生产链：分镜与关键帧描述 → 素材来源与授权合规 → 视觉一致性约束 → 拼接／配乐／字幕／封面收口 → 导出前检查 | lecture_derived | s1 | 第 04 篇 | asr-derived/rewritten |
| F-015 | 素材商用授权、版权检测等被口播归给「官方规则」的说法，本包一律标为待核验主张，不写成事实或操作保证 | unverified_claim | s1 | 第 04 篇 | pending-verification |
| F-016 | 变现链按「内容生产 → 流量 → 成交」三段定位，再按产品形态分类；先判自身前提（人群／交付能力／履约成本），最后才谈付费投放的最小验证与止损 | lecture_derived | s1 | 第 05 篇 | asr-derived/rewritten |
| F-017 | 所有收益、转化、涨粉、投放回报、费率、定价与人数数字，均登记为「出现但不采信」，不进入教程结论 | scoped | s1 | 第 05 篇 | observed/scoped |
| F-018 | 运营链：分层看受众关系 → 用数据定位掉点环节而非只看总量 → 异常按「先自查动作、再查内容、最后归因机制」诊断 → 迭代一次只改一个变量 | lecture_derived | s1 | 第 06 篇 | asr-derived/rewritten |
| F-019 | 账号权重、限流规则、审核机制等被口播归给平台官方的说法均为待核验主张；idx 33 与 idx 34 口径重叠，按不同场次表述差异并列登记 | unverified_claim | s1 | 第 06 篇 | pending-verification |
| F-020 | 本包 F 编号独立（F-001～F-030），与同组短故事包的 F-001～F-139 编号互不通用、不交叉引用 | scoped | s1/s2 | 编号分账 | observed/scoped |
| F-021 | 两包共用一次已购课会话，但赠课属另一产品线；方法、案例与结论互不印证，不拼成因果链，也不互相背书 | scoped | s1/s2 | 双包分账 | observed/scoped |
| F-022 | 本包不认证任何平台规则的当前状态：平台规则高频修订，课堂口播不是官方文本，静态清单会过期 | scoped | s1 | 适用边界 | observed/scoped |
| F-023 | 教程层不出现具体产品名、平台名、机构名、人名、金额、作品名、课程编号与讲师头衔；举例只保留类型与用途 | scoped | s1 | 去品牌化 | observed/scoped |
| F-024 | 本包所有表格均为依据口述内容重新组织的原创改述，不是课堂讲义表格；课件画面文字、模板截图与官方字幕未取得 | negative | s1 | 表格纪律 | observed |
| F-025 | 课堂未给出可复现的版本、输入输出与验收结果，可复现性两问皆否，故不建 examples/ | scoped | s1 | 结构决策 | observed/scoped |
| F-026 | 全包 route 恒为 chaptered-summary、status 恒为 flagged；逐字转录不在批准集内 | scoped | s1 | 路线决策 | observed/scoped |
| F-027 | L1 模式为单案例（一次会话、一门搭售赠课），成熟度不因覆盖面扩大而升级 | scoped | s1 | 模式 | observed/scoped |
| F-028 | 四视角对抗审查 8 条全部采纳，覆盖待核验主张、去品牌化、双包分账、表格纪律与口径冲突 | scoped | s1 | V 门 | observed/scoped |
| F-029 | 全包 16 篇 Markdown（6 教程／6 参考正文／3 索引／1 日志）、30 条事实、30/30 内容级覆盖 | scoped | s1 | 规模 | observed/scoped |
| F-030 | 新增事实从 F-031 顺延，不重排既有编号；既有行结论不因后续核验追改，只在核验页补裁决 | scoped | s1 | 编号维护 | observed/scoped |

## 编号维护

新增事实从 **F-031** 起顺延，不重排既有编号。30 条一次性登记，对应 30 节赠课完成内容级转写这一轮采集；若后续取得讲义、课件画面文字或平台官方规则全文，应各自新增编号并补裁决，不修改本表已有行的结论。
