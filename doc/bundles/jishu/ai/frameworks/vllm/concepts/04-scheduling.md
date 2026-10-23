---
type: Concept
title: "调度与批处理：continuous batching、chunked prefill 与调度策略"
description: "vLLM V1 调度器——waiting/running 双队列、decode 优先 + prefill 补位的调度顺序、token 预算与 allocate_slots 三步、FCFS 与 priority 策略、chunked prefill 默认开启与 preemption"
tags: [vllm, scheduler, continuous-batching, chunked-prefill, fcfs, priority, 核心模块]
generated: { by: seven-concepts-cmd+source-code-to-okf-wiki/E, at: "2026-10-22T16:40:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: v1-guide
    resource: /references/facts.md
    title: docs/usage/v1_guide.md + docs/design/arch_overview.md（本地检出）
  - id: anatomy-blog
    url: https://vllm.ai/blog/2025-09-05-anatomy-of-vllm
---

# 调度与批处理：continuous batching、chunked prefill 与调度策略

调度器（`vllm/v1/core/sched/scheduler.py`，约 3500 行）是 V1 引擎的心脏（F-002）。它每个 engine step 回答一个问题：**这一步把哪些请求的哪些 token 放进去算**。

## 两种负载，一次混编

- **Prefill 请求**：对整个 prompt 做一次前向，通常 **compute-bound**；最后一个 token 位置采样出新 token（F-043）。
- **Decode 请求**：只对最新 token 做前向，**memory-bandwidth-bound**（算一个 token 也要加载全部权重与 KV cache）（F-043）。

V0 一次 step 只能处理一种；**V1 统一调度器把两者视为同一件事**：用 `{request_id: num_tokens}` 字典动态分配固定的每步 token 预算，prefill 与 decode 无硬性阶段分离（F-018）。

## 调度顺序：decode 优先，prefill 补位

每个 step（F-042）：

1. **先 decode（running 队列）**：计算每个请求要生成的新 token 数（不总是 1——投机解码与异步调度时会更多）→ `allocate_slots` → 扣减 token 预算；
2. **再 prefill（waiting 队列）**：查已计算 block 数（前缀缓存关闭时为 0）→ `allocate_slots` → 从 waiting 移入 running → 扣减预算。

`allocate_slots` 三步（F-042）：

1. **算 block 数**：按需分配的新 KV block 数（默认每 block 存 16 token；17 个新 token 需 `ceil(17/16) = 2` blocks）；
2. **查可用性**：块池不足则提前退出——可能触发 recompute preemption（驱逐低优先级请求释放 KV）或跳过本步调度；
3. **分配**：经 coordinator 从 `free_block_queue`（双向链表）取出前 n 个 block，记入 `req_to_blocks`（request_id → block 列表映射）。

## 调度策略

`--scheduling-policy` 二选一（F-040）：

- **FCFS**（默认）：先来先服务；
- **priority**：按请求优先级，FCFS 作 tie-breaker。

## chunked prefill：长 prompt 不霸凌

动机：单个超长 prompt 若独占一个 step，会阻塞其他 prefill 请求、推高它们的 TTFT。做法：限制每步新 token 数（`long_prefill_token_threshold`），超长 prompt 截断为多个 chunk 分步算（F-019）。

- **V1 默认开启**（V0 按模型条件启用）（F-019）；
- 即便不设阈值，prompt 超过每步 token 预算时也会自动按 chunked prefill 处理；
- 只有最后一个 chunk 采样新 token。

## 前缀缓存（调度视角）

前缀缓存（prefix caching）默认开启，对**调度**的含义是：prefill 请求进来先查本地已计算 block 数（命中数），只对未命中部分 `allocate_slots` 与计算——直接省掉重复 prefill（F-033）。哈希与块管理细节见 [05 KV 缓存与 PagedAttention](05-kv-cache.md)。

## continuous batching 的实现根基

前向时所有序列被 flatten 拼成一条「super sequence」，靠 position 索引与 attention mask 保证每个序列只关注自己的 token——**不需要 right-padding**，这是 continuous batching（请求随到随加入批次、完成即退出）能在 vLLM 高效落地的原因（F-034）。

## 指标视角

调度质量最终体现在四个指标上（F-146）：TTFT（首 token 延迟，prefill 调度质量）、ITL/TPOT（token 间延迟，decode 质量）、吞吐（整体）、goodput（满足 SLO 的吞吐）。调优闭环见 [examples/04 基准测试](../examples/04-benchmarking.md)。

## 延伸阅读

- [05 KV 缓存与 PagedAttention](05-kv-cache.md)：块池、哈希与前缀缓存细节
- [11 投机解码](11-speculative-decoding.md)：为什么 decode 的「新 token 数」可以不等于 1
- [13 进阶主题](13-advanced.md)：异步调度与多步调度
