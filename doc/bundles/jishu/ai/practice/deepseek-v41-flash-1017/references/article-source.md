---
okf_version: "0.2"
type: reference
title: 博文原文事实清单（DeepSeek V4.1-Flash-1017 发布）
description: 微信公众号「赛博禅心」博文《DeepSeek V4.1 Flash 新版发布》事实采集与外部核验登记，F-001 至 F-068，含 P0 核验结果与观点分层
tags: [deepseek, v4.1-flash, model-release, search-api, fetch-api, wishful-programming, pareto, token-cost]
generated:
  by: workbuddy-seven-concepts-cmd
  at: "2026-10-20T13:50:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-20T14:30:00+08:00"
status: stable
stale_after: 2027-04-20
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/7vCZt_lPc5x7EqQAqBTrQQ
  - id: official-announcement
    url: http://mp.weixin.qq.com/s?__biz=MzI1OTU5ODUyNA==&mid=2247484168&idx=1&sn=058bdfe4afce8ab1a6e4f00efd5b8f2d
  - id: api-pricing
    url: https://api-docs.deepseek.com/zh-cn/quick_start/pricing
  - id: hf-model-card
    url: https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017
  - id: modelscope
    url: https://modelscope.cn/models/deepseek-ai/DeepSeek-V4.1-Flash-1017
  - id: qq-news
    url: https://news.qq.com/rain/a/20261017A09MZN00
  - id: explainx
    url: https://explainx.ai/blog/deepseek-v4-1-flash-1017-open-weights-mit-terminal-bench-4-42-benchmarks-pricing-2026
---

# 博文原文事实清单

> **信源**：微信公众号文章《DeepSeek V4.1 Flash 新版发布：api 自带搜索能力》
> **公众号/作者**：赛博禅心 / 金色传说大聪明（标注原创，IP 属地北京）
> **推文链接**：https://mp.weixin.qq.com/s/7vCZt_lPc5x7EqQAqBTrQQ
> **发布时间**：2026-10-17 16:32
> **采集时间**：2026-10-20（WebFetch 提取全文，正文约 1900 字，含两张官方图表转录）
> **信源距离**：第三方转述（对 DeepSeek 官方公告的中文编译 + 作者评点），非厂商自宣、非作者一手实测
> **核验方式**：P0 声明逐项回到 DeepSeek 官方公告、API 文档定价页、HuggingFace 模型卡（经搜索快照）与多家媒体报道交叉比对，详见 [verification.md](verification.md)

---

## 完整 F 编号清单（F-001 至 F-068，连续无跳号）

### A. 元信息与信源距离

| F 编号 | 声明摘要 | P 级 | 核验结果 |
|--------|---------|------|---------|
| F-001 | 目标文章标题《DeepSeek V4.1 Flash 新版发布：api 自带搜索能力》，公众号「赛博禅心」，署名金色传说大聪明，原创，2026-10-17 16:32 北京发布 | — | ✅ |
| F-002 | DeepSeek 官方公众号「深度求索」2026-10-17 16:11 发布官方公告《DeepSeek V4.1 Flash新版本：许愿式编程一键成真》 | P0 | ✅ 官方一手信源，与博文同日（早 21 分钟） |
| F-003 | 腾讯新闻、澎湃新闻、央视财经、四川广播电视台等媒体 2026-10-17 报道同一发布事件 | P1 | ✅ 多源交叉一致 |
| F-004 | 目标文章为官方公告的二手转述 + 作者评点，文中无作者一手实测过程与结果 | P1 | ✅ 信源距离判定依据 |

### B. 发布与开源

| F 编号 | 声明摘要 | P 级 | 核验结果 |
|--------|---------|------|---------|
| F-005 | DeepSeek V4.1 Flash 更新至 V4.1-Flash-1017 版本，官方网页端、App 与 API 模型同步换新 | P0 | ✅ 官方公告原文 |
| F-006 | 模型权重上线 HuggingFace 与魔搭（ModelScope），仓库名 `deepseek-ai/DeepSeek-V4.1-Flash-1017` | P0 | ✅ 官方公告文末参考区给出两平台仓库地址 |
| F-007 | 模型总参数 763B（MoE），MIT 开源协议 | P0 | ✅ HuggingFace 模型卡 "763B params / License: mit"（搜索快照） |
| F-008 | HuggingFace 模型卡元数据：Image-Text-to-Text 类型，Transformers + Safetensors 格式，张量类型 BF16·F32·F8_E4M3·I8 | P1 | ✅ 搜索快照（HF 页面直连被网络策略拦截，以快照+官方公告双源采信） |
| F-009 | 支持图文交错输入；上下文窗口 1M tokens；API 输出长度最大 384K | P0 | ✅ API 文档模型细节表（"上下文长度 1M / 输出长度 最大 384K / 图像理解 支持"） |
| F-010 | 官方推荐参数：temperature 1.0、top_p 1.0、max_tokens 不低于 256K | P0 | ✅ 博文与官方公告一致 |
| F-011 | API 模型名仍为 `deepseek-flash`；旧模型名 `deepseek-v4-flash`、`deepseek-v4-flash-vision-exp` 仍可调用，但对应模型已下线，请求将由 V4.1-Flash-1017 服务并按 Flash 价格计费 | P0 | ✅ API 文档脚注(1)，博文遗漏补全 |
| F-012 | 版本号 1017 对应 2026-10-17 快照命名；发布前数小时有用户在模型列表短暂见到该条目、接口系统指纹发生变化 | P2 | ⚠️ 第三方信源（梁圣降临公众号）单源，仅作背景采信 |

### C. 基准测试纵向对比（V4.1-Flash-1017 vs 上一版，11 项全涨）

| F 编号 | 声明摘要 | P 级 | 核验结果 |
|--------|---------|------|---------|
| F-013 | HLE (w/o tools)：42.6（文本子集 44.0）vs 上一版 36.8（文本子集 39.1），+5.8 | P0 | ✅ 官方公告图表 |
| F-014 | Terminal-Bench 4.0：42.3 vs 31.2，+11.1（11 项中涨幅最大） | P0 | ✅ 官方公告图表 |
| F-015 | DeepSWE v1.1：77.0 vs 74.2，+2.8 | P0 | ✅ 官方公告图表 |
| F-016 | ProgramBench：29.1 vs 20.3，+8.8 | P0 | ✅ 官方公告图表 |
| F-017 | NL2Repo-Bench：68.2 vs 65.4，+2.8 | P0 | ✅ 官方公告图表 |
| F-018 | Automation-Bench V1.0.6：60.5 vs 54.8，+5.7 | P0 | ✅ 官方公告图表 |
| F-019 | Agents' Last Exam：35.4 vs 31.8，+3.6 | P0 | ✅ 官方公告图表 |
| F-020 | Apex Bench v1.1：72.1 vs 64.6，+7.5 | P0 | ✅ 官方公告图表 |
| F-021 | Chartography (w/ tools)：83.0 vs 78.9，+4.1 | P0 | ✅ 官方公告图表 |
| F-022 | BabyVision (w/ tools)：92.5 vs 89.6，+2.9 | P0 | ✅ 官方公告图表 |
| F-023 | ZeroBench-main (w/ tools)：51.0 vs 49.0，+2.0（Pass@5 评测口径） | P0 | ✅ 官方公告图表 |
| F-024 | 测试框架口径：Terminal-Bench 4.0 使用 Claude Code 框架、DeepSWE 使用 Mini-SWE-V2 框架、ZeroBench-main 使用 Pass@5 评测 | P0 | ✅ 官方公告脚注 |
| F-025 | 表中全部跑分为 DeepSeek 自报；发布时点未见独立第三方复现 | P1 | ⚠️ explainx 核验说明；bundle 正文按厂商自报口径标注 |

### D. 横向对比（vs Kimi K3 / GLM 5.3 / GPT-5.6 Sol / Claude Opus 5）

| F 编号 | 声明摘要 | P 级 | 核验结果 |
|--------|---------|------|---------|
| F-026 | DeepSWE v1.1：77.0 vs Claude Opus 5 74.0、GPT-5.6 Sol 73.0、Kimi K3 67.5、GLM 5.3 66.9（1017 版最高） | P0 | ✅ 官方公告图表 |
| F-027 | Automation-Bench V1.0.6：60.5 vs Opus 5 50.3、GPT-5.6 Sol 45.8、GLM 5.3 48.8、Kimi K3 46.7（1017 版最高） | P0 | ✅ 官方公告图表 |
| F-028 | Agents' Last Exam：35.4 为对照六模型最高（Opus 5 28.6、GLM 5.3 28.5、Kimi K3 27.6、GPT-5.6 Sol 26.7） | P0 | ✅ 官方公告图表 |
| F-029 | Apex Bench v1.1：72.1 vs Opus 5 65.8、GPT-5.6 Sol 54.3、GLM 5.3 56.6、Kimi K3 47.8（1017 版最高） | P0 | ✅ 官方公告图表 |
| F-030 | HLE (w/o tools)：42.6 vs Opus 5 56.3、GPT-5.6 Sol 44.5、Kimi K3 43.5、GLM 5.3 42.0*（*为文本子集口径） | P0 | ✅ 官方公告图表 |
| F-031 | Terminal-Bench 4.0：42.3 vs Opus 5 51.8、GPT-5.6 Sol 39.9、GLM 5.3 37.9、Kimi K3 12.6 | P0 | ✅ 官方公告图表 |
| F-032 | NL2Repo-Bench 68.2 vs Opus 5 75.3；ProgramBench 29.1 vs Opus 5 37.0；Chartography 83.0 vs Opus 5 84.0；BabyVision 92.5 vs Opus 5 94.1；ZeroBench-main 51.0 vs GPT-5.6 Sol 53.0 | P0 | ✅ 官方公告图表 |

### E. 单任务成本（DeepSWE v1.1，mini-swe-v2 框架，官方图表口径）

| F 编号 | 声明摘要 | P 级 | 核验结果 |
|--------|---------|------|---------|
| F-033 | 1017 max 档：通过率 77.0%，每任务约 ¥1.3 | P0 | ✅ 博文与官方"性能-费用帕累托图"一致 |
| F-034 | 1017 low 档：通过率 72.6%，每任务约 ¥0.75（博文表述"一个任务不到 8 毛钱"） | P0 | ✅ 官方三档口径（第三方转录文章明确 low 约 ¥0.75） |
| F-035 | 1017 high 档：通过率 73.0%，每任务约 ¥1.0 | P1 | ⚠️ 官方图表读取的近似值（第三方转录文章口径） |
| F-036 | 上一版 max 档：通过率 74.2%，每任务约 ¥3.3 | P0 | ✅ 博文与官方图表一致 |
| F-037 | Claude Opus 5 max 档：通过率 73.7%，每任务约 ¥79（博文表述"将近 80 元"） | P0 | ✅ 官方图表（约数） |
| F-038 | 官方对本次更新的定性：「性能—费用的帕累托改进」 | P0 | ✅ 官方公告小标题 |
| F-039 | 官方口径：新模型跑同样任务用时更短、输出也更短 | P0 | ✅ 博文转述官方公告 |
| F-040 | 官方图表另列对照模型（通过率/每任务费用）：GPT-6 Luna 66.6%/约¥1.5、GLM-5.3 Flash 63.5%/约¥1.6、V4 Flash 53.5%/约¥3.1、GPT-6.1 Sol 75.2%/约¥4.3、Gemini 3.8 Flash 73.8%/约¥16、GPT-6 Sol 68.9%/约¥18、GLM-5.3 69.1%/约¥27、GPT-6 Astra 74.1%/约¥30、Kimi K3 68.6%/约¥31、Claude Fable 5 70.0%/约¥90；美元按 1USD=6.6862CNY 折算 | P1 | ⚠️ 均为官方图表读取近似值（第三方转录文章口径） |

### F. API 定价（官方 API 文档核验，博文未含）

| F 编号 | 声明摘要 | P 级 | 核验结果 |
|--------|---------|------|---------|
| F-041 | `deepseek-flash`：上下文长度 1M，输出长度最大 384K；思考模式支持非思考与思考模式（默认思考） | P0 | ✅ API 文档模型细节表 |
| F-042 | 输入（缓存命中）：空闲时段 ¥0.02/百万 tokens，高峰时段 ¥0.04 | P0 | ✅ API 文档价格表 |
| F-043 | 输入（缓存未命中）：空闲时段 ¥1/百万 tokens，高峰时段 ¥2 | P0 | ✅ API 文档价格表 |
| F-044 | 输出：空闲时段 ¥4/百万 tokens，高峰时段 ¥8 | P0 | ✅ API 文档价格表 |
| F-045 | 空闲时段价格为高峰时段一半；高峰时段为北京时间周一至周五（不含中国法定节假日）9:00-12:00、14:00-18:00；其余时段（含周末全天）为空闲时段 | P0 | ✅ API 文档脚注(2) |
| F-046 | `deepseek-flash` 并发限制 2500；FIM 补全仅非思考模式支持；图像理解支持 | P1 | ✅ API 文档模型细节表 |
| F-047 | 第三方文章 explainx 所称 "$0.15/$0.60 per million tokens" 与官方人民币定价页不一致，本 bundle 不采信 | P2 | ❌ 第三方口径与官方冲突，以官方页为准 |

### G. 平台适配与活动

| F 编号 | 声明摘要 | P 级 | 核验结果 |
|--------|---------|------|---------|
| F-048 | 本次更新着重针对 DeepSeek Harness、腾讯 CodeBuddy、WorkBuddy 等平台框架进行优化 | P0 | ✅ 官方公告原文 |
| F-049 | 需升级 DeepSeek Harness 至 0.2.1-rc.1 及以上版本以获得适配新版模型的最优体验；官方同步发布 DeepSeek Harness 0.2.1 | P0 | ✅ 官方公告 + 博文一致 |
| F-050 | 符合活动条件的用户首次登录 DeepSeek Harness 可获得 6 元赠金，无需充值，限量发放，到账后 7 天内有效 | P0 | ✅ 博文与官方公告一致 |

### H. 许愿式编程

| F 编号 | 声明摘要 | P 级 | 核验结果 |
|--------|---------|------|---------|
| F-051 | 官方将新能力称为「许愿式编程一键成真」：用更少的提示词、更少的参考素材，在 DeepSeek Harness 里交互几轮，模型从零搭出完整项目 | P0 | ✅ 官方公告标题与正文 |
| F-052 | 训练方法为基于自反馈的强化学习（RL）：模型对产出自我评估、自行修正 | P0 | ✅ 官方公告 + 博文一致 |
| F-053 | 能力提升方向为游戏开发、3D 建模这类从零搭建完整项目的能力 | P0 | ✅ 官方公告 |
| F-054 | 官方 demo 四个：可实时浏览的 3D 故宫、网页版赛车游戏、基于开源游戏引擎 Godot 复刻的《传送门 2》、Valley of Ages（同一片 3D 河谷从史前时代演化到现代） | P0 | ✅ 官方公告 + 博文一致 |
| F-055 | [解读] demo 的含金量在于多文件工程结构、资源管理与可运行性，传统"补全式"模型难以一次给全 | P2 | 第三方解读（梁圣降临公众号），观点分层 |

### I. 自研搜索 API 开放

| F 编号 | 声明摘要 | P 级 | 核验结果 |
|--------|---------|------|---------|
| F-056 | DeepSeek 网页端和 API 的联网搜索一直由自家搜索引擎驱动，每天处理来自全球的数亿次请求 | P0 | ✅ 博文与官方公告一致 |
| F-057 | 自研搜索为 AI 原生的通用搜索引擎：索引全球千亿级网页、支持多语言、实时返回结果 | P0 | ✅ 官方公告 |
| F-058 | 对 SEO 作弊、GEO 操纵（专门让 AI 在回答里引用自家内容的优化）和低质量 AI 生成内容，有识别与过滤机制 | P0 | ✅ 官方公告 |
| F-059 | DeepSeek API 新增 Search（搜索）与 Fetch（抓取网页）两个独立接口，价格均为每 1,000 次成功请求 5 元 | P0 | ✅ API 文档「网页搜索与抓取价格」表 |
| F-060 | 接口用法写在 DeepSeek API 文档「网页搜索与抓取」指南中 | P0 | ✅ 博文与 API 文档一致 |
| F-061 | 在 DeepSeek Harness、Claude Code 或 Codex 中接入 DeepSeek API 时，Server 端工具调用已自动访问 Search/Fetch，这部分调用当前未计费 | P0 | ✅ API 文档定价页 Note |
| F-062 | 上述工具内 Search/Fetch 调用将自北京时间 2026-11-01 00:00 起按次收取费用 | P0 | ✅ API 文档定价页 Note |
| F-063 | 扣费规则：Search/Fetch 按成功请求次数计费；失败、无结果或超时不收费；充值余额与赠送余额同时存在时优先扣减赠送余额 | P1 | ✅ API 文档（扣费规则）；⚠️ 失败不计费一条为第三方信源补充 |
| F-064 | [观点] 这是国内头部模型厂商第一次把自研搜索能力作为独立计费 API 开放，对标 Perplexity、OpenAI 的搜索接口体系 | P2 | 第三方观点（梁圣降临公众号），观点分层 |

### J. 观点与解读层（不入正文事实）

| F 编号 | 声明摘要 | P 级 | 核验结果 |
|--------|---------|------|---------|
| F-065 | [作者观点] 博文以「斩杀线」比喻 1017 版与 Opus 5 的成本对比 | P2 | 修辞分层 |
| F-066 | [作者观点] 博文以「V 社至今还没数到 3」玩梗 Godot 复刻《传送门 2》 | P2 | 修辞分层 |
| F-067 | [解读] Agent 任务的账单大头为输出 token 总量 × 循环轮数；模型输出变短比单价下降更能降低单任务成本 | P2 | 基于 F-033/F-036/F-039/F-043/F-044 的归纳，非官方原文 |
| F-068 | [解读] 大多数任务不需要开满推理档位：low 与 max 通过率相差 4.4 个百分点、每任务成本相差约 40%（¥0.75 vs ¥1.3） | P2 | 基于 F-033/F-034 的归纳 |

---

## 登记说明

- 本表为 R 阶段事实采集产物，按 G1 质量门标准登记：纯客观陈述、无因果推断词；解读与观点以 [解读]/[观点] 标注并集中在 J 区，不混入事实区。
- 标注【核验补充】性质的条目（F-011/F-041~F-047/F-063）为博文未含、由官方权威信源补充的事实。
- 完整勘误与核验过程见 [verification.md](verification.md)。
