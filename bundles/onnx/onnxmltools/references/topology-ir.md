---
type: reference
title: "Topology IR 三层核心类与编译五阶段流水线"
description: "onnxmltools Topology IR 的核心类（Topology/Scope/Operator/Variable/RawModelContainer）定义、C风格唯一名称生成、raw_name隐藏机制、is_fed拓扑遍历、compile五阶段、convert_topology后端生成的源码信源登记"
sources:
  - path: "external/libs/models/onnx/onnxmltools/onnxmltools/convert/common/_container.py"
    facts: [F-015, F-016, F-017, F-018, F-021, F-022, F-039]
  - path: "external/libs/models/onnx/onnxmltools/onnxmltools/convert/common/_topology.py"
    facts: [F-019, F-020, F-023, F-024]
  - path: "external/libs/models/onnx/onnxmltools/onnxmltools/convert/common/onnx_ex.py"
    facts: [F-024, F-025]
---

# Topology IR 三层核心类与编译五阶段流水线

## 信源概述

| 信源 | 类型 | 职责 |
|------|------|------|
| `common/_container.py` | IR核心定义 | Topology/Scope/Operator/Variable/RawModelContainer/ModelComponentContainer 类实现、名称生成、拓扑遍历 |
| `common/_topology.py` | 编译与生成 | compile() 五阶段、_resolve_duplicates、convert_topology、make_model_ex |
| `common/onnx_ex.py` | ONNX扩展 | OPSET_TO_IR_VERSION 映射、DEFAULT_OPSET_NUMBER、make_model_ex |

## IR核心类层次（F-015）

**信源**：`common/_container.py` L193-L539

```
Topology（计算图容器）
├── raw_model: RawModelContainer        # 原始模型封装（多态）
├── scopes: List[Scope]                 # 作用域列表
├── initial_types: List                 # 输入类型声明
├── custom_conversion_functions: dict   # 自定义转换器
├── custom_shape_calculators: dict      # 自定义形状计算器
└── target_opset: int                   # 目标opset版本

Scope（作用域/命名空间）
├── topology: Topology                  # 回指Topology
├── parent: Scope | None                # 父作用域
├── onnx_name_to_variable: dict         # onnx_name → Variable
├── variable_name_mapping: dict         # raw_name → [onnx_name列表]（隐藏机制）
└── operators: List[Operator]           # 本作用域内的算子

Operator（算子节点）
├── type: str                           # 算子类型字符串（注册key）
├── onnx_name: str                      # 唯一ONNX名称
├── inputs: List[Variable]              # 输入变量
├── outputs: List[Variable]             # 输出变量
├── is_evaluated: bool                  # 是否已被拓扑遍历执行
├── operator_version: int               # 算子版本
└── raw_operator: object                # 原始算子引用

Variable（数据流边）
├── onnx_name: str                      # 唯一ONNX名称
├── raw_name: str                       # 原始名称（可能重复）
├── type: DataType                      # 数据类型
├── is_fed: bool                        # 数据流标记（拓扑遍历用）
├── is_abandoned: bool                  # 废弃标记（identity消重用）
└── doc_string/denotation/channel_denotations  # 语义标注

RawModelContainer（原始模型封装·多态基类）
├── input_names / output_names: List[str]
├── raw_model: object                   # 实际模型对象
└── 子类：CoremlModelContainer / LightGbmModelContainer / XGBoostModelContainer 等
```

## C风格唯一名称生成（F-016）

**信源**：`common/_container.py` L595-L623

`Topology._generate_unique_name(seed)` 方法生成全局唯一名称：

```python
def _generate_unique_name(self, seed):
    # 1. 将非字母数字字符替换为下划线
    seed = re.sub("[^0-9a-zA-Z]", "_", seed)
    # 2. 数字开头补下划线前缀（ONNX名称不能以数字开头）
    if seed and seed[0].isdigit():
        seed = "_" + seed
    # 3. 重名时追加递增数字
    if seed not in self.unique_name_set:
        self.unique_name_set.add(seed)
        return seed
    i = 1
    while f"{seed}{i}" in self.unique_name_set:
        i += 1
    result = f"{seed}{i}"
    self.unique_name_set.add(result)
    return result
```

示例：`"input:0"` → `"input_0"`；`"123abc"` → `"_123abc"`；重名 `"x"` → `"x1"` → `"x2"`。

## Variable的raw_name→onnx_name多对一隐藏机制（F-017）

**信源**：`common/_container.py` L428-L510

同一 `raw_name` 在 Scope 内可声明多个 Variable，通过 `variable_name_mapping` 维护映射：

```
variable_name_mapping = {
    "input": ["input0", "input01", "input02"]  # 最新声明隐藏之前的
}
```

`get_local_variable_or_declare_one(raw_name)` 逻辑：
1. 若 raw_name 已在 mapping 中，返回列表**最后一个** Variable（最新声明）
2. 否则调用 `declare_local_variable(raw_name)` 创建新 Variable，生成唯一 onnx_name，加入 mapping
3. 返回新 Variable

这种"隐藏"机制模拟了 SSA（静态单赋值）中的变量版本链——同一逻辑变量在不同阶段可能由不同算子产出，最新版本"遮蔽"旧版本。

## is_fed数据驱动拓扑遍历（F-018）

**信源**：`common/_container.py` L674-L759

`topological_operator_iterator()` 不使用传统DFS/Kahn算法，而是数据驱动的Level-Order调度：

```python
def topological_operator_iterator(self):
    # 初始化：所有变量 is_fed=True，然后将所有算子的输出设为 is_fed=False
    # （即根变量天然is_fed=True，无需额外查找根节点）
    self._initialize_graph_status_for_traversing()

    priorities = {"tensorToProbabilityMap": 2, "tensorToLabel": 1}
    while True:
        next_step_ops = []
        is_evaluation_happened = False
        for operator in self.unordered_operator_iterator():
            if operator.is_evaluated:
                continue
            # 所有输入都已fed？
            if all(var.is_fed for var in operator.inputs):
                next_step_ops.append(operator)

        if not next_step_ops:
            break  # 死锁检测：一轮无进展则终止

        # 按优先级排序（高优先级后执行）
        next_step_ops.sort(key=lambda op: priorities.get(op.type, 0))

        for operator in next_step_ops:
            operator.is_evaluated = True
            is_evaluation_happened = True
            yield operator  # 交给converter执行
            # converter执行后，将该算子输出标记为fed
            for var in operator.outputs:
                var.is_fed = True

        # 额外处理：不是任何算子输出但也不是root的变量
        # （converter通过container.add_input注入的中间变量）
        for var in self.variables.values():
            if not var.is_fed and not any(...):
                var.is_fed = True
```

关键设计：
- **反向标记初始化**：先标记所有变量 fed，再将算子输出置为 unfed——根变量（非任何算子输出）天然保持 fed
- **动态图增长支持**：converter 内部可创建新算子/变量，下一轮扫描自然发现
- **优先级调度**：`tensorToProbabilityMap`(2) 和 `tensorToLabel`(1) 最后执行，确保概率/标签在所有计算完成后生成
- **重复赋值检测**：若一个变量被多个算子输出，抛 RuntimeError

## compile() 五阶段流水线（F-019）

**信源**：`common/_topology.py` L1047-L1056

```python
def compile(self):
    self._prune()                    # 阶段1：剪除不可达节点/变量
    self._resolve_duplicates()       # 阶段2：identity算子消重
    self._fix_shapes()               # 阶段3：CoreML 2D→4D输入补全
    self._infer_all_types()          # 阶段4：形状/类型推断
    self._check_structure()          # 阶段5：孤立节点/变量检测
```

### 阶段1：_prune()
从输出变量反向BFS，标记可达算子/变量，删除不可达节点。

### 阶段2：_resolve_duplicates()（F-020）

**信源**：`common/_topology.py` L903-L984

Identity 算子消重采用"先替换后删除"的延迟策略：
1. 遍历所有 identity 算子
2. 将所有引用该 identity 输出变量的算子的 input 替换为 identity 的输入变量
3. 合并 doc_string、denotation、channel_denotations
4. 用输出变量已知维度填充输入变量中的 None 维度
5. 标记 identity 算子和重复变量为 `is_abandoned=True`
6. 遍历结束后统一 `delete_local_operator`/`delete_local_variable`

### 阶段3：_fix_shapes()
CoreML 前端特定补丁：硬编码17个算子类型名列表，将2D输入 `[N,C]` 补全为4D `[N,C,1,1]`。

### 阶段4：_infer_all_types()
遍历拓扑顺序，对每个算子：
- 若在 `custom_shape_calculators` 中 → 调用自定义函数
- 若在 `custom_conversion_functions` 中 → pass（Keras特殊通道）
- 否则 → `operator.infer_types()` → `get_shape_calculator(self.type)(self)`

### 阶段5：_check_structure()
检测并报告孤立算子（无输入/输出）和孤立变量。

## ModelComponentContainer（F-021, F-022）

**信源**：`common/_container.py` L83-L191

容器类收集转换产物，持有6个列表：

| 列表 | 类型 | 说明 |
|------|------|------|
| `inputs` | List[ValueInfoProto] | 模型输入 |
| `outputs` | List[ValueInfoProto] | 模型输出 |
| `initializers` | List[TensorProto] | 初始化参数（权重） |
| `value_info` | List[ValueInfoProto] | 中间变量类型信息 |
| `nodes` | List[NodeProto] | ONNX算子节点 |
| `node_domain_version_pair_sets` | Set[Tuple[str,int]] | 节点使用的domain-version集合 |

`add_node(op_type, inputs, outputs, op_domain='', op_version=1, **attrs)` 方法：
1. 验证 inputs/outputs 为字符串列表
2. 验证属性值不为 None
3. 调用 `helper.make_node` 创建 NodeProto
4. 自动将 `(op_domain, op_version)` 加入 `node_domain_version_pair_sets`

## convert_topology：从IR到ModelProto（F-023）

**信源**：`common/_topology.py` L197-L366

```
convert_topology(topology, model_name, target_opset, ...)
  │
  ├─ 1. 验证/默认 target_opset
  ├─ 2. 初始化 ModelComponentContainer
  ├─ 3. 分类 roots/leaves 为 tensor 类和其他类
  ├─ 4. 按 raw_model 顺序添加 inputs/outputs（含命名合规警告 F-040）
  ├─ 5. NHWC→NCHW 转换（channel_first_inputs）
  ├─ 6. 拓扑迭代调度：
  │     for operator in topological_operator_iterator():
  │         if operator.type in custom_conversion_functions:
  │             custom_conversion_functions[operator.type](scope, operator, container)
  │         else:
  │             get_converter(operator.type)(scope, operator, container)
  ├─ 7. opset<9 时将 initializers 也加入 inputs
  ├─ 8. 可选 onnxconverter_common 优化
  └─ 9. make_graph + make_model_ex → ModelProto
```

## make_model_ex：opset合并与IR版本映射（F-024, F-025）

**信源**：`common/_topology.py` L83-L143; `common/onnx_ex.py` L6-L41

```python
DEFAULT_OPSET_NUMBER = 15

OPSET_TO_IR_VERSION = {
    (1,2,3,4,5,6,7): 3,      # IRv3
    (8,9): 4,                 # IRv4 (initializer独立)
    (10,): 5,                 # IRv5
    (11,12,13,14): 7,         # IRv7
    (15,16,17,18): 8,         # IRv8
    (19,20): 9,               # IRv9
    (21,22,23,24): 10,        # IRv10
}
```

`make_model_ex` 流程：
1. 按 domain 合并 opset，取每个 domain 的最大版本
2. ai.onnx domain 最低要求 opset 8（IRv4，initializer 独立于 inputs）
3. 通过 OPSET_TO_IR_VERSION 映射表设置 `ir_version`
4. 自动填充 `producer_name="OnnxMLTools"`、`producer_version="1.17.0"`、`domain="onnxml"`、`model_version=0`

## Operator.infer_types 分发（F-039）

**信源**：`common/_container.py` L395-L397

```python
def infer_types(self):
    self.get_shape_calculator(self.type)(self)
```

`Operator.infer_types()` 直接从 `_shape_calculator_pool` 查找对应函数并传入 operator 自身，未注册则抛 ValueError。
