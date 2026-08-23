---
type: example
title: "从零构建线性回归模型"
description: "使用 make_tensor_value_info 定义输入输出→make_node 创建节点→make_graph 构建图→make_model 封装→save_model 保存的完整可运行代码"
sources:
  concepts: [../concepts/09-python-helpers.md, ../concepts/01-protobuf-ir.md, ../concepts/03-computation-graph.md, ../concepts/04-opset-versioning.md]
  references: [../references/helper-api.md, ../references/onnx-proto.md]
---

# 从零构建线性回归模型

## 目标

使用 ONNX Python Helper API 从零构建一个简单的线性回归模型 Y = X · W + B，并保存为 .onnx 文件。通过这个例子掌握 make_tensor_value_info、make_node、make_graph、make_model 的基本用法。

## 完整代码

```python
"""
从零构建线性回归模型: Y = X @ W + B
  X: [1, 3]  输入特征
  W: [3, 1]  权重
  B: [1, 1]  偏置
  Y: [1, 1]  输出预测
"""

import numpy as np
import onnx
from onnx import helper, TensorProto, numpy_helper


def build_linear_regression():
    """构建线性回归 ONNX 模型"""

    # ============================================================
    # 步骤1: 定义输入和输出（ValueInfoProto）
    # ============================================================
    # X 是运行时输入（动态batch可以用 "N" 等符号维度）
    X = helper.make_tensor_value_info(
        "X",       # 名字
        TensorProto.FLOAT,  # 数据类型
        [1, 3],    # 形状: [batch=1, features=3]
    )

    # Y 是模型输出
    Y = helper.make_tensor_value_info(
        "Y",
        TensorProto.FLOAT,
        [1, 1],    # [batch=1, output=1]
    )

    # ============================================================
    # 步骤2: 创建初始化器（常量权重，TensorProto）
    # ============================================================
    # 权重 W: shape [3, 1]
    W_data = np.array([[0.5], [-0.3], [0.8]], dtype=np.float32)
    W = numpy_helper.from_array(W_data, name="W")

    # 偏置 B: shape [1, 1]
    B_data = np.array([[0.1]], dtype=np.float32)
    B = numpy_helper.from_array(B_data, name="B")

    # 也可以用 make_tensor 创建（不用 numpy）:
    # W = helper.make_tensor(
    #     "W", TensorProto.FLOAT, [3, 1],
    #     [0.5, -0.3, 0.8]
    # )
    # B = helper.make_tensor(
    #     "B", TensorProto.FLOAT, [1, 1], [0.1]
    # )

    # ============================================================
    # 步骤3: 创建计算节点（NodeProto）
    # ============================================================
    # 矩阵乘法: MatMul(X, W) -> hidden
    matmul_node = helper.make_node(
        "MatMul",        # op_type
        ["X", "W"],      # inputs: 引用输入名和初始器名
        ["hidden"],      # outputs: 定义新的中间值名
        name="matmul",   # 节点名（可选）
    )

    # 加法: Add(hidden, B) -> Y
    add_node = helper.make_node(
        "Add",
        ["hidden", "B"],
        ["Y"],           # 输出名必须匹配 graph 的 output 名
        name="add",
    )

    # ============================================================
    # 步骤4: 构建计算图（GraphProto）
    # ============================================================
    graph = helper.make_graph(
        nodes=[matmul_node, add_node],  # 节点列表（拓扑序）
        name="linear_regression",       # 图名
        inputs=[X],                     # 图输入：只有 X（W 和 B 是常量）
        outputs=[Y],                    # 图输出
        initializer=[W, B],             # 初始化器：模型权重
    )

    # ============================================================
    # 步骤5: 封装为模型（ModelProto）
    # ============================================================
    # make_model 自动设置 ir_version 和 opset_import 为最新版本
    model = helper.make_model(
        graph,
        producer_name="linear_regression_example",
        producer_version="1.0",
        doc_string="A simple linear regression model: Y = X @ W + B",
    )

    # 也可以指定 opset 版本（更兼容）:
    # model = helper.make_model_gen_version(
    #     graph,
    #     producer_name="linear_regression_example",
    #     opset_imports=[helper.make_operatorsetid("", 17)],
    # )

    return model


def main():
    # 构建模型
    model = build_linear_regression()

    # ============================================================
    # 步骤6: 检查模型有效性
    # ============================================================
    try:
        onnx.checker.check_model(model, full_check=True)
        print("✓ 模型检查通过（full_check=True）")
    except onnx.checker.ValidationError as e:
        print(f"✗ 模型检查失败: {e}")
        return

    # ============================================================
    # 步骤7: 形状推断（填充 value_info）
    # ============================================================
    model = onnx.shape_inference.infer_shapes(model)
    print("✓ 形状推断完成")

    # 打印中间值信息
    print("\n中间值类型信息（value_info）:")
    for vi in model.graph.value_info:
        shape = [
            d.dim_value if d.dim_value else d.dim_param
            for d in vi.type.tensor_type.shape.dim
        ]
        print(f"  {vi.name}: {shape}")

    # ============================================================
    # 步骤8: 保存模型
    # ============================================================
    onnx.save(model, "linear_regression.onnx")
    print("\n✓ 模型已保存到 linear_regression.onnx")

    # ============================================================
    # 验证：打印模型结构
    # ============================================================
    print(f"\n模型摘要:")
    print(model)


if __name__ == "__main__":
    main()
```

## 构建与运行

```bash
# 安装 ONNX
pip install onnx numpy

# 运行脚本
python build_linear_regression.py
```

预期输出：
```
✓ 模型检查通过（full_check=True）
✓ 形状推断完成

中间值类型信息（value_info）:
  hidden: [1, 1]

✓ 模型已保存到 linear_regression.onnx

模型摘要:
ir_version: ...
opset_import: {"": ...}
producer_name: "linear_regression_example"
producer_version: "1.0"
graph: [1 inputs, 1 outputs, 2 nodes, 2 initializers]
```

## 要点解析

### 为什么 W 和 B 不在 inputs 中？

IR_VERSION >= 4（当前是14）支持 initializer 不在 graph.input 中声明。W 和 B 是模型的学习参数（常量权重），存储在 initializer 中随模型文件一起保存。graph.input 只包含运行时需要外部提供的输入（这里只有 X）。

如果在旧版 IR（<4）中，initializer 中的名字必须同时出现在 input 中：
```python
# 旧 IR 写法（不推荐，仅兼容旧引擎）
graph = helper.make_graph(
    nodes=[matmul_node, add_node],
    name="linear_regression",
    inputs=[X, W_info, B_info],  # 需要额外定义 W 和 B 的 ValueInfoProto
    outputs=[Y],
    initializer=[W, B],
)
```

### 节点顺序要求

nodes 列表中的节点应该按**拓扑序**排列（即被引用的节点必须在引用它的节点之前）。上例中 matmul_node 必须在 add_node 之前，因为 add_node 的输入 "hidden" 由 matmul_node 产生。

虽然 checker 不会严格验证拓扑序（只要名字引用存在即可），但保持拓扑序是好习惯，某些推理引擎依赖它。

### 字符串名字连接机制

注意节点之间通过**字符串名字**连接，而不是对象引用：
- matmul_node 定义输出名 "hidden"
- add_node 引用输入名 "hidden"

这意味着如果拼写错误（如 "hiddne"），checker 会在验证时报错"名字未定义"。

### make_model vs make_model_gen_version

- `make_model`：自动设置最新 IR_VERSION 和最新 opset，最简单但模型可能不兼容旧版推理引擎
- `make_model_gen_version`：根据指定的 opset_imports 自动计算最小需要的 IR_VERSION，最大化兼容性

### 动态形状

如果要支持动态 batch size，将 shape 中的具体数字替换为字符串：

```python
# 动态 batch 输入
X = helper.make_tensor_value_info(
    "X", TensorProto.FLOAT, ["batch_size", 3]
)
```

这样的模型可以接受任意 batch size 的输入。

## 延伸阅读

- [Python Helper API 详解](../concepts/09-python-helpers.md) — 深入了解 make_* 函数的参数和行为
- [计算图模型](../concepts/03-computation-graph.md) — 理解 initializer 与 input 的区别
- [张量类型系统](../concepts/02-tensor-type-system.md) — DataType 枚举和 shape 表示
- [模型加载、检查与形状推断](load-check-model.md) — 如何加载和验证模型
