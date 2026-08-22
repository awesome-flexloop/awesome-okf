---
okf_version: "0.2"
type: Concept
title: "类型 Shape 系统"
description: "Nuitka类型形状系统——ShapeBase层次、12种内置类型单例、类型推断驱动的特化代码生成"
tags: ["nuitka", "type", "shape", "type-inference", "optimization"]
sources:
  - id: REF-SHAPE-001
    path: "nuitka/nodes/shapes/Shapes.py"
    description: "Shape基类与标准单例"
  - id: REF-SHAPE-002
    path: "nuitka/nodes/shapes/BuiltinTypes.py"
    description: "12种内置类型形状"
  - id: REF-SHAPE-003
    path: "nuitka/nodes/shapes/ControlFlow.py"
    description: "控制流形状"
  - id: REF-SHAPE-004
    path: "nuitka/nodes/shapes/Abstract.py"
    description: "抽象形状"
prerequisites:
  - "04-node-ir-system"
next:
  - "06-module-import-system"
related:
  - "07-optimization-passes"
  - "08-c-code-generation"
  - "../references/node-base-api.md"
verified: true
status: active
---

# 类型 Shape 系统

Shape是Nuitka的**流敏感类型推断系统**。每个表达式节点通过`getTypeShape()`方法返回一个Shape对象，表示该表达式在当前控制流点上的可能类型。Shape信息贯穿优化和代码生成两个阶段，是Nuitka在不要求类型标注的情况下实现类型特化优化的关键。

## 为什么需要Shape

Python是动态类型语言，变量类型在运行时才能确定。但如果编译器能在编译时推断出某个表达式的类型，就可以：
1. **跳过通用PyObject路径**：直接操作C原生类型（如`long`、`double`）
2. **选择快速方法调用**：已知类型时直接调用C函数，不走`PyObject_Call`
3. **常量折叠**：已知类型+已知值→编译时计算
4. **消除类型检查**：已知为int就不需要`PyLong_Check()`
5. **内联属性访问**：已知类型时属性偏移量是编译期常量

Shape与类型标注不同：
- Shape是**编译器推断**的结果，不需要程序员写类型标注
- Shape是**流敏感**的——同一个变量在不同代码路径上可以有不同的Shape
- Shape描述**可能性集合**——可以表示"可能是int，也可能是float"

## ShapeBase 层次

```
ShapeBase
├── ShapeUnknown              # 完全未知类型（最保守）
├── ShapeVoid                 # 无返回值（语句的"值"）
├── ShapeAny                  # 任意Python对象（但不是void/unknown）
├── ShapeLoopBase             # 循环控制流相关形状
│   ├── ShapeLoopCompleteAlternative   # 循环完整执行，已知迭代次数
│   └── ShapeLoopIncompleteAlternative # 循环可能提前退出（break/异常）
├── ShapeBuiltinObject        # 内置类型（基类，12种具体单例）
│   ├── ShapeInt → int_shape              # int
│   ├── ShapeFloat → float_shape          # float
│   ├── ShapeBool → bool_shape            # bool（int的子类）
│   ├── ShapeStr → str_shape              # str
│   ├── ShapeBytes → bytes_shape          # bytes
│   ├── ShapeList → list_shape            # list
│   ├── ShapeTuple → tuple_shape          # tuple
│   ├── ShapeDict → dict_shape            # dict
│   ├── ShapeSet → set_shape              # set
│   ├── ShapeNoneType → none_shape        # None
│   ├── ShapeType → type_shape            # type（类对象）
│   └── ShapeSlice → slice_shape          # slice
├── ShapeIter                 # 迭代器
├── ShapeTupleUnbounded       # 不定长元组（与固定长度tuple_shape区分）
└── 插件扩展形状
    ├── ShapeNumpy.ndarray    # NumPy数组（NumPy插件添加）
    ├── ShapePandas*          # Pandas类型（Pandas插件添加）
    └── ...
```

## 12种内置类型单例

12种内置类型各有一个全局单例实例（如`int_shape`、`str_shape`），通过`ShapeBase.getBuiltinShapeFromType(type_obj)`或节点的`getTypeShape()`方法获取。这些单例在整个编译过程中共享，通过`is`运算符比较，零分配开销。

### Shape的核心API

每个Shape对象提供以下查询方法：

| 方法 | 返回值 | 说明 |
|------|--------|------|
| `getTypeShape()` | ShapeBase | 节点的Shape（节点方法） |
| `hasShape()` | bool | 是否有具体Shape（非Unknown/Void） |
| `isShapeInt()` | bool | 是否为int形状 |
| `isShapeStr()` | bool | 是否为str形状 |
| `isShapeBool()` | bool | 是否为bool形状 |
| `isShapeNone()` | bool | 是否为None |
| `isShapeIterable()` | bool | 是否可迭代 |
| `getComparisonShape()` | ShapeBase | 比较结果形状（bool/NotImplemented） |
| `getIntegerValue()` | int/None | 已知的整数值（常量） |
| `getIntValue()` | int/None | 编译时已知的整数（优化用） |

## Shape 推断如何工作

Shape推断发生在**优化阶段**的`computeExpression()`方法中。每个节点在自我优化时，会根据子节点的Shape推断自身的Shape：

### 常量节点

`ExpressionConstantRef`的Shape直接由其常量值决定：
```python
# ExpressionConstantRef(value=42).getTypeShape() → int_shape
# ExpressionConstantRef(value="hello").getTypeShape() → str_shape
# ExpressionConstantRef(value=None).getTypeShape() → none_shape
```

### 二元运算

`ExpressionBinaryOperation`根据操作符和两侧Shape推断结果Shape：
```python
# int + int → int_shape
# str + str → str_shape
# int + float → float_shape（提升规则）
# int + str → ShapeUnknown（__add__可能有副作用）
```

### 比较运算

`ExpressionComparison`的结果Shape几乎总是`bool_shape`，除非操作数类型不支持该比较。

### 函数调用

`ExpressionCall`的Shape推断较复杂：
- 内置函数：根据函数名和参数Shape推断（如`len()` → `int_shape`，`str()` → `str_shape`）
- 已知返回类型的函数：通过ValueTrace追踪
- 未知函数：`ShapeUnknown`

### 控制流合并

在if/else、try/except等控制流汇合点，Shape会合并为多个路径Shape的联合：
```python
# if cond:
#     x = 1      # x: int_shape
# else:
#     x = "a"    # x: str_shape
# print(x)        # x: ShapeUnknown（int或str，无法确定）
```

### 循环中的Shape

循环中的变量Shape更复杂：
- **ShapeLoopCompleteAlternative**：循环完整执行了所有迭代（如`for i in range(10)`已知迭代10次）
- **ShapeLoopIncompleteAlternative**：循环可能被break/return/异常中断，变量值不确定

## Shape 驱动代码生成

在代码生成阶段，Expression根据自身Shape选择不同的C代码路径：

### 整数特化（ShapeInt）

```c
// 通用路径（ShapeUnknown/Any）：
PyObject *result = PyNumber_Add(left, right);

// ShapeInt特化路径：
NUITKA_INT_LONG_VAL(result) = NUITKA_INT_LONG_VAL(left) + NUITKA_INT_LONG_VAL(right);
// 直接操作C long，跳过PyObject创建和类型检查
```

### 布尔特化（ShapeBool）

```c
// ShapeBool: 直接用C的1/0，不需要Py_True/Py_False的INCREF/DECREF
int truth = (left && right);  // 直接C布尔运算
```

### None特化（ShapeNone）

```c
// ShapeNone: 直接用Py_RETURN_NONE宏
Py_RETURN_NONE;  // 不需要创建新的None引用
```

### 容器特化（ShapeList/ShapeTuple/ShapeDict）

```c
// ShapeTuple: 使用预计算的TupleDescriptor直接构建元组
// 跳过通用的PyTuple_Pack，直接设置ob_item
```

### 属性访问特化

```c
// 已知类型的属性访问：直接计算C结构体偏移量
// obj.attr → ((PyObject**)obj)[offset]
// 不需要PyObject_GetAttrString的哈希查找
```

## Shape 与 SSA 值追踪的关系

Shape是**类型层面**的信息，而ValueTrace是**值层面**的信息。两者在优化阶段协同工作：

1. **ValueTrace**追踪变量在每个赋值点的具体值（可能是常量、另一个变量、或merge节点）
2. **Shape**从ValueTrace中推断类型信息
3. 如果ValueTrace记录某个变量总是被赋整数值，其Shape就是`int_shape`
4. 如果ValueTrace记录变量在某路径被赋str值，另一路径被赋int值，Shape退化为`ShapeUnknown`

```
ValueTrace (值追踪)
  ├── TraceAssign: 记录赋值来源（哪个表达式赋的值）
  ├── TraceMerge:  记录控制流合并后的值
  └── TraceDelete: 记录变量删除
       │
       ▼
   根据赋值表达式的Shape
   推断变量在当前Trace中的Shape
       │
       ▼
   Shape信息传递给
   computeExpression()和代码生成
```

> 值追踪的详细机制见 [07-优化遍](07-optimization-passes.md)。

## Shape 的保守性原则

Shape推断遵循**"不确定就保守"**原则：
- 如果无法100%确定类型，返回`ShapeUnknown`
- 不会为了优化而冒险假设类型——错误假设会导致生成错误的C代码
- 用户定义的`__add__`/`__getattr__`等可以返回任意类型，因此涉及用户自定义方法的操作通常保守为`ShapeUnknown`
- 插件可以为特定库（如NumPy、Pandas）提供更精确的Shape信息

这意味着Nuitka的Shape推断是**正确但不完整**的——它不会遗漏类型安全，但可能错过一些优化机会（通过插件可以补充）。
