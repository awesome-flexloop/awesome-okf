---
type: concept
title: "装饰器驱动的版本化算子注册表"
description: "@tf_op 装饰器的工作原理：version_N 方法约定、_OPSETS 三维索引、create_mapping 版本堆叠算法，以及新增 opset 支持为何是纯增量操作"
sources:
  references: [../references/opset-mapping.md]
  facts: [F-015, F-016, F-017, F-018, F-019, F-020, F-043]
  insights: [I-001]
---

# 装饰器驱动的版本化算子注册表

## 核心理解

tf2onnx 支持多个 ONNX opset 版本（6-18），但转换代码中**几乎看不到** `if opset >= N` 这样的条件判断。这归功于 `@tf_op` 装饰器构建的版本化算子注册表——多版本兼容不是通过运行时条件分支实现的，而是通过注册表的版本堆叠机制在初始化时一次性完成的。

**核心洞察**：版本选择是**注册表查询问题**，不是条件分支问题。

## @tf_op 装饰器工作原理

### 装饰器语法

`@tf_op` 是一个类装饰器，用于将处理类注册到算子注册表：

```python
@tf_op(op_name_or_names, domain="", **kwargs)
class HandlerClass:
    @classmethod
    def version_N(cls, ctx, node, **kwargs):
        """opset N 版本的处理逻辑"""
        ...
```

**参数说明**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `op_name_or_names` | str 或 list | TF 算子名，支持单个或多个算子共享同一处理类 |
| `domain` | str | ONNX domain，默认空字符串（ONNX 主域） |
| `onnx_op` | str (kwarg) | 将 TF 算子名映射为不同的 ONNX 算子名 |
| `tf_op` | str (kwarg) | TFLite 路径传递原始 TF 算子名 |

### 最简单的处理器：DirectOp 模式

对于 TF 和 ONNX 完全同名同语义的算子（如 Abs、Relu、Exp），处理器只需要空实现：

```python
@tf_op("Abs")
class Abs:
    @classmethod
    def version_6(cls, ctx, node, **kwargs):
        pass  # 什么都不做，TF Abs == ONNX Abs
```

这表示 Abs 算子从 opset 6 开始支持，映射时直接保留类型名即可。DirectOp 模式的算子在 onnx_opset/math.py 中大量存在。

### 多版本处理器示例：BroadcastOp

广播运算（Add/Sub/Mul/Div 等）在不同 opset 版本中语义不同：

```python
@tf_op("Add", "Sub", "Mul")
class BroadcastOp:
    @classmethod
    def version_1(cls, ctx, node, **kwargs):
        """opset 1-5：需要设置 broadcast 属性"""
        bcast = cls._need_broadcast(ctx, node)
        if bcast:
            node.set_attr("broadcast", 1)
            cls._insert_broadcast_op(ctx, node)

    @classmethod
    def version_6(cls, ctx, node, **kwargs):
        """opset 6+：原生支持 multi-directional broadcast，不需要特殊处理"""
        pass  # opset 6+ Add/Sub/Mul 自动广播，只需确保形状正确

    @classmethod
    def version_7(cls, ctx, node, **kwargs):
        """opset 7+：可能需要额外处理（如有新语义变化）"""
        cls.version_6(ctx, node, **kwargs)
```

**关键**：每个 `version_N` 方法只关注该 opset 版本引入的语义变化，不需要知道其他版本的存在。

### 算子重命名：onnx_op kwargs

当 TF 算子名与 ONNX 算子名不同时，通过 `onnx_op` 指定映射名：

```python
# TF 中的 RealDiv 在 ONNX 中就是 Div
@tf_op("RealDiv", onnx_op="Div")
class RealDiv(BroadcastOp):
    """RealDiv 复用 BroadcastOp 的版本处理逻辑，只是改名"""
    pass

# TF 中的 Sub 已经映射为 Sub，不需要改名
# TF 中的 Maximum → ONNX Max（注意：ONNX Max 是归约，需要特殊处理）
```

`onnx_op` 的改名在 `tensorflow_onnx_mapping` 中执行，在调用处理函数之前。

## _OPSETS 数据结构

注册表的核心是 `tf_op._OPSETS`，一个三层嵌套的 OrderedDict：

```
_OPSETS = OrderedDict({
    "": [                    # domain: ONNX 主域（空字符串）
        {},                  # index 0: 占位（opset 从 1 开始）
        {                    # index 1: opset 1
            "Abs": (version_6_func, {}),  # ← 注意：Abs 从 opset 6 开始
            "Add": (version_1_func, {}),
            "Relu": (version_6_func, {}),
            ...
        },
        {                    # index 2: opset 2
            "Add": (version_1_func, {}),  # 继承 opset 1
            ...
        },
        ...
        {                    # index 6: opset 6
            "Abs": (version_6_func, {}),   # Abs 在此版本首次出现
            "Add": (version_6_func, {}),   # Add 在 opset 6 有新处理器
            "BatchNormalization": ...,
            ...
        },
        ...
        {                    # index 13: opset 13
            "Add": (version_6_func, {}),   # 没有新处理器，沿用 opset 6
            ...
        },
    ],
    "com.microsoft": [...],   # 自定义 domain
    "ai.onnx.ml": [...],      # ML domain
})
```

**三层索引逻辑**：

1. **Domain 层**：按 ONNX domain 分组，支持标准 ONNX 和自定义扩展域
2. **Opset 层**：列表索引即 opset 版本号，列表中每个元素是该 opset 版本新增或更新的算子映射
3. **Op 层**：字典 key 是 TF 算子名，value 是 `(handler_func, kwargs)` 元组

## create_mapping：版本堆叠算法

这是注册表的核心算法——从 _OPSETS 构建目标 opset 版本的最终映射字典：

```python
@classmethod
def create_mapping(cls, opset_version, extra_opset=None):
    """
    构建目标 opset 版本的算子映射。
    
    算法核心：从 opset 1 到目标 opset 逐层 update，
    高版本处理器自然覆盖低版本。
    """
    mapping = {}
    for domain, opsets in cls._OPSETS.items():
        # 确定该 domain 的目标 opset 版本
        if domain == "":
            target_opset = opset_version
        else:
            target_opset = get_extra_opset_version(domain, extra_opset)
        
        # 版本堆叠：从 opset 1 遍历到目标版本
        version_map = {}
        for i in range(1, min(target_opset + 1, len(opsets))):
            version_map.update(opsets[i])  # 高版本覆盖低版本
        
        mapping[domain] = version_map
    return mapping
```

**堆叠过程可视化**（目标 opset=13）：

```
opset 1:  {"Add": v1, "Relu": v6→v6, ...}
opset 2:  {"Add": v1, ...}                         # update 后：Add 仍为 v1
opset 3:  {...}                                    # 继续 update
opset 4:  {...}
opset 5:  {...}
opset 6:  {"Abs": v6, "Add": v6, "BatchNorm": v6}  # update 后：Add 变为 v6，新增 Abs/BatchNorm
opset 7:  {"Add": v7, ...}                         # update 后：Add 变为 v7
...
opset 13: {...}                                    # 最终版本

结果：{"Abs": v6, "Add": v7, "BatchNorm": v6, "Relu": v6, ...}
```

### 为什么不直接存每个算子的最高版本？

你可能会想：为什么不直接为每个算子存最高版本的处理器，而要逐层堆叠？答案是**向前兼容**：

- 如果目标 opset=7，但 Add 在 opset 7 没有新处理器，则沿用 opset 6 的处理器（如果 opset 6 也没有，则用 opset 1）
- 逐层 update 自然处理了"继承"——不需要显式声明某个算子在哪个版本之后保持不变
- 新 opset 版本只需添加该版本变化的算子，不变的算子自动继承旧版本

### 新增 opset 支持是纯增量操作

假设现在要支持 opset 19，只需要：

```python
# 在现有处理类中添加 version_19 方法即可
@tf_op("SomeOp")
class SomeOp:
    @classmethod
    def version_13(cls, ctx, node, **kwargs):
        ...
    
    @classmethod
    def version_19(cls, ctx, node, **kwargs):
        """opset 19 的新处理逻辑"""
        ...
```

**不需要**：
- 修改任何现有代码
- 添加 if 条件判断
- 重新组织注册表
- 修改其他算子的处理器

这就是"版本选择是注册表查询问题"的实际体现。

## onnx_opset 目录组织

算子处理器按功能类别分文件组织在 `onnx_opset/` 目录：

```
tf2onnx/onnx_opset/
├── __init__.py      # 包初始化，导入所有子模块以触发注册
├── common.py        # 广播运算（Add/Sub/Mul/Div/Pow/Maximum/Minimum）
├── math.py          # 数学运算（Abs/Exp/Log/Sqrt/Tanh/Relu/MatMul）
├── nn.py            # 神经网络（Conv/Pool/BatchNorm/Softmax/Dropout）
├── controlflow.py   # 控制流（If/Loop/Switch/Merge）
├── rnn.py           # 循环神经网络（LSTM/GRU）
├── reduction.py     # 归约运算（ReduceSum/ReduceMean/ArgMax）
├── tensor.py        # 张量操作（Reshape/Transpose/Concat/Split/Gather）
├── logical.py       # 逻辑运算（And/Or/Not/Equal/Where）
├── misc.py          # 杂项（Identity/Const/Shape）
├── quantize.py      # 量化算子
├── signal.py        # 信号处理（RFFT/IRFFT）
├── generator.py     # 生成器（ConstantOfShape/OneHot）
└── traditionalml.py # 传统 ML（TreeEnsemble/SVM）
```

包初始化时导入所有子模块：

```python
# onnx_opset/__init__.py
from tf2onnx.onnx_opset import common, math, nn, controlflow, rnn, \
    reduction, tensor, logical, misc, quantize, signal, generator, traditionalml
```

导入时 `@tf_op` 装饰器自动执行，将所有处理器注册到 `_OPSETS`。

## 自定义算子扩展

用户可以通过两种方式注册自定义算子：

### 方式一：@tf_op 装饰器（新 API，推荐）

```python
from tf2onnx.handler import tf_op

@tf_op("MyCustomOp", domain="com.example")
class MyCustomOp:
    @classmethod
    def version_1(cls, ctx, node, **kwargs):
        # 自定义转换逻辑
        # node.type 当前是 "MyCustomOp"
        # 可以通过 ctx 访问 Graph，插入新节点、修改输入等
        pass
```

使用时通过 `extra_opset` 指定自定义 domain 版本：

```python
import my_custom_op_module  # 导入以触发注册
model_proto, _ = tf2onnx.convert.from_saved_model(
    "saved_model_dir",
    opset=15,
    extra_opset=[("com.example", 1)]
)
```

### 方式二：custom_op_handlers 字典（旧 API）

```python
def my_handler(ctx, node, **kwargs):
    # 转换逻辑
    pass

custom_op_handlers = {"MyCustomOp": (my_handler, {"arg": "value"})}

model_proto, _ = tf2onnx.convert.from_saved_model(
    "saved_model_dir",
    custom_op_handlers=custom_op_handlers
)
```

旧 API 内部通过 `compat_handler` 包装适配新接口。新代码推荐使用 `@tf_op` 装饰器。

## 处理函数签名约定

所有版本处理函数遵循统一签名：

```python
@classmethod
def version_N(cls, ctx, node, **kwargs):
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `cls` | class | 处理类本身（用于调用辅助方法） |
| `ctx` | Graph | 当前图对象（可调用 make_node、get_shape 等） |
| `node` | Node | 当前正在处理的节点（可修改 type、inputs、attrs） |
| `**kwargs` | dict | 额外参数（onnx_op、tf_op 等装饰器参数） |

处理函数可以通过 `ctx` 执行图操作：
- `ctx.make_node(op_type, inputs, outputs, ...)` 创建新节点
- `ctx.replace_all_inputs(old_name, new_name)` 替换所有输入引用
- `ctx.remove_node(node)` 删除节点
- `ctx.get_shape(tensor_name)` 获取张量形状
- `ctx.set_dtype(tensor_name, dtype)` 设置张量类型

## 关联概念

- [tf2onnx 整体架构](00-overall-architecture.md) — 回到架构总览
- [转换流水线详解](01-conversion-pipeline.md) — 理解 Mapper 阶段如何使用注册表
- [图重写与模式匹配](03-graph-rewriting.md) — 理解为什么重写器先于映射器运行
- [内部 Graph API 设计](04-graph-internal-api.md) — 理解处理函数中 ctx (Graph) 的操作能力
- [自定义算子映射示例](../examples/custom-op-mapping.md) — 实战自定义算子注册
