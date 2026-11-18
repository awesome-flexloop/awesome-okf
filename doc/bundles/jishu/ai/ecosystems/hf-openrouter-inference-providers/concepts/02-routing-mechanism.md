---
type: Concept
title: "路由机制与策略后缀：默认不是最便宜"
description: "解释 OpenRouter 默认路由的 Routing Cost 六项实时信号、竞争边与流量分配、故障转移与提示词缓存粘滞，并对照 HF 后缀与 OpenRouter 原生 provider 对象。"
tags: [路由算法, Routing Cost, TTFT, 故障转移, 提示词缓存, provider 排序, 模型后缀]
sources:
  - id: hf-ip-routing
    resource: https://huggingface.co/docs/inference-providers/routing
    title: "Routing and Providers 官方文档"
  - id: or-routing-rebuild
    resource: https://openrouter.ai/blog/announcements/how-we-rebuilt-provider-routing/
    title: "OpenRouter 路由算法重建公告（2026-10-28）"
  - id: or-provider-selection
    resource: https://openrouter.ai/docs/guides/routing/provider-selection
    title: "Provider Routing 官方文档"
  - id: hf-ip-caching
    resource: https://huggingface.co/docs/inference-providers/prompt-caching
    title: "Prompt Caching 官方文档"
---

# 路由机制与策略后缀：默认不是最便宜

## 默认路由在优化什么

HF 官方文档把默认路由描述为「比较每个供应商给出一个好答案的成本」（F-015），OpenRouter 2026-10-28 的算法公告把它命名为 **Routing Cost**：一次尝试的代价 × 需要尝试多少次（F-033）。它由六项基于近期生产流量的实时测量构成：

| 信号 | 含义 | 备注 |
|---|---|---|
| Effective price | 供应商**实际**收的钱，含真实缓存命中率与该模型常见的输入/输出 token 配比 | 不是目录标价；防止用极低输入价 + 极高缓存/输出价「做价格」 |
| Throughput | 端到端每秒输出 token 数 | 含 TTFT 与完整流式输出时间；快供应商可以更贵仍胜出 |
| TTFT | 首 token 延迟 | 单独计权，因为 Agent 场景里连续多次工具调用都在等首 token |
| Rate limits | HTTP 429 的频率 | 加等待时间 + 惩罚，并按发生频率加权 |
| Reliability | 供应商侧失败率 | 某家远高于同模型其他家时，暂停给它流量直到恢复 |
| Quality | 响应是否可用 | 当前主要检查 tool call 是否格式完好，官方称还在增加检查项 |

一句话概括：**默认路由最小化「拿到一个可用答案的期望成本」，不是最小化单价**（F-033、F-034）。旧版路由约 77% 的多供应商模型请求主要按输入 token 标价排序，失败再换次便宜的（F-032）。

## 流量不是赢家通吃

算法公告给了三条护栏（F-034、F-036）：

- **competitive edge**：接近最优的供应商共享大部分流量，按份额随机挑选；落后一点只损失一点，落后过多份额快速衰减；
- **floor**：每家保留一点探测流量，新端点从该模型的典型数值起步，不需要历史流量；
- **back off**：开始失败或限流的供应商逐步降份额，恢复后再升回来。

会话维度和请求维度行为不同：**一段会话只有第一个请求由算法挑供应商，后续请求固定在原供应商**，以保持提示词缓存温度；该供应商不可用时才自动回退；某次尝试失败则按剩余供应商中的排名重试（F-036、F-017）。

## HF 侧的三个后缀

在模型 id 后追加后缀即可改策略，且对只能填「模型名」的工具同样有效（F-014、F-015）：

```text
zai-org/GLM-5.3            # 默认：价格 / 速度 / 可靠性的最佳组合
zai-org/GLM-5.3:fastest    # 最高吞吐
zai-org/GLM-5.3:cheapest   # 最低价格
zai-org/GLM-5.3:novita     # 只用 Novita；不服务该模型则报错
```

要点：`:<provider>` 是**硬 pin**，官方明确写「永不被替换」（F-017），所以它同时关掉了自动故障转移；在设置里关掉的供应商，用后缀 pin 会返回错误（F-016）。换句话说，确定性换来的是可用性下降，生产环境要显式评估。

## 与 OpenRouter 原生写法对照

OpenRouter 自家 API 用请求体里的 `provider` 对象（F-049）：`order` / `allow_fallbacks` / `only` / `ignore` / `sort`（`price` / `throughput` / `latency`）/ `max_price` / `zdr` / `data_collection` / `quantizations` / `preferred_min_throughput` / `preferred_max_latency` 等。另外有 `:floor`（按价格排序 + 允许 flex service tier 端点）与 `:nitro`（按吞吐排序 + 允许 priority tier 端点）两个 routing variant（F-051）。

**不要交叉套用**：`:fastest` / `:cheapest` 是 HF 路由的后缀；`:floor` / `:nitro` 与 `provider.sort` 是 OpenRouter 的写法。显式 `sort`、`order`、`:floor`、`:nitro` 或自有供应商 key 都会绕过新路由；`only` / `ignore` 过滤后若还剩 ≥2 家，仍由新算法挑选（F-035）。价格上限 `max_price` 是硬约束——没有端点满足时返回 404 `No endpoints found that satisfy the max price for this request`（F-048、F-050）。

## 缓存感知与 `X-HF-Session-Id`

HF 侧缓存自动生效，无需开关；响应 `usage.prompt_tokens_details.cached_tokens` 给出命中数（F-012）。要让多轮对话稳定落在持有缓存的同一供应商，官方文档要求在每个会话传一个**稳定 UUID** 到 `X-HF-Session-Id`，其他取值会被忽略（F-012）。两条配套建议（F-013）：不变的内容（system prompt、tools）放最前，避免在 system prompt 顶部放时间戳或随机 id。

## 效果的代价（务必一起读）

HF 公告只报收益：capacity errors -46%、TTFT +16.9%、throughput +16.3%（F-027）。OpenRouter 同一份实验还给出每千请求成本 $1.25→$1.32（**+6.0%**）、每百万 token $0.301→$0.324（**+7.3%**）（F-038），并在 FAQ 直接承认「会，可能更贵」。因此：

- 成本敏感且能容忍慢一点的场景，显式选 `:cheapest`（或 OpenRouter 侧 `sort: price`）才有价格优先语义；
- 默认路由适合把「可用性与速度」放在单价之前的交互式 / Agent 场景；
- 任何收益数字都应连同实验方法（switchback、2400 万请求、1030 亿 input token、一周）一起引用，见 [C-03](../references/conflicts-and-adversarial-review.md)。
