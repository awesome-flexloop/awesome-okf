---
type: Reference
title: "事实台账 F-001~F-052"
description: "R 阶段客观事实清单，逐条挂信源 id；按公告/接口/规模/路由算法/市场数据五组编号，供概念页与示例页交叉引用。"
tags: [事实台账, G1, 可追溯, 多源分账]
sources:
  - id: source-manifest
    resource: source-manifest.md
    title: "信源清单 S-01~S-14（每条事实的 id 对应表）"
---

# 事实台账 F-001~F-052

> **G1 门约束**：本页只登记可验证的客观陈述，不写因果推断、不写评价、不写本库结论。凡属厂商主张或自测结果，一律用「公告称 / 文档载 / 官方实验测得」显式归因。数字、URL、命令、日期按原文保留。
>
> 信源 id 见 [信源清单](source-manifest.md)；冲突项见 [C-01~C-06](conflicts-and-adversarial-review.md)。**本页不合并冲突口径。**

## A 组｜公告与切换（F-001~F-006）

| 编号 | 事实 | 信源 |
|---|---|---|
| F-001 | Hugging Face 博客文章标题为 "Hugging Face and OpenRouter join forces to make open-weight models easy to run"，页面标注 Published November 16, 2026；frontmatter 列出 7 位作者：celinah、victor、kramp、Wauplin、pierric、coyotte508、julien-c；页面显示 39 个 upvote。 | S-01、S-02 |
| F-002 | 公告称当日把 Inference Providers 从「自研路由」切换到 OpenRouter 路由；语言模型请求经 OpenRouter 按实时价格、速度、可靠性挑选供应商；原文写 "Your code stays the same."。同段写明一个 HF token 同时提供 Storage Buckets、Jobs 与 Inference Endpoints。 | S-01、S-02 |
| F-003 | 公告载：此前 Inference Providers 为请求选定一家供应商并把它的失败返回给调用方；切换后失败请求在同一次调用内于另一家供应商重试。 | S-01、S-04 |
| F-004 | 公告载：图像、视频、音频生成「完全照旧」直接经 Hugging Face Inference Providers，不经 OpenRouter；沿用同一 token 与 API；可访问数以万计的 LoRAs。 | S-01 |
| F-005 | 公告「Breaking change: custom provider keys」节载：语言模型请求记入 HF 账户或组织账单，不能再对语言模型使用自己的供应商 API key；仍可用 `model:provider` 后缀或设置里关闭供应商；图像与视频供应商的自定义 key 继续可用。 | S-01 |
| F-006 | 公告「What's next」列两项：把 OpenRouter 账户连到 Hugging Face；更多任务经 OpenRouter 路由。公告自述这是合作第一步。 | S-01 |

## B 组｜接口、鉴权与路由配置（F-007~F-021）

| 编号 | 事实 | 信源 |
|---|---|---|
| F-007 | 公告载：路由对每个聊天模型支持 OpenAI Chat Completions、OpenAI Responses、Anthropic Messages 三种 API，「无论背后的供应商是谁」。 | S-01、S-07、S-08 |
| F-008 | 官方文档示例把 OpenAI 兼容客户端的 `base_url` 设为 `https://router.huggingface.co/v1`，`api_key` 取 `HF_TOKEN`；`huggingface_hub.InferenceClient()` 文档说明其自动处理供应商选择与请求路由。 | S-03、S-05 |
| F-009 | 官方文档出现的三个端点：`https://router.huggingface.co/v1/chat/completions`、`https://router.huggingface.co/v1/responses`、`https://router.huggingface.co/v1/messages`。 | S-03、S-07、S-08 |
| F-010 | Messages API 与集成指南的前置条件：fine-grained HF token，带 "Make calls to Inference Providers" 权限（创建链接参数为 `ownUserPermissions=inference.serverless.write&tokenType=fineGrained），存于 `HF_TOKEN`；账户需有 compute credits。 | S-07、S-09、S-10 |
| F-011 | 官方 Pricing 文档载 Team / Enterprise 集中计费头 `X-HF-Bill-To: <org-name>`；三种等价写法为 `InferenceClient(bill_to=...)`、OpenAI SDK 的 `extra_headers`、直接 HTTP header。Claude Code 侧另有 `hf claude --bill-to`、`HF_BILL_TO`、`ANTHROPIC_CUSTOM_HEADERS="X-HF-Bill-To: ..."`。 | S-05、S-09 |
| F-012 | Prompt Caching 文档载：缓存自动生效无开关；响应 `usage.prompt_tokens_details.cached_tokens` 给出命中数；`X-HF-Session-Id` 传每会话一个稳定 UUID 可把会话固定在同一供应商，其他取值被忽略；HF 官方 Python / JS 客户端自动处理缓存。 | S-06 |
| F-013 | 同文档两条 Tips：不变内容（system prompt、tools）放最前、变化内容放最后；避免在 system prompt 顶部放时间戳或随机 id。 | S-06 |
| F-014 | 官方 Routing 文档给出四个模型 id 写法：`deepseek-ai/DeepSeek-V4.1-Flash`（默认）、`:fastest`（最高吞吐）、`:cheapest`（最低价）、`:novita`（只用 Novita，不服务该模型则返回失败响应）。公告用 `zai-org/GLM-5.3` 举例同样四种后缀。 | S-01、S-04、S-03 |
| F-015 | HF 官方 Routing 文档把默认路由描述为比较「每个供应商给出一个好答案的成本」，列三项：effective price（真实缓存命中率与该模型常见输入/输出配比下的实际收费）、速度（吞吐与 TTFT）、可靠性（失败率、畸形 tool call、容量不足）；文档载这些测量实时更新。 | S-04 |
| F-016 | 官方 Routing 文档载：设置里关掉的供应商不再接收请求，用后缀 pin 被关掉的供应商返回失败响应；记到组织的请求采用组织设置而非个人设置。Pricing 文档载组织管理员可设消费上限并禁用部分供应商。 | S-04、S-05 |
| F-017 | 官方 Routing 文档「Failover」节载：供应商失败时 OpenRouter 在该模型的另一家供应商重试；被 pin 的供应商（`:novita`）永不被替换。 | S-04 |
| F-018 | 官方首页载：`hf models ls --warm` 列出至少被一家供应商服务的模型，`--json` 供脚本与 Agent 使用。 | S-03 |
| F-019 | 公告列出五份接入指南：Claude Code、Codex、OpenCode、Pi、Hermes Agent；并内嵌一个可复制整套配置为 prompt 的 setup Space。 | S-01 |
| F-020 | Claude Code 指南给出手动配置 9 个环境变量（`ANTHROPIC_BASE_URL`、`ANTHROPIC_AUTH_TOKEN`、`ANTHROPIC_API_KEY`、四个 `ANTHROPIC_DEFAULT_*_MODEL`、`CLAUDE_CODE_SUBAGENT_MODEL`），`ANTHROPIC_BASE_URL` 值为 `https://router.huggingface.co`；推荐路径为 `hf extensions install hf-claude` + `hf claude`；文档说明五个模型变量对应内部槽位并给出按槽位配不同模型的示例。 | S-09 |
| F-021 | OpenCode 指南载其原生支持 HF Inference Providers，`opencode auth login` 选 Hugging Face 并填 token，`/models` 选模型；组织计费写 `~/.config/opencode/opencode.json` 的 `provider.huggingface.options.headers`。文档同段写「17+ providers」。 | S-10 |

## C 组｜规模、份额与定价（F-022~F-031）

| 编号 | 事实 | 信源 |
|---|---|---|
| F-022 | 公告载 OpenRouter 每月服务超过 800 万亿 token、超过 1000 万用户、600+ 模型、80+ 供应商。 | S-01 |
| F-023 | 公告载 OpenRouter 上 open-weight 模型 token 份额从 2025-10 的 26.8% 到 2026-09 末的 71.7%，7 月峰值 77.5%；同期周 open-weight 量增长超过 60 倍，closed 接近 10 倍。公告引注 OpenRouter 2026-10 文章。 | S-01、S-12 |
| F-024 | 公告载当周 OpenRouter 用量最高的模型是 open-weight 的 DeepSeek V4.1 Flash 1017，59.2 万亿 token，附 rankings 链接。 | S-01 |
| F-025 | 公告载平均价格：open-weight 每百万输入 token $0.28、输出 $1.62；closed 为 $1.27 与 $6.36。 | S-01 |
| F-026 | 公告载 Artificial Analysis Intelligence Index 上 Kimi K3.1 Pro（称最佳 open-weight）46 分、Claude Fable 5.2 65 分；单任务成本 $3.68 对 $26.54，约七分之一。 | S-01、S-14 |
| F-027 | 公告载 OpenRouter 自测新路由：capacity errors 减少 46%、time to first token 改善 16.9%、throughput 改善 16.3%。 | S-01、S-11 |
| F-028 | 公告载定价不变：按供应商原价记 HF 账单、HF 不加价；PRO 每月 $2 credits，Team / Enterprise 每席位 $2。Pricing 文档表：Free 无赠送额度，需购买 credits 或升级；超额均可按量付费。 | S-01、S-05 |
| F-029 | Pricing 文档载：赠送的是通用 compute credits，可用于 Inference Endpoints、Spaces 升级硬件（含 ZeroGPU 超额）、Jobs；每月发放并在按量计费前自动抵扣；Team / Enterprise 额度成员共享但须显式指定计费组织，未指定时无法享受；Enterprise 可用 usage API 取日粒度序列（请求数、成本（分）、输入/输出/缓存输入 token，最多延迟 2 小时，成本按行四舍五入到分）；`"hf-inference"` 为旧称 "Inference API (serverless)"，按计算时长 × 硬件单价计费，2025-07 起主要做 CPU 推理。 | S-05 |
| F-030 | 公告载用量总览（`settings/inference-providers/overview`）按每笔请求实际落到哪一家供应商拆分花费；Pricing 文档载同视图按模型与供应商拆分。 | S-01、S-05 |
| F-031 | 公告载模型页新增两个页签：Providers 列可路由到的每家供应商及其输入/输出价格、速度、近 24 小时 uptime；Metrics 列这些供应商里的最优价格、吞吐、TTFT、上下文长度与 uptime。 | S-01 |

## D 组｜OpenRouter 路由算法（F-032~F-039、F-049~F-052）

| 编号 | 事实 | 信源 |
|---|---|---|
| F-032 | OpenRouter 2026-10-28 算法公告（Scott Morse）载：约 77% 的请求落在由多家供应商服务的模型上；旧默认路由主要按输入 token 标价排序，失败后重路由到次便宜选项；并列出 price-only 路由的四类局限（低价即胜、静态排名、利润压缩、定价组合游戏）。 | S-11 |
| F-033 | 同公告定义 Routing Cost：一次尝试的代价（实际价格 + 等待时间）× 需要尝试多少次；逐项列 effective price、throughput（端到端每秒输出 token）、TTFT、rate limits（429）、reliability、quality（当前主要检查 tool call 格式完好）。 | S-11、S-13 |
| F-034 | 同公告载流量分配三条机制：competitive edge 内按份额共享流量、floor（每家保留探测流量，新端点从模型典型数值起步）、back off（失败或限流时降份额直到恢复）。 | S-11、S-13 |
| F-035 | 同公告「What stays the same」载：`provider.order`、显式 `provider.sort`（price/throughput/latency）、`:floor`、`:nitro`、自有供应商 key 会绕过新路由；`provider.only` / `ignore` 过滤后若剩 ≥2 家仍由新算法挑选；FAQ 载无需改代码，设置 `sort: price` 可保留 price-only。 | S-11、S-13 |
| F-036 | 同公告载：一段会话只有第一个请求由算法挑供应商，后续固定在原供应商以保持 prompt cache 温度；原供应商不可用时自动回退；某次尝试失败则在剩余供应商中按排名重试。 | S-11、S-13 |
| F-037 | 同公告载实验方法：switchback 实验，每天切为 3 小时区块并配对翻转新旧路由，每次切换丢弃 1 小时 burn-in，覆盖一周、代表性开源模型样本；共 2400 万请求、1030 亿输入 token 在两组间均分。 | S-11 |
| F-038 | 同公告结果表：TTFT p50 1007→837 ms（-16.9%，95% 区间 13.9%~19.8%）；throughput p50 62.4→72.6 tok/s（+16.3%）；每千请求成本 $1.25→$1.32（+6.0%）；每百万 token $0.301→$0.324（+7.3%）；至少遇到一次 429 从 7.1%→3.8%（-3.3 个百分点，公告表述为 46% fewer）；需要重试从 10.4%→6.9%（-34%）。 | S-11 |
| F-039 | 同公告 FAQ 载：使用新路由无需改代码（API key、请求体、模型 id 不变）；显式 sort 可保留 price-only；「新路由会不会更贵」答「会，有时会选更快或更可靠的供应商而非最便宜的」，并复述 +6.0% 成本与三项收益。 | S-11 |
| F-049 | Provider Routing 文档列出 `provider` 对象字段：`order`、`allow_fallbacks`、`require_parameters`、`data_collection`、`zdr`、`enforce_distillable_text`、`only`、`ignore`、`quantizations`、`sort`、`preferred_min_throughput`、`preferred_max_latency`、`max_price`。 | S-13 |
| F-050 | OpenRouter 2026-10-31 文章给出价格上限优先、其余按吞吐排序的写法 `{"max_price": {"prompt": 1, "completion": 4}, "sort": "throughput"}`（单位为每百万 token 美元）。 | S-12、S-13 |
| F-051 | Provider Routing 文档载：`:nitro` 是按吞吐排序并额外纳入 priority service tier 端点的 shortcut；`:floor` 是按价格排序并额外纳入 flex service tier 端点的 shortcut；两者都是 routing variant，不是 models API 里的独立条目。 | S-13 |
| F-052 | Provider Routing 文档载：Business / Enterprise 可用 `https://eu.openrouter.ai` 与 `https://us.openrouter.ai` 做区域内处理。 | S-13 |

## E 组｜开放权重市场数据（F-040~F-048）

| 编号 | 事实 | 信源 |
|---|---|---|
| F-040 | OpenRouter 2026-10-31 文章定义 open-weight 为公开训练权重、可自行下载运行/微调/对外服务；closed-weight 仅能由厂商或其授权云提供；并说明按 OSI 定义 open source 还要求训练数据（或充分说明）与代码，多数 open-weight 模型未公开训练数据。 | S-12 |
| F-041 | 同文章「How we measured this」载：份额基于 top 50 模型按周 token 量的分类，模型条目链接到 Hugging Face 仓库即计 open-weight；数据集的 "other" 行每周 0.3~10.8 万亿 token 不计入，未公布的 stealth 模型最近一周 38.7 万亿 token 不计入；token 数来自各供应商自己的 tokenizer，适合看趋势而非精确同口径比较。 | S-12 |
| F-042 | 同文章份额表：2025-10-06 26.8%（open 1.3T / closed 3.4T）、2026-01-26 35.1%（2.6T / 4.9T）、2026-04-20 47.7%（8.9T / 9.8T）、2026-07-20 77.5%（41.1T / 11.9T）、2026-09-28 71.7%（83.5T / 33.0T）。 | S-12 |
| F-043 | 按上表机械复核：83.5 / 1.3 ≈ 64.2；33.0 / 3.4 ≈ 9.7。 | 本束算术复核（基于 F-042） |
| F-044 | 同文章载价格口径：近四周 token 加权目录标价，open $0.28/$1.62、closed $1.27/$6.36（每百万 token），取自 2026-10-08 的 models / endpoints API；供应商数与价格区间取自 2026-10-21。 | S-12 |
| F-045 | 同文章 2026-10-21 表：`z-ai/glm-5.3-flash` 30 家（输入 $0.04~$1.15）、`deepseek/deepseek-v4.1-flash` 31 家（$0.03~$0.60）、`moonshotai/kimi-k3` 20 家（$0.24~$4.50）、`anthropic/claude-sonnet-5.5` 5 家（$2.00~$2.20）、`openai/gpt-6-luna` 3 家（$0.05~$0.20）、`google/gemini-3.8-flash` 2 家（$0.38~$1.35）。 | S-12 |
| F-046 | 同文章载 Artificial Analysis Intelligence Index（经其 benchmarks endpoint 汇总）：最佳 closed 为 Claude Opus 5.5 57.6、Claude Sonnet 5.5 56.0；最佳 open 为 MiMo-V2.6-Pro 46.3、GLM-5.3 44.8、Step 5 Preview 43.7、Kimi K3 43.6；文中表述差约 11 分，并称 2026-06 的 roundup 里该差距约 5 分。每个分数为模型最高 reasoning effort 设置下的取值。 | S-12 |
| F-047 | 同文章载类别重叠例：Kimi K3 最便宜端点低于 Claude Sonnet 5.5、最贵端点约为其两倍；GPT-6 Luna 目录标价每百万输入 token $0.10，低于任何 Kimi K3 供应商。文中建议按具体模型比较而非按类别比较。 | S-12 |
| F-048 | 同文章给出 `models` 数组以 closed 在前、open 在后作 fallback 的请求示例，并附 `provider.max_price` 封顶 `{"prompt": 1, "completion": 4}`；示例中 Claude Sonnet 5.5 超出上限，请求被路由到 GLM-5.3 Flash；移除后者后返回 404，消息为 `No endpoints found that satisfy the max price for this request`，`failed_routing_step` 为 `Filter by Max Price`。 | S-12 |

---

**统计**：F-001~F-052 共 52 条；A 组 6 条、B 组 15 条（F-007~F-021）、C 组 10 条（F-022~F-031）、D 组 12 条（F-032~F-039、F-049~F-052）、E 组 9 条（F-040~F-048）。编号连续无缺号，区间上界 52 与实际登记数一致。
