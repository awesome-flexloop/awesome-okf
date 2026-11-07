---
type: Reference
title: "课程事实与主张登记（F-001～F-060）"
route: chaptered-summary
sources:
  - id: facts
    resource: "course-facts.md"
status: flagged
stale_after: 2026-12-07
generated: { by: "process:seven-concepts-cmd", at: "2026-11-07T02:52:45Z" }
---

# 课程事实与主张登记

F-001～F-060 共 **60 条**，是本包唯一 F 台账，其它页面只引用编号，不建立第二份。分层：F-001～F-012 详情页页面事实，F-013～F-024 售卖页页面事实，F-025～F-040 宣传长图单源主张，F-041～F-054 第三方公开旁证，F-055～F-060 负向事实与适用边界。

`page_fact` 只确认「页面字段／渲染文字写了什么」；`poster_claim` 只记录「宣传图怎么说」，单源、无样本、无对照；`third_party` 记录第三方主体怎么转述，不认证其真实性；`negative` 记录明确缺席；`scoped` 记录适用边界。逐项裁决见[核验与勘误](verification.md)。

| F | claim | type | source_id | locator | status |
|---|---|---|---|---|---|
| F-001 | 详情页 URL 为 `course-detail/2097021606392607963`，HTML `title` 为「短故事系统课【261102】」，免登录可读 | page_fact | s1 | HTML head | observed |
| F-002 | 内嵌 JSON 中 `course.id=2097021606392607963`、`course.title` 与 `sku.name` 同为课程标题、`sku.id=2097021607579592530`、`teacher=["知乎知学堂"]`（机构名） | page_fact | s1 | `__connectedAutoFetch` | observed |
| F-003 | `course.courseType` 为「正价课」 | page_fact | s1 | `base.course` | observed |
| F-004 | `onlineSectionCount=39`、`presetSectionCount=39`、`fishedSectionCount=0` | page_fact | s1 | `base.course` | observed |
| F-005 | `ownerShip.hasOwnership=false`、`hasMonitorCourseMember=false`、`isPermanent=false`；采集会话无购课权限 | page_fact | s1 | `base.ownerShip` | observed/scoped |
| F-006 | `chapter` 列表 6 项，`firstSectionIdx` 依次为 0、3、4、7、8、9；另有等价的 `chapters` 列表 | page_fact | s1 | `base.chapter` | observed |
| F-007 | 6 个章节标题：【导学课】、【开营直播】、第一章-拆爆款找素材、【课程主题直播】、【小灶答疑直播】、【AI超级个体-赠课】 | page_fact | s1 | `base.chapter[].title` | observed |
| F-008 | `classNote` 给出两种上课方式：独立 APP 用购课手机号登录；主站 APP「我的-已购-课程卡片」进入，连麦与交作业需独立 APP | page_fact | s1 | `base.course.classNote` | observed |
| F-009 | `attentionPoint` 提示订单信息同步至教学平台，并要求保持在平台内下单与上课 | page_fact | s1 | `base.course.attentionPoint` | observed |
| F-010 | `description` 仅含一张 1280×13015 的 PNG 图片（`<figure><img>`），无文本层；`rawDescription` 为 3 个 block，其中 1 个是 IMAGE 实体 | page_fact | s1 | `base.course.description` | observed |
| F-011 | `homeWork.hasHomeWork=false`、`downloadCache.canDownload=0`、`courseDatum.isShow=false`、`learnReport.isShow=true` | page_fact | s1 | `base.*` | observed |
| F-012 | 课程卡片渲染「已学习 0 / 39」 | page_fact | s1 | 页面文本 | observed |
| F-013 | 售卖页 URL 为 `sku-detail/2097021607579592530`，HTML `title` 与详情页一致，免登录可读 | page_fact | s2 | HTML head | observed |
| F-014 | `priceBar`：`originPrice=3980`、`payType=0`、`promotionType="normal_sale"`、`joinPeopleCount=11`、`interestCount=999`、`heatCount=1529` | page_fact | s2 | `priceBar` | observed |
| F-015 | 页面文案渲染「999 人感兴趣 · 1529 热度」 | page_fact | s2 | 页面文本 | observed |
| F-016 | `catalog.paging` 为 `{limit:20, offset:0, total:39}` | page_fact | s2 | `catalog.paging` | observed |
| F-017 | `catalog.extra`：`headerText="已完结"`、`footerText=""`、`showChapterName=true`、`isDisabledBuy=false` | page_fact | s2 | `catalog.extra` | observed |
| F-018 | `catalog` 第一页 20 条、`offset=20` 第二页 19 条，按 `idx` 合并得 39 条连续快照（0～38）；`offset=40` 回落首页 | page_fact | s2 | 两次 SSR 抓取 | observed |
| F-019 | 39 节按 `type` 分为 `video` 36 节、`live_stream` 3 节 | page_fact | s2 | `catalog.data[].type` | observed |
| F-020 | 3 个 `live_stream` 的 `status.text` 均为「直播 · 已结束」、`livestreamStatus="ended"`、`isLiveStreaming=false` | page_fact | s2 | `catalog.data[].status` | observed |
| F-021 | 章节分布：导学 3、开营直播 1、第一章 3、主题直播 1、答疑直播 1、赠课 30；赠课 30 节标题仅为顺序编号，公开页未给各节主题 | page_fact | s2 | `catalog.data[].chapter` | observed |
| F-022 | 每节 `right` 均为 `isFree=false`、`canExperience=false`、`appCanBuy=true`；未购不可试看 | page_fact | s2 | `catalog.data[].right` | observed |
| F-023 | 6 节与正课直接相关的录播及 `status.text`：导学01 20:00、导学02 20:45、导学03 17:58、第1课 31:29、第2课 30:00、第3课 36:08；标题依次涉及变现、AI 辅助从选题到成稿、影视化影响力、拆解爆款、生活素材、隐藏爆款类型 | page_fact | s2 | `catalog.data[]` | observed |
| F-024 | `startAt` 换算到北京时间：导学 2026-10-26 00:00；开营直播 11-02 19:00；第一章三节 11-02／03／04 00:01；主题直播 11-04 19:00；答疑直播 11-06 19:00；赠课 11-02 00:00 | page_fact | s2 | `catalog.data[].status.startAt` | observed |
| F-025 | 课程介绍长图为 1280×13015 RGB PNG、无文本层；本次以标准库无损裁成 9 块逐块读图，未做 OCR | page_fact | s3 | 图片采集记录 | observed/scoped |
| F-026 | 长图「课程背景」设问：想通过写作投稿签约？想拥有副业 + 稳定收入？并配「困难重重」「一筹莫展」标签 | poster_claim | s3 | 第 1 块 | single-source |
| F-027 | 「一次性解决」列 5 个痛点：没想法、没方法、不会投、不会用AI、用不好AI | poster_claim | s3 | 第 1～2 块 | single-source |
| F-028 | 5 个痛点分别配解释：写故事没灵感无从下笔；写稿枯燥无技法可循；想投稿不知怎么投、投到哪；想用 AI 写故事但工具技巧一窍不通；有 AI 基础仍写不好故事 | poster_claim | s3 | 第 1～2 块 | single-source |
| F-029 | 口号「多年积累的写作成功经验 + 真实解决痛点的实战教学」 | poster_claim | s3 | 第 2 块 | single-source/flagged |
| F-030 | 适用人群 4 类：对 AI 创作感兴趣想跟上风口、想经济独立利用空闲时间开启第二职业、要工作以外多份收益补贴家用、有故事想讲却无从下笔的写作爱好者 | poster_claim | s3 | 第 2～3 块 | single-source |
| F-031 | 课程亮点 5 项：顶级课程研发、爆款黄金公式、编辑精细批改、审稿反馈直通、长期投稿绿通 | poster_claim | s3 | 第 3～4 块 | single-source/flagged |
| F-032 | 亮点标语「爆款方法全拆解，精批投稿一路通」 | poster_claim | s3 | 第 4 块 | single-source/flagged |
| F-033 | 「授课名师」列 3 位，自述头衔含作协副主席、网络作协副主席、男频／女频创作导师、影视编剧、出版作者、S+ 级年番策划、平台签约作者等 | poster_claim | s3 | 第 4～6 块 | single-source |
| F-034 | 名师自述数字：网络文学创作近 20 年、短篇与长篇 50 余篇、总字数超八千万、总阅读量超 10 亿次、图书累计销量 50 万+、累计创作近 200 万字、数十篇万赞爆款、作品累计超百万点赞 | poster_claim | s3 | 第 4～6 块 | single-source/flagged |
| F-035 | 「课程大纲」按 5 模块组织：打通商业路径、搭建故事骨架、完成故事创作、掌握投稿变现、进阶短剧改编 | poster_claim | s3 | 第 6～7 块 | single-source |
| F-036 | 5 模块说明：看懂变现模式并建立 AI 创作与影视化思维；掌握爆款选题、人物塑造与结构设计并完成大纲；强化开篇情节细节对白并独立完成一篇；优化包装与付费卡点匹配收稿偏好；掌握 AI 辅助编剧与原著拆解、短剧工业化改编流程 | poster_claim | s3 | 第 6～7 块 | single-source |
| F-037 | 「课程权益」列 7 项：学习权益、大咖直播课、小班制陪跑、打磨人生作品、绿通投稿渠道、投稿有回响、长周期培养 | poster_claim | s3 | 第 8～9 块 | single-source |
| F-038 | 权益数字：33 名师讲堂、每周 2 节导师陪跑直播（共 16 节）；每月 1 次知名作家直播持续 6 个月（至少 6 节）；20–25 人小班、4 次作业点评；50+ 投稿联盟平台；8 家平台审稿编辑部；6 个月新作家培养扶持计划 | poster_claim | s3 | 第 8～9 块 | single-source/flagged |
| F-039 | 「只要稿件符合最基础的要求，保证收稿」 | poster_claim | s3 | 第 8 块 | single-source/flagged |
| F-040 | 「稿件直达 8 家顶级平台审稿编辑部……篇篇有反馈」 | poster_claim | s3 | 第 9 块 | single-source/flagged |
| F-041 | 媒体报道：知乎自 2020 年起开设故事写作类付费课程；据平台数据，2023 年向付费阅读业务输送超 800 位签约创作者、向社区输送超 1500 位商业创作者、向全网输送超 3000 位创作者，超 5000 篇内容上线并创造收益 | third_party | s4 | 报道第 2 节 | single-source |
| F-042 | 同报道：盐言故事内容超 10 万篇、覆盖 180 多个细分品类、近百部售出影视版权、改编有声剧超 2700 部 | third_party | s4 | 报道第 1 节 | single-source |
| F-043 | 同报道：体验课后正式课学费 3980 元，对应长达四个月的课程安排 | third_party | s4 | 报道第 2 节 | single-source |
| F-044 | 同报道转述推广信息：新人过稿签约后单篇单月平均分成 2000–5000 元、盐选收益单月最高 80W+；编辑带教、内投绿色通道、编辑直审与流量扶持 | third_party | s4 | 报道第 2 节 | single-source/flagged |
| F-045 | 同报道：记者体验另一门体验课后转述的技巧为「开头第一段就要吸引读者兴趣」与「尽量选择甜、虐、爽等强情绪题材」 | third_party | s4 | 报道第 2 节 | single-source/scoped |
| F-046 | 同报道：受访购课学员称课程让学员对爆款文章做拆解与仿写但「没有任何写作技巧方面的」，投稿未过审理由为「主线不够清晰，叙事拖沓、混乱」；平台回应承认「在线教育仍然存在个性化服务不足」 | third_party | s4 | 报道第 2 节 | single-source |
| F-047 | 学员自述：作者为 250623 期学员，课程为八周、每周解锁知识点，含案例、直播讲解、作业批改与助教陪同 | third_party | s5 | 自述第 2 节 | single-source |
| F-048 | 同文：首次投稿被拒理由为「情节设计套路化或情节张力不足」；后续调整被描述为「反套路、微创新」，理由是人工审稿者已读大量同类题材、需要新素材新设定新情节 | third_party | s5 | 自述第 2 节 | single-source |
| F-049 | 同文：称这类短篇「最好的文笔是精准」，用口语化表达把事情、情绪、主线讲清楚即可，不必华丽辞藻 | third_party | s5 | 自述第 2 节 | single-source |
| F-050 | 同文给出工作流：加工提炼主线 → 人物设计 → 写出大纲 → AI 辅助 → 按课堂所教做人工修改 | third_party | s5 | 自述第 2 节 | single-source |
| F-051 | 同文：四类取材提法（改编社区原新闻事件、按教学方法踩中节日流量、社区论坛自带话题与「世情文」、生活观察），并给出单方晒单：三四月合计 5100 多元、4 月分账 17992.12 元、单月完读 80 万次、男频榜第五名、漫改与漫剧版权邀请 | third_party | s5 | 自述第 2～3 节 | single-source/flagged |
| F-052 | 第三方开源仓库 `zhihu-style.md`：盐言风格 4 特征（第一人称限定、`「」` 对话独立成段、短句一句一信息点、段首两全角空格）；7 项拆文检查（含短句占比 > 70%、反转在 70–85% 位置、章尾钩子）；6 类题材情绪模式；知乎／番茄／小红书三平台差异表（含 8000–20000 字等数值） | third_party | s6 | 全文 | single-source/scoped |
| F-053 | 公开检索中「七步故事法」至少有 4 个互不相同的版本：目标-阻碍-行动-意外-转折-结果；目标-阻碍-努力-结果-意外-转弯-结局；背景-倾斜-斗争-挫折-抉择-转折-结果；开场-触发-尝试-危机-转折-高潮-收尾 | third_party | s7 | 4 个转载页 | single-source |
| F-054 | 招募推文：2 日体验课安排（DAY1 三大变现主题与起步秘诀；DAY2 两大渠道、「7 步故事法」与平台中稿秘诀），并列出六种开篇钩子（反转型、悬念型、反常型、矛盾型、突发型、引人共情式）；均未给公式内容 | third_party | s7 | 推文正文 | single-source |
| F-055 | 本次未取得任何一节课程视频、讲义、字幕、作业正文、批改记录或课堂原始表格 | negative | s1/s2 | 采集边界 | observed/negative |
| F-056 | 本次未取得退款条款、合同文本、学员协议，也未取得对师资自述头衔与作品数据的第三方核验 | negative | 全部 | 采集边界 | observed/negative |
| F-057 | 口径冲突一：宣传图「33 名师讲堂 + 共 16 节直播」与售卖页 `catalog.total=39`（直播仅 3 节）不一致；33+16=49≠39，成因在公开面不可判定，并存不合并 | negative | s2/s3 | 交叉核对 | observed/negative |
| F-058 | 口径冲突二：宣传图 5 个能力模块与售卖页 6 个运营章节无一一对应，且售卖页仅到「第一章」；`catalog.extra.headerText="已完结"` 与按 `startAt` 推算的解锁进度（采集日距开营 5 天）并存 | negative | s1/s2/s3 | 交叉核对 | observed/negative |
| F-059 | 适用边界：s6 的风格清单是第三方开源项目自拟，非平台官方规则；同组知识包所记征文活动承诺书中的 AI 红线只适用该活动，不自动适用于日常投稿或本门课程 | scoped | s6 | 适用范围 | observed/scoped |
| F-060 | 适用边界：七步骨架各版本与六种开篇钩子均非本门课程官方文本；媒体观察、平台生态数据、学员晒单三者主体不同，不能互证课程效果 | scoped | s4/s5/s7 | 适用范围 | observed/scoped |

## 编号维护

新增事实从 F-061 起顺延，不重排既有编号。若后续取得课程正文、原始对账单、平台规则全文或目录后续章节，应各自新增编号并在[核验与勘误](verification.md)补裁决，不修改本表已有行的结论。
