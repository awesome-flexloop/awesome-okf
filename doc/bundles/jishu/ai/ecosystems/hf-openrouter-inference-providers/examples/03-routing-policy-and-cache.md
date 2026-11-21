---
type: Example
title: "策略选择与缓存粘滞演练（含迁移自查）"
description: "设计一个默认路由 vs :cheapest 的对照实验，给出 X-HF-Session-Id 的正确用法与一份旧用法迁移自查表，附可迁移的「统一网关接入五步法」。"
tags: [对照实验, 路由策略, 提示词缓存, 迁移清单, 反模式, 可迁移模式]
sources:
  - id: hf-ip-routing
    resource: https://huggingface.co/docs/inference-providers/routing
    title: "Routing and Providers 官方文档"
  - id: hf-ip-caching
    resource: https://huggingface.co/docs/inference-providers/prompt-caching
    title: "Prompt Caching 官方文档"
  - id: or-routing-rebuild
    resource: https://openrouter.ai/blog/announcements/how-we-rebuilt-provider-routing/
    title: "OpenRouter 路由算法重建公告（2026-10-28）"
  - id: or-open-vs-closed
    resource: https://openrouter.ai/blog/insights/open-weight-vs-closed-weight-models/
    title: "OpenRouter 开放权重与闭源模型对比（2026-10-31）"
---

# 策略选择与缓存粘滞演练（含迁移自查）

> 本页是**实验设计与操作清单**，不是实测结果。本库没有真实 `HF_TOKEN`，未运行下面任何一组请求。

## 演练一：默认路由到底贵不贵

官方实验在同一周内测得默认（新）路由相对旧 price-only 路由：TTFT p50 -16.9%、吞吐 p50 +16.3%、429 命中率 -46%，同时每千请求成本 +6.0%（F-038）。要在**你自己的流量**上验证这个取舍，做一次最小对照：

| 组 | model 字段 | 观测指标 |
|---|---|---|
| A | `deepseek-ai/DeepSeek-V4.1-Flash` | TTFT、总耗时、`usage`、429/5xx 次数、用量页的供应商拆分 |
| B | `deepseek-ai/DeepSeek-V4.1-Flash:cheapest` | 同上一组，逐项对照 |
| C（可选） | `deepseek-ai/DeepSeek-V4.1-Flash:fastest` | 同上一组，看吞吐上限 |

控制变量：同一段 prompt、同一时间窗、每组足够多次请求（供应商实时指标按滚动窗口更新，一两次请求说明不了问题）；不要在同一会话里混用策略，否则缓存粘滞会污染结果。

**读法**：B 组若单价明显低但 TTFT / 失败率明显差，就是「速度换价格」的量化证据；若两组差异很小，说明该模型当前供应商差距不大，可按可维护性选默认。

## 演练二：把会话钉在同一供应商

```bash
SESSION_ID=$(python -c "import uuid; print(uuid.uuid4())")
# 该会话所有轮次复用同一个 SESSION_ID
for prompt in "读一下这个仓库的结构" "刚才第二个模块做什么" "给它补一段测试"; do
  curl https://router.huggingface.co/v1/chat/completions \
    -H "Authorization: Bearer $HF_TOKEN" \
    -H "X-HF-Session-Id: $SESSION_ID" \
    -H "Content-Type: application/json" \
    -d "{\"model\": \"deepseek-ai/DeepSeek-V4.1-Flash\",
         \"messages\": [{\"role\": \"user\", \"content\": \"$prompt\"}]}"
done
```

三条纪律（F-012、F-013、F-036）：

1. UUID **每会话一个**，不是每请求一个；换个 UUID 等于换个会话；
2. 只有稳定 UUID 生效，其他取值被忽略；
3. 每轮把不变的 system prompt / tools 放最前、变量放最后，别在开头放时间戳。

验收：第 2、3 轮响应的 `usage.prompt_tokens_details.cached_tokens` 应明显大于第 1 轮。官方说明会话首请求由算法挑供应商、后续固定在原供应商；原供应商不可用时才自动回退（F-036）。

## 旧用法迁移自查表

| # | 检查项 | 命中后怎么办 |
|---|---|---|
| 1 | 是否在语言模型请求里传了供应商自己的 API key？ | 改为 `HF_TOKEN`；BYOK 对语言模型已不可用（F-005） |
| 2 | 成本脚本是否按供应商账单/自有合同价核算？ | 改为 HF 账单 + 用量页按供应商拆分（F-028、F-030） |
| 3 | 是否用 `:<provider>` 硬 pin 了某家？ | 确认是否接受「永不被替换」——它会关掉自动故障转移（F-017） |
| 4 | 是否把组织额度当成自动生效？ | 显式加 `X-HF-Bill-To` / `--bill-to` / `bill_to=`（F-011、F-029） |
| 5 | 组织是否禁用了你 pin 的供应商？ | 组织设置优先于个人设置，显式请求被禁用的会报错（F-016） |
| 6 | 是否把图像/视频/音频请求也当成走 OpenRouter？ | 三者链路不变，自定义 key 仍可用（F-004、F-005） |
| 7 | 是否把 OpenRouter 的 `:floor` / `:nitro` / `provider.sort` 写进 HF 请求？ | 两套后缀体系不通用（C-04、F-051） |

## 可迁移模式：统一网关接入五步法

> 触发场景：需要用一个身份、一个 API 接入多家后端，同时保留策略可调与事后归因。不适用于单一供应商、或对数据驻留/合同价有硬约束的场景（此时 BYOK 或专属端点更合适）。

1. **定协议与基址**：先确认网关支持哪几种协议、各自的 base URL 形态（本例 Anthropic 侧不带 `/v1`）；
2. **最小请求验身份**：用一个 id、一个 prompt 打通鉴权；先查可用模型清单，别在业务代码里猜 id；
3. **显式决定路由策略**：默认 / 价格优先 / 吞吐优先 / 硬 pin，写进配置而不是散落在调用点；理解默认策略的优化目标；
4. **做会话粘滞**：有缓存就把会话固定到同一后端，并让 prompt 前缀稳定；
5. **落账单与可观测**：明确记在谁账上，打开按后端的用量拆分，才能事后判断策略是否合算。

**检验标准**：三种协议各跑通一次；能解释一次 429 之后是否发生了跨供应商重试；能指出本次请求记在谁账上、落在哪家供应商。

**至少三条反模式**（均来自本束材料）：① 把两家平台的模型 id 与后缀混用；② 假定默认路由就是最便宜（官方实验里它贵 6.0%）；③ 把不同来源、不同分母的份额/分数合并成一句结论；④ 迁移时只看 "Your code stays the same" 而漏掉 BYOK 破坏性变更。

**跨领域迁移示例**：CDN 选源或多副本读取是同构问题——按健康度加权挑源（Routing Cost）、会话粘滞保持缓存（prompt cache）、显式 pin 到指定节点（`:provider`）、失败换源重试（failover）。把「选最便宜」换成「算期望成本」这一步在两个领域都成立。
