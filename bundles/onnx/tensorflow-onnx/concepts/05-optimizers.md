---
type: concept
title: "ONNX 图优化器：常量折叠/布局转换/冗余消除"
description: "tf2onnx 内置的 12 个 ONNX 图优化器详解：优化器注册顺序、迭代收敛策略、错误隔离机制，以及优化器与重写器的本质区别"
sources:
  references: [../references/graph-rewriter.md]
  facts: [F-031, F-032, F-042]
  insights: [I-002]
---

# ONNX 图优化器：常量折叠/布局转换/冗余消除

## 核心理解

图优化器是 tf2onnx 转换流水线的最后阶段，在算子映射完成后操作**纯 ONNX 图**。与重写器（Rewriter）不同，优化器不感知 TF 语义——它只知道 ONNX 算子，执行的是与来源无关的通用图变换。优化器的目标是提升推理性能、消除冗余、简化图结构。

**优化器 vs 重写器的本质区别**：

| 特性 | 重写器（Rewriter） | 优化器（Optimizer） |
|------|-------------------|-------------------|
| 执行时机 | 算子映射**之前**（pre）和**之后**（late） | 算子映射**之后** |
| 输入图 | 混合 TF/ONNX 类型名 | 纯 ONNX 类型名 |
| 是否感知 TF 语义 | ✅ 是（识别 TF 特定模式） | ❌ 否（纯 ONNX 变换） |
| 目标 | 语义等价变换（TF 子图→ONNX 子图） | 性能优化（冗余消除/常量折叠） |
| 可独立复用 | ❌ 依赖 TF 语义 | ✅ 可被其他 ONNX 工具复用 |
| 迭代收敛 | 单次遍历 | 迭代直到无变化 |

## 12 个内置优化器

优化器在 `tf2onnx/optimizer/__init__.py` 中按固定顺序注册：

```python
_OPTIMIZERS = OrderedDict([
    ("transpose", TransposeOptimizer),
    ("upsample", UpsampleOptimizer),
    ("constfold", ConstFoldOptimizer),
    ("constdequantize", ConstDequantizeOptimizer),
    ("loop", LoopOptimizer),
    ("mergeduplicates", MergeDuplicatedNodesOptimizer),
    ("reshape", ReshapeOptimizer),
    ("globalpool", GlobalPoolOptimizer),
    ("qdq", QDQOptimizer),
    ("identity", IdentityOptimizer),
    ("backtoback", BackToBackOptimizer),
    ("einsum", EinsumOptimizer),
])
```

### 功能分类

| 类别 | 优化器 | 功能 |
|------|--------|------|
| **布局优化** | TransposeOptimizer | 消除冗余 Transpose，简化转置链 |
| | UpsampleOptimizer | 优化 Upsample/Resize 算子 |
| **常量折叠** | ConstFoldOptimizer | ONNX 层面常量折叠（第三层折叠） |
| | ConstDequantizeOptimizer | 折叠 QDQ 中的常量部分 |
| **控制流优化** | LoopOptimizer | 优化 Loop 子图（常量迭代次数等） |
| **冗余消除** | MergeDuplicatedNodesOptimizer | 合并相同输入和属性的重复节点 |
| | IdentityOptimizer | 消除无意义的 Identity 节点 |
| **算子简化** | ReshapeOptimizer | 简化连续 Reshape、消除冗余 Reshape |
| | GlobalPoolOptimizer | 将 ReduceMean+Squeeze 模式替换为 GlobalAveragePool |
| | BackToBackOptimizer | 融合连续的同类型算子（如连续 Transpose） |
| | EinsumOptimizer | 优化 Einsum 表达式 |
| **量化优化** | QDQOptimizer | QDQ 量化模式优化 |

### 关键优化器详解

#### TransposeOptimizer

这是最重要的布局优化器，负责消除冗余 Transpose 节点：

- **连续 Transpose 消除**：Transpose(perm=a) → Transpose(perm=b) 合并为 Transpose(perm=compose(a,b))，如果 compose 后为恒等 perm 则全部消除
- **Transpose 传播**：将 Transpose 推过支持布局变换的算子（如 Conv 配合 kernel 重排）
- **冗余 Transpose 消除**：如果 Transpose 前后的算子可以直接处理对应布局，消除 Transpose

这是 NHWC→NCHW 转换后的关键优化——用户指定 `inputs_as_nchw` 时在输入端插入 Transpose，优化器尝试将这些 Transpose 向后传播或消除。

#### ConstFoldOptimizer

第三层常量折叠（在 TF 层面和 numpy 层面之后）：

- 对输入全为常量的算子，在转换时直接计算输出值
- 支持大部分 ONNX 一元/二元算子的常量计算
- 与前面的常量折叠不同，这一层完全在 ONNX 语义下进行
- 可以显著减少模型中的常量节点数量

```python
# 常量折叠示例
# 转换前：
#   Const([1,2,3]) → Add ← Const([4,5,6])
# 折叠后：
#   Const([5,7,9])
```

#### IdentityOptimizer

消除无意义的 Identity 节点：

- Identity 的输入直接传递给所有消费者
- 但图的输出端 Identity（由构造函数自动添加的保护节点）不消除
- 这保证了输出名称的稳定性

#### MergeDuplicatedNodesOptimizer

合并"计算相同"的节点：
- 两个节点具有相同的 op_type、相同的输入、相同的属性
- 将其中一个节点的输出替换为另一个节点的输出
- 消除冗余计算，尤其在常量折叠后可能产生大量重复节点

#### ReshapeOptimizer

- 消除输入输出形状相同的 Reshape
- 合并连续 Reshape：Reshape→Reshape 简化为单个 Reshape
- 对 Shape→Reshape 模式进行简化

#### BackToBackOptimizer

融合连续的可融合算子对：
- 连续 Transpose 合并
- 连续 Cast 消除（Cast to same type）
- 其他可组合的算子对

## 优化器执行机制

### 迭代收敛策略

```python
def optimize_graph(graph, optimizers=None, catch_errors=True, onnx_optimizer=None):
    if optimizers is None:
        optimizers = _OPTIMIZERS
    
    continue_flag = True
    iteration = 0
    while continue_flag:
        continue_flag = False
        iteration += 1
        opts = list(optimizers.values()) if isinstance(optimizers, dict) else optimizers
        for opt_class in opts:
            try:
                if catch_errors:
                    bk_graph = deepcopy(graph)
                opt = opt_class()
                if opt.main(graph):
                    continue_flag = True  # 有变化，需要继续迭代
            except Exception as e:
                if catch_errors:
                    # 回滚到优化前状态
                    graph = bk_graph
                    logger.warning(f"Optimizer {opt_class.__name__} failed: {e}")
                else:
                    raise
    
    # 优化完成后拓扑排序
    graph.topological_sort(graph.get_nodes())
    
    # 可选：调用 ONNX 官方优化器
    if onnx_optimizer:
        model_proto = graph.make_model()
        model_proto = onnx_optimizer.optimize(model_proto)
        # 重新加载...
    
    return graph
```

**为什么需要迭代？**

一个优化器的输出可能为另一个优化器创造优化机会：

```
初始图：Transpose(A→B) → Conv → Transpose(B→A) → Relu → Transpose(A→B)

第1轮：
  TransposeOptimizer: 消除 Transpose(B→A)→Relu→Transpose(A→B) 的冗余
  → Transpose(A→B) → Conv → Relu (在B布局)
  
  ConstFoldOptimizer: 可能折叠了某些常量
  → 产生新的可优化模式

第2轮：
  TransposeOptimizer: 发现 Transpose(A→B)→Conv 可以融合
  → Conv (带重排kernel) → Relu
  
  IdentityOptimizer: 消除空 Identity
  → 无新变化

收敛：所有优化器无变化，退出循环
```

### 错误隔离机制

`catch_errors=True` 模式下，每个优化器执行前会深拷贝图状态。如果优化器抛出异常：
1. 回滚到优化前的图状态
2. 记录警告日志
3. 继续执行下一个优化器

这确保了单个优化器的 bug 不会导致整个转换失败。优化器是"尽力而为"的——失败时跳过，不影响最终正确性。

### 优化前后统计

优化器执行前后会输出节点统计，帮助开发者理解优化效果：

```
Optimizer step:
  Initial nodes: 1234
  After transpose: 1180 (-54)
  After constfold: 1050 (-130)
  After identity: 1045 (-5)
  ...
  Final nodes: 1023
```

## 三层常量折叠对比

tf2onnx 有三层常量折叠，分别在不同阶段执行：

| 层级 | 执行时机 | 方法 | 能力 |
|------|----------|------|------|
| 第一层 | graphs_from_tf | `compute_const_folding_using_tf` | **最强**：利用 TF 运行时，可以折叠任何 TF 可以静态计算的表达式 |
| 第二层 | pre-rewriters | `rewrite_constant_fold`（numpy） | **中等**：使用 numpy 计算 Add/Mul/Cast/Concat/Pack/Range 等 |
| 第三层 | optimizer | `ConstFoldOptimizer`（ONNX） | **最弱但通用**：仅在 ONNX 语义下折叠，不依赖 TF |

为什么需要三层？因为：
1. TF 层面的常量折叠能力最强，但需要 TF 运行时，且只在转换早期可用
2. numpy 层面在重写阶段可用，可以折叠新创建的常量表达式
3. ONNX 层面是通用保险，即使前面没有折叠也能处理

## 自定义优化器

用户可以通过 `optimizers` 参数选择或排除特定优化器：

```python
# 只使用常量折叠和 Identity 消除
from tf2onnx.optimizer import ConstFoldOptimizer, IdentityOptimizer

model_proto, _ = tf2onnx.convert.from_saved_model(
    "saved_model_dir",
    optimizers=[ConstFoldOptimizer, IdentityOptimizer]
)
```

也可以通过继承 `GraphOptimizer` 基类实现自定义优化器：

```python
from tf2onnx.optimizer import GraphOptimizer

class MyCustomOptimizer(GraphOptimizer):
    def __init__(self):
        super().__init__("MyCustom")
    
    def optimize(self, graph):
        # 自定义图优化逻辑
        modified = False
        for node in graph.get_nodes():
            if self._should_optimize(node):
                self._do_optimize(graph, node)
                modified = True
        return modified  # 返回 True 表示图被修改
```

## ONNX Runtime 优化器（可选）

tf2onnx 还可以调用 ONNX Runtime 的官方优化器（如果安装了 onnxruntime）：

```python
model_proto, _ = tf2onnx.convert.from_saved_model(
    "saved_model_dir",
    onnx_optimizer=True  # 启用 ONNX Runtime 优化
)
```

这会在 tf2onnx 自身的 12 个优化器之后，再执行 ONNX Runtime 的图优化（如算子融合、常量折叠等），通常能进一步提升性能。

## 关联概念

- [tf2onnx 整体架构](00-overall-architecture.md) — 理解优化器在三阶段流水线中的位置
- [转换流水线详解](01-conversion-pipeline.md) — 理解优化器的执行时机和前后处理
- [图重写与模式匹配](03-graph-rewriting.md) — 对比重写器与优化器的区别
- [内部 Graph API 设计](04-graph-internal-api.md) — 理解优化器如何操作 Graph 对象
- [数据布局、类型系统与 Target 适配](06-data-layout-types.md) — 理解 TransposeOptimizer 与 NHWC/NCHW 转换的关系
