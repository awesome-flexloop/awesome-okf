---
type: bundle
okf_version: "0.2"
scope: lplb
name: lplb
version: "0.1.0"
source: https://github.com/deepseek-ai/LPLB
description: LPLB（Linear-Programming-based Load Balancer）——DeepSeek 开源的基于线性规划的 MoE 专家并行负载均衡库，使用 CUDA 端内点法 LP 求解器和拓扑感知路由，实时优化专家负载分配
---

# LPLB

**LPLB（Linear-Programming-based Load Balancer）** 是 DeepSeek 开发的开源 MoE（Mixture-of-Experts）专家并行负载均衡库。它通过线性规划（LP）在 GPU 上实时求解最优的专家复制与 token 分配策略，解决大模型训练中热专家（hot experts）导致的负载不均衡问题。

- **版本**：0.1.0（早期研究阶段）
- **作者**：Huanqi Cao (caohuanqi@deepseek.com)
- **核心依赖**：PyTorch、CUDA ≥ 12.6.3（含 cuSolverDx）
- **可选依赖**：DeepEP（NVSHMEM 通信加速）

## 核心特性

- **GPU 端 LP 求解**：基于 cuSolverDx/cuBLASDx 的内点法求解器，NVRTC JIT 编译特化内核，单 SM block 在 ~100µs 内完成 LP 求解，零 CPU 回传。
- **拓扑感知路由**：支持 Cube（立方体）、Hypercube（超立方体）、Ring（环形）、Torus（二维环面）等多种预定义拓扑，支持自定义拓扑矩阵。
- **分层负载均衡**：嵌入 EPLB 算法做慢时间尺度静态重排+复制，LPLB LP 求解做快时间尺度动态 token 分配。
- **DeepEP 集成**：通过 NVSHMEM 实现 kernel 内部的跨节点/节点内 workload 聚合，替代 torch.distributed.all_reduce 降低通信延迟。
- **加权哈希路由**：确定性加权哈希将 token 分配到原始专家或副本，分配误差 < 5%。

## 相关 Deep 生态组件

| 组件 | 路径 | 关系 |
|---|---|---|
| DeepEP | [/deepseek/deep-ep/](/ai/deepseek/deep-ep/) | EP 通信库，提供高效 all-to-all 和 NVSHMEM 通信原语 |
| DeepGEMM | [/deepseek/deep-gemm/](/ai/deepseek/deep-gemm/) | MoE grouped GEMM 计算内核，LPLB 均衡直接影响其尾延迟 |

## 快速开始

```python
import torch
from lplb import Planner

# 定义 Cube8P2E 拓扑
r2o = torch.tensor([
    [3, 0, 1, 2, 7, 4, 5, 6],
    [6, 7, 4, 5, 0, 1, 2, 3],
]).T.int().cuda()

# 创建 Planner
planner = Planner(
    redundant_to_original=r2o,
    n_routed_experts=320,    # 256 逻辑 + 2×32 冗余
    n_logical_routed_experts=256,
    ep_size=32,
)

# 执行负载均衡
idx = torch.randint(0, 256, (4096, 48), device='cuda')
avail_counter = torch.zeros((), dtype=torch.int32, device='cuda')
mapped_idx = planner.run(idx, avail_counter)
```

## 文档导航

### 核心概念

- [总览](/ai/deepseek/lplb/concepts/overview) — LPLB 是什么、解决什么问题、核心机制
- [负载均衡问题建模](/ai/deepseek/lplb/concepts/load-balancing-problem) — MoE 负载不均衡的数学形式化与 LP 模型
- [LP 求解器设计](/ai/deepseek/lplb/concepts/lp-solver-design) — GPU 端内点法、cuSolverDx 集成、JIT 编译架构
- [拓扑感知路由](/ai/deepseek/lplb/concepts/topology-aware-routing) — 拓扑矩阵语义、预定义拓扑、副本组布局
- [EPLB 集成](/ai/deepseek/lplb/concepts/eplb-integration) — 静态重平衡与动态求解的分层协作

### API 参考

- [API 参考](/ai/deepseek/lplb/references/api) — Planner 类、EPLB 函数、CompiledSolver 接口
- [LP 求解器](/ai/deepseek/lplb/references/lp-solver) — CUDA 内核、JIT 编译流程、NVSHMEM 通信
- [拓扑配置](/ai/deepseek/lplb/references/topology) — r2o 矩阵约束、内置拓扑、副本组机制

### 使用示例

- [基础专家复制规划](/ai/deepseek/lplb/examples/basic-planning) — 创建 Planner、分步执行、验证均衡效果
- [拓扑感知配置](/ai/deepseek/lplb/examples/topology-config) — 各种拓扑使用、自定义拓扑、DeepEP 集成

## 目录结构

```
lplb/
├── spec/
│   ├── facts.md           # 源码事实验证清单
│   └── insights.md        # 设计决策与深度洞察
├── concepts/              # 核心概念（5 篇）
├── references/            # API/技术参考（3 篇）
├── examples/              # 使用示例（2 篇）
└── index.md               # 本文件
```

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
spec/facts
spec/insights
```
