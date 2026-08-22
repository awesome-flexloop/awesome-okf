---
type: example
title: "图遍历与变换实战"
description: "遍历 GraphProto.node、修改节点属性、添加/删除节点、操作 initializer、形状推断后访问 value_info 的实战代码"
sources:
  concepts: [../concepts/03-computation-graph.md, ../concepts/01-protobuf-ir.md, ../concepts/06-shape-inference.md, ../concepts/09-python-helpers.md]
  references: [../references/onnx-proto.md, ../references/helper-api.md, ../references/shape-inference.md]
---

# 图遍历与变换实战

## 目标

掌握在 Python 端操作 ONNX 计算图（Protobuf message）的常用技巧：遍历节点、查找特定算子、修改属性、添加/删除节点、操作初始化器（权重）、以及在形状推断后访问中间值类型信息。

> **前提**：Python 端没有 Graph/Node 类，所有操作直接在 Protobuf message 对象上进行。

## 完整代码

```python
"""
图遍历与变换实战：直接操作 Protobuf message
"""

import copy
import numpy as np
import onnx
from onnx import helper, TensorProto, numpy_helper


def load_or_create_model():
    """加载已有模型或创建一个示例模型"""
    try:
        return onnx.load("linear_regression.onnx")
    except FileNotFoundError:
        # 创建一个稍微复杂的示例模型: Y = Relu(X @ W + B)
        X = helper.make_tensor_value_info("X", TensorProto.FLOAT, [1, 3])
        Y = helper.make_tensor_value_info("Y", TensorProto.FLOAT, [1, 2])

        W = numpy_helper.from_array(
            np.random.randn(3, 2).astype(np.float32), name="W"
        )
        B = numpy_helper.from_array(
            np.zeros((1, 2), dtype=np.float32), name="B"
        )

        matmul = helper.make_node("MatMul", ["X", "W"], ["hidden"])
        add = helper.make_node("Add", ["hidden", "B"], ["biased"])
        relu = helper.make_node("Relu", ["biased"], ["Y"])

        graph = helper.make_graph(
            [matmul, add, relu],
            "mlp",
            [X], [Y],
            [W, B],
        )
        model = helper.make_model(graph)
        onnx.checker.check_model(model, full_check=True)
        return model


# ================================================================
# 1. 图遍历
# ================================================================

def traverse_graph(model: onnx.ModelProto):
    """遍历图中的节点、输入、输出、初始化器"""
    graph = model.graph

    print("=" * 60)
    print("1. 图遍历")
    print("=" * 60)

    # 遍历所有节点
    print("\n所有节点:")
    for i, node in enumerate(graph.node):
        print(f"  [{i}] {node.op_type} (name='{node.name}')")
        print(f"      inputs: {list(node.input)}")
        print(f"      outputs: {list(node.output)}")
        if node.attribute:
            print(f"      attributes:")
            for attr in node.attribute:
                print(f"        {attr.name}: {attr_value_to_str(attr)}")

    # 构建名字→初始化器映射
    init_map = {init.name: init for init in graph.initializer}
    print(f"\n初始化器: {list(init_map.keys())}")

    # 构建名字→ValueInfo映射（输入+输出+value_info）
    value_info_map = {}
    for vi in list(graph.input) + list(graph.output) + list(graph.value_info):
        value_info_map[vi.name] = vi

    return init_map, value_info_map


def attr_value_to_str(attr: onnx.AttributeProto) -> str:
    """将属性值转换为可读字符串"""
    if attr.type == AttributeProto.FLOAT:
        return f"float = {attr.f}"
    elif attr.type == AttributeProto.INT:
        return f"int = {attr.i}"
    elif attr.type == AttributeProto.STRING:
        return f"string = {attr.s.decode()}"
    elif attr.type == AttributeProto.INTS:
        return f"ints = {list(attr.ints)}"
    elif attr.type == AttributeProto.FLOATS:
        return f"floats = {list(attr.floats)}"
    elif attr.type == AttributeProto.TENSOR:
        return f"tensor shape={list(attr.t.dims)}"
    else:
        return f"type={attr.type}"


# 需要导入 AttributeProto
from onnx import AttributeProto


# ================================================================
# 2. 查找特定算子
# ================================================================

def find_nodes_by_op_type(graph: onnx.GraphProto, op_type: str) -> list:
    """查找指定类型的所有节点"""
    return [node for node in graph.node if node.op_type == op_type]


def find_node_by_output(graph: onnx.GraphProto, output_name: str):
    """查找生产指定输出的节点"""
    for node in graph.node:
        if output_name in node.output:
            return node
    return None


def find_consumers(graph: onnx.GraphProto, value_name: str) -> list:
    """查找消费指定值的所有节点"""
    consumers = []
    for node in graph.node:
        if value_name in node.input:
            consumers.append(node)
    return consumers


# ================================================================
# 3. 修改节点属性
# ================================================================

def modify_node_attributes(model: onnx.ModelProto) -> onnx.ModelProto:
    """修改节点属性示例：为 Conv 节点添加/修改属性"""
    # 创建副本，不修改原模型
    model = copy.deepcopy(model)
    graph = model.graph

    print("\n" + "=" * 60)
    print("3. 修改节点属性")
    print("=" * 60)

    # 示例：查找第一个节点并修改其 name 属性
    if len(graph.node) > 0:
        node = graph.node[0]
        old_name = node.name
        node.name = "modified_node"
        print(f"  将节点 [{node.op_type}] 的 name 从 '{old_name}' 改为 '{node.name}'")

    # 添加一个属性（以一个有属性的节点为例）
    # 如果有 Relu 节点（通常无属性），我们可以添加 doc_string
    for node in graph.node:
        if node.op_type == "Relu":
            node.doc_string = "ReLU activation function"
            print(f"  为 {node.name or node.op_type} 添加 doc_string")

    return model


# ================================================================
# 4. 替换/添加节点（图变换）
# ================================================================

def add_sigmoid_after_relu(model: onnx.ModelProto) -> onnx.ModelProto:
    """在 Relu 输出后添加 Sigmoid 节点（示例：修改输出路径）"""
    model = copy.deepcopy(model)
    graph = model.graph

    print("\n" + "=" * 60)
    print("4. 图变换：添加 Sigmoid 节点")
    print("=" * 60)

    # 查找 Relu 节点
    relu_nodes = find_nodes_by_op_type(graph, "Relu")
    if not relu_nodes:
        print("  未找到 Relu 节点，跳过")
        return model

    relu_node = relu_nodes[0]
    relu_output = relu_node.output[0]  # 通常是 "Y"

    # 创建新的输出名
    sigmoid_output = relu_output + "_sigmoid"

    # 创建 Sigmoid 节点
    sigmoid_node = helper.make_node(
        "Sigmoid",
        [relu_output],      # 输入是 Relu 的输出
        [sigmoid_output],   # 新的输出名
        name="added_sigmoid",
    )

    # 找到 Relu 节点在列表中的位置
    relu_idx = list(graph.node).index(relu_node)

    # 在 Relu 后面插入 Sigmoid 节点
    graph.node.insert(relu_idx + 1, sigmoid_node)

    # 找到原来的输出（output中引用 relu_output 的），将其改为引用 sigmoid_output
    for output in graph.output:
        if output.name == relu_output:
            output.name = sigmoid_output

    # 也需要更新消费 relu_output 的其他节点（如果有）
    # 在这个简单例子中，relu_output 是图输出，所以只需要改 graph.output

    # 更新名字：我们需要确保原始输出名对应的 ValueInfo 也更新
    # 更好的做法是：找到 consumers 并逐个更新
    for consumer in find_consumers(graph, relu_output):
        # 注意：sigmoid_node 自己也是 consumer，但我们不想改它
        if consumer == sigmoid_node:
            continue
        for i, inp in enumerate(consumer.input):
            if inp == relu_output:
                consumer.input[i] = sigmoid_output

    print(f"  在 Relu 后添加了 Sigmoid 节点")
    print(f"  新的输出路径: ... → Relu → Sigmoid → {sigmoid_output}")

    return model


# ================================================================
# 5. 操作初始化器（权重）
# ================================================================

def modify_weights(model: onnx.ModelProto) -> onnx.ModelProto:
    """读取和修改模型权重"""
    model = copy.deepcopy(model)
    graph = model.graph

    print("\n" + "=" * 60)
    print("5. 操作初始化器（权重）")
    print("=" * 60)

    # 方法1：直接遍历 initializer 列表
    for init in graph.initializer:
        arr = numpy_helper.to_array(init)
        print(f"  权重 '{init.name}': shape={arr.shape}, mean={arr.mean():.4f}")

    # 方法2：通过名字查找特定权重
    init_map = {init.name: init for init in graph.initializer}
    if "B" in init_map:
        B_arr = numpy_helper.to_array(init_map["B"])
        print(f"\n  原偏置 B = {B_arr.flatten()}")

        # 修改偏置值：加 0.1
        new_B = (B_arr + 0.1).astype(np.float32)
        new_B_tensor = numpy_helper.from_array(new_B, name="B")

        # 替换 initializer（需要找到正确的索引）
        for i, init in enumerate(graph.initializer):
            if init.name == "B":
                graph.initializer[i].CopyFrom(new_B_tensor)
                break

        print(f"  新偏置 B = {new_B.flatten()}")

    # 添加新的初始化器
    new_const = numpy_helper.from_array(
        np.array([42.0], dtype=np.float32), name="my_constant"
    )
    graph.initializer.append(new_const)
    print(f"\n  添加了新的初始化器: 'my_constant'")

    return model


# ================================================================
# 6. 形状推断后访问 value_info
# ================================================================

def inspect_shapes(model: onnx.ModelProto):
    """执行形状推断并检查中间值形状"""
    print("\n" + "=" * 60)
    print("6. 形状推断与中间值类型信息")
    print("=" * 60)

    # 执行形状推断
    model = onnx.shape_inference.infer_shapes(model)

    print(f"\n  推断后 value_info 数量: {len(model.graph.value_info)}")
    print("\n  中间值类型信息:")
    for vi in model.graph.value_info:
        if vi.type.HasField("tensor_type"):
            shape = []
            for d in vi.type.tensor_type.shape.dim:
                if d.dim_value:
                    shape.append(d.dim_value)
                elif d.dim_param:
                    shape.append(d.dim_param)
                else:
                    shape.append("?")
            dtype = vi.type.tensor_type.elem_type
            print(f"    {vi.name}: dtype={dtype}, shape={shape}")

    return model


# ================================================================
# 7. 删除节点（注意：需要重连边）
# ================================================================

def remove_relu(model: onnx.ModelProto) -> onnx.ModelProto:
    """删除指定节点并重新连接边（示例：移除 Relu 激活）"""
    model = copy.deepcopy(model)
    graph = model.graph

    print("\n" + "=" * 60)
    print("7. 删除节点（移除 Relu）")
    print("=" * 60)

    relu_nodes = find_nodes_by_op_type(graph, "Relu")
    if not relu_nodes:
        print("  未找到 Relu 节点，跳过")
        return model

    relu_node = relu_nodes[0]
    relu_input = relu_node.input[0]   # Relu 的输入（来自前一个节点）
    relu_output = relu_node.output[0] # Relu 的输出（图输出或后续节点输入）

    print(f"  Relu 节点: input={relu_input}, output={relu_output}")

    # 步骤1：将所有引用 relu_output 的地方改为引用 relu_input
    # （相当于"短路"Relu 节点）
    for node in graph.node:
        for i, inp in enumerate(node.input):
            if inp == relu_output:
                node.input[i] = relu_input
                print(f"  重连: {node.op_type}.input[{i}] {relu_output} → {relu_input}")

    # 更新图输出
    for output in graph.output:
        if output.name == relu_output:
            output.name = relu_input
            print(f"  重连: graph.output {relu_output} → {relu_input}")

    # 步骤2：从节点列表中移除 Relu 节点
    nodes_list = list(graph.node)
    nodes_list.remove(relu_node)

    # Clear and re-add
    del graph.node[:]
    graph.node.extend(nodes_list)

    print(f"  已删除 Relu 节点，当前节点数: {len(graph.node)}")

    return model


def main():
    # 加载/创建模型
    model = load_or_create_model()
    print("原始模型:")
    print(model)

    # 1. 遍历
    init_map, vi_map = traverse_graph(model)

    # 2. 查找
    print("\n" + "=" * 60)
    print("2. 查找操作")
    print("=" * 60)
    matmul_nodes = find_nodes_by_op_type(model.graph, "MatMul")
    print(f"  MatMul 节点数: {len(matmul_nodes)}")

    y_producer = find_node_by_output(model.graph, "hidden")
    if y_producer:
        print(f"  生产 'hidden' 的节点: {y_producer.op_type}")

    w_consumers = find_consumers(model.graph, "W")
    print(f"  消费 'W' 的节点数: {len(w_consumers)}")

    # 3. 修改属性
    model = modify_node_attributes(model)

    # 4. 添加节点
    model = add_sigmoid_after_relu(model)

    # 5. 修改权重
    model = modify_weights(model)

    # 6. 形状推断
    model = inspect_shapes(model)

    # 验证变换后的模型
    print("\n" + "=" * 60)
    print("验证变换后的模型")
    print("=" * 60)
    try:
        onnx.checker.check_model(model, full_check=True)
        print("  ✓ 变换后的模型验证通过")
    except onnx.checker.ValidationError as e:
        print(f"  ✗ 验证失败: {e}")

    # 7. 删除节点
    model = remove_relu(model)

    # 再次验证
    try:
        onnx.checker.check_model(model, full_check=True)
        print("  ✓ 删除节点后验证通过")
    except onnx.checker.ValidationError as e:
        print(f"  ✗ 删除后验证失败: {e}")

    # 保存变换后的模型
    onnx.save(model, "transformed_model.onnx")
    print("\n变换后的模型已保存到 transformed_model.onnx")


if __name__ == "__main__":
    main()
```

## 构建与运行

```bash
pip install onnx numpy

# 如果有 linear_regression.onnx 则加载，否则自动创建示例模型
python graph_transformation.py
```

## 要点解析

### Python 端图操作的本质

Python 端操作的始终是 Protobuf message 对象。Protobuf 的 `repeated` 字段（如 `graph.node`、`node.input`）类似 Python 列表，可以：
- 遍历：`for node in graph.node`
- 索引访问：`graph.node[0]`
- 添加：`graph.node.append(new_node)`
- 删除：需要 `del graph.node[:]` 后重新 extend，或使用 list 转换操作
- 修改：直接赋值属性 `node.name = "new_name"`

### 图变换的核心：边重连

添加或删除节点时，核心操作是**重连边**（修改 input/output 字符串引用）：

```python
# 添加节点后：
# 1. 新节点的 input 引用前一个节点的 output
new_node = helper.make_node("Op", [old_output], [new_output])
# 2. 所有原来引用 old_output 的地方改为引用 new_output
for consumer in consumers_of(old_output):
    consumer.input[i] = new_output
# 3. 插入节点到正确位置
graph.node.insert(idx + 1, new_node)

# 删除节点时：
# 1. 将被删除节点的输入"短路"给消费者
for consumer in consumers_of(removed_output):
    consumer.input[i] = removed_input
# 2. 从列表移除节点
```

### 重要：深拷贝

修改模型前使用 `copy.deepcopy(model)` 创建副本，避免意外修改原始模型。ONNX Protobuf 对象支持 Python 的 deepcopy。

### initializer 替换注意事项

替换 initializer 时，不能直接赋值（`graph.initializer[i] = new_tensor` 在某些 protobuf 版本中可能有问题），更安全的方式是使用 `CopyFrom`：

```python
graph.initializer[i].CopyFrom(new_tensor_proto)
```

### value_info 不自动更新

手动修改图结构后，value_info 不会自动更新。需要重新运行 `infer_shapes()` 才能获得正确的中间值类型信息。

### 删除节点不是简单的 list.remove

删除节点后必须：
1. 将所有引用该节点输出的 input 重定向到该节点的输入（或适当的值）
2. 更新图输出（如果被删除节点的输出是图输出）
3. 然后才从 node 列表移除节点

否则会产生"名字未定义"的引用，checker 会报错。

## 延伸阅读

- [计算图模型](../concepts/03-computation-graph.md) — 理解字符串名字连接机制
- [Protobuf IR：核心 Message 结构](../concepts/01-protobuf-ir.md) — NodeProto/GraphProto 的字段定义
- [形状推断实现](../concepts/06-shape-inference.md) — value_info 的生成方式
- [模型加载、检查与形状推断](load-check-model.md) — 模型验证流程
