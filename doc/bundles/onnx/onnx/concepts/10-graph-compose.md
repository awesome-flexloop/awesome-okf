---
type: concept
title: "图组合 Compose 与子图处理"
description: "merge_models 前提条件、add_prefix 前缀策略、check_overlapping_names 名字冲突检测、子图属性递归处理、rename_functions"
sources:
  references: [../references/compose-parser-printer.md, ../references/onnx-proto.md]
  facts: [F-065, F-066, F-067, F-068]
---

# 图组合 Compose 与子图处理

## 核心理解

ONNX 提供了图组合（compose）工具，允许将多个模型或子图合并为一个。核心挑战在于**名字唯一性**——两个图可能使用相同的值名、节点名或初始化器名，合并前必须检测冲突并通过前缀策略解决。子图（GRAPH 类型属性中的嵌套图）需要递归处理以确保全图名字一致。

## 机制详解

### merge_models：模型合并

`merge_models` 将两个 ModelProto 合并为一个（F-065）：

```python
from onnx import compose

merged_model = compose.merge_models(model1, model2)
```

#### 合并前提条件

merge_models 执行以下兼容性检查，**不满足则抛出 ValueError**：

| 检查项 | 要求 | 原因 |
|--------|------|------|
| ir_version 相同 | model1.ir_version == model2.ir_version | IR 版本不兼容无法合并 |
| opset_import 兼容 | 同一域的版本必须完全相同 | 同一模型不能同一域使用不同版本 |
| metadata_props 不冲突 | 同名 key 的值必须相同 | 元数据不能有矛盾 |
| functions 不重名 | (domain, name, overload) 三元组唯一 | 函数不能重复定义 |
| 图内名字不冲突 | edge/value_info/initializer 名不重叠 | 名字必须全局唯一 |

```
merge_models 前的检查流程：

model1 ──→ 检查 ir_version/opset ──┐
                                  ├─→ 兼容性检查通过
model2 ──→ 检查 ir_version/opset ──┘         │
                                            ↓
                              check_overlapping_names(g1, g2)
                                            │
                              ┌─ 无冲突 → 合并
                              └─ 有冲突 → ValueError（建议 add_prefix）
```

#### 合并内容

合并时，以下字段被合并：
- graph.node：两个图的节点列表拼接
- graph.initializer：初始化器合并
- graph.input/ output：输入输出合并（需注意连接逻辑）
- graph.value_info：值信息合并
- functions：局部函数合并（不能重名）
- metadata_props：元数据合并（同key值必须相同）
- opset_import：取并集（同一域版本必须相同）

### check_overlapping_names：名字冲突检测

`check_overlapping_names` 检测两个图之间的名字冲突（F-066）：

```python
def check_overlapping_names(
    g1: GraphProto,
    g2: GraphProto,
    io_map: Optional[Dict[str, str]] = None,
) -> List[str]:
```

检测范围：
- **edge names**：节点输出名（计算图中定义的值名）
- **value_info names**：中间值类型信息名
- **initializer names**：初始化器名
- **sparse_initializer names**：稀疏初始化器名

返回冲突名字的列表。如果有冲突，merge_models 会建议使用 `add_prefix` 解决。

```python
# 检查冲突
conflicts = compose.check_overlapping_names(g1, g2)
if conflicts:
    print(f"名字冲突: {conflicts}")
    # 建议: g2 = add_prefix(g2, prefix="g2_")
```

### add_prefix_graph：图级前缀添加

`add_prefix_graph` 为图中的各种名字添加前缀（F-067）：

```python
def add_prefix_graph(
    graph: GraphProto,
    prefix: str,
    nodes: bool = True,
    edges: bool = True,
    inputs: bool = True,
    outputs: bool = True,
    initializers: bool = True,
    value_infos: bool = True,
    rename_edges: bool = True,
    inplace: bool = False,
) -> GraphProto:
```

#### 可选择前缀范围

| 参数 | 控制对象 | 默认值 |
|------|---------|--------|
| nodes | 节点名 (node.name) | True |
| edges | 边/值名（input/output 字符串） | True |
| inputs | 图输入名 | True |
| outputs | 图输出名 | True |
| initializers | 初始化器名 | True |
| value_infos | value_info 名 | True |

#### 关键行为

1. **空名字不加前缀**：如果某个名字是空字符串 `""`（可选输入未连接），保持为空
2. **rename_edges 跳过图输出**：重命名边时，图输出名由 `outputs` 参数单独控制，不随 edges 一起重命名
3. **子图递归处理**：遍历节点的 GRAPH 和 GRAPHS 类型属性（子图），递归调用 add_prefix_graph

```
add_prefix_graph 递归处理示意：

main_graph (prefix="g1_")
├── node1: Conv("X", "W") → "Y"
│   → Conv("g1_X", "g1_W") → "g1_Y"
├── node2: If("cond") → "Z"
│   └── attribute g (GRAPH): then_branch
│       ├── input: ["cond"]
│       ├── node: Relu("X_if") → "Y_if"
│       └── output: ["Y_if"]
│       ──→ 递归 add_prefix_graph(then_branch, prefix="g1_")
│           └── Relu("g1_X_if") → "g1_Y_if"
└── output: ["Z"]
    → "g1_Z"
```

### add_prefix：模型级前缀添加

`add_prefix` 在 add_prefix_graph 基础上额外支持函数重命名（F-068）：

```python
def add_prefix(
    model: ModelProto,
    prefix: str,
    rename_functions: bool = False,
    **kwargs: Any,
) -> ModelProto:
```

- 对 model.graph 调用 add_prefix_graph
- `rename_functions=True` 时，同时对 model.functions 中的局部函数名添加前缀
- 其他 kwargs 传递给 add_prefix_graph

### 典型合并工作流

```python
from onnx import compose, helper, TensorProto

# 场景：将 model2 作为子模块连接到 model1 后面
# 例如：encoder → decoder

# 步骤1：检查冲突
conflicts = compose.check_overlapping_names(model1.graph, model2.graph)
if conflicts:
    # 步骤2：为 model2 添加前缀避免冲突
    model2 = compose.add_prefix(model2, prefix="decoder_")

# 步骤3：指定 IO 映射（model1 的某些输出连接到 model2 的输入）
io_map = [("output1", "input1")]  # model1.output1 → model2.input1

# 步骤4：合并
merged = compose.merge_models(
    model1, model2,
    io_map=io_map,
    # 可以指定哪些输入/输出暴露在外
    # inputs=..., outputs=...
)
```

## 关键洞察/反常识

1. **前缀不是自动的**：merge_models 不会自动为冲突名字加前缀——它检测到冲突直接报错，要求用户显式调用 add_prefix。这避免了隐式改名导致的难以调试的问题。
2. **空字符串输入不加前缀**：如果节点的某个输入是空字符串（表示可选输入未连接），加前缀时保持为空。这很重要，因为空字符串有特殊语义（"无连接"）。
3. **子图必须递归处理**：If/Loop/Scan 等算子包含子图属性，如果不递归处理子图内的名字，会导致子图内的名字与主图或兄弟子图冲突。
4. **图输出名需要特殊处理**：rename_edges 不会重命名图输出——因为图输出名是图的"公共接口"，是否改变需要由用户决定（outputs 参数控制）。
5. **函数也需要重命名**：如果模型使用了局部函数（IR ≥ 8），合并时函数名也可能冲突，需要 rename_functions=True 一起处理。

## 关联概念

- [计算图模型](03-computation-graph.md) — 图的基本结构和字符串名字连接
- [Protobuf IR：核心 Message 结构](01-protobuf-ir.md) — NodeProto 的 attribute 字段和子图属性
- [模型检查器 Checker](07-model-checker.md) — 合并后需要 check_model 验证
- [图遍历与变换实战](../examples/graph-transformation.md) — 手动操作图结构
