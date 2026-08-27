---
type: example
scope: lplb
name: basic-planning
version: "0.1.0"
source: https://github.com/deepseek-ai/LPLB
description: LPLB 基础使用示例——创建 Planner、执行负载均衡规划
---

# 基础专家复制规划

本示例演示 LPLB 的核心使用流程：定义拓扑 → 创建 Planner → 执行负载均衡。

## 前置条件

- CUDA Toolkit ≥ 12.6.3（含 cuSolverDx）
- PyTorch ≥ 1.12（CUDA 版本）
- 已安装 lplb（`pip install --no-build-isolation -e .`）

## 最小示例：单步负载均衡

```python
import torch
from lplb import Planner

# 1. 定义冗余拓扑（Cube8P2E：8 rank，每 rank 2 个冗余专家）
#    r2o[i][j] = k 表示 rank i 的第 j 个冗余专家是 rank k 原始专家的副本
r2o = torch.tensor([
    [3, 0, 1, 2, 7, 4, 5, 6],
    [6, 7, 4, 5, 0, 1, 2, 3],
]).T.int().cuda()  # shape: (8, 2)

# 2. 配置专家参数
n_logical_experts = 256       # 逻辑专家总数
ep_size = 32                  # EP 总 rank 数
n_redundants_per_rank = 2     # 每 rank 冗余专家数（与 r2o 列数一致）
n_routed_experts = n_logical_experts + n_redundants_per_rank * ep_size  # 物理专家总数 = 320

# 3. 创建 Planner 实例
planner = Planner(
    redundant_to_original=r2o,
    n_routed_experts=n_routed_experts,
    n_logical_routed_experts=n_logical_experts,
    ep_size=ep_size,
    # group=ep_group,  # 可选：传入 torch.distributed ProcessGroup 用于 allreduce
)

# 4. 准备输入：模拟 router 输出的逻辑专家索引
#    值范围 [-1, n_logical_experts)，-1 表示 padding/drop
batch_size = 4096
seq_len = 8
top_k = 6
idx = torch.randint(-1, n_logical_experts, (batch_size, seq_len * top_k), device='cuda')

# 5. 创建可行解计数器（统计 LP 求解成功率）
avail_counter = torch.zeros((), dtype=torch.int32, device='cuda')

# 6. 一站式执行：统计 → 求解 → 路由
mapped_idx = planner.run(idx, avail_counter)

# 7. 查看结果
print(f"输入 idx 形状: {idx.shape}")
print(f"输出 mapped_idx 形状: {mapped_idx.shape}")
print(f"输出值范围: [{mapped_idx[mapped_idx >= 0].min()}, {mapped_idx.max()}]")
print(f"LP 可行组数: {avail_counter.item()} / {planner.n_group}")
```

## 分步执行（更精细控制）

```python
import torch
from lplb import Planner

r2o = torch.tensor([
    [3, 0, 1, 2, 7, 4, 5, 6],
    [6, 7, 4, 5, 0, 1, 2, 3],
]).T.int().cuda()

n_logical_experts = 256
ep_size = 32
n_redundants_per_rank = 2
n_routed_experts = n_logical_experts + n_redundants_per_rank * ep_size

planner = Planner(r2o, n_routed_experts, n_logical_experts, ep_size)

n_sms = torch.cuda.get_device_properties(torch.cuda.current_device()).multi_processor_count

# 模拟 router 输出
idx = torch.randint(0, n_logical_experts, (4096, 48), device='cuda')
avail_counter = torch.zeros((), dtype=torch.int32, device='cuda')

# 步骤 1：统计当前 batch 各专家的 token 负载
local_workload, local_workload_by_sm = planner.count_workload(idx, n_sms)
print(f"负载统计 shape: {local_workload.shape}")  # (256,)
print(f"按SM分片 shape: {local_workload_by_sm.shape}")  # (n_sms, 256)
print(f"总 token 数: {local_workload.sum().item()}")

# 步骤 2：LP 求解，得到冗余专家的分配比例
o_weight, global_workload = planner.solve_probs(local_workload, avail_counter)
print(f"分配比例 shape: {o_weight.shape}")  # (2, combined_redundant_experts)
print(f"分配比例范围: [{o_weight.min().item():.3f}, {o_weight.max().item():.3f}]")

# 步骤 3：基于比例将逻辑索引映射到物理专家
mapped_idx = planner.weighted_select_target(idx, o_weight, local_workload_by_sm, n_sms)
print(f"映射结果 shape: {mapped_idx.shape}")
```

## 使用 EPLB 重排序（基于历史负载）

```python
# 模拟历史负载统计（实际中由训练过程中累积）
workload_history = torch.randn(n_logical_experts, device='cuda') * 0.15 + 1
workload_history = workload_history.clamp_min(0).mul(2**20).long()

# 基于历史负载更新冗余映射（EPLB 重排 + 拓扑副本创建）
phy2log, log2phy, logcnt = planner.update_redundancy_mapping(workload_history)
print(f"phy2log shape: {phy2log.shape}")      # (n_routed_experts,)
print(f"log2phy shape: {log2phy.shape}")      # (n_logical_experts, 2)
print(f"logcnt shape: {logcnt.shape}")        # (n_logical_experts,)
print(f"有副本的专家数: {(logcnt > 1).sum().item()}")
```

## 验证负载均衡效果

```python
# 模拟不均衡负载（某些专家特别热）
current_workload = torch.randn(n_logical_experts, device='cuda') * 0.3 + 1
current_workload = current_workload.clamp_min(0).mul(2**12).int()

# 求解
avail_counter.zero_()
probs, _ = planner.solve_probs(current_workload, avail_counter)

# 计算均衡前后的负载分布
phy_experts_workload = current_workload[planner.phy2log].reshape(
    ep_size // r2o.shape[0], r2o.shape[0], -1
)
# 均衡前（原始负载全在本 rank）
before_max = phy_experts_workload.sum(-1).max().item()
before_mean = phy_experts_workload.sum(-1).float().mean().item()

# 均衡后（按 LP 比例分流）
dup_workload = phy_experts_workload[
    :, :, :planner.combined_redundant_experts * r2o.shape[1]
].reshape(
    ep_size // r2o.shape[0], r2o.shape[0], planner.combined_redundant_experts, r2o.shape[1]
).sum(2)
dup_workload = dup_workload * probs + (dup_workload * (1 - probs)).gather(
    dim=1, index=r2o.expand(*probs.shape).long()
)
fixed_workload = phy_experts_workload[
    :, :, planner.combined_redundant_experts * r2o.shape[1]:
    -planner.combined_redundant_experts * r2o.shape[1]
].sum(2)
after_workload = dup_workload.sum(2) + fixed_workload

after_max = after_workload.max().item()
after_mean = after_workload.float().mean().item()

print(f"均衡前 max/mean: {before_max / before_mean:.3f}")
print(f"均衡后 max/mean: {after_max / after_mean:.3f}")
print(f"LP 可行率: {avail_counter.item()}/{planner.n_group}")
```

## 与 torch.distributed 配合（多 GPU）

```python
import torch.distributed as dist

# 初始化分布式（假设已通过 torchrun 启动）
dist.init_process_group(backend='nccl')
rank = dist.get_rank()
world_size = dist.get_world_size()
torch.cuda.set_device(rank)

# 创建 EP 通信组
ep_group = dist.new_group(ranks=list(range(world_size)))

# 创建 Planner（传入 group 以启用 allreduce）
planner = Planner(
    redundant_to_original=r2o.cuda(),
    n_routed_experts=n_routed_experts,
    n_logical_routed_experts=n_logical_experts,
    ep_size=world_size,
    group=ep_group,
)

# 后续使用与单卡相同，solve_probs 内部会自动 allreduce workload
mapped_idx = planner.run(idx, avail_counter)
```

## 注意事项

1. **首次运行 JIT 编译**：首次创建 Planner 时会触发 NVRTC 编译 CUDA 内核（数秒），后续通过缓存跳过。
2. **r2o 必须在 CUDA 上**：`redundant_to_original` 需为 int32 类型且存储在 CUDA 设备上。
3. **n_routed_experts 计算**：物理专家总数 = 逻辑专家数 + 每 rank 冗余数 × ep_size，确保每 rank 有足够的副本槽位。
4. **avail_counter 监控**：实际部署中应监控 `avail_counter / n_group` 的比值，若频繁低于 1.0 说明 LP 经常不可行，可能需要调整拓扑。
5. **n_sms 参数**：`run()` 不传 n_sms 时会自动查询当前设备 SM 数量；分步执行时需手动获取。

相关参考：
- API 参考
- 拓扑配置示例
- 拓扑感知路由概念
