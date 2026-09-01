# 变更日志

## 2026-08-29 — 初始生成（v1）

### 元信息

| 项 | 值 |
|----|----|
| CMD-LOG session | sc-20260829-blog13-okf |
| 来源博文 | 《Agora 携手 Google Gemini 3.5 Transcribe，共同加速对话式 AI 应用落地》 |
| 博文作者/发布 | 微信公众号"声网"（Agora 官方中文品牌，NASDAQ: API），2026-08-27 17:35 |
| 博文 URL | https://mp.weixin.qq.com/s/sbXT5BPvrj4CcuiyJttcgA |
| 内容性质 | **厂商自宣新闻稿/资讯速报**（第一人称"我们"，约千字，无代码/无步骤/无成效数字） |
| 信源距离 | 厂商自宣（合作与产品声明经 Google 官方、Agora 官方文档/新闻稿、第三方媒体三方佐证） |
| 所属组 | ai/ai-agent（组内第 29 个 bundle） |
| 骨架 | 资讯速报骨架，10 文件，**无 examples/**（操作可复现性两问皆"否"） |
| status | verified（5✅1⚠️0❌，不触发 flagged） |
| stale_after | 2026-11-30 |

### R→I→E→V 链路

- **R 阶段**：browser_use 采集博文全文与元信息（标题/公众号/发布时间）；WebSearch 4 轮核验（Gemini 3.5 Transcribe 官方信息、Agora×Gemini 合作、Agora×OpenAI Realtime API 时间线、Agora SDK 与产品页）
- **I 阶段**：判定为厂商新闻稿/资讯速报 → 无 examples/；事实登记 F-001~F-024（博文事实，📝 作者观点 7 条：F-007/F-011/F-012/F-015/F-022/F-023/F-024）
- **E 阶段**：生成 10 文件（见下清单）；更新组索引与 bundles 总索引
- **V 阶段**：P0 核验 6 项 = **5✅ 1⚠️ 0❌**；勘误四张清单执行；**V 阶段核验补充事实 F-025~F-032 共 8 条**（模型双 API/模型 ID、WER 与定价、Chirp 3 对比、OpenAI 合作精确时间线、Agora SDK 包名与两架构、SD-RTN™ 规模、媒体转载核对），已登记于 article-source.md 第六节并在事实表"来源"列标注

### 文件清单（10）

- index.md
- concepts/index.md + 00-voice-agent-runtime + 01-gemini-transcribe-model + 02-agora-conversational-ai + 03-smart-transcription-scenarios
- references/index.md + article-source + verification
- log.md

### 事实基数

- F-001~F-032 共 **32 条**，编号连续无跳号
- 博文事实 24 条（📝 作者观点 7 条）；V 阶段核验补充 8 条（F-025~F-032）
- 博文无成效数字；模型性能数字均来自 Google 官方引述的 Artificial Analysis 第三方测评

### 关键核验结论

- ✅ P0-1 Gemini 3.5 Transcribe 真实存在：Google 官方博客 2026-08-26 发布，CEO Pichai 在 X 宣布
- ✅ P0-2 Agora×Gemini 合作：Agora 文档已有 Gemini Live (Vertex AI) 集成页（2026-07-30）+ 2026-05-07 官方教程 + 媒体转载
- ✅ P0-3 Agora Agents SDK 真实：Python `agora_agent` / TS `agora-agents` / Go `agora-agents-go`；链式与 MLLM 两种架构
- ✅ P0-4 Smart Transcription 为 Google 已发布能力，博文"计划支持"未来时表述准确
- ⚠️ **P0-5 勘误**："全球首个 Realtime API"措辞归属含糊——Realtime API 为 OpenAI 产品，Agora 是 2024-10 公测首发语音 API 合作方、2025-09-04 GA；准确表述"首发语音合作/集成方"（F-029）
- ✅ P0-6 噪声/专业词汇/口语停顿应对与 Google 官方博客表述一致

### G1-G4 质量门

- **G1 信源门**：厂商自宣预判 → 全部合作/产品声明列 P0 并三方独立佐证；10 个权威信源登记
- **G2 结构门**：10 文件齐备；toctree 三层（index→concepts/references/log）完整；相对链接无 file:///
- **G3 事实门**：32 条 F 编号连续；事实/观点分离（📝 7 条）；V 补充事实单独成节并注记；勘误四张清单执行
- **G4 迁移门**：与前 12 个 bundle（同模式）结构一致；siemens-industrial-agent 资讯速报骨架复用

### 已知限制

1. 博文为千字厂商稿，无代码/配置/实测/成效数字，信息密度低
2. 3.5 Transcribe 在 Agora 侧的专属接入文档尚未公开，集成可用性状态（预览/GA）、定价、SLA 未给出
3. Smart Transcription 的 Agora 侧落地时间未公布
4. Agora 网络规模数字（800亿分钟/月等）为厂商自述
5. stale_after 2026-11-30：届时复核 Agora 3.5 Transcribe 接入页与 Smart Transcription 支持是否落地
