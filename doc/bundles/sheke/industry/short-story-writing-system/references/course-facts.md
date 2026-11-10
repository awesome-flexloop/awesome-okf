---
type: Reference
title: "课程事实与主张登记（F-001～F-171）"
route: chaptered-summary
sources:
  - id: facts
    resource: "course-facts.md"
status: flagged
stale_after: 2026-12-07
generated: { by: "process:seven-concepts-cmd", at: "2026-11-07T02:52:45Z" }
---

# 课程事实与主张登记

F-001～F-171 共 **171 条**，是本包唯一 F 台账，其它页面只引用编号，不建立第二份。分层：F-001～F-012 详情页页面事实，F-013～F-024 售卖页页面事实，F-025～F-040 宣传长图单源主张，F-041～F-054 第三方公开旁证，F-055～F-060 首轮负向事实与适用边界；F-061～F-080 为 2026-11-09 上午播放页复核与开放平台检索；**F-081～F-115 为同日稍晚第三轮已购课会话新增**（会话与覆盖 14 条、课堂方法原创改写 16 条、分账与模式 5 条），；**F-116～F-139 为同日更晚第四轮全量录播补齐新增**（采集与覆盖 10 条、逐课走查原创改写 7 条、分账与模式 7 条），**F-140～F-155 为 11-10 第五轮证据范围复核新增**（接口与字段复核、载体取证、结论修正与目录时点漂移），**F-156～F-171 为 11-10 更晚第六轮新增两节正课内容级转写新增**（采集与目录、两课方法链原创改写、覆盖时点与结论），不改写既有行。

`page_fact` 只确认「页面字段／渲染文字写了什么」；`poster_claim` 只记录「宣传图怎么说」，单源、无样本、无对照；`third_party` 记录第三方主体怎么转述，不认证其真实性；`negative` 记录明确缺席；`scoped` 记录适用边界；**`lecture_derived` 记录课堂主线录播 ASR 派生稿的原创改写，只回答「课堂讲了什么」，不认证方法有效性、不作逐字引语**，引用体例见[课堂本体覆盖与证据分层](lecture-coverage.md)。逐项裁决见[核验与勘误](verification.md)。

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

| F-061 | 播放页 URL 为 `/xen/market/training/training-video/{productId}/{sectionId}`；给定 `sectionId=2098475336661055368` 对应「导学01：如何靠写短篇小说变现？」，免登录 GET 返回 200，HTML `title` 与该节标题一致 | page_fact | s8 | 播放页 HTML head | observed |
| F-062 | 播放页 SSR `<textarea id="resolved">` 的 `appContext.__connectedAutoFetch.trainingVideo.data` 含 8 个键：`rights`、`product`、`videoInfo`、`isUseNewProgressApi`、`bindDesktopInfo`、`noteCount`、`isShowAiEntry`、`extData` | page_fact | s8 | SSR JSON | observed |
| F-063 | `GET /api/education/training/{cid}/video_page/catalog?limit=50&include=0&order_by=global_idx` 免登录返回 40 条，`paging.totals=40`、`is_end=true`、`is_start=true` | page_fact | s8 | 目录接口 | observed |
| F-064 | 沿 `videoInfo.nextVideoHref` 连续取得 40 个播放页，逐节 `id`／`title`／`resource.data.duration` 与目录接口 40 条完全一致（0 处差异），`index.global` 0～39 连续、id 去重后 40 个，最后一节无 `nextVideoHref` | page_fact | s8 | 链式快照与接口对账 | observed |
| F-065 | 2026-11-09 复核详情页：`onlineSectionCount=40`、`presetSectionCount=40`、`fishedSectionCount=0`；`chapter` 增至 7 项，新增「第二章-选题大纲设计」且 `firstSectionIdx=7` | page_fact | s8 | `base.course`、`base.chapter` | observed |
| F-066 | 2026-11-09 复核售卖页：`catalog.paging.total=40`，`offset=0/20` 两页各 20 条按 `idx` 合并 0～39 连续，与播放页 40 条 `id`／`title` 逐条一致（0 处差异）；`extra.headerText` 仍为「已完结」 | page_fact | s8 | sku-detail SSR | observed |
| F-067 | 新增小节 global 7「第4课：如何构思你的故事？」，属「第二章-选题大纲设计」，`meta.media="录播 · 32:53"`、`duration=1973302` ms；11-07 的 39 节快照无此节与该章节 | page_fact | s8 | 目录接口 idx 7 | observed |
| F-068 | 40 节按 `section_type` 分为 `video` 37 节、`live_stream` 3 节；按 `chapter.title` 分为导学 3、开营 1、第一章 3、第二章 1、主题直播 1、答疑直播 1、赠课 30 | page_fact | s8 | 机械计数 | observed |
| F-069 | 40 节 `resource.data.duration` 合计 86605844 ms（24 小时 3 分 25.844 秒）；37 节录播合计 73461910 ms，3 节直播回放合计 13143934 ms | page_fact | s8 | 标准库求和 | observed |
| F-070 | 与短故事正课直接相关的录播为 7 节（导学 3 + 第一章 3 + 第二章 1），合计 11356281 ms（3 小时 9 分 16.281 秒），占 40 节的 17.5%；赠课 30 节占 75% | page_fact | s8 | 分类计数 | observed |
| F-071 | 40 节的权限与资源字段取值一致：`right.ownership=false`、`purchased=false`、`can_experience=false`、`is_free=false`、`trial_duration=0`、`playlist/playlist_v2=null`、`file_list=[]`、`can_download_section_file=false` | page_fact | s8 | 逐条字段分布 | observed/scoped |
| F-072 | `product.duration_text` 为「试看部分内容，观看完整内容请」，与 `trial_duration=0`、`can_experience=false` 并存；前者为模板文案，后两者为权限字段 | page_fact | s8 | `trainingVideo.data.product` | observed |
| F-073 | 3 节直播在播放页 `meta.media="直播课 · 回放"`、`section_status=3`、`resource.data.status` 缺省；37 节录播 `section_status=2`、`status="started"`；售卖页同一 3 节仍标「直播 · 已结束」 | page_fact | s8 | 播放页／售卖页字段 | observed |
| F-074 | `noteCount.data.total=0`；`GET /api/knowledge_school/courses/{cid}/sections/{sid}/notes` 返回空 `list`；`isShowAiEntry=false`、`bindDesktopInfo.show=false` | page_fact | s8 | 播放页与笔记接口 | observed |
| F-075 | `video_page/detail` 返回 `serial_status="end"`、`is_on_shelf=false` 与 `on_shelves=true` 并存、`duration=0`、`section_unit="节"`、`authors` 仅 1 个机构账号；`create_time=1792777712` 按 +08:00 换算为 2026-10-24 01:48:32 | page_fact | s8 | 详情接口 | observed |
| F-076 | 11-07 的 39 节／6 章节快照与 11-09 的 40 节／7 章节快照是同一组字段在两个时点的取值，不是页面之间的口径矛盾；按幂等规则并存登记，不改写 F-004、F-006、F-018 等既有行 | negative | s1/s2/s8 | 两轮快照比对 | observed/negative |
| F-077 | 适用边界：`resource.data.status="started"` 是资源状态、`serial_status="end"` 是连载状态、`catalog.extra.headerText="已完结"` 是目录展示文案、`update_finished=true` 是课程级更新标志；四者对象不同，不能合并成「课程已结束且全部可看」 | scoped | s8 | 字段语义 | observed/scoped |
| F-078 | 2026-11-09 复核后仍未取得任何一节视频画面（4 张小节封面帧除外）、音轨、字幕、讲义、作业正文、批改记录或课堂原始表格；F-055 的缺席结论在本轮仍成立 | negative | s8 | 采集边界 | observed/negative |
| F-079 | 开放平台公开检索命中的结果以推广／引流文案为主，反复出现「七步故事法」「8G 素材包」「内部绿通」「导语」「付费节点」等说法，未出现课程正文、讲义或逐字转录 | third_party | s9 | 两次检索各 10 条 | single-source/scoped |
| F-080 | 取回 4 张小节封面：有的为标题卡（含机构标识与小节标题），有的为视频内帧（含三行要点文字与一句字幕）；单帧不构成课程内容，本包不逐字转录、不用其推断课堂步骤 | negative | s8 | 图片读图 | observed/negative |
| F-081 | 2026-11-09 第三轮以已购课浏览器会话复核：`video_page/detail` 的 `right` 为 `ownership=true`、`purchased=true`、`can_experience=false`；与 11-09 上午免登录会话的同字段全 false 并存，属不同会话时点而非页面口径冲突 | page_fact | s10 | 已购课会话详情接口 | observed |
| F-082 | 登录态课程级 `product.course.ownership=true`、`section_count=40`、`updated_section_count=40`、`update_finished=true`；40 节目录每行 `right` 均为已购 | page_fact | s10 | 登录态 SSR 与目录接口 | observed |
| F-083 | 登录态目录 40 节每行 `resource.data.playlist` 含四档 mp4（FHD 1080p／HD 720p／LD／SD 476p）；主线 7 节与直播回放 3 节含 FHD，搭售赠课 30 节仅 HD／LD／SD | page_fact | s10 | 目录接口字段分布 | observed |
| F-084 | 登录态 40 节 `file_list` 全空、`playlist_v2` 全 null；`can_download_section_file` 40 节全 true 但无任何实际附件，模板权限不等于有课件 | page_fact | s10 | 目录接口逐条统计 | observed/scoped |
| F-085 | 登录态 40 节均带 `learning_record`：6 节 `is_finished=true`、34 节 false，部分进度接近 1；这是账号学习记录，不是课程或内容属性 | page_fact | s10 | 目录接口字段分布 | observed/scoped |
| F-086 | 播放器前端 JS 中 `caption`／`subtitle` 的命中均为表单字段与版式类名，无字幕接口；登录态目录亦无字幕资源字段，课程未提供官方字幕 | negative | s10 | 前端脚本与目录字段 | observed/negative |
| F-087 | 登录态 `note_catalog` 与 `notes` 接口仍返回空 `list`；课堂笔记正文未取得 | negative | s10 | 笔记接口 | observed/negative |
| F-088 | 登录态 40 节时长合计 24.06 小时，与 F-069／F-070 的免登录统计一致；主线录播 7 节约 3.2 h、直播回放 3 节约 3.6 h、搭售赠课 30 节约 17.2 h | page_fact | s10 | 分类计数复核 | observed |
| F-089 | 本轮下载前 10 节最小清晰度 mp4 共 535.6 MB，逐文件 `ftyp` 魔数与 SHA-256 记入私域取证清单；播放列表签名字串不写入任何文档 | page_fact | s10 | 原件取证 | observed |
| F-090 | 7 节主线录播经音频转写得到带时间戳派生文本；属 ASR 派生稿而非逐字稿，存在同音字、专名误识与断句漂移 | lecture_derived | s10 | 主线录播 7 节 | asr-derived |
| F-091 | 3 场直播回放原件已取得但本轮未做内容级转写，课堂问答与加餐内容仍为空白 | negative | s10 | 覆盖矩阵 | observed/negative |
| F-092 | 30 节搭售赠课属另一产品线，本轮仅登记元数据，未下载、未转写 | negative | s10 | 覆盖矩阵 | observed/negative |
| F-093 | 课件画面上的拆文表格、共鸣清单、提示词模板与截图文字未取得；本轮只取音轨，相关内容仅为口述转述，本包表格均为原创改述 | negative | s10 | 采集边界 | observed/negative |
| F-094 | ASR 派生稿未逐字落盘；原件留存私域取证目录可重转复核；引用体例固定为「课程主线录播 · ASR 派生 · 原创改写」，不得写成课程原文或讲义原表 | scoped | s10 | 引用体例 | observed/scoped |
| F-095 | 课堂把拆解分为「为什么拆／如何识别／如何拆」三段；识别途径归为四类观察面：分类榜单、互动数据与评论区、分类账号、站外流通内容；读完正文还要看评论区是识别与拆解的接点 | lecture_derived | s10 | 拆解录播 | asr-derived/rewritten |
| F-096 | 课堂列出四项动笔前可检查的要素：话题性素材、出人意料的设定、一句话可概括的主线、极短篇幅内立起悬念钩子的高密度开篇 | lecture_derived | s10 | 拆解录播 | asr-derived/rewritten |
| F-097 | 拆解两步为细读与提炼：细读按小节列概括、人物与关系、主要情节、情绪落点、高亮之处；提炼压成一句主线后追问目标、阻碍、对抗、成长、关系、悬念与伏笔；课堂自检是「一句话讲不清即主线没立住」 | lecture_derived | s10 | 拆解录播 | asr-derived/rewritten |
| F-098 | 课堂把素材来源归为三条路径：向自身经验要真实、向人群与社会观察要冲突、向既有故事模式要结构；并强调把消费内容改成加工内容 | lecture_derived | s10 | 素材录播 | asr-derived/rewritten |
| F-099 | 「写自己」三步：随手记录碎片不追求成篇、把一句情绪扩写成有场景与动作的画面、定期回看并问反复被哪类人物打动与反复在想什么；另有随手存取、每周回翻的灵感库做法 | lecture_derived | s10 | 素材录播 | asr-derived/rewritten |
| F-100 | 社会观察三问：发生在什么场景、人物各是什么处境、大众最共情的点在哪；课堂要求先追问各方动机而不急着站队，使素材从情绪沉淀成人物 | lecture_derived | s10 | 素材录播 | asr-derived/rewritten |
| F-101 | 课堂把故事模式定位为骨架与种子而非成品：既不把套路当原创之敌，也不当成功密码；建议从生活提炼模式、也带着既有模式回生活找人物细节，双向联动 | lecture_derived | s10 | 素材录播 | asr-derived/rewritten |
| F-102 | 课堂把常见类型归为情感向、脑洞向、真实向三大类，另列科幻与逻辑推理两个鼓励方向；前置限制是选自己读得进去、写得出来的那类，分类不用于判断成功率 | lecture_derived | s10 | 类型录播 | asr-derived/rewritten |
| F-103 | 求新位置按类型分：情感向换人设／职业／人物关系，脑洞向换内核视角／表现形式／剧情机制，真实向守真实性／稀缺性／获得感；并提示不熟悉的职业易出逻辑漏洞、真实向一味求刺激反而失去差异化 | lecture_derived | s10 | 类型录播 | asr-derived/rewritten |
| F-104 | 课堂区分灵感（只提供冲动与碎片）与构思（校准方向并组装成完整故事）；构思三步为向读者找共鸣、小范围做剪辑聚焦、选视角与人称，分别回答拿什么打动、从哪讲到哪、用谁的眼睛看 | lecture_derived | s10 | 新解锁的构思录播 | asr-derived/rewritten |
| F-105 | 共鸣筛选四问：有趣或有用、能否激起真实情绪、有无意外感或认同慰藉、读后能否带走思考支撑；课堂另区分轻微矛盾与威胁前途／生存／精神状态的强冲突，并保留自我表达与受众意识的平衡 | lecture_derived | s10 | 构思录播 | asr-derived/rewritten |
| F-106 | 剪辑师思维：压缩平淡日常、放大情感浓度最高的少数片段，铺垫与过渡都为一到两个名场面服务；两则稿件反面案例的共同病因是线索发散与素材堆砌，「爆点多不等于故事强」 | lecture_derived | s10 | 构思录播 | asr-derived/rewritten |
| F-107 | 视角问题压成「谁站在何处看到了什么」：三种人称各有适用场景，第一人称的叙述者不可与事件毫无关联；心理距离影响人物可信度，动笔前写人物小传，理解动机不等于替角色洗白、仍须守内容尺度 | lecture_derived | s10 | 构思录播 | asr-derived/rewritten |
| F-108 | 导学把工具定位为「帮你思考、不替你思考」，能力归为补资料／给反馈／发散脑洞三类；找选题分热点型与类型型两路径，共用「提问越具体、输出越有用，先要方向再迭代、不要一步成稿」的纪律；判断环节只输出分析与四项风险（钩子、延展潜力、反转新鲜度、结局），不改原文，决定权归创作者 | lecture_derived | s10 | AI 共创导学 | asr-derived/rewritten |
| F-109 | 改编导学按门槛、周期与成本把改编形态分层，并区分长链条（先磨本子后制作、按年计）与短形态（先立钩子让市场说话）两套工业逻辑；由制作侧反推写作：多一个角色多一份成本与记忆负担，同一爽点不反复拉扯 | lecture_derived | s10 | 改编导学 | asr-derived/rewritten |
| F-110 | 改编侧强调「先过内容合规、再逐条看合同」的顺序；渠道归为平台版权部门／制作方／赛事／中介四类，稿酬结构归为保底加分成／纯分成／买断／按集按字四种，各有各的账；署名权与后续改编权须落在纸面，中介先收费即风险 | lecture_derived | s10 | 改编导学 | asr-derived/rewritten |
| F-111 | 课堂中的市场规模、用户量、收益与稿酬数字、具体作品名、平台与工具产品名、讲师身份及题材协审清单，均不进入本包教程结论；平台当前口径须另查，静态清单会过期 | scoped | s10 | 去品牌化与适用边界 | observed/scoped |
| F-112 | 第三轮与首两轮构成两条独立证据通道：A 免登录公开面回答目录与字段口径，B 已购课会话回答课堂讲了什么；B 不给 A 的宣传承诺背书，A 不证明 B 的讲法有效，两者不得拼成因果链 | scoped | s8/s10 | 通道分账 | observed/scoped |
| F-113 | 教程第 07 篇「内容可读范围没有增加」是 11-09 上午免登录会话的时点真值；本轮并列登记另一会话时点，不改其结论、不覆盖旧快照 | scoped | s8/s10 | 时点分账 | observed/scoped |
| F-114 | 按幂等规则 F-001～F-080 与两份历史目录快照一字不改；第三轮新增事实占 F-081～F-115，全包共 115 条；后续补齐直播、赠课或课件画面仍另起编号 | scoped | s10 | 编号维护 | observed/scoped |
| F-115 | 模式补第 7 步「证据层级跃迁要分账」与第 7 条反模式；L1 成熟度不升级（通道增加不等于案例数增加）；第三轮四视角对抗审查 6 条全部采纳 | scoped | s10 | 模式与 V 门 | observed/scoped |


| F-116 | 用户要求「录播课全部转为 OKF wiki 教程内容」，命中第三轮登记的复核条件「直播或赠课完成内容级转写」；按幂等规则只新增编号，不改写既有行 | scoped | s11 | 触发 | observed/scoped |
| F-117 | 播放签名地址过期后由登录态目录接口重新签发，40 节元数据未变化；未重新登录、未导出或保存账号凭据 | session_fact | s11 | 签名刷新 | observed |
| F-118 | 40 节最小清晰度原件全部到位，合计 1736.8 MB / 24.06 小时；课程本体 10 节 535.6 MB / 6.81 h，搭售赠课 30 节 1201.2 MB / 17.25 h | session_fact | s11 | 取证清单 | observed |
| F-119 | 40 节逐文件校验 ftyp 魔数、字节数与 HTTP 200；全部通过，无失败与截断 | session_fact | s11 | 下载校验 | observed |
| F-120 | 逐文件 SHA-256 前缀、标题、章节、毫秒时长与清晰度记入私域取证清单；签名地址不写入任何文档 | session_fact | s11 | 取证清单 | observed/scoped |
| F-121 | 3 场直播回放（开营／主题／答疑，约 3.6 h）完成全量音频转写，产出带时间戳的 ASR 派生稿 | session_fact | s11 | ASR 覆盖 | observed/scoped |
| F-122 | 30 节搭售赠课（17.25 h）完成全量音频转写，产出带时间戳的 ASR 派生稿；逐字文本不入库 | session_fact | s11 | ASR 覆盖 | observed/scoped |
| F-123 | 7 节主线录播的 ASR 全文从会话上下文回取，作为逐课走查素材；逐字稿只在临时目录，不入库、不作逐字引语 | scoped | s10/s11 | 入库边界 | observed/scoped |
| F-124 | 全课内容级覆盖达到 40/40；覆盖口径按包分账读：本包课程本体 10/10、独立包赠课 30/30 | session_fact | s11 | 覆盖矩阵 | observed/scoped |
| F-125 | 本包课程本体 10 节（3 导学 + 4 正课 + 3 直播）全部有对应教程内容，内容级覆盖 10/10 | session_fact | s11 | 覆盖矩阵 | observed |
| F-126 | 30 节搭售赠课属另一产品线，主题为内容账号运营；按主题一致性原则独立成包，不并入本包凑节数 | scoped | s11 | 范围决策 | observed/scoped |
| F-127 | 两包共用一次已购课会话通道，但结论互不印证、不拼因果链；F 编号各自独立、互不通用 | scoped | s10/s11 | 双包分账 | observed/scoped |
| F-128 | 第四轮新增 3 篇按课次走查教程：导学三节、四节正课、三场直播；与第三轮按主题的三篇互补，不复述其结论 | lecture_derived | s11 | 第 11～13 篇 | asr-derived/rewritten |
| F-129 | 导学三节按「文体与变现认知 → AI 辅助从选题到成稿 → 影视化表达出口」递进，三节各自承担不同定位 | lecture_derived | s11 | 导学走查 | asr-derived/rewritten |
| F-130 | 四节正课按「拆爆款 → 找素材 → 辨类型 → 构思故事」推进；课堂当场给出检查动作与相邻课的依赖关系 | lecture_derived | s11 | 正课走查 | asr-derived/rewritten |
| F-131 | 三场直播功能分工：开营负责节奏与作业规则，主题直播负责延伸与任务，答疑直播负责集中处理卡点 | lecture_derived | s11 | 直播走查 | asr-derived/rewritten |
| F-132 | 作业按真实创作流程递进（灵感→人物大纲→开篇→正文），初稿阶段先求产出、只与学习前自身状态比较；课前要求建立读者→创作者→编辑三级视角与分类素材库 | lecture_derived | s11 | 开营直播 | asr-derived/rewritten |
| F-133 | 主题直播讲主线设计与避坑：先立一条能收束的主线，再检查线索发散与素材堆砌，避免把「爆点多」当成「故事强」 | lecture_derived | s11 | 主题直播 | asr-derived/rewritten |
| F-134 | 答疑直播讲短故事标准、内容红线与创作流程，反复出现的卡点集中在选题空泛、开篇不抓人与结尾不收束 | lecture_derived | s11 | 答疑直播 | asr-derived/rewritten |
| F-135 | 第四轮复核后，讲义、课件画面文字、官方字幕、作业与批改原件仍全部缺席；本包所有表格均为自拟，不是课堂原表 | negative | s11 | 负向事实 | observed |
| F-136 | 覆盖面扩大不等于证据等级提升，也不等于案例数增加；L1 模式成熟度不升级 | scoped | s11 | 模式 | observed/scoped |
| F-137 | 第四轮未引入新证据通道，只是把通道 B（已购课会话）的覆盖从 7 节补全到全课；A／B 双通道分账结论不变 | scoped | s10/s11 | 通道分账 | observed/scoped |
| F-138 | 第四轮四视角对抗审查 6 条全部采纳；四轮累计 8+6+6+6 共 26 条 | scoped | s11 | V 门 | observed/scoped |
| F-139 | 按幂等规则 F-001～F-115 与两份历史目录快照一字不改；第四轮占 F-116～F-139，全包 139 条；下一轮从 F-140 顺延 | scoped | s11 | 编号维护 | observed/scoped |
| F-140 | 11-10 登录态仍有效；课程级资料接口只返回版本标志、卡片接口只返回营销卡字段，均无讲义或资料清单 | session_fact | s12 | SKU 级资料复核 | observed |
| F-141 | 共学设置返回未启用、桌面实操未开放、笔记目录与本节笔记均为空列表；播放页标签只有课程详情／小节资料／目录／笔记，无作业、批改或字幕入口 | negative | s12 | 界面与能力枚举 | observed |
| F-142 | 播放器脚本真身只暴露一个由小节资料列表驱动的下载端点；全包枚举无字幕、作业与批改端点 | session_fact | s12 | 端点枚举 | observed |
| F-143 | 11-10 目录 42 节资料列表全为空；可下载标志为模板权限，界面文案为「本小节没有资料哦~」 | negative | s12 | 小节资料 | observed |
| F-144 | 11-09 归档的 40 个录播原件全部只有视频与音频 2 条流、0 条字幕轨；抽查 4 张全分辨率帧未见独立字幕条 | negative | s12 | 字幕载体 | observed |
| F-145 | 对 13 节各抽 3 个时点的联系表普遍可见课件页、对照表、标题卡与软件截图，中文可读文字存在；此前「课件画面文字缺席」是未抽帧而非平台不提供 | session_fact | s12 | 像素取证 | observed |
| F-146 | 一节正课画面为作业清单页，列四项按周递进的任务并标「必须完成」；作业要求作为课堂内容已可读取 | session_fact | s12 | 作业载体 | observed |
| F-147 | ASR 派生稿含作业布置：一节明确列三项课后练习并声明「不需要提交给老师、自己留存」，另有课后思考题与完成作业提醒；一对一批改建议属服务承诺 | lecture_derived | s12 | 作业口播 | asr-derived/rewritten |
| F-148 | 公开检索中的「编辑批改」「作业点评」属服务描述与同类课程常见话术，命中多为招生或无关课程，不能推定本课程已交付批改记录 | third_party | s12 | 公开口径 | unverified |
| F-149 | 11-10 登录态目录 include=0/1 同为 42 节、总数 42；较 11-09 快照新增第二章两节正课 | session_fact | s12 | 目录复核 | observed |
| F-150 | 新增两节合计 4,321,443 ms，与总时长 86,605,844 → 90,927,287 ms 的增量精确相等；34 节同名标题的资源标识变化但毫秒时长逐条相同，不据此推断内容替换 | session_fact | s12 | 时长对账 | observed |
| F-151 | 章节名改写；第 6 课的上架状态位与其余节不同 | session_fact | s12 | 章节口径 | observed |
| F-152 | 覆盖率须带时点：11-09 目录 40 节为 40/40；11-10 目录 42 节中新增两节未下载、未转写，不得再写「全课已覆盖」而无日期 | scoped | s12 | 覆盖时点 | observed/scoped |
| F-153 | 第五轮把「缺席」拆成四层：结构化附件（无）、视频像素（有、未逐字转录）、口播音轨（有、已入库）、服务承诺（有文案、无交付对象）；旧行不改写，只补裁决 | scoped | s12 | 结论修正 | observed/scoped |
| F-154 | 按路线恒为 chaptered-summary，不做课件文字的逐字 OCR、不整图重发；页内表格继续标注为自拟，L1 成熟度不升级 | scoped | s12 | 路线纪律 | observed/scoped |
| F-155 | 第五轮四视角对抗审查 5 条全部采纳；五轮累计 8+6+6+6+5 共 31 条；F-001～F-139 与两份历史快照一字不改，下一轮从 F-156 顺延 | scoped | s12 | V 门与编号 | observed/scoped |
| F-156 | 11-10 目录 42 节按标题与 11-09 的 40 节逐条比对：40 个旧标题全在，净新增「第5课：如何让你的角色深入人心？」「第6课：如何写出把握人心的黄金结构？」两节正课；登录态与免登录快照的资源标识整体重签，不据此推断内容替换 | session_fact | s13 | 目录对账 | observed |
| F-157 | 两节时长 2,097,900 ms 与 2,223,543 ms，合计 4,321,443 ms，与第五轮 F-150 登记的总时长增量精确相等 | session_fact | s13 | 时长对账 | observed |
| F-158 | 两节权限均为已购，播放列表四档 mp4，独立资料列表与字幕清单仍空；取最小档下载 100.1 MB，ftyp 魔数、字节数与 SHA-256 全部校验通过 | session_fact | s13 | 原件校验 | observed |
| F-159 | 两节原件容器均为视频与音频 2 条流、0 条字幕轨（MP4 box 机械解析），与第五轮 40 个原件口径一致；画面文字仍按路线不逐字转录 | negative | s13 | 字幕载体 | observed |
| F-160 | 两节音轨 ASR 派生稿各约 1.56 万／1.60 万字符，去品牌化要点笔记落在临时目录；逐字稿、签名地址与账号凭据不入库 | lecture_derived | s13 | 转写加工 | asr-derived/rewritten |
| F-161 | 人物课把「把扁平人物写成人」拆成原型→框架→加工→真实四步并规定先后，反例是写到一半才回头补设定；框架决定成立、加工决定被记住，属两道工序 | lecture_derived | s13 | 人物主路径 | asr-derived/rewritten |
| F-162 | 人物三维（外在／社会／心理）各自决定第一眼判断、所处位置与如何选择，判据是一切行为可回到三维解释；顺序为先定读者与题材再设三维，附读者匹配反例 | lecture_derived | s13 | 人物框架 | asr-derived/rewritten |
| F-163 | 个性化加工三方向（高亮特点须与故事连续、层次与矛盾须有来处、标志性动作求真实而非精彩）、反差与表象／真相对比、弧光目标—意外—结果三柱、真实感与代入目标读者的判据 | lecture_derived | s13 | 人物加工 | asr-derived/rewritten |
| F-164 | 配角只承担推动情节与塑造主角两类作用，短篇有数量上限且多一个配角多一份交代成本；人设取向分反套路（脱颖而出）与接地气（让人相信），后者归因于外部传播形态仅登记推理结构 | lecture_derived | s13 | 配角与取向 | asr-derived/rewritten |
| F-165 | 结构课把「故事平淡」先归因于结构而非文笔，自检是「这一段写完，下一段该往哪去」；单线叙事的适用判据来自短篇体量，两条理由分别是共情聚焦与对写作者的保护 | lecture_derived | s13 | 结构归因 | asr-derived/rewritten |
| F-166 | 单线内反转的五步序列（困境→主角亲自直面→两三次事件→目标交代→由主角自己挣来）与两条反例；统一判据是所有波动长在同一根主线上、方向统一 | lecture_derived | s13 | 单线反转 | asr-derived/rewritten |
| F-167 | 四段式起／成／转／和各自的当堂检查清单与反例：起须同时完成五项且不堆背景，成须每步往前走一步，转把行动权交回主角并放置最高能点，和须四项闭合且禁新开局／巧合外力 | lecture_derived | s13 | 四段式 | asr-derived/rewritten |
| F-168 | 一句话故事→四段式大纲→初稿的三步流程与「先小后大」原则；一句话四问自检，以及写完回头用这句话校准主线、回看大纲定位结构松动的动作 | lecture_derived | s13 | 动笔流程 | asr-derived/rewritten |
| F-169 | 覆盖率须带目录时点：11-09 目录 40/40（本体 10/10＋赠课 30/30）与 11-10 目录 42/42（本体 12/12＋赠课 30/30）并列为两个时点真值，互不推翻；新增两节不并入赠课包凑节数 | scoped | s13 | 覆盖时点 | observed/scoped |
| F-170 | 新增两节只以 ASR 派生的原创改写进入教程第 14／15 篇；与前序方法链的衔接仅据本节口述回指归纳，不追认具体课次、不替课程下体系完整或方法有效的结论；课中归给外部著作、行业共识与读者偏好的说法均登记为待核验主张 | scoped | s13 | 引用体例 | observed/scoped |
| F-171 | 第六轮四视角对抗审查 4 条全部采纳；六轮累计 8+6+6+6+5+4 共 35 条；F-001～F-155 与两份历史目录快照一字不改，下一轮从 F-172 顺延；L1 成熟度不升级 | scoped | s13 | V 门与编号 | observed/scoped |



## 编号维护

新增事实从 **F-172** 起顺延，不重排既有编号。2026-11-09 上午的第二轮复核占用 F-061～F-080（触发「课程目录继续解锁」），同日稍晚的第三轮占用 F-081～F-115（触发「取得课程正文」），全包现为 F-001～F-171 共 **171 条**。第三轮新增第五层 `lecture_derived`：F-095～F-110 是课堂主线录播 ASR 派生稿的原创改写，只回答「课堂讲了什么」，不认证有效性、不作逐字引语；引用体例与覆盖矩阵见[课堂本体覆盖与证据分层](lecture-coverage.md)。逐项裁决见[核验与勘误](verification.md)第三轮段。第四轮占用 F-116～F-139（触发「直播或赠课完成内容级转写」），全量覆盖与双包分账见[全量录播覆盖与双包分账](full-course-coverage.md)。第五轮占用 F-140～F-155（触发「课程目录继续解锁」与「课件画面文字载体取得」），四层可得性裁决见[证据范围复核与四层可得性](evidence-scope-audit.md)。第六轮占用 F-156～F-171（触发「新增两节正课完成内容级转写」），两课方法链与 42/42 时点口径见[全量录播覆盖与双包分账](full-course-coverage.md)第六轮注记。若后续取得官方讲义全文、字幕文件或批改记录，应各自新增编号并补裁决，不修改本表已有行的结论。
