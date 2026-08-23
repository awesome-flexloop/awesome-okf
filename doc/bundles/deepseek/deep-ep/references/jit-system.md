---
type: reference
scope: deep-ep
name: JIT 编译系统
version: "2.1.0"
source: csrc/jit/, csrc/kernels/elastic/
description: DeepEP 运行时 CUDA 内核 JIT 编译系统，包括编译器、内核缓存、运行时加载、CRTP 启动器框架
---

# JIT 编译系统参考

DeepEP 使用 JIT（Just-In-Time）编译系统在运行时根据实际配置（专家数、top-k、hidden 维度、SM 数、QP 数等）生成最优 CUDA 内核，避免预编译所有参数组合的不可行性。

## 系统架构

JIT 系统位于 `csrc/jit/`，命名空间 `deep_ep::jit`，由四个核心组件构成：

```
┌─────────────┐     ┌──────────────┐     ┌───────────────┐     ┌──────────────┐
│  NVCCCompiler│────▶│KernelRuntime │────▶│KernelRuntime  │────▶│ LaunchRuntime│
│  (代码编译)   │     │  (CUBIN加载)  │     │Cache (内核缓存)│     │ (CRTP启动器)  │
└─────────────┘     └──────────────┘     └───────────────┘     └──────────────┘
```

## 初始化

包导入时调用 `_C.init_jit(library_root_path, cuda_home_path, nccl_root_path)`，依次初始化：

1. **Compiler::prepare_init**：准备 NVCC 编译器路径和编译选项
2. **KernelRuntime::prepare_init**：准备内核运行时加载环境
3. **IncludeParser::prepare_init**：准备 include 路径解析

### 持久化环境变量

以下环境变量在 `setup.py` 安装时被捕获并烘焙到包中作为默认值：

| 环境变量 | 说明 |
|----------|------|
| `EP_JIT_CACHE_DIR` | JIT 编译缓存目录 |
| `EP_JIT_PRINT_COMPILER_COMMAND` | 是否打印编译命令 |
| `EP_NUM_TOPK_IDX_BITS` | Top-k 索引位宽（默认 64） |
| `EP_NCCL_ROOT_DIR` | NCCL 安装根目录 |

运行时可通过 `EP_JIT_DEBUG`（默认 0）控制调试输出，非零时打印生成的内核代码和启动配置。

---

## DeviceRuntime

```cpp
class DeviceRuntime {
    int get_clock_rate();        // GPU 时钟频率（Hz，从 kHz 转换）
    int get_num_smem_bytes();    // 每 block 最大动态共享内存字节数
    int get_num_sms();           // SM 数量
    std::string get_arch();      // 架构字符串（如 "90a"、"100a"）
};
```

全局静态变量 `device_runtime` 使用 `LazyInit<DeviceRuntime>` 懒初始化，提供设备属性查询。

GPU 超时通过 `num_gpu_timeout_secs * device_runtime->get_clock_rate()` 转换为 GPU 周期数，在内核中用于死锁检测。

---

## Compiler / NVCCCompiler

`Compiler` 类（`csrc/jit/compiler.hpp`）负责将 CUDA C++ 源代码编译为 CUBIN：

- 通过 `compiler->build(kernel_name, code)` 编译并返回 `shared_ptr<KernelRuntime>`
- 编译过程：生成临时 `.cu` 文件 → 调用 NVCC 编译为 `.cubin` → 返回 KernelRuntime
- 支持编译缓存：相同参数组合不会重复编译

编译选项自动根据设备架构生成（如 `-arch=sm_90a`），并包含 DeepEP 的 include 路径。

---

## KernelRuntime 与缓存

### KernelRuntime

`KernelRuntime` 类（`csrc/jit/kernel_runtime.hpp`）从编译输出目录加载 CUBIN 文件：

1. 使用 `cuobjdump -symbols` 解析 CUBIN 中的唯一入口符号
2. 排除内部符号：`vprintf`、`__instantiate_kernel`、`__internal`、`__assertfail`
3. 通过 `load_kernel` 加载内核函数句柄

有效性检查：`KernelRuntime::check_validity(dir_path)` 检查目录中 `kernel.cu` 和 `kernel.cubin` 是否同时存在。

### KernelRuntimeCache

```cpp
class KernelRuntimeCache {
    unordered_map<string, shared_ptr<KernelRuntime>> cache;
    shared_ptr<KernelRuntime> find(const string& dir_path);
};
```

全局静态变量 `kernel_runtime_cache` 持有缓存实例，基于目录路径查找已编译内核，避免重复编译。

### 内核句柄类型

通过条件编译区分 CUDA API 版本：

| 条件 | 句柄类型 |
|------|----------|
| CUDA >= 12.8 且 `EP_JIT_USE_RUNTIME_API` | `cudaLibrary_t` / `cudaKernel_t` / `cudaLaunchConfig_t` |
| 其他（默认） | `CUmodule` / `CUfunction` / `CUlaunchConfig`（Driver API） |

定义在 `csrc/jit/handle.hpp`。

---

## LaunchRuntime CRTP 框架

所有通信内核通过 CRTP（Curiously Recurring Template Pattern）基类 `LaunchRuntime<Derived>` 启动：

```cpp
template<typename Derived>
class LaunchRuntime {
    static void generate(/* args */);     // 生成 CUDA C++ 代码
    static void launch(/* args */);       // 配置启动参数并启动内核
};
```

### LaunchArgs

```cpp
struct LaunchArgs {
    pair<int,int> grid_dim;     // (grid_x, grid_y)
    int num_threads;            // block 线程数
    int smem_size;              // 动态共享内存字节数
    int cluster_dim;            // cluster 维度（DSA）
    bool cooperative;           // 是否协作启动
    bool pdl_enabled;           // 是否启用 Programmatic Dependent Launch
};
```

### generate() 流程

1. 调用 `Derived::generate_impl(args)` 生成 CUDA C++ 源代码
2. 附加 include 路径哈希（头文件变化时自动失效缓存）
3. 通过 Compiler 编译为 CUBIN
4. 通过 KernelRuntimeCache 查找或创建 KernelRuntime

### launch() 流程

1. 根据 LaunchArgs 配置 grid/block 维度和共享内存大小
2. 调用 `construct_launch_config` 配置启动参数（支持 cluster dimension、cooperative launch、PDL 属性）
3. 调用 `Derived::launch_impl` 启动内核

---

## ElasticBuffer 内核清单

| 内核运行时类 | 文件 | 功能 | 线程数 |
|-------------|------|------|--------|
| `BarrierRuntime` | `csrc/kernels/elastic/barrier.hpp` | GPU barrier | 模板参数 |
| `DispatchRuntime` | `csrc/kernels/elastic/dispatch.hpp` | Dispatch 数据推送 | 1024 |
| `DispatchCopyEpilogueRuntime` | 同上 | Dispatch 拷贝收尾 | 模板参数 |
| `CombineRuntime` | `csrc/kernels/elastic/combine.hpp` | Combine 数据推送 | 1024 |
| `CombineReduceEpilogueRuntime` | 同上 | Combine 规约收尾 | 模板参数 |
| `EngramFetchRuntime` | `csrc/kernels/elastic/engram.hpp` | Engram 远程获取 | 1024 |
| `EngramFetchWaitRuntime` | 同上 | Engram 获取等待 | 1024 |
| `PPSendRuntime` | `csrc/kernels/elastic/pp_send_recv.hpp` | PP 发送 | 32 |
| `PPRecvRuntime` | 同上 | PP 接收 | 32 |

聚合头文件：`csrc/kernels/elastic/api.hpp`。

### Dispatch 内核模板参数

```cpp
template<int num_qps, int num_max_tokens_per_rank, int num_hidden_bytes,
         int num_sf_packs, int num_topk, int num_experts, int num_threads,
         int num_channels_per_sm, bool is_scaleup_nvlink, int team_tag>
void dispatch_kernel(...)
```

这些模板参数在运行时根据实际配置确定，JIT 为每组参数生成特化内核，实现循环展开和最优寄存器分配。

---

## JIT 编译调试

设置环境变量启用调试：

```bash
export EP_JIT_DEBUG=1        # 打印生成的内核代码和启动配置
export EP_JIT_PRINT_COMPILER_COMMAND=1  # 打印 NVCC 编译命令
```

---

## 相关参考

- [ElasticBuffer API](/deepseek/deep-ep/references/buffer-elastic)
- [JIT 编译概念](/deepseek/deep-ep/concepts/jit-compilation)
- [公开 API 概览](/deepseek/deep-ep/references/api)
