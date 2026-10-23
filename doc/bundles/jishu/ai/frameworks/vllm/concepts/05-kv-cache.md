---
type: Concept
title: "KV 缓存与 PagedAttention"
description: "vLLM 的显存管理核心——KV block 池与 block table、前缀缓存的哈希-命中-失效机制、KV cache 量化（FP8）、CPU/NVMe 卸载与混合缓存（MLA/滑窗/SSM）"
tags: [vllm, paged-attention, kv-cache, prefix-caching, kv-quantization, kv-offloading, 核心模块]
generated: { by: seven-concepts-cmd+source-code-to-okf-wiki/E, at: "2026-10-22T16:40:00+08:00" }
status: stable
stale_after: 2027-04-22
sources:
  - id: paper
    url: https://arxiv.org/abs/2309.06180
    title: PagedAttention 论文（SOSP 2023）
  - id: local-kv
    resource: /references/facts.md
    title: docs/design/paged_attention.md + v1/core/（本地检出）
  - id: anatomy-blog
    url: https://vllm.ai/blog/2025-09-05-anatomy-of-vllm
---

# KV 缓存与 PagedAttention

PagedAttention 是 vLLM 的立身之本（SOSP 2023 论文，F-007）：把 KV cache 切成固定大小的 **block**，像操作系统管理虚拟内存页一样按需分配、按块寻址，消掉为「最坏情况长度」预分配的浪费。

## Block 池与块表

核心数据结构（`vllm/v1/core/block_pool.py`、`kv_cache_manager.py`，F-002）：

- **KVCacheBlock**：一个 block 存固定数量 token 的 KV，**默认 16 token**（F-031）；
- **BlockPool / free_block_queue**：可用 block 的双向链表池，数量级可达数十万（取决于显存与 block 大小）（F-032）；
- **req_to_blocks**：request_id → block 列表的映射，即每个请求的「块表」；
- **BlockHashToBlockMap**：内容哈希 → block 的映射，前缀缓存的索引（F-033）。

block 的显存占用（非 MLA 标准 transformer 层，F-031）：

```
2 (K/V) × block_size(16) × num_kv_heads × head_size × dtype_bytes(bf16=2)
```

## 前缀缓存：重复 prompt 不重算

默认开启（`--enable-prefix-caching` 关闭则禁，F-033）。机制分五步（F-033）：

1. **哈希**：`hash_request_tokens` 把输入切成 16-token chunk，对每个完整 chunk 计算哈希——哈希输入含前一 block 哈希、当前 token、可选元数据（多模态 hash、LoRA ID、cache salt），形成链式 `BlockHash`；
2. **查命中**：`find_longest_cache_hit` 在 `cached_block_hash_to_block` 查最长命中前缀；
3. **分配**：`allocate_slots` 只为未命中部分取 block；
4. **登记**：`coordinator.cache_blocks` 把 BlockHash 与物理 block 关联；
5. **失效**：block 被重新分配给其他请求时清除哈希与映射；引用计数管理存活请求的复用。

两条实操口径（F-033）：

- **命中粒度**：可复用前缀须长于一个 block（16 token）且最好对齐 block 边界，否则尾部 `long_prefix_len % block_size` 个 token 要重算；
- **收益面**：只加速 **prefill**，对 decode 无帮助——多轮对话、系统提示词共享、few-shot 模板是典型受益场景。

## 前向中的块寻址

decode 时模型对每个序列只需算最新 token 的 query，注意力内核按块表索引拼接历史 KV——block 在显存中**物理不连续**，逻辑上连续（F-032）。本地 `docs/design/paged_attention.md` 明确标注：该文档是基于原始论文的历史文档，不再描述今天的代码实现；今天的注意力内核见 `csrc/` 与 `vllm/v1/attention/backends/`（F-002）。

## KV cache 量化与卸载

- **FP8 KV cache**：`--kv-cache-dtype fp8`（或 `fp8_e4m3`/`fp8_e5m2`）把 KV 以 FP8 存储，显存约减半，精度损失依模型而异（F-090、F-095）；
- **CPU 卸载**：`--cpu-offload-gb` 指定卸载到 CPU 内存的 GB 数，冷块换出、按需换入（F-140）；
- **分层/外部卸载**：NVMe、分级存储（tiered offloading）经 KV connector 实现，见 [13 进阶主题](13-advanced.md) 与 [12 分布式](12-distributed.md) 的 PD 分离（F-140）。

## 混合模型与缓存分组

混合注意力/状态空间模型（Mamba、Qwen3.5 类 hybrid、滑窗注意力、MLA）有不同的 KV 结构，V1 用 **KV cache spec 分组**管理：`register_all_kvcache_specs` 按层注册 spec，`single_type_kv_cache_manager.py` 分管各类型（F-002）。多模态另有 **encoder cache**（视觉编码器输出缓存，F-068 的 `/reset_encoder_cache` 即其管理端点）。

## 容量是怎么测出来的

Worker 初始化时跑 dummy/profiling 前向 + 显存快照，结合 `gpu_memory_utilization`（默认 0.9，权重+激活+KV 总量占显存比例）算出能容纳多少 block——这就是「改一个利用率参数就能换 KV 容量」的来历（F-053、F-013）。KV 容量也可以直接用 `--kv-cache-memory-bytes` 按字节指定（F-013）。

## 延伸阅读

- [04 调度与批处理](04-scheduling.md)：allocate_slots 的调度视角
- [06 执行层：Executor 与模型运行](06-execution.md)：块表如何变成 attention metadata
- [10 量化](10-quantization.md)：FP8 KV 与权重量化的配合
