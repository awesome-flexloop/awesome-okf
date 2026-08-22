---
type: example
title: "模型加载、检查与形状推断"
description: "load_model 加载→check_model 基础检查→infer_shapes 形状推断→check_model(full_check=True) 完整检查→numpy_helper.to_array 读取张量"
sources:
  concepts: [../concepts/07-model-checker.md, ../concepts/06-shape-inference.md, ../concepts/08-serialization.md, ../concepts/02-tensor-type-system.md]
  references: [../references/checker.md, ../references/shape-inference.md, ../references/serialization.md]
---

# 模型加载、检查与形状推断

## 目标

演示完整的模型加载、验证、形状推断和张量读取流程：从 .onnx 文件加载模型，执行基础检查、形状推断、完整验证，并从模型中读取权重数据为 numpy 数组。

## 完整代码

```python
"""
模型加载、检查与形状推断完整流程
"""

import numpy as np
import onnx
from onnx import numpy_helper, TensorProto


def load_and_verify_model(model_path: str) -> onnx.ModelProto:
    """加载模型并执行完整验证流程"""

    # ============================================================
    # 步骤1: 加载模型
    # ============================================================
    print(f"加载模型: {model_path}")
    model = onnx.load(model_path)

    # 也可以从字节流加载:
    # with open(model_path, "rb") as f:
    #     model = onnx.load(f)

    # 加载时不自动加载外部数据（对于大模型/外部数据模型）:
    # model = onnx.load(model_path, load_external_data=False)
    # # 后续按需加载:
    # onnx.load_external_data(model, base_dir="path/to/data")

    print(f"  IR 版本: {model.ir_version}")
    print(f"  Producer: {model.producer_name} v{model.producer_version}")

    # 打印 opset 信息
    print("  Opset 导入:")
    for opset in model.opset_import:
        domain = opset.domain if opset.domain else "(标准域)"
        print(f"    {domain}: v{opset.version}")

    # ============================================================
    # 步骤2: 基础结构检查（full_check=False，默认）
    # ============================================================
    print("\n执行基础结构检查...")
    try:
        onnx.checker.check_model(model)
        print("  ✓ 基础检查通过")
    except onnx.checker.ValidationError as e:
        print(f"  ✗ 基础检查失败: {e}")
        raise

    # 基础检查验证的内容:
    # - ir_version 设置且有效
    # - opset_import 存在（IR>=3）
    # - 节点输入引用的名字在图中定义
    # - 节点 op_type 在对应 opset 版本中存在
    # - 无重名
    # 注意: 基础检查不验证形状和类型兼容性！

    # ============================================================
    # 步骤3: 形状推断
    # ============================================================
    print("\n执行形状推断...")
    try:
        model = onnx.shape_inference.infer_shapes(
            model,
            check_type=False,    # 不做类型检查（宽松模式）
            strict_mode=False,   # 不抛节点级错误
            data_prop=False,     # 不做数据传播
        )
        print("  ✓ 形状推断完成")
    except Exception as e:
        print(f"  ✗ 形状推断失败: {e}")
        # 形状推断失败不一定意味着模型无效，可能是动态形状过于复杂

    # 其他选项:
    # infer_shapes(model, check_type=True)  # 检查类型一致性
    # infer_shapes(model, strict_mode=True) # 严格模式，遇到错误立即抛异常
    # infer_shapes(model, data_prop=True)   # 启用数据传播（更精确但更慢）

    # ============================================================
    # 步骤4: 完整检查（full_check=True）
    # ============================================================
    print("\n执行完整检查（含形状+类型验证）...")
    try:
        onnx.checker.check_model(model, full_check=True)
        print("  ✓ 完整检查通过——模型结构、形状、类型均有效")
    except onnx.checker.ValidationError as e:
        print(f"  ✗ 完整检查失败: {e}")
        print("    （可能存在形状不兼容或类型错误）")
        raise

    return model


def inspect_model_structure(model: onnx.ModelProto):
    """检查模型结构信息"""

    graph = model.graph
    print(f"\n模型结构:")
    print(f"  图名: {graph.name}")
    print(f"  输入数: {len(graph.input)}")
    print(f"  输出数: {len(graph.output)}")
    print(f"  节点数: {len(graph.node)}")
    print(f"  初始化器数: {len(graph.initializer)}")
    print(f"  中间值信息数: {len(graph.value_info)}")
    if model.functions:
        print(f"  局部函数数: {len(model.functions)}")

    # 打印输入信息
    print("\n输入:")
    for inp in graph.input:
        shape = get_shape_from_value_info(inp)
        dtype = get_dtype_name(inp.type.tensor_type.elem_type)
        print(f"  {inp.name}: {dtype}{shape}")

    # 打印输出信息
    print("\n输出:")
    for out in graph.output:
        shape = get_shape_from_value_info(out)
        dtype = get_dtype_name(out.type.tensor_type.elem_type)
        print(f"  {out.name}: {dtype}{shape}")

    # 统计算子类型
    op_counts = {}
    for node in graph.node:
        key = f"{node.domain}.{node.op_type}" if node.domain else node.op_type
        op_counts[key] = op_counts.get(key, 0) + 1
    print("\n算子统计:")
    for op, count in sorted(op_counts.items(), key=lambda x: -x[1]):
        print(f"  {op}: {count}")


def get_shape_from_value_info(vi: onnx.ValueInfoProto) -> list:
    """从 ValueInfoProto 提取形状列表"""
    if not vi.type.HasField("tensor_type"):
        return ["<non-tensor>"]
    shape = []
    for d in vi.type.tensor_type.shape.dim:
        if d.dim_value:
            shape.append(d.dim_value)
        elif d.dim_param:
            shape.append(d.dim_param)
        else:
            shape.append("?")
    return shape


def get_dtype_name(elem_type: int) -> str:
    """将 DataType 枚举值转换为可读名称"""
    dtype_map = {
        TensorProto.FLOAT: "float32",
        TensorProto.DOUBLE: "float64",
        TensorProto.FLOAT16: "float16",
        TensorProto.INT8: "int8",
        TensorProto.INT16: "int16",
        TensorProto.INT32: "int32",
        TensorProto.INT64: "int64",
        TensorProto.UINT8: "uint8",
        TensorProto.UINT16: "uint16",
        TensorProto.UINT32: "uint32",
        TensorProto.UINT64: "uint64",
        TensorProto.BOOL: "bool",
        TensorProto.STRING: "string",
        TensorProto.BFLOAT16: "bfloat16",
    }
    return dtype_map.get(elem_type, f"type_{elem_type}")


def read_weights(model: onnx.ModelProto) -> dict:
    """从模型中读取所有权重为 numpy 数组"""
    weights = {}
    for init in model.graph.initializer:
        arr = numpy_helper.to_array(init)
        weights[init.name] = arr
        print(f"  权重 '{init.name}': shape={arr.shape}, dtype={arr.dtype}")
    return weights


def infer_shapes_for_dynamic_inputs(model: onnx.ModelProto) -> onnx.ModelProto:
    """使用符号形状推断（处理动态维度）"""
    # 对于含动态维度的模型（如 batch_size），infer_shapes 仍然可以
    # 推断出中间张量的秩和部分维度关系
    model = onnx.shape_inference.infer_shapes(model)

    print("\n推断后的中间值信息:")
    for vi in model.graph.value_info:
        shape = get_shape_from_value_info(vi)
        dtype = get_dtype_name(vi.type.tensor_type.elem_type)
        print(f"  {vi.name}: {dtype}{shape}")

    return model


def main():
    # 如果有上一个例子生成的模型，加载它
    model_path = "linear_regression.onnx"

    try:
        model = load_and_verify_model(model_path)
    except FileNotFoundError:
        print(f"未找到 {model_path}，请先运行 build-linear-regression 示例")
        print("或加载任意 ONNX 模型文件")
        return

    # 检查模型结构
    inspect_model_structure(model)

    # 读取权重
    print("\n读取权重数据:")
    weights = read_weights(model)

    # 例如：使用权重进行计算
    if "W" in weights and "B" in weights:
        print("\n权重验证:")
        print(f"  W =\n{weights['W']}")
        print(f"  B =\n{weights['B']}")

        # 手动计算验证
        X = np.array([[1.0, 2.0, 3.0]], dtype=np.float32)
        Y_expected = X @ weights["W"] + weights["B"]
        print(f"\n  手动验证: X={X} → Y={Y_expected}")

    # 保存推断后的模型
    inferred_path = "linear_regression_inferred.onnx"
    onnx.save(model, inferred_path)
    print(f"\n推断后的模型已保存到: {inferred_path}")


if __name__ == "__main__":
    main()
```

## 构建与运行

```bash
# 确保已安装 ONNX 和 numpy
pip install onnx numpy

# 先运行前一个示例生成模型
python build_linear_regression.py

# 然后运行本例
python load_check_model.py
```

预期输出（使用线性回归模型时）：
```
加载模型: linear_regression.onnx
  IR 版本: 14
  Producer: linear_regression_example v1.0
  Opset 导入:
    (标准域): v...

执行基础结构检查...
  ✓ 基础检查通过

执行形状推断...
  ✓ 形状推断完成

执行完整检查（含形状+类型验证）...
  ✓ 完整检查通过——模型结构、形状、类型均有效

模型结构:
  图名: linear_regression
  输入数: 1
  输出数: 1
  节点数: 2
  初始化器数: 2
  ...
```

## 要点解析

### check_model vs check_model(full_check=True) 的区别

| 检查项 | 默认 (full_check=False) | full_check=True |
|--------|------------------------|-----------------|
| ir_version/opset 验证 | ✅ | ✅ |
| 名字引用合法性 | ✅ | ✅ |
| 算子存在性 | ✅ | ✅ |
| 形状推断 | ❌ | ✅（在副本上执行） |
| 类型一致性检查 | ❌ | ✅（check_type=true） |
| 节点级错误处理 | 宽松 | 严格（error_mode=1） |

**最佳实践**：开发调试阶段用默认检查快速验证结构，发布/部署前用 full_check=True 做完整验证。

### infer_shapes 不修改原模型

`infer_shapes()` 返回新的 ModelProto 对象（C++ 端对序列化副本操作），原模型不会被修改。必须使用返回值获取推断结果。

```python
# ❌ 错误：原模型不会被修改
onnx.shape_inference.infer_shapes(model)
# model.graph.value_info 仍然为空

# ✅ 正确：使用返回值
model = onnx.shape_inference.infer_shapes(model)
# model.graph.value_info 现在包含推断结果
```

### numpy_helper.to_array 的完整行为

`to_array()` 处理多种数据存储方式：
1. 有 `raw_data` 时：按小端序读取，大端系统自动 byteswap
2. 有类型特定字段时：从 float_data/int32_data/int64_data 等读取
3. 使用外部数据时：自动从外部文件加载
4. 亚字节类型（INT4/UINT4/INT2/UINT2）：自动解包

### 动态形状的处理

对于含动态维度的模型（如 `["batch", 3, 224, 224]`），形状推断仍然有效——它可以推断出中间张量的秩和静态已知的维度。符号维度（如 "batch"）会在推断中传播。

### 加载外部数据模型

对于使用外部数据的大模型：

```python
# 方式1：默认加载外部数据（需要数据文件在模型同目录）
model = onnx.load("large_model.onnx")  # load_external_data=True

# 方式2：仅加载结构（不加载权重数据）
model = onnx.load("large_model.onnx", load_external_data=False)

# 后续按需加载
onnx.load_external_data(model, base_dir="path/to/model_dir")
```

## 延伸阅读

- [模型检查器 Checker](../concepts/07-model-checker.md) — 深入了解验证规则
- [形状推断实现](../concepts/06-shape-inference.md) — 形状推断的工作原理
- [序列化/反序列化与外部数据](../concepts/08-serialization.md) — 外部数据加载机制
- [从零构建线性回归模型](build-linear-regression.md) — 生成示例模型
- [图遍历与变换实战](graph-transformation.md) — 在加载的模型上进行修改
