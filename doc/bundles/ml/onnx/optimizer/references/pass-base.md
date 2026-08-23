---
type: reference
title: "Pass 基类与注册机制"
description: "ONNX Optimizer 的 Pass 抽象基类、PredicateBasedPass/FullGraphBasedPass/ImmutablePass 继承体系、GlobalPassRegistry 注册中心的源码信源登记"
sources:
  - path: "external/libs/models/onnx/optimizer/onnxoptimizer/pass.h"
    facts: [F-016, F-017, F-018, F-019, F-020, F-021, F-022, F-023, F-024, F-027, F-028, F-029, F-030, F-031]
  - path: "external/libs/models/onnx/optimizer/onnxoptimizer/pass.cc"
    facts: [F-023, F-025, F-026]
  - path: "external/libs/models/onnx/optimizer/onnxoptimizer/pass_registry.h"
    facts: [F-032, F-033, F-034, F-035]
  - path: "external/libs/models/onnx/optimizer/onnxoptimizer/pass_registry.cc"
    facts: [F-036]
---

# Pass 基类与注册机制

## 信源概述

| 信源 | 类型 | 职责 |
|------|------|------|
| `onnxoptimizer/pass.h` | 头文件 | Pass 基类、枚举类型、PredicateBasedPass/FullGraphBasedPass/ImmutablePass 派生类声明 |
| `onnxoptimizer/pass.cc` | 实现文件 | Pass 基类子图递归方法、PredicateBasedPass 核心遍历算法实现 |
| `onnxoptimizer/pass_registry.h` | 头文件 | GlobalPassRegistry 单例注册表、registerPass 模板方法 |
| `onnxoptimizer/pass_registry.cc` | 实现文件 | GetFuseAndEliminationPass 默认 pass 集合筛选逻辑 |

## 命名空间

**F-016**：所有优化相关代码位于 `ONNX_NAMESPACE::optimization` 命名空间。

```cpp
namespace ONNX_NAMESPACE {
namespace optimization {
// ... Pass 体系全部代码
} // namespace optimization
} // namespace ONNX_NAMESPACE
```

## 枚举类型

### F-017：PassType 枚举——pass 分类

| 值 | 名称 | 含义 |
|----|------|------|
| 0 | `Fuse` | 算子融合（如 Conv+BN 融合） |
| 1 | `Nop` | 移除无用操作（如消除恒等 Transpose） |
| 2 | `Separate` | 分离/拆分（如 split_init/predict） |
| 3 | `Immutable` | 不可变/分析 pass |
| 4 | `Replace` | 节点替换（如 Einsum→MatMul） |
| 5 | `Other` | 其他（如重命名、设置唯一名称） |

### F-018：PassEfficiency 枚举——执行效率

| 值 | 名称 | 含义 |
|----|------|------|
| 0 | `Partial` | 连续两次执行不等价于一次，可能需要定点迭代 |
| 1 | `Complete` | 连续两次执行等价于一次（幂等） |

### F-019：PassOptimizationType 枚举——优化目标

| 值 | 名称 | 含义 |
|----|------|------|
| 0 | `None` | 无特定优化目标 |
| 1 | `Compute` | 计算优化 |
| 2 | `Memory` | 内存优化 |
| 3 | `ComputeMemory` | 计算+内存双重优化 |
| 4 | `Stability` | 数值稳定性（如 log-sum-exp 技巧） |

### F-020：PassAnalysisType 枚举——分析结果类型

| 值 | 名称 | 含义 |
|----|------|------|
| 0 | `Empty` | 空分析结果 |
| 1 | `CountBased` | 基于变换计数的分析 |

### F-021：NodeDestroyType 枚举——节点销毁策略

| 值 | 名称 | 含义 |
|----|------|------|
| 0 | `DestroyZero` | 不销毁当前节点 |
| 1 | `DestroyOne` | 调用一次 `it.destroyCurrent()` 销毁节点 |

> 注：之前存在的 `DestroyTwo` 因拓扑序不明确已移除。

## F-022：Pass 抽象基类

`Pass` 是所有优化 pass 的抽象基类。

```cpp
class Pass {
public:
  Pass(PassType pass_type, PassEfficiency pass_efficiency,
       PassOptimizationType pass_optimization_type);
  virtual ~Pass();

  virtual PassAnalysisType getPassAnalysisType() const = 0;
  virtual std::shared_ptr<PostPassAnalysis> runPass(Graph& graph) = 0;
  virtual std::string getPassName() const = 0;

  // 可覆盖的生命周期钩子
  virtual bool initializePass(Graph&);     // 默认返回 false
  virtual bool finalizePass(Graph&);       // 默认返回 false
};
```

三个元数据字段在构造时设置，通过 getter 访问：
- `pass_type`：F-017 中的 PassType
- `pass_efficiency`：F-018 中的 PassEfficiency
- `pass_optimization_type`：F-019 中的 PassOptimizationType

## F-023：子图递归工具方法

`Pass` 基类提供两个保护方法用于递归处理子图属性（如 Loop/If 节点体内的子图）：

```cpp
protected:
  // 对节点的 graph 属性递归应用 fn 并累计变更计数
  unsigned DescendOnGraphAttributesAndCount(
      Node* n,
      std::function<unsigned(Graph&)> fn);

  // 无返回值约束的版本
  void DescendOnGraphAttributesUnconstrained(
      Node* n,
      std::function<void(Graph&)> fn);
```

递归处理的图属性为 `g`（单个子图）和 `gs`（子图列表），对应 ONNX 中 Loop/If/Scan 等控制算子的子图属性。

## F-024~F-027：PredicateBasedPass——最常用的 pass 基类

`PredicateBasedPass` 继承自 `Pass`，是大多数优化 pass 的基类，采用"单节点谓词匹配+原地变换"范式。

### 子类必实现的纯虚方法

```cpp
protected:
  // 模式匹配谓词：判断当前节点是否匹配优化模式
  virtual bool patternMatchPredicate(Node* node) = 0;

  // 执行变换：对匹配的节点执行优化，通过 destroy_current 控制是否销毁节点
  virtual bool runTransform(Node* node, Graph& graph,
                            NodeDestroyType& destroy_current) = 0;
```

### F-025：核心遍历算法 `_runPassInternal`

```
对图中所有节点按拓扑序遍历：
  1. 先递归处理当前节点的子图属性（DescendOnGraphAttributesAndCount）
  2. 调用 patternMatchPredicate(node) 判定是否匹配
  3. 若匹配，调用 runTransform(node, graph, destroy_current)
  4. 根据 destroy_current 决定是否销毁当前节点
  5. 累计成功变换计数
```

### F-026：runPass 完整流程

```
initializePass(graph) → _runPassInternal(graph) → finalizePass(graph)
→ 返回 CountBasedPassAnalysis
```

### F-027：Opset 版本查询工具

```cpp
static std::int64_t getOpsetVersion(const Graph& g);
```

遍历图的 opset_versions，查找空域名（`""`，即默认 ONNX 域）的 opset 版本，默认返回 0。

## F-028：FullGraphBasedPass——全图遍历基类

`FullGraphBasedPass` 继承自 `Pass`，不约束匹配模式，允许子类直接操作整个图引用。适用于需要全局分析的优化：

- `SplitInit` / `SplitPredict`
- `EliminateDeadEnd`
- `EliminateUnusedInitializer`
- `EliminateDuplicateInitializer`
- `EliminateCommonSubexpression`（CSE）
- `LiftLexicalReferences`
- `RenameInputOutput`
- `NopEmptyPass`

## F-029：ImmutablePass——分析 pass 基类

`ImmutablePass` 继承自 `Pass`，构造时硬编码：
- `PassType::Immutable`
- `PassEfficiency::Complete`
- `PassOptimizationType::None`

用于只读分析类 pass。注意当前代码中 `AdjustAdd` 虽然使用 `PassType::Immutable` 标记，但继承自 `PredicateBasedPass` 而非 `ImmutablePass`。

## F-030：PostPassAnalysis 与 CountBasedPassAnalysis

`PostPassAnalysis` 是 pass 执行后返回的分析结果基类（虚析构函数）。

`CountBasedPassAnalysis` 继承 `PostPassAnalysis`，记录：
- `pass`：执行的 pass 指针
- `num_positive_transforms`：成功变换次数
- `initialization_done` / `finalization_done`：生命周期标记

提供的关键方法：
- `graphChanged()`：变换次数 > 0
- `numSucceededTransforms()`：返回成功变换次数
- `fixedPointOptimizationNeeded()`：图已变更 **且** pass 效率为 Partial，需要定点迭代

## F-031：安全替换工具函数

`pass.h` 提供两个内联工具函数，用于安全替换值/节点的所有使用：

```cpp
// 替换 oldValue 的所有使用为 newValue
bool tryReplacingAllUsesWith(Value* oldValue, Value* newValue);

// 替换 oldNode 的所有输出使用为 newNode 的输出
bool tryReplacingAllUsesWith(Node* oldNode, Node* newNode);
```

**保护机制**：替换前检查两个值是否同为 graph input 或同为 graph output，若是则拒绝替换，避免破坏输入输出名称。

## F-032~F-036：GlobalPassRegistry 注册中心

### F-032：注册表数据结构

```cpp
struct GlobalPassRegistry {
  std::map<std::string, std::shared_ptr<Pass>> passes;  // 名称→Pass 实例
  std::vector<std::string> pass_names;                  // 注册顺序列表
};
```

以静态成员方式持有，是全局单例。

### F-033：50 个 pass 的注册

构造函数中通过 `registerPass<T>()` 模板方法注册全部 50 个 pass，注册顺序即为 pass 的默认执行顺序。

### F-034：registerPass 模板方法

```cpp
template <typename T>
void registerPass() {
  static_assert(std::is_base_of<Pass, T>::value,
                "T must inherit from Pass");
  auto pass = std::make_shared<T>();
  passes[pass->getPassName()] = pass;
  pass_names.push_back(pass->getPassName());
}
```

编译期约束 T 必须继承 Pass，以 pass 名称为 key 存入 map，并按注册顺序追加到 pass_names。

### F-035：按名称查找 pass

```cpp
std::shared_ptr<Pass> find(const std::string& pass_name) const;
```

若名称不存在，通过 `ONNX_ASSERTM` 触发断言失败，输出 `"pass %s is unknown."`。

### F-036：GetFuseAndEliminationPass——默认优化集

遍历 `pass_names`，筛选 `PassType::Fuse` 或 `PassType::Nop` 类型的 pass 名称返回。即默认优化集**仅包含**融合类和消除类 pass，不包含 Separate/Replace/Other/Immutable 类型。
