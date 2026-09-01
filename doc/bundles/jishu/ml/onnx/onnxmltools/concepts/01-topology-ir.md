---
type: concept
title: "Topology IR：三层核心类、C风格唯一名称、raw_name隐藏"
description: "onnxmltools Topology IR 的核心数据结构：Topology（计算图）、Scope（作用域）、Operator（算子节点）、Variable（数据流边）四核心类的设计，C风格唯一名称生成算法，raw_name→onnx_name多对一隐藏机制模拟SSA"
sources:
  references: [../references/topology-ir.md, ../references/registration-types.md]
  facts: [F-015, F-016, F-017, F-018, F-039]
---

# Topology IR：三层核心类、C风格唯一名称、raw_name隐藏

## 核心理解

Topology IR 是 onnxmltools 自有转换路径的"中间语言"，采用**三层嵌套结构**：

- **Topology**（顶层计算图）：持有所有 Scope、原始模型容器、全局配置
- **Scope**（作用域）：管理命名空间，持有本作用域的 Operator 和 Variable
- **Operator**（算子节点）：代表一次计算，通过输入/输出 Variable 连接成图
- **Variable**（数据流边）：连接 Operator 的输入输出，携带类型信息

```
Topology
├── Scope 0（根作用域）
│   ├── Operator "LgbmClassifier"
│   │   ├── inputs:  [Variable "input"]
│   │   └── outputs: [Variable "label", Variable "probabilities"]
│   ├── Operator "LgbmZipMap"
│   │   ├── inputs:  [Variable "probabilities"]
│   │   └── outputs: [Variable "output_probability"]
│   └── Variable 映射表...
└── Scope N（子作用域，如Pipeline内部步骤）
```

## 四核心类详解

### Topology：计算图容器

Topology 是整个 IR 的根对象，持有：

| 属性 | 类型 | 说明 |
|------|------|------|
| `raw_model` | RawModelContainer | 原始模型的多态封装 |
| `scopes` | List[Scope] | 所有作用域列表 |
| `initial_types` | List | 输入类型声明 |
| `target_opset` | int | 目标 opset 版本 |
| `custom_conversion_functions` | dict | 自定义转换器 |
| `custom_shape_calculators` | dict | 自定义形状计算器 |
| `unique_name_set` | Set[str] | 全局唯一名称集合 |

Topology 提供 `_generate_unique_name(seed)` 方法生成全局唯一名称，`compile()` 方法执行五阶段编译优化，以及拓扑迭代器方法。

### Scope：作用域与命名空间

Scope 是变量和算子的命名空间容器：

| 属性 | 类型 | 说明 |
|------|------|------|
| `topology` | Topology | 回指所属 Topology |
| `parent` | Scope \| None | 父作用域（根作用域为None） |
| `onnx_name_to_variable` | dict | onnx_name → Variable 映射（唯一名称查找） |
| `variable_name_mapping` | dict | raw_name → [onnx_name列表]（隐藏机制） |
| `operators` | List[Operator] | 本作用域内的算子 |

Scope 的核心方法：
- `declare_local_variable(raw_name)`：创建新 Variable，生成唯一 onnx_name
- `get_local_variable_or_declare_one(raw_name)`：获取最新变量或创建新变量
- `declare_local_operator(op_type, raw_model=None)`：创建新 Operator
- `delete_local_operator(operator)` / `delete_local_variable(variable)`：延迟删除

### Operator：计算节点

Operator 代表一次原子计算（对应一个或多个 ONNX 节点）：

| 属性 | 类型 | 说明 |
|------|------|------|
| `type` | str | 算子类型字符串（注册key，如"LgbmClassifier"） |
| `onnx_name` | str | 唯一 ONNX 名称 |
| `inputs` | List[Variable] | 输入变量列表 |
| `outputs` | List[Variable] | 输出变量列表 |
| `is_evaluated` | bool | 拓扑遍历标记：是否已执行 |
| `operator_version` | int | 算子版本 |
| `raw_operator` | object | 原始模型中的对应对象 |
| `is_abandoned` | bool | identity消重时的废弃标记 |

Operator 的核心方法：
- `infer_types()`：通过注册表分发到 shape_calculator 函数（F-039）
- `add_input`/`add_output`：添加输入/输出变量

### Variable：数据流边

Variable 是 Operator 之间的连接边，携带类型信息：

| 属性 | 类型 | 说明 |
|------|------|------|
| `onnx_name` | str | 唯一 ONNX 名称（最终在ONNX图中使用的名称） |
| `raw_name` | str | 原始名称（parse阶段使用的逻辑名称，可能重复） |
| `type` | DataType | 数据类型（FloatTensorType等） |
| `is_fed` | bool | 数据流标记：该变量的值是否已"就绪" |
| `is_abandoned` | bool | 废弃标记（identity消重用） |
| `doc_string` | str | 文档字符串 |
| `denotation` | str | 语义标注（如"DATA_BATCH"） |
| `channel_denotations` | dict | 通道级语义标注 |

## C风格唯一名称生成（F-016）

ONNX 对节点和变量的命名有严格要求：名称必须符合 C 标识符风格（字母数字下划线，不能数字开头）。`Topology._generate_unique_name(seed)` 的算法：

```
输入：seed（原始名称字符串）
1. 正则替换：将所有非 [0-9a-zA-Z] 字符替换为 "_"
2. 数字前缀处理：如果首字符是数字，前面补 "_"
3. 重名处理：如果名称已存在，追加递增数字（1, 2, 3...）
输出：唯一合法名称
```

示例：

| seed | 生成名称 |
|------|----------|
| `"input"` | `"input"` |
| `"input:0"` | `"input_0"` |
| `"123feature"` | `"_123feature"` |
| `"x"`（首次） | `"x"` |
| `"x"`（重复） | `"x1"` |
| `"x"`（再次） | `"x2"` |

这个算法确保所有 onnx_name 在全局范围内唯一且符合 ONNX 命名规范。

## raw_name隐藏机制：模拟SSA（F-017）

在转换过程中，同一逻辑变量可能在不同阶段被不同算子"重新赋值"（例如：先经过 Scaler 归一化，再经过 Classifier 分类）。但 ONNX 计算图是 SSA（静态单赋值）形式——每个变量只能被一个算子产出。

onnxmltools 通过 `variable_name_mapping` 实现"隐藏"机制来处理这个矛盾：

```
假设 parse 阶段创建了以下变量：
1. Variable(raw_name="features", onnx_name="features") → 原始输入
2. Variable(raw_name="features", onnx_name="features1") → Scaler的输出
3. Variable(raw_name="label", onnx_name="label") → Classifier的输出

variable_name_mapping = {
    "features": ["features", "features1"],  # features1隐藏了features
    "label": ["label"],
}
```

`get_local_variable_or_declare_one("features")` 总是返回列表中**最后一个** Variable（`features1`），即最新版本"隐藏"了旧版本。这在行为上模拟了 SSA 的 φ 节点效果——引用同一逻辑名称时自动获取最新版本。

这是一种"先膨胀后收缩"策略：parse 阶段为同一逻辑名创建多个 Variable（通过 identity 算子连接），compile 阶段的 `_resolve_duplicates()` 再将它们合并消除冗余。

## is_fed数据驱动拓扑遍历（F-018）

拓扑遍历不使用传统的DFS或Kahn算法，而是一种**数据驱动的Level-Order调度**：

```
初始化阶段（反向标记技巧）：
  1. 所有变量 is_fed = True
  2. 遍历所有算子，将其输出变量 is_fed = False
  → 根变量（非任何算子输出）天然保持 is_fed = True

调度循环：
  while True:
    收集所有"输入全部fed且自身未evaluated"的算子
    if 没有这样的算子: break（死锁检测）
    按优先级排序（tensorToProbabilityMap最后执行）
    for 每个可执行算子:
      标记 is_evaluated = True
      yield 算子给converter执行
      标记其输出变量 is_fed = True
    额外检查：标记"不被任何算子产出"的变量为fed
```

这种设计相比传统拓扑排序的优势：
1. **支持动态图增长**：converter 执行过程中可以创建新的 Operator 和 Variable，下一轮扫描自然发现
2. **天然支持优先级**：同一轮中可按优先级排序后处理
3. **简单鲁棒**：无需预先构建邻接表，对百级算子规模性能完全可接受
4. **反向标记初始化**：通过"全标fed→输出置unfed"的技巧，根变量天然fed，无需额外查找

## 关联概念

- [编译流水线五阶段：createTopology→compile→convert_topology→make_model](02-conversion-pipeline.md) — 了解IR如何被编译和转换为ONNX
- [转换器注册与分发：双注册池、导入副作用、委托路径](03-converter-registration.md) — 了解converter如何注册和分发
- [数据类型系统：四层DataType、TensorType维度规格、三向类型猜测](04-type-system.md) — 了解Variable的type字段含义
