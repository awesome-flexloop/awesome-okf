---
type: reference
title: "来源清单：文章本体与 8 条独立参考源"
description: "登记公众号文章本体的账号、归属信号与访问方式，以及作者文末列出的 8 条参考源的独立可达性与核验结果"
tags: [provenance, source-manifest, psychology, single-source, personal-growth]
status: draft
stale_after: 2027-12-31
generated:
  by: process:seven-concepts-blog-okf
  at: 2026-10-24T02:38:32Z
sources:
  - id: src-001
    resource: https://mp.weixin.qq.com/s/4QDIGjD4gqRijiZY303Yzg
    title: "数据与逻辑（公众号「数据与逻辑」）：心理学能解释什么，又能改变什么？——从武志红、俞敏洪、周文强到彭凯平，浅谈心理学的归因偏差、目的偏差与实践价值"
---

# 来源清单

## src-001 — 文章本体

| 字段 | 内容 |
|---|---|
| 来源 ID | src-001 |
| URL | `https://mp.weixin.qq.com/s/4QDIGjD4gqRijiZY303Yzg` |
| 页面标题 | 心理学能解释什么，又能改变什么？——从武志红、俞敏洪、周文强到彭凯平，浅谈心理学的归因偏差、目的偏差与实践价值 |
| 页面显示账号 | 数据与逻辑 |
| 账号标识 | `user_name: gh_c0c45475466b`；`biz: MzIxNDE0MzA0MA==` |
| 作者署名 | 页面 `meta author` 为「永辉」；页面标注「原创」 |
| 页面显示日期 | 2026-10-24（`ct` = 1792809512，对应 UTC 2026-10-24 02:38:32 / CST 10:38:32） |
| 篇幅结构 | 引子 + 五节正文（一至五）+ 「主要参考资料」8 条 |
| 发现渠道 | 用户在会话中直接提供 URL（指定「全面学习」并要求生成 OKF wiki 教程） |
| 访问时间 | 2026-10-24 |
| 可访问性 | 常规请求直接返回完整正文，**无登录墙、无邀请码、无验证码、无付费门槛**；页面公开性门禁通过 |
| 采集方式 | HTTP 直取页面 HTML → 自建正文抽取（定位 `id="js_content"` 后逐块转换）→ 正文 131 段 / 约 6,357 字 |
| 归属信号 | 页面自载账号名、作者署名、原创标记；页面自身未声明与任何机构的商业关系 |
| 商业转化信号 | **无**。全文未出现课程、社群、付费、购买、报名等引导；文末仅列参考来源 |
| 采集状态 | collected（完整） |
| 保存范围 | 仅保存元信息、章节骨架与本 bundle 的原创改写；**未保存原文全文，未保存 raw HTML** |

### 停止规则与限制

- 采集在取得完整正文后即停止，不遍历该账号其他文章——本 bundle 的范围严格限定为用户指定的这一篇。
- 原始 HTML 与抽取脚本仅作采集中间件留存于系统临时目录，未进入 bundle、未入库。
- 文中涉及的四个公众人物（武志红、李雪、俞敏洪、周文强、彭凯平）均属**公开人物**，本 bundle 只转述其公开言论与公开报道中的可核验部分，不处理任何私人信息。
- 页面随时可能被作者删除或修改；`stale_after: 2027-12-31` 届时须复查页面是否仍可访问、作者表述是否发生变化。

## src-002 ~ src-009 — 作者文末列出的独立参考源

这 8 条**不是**本 bundle 的内容来源，而是作者用来支撑论证的外部证据。本 bundle 的独立核验正是逐条回到这些来源，检查作者引用是否忠实、量化声明是否成立。

| 来源 ID | URL | 页面标题 | 独立可达性（2026-10-24 核验） | 核验结论 |
|---|---|---|---|---|
| src-002 | `https://feng.ifeng.com/c/8xQovt0YhWU` | 知名心理学博主武志红与前女友李雪用「NPD」等术语公开发文互呛，双方就旧情与经济问题各执一词；武志红删文后，李雪：我也到此为止 | HTTP 200，正文可达 | `[VERIFIED]` 争执事件、NPD 术语使用、删文与「我也到此为止」均可核；页面标注 2026-10-22 |
| src-003 | `https://m.thepaper.cn/newsDetail_forward_15403467` | 专访武志红：孩子最核心的竞争力就是人格 | HTTP 200，正文可达 | `[VERIFIED]` 「原生家庭就是一个人最大的命运」为**逐字原文**；页面 `datePublished` = 2021-11-16 |
| src-004 | `https://finance.sina.com.cn/tech/roll/2024-08-06/doc-inchsmtm7003937.shtml` | 俞敏洪20年好友斥罗永浩五宗罪：忘恩负义人品极差 | HTTP 200，正文可达 | `[VERIFIED-PARTIAL]` 「张翔」「五宗罪」「铁公鸡」均命中；页面日期 2024-08-06 |
| src-005 | `https://www.who.int/news-room/fact-sheets/detail/mental-health-strengthening-our-response` | Mental health | HTTP 200，标题可达 | `[VERIFIED-EXISTENCE]` 页面存在、标题为「Mental health」、页面显示 11 September 2026；正文由脚本渲染，静态抓取未取到量表正文 |
| src-006 | `https://www.ccs.tsinghua.edu.cn/info/1107/1247.htm` | 2025年幸福感研究学术研讨会于清华大学召开 | HTTP 200，正文可达 | `[VERIFIED]` 会议时间 2025-09-23、页面发布时间 2025-09-25；「彭凯平正式发布了《2025年中国人幸福感报告》」为页面原文；运动/正念/社区联结/自我突破四方向命中 |
| src-007 | `https://www.oecd.org/en/publications/oecd-guidelines-on-measuring-subjective-well-being-2025-update_9203632a-en.html` | OECD Guidelines on Measuring Subjective Well-being (2025 Update) | 出版页 HTTP 403（站点反爬）；经 OECD iLibrary 全文页与出版目录独立确认 | `[VERIFIED-EXISTENCE]` 出版物真实存在，标注日期 3 October 2025、95 页，为第二版（2025 update） |
| src-008 | `https://www.nature.com/articles/s41562-025-02369-1` | A systematic review and network meta-analysis of randomized controlled trials of well-being-focused interventions | HTTP 200，正文可达 | `[VERIFIED]` 标题逐字一致；`datePublished` = 2026-01-02；「183 trials (n = 22,811)」逐字命中 |
| src-009 | `https://www.apa.org/practice/guidelines/evidence-based-statement.html` | Policy statement on evidence-based practice in psychology | HTTP 200，正文由脚本渲染，静态抓取未取到正文 | `[VERIFIED-EXISTENCE]` 页面与政策声明标题存在；声明内容经检索快照确认 |

### 核验方式说明

- src-002/003/004/006/008 通过 HTTP 直取并做**关键词上下文取证**（命中的原句片段随[核验报告](verification.md)登记）。
- src-007/009 的主域页面分别返回 403 与脚本渲染静态空白，改用其官方镜像（OECD iLibrary）与独立检索快照确认存在性与标题；src-005 同样为脚本渲染。
- **未使用搜索引擎摘要作为唯一证据**：凡主域可达的来源，一律以页面正文取证为准；仅当主域不可达时才降级为「存在性核验」，并在[核验报告](verification.md)中明确标注证据强度差异。
- 所有 8 条均**无需登录或特殊权限**即可获取，符合公开性门禁。
