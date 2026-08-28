---
type: Reference
title: 核验报告
description: 2026-08-28 对博文三项关键声明的官方来源核验结论、细节差异说明（豆包阶梯定价、音频输入差异）与未核验声明清单
tags: [核验报告, 信源核验, 官方文档]
generated: { by: "seven-concepts-cmd", at: "2026-08-28T23:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-28T23:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: deepseek-official-news-260821
    resource: https://api-docs.deepseek.com/news/news260821/
    title: DeepSeek-V4-Flash-Vision-Exp 官方发布新闻
  - id: wechat-article-hubei
    resource: https://mp.weixin.qq.com/s/iqoikK7m7arGSHnso-q9hQ
    title: 《DeepSeek 多模态视觉实验模型发布！》
---

# 核验报告

**核验日期**：2026-08-28（轻量核验，Task 1.2）

**总结论**：三项关键声明全部核验通过，博文与官方发布日期同步（均为 2026-08-21），未发现编造或过时信息。

## 核验结论一：DeepSeek-V4-Flash-Vision-Exp ✅ 通过

**官方来源**：[https://api-docs.deepseek.com/news/news260821/](https://api-docs.deepseek.com/news/news260821/) （DeepSeek 官方发布新闻）

| 博文声明 | 核验结果 | 事实编号 |
|---------|---------|---------|
| DeepSeek 发布原生视觉模型，型号为 DeepSeek-V4-Flash-Vision-Exp | ✅ 官方 2026-08-21 发布 | F-002 |
| 图片输入方式：Base64、图片链接和 Files API 文件 | ✅ 三方式均确认 | F-006 |
| 图片格式：JPEG、PNG、GIF、WebP | ✅ 四格式均确认 | F-005 |
| 未同步开放模型权重 | ✅ 确认 | F-008 |

**官方补充细节**（博文未提及，登记为核验补充事实）：

- 单图最多折算 384 tokens，按 V4-Flash 费率计费（F-034）；
- 多模态 Agent 性能接近 Claude Opus-4.8（核验记录原文，未分配事实编号）。

## 核验结论二：GLM-4.6V-Flash 免费 + FlashX 定价 ✅ 通过

**官方来源**：智谱官方文档（[https://docs.bigmodel.cn](https://docs.bigmodel.cn)）、z.ai 定价页（域名级引用，完整 URL 未在核验记录中登记）

| 博文声明 | 核验结果 | 事实编号 |
|---------|---------|---------|
| GLM-4.6V-Flash 目前官方价格为免费 | ✅ 智谱官方文档确认免费版本 | F-010 |
| FlashX 价格：输入 $0.04、输出 $0.40／百万 tokens | ✅ z.ai 定价页确认，与博文完全一致 | F-013 |

无细节差异。

## 核验结论三：Doubao-Seed-2.0-mini ✅ 通过（含细节差异）

**官方来源**：火山引擎官方价格文档（核验记录未登记完整 URL）

| 博文声明 | 核验结果 | 事实编号 |
|---------|---------|---------|
| 支持图像、视频、音频和文本 | ✅ 火山引擎确认四模态 | F-014 |
| 价格：输入 ¥0.2、输出 ¥2／百万 tokens 起 | ✅ 起步价口径成立（细节见下） | F-015 |

**细节差异说明**：

1. **阶梯定价**：¥0.2/¥2 为 ≤32K 输入档起步价，阶梯定价至 0.8/8.0。博文"起"字表述与官方口径一致，无冲突。
2. **音频输入差异**：音频输入 3.0 元/百万 tokens 起，博文未区分音频与文本/视觉输入的价格差异，属轻微简化。已登记为 F-036。

## 细节差异汇总

| 差异点 | 博文表述 | 官方口径 | 处理 |
|-------|---------|---------|------|
| 豆包输入价适用范围 | 输入 ¥0.2／百万 tokens 起 | ¥0.2 仅适用于非音频输入且输入长度 ≤32K 档（阶梯定价至 0.8/8.0） | 补充事实 F-036 |
| 豆包音频输入价格 | 未区分 | 音频输入 3.0 元/百万 tokens 起 | 补充事实 F-036 |
| DeepSeek 单图计量 | 未提及 | 单图最多折算 384 tokens，按 V4-Flash 费率计费 | 补充事实 F-034 |

## 未核验声明清单

以下声明仅博文单源，本次核验未覆盖，引用时请注意甄别：

- **Gemini 2.5 Flash-Lite**（F-018 ~ F-020）：模态覆盖、价格、"给 DeepSeek 提供视觉事实不必硬上 Gemini Pro"；
- **GPT-5 nano**（F-021）：价格与适用任务；
- **MiniCPM-V 4.6**（F-022 ~ F-024）：参数规模（约 1.3B）、Ollama 支持、分工模式；
- **DeepSeek-OCR-2 / GLM-OCR**（F-025 ~ F-027）：文档场景优先级与验收建议——其中 DeepSeek-OCR-2 的架构与用法可参考既有知识包 [DeepSeek-OCR-2](../../deepseek-ocr2/index.md)，但博文的选型观点（F-025）仍属单源；
- **F-035**（官方视觉权重 2026 年第三季度发布计划）：来源为第三方信息，属弱信源，即使官方新闻亦未覆盖。

## 核验方法说明

核验采用轻量方式（Task 1.2）：对照各厂商官方发布页 / 文档 / 定价页逐条确认博文关键声明，不改写博文原文；官方补充的细节以 F-034 ~ F-036 追加登记，不与博文事实（F-001 ~ F-033）混排。事实完整清单见 [博文信源事实清单](article-source.md)。
