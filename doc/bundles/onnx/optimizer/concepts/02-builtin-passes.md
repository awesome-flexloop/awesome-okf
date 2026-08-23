---
type: concept
title: "内置优化 Passes 分类与功能"
description: "ONNX Optimizer 50 个内置优化 pass 的完整分类：算子融合、无用操作消除、结构/元数据、算子替换、图分离五大类，各 pass 的功能与适用条件"
sources:
  references: [../references/pass-base.md]
  facts: [F-033, F-036, F-045, F-046, F-047, F-048, F-049, F-050, F-051, F-052, F-053, F-059]
---

# 内置优化 Passes 分类与功能

## 核心理解

ONNX Optimizer v0.4.2 内置 50 个优化 pass，按 PassType 分为五大类。默认优化集（`get_fuse_and_elimination_passes()`）只包含 **Fuse（融合）** 和 **Nop（消除）** 两类共 38 个 pass，其余 12 个 pass 需要显式指定。理解每个 pass 的功能和限制是正确使用优化器的前提。

## Pass 分类总览

| 类别 | PassType | 数量 | 默认集? | 说明 |
|------|----------|:----:|:-------:|------|
| 算子融合 | Fuse | 17 | ✅ | 合并多个算子为等价的更少算子 |
| 无用操作消除 | Nop | 21 | ✅ | 移除恒等操作、死代码、冗余节点 |
| 算子替换 | Replace | 4 | ❌ | 将一种算子替换为另一种等价算子 |
| 图分离 | Separate | 3 | ❌ | 将图拆分为子图或改变图结构 |
| 结构/元数据 | Other/Immutable | 4+1 | ❌ | 调整结构、重命名、设置名称 |

## 一、算子融合类（Fuse，17 个，默认包含）

算子融合将多个相邻算子合并为更少的算子，减少内核启动开销和中间结果内存读写。

| Pass 名称 | 基类 | 效率 | 优化目标 | 功能说明 |
|-----------|------|:----:|:--------:|----------|
| `fuse_add_bias_into_conv` | PredicateBased | Complete | Compute | 将 Conv 后的 Add（偏置）融合进 Conv 的 bias 输入 |
| `fuse_bn_into_conv` | PredicateBased | Complete | Compute | 推理模式下将 BatchNormalization 的 scale/bias/mean/var 数学合并到 Conv 权重和偏置中 |
| `fuse_consecutive_concats` | PredicateBased | Partial | Compute | 融合相邻的 Concat 操作 |
| `fuse_consecutive_log_softmax` | PredicateBased | Complete | Compute | 将 Log+Softmax 融合为 LogSoftmax |
| `fuse_consecutive_reduce_unsqueeze` | PredicateBased | Complete | Compute | 融合 Reduce+Unsqueeze 组合 |
| `fuse_consecutive_squeezes` | PredicateBased | Complete | Compute | 融合相邻的 Squeeze 操作 |
| `fuse_consecutive_squeeze_unsqueeze` | PredicateBased | Partial | Compute | 融合 Squeeze-Unsqueeze 对 |
| `fuse_consecutive_transposes` | PredicateBased | Partial | Compute | 融合相邻的 Transpose，合并 perm 矩阵 |
| `fuse_consecutive_slices` | PredicateBased | Partial | Compute | 融合相邻的 Slice 操作 |
| `fuse_consecutive_unsqueezes` | PredicateBased | Complete | Compute | 融合相邻的 Unsqueeze 操作 |
| `fuse_matmul_add_bias_into_gemm` | PredicateBased | Complete | Compute | 将 MatMul+Add 融合为 Gemm（带 bias） |
| `fuse_mul_into_conv` | PredicateBased | Complete | Compute | 将 Conv 后的 Mul（逐通道缩放）融合进 Conv 权重 |
| `fuse_pad_into_conv` | PredicateBased | Complete | Compute | 将显式 Pad 融合进 Conv 的 auto_pad 属性 |
| `fuse_pad_into_pool` | PredicateBased | Complete | Compute | 将显式 Pad 融合进 Pool 的 auto_pad 属性 |
| `fuse_transpose_into_gemm` | PredicateBased | Complete | Compute | 将 Gemm 输入的 Transpose 融合进 Gemm 的 transA/transB 属性 |
| `fuse_concat_into_reshape` | PredicateBased | Complete | Compute | 将特定模式的 Concat 融合为 Reshape |
| `fuse_qkv` | PredicateBased | Complete | Compute | 将三个共享输入的 MatMul（Q/K/V 投影）融合为 Concat+MatMul+Split |

### 重点融合 pass 说明

**fuse_bn_into_conv**：推理模式（training_mode=0）下，当 BN 的 scale/bias/mean/var 均为常量且 Conv 权重为常量时，将 BN 的线性变换参数（缩放因子 γ/β、均值 μ、方差 σ²）数学合并到 Conv 的权重 W 和偏置 b 中：

```
原始：Conv(W, b) → BN(γ, β, μ, σ²)
融合后：Conv(W', b')
其中：
  W' = W * (γ / sqrt(σ² + ε))
  b' = (b - μ) * (γ / sqrt(σ² + ε)) + β
```

适用条件：BN 输入仅被 BN 使用、BN 只有一个输出。

**fuse_qkv**：Transformer 注意力机制中的 Q/K/V 三个投影 MatMul 共享同一输入，且权重形状相同时，将三个权重 Concat 为一个大权重执行单个 MatMul，再 Split 为 Q/K/V 三个输出：

```
原始：X → MatMul(Wq) → Q
      X → MatMul(Wk) → K    （三个独立 MatMul）
      X → MatMul(Wv) → V
融合后：X → MatMul(Concat(Wq,Wk,Wv)) → Split → Q, K, V
```

## 二、无用操作消除类（Nop，21 个，默认包含）

消除恒等操作（no-op）、死代码和冗余节点。这类 pass 安全且通常带来显著的图简化效果。

### 恒等操作消除（11 个）

| Pass 名称 | 功能说明 |
|-----------|----------|
| `eliminate_nop_cast` | 消除源类型和目标类型相同的 Cast |
| `eliminate_nop_dropout` | 消除 ratio=0 的 Dropout（直通） |
| `eliminate_nop_flatten` | 消除轴为 1 且无实际展平效果的 Flatten |
| `eliminate_nop_pad` | 消除所有 padding 为 0 的 Pad |
| `eliminate_nop_transpose` | 消除 perm 为恒等排列的 Transpose |
| `eliminate_nop_reshape` | 消除形状不变的 Reshape |
| `eliminate_nop_concat` | 消除只有一个输入的 Concat |
| `eliminate_nop_split` | 消除只有一个输出的 Split |
| `eliminate_nop_expand` | 消除形状与输入相同的 Expand |
| `eliminate_nop_monotone_argmax` | 消除单调 ArgMax 前后的冗余操作 |
| `eliminate_nop_with_unit` | 消除带单位的 nop（如乘以 1、加 0 等） |

### 恒等/冗余消除（4 个）

| Pass 名称 | 基类 | 功能说明 |
|-----------|------|----------|
| `eliminate_identity` | PredicateBased | 移除 Identity 节点，直接连接输入输出 |
| `eliminate_deadend` | FullGraphBased | 反向拓扑遍历，移除所有无输出使用的死节点 |
| `eliminate_if_with_const_cond` | PredicateBased | 常量条件 If 的内联：根据条件值选择 then/else 分支重建到父图 |
| `extract_constant_to_initializer` | PredicateBased | 将 Constant 节点转为 graph initializer（若输出不是 graph output） |

### Shape 相关消除（3 个）

| Pass 名称 | 功能说明 |
|-----------|----------|
| `eliminate_shape_op` | 消除可被静态推断的 Shape 算子 |
| `eliminate_shape_gather` | 消除 Shape+Gather 的冗余模式 |
| `eliminate_slice_after_shape` | 消除 Shape 后跟随的 Slice 冗余模式 |

### Initializer/冗余消除（3 个）

| Pass 名称 | 基类 | 功能说明 |
|-----------|------|----------|
| `eliminate_unused_initializer` | FullGraphBased | 移除未被任何节点使用的 initializer |
| `eliminate_duplicate_initializer` | FullGraphBased | 合并内容相同的重复 initializer |
| `eliminate_common_subexpression` | FullGraphBased | 公共子表达式消除（CSE）：结构等价的节点只保留第一个 |

### 重点消除 pass 说明

**eliminate_deadend**：`FullGraphBasedPass`，通过反向拓扑遍历，从图输出出发标记所有可达节点，未标记的节点即为死代码，予以移除。

**eliminate_if_with_const_cond**：匹配条件为常量的 If 节点，根据条件值选择 then_branch 或 else_branch 子图，将子图中所有节点重建到父图中（处理 captured value 和 param/initializer），然后替换 If 输出并删除 If 节点。注释明确指出"此 pass 与常量折叠配合效果最好，理想情况应被稀疏条件常量传播替代"。

**extract_constant_to_initializer**：匹配 `kConstant` 且有 `kvalue` 属性的节点，将其 value 张量提取为 graph initializer，替换所有使用后销毁原节点。若该常量输出同时是 graph output 则不替换（保持输出签名）。

**eliminate_common_subexpression**：使用自定义哈希 `CSENodeHash` 和相等比较 `CSEEqual` 构建 hash_map，遍历所有节点，对结构等价（相同算子类型、相同属性、相同输入）的节点将后续节点的输出替换为第一个节点的输出。

## 三、算子替换类（Replace，4 个，默认排除）

| Pass 名称 | 功能说明 | 为什么默认排除 |
|-----------|----------|---------------|
| `replace_einsum_with_matmul` | 将 Einsum 替换为等价的 MatMul 组合 | 改变算子类型，某些后端可能优先支持 Einsum |
| `rewrite_input_dtype` | 重写输入数据类型 | 改变模型输入类型签名 |
| `rewrite_where` | 重写 Where 算子模式 | 可能改变执行方式 |
| `adjust_slice_and_matmul` | 调整 Slice 和 MatMul 的顺序 | 可能改变中间结果形状 |

## 四、图分离类（Separate，3 个，默认排除）

| Pass 名称 | 基类 | 功能说明 | 注意事项 |
|-----------|------|----------|----------|
| `split_init` | FullGraphBased | 提取 init 子图（常量计算部分，可预执行），删除 predict 节点和输入 | 改变图结构，只保留初始化部分 |
| `split_predict` | FullGraphBased | 提取 predict 子图（推理时执行部分），删除 init 节点和所有 initializer | 改变图结构，需要配合 split_init 使用 |
| `lift_lexical_references` | FullGraphBased | 将子图中引用外层作用域的值显式提升为控制算子的 `__control_inputs` | **产出不符合 ONNX 规范**，用于框架并行调度 |

### split_init / split_predict 机制

基于不纯算子列表（RandomNormal/RandomNormalLike/RandomUniform/RandomUniformLike/Loop/If/Scan）和输入/initializer 区分：
- **init 网**：只依赖 initializer 和常量输入的计算，可在部署时预执行
- **predict 网**：依赖实际输入的推理计算

`split_init` 删除 predict 节点和输入，`split_predict` 删除 init 节点和所有 initializer。这两个 pass **必须在其他 pass 之后执行**（在 PassManager 中排在最后）。

### lift_lexical_references 机制

使用环境栈（Environment 链表）递归遍历图和子图（Loop/If），将子图中隐式引用外层作用域的值显式添加为控制算子的 `__control_inputs` 属性（string 列表）。这暴露了控制块内的数据依赖，支持框架并行调度，但产出的图不符合 ONNX 规范。

## 五、结构/元数据类（Other/Immutable，4+1 个，默认排除）

| Pass 名称 | PassType | 基类 | 功能说明 |
|-----------|----------|------|----------|
| `adjust_add` | Immutable | PredicateBased | 调整 Add 输入顺序，使常量在右侧（便于后续融合） |
| `rename_input_output` | Other | FullGraphBased | 按环境变量模式重命名输入输出 |
| `set_unique_name_for_nodes` | Other | - | 为无名节点设置唯一名称 |
| `nop` | Other | FullGraphBased | 空 pass（无操作，用于测试） |

### rename_input_output

从环境变量读取命名模式：
- `OPTIMIZER_RENAME_INPUT_PATTERN`：默认 `input_%d`
- `OPTIMIZER_RENAME_OUTPUT_PATTERN`：默认 `output_%d`

按索引重命名图的输入和输出，跳过同时是 initializer 的输入（避免破坏 initializer 引用）。

## Pass 执行顺序要点

1. **结构调整先于融合消除**：`adjust_add` 应先执行（确保常量位置正确，便于后续融合）
2. **提取常量先于消除**：`extract_constant_to_initializer` 应在死代码消除前执行
3. **消除先于融合**：先移除 nop 和死代码，再做融合（避免对死代码做无效融合）
4. **split 必须最后**：`split_init`/`split_predict` 改变图结构，必须在所有其他优化之后
5. **rename 最后**：`rename_input_output` 改变名称，应在所有结构变换之后

## 关联概念

- [Pass 系统：基类继承体系与注册机制](01-pass-system.md) — 了解 pass 的基类和注册机制
- [PassManager 执行模型与定点收敛](03-pass-execution.md) — 了解 pass 的执行顺序和收敛机制
- [算子融合模式](04-fusion-patterns.md) — 深入理解 Fuse 类 pass 的数学原理
- [Python/CLI/C API 使用指南](05-python-cli-api.md) — 了解如何指定 pass 列表
