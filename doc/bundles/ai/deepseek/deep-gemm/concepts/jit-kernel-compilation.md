---
type: concept
scope: deep-gemm
name: JIT 内核编译系统
version: "2.6.1"
source: csrc/jit/compiler.hpp, csrc/jit/kernel_runtime.hpp, csrc/jit/include_parser.hpp, csrc/jit/cache.hpp, csrc/jit/handle.hpp
description: DeepGEMM 运行时 JIT 编译系统的工作原理，包括代码生成、NVCC/NVRTC 编译、缓存机制和内核加载
---

# JIT 内核编译系统

DeepGEMM 采用运行时 JIT（Just-In-Time）编译策略，在首次调用特定配置的核函数时动态生成 CUDA C++ 源码、编译为 CUBIN、加载并执行。这种设计使得核函数能够针对具体的 GPU 架构、矩阵维度、数据布局进行极致特化，避免了预编译二进制中为兼容多种配置而引入的性能损失。

---

## 一、为什么需要 JIT

传统的核函数发布方式（预编译 .so / .cubin）面临以下困境：

1. **维度组合爆炸**：M、N、K 的可能取值范围极大，预编译所有组合不现实
2. **架构差异**：SM90 和 SM100 的指令集（WGMMA 形状、TMA 行为、cluster launch）有显著差异
3. **布局多样性**：K-major vs MN-major、不同 scaling factor 粒度、UE8M0 打包与否
4. **编译标志选择**：不同 CUDA 版本支持的编译选项不同（如 NVRTC PCH、--device-int128）

JIT 编译在运行时根据实际参数生成精确匹配的核函数，同时通过多层缓存避免重复编译开销。

---

## 二、编译流程

### 2.1 整体流程

```
首次调用 fp8_gemm_nt(M=4096, N=4096, K=8192, ...)
    │
    ▼
┌─────────────────────────────────────────────────┐
│ Step 1: 代码生成 (generate)                       │
│  - LaunchRuntime<Derived>::generate(args)        │
│  - 调用 Derived::generate_impl() 生成 CUDA C++   │
│  - 首次调用时计算 include hash 并缓存             │
│  - 代码头部添加 "// Includes' hash: {hash}"      │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│ Step 2: 缓存查找                                  │
│  - 计算 kernel_signature =                       │
│    "{name}$${compiler_sig}$${flags}$${code}"     │
│  - 查内存缓存 kernel_runtime_cache               │
│  - 查磁盘缓存 ~/.deep_gemm/cache/kernel.{name}.* │
│  - 命中 → 直接返回 KernelRuntime                 │
└──────────────────────┬──────────────────────────┘
                       │ 未命中
                       ▼
┌─────────────────────────────────────────────────┐
│ Step 3: 编译 (compile)                           │
│  - 创建临时目录 tmp_dir                          │
│  - 写入 kernel.cu                                │
│  - NVCC: nvcc -cubin → kernel.cubin (+ ptx/sass) │
│  - NVRTC: nvrtcCompile → 获取 PTX/CUBIN         │
│  - fsync 确保持久化                               │
│  - 原子 rename 到正式缓存目录                     │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│ Step 4: 加载 (KernelRuntime 构造)                │
│  - cuobjdump -symbols 获取入口函数名             │
│  - cuLibraryLoadFromFile / cuModuleLoad         │
│  - cuLibraryGetKernel / cuModuleGetFunction     │
│  - 存入内存缓存                                  │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│ Step 5: 启动 (launch)                            │
│  - 获取当前 CUDA stream                          │
│  - 构造 grid/block dims                          │
│  - construct_launch_config（含 cluster/PDL）    │
│  - cuLaunchKernelEx / cudaLaunchKernelExC       │
└─────────────────────────────────────────────────┘

后续相同配置调用 → Step 2 缓存命中 → Step 5 直接启动
```

### 2.2 代码生成

每个核函数实现通过 CRTP（Curiously Recurring Template Pattern）继承 `LaunchRuntime<Derived>`：

```cpp
// 模板方法模式
template<typename Derived>
class LaunchRuntime {
    static std::string generate(const Args& args) {
        std::string code = Derived::generate_impl(args);
        // 首次调用时计算 include hash
        static std::string include_hash = include_parser->get_hash_value(code);
        return "// Includes' hash value: " + include_hash + "\n" + code;
    }

    static void launch(std::shared_ptr<KernelRuntime> runtime, const Args& args) {
        // 获取 stream、构造 launch config、启动 kernel
        auto stream = get_current_stream();
        auto launch_args = args.launch_args;
        launch_args.enable_pdl &= device_runtime->get_pdl();
        // ... construct dim3 grid/block, launch config ...
        Derived::launch_impl(runtime->kernel, config, args);
    }
};
```

`Derived::generate_impl(args)` 根据输入参数（M、N、K、major 类型、recipe 等）生成特化的 CUDA C++ 代码。JIT 核函数源码位于 `deep_gemm/include/deep_gemm/impls/` 目录，使用 CUTLASS/CUTE 模板库。

### 2.3 Include 依赖 Hash

```cpp
class IncludeParser {
    std::unordered_map<std::string, std::optional<std::string>> cache;

    std::string get_hash_value(const std::string& code, bool exclude_code = true);
    // 1. 正则提取 #include <deep_gemm/...>
    // 2. 递归读取每个被包含的文件
    // 3. 对所有文件内容计算 SHA-256 hash
    // 4. 返回 hex digest
    // 循环 include 检测：cache 中 nullopt 表示正在处理
};
```

Include hash 确保当头文件依赖变化时（如升级 DeepGEMM 版本），旧的缓存自动失效。

---

## 三、编译器对比

### 3.1 NVCC（默认）

| 特性 | 说明 |
|---|---|
| 编译器路径 | `$CUDA_HOME/bin/nvcc`，可通过 `DG_JIT_NVCC_COMPILER` 覆盖 |
| 版本要求 | ≥ 12.3；< 12.9 时打印性能警告 |
| 编译命令 | `nvcc -cubin -std=c++20 -O3 --gpu-architecture=sm_XX ... kernel.cu -o kernel.cubin` |
| 产物 | kernel.cubin（必需），可选 kernel.ptx、kernel.sass（反汇编） |
| 编译速度 | 较慢（外部进程调用） |
| 优化级别 | 完整 nvcc 优化（最高性能） |
| 适用场景 | 生产环境，追求最高性能 |

### 3.2 NVRTC（可选）

| 特性 | 说明 |
|---|---|
| 启用方式 | `DG_JIT_USE_NVRTC=1` 环境变量 |
| 版本要求 | ≥ 12.3 |
| 编译方式 | 进程内调用 `nvrtcCompileProgram`，无需 fork nvcc 进程 |
| 预编译头 | ≥ 12.8 支持 `--pch`，显著加速重复编译 |
| 产物 | PTX（通过 JIT linking）或 CUBIN |
| 编译速度 | 较快（进程内、PCH 加速） |
| 优化级别 | 与 NVCC 相同的后端优化 |
| 适用场景 | 开发调试、快速迭代、首次编译延迟敏感 |

### 3.3 编译标志详解

**通用标志**：
- `-std=c++20`：使用 C++20 标准（concepts、constexpr 等）
- `--diag-suppress=39,161,174,177,186,940`：抑制特定警告
- `--ptxas-options=--register-usage-level=10`：最大寄存器使用（提升 occupancy）
- `-O3`：最高优化级别
- `--expt-relaxed-constexpr`：放宽 constexpr 限制（CUTLASS 需要）
- `--expt-extended-lambda`：扩展 lambda（核函数内 lambda 捕获）

**NVCC 特有**：
- `-I{include_path}`：头文件搜索路径
- `--gpu-architecture=sm_{arch}`：目标架构
- `--compiler-options=-fPIC,-O3,-fconcepts,-Wno-deprecated-declarations,-Wno-abi`：主机编译器选项

**NVRTC 特有**：
- `-I{library_include_path} -I{cuda_home}/include`：两个 include 路径
- `--gpu-architecture=sm_{arch}`：目标架构
- `-default-device`：默认设备端编译
- `--pch`：预编译头（≥ 12.8）
- `--device-int128`：设备端 int128 支持（Blackwell 需要）

**调试标志**：
- `DG_JIT_DEBUG` 或 `DG_JIT_PTXAS_VERBOSE`：追加 `--ptxas-options=--verbose,--warn-on-local-memory-usage`
- `DG_JIT_PTXAS_CHECK`：编译后断言无 local memory 使用
- `DG_JIT_WITH_LINEINFO`：追加 `-Xcompiler -rdynamic -lineinfo`（用于 Nsight Compute profiling）

---

## 四、缓存机制

### 4.1 两级缓存

```
┌─────────────────────────────────────────────┐
│  L1: 内存缓存 (KernelRuntimeCache)           │
│  unordered_map<string, shared_ptr<KernelRuntime>>│
│  进程内，最快命中                             │
└──────────────────┬──────────────────────────┘
                   │ miss
                   ▼
┌─────────────────────────────────────────────┐
│  L2: 磁盘缓存 (~/.deep_gemm/cache/)          │
│  kernel.{name}.{signature_hash}/             │
│  ├── kernel.cu         (源码，用于校验)       │
│  └── kernel.cubin      (编译产物)             │
│  跨进程持久，多进程安全                       │
└──────────────────┬──────────────────────────┘
                   │ miss
                   ▼
              触发 JIT 编译
```

### 4.2 缓存键计算

```
kernel_signature = "{kernel_name}$${compiler_signature}$${compile_flags}$${source_code}"
```

- `kernel_name`：核函数名称（如 `fp8_gemm_nt`）
- `compiler_signature`：编译器类型和版本（如 `"NVCC12.8"`、`"NVRTC12.8"`）
- `compile_flags`：完整编译标志字符串
- `source_code`：生成的 CUDA C++ 源码（含 include hash 注释）

缓存目录命名：`kernel.{name}.{hex_digest(signature)}`

### 4.3 多进程安全

编译过程采用写入时复制（copy-on-write）+ 原子 rename 策略：

1. 在 `tmp/` 目录创建临时子目录
2. 写入 `kernel.cu` 和 `kernel.cubin`
3. 对所有文件和目录执行 `fsync`，确保持久化到磁盘
4. 调用 `rename(tmp_dir, cache_dir)` 原子移动
5. 若 rename 失败（EEXIST，其他进程已编译），删除临时目录

这保证了多个进程同时首次调用同一核函数时不会产生竞态条件。

### 4.4 缓存有效性检查

`KernelRuntime::check_validity(dir_path)` 验证：
- 目录存在
- `kernel.cu` 存在（源码校验）
- `kernel.cubin` 存在（编译产物存在）
- 损坏时打印错误并断言失败

---

## 五、内核加载与启动

### 5.1 内核加载路径

根据 CUDA 版本选择不同的加载 API：

| CUDA 版本 | API | 句柄类型 | 符号发现方式 |
|---|---|---|---|
| ≥ 12.8 (Runtime API) | cudaLibrary API | `cudaLibrary_t` / `cudaKernel_t` | 直接加载，不需符号名 |
| ≥ 12.4 (Driver API) | cuLibrary API | `CUlibrary` | `cuLibraryEnumerateKernels` 枚举 |
| < 12.4 (Driver API) | cuModule API | `CUmodule` | `cuModuleGetFunction` 按名获取 |

**符号过滤**：过滤掉 `vprintf`、`__instantiate_kernel`、`__internal`、`__assertfail` 等辅助符号，断言 cubin 中仅有 1 个入口核函数。

### 5.2 CUDA Driver API 懒加载

为避免启动时链接 libcuda.so，所有 CUDA Driver API 函数通过 `dlsym` 懒加载：

```cpp
// get_driver_handle() 首次调用时 dlopen("libcuda.so.1")
// 宏 DECL_LAZY_CUDA_DRIVER_FUNCTION(cuLaunchKernelEx) 生成：
//   template<typename... Args>
//   CUsresult lazy_cuLaunchKernelEx(Args... args) {
//       static auto fn = (PFN_cuLaunchKernelEx)dlsym(get_driver_handle(), "cuLaunchKernelEx");
//       return fn(args...);
//   }
```

懒加载的 Driver API 包括：cuGetErrorName/ErrorString、cuFuncSetAttribute、cuModuleLoad/Unload/GetFunction、cuLibraryLoadFromFile/Unload、cuKernelGetFunction、cuLaunchKernelEx、cuTensorMapEncodeTiled。

### 5.3 启动配置

```cpp
struct LaunchArgs {
    pair<int,int> grid_dim;     // (grid_x, grid_y)
    int num_threads;            // block 大小（通常 128/256/512）
    int smem_size = 0;          // 动态 shared memory 字节数
    int cluster_dim = 1;        // thread block cluster 维度（1 或 2）
    bool enable_pdl = true;     // PDL 开关（运行时被 device_runtime 覆盖）
};
```

Cluster launch 是 SM90+ 特性，允许多个 thread block 组成 cluster 协同执行，共享 distributed shared memory。MegaMoE 核函数使用 cluster_dim=2。

---

## 六、初始化

### 6.1 初始化入口

```python
# deep_gemm/__init__.py
_C.init(library_root_path, cuda_home_path)
```

C++ 端执行三步初始化：
1. `Compiler::prepare_init()`：设置 library_root、include_path、cuda_home、cuobjdump_path
2. `KernelRuntime::prepare_init()`：设置 cuda_home（用于 cuobjdump 路径）
3. `IncludeParser::prepare_init()`：设置 include 搜索路径（`library_root / "include"`）

### 6.2 全局单例

| 单例 | 类型 | 职责 |
|---|---|---|
| `device_runtime` | `LazyInit<DeviceRuntime>` | GPU 设备属性、SM/TC/PDL 配置、cuBLASLt 管理 |
| `compiler` | `LazyInit<Compiler>` | NVCC/NVRTC 编译器实例 |
| `include_parser` | `shared_ptr<IncludeParser>` | Include 依赖解析和 hash 计算 |
| `kernel_runtime_cache` | `shared_ptr<KernelRuntimeCache>` | 内存中的 KernelRuntime 缓存 |
| `heuristics_runtime` | `LazyInit<HeuristicsRuntime>` | 启发式参数配置 |

使用 `LazyInit<T>` 延迟初始化，首次访问时才构造，避免导入时的开销。

---

## 七、相关链接

- [/deepseek/deep-gemm/references/jit-system](/ai/deepseek/deep-gemm/references/jit-system) — JIT 系统 API 参考
- [/deepseek/deep-gemm/references/runtime-config](/ai/deepseek/deep-gemm/references/runtime-config) — 运行时配置与环境变量
- [/deepseek/deep-gemm/concepts/performance-optimization](/ai/deepseek/deep-gemm/concepts/performance-optimization) — TMA/WGMMA/PDL 等硬件特性
