---
type: Reference
title: "文章事实与官方补充"
description: "四十条声明的来源、归属和证据边界；案例数字保留原文单源标记"
tags: [Jev, TypeSafe, 事实核验]
generated: { by: "process:seven-concepts-e", at: "2026-09-20" }
status: flagged
stale_after: 2026-10-20
sources:
  - { id: article, resource: "https://mp.weixin.qq.com/s/lnWrTGbsLO59w_7cK_rTqQ" }
  - { id: launch, resource: "https://typesafe.ai/blog/introducing-system-one-models-and-jev" }
  - { id: api, resource: "https://docs.typesafe.ai/api" }
  - { id: models, resource: "https://docs.typesafe.ai/models" }
  - { id: primitives, resource: "https://docs.typesafe.ai/primitives" }
  - { id: confidence, resource: "https://docs.typesafe.ai/confidence" }
  - { id: state, resource: "https://docs.typesafe.ai/concepts/state" }
---

# 文章事实与官方补充

## 阅读范围

微信页面为逛逛GitHub的《外网 3500 万人围观的 Jev 模型，有这 10 个神奇玩法。》。本次于2026-09-20读取正文 DOM（含控件共2886字符），未提取图片文字、转录视频或复制全文。以下全部为原创转述。

官方页面通过 Defuddle 阅读正文。官方机制说明是接口认知的直接来源；官方性能仍属于厂商自述。十个演示是微信二手转述，不能与官方文档拼成“多源独立复现”。逐链接访问记录见[核验报告](verification.md)。

## 来源代号

| 代号 | 来源 | 信源距离 |
| --- | --- | --- |
| W | [微信文章](https://mp.weixin.qq.com/s/lnWrTGbsLO59w_7cK_rTqQ) | 第三方应用盘点 |
| O1 | [发布说明](https://typesafe.ai/blog/introducing-system-one-models-and-jev) | 厂商定位、测量与预测 |
| O2 | [API 文档](https://docs.typesafe.ai/api) | 官方接口契约 |
| O3 | [模型配置](https://docs.typesafe.ai/models) | 官方时效快照 |
| O4 | [原语说明](https://docs.typesafe.ai/primitives) | 官方机制与设计建议 |
| O5 | [置信度说明](https://docs.typesafe.ai/confidence) | 官方统计量与阈值建议 |
| O6 | [状态说明](https://docs.typesafe.ai/concepts/state) | 官方输入组织方式 |

## 事实登记

编号与上游 Spec 的 facts.md 一一对应。状态中的“已读”仅表示本次获得页面证据，“官方口径”不等于独立实测。正文引用 F 编号时可以在本表查到对应来源。

| 编号 | 声明 | 来源 | 状态与限制 |
| --- | --- | --- | --- |
| F-001 | 微信作者逛逛，公众号逛逛GitHub；标题含3500万人与十种玩法，页面显示2026-09-19 11:48、北京。 | W | 元信息已读；热度未核实 |
| F-002 | 标题3500万人没有平台、期间、统计对象与去重口径。 | W | 原文单源，不能当用户数 |
| F-003 | 发布文署名 Diogo Almeida、TypeSafe founder；其自述曾在 OpenAI 参与指令跟随和聊天方法研究。 | O1 | 署名与履历自述；未独立查履历 |
| F-004 | TypeSafe 将 Jev 定位为首个公开 System One Model：状态输入、类型化概率决策输出，放弃自由字符串生成。 | O1 | 官方定位 |
| F-005 | 发布文介绍新架构、并行采样及 RLCD，即 Reinforcement Learning for Calibrated Decisions。 | O1 | 官方路线；不足以复原训练算法 |
| F-006 | 每百万输入 token 0.042美元，每十亿42美元，输出不计费。 | O1、O3 | 同厂商两页一致；2026-09-20快照 |
| F-007 | 官方称端到端70–500 ms，发布评测一般在美国西海岸笔记本访问当地服务。 | O1 | 厂商口径，非全球SLA |
| F-008 | 193.6倍快、444.6倍便宜来自官方工作流评测；官方称处于真实收益区间高端。 | O1 | 非普遍收益承诺 |
| F-009 | 工作流评测参考为 GPT-6 Astra 与 Fable 5.1 的平均预测，工作流由能力团队设计，官方承认潜在偏差。 | O1 | 非人工真值或独立评测 |
| F-010 | 官方0%指schema/type约束，并说明不是经验测量。 | O1 | 不证明业务判断全对 |
| F-011 | 发布文写 early access 与 waitlist；本次正文未提供可确认的精确发布日期。 | O1 | 不写成GA或确切发布日期 |
| F-012 | 跑酷案例称50局并行、该次运行不到1美分。 | W第1项 | 原文单源；无时长、调用数、成绩、账单 |
| F-013 | 马里奥案例描述按游戏状态选择移动、跳跃动作。 | W第2项 | 原文单源；无schema和测量日志 |
| F-014 | 杀戮尖塔2案例称此前使用 GPT-6 Astra、Jev思考约0.7秒；人名paulwei与链接账号coolish并存。 | W第3项 | 原文单源；账号对应待核 |
| F-015 | 3D城市交通仿真描述状态、决策、执行、反馈，称搭建不到一小时。 | W第4项 | 原文单源；开发时间不是推理时间 |
| F-016 | MuJoCo火箭仿真涉及点火、发动机数和阶段；称调整12次、成功运行245次API、约0.04美元。 | W第5项 | 原文单源；费用范围未知 |
| F-017 | 像素案例逐像素选择颜色及概率，由程序汇总渲染。 | W第6项 | 原文单源；非原生图像生成接口证据 |
| F-018 | 航班案例由Jev选浏览器动作、小LLM处理文本输入，称7秒、0.0039美元。 | W第7项 | 原文单源；完整成本边界未知 |
| F-019 | Riley Brown写作案例对帖子传播潜力提供实时反馈。 | W第8项 | 原文单源；无传播预测效果证据 |
| F-020 | 广告案例称37品牌、724广告、40秒、9美分，评价钩子、素材、优惠、转化目标与落地页匹配。 | W第9项 | 原文单源；数据集和准确率未给出 |
| F-021 | 上下文案例评价历史网页、文件、工具结果对当前任务的相关性并筛选。 | W第10项 | 原文单源；无压缩率、误删率、质量对照 |
| F-022 | 第8项混入01编号与角色卡描写，结尾11为关注引导；技术案例仍为十项。 | W | 正文结构观察 |
| F-023 | POST https://api.typesafe.ai/v1/systemone 使用Bearer鉴权，请求必需state、model、questions。 | O2 | 契约已读，未调用 |
| F-024 | questions的key只用于映射，不发送给底层模型或参与推断。 | O2、O4 | 完整问题需写instructions |
| F-025 | Noul的type为noul，返回noul（0～1的yes概率），无独立confidence；criteria可选。 | O2、O4 | 0.5不表示中等质量 |
| F-026 | Choice的type为choice，criteria为选项与说明映射，返回choice、probabilities、confidence。 | O2、O4 | criteria必需 |
| F-027 | Score的type为score，criteria为至少两个有序等级，返回score、legend、probabilities、confidence，可落在等级间。 | O2 | 分值依赖等级定义 |
| F-028 | Choice/Score的confidence来自概率分布形状；Noul通过yes概率表达不确定性。 | O2、O4、O5 | 所读页面未提供精确计算公式 |
| F-029 | 同请求各问题共享state、独立并行，一个答案不作为另一题隐藏上下文。 | O4 | 真依赖需要后续请求 |
| F-030 | 响应含answers、model和usage的input_tokens/output_tokens；错误列401、422、429、529。 | O2 | 429/529建议指数退避，SDK默认处理；未实测 |
| F-031 | 当前模型页列jev-1.13.0，jev-latest/jev-preview都指向它；别名会移动，响应model可记录版本。 | O3 | 2026-09-20快照 |
| F-032 | 当前限额250,000 tokens/s、1,200 requests/min，官方同时说明动态调整。 | O3 | 非固定合同限额 |
| F-033 | 模型页总请求预算64k tokens；state加最长单题预算32k tokens。 | O3 | 与原语页口径有冲突 |
| F-034 | 原语页仍称state与questions共享约32,000 tokens。 | O4 | 未做临界请求测试 |
| F-035 | 当前仅文本输入：string、JSON object或文本值数组，不接受图像、音频、视频。 | O3、O6 | 其他模态需外围预处理 |
| F-036 | 英语为主要训练语言且当前表现最好；CJK等其他语言支持但表现不等同英语。 | O3 | 需要本域语料评测 |
| F-037 | 官方不按客户数据fine-tune/LoRA，同权重服务各账户；请求响应不用于训练；企业ZDR另见法律文档。 | O3 | 法律全文未审计，不代表所有账户零留存 |
| F-038 | 官方建议原子问题拆分、代码组合；Choice不穷尽时增加other/none。 | O4 | 设计建议，不是授权政策 |
| F-039 | 官方Doom演示使用结构化文本状态；发布文另述Choice上限255，更多候选先评分再选择。 | O1 | 不替代微信十案例的独立证据 |
| F-040 | 官方以William Stanley Jevons为命名来源并预期成本降低扩大用途；微信将低价与高密度调用关联。 | O1、W | 厂商预期与作者观点，非采用率统计 |

## 原文与解释的分界

教程对每例的“状态、判断、输出、外围执行”拆解是依据官方契约作出的教学建模，不是对原项目源码的还原。没有获得的输入字段、参数、代码版本和性能结果均不补写。

返回[信源导航](index.md)。
