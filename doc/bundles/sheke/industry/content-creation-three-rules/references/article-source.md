---
type: Reference
title: "文章事实与作者主张登记"
route: chaptered-summary
sources:
  - id: article
    resource: "https://mp.weixin.qq.com/s/HxlYpCNu0Kgb-mlm3qHdhQ"
  - id: finder-originality
    resource: "https://weixin.qq.com/cgi-bin/readtemplate?t=finder_appeal"
status: flagged
stale_after: 2026-12-31
generated: { by: "process:seven-concepts-cmd", at: "2026-11-06T06:00:47Z" }
---

# 文章事实与作者主张登记

F-001～F-012 是页面事实，F-013～F-030 是作者主张，F-031～F-037 来自平台官方条款原文，F-038～F-040 是负向事实与适用边界，总计 **40 条**。本表是本包唯一 F 台账，其它页面只引用编号，不建立第二份。

`page_fact` 只确认「页面写了什么」，不认证方法有效性；`author_claim` 只记录「作者怎么说」，单源、无样本、无对照；`verification_fact` 来自所列官方条款原文，且只在其适用范围内成立；`negative` 记录明确缺席的内容；`scoped` 记录适用边界。逐项裁决见[核验与勘误](verification.md)。

| F | claim | type | source_id | locator | status |
|---|---|---|---|---|---|
| F-001 | 页面 HTML `title` 标签抓取返回「微信公众平台」 | page_fact | article | HTML title | observed |
| F-002 | 正文首行标题为「课后深度讲解，干货复盘」 | page_fact | article | 正文首行 | observed |
| F-003 | 页面显示账号「特级班班资料小屋」、署名「金娜」 | page_fact | article | 页面署名区 | observed |
| F-004 | 页面显示发布时间 2026-11-05 19:17，并标注「北京」 | page_fact | article | 发布时间区 | observed |
| F-005 | 源 URL 为 `https://mp.weixin.qq.com/s/HxlYpCNu0Kgb-mlm3qHdhQ`，带 `scene=1` 与 `click_id` 追踪参数，无访问控制参数 | page_fact | article | 请求 URL | observed |
| F-006 | 采集日为 2026-11-06，采集通道为网页文本提取；未取得原始 HTML DOM，未核读图片与视频元素 | page_fact | article | 采集记录 | observed/scoped |
| F-007 | 正文以三个 ✅ 编号小标题组织：一、会模仿；二、只做「利他」内容；三、不内耗自己 | page_fact | article | 全文结构 | observed |
| F-008 | 第一节含 2 个编号子项，第三节含 4 条指标映射，第二节无编号子项 | page_fact | article | 全文结构 | observed |
| F-009 | 正文出现 7 处举例：备考不自律、化妆卡粉、30 天马甲线、10 分钟体态、00 后整顿职场、四六级 2 周、摆烂天赋 | page_fact | article | 第一、二节 | observed |
| F-010 | 第三节给出 4 组「指标 → 优化项」映射，指标为点击率、赞藏数、互动率、转粉率 | page_fact | article | 第三节 | observed |
| F-011 | 正文含课程运营安排：次日 15:00 加餐直播、21 天进阶课程、图片／文章板块之后进入视频板块 | page_fact | article | 首尾段 | observed |
| F-012 | 正文出现两类人物指代（授课者与班主任），原文以空格分隔书写 | page_fact | article | 首尾段 | observed |
| F-013 | 作者称新手一条内容打磨好几天仍不火，成熟自媒体人起号前期直接找爆款 | author_claim | article | 第一节 1 | single-source |
| F-014 | 作者称「抄封面、抄标题，但是抄≠抄袭」 | author_claim | article | 第一节 1 | single-source/flagged |
| F-015 | 作者称可模仿爆款标题的万能公式，以及封面的排版、文案和风格 | author_claim | article | 第一节 1 | single-source |
| F-016 | 作者称前期要保持更新频率，不要怕产出垃圾，先完成才能完美 | author_claim | article | 第一节 1 | single-source |
| F-017 | 作者称模仿内容要从用户角度出发，思考用户想看什么 | author_claim | article | 第一节 2 | single-source |
| F-018 | 作者给出的需求类型①：替用户解决当下棘手的问题 | author_claim | article | 第一节 2 ① | single-source |
| F-019 | 作者给出的需求类型②：满足不是必要但也很想要的需求 | author_claim | article | 第一节 2 ② | single-source |
| F-020 | 作者给出的需求类型③：拿捏被满足了就会感到很爽的需求 | author_claim | article | 第一节 2 ③ | single-source |
| F-021 | 作者把「利他」定义为对用户有实用价值或情绪价值，要么解决问题，要么引起情绪共鸣 | author_claim | article | 第二节 | single-source |
| F-022 | 作者称掌握实用与情绪两点，内容才更容易爆 | author_claim | article | 第二节 | single-source/flagged |
| F-023 | 作者称「自嗨」内容不讨用户喜欢，因为没有考虑选题痛点、封面标题吸引力、是否替用户解决问题 | author_claim | article | 第二节 | single-source |
| F-024 | 作者用「不要你觉得怎么样怎么样」概括自嗨的反面 | author_claim | article | 第二节 | single-source |
| F-025 | 作者称新手易因数据起伏焦虑内耗，聪明人只做复盘、反思、优化，从数据上找问题 | author_claim | article | 第三节 | single-source |
| F-026 | 作者称点击率低时重点优化选题、标题和封面 | author_claim | article | 第三节 | single-source |
| F-027 | 作者称赞藏数少是内容干货不够、价值点不够 | author_claim | article | 第三节 | single-source |
| F-028 | 作者称互动率低是正文互动不够、没有可互动的点 | author_claim | article | 第三节 | single-source |
| F-029 | 作者称转粉率低是缺乏人设，重点优化主页风格 | author_claim | article | 第三节 | single-source |
| F-030 | 首尾含效果与价值承诺：「含金量很高」「错过损失 1 个亿」「近些年最正确的选择」「战胜整个行业至少 70% 以上的创作者」 | author_claim | article | 首尾段 | single-source/flagged |
| F-031 | 《微信视频号原创声明功能使用条款》1.6 定义「作品」为依《中华人民共和国著作权法》受保护且具有独创性的智力成果 | verification_fact | finder-originality | 1.6 | observed |
| F-032 | 条款 4.3.2 要求作品由本人创作且本人享有发表权，或获原权利人合法、有效、完整的授权 | verification_fact | finder-originality | 4.3.2 | observed |
| F-033 | 条款 4.3.6(1)：抄袭或剽窃的作品，或构成元素（配音、音乐、图片等）未获合法授权致权属争议的内容，不得原创声明 | verification_fact | finder-originality | 4.3.6(1) | observed |
| F-034 | 条款 4.3.6(2)：成果本身不是作品或不受著作权法保护的列举（法律法规、时事新闻、历法、通用数表等），附「讲解或解读目的制作的作品除外」但书 | verification_fact | finder-originality | 4.3.6(2) | observed |
| F-035 | 条款 4.3.6(3)：未经授权不合理引用或大篇幅整合网络信息、公共信息、报刊杂志、他人创作（书摘、文摘、报摘、视频汇编）不得原创声明 | verification_fact | finder-originality | 4.3.6(3) | observed |
| F-036 | 条款 4.3.6(4)：营销性质的内容，即主要目的为推广、宣传和销售的内容，不得原创声明 | verification_fact | finder-originality | 4.3.6(4) | observed |
| F-037 | 条款 4.3.4 与 5.2.1：平台不对声明后的传播量、关注量、点赞量作任何承诺；原创声明能力的授予不代表平台对作品合法性的认可或担保 | verification_fact | finder-originality | 4.3.4 / 5.2.1 | observed |
| F-038 | 正文不含平台官方规则链接、统计数据来源、案例样本量或效果数据 | negative | article | 全文 | observed/negative |
| F-039 | 正文不含课程价格、退款条款、合同文本，也未指明方法适用的平台名称 | negative | article | 全文 | observed/negative |
| F-040 | 所引条款属微信视频号原创声明功能，不自动适用于源文未指明的平台；本包只用它说明「模仿边界须按目标平台规则查」 | scoped | finder-originality | 条款适用范围 | observed/scoped |

## 编号维护

新增事实从 F-041 起顺延，不重排既有编号。若后续取得著作权法官方全文、原始 HTML DOM 或目标平台规则页，应各自新增编号并在[核验与勘误](verification.md)补裁决，不修改本表已有行的结论。
