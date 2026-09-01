---
type: reference
title: "Python API、命令行 API 与 C API"
description: "onnxoptimizer Python 包入口、nanobind C++ 绑定、命令行工具、纯 C API、模型 IO 工具、辅助工具库的源码信源登记"
sources:
  - path: "external/libs/models/onnx/optimizer/onnxoptimizer/__init__.py"
    facts: [F-006, F-007, F-008, F-009, F-010]
  - path: "external/libs/models/onnx/optimizer/onnxoptimizer/cpp2py_export.cc"
    facts: [F-011, F-012]
  - path: "external/libs/models/onnx/optimizer/onnxoptimizer/__main__.py"
    facts: [F-013]
  - path: "external/libs/models/onnx/optimizer/onnxoptimizer/onnxoptimizer_main.py"
    facts: [F-014, F-015]
  - path: "external/libs/models/onnx/optimizer/onnxoptimizer/model_util.h"
    facts: [F-054]
  - path: "external/libs/models/onnx/optimizer/onnxoptimizer/model_util.cc"
    facts: [F-054, F-055]
  - path: "external/libs/models/onnx/optimizer/onnxoptimizer/c_api/onnxoptimizer_c_api.h"
    facts: [F-056]
  - path: "external/libs/models/onnx/optimizer/onnxoptimizer/passes/pass_util.h"
    facts: [F-057]
  - path: "external/libs/models/onnx/optimizer/onnxoptimizer/passes/data_type.h"
    facts: [F-058]
  - path: "external/libs/models/onnx/optimizer/onnxoptimizer/passes/rename_input_output.h"
    facts: [F-059]
  - path: "external/libs/models/onnx/optimizer/examples/onnx_optimizer_exec.cpp"
    facts: [F-060]
---

# Python API、命令行 API 与 C API

## 信源概述

| 信源 | 类型 | 职责 |
|------|------|------|
| `onnxoptimizer/__init__.py` | Python | Python 包入口，optimize/get_available_passes 等函数 |
| `onnxoptimizer/cpp2py_export.cc` | C++ | nanobind C++→Python 绑定定义 |
| `onnxoptimizer/__main__.py` | Python | 命令行入口 `python -m onnxoptimizer` |
| `onnxoptimizer/onnxoptimizer_main.py` | Python | CLI 参数解析与执行流程 |
| `onnxoptimizer/model_util.h/cc` | C++ | 模型加载/保存，外部数据处理 |
| `onnxoptimizer/c_api/onnxoptimizer_c_api.h` | C | 纯 C API 声明 |
| `onnxoptimizer/passes/pass_util.h` | C++ | Pass 开发工具模板函数库 |
| `onnxoptimizer/passes/data_type.h` | C++ | 自定义数据类型（FP16/BF16/复数） |
| `onnxoptimizer/passes/rename_input_output.h` | C++ | 环境变量控制的输入输出重命名 pass |
| `examples/onnx_optimizer_exec.cpp` | C++ | C++ 使用示例 |

## F-006~F-010：Python API

### F-006：公开导出符号

Python 包 `onnxoptimizer` 通过 `__init__.py` 导出四个公开符号：

| 符号 | 类型 | 说明 |
|------|------|------|
| `optimize` | 函数 | 核心优化函数 |
| `get_available_passes` | 函数 | 获取所有可用 pass 名称 |
| `get_fuse_and_elimination_passes` | 函数 | 获取默认优化集名称 |
| `main` | 函数 | CLI 入口函数 |

### F-007：optimize() 函数签名

```python
def optimize(
    model: onnx.ModelProto,
    passes: list[str] | None = None,
    fixed_point: bool = False
) -> onnx.ModelProto
```

参数：
- `model`：输入 ONNX 模型（ModelProto 对象）
- `passes`：要执行的 pass 名称列表，`None` 表示使用默认 fuse+elimination 集合
- `fixed_point`：是否启用定点迭代模式

### F-008：默认 pass 集合

当 `passes=None` 时，`optimize()` 调用 `get_fuse_and_elimination_passes()` 获取默认 pass 集合，仅包含 Fuse 和 Nop 类型的 pass。

### F-009~F-010：大模型回退路径

```
optimize(model, passes, fixed_point):
  try:
    # 路径1：内存序列化（适用于 <2GB 模型）
    model_bytes = model.SerializeToString()
    if fixed_point:
      result_bytes = _c.optimize_fixedpoint(model_bytes, passes)
    else:
      result_bytes = _c.optimize(model_bytes, passes)
    return onnx.ModelProto.FromString(result_bytes)
  except ValueError:
    # 路径2：临时文件（适用于 >2GB 模型，序列化 ValueError）
    tmp_dir = tempfile.mkdtemp()
    try:
      tmp_in = os.path.join(tmp_dir, "tmp_in.onnx")
      tmp_out = os.path.join(tmp_dir, "tmp_out.onnx")
      onnx.save(model, tmp_in, save_as_external_data=True)
      if fixed_point:
        _c.optimize_fixedpoint_from_path(tmp_in, tmp_out, passes, "data")
      else:
        _c.optimize_from_path(tmp_in, tmp_out, passes, "data")
      return onnx.load(tmp_out)
    finally:
      # 清理所有临时文件
      shutil.rmtree(tmp_dir)
```

当模型超过 2GB 时，protobuf 序列化会抛出 `ValueError`，此时自动回退到临时文件路径，使用 `save_as_external_data=True` 保存模型，通过文件路径调用 C++ 层优化后再加载。

## F-011~F-012：nanobind C++ 绑定

### F-011：绑定模块

C++ 绑定模块名为 `onnx_opt_cpp2py_export`，通过 nanobind 库绑定（而非 pybind11）。

### F-012：暴露的 C++ 函数

nanobind 模块向 Python 暴露六个 C++ 函数：

| 函数 | 签名 | 说明 |
|------|------|------|
| `optimize(bytes, names)` | `(bytes, list[str]) → bytes` | 内存模式单次优化 |
| `optimize_fixedpoint(bytes, names)` | `(bytes, list[str]) → bytes` | 内存模式定点优化 |
| `optimize_from_path(import_path, export_path, names, data_file_name)` | `(str, str, list[str], str) → None` | 文件模式单次优化 |
| `optimize_fixedpoint_from_path(import_path, export_path, names, data_file_name)` | `(str, str, list[str], str) → None` | 文件模式定点优化 |
| `get_available_passes()` | `() → list[str]` | 获取所有 pass 名称 |
| `get_fuse_and_elimination_passes()` | `() → list[str]` | 获取默认 pass 名称 |

## F-013~F-015：命令行 API

### F-013：命令行入口

```bash
python -m onnxoptimizer input_model.onnx output_model.onnx
```

通过 `__main__.py` 调用 `main()` 函数。

### F-014：CLI 参数

| 参数 | 说明 |
|------|------|
| `--print_all_passes` | 打印所有可用 passes 并退出 |
| `--print_fuse_elimination_passes` | 打印融合和消除 passes 并退出 |
| `-p` / `--passes` | 指定优化 passes 列表（逗号分隔或 nargs='+'） |
| `--fixed_point` | 启用定点迭代优化 |
| `--skip_infer_shapes` | 跳过优化后形状推断 |

### F-015：CLI 执行流程

```
1. onnx.load(input_path) → 加载模型
2. onnx.checker.check_model(input) → 校验输入模型
3. onnxoptimizer.optimize(model, passes, fixed_point) → 执行优化
4. 若未指定 --skip_infer_shapes:
     onnx.shape_inference.infer_shapes(model) → 形状推断
5. onnx.save(output) → 保存（大模型自动 save_as_external_data=True）
6. onnx.checker.check_model(output) → 校验输出模型
```

## F-054~F-055：模型 IO 与外部数据

### F-054：loadModel / saveModel

`model_util.h/cc` 提供模型加载/保存功能：

- `loadModel(path, load_external_data=True)`：从路径加载 ModelProto，可选加载外部张量数据
- `saveModel(mp, path, size_threshold=1024)`：序列化模型到文件，tensor 超过阈值时自动转外部数据

### F-055：外部数据格式

外部数据格式中 tensor 的 `external_data` 字段包含三个键值对：
- `location`：数据文件名
- `offset`：在数据文件中的字节偏移
- `length`：数据字节长度

`saveModel` 以 append 模式将所有外部张量的 raw_data 写入同一个数据文件，使用 UUID 生成唯一数据文件名，各张量记录各自的偏移量和长度。

## F-056：纯 C API

`c_api/onnxoptimizer_c_api.h` 暴露以下 C 函数：

| 函数 | 说明 |
|------|------|
| `C_API_GetAvailablePasses(const char*** out_names, int* out_len)` | 获取所有 pass 名称 |
| `C_API_GetFuseAndEliminationPass(const char*** out_names, int* out_len)` | 获取默认 pass 名称 |
| `C_API_ReleasePasses(const char** names, int len)` | 释放 pass 名称数组内存 |
| `C_API_Optimize(const void* in_data, int in_size, const char** passes, int num_passes, void** out_data, int* out_size, int fixed_point)` | 内存缓冲模式优化 |
| `C_API_OtimizeFromFile(const char* in_path, const char* out_path, const char** passes, int num_passes, int fixed_point, const char* data_file_name)` | 文件模式优化（注意函数名拼写：Otimize 非 Optimize） |

> ⚠️ **已知 API 缺陷**：`C_API_OtimizeFromFile` 函数名缺少 'p'（`Otimize` 而非 `Optimize`），因 C ABI 兼容性原因无法修复。调用者必须负责调用 `C_API_ReleasePasses()` 释放 `C_API_GetAvailablePasses()` 和 `C_API_GetFuseAndEliminationPass()` 返回的字符串数组。

## F-057：pass_util.h 工具函数库

`pass_util.h` 提供大量模板工具函数供 pass 实现使用：

| 函数/模板 | 用途 |
|-----------|------|
| `CheckKind<T>()` | 递归检查节点/前驱算子类型 |
| `IsConstantTensor(v)` | 判断值是否为常量节点或 initializer |
| `FetchConstantTensor(v)` | 获取常量张量指针 |
| `GetValueFromAttr<T>(node, name)` | 类型安全的属性读取（无默认值） |
| `GetValueFromAttrWithDefault<T>(node, name, default)` | 带默认值的属性读取 |
| `GetValueFromInput<T>(node, idx)` | 从常量输入读取张量数据 |
| `PrevNode(node, idx)` | 获取前驱节点（支持链式调用） |
| `FetchSoleIntValueOfTensor(tensor)` | 获取标量张量的整数值 |
| `isABroadcastToB(a_shape, b_shape)` | 广播兼容性检查 |

## F-058：自定义数据类型

`data_type.h` 定义项目自定义数据类型：

| 类型 | 底层表示 | 说明 |
|------|----------|------|
| `Complex64` | `std::complex<float>` | float 复数 |
| `Complex128` | `std::complex<double>` | double 复数 |
| `Float16` | `uint16_t` | FP16 位模式 |
| `BFloat16` | `uint16_t` | BF16 位模式（通过 FP32ToBits/FP32FromBits 转换） |

并在 `std` 命名空间特化了 `hash` 模板以支持哈希表使用。

## F-059：环境变量控制的重命名

`rename_input_output` pass 从环境变量读取命名模式：
- `OPTIMIZER_RENAME_INPUT_PATTERN`：输入命名模式，默认 `input_%d`
- `OPTIMIZER_RENAME_OUTPUT_PATTERN`：输出命名模式，默认 `output_%d`

按索引重命名图的输入和输出，跳过同时是 initializer 的输入。

## F-060：C++ 使用示例

`examples/onnx_optimizer_exec.cpp` 展示标准 C++ 使用流程：

```cpp
#include "onnxoptimizer/model_util.h"
#include "onnxoptimizer/optimize.h"

int main(int argc, char** argv) {
  // 1. 加载模型
  auto model = onnx::optimization::loadModel(argv[1]);
  // 2. 校验
  onnx::checker::check_model(model);
  // 3. 优化（使用默认 fuse+elimination passes）
  auto result = onnx::optimization::Optimize(
      model,
      onnx::optimization::GetFuseAndEliminationPass());
  // 4. 校验结果
  onnx::checker::check_model(result);
  // 5. 保存
  onnx::optimization::saveModel(result, argv[2]);
  return 0;
}
```
