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
| **RMB/元** | — | 人民币计价单位。国内平台常用（如DeepSeek 1元/百万Token、阿里云Coding Plan 200元/月）。 | 付费平台定价 |
| **USD/$** | — | 美元计价单位。国际平台常用（如OpenAI Free Tier曾提供$5赠金）。 | OpenAI、Google AI Studio等 |

---

## 速率限制术语

| 术语 | 全称 | 解释 | 典型值 |
|------|------|------|--------|
| **RPM** | Requests Per Minute | 每分钟最多可发起的请求次数。超过后API返回429错误，需等待下一分钟窗口。 | 智谱GLM-4-Flash：不限；Google Gemini 2.5 Pro：5 RPM |
| **RPD** | Requests Per Day | 每天最多可发起的请求次数。按自然日或滚动24小时计算。 | Google Gemini 2.5 Pro：50 RPD（非博文所述的400 RPD） |
| **TPM** | Tokens Per Minute | 每分钟最多可消耗的Token总数。同时受RPM和TPM双重限制。 | Google Gemini 2.5 Flash：250K TPM |
| **并发** | Concurrency | 同时可处理的请求数量。高并发场景需要多路请求同时发送。 | 智谱GLM-4-Flash：限30并发 |
| **RPS** | Requests Per Second | 每秒最多可发起的请求次数。高RPS通常意味着低延迟。 | Groq：约14400次/天≈4次/秒 |

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
| **DeepSeek-R1** |  DeepSeek推出的推理模型系列，擅长数学、代码、逻辑推理。 | 多家平台接入 |

---

## 平台专有术语

| 术语 | 所属平台 | 解释 |
|------|---------|------|
| **Token Plan** | 阿里云百炼 | 按Token计费的订阅方案，首月5折、包季4.5折。另有Coding Plan（200元/月）专注编程场景。 |
| **Credits** | 小米MiMo | MiMo平台的通用额度单位，380亿Credits（Pro档）相当于约380万亿Token的购买力（视模型而定）。 |
| **MoMA** | 中国移动 | Model Orchestration & Management Architecture的缩写，中国移动的大模型联邦平台。 |
| **LongCat** | 美团 | 美团推出的长期免费大模型API服务，每天自动刷新额度。 |
| **TokenHub** | 腾讯云 | 腾讯云的一站式多模型API聚合平台。 |
| **日日新** | 商汤 | 商汤SenseNova大模型平台，提供免费多模态API。 |

---

## 其他术语

| 术语 | 解释 |
|------|------|
| **Free Tier** | 云服务商提供的免费使用层级，通常有额度或速率限制，超出后需付费或降级。 |
| **BYOK** | Bring Your Own Key，用户自带API Key调用模型。GitHub Models曾支持此模式。 |
| **Rate Limiting** | 速率限制，平台为防止滥用而对API调用频率施加的限制。 |
| **429 Error** | HTTP状态码"Too Many Requests"，表示请求频率超过了平台限制。 |
| **Base URL** | API请求的基础URL，不同平台的base_url不同。OpenAI兼容接口允许直接替换base_url切换平台。 |
| **P0核验** | Priority 0 核验，指对核心推荐或关键事实进行的最高优先级权威验证。本bundle中完成了9组P0核验。 |
