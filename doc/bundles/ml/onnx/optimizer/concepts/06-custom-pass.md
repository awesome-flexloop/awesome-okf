---
type: concept
title: "自定义 Pass 开发方法"
description: "如何选择 PredicateBasedPass vs FullGraphBasedPass 基类、patternMatchPredicate 编写模式、runTransform 节点操作规范、tryReplacingAllUsesWith 保护机制、pass_util 工具函数、子图递归处理、opset 版本兼容、注册新 pass 的方法"
sources:
  references: [../references/pass-base.md]
  facts: [F-022, F-023, F-024, F-025, F-026, F-027, F-028, F-031, F-034, F-046, F-047, F-048, F-049, F-053, F-057]
---

# 自定义 Pass 开发方法

## 核心理解

ONNX Optimizer 的扩展性体现在 Pass 类体系上——添加新优化只需继承合适的基类、实现匹配和变换逻辑、注册到 GlobalPassRegistry 即可。绝大多数局部优化（如 peephole 优化、简单融合、nop 消除）应使用 `PredicateBasedPass`；需要全局分析的优化（如死代码消除、CSE）使用 `FullGraphBasedPass`。理解框架提供的工具函数和节点操作规范是正确开发 pass 的关键。

## 基类选择决策树

```
需要开发新的优化 pass
        │
        ├── 优化模式是"逐节点判断→局部变换"？
        │       │
        │       ├── 是 → PredicateBasedPass（绝大多数情况）
        │       │         实现 patternMatchPredicate() + runTransform()
        │       │
        │       └── 否 → 需要全图分析？
        │               │
        │               ├── 是 → FullGraphBasedPass
        │               │       直接实现 runPass()
        │               │
        │               └── 否 → 是否只读分析？
        │                       │
        │                       ├── 是 → ImmutablePass（当前极少使用）
        │                       └── 否 → FullGraphBasedPass（通用基类）
```

### 选择 PredicateBasedPass 的场景

- 消除恒等操作（如检测到恒等模式直接移除）
- 简单算子融合（两个或三个相邻算子的固定模式匹配）
- 单节点属性调整（如修改某个属性值）
- 常量提取（匹配 Constant 节点转为 initializer）

### 选择 FullGraphBasedPass 的场景

- 死代码消除（需要从输出反向遍历可达性）
- 公共子表达式消除（需要全局哈希表）
- 图结构拆分（如 init/predict 分离）
- 跨子图分析（如词法引用提升）
- 需要多次遍历图的优化

## PredicateBasedPass 开发模板

### 最小实现框架

```cpp
#pragma once
#include "onnxoptimizer/pass.h"

namespace ONNX_NAMESPACE {
namespace optimization {

struct MyCustomPass final : public PredicateBasedPass {
  // 1. 构造函数：指定三个元数据
  explicit MyCustomPass()
      : PredicateBasedPass(
            PassType::Nop,             // 变换类型
            PassEfficiency::Complete,   // 执行效率
            PassOptimizationType::Compute  // 优化目标
        ) {}

  // 2. Pass 名称
  std::string getPassName() const override {
    return "my_custom_pass";
  }

  // 3. 模式匹配谓词
  bool patternMatchPredicate(Node* node) override {
    // 检查节点是否匹配你的优化模式
    // 常用检查：
    //   node->kind() == kRelu        // 算子类型
    //   CheckKind<kRelu>(node)       // 递归检查（含前驱）
    return node->kind() == kMyTargetOp
        && node->hasAttribute(kalpha)
        && node->f(kalpha) == 0.0;  // 特定属性值
  }

  // 4. 执行变换
  bool runTransform(Node* node, Graph& graph,
                    NodeDestroyType& destroy_current) override {
    // 执行你的变换逻辑...
    // 常见操作：
    //   - 创建新节点替换旧节点
    //   - 修改输入/输出连接
    //   - 修改属性值
    //   - 销毁节点

    // 如果变换后应该销毁当前节点：
    destroy_current = NodeDestroyType::DestroyOne;
    // 如果保留当前节点：
    // destroy_current = NodeDestroyType::DestroyZero;

    return true;  // 返回 true 表示执行了变换
  }
};

} // namespace optimization
} // namespace ONNX_NAMESPACE
```

### patternMatchPredicate 编写模式

**检查算子类型**：

```cpp
// 简单类型检查
bool patternMatchPredicate(Node* node) override {
  return node->kind() == kTranspose;
}
```

**检查前驱算子类型（使用 pass_util）**：

```cpp
#include "onnxoptimizer/passes/pass_util.h"

bool patternMatchPredicate(Node* node) override {
  // 当前节点是 Add，且第一个输入来自 Conv
  return node->kind() == kAdd
      && CheckKind<kConv>(node, 0);  // 检查第0个输入的前驱是 Conv
}
```

**检查常量输入**：

```cpp
bool patternMatchPredicate(Node* node) override {
  // 节点的某个输入是常量
  return IsConstantTensor(node->inputs()[1]);
}
```

**检查属性**：

```cpp
bool patternMatchPredicate(Node* node) override {
  return node->kind() == kDropout
      && node->hasAttribute(kratio)
      && node->f(kratio) == 0.0f;
}
```

### runTransform 常见操作模式

**模式1：移除恒等节点**

```cpp
bool runTransform(Node* node, Graph& graph,
                  NodeDestroyType& destroy_current) override {
  // 将所有输出替换为输入（Identity 模式）
  if (node->output()->has_sizes()) {
    node->inputs()[0]->setSizes(node->output()->sizes());
  }
  if (node->output()->has_same_sizes()) {
    node->inputs()[0]->setSameSizes(node->output()->same_sizes());
  }
  node->output()->replaceAllUsesWith(node->inputs()[0]);
  destroy_current = NodeDestroyType::DestroyOne;
  return true;
}
```

**模式2：提取常量到 initializer**

```cpp
bool runTransform(Node* node, Graph& graph,
                  NodeDestroyType& destroy_current) override {
  // 获取 Constant 节点的 value 属性
  Tensor t = node->t(kvalue);
  // 创建新的 initializer
  Value* new_init = graph.addInitializerAndCreateValue(t);
  // 替换所有使用
  if (!tryReplacingAllUsesWith(node->output(), new_init)) {
    // 替换失败（如输出是 graph output），不销毁节点
    destroy_current = NodeDestroyType::DestroyZero;
    return false;
  }
  destroy_current = NodeDestroyType::DestroyOne;
  return true;
}
```

**模式3：融合两个节点**

```cpp
bool runTransform(Node* node, Graph& graph,
                  NodeDestroyType& destroy_current) override {
  // node 是后面的节点（如 BN），前驱是 Conv
  Node* conv = PrevNode(node, 0);  // 获取第0个输入的前驱节点

  // 计算融合后的权重和偏置
  Tensor fused_W = compute_fused_weight(conv, node);
  Tensor fused_b = compute_fused_bias(conv, node);

  // 更新 Conv 的权重 initializer
  // ...（替换 initializer 值）

  // 将 BN 的输出替换为 Conv 的输出
  node->output()->replaceAllUsesWith(conv->output());

  // 销毁 BN 节点（Conv 保留）
  destroy_current = NodeDestroyType::DestroyOne;
  return true;
}
```

**模式4：创建新节点替换**

```cpp
bool runTransform(Node* node, Graph& graph,
                  NodeDestroyType& destroy_current) override {
  // 创建替换节点
  Node* new_node = graph.create(kNewOp, 1);  // 1个输出
  new_node->addInput(node->inputs()[0]);
  new_node->addInput(node->inputs()[1]);
  new_node->i_(kattr_name, 42);  // 设置属性
  new_node->insertBefore(node);
  new_node->output()->setSizes(node->output()->sizes());

  // 替换使用
  tryReplacingAllUsesWith(node->output(), new_node->output());

  destroy_current = NodeDestroyType::DestroyOne;
  return true;
}
```

## 安全替换：tryReplacingAllUsesWith

Pass 基类提供两个安全替换函数：

```cpp
// 替换 oldValue 的所有使用为 newValue
bool tryReplacingAllUsesWith(Value* oldValue, Value* newValue);

// 替换 oldNode 的所有输出使用为 newNode 的对应输出
bool tryReplacingAllUsesWith(Node* oldNode, Node* newNode);
```

**保护机制**：如果 oldValue 和 newValue 同为 graph input 或同为 graph output，函数返回 false 并拒绝替换——避免破坏模型的输入输出签名。

**使用建议**：
- 始终检查返回值
- 返回 false 时设置 `destroy_current = DestroyZero`，不要销毁节点
- 不要直接调用 `oldValue->replaceAllUsesWith(newValue)`（绕过保护）

## FullGraphBasedPass 开发模板

```cpp
struct MyGlobalPass final : public FullGraphBasedPass {
  explicit MyGlobalPass()
      : FullGraphBasedPass(
            PassType::Nop,
            PassEfficiency::Complete,
            PassOptimizationType::Compute
        ) {}

  std::string getPassName() const override {
    return "my_global_pass";
  }

  std::shared_ptr<PostPassAnalysis> runPass(Graph& graph) override {
    unsigned num_changes = 0;

    // 自定义全图遍历逻辑
    // 示例：反向拓扑遍历（死代码消除模式）
    for (auto it = graph.nodes().rbegin();
         it != graph.nodes().rend(); ++it) {
      Node* n = *it;
      if (!n->hasUses()) {
        // 无输出使用的节点是死代码
        node->destroy();
        num_changes++;
      }
    }

    return std::make_shared<CountBasedPassAnalysis>(
        this, num_changes, false, false);
  }
};
```

### 子图递归

FullGraphBasedPass 中需要自行处理子图递归：

```cpp
void processGraph(Graph& g, unsigned& num_changes) {
  // 处理当前图
  for (auto* node : g.nodes()) {
    // 递归处理子图（Loop/If/Scan 的 body 属性）
    for (Block* block : node->blocks()) {
      processGraph(*block, num_changes);  // 如有必要
    }
    if (node->hasAttribute(ksubgraph)) {
      Graph& sub = node->g(ksubgraph);
      processGraph(sub, num_changes);
    }
    // ... 节点处理逻辑
  }
}
```

PredicateBasedPass 自动通过 `DescendOnGraphAttributesAndCount` 处理子图递归，无需手动处理。

## pass_util.h 工具函数库

`passes/pass_util.h` 提供了大量模板工具函数，开发 pass 时应优先使用：

| 工具 | 用途 | 示例 |
|------|------|------|
| `CheckKind<Op>(node, idx)` | 检查第 idx 个输入的前驱是否为 Op 类型 | `CheckKind<kConv>(node, 0)` |
| `IsConstantTensor(v)` | 判断值是否为常量节点或 initializer | `IsConstantTensor(node->inputs()[1])` |
| `FetchConstantTensor(v)` | 获取常量张量指针 | `const Tensor* t = FetchConstantTensor(v)` |
| `PrevNode(node, idx)` | 获取第 idx 个输入的前驱节点 | `Node* prev = PrevNode(node, 0)` |
| `GetValueFromAttr<T>(node, name)` | 类型安全读取属性（无默认值） | `float alpha = GetValueFromAttr<float>(node, kalpha)` |
| `GetValueFromAttrWithDefault<T>(node, name, def)` | 带默认值的属性读取 | `float alpha = GetValueFromAttrWithDefault(node, kalpha, 1.0f)` |
| `FetchSoleIntValueOfTensor(t)` | 获取标量张量的整数值 | `int64_t axis = FetchSoleIntValueOfTensor(t)` |
| `isABroadcastToB(a_shape, b_shape)` | 检查 a 能否广播到 b | `if (isABroadcastToB(a_sizes, b_sizes))` |
| `GetValueFromInput<T>(node, idx)` | 从常量输入读取数据 | `auto vals = GetValueFromInput<float>(node, 1)` |

> **开发规范**：新增 `.agents/scripts/` 脚本前必须先查阅 `pass_util.h`，禁止重复实现已有功能。

## Opset 版本兼容

当 pass 逻辑依赖 opset 版本时，使用 `getOpsetVersion()`：

```cpp
bool patternMatchPredicate(Node* node) override {
  auto opset = getOpsetVersion(node->owningGraph());
  if (opset >= 11) {
    // opset 11+ 的模式
    return node->kind() == kSomeOp;
  } else {
    // opset 10 及以下的模式
    return node->kind() == kSomeOpV10;
  }
}
```

`getOpsetVersion()` 遍历图的 opset_versions，查找默认 ONNX 域（空域名 ""）的版本号，默认返回 0（表示未知/最旧版本）。

## 生命周期钩子

大多数 pass 不需要覆盖 `initializePass` 和 `finalizePass`，但某些场景有用：

```cpp
bool initializePass(Graph& graph) override {
  // 遍历前初始化（如构建数据结构）
  // 返回 true 表示修改了图
  return false;
}

bool finalizePass(Graph& graph) override {
  // 所有节点遍历后收尾（如清理临时数据）
  return false;
}
```

## 注册新 Pass

开发完 pass 后，需要在 `pass_registry.h` 的 `GlobalPassRegistry` 构造函数中注册：

```cpp
// 在 pass_registry.h 的 GlobalPassRegistry 构造函数中添加：
registerPass<MyCustomPass>();
```

`registerPass<T>()` 模板会：
1. 编译期检查 T 继承自 Pass（`static_assert`）
2. 创建 `shared_ptr<T>` 实例
3. 以 `getPassName()` 返回的名称为 key 存入 map
4. 将名称追加到 pass_names 列表（决定执行顺序）

**注册顺序很重要**：pass 按注册顺序执行。新增 pass 时需要考虑其在执行序列中的位置（通常在消除类 pass 之后、split 类 pass 之前）。

## 开发注意事项

1. **不要破坏 graph input/output**：使用 `tryReplacingAllUsesWith` 而非直接 `replaceAllUsesWith`
2. **节点销毁时机**：在 PredicateBasedPass 中通过 `destroy_current` 参数控制，不要手动 `delete` 节点
3. **子图递归**：PredicateBasedPass 自动处理，FullGraphBasedPass 需要手动处理
4. **线程安全**：Pass 实例是全局单例（GlobalPassRegistry 持有），runPass/runTransform 不能修改 pass 自身的状态
5. **效率标注**：正确标注 PassEfficiency——单次幂等的标 Complete，可能需要迭代的标 Partial
6. **返回值**：runTransform 返回 true 表示执行了变换（影响 CountBasedPassAnalysis 计数）
7. **常量条件**：涉及权重修改的融合必须检查权重是否为常量（initializer），否则无法在编译时计算融合权重
8. **数值精度**：浮点融合计算注意数值精度问题（如 BN 融合中的 epsilon 处理）

## 关联概念

- [Pass 系统：基类继承体系与注册机制](01-pass-system.md) — 深入理解 Pass 类层次和元数据
- [算子融合模式](04-fusion-patterns.md) — 参考内置融合 pass 的实现模式
- [内置优化 Passes 分类详解](02-builtin-passes.md) — 查看内置 pass 的分类作为参考
- [开发自定义优化 Pass](../examples/custom-pass-dev.md) — 完整的自定义 pass 实现示例
