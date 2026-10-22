---
type: concept
scope: deepinfer
name: DeepInfer 引擎架构
version: "0.1.0"
source: deepinfer/engine/, csrc/engine/, deepinfer/_C/engine.pyi, doc/inference_deployment_qa.md
description: LLMEngine 引擎组织、C++ 调度器与 ZOS 零开销异步调度流水线
sources:
  - id: deepseek-zhihu-report
    resource: https://zhuanlan.zhihu.com/p/2095560295930508953
    title: DeepSeek V4.1 Flash 大规模推理部署实践
---

# 引擎架构与零开销调度

DeepInfer 的引擎是"Python 壳 + C++ 芯"的组织：Python 层 `LLMEngine` 负责配置与编排，调度器、块管理器等性能敏感组件全部下沉到 C++ 扩展，通过 `.pyi` 存根暴露类型契约。

---

## 一、引擎组件地图

| 组件 | 位置 | 职责 |
|---|---|---|
| `LLMEngine` | `deepinfer/engine/llm_engine.py` | 主引擎类（约 1029 行），直接从 C++ 扩展导入调度器组件 |
| `EngineArgs` | `deepinfer/engine/arg_utils.py` | 引擎参数与环境变量注入（ZOS 等默认值在此生效） |
| EngineType | `deepinfer/engine/engine_type.py` | NORMAL / PROMPT / COMPLETION 三形态 |
| `Scheduler` | `csrc/engine/scheduler.hpp` + `pybind_scheduler.cpp` | 批调度状态机（C++ 实现） |
| `BlockManager` | `csrc/engine/block_manager.hpp` | KV block 分配 |
| `RequestOutputPool` | `csrc/engine/` | 请求输出池（返回值多为零拷贝借用缓冲） |
| ZOS | `csrc/engine/zos.cpp/.hpp` | Zero-Overhead Scheduling 实现 |
| `stats_logger` | `deepinfer/engine/stats_logger.py` | 周期性日志（moe_lb 等指标在此读取） |

C++ 接口契约集中在 `deepinfer/_C/engine.pyi`（735 行，最核心存根），`schedule()`/`process_outputs()`/`update_mtp_runtime()` 等方法返回值多为零拷贝借用缓冲。

---

## 二、ZOS 零开销调度流水线

### 2.1 问题：Decode 步间的 GPU 空闲

Decode 第 N 步的朴素流程是：

```
schedule(N) → forward(N) → sample(N) → post-process(N)
```

其中 schedule 与 post-process 是纯 CPU 逻辑，但 post-process(N) 之前必须 GPU-CPU 同步拿到 sample(N) 的结果——于是 post-process(N) 与 schedule(N+1) 执行期间 GPU 处于空闲。

### 2.2 解法：CPU/GPU 流水线重叠

DeepInfer 参考已有实现（SGLang、Nanoflow），通过异步调度把流水线重叠起来：

```
GPU: forward(N) ──────→ sample(N) ──────→ forward(N+1) ...
CPU:            schedule(N+1) → launch_forward(N+1) → post-process(N-1) → launch_sample(N+1) ...
```

GPU 执行 `forward(N) → sample(N)` 的同时，CPU 同步执行 `schedule(N+1) → launch_forward(N+1) → post-process(N-1) → launch_sample(N+1)`，**GPU 全程无空闲**。

### 2.3 开关与生效路径

- 环境变量：`DEEPINFER_ZERO_OVERHEAD_SCHEDULING`，由 `arg_utils.py` 按引擎类型 `os.environ.setdefault` 注入——`EngineType.NORMAL/COMPLETION` 默认置 "1"（即 README 所述"默认开启"）。
- 生效路径：`model_metadata_utils.py` 选择 `prepare_decode_v4_zos` → `worker/worker.py` → `config.py` 中 `scheduler_overhead = nextn + (nextn + 1)` 个 token 的预算。

---

## 三、与推测解码的联动

ZOS 与 DSpark 变长验证深度耦合（详见[DSpark 推测解码](speculative-decoding.md)）：schedule(N+1) 执行时，第 N 步各 draft token 的 confidence 尚未回传，因此 CPU 调度只确定**总预算**，逐请求验证长度改由 GPU 上一个 TileLang kernel 重算（累乘、全局排序取 top-k、融合 remap scatter），结果回写 pinned buffer。

---

## 四、其他引擎层机制

- **三形态引擎**：NORMAL（常规）/ PROMPT / COMPLETION 分别对应不同工作负载形态，ZOS 与多模态内存池的默认值按形态区分。
- **CUDA Graph**：`cuda_graph_runner.py` 与 DSpark 专用的 `dflash_cuda_graph_runner.py`；`DEEPINFER_ENFORCE_EAGER` / `DEEPINFER_DFLASH_ENFORCE_EAGER` 可关闭图捕获换取调试便利。
- **性能观测**：`stats_logger` 周期输出 moe_lb 等指标；`csrc/graph_timer/` 提供按平台的性能计时（`graph_timer_cuda.cpp` / `graph_timer_asc.cpp`）。
- **分布式广播**：`deepinfer/distributed/shm_broadcast.py` 提供 ZMQ XPUB/SUB + 共享内存广播（源自 vLLM），用于引擎与前端进程间通信。
