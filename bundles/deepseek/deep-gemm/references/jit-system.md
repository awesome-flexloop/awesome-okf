---
type: api-reference
scope: deep-gemm
name: JIT Compilation System
version: "2.6.1"
source: csrc/jit/compiler.hpp, csrc/jit/device_runtime.hpp, csrc/jit/kernel_runtime.hpp, csrc/jit/include_parser.hpp, csrc/jit/cache.hpp, csrc/jit/handle.hpp
description: DeepGEMM JIT 编译系统架构与 API
---

# JIT 编译系统

DeepGEMM 采用运行时 JIT（Just-In-Time）编译技术，在首次调用核函数时根据输入维度和架构动态生成并编译最优 CUDA C++ 核函数，缓存编译结果供后续复用。JIT 系统由编译器、运行时缓存、设备运行时、Include 解析器和内核加载器五个核心组件构成。

---

## 一、架构概览

```
┌─────────────────────────────────────────────────┐
│              Python API (pybind11)               │
├─────────────────────────────────────────────────┤
│           LaunchRuntime<Derived> (CRTP)          │
│  ┌──────────┐  ┌──────────────┐  ┌───────────┐  │
│  │ generate │→│   Compiler   │→│  Kernel   │  │
│  │  (code)  │  │ (NVCC/NVRTC) │  │ Runtime   │  │
│  └──────────┘  └──────────────┘  └───────────┘  │
│        ↑                              ↓          │
│  ┌──────────────┐           ┌──────────────┐    │
│  │IncludeParser │           │  Handle      │    │
│  │ (hash deps)  │           │ (load/launch)│    │
│  └──────────────┘           └──────────────┘    │
│                       ↑                          │
│              ┌─────────────────┐                 │
│              │  DeviceRuntime  │                 │
│              │ (SM count, arch)│                 │
│              └─────────────────┘                 │
└─────────────────────────────────────────────────┘
```

---

## 二、编译器（Compiler）

### 2.1 抽象基类

文件：`csrc/jit/compiler.hpp`，命名空间 `deep_gemm::jit`

```cpp
class Compiler {
    static filesystem::path library_root_path;
    static filesystem::path library_include_path;
    static filesystem::path cuda_home;
    static filesystem::path cuobjdump_path;

    std::string signature;      // 编译器签名（如 "NVCC12.8"）
    std::string flags;          // 编译标志
    filesystem::path cache_dir_path;  // 缓存目录
};
```

### 2.2 NVCC 编译器（NVCCCompiler）

- **可执行文件**：默认 `$CUDA_HOME/bin/nvcc`，可通过 `DG_JIT_NVCC_COMPILER` 环境变量覆盖
- **版本要求**：CUDA ≥ 12.3，< 12.9 时打印性能警告
- **签名格式**：`"NVCC{major}.{minor}"`
- **编译标志**：
  ```
  -std=c++20
  --diag-suppress=39,161,174,177,186,940
  --ptxas-options=--register-usage-level=10
  -I{include_path}
  --gpu-architecture=sm_{arch}
  --compiler-options=-fPIC,-O3,-fconcepts,-Wno-deprecated-declarations,-Wno-abi
  -O3 --expt-relaxed-constexpr --expt-extended-lambda
  ```
- **目标架构**：通过 `device_runtime->get_arch(false, nvcc>=12.9)` 获取，SM100 区分 "100a"/"100f"
- **编译产物**：`kernel.cubin`（必需），可选 `kernel.ptx`、`kernel.sass`

### 2.3 NVRTC 编译器（NVRTCCompiler）

- **启用条件**：`DG_JIT_USE_NVRTC` 环境变量非零
- **版本要求**：NVRTC ≥ 12.3
- **签名格式**：`"NVRTC{major}.{minor}"`
- **编译标志**：
  ```
  -I{library_include_path} -I{cuda_home}/include
  --gpu-architecture=sm_{arch}
  -default-device
  --pch  (NVRTC >= 12.8，可通过 DG_JIT_DEBUG 加 --pch-verbose=true)
  --device-int128
  ```
- **编译流程**：`nvrtcCreateProgram` → `nvrtcCompileProgram` → 获取 PTX/CUBIN → 写入文件 → `nvrtcDestroyProgram`

### 2.4 编译流程

`Compiler::build(name, code) -> shared_ptr<KernelRuntime>`：

1. 计算 `kernel_signature = "{name}$${signature}$${flags}$${code}"`
2. 生成目录路径：`cache_dir / "cache" / "kernel.{name}.{hex(signature)}"`
3. 检查内存缓存 `kernel_runtime_cache->get(dir_path)`，命中直接返回
4. 未命中：编译到临时目录 `tmp_dir`（含 `kernel.cu`、`kernel.cubin`）
5. `fsync` 确保写入持久化后原子 `rename` 到正式目录
6. rename 失败（其他进程已创建）则清理临时目录
7. 返回 `kernel_runtime_cache->get(dir_path)`

### 2.5 缓存目录

- 默认：`$HOME/.deep_gemm/cache/`
- 可通过 `DG_JIT_CACHE_DIR` 环境变量覆盖
- 临时编译目录：`$HOME/.deep_gemm/tmp/`

### 2.6 调试环境变量

| 环境变量 | 功能 |
|---|---|
| `DG_JIT_DEBUG` | 启用调试模式（verbose ptxas、lineinfo） |
| `DG_JIT_PTXAS_VERBOSE` | ptxas 详细输出 |
| `DG_JIT_PTXAS_CHECK` | 断言无 local memory 使用 |
| `DG_JIT_WITH_LINEINFO` | 添加 `-Xcompiler -rdynamic -lineinfo`（profiling 用） |
| `DG_JIT_NVCC_COMPILER` | 自定义 nvcc 路径 |
| `DG_JIT_USE_NVRTC` | 使用 NVRTC 替代 NVCC |
| `DG_JIT_CACHE_DIR` | 自定义缓存目录 |
| `DG_JIT_USE_LIBRARY_ENUM_KERNELS` | 使用 cuLibraryEnumerateKernels 加载（无需符号名） |
| `DG_JIT_PRINT_LOAD_TIME` | 打印 kernel 加载耗时 |

---

## 三、设备运行时（DeviceRuntime）

文件：`csrc/jit/device_runtime.hpp`

### 3.1 核心成员

```cpp
class DeviceRuntime {
    int num_sms = 0;           // 使用的 SM 数量，0 表示全部
    int tc_util = 0;           // Tensor Core 利用率，0 表示 100%
    bool enable_pdl = false;   // 是否启用 PDL
    shared_ptr<cudaDeviceProp> cached_prop;
    cublasLtHandle_t cublaslt_handle;
    torch::Tensor cublaslt_workspace;  // 32MB workspace
};
```

### 3.2 cuBLASLt 管理

- Workspace 大小：32MB（`kCublasLtWorkspaceSize`）
- Handle 模式：
  - `DG_USE_PYTORCH_CUBLASLT_HANDLE=1`：使用 PyTorch 管理的 cuBLASLt handle
  - 默认：自管理，构造时 `cublasLtCreate`，析构时 `cublasLtDestroy`
- Workspace 模式：
  - `DG_USE_TEMP_CUBLASLT_WORKSPACE=1`：每次调用临时分配
  - 默认：持有 32MB 预分配 workspace

### 3.3 架构检测

```cpp
get_arch_pair() -> pair<int,int>       // (major, minor)
get_arch(number_only, support_arch_family) -> string
// SM100: minor!=1 → "100f"/"100", 否则 → "100a"/"100"
// 其他:  "{major*10+minor}a" / "{major*10+minor}"
get_arch_major() -> int                 // 9 (Hopper) 或 10 (Blackwell)
get_num_sms() -> int                    // num_sms==0 → multiProcessorCount
get_l2_cache_size() -> int              // L2 缓存大小（字节）
```

### 3.4 SM/TC 利用率配置

- `set_num_sms(n)`：断言 `0 <= n <= multiProcessorCount`
- `get_num_sms()`：返回配置值或全部 SM 数
- `set_tc_util(n)`：断言 `0 <= n <= 100`
- `get_tc_util()`：返回配置值或默认 100
- `set_pdl(bool)` / `get_pdl()`：PDL 开关

---

## 四、内核运行时（KernelRuntime）

文件：`csrc/jit/kernel_runtime.hpp`

### 4.1 启动参数

```cpp
struct LaunchArgs {
    pair<int,int> grid_dim;     // (grid_x, grid_y)
    int num_threads;            // block 大小
    int smem_size = 0;          // 动态 shared memory 大小
    int cluster_dim = 1;        // thread block cluster 维度
    bool enable_pdl = true;     // 是否启用 PDL（运行时可被 device_runtime 覆盖）
};
```

### 4.2 内核加载

构造函数 `KernelRuntime(dir_path)`：
1. 定位 `kernel.cubin`
2. 若启用 `DG_JIT_USE_LIBRARY_ENUM_KERNELS`：直接 `load_kernel` 加载
3. 否则：调用 `cuobjdump -symbols` 获取符号列表，过滤 vprintf/`__instantiate_kernel`/`__internal`/`__assertfail`，断言仅有 1 个入口函数
4. 调用 `load_kernel(cubin_path, symbol_name, &library)` 加载

### 4.3 有效性检查

`KernelRuntime::check_validity(dir_path) -> bool`：检查目录存在且 `kernel.cu` 和 `kernel.cubin` 均存在

### 4.4 CRTP 启动模式

```cpp
template<typename Derived>
class LaunchRuntime {
    static string generate(const Args& args);     // 生成 CUDA C++ 代码
    static void launch(shared_ptr<KernelRuntime>, const Args&);  // 启动内核
};
```

- `generate()`：调用 `Derived::generate_impl(args)` 生成代码，首次调用时通过 `IncludeParser` 计算并缓存 include hash，在代码头部添加 `// Includes' hash value: {hash}` 注释
- `launch()`：获取当前 CUDA stream → 从 args 获取 LaunchArgs（enable_pdl 被运行时覆盖）→ 构造 dim3 grid/block → `construct_launch_config` → `Derived::launch_impl`

---

## 五、Include 解析器（IncludeParser）

文件：`csrc/jit/include_parser.hpp`

### 5.1 功能

递归解析 CUDA C++ 代码中的 `#include <deep_gemm/*>` 依赖，计算所有依赖文件的 hash 值，用于精确缓存失效。

### 5.2 核心方法

- `get_includes(code, file_path="") -> vector<string>`：正则提取 `#\s*include\s*[<"][^>"]+[>"]`，仅处理 `<deep_gemm/*>` 格式
- `get_hash_value(code, exclude_code=true) -> string`：递归计算所有 include 依赖的 hash（可选包含 code 本身），返回 hex digest
- `get_hash_value_by_path(path) -> string`：读取文件内容并递归计算依赖 hash；检测循环 include（通过 cache 中的 nullopt 标记）

### 5.3 初始化

`IncludeParser::prepare_init(library_root_path)`：设置 `library_include_path = library_root_path / "include"`，即 `deep_gemm/include/deep_gemm/` 目录

---

## 六、句柄管理（Handle）

文件：`csrc/jit/handle.hpp`

### 6.1 CUDA Driver API 懒加载

- `get_driver_handle() -> void*`：通过 `dlopen("libcuda.so.1")` 懒加载 CUDA driver 库
- 宏 `DECL_LAZY_CUDA_DRIVER_FUNCTION(name)`：生成懒加载函数模板，通过 `dlsym` 获取函数指针
- 懒加载的 Driver API 函数：cuGetErrorName/ErrorString、cuFuncSetAttribute、cuModuleLoad/Unload/GetFunction、cuLibraryLoadFromFile/Unload、cuKernelGetFunction、cuLaunchKernelEx、cuTensorMapEncodeTiled

### 6.2 内核加载路径（双模式）

**CUDART ≥ 12.8 且 DG_JIT_USE_RUNTIME_API 定义**（Runtime API 路径）：
- `LibraryHandle = cudaLibrary_t`，`KernelHandle = cudaKernel_t`
- `cudaLibraryLoadFromFile` + `cudaLibraryGetKernel` 加载
- `cudaLaunchKernelExC` 启动

**否则**（Driver API 路径）：
- CUDA ≥ 12.4：使用 `cuLibrary` API（`LibraryHandle = CUlibrary`）
- CUDA < 12.4：使用 `cuModule` API（`LibraryHandle = CUmodule`）
- `cuModuleLoad` + `cuModuleGetFunction`（或 `cuLibraryLoadFromFile` + `cuLibraryEnumerateKernels`）加载
- 断言 cubin 中仅包含 1 个 kernel 函数
- `cuLaunchKernelEx` 启动

---

## 七、运行时缓存（KernelRuntimeCache）

文件：`csrc/jit/cache.hpp`

```cpp
class KernelRuntimeCache {
    unordered_map<string, shared_ptr<KernelRuntime>> cache;

    shared_ptr<KernelRuntime> get(path dir_path);
    // 命中 → 直接返回
    // 未命中 → KernelRuntime::check_validity() → 有效则创建并缓存，无效返回 nullptr
};
```

全局单例：`kernel_runtime_cache`

---

## 八、初始化流程

```python
# deep_gemm/__init__.py
_C.init(
    library_root_path,     # deep_gemm 包目录
    _find_cuda_home()      # CUDA 安装路径
)
```

C++ 端 `runtime::init()` 执行：
1. `Compiler::prepare_init()`：设置路径、cuobjdump 路径
2. `KernelRuntime::prepare_init()`：设置 cuda_home
3. `IncludeParser::prepare_init()`：设置 include 路径

环境变量持久化：包加载时从 `.envs.persistent_envs` 字典读取预设环境变量，仅在 key 不存在时设置。
