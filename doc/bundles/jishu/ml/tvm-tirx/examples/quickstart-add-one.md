---
type: Example
title: Quickstart：add_one 的 CPU/CUDA 编译、运行与导出
description: 按官方 Quick Start 走通 tvm-tirx：写 add_one、编译到 llvm/cuda、用 PyTorch 张量调用、导出 .so 并在 Python/C++ 侧重新加载
tags: [tvm-tirx, quickstart, add-one, cuda, llvm, export-library, c++]
generated: { by: seven-concepts-cmd/1.1.0, at: 2026-11-09T00:00:00+08:00 }
verified: { by: process:seven-concepts-v, at: 2026-11-09T00:00:00+08:00 }
status: stable
stale_after: 2027-02-09
sources:
  - id: tvm-tirx-docs
    resource: https://tvm.apache.org/tirx/get_started/quick_start.html
  - id: apache-blog
    resource: https://tvm.apache.org/2026/11/03/rethinking-abstractions-in-the-agentic-era
---

# Quickstart：add_one

> 文中 `[F-xxx]` 为编号事实，来源见 [facts.md](../references/facts.md)。本示例基于官方 Quick Start 整理 [F-008]。

## 1. 环境准备

```bash
# Python 3.10+，建议用独立虚拟环境
pip install --upgrade --force-reinstall apache-tvm-tirx
pip install torch

# 可选：CUDA 支持
pip install --upgrade --force-reinstall "apache-tvm-tirx[cuda]"
```

前置要求：Python 3.10+、PyTorch；CUDA 示例需要 CUDA 13 或更新环境 [F-007]。

## 2. 写程序

TIRx 程序是带 `@T.function` 标记的普通 Python 函数。这里用 `T.dynamic("n")` 保留动态长度：

```python
from tvm_tirx.script import tirx as T

n = T.dynamic("n")

@T.function
def add_one(A: T.Tensor((n,), T.float32), B: T.Tensor((n,), T.float32)):
    for i in range(n):
        B[i] = A[i] + 1
```

CUDA 版本把循环换成线程映射：

```python
@T.function
def add_one(A: T.Tensor((n,), T.float32), B: T.Tensor((n,), T.float32)):
    T.device_entry(launch=T.cuda.LaunchConfig(grid=T.ceildiv(n, 256), block=256))
    i = T.cuda.block_idx("x") * 256 + T.cuda.thread_idx("x")
    if i < n:
        B[i] = A[i] + 1
```

三处细节：

- `grid=T.ceildiv(n, 256)`：块数向上取整，覆盖全部元素；
- `i = block_idx * 256 + thread_idx`：每个线程算出自己的全局下标；
- `if i < n`：最后一块可能多出线程，必须做越界保护。

## 3. 编译与运行

```python
import torch
import tvm_tirx

add_one_compiled = tvm_tirx.compile(add_one, target="llvm")

a = torch.arange(10, dtype=torch.float32)
b = torch.empty_like(a)
add_one_compiled(a, b)
torch.testing.assert_close(b, a + 1)
print(b)
```

输出：

```text
tensor([ 1.,  2.,  3.,  4.,  5.,  6.,  7.,  8.,  9., 10.])
```

CUDA 版只改两处：

```python
add_one_compiled = tvm_tirx.compile(add_one, target="cuda")
a = torch.arange(10, dtype=torch.float32, device="cuda")
```

> `compile` 不会叠加额外启发式优化，而是把程序直接交给 LLVM/CUDA 工具链 [F-022]。这解释了为什么同一个程序的行为稳定、可预测。

## 4. 检查 IR

编译不是黑盒，随时可以把程序打印成树：

```python
import tvm_tirx

print(tvm_tirx.ir.format_tree(add_one))
```

CPU 版本的关键结构：

```text
Function
├── params[0]: A = Var(ty=TensorType(shape=[n], dtype=float32))
├── params[1]: B = Var(ty=TensorType(shape=[n], dtype=float32))
└── body: SeqStmt
    └── seq[0]: For(begin=IntImm(value=0), end=n)
        ├── var: i = Var(ty=int32)
        └── body: SeqStmt
            └── seq[0]: TensorStore(dest=B, indices=[i])
                └── value: Add
                    ├── a: TensorLoad(source=A, indices=[i])
                    └── b: FloatImm(value=1.0)
```

也可以沿字段直接取值：

```python
A, B = add_one.params
n = A.ty.shape[0]
loop = add_one.body[0]
print(loop.body[0].value)   # A[i] + T.float32(1.0)
```

## 5. 导出共享库

```python
add_one_compiled.export_library("./add_one_cpu.so")
# CUDA 版本
# add_one_compiled.export_library("./add_one_cuda.so")
```

导出物是标准 TVM-FFI 模块 [F-028]：

- 运行不需要编译器；
- 只需要 `libtvm_runtime.so` 或 `libtvm_runtime_cuda.so`，各自小于 1 MB；
- C++、Rust、JAX 等支持 TVM-FFI 的运行时都能加载。

## 6. 在新进程里加载（Python）

```python
import torch
import tvm_ffi
import tvm_tirx  # noqa: F401  加载运行时库

loaded = tvm_ffi.load_module("./add_one_cpu.so")

a = torch.arange(10, dtype=torch.float32)
b = torch.empty_like(a)
loaded.add_one(a, b)
torch.testing.assert_close(b, a + 1)
```

## 7. 在 C++ 里加载

```cpp
#include <tvm/ffi/extra/module.h>
#include <tvm/ffi/tvm_ffi.h>
#include <tvm/runtime/tensor.h>
#include <iostream>

namespace ffi = tvm::ffi;

int main() {
    DLDataType f32{kDLFloat, 32, 1};
    DLDevice cpu{kDLCPU, 0};

    // TIRx kernel 要求 64B 对齐，使用运行时分配器
    ffi::Tensor a = tvm::runtime::Empty({10}, f32, cpu);
    ffi::Tensor b = tvm::runtime::Empty({10}, f32, cpu);

    float* a_data = static_cast<float*>(a.data_ptr());
    for (int i = 0; i < 10; ++i) a_data[i] = static_cast<float>(i);

    ffi::Module mod = ffi::Module::LoadFromFile("./add_one_cpu.so");
    ffi::Function add_one = mod->GetFunction("add_one").value();
    add_one(a, b);

    const float* b_data = static_cast<const float*>(b.data_ptr());
    for (int i = 0; i < 10; ++i) std::cout << b_data[i] << " ";
    std::cout << std::endl;
    return 0;
}
```

编译（官方推荐方式）[F-028]：

```bash
g++ -O2 load_cpp.cc \
  $(tvm-tirx-config --cxxflags --ldflags --libs runtime) \
  -Wl,-rpath,$(tvm-tirx-config --libdir) \
  -Wl,-rpath,$(tvm-ffi-config --libdir) \
  -o load_cpp
```

## 8. 常见问题

| 问题 | 处理 |
|------|------|
| CUDA 编译报 `requires an explicit backend_config arch` | 安装 CUDA 13 版 PyTorch，或安装 CUDA 13 toolkit 并把 `lib64` 加入 `LD_LIBRARY_PATH` [F-037] |
| C++ 侧结果异常 | 检查张量是否 64B 对齐 [F-028] |
| 形状不匹配 | host 代码会给出具体约束错误，例如 `expected A.shape[0] to be divisible by 2` [F-023] |

## 9. 下一步

- 想看「同一程序如何被改写」→ [structural-specialization](structural-specialization.md)
- 想理解 IR 结构与命名空间 → [02-ir-object-model](../concepts/02-ir-object-model.md)
- 想写扩展 → [extension-skeleton](extension-skeleton.md)
