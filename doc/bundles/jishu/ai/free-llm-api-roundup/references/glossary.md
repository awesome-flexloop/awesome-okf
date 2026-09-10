---
okf_version: "0.2"
title: "术语表"
description: "本bundle中出现的API额度计量、速率限制、平台专有术语解释。"
---

# 术语表

> 本文档汇总本bundle中出现的各类术语，帮助读者理解各平台的额度描述与限制条件。

---

## 额度计量单位

| 术语 | 全称 | 解释 | 常见场景 |
|------|------|------|---------|
| **Token** | — | LLM处理文本的最小单位。大致相当于0.75个英文单词或0.5个中文字符。不同模型的分词器不同，实际换算略有差异。 | 几乎所有平台用Token计量免费额度（如"7000万Token"） |
| **Credits** | — | 部分平台（如小米MiMo）使用的通用额度单位。1 Credit ≈ 1000 Tokens，但具体换算因模型而异。Credits可用于调用不同模型，不受单一模型Token限制。 | 小米MiMo：380亿Credits（Pro档） |
| **动态积分** | Dynamic Credits | HuggingFace等平台的积分制度：每月根据账户等级（Free/Plus/Premium）动态发放免费推理积分。 | HuggingFace Serverless Inference：按月动态积分 |
| **RMB/元** | — | 人民币计价单位。国内平台常用（如DeepSeek 1元/百万Token、阿里云Coding Plan 200元/月）。 | 付费平台定价 |
| **USD/$** | — | 美元计价单位。国际平台常用（如OpenAI Free Tier曾提供$5赠金）。 | OpenAI、Google AI Studio等 |
| **API Key** | API Key | 应用程序接口密钥，用户通过平台注册后获取的唯一身份凭证，用于调用API时的身份鉴权。 | 所有平台均需 |

---

## 速率限制术语

| 术语 | 全称 | 解释 | 典型值 |
|------|------|------|--------|
| **RPM** | Requests Per Minute | 每分钟最多可发起的请求次数。超过后API返回429错误，需等待下一分钟窗口。 | 智谱GLM-4-Flash：不限；Google Gemini 2.5 Pro：5 RPM |
| **RPD** | Requests Per Day | 每天最多可发起的请求次数。按自然日或滚动24小时计算。 | Google Gemini 2.5 Pro：50 RPD（非博文所述的400 RPD） |
| **TPM** | Tokens Per Minute | 每分钟最多可消耗的Token总数。同时受RPM和TPM双重限制，大Token模型优先受TPM制约。 | Google Gemini 2.5 Flash：250K TPM；Mistral AI：50万tokens/min |
| **TPS** | Tokens Per Second | 每秒生成Token数，衡量推理速度而非限流指标。与RPM不同——TPS是性能指标，RPM是频率限制。 | Groq：300+ TPS；Cerebras：2600+ TPS |
| **并发** | Concurrency | 同时可处理的请求数量。高并发场景需要多路请求同时发送，超过后请求排队或直接拒绝。 | 智谱GLM-4-Flash：限30并发；Modal：1-2路并发 |
| **RPS** | Requests Per Second | 每秒最多可发起的请求次数，与RPM可换算（RPS×60=RPM）。部分平台用RPS而非RPM表示限制。 | Scaleway：100 RPM≈1.7 RPS |
| **Fair Use** | 公平使用 | 平台对免费用户施加的使用限制策略，通常隐含在"免费"条款中，超出后会被降速或暂停。 | 讯飞星火：Spark 4.0 Ultra免费使用（Fair use） |
| **Rate Limiting** | 速率限制 | 平台为防止滥用而对API调用频率施加的限制，通常通过RPM/RPD/TPM等维度实现。 | 见"RPM"/"RPD"/"TPM"各条目 |
| **429 Error** | HTTP 429 Too Many Requests | 请求频率超过平台限制时返回的HTTP状态码，表示需要等待限流窗口重置后再发起请求。 | 所有平台通用 |
| **8B模型** | 8-Billion Parameter Model | 参数量约80亿参数的轻量级开源模型（如Llama-3.1-8B、Qwen2.5-7B），推理速度快、免费额度通常更高。 | Groq 8B模型：14400次/天；硅基流动：Qwen2.5-7B永久免费 |

---

## 模型能力术语

| 术语 | 解释 | 本bundle中的出现 |
|------|------|----------------|
| **上下文窗口** (Context Window) | 模型单次请求可处理的最大Token数。大上下文窗口支持长文档、长代码库的理解。 | 阿里云百炼：100万token；Kimi：256K；Google Gemini：百万级 |
| **多模态** (Multimodal) | 模型可同时处理文本、图像、音频、视频等多种输入类型。 | 百度千帆、腾讯混元、Google Gemini |
| **Serverless Inference** | 按需分配算力的推理模式，无请求时不消耗资源，适合低频使用场景。 | HuggingFace Serverless Inference |
| **模型联邦** | 通过智能路由将请求分发到多个后端模型，实现成本优化与高可用。 | 中国移动MoMA：300+模型联邦路由 |
| **LPU** | Language Processing Unit，Groq定制的AI推理芯片，相比GPU在自回归生成场景下速度更快。 | Groq：300+ tokens/s推理速度 |
| **OpenAI兼容接口** | API格式与OpenAI官方接口保持一致，可直接替换base_url切换到其他平台。 | 阿里云百炼、硅基流动、ManyAPI等均支持 |
| **DeepSeek-R1** | DeepSeek推出的推理模型系列，擅长数学、代码、逻辑推理。 | 多家平台接入 |
| **Embedding** | 将文本转换为高维向量表示的技术，用于语义搜索、RAG检索增强等场景。 | Jina AI：jina-embeddings-v3（专门做Embedding） |
| **Reranker** | 对初步检索结果按相关性重新排序的模型，提升RAG检索精度。 | Jina AI：jina-reranker-v2 |
| **WSE** | WebScale Engine，Cerebras定制的AI训练/推理芯片，单芯片即可容纳完整大模型，无需模型并行。 | Cerebras：2600+ tokens/s推理速度 |
| **Neurons** | Cloudflare Workers AI的算力计量单位，用于衡量AI推理消耗的资源量。 | Cloudflare Workers AI：10,000 Neurons/天免费额度 |
| **Free Trial** | 免费试用，平台为新用户提供有限额度或期限的试用服务，试用期结束后需付费。 | NVIDIA NIM：限时免费；Modal：限时免费；Fireworks AI：$1积分 |
| **推理成本** | 模型推理的单位Token价格，反映调用成本效率。不同模型推理成本差异巨大（如DeepSeek 1元/百万Token vs GPT-4o约$30/百万Token）。 | 字节火山方舟：推理成本极低；DeepSeek官方：1元/百万Token |
| **混合架构** | 模型采用多种架构组件（如MoE混合专家、状态空间模型等）的组合设计，以提升效率。 | AI21 Labs Jamba：混合架构 |
| **MoE** | Mixture of Experts，混合专家架构，模型包含多个"专家"子网络，每次推理只激活部分专家，提升效率。 | 业界大模型普遍采用（如DeepSeek-V3使用MoE） |

---

## 平台专有术语

| 术语 | 所属平台 | 解释 |
|------|---------|------|
| **Token Plan** | 阿里云百炼 | 按Token计费的订阅方案，首月5折、包季4.5折。另有Coding Plan（200元/月）专注编程场景。 |
| **Coding Plan** | 阿里云百炼 / 联通云 | 专注编程场景的订阅方案。阿里云百炼Coding Plan Pro版200元/月（每月90,000次请求）；联通云Coding Plan 0元订阅按调用次数计费。 |
| **Lite Plan / Pro Plan** | 字节火山方舟 / 阿里云百炼 | 平台套餐分级：Lite为轻量免费版，Pro为付费高级版，功能与额度不同。 |
| **Andante Plan** | Kimi | Kimi的月度付费套餐，¥49/月，提供更高调用额度。 |
| **Credits** | 小米MiMo | MiMo平台的通用额度单位，380亿Credits（Pro档）相当于约380万亿Token的购买力（视模型而定）。 |
| **MoMA** | 中国移动 | Model Orchestration & Management Architecture的缩写，中国移动的大模型联邦平台。 |
| **LongCat** | 美团 | 美团推出的长期免费大模型API服务，每天自动刷新额度。 |
| **TokenHub** | 腾讯云 | 腾讯云的一站式多模型API聚合平台。 |
| **日日新** | 商汤 | 商汤SenseNova大模型平台，提供免费多模态API。 |
| **OpenClaw** | 智谱AI / 白山智算 | 跨平台AI编码框架，支持多模型接入；智谱AI原生支持OpenClaw，白山智算也为其模型提供OpenClaw适配。 |
| **OpenRouter** | — | 聚合30+模型的API网关平台，一个API Key可调用多家厂商模型，国内可直连。 |
| **Tier System** | OpenAI | OpenAI按累计付款金额解锁更高层级额度限制的分层系统，Free Tier为基础免费层。 |
| **邀请码** | 白山智算 / 部分国内平台 | 平台注册或获取额度所需的邀请码/兑换码，部分平台通过活动或合作发放。 |
| **实名认证** | 讯飞星辰MaaS / 多数国内平台 | 用户需提供真实身份信息才能使用API，是国内平台常见的合规要求。 |
| **手机号验证** | NVIDIA NIM / 多数国内平台 | 仅需中国大陆手机号即可完成注册验证，无需信用卡，是国产平台对用户友好的门槛。 |
| **Singapore Node** | 小米MiMo | MiMo新加坡节点，API兼容OpenAI格式，非高峰期享8折优惠。 |

---

## 其他术语

| 术语 | 解释 |
|------|------|
| **Free Tier** | 云服务商提供的免费使用层级，通常有额度或速率限制，超出后需付费或降级。OpenAI Free Tier目前已仅剩GPT-3.5 Turbo（3 RPM），$5赠金已于2023年底取消。 |
| **Base URL** | API请求的基础URL，不同平台的base_url不同。OpenAI兼容接口允许直接替换base_url切换平台。 |
| **P0核验** | Priority 0 核验，指对核心推荐或关键事实进行的最高优先级权威验证。本bundle中完成了9组P0核验。 |
| **Brownout** | 渐进式限电/限服演练。GitHub Models退役前于2026-07-16和07-23进行了两次brownout演练，模拟服务关停状态。 |
| **GDPR** | General Data Protection Regulation（通用数据保护条例），欧盟数据保护法规。Mistral AI和Scaleway因服务器在欧洲，天然满足GDPR合规。 |
| **RAG** | Retrieval-Augmented Generation（检索增强生成），将外部知识库检索结果作为上下文注入LLM生成过程，提升回答准确性。Jina AI的Embedding/Reranker技术专为RAG场景优化。 |
| **Token化** (Tokenization) | 将文本分割为模型可处理的最小单位（Token）的过程，不同模型使用不同的分词器，实际换算略有差异（约0.75英文词/Token，0.5中文字符/Token）。 |
| **开源模型生态** | 平台开放的开源模型集合，用户可直接部署或微调。小米MiMo、HuggingFace等平台支持接入Claude Code等第三方工具链。 |
| **Ray分布式框架** | Anyscale基于的分布式计算框架，由UC Berkeley教授创办，用于大规模模型推理加速。 |
| **幻觉率** (Hallucination Rate) | 模型生成内容中与事实不符的比例。xAI Grok宣称业界最低幻觉率，适合需要高准确性的场景。 |
| **数据共享计划** | xAI曾推出$150/月的数据共享计划，用户可将数据分享给xAI以换取服务权益，该计划已终止。 |
| **厂商自宣** | 厂商自行宣传的能力数据或成效数字，未经独立第三方验证。本bundle中标注了多处厂商自宣（如MoMA"降低30%成本"、百度千帆"数理逻辑准确率92%+"）。 |
| **额度有效期** | 免费Token额度的使用期限，常见有3天（DeepSeek）、30天（小米MiMo）、90天（阿里云百炼）、1年（腾讯混元）不等，过期未用即作废。 |
| **认证奖励** | 平台通过用户认证（学生认证、企业认证、个人认证）额外赠送的额度。如硅基流动企业认证送500元、学生认证送50元；Kimi个人认证送15元。 |
| **按需计费** | 按实际使用的Token数或调用次数计费，无固定套餐。与订阅制相对，适合用量波动大的场景。 |
| **API Key轮换** | 当某个API Key达到限流或额度上限时，切换至另一个Key继续调用。部分用户通过多账号策略实现额度叠加。 |
