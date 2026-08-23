# DeepEP 架构洞察

> I-Phase: 基于源码事实提取的深度洞察，从设计意图、架构决策、性能权衡三个维度理解 DeepEP。

## 1. 两代缓冲区的设计哲学演进

### 1.1 V1 Buffer：NVSHMEM 中心化的三模式设计

V1 `Buffer`（[deep_ep/buffers/legacy.py](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/DeepEP/deep_ep/buffers/legacy.py)）基于 NVSHMEM 构建，将通信场景分为三种模式：
- **节点内高吞吐（intranode）**：纯 NVLink，IPC 句柄交换 + P2P 读写
- **节点间高吞吐（internode）**：RDMA + NVLink 分层，通过 NVSHMEM team 实现
- **低延迟模式（low-latency）**：IBGDA（InfiniBand GPU Direct Async）+ 用户态 QP 直接读写，绕过 CPU 参与

这种三模式分离的设计导致 API 分裂：`intranode_dispatch`/`internode_dispatch`/`low_latency_dispatch` 三套内核，用户需要显式选择模式，且缓冲区按 NVLink 段（`num_nvl_bytes`）和 RDMA 段（`num_rdma_bytes`）分别管理。SM 数量通过类变量 `Buffer.num_sms` 全局配置（默认 20，必须为偶数），缺乏自适应能力。

### 1.2 V2 ElasticBuffer：NCCL 对称内存 + 统一架构

V2 `ElasticBuffer`（[deep_ep/buffers/elastic.py](file:///d:/spaces/SpecWeave/external/libs/ai/deepseek-ai/DeepEP/deep_ep/buffers/elastic.py)）是一次根本性的架构重写：

**核心转变**：从 NVSHMEM 对称内存迁移到 NCCL 对称内存（`NCCLSymmetricMemoryContext`）。这一转变的原因包括：
1. **NCCL 生态集成**：DeepEP 可以直接复用 PyTorch 已有的 NCCL 通信器（通过 `EP_REUSE_NCCL_COMM` 环境变量控制，默认启用），避免 NVSHMEM 与 NCCL 共存的资源冲突
2. **统一内存布局**：`[[[Workspace] GPU buffer] CPU buffer]` 三段式布局，GPU 和 CPU 缓冲区在同一对称内存空间中管理，支持 Engram 等需要 CPU 存储的场景
3. **混合模式（Hybrid Mode）**：自动在 scaleout（RDMA 跨节点）和 scaleup（NVLink 节点内）之间分层，无需用户手动选择 intranode/internode

**自动 SM/QP 估算**：V2 引入 `get_theoretical_num_sms()` 基于带宽建模自动计算最优 SM 数量，而非 V1 的固定值。模型考虑 RDMA 带宽、NVLink 带宽、SM 读写带宽，且当 `prefer_overlap_with_compute=True` 时倾向使用更少 SM，将更多 SM 留给计算。

**EPHandle 统一路由元数据**：V1 的 dispatch/combine 使用隐式状态管理，V2 将所有路由元数据封装在 `EPHandle` 中，支持：
- 缓存模式（cached dispatch）：复用 handle 跳过布局重计算
- 确定性排序（deterministic sort）：通过 `EPHandle.deterministic_sort()` 保证相同输入产生相同输出
- Expand 模式：每个 top-k 槽位独立展开，支持灵活的专家分配策略

## 2. 通信拓扑的双层抽象

DeepEP V2 引入了物理域和逻辑域的双层抽象：

### 2.1 物理域：`get_physical_domain_size()`

返回 `(num_rdma_ranks, num_nvlink_ranks)`，反映硬件拓扑：
- `num_rdma_ranks`：需要通过 RDMA 通信的 rank 组数（跨节点）
- `num_nvlink_ranks`：通过 NVLink 直连的 rank 数（节点内）

物理域由 NCCL 通信拓扑自动检测，反映 GPU 间的实际互连方式。

### 2.2 逻辑域：`get_logical_domain_size()`

返回 `(num_scaleout_ranks, num_scaleup_ranks)`，是通信策略的逻辑分组：
- `num_scaleout_ranks`：scaleout 维度的 rank 数（对应 RDMA 跨节点通信）
- `num_scaleup_ranks`：scaleup 维度的 rank 数（对应 NVLink 节点内通信）

逻辑域支持混合模式（hybrid mode）：当 `allow_hybrid_mode=True` 时，节点内使用 NVLink 高带宽通信，节点间使用 RDMA，形成两层通信层次。

每个 rank 在逻辑域中有 `(scaleout_rank_idx, scaleup_rank_idx)` 坐标：
```python
self.scaleout_rank_idx = self.rank_idx // self.num_scaleup_ranks
self.scaleup_rank_idx = self.rank_idx % self.num_scaleup_ranks
```

## 3. Dispatch/Combine 的数据流动模型

### 3.1 Dispatch：Token 路由到专家

Dispatch 的本质是 **all-to-all 个性化通信**：每个 token 根据 top-k 路由决策被发送到持有对应专家的 GPU。

V2 的 dispatch 执行流程：
1. **布局计算**：根据 `topk_idx` 计算每个 rank/每个专家接收的 token 数量（通过 JIT 编译的内核完成前缀和计算）
2. **数据写入**：每个 SM 作为独立的"信道"（channel），通过 NCCL 对称内存的 put 操作将 token 数据直接写入目标 rank 的缓冲区槽位
3. **Copy Epilogue**：将中间缓冲区的数据拷贝到最终的 `recv_x` 张量，并填充 `EPHandle` 中的元数据

关键设计：**信道链表（channel_linked_list）**。混合模式下每个 SM 维护到 scaleup peer 的链表，实现 NVLink 和 RDMA 的流水线传输。

### 3.2 Combine：专家输出聚合回源

Combine 是 dispatch 的逆操作：每个专家计算完输出后，需要将结果聚合回 token 源 GPU，按 top-k 权重加权求和。

V2 的 combine 分为两步内核：
1. **Combine Push**：将每个专家的输出推送到源 rank 的对称内存缓冲区
2. **Combine Reduce Epilogue**：在源 rank 上执行加权规约加法，支持 `allow_multiple_reduction` 控制精度与性能的权衡

`allow_multiple_reduction=True`（默认）允许多次规约减少传输数据量但可能损失精度；`False` 时仅在 epilogue 做一次规约，精度最高但传输量更大。

## 4. 计算-通信重叠机制

DeepEP 的事件系统（`EventOverlap`/`EventHandle`）是实现计算通信重叠的核心。

### 4.1 独立通信流

ElasticBuffer 使用独立的高优先级 CUDA 通信流（通过 `get_global_comm_stream()` 从 CUDA 流池获取）。通信操作在通信流上执行，不阻塞计算流。

### 4.2 EventOverlap 模式

典型的重叠模式：
```python
# Dispatch 在通信流上执行，立即返回
recv_x, _, _, handle, event = buffer.dispatch(x, topk_idx, ...)
# 计算流可以立即做不依赖 dispatch 结果的工作
with event:  # 退出 with 时自动等待通信完成
    expert_output = expert_forward(recv_x)  # 依赖 dispatch 结果，自动等待
# Combine 在通信流上执行
combined_x, _, event = buffer.combine(expert_output, handle, ...)
```

`EventOverlap` 的 `register_hook_after_wait()` 支持在通信完成后插入回调（如确定性排序），使排序在等待通信的流上执行，进一步隐藏延迟。

### 4.3 previous_event 链式等待

`dispatch`/`combine` 接受 `previous_event` 参数，形成事件链：前一个通信事件完成后才开始当前通信，避免多个通信操作竞争网络资源。

## 5. JIT 编译系统的设计

DeepEP 的 JIT 系统（`csrc/jit/`）是其高性能的关键支撑：

### 5.1 为什么需要 JIT

MoE 通信内核的性能高度依赖于运行时常量：专家数量、top-k 值、hidden 维度、SM 数量、QP 数量、是否 FP8、是否混合模式等。这些参数组合空间极大，无法预编译所有变体。JIT 允许根据实际配置生成最优内核：
- 循环展开（基于 `num_topk`、`num_experts` 等编译时常量）
- 模板特化（通过 `LaunchRuntime<Derived>` CRTP 模式）
- 共享内存大小计算（在编译时确定）

### 5.2 CRTP 内核启动器

所有内核运行时类继承 `LaunchRuntime<Derived>`，通过 CRTP（Curiously Recurring Template Pattern）实现静态多态：
- `Derived::generate_impl(args)`：生成 CUDA C++ 源代码字符串
- `Derived::launch_impl(...)`：配置 grid/block/smem 并启动内核
- 基类 `launch()` 方法：处理代码生成 → 缓存查找 → NVCC 编译 → CUBIN 加载 → 内核启动的完整流水线

### 5.3 内核缓存

`KernelRuntimeCache` 基于目录路径缓存已编译的 CUBIN，避免重复编译。`KernelRuntime::check_validity()` 通过检查 `kernel.cu` 和 `kernel.cubin` 的存在性判断缓存是否有效。include 路径哈希附加到代码中，当头文件变化时自动失效重编译。

## 6. 资源管理的精细控制

### 6.1 SM 资源

SM（Streaming Multiprocessor）是 GPU 的核心计算单元。通信内核占用的 SM 越多，通信带宽越高，但留给计算的 SM 越少。V2 的 `get_theoretical_num_sms()` 基于带宽建模平衡这一权衡：
- RDMA 带宽受限：使用更多 SM 填充网络管道
- NVLink 带宽受限：SM 数量与带宽匹配
- `prefer_overlap_with_compute=True`：使用更少 SM（至少 4，偶数），将大部分 SM 留给计算

### 6.2 QP 资源

QP（Queue Pair）是 RDMA 通信的端点。混合模式需要更多 QP（每个 SM 多个 QP 实现多信道并行）：
- 直接模式：`min(num_sms, 9)` 个 QP
- 混合模式：`num_sms * 16 + 1` 个 QP
- 自动分配：65（支持快速 RDMA 原子）或 129 个 QP

### 6.3 超时保护

GPU 超时通过 `num_gpu_timeout_secs * device_runtime->get_clock_rate()` 转换为 GPU 周期数，在内核中检测死锁或通信故障。CPU 超时（默认 300 秒）用于 CPU 侧同步操作。

## 7. Engram：条件内存与远程 KV 缓存

Engram 是 DeepSeek-V4/R1 引入的条件内存机制，允许将 KV 缓存存储在远程 GPU 的 CPU 内存中：
- `engram_write()`：将 KV 缓存数据写入本地 CPU 缓冲区
- `engram_fetch()`：通过 RDMA 从远程 rank 的 CPU 内存获取 KV 条目，返回一个等待句柄

这一机制使得 MoE 推理时可以将非活跃专家的 KV 缓存卸载到 CPU 内存，仅在需要时通过 RDMA 拉取，大幅降低 GPU 内存占用。

## 8. 生态位与 DeepSeek 训练栈

DeepEP 在 DeepSeek 训练/推理栈中的定位：

| 组件 | 职责 | 与 DeepEP 的关系 |
|------|------|-----------------|
| [DeepGEMM](/deepseek/deep-gemm) | MoE 分组 GEMM 内核 | 在 dispatch 之后、combine 之前执行专家计算 |
| [LPLB](/deepseek/lplb) | 专家负载均衡器 | 决定 top-k 路由，输出 `topk_idx` 给 dispatch |
| [DualPipe](/deepseek/dual-pipe) | 双向流水线并行 | EP + PP 混合并行，ElasticBuffer 提供 PP send/recv |
| DeepEP | EP 通信 | dispatch/combine/Engram/PP/AGRS 统一通信层 |

DeepEP 的 ElasticBuffer 不仅服务于 EP dispatch/combine，还通过 PP send/recv 和 AGRS 统一了流水线并行和序列并行的通信需求，成为 DeepSeek 混合并行训练的通信基石。
