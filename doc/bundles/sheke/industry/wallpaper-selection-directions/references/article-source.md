---
type: Reference
title: "文章事实与作者主张登记"
sources:
  - id: article
    resource: "https://mp.weixin.qq.com/s/Tql__N-ywlCbhDtjQ3kcqA"
  - id: wef-cn
    resource: "https://cn.weforum.org/agenda/2018/07/bb583d2f-3bd3-4607-8617-ac138ef196e2/"
  - id: gov-ai-plan
    resource: "https://www.gov.cn/zhengce/content/2017-07/20/content_5211996.htm"
  - id: cac-label
    resource: "https://www.cac.gov.cn/2025-03/14/c_1743654684782215.htm"
  - id: cac-interpretation
    resource: "https://www.cac.gov.cn/2025-09/05/c_1758792061408012.htm"
  - id: 36kr-report
    resource: "https://36kr.com/p/3637927130402176"
status: flagged
stale_after: 2026-12-31
generated: { by: "process:seven-concepts-cmd", at: "2026-11-01T10:55:52Z" }
---

# 文章事实与作者主张登记

F-001～F-025 记录页面信息或作者主张，F-026～F-032 记录补充核验与第三方报道。`page_fact` 只确认页面写了什么，不认证平台规则或商业效果；`author_claim` 保留作者归属；`verification_fact` 来自所列官方文本或机构页面；`third_party_claim` 是媒体报道中的他人陈述，不升级为平台口径。逐项裁决见[核验与勘误](verification.md)。

| F | claim | type | source_id | locator | status |
|---|---|---|---|---|---|
| F-001 | 页面标题为《D5午间分享》 | page_fact | article | activity-name | observed |
| F-002 | 页面显示账号“特级班班资料小屋”，署名“金娜” | page_fact | article | js_name / js_author_name | observed |
| F-003 | 页面 ct 值为 1793465755，对应 2026-11-01 00:55（Asia/Shanghai） | page_fact | article | var ct | observed |
| F-004 | 正文共 19 个段落、约 680 字符，未使用小标题分段 | page_fact | article | #js_content | observed |
| F-005 | 正文称学员已学会“推图社壁纸仓库上传的步骤”，把该步骤指向前期课程 | page_fact | article | 第 2 段 | observed |
| F-006 | 正文列出 9 条编号壁纸主题，编号自 1 至 9 | page_fact | article | 类别清单 | observed |
| F-007 | 正文称这些类别既可能用于手机壁纸，也可能用于电脑壁纸 | page_fact | article | 清单引导句 | observed |
| F-008 | 正文含 2 个视频播放器（mpvideo 内嵌页），图片元素为 0 | page_fact | article | #js_content DOM | observed |
| F-009 | 正文末尾提醒只读以上内容、不要点下方广告 | page_fact | article | 末段 | observed |
| F-010 | 正文不含单价、收入、分成比例、上传步骤、平台规则或收益数据 | page_fact | article | 全文 | observed/negative |
| F-011 | 作者称壁纸偏好因人而异，人们通常倾向选择能反映个性、兴趣或情绪的图片 | author_claim | article | 方法立场句 | single-source |
| F-012 | 作者把自然风景列为首类，称其“非常受欢迎”，并解释为离开都市喧嚣的体验 | author_claim | article | 类别 1 | single-source |
| F-013 | 作者列出城市风光，举例现代感都市与夜景，提到纽约天际线与东京街头 | author_claim | article | 类别 2 | single-source |
| F-014 | 作者列出艺术和抽象，举例抽象图形、色彩设计与现代艺术作品 | author_claim | article | 类别 3 | single-source |
| F-015 | 作者列出名人和电影，举例电影海报、名人肖像与剧照 | author_claim | article | 类别 4 | single-source |
| F-016 | 作者列出动物和宠物，举例猫、狗与野生动物，并称常带来温馨感觉 | author_claim | article | 类别 5 | single-source |
| F-017 | 作者列出动漫和游戏，并称其在年轻人中非常流行 | author_claim | article | 类别 6 | single-source/flagged |
| F-018 | 作者列出励志和引用，称这类壁纸可提供动力、帮助保持积极心态 | author_claim | article | 类别 7 | single-source |
| F-019 | 作者列出科技和未来主义，称其吸引了不少科技爱好者 | author_claim | article | 类别 8 | single-source |
| F-020 | 作者列出季节和节日，称人们会按季节与节日更换壁纸 | author_claim | article | 类别 9 | single-source |
| F-021 | 作者称这些类别提供了广泛选择，每个人都能找到符合自己偏好的壁纸 | author_claim | article | 清单小结 | single-source/flagged |
| F-022 | 作者称该清单是“创作壁纸的思路”，供读者借鉴 | author_claim | article | 清单之后 | single-source |
| F-023 | 作者称人工智能的创新与普及“被称为第四次科技革命” | author_claim | article | 视频引导前 | single-source/flagged |
| F-024 | 作者请读者看完上方视频，称会有“全新的看法和感悟” | author_claim | article | 视频引导 | single-source |
| F-025 | 正文未说明视频来源、制作方或与课程的从属关系 | page_fact | article | 视频区域 | observed/negative |
| F-026 | “第四次工业革命”（The Fourth Industrial Revolution）是克劳斯·施瓦布在《第四次工业革命》一书中的框架；世界经济论坛中文页 2018-07-01 引其论述，并称“工业4.0”概念最初在汉诺威工业展提出 | verification_fact | wef-cn | 正文首段与引文 | observed |
| F-027 | 国务院《新一代人工智能发展规划》（国发〔2017〕35 号，2017-07-08 成文、2017-07-20 发布）称人工智能是“新一轮产业变革的核心驱动力” | verification_fact | gov-ai-plan | 一、战略态势 | observed |
| F-028 | 《人工智能生成合成内容标识办法》（国信办通字〔2025〕2 号）由四部门联合发布，2025-03-07 成文、2025-09-01 施行；第十条要求用户发布生成合成内容时主动声明并使用标识功能 | verification_fact | cac-label | 通知与办法正文 | observed |
| F-029 | 配套强制性国家标准《网络安全技术 人工智能生成合成内容标识方法》（GB 45438-2025）与《标识办法》同日施行 | verification_fact | cac-interpretation | 首段 | observed |
| F-030 | 第三方报道称“推图社”是“一个开放壁纸等图片的小程序”，并记录受访者单条作品收益约 0.1～2 元 | third_party_claim | 36kr-report | 正文第 1 节 | observed/quoted |
| F-031 | 同一报道记录另一家 AI 培训机构的学费与退费争议个案，报道对象不涉本账号 | third_party_claim | 36kr-report | 正文第 1 节 | observed/quoted |
| F-032 | 页面未提供平台官方条款、投稿协议或收益规则的链接 | page_fact | article | 全文 | observed/negative |

## 编号维护

新增事实从 F-033 起顺延，不重排既有编号。若后续获得视频转录稿或平台官方规则，应各自新增编号并在[核验与勘误](verification.md)补裁决，不修改本表已有行的结论。
