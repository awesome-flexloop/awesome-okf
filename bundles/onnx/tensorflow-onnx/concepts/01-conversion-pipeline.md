---
type: concept
title: "转换流水线：Loader→Rewriter→Mapper→Optimizer"
description: "tf2onnx 转换流水线的详细执行流程：从模型加载、形状推断、protobuf 1:1 转换、预处理重写、算子映射、后处理重写到图优化的完整链路"
sources:
  references: [../references/convert-entry.md, ../references/opset-mapping.md, ../references/graph-rewriter.md]
  facts: [F-006, F-007, F-008, F-009, F-010, F-011, F-012, F-013, F-014, F-033, F-034, F-035, F-036, F-037, F-042]
  insights: [I-002]
---

# 转换流水线：Loader→Rewriter→Mapper→Optimizer

## 核心理解

tf2onnx 的转换流水线是一个由 `process_tf_graph` 驱动的多阶段处理链。从用户调用 `from_keras()`/`from_saved_model()` 等 API 开始，到输出 ONNX `ModelProto` 结束，整个流程可以分解为六个主要步骤：模型加载 → Protobuf 1:1 转换 → 预处理重写 → 算子映射 → 后处理重写 → 图优化。

理解流水线的关键在于：**每个阶段有明确的输入/输出契约，阶段间通过统一的 Graph 对象传递状态**。

## 完整调用链

```
用户调用 API
    │
    ├─ from_keras(model, ...)
    ├─ from_function(func, input_signature=..., ...)
    ├─ from_saved_model(model_path, ...)
    ├─ from_graph_def(graph_def, input_names=..., output_names=..., ...)
    └─ from_tflite(tflite_path, ...)
    │
    ▼
_convert_common(frozen_graph, ...)  ──── 所有入口共用
    │
    ├─ 1. 处理 custom_op_handlers（旧 API 兼容层）
    ├─ 2. 大模型常量压缩
    ├─ 3. 导入冻结图到 tf.Graph（/cpu:0 设备）
    │
    ▼
process_tf_graph(tf_graph, opset, ...)  ──── TF 图→ONNX 图核心
    │
    ├─ A. graphs_from_tf()  ──── 解析源模型
    │   ├─ infer_shape_for_graph()  ──── TF 原生形状推断
    │   ├─ compute_const_folding_using_tf()  ──── TF 层面常量折叠
    │   ├─ tflist_to_onnx()  ──── Protobuf 1:1 转换（关键！）
    │   │   └─ TF NodeDef → ONNX NodeProto（类型名保持 TF 原名）
    │   ├─ 创建 Graph 对象（Node/Graph 包装）
    │   └─ fold_constants_using_tf()  ──── 再一次常量折叠
    │
    ├─ B. process_parsed_graph()  ──── 处理每个图
    │   ├─ (TFLite路径) TFL重写器 → TFL→TF映射
    │   ├─ 创建 ops_mapping = tf_op.create_mapping(opset)
    │   ├─ transpose_inputs/transpose_outputs()  ──── NHWC→NCHW 转置插入
    │   ├─ run_rewriters(pre-rewriters)  ──── 预处理重写器（20+个）
    │   ├─ 删除未使用节点 + 拓扑排序
    │   ├─ tensorflow_onnx_mapping()  ──── 算子映射（Mapper 阶段）
    │   ├─ run_rewriters(late_rewriters)  ──── 后处理重写器（target 条件）
    │   ├─ 拓扑排序
    │   └─ g.update_proto()  ──── 将 Graph 状态同步回 ONNX proto
    │
    └─ C. 子图注册：set_function 注册 If/Loop/Scan 的 body 子图
    │
    ▼
optimizer.optimize_graph(g)  ──── ONNX 图优化
    │
    └─ 迭代执行 12 个优化器直到收敛
    │
    ▼
g.make_model(...)  ──── 构建最终 ModelProto
    │
    ├─ make_graph() → GraphProto
    ├─ 设置 producer_name/version
    ├─ 添加 opset_imports
    ├─ 设置 IR 版本
    └─ (可选) onnx optimizer 优化
    │
    ▼
返回 (model_proto, external_tensor_storage)
```

## 各阶段详解

### 阶段一：模型加载（Loader）

模型加载由 `tf_loader` 模块和 `convert.py` 中的入口函数共同完成，目标是将各种格式的 TF 模型统一转化为**冻结的 tf.Graph 对象**（除 TFLite 外）。

**五种加载路径**：

| 入口函数 | 源格式 | 关键步骤 |
|----------|--------|----------|
| `from_keras` | `tf.keras.Model` | `_get_concrete_function` → 获取 concrete function → freeze |
| `from_function` | `tf.function` | `get_concrete_function(input_signature)` → 过滤 resource 输入 → freeze |
| `from_saved_model` | SavedModel 目录 | `tf.saved_model.load` → 获取签名 → concrete function → freeze |
| `from_graph_def` | GraphDef 文件 | 直接解析 GraphDef proto → 导入 tf.Graph |
| `from_tflite` | `.tflite` 文件 | 跳过 TF 冻结，直接走 TFLite 专用路径 |

**freeze_session 的作用**：将变量（Variable）转换为常量（Const），消除变量读取/赋值节点，使图成为纯计算图。这是转换为 ONNX 的必要前提，因为 ONNX 不支持 TF 风格的变量。

**TF 版本兼容**：`_get_concrete_function` 处理 TF<2.16（trace_model_call）和 TF2.16+（回退到 tf.function）两种路径。`_Lazy` 代理类解决 Windows 上 TF 模块导入的符号缺失问题。

### 阶段二：Protobuf 1:1 转换（tflist_to_onnx）

这是整个转换流水线中最关键的设计决策：**第一步就将 TF 节点转为 ONNX protobuf 格式**，而不是先转为自定义 IR。

```python
# tf_utils.py - tflist_to_onnx 核心逻辑（简化）
def tflist_to_onnx(tf_graph, ...):
    onnx_nodes = []
    for tf_op in tf_graph.get_operations():
        # 1. 读取属性
        attr = _get_onnx_attrs(tf_op)
        # 2. 处理 TensorProto 常量 → ONNX tensor
        if tf_op.type == "Const":
            tensor = tf_op.get_attr("value")
            onnx_tensor = tf_to_onnx_tensor(tensor)
            attr["value"] = onnx_tensor
        # 3. 特殊处理 PlaceholderWithDefault
        # 4. 创建 ONNX 节点（类型名保持 TF 原名！）
        onnx_node = make_onnx_node_with_attr(
            tf_op.type,        # 注意：这里使用 TF 的 op type
            inputs=tf_op.inputs,
            outputs=tf_op.outputs,
            **attr
        )
        onnx_nodes.append(onnx_node)
    return onnx_nodes
```

**关键点**：创建的 ONNX 节点使用的是 **TF 的算子类型名**（如 `"Relu"` 是同名的，但 `"FusedBatchNorm"` 在 ONNX 中不存在）。这些节点是"伪 ONNX 节点"——结构符合 ONNX protobuf 格式，但类型名不一定是合法的 ONNX 算子。后续阶段逐步修正。

### 阶段三：预处理重写（Pre-rewriters）

预处理重写器在算子映射之前运行，目标是识别并替换 TF 特有的复合算子子图为 ONNX 可表达的等价形式。这是复杂度最高的阶段。

**为什么重写在映射之前？**

TF 的很多算子在 ONNX 中不是单个算子，而是多个算子的组合：
- `FusedBatchNorm` → ONNX 中需要 `BatchNormalization`（opset 9+ 支持）
- `BiasAdd + Conv2D` → ONNX 中 Conv 自带 bias 输入，需要融合模式识别
- LSTM/GRU 的 TF 实现 → 大量小算子组成的子图，需要识别并替换为 ONNX LSTM/GRU
- `Conv2D + Pad` → 需要合并为带 pad 属性的 Conv
- `FusedBatchNormV3` 等融合算子 → 需要拆分为多算子子图

如果跳过重写直接映射，这些复合算子会因为找不到对应的 ONNX 单算子而失败。

**重写器执行机制**：

```python
def run_rewriters(g, ops, rewriters, name="rewriter"):
    for rewrite_func in rewriters:
        ops = rewrite_func(g, ops)  # 每个重写器返回新的 ops 列表
        # 对 contained_graphs（子图）递归应用
        for subgraph in g.contained_graphs.values():
            run_rewriters(subgraph, subgraph.get_nodes(), rewriters, name)
    return ops
```

**三层常量折叠**：

| 层级 | 时机 | 方法 | 折叠范围 |
|------|------|------|----------|
| TF 层面 | graphs_from_tf | `compute_const_folding_using_tf` | 利用 TF 运行时计算，覆盖最广 |
| numpy 层面 | pre-rewriters | `rewrite_constant_fold` | Add/Mul/Cast/ConcatV2/Pack/Range 等 |
| ONNX 层面 | optimizer | `ConstFoldOptimizer` | ONNX 算子的常量折叠 |

### 阶段四：算子映射（Mapper）

算子映射是最直接的阶段：遍历图中每个尚未转换的节点，通过 `ops_mapping` 查找对应的处理函数并执行。

```python
# tfonnx.py - tensorflow_onnx_mapping（简化）
def tensorflow_onnx_mapping(g, ops_mapping, ...):
    for node in g.get_nodes():
        if node.skip_conversion:
            continue  # 已被重写器处理的节点跳过
        op_name = node.type
        handler = ops_mapping.get(op_name)
        if handler:
            handler_func, kwargs = handler
            # 如果 onnx_op 指定了映射名，先改名
            if "onnx_op" in kwargs:
                node.type = kwargs["onnx_op"]
            # 执行处理函数（可能修改属性、插入节点等）
            handler_func(g, node, **kwargs)
            node.skip_conversion = True
        # 递归处理子图
        for body_graph in node.contained_graphs.values():
            tensorflow_onnx_mapping(body_graph, ops_mapping, ...)
```

**ops_mapping 的构建**：通过 `tf_op.create_mapping(opset_version)` 在运行时根据目标 opset 版本构建，自动选择每个算子的最高可用版本处理器。

### 阶段五：后处理重写（Late-rewriters）

后处理重写器在算子映射完成后运行，根据目标平台条件性应用：

- `rewrite_incomplete_type_support_rs5/rs6`：为 Windows ML 不同版本插入 Cast 节点处理不支持的类型
- `rewrite_channels_last`：为 channels_last target 插入额外的 Transpose

### 阶段六：图优化（Optimizer）

图优化阶段操作纯 ONNX 图（不再有 TF 类型名的节点），执行与语义无关的性能优化：

```python
def optimize_graph(graph, optimizers=all_optimizers, catch_errors=True):
    continue_flag = True
    while continue_flag:
        opts = list(optimizers)
        for opt in opts:
            try:
                current_graph = deepcopy(graph) if catch_errors else graph
                opt_instance = opt()
                if opt_instance.main(graph):
                    continue_flag = True  # 有变化，继续迭代
            except Exception as e:
                if catch_errors:
                    graph = current_graph  # 失败回滚
                    logger.warning(f"Optimizer {opt} failed: {e}")
                else:
                    raise
    graph.topological_sort(graph.get_nodes())
    return graph
```

优化器迭代执行直到无变化（不动点收敛），每个优化器失败时 catch_errors 模式下记录警告但不中断流程。

## 形状推断

形状推断在 graphs_from_tf 阶段执行，采用三阶段策略：

1. **shape_override**：应用用户指定的输入形状覆盖
2. **TF 原生推断**：`infer_shape_for_graph` 利用 TF 运行时推断形状，基于关键假设（Merge 输出同输入形状、tf.cond 分支同 rank、while_loop 循环变量不变 rank）迭代直到收敛
3. **Legacy 推断**：对仍有 None 形状的节点，使用自定义推断规则

## TFLite/TFJS 路径差异

| 特性 | TF 路径 | TFLite 路径 | TFJS 路径 |
|------|---------|-------------|-----------|
| 源格式 | frozen tf.Graph | `.tflite` 文件 | TF.js model.json |
| 解析函数 | `graphs_from_tf` | `graphs_from_tflite` | `graphs_from_tfjs` |
| 额外步骤 | 无 | TFL 重写器 → TFL→TF 映射 | TFJS 层处理 |
| freeze | 需要（变量→常量） | 不需要 | 需要 |

## 关联概念

- [tf2onnx 整体架构](00-overall-architecture.md) — 回到架构总览
- [装饰器驱动的版本化算子注册表](02-versioned-opset-registry.md) — 理解 ops_mapping 如何构建
- [图重写与模式匹配](03-graph-rewriting.md) — 理解 Rewriter 阶段的模式匹配机制
- [内部 Graph API 设计](04-graph-internal-api.md) — 理解 Graph 对象如何在阶段间传递
- [ONNX 图优化器](05-optimizers.md) — 理解 Optimizer 阶段的 12 个优化器
- [数据布局、类型系统与 Target 适配](06-data-layout-types.md) — 理解 transpose_inputs/outputs 和类型映射
