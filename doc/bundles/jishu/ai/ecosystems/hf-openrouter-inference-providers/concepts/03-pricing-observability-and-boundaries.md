---
type: Concept
title: "定价、可观测性与边界：请求到底去了哪、记在谁账上"
description: "整理无加价计费与月度 credits、模型页 Providers / Metrics 页签、按供应商拆分的用量视图、供应商开关与组织设置覆盖关系，并列出时效与口径边界。"
tags: [计费, credits, 可观测性, provider 开关, 用量拆分, 时效边界]
sources:
  - id: hf-announcement
    resource: https://huggingface.co/blog/openrouter
    title: "Hugging Face × OpenRouter 官方合作公告（2026-11-16）"
  - id: hf-ip-pricing
    resource: https://huggingface.co/docs/inference-providers/pricing
    title: "Pricing and Billing 官方文档"
  - id: hf-ip-routing
    resource: https://huggingface.co/docs/inference-providers/routing
    title: "Routing and Providers 官方文档"
  - id: or-open-vs-closed
    resource: https://openrouter.ai/blog/insights/open-weight-vs-closed-weight-models/
    title: "OpenRouter 开放权重与闭源模型对比（2026-10-31）"
---

# 定价、可观测性与边界：请求到底去了哪、记在谁账上

## 计费口径

公告的定价结论是「不变」：按供应商原价记在 Hugging Face 账单上，**HF 不加价**（F-028）。官方 Pricing 文档补了完整表格（F-028、F-029）：

| 账户类型 | 每月赠送 credits | 可用于 | 超额 |
|---|---|---|---|
| Free | 无 | — | 需先购买 credits，或升级 PRO |
| PRO | $2.00 | 所有 HF 计算服务 | 按量付费 |
| Team / Enterprise | 每席位 $2.00 | 所有 HF 计算服务 | 按量付费 |

赠送的是**通用 compute credits**：除 Inference Providers 外还可用于 Inference Endpoints、Spaces 的 CPU/GPU 升级（含超出配额的 ZeroGPU）、Jobs；每月发放，并在按量计费之前自动抵扣。Team / Enterprise 的额度在成员间共享，但要显式指定计费组织（见 [01 三种 API 协议与鉴权](01-three-protocols-and-auth.md)）。

另有一条容易混淆的历史口径：文档里的 `"hf-inference"` 供应商是旧称 "Inference API (serverless)" 的服务，2025-07 起主要做 CPU 推理（embedding、文本排序/分类、BERT/GPT-2 一类小模型），按「计算时长 × 硬件单价」计费，与按 token 计费的多供应商路由不是同一套账（F-029 附）。

## 三个可观测入口

切换后公告新增/强调了三处「看得见路由」的界面（F-030、F-031）：

1. **模型页 Providers 页签**：列出 OpenRouter 能把该模型路由到的每家供应商，附输入/输出价格、速度、近 24 小时 uptime；
2. **模型页 Metrics 页签**：给出这些供应商里的最优价格、吞吐、TTFT、上下文长度与 uptime；
3. **用量总览**（`settings/inference-providers/overview`）：按模型与供应商拆分花费；官方 Pricing 文档另说明 Enterprise 及以上可用 usage API 拉日粒度时间序列（请求数、成本（分）、输入/输出/缓存输入 token 数，最多延迟 2 小时，成本按行四舍五入到分）。

这三者解决的是同一个问题：**默认路由把「选哪家」变成了系统决策，就必须提供事后归因**。做成本归因时别只看总账，要下钻到供应商维度，才能判断默认路由在你的流量结构上是否合算。

## 供应商开关与组织覆盖

在 Inference Providers 设置里可以逐家关掉不想用的供应商，路由**永不**把请求送过去；用后缀 pin 一个被关掉的供应商会返回错误（F-016）。组织也有同样的开关，且作用于所有记到该组织账单的请求。

覆盖关系值得单独记：一旦请求通过 `X-HF-Bill-To` 记到组织，**采用组织的供应商启停设置而非请求者个人设置**；组织管理员还能设消费上限（F-016、F-029）。所以「我本地关掉了某家」在组织计费场景下不成立——排查路由意外落到某家供应商时，先确认这笔请求记在谁账上。

## 公告引用的市场数据（按口径读）

公告用三组数字说明为什么开放权重值得统一路由（F-023~F-026）：

- 份额：2025-10 26.8% → 2026-09 末 71.7%，7 月峰值 77.5%；同期周 open-weight 量增长 >60 倍，closed 近 10 倍；
- 价格：open-weight 平均 $0.28/M 输入、$1.62/M 输出；closed $1.27 / $6.36；
- 能力：Artificial Analysis Intelligence Index 上，Kimi K3.1 Pro 46 分对 Claude Fable 5.2 65 分，单任务成本 $3.68 对 $26.54。

OpenRouter 自家同期文章给的是另一组（F-042、F-044、F-046）：份额分母为 **top 50 模型的周 token**，排除 "other" 行与 stealth 模型；最佳 open 46.3（MiMo-V2.6-Pro）、最佳 closed 57.6（Claude Opus 5.5），差约 11 分；并明确提醒「按具体模型比，不要按类别比」——GPT-6 Luna 标价 $0.10/M 输入，低于任何 Kimi K3 供应商。

两组数字**不能合并成一句结论**。引用时必须带上「哪份材料、什么分母、哪一天」，详见 [C-01 / C-02](../references/conflicts-and-adversarial-review.md)。

## 消费前的边界清单

1. **时效**：公告自述为合作第一步；模型清单、供应商启停、额度与页签随时点变化，本束截点 2026-11-17，`stale_after: 2027-02-17`。
2. **厂商自述**：路由收益、份额、价格、能力分数均来自 HF / OpenRouter 自己的材料或它们引用的第三方榜单；本束未做独立测量。
3. **未实跑**：三个端点与所有环境变量取自官方文档，本库未用真实 token 运行验证。
4. **不可外推**：图像 / 视频 / 音频链路不在上述计费与页签的同一套描述里（F-004）；组织覆盖、BYOK 限制也只对语言模型成立。
