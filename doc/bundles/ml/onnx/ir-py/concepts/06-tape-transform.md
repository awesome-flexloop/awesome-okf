---
type: concept
title: "Tape 图变换：算子录制、Builder 魔术方法与运算符重载"
description: "Tape 作为图构建录制器收集节点和初始化值，Builder 通过 __getattr__ 魔术方法实现 builder.Add(...) 风格调用，Value 通过 WithArithmeticMethods mixin 和 _magic_handler 支持运算符重载实现算子自动录制"
sources:
  references: [../references/tape-serde.md, ../references/core-entities.md]
  facts: [F-056, F-057, F-058, F-029]
---

# Tape 图变换：算子录制、Builder 魔术方法与运算符重载

## 核心理解

构建 ONNX 计算图传统上需要手动创建 NodeProto/ValueInfoProto 并管理输入输出名称映射，非常繁琐。onnx-ir 通过 `Tape`/`Builder` 实现声明式图构建——`Tape.op()` 在创建 Node+Value 的同时将节点录制到内部列表，`Builder` 更通过 `__getattr__` 魔术方法将任意属性访问转为算子调用（如 `builder.Add(x, b)`）。同时，`Value` 通过 `WithArithmeticMethods` mixin 和类级别 `_magic_handler` 支持运算符重载，框架作者可注入自定义 handler 实现类似 PyTorch eager 模式的算子录制。

## Tape：图构建录制器

Tape 是图构建的核心录制器（F-056），在创建节点和初始化值的同时自动收集它们，最终可直接喂给 Graph 构造函数。

### 基本用法

```python
import onnx_ir as ir

# 创建 Tape，指定 opset 版本
tape = ir.Tape({"": 20})  # "" 表示 ai.onnx 域

# 创建输入值
x = ir.val(name="x", shape=ir.Shape((1, 3, 224, 224)), dtype=ir.DataType.FLOAT)
w = tape.initializer(ir.tensor(np.random.randn(64, 3, 7, 7), name="w"))
b = tape.initializer(ir.tensor(np.zeros(64), name="b"))

# 录制算子
conv_out = tape.op("Conv", x, w, b,
                   kernel_shape=(7, 7),
                   pads=(3, 3, 3, 3),
                   strides=(2, 2))
relu_out = tape.op("Relu", conv_out)

# 构建图
graph = ir.Graph(
    tape.nodes,
    inputs=[x],
    outputs=[relu_out],
    initializers=tape.initializers_dict(),
    opset_imports=tape.used_opsets,
)
```

### 内部结构

```python
class Tape:
    _nodes: list[Node]              # 已录制的节点列表
    _initializers: list[TensorProtocol]  # 已注册的初始化值
    _used_opsets: dict[str, int]    # 自动收集的 (domain, version) 集合
    _graph_like: Graph | Function | None  # 可选：绑定到现有图/函数
```

### 核心 API

| 方法 | 返回值 | 说明 |
|------|--------|------|
| `op(op_type, *inputs, _domain="", _version=None, outputs=None, **attrs)` | Value | 创建单输出节点并录制，返回第一个输出 Value |
| `op_multi_out(op_type, *inputs, outputs=1, _domain="", _version=None, **attrs)` | Sequence[Value] | 创建多输出节点，返回所有输出 Value 序列 |
| `initializer(value, name=None)` | Value | 注册初始化张量，返回其对应的 Value |
| `nodes` (property) | list[Node] | 已录制节点列表 |
| `initializers` (property) | list[Value] | 已录制初始化值对应的 Value 列表 |
| `used_opsets` (property) | dict[str, int] | 所有用到的 (domain, version) 对 |

### op() 的 outputs 参数

- `outputs=None`（默认）：创建1个输出，返回单个 Value
- `outputs=3`（int）：创建3个输出
- `outputs=("y1", "y2")`（Sequence[str]）：创建指定名称的输出

### graph_like 绑定模式

当创建 Tape 时传入 `graph_like=existing_graph`，录制的节点会自动添加到该图中，无需手动管理：

```python
graph = ir.Graph([], inputs=[x], outputs=[], opset_imports=opset)
tape = ir.Tape(graph_like=graph)
# op() 创建的节点自动 append 到 graph
y = tape.op("Relu", x)
graph.append(ir.Node("Output", inputs=[y], outputs=[]))
```

### used_opsets 自动收集

每次调用 `op()` 时，Tape 自动记录该算子使用的 `(domain, version)` 对：
- 如果指定了 `_version`，使用指定版本
- 如果未指定但 opset_imports 中有该 domain 的版本，使用已有版本
- 如果完全未指定，不记录版本（由 Graph 构造时处理）

## Builder：魔术方法算子调用

Builder 继承 Tape，通过 `__getattr__` 魔术方法实现更自然的算子调用 API（F-057）：

```python
class Builder(Tape):
    def __getattr__(self, op_type: str):
        def op_caller(*args, _domain="", _version=None, _outputs=None, **kwargs):
            if _outputs is not None:
                return self.op_multi_out(op_type, *args,
                                         outputs=_outputs,
                                         _domain=_domain,
                                         _version=_version,
                                         **kwargs)
            return self.op(op_type, *args,
                          _domain=_domain, _version=_version, **kwargs)
        return op_caller
```

这使得任何未在 Builder 上定义的属性访问都被解释为算子类型，返回一个可调用的 op_caller：

```python
b = ir.Builder({"": 20})
x = ir.val(name="x", dtype=ir.DataType.FLOAT)
w = b.initializer(ir.tensor(weight_np, name="w"))

# 直接用方法名调用算子！
conv = b.Conv(x, w, kernel_shape=(3, 3), pads=(1, 1, 1, 1))
bn = b.BatchNormalization(conv, b_scale, b_bias, b_mean, b_var, epsilon=1e-5)
relu = b.Relu(bn)
pool = b.MaxPool(relu, kernel_shape=(2, 2), strides=(2, 2))

# 多输出算子用 _outputs 参数
boxes, labels, scores = b.NonMaxSuppression(
    bbs, scores, max_output_boxes_per_class=100, _outputs=3
)

# 指定输出名称
y = b.Add(a, c, _outputs=("output",))
```

### 特殊 kwargs

Builder 的 op_caller 支持三个特殊 kwargs（以 `_` 前缀区分算子属性）：

| kwarg | 类型 | 说明 |
|-------|------|------|
| `_domain` | str | 算子域（默认 `""` = ai.onnx） |
| `_version` | int | 算子版本（覆盖默认 opset） |
| `_outputs` | int \| Sequence[str] | 输出数量或输出名称 |

注意：Builder 是**内部扩展类**（`_tape.py` 中的 `_Builder`），公开模块 `tape.py` 仅导出 `Tape`（F-058）。但可以通过 `_tape.Builder` 访问，或使用 `ir.Builder`（如果有导出）。

## Value 运算符重载：_magic_handler 注入

`Value` 继承 `WithArithmeticMethods` mixin，通过类级别的 `_magic_handler`（ClassVar）实现算术运算符重载（F-029）：

```python
class WithArithmeticMethods:
    _magic_handler: ClassVar[Callable[[str, Value, Any], Value] | None] = None

    def __add__(self, other):
        if self._magic_handler is not None:
            return self._magic_handler("Add", self, other)
        return NotImplemented

    def __mul__(self, other):
        if self._magic_handler is not None:
            return self._magic_handler("Mul", self, other)
        return NotImplemented

    # __sub__/__truediv__/__neg__/__radd__/__rmul__/... 同理
```

### 为什么用 ClassVar 而非硬编码？

**反直觉设计**：Value 的运算符重载不是硬编码为创建 Add/Mul 节点，而是通过可注入的 handler 实现。这意味着 IR 核心本身对"加法产生什么节点"一无所知，完全由上层框架决定：

- 在简单图构建场景，handler 可以创建 Add 节点并录制到 Tape
- 在形状推断场景，handler 可以直接计算常量折叠结果
- 在符号执行场景，handler 可以返回符号表达式
- 不设置 handler 时，运算符返回 `NotImplemented`（即不支持）

### 使用示例

```python
import onnx_ir as ir

# 创建一个 Tape 作为录制目标
tape = ir.Tape({"": 20})

# 定义 magic_handler：将算术运算录制到 tape
def tape_magic_handler(op_type: str, self: ir.Value, other):
    if not isinstance(other, ir.Value):
        other = ir.tensor(np.array(other, dtype=np.float32))
        other = tape.initializer(other)
    return tape.op(op_type, self, other)

# 注入 handler
ir.set_value_magic_handler(tape_magic_handler)

# 现在可以像 PyTorch 一样写表达式！
x = ir.val(name="x", dtype=ir.DataType.FLOAT)
w = tape.initializer(ir.tensor(weight_np, name="w"))
b = tape.initializer(ir.tensor(bias_np, name="b"))

# x @ w + b 自动录制 MatMul 和 Add 节点
y = x @ w + b  # 等价于 tape.op("Add", tape.op("MatMul", x, w), b)
```

### 支持的运算符

| 运算符 | op_type | 反向版本 |
|--------|---------|----------|
| `+` | Add | `__radd__` |
| `-` | Sub | `__rsub__` |
| `*` | Mul | `__rmul__` |
| `/` | Div（若支持）或 Truediv | `__rtruediv__` |
| `@` | MatMul | `__rmatmul__` |
| `-`（一元） | Neg | — |

具体的运算符集合取决于 `WithArithmeticMethods` 实现的魔术方法，至少覆盖 `+`, `-`, `*`, `/`, `@` 及其反向版本和一元负号。

## 三种图构建方式对比

| 方式 | API 风格 | 适用场景 | 示例 |
|------|---------|---------|------|
| 直接构造 Node/Graph | 手动创建对象 | 精细控制、序列化代码 | `Graph([Node("Add", [x, y])], ...)` |
| Tape.op() | 方法调用 | 标准图构建 | `tape.op("Add", x, y)` |
| Builder.__getattr__ | 伪方法调用 | 快速原型、脚本 | `b.Add(x, y)` |
| _magic_handler | 运算符表达式 | 框架集成、eager-like 体验 | `x + y` |

### 推荐实践

1. **大多数场景使用 Builder**：`b = ir.Builder(opset_imports)` 通过方法调用创建节点，最后用 `b.nodes`/`b.initializers`/`b.used_opsets` 构造 Graph
2. **Initializer 必须显式注册**：`b.initializer(tensor)` 注册初始化值，Tape 不会自动从节点输入中识别常量
3. **复杂框架使用 magic_handler**：通过 `set_value_magic_handler()` 注入自定义 handler，实现 DSL 风格的图构建
4. **graph_like 绑定简化流程**：在已有 Graph 上直接用 Tape 录制，省去手动 extend
