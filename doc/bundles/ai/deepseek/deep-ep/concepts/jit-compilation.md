---
type: concept
scope: deep-ep
name: JIT 编译系统
version: "2.1.0"
source: csrc/jit/, csrc/kernels/elastic/, csrc/kernels/backend/
description: DeepEP 运行时 CUDA 内核 JIT 编译的设计原理、CRTP 启动器框架、内核缓存机制，以及为什么通信内核需要 JIT
---

# JIT 编译系统

DeepEP 的高性能很大程度上归功于其 JIT（Just-In-Time）编译系统。该系统在运行时根据实际硬件拓扑和模型参数生成最优 CUDA 内核，避免了预编译所有参数组合的不可行性。

## 为什么通信内核需要 JIT

MoE 通信内核的性能高度依赖于一组**运行时常量**——这些值在编译 DeepEP 时是未知的，只有在实际运行时才能确定：

| 参数 | 影响 | 示例值 |
|------|------|--------|
| `num_experts` | 专家循环展开、共享内存布局 | 64, 128, 256 |
| `num_topk` | Top-k 循环展开 | 1, 4, 8 |
| `hidden` | 向量化加载宽度、寄存器分配 | 4096, 7168 |
| `num_sms` | Grid 维度、信道数 | 4-132（因 GPU 型号而异） |
| `num_qps` | RDMA QP 并行度 | 9, 17, 65, 129 |
| `is_scaleup_nvlink` | 是否使用 NVLink 路径 | true/false |
| `use_fp8` | 数据类型、缩放因子处理 | true/false |
| `num_sf_packs` | FP8 缩放因子包数 | hidden/128 |
| GPU 架构 | 指令集、TMA 支持 | sm_90a, sm_100a |

这些参数的笛卡尔积组合空间极大（仅 num_experts × num_topk × hidden × num_sms 就有数千种组合），预编译所有变体既不现实也会导致包体积膨胀。更重要的是，这些参数作为**编译时常量**可以让 NVCC 进行：

- **循环完全展开**：消除循环计数器和分支开销
- **常量传播**：将除法/取模优化为位运算和乘法
- **寄存器最优分配**：根据已知数据大小分配寄存器，减少寄存器溢出
- **共享内存静态计算**：编译时确定 shared memory 大小和偏移
- **模板特化**：为不同路径生成专用代码，消除运行时分支

JIT 编译使得每个部署场景都能获得与"手写专用内核"相当的性能。

## 系统架构

JIT 系统位于 `csrc/jit/`，命名空间 `deep_ep::jit`，由五个核心模块构成：

```
┌─────────────────────────────────────────────────────────┐
│                    LaunchRuntime (CRTP)                  │
│  generate() → compile() → cache_lookup() → launch()     │
└───────────┬─────────────────────────────────────────────┘
            │
    ┌───────┴───────┐
    ▼               ▼
┌────────┐   ┌─────────────┐
│Compiler│   │KernelRuntime │
│(NVCC)  │   │Cache        │
└───┬────┘   └──────┬──────┘
    │               │
    ▼               ▼
┌──────────────────────────────────────────┐
│           KernelRuntime                  │
│  (CUBIN loading, symbol resolution)      │
└──────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────┐
│           DeviceRuntime                  │
│  (GPU properties: SM count, clock, arch) │
└──────────────────────────────────────────┘
```

## CRTP 启动器框架

所有通信内核通过 CRTP（Curiously Recurring Template Pattern，奇异递归模板模式）基类 `LaunchRuntime<Derived>` 统一启动。这是 JIT 系统的核心设计模式。

### 工作原理

```cpp
// 基类：通用的 JIT 编译 + 启动流程
template<typename Derived>
class LaunchRuntime {
public:
    // 1. 生成代码 → 编译 → 缓存查找 → 启动内核
    static void launch(KernelRuntime* kernel_runtime, const Args& args,
                       cudaStream_t stream = nullptr) {
        // 调用派生类的 generate_impl 生成 CUDA C++ 代码
        std::string code = Derived::generate_impl(args);

        // 附加 include 路径哈希（头文件变化时自动重编译）
        code += generate_include_hash();

        // 通过编译器编译或从缓存加载
        auto kernel = compiler->build(Derived::kernel_name, code);

        // 调用派生类的 launch_impl 启动内核
        Derived::launch_impl(kernel, args, stream);
    }
};

// 派生类：定义具体内核的代码生成和启动配置
class DispatchRuntime : public LaunchRuntime<DispatchRuntime> {
public:
    static constexpr const char* kernel_name = "dispatch_kernel";

    static std::string generate_impl(const DispatchArgs& args) {
        // 根据模板参数生成 CUDA C++ 源代码
        // 参数如 num_qps, num_topk, num_experts 等在代码中作为常量
        return generate_dispatch_code(args);
    }

    static void launch_impl(KernelRuntime* kernel, const DispatchArgs& args,
                            cudaStream_t stream) {
        LaunchArgs launch_args = {
            .grid_dim = {args.num_sms, args.num_channels_per_sm},
            .num_threads = 1024,
            .smem_size = calculate_smem_size(args),
            .cluster_dim = 1,
            .cooperative = false,
            .pdl_enabled = false,
        };
        launch_kernel(kernel, launch_args, stream, args...);
    }
};
```

### CRTP 的优势

1. **零开销静态多态**：编译时确定调用目标，无虚函数开销
2. **代码复用**：基类统一处理代码生成→编译→缓存→启动的通用流程
3. **类型安全**：派生类必须实现 `generate_impl` 和 `launch_impl`，编译期检查
4. **易扩展**：新增内核只需继承 `LaunchRuntime<NewKernel>` 并实现两个方法

### ElasticBuffer 内核清单

每个通信操作对应一个或多个 `LaunchRuntime` 派生类：

| 操作 | 启动器类 | 线程数 | 说明 |
|------|---------|--------|------|
| Barrier | `BarrierRuntime` | 模板参数 | GPU 级同步屏障 |
| Dispatch | `DispatchRuntime` | 1024 | Token 数据推送到目标 rank |
| Dispatch Epilogue | `DispatchCopyEpilogueRuntime` | 模板参数 | 中间缓冲→最终接收张量拷贝 |
| Combine | `CombineRuntime` | 1024 | 专家输出推送到源 rank |
| Combine Epilogue | `CombineReduceEpilogueRuntime` | 模板参数 | 源 rank 加权规约 |
| Engram Fetch | `EngramFetchRuntime` | 1024 | 远程 KV 条目 RDMA 获取 |
| Engram Wait | `EngramFetchWaitRuntime` | 1024 | 等待 Engram RDMA 完成 |
| PP Send | `PPSendRuntime` | 32 | 流水线并行发送 |
| PP Recv | `PPRecvRuntime` | 32 | 流水线并行接收 |

## 代码生成

`generate_impl` 方法生成 CUDA C++ 源代码字符串。代码中包含：

1. **头文件包含**：`#include` DeepEP 的 CUDA 头文件（内核实现、通信原语、数据结构等）
2. **模板参数**：将运行时常量作为 `constexpr` 或模板参数嵌入代码
3. **内核函数**：实际的 CUDA `__global__` 函数实现
4. **入口函数**：`extern "C"` 导出的 C 链接入口点，供 KernelRuntime 查找

例如，dispatch 内核的代码生成会产生类似如下的代码（伪代码）：

```cpp
#include <deep_ep/kernels/backend/api.cuh>
#include <deep_ep/kernels/elastic/dispatch_impl.cuh>

constexpr int kNumQPs = 17;
constexpr int kNumMaxTokensPerRank = 2048;
constexpr int kNumHiddenBytes = 8192;  // 4096 * sizeof(bfloat16)
constexpr int kNumTopk = 8;
constexpr int kNumExperts = 64;
constexpr int kNumThreads = 1024;

extern "C" __global__ void __launch_bounds__(1024)
dispatch_kernel(/* kernel arguments */) {
    dispatch_kernel_impl<kNumQPs, kNumMaxTokensPerRank, kNumHiddenBytes,
                         /* ... */>(/* arguments */);
}
```

## 编译与缓存

### 编译流程

1. 将生成的代码写入临时目录的 `kernel.cu` 文件
2. 调用 NVCC 编译器编译为 `kernel.cubin`
3. 编译选项自动包含：
   - GPU 架构标志（如 `-arch=sm_90a`）
   - DeepEP include 路径
   - 优化标志（`-O3` 等）
4. 编译完成后，通过 `KernelRuntime` 加载 CUBIN

### 缓存机制

`KernelRuntimeCache` 基于目录路径缓存已编译的内核：

- 使用 `unordered_map<string, shared_ptr<KernelRuntime>>` 存储缓存
- 缓存键为编译输出目录路径（包含参数编码）
- `check_validity()` 检查 `kernel.cu` 和 `kernel.cubin` 是否同时存在
- Include 路径哈希嵌入代码中，当头文件变化时，代码内容变化导致缓存键变化，自动触发重编译

调试缓存行为：
```bash
export EP_JIT_DEBUG=1                  # 打印生成的代码和启动配置
export EP_JIT_PRINT_COMPILER_COMMAND=1 # 打印 NVCC 编译命令
```

### 缓存目录

JIT 缓存目录由环境变量 `EP_JIT_CACHE_DIR` 控制，在 `setup.py` 安装时被烘焙为默认值。缓存按内核参数组织，相同参数的内核只编译一次，后续进程可以复用已编译的 CUBIN。

## 内核加载与启动

### CUBIN 加载

`KernelRuntime` 从编译输出目录加载 CUBIN 文件：

1. 使用 `cuobjdump -symbols` 解析 CUBIN 中的符号表
2. 找到唯一的入口符号（排除 `vprintf`、`__instantiate_kernel`、`__internal`、`__assertfail` 等内部符号）
3. 根据 CUDA 版本选择加载方式：
   - CUDA ≥ 12.8 且 `EP_JIT_USE_RUNTIME_API`：使用 CUDA Runtime API（`cudaLibrary_t`/`cudaKernel_t`）
   - 其他：使用 CUDA Driver API（`CUmodule`/`CUfunction`）

### 启动配置

`LaunchArgs` 结构体配置内核启动参数：

| 字段 | 说明 |
|------|------|
| `grid_dim` | Grid 维度 `(grid_x, grid_y)`，通常为 `(num_sms, num_channels_per_sm)` |
| `num_threads` | Block 线程数，dispatch/combine 为 1024，PP 为 32 |
| `smem_size` | 动态共享内存大小（字节） |
| `cluster_dim` | Cluster 维度（用于 DSAs，如 Hopper 的 Distributed Shared Memory） |
| `cooperative` | 是否使用协作启动（cooperative launch） |
| `pdl_enabled` | 是否启用 Programmatic Dependent Launch（SM100+） |

`construct_launch_config` 函数将这些参数转换为 CUDA 启动配置，支持 cluster launch、cooperative groups 和 PDL 属性。

## Include 解析

`IncludeParser` 处理 `#include` 指令的解析，确保：
- 正确找到 DeepEP 头文件路径
- 计算 include 文件的哈希值用于缓存失效
- 支持 CUDA 系统头文件路径

## 初始化时机

JIT 系统在包导入时初始化：

```python
# deep_ep/__init__.py
def init_jit():
    import deep_ep._C as _C
    _C.init_jit(
        library_root_path,   # deep_ep 包目录
        find_cuda_home(),    # CUDA 安装路径
        find_nccl_root(),    # NCCL 安装路径
    )

init_jit()  # 导入时自动执行
```

初始化流程：
1. `Compiler::prepare_init`：定位 NVCC 编译器
2. `KernelRuntime::prepare_init`：准备 CUBIN 加载环境
3. `IncludeParser::prepare_init`：设置 include 搜索路径

首次调用某个内核时才会触发 JIT 编译（惰性编译），后续调用命中缓存。

## 性能影响

JIT 编译的开销是一次性的：
- **首次调用**：NVCC 编译一个内核通常需要 1-5 秒
- **后续调用**：缓存命中，直接加载 CUBIN，开销 < 1ms
- **跨进程复用**：缓存文件写入磁盘，不同进程可以共享

因此，JIT 编译开销在长周期训练中可以完全忽略（训练运行数小时甚至数天，首次编译的几秒开销占比极小）。推理场景中，建议在服务启动时预热（warmup）所有需要的内核变体，避免首次请求延迟。

## 相关参考

- [JIT 编译系统 API](/ai/deepseek/deep-ep/references/jit-system)
- [ElasticBuffer API](/ai/deepseek/deep-ep/references/buffer-elastic)
- [架构概述](overview.md)
- [Dispatch/Combine 流程](dispatch-combine.md)
