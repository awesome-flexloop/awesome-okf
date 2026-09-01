---
type: reference
title: "PassManager 执行引擎与 Optimizer 入口类"
description: "PassManager 抽象基类、GeneralPassManager 线性执行、FixedPointPassManager 定点迭代、Optimizer C++ 入口类的源码信源登记"
sources:
  - path: "external/libs/models/onnx/optimizer/onnxoptimizer/pass_manager.h"
    facts: [F-037, F-038]
  - path: "external/libs/models/onnx/optimizer/onnxoptimizer/pass_manager.cc"
    facts: [F-038, F-039]
  - path: "external/libs/models/onnx/optimizer/onnxoptimizer/optimize.h"
    facts: [F-040, F-042, F-043, F-044]
  - path: "external/libs/models/onnx/optimizer/onnxoptimizer/optimize.cc"
    facts: [F-041, F-044]
---

# PassManager 执行引擎与 Optimizer 入口类

## 信源概述

| 信源 | 类型 | 职责 |
|------|------|------|
| `onnxoptimizer/pass_manager.h` | 头文件 | PassManager/GeneralPassManager 类声明 |
| `onnxoptimizer/pass_manager.cc` | 实现文件 | 线性执行和定点迭代算法实现 |
| `onnxoptimizer/optimize.h` | 头文件 | Optimizer 入口类声明、自由函数 API |
| `onnxoptimizer/optimize.cc` | 实现文件 | Optimizer 构造与 optimize() 实现、自由函数封装 |

## F-037：PassManager 抽象基类

`PassManager` 是 pass 执行引擎的抽象基类：

```cpp
class PassManager {
public:
  virtual ~PassManager() = default;
  virtual void add(std::shared_ptr<Pass> pass) = 0;
  virtual std::shared_ptr<PostPassAnalysis> run(Graph& graph) = 0;
};
```

两个纯虚接口：
- `add()`：添加一个 pass 到执行队列
- `run()`：对给定 Graph 执行所有已添加的 pass

## F-038：GeneralPassManager——线性执行器

`GeneralPassManager` 继承 `PassManager`，实现按添加顺序线性执行：

```cpp
class GeneralPassManager : public PassManager {
public:
  void add(std::shared_ptr<Pass> pass) override;
  std::shared_ptr<PostPassAnalysis> run(Graph& graph) override;
protected:
  std::vector<std::shared_ptr<Pass>> passes;
};
```

### 执行流程

```
run(graph):
  for each pass in passes:
    pass->runPass(graph)
```

> ⚠️ **顺序敏感**：源码注释明确指出"对某些 pass 顺序很关键，例如 split_init 和 split_predict 应在列表最后"。pass 的执行顺序与 `GlobalPassRegistry` 中的注册顺序一致。

## F-039：FixedPointPassManager——定点迭代器

`FixedPointPassManager` 继承 `GeneralPassManager`，重写 `run()` 实现定点收敛：

```
run(graph):
  do {
    graph_changed = false
    for each pass in passes:
      analysis = pass->runPass(graph)
      if analysis->fixedPointOptimizationNeeded():
        // Partial 效率的 pass：反复执行直到不再产生变换
        do {
          analysis = pass->runPass(graph)
        } while (analysis->fixedPointOptimizationNeeded())
        graph_changed = true
      else if analysis->graphChanged():
        graph_changed = true
  } while (graph_changed)
```

### 定点迭代算法详解

定点迭代分为两层循环：

1. **外层循环**：遍历所有 pass，只要任意一轮有 pass 产生了图变换就继续
2. **内层循环**：对 Partial 效率的 pass，反复执行直到该 pass 单次执行不再产生变换

`fixedPointOptimizationNeeded()` 返回 true 的条件是：
- `graphChanged()` 为 true（本次执行有变换）**且**
- pass 的效率为 `PassEfficiency::Partial`（连续两次执行不等价）

Complete 效率的 pass 即使产生变换也不需要内层迭代（单次即收敛），但可能触发外层循环的下一轮（因为前序 pass 产生的变换可能让当前 pass 有新的匹配机会）。

## F-040~F-043：Optimizer——C++ 优化入口类

### F-040：类结构

```cpp
struct Optimizer {
  static GlobalPassRegistry passes;  // 全局唯一注册表（静态成员）
  std::shared_ptr<PassManager> pass_manager;

  Optimizer(const std::vector<std::string>& pass_names, bool fixed_point);
  ModelProto optimize(const ModelProto& _mp_in);
};
```

### F-041：构造函数

```
Optimizer(names, fixed_point):
  if fixed_point:
    pass_manager = make_shared<FixedPointPassManager>()
  else:
    pass_manager = make_shared<GeneralPassManager>()
  for name in names:
    pass_manager->add(passes.find(name))
```

按 pass 名称从全局注册表查找并添加到 PassManager。若名称不存在，`find()` 会触发断言失败。

### F-042：optimize() 完整流程

```
optimize(_mp_in):
  1. IR 版本检查与升级
     - 若 mp_in.ir_version() == 3: 升级到 IR v4（使 initializer 不必在 input 中）
  2. ImportModelProto(mp_in) → Graph* g
     - 将 protobuf 表示转换为内存 Graph 对象
  3. 若 g == nullptr（IR 版本过旧无法解析）:
     - 输出警告
     - 返回原始模型 _mp_in
  4. pass_manager->run(*g)
     - 执行所有已注册的优化 pass
  5. PrepareOutput() + ExportModelProto()
     - 将内存 Graph 转回 ModelProto
  6. AddFunctionsToModel()
     - 复制原始模型的 functions 到输出
  7. 返回优化后的 ModelProto
```

### F-043：IR 版本兼容性

当输入模型 IR 版本为 3 时，optimizer 静默升级到 v4。IR v4 的关键变化是 initializer 不必同时出现在 graph input 列表中。若 `ImportModelProto()` 返回 nullptr（IR 版本过旧无法解析），输出警告并返回原始模型。

## F-044：C++ 自由函数 API

在 `optimize.h` 中提供四个便捷自由函数，封装 Optimizer 类的使用：

```cpp
// 单次遍历优化（使用 GeneralPassManager）
ModelProto Optimize(
    const ModelProto& mp_in,
    const std::vector<std::string>& names);

// 定点迭代优化（使用 FixedPointPassManager）
ModelProto OptimizeFixed(
    const ModelProto& mp_in,
    const std::vector<std::string>& names);

// 获取所有已注册 pass 名称
const std::vector<std::string> GetAvailablePasses();

// 获取默认优化集（Fuse + Nop 类型）
const std::vector<std::string> GetFuseAndEliminationPass();
```

`Optimize()` 和 `OptimizeFixed()` 的实现分别创建 `Optimizer(names, false)` 和 `Optimizer(names, true)`，然后调用 `optimizer.optimize(mp_in)`。
