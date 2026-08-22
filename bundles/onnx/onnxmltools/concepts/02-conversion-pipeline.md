---
type: concept
title: "编译流水线五阶段：createTopology→compile→convert_topology→make_model"
description: "onnxmltools 转换流水线的完整流程：parse创建Topology IR、compile五阶段优化（剪枝→identity消重→形状补全→类型推断→结构校验）、convert_topology拓扑遍历调度、make_model_ex opset合并与IR版本映射"
sources:
  references: [../references/topology-ir.md, ../references/convert-entry.md, ../references/registration-types.md]
  facts: [F-019, F-020, F-023, F-024, F-025, F-031, F-032, F-040]
---

# 编译流水线五阶段：createTopology→compile→convert_topology→make_model

## 核心理解

所有走自有 IR 路径的框架（CoreML/LightGBM/XGBoost/H2O/LibSVM/SparkML）遵循统一的四步流水线：

```
原始模型 → parse → Topology IR → compile (5阶段) → convert_topology → make_model_ex → ONNX ModelProto
```

这个流水线是 onnxmltools 的核心——parse 阶段负责"翻译"（模型→IR），compile 阶段负责"优化和验证"（IR→IR），convert 阶段负责"生成"（IR→ONNX节点），make_model 阶段负责"组装"（节点→完整模型）。

## 第一步：parse — 创建Topology IR

各框架的 `_parse.py` 将原始模型翻译为 Topology IR：

```python
# 以LightGBM为例
def parse_lightgbm(model, initial_types, target_opset, custom_conversion_functions, custom_shape_calculators):
    # 1. 包装原始模型（Booster自动包装为WrappedBooster）
    if isinstance(model, lightgbm.Booster):
        model = WrappedBooster(model)
    container = LightGbmModelContainer(model)
    
    # 2. 创建Topology
    topology = Topology(container, default_batch_size=1, 
                        initial_types=initial_types,
                        custom_conversion_functions=custom_conversion_functions,
                        custom_shape_calculators=custom_shape_calculators,
                        target_opset=target_opset)
    
    # 3. 声明输入变量
    scope = topology.declare_scope('RawInput')
    for input_name, input_type in initial_types:
        variable = scope.declare_local_variable(input_name, input_type)
    
    # 4. 递归解析模型结构，创建Operator和Variable
    # ...根据模型类型创建LgbmClassifier/LgbmRegressor等算子...
    
    return topology
```

parse 阶段的特点：
- 可能创建 identity 算子连接同名变量的不同版本（为了简化处理，故意制造冗余）
- 可能创建多个 Variable 共享同一 raw_name（隐藏机制）
- 模型中的每个组件（如树节点、scaler参数）被翻译为对应的 Operator

**initial_types 是强制参数**（F-032）：LightGBM/XGBoost/LibSVM 在 `initial_types is None` 时直接抛 ValueError；H2O 提供默认值 `[("input", FloatTensorType(["None", "None"]))]`。

## 第二步：compile — 五阶段优化

`Topology.compile()` 依次执行五个阶段：

```python
def compile(self):
    self._prune()                    # 阶段1：剪枝
    self._resolve_duplicates()       # 阶段2：identity消重
    self._fix_shapes()               # 阶段3：形状补全
    self._infer_all_types()          # 阶段4：类型推断
    self._check_structure()          # 阶段5：结构校验
```

### 阶段1：_prune() — 剪除不可达节点

从输出变量（leaves）开始反向BFS，标记所有可达的算子和变量，然后删除不可达节点。这一步清除 parse 阶段可能产生的"死代码"。

### 阶段2：_resolve_duplicates() — identity算子消重（F-020）

这是最精巧的阶段。parse 阶段为了简化处理，经常创建 identity 算子连接同一逻辑变量的不同版本。`_resolve_duplicates()` 采用**先替换后删除**的延迟策略：

```
对每个 identity 算子：
1. 找到 identity 的输入变量（original）和输出变量（duplicate）
2. 遍历所有其他算子，将引用 duplicate 的 input 替换为 original
3. 合并元信息：将 duplicate 的 doc_string/denotation/channel_denotations 复制到 original
4. 维度补全：如果 original 的某些维度是 None 而 duplicate 已知，用已知值填充
5. 标记 identity 算子和 duplicate 变量为 is_abandoned=True

遍历结束后：
6. 统一删除所有 is_abandoned 的算子和变量
```

**为什么先替换后删除？** 如果边遍历边删除，会导致迭代器失效或引用悬挂。先标记后统一删除是安全的图重写模式。

### 阶段3：_fix_shapes() — CoreML 2D→4D补全

CoreML 前端特定的后处理补丁：硬编码了17个算子类型名列表，将2D输入 `[N,C]` 补全为4D `[N,C,1,1]`。这是因为 CoreML 的图像输入习惯用4D（NCHW），但传统 ML 模型用2D。

### 阶段4：_infer_all_types() — 形状/类型推断

按拓扑顺序遍历算子，对每个算子执行形状推断：

```
for operator in 拓扑顺序:
    if operator.type in custom_shape_calculators:
        custom_shape_calculators[operator.type](operator)
    elif operator.type in custom_conversion_functions:
        pass  # Keras特殊通道：跳过形状推断
    else:
        operator.infer_types()  # → get_shape_calculator(operator.type)(operator)
```

⚠️ **不对称风险**：如果用户注册了 `custom_conversion_functions` 但没注册 `custom_shape_calculators`，形状推断会被静默跳过（走 `pass` 分支），可能导致输出形状错误。这是为 Keras 转换器保留的特殊通道，对其他场景是潜在 bug 源。

### 阶段5：_check_structure() — 孤立节点检测

检测并报告孤立算子（无输入或无输出连接）和孤立变量。

## 第三步：convert_topology — 拓扑遍历与ONNX节点生成（F-023）

`convert_topology()` 是IR到ONNX的核心转换函数：

```
convert_topology(topology, model_name, target_opset, ...)
  │
  ├─ 1. 验证/默认 target_opset（默认 min(15, onnx_opset_version())）
  ├─ 2. 创建 ModelComponentContainer（持有nodes/inputs/outputs/initializers列表）
  ├─ 3. 分类roots/leaves为tensor类和其他类
  ├─ 4. 按raw_model顺序添加inputs/outputs
  │     └─ ONNX命名合规校验（F-040）：替换_:/\/后若不合规发出警告
  ├─ 5. NHWC→NCHW转换（channel_first_inputs参数）
  ├─ 6. 拓扑迭代调度（核心循环）：
  │     for operator in topological_operator_iterator():
  │         if operator.type in topology.custom_conversion_functions:
  │             topology.custom_conversion_functions[operator.type](scope, operator, container)
  │         else:
  │             get_converter(operator.type)(scope, operator, container)
  │     # converter内部通过container.add_node()添加ONNX节点
  │     # converter可以创建新的Operator/Variable，下一轮扫描处理
  ├─ 7. opset<9时将initializers也加入inputs（旧版兼容）
  ├─ 8. 可选onnxconverter_common优化
  └─ 9. make_graph + make_model_ex → ModelProto
```

### ModelComponentContainer的作用

容器类收集所有转换产物：
- `nodes`：ONNX NodeProto 列表（算子节点）
- `inputs`/`outputs`：ValueInfoProto 列表（模型输入输出）
- `initializers`：TensorProto 列表（权重/参数）
- `value_info`：ValueInfoProto 列表（中间变量类型信息）
- `node_domain_version_pair_sets`：自动追踪使用的 (domain, version) 对

`add_node()` 方法自动管理 domain-version 对：创建节点后自动将 (op_domain, op_version) 加入集合，用于后续生成 opset_import。

## 第四步：make_model_ex — 模型组装（F-024, F-025）

```python
def make_model_ex(graph, ...):
    # 1. opset合并：按domain取最大版本
    opset_imports = {}
    for domain, version in node_domain_version_pair_sets:
        if domain not in opset_imports or version > opset_imports[domain]:
            opset_imports[domain] = version
    
    # 2. IR版本映射
    #    ai.onnx domain最低要求opset 8（IRv4，initializer独立）
    ir_version = OPSET_TO_IR_VERSION[opset_imports['']]
    
    # 3. 元数据填充
    model = helper.make_model(graph, ir_version=ir_version, opset_imports=...)
    model.producer_name = "OnnxMLTools"
    model.producer_version = "1.17.0"
    model.domain = "onnxml"
    model.model_version = 0
    
    return model
```

OPSET_TO_IR_VERSION 映射表：

| opset范围 | IR版本 | 关键变化 |
|-----------|--------|----------|
| 1-7 | IRv3 | initializer必须在inputs中 |
| 8-9 | IRv4 | initializer可独立于inputs |
| 10 | IRv5 | |
| 11-14 | IRv7 | |
| 15-18 | IRv8 | 默认目标opset |
| 19-20 | IRv9 | |
| 21-24 | IRv10 | |

## 各框架convert函数共性流程（F-031）

```python
# LightGBM/XGBoost/CoreML/H2O/LibSVM/SparkML 的统一模式
def convert(model, name=None, initial_types=None, doc_string="", 
            target_opset=None, targeted_onnx=None,
            custom_conversion_functions=None, custom_shape_calculators=None):
    # 1. 废弃参数警告
    if targeted_onnx is not None:
        warnings.warn("targeted_onnx is deprecated...", DeprecationWarning)
    
    # 2. 生成默认模型名（uuid4）
    if name is None:
        name = f"ONNX({model.__class__.__name__})" or str(uuid.uuid4())
    
    # 3. 默认target_opset
    if target_opset is None:
        target_opset = get_maximum_opset_supported()
    
    # 4. Booster自动包装（LightGBM/XGBoost特有）
    if isinstance(model, (lightgbm.Booster, xgboost.Booster)):
        model = WrappedBooster(model)
    
    # 5. Parse → IR
    topology = parse_xxx(model, initial_types, target_opset, 
                         custom_conversion_functions, custom_shape_calculators)
    
    # 6. Compile五阶段
    topology.compile()
    
    # 7. Convert → ONNX
    onnx_model = convert_topology(topology, name, doc_string, target_opset, ...)
    
    # 8. 后处理（框架特有）
    # - CoreML: 从spec提取metadata（author/license/shortDescription）
    # - LightGBM: zipmap/split/without_onnx_ml选项
    # - H2O: MOJO JSON临时文件处理
    
    return onnx_model
```

## 设计洞察

1. **四步分离职责**：parse负责翻译、compile负责验证优化、convert负责代码生成、make_model负责组装——这是编译器经典的阶段分离设计。
2. **延迟删除保证安全**：identity消重采用"先替换引用→标记废弃→统一删除"策略，避免遍历过程中修改数据结构导致迭代器失效。
3. **is_fed遍历支持动态图**：数据驱动调度天然支持converter在执行过程中创建新节点，这是传统Kahn算法无法直接处理的。
4. **opset版本管理集中化**：OPSET_TO_IR_VERSION映射表和自动domain-version追踪，确保输出模型版本一致性。

## 关联概念

- [Topology IR：三层核心类、C风格唯一名称、raw_name隐藏](01-topology-ir.md) — 深入理解IR数据结构
- [转换器注册与分发：双注册池、导入副作用、委托路径](03-converter-registration.md) — 了解converter查找和调度
- [XGBoost模型转ONNX实战](../examples/xgboost-conversion.md) — 完整示例
- [LightGBM Pipeline转换实战](../examples/lightgbm-pipeline.md) — 带zipmap/split选项的示例
