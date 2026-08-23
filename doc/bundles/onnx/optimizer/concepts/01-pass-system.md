---
type: concept
title: "Pass 系统：基类继承体系与注册机制"
description: "ONNX Optimizer 的 Pass 类层次结构、三个元数据注解（类型/效率/优化目标）、PredicateBasedPass 单节点匹配范式、FullGraphBasedPass 全图遍历、GlobalPassRegistry 注册中心"
sources:
  references: [../references/pass-base.md]
  facts: [F-016, F-017, F-018, F-019, F-020, F-021, F-022, F-023, F-024, F-025, F-026, F-027, F-028, F-029, F-030, F-031, F-032, F-033, F-034, F-035, F-036]
---

# Pass 系统：基类继承体系与注册机制

## 核心理解

Pass 是 ONNX Optimizer 的核心抽象——每个优化变换都封装为一个 Pass 对象。Pass 系统采用**模板方法模式**：基类定义执行骨架，子类实现具体的匹配和变换逻辑。绝大多数 pass 采用"单节点谓词匹配+原地变换"的 PredicateBasedPass 范式，需要全局分析的 pass 则使用 FullGraphBasedPass。

## Pass 类继承体系

```
Pass（抽象基类）
├── PredicateBasedPass（最常用：逐节点匹配+变换）
│   ├── fuse_add_bias_into_conv
│   ├── fuse_bn_into_conv
│   ├── eliminate_nop_transpose
│   ├── fuse_qkv
│   ├── eliminate_if_with_const_cond
│   ├── extract_constant_to_initializer
│   └── ... （约 40+ 个内置 pass）
├── FullGraphBasedPass（全图遍历，无匹配约束）
│   ├── eliminate_deadend
│   ├── eliminate_unused_initializer
│   ├── eliminate_duplicate_initializer
│   ├── eliminate_common_subexpression (CSE)
│   ├── split_init / split_predict
│   ├── lift_lexical_references
│   ├── rename_input_output
│   └── nop（空 pass）
└── ImmutablePass（分析 pass，当前未直接使用）
    └── （AdjustAdd 虽然标记 Immutable 类型，但继承 PredicateBasedPass）
```

## 三个元数据注解

每个 Pass 在构造时必须指定三个元数据，用于分类和执行策略决策：

### PassType——做什么类型的变换

| 类型 | 值 | 含义 | 默认集包含? |
|------|----|------|:-----------:|
| Fuse | 0 | 算子融合（合并多个算子为一个） | ✅ |
| Nop | 1 | 移除无用/恒等操作 | ✅ |
| Separate | 2 | 图分离/拆分（改变图结构） | ❌ |
| Immutable | 3 | 不可变分析 pass | ❌ |
| Replace | 4 | 算子替换（如 Einsum→MatMul） | ❌ |
| Other | 5 | 其他（重命名、设置名称等） | ❌ |

> 默认优化集（`GetFuseAndEliminationPass`）只包含 Fuse 和 Nop 两类，因为它们是"安全等价变换"——不改变图结构、不改变输入输出签名、不改变计算结果。

### PassEfficiency——执行多少次能收敛

| 类型 | 值 | 含义 | 需要定点迭代? |
|------|----|------|:-------------:|
| Partial | 0 | 单次执行不幂等，连续执行可能继续产生变换 | ✅ |
| Complete | 1 | 单次执行幂等，连续两次执行等价于一次 | ❌ |

Partial 效率的 pass 在 FixedPointPassManager 中会被反复执行直到不再产生变换。例如 `fuse_consecutive_transposes`：第一次融合相邻的两个 Transpose 可能产生新的相邻 Transpose 对，需要迭代。

### PassOptimizationType——优化什么目标

| 类型 | 值 | 典型场景 |
|------|----|----------|
| None | 0 | 结构/元数据变换（重命名、设名称） |
| Compute | 1 | 减少计算量（融合、消除） |
| Memory | 2 | 减少内存占用（消除冗余数据） |
| ComputeMemory | 3 | 同时优化计算和内存 |
| Stability | 4 | 提升数值稳定性（如 log-sum-exp） |

## Pass 生命周期

```
Pass 被添加到 PassManager
        ↓
  runPass(Graph&) 被调用
        ↓
  ┌─ initializePass(Graph&)  ── 初始化（可覆盖，默认 false）
  │      ↓
  │  具体变换逻辑（子类实现）
  │      ↓
  └─ finalizePass(Graph&)    ── 收尾（可覆盖，默认 false）
        ↓
  返回 PostPassAnalysis（通常是 CountBasedPassAnalysis）
```

- `initializePass`：在变换前执行一次性初始化，返回 true 表示图已被修改
- `finalizePass`：在变换后执行收尾，返回 true 表示图已被修改
- 大多数 pass 不需要覆盖这两个方法，使用默认实现（返回 false）

## PredicateBasedPass：核心范式

PredicateBasedPass 是最常用的 pass 基类，采用**逐节点谓词匹配+原地变换**范式。子类只需实现两个方法：

```cpp
class MyPass : public PredicateBasedPass {
public:
  MyPass() : PredicateBasedPass(
      PassType::Fuse,           // 类型
      PassEfficiency::Complete, // 效率
      PassOptimizationType::Compute  // 目标
  ) {}

  std::string getPassName() const override { return "my_pass"; }

protected:
  // 模式匹配：判断当前节点是否是要优化的模式
  bool patternMatchPredicate(Node* node) override {
    return node->kind() == kMyOp;  // 检查算子类型等条件
  }

  // 执行变换：对匹配的节点执行优化
  bool runTransform(Node* node, Graph& graph,
                    NodeDestroyType& destroy_current) override {
    // 执行变换逻辑...
    // destroy_current = DestroyOne 表示销毁当前节点
    // destroy_current = DestroyZero 表示保留当前节点
    return true;  // 返回 true 表示执行了变换
  }
};
```

### 核心遍历算法

```
对图中所有节点按拓扑序遍历：
  1. DescendOnGraphAttributesAndCount(node, fn)
     → 递归处理节点的子图属性（Loop/If/Scan 的 body）
  2. if patternMatchPredicate(node):
     → destroy_current = DestroyZero
     → runTransform(node, graph, destroy_current)
     → if destroy_current == DestroyOne:
          it.destroyCurrent()  // 销毁当前节点
     → num_transforms++
返回 CountBasedPassAnalysis(num_transforms)
```

**关键特性**：
- **拓扑序遍历**：保证前驱节点在后继之前处理
- **子图递归**：自动递归处理控制算子内的子图
- **节点销毁控制**：通过 `destroy_current` 输出参数控制是否销毁匹配节点
- **变换计数**：记录成功变换次数用于定点收敛判断

### Opset 版本感知

PredicateBasedPass 提供静态工具方法：

```cpp
static std::int64_t getOpsetVersion(const Graph& g);
```

遍历图的 opset_versions 查找默认 ONNX 域（空域名 ""）的 opset 版本，用于根据 opset 版本选择不同的变换策略（例如某些算子在高版本 opset 中新增了属性）。

## FullGraphBasedPass：全图遍历

FullGraphBasedPass 继承 Pass，不约束匹配模式，子类直接在 `runPass(Graph&)` 中操作整个图：

```cpp
class MyGlobalPass : public FullGraphBasedPass {
public:
  MyGlobalPass() : FullGraphBasedPass(
      PassType::Nop, PassEfficiency::Complete, PassOptimizationType::Compute
  ) {}
  std::string getPassName() const override { return "my_global_pass"; }
  std::shared_ptr<PostPassAnalysis> runPass(Graph& graph) override {
    // 直接遍历整个图，执行全局分析和变换
    unsigned num_changes = 0;
    for (auto it = graph.begin(); it != graph.end(); ++it) {
      // 自定义逻辑...
    }
    return std::make_shared<CountBasedPassAnalysis>(
        this, num_changes, false, false);
  }
};
```

适用于需要全局视图的优化：
- **死代码消除**（eliminate_deadend）：需要从图输出反向遍历可达性
- **CSE**（eliminate_common_subexpression）：需要全局哈希表
- **init/predict 分离**（split_init/split_predict）：需要区分不纯算子
- **词法引用提升**（lift_lexical_references）：需要环境栈跨子图分析

## CountBasedPassAnalysis 与定点收敛

每个 pass 执行后返回 `CountBasedPassAnalysis`，记录变换次数和 pass 效率：

```cpp
// 是否需要定点迭代？
bool fixedPointOptimizationNeeded() const {
  return num_positive_transforms > 0     // 本轮有变换
      && pass->getPassEfficiency() == Partial;  // 且 pass 非幂等
}

// 图是否被修改？
bool graphChanged() const {
  return num_positive_transforms > 0;
}
```

这两个方法是 FixedPointPassManager 判断是否继续迭代的依据。详见 [PassManager 执行模型](03-pass-execution.md)。

## 安全替换工具

`pass.h` 提供 `tryReplacingAllUsesWith` 工具函数，安全地替换值或节点的所有使用：

```cpp
// 将 oldValue 的所有使用替换为 newValue
bool tryReplacingAllUsesWith(Value* oldValue, Value* newValue);

// 将 oldNode 的所有输出使用替换为 newNode 的对应输出
bool tryReplacingAllUsesWith(Node* oldNode, Node* newNode);
```

**保护机制**：如果 oldValue 和 newValue 同为 graph input 或同为 graph output，拒绝替换——避免破坏模型的输入输出签名。

## GlobalPassRegistry：全局注册中心

`GlobalPassRegistry` 以静态成员方式持有所有已注册 pass，是单例模式：

```
注册阶段（程序启动时，构造函数中）：
  registerPass<FuseBNIntoConv>()   →  passes["fuse_bn_into_conv"] = instance
  registerPass<EliminateNopTranspose>() → ...
  ...（共 50 个 pass）

查找阶段：
  find("fuse_bn_into_conv")  →  shared_ptr<Pass>
  find("unknown_pass")       →  ONNX_ASSERTM 失败，输出 "pass unknown_pass is unknown."
```

### registerPass 模板方法

```cpp
template <typename T>
void registerPass() {
  static_assert(std::is_base_of<Pass, T>::value, "T must inherit from Pass");
  auto pass = std::make_shared<T>();
  passes[pass->getPassName()] = pass;
  pass_names.push_back(pass->getPassName());
}
```

编译期确保 T 继承自 Pass，按 `getPassName()` 返回的名称注册，同时维护注册顺序列表 `pass_names`。

### 默认 pass 集合

`GetFuseAndEliminationPass()` 筛选出 PassType 为 Fuse 或 Nop 的 pass 名称。这是：
- Python `optimize()` 在 `passes=None` 时使用的集合
- CLI 在未指定 `--passes` 时使用的集合
- C++ `GetFuseAndEliminationPass()` 返回的集合

50 个 pass 中，Fuse 类 17 个、Nop 类 21 个，共 38 个在默认集合中；Separate 类 3 个、Replace 类 4 个、Other 类 3 个、Immutable 类 1 个、Nop(Fused) 1 个不在默认集合中。

## 子图递归处理

Pass 基类提供两个保护方法用于递归处理子图（控制算子体内的嵌套计算图）：

```cpp
// 返回变换计数的版本
unsigned DescendOnGraphAttributesAndCount(
    Node* n, std::function<unsigned(Graph&)> fn);

// 无返回值的版本
void DescendOnGraphAttributesUnconstrained(
    Node* n, std::function<void(Graph&)> fn);
```

递归处理的图属性名为 `g`（单个子图，如 If 的 then_branch/else_branch）和 `gs`（子图列表，如 Loop 的 body）。PredicateBasedPass 的 `_runPassInternal` 自动调用此方法，确保子图中的节点也被优化。

## 关联概念

- [内置优化 Passes 分类详解](02-builtin-passes.md) — 了解 50 个内置 pass 的具体功能
- [PassManager 执行模型与定点收敛](03-pass-execution.md) — 了解 pass 如何被调度执行
- [算子融合模式](04-fusion-patterns.md) — 深入理解 Fuse 类 pass 的变换模式
- [自定义 Pass 开发方法](06-custom-pass.md) — 学习如何编写自己的优化 pass
