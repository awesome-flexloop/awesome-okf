---
okf_version: "0.2"
type: Reference
title: "Nuitka 节点基类 API"
description: "nuitka/nodes/模块——NodeBase、StatementBase、ExpressionBase核心基类与元类自动注册机制"
tags: ["nuitka", "ir", "ast", "node", "metaclass"]
sources:
  - id: REF-NODE-001
    path: "nuitka/nodes/NodeBase.py"
    description: "节点基类定义"
  - id: REF-NODE-002
    path: "nuitka/nodes/ExpressionBases.py"
    description: "表达式节点基类"
  - id: REF-NODE-003
    path: "nuitka/nodes/StatementBases.py"
    description: "语句节点基类"
  - id: REF-NODE-004
    path: "nuitka/nodes/shapes/ControlFlow.py"
    description: "控制流形状类型"
  - id: REF-NODE-005
    path: "nuitka/nodes/shapes/BuiltinTypes.py"
    description: "内置类型形状"
  - id: REF-NODE-006
    path: "nuitka/nodes/shapes/Shapes.py"
    description: "Shape基类与标准形状单例"
  - id: REF-NODE-007
    path: "nuitka/nodes/shapes/Abstract.py"
    description: "抽象形状"
verified: true
status: active
---

# Nuitka 节点基类 API 参考

> 源码路径：nuitka/nodes/

## 类层次

```
NodeBase (自动注册元类 NodeCheckMetaClass)
├── CompileTimeConstantNode       # 编译时常量节点
├── ModuleNode (ExpressionModuleMixin)
│   ├── CompiledPythonModule      # 编译到C的模块
│   ├── CompiledPythonPackage     # 编译到C的包
│   └── UncompiledPythonModule    # 保留字节码的模块
├── ExpressionBase (ExpressionNodeBaseMixin)
│   ├── ExpressionFunctionBodyBase
│   │   ├── ExpressionFunctionBody
│   │   ├── ExpressionAsyncFunctionBody
│   │   ├── ExpressionCoroutineBody
│   │   ├── ExpressionGeneratorBody
│   │   └── ExpressionAsyncgenBody
│   ├── ExpressionBuiltinRefBase
│   ├── ExpressionLookupMixin
│   └── ...50+ 具体表达式子类
└── StatementBase
    ├── StatementAssignmentVariable
    ├── StatementReturn
    ├── StatementRaiseException
    └── ...30+ 具体语句子类
```

---

## NodeCheckMetaClass（元类）

元类在类定义时自动执行以下注册：

1. **kind注册**：将`__name__`转换为kind字符串（如`ExpressionFunctionBody` → `"EXPRESSION_FUNCTION_BODY"`），注册到`kinds`字典
2. **is<Kind>()方法注入**：为NodeBase自动添加`isExpressionFunctionBody()`等检查方法
3. **__slots__生成**：根据`named_children`和`nice_children`列表自动生成`__slots__`，避免内存浪费
4. **子节点描述符**：为每个named_child生成访问器属性

## NodeBase 核心方法

| 方法 | 返回值 | 说明 |
|------|--------|------|
| `getKind()` | str | 返回节点kind字符串（由元类设置） |
| `is<KindName>()` | bool | 类型检查方法（由元类自动生成） |
| `getParent()` | Node | 返回父节点引用 |
| `getModule()` | CompiledPythonModule | 返回所在模块 |
| `getCompileTimeConstant()` | Any | 获取编译时常量值（仅ConstantNode有效） |
| `getVisitableNodes()` | list[Node] | 返回可遍历的子节点列表 |
| `getName()` | str | 返回节点名称 |
| `getDescription()` | str | 返回人类可读描述 |
| `finalize()` | None | 节点终结，清理引用和闭包关系 |
| `dump(level)` | str | 调试用树状转储 |
| `simulator(operator, args)` | Any | 编译时模拟求值（用于常量折叠） |

## StatementBase 核心方法

| 方法 | 返回值 | 说明 |
|------|--------|------|
| `computeStatement(trace_collection)` | (Statement, bool, Sequence) | 语句优化入口，返回优化后语句、是否改变、终止标记 |
| `computeStatementRaw(trace_collection)` | (Statement, bool, Sequence) | 原始语句优化（不包装） |
| `mayRaiseException(ExceptionShape)` | bool | 该语句是否可能抛出异常 |
| `needsLineNumber()` | bool | 该语句是否需要行号（用于异常栈追踪） |
| `getStatementDelimiter()` | int | 语句分隔符标记 |

## ExpressionBase 核心方法

| 方法 | 返回值 | 说明 |
|------|--------|------|
| `computeExpression(trace_collection)` | (Expression, bool, Sequence) | 表达式优化入口 |
| `computeExpressionRaw(trace_collection)` | (Expression, bool, Sequence) | 原始表达式优化 |
| `getTypeShape()` | ShapeBase | 返回类型形状（Shape系统，驱动类型特化） |
| `getComparisonShape()` | ShapeBase | 返回比较结果形状（bool/NotImplemented） |
| `getIntegerValue()` | int/None | 返回整数值（用于常量折叠） |
| `getIntValue()` | int/None | 返回已知整数值（优化阶段使用） |
| `isCompileTimeConstant()` | bool | 是否为编译时已知常量 |
| `isKnownToBeHashable()` | bool | 是否已知可哈希 |
| `mayHaveSideEffects()` | bool | 是否可能有副作用 |
| `isKnownTruthy()` | bool/None | 是否已知为真值 |
| `countArgs()` | int/None | 返回参数数量（调用节点） |
| `onReleaseEscaped()` | None | 引用转义时的回调 |

## Mixin 类

| Mixin类 | 提供能力 | 被哪些节点使用 |
|---------|---------|--------------|
| `ClosureGiverMixin` | 变量提供者（管理局部变量） | Function/Class/Module |
| `ClosureTakerMixin` | 闭包变量引用者（从外层获取变量） | 嵌套函数/类 |
| `CodeNodeMixin` | 代码节点（有行号、代码对象） | Function/Generator/Module |
| `ExpressionModuleMixin` | 模块特定行为 | Module/CompiledModule |
| `ExpressionNodeBaseMixin` | 表达式公共行为 | 所有Expression子类 |
| `ChildrenHavingMixin` | 具名子节点管理 | 大部分复合节点 |
| `ContainerShapeMixin` | 容器形状（list/tuple/set/dict） | 容器字面量节点 |
| `NumberShapeMixin` | 数值形状（int/float/complex） | 数值常量节点 |
| `ShapeLoopMixin` | 循环控制流形状 | 循环语句中的表达式 |
| `SubscriptContainerLookupMixin` | 下标查找优化 | __getitem__等下标节点 |

---

## dispatch 字典

代码生成和树构建通过全局字典按kind分发：

- `tree.Building.dispatch_dict`：kind→构建函数映射（50+个AST节点）
- `code_generation.ExpressionCodes.expression_dispatch_dict`：kind→C代码生成函数映射
- `code_generation.StatementCodes.statement_dispatch_dict`：kind→C代码生成函数映射

---

## Shape 类型体系

```
ShapeBase
├── ShapeLoopBase
│   ├── ShapeLoopCompleteAlternative      # 循环完整（已知迭代次数）
│   └── ShapeLoopIncompleteAlternative    # 循环不完整
├── ShapeUnknown                          # 未知类型
├── ShapeVoid                             # 无返回值
├── ShapeAny                              # 任意类型
├── ShapeBuiltinObject                    # 内置类型（含12种单例）
│   ├── ShapeInt → int_shape
│   ├── ShapeFloat → float_shape
│   ├── ShapeStr → str_shape
│   ├── ShapeBytes → bytes_shape
│   ├── ShapeBool → bool_shape
│   ├── ShapeList → list_shape
│   ├── ShapeTuple → tuple_shape
│   ├── ShapeDict → dict_shape
│   ├── ShapeSet → set_shape
│   ├── ShapeNoneType → none_shape
│   ├── ShapeType → type_shape
│   └── ShapeSlice → slice_shape
├── ShapeIter                             # 迭代器
├── ShapeNumpy.ndarray                    # NumPy数组（插件扩展）
├── ShapePandas*系列                     # Pandas类型（插件扩展）
└── ShapeTupleUnbounded                   # 不定长元组
```

Shape用于优化阶段类型特化：如果已知表达式类型是`ShapeInt`，可以生成直接操作C `long` 的代码，避免`PyObject*`通用路径的开销。

---

## 相关概念

- [节点IR系统](../concepts/04-node-ir-system.md)
- [类型Shape系统](../concepts/05-type-shapes.md)
- [AST树构建](../concepts/03-ast-tree-building.md)
- [C代码生成](../concepts/08-c-code-generation.md)
- [变量与闭包](../concepts/12-variables-closures.md)
