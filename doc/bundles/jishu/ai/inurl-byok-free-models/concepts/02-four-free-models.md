---
okf_version: "0.2"
type: concept
title: 四个免费模型资源核验（Agnes / GLM-4-Flash / 硅基流动 / LongCat）
description: 博文推荐的 4 个免费模型逐一对照官方口径：免费性质、上下文、额度领取前提与限速，数据时点 2026-09-16（F-017 至 F-020、F-030 至 F-035）
tags: [免费模型, agnes, glm-4-flash, siliconflow, longcat, openai兼容, 额度核验]
generated:
  by: trae-agent
  at: "2026-09-16T20:30:00+08:00"
sources:
  - id: weixin-blog
    url: https://mp.weixin.qq.com/s/xbpFUmp2s87BUbcFagwQ0A
  - id: agnes-wiki
    url: https://wiki.agnes-ai.com/zh-Hans/docs/agnes-25-flash
  - id: agnes-pr
    url: https://www.prnewswire.com/apac/news-releases/sapiensai-launches-agnes--singapores-homegrown-answer-to-deepseek-302443885.html
  - id: zhipu-glm4
    url: https://docs.bigmodel.cn/cn/guide/models/text/glm-4
  - id: siliconflow-news
    url: https://siliconflow.cn/news/od7wj9rr23p95uhihmhrombp
  - id: longcat-docs
    url: https://longcat.chat/platform/docs/zh/
  - id: meituan-longcat2
    url: https://tech.meituan.com/2026/06/30/LongCat2.0.html
---

# 四个免费模型资源核验

> **数据时点：2026-09-16**（博文发布 2026-09-04 后第 12 天）。免费额度是厂商可随时调整的阶段性政策，以下口径以各平台官方页面为准；博文给出的 4 条 `inurl.link/<x>` 均为导流短链，领取请走各平台官方域名。

## 总览：博文口径 vs 官方口径

| 模型 | 博文标签 | 实际免费性质（2026-09-16） | 上下文 | 博文错误/省略 |
|------|---------|---------------------------|--------|--------------|
| Agnes AI `agnes-2.5-flash` | 美国·完全免费 | 阶段性 $0 优惠 + 免费层限速 | **512K**（非百万） | ❌ 国籍错（新加坡）；❌ 上下文错；⚠️ 免费有条件 |
| 智谱 `GLM-4-Flash` | 完全免费 | **长期免费（¥0）** | 128K | ✅ 属实（博文未提并发限制） |
| 硅基流动免费通道 | 注册送额度 | 免费小模型全员 0 元 + 实名 ¥16 券 | 因模型而异 | ⚠️ 免费的是 9B 级开源模型，非满血 |
| 美团 `LongCat` | 注册送额度 | 实名领 1000 万 Tokens（30 天） | LongCat-2.0 1M | ⚠️ 漏实名/30 天/限时三前提；万亿与 1M 仅属 2.0 |

四家均提供 OpenAI 兼容接口（F-017~F-020 的"OpenAI 兼容"一项全部属实）。

## 1. Agnes AI —— agnes-2.5-flash

**博文口径（F-017）**：美国 · 完全免费 · Sapiens AI 出品的全模态免费网关；agnes-2.5-flash 支持百万级上下文；注册即送 Key。

**官方口径（F-030~F-032）**：

| 维度 | 核验值 |
|------|--------|
| 运营主体 | **新加坡** Sapiens Technology Pte. Ltd.（非美国；PRNewswire 2025-05-01 新闻稿、App Store 上架主体、Tech in Asia 报道三源一致），创始人 Bruce Yang（NUS 博士生） |
| 产品形态 | 全模态（文本/图像/视频/Agent）网关，OpenAI 兼容（另有 Responses、Anthropic Messages 兼容），端点 `apihub.agnes-ai.com/v1` |
| 模型 | `agnes-2.5-flash` 真实在线（2026-07-13 全量上线）；旧 `agnes-2.0-flash` 已废弃 |
| 上下文 | **512K，最大输出 65.5K**——博文"百万级"错误；1M 是已废弃 2.0-flash 的临时窗口（2026-06 已回退 256K） |
| 免费政策 | 2.5-flash 当前 **$0**，但官方明示"阶段性优惠，结束时间以平台公告为准"；刊例价输入 $0.05 / 输出 $0.15 每百万 token |
| 限速 | 免费用户文本名义 30 RPM、**实际约 20 RPM**（第三方 2026-09 百供应商压测：20 RPM / 1,000 RPD） |
| 付费并存 | Token Plan 订阅（Starter/Plus/Pro）、`agnes-2.5-pro` 收费（$0.45/$0.90）、视频按秒计费 |

**结论**：模型与免费注册可用属实，但"美国/百万上下文/完全免费"三处营销拔高均不成立。长文档场景按 **512K** 规划。本库 [`../../agnes-ai/agnes-ai-models/index.md`](../../agnes-ai/agnes-ai-models/index.md) 对该模型族有完整 API 教程（同样标注 512K）可交叉阅读。

## 2. 智谱 GLM-4-Flash —— 四者中唯一的长期 $0 模型

**博文口径（F-018）**：中国 · 完全免费 · OpenAI 兼容；按量计费 ¥0；中文理解强。

**官方口径（F-033）**：

| 维度 | 核验值 |
|------|--------|
| 型号 | `GLM-4-Flash-250414`（2024-08 首发的免费档），**当前仍在线、价格栏为空（¥0）**，未下架 |
| 上下文 | 128K，最大输出 16K |
| 限速 | 只按**在途并发数**限制（官方不公布 QPS/RPM）：零消费 V0 用户 **200 并发**，V1/V2/V3 为 1000/2000/3000 |
| 接入 | 官方 OpenAI 兼容端点 `https://open.bigmodel.cn/api/paas/v4/` |
| 易混淆型号 | **GLM-4.5-Flash 已于 2026-01-30 下线**，请求自动路由至 GLM-4.7-Flash（2026-01-20 发布、200K、官方宣布免费）；GLM-4.6V-Flash 为视觉免费型号 |

**结论**：✅ 博文声明属实，是四者中免费承诺最"硬"的一家（型号持续在线一年以上、官方长期标注免费版）。注意免费的是 2024 年的 GLM-4 代架构，新型号走各自定价/免费政策。

## 3. 硅基流动免费通道 —— 全员可用的免费小模型 + 实名代金券

**博文口径（F-019）**：新老用户都有免费 Token 额度，可零成本体验 Qwen、DeepSeek、GLM 等开源模型。

**官方口径（F-034）**：

| 维度 | 核验值 |
|------|--------|
| 免费模型 | 实名认证后，**免费模型对所有用户（含老用户）长期 0 元**，账单消耗为 0；收费版以 `Pro/` 前缀区分 |
| 免费型号 | **9B 级及以下开源小模型**，如 Qwen3-8B、DeepSeek-R1-Distill-Qwen-7B（约 30 RPM / 60K TPM）、glm-4-9b-chat 等；完整实时名单以登录后模型广场为准 |
| 关键澄清 | 平台**没有 GLM-4-Flash 这个型号 ID**；DeepSeek 满血 R1/V3（Pro/高速版）**付费**，免费的是 7B 蒸馏版——博文"体验 DeepSeek/GLM"措辞容易被读成满血版 |
| 注册激励（2026 现行） | 完成实名认证后在活动中心**手动领取 ¥16（国际站 $1）通用代金券**，**180 天有效**，活动至 2026-12-31；网上流传的"¥14/2000 万 token"是 2025 年初旧政 |
| 接入 | OpenAI 兼容 `https://api.siliconflow.cn/v1` |

**结论**：✅"新老用户都有免费额度"在"免费小模型 0 元"意义上成立；⚠️ 读者须明确这里免费的是**开源小模型**，适合学习与轻量任务，不等同于厂商旗舰能力。

## 4. 美团 LongCat —— 1000 万 Tokens 的三个省略前提

**博文口径（F-020）**：美团自研万亿参数 MoE；新用户注册送 1000 万 Tokens；原生 1M 上下文；OpenAI 兼容。

**官方口径（F-035）**：

| 维度 | 核验值 |
|------|--------|
| 当前在售模型 | **LongCat-2.0**（2026-06-30 发布），平台仅售此代；Flash 系列 6 个老模型 2026-05-29 已停调 |
| 参数 | LongCat-2.0 **总参数 1.6T（万亿）**、每 token 平均激活约 **48B**（动态 33B–56B，零计算专家+ScMoE）；上一代 Flash 为 560B 总参——"万亿"指总参而非实际推理算力 |
| 上下文 | LongCat-2.0 基于 LSA 稀疏注意力**正式支持 1M**，单次最大输出 128K；Flash-Chat 仅 128K |
| 1000 万 Tokens | 出自美团官网发布活动海报，但有三个博文省略的前提：**①完成实名认证后领取（非注册自动到账）；②30 天有效；③限时活动，规则以活动页公示为准**（另有 ¥9.9/5000 万、¥399/10 亿付费包；Cache 命中不计入） |
| 接入 | OpenAI 兼容 `https://api.longcat.chat/openai`，另提供 Anthropic 格式端点 |
| 限速 | 官方确认有限流（429 + retry_after），**未公开 RPM/TPM 数值** |

**结论**：⚠️ 三个数字都有官方出处，但"注册送"表述不准确（实名领取 + 30 天 + 限时）；"万亿/1M"是 LongCat-2.0 专属能力，不代表整个系列。是否仍能领取需登录活动页确认。

## 5. 选用建议（基于核验事实，非投资/采购建议）

- **要长期稳定的免费中文文本接口**：GLM-4-Flash（¥0 承诺最久、200 并发），接受其为 2024 代模型能力。
- **要超大窗口**：Agnes 2.5-flash 按 512K 规划（非博文所称 1M）；LongCat-2.0 确为 1M 但额度仅 30 天。
- **要免费体验开源小模型/做学习实验**：硅基流动免费档（全员 0 元，型号随广场更新）。
- **额度到账后先做两件事**：核对官方活动页的有效期与领取条件；给 Key 设置消费限额——这也正是把多厂 Key 交给任何聚合工具（包括博文推荐的 inurl）之前的底线动作，产品侧风险见 [00-byok-token-landscape.md](00-byok-token-landscape.md)。

## 本篇事实索引

F-017~F-020（博文模型声明）、F-030~F-035（Agnes/智谱/硅基/美团官方核验）；逐项信源 URL 与残留不确定性见 [../references/verification.md](../references/verification.md)。
