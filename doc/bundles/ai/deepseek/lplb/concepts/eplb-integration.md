---
type: concept
scope: lplb
name: eplb-integration
version: "0.1.0"
source: https://github.com/deepseek-ai/LPLB
description: LPLB 与 EPLB 的集成——静态专家重平衡与动态 LP 求解的分层协作
---

# EPLB 集成

## 分层架构

LPLB 采用两层分离架构解决 MoE 负载不均衡：

- **EPLB（静态层）**：每 N 步在 CPU 上执行贪心重排+复制+装箱，决定"哪些专家需要副本、放在哪些 GPU 上"。处理慢时间尺度的结构性不均衡。
- **LPLB（动态层）**：每个 batch 在 GPU 上执行 LP 求解+加权哈希路由，决定"当前 batch 的 token 如何在原始和副本间分配"。处理快时间尺度的 per-batch 波动。

EPLB 源码嵌入在 `lplb/eplb.py` 中。

## EPLB 核心算法

### balanced_packing：贪心装箱

将 n 个带权对象打包到 m 个 pack，每 pack 恰好 n/m 个对象，最小化各 pack 最大权重。算法：按权重降序排列，贪心选择当前最轻且未满的 pack。这是 LPT（Longest Processing Time first）近似算法。

**用途**：Step 1 将 expert groups 打包到节点；Step 3 将物理专家打包到 GPU。

### replicate_experts：贪心复制

将 `num_log` 个专家复制到 `num_phy` 个副本，最小化最大副本负载。算法：从 num_log 个专家开始，逐个复制 `weight/logcnt` 比值最大的专家（水填充策略）。

**用途**：Step 2 在节点内构造冗余专家。

### rebalance_experts_hierarchical：层次化重平衡

三步流程：
1. **Groups→Nodes**：按 group 总负载用 balanced_packing 分配到节点。
2. **节点内复制**：每个节点内用 replicate_experts 贪心复制热专家。
3. **Physical→GPUs**：按物理专家预期负载用 balanced_packing 分配到 GPU。

层次化策略适应 NVLink（快）和 RDMA（慢）的异构网络，减少跨节点冗余。

### rebalance_experts：入口函数

当 `num_groups % num_nodes == 0` 时使用层次化策略，否则退化到全局策略（单节点等效）。返回 `(phy2log, log2phy, logcnt)` 三元组。

## 在 LPLB 中的调用链

EPLB 通过 `update_redundancy_mapping(workload)` 被调用：

1. **无 workload**：使用 `arange(n_logical_routed_experts)` 恒等映射，不做重排。
2. **有 workload**：调用 `rebalance_experts()` 做层次化重平衡，然后按负载降序排列每设备专家。
3. **冗余选择**：取前 `combined * num_redundants` 个专家（热专家），通过 r2o 映射在邻接 rank 创建副本。
4. **拼接构建**：`cat([nored_phy2log, tored_log_dup])` 形成完整 phy2log，遍历转置构建 log2phy 和 logcnt（保证原始在前、副本在后）。

### 关键设计

- **EPLB 仅重排不增副本**：调用 `rebalance_experts` 时 `num_replicas = n_logical_routed_experts`，EPLB 只做专家重排序。副本槽位由拓扑静态决定。
- **max_logcnt=2**：每个专家最多一个副本（原始+副本），简化了路由逻辑为二选一。
- **assert 保证**：`phy2log.shape[0] == n_routed_experts` 和 `max_logcnt == 2` 是硬约束。

## 与 DeepEP 的集成

`init_from_deep_ep(buffer)` 初始化 NVSHMEM 通信：
- 根据 `buffer.low_latency_mode` 选择 multi-plane（`cpu_rdma_team`）或单 plane（`NVSHMEM_TEAM_WORLD`）。
- 根据 `buffer.num_rdma_bytes == 0` 决定是否调用 `nvshmemx_init_attr`。
- 通过 `sync_current_to_module()` 将 DeepEP 的 NVSHMEM 全局状态（`nvshmemi_device_state_d` 等）复制到 JIT 编译模块。

### 通信模式对比

| 阶段 | 无 DeepEP | 有 DeepEP（NVSHMEM） |
|---|---|---|
| Workload 聚合 | `torch.distributed.all_reduce`（Python） | NVSHMEM put+signal（kernel 内部） |
| 节点内 | NCCL allreduce | CUDA IPC + atomic signal |
| 跨节点 | NCCL allreduce | `nvshmem_putmem_signal_nbi`（RDMA one-sided） |

## 完整训练流程

```
每步训练:
  1. Router → 逻辑专家索引 idx
  2. count_workload(idx) → 统计负载
  3. solve_probs(workload) → LP 求解分配比例
  4. weighted_select_target(idx, o_weight) → 路由到物理专家
  5. DeepEP dispatch → token 发送
  6. DeepGEMM grouped GEMM → 专家计算
  7. DeepEP combine → 结果回传

每 N 步:
  8. update_redundancy_mapping(history)
     → rebalance_experts 重排
     → 基于拓扑更新副本映射
  9. 更新 DeepEP buffer 专家布局
```

## 设计权衡

1. **EPLB 在 CPU**：重平衡频率低，CPU 执行可接受，贪心算法易调试。
2. **LPLB 在 GPU**：每步需求解，GPU 执行避免 PCIe 开销，编译期特化保证低延迟。
3. **副本数静态**：副本槽位数由拓扑决定（不随负载动态变化），EPLB 仅决定哪些专家占据这些槽位，LP 规模固定。
4. **单副本限制**：max_logcnt=2 简化路由为二选一，是当前版本的约束。

相关参考：[API 参考](/ai/deepseek/lplb/references/api)、[拓扑配置](/ai/deepseek/lplb/references/topology)。
