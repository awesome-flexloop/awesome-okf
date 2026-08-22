---
type: api-reference
scope: deep-gemm
name: Runtime Configuration
version: "2.6.1"
source: csrc/apis/runtime.hpp, csrc/jit/device_runtime.hpp, csrc/jit_kernels/heuristics/runtime.hpp
description: DeepGEMM 运行时配置 API
---

# 运行时配置

DeepGEMM 提供一组运行时配置函数，用于控制 SM 利用率、Tensor Core 利用率、PDL 开关、JIT 编译行为和 block 大小等。这些配置直接影响核函数的性能表现和资源使用。

---

## 一、SM 数量配置

控制 DeepGEMM 核函数使用的流式多处理器（SM）数量。在多实例共享 GPU（如 MPS）场景下，限制 SM 数可实现公平的资源分配。

### 1.1 set_num_sms

```python
import deep_gemm

deep_gemm.set_num_sms(n: int) -> None
```

- **参数**：`n` 为使用的 SM 数量
- **约束**：`0 ≤ n ≤ multiProcessorCount`（GPU 总 SM 数）
- **特殊值**：`n=0` 表示使用全部 SM（默认行为）
- **C++ 实现**：`device_runtime->set_num_sms(n)`

### 1.2 get_num_sms

```python
deep_gemm.get_num_sms() -> int
```

- **返回**：当前配置的 SM 数量；若配置为 0，返回 GPU 实际 SM 总数（`multiProcessorCount`）

---

## 二、Tensor Core 利用率配置

控制核函数对 Tensor Core 的利用率百分比。降低此值可减少功耗或为其他核函数预留资源。

### 2.1 set_tc_util

```python
deep_gemm.set_tc_util(n: int) -> None
```

- **参数**：`n` 为 TC 利用率百分比
- **约束**：`0 ≤ n ≤ 100`
- **特殊值**：`n=0` 表示 100% 利用率（默认行为）
- **C++ 实现**：`device_runtime->set_tc_util(n)`

### 2.2 get_tc_util

```python
deep_gemm.get_tc_util() -> int
```

- **返回**：当前 TC 利用率；若配置为 0，返回默认值 100

---

## 三、PDL（Programmatic Dependent Launch）配置

PDL 是 Hopper/Blackwell 架构引入的核函数间依赖控制机制，允许核函数在不经过 CPU 调度的情况下直接在 GPU 上启动后续核函数，减少 launch overhead。

### 3.1 set_pdl

```python
deep_gemm.set_pdl(enable: bool) -> None
```

- **参数**：`enable` 为 True 时启用 PDL，False 时禁用
- **默认值**：False
- **影响范围**：所有支持 PDL 的核函数（如 WGMMA 核函数）
- **注意**：PDL 启动属性会在 `LaunchRuntime::launch()` 中被 `device_runtime->get_pdl()` 覆盖，即运行时配置优先级最高

### 3.2 get_pdl

```python
deep_gemm.get_pdl() -> bool
```

- **返回**：当前 PDL 是否启用

---

## 四、JIT 编译维度配置

控制 JIT 编译时的维度特化行为。默认情况下，核函数会为特定的 M/N/K 维度生成特化代码以获得最佳性能；忽略编译维度可减少编译次数和缓存大小，但可能略微降低性能。

### 4.1 set_ignore_compile_dims

```python
deep_gemm.set_ignore_compile_dims(new_value: bool) -> None
```

- **参数**：`new_value=True` 时忽略编译维度特化，使用通用 kernel
- **默认值**：False（即启用维度特化）
- **C++ 实现**：`heuristics_runtime->set_ignore_compile_dims(new_value)`
- **使用场景**：
  - 维度变化频繁导致编译开销过大时
  - 首次编译延迟敏感场景
  - 减少磁盘缓存占用

---

## 五、Block 大小倍数配置

强制 JIT 生成的核函数 block 大小为指定值的倍数。用于对齐外部约束（如分布式通信的 tile 大小）。

### 5.1 set_block_size_multiple_of

```python
deep_gemm.set_block_size_multiple_of(new_value) -> None
```

- **参数**：
  - 单个整数：M 和 N 维度的 block 大小均为此值的倍数
  - `(m_multiple, n_multiple)` 元组：分别设置 M 和 N 维度的倍数
- **默认值**：M 和 N 均为 1（无约束）
- **C++ 实现**：调用 `heuristics_runtime->set_block_size_multiple_of(m, n)`
- **示例**：
  ```python
  deep_gemm.set_block_size_multiple_of(64)          # M/N 均对齐到 64
  deep_gemm.set_block_size_multiple_of((128, 64))   # M=128倍数, N=64倍数
  ```

---

## 六、MK 对齐配置（Contiguous 布局）

控制 M-grouped 和 K-grouped GEMM 的连续布局对齐值。影响 TMA 加载效率和 padding 策略。

### 6.1 Python 层 API

```python
# 设置对齐值
deep_gemm.set_mk_alignment_for_contiguous_layout(new_value: int) -> None

# 获取当前对齐值
deep_gemm.get_mk_alignment_for_contiguous_layout() -> int

# 获取理论最优对齐值
deep_gemm.get_theoretical_mk_alignment_for_contiguous_layout(expected_m=None) -> int
```

**别名**（向后兼容）：
- `deep_gemm.get_m_alignment_for_contiguous_layout()`
- `deep_gemm.get_k_alignment_for_contiguous_layout()`

### 6.2 对齐策略

- **SM90（Hopper）**：理论对齐值为 128
- **SM100（Blackwell）**：理论对齐值从 224 开始以 32 为步长递减，确保 `block_m - 32 >= expected_m`，最小值 32
- **默认值**：128（`kLegacyMKAlignmentForContiguousLayout`）
- **K-alignment 约束**：必须为 32 的倍数（`k_alignment % 32 == 0`）

### 6.3 理论对齐计算

```cpp
// SM100: 从 224 递减，找满足 block_m - 32 >= expected_m 的最大值
static int get_theoretical_mk_alignment_for_contiguous_layout(optional<int> expected_m) {
    if (arch != SM100) return 128;
    for (int block_m = 224; block_m >= 32; block_m -= 32) {
        if (!expected_m || block_m - 32 >= *expected_m)
            return block_m;
    }
    return 32;
}
```

---

## 七、cuBLASLt 配置

### 7.1 环境变量控制

| 环境变量 | 默认值 | 功能 |
|---|---|---|
| `DG_USE_PYTORCH_CUBLASLT_HANDLE` | 0 | 设为 1 时使用 PyTorch 管理的 cuBLASLt handle |
| `DG_USE_TEMP_CUBLASLT_WORKSPACE` | 0 | 设为 1 时每次调用临时分配 workspace |

### 7.2 Workspace 大小

- 固定为 32MB（`DeviceRuntime::kCublasLtWorkspaceSize = 32 * 1024 * 1024`）
- 非临时模式下在 DeviceRuntime 构造时预分配

---

## 八、初始化

### 8.1 自动初始化

导入 `deep_gemm` 包时自动执行：

```python
# deep_gemm/__init__.py
_C.init(
    os.path.dirname(os.path.abspath(__file__)),  # 库根目录
    _find_cuda_home()                             # CUDA 安装路径
)
```

C++ 端初始化序列：
1. `Compiler::prepare_init()`：设置库路径、CUDA 路径、cuobjdump 路径
2. `KernelRuntime::prepare_init()`：设置 CUDA home 路径
3. `IncludeParser::prepare_init()`：设置 include 搜索路径

### 8.2 CUDA Home 检测

`_find_cuda_home()` 查找顺序：
1. `CUDA_HOME` 环境变量
2. `CUDA_PATH` 环境变量
3. `which nvcc` 推断路径
4. 默认 `/usr/local/cuda`

---

## 九、环境变量汇总

| 环境变量 | 默认值 | 功能 |
|---|---|---|
| `DG_JIT_USE_NVRTC` | 0 | 使用 NVRTC 编译器 |
| `DG_JIT_CACHE_DIR` | `~/.deep_gemm` | JIT 缓存目录 |
| `DG_JIT_NVCC_COMPILER` | `$CUDA_HOME/bin/nvcc` | 自定义 nvcc 路径 |
| `DG_JIT_DEBUG` | 0 | JIT 调试模式 |
| `DG_JIT_PTXAS_VERBOSE` | 0 | ptxas 详细输出 |
| `DG_JIT_PTXAS_CHECK` | 0 | 检查 local memory 使用 |
| `DG_JIT_WITH_LINEINFO` | 0 | 生成 lineinfo（profiling 用） |
| `DG_JIT_USE_LIBRARY_ENUM_KERNELS` | 0 | 使用 cuLibraryEnumerateKernels |
| `DG_JIT_PRINT_LOAD_TIME` | 0 | 打印 kernel 加载时间 |
| `DG_USE_PYTORCH_CUBLASLT_HANDLE` | 0 | 使用 PyTorch cuBLASLt handle |
| `DG_USE_TEMP_CUBLASLT_WORKSPACE` | 0 | 临时分配 cuBLASLt workspace |
| `DG_COMM_KERNEL_DEBUG` | 0 | 通信核函数调试（执行后清零缓冲区） |
| `DG_USE_NVIDIA_TOOLS` | 0 | 跳过 kineto profiling |
