---
type: example
title: "自定义算子注册与使用示例"
description: "使用 helper.py 构建包含自定义算子的模型、理解 OpSchema 算子签名、在模型中使用自定义 op、checker 对自定义 op 的行为"
sources:
  concepts: [../concepts/05-operator-schema.md, ../concepts/07-model-checker.md, ../concepts/09-python-helpers.md, ../concepts/04-opset-versioning.md]
  references: [../references/op-schema.md, ../references/helper-api.md, ../references/checker.md]
---

# 自定义算子注册与使用示例

## 目标

演示如何在 ONNX 模型中使用自定义算子（Custom Operator）：使用 helper.py 构建包含自定义 op 节点的模型，理解 OpSchema 签名机制，观察 checker 对自定义算子的行为，以及如何为自定义算子注册 OpSchema 以通过完整检查。

## 完整代码

```python
"""
自定义算子（Custom Operator）使用示例

有两种使用自定义算子的方式：
1. 简单方式：直接在 make_node 中使用自定义 op_type，不注册 OpSchema
   - checker 默认不检查自定义域算子
   - 推理引擎需要自行支持该算子
2. 完整方式：通过 C++ 注册 OpSchema（需编译 C++ 扩展）
   - checker 可以验证算子签名
   - 形状推断可以工作
   - 适用于正式的自定义算子开发
"""

import numpy as np
import onnx
from onnx import helper, TensorProto, numpy_helper, checker


# ================================================================
# 方式1：简单使用自定义算子（不注册 OpSchema）
# ================================================================

def create_model_with_custom_op():
    """创建包含自定义算子的模型（不注册 OpSchema）"""

    # 自定义算子信息
    CUSTOM_DOMAIN = "com.example.custom"
    CUSTOM_OP_VERSION = 1
    CUSTOM_OP_NAME = "MyCustomGemm"

    # 输入输出定义
    X = helper.make_tensor_value_info("X", TensorProto.FLOAT, [1, 3])
    W = helper.make_tensor_value_info("W", TensorProto.FLOAT, [3, 2])
    Y = helper.make_tensor_value_info("Y", TensorProto.FLOAT, [1, 2])

    # 初始化器
    B_data = np.array([[0.1, 0.2]], dtype=np.float32)
    B = numpy_helper.from_array(B_data, name="B")

    # 使用标准算子构建部分计算
    matmul = helper.make_node("MatMul", ["X", "W"], ["mm_out"])

    # 使用自定义算子: 模拟 Gemm = MatMul + Add(bias) + optional activation
    # 通过设置 domain 参数指定自定义域
    custom_node = helper.make_node(
        CUSTOM_OP_NAME,       # op_type: 自定义算子名
        ["mm_out", "B"],      # inputs
        ["Y"],                # outputs
        name="my_custom_gemm",
        domain=CUSTOM_DOMAIN,  # 关键：指定自定义域！
        # 自定义属性
        alpha=1.0,
        beta=1.0,
        activation="RELU",
    )

    # 创建图
    graph = helper.make_graph(
        [matmul, custom_node],
        "custom_op_model",
        [X, W],    # X 和 W 是输入（B 是常量）
        [Y],
        [B],
    )

    # 创建模型
    # 重要：必须为自定义域添加 opset_import！
    model = helper.make_model(
        graph,
        producer_name="custom_op_example",
        opset_imports=[
            helper.make_operatorsetid("", 17),               # 标准域
            helper.make_operatorsetid(CUSTOM_DOMAIN, CUSTOM_OP_VERSION),  # 自定义域
        ],
    )

    return model, CUSTOM_DOMAIN


def demonstrate_checker_behavior(model, custom_domain):
    """演示 checker 对自定义算子的不同行为"""

    print("=" * 60)
    print("Checker 对自定义算子的行为")
    print("=" * 60)

    # 1. 默认 check_model（不指定 full_check）
    print("\n1. 默认 check_model (full_check=False):")
    try:
        checker.check_model(model)
        print("   ✓ 通过")
        print("   （checker 默认不验证自定义域算子的签名）")
    except checker.ValidationError as e:
        print(f"   ✗ 失败: {e}")

    # 2. full_check=True（形状推断+类型检查）
    print("\n2. check_model(full_check=True):")
    try:
        checker.check_model(model, full_check=True)
        print("   ✓ 通过")
    except checker.ValidationError as e:
        print(f"   ✗ 失败（预期行为）:")
        print(f"   {e}")
        print("   （自定义算子没有注册 OpSchema 和形状推断函数，")
        print("    full_check 无法推断输出形状，导致检查失败）")


def workaround_for_full_check(model):
    """绕过 full_check 对自定义算子的限制"""

    print("\n" + "=" * 60)
    print("绕过 full_check 限制的方法")
    print("=" * 60)

    # 方法A：手动设置 value_info（提供自定义算子的输出类型信息）
    # 这样形状推断不需要推断自定义算子的输出
    import copy
    model_with_shapes = copy.deepcopy(model)

    # 为自定义节点的输出手动添加 value_info
    Y_info = helper.make_tensor_value_info("Y", TensorProto.FLOAT, [1, 2])
    # 注意：如果自定义节点有中间输出，也需要添加

    # 添加自定义节点输出的 value_info
    # 需要在形状推断前告诉 ONNX 自定义节点输出的类型
    # 具体做法：将自定义算子的输出添加到 graph.output 或 graph.value_info
    # 这里 Y 已经在 output 中，所以形状推断时 MatMul 的输出需要提供

    # 为 MatMul 的输出 mm_out 添加 value_info（中间值）
    mm_out_info = helper.make_tensor_value_info("mm_out", TensorProto.FLOAT, [1, 2])
    model_with_shapes.graph.value_info.append(mm_out_info)

    print("\n方法A：手动为自定义节点的输入/输出提供 value_info")
    try:
        checker.check_model(model_with_shapes, full_check=True)
        print("  ✓ full_check 通过（提供了足够的类型信息）")
    except checker.ValidationError as e:
        print(f"  结果: {e}")

    # 方法B：使用 skip_opset_compatibility_check（不推荐，跳过所有检查）
    # 这是 C++ API 的选项，Python 端没有直接暴露

    # 方法C：自定义算子内联为标准算子（最佳实践）
    print("\n方法C（推荐）：将自定义算子展开为标准算子")
    model_expanded = inline_custom_op(model)
    try:
        checker.check_model(model_expanded, full_check=True)
        print("  ✓ full_check 通过（全部为标准算子）")
    except checker.ValidationError as e:
        print(f"  ✗ 失败: {e}")

    return model_with_shapes, model_expanded


def inline_custom_op(model):
    """将自定义 MyCustomGemm 算子内联展开为标准算子（MatMul + Add + Relu）"""
    import copy
    model = copy.deepcopy(model)
    graph = model.graph

    CUSTOM_DOMAIN = "com.example.custom"
    nodes_to_remove = []
    nodes_to_add = []

    for node in graph.node:
        if node.domain == CUSTOM_DOMAIN and node.op_type == "MyCustomGemm":
            # 解析属性
            activation = None
            for attr in node.attribute:
                if attr.name == "activation":
                    activation = attr.s.decode()

            input_mm = node.input[0]  # mm_out (MatMul结果)
            input_bias = node.input[1]  # B (偏置)
            output = node.output[0]  # Y

            # 创建 Add 节点
            add_out = output + "_pre_act"
            add_node = helper.make_node(
                "Add", [input_mm, input_bias], [add_out]
            )
            nodes_to_add.append(add_node)

            # 如果有激活函数，添加对应节点
            if activation == "RELU":
                relu_node = helper.make_node(
                    "Relu", [add_out], [output]
                )
                nodes_to_add.append(relu_node)
            elif activation == "NONE" or activation is None:
                # 无激活，直接连接
                # 需要重命名 add_out → output
                # 找到所有引用 add_out 的节点...
                # 简化处理：这里直接让 Add 输出 Y
                # 实际代码中需要更仔细的重连
                nodes_to_add[-1].output[0] = output
            else:
                # 未知激活，直接连接
                nodes_to_add[-1].output[0] = output

            nodes_to_remove.append(node)

    # 移除自定义节点，添加标准节点
    for node in nodes_to_remove:
        graph.node.remove(node)
    graph.node.extend(nodes_to_add)

    # 移除自定义域的 opset_import（如果不再使用）
    # （实际生产代码中应检查是否还有其他自定义节点使用该域）
    new_opset_imports = [
        opset for opset in model.opset_import
        if opset.domain != CUSTOM_DOMAIN
    ]
    # 注意：不能直接修改 opset_imports，需要重新构建
    # 简化起见保留自定义域的 opset 声明

    return model


# ================================================================
# 方式2：运行模型时自定义算子的处理
# ================================================================

def demonstrate_runtime_handling():
    """演示推理时自定义算子的处理概念"""

    print("\n" + "=" * 60)
    print("推理时自定义算子的处理（概念说明）")
    print("=" * 60)

    print("""
在 ONNX Runtime 等推理引擎中运行含自定义算子的模型，有三种方式：

1. 自定义算子库（Custom Op Library）:
   - C++ 实现自定义算子的 Kernel
   - 编译为共享库（.so/.dll）
   - 推理时注册:
     sess_options = ort.SessionOptions()
     sess_options.register_custom_ops_library("my_custom_ops.dll")
     session = ort.InferenceSession("model.onnx", sess_options)

2.  contrib ops / 内置自定义域:
   - 某些域（如 com.microsoft）的算子由推理引擎内置提供
   - 无需额外注册

3. 模型预处理（内联/转换）:
   - 推理前将自定义算子转换为标准算子组合
   - 优点：兼容性最好
   - 缺点：可能丧失算子融合等优化机会
""")


# ================================================================
# 示例：函数作为"自定义算子"（模型局部函数）
# ================================================================

def create_model_with_local_function():
    """使用模型局部函数（FunctionProto）定义可复用的算子组合"""

    print("\n" + "=" * 60)
    print("使用模型局部函数（FunctionProto）")
    print("=" * 60)

    # 定义函数体节点
    # Gemm(X, W, B) = Relu(MatMul(X, W) + B)
    mm_node = helper.make_node("MatMul", ["X", "W"], ["mm_out"])
    add_node = helper.make_node("Add", ["mm_out", "B"], ["add_out"])
    relu_node = helper.make_node("Relu", ["add_out"], ["Y"])

    # 创建函数定义
    my_gemm_func = helper.make_function(
        domain="",  # 使用标准域（或自定义域）
        fname="MyGemm",
        inputs=["X", "W", "B"],
        outputs=["Y"],
        nodes=[mm_node, add_node, relu_node],
        opset_imports=[helper.make_operatorsetid("", 17)],
        attributes=[],  # 无属性参数
    )

    # 创建使用该函数的模型
    X = helper.make_tensor_value_info("X", TensorProto.FLOAT, [1, 3])
    W = helper.make_tensor_value_info("W", TensorProto.FLOAT, [3, 2])
    Y = helper.make_tensor_value_info("Y", TensorProto.FLOAT, [1, 2])
    B = numpy_helper.from_array(np.array([[0.1, 0.2]], dtype=np.float32), name="B")

    # 调用函数（与调用普通算子一样！）
    call_node = helper.make_node(
        "MyGemm",
        ["X", "W", "B"],
        ["Y"],
        # domain="" 表示使用模型局部函数或标准opset中的函数
    )

    graph = helper.make_graph(
        [call_node],
        "local_function_model",
        [X, W],
        [Y],
        [B],
    )

    model = helper.make_model(
        graph,
        functions=[my_gemm_func],  # 注册局部函数
        opset_imports=[helper.make_operatorsetid("", 17)],
    )

    return model


def main():
    # 方式1：直接使用自定义算子
    print("方式1：直接使用自定义域算子")
    model, custom_domain = create_model_with_custom_op()
    print(f"模型包含自定义域: {custom_domain}")
    print(f"节点列表:")
    for node in model.graph.node:
        domain_str = f" (domain='{node.domain}')" if node.domain else ""
        print(f"  {node.op_type}{domain_str}: {list(node.input)} → {list(node.output)}")

    # 检查模型
    try:
        checker.check_model(model)
        print("\n✓ 基础检查通过")
    except checker.ValidationError as e:
        print(f"\n✗ 基础检查失败: {e}")

    # 演示 checker 行为
    demonstrate_checker_behavior(model, custom_domain)

    # 绕过方法
    workaround_for_full_check(model)

    # 推理处理说明
    demonstrate_runtime_handling()

    # 方式2：使用局部函数
    model_func = create_model_with_local_function()
    print(f"创建含局部函数的模型: {len(model_func.functions)} 个函数")
    for func in model_func.functions:
        print(f"  函数: {func.name}, inputs={list(func.input)}, outputs={list(func.output)}")
        print(f"  函数体包含 {len(func.node)} 个节点:")
        for n in func.node:
            print(f"    {n.op_type}: {list(n.input)} → {list(n.output)}")

    try:
        checker.check_model(model_func)
        print("\n✓ 局部函数模型基础检查通过")
    except checker.ValidationError as e:
        print(f"\n✗ 检查失败: {e}")

    # 内联局部函数
    from onnx import inliner
    inlined = inliner.inline_local_functions(model_func)
    print(f"\n内联后节点数: {len(inlined.graph.node)}")
    for node in inlined.graph.node:
        print(f"  {node.op_type}: {list(node.input)} → {list(node.output)}")

    try:
        checker.check_model(inlined, full_check=True)
        print("✓ 内联后 full_check 通过")
    except checker.ValidationError as e:
        print(f"✗ 内联后检查失败: {e}")

    # 保存模型
    onnx.save(model, "custom_op_model.onnx")
    onnx.save(inlined, "custom_op_inlined.onnx")
    print("\n模型已保存")


if __name__ == "__main__":
    main()
```

## 构建与运行

```bash
pip install onnx numpy
python custom_operator.py
```

预期输出要点：
1. 基础 check_model 对自定义域算子默认通过（不检查未知域）
2. full_check 对自定义算子失败（无 OpSchema 无法推断形状）
3. 手动提供 value_info 或内联展开后 full_check 通过
4. 局部函数可以定义可复用算子组合，并通过 inliner 展开

## 要点解析

### domain 是自定义算子的关键

自定义算子必须通过 `domain` 参数指定非空、非标准域名：

```python
# ❌ 错误：不指定 domain，checker 会在标准域中查找该 op_type
node = helper.make_node("MyCustomOp", ["X"], ["Y"])
# checker 报错："No OpSchema registered for (domain='', op_type='MyCustomOp')"

# ✓ 正确：指定自定义域
node = helper.make_node(
    "MyCustomOp", ["X"], ["Y"],
    domain="com.example.custom"
)
```

### opset_import 必须包含自定义域

模型使用自定义算子时，opset_imports 必须包含该自定义域的条目：

```python
model = helper.make_model(
    graph,
    opset_imports=[
        helper.make_operatorsetid("", 17),                  # 标准域
        helper.make_operatorsetid("com.example.custom", 1), # 自定义域
    ],
)
```

缺少自定义域的 opset_import 会导致 checker 报错。

### checker 对自定义算子的默认行为

| 检查模式 | 自定义算子行为 |
|---------|-------------|
| 默认（full_check=False） | 跳过自定义域算子的签名验证，只检查结构合法性（名字引用等） |
| full_check=True | 尝试形状推断，但自定义算子没有注册 InferenceFunction 时失败 |

这意味着：使用自定义算子的模型**基础检查可以通过**，但**完整检查需要额外工作**。

### 通过 full_check 的方法

1. **手动提供 value_info**：为自定义算子的输入输出预先添加类型信息，形状推断可以"跨越"自定义节点
2. **注册 OpSchema**（C++扩展）：为自定义算子注册签名和形状推断函数（最完整，但需要编译 C++）
3. **内联展开**：推理前将自定义算子展开为标准算子组合（兼容性最好）
4. **模型局部函数**：使用 FunctionProto 定义自定义算子为标准算子组合，inliner 可以展开

### 模型局部函数 vs 自定义域算子

| 特性 | 自定义域算子 (domain) | 模型局部函数 (FunctionProto) |
|------|---------------------|---------------------------|
| 定义位置 | C++ 编译的 OpSchema 注册 | ModelProto.functions 字段 |
| 实现语言 | C++（Kernel实现） | 纯 ONNX 标准算子组合 |
| 推理引擎支持 | 需要自定义 Kernel | 可以内联为标准算子 |
| checker 支持 | 需要注册 OpSchema 才能 full_check | 有函数体定义，可以检查 |
| 适用场景 | 高性能/新算子/融合算子 | 可复用组合/宏展开 |
| 跨模型复用 | 可（通过共享库） | 否（函数定义在模型内） |

### 自定义算子命名最佳实践

使用反向域名风格的 domain 避免冲突：
- `com.yourcompany.yourop`
- `org.yourorg.custom`
- `ai.onnx.contrib`（ONNX 贡献域）

避免使用：
- 空字符串（标准域）
- `ai.onnx*`（官方域前缀）
- 过于通用的名字（可能与其他自定义算子冲突）

## 延伸阅读

- [算子定义与注册机制 OpSchema](../concepts/05-operator-schema.md) — OpSchema 链式API和注册机制
- [模型检查器 Checker](../concepts/07-model-checker.md) — checker 的验证规则和自定义域行为
- [Opset版本机制与算子域](../concepts/04-opset-versioning.md) — 四个算子域和 opset_import
- [版本转换与函数内联](../concepts/13-version-converter-inliner.md) — inline_local_functions 展开函数
- [图遍历与变换实战](graph-transformation.md) — 手动操作图结构进行内联展开
