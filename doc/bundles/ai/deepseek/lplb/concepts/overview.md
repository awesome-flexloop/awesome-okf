---
type: concept
scope: lplb
name: overview
version: "0.1.0"
source: https://github.com/deepseek-ai/LPLB
description: LPLB 总览——基于线性规划的 MoE 专家负载均衡库
---

# LPLB 总览

## 什么是 LPLB

LPLB（Linear-Programming-based Load Balancer）是 DeepSeek 开发的 MoE（Mixture-of-Experts）专家并行负载均衡库。它使用线性规划（LP）在 GPU 上实时求解最优的专家复制与 token 分配策略，解决大模型训练中"热专家"导致的负载不均衡问题。

- **版本**：0.1.0（早期研究阶段）
- **作者**：Huanqi Cao (caohuanqi@deepseek.com)
- **核心依赖**：PyTorch、CUDA Toolkit ≥ 12.6.3（含 cuSolverDx）

## 解决的问题

在 MoE 模型训练中，router 网络为每个 token 选择 top-k 个专家。由于路由决策的动态性和数据分布不均匀，某些专家收到远多于其他专家的 token（"热专家"），导致：

1. **计算不均衡**：各 GPU 专家计算量差异大，grouped GEMM 尾延迟由最慢 GPU 决定。
2. **通信瓶颈**：all-to-all 通信量不均匀，部分 GPU 成为热点。
3. **训练效率下降**：整体吞吐受限于最重载的 GPU。

传统 EPLB 通过定期重排专家、复制热专家缓解静态不均衡，但无法应对 per-batch 动态波动。LPLB 引入**实时 LP 优化**，每个 batch 动态分配 token 到原始专家或其副本，最小化最大专家负载。

## 核心机制

LPLB 工作流程分三阶段：

```
模型输出逻辑专家索引 idx
        │
        ▼
┌─────────────────────┐
│ 1. count_workload   │ ← GPU 原子计数统计各专家负载
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│ 2. solve_probs      │ ← 内点法 LP 求解最优分配比例
│    (cuSolverDx)     │   （全 GPU，无 CPU 回传）
└─────────┬───────────┘
          ▼
┌─────────────────────┐
│ 3. weighted_select  │ ← 加权哈希路由 token 到物理专家
│    _target          │   （原始或副本）
└─────────┬───────────┘
          ▼
物理专家索引 → DeepEP dispatch → 专家计算
```

### 冗余专家与拓扑

副本布局由预定义拓扑（r2o 矩阵）静态确定，在 GPU 间形成图结构边：

- **Cube**：8 GPU 立方体，节点内 NVLink 场景
- **Hypercube**：16 GPU 超立方体，双节点场景
- **Torus**：二维环面，多节点全局均衡
- **Ring**：简单环形，用于验证

详见 [拓扑感知路由](/ai/deepseek/lplb/concepts/topology-aware-routing)。

### GPU 端 LP 求解

- NVRTC 运行时编译，拓扑参数作为编译期常量，生成特化 CUDA 内核。
- 内点法（5 步迭代）使用 cuSolverDx Cholesky 分解和 cuBLASDx 矩阵乘法，在单 SM block 共享内存中完成。
- 节点内约 100µs 完成一次求解。

详见 [LP 求解器设计](/ai/deepseek/lplb/concepts/lp-solver-design)。

### 加权哈希路由

LP 得到分配比例后，token 通过确定性加权哈希分配到原始专家或副本，保证路由决策完全在 GPU 上完成。

## 与 EPLB 的关系

- **EPLB（静态层）**：定期根据历史负载重排专家、复制热专家，决定"哪些专家需要副本"。
- **LPLB（动态层）**：每个 batch 实时求解 LP，决定"当前 batch 的 token 如何在原始和副本间分配"。

两者互补：EPLB 处理慢时间尺度的结构性不均衡，LPLB 处理快时间尺度的 per-batch 波动。详见 [EPLB 集成](/ai/deepseek/lplb/concepts/eplb-integration)。

## 与 Deep 生态的关系

| 组件 | 路径 | 关系 |
|---|---|---|
| DeepEP | [/deepseek/deep-ep/](/ai/deepseek/deep-ep/) | EP 通信库，提供 all-to-all 和 NVSHMEM 通信。LPLB 复用其通信缓冲区优化 workload 同步。 |
| DeepGEMM | [/deepseek/deep-gemm/](/ai/deepseek/deep-gemm/) | MoE grouped GEMM 计算库。LPLB 的均衡直接影响 DeepGEMM 尾延迟。 |

## 架构概览

```
lplb/
├── __init__.py          # 导出 Planner 类
├── planner.py           # Planner 类核心 API
├── eplb.py              # EPLB 静态重平衡算法
└── resources/
    ├── csrc-tmpl/minilp.cu   # CUDA 内核模板
    └── mathdx/               # cuSolverDx/cuBLASDx 库
csrc/
├── plugin.cpp           # C++ 扩展：JIT 编译、内核加载、绑定
└── deepep_rt_slim.h     # DeepEP NVSHMEM 最小声明
```

## 使用入口

```python
from lplb import Planner

r2o = torch.tensor([
    [3, 0, 1, 2, 7, 4, 5, 6],
    [6, 7, 4, 5, 0, 1, 2, 3],
]).T.int().cuda()

planner = Planner(r2o, n_routed_experts, n_logical_experts, ep_size, group=ep_group)
avail_counter = torch.zeros((), dtype=torch.int32, device='cuda')
redirected_indices = planner.run(indices, avail_counter)
```

详见 [API 参考](/ai/deepseek/lplb/references/api) 和 [基础规划示例](/ai/deepseek/lplb/examples/basic-planning)。

## 已知限制

1. 仅平衡 token 数量，不考虑 grouped GEMM 非线性时间开销。
2. 求解延迟约 100µs（节点内），对小 batch 可能不可忽略。
3. 极端全局不均衡时可能不如纯 EPLB。
4. 项目处于早期研究阶段。

## 进一步阅读

- [负载均衡问题建模](/ai/deepseek/lplb/concepts/load-balancing-problem)
- [LP 求解器设计](/ai/deepseek/lplb/concepts/lp-solver-design)
- [拓扑感知路由](/ai/deepseek/lplb/concepts/topology-aware-routing)
- [EPLB 集成](/ai/deepseek/lplb/concepts/eplb-integration)
