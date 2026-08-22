---
type: concept
title: "Python API、CLI 与 C API 使用指南"
description: "onnxoptimizer Python optimize() 函数用法、get_available_passes()/get_fuse_and_elimination_passes() 辅助函数、命令行工具参数与流程、C++ 自由函数 API、纯 C API 的使用方式与注意事项"
sources:
  references: [../references/python-c-api.md, ../references/pass-manager.md]
  facts: [F-006, F-007, F-008, F-009, F-010, F-011, F-012, F-013, F-014, F-015, F-044, F-054, F-055, F-056, F-060]
---

# Python API、CLI 与 C API 使用指南

## 核心理解

ONNX Optimizer 提供三层用户 API：Python API（最常用）、命令行工具（CLI，用于快速模型处理）和 C++/C API（用于集成到推理引擎等原生应用）。三层 API 底层共享同一个 C++ 优化引擎，核心功能完全一致。Python 层是最便捷的入口，自动处理大模型回退、序列化等细节。

## Python API

### 核心函数：optimize()

```python
import onnx
import onnxoptimizer

# 1. 加载模型
model = onnx.load("model.onnx")

# 2. 使用默认 pass 优化（fuse + elimination）
optimized_model = onnxoptimizer.optimize(model)

# 3. 保存结果
onnx.save(optimized_model, "optimized_model.onnx")
```

**函数签名**：

```python
def optimize(
    model: onnx.ModelProto,
    passes: list[str] | None = None,
    fixed_point: bool = False
) -> onnx.ModelProto
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `model` | `onnx.ModelProto` | 必填 | 输入 ONNX 模型 |
| `passes` | `list[str] \| None` | `None` | 要执行的 pass 名称列表，`None` 使用默认 fuse+elimination 集合 |
| `fixed_point` | `bool` | `False` | 是否启用定点迭代（对 Partial pass 反复执行直到收敛） |

### 默认 pass 集合

当 `passes=None` 时，使用 `get_fuse_and_elimination_passes()` 返回的集合（38 个 Fuse+Nop 类型 pass）。这是最安全的选择，只做等价变换。

### 指定自定义 pass 列表

```python
# 使用全部可用 pass（注意：包含可能改变图结构的 pass）
all_passes = onnxoptimizer.get_available_passes()
optimized_model = onnxoptimizer.optimize(model, passes=all_passes)

# 自定义 pass 组合
my_passes = [
    "fuse_bn_into_conv",
    "fuse_add_bias_into_conv",
    "eliminate_identity",
    "eliminate_deadend",
    "eliminate_nop_transpose",
]
optimized_model = onnxoptimizer.optimize(model, passes=my_passes)

# 定点迭代模式
optimized_model = onnxoptimizer.optimize(model, passes=my_passes, fixed_point=True)
```

> ⚠️ **警告**：`get_available_passes()` 返回全部 50 个 pass，包含 `split_init`（只保留初始化部分）、`lift_lexical_references`（产出非标准 ONNX）等破坏性 pass。生产环境不要直接使用全部 pass。

### 辅助函数

```python
# 获取所有可用 pass 名称（50个）
all_passes = onnxoptimizer.get_available_passes()
print(f"Total passes: {len(all_passes)}")

# 获取默认 fuse+elimination pass 名称（38个）
default_passes = onnxoptimizer.get_fuse_and_elimination_passes()
print(f"Default passes: {len(default_passes)}")
```

### 大模型自动处理

Python `optimize()` 函数内置大模型（>2GB）回退机制：

1. **首选路径**：将 ModelProto 序列化为字节串，调用 C++ 内存模式优化
2. **回退路径**：若序列化抛出 `ValueError`（通常因 protobuf 2GB 限制）：
   - 创建临时目录
   - 以 `save_as_external_data=True` 保存模型到临时文件
   - 调用 C++ 文件模式优化
   - 加载优化后的模型
   - finally 块中清理临时目录

用户无需关心模型大小，API 自动处理。

### 形状推断注意事项

Python `optimize()` **不自动执行形状推断**。CLI 默认执行形状推断（`onnx.shape_inference.infer_shapes()`），但 Python API 需要用户手动调用：

```python
optimized_model = onnxoptimizer.optimize(model)
optimized_model = onnx.shape_inference.infer_shapes(optimized_model)  # 手动推断
onnx.save(optimized_model, "optimized_model.onnx")
```

### 模型检查

建议在优化前后进行模型检查：

```python
model = onnx.load("model.onnx")
onnx.checker.check_model(model)  # 优化前检查

optimized_model = onnxoptimizer.optimize(model)
onnx.checker.check_model(optimized_model)  # 优化后检查
```

## 命令行工具（CLI）

### 基本用法

```bash
# 基本优化（默认 passes + 形状推断）
python -m onnxoptimizer input.onnx output.onnx

# 指定 passes
python -m onnxoptimizer input.onnx output.onnx -p fuse_bn_into_conv eliminate_deadend

# 定点迭代
python -m onnxoptimizer input.onnx output.onnx --fixed_point

# 跳过形状推断
python -m onnxoptimizer input.onnx output.onnx --skip_infer_shapes

# 查看所有可用 passes
python -m onnxoptimizer --print_all_passes

# 查看默认 fuse+elimination passes
python -m onnxoptimizer --print_fuse_elimination_passes
```

### CLI 参数一览

| 参数 | 缩写 | 说明 |
|------|------|------|
| `--print_all_passes` | - | 打印所有可用 passes 并退出 |
| `--print_fuse_elimination_passes` | - | 打印 fuse+elimination passes 并退出 |
| `--passes` | `-p` | 指定 passes 列表（空格分隔或逗号分隔） |
| `--fixed_point` | - | 启用定点迭代 |
| `--skip_infer_shapes` | - | 跳过优化后形状推断 |

### CLI 执行流程

CLI 自动执行完整的"加载→校验→优化→推断→保存→校验"流程：

```
1. onnx.load(input_path)
2. onnx.checker.check_model(input)     ← 输入校验
3. onnxoptimizer.optimize(model, passes, fixed_point)
4. onnx.shape_inference.infer_shapes() ← 除非 --skip_infer_shapes
5. onnx.save(output)                  ← 大模型自动 save_as_external_data
6. onnx.checker.check_model(output)   ← 输出校验
```

## C++ API

C++ 层提供自由函数和 Optimizer 类两种使用方式。

### 自由函数（推荐）

```cpp
#include "onnxoptimizer/optimize.h"
#include "onnxoptimizer/model_util.h"

// 加载模型
auto model = onnx::optimization::loadModel("input.onnx");

// 校验
onnx::checker::check_model(model);

// 单次遍历优化（默认 passes）
auto result = onnx::optimization::Optimize(
    model,
    onnx::optimization::GetFuseAndEliminationPass());

// 或定点迭代优化
auto result_fixed = onnx::optimization::OptimizeFixed(
    model,
    my_pass_list);

// 校验结果
onnx::checker::check_model(result);

// 保存
onnx::optimization::saveModel(result, "output.onnx");
```

### C++ API 函数列表

| 函数 | 说明 |
|------|------|
| `Optimize(mp_in, names)` | 单次遍历优化（GeneralPassManager） |
| `OptimizeFixed(mp_in, names)` | 定点迭代优化（FixedPointPassManager） |
| `GetAvailablePasses()` | 获取所有 pass 名称（`vector<string>`） |
| `GetFuseAndEliminationPass()` | 获取默认 pass 名称 |
| `loadModel(path, load_external_data)` | 加载模型（支持外部数据） |
| `saveModel(mp, path, size_threshold)` | 保存模型（自动处理外部数据） |

### model_util 外部数据处理

`saveModel()` 在 tensor 大小超过阈值（默认 1024 字节）时自动转为外部数据格式：
- 外部数据包含 `location`（文件名）、`offset`（偏移）、`length`（长度）
- 所有外部张量的 raw_data 写入同一个数据文件（append 模式）
- 使用 UUID 生成唯一数据文件名
- `loadModel()` 可选择性加载外部张量数据

### IR 版本注意事项

C++ 优化器对 IR v3 模型自动升级到 IR v4（initializer 不必在 input 中）。输出模型 IR 版本为 v4。若模型 IR 过旧无法解析，输出警告并返回原始模型。

## C API（嵌入式）

纯 C API 位于 `c_api/onnxoptimizer_c_api.h`，为非 C++ 语言提供嵌入能力。

### 内存模式

```c
// 1. 获取 pass 列表
const char** pass_names = NULL;
int num_passes = 0;
C_API_GetFuseAndEliminationPass(&pass_names, &num_passes);

// 2. 优化（内存模式）
void* out_data = NULL;
int out_size = 0;
C_API_Optimize(
    in_data, in_size,           // 输入模型字节
    pass_names, num_passes,     // pass 列表
    &out_data, &out_size,       // 输出模型字节
    0                           // fixed_point: 0=单次, 1=定点
);

// 3. 释放内存
C_API_ReleasePasses(pass_names, num_passes);
free(out_data);  // 调用者负责释放输出数据
```

### 文件模式

```c
// 文件模式优化
C_API_OtimizeFromFile(  // ⚠️ 注意拼写：Otimize 而非 Optimize
    "input.onnx",
    "output.onnx",
    pass_names, num_passes,
    1,  // fixed_point
    "data_file"  // 外部数据文件名
);
```

### C API 注意事项

| 事项 | 说明 |
|------|------|
| **拼写错误** | `C_API_OtimizeFromFile` 缺少 'p'（Otimize），因 C ABI 兼容性无法修复 |
| **内存管理** | 调用者必须调用 `C_API_ReleasePasses()` 释放 pass 名称数组；输出数据也需要调用者释放 |
| **线程安全** | C API 函数本身无全局状态修改，但 ONNX 模型解析/序列化可能不是线程安全的 |

## nanobind 绑定层

Python 绑定使用 nanobind（而非 pybind11），模块名为 `onnx_opt_cpp2py_export`，暴露 6 个 C++ 函数：

| nanobind 函数 | 对应 Python 调用 |
|---------------|-----------------|
| `optimize(bytes, names) → bytes` | 内存模式单次优化 |
| `optimize_fixedpoint(bytes, names) → bytes` | 内存模式定点优化 |
| `optimize_from_path(in, out, names, data) → None` | 文件模式单次优化 |
| `optimize_fixedpoint_from_path(in, out, names, data) → None` | 文件模式定点优化 |
| `get_available_passes() → list[str]` | 获取所有 pass 名称 |
| `get_fuse_and_elimination_passes() → list[str]` | 获取默认 pass 名称 |

Python `__init__.py` 的 `optimize()` 函数在此基础上增加了序列化/反序列化和大模型回退逻辑。

## API 选型指南

| 场景 | 推荐 API | 理由 |
|------|----------|------|
| Python 环境快速优化模型 | Python `optimize()` | 最简 API，自动处理大模型 |
| 脚本/批处理模型 | CLI | 一行命令，自动校验+形状推断 |
| C++ 推理引擎集成 | C++ 自由函数 | 零额外依赖，性能最优 |
| 非 C++ 语言集成（Rust/Go/Java JNI） | C API | 标准 C ABI，跨语言 FFI 友好 |
| 需要自定义 pass | C++ API | 可注册自定义 Pass 子类 |

## 典型优化管道

结合 ONNX 生态工具的完整优化管道：

```python
import onnx
import onnxoptimizer
from onnxsim import simplify  # onnx-simplifier（常量折叠）

# 1. 加载
model = onnx.load("model.onnx")
onnx.checker.check_model(model)

# 2. 常量折叠（onnx-simplifier，非 onnxoptimizer 功能）
model_simplified, check = simplify(model)
assert check, "Simplification failed"

# 3. 图优化（onnxoptimizer）
model_optimized = onnxoptimizer.optimize(
    model_simplified,
    fixed_point=True
)

# 4. 形状推断
model_optimized = onnx.shape_inference.infer_shapes(model_optimized)

# 5. 校验
onnx.checker.check_model(model_optimized)

# 6. 保存
onnx.save(model_optimized, "optimized.onnx")
```

> 注：onnxoptimizer 不做常量折叠（常量子图解释执行），这是 onnx-simplifier 的职责。两者互补：onnx-simplifier 折叠常量，onnxoptimizer 做图重写和死代码消除。

## 关联概念

- [ONNX Optimizer 整体架构](00-overall-architecture.md) — 了解三层 API 在整体架构中的位置
- [PassManager 执行模型与定点收敛](03-pass-execution.md) — 了解 fixed_point 参数的作用
- [内置优化 Passes 分类详解](02-builtin-passes.md) — 了解可指定的 pass 名称和功能
- [使用预打包优化 Passes 优化模型](../examples/optimize-model.md) — 完整的 Python 优化示例
