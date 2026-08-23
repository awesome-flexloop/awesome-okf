---
type: concept
title: "PassManager 执行模型与定点收敛"
description: "GeneralPassManager 线性执行、FixedPointPassManager 定点迭代算法、全局 pass vs 局部 pass 的执行差异、pass 排序策略、Optimizer 入口的完整优化流程"
sources:
  references: [../references/pass-base.md, ../references/pass-manager.md]
  facts: [F-018, F-025, F-026, F-030, F-037, F-038, F-039, F-040, F-041, F-042, F-043, F-044]
---

# PassManager 执行模型与定点收敛

## 核心理解

PassManager 是 pass 执行的调度引擎，决定了多个 pass 以何种顺序、何种策略执行。ONNX Optimizer 提供两种执行模式：**线性单次执行**（GeneralPassManager）和**定点迭代执行**（FixedPointPassManager）。理解这两种模式的差异以及 pass 效率（Partial/Complete）与定点收敛的关系，是正确选择优化策略的关键。

## 两种 PassManager

```
PassManager（抽象基类）
├── GeneralPassManager（线性执行器）
│   └── 按添加顺序线性执行每个 pass 一次
└── FixedPointPassManager（定点迭代器）
    └── 外层循环：反复执行所有 pass 直到无变换
        └── 内层循环：对 Partial pass 反复执行直到收敛
```

## GeneralPassManager：线性执行

GeneralPassManager 是默认的执行引擎，按 pass 添加顺序**线性执行一遍**：

```
run(graph):
  for each pass in passes（按添加顺序）:
    analysis = pass->runPass(graph)
    // 不检查 analysis，继续下一个 pass
```

**特点**：
- 每个 pass 只执行一次
- 执行顺序与 `GlobalPassRegistry` 注册顺序一致（或按用户指定的顺序）
- 适用于 Complete 效率的 pass 集合（单次执行即收敛）
- 执行速度快，但可能遗漏 pass 间交互产生的新优化机会

### 顺序敏感性

源码注释明确指出：

> *"对某些 pass 顺序很关键，例如 split_init 和 split_predict 应在列表最后。"*

为什么顺序重要？举例说明：

1. **extract_constant_to_initializer → eliminate_deadend**：先提取常量，再消除死代码（提取后原 Constant 节点变为死代码）
2. **eliminate_nop → fuse_xxx**：先移除恒等操作，再做融合（nop 可能阻断融合模式匹配）
3. **fuse_consecutive_transposes（Partial）→ 其他 pass**：融合 Transpose 可能为其他融合创造机会，但单次执行可能不够
4. **所有其他 pass → split_init/split_predict**：split 会拆图，必须最后执行

## FixedPointPassManager：定点迭代

FixedPointPassManager 继承 GeneralPassManager，重写 `run()` 实现定点收敛：

```
run(graph):
  do {
    graph_changed_overall = false

    for each pass in passes:
      analysis = pass->runPass(graph)

      if analysis->fixedPointOptimizationNeeded():
        // Partial 效率的 pass：内层循环反复执行
        do {
          analysis = pass->runPass(graph)
        } while (analysis->fixedPointOptimizationNeeded())
        graph_changed_overall = true

      else if analysis->graphChanged():
        // Complete 效率的 pass 有变换，标记外层需要继续
        graph_changed_overall = true

  } while (graph_changed_overall)
```

### 双层循环结构

定点迭代分为两层：

**内层循环（pass 内收敛）**：
- 触发条件：单个 pass 执行后 `fixedPointOptimizationNeeded()` 返回 true
- 含义：本次有变换 **且** pass 效率为 Partial（非幂等）
- 行为：反复执行同一个 pass 直到单次执行不再产生变换
- 目的：确保单个 Partial pass 达到自身的定点（如连续融合所有可融合的 Transpose）

**外层循环（pass 间收敛）**：
- 触发条件：任一轮中有任何 pass 产生了变换
- 含义：前序 pass 的变换可能为后序 pass 创造新的匹配机会
- 行为：重新从头执行所有 pass
- 目的：确保 pass 间交互也达到定点（如消除 nop 后新的融合机会出现）

### fixedPointOptimizationNeeded 的判定

```cpp
// CountBasedPassAnalysis 中的逻辑
bool fixedPointOptimizationNeeded() const {
  return num_positive_transforms > 0      // 本次执行有变换
      && pass->getPassEfficiency() == Partial;  // 且 pass 非幂等
}
```

| 条件组合 | 行为 |
|----------|------|
| 有变换 + Partial | 内层循环继续执行该 pass |
| 有变换 + Complete | 不做内层循环，但标记外层继续 |
| 无变换 + Partial | 该 pass 已收敛，继续下一个 |
| 无变换 + Complete | 该 pass 无变化，继续下一个 |

### 为什么需要定点迭代？

单次线性执行不够的典型场景：

**场景1：连续 Transpose 融合**

```
T1(perm=[1,0]) → T2(perm=[1,0]) → T3(perm=[1,0])
```

- 第一次执行 `fuse_consecutive_transposes`（Partial）：融合 T1+T2 → 产生 T12(perm=[0,1]，恒等)
- T12 是 nop，但还没到 eliminate_nop_transpose
- 第二次迭代：eliminate_nop_transpose 消除 T12 → T3 可能与前后的 Transpose 形成新的融合机会
- 外层循环继续，直到没有新变换

**场景2：Pass 间交互**

```
Constant → Add → Conv → BN → Relu
```

- `extract_constant_to_initializer` 将 Constant 提取为 initializer
- `fuse_bn_into_conv` 融合 BN 到 Conv
- 融合后 Conv 权重改变，可能使 `fuse_add_bias_into_conv` 的模式匹配条件满足
- 需要外层循环重新执行 fuse_add_bias_into_conv

### 收敛性保证

定点迭代为什么会终止？因为每次变换都在**减少**图中的某种度量：
- 节点数量（消除、融合减少节点）
- 边数量（消除减少边）
- 特定模式数量（每次融合减少一个可融合模式）

这些度量都是非负整数，单调递减，因此迭代必然在有限步内终止。但注意：如果 pass 实现有 bug（如变换后创建了新的匹配节点），理论上可能不收敛。

## 全局 pass vs 局部 pass 的执行差异

### 局部 pass（PredicateBasedPass）

```
按拓扑序遍历每个节点：
  → 递归处理子图
  → patternMatchPredicate（看当前节点）
  → runTransform（只修改当前节点和局部连接）
```

- 决策范围：单节点
- 遍历方式：框架自动拓扑遍历
- 销毁控制：通过 destroy_current 参数

### 全局 pass（FullGraphBasedPass）

```
runPass(Graph& graph):
  → 自定义全图遍历逻辑
  → 自定义分析和变换
  → 返回 CountBasedPassAnalysis
```

- 决策范围：全图
- 遍历方式：子类自己实现（可能是多次遍历、反向遍历等）
- 销毁控制：子类自行管理节点迭代器

典型例子：
- `eliminate_deadend`：反向拓扑遍历（从输出标记可达性）
- `eliminate_common_subexpression`：构建全局哈希表
- `split_init/split_predict`：全图分析不纯算子依赖

## Optimizer 入口的完整流程

```
Optimizer(names, fixed_point):
  if fixed_point:
    pass_manager = FixedPointPassManager
  else:
    pass_manager = GeneralPassManager
  for name in names:
    pass_manager.add(GlobalPassRegistry.find(name))

optimize(mp_in):
  ┌─ IR 版本处理
  │  if mp_in.ir_version() == 3:
  │    升级到 IR v4（initializer 不必在 input 中）
  │
  ├─ Proto → Graph
  │  g = ImportModelProto(mp_in)
  │  if g == nullptr:  // IR 过旧
  │    输出警告，返回原始模型
  │
  ├─ 执行优化
  │  pass_manager->run(*g)
  │
  ├─ Graph → Proto
  │  PrepareOutput()       // 优化后清理
  │  mp_out = ExportModelProto()
  │
  └─ 补充 functions
     AddFunctionsToModel(mp_in, mp_out)  // 复制原始模型的 functions
     return mp_out
```

## Pass 效率选择指南

开发自定义 pass 时如何选择 PassEfficiency？

| 场景 | 选择 | 原因 |
|------|------|------|
| 单次遍历即可完成所有匹配的变换 | Complete | 幂等，不需要内层循环 |
| 变换后可能在同一位置产生新的匹配 | Partial | 需要内层迭代到定点 |
| 消除恒等操作（nop） | Complete | 单次消除后不会在同一位置重现 |
| 融合连续相同算子 | Partial | 融合后可能产生新的连续对 |
| 全局分析（CSE、死代码消除） | Complete | 一次全图分析即可标记所有冗余 |

## 何时使用 fixed_point 模式？

| 场景 | 建议 |
|------|------|
| 使用默认 fuse+elimination passes | 可不用（Complete pass 为主，少数 Partial pass 单次效果可能不够但通常可接受） |
| 自定义 pass 列表包含 Partial pass | 建议使用 fixed_point=True |
| 追求最大优化效果 | 建议使用 fixed_point=True（代价是更多迭代） |
| 调试/快速验证 | 不用 fixed_point（更快） |
| 部署生产环境 | 建议使用 fixed_point=True |

## 关联概念

- [Pass 系统：基类继承体系与注册机制](01-pass-system.md) — 了解 PredicateBasedPass 和 FullGraphBasedPass 的区别
- [内置优化 Passes 分类详解](02-builtin-passes.md) — 了解各 pass 的效率类型
- [算子融合模式](04-fusion-patterns.md) — 了解融合类 pass 为何有些是 Partial
- [自定义 Pass 开发方法](06-custom-pass.md) — 开发自定义 pass 时如何选择效率类型
