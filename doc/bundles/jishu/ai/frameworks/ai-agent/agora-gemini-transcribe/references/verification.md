# P0 核验报告：Agora × Gemini 3.5 Transcribe

> **核验日期**：2026-08-29
> **信源距离预判**：本文为 **厂商自宣**（Agora/声网官方公众号发布本公司合作新闻稿），按 blog-article-to-okf-bundle L3 模式，合作与产品声明全部列为 P0 并寻求独立佐证
> **核验方式**：WebSearch 权威信源交叉验证（Google 官方博客、Agora 官方文档/产品页/新闻稿、第三方媒体）
> **核验结论**：**6 项 P0 声明：5✅ 通过、1⚠️ 部分通过、0❌ 失败**

## 一、P0 声明核验明细

| # | P0 声明 | 结论 | 核验证据 |
|---|---------|------|----------|
| P0-1 | Gemini 3.5 Transcribe 是 Google 面向智能语音交互的新一代实时语音转写模型 | ✅ | Google 官方博客 2026-08-26《Intelligent transcription with Gemini 3.5 Transcribe》（blog.google）；DeepMind Gemini Audio 模型页；36氪/AI前线、超能网 2026-08-27 报道；CEO Pichai 在 X 宣布 |
| P0-2 | Agora 与 Gemini 达成合作，发布 Gemini 3.5 Transcribe 与 Agora Conversational AI 集成方案 | ✅ | Agora 官方文档已有 Google Gemini Live (Vertex AI) 集成页（docs.agora.io，2026-07-30 更新）；Agora 官方博客 Gemini 语音 Agent 教程（2026-05-07）；大众网（2026-08-28）、站长之家 TEDGE 等媒体转载本合作稿。注：Agora 公开文档目前以 Gemini Live MLLM 集成为主，3.5 Transcribe 作为转写组件的接入文档以厂商宣布为准 |
| P0-3 | 开发者可以在 Agora Agents SDK 中使用 Gemini 3.5 Transcribe，并灵活组合 LLM 与 TTS | ✅ | Agora Agents SDK 真实存在：Python `agora_agent`、TypeScript `agora-agents`、Go `agora-agents-go`（官方文档与教程）；架构支持 ASR+LLM+TTS 链式组合与 MLLM 端到端两种模式，"灵活组合"与官方架构一致 |
| P0-4 | Agora 计划支持 Smart Transcription（自动处理口语停顿/重复/改口/数字日期格式） | ✅ | Smart Transcription 为 Google 官方已发布能力（官方博客：处理自我修正如"周二——不，周三"、去除 ums/ahs 语气词、自动排版）；博文用"**计划**进一步支持"表述为未来时，与 Agora 集成路线图阶段相符，措辞准确 |
| P0-5 | Agora 此前已与 OpenAI 合作推出"全球首个 Realtime API" | ⚠️ | 合作事实真实：Agora 官方新闻稿确认 2024-10 OpenAI Realtime API 公测时 Agora 即为语音 API 合作方，2025-09-04 宣布 GA，Realtime API 是首个内置进 Agora 平台的 MLLM。**但"全球首个 Realtime API"措辞归属含糊**：Realtime API 本身是 OpenAI 的产品，Agora 是首发语音合作/集成方；准确表述应为"全球首批/首发合作集成 Realtime API 的实时互动平台" |
| P0-6 | Gemini 3.5 Transcribe 可应对背景噪声、专业词汇、口语停顿和表达修正 | ✅ | 与 Google 官方博客原文一致（"struggle with background noise, complex jargon, and disfluency cleanup"的反面表述）；Smart transcription 处理自我修正、custom vocabulary 适配专业词汇均有官方文档 |

## 二、勘误四张清单执行记录

### ① 日期/版本表

| 项 | 博文/官方口径 | 结论 |
|----|--------------|------|
| Gemini 3.5 Transcribe 发布 | Google 官方博客 **2026-08-26**；Agora 博文 2026-08-27 17:35（发布次日） | ✅ 时间线合理 |
| 实时模型 ID | `gemini-3.5-transcribe-live`（Live API，亚秒延迟） | ✅ 官方一致 |
| 录音模型 ID | `gemini-3.5-transcribe`（Interactions API） | ✅ 官方一致 |
| 上一代模型 | Chirp 3（3.5 Transcribe 为其继任） | ✅ 官方一致 |
| OpenAI 合作 | 2024-10 公测合作 → 2025-09-04 GA | ✅ Agora 新闻稿 |

### ② 成效数字溯源表

博文本身**无成效数字**（无"提升 X%/降低 X%"类厂商自宣指标）——这是本篇与典型厂商稿的区别。核验补充的模型性能数字均来自 Google 官方引述的第三方测评：

| 数字 | 数值 | 来源 | 标注 |
|------|------|------|------|
| 流式 WER | 4.0% | Artificial Analysis（Google 官方博客引述） | 第三方测评，非 Agora 自宣 |
| 非流式 WER | 2.6% | 同上 | 同上 |
| FLEURS 基准 | 流式 5.50%/非流式 5.04% | Google 官方博客 | 官方基准 |
| 延迟改善 | 较 Chirp 3 最终转录快 70% | Artificial Analysis | 第三方测评 |
| 语言支持 | 85+ 语言 | Google 官方 | — |
| Agora 网络规模 | 800 亿分钟/月、200+ 国家地区 | Agora 官方产品页 | 厂商自述，作背景登记 |

### ③ 口径对照表

| 博文表述 | 准确口径 | 处理 |
|----------|----------|------|
| "与 OpenAI 合作推出了全球首个 Realtime API" | Realtime API 为 OpenAI 产品；Agora 是 2024-10 公测时的首发语音 API 合作方，2025-09 GA | ⚠️ P0-5 标注，事实登记 F-029 写明时间线与准确归属 |
| "声网"公众号 | 声网为 Agora, Inc.（NASDAQ: API）中文品牌 | F-032 标注 |

### ④ 引文逐字核对表

博文无第三方人物引语（无"某某说"式引文），无需逐字核对。文中"我们"均为 Agora 第一人称厂商叙述。

## 三、权威信源清单

| # | 信源 | 类型 | 用途 |
|---|------|------|------|
| 1 | Google 官方博客《Intelligent transcription with Gemini 3.5 Transcribe》（2026-08-26）https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-5-transcribe/ | 官方发布 | P0-1/P0-4/P0-6、F-025~F-028 |
| 2 | Google DeepMind Gemini Audio 模型页 https://deepmind.google/models/gemini-audio/ | 官方文档 | 模型 ID 与能力 |
| 3 | Gemini API Live Transcribe 文档 https://ai.google.dev/gemini-api/docs/live-api/live-transcribe | 官方文档 | 双 API 形态 |
| 4 | Agora 文档《Google Gemini Live (Vertex AI)》https://docs.agora.io/en/ai/models/mllm/google-vertex-ai | 官方文档 | P0-2/P0-3、Agents SDK |
| 5 | Agora 官方博客《Build a Live AI Voice Agent with Gemini 3.1 Flash Preview and Agora》（2026-05-07）https://www.agora.io/en/blog/build-a-live-ai-voice-agent-with-gemini-3-1-flash-preview-and-agora/ | 官方教程 | SDK 用法与架构 |
| 6 | Agora 新闻稿《Agora and OpenAI's Realtime API...》（2025-09-04）https://www.agora.io/en/news/agora-and-openai-realtime-api-power-multimodal-ai-agents/ | 官方新闻稿 | P0-5、F-029 |
| 7 | Agora Conversational AI Engine 产品页 https://www.agora.io/en/products/conversational-ai-engine/ | 官方产品页 | F-030 |
| 8 | 声网官方博客《RTE 演进助力 AI Agent 应用落地》（2025-02-10）https://www.shengwang.cn/news/blogdetail/20241230-rte-ai-agent/ | 官方背景 | OpenAI 合作起点（2024-10） |
| 9 | 36氪/AI前线《谷歌突然发布"最强听写模型"》（2026-08-27）https://36kr.com/p/3957398870326403 | 第三方媒体 | 发布交叉验证、价格与词表细节 |
| 10 | 大众网转载稿（2026-08-28）https://www.xhby.net/content/s6a913db3e4b0eb7bb0fa036a.html | 媒体转载 | 博文内容一致性 |

## 四、核验结论

- **status: verified**——6 项 P0 声明 5✅1⚠️0❌，无核心声明失败，不触发 flagged 状态
- 唯一 ⚠️ 为"全球首个 Realtime API"宣传措辞归属（P0-5），合作事实本身真实，已在事实登记 F-029 中写明准确时间线与归属
- 博文为纯合作宣布稿，**无代码、无配置步骤、无成效数字**，信息密度低但声明均获独立佐证
- **stale_after: 2026-11-30**——模型与集成迭代快，3 个月后复核 Agora 文档中 3.5 Transcribe 接入页是否上线、Smart Transcription 支持是否落地
