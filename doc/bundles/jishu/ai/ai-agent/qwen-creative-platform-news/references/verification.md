---
type: Reference
title: 核验报告
description: 2026-08-28对博文8项关键声明的核验结论——5项通过3项需更正/标注（Wan版本号/Arena排名时效性/小云雀表述简化），含权威来源URL与勘误详解
tags: [核验报告, 信源核验, 财联社, 阿里云, Arena.ai, 广电总局, 中文在线, ManClaw]
generated: { by: "blog-article-to-okf-bundle", at: "2026-08-28T23:30:00+08:00" }
status: stable
stale_after: 2026-10-31
sources:
  - id: wechat-article-luodao
    resource: https://mp.weixin.qq.com/s/7QNQ3_CpIya3MR45Twq07g
    title: 《阿里做了个AI短剧团队，不是工具》（罗导聊Ai，2026-08-27）
  - id: cls-exclusive-2465003
    resource: https://www.cls.cn/detail/2465003
    title: 财联社/科创板日报：千问创作平台多Agent协同（2026-08-26）
---

# 核验报告

**核验日期**：2026-08-28（轻量核验）

**总结论**：8 项声明经 WebSearch 核验，**5 项通过，3 项发现需更正或标注**。产品发布事件本身（F-003~F-007）可信度高，经财联社/科创板日报独家+多媒体交叉验证；3 项问题分别是 Wan 上一代版本号错误（F-039）、Arena 排名时效性（F-038）、小云雀表述简化（F-036），均不影响核心论点但引用时须以本报告口径为准。

---

## 八项核验结论总表

| 序号 | 核验对象 | 结论 | 权威来源 | 差异说明 |
|------|---------|------|---------|---------|
| 1 | F-003~F-007 千问多Agent协同 | ✅ 通过 | [财联社/科创板日报](https://www.cls.cn/detail/2465003) + DoNews + 网经社 + 观点网 | 8月26日小范围测试，5环节完全吻合 |
| 2 | F-008~F-014 Wan 3.0规格 | ⚠️ 部分有误 | [阿里云官方API文档](https://help.aliyun.com/zh/model-studio/wan3-video-generation-api-reference) + [阿里云国际博客](https://www.alibabacloud.com/blog/wan3-0-at-general-availability_603505) | 上一代版本号应为Wan 2.7非2.5（F-039）；其余规格全部通过 |
| 3 | F-015~F-017 Qwen-Image 3.0 Pro | ⚠️ 部分有误 | [Arena.ai榜单](https://arena.ai/leaderboard/text-to-image) + 88设计 | 模型与4500 token属实；"中文第一"未限定品类和时点，综合榜已被字节超越（F-038） |
| 4 | F-018~F-024 ManClaw | ✅ 通过（附注意） | [什么值得买](https://post.m.smzdm.com/p/aww5ozvp/) + [manclaw.art](https://manclaw.art/) + 潮新闻 | 产品能力全部验证；注意搭载字节Seedance 2.0非阿里Wan（F-035） |
| 5 | F-025 书旗5万IP | ✅ 通过 | [金羊网/羊城晚报](http://news.ycwb.com/ikimvkctio/content_54276944.htm) + 潮新闻 | "超过五万部"交叉确认 |
| 6 | F-026 阿里云AI收入12季度增长 | ✅ 通过 | [阿里巴巴集团官网财报](https://home.alibabagroup.com/document-2027233133950140416) + 新浪财经 | Q1收入123.76亿，ARR 495亿，吴泳铭原话确认 |
| 7 | F-028/F-029 竞争对手数据 | ⚠️ 部分有误 | 上证报 + 腾讯新闻/极客电影 + DoNews | 中文在线1200部✅；小云雀表述简化（F-036） |
| 8 | F-030 微短剧管理办法 | ✅ 通过 | [国家广电总局](http://www.nrta.gov.cn/art/2026/7/31/art_113_73785.html) + 法治日报 | 9月1日施行确认；补充AI投资阈值（F-037） |

---

## 勘误详解

### 勘误 1：Wan 上一代版本号（F-039）

博文 F-009 称"Wan 2.5 只能 15 秒"。核验发现上一代版本号应为 **Wan 2.7**：

- 阿里云国际站博客原文："Wan2.7's window ran from 2 to 15 seconds"
- Wan 系列版本迭代路径：2.1→2.5→2.6→2.7→3.0
- 15 秒时长对应的是 Wan 2.7 而非 Wan 2.5

**已通过的 Wan 3.0 规格**：

| 规格项 | 博文说法 | 核验结果 |
|--------|---------|---------|
| 输出时长 | 30秒 | ✅ 最长30秒，30fps |
| 混合输入 | 10图+5视频+5音频 | ✅ 官方API：reference_image≤10, reference_video≤5, reference_audio≤5 |
| 文档输入 | PDF/网页/PPT | ✅ 支持doc/xls/ppt/pdf/txt/md等+网页链接 |
| 双版本 | Standard/Prime | ✅ wan3.0-video（标准版）和wan3.0-video-prime（高速版） |
| 7折优惠 | Standard打七折 | ✅ 8月24日-9月23日限时，折后0.21/0.42/0.84元/秒 |

### 勘误 2：Arena.ai 排名时效性（F-038）

博文 F-017 称 Qwen-Image 3.0 Pro"在 Arena.ai 中文模型排名第一"。核验发现：

| 时点 | 排名 | 说明 |
|------|------|------|
| 8月5日（上线初期） | 全球第5、中国第1（1263分） | 88设计等媒体报道 |
| 8月10日（综合榜） | 全球第9（1257分），被字节seedream-5.0-pro（第8，1258分）超越 | Arena.ai官方榜单 |
| 8月25日（商业设计分类） | 分类第1（1258分） | 细分品类仍第一 |

博文未限定品类和时点，易使读者误认为综合排名第一。引用时应表述为"上线初期位列中国模型第一"或"商业设计分类第一"。

### 勘误 3：小云雀表述简化（F-036）

博文 F-029 称字节"小云雀"是《被裁掉的女孩》幕后工具。核验发现：

- **第二季**确实使用小云雀 Seedance 2.5 制作，并入选"小云雀创作者计划"
- **第一季**制作工具更为多元，演语科技 LibTV 也参与其中（资产管理和人脸辅助功能）
- 小云雀是剪映团队 2025 年 6 月推出的 AI 创作工具，Seedance 是其底层视频模型

准确说法应为"该剧第二季使用小云雀作为主要生成工具"，而非全剧唯一工具。

---

## 已通过项简要说明

- **第 1 项**：财联社/科创板日报 2026-08-26 独家报道，DoNews、网经社、观点网跟进，确认"串联创意策划、脚本创作、视觉设计、分镜生成和成片制作等环节"，与博文 5 个 Agent 完全吻合。
- **第 4 项 ManClaw**：什么值得买汇总多家媒体实测、产品信息站功能清单、潮新闻书旗大赛报道、manclaw.art 官网（内测中）交叉验证。注意：ManClaw 搭载字节 Seedance 2.0（F-035），非阿里自家 Wan 3.0。
- **第 5 项**：金羊网/羊城晚报 2026-08-24 南国书香节报道"赛事开放五万多部优质IP授权"，潮新闻 2026-07-01 报道"开放超过五万部优质IP授权"。
- **第 6 项**：阿里巴巴 2027 财年 Q1 财报（截至 2026-06-30），AI 相关产品季度收入 123.76 亿元，连续 12 个季度三位数增长，ARR 495 亿元。CEO 吴泳铭原话确认。
- **第 8 项**：国家广电总局令第 16 号，2026 年 7 月 27 日局务会通过，7 月 30 日公布，9 月 1 日施行。配套细则 8 月 17 日发布，AI 微短剧投资阈值单独设定（F-037）。

---

## 核验方法说明

核验采用轻量 WebSearch 方式：对照财联社/科创板日报、阿里云官方文档、Arena.ai 榜单、金羊网/羊城晚报、阿里巴巴财报、中文在线半年报、国家广电总局官网、腾讯新闻/极客电影等权威来源逐条确认博文关键声明。核验发现的错误以 F-036/F-038/F-039 勘误形式追加登记，补充信息以 F-035/F-037 追加登记，不与博文事实（F-001~F-034）混排。事实完整清单见 [博文信源事实清单](article-source.md)。

## 核验来源汇总

| 来源 | URL | 用途 |
|------|-----|------|
| 财联社/科创板日报 | https://www.cls.cn/detail/2465003 | F-003 千问多Agent协同独家报道 |
| DoNews | https://www.donews.com/news/detail/8/6686319.html | F-003 交叉验证 |
| 阿里云官方API文档 | https://help.aliyun.com/zh/model-studio/wan3-video-generation-api-reference | F-010 Wan 3.0 素材上限 |
| 阿里云Prime定价页 | https://help.aliyun.com/zh/model-studio/wan3-0-video-prime | F-012 双版本与定价 |
| 阿里云国际博客 | https://www.alibabacloud.com/blog/wan3-0-at-general-availability_603505 | F-039 Wan 2.7版本号确认 |
| Arena.ai | https://arena.ai/leaderboard/text-to-image | F-038 排名时效性 |
| 什么值得买 | https://post.m.smzdm.com/p/aww5ozvp/ | F-018~F-024 ManClaw能力汇总 |
| ManClaw官网 | https://manclaw.art/ | F-018 产品存在性（内测中） |
| 金羊网/羊城晚报 | http://news.ycwb.com/ikimvkctio/content_54276944.htm | F-025 书旗5万IP |
| 阿里巴巴集团官网 | https://home.alibabagroup.com/document-2027233133950140416 | F-026 财报 |
| 新浪财经 | https://cj.sina.com.cn/articles/view/7879848900/1d5acf3c406803a7vm | F-026 财报解读 |
| 上证报 | http://m.toutiao.com/group/7677955956793164314/ | F-028 中文在线1200部 |
| 腾讯新闻/极客电影 | http://news.qq.com/rain/a/20260818A03JK000 | F-036 小云雀S2确认 |
| DoNews（小云雀） | https://www.donews.com/news/detail/4/6657796.html | F-036 出品方与播放量 |
| 国家广电总局 | http://www.nrta.gov.cn/art/2026/7/31/art_113_73785.html | F-030 管理办法全文 |
| 法治日报 | http://m.legaldaily.com.cn/index/content/2026-08/07/content_9437287.htm | F-030 AI条款解读 |
| 中国经济时报 | http://news.cnr.cn/native/gd/20260805/t20260805_527748545.shtml | F-037 AI投资阈值 |
