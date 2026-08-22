---
type: example
title: "开发自定义优化 Pass"
description: "从零开始开发一个 ONNX Optimizer 自定义优化 pass 的完整示例，包括 PredicateBasedPass 实现、pass_util 工具使用、安全替换、注册编译流程"
sources:
  concepts: [../concepts/01-pass-system.md, ../concepts/03-pass-execution.md, ../concepts/06-custom-pass.md]
  references: [../references/pass-base.md]
---

# 开发自定义优化 Pass

## 目标

开发一个自定义 ONNX Optimizer pass，学习从需求分析、基类选择、模式匹配、变换实现到注册编译的完整流程。本示例实现两个 pass：一个消除 Relu(Relu(x)) 的简单融合 pass（PredicateBasedPass），以及一个统计图中各算子数量的分析 pass（FullGraphBasedPass）。

## 前置知识

- [Pass 系统：基类继承体系与注册机制](../concepts/01-pass-system.md)
- [自定义 Pass 开发方法](../concepts/06-custom-pass.md)

## 示例1：消除 Relu(Relu(x)) 双重激活

### 需求分析

ONNX 模型中有时会出现连续两个 Relu 激活函数的情况（如模型转换或其他优化产生）。由于 `Relu(Relu(x)) = Relu(x)`（Relu 是幂等的），可以安全地消除第二个 Relu。

变换模式：
```
X → Relu → Relu → Y
```
变换为：
```
X → Relu → Y
```

**基类选择**：逐节点匹配，选择 PredicateBasedPass。
**PassType**：Nop（消除冗余操作）。
**PassEfficiency**：Complete（单次遍历即可，消除后同一位置不会重现双重 Relu）。
**PassOptimizationType**：Compute。

### 完整实现

```cpp
#pragma once
#include "onnxoptimizer/pass.h"
#include "onnxoptimizer/passes/pass_util.h"

namespace ONNX_NAMESPACE {
namespace optimization {

struct EliminateDuplicateRelu final : public PredicateBasedPass {
  explicit EliminateDuplicateRelu()
      : PredicateBasedPass(
            PassType::Nop,
            PassEfficiency::Complete,
            PassOptimizationType::Compute) {}

  std::string getPassName() const override {
    return "eliminate_duplicate_relu";
  }

  bool patternMatchPredicate(Node* node) override {
    // 匹配条件：
    // 1. 当前节点是 Relu
    // 2. 当前节点的唯一输入也来自 Relu（前驱是 Relu）
    // 3. 前驱 Relu 的输出只被当前 Relu 使用（独占）
    if (node->kind() != kRelu) {
      return false;
    }
    // 检查输入是否来自 Relu
    if (node->inputs().size() != 1) {
      return false;
    }
    Node* prev_relu = PrevNode(node, 0);
    if (prev_relu == nullptr || prev_relu->kind() != kRelu) {
      return false;
    }
    // 检查前驱 Relu 的输出只被当前节点使用（独占使用才能安全移除）
    if (prev_relu->output()->uses().size() != 1) {
      return false;
    }
    return true;
  }

  bool runTransform(Node* node, Graph& graph,
                    NodeDestroyType& destroy_current) override {
    // node 是第二个 Relu（要消除的那个）
    // prev_relu 是第一个 Relu（保留的那个）
    Node* prev_relu = PrevNode(node, 0);
    Value* relu_out = prev_relu->output();
    Value* node_out = node->output();

    // 传递形状信息（如果有的话）
    if (node_out->has_sizes()) {
      relu_out->setSizes(node_out->sizes());
    }
    if (node_out->has_same_sizes()) {
      relu_out->setSameSizes(node_out->same_sizes());
    }

    // 将第二个 Relu 的所有输出使用替换为第一个 Relu 的输出
    // 使用 tryReplacingAllUsesWith 保护 graph input/output
    if (!tryReplacingAllUsesWith(node_out, relu_out)) {
      // 替换失败（输出是 graph output），不销毁
      destroy_current = NodeDestroyType::DestroyZero;
      return false;
    }

    // 销毁第二个 Relu 节点
    destroy_current = NodeDestroyType::DestroyOne;
    return true;
  }
};

} // namespace optimization
} // namespace ONNX_NAMES
```

### 注册 Pass

在 `onnxoptimizer/pass_registry.h` 的 `GlobalPassRegistry` 构造函数中添加注册：

```cpp
// 在其他 registerPass 调用后添加
registerPass<EliminateDuplicateRelu>();
```

注意注册顺序：建议在 Nop 消除类 pass 附近注册（与其他 eliminate_nop_xxx 放在一起）。

### 使用自定义 Pass

```python
import onnx
import onnxoptimizer

model = onnx.load("model_with_dup_relu.onnx")

# 方法1：如果已编译进库，直接指定名称
optimized = onnxoptimizer.optimize(
    model, passes=["eliminate_duplicate_relu"]
)

# 方法2：与默认 passes 组合使用
default = onnxoptimizer.get_fuse_and_elimination_passes()
all_passes = default + ["eliminate_duplicate_relu"]
optimized = onnxoptimizer.optimize(model, passes=all_passes, fixed_point=True)
```

## 示例2：常量输入 Add 消除

### 需求分析

消除 `Add(x, 0)` 模式——加零是恒等操作。

```
X → Add(0) → Y
```
变换为：
```
X → Y
```

### 完整实现

```cpp
#pragma once
#include "onnxoptimizer/pass.h"
#include "onnxoptimizer/passes/pass_util.h"

namespace ONNX_NAMESPACE {
namespace optimization {

struct EliminateAddZero final : public PredicateBasedPass {
  explicit EliminateAddZero()
      : PredicateBasedPass(
            PassType::Nop,
            PassEfficiency::Complete,
            PassOptimizationType::Compute) {}

  std::string getPassName() const override {
    return "eliminate_add_zero";
  }

  bool patternMatchPredicate(Node* node) override {
    if (node->kind() != kAdd) {
      return false;
    }
    // 检查任一输入是否为常量零
    for (size_t i = 0; i < node->inputs().size(); ++i) {
      Value* input = node->inputs()[i];
      if (IsConstantTensor(input)) {
        const Tensor* t = FetchConstantTensor(input);
        if (t && t->sizes().size() <= 1) {  // 标量或1D
          // 检查是否全零
          if (t->is_raw_data()) {
            // 对于原始数据，检查是否全零字节
            auto data = t->raw();
            bool all_zero = true;
            for (size_t j = 0; j < data.size(); ++j) {
              if (data[j] != 0) { all_zero = false; break; }
            }
            if (all_zero) return true;
          }
        }
      }
    }
    return false;
  }

  bool runTransform(Node* node, Graph& graph,
                    NodeDestroyType& destroy_current) override {
    // 找到零输入的位置，另一个输入就是实际数据
    Value* data_input = nullptr;
    for (size_t i = 0; i < node->inputs().size(); ++i) {
      Value* input = node->inputs()[i];
      if (!IsConstantTensor(input)) {
        data_input = input;
        break;
      }
      // 如果两个都是常量（包括零），保留另一个
      const Tensor* t = FetchConstantTensor(input);
      if (t) {
        auto data = t->raw();
        bool all_zero = true;
        for (size_t j = 0; j < data.size(); ++j) {
          if (data[j] != 0) { all_zero = false; break; }
        }
        if (!all_zero) {
          data_input = input;
          break;
        }
      }
    }

    if (data_input == nullptr) {
      destroy_current = NodeDestroyType::DestroyZero;
      return false;
    }

    // 传递形状信息
    if (node->output()->has_sizes()) {
      data_input->setSizes(node->output()->sizes());
    }

    // 替换输出
    if (!tryReplacingAllUsesWith(node->output(), data_input)) {
      destroy_current = NodeDestroyType::DestroyZero;
      return false;
    }

    destroy_current = NodeDestroyType::DestroyOne;
    return true;
  }
};

} // namespace optimization
} // namespace ONNX_NAMES
```

## 示例3：全图分析 Pass——算子统计

### 需求分析

一个分析类 pass，统计图中各类算子的数量（不修改图，仅用于调试/分析）。

**基类选择**：需要遍历全图统计，选择 FullGraphBasedPass。

### 完整实现

```cpp
#pragma once
#include "onnxoptimizer/pass.h"
#include <map>
#include <iostream>

namespace ONNX_NAMESPACE {
namespace optimization {

struct CountOperatorsPass final : public FullGraphBasedPass {
  explicit CountOperatorsPass()
      : FullGraphBasedPass(
            PassType::Other,
            PassEfficiency::Complete,
            PassOptimizationType::None) {}

  std::string getPassName() const override {
    return "count_operators";
  }

  std::shared_ptr<PostPassAnalysis> runPass(Graph& graph) override {
    std::map<std::string, int> op_counts;

    for (auto it = graph.begin(); it != graph.end(); ++it) {
      Node* node = *it;
      std::string op_name = node->kind().toString();
      op_counts[op_name]++;
    }

    // 也统计子图中的算子
    for (auto it = graph.begin(); it != graph.end(); ++it) {
      for (Block* block : it->blocks()) {
        countOpsInBlock(*block, op_counts);
      }
    }

    // 打印统计结果
    std::cout << "\n=== Operator Count (Pass: count_operators) ==="
              << std::endl;
    int total = 0;
    for (const auto& [op, count] : op_counts) {
      std::cout << "  " << op << ": " << count << std::endl;
      total += count;
    }
    std::cout << "  Total: " << total << " nodes\n" << std::endl;

    // 不修改图，变换计数为 0
    return std::make_shared<CountBasedPassAnalysis>(
        this, 0, false, false);
  }

private:
  void countOpsInBlock(Block& block,
                       std::map<std::string, int>& counts) {
    for (auto* node : block.nodes()) {
      std::string op_name = node->kind().toString();
      counts[op_name]++;
      for (Block* sub : node->blocks()) {
        countOpsInBlock(*sub, counts);
      }
    }
  }
};

} // namespace optimization
} // namespace ONNX_NAMESPACE
```

> 注：此 pass 用于调试目的，不修改图结构。在实际生产中，分析 pass 应该将结果通过 `PostPassAnalysis` 返回而非直接打印。

## 编译与集成

### 1. 文件放置

将自定义 pass 头文件放在 onnxoptimizer 源码目录中：

```
onnxoptimizer/
├── passes/
│   ├── eliminate_duplicate_relu.h    ← 新增
│   ├── eliminate_add_zero.h          ← 新增
│   ├── count_operators.h             ← 新增
│   └── ... (原有 passes)
├── pass_registry.h                   ← 修改，添加注册
└── ...
```

### 2. 注册

在 `pass_registry.h` 的 `GlobalPassRegistry` 构造函数中添加：

```cpp
registerPass<EliminateDuplicateRelu>();
registerPass<EliminateAddZero>();
registerPass<CountOperatorsPass>();
```

### 3. 编译

按照 onnxoptimizer 的编译流程重新编译：

```bash
# 使用 setup.py 编译
cd external/libs/models/onnx/optimizer
pip install -e .

# 或使用 cmake
mkdir build && cd build
cmake ..
make -j$(nproc)
```

### 4. 验证

```python
import onnxoptimizer

# 确认新 pass 已注册
all_passes = onnxoptimizer.get_available_passes()
assert "eliminate_duplicate_relu" in all_passes
assert "eliminate_add_zero" in all_passes
assert "count_operators" in all_passes
print("自定义 pass 注册成功！")
```

## 开发要点总结

### 常见错误与陷阱

| 错误 | 原因 | 正确做法 |
|------|------|----------|
| 直接 `node->output()->replaceAllUsesWith()` | 可能破坏 graph output 名称 | 使用 `tryReplacingAllUsesWith()` 并检查返回值 |
| PredicateBasedPass 中手动遍历子图 | 框架已自动通过 DescendOnGraphAttributesAndCount 处理 | 只关注当前节点，子图递归由框架完成 |
| Pass 中修改成员变量 | Pass 实例是全局单例，多线程不安全 | 使用局部变量或 Graph 临时存储 |
| 忘记检查独占使用 | 前驱节点输出被多个消费者使用时不能移除 | 检查 `value->uses().size() == 1` |
| Partial/Complete 标注错误 | 导致定点迭代行为异常 | 单次幂等标 Complete，可能继续产生变换标 Partial |
| 不处理形状信息传递 | 优化后形状信息丢失 | 在替换前传递 sizes() 和 same_sizes() |

### 调试技巧

1. **先写 patternMatchPredicate 测试**：确保能匹配到目标模式
2. **小模型验证**：用包含目标模式的最小 ONNX 模型测试
3. **check_model 验证**：优化后始终调用 `onnx.checker.check_model()`
4. **数值对比**：用随机输入对比优化前后输出是否一致
5. **CountOperatorsPass 分析**：先用统计 pass 了解图中算子分布

### 测试模板

```python
import onnx
import numpy as np
import onnxoptimizer
from onnx import helper, TensorProto

def test_eliminate_duplicate_relu():
    # 创建包含双重 Relu 的测试模型
    X = helper.make_tensor_value_info("X", TensorProto.FLOAT, [1, 3, 224, 224])
    Y = helper.make_tensor_value_info("Y", TensorProto.FLOAT, [1, 3, 224, 224])

    relu1 = helper.make_node("Relu", ["X"], ["X_relu1"])
    relu2 = helper.make_node("Relu", ["X_relu1"], ["Y"])

    graph = helper.make_graph([relu1, relu2], "dup_relu_test", [X], [Y])
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 13)])

    print(f"Before: {len(model.graph.node)} nodes")
    assert len(model.graph.node) == 2

    # 优化
    optimized = onnxoptimizer.optimize(model, passes=["eliminate_duplicate_relu"])
    print(f"After: {len(optimized.graph.node)} nodes")
    assert len(optimized.graph.node) == 1
    assert optimized.graph.node[0].op_type == "Relu"

    # 校验
    onnx.checker.check_model(optimized)
    print("测试通过！")

test_eliminate_duplicate_relu()
```

## 延伸阅读

- [Pass 系统：基类继承体系与注册机制](../concepts/01-pass-system.md) — 深入理解 Pass 类层次
- [内置优化 Passes 分类详解](../concepts/02-builtin-passes.md) — 参考内置 pass 作为实现范例
- [算子融合模式](../concepts/04-fusion-patterns.md) — 了解融合 pass 的数学原理
- [PassManager 执行模型](../concepts/03-pass-execution.md) — 理解定点迭代机制
