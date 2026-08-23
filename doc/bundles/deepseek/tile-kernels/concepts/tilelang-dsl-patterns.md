---
type: concept
scope: tile-kernels
name: TileLang DSL 编程模式
version: "0.1.0"
source: tile-kernels-spec-facts
description: TileKernels 中使用的 TileLang DSL 编程模式——@tilelang.jit、T.prim_func、T.Kernel、T.Parallel、共享内存、warp原语、宏复用
---

# TileLang DSL 编程模式

TileKernels 使用 [TileLang](https://github.com/tile-ai/tilelang) 作为核函数编写 DSL。TileLang 是一种类 TVMScript 的 Python DSL，允许开发者以接近数学公式的抽象级别编写 CUDA kernel，同时精确控制线程映射、内存层次和硬件原语。本文档总结 TileKernels 中使用的核心 TileLang 编程模式。

---

## 一、Kernel 基本结构

### 1.1 JIT 编译装饰器

TileLang kernel 采用"工厂函数 + JIT 装饰"模式。工厂函数接受编译期常量参数（如 hidden size、mhc_mult 等），返回一个 JITKernel 对象；运行时参数（如动态维度、数据指针）在调用时传入。

```python
import tilelang
import tilelang.language as T

@tilelang.jit
def get_my_kernel(hidden: int, block_size: int):
    # 编译期参数用于确定 tensor shape、循环边界、向量化大小等
    num_threads = 128
    vec_size = 8

    @T.prim_func
    def main(
        x: T.Tensor[(T.dynamic('M'), hidden), T.bfloat16],   # 动态维度
        out: T.Tensor[(T.dynamic('M'), hidden), T.bfloat16],
    ):
        # kernel 主体
        with T.Kernel(T.ceildiv(T.dynamic('M'), block_size), threads=num_threads) as (pid):
            # 每个 thread block 的逻辑
            ...

    return main
```

**编译期 vs 运行期参数**：
- 编译期参数：影响 kernel 生成的形状参数（hidden、block 大小、mhc_mult 等），传给工厂函数
- 运行期参数：实际数据维度和数据指针，在调用 JITKernel 时传入，动态维度用 `T.dynamic('name')` 声明

### 1.2 T.prim_func：Kernel 函数签名

`@T.prim_func` 装饰 kernel 的主函数，定义输入输出 tensor 的类型和形状。

```python
@T.prim_func
def main(
    x: T.Tensor[(M, K), T.bfloat16],              # 普通 tensor
    sf: T.Tensor[(M_sf, K_sf), T.float32],        # 缩放因子
    out: T.Tensor[(M, K), T.float8_e4m3fn],       # FP8 输出
):
```

对于带自定义 stride 的 tensor，使用 `T.StridedTensor`：

```python
x: T.StridedTensor[(M, K), (stride_m, stride_k), T.bfloat16]
```

### 1.3 T.Kernel：Grid 和 Block 配置

`with T.Kernel(...) as (pid...)` 定义 kernel 的 grid 维度和 thread block 大小：

```python
# 1D grid
with T.Kernel(T.ceildiv(M, block_m), threads=256) as (pid_m):
    ...

# 2D grid
with T.Kernel(T.ceildiv(M, block_m), T.ceildiv(N, block_n), threads=256) as (pid_m, pid_n):
    ...
```

`pid` 变量是当前 block 在 grid 中的索引，可用于计算该 block 负责的数据范围。

---

## 二、内存层次

TileLang 显式管理 CUDA 的三级内存层次：全局内存 → 共享内存 → 寄存器/片段。

### 2.1 全局内存

Kernel 函数参数中的 tensor 位于全局内存（Global Memory），使用 `T.Tensor` 声明。

### 2.2 共享内存（Shared Memory）

```python
# 在 kernel 内部分配 shared memory
shared = T.alloc_shared((block_m, block_k), T.bfloat16)
```

共享内存用于 thread block 内的线程间数据共享和全局内存访问的 coalescing。TileKernels 中常见用法：

```python
# TileLang 量化 kernel 中的 shared memory 使用
x_shared = T.alloc_shared((block_m, block_k), dtype)
sf_shared = T.alloc_shared((block_m, block_k_sf), T.float32)

# TMA 异步拷贝全局内存到共享内存
T.copy(x[pid_m*block_m:(pid_m+1)*block_m, :], x_shared)
```

**Bank Conflict 优化**：在转置 kernel 中，shared memory 使用 padding 减少 bank conflict：

```python
# (block_y, block_x + block_k) padding 避免 bank conflict
shared = T.alloc_shared((block_y, block_x + block_k), dtype)
```

### 2.3 寄存器和 Fragment

```python
# 寄存器数组
local_acc = T.alloc_local((vec_size,), T.float32)

# MMA fragment（WGMMA/TCGen 使用）
# 注意：部分 kernel 禁用 WGMMA (TL_DISABLE_WGMMA: True)
frag = T.alloc_fragment((mma_m, mma_n), T.float32)
```

---

## 三、循环模式

### 3.1 T.Parallel：自动并行化循环

`T.Parallel` 是 TileLang 中最核心的循环模式，表示循环迭代可以跨线程并行执行。

```python
for i, j in T.Parallel(M, N):
    out[i, j] = x[i, j] * scale
```

编译器会自动将 `T.Parallel` 循环的迭代空间映射到 CUDA 线程。嵌套的 `T.Parallel` 表示多维并行。

### 3.2 T.vectorized：向量化加载/存储

```python
for i in T.vectorized(vec_size):
    local_buf[i] = x_shared[offset + i]
```

向量化循环使用 LDG.128/STS.128 等宽向量指令，一次加载/存储多个元素。vec_size 通常为 4/8/16（对应 16B/32B/64B 向量宽度）。

```python
# 量化 kernel 中根据 dtype 选择最佳 vectorize size
vec_size = get_best_vectorize_size(dtype)  # 根据 compute capability 返回 16/32 / dtype.bytes
```

### 3.3 T.unroll：循环展开

```python
for k in T.unroll(block_k):
    acc += x_shared[i, k] * w_shared[k, j]
```

`T.unroll` 提示编译器完全展开循环，减少循环控制开销并增加指令调度机会。

### 3.4 串行循环

普通 `for` 循环（不使用 T.Parallel/T.vectorized/T.unroll）在每个线程内串行执行：

```python
for m_idx in range(block_m):
    amax = T.max(amax, T.abs(x_shared[m_idx, k_idx]))
```

---

## 四、Warp 级原语

TileKernels 的 MoE 和归约 kernel 大量使用 warp 级原语实现高效的 warp 内通信。

### 4.1 T.shfl_sync：Warp Shuffle

```python
# Warp 内全规约（all-reduce sum）
@T.macro
def warp_reduce_sum(x):
    for offset in [16, 8, 4, 2, 1]:
        x += T.shfl_sync(x, x + offset, 0xFFFFFFFF)
    return x
```

Warp shuffle 允许 warp 内的线程直接交换寄存器值，不需要经过 shared memory，延迟极低。

### 4.2 T.sync_warp 和 T.sync_threads

```python
T.sync_warp()        # Warp 内同步
T.sync_threads()     # Block 内所有线程同步（__syncthreads）
```

在 shared memory 读写后需要同步以保证数据可见性。

### 4.3 Warp 级 Top-K

MoE topk_gate kernel 使用 warp shuffle 在 warp 内做并行 top-k 选择：

```python
@T.macro
def get_topk_group_idx(scores_shared, topk_idx_shared, ...):
    # 每个 warp 处理一组 token
    # 使用 warp shuffle 在 warp 内做 k 轮冒泡选择
    for i in range(num_topk_groups):
        # 每个线程找局部最大值
        # warp shuffle 比较 → 全局最大值
        # 记录最大值位置，设为 -inf
        # 重复 k 次
```

---

## 五、归约（Reducer）

TileLang 提供 `T.alloc_reducer` 用于 block 级归约：

```python
reducer = T.alloc_reducer(num_threads, T.float32, replication='all')
# ... 每个线程计算 partial sum ...
reduced_val = reducer.reduce(partial_val, 'sum')
```

MHC backward kernel 使用 reducer 做 scale/base 梯度的 partial sum 归约：

```python
# mhc_head_compute_mix_bwd 中的梯度归约
scale_grad_reducer = T.alloc_reducer(num_sms, T.float32, replication='all')
```

---

## 六、宏（@T.macro）

`@T.macro` 是 TileLang 的代码复用机制，类似于 C 宏但支持类型检查。在不同 kernel 间共享代码片段。

```python
@T.macro
def get_sf_and_inv(amax, out_config):
    """从 amax 计算 scale factor 和 inverse scale factor"""
    sf = amax / T.max_value(out_config.dtype)
    if out_config.round_sf:
        # Round sf to nearest power of 2
        ...
    sf_inv = 1.0 / sf
    return sf, sf_inv

@T.macro
def load_sf(tensor, m_idx, k_idx, config):
    """从全局内存加载 sf（支持 packed_ue8m0 和 col-major）"""
    ...

# 在 kernel 中使用
sf, sf_inv = get_sf_and_inv(amax, out_config)
```

TileKernels 中使用的关键宏：

| 宏 | 定义位置 | 用途 |
|---|---|---|
| `get_sf_and_inv` | quant/common.py | 计算 sf 和 sf_inv |
| `load_sf` | quant/common.py | 加载 sf（支持多种布局） |
| `transform_sf` | quant/common.py | sf 转 float32 |
| `store_sf` | quant/common.py | 存储 sf |
| `softplus` | moe/scoring.py | Softplus 激活函数 |
| `get_topk_group_idx` | moe/common.py | Warp 内 topk group 选择 |
| `warp_reduce_sum` | moe/top2_sum_gate_kernel.py | Warp 求和规约 |
| `divide_task` | moe/get_fused_mapping_kernel.py | 任务划分 |

---

## 七、Pass 配置

Pass 配置控制 TileLang 编译器的优化行为，在 JIT 装饰器中传入：

```python
@tilelang.jit(pass_configs={
    "tl.disable_warp_specialized": True,
    "tl.disable_wgmma": True,
    "tl.ptxas_register_usage_level": 10,
    "tl.disable_vectorize_256": True,
})
def get_my_kernel(...):
    ...
```

TileKernels 中常用的 pass 配置：

| Pass 配置 | 值 | 作用 | 使用场景 |
|---|---|---|---|
| `TL_DISABLE_WARP_SPECIALIZED` | True | 禁用 warp specialization（生产者-消费者流水线） | 不使用异步 TMA 流水线的 kernel |
| `TL_DISABLE_WGMMA` | True | 禁用 WGMMA（Warp Group Matrix Multiply-Accumulate） | 使用 FFMA/TF32 MMA 而非 WGMMA 的 kernel |
| `TL_PTXAS_REGISTER_USAGE_LEVEL` | 10 | 控制 PTXAS 寄存器分配（越高越激进，占用越少寄存器） | 需要高 occupancy 的 kernel |
| `TL_DISABLE_VECTORIZE_256` | True | 禁用 256-bit 向量化 | 避免某些数据对齐问题 |

---

## 八、Kernel 调用

JIT 编译的 kernel 在 Python 端像普通函数一样调用：

```python
# 获取（或从缓存获取）JIT kernel
kernel = get_per_token_cast_kernel(hidden, num_per_channels, ...)

# 调用 kernel（传入 torch tensors）
out_data = torch.empty(num_tokens, logical_hidden, device='cuda', dtype=torch_dtype)
out_sf = alloc_scaling_factors(sf_shape, out_config, device)
kernel(x, out_data, out_sf)  # JIT kernel 直接接受 torch tensors
```

TileLang JIT 会自动：
1. 检查输入 tensor 的 device/dtype/shape
2. 如未编译则触发 JIT 编译（NVCC/NVRTC）并缓存
3. 准备 kernel 启动参数
4. 启动 CUDA kernel
5. 如设置 `TK_PRINT_KERNEL_SOURCE=1` 环境变量，打印生成的 CUDA 源码

---

## 九、典型 Kernel 模板

以下是 TileKernels 中典型的量化 kernel 结构：

```python
@tilelang.jit
def get_cast_kernel(M, N, block_M, block_N, dtype_in, dtype_out, dtype_sf):
    vec_size = get_best_vectorize_size(dtype_out)
    num_threads = 128

    @T.prim_func
    def main(
        x: T.Tensor[(T.dynamic('M'), N), dtype_in],
        out: T.Tensor[(T.dynamic('M'), N_physical), dtype_out],
        out_sf: T.Tensor[(T.dynamic('M'), T.ceildiv(N, sf_block_N)), dtype_sf],
    ):
        with T.Kernel(T.ceildiv(T.dynamic('M'), block_M), threads=num_threads) as (pid_m):
            # 分配 shared memory
            x_shared = T.alloc_shared((block_M, block_N), dtype_in)
            amax_shared = T.alloc_shared((block_M,), T.float32)

            # 计算 amax
            for m, k in T.Parallel(block_M, block_N):
                x_shared[m, k] = x[pid_m*block_M + m, k]
                amax_shared[m] = T.max(amax_shared[m], T.abs(x_shared[m, k]))
            T.sync_threads()

            # 计算 sf
            sf, sf_inv = get_sf_and_inv(amax_shared, out_config)

            # 量化并存储
            for m, k in T.Parallel(block_M, block_N // vec_size):
                for vk in T.vectorized(vec_size):
                    val = T.cast(x_shared[m, k*vec_size + vk], T.float32) * sf_inv[m]
                    out[pid_m*block_M + m, k*vec_size + vk] = T.cast(val, dtype_out)

            # 存储 sf
            for m in T.Parallel(block_M):
                store_sf(out_sf, sf, pid_m*block_M + m, 0, out_config)

    return main
```

---

## 十、环境变量调试

| 环境变量 | 作用 |
|---|---|
| `TK_PRINT_KERNEL_SOURCE=1` | 多个 kernel 启动时打印生成的 CUDA 源码 |
