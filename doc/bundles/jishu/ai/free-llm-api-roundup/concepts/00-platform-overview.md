---
okf_version: "0.2"
title: "2026免费大模型API全景：平台盘点与关键发现"
description: "2026年免费大模型API平台的全球全景概览——40家平台（国内23+国际17）的分类体系、额度规则、时效性警示，以及GitHub Models退役等重大变化。"
---

# 2026免费大模型API全景：平台盘点与关键发现

> ⚠️ **时效警示**：本文基于2026-06-17知乎文章，部分平台政策已发生变化（详见[references/verification.md](references/verification.md)）。各平台免费额度请以官方最新公告为准。

## 1. 平台总览

2026年上半年，中国及全球AI厂商纷纷推出免费大模型API服务，形成了激烈的"免费Token争夺战"。本文汇总了40家主流平台（国内23家 + 国际17家），覆盖文本生成、代码编写、多模态理解等多个场景。

### 国内平台（23家）

| 平台 | 代表模型 | 新用户免费额度 | 有效期 | 核心特点 | F编号 |
|------|---------|-------------|--------|---------|-------|
| 阿里云百炼 | Qwen3.6-Plus、DeepSeek全系 | 7000万Token | 90天 | 原生多模态、100万上下文 | F-007~F-016 |
| 腾讯云TokenHub | Hy3 preview、DeepSeek-V4-Flash | 50-100万Token | 90天 | 一站式聚合 | F-017~F-020 |
| 中国移动MoMA | 九天、DeepSeek全系 | 9000万Token | 未明确 | 300+模型联邦路由 | F-021~F-026 |
| 百度智能云千帆 | ERNIE-4.5-Turbo、DeepSeek R1 | 100万Token | 3个月 | 数理逻辑92%+ | F-027~F-032 |
| 字节火山方舟 | Doubao-Pro-128k、Seed 2.0 | 50万Token/模型 | 未明确 | 推理成本极低 | F-033~F-038 |
| 智谱AI（BigModel） | GLM-5、GLM-4-Flash | 2000万Token | 未明确 | GLM-4-Flash永久免费 | F-039~F-044 |
| 硅基流动 | DeepSeek-R1-0528、Qwen3-8B | ¥14赠金 | 未明确 | 1000 RPM高并发 | F-045~F-051 |
| Kimi（月之暗面） | Kimi-K2.6系列 | 不限总量/3次/分钟 | 未明确 | 256K超长上下文 | F-052~F-056 |
| DeepSeek官方 | V4-Pro（1.6T参数）、V4-Flash（284B） | 100万Token | 3天 | 1元/百万Token | F-057~F-061 |
| 百川智能 | Baichuan系列 | 500万Token | 未明确 | 开源模型 | F-062~F-064 |
| 腾讯混元 | 腾讯混元系列 | 100万Token | 1年 | 多模态能力强 | F-065~F-068 |
| 美团LongCat | LongCat-Flash系列 | 500万Token/天（Chat） | 每天刷新 | 长期免费 | F-069~F-073 |
| 讯飞星火 | Spark 4.0 Ultra | 200万Token | 未明确 | 语音交互 | F-074~F-078 |
| 讯飞星辰MaaS | GLM-5、Kimi-K2.5 | 0元/百万Token | 限时 | 完美适配OpenClaw | F-079~F-083 |
| 白山智算 | GLM-5 | 450元（邀请+实名） | 未明确 | 编程场景优化 | F-084~F-088 |
| 商汤日日新 | SenseNova 6.7 Flash-Lite | Token Plan限时免费 | 未明确 | 轻量级多模态 | F-089~F-092 |
| 小米MiMo | MiMo-V2.5系列 | 7亿→380亿Token | 30天 | 300亿总激励计划 | F-093~F-098 |
| 联通云Coding Plan | GLM5、Qwen3.5、MiniMax | 0元订阅 | 未明确 | 按调用次数计费 | F-099~F-102 |
| 欧派算力云 | DeepSeek-R1、V3 | 100万Token | 6个月 | 高性能编程 | F-103~F-105 |
| 零一万物 | Yi-Lightning | ¥10额度 | 未明确 | 李开复创办 | F-106~F-112 |
| 国家超算互联网 | DeepSeek API | 1000万Token | 3个月 | 国家队算力 | F-113~F-115 |
| Jina AI | jina-embeddings-v3、reranker-v2 | 100万Token | 未明确 | Embedding/Reranker专用 | F-116~F-120 |
| ModelScope魔搭 | Flux.1、QWen-Image | 2000次/天 | 未明确 | 阿里达摩院出品 | F-121~F-124 |
| OpenRouter | 聚合30+模型 | 50次/天（充值后1000次） | 未明确 | 国内可直连 | F-125~F-131 |

### 国际平台（17家）

| 平台 | 代表模型 | 免费额度 | 核心特点 | F编号 |
|------|---------|---------|---------|-------|
| Google AI Studio | Gemini 2.5 Flash/Pro | 按模型动态调整 | 百万级上下文 | F-132~F-139 |
| Groq | Llama 3系列、Mixtral | 1000次/天 | LPU硬件加速 | F-140~F-144 |
| ~~GitHub Models~~ | ~~GPT-4.1、Phi系列~~ | ~~已退役~~ | ❌ 2026-07-30退役 | F-145~F-150 |
| NVIDIA Build/NIM | DeepSeek V3.2、GLM-5.1 | 40 RPM（无总量限制） | 100+模型 | F-151~F-154 |
| Mistral AI | Mistral Large、Codestral | 约10亿Token/月 | 欧洲最强开源 | F-155~F-160 |
| Cerebras | Llama系列 | 100万Token/天 | 2600+ tokens/s | F-161~F-165 |
| Cloudflare Workers AI | 多种开源模型 | 10,000 Neurons/天 | 全球CDN边缘 | F-166~F-169 |
| HuggingFace | 数千开源模型 | 动态积分 | Serverless Inference | F-170~F-173 |
| AI21 Labs | Jamba Large/Mini | $10积分 | 长上下文处理 | F-174~F-176 |
| Scaleway Generative | — | 100 RPM | 欧洲GDPR合规 | F-177~F-179 |
| Together Free | Meta-Llama-3.1-8B | 无明确限制 | — | F-180~F-181 |
| Fireworks AI | — | $1积分 | 高并发企业级 | F-182~F-183 |
| Cohere | command-a系列 | 20 RPM | RAG优化 | F-184~F-186 |
| Modal | GLM-5 | 1-2路并发 | 限流非限Token | F-187~F-189 |
| xAI Grok | Grok 4.20、Grok-3 | $25/月 | 实时X数据访问 | F-190~F-196 |
| Anyscale | Llama 3.3 70B | $10额度 | Ray分布式加速 | F-197~F-201 |
| OpenAI | GPT-4o、GPT-4.1 | Free Tier（GPT-3.5 Turbo 3 RPM） | 行业标杆 | F-202~F-208 |

## 2. 关键发现

### 2.1 GitHub Models 已退役（F-145~F-150）⚠️【最重要变化】

GitHub Models 是博文发布时（2026-06-17）最热门的自由API平台之一，提供GPT-4.1、GPT-4o、Phi系列等模型。**然而该服务已于2026-07-30彻底退役下线**（[GitHub Blog](https://github.blog/changelog/2026-07-01-github-models-is-retiring-on-july-30th/)）。

退役时间线：
- 2026-06-16：停止新客户接入
- 2026-07-01：正式宣布退役
- 2026-07-16/07-23：两次brownout演练
- 2026-07-30：全面关停

**影响**：博文中将GitHub Models列为"代码生成&编程辅助推荐"（F-210）和"永久免费兜底推荐"（F-215）均失效。如需替代，可考虑NVIDIA NIM（F-151~F-154）或Google AI Studio（F-132~F-139）。

### 2.2 小米MiMo额度大幅升级（F-093~F-094）

博文发布时小米MiMo为7亿Token级别，但2026-05-27已宣布MiMo-V2.5升级：
- Pro档从7亿升至**380亿Credits**（5-8倍增长）
- Lite档最低也有5亿Token
- 新加坡节点API兼容OpenAI格式，非高峰期打8折

### 2.3 OpenAI Free Tier 已基本失效（F-055）

OpenAI Free Tier 的 $5 赠金已于2023年底取消。目前仅剩 GPT-3.5 Turbo（3 RPM），免费额度极为有限。

### 2.4 Google AI Studio限额因模型差异巨大（F-132~F-134）

"1500次/天"仅适用于部分旧版Flash模型。新版限额：
- Gemini 2.5 Flash：250K TPM / 10 RPM
- Gemini 2.5 Pro：50 RPD（非博文所述的400 RPD）
- 限额因账户、地区、使用历史动态变化

### 2.5 中国移动MoMA额度口径存疑（F-115）

官方宣传页面显示为2500万Token，9000万可能为活动叠加后的累计总额。建议以官方口径为准。

## 3. 额度对比：薅最多Token的平台

按新用户免费额度排序（估算）：

| 排名 | 平台 | 免费额度 | 备注 |
|------|------|---------|------|
| 1 | 小米MiMo | 380亿Credits（Pro档） | 2026-05-27升级，30天有效 |
| 2 | 中国移动MoMA | 2500万~9000万Token | 口径存疑，官方为2500万 |
| 3 | 阿里云百炼 | 7000万Token + 100亿（企业） | 90天有效 |
| 4 | 智谱AI | 2000万Token | GLM-4-Flash永久免费 |
| 5 | 字节火山方舟 | 50万Token/模型 + 200万/天协作 | 推理成本极低 |
| 6 | 美团LongCat | 5亿Token/天（Flash-Lite） | 长期免费，每天刷新 |
| 7 | 百度千帆 | 100万Token/模型 | 3个月有效 |

> 注：F-216"薅最多Token推荐：小米MiMo（7亿+）、中国移动MoMA（9000万）、阿里云百炼（7000万）"整体方向正确，但小米MiMo额度已大幅升级至380亿Credits。

## 4. 内容导航

- [国内平台详解（23家）](concepts/01-domestic-platforms.md)
- [国际平台详解（17家）](concepts/02-international-platforms.md)
- [选型指南](concepts/03-selection-guide.md)
- [参考与附件](references/index.md)

```{toctree}
:maxdepth: 2
:hidden:

concepts/01-domestic-platforms
concepts/02-international-platforms
concepts/03-selection-guide
references/index
log
```
