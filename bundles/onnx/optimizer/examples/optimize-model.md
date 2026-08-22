---
type: example
title: "使用预打包优化 Passes 优化 ONNX 模型"
description: "通过 Python API 和命令行工具使用 onnxoptimizer 优化 ONNX 模型的完整实战示例，涵盖默认优化、自定义 pass 列表、定点迭代、大模型处理、模型校验等"
sources:
  concepts: [../concepts/00-overall-architecture.md, ../concepts/02-builtin-passes.md, ../concepts/03-pass-execution.md, ../concepts/05-python-cli-api.md]
  references: [../references/python-c-api.md, ../references/pass-manager.md]
---

# 使用预打包优化 Passes 优化 ONNX 模型

## 目标

使用 onnxoptimizer 的预打包优化 passes 优化 ONNX 模型，掌握默认优化、自定义 pass 选择、定点迭代模式的使用方法，以及优化前后的模型校验流程。

## 前置条件

```bash
# 安装依赖
pip install onnx onnxoptimizer
```

## 示例1：最简单的默认优化

使用默认的 fuse+elimination passes 优化模型：

```python
import onnx
import onnxoptimizer

# 加载模型
model = onnx.load("model.onnx")
print(f"Optimization前: {len(model.graph.node)} nodes")

# 使用默认 passes 优化（38个 Fuse+Nop 类型 pass）
optimized_model = onnxoptimizer.optimize(model)
print(f"Optimization后: {len(optimized_model.graph.node)} nodes")

# 形状推断（Python API 不自动执行，需手动调用）
try:
    optimized_model = onnx.shape_inference.infer_shapes(optimized_model)
except Exception as e:
    print(f"形状推断警告: {e}")

# 校验
onnx.checker.check_model(optimized_model)

# 保存
onnx.save(optimized_model, "optimized_model.onnx")
```

## 示例2：查看可用 Passes

```python
import onnxoptimizer

# 查看所有 50 个可用 passes
all_passes = onnxoptimizer.get_available_passes()
print(f"全部可用 passes ({len(all_passes)}):")
for p in sorted(all_passes):
    print(f"  - {p}")

# 查看默认的 fuse+elimination passes（38个）
default_passes = onnxoptimizer.get_fuse_and_elimination_passes()
print(f"\n默认优化 passes ({len(default_passes)}):")
for p in sorted(default_passes):
    print(f"  - {p}")

# 对比：哪些 pass 不在默认集合中
non_default = set(all_passes) - set(default_passes)
print(f"\n非默认 passes ({len(non_default)})，需显式指定:")
for p in sorted(non_default):
    print(f"  - {p}")
```

输出示例：

```
非默认 passes (12)，需显式指定:
  - adjust_add
  - adjust_slice_and_matmul
  - fuse_concat_into_reshape
  - fuse_qkv
  - lift_lexical_references
  - nop
  - rename_input_output
  - replace_einsum_with_matmul
  - rewrite_input_dtype
  - rewrite_where
  - set_unique_name_for_nodes
  - split_init
  - split_predict
```

## 示例3：自定义 Pass 列表

根据模型特点选择合适的 passes：

```python
import onnx
import onnxoptimizer

model = onnx.load("model.onnx")

# 针对推理部署的 pass 组合（含额外的融合 pass）
inference_passes = [
    # === 常量提取 ===
    "extract_constant_to_initializer",
    # === Nop 消除（默认集已含，显式列出便于理解）===
    "eliminate_identity",
    "eliminate_nop_transpose",
    "eliminate_nop_pad",
    "eliminate_nop_cast",
    "eliminate_deadend",
    "eliminate_unused_initializer",
    "eliminate_duplicate_initializer",
    # === 算子融合 ===
    "fuse_bn_into_conv",
    "fuse_add_bias_into_conv",
    "fuse_consecutive_transposes",
    "fuse_matmul_add_bias_into_gemm",
    "fuse_transpose_into_gemm",
    "fuse_pad_into_conv",
    "fuse_qkv",  # Transformer 模型专用，不在默认集中
]

optimized = onnxoptimizer.optimize(
    model,
    passes=inference_passes,
    fixed_point=True  # 定点迭代确保收敛
)

onnx.checker.check_model(optimized)
onnx.save(optimized, "inference_optimized.onnx")
```

## 示例4：定点迭代模式对比

对比单次执行和定点迭代的效果：

```python
import onnx
import onnxoptimizer

model = onnx.load("model.onnx")

# 单次执行
opt_single = onnxoptimizer.optimize(model, fixed_point=False)
nodes_single = len(opt_single.graph.node)

# 定点迭代（对 Partial pass 反复执行直到收敛）
opt_fixed = onnxoptimizer.optimize(model, fixed_point=True)
nodes_fixed = len(opt_fixed.graph.node)

print(f"原始节点数: {len(model.graph.node)}")
print(f"单次优化后:  {nodes_single} nodes")
print(f"定点优化后:  {nodes_fixed} nodes")
print(f"定点多消除:  {nodes_single - nodes_fixed} nodes")
```

定点迭代在包含 `fuse_consecutive_transposes`、`fuse_consecutive_concats`、`fuse_consecutive_slices` 等 Partial 效率 pass 时效果更明显。

## 示例5：命令行工具使用

```bash
# 基本用法（默认 passes + 自动形状推断 + 双向校验）
python -m onnxoptimizer model.onnx optimized.onnx

# 查看所有可用 passes
python -m onnxoptimizer --print_all_passes

# 查看默认 passes
python -m onnxoptimizer --print_fuse_elimination_passes

# 指定 passes 并启用定点迭代
python -m onnxoptimizer model.onnx optimized.onnx \
    -p fuse_bn_into_conv fuse_add_bias_into_conv eliminate_deadend \
    --fixed_point

# 跳过形状推断（当形状推断失败时）
python -m onnxoptimizer model.onnx optimized.onnx --skip_infer_shapes
```

CLI 自动执行的流程：加载 → 校验 → 优化 → 形状推断 → 保存 → 校验。

## 示例6：与 onnx-simplifier 组合使用

onnxoptimizer 不做常量折叠（常量子图解释执行），与 onnx-simplifier 组合效果最佳：

```python
import onnx
import onnxoptimizer
from onnxsim import simplify

# 1. 加载
model = onnx.load("model.onnx")
onnx.checker.check_model(model)
print(f"原始: {len(model.graph.node)} nodes")

# 2. 常量折叠（onnx-simplifier 负责常量子图求值）
model_simplified, ok = simplify(model)
assert ok, "Simplification failed"
print(f"常量折叠后: {len(model_simplified.graph.node)} nodes")

# 3. 图优化（onnxoptimizer 负责图重写和死代码消除）
model_optimized = onnxoptimizer.optimize(
    model_simplified, fixed_point=True
)
print(f"图优化后: {len(model_optimized.graph.node)} nodes")

# 4. 再次常量折叠（优化可能产生新的常量折叠机会）
model_final, ok = simplify(model_optimized)
assert ok, "Second simplification failed"
print(f"最终: {len(model_final.graph.node)} nodes")

# 5. 校验和保存
onnx.checker.check_model(model_final)
onnx.save(model_final, "fully_optimized.onnx")
```

## 示例7：C++ 直接调用

C++ 项目中直接链接 onnxoptimizer 库：

```cpp
#include <iostream>
#include "onnxoptimizer/model_util.h"
#include "onnxoptimizer/optimize.h"

int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0]
                  << " <input.onnx> <output.onnx>" << std::endl;
        return 1;
    }

    // 1. 加载模型（支持外部数据）
    auto model = onnx::optimization::loadModel(argv[1], true);
    std::cout << "加载模型完成" << std::endl;

    // 2. 输入校验
    onnx::checker::check_model(model);

    // 3. 使用默认 passes 优化（定点迭代）
    auto result = onnx::optimization::OptimizeFixed(
        model,
        onnx::optimization::GetFuseAndEliminationPass()
    );
    std::cout << "优化完成" << std::endl;

    // 4. 输出校验
    onnx::checker::check_model(result);

    // 5. 保存（大 tensor 自动转外部数据，阈值1024字节）
    onnx::optimization::saveModel(result, argv[2]);
    std::cout << "保存到: " << argv[2] << std::endl;

    return 0;
}
```

## 要点解析

### 为什么默认不使用所有 passes？

`get_available_passes()` 返回 50 个 pass，但其中：
- `split_init`/`split_predict` 会拆图，只保留初始化/推理部分
- `lift_lexical_references` 产出不符合 ONNX 规范的图
- `rename_input_output` 会改变输入输出名称
- `replace_einsum_with_matmul` 等替换类 pass 可能在某些后端上不必要

默认的 `get_fuse_and_elimination_passes()` 只包含 38 个"安全等价变换"pass。

### fixed_point 什么时候需要？

| 场景 | 是否需要 fixed_point |
|------|:-------------------:|
| 默认 pass 集合 | 可选（效果更好但稍慢） |
| 包含 fuse_consecutive_transposes | 建议使用 |
| 包含 fuse_consecutive_concats/slices | 建议使用 |
| 全部是 Complete 效率 pass | 不需要 |
| 生产环境部署 | 建议使用 |

### Python API vs CLI 的区别

| 特性 | Python API | CLI |
|------|:----------:|:---:|
| 自动形状推断 | ❌ 需手动调用 | ✅ 默认执行 |
| 自动输入校验 | ❌ 需手动调用 | ✅ 默认执行 |
| 自动输出校验 | ❌ 需手动调用 | ✅ 默认执行 |
| 大模型处理 | ✅ 自动回退 | ✅ 自动处理 |
| 自定义逻辑 | ✅ 完全可编程 | ❌ 参数有限 |

### 大模型自动处理

Python `optimize()` 函数自动处理超过 2GB 的模型：
- 首先尝试内存序列化（`SerializeToString`）
- 如果抛出 `ValueError`（protobuf 2GB 限制），自动回退到临时文件路径
- 使用 `save_as_external_data=True` 保存，调用 C++ 文件模式优化
- finally 块中清理所有临时文件

用户无需任何额外代码。

## 延伸阅读

- [开发自定义优化 Pass](custom-pass-dev.md) — 学习编写自己的优化 pass
- [ONNX Optimizer 整体架构](../concepts/00-overall-architecture.md) — 了解三层 API 架构
- [内置优化 Passes 分类详解](../concepts/02-builtin-passes.md) — 了解每个 pass 的功能
- [PassManager 执行模型](../concepts/03-pass-execution.md) — 了解定点迭代原理
- [Python/CLI/C API 使用指南](../concepts/05-python-cli-api.md) — API 详细参考
