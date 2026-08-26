# LPLB 核心概念

- [总览](/ai/deepseek/lplb/concepts/overview) — LPLB 是什么、解决什么问题、核心机制与架构概览
- [负载均衡问题建模](/ai/deepseek/lplb/concepts/load-balancing-problem) — MoE 专家负载不均衡的数学形式化与 LP 模型
- [LP 求解器设计](/ai/deepseek/lplb/concepts/lp-solver-design) — GPU 端内点法求解器、cuSolverDx/cuBLASDx 集成、JIT 编译
- [拓扑感知路由](/ai/deepseek/lplb/concepts/topology-aware-routing) — Cube/Hypercube/Ring/Torus 拓扑、r2o 矩阵、副本组布局
- [EPLB 集成](/ai/deepseek/lplb/concepts/eplb-integration) — 静态重平衡与动态求解的分层协作、DeepEP 通信集成

```{toctree}
:maxdepth: 7

eplb-integration
load-balancing-problem
lp-solver-design
overview
topology-aware-routing
```
