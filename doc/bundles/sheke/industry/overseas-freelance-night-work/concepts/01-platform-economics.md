---
type: Concept
title: "平台费率、资格与净收入边界"
description: "把平台标价拆成资格、抽成、支付费和等待成本，避免把页面价格当成收入。"
tags: [平台费率, 收款, 净收入, 风险边界]
generated: { by: "agent/seven-concepts-cmd", at: "2026-09-20T06:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-20T06:00:00Z" }
status: stable
stale_after: "2026-12-31"
sources:
  - { id: blog, resource: "https://mp.weixin.qq.com/s/S2XalFkN_5HV4tBpUZljrA" }
  - { id: italki, resource: "https://support.italki.com/hc/en-us/articles/206352068-How-does-italki-charge-a-commission" }
  - { id: preply, resource: "https://help.preply.com/en/articles/4171383-preply-commission-model" }
  - { id: upwork, resource: "https://community.upwork.com/hc/en-us/articles/211062538-Learn-about-the-Freelancer-Service-Fee" }
  - { id: crowdgen, resource: "https://crowdgen.com/docs/payments/general-payments-faq/payout-options-and-fees/" }
  - { id: gumroad, resource: "https://gumroad.com/pricing/" }
---

# 平台费率、资格与净收入边界

## 四层收入模型

不要用“公开报价 × 工作时长”直接估算收入。至少拆成：

`可接单收入 = 标价 × 完成量 × (1 - 平台抽成) - 支付费 - 返工成本 - 获客成本`

同时要先乘上两个资格系数：地区/项目可用性与个人审核通过率。任何一个为零，公开标价都没有意义。

## 官方规则快照

| 平台 | 官方事实 | 不能推断的内容 |
|---|---|---|
| italki | 试听 0%，单节 21%，5 节包 19%，10 节包 17%，15/20 节包 15%（F-028）。 | 不能推断教师一定能获得学生或达到博文价格。 |
| Preply | 新学生试听课佣金 100%，后续 18%–33%，新教师起始 33%，20 小时后 28%（F-029）。 | 不能把“佣金下降”写成净收入增长保证。 |
| Upwork | 自由职业者服务费为 0%–15%，合同开始后固定（F-031）。 | 职类页面报价不是你的合同报价。 |
| Rev | 字幕翻译 1.70–4.00+ 美元/音频视频分钟，按周 PayPal 付款（F-030）。 | 费率按语言、项目和审核结果变化。 |
| CrowdGen | 支付方式与费率按国家和第三方提供商变化，中国 CNY 示例为 1.36 美元+1.53%（F-034、F-035）。 | 不能从费率表推断项目一定对大陆开放。 |
| Gumroad | 直链/个人主页成交 10%+0.50 美元，Discover 30%，无月费（F-036）。 | 不能忽略提现、税务和获客成本。 |

## 核验顺序

1. 打开官方资格页，确认所在地区和语言。
2. 打开平台费率页，记录当前抽成与支付费。
3. 完成支付账户验证，确认能收到款。
4. 用一个小样品测试接单和交付。
5. 记录实际净收入，不记录“理论时薪”。
