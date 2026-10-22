---
type: concept
scope: deepinfer
name: DeepInfer 并行策略
version: "0.1.0"
source: deepinfer/model_executor/parallel_utils/, deepinfer/model_executor/eplb/, deep_cluster/, doc/inference_deployment_qa.md
description: EP/DP/CP/EPLB 并行策略、deep_cluster 硬件探测层与 Wide-EP 生产部署口径
sources:
  - id: deepseek-zhihu-report
    resource: https://zhuanlan.zhihu.com/p/2095560295930508953
    title: DeepSeek V4.1 Flash 大规模推理部署实践
---

# 并行策略：EP / DP / CP / EPLB

DeepInfer 继承 DeepSeek-V3/R1 推理系统的并行骨架：**（超）节点内 MoE 专家并行（EP）+ Attention 数据并行（DP）**，生产部署采用 Prefill 与 Decode 分离的不同并行尺度。

---

## 一、总体并行设计

知乎技术报告给出的系统级选择：

- **（超）节点内 MoE EP**：增大 batch size，提高 GPU 矩阵乘法效率 → 提高吞吐。
- **Vision Encoder / Prefill / Decode 分离部署**：解耦各阶段资源分配，独立控制并分别优化 TTFT 与 TBT。
- **Attention DP（#DP = #EP）**：继承 V3/R1 系统；不同 DP/EP 组间由负载均衡器调度（生产侧组件，见[部署实践](deployment-practice.md)）。

## 二、生产并行口径

| 阶段 | 并行规模 | 原则 |
|---|---|---|
| Prefill | EP2～8 / DP2～8 | 显存足够时用**尽可能小**的 EP/DP |
| Decode | EP64～128 / DP64～128（Wide-EP） | 显卡可用时用**尽可能大**的 EP/DP |
| Vision Encoder | 单卡部署 | 用可用范围内**最便宜**的卡 |

> 部署 Q&A（`doc/inference_deployment_qa.md`）注明：TP/CP 生产暂不使用，框架仍保留 `--cp` 支持（`--cp` 须整除 `ep_size`）。

## 三、代码层实现

### 3.1 parallel_utils/

| 模块 | 职责 |
|---|---|
| `parallel_state.py` | 进程组（PG）管理 |
| `cp.py` | CP（上下文并行）通信 |
| `communication_op.py` | `cp_broadcast_multi_tensor` 等通信算子 |
| `userbuffer.py` | UserBuffer 通信 |
| `nccl_memory.py` | NCCL 通信内存 |

### 3.2 EPLB（专家负载均衡）

`deepinfer/model_executor/eplb/` 提供 `policy.py`（重排策略）+ `shuffle.py`（专家重排执行）：

- **冗余专家机制**：每卡在常驻专家之外多备若干冗余专家放热门专家的副本；`DEEPINFER_OVERRIDE_NUM_EXTRA_EXPERTS` 为冗余专家数下界（实践默认 32），引擎把 `num_routed_experts + num_extra_experts` 向上取整到 `ep_size` 的倍数。
- **对称内存转移**：专家权重在 scale-up network 里经 `symm_mem` 在并行组内转移；`eplb/__init__.py` 设置 `TORCH_SYMMEM_ALLOW_OVERLAPPING_DEVICES=1` 支持对称内存 shuffle。
- **统计窗口**：`DEEPINFER_MOE_LB_STAT_INTERVAL`（默认 128 step）控制 MoE 负载统计间隔；线上实测 moe_lb（最慢 rank/均值）= 1.0320（EP2/DP2）/ 1.0618（EP4/DP4）prefill、1.090（EP64）decode。

### 3.3 deep_cluster 硬件探测层

`deep_cluster/` 是构建期与运行期共用的**硬件发现/拓扑库**，刻意不依赖 torch，以便在 `import torch` 之前完成平台探测：

- `hardware/` 提供 14 个硬件中立函数：`accelerator_kind()`、`get_bf16_tflops_limit()`、`is_sm_major_10()` 等，按 `nvidia.py` / `ascend.py` / `cpu.py` 三实现分发；
- `topology/bind.py` 提供 NUMA 绑定；
- `setup.py` 构建期用它选择 NPU/CUDA 后端；`deepinfer/__init__.py` 运行期用它探测平台标签。

## 四、多机并行

单机示例设置：

```bash
export WORLD_SIZE=1 RANK=0
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
```

并行规模由环境决定：`ep_size = WORLD_SIZE × len(CUDA_VISIBLE_DEVICES)`（`WORLD_SIZE` 为节点数；`CUDA_VISIBLE_DEVICES` 未设时用 `ASCEND_RT_VISIBLE_DEVICES`）。多机 DP 拆分由 `examples/_launch.py` 的 `launch_dp`/`run_dp` 承担——DP ranks 跨节点拆分，本地 stdout 只携带本地 rank。
