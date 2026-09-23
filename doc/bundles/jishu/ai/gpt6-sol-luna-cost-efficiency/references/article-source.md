---
type: Reference
title: "GPT-6 Sol 与 GPT-6 Luna 博文事实清单"
description: "登记原文事实、厂商声明、第三方实测和作者判断，并记录官方核验状态。"
tags: [gpt-6, openai, deepseek, source-register]
generated: { by: "reference_agent/trae", at: "2026-09-23T12:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-09-23T12:00:00+08:00" }
status: stable
stale_after: "2026-12-31"
sources:
  - id: blog
    resource: https://mp.weixin.qq.com/s/1190GW6WFZIzZ8YkDD44eg?from=industrynews&color_scheme=light#rd
    title: "刚刚，GPT-6 新模型掀桌！「白菜价」杀进 DeepSeek 腹地"
  - id: openai
    resource: https://openai.com/index/introducing-gpt-6-sol-and-luna/
  - id: deepseek
    resource: https://api-docs.deepseek.com/quick_start/pricing
---

# GPT-6 Sol 与 GPT-6 Luna 博文事实清单

| 编号 | 事实或声明 | 来源层级 | 核验 |
|---|---|---|---|
| F-001 | 文章标题为《刚刚，GPT-6 新模型掀桌！「白菜价」杀进 DeepSeek 腹地》。 | 博文元信息 | 单源 |
| F-002 | 文章署名“发现明日产品的”，发布日期为 2026-09-23。 | 博文元信息 | 单源 |
| F-003 | OpenAI 发布 GPT-6 Sol 与 GPT-6 Luna。 | 官方发布 | 通过 |
| F-004 | GPT-6 Sol API 输入/输出价格为 `$2/$10` 每百万 token。 | 官方发布 | 通过 |
| F-005 | GPT-6 Luna API 输入/输出价格为 `$0.10/$0.50` 每百万 token。 | 官方发布 | 通过 |
| F-006 | 两款模型相较对应 GPT-5.6 促销价约低 50%。 | 官方发布 | 通过 |
| F-007 | Sol 面向专业工作，Luna 面向高吞吐和成本敏感工作。 | 官方发布 | 通过 |
| F-008 | 两款模型吸收 Astra 在专业工作、事实性、编程、计算机操作和对齐方面的训练进展。 | 官方发布 | 通过 |
| F-009 | 文章使用 DeepSeek V4.1 Flash 做价格对照，并讨论缓存与峰谷价格。 | 博文 + 官方 DeepSeek | 需按官方价表解释 |
| F-010 | DeepSeek V4.1-Flash 官方 API 名称为 `deepseek-flash`，上下文长度为 1M。 | 官方 DeepSeek | 通过 |
| F-011 | DeepSeek 官方价格按缓存命中/未命中、输入/输出和峰谷时段区分。 | 官方 DeepSeek | 通过 |
| F-012 | 文章提出 Agent 应以每任务成本而非 token 单价衡量经济性。 | 官方/作者观点 | 方法论观点 |
| F-013 | 文章引用多个 Agent、编程和电脑操作 benchmark。 | 博文转述 | 厂商自述为主 |
| F-014 | 文章给出 Sol 在多个 benchmark 上的分数。 | 厂商自述 | 未独立复算 |
| F-015 | 文章给出 Luna 在 DeepSWE 等测试上的分数。 | 厂商自述 | 未独立复算 |
| F-016 | 文章给出 Sol/Luna 相比 Claude 的任务成本下降比例。 | 厂商自述 | 未独立复算 |
| F-017 | 文章转述 Sol 内部真实对话测试错误约减半。 | 厂商内部测试 | 仅厂商自述 |
| F-018 | 文章转述编程 Agent 研究人员 token 日耗成本统计。 | 厂商内部统计 | 仅厂商自述 |
| F-019 | GPT-6 缓存读取宣称可获得 90% 折扣。 | 官方发布 | 通过机制，效果依负载 |
| F-020 | 文章转述中途调整推理强度/工具并复用缓存、显式断点等能力。 | 官方发布/文档 | 以当前文档为准 |
| F-021 | 文章转述 ChatGPT Work、Codex、桌面应用的分层开放范围。 | 官方发布 | 随滚动开放变化 |
| F-022 | API 模型名为 `gpt-6-sol` 与 `gpt-6-luna`。 | 官方发布 | 通过 |
| F-023 | 作者认为价格接近后，入口、工具、稳定性和生态会影响选择。 | 作者观点 | 方法论观点 |
| F-024 | 文章包含 Three.js 游戏、纽约场景等实测或第三方评价。 | 第三方/作者实测 | 不等同基准 |
| F-025 | 文章转述 Artificial Analysis 对智能水平与成本的观察。 | 第三方分析转述 | 需查原始报告 |
