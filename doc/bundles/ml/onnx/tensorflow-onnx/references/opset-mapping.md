---
type: reference
title: "算子版本化注册表：@tf_op 装饰器与 onnx_opset 目录"
description: "tf2onnx 算子注册机制的信源登记，包括 tf_op 装饰器、版本化处理器约定、onnx_opset 目录组织与 create_mapping 算法"
sources:
  - path: "tf2onnx/handler.py"
    facts: [F-015, F-016, F-017, F-018]
  - path: "tf2onnx/onnx_opset/__init__.py"
    facts: [F-019, F-020]
  - path: "tf2onnx/tfonnx.py"
    facts: [F-021, F-043]
---

# 算子版本化注册表：@tf_op 装饰器与 onnx_opset 目录

## 信源概述

| 信源 | 类型 | 职责 |
|------|------|------|
| `tf2onnx/handler.py` | Python 模块 | `tf_op` 装饰器类定义，`_OPSETS` 全局注册表，`create_mapping` 版本堆叠算法 |
| `tf2onnx/onnx_opset/` | Python 包 | 按算子类别分文件的算子处理器实现，每个文件包含多个 `@tf_op` 装饰的处理类 |
| `tf2onnx/tfonnx.py` | Python 模块 | `tensorflow_onnx_mapping` 遍历函数，custom_op_handlers 兼容层 |

## 关键事实登记

### F-015：tf_op 类——算子注册装饰器

**信源**：`tf2onnx/handler.py`

`tf_op` 类是算子注册的核心装饰器，使用方式为 `@tf_op(op_name_list, domain=..., **kwargs)` 装饰处理类：

```python
@tf_op("Relu")
class Relu:
    @classmethod
    def version_6(cls, ctx, node, **kwargs):
        """opset 6+ 的 Relu 处理（DirectOp，无需额外操作）"""
        pass

@tf_op("Add", "Sub", "Mul")
class BroadcastOp:
    @classmethod
    def version_1(cls, ctx, node, **kwargs):
        """opset 1-5：使用 broadcast 属性"""
        node.set_attr("broadcast", 1)

    @classmethod
    def version_6(cls, ctx, node, **kwargs):
        """opset 6+：使用 multi-broadcast（显式广播）"""
        pass  # opset 6+ 原生支持 multi-directional broadcast
```

处理类通过 `version_N` 类方法定义不同 opset 版本的处理逻辑，`N` 为该处理器开始支持的 opset 版本号。

### F-016：_OPSETS 数据结构——domain→opset→op_map 三维索引

**信源**：`tf2onnx/handler.py`

```python
class tf_op(object):
    _OPSETS = collections.OrderedDict()
    # _OPSETS 结构：
    # {
    #   "": [  # 空字符串 = ONNX 主 domain
    #     {},  # opset 0（占位）
    #     {},  # opset 1
    #     {"Relu": (version_6_func, kwargs), ...},  # opset 6
    #     ...  # 更高 opset
    #   ],
    #   "com.microsoft": [...],  # 自定义 domain
    # }
```

**索引维度**：
1. **第一层**：按 domain 分组（ONNX 主域为空字符串，自定义域用 domain URI）
2. **第二层**：按 opset 版本排列为列表（列表索引 = opset 版本号）
3. **第三层**：每个 opset 版本内是 `{op_name: (handler_func, kwargs)}` 字典

### F-017：create_mapping——版本堆叠算法

**信源**：`tf2onnx/handler.py`

```python
@classmethod
def create_mapping(cls, opset_version, extra_opset=None):
    """
    根据目标 opset 版本构建最终映射字典。
    
    算法：对每个 domain，从 opset 1 遍历到目标 opset，
    逐层更新映射字典，使得高版本 opset 的处理器覆盖低版本。
    """
    mapping = {}
    for domain, opsets in cls._OPSETS.items():
        version_map = {}
        target_opset = opset_version if domain == "" else get_extra_opset(domain, extra_opset)
        for oplist in opsets[1:target_opset + 1]:
            version_map.update(oplist)
        mapping[domain] = version_map
    return mapping
```

**核心思想**：从 opset 1 到目标 opset 逐层 `update`，高版本自动覆盖低版本。这意味着：
- 如果一个算子在 opset 6 和 opset 13 都有处理器，目标 opset ≥ 13 时使用 version_13
- 如果一个算子只在 opset 6 有处理器，目标 opset 18 时仍使用 version_6（向前兼容）
- 新增 opset 支持只需添加 `version_18` 方法，不修改任何现有代码

### F-018：kwargs——算子重命名与 TFLite 特殊处理

**信源**：`tf2onnx/handler.py`

`@tf_op` 装饰器的 kwargs 参数支持两个特殊键：

| 键 | 作用 | 示例 |
|----|------|------|
| `onnx_op` | 将 TF 算子名映射为不同的 ONNX 算子名 | `@tf_op("RealDiv", onnx_op="Div")` |
| `tf_op` | TFLite 路径中传递原始 TF 算子名 | TFLite 内部使用 |

```python
# 示例：RealDiv 在 ONNX 中就是 Div
@tf_op("RealDiv", onnx_op="Div")
class RealDiv(BroadcastOp):
    # 继承 BroadcastOp 的版本处理逻辑
    pass
```

### F-019：onnx_opset 目录——按算子类别组织

**信源**：`tf2onnx/onnx_opset/__init__.py`

`onnx_opset` 目录按算子功能类别分文件组织：

| 文件 | 算子类别 | 典型算子 |
|------|----------|----------|
| `common.py` | 广播运算 | Add, Sub, Mul, Div, Pow, Maximum, Minimum |
| `math.py` | 数学运算 | Abs, Exp, Log, Sqrt, Tanh, Relu, Sigmoid, MatMul |
| `nn.py` | 神经网络 | Conv, MaxPool, BatchNormalization, Softmax, Dropout |
| `controlflow.py` | 控制流 | If, Loop, Switch, Merge, Enter, Exit, NextIteration |
| `rnn.py` | 循环神经网络 | LSTM, GRU, BasicLSTMCell, GRUCell |
| `reduction.py` | 归约运算 | ReduceSum, ReduceMean, ReduceMax, ReduceMin, ArgMax |
| `tensor.py` | 张量操作 | Reshape, Transpose, Concat, Split, Gather, Slice, Pad |
| `logical.py` | 逻辑运算 | And, Or, Not, Equal, Less, Greater, Where |
| `misc.py` | 杂项 | Identity, Const, Placeholder, Shape, Rank, Size |
| `quantize.py` | 量化 | QuantizeLinear, DequantizeLinear, QLinearConv |
| `signal.py` | 信号处理 | RFFT, IRFFT |
| `generator.py` | 生成器 | ConstantOfShape, OneHot, EyeLike |
| `traditionalml.py` | 传统 ML | TreeEnsemble, SVM, LinearClassifier |

包初始化时通过 `from tf2onnx.onnx_opset import *` 导入所有子模块，触发 `@tf_op` 装饰器执行注册。

### F-020：DirectOp 模式——零成本映射

**信源**：`tf2onnx/onnx_opset/math.py`

最简单的算子映射是空实现（`pass`），称为 DirectOp 模式，表示 TF 算子与 ONNX 算子一一对应，无需额外处理：

```python
@tf_op("Abs")
class Abs:
    @classmethod
    def version_6(cls, ctx, node, **kwargs):
        pass  # TF Abs == ONNX Abs，直接映射

@tf_op("Ceil")
class Ceil:
    @classmethod
    def version_6(cls, ctx, node, **kwargs):
        pass

# Exp, Log, Relu, Sigmoid, Sqrt, Tanh, Floor, Neg, Reciprocal 等同理
```

DirectOp 模式的处理器只需要声明 `version_N` 方法存在，方法体为空即可。这意味着这些算子在转换时只需要改名（如果 `onnx_op` 指定了）或直接保留原类型名。

### F-021：tensorflow_onnx_mapping——遍历映射执行

**信源**：`tf2onnx/tfonnx.py`

```python
def tensorflow_onnx_mapping(g, ops_mapping, ...):
    """遍历图中所有节点，通过 ops_mapping 查找处理函数"""
    for node in g.get_nodes():
        if node.skip_conversion:
            continue  # 已被重写器处理
        op_name = node.type
        handler = ops_mapping.get(op_name)
        if handler:
            handler_func, kwargs = handler
            # 1. 如果指定了 onnx_op，改节点类型名
            if "onnx_op" in kwargs:
                node.type = kwargs["onnx_op"]
            # 2. 执行处理函数
            handler_func(g, node, **kwargs)
            # 3. 标记已转换
            node.skip_conversion = True
        # 对子图递归处理
        for body_graph in node.contained_graphs.values():
            tensorflow_onnx_mapping(body_graph, ops_mapping, ...)
```

**关键机制**：
1. 遍历所有节点，跳过已标记 `skip_conversion` 的节点（被重写器替换的）
2. 查找 ops_mapping 中的处理函数
3. 处理函数可能插入新节点、修改输入输出、设置属性
4. 处理后标记 `skip_conversion = True`
5. 对有 body_graphs（If/Loop/Scan）的节点递归处理子图

### F-043：自定义算子扩展——新旧两种 API

**信源**：`tf2onnx/tfonnx.py`

自定义算子支持两种 API：

**旧 API**（通过 `custom_op_handlers` 字典）：
```python
custom_op_handlers = {
    "MyCustomOp": (my_handler_func, {"arg1": value1})
}
```
内部通过 `compat_handler` 包装适配新接口。

**新 API**（使用 `@tf_op` 装饰器）：
```python
from tf2onnx.handler import tf_op

@tf_op("MyCustomOp", domain="com.example")
class MyCustomOp:
    @classmethod
    def version_1(cls, ctx, node, **kwargs):
        # 自定义转换逻辑
        pass

# 模块导入时自动注册，通过 extra_opset 指定 domain 版本
```

新 API 模块在导入时自动生效（装饰器注册），通过 `extra_opset=[("com.example", 1)]` 指定自定义 domain 的 opset 版本。

## 代码引用

```python
# handler.py - tf_op 装饰器核心逻辑（简化）
class tf_op(object):
    _OPSETS = collections.OrderedDict()

    def __init__(self, op_names, domain="", **kwargs):
        self._op_names = op_names if isinstance(op_names, (list, tuple)) else [op_names]
        self._domain = domain
        self._kwargs = kwargs

    def __call__(self, func):
        """装饰处理类，注册 version_N 方法"""
        if self._domain not in self._OPSETS:
            self._OPSETS[self._domain] = []
        
        # 找到类中所有 version_N 方法
        opsets = self._OPSETS[self._domain]
        for version in range(1, 20):  # 支持到 opset 19+
            version_func = getattr(func, f"version_{version}", None)
            if version_func:
                # 确保 opsets 列表长度足够
                while len(opsets) <= version:
                    opsets.append({})
                # 注册每个算子名到该版本处理器的映射
                for op_name in self._op_names:
                    opsets[version][op_name] = (version_func, self._kwargs)
        return func
```
