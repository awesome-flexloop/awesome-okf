---
okf_version: "0.2"
type: Concept
title: "变量与闭包"
description: "Nuitka变量系统——Variable类层次、ClosureGiver/Taker闭包机制、TempVariable临时变量、C变量分配策略"
tags: ["nuitka", "variable", "closure", "scope", "temp-variable", "cell"]
sources:
  - id: REF-VAR-001
    path: "nuitka/variables/Variable.py"
    description: "Variable类定义"
  - id: REF-VAR-002
    path: "nuitka/variables/Closure.py"
    description: "闭包giver/taker管理"
  - id: REF-VAR-003
    path: "nuitka/variables/TempVariable.py"
    description: "临时变量管理"
  - id: REF-VAR-004
    path: "nuitka/code_generation/VariableCodes.py"
    description: "变量访问C代码生成"
prerequisites:
  - "04-node-ir-system"
next:
  - "13-cli-options"
related:
  - "07-optimization-passes"
  - "08-c-code-generation"
  - "../references/code-generation-api.md"
verified: true
status: active
---

# 变量与闭包

Nuitka的变量系统处理Python的变量作用域、闭包和C代码生成中的变量分配。理解变量系统对于理解Nuitka如何生成高效C代码至关重要——不逃逸的变量可以分配为C局部变量（栈上），而闭包变量需要通过cell对象间接访问。

## Variable 类层次

```
VariableBase
├── LocalVariable           # 函数/方法的局部变量
│   └── 最常见的变量类型，在函数作用域内定义
├── ClosureVariable         # 从外层作用域闭包引用的变量
│   └── 通过cell间接访问
├── ModuleVariable          # 模块级全局变量
│   └── 通过模块字典访问
├── TempVariable            # C代码生成时的临时变量
│   └── 编译器内部使用，不对应Python变量
├── TempVariableMixin       # 临时变量Mixin
├── ParameterVariable       # 函数参数变量
│   └── 特殊的局部变量，从args数组获取
├── SelfVariable            # self/cls参数
│   └── ParameterVariable的特化
└── StarListVariable/StarDictVariable  # *args/**kwargs
```

每个Variable对象有：
- `variable_name`：变量名
- `owner`：变量所属的作用域（FunctionBody/Module/Class）
- `version_number`：SSA版本号
- `traces`：值追踪列表
- `closure_reference`：是否被闭包引用

## ClosureGiver / ClosureTaker 闭包机制

Python支持闭包——内部函数可以引用外部函数的变量。Nuitka通过ClosureGiver（变量提供者）和ClosureTaker（变量引用者）两个Mixin管理闭包关系：

### ClosureGiverMixin

作为变量"提供者"的作用域（Module、Function、Class）：
- 管理自己创建的所有局部变量
- 追踪哪些变量被闭包引用（被内部函数拿走）
- 为闭包变量创建cell对象
- 提供`getVariableForClosure(name)`方法给内部函数调用

### ClosureTakerMixin

引用外层变量的作用域（嵌套函数、嵌套类）：
- 记录从哪些giver获取了哪些变量
- 在函数对象创建时从外层获取cell
- 提供`getClosureVariable(name)`获取闭包变量

### 闭包建立过程

```python
def outer(x):          # outer是ClosureGiver
    y = x + 1          # y是LocalVariable
    def inner():       # inner是ClosureTaker
        return y       # 引用外层y → y成为ClosureVariable
    return inner
```

编译时闭包关系建立：

```
1. buildFunctionNode(inner)
     ├── inner.markAsClosureTaker()
     ├── inner.takeClosureVariable(outer, "y")
     │     └── outer.registerClosureVariable("y") → y从LocalVariable升级为ClosureVariable
     └── outer.addClosureTaker(inner)

2. 代码生成时:
     outer:
       ├── 创建PyCellObject for y
       ├── 将cell存入inner的closure元组
       └── 访问y时通过cell: PyCell_GET(cell)
     inner:
       ├── 从closure参数获取cell
       └── 访问y时: PyCell_GET(self->m_closed[y_index])
```

### 闭包变量的C表示

在C代码中，闭包变量通过Nuitka_CellObject表示：

```c
// 闭包变量访问（非局部）
PyObject *y_value = PyCell_GET(closure->m_closed[0]);

// 修改闭包变量
PyCell_SET(closure->m_closed[0], new_value);
```

Cell对象是CPython标准的闭包机制，Nuitka直接使用相同的结构以保持兼容。

## 变量的C分配策略

Nuitka根据变量的逃逸情况和作用域，选择不同的C分配策略：

### 1. C局部变量（栈上）——最高效

**条件**：变量不被闭包引用、不被嵌套函数访问、不逃逸到函数外（不作为返回值/存入全局容器）。

```c
// 直接分配为C局部变量，PyObject*指针
PyObject *tmp_y = NULL;
tmp_y = PyLong_FromLong(42);
// 使用tmp_y...
Py_DECREF(tmp_y);  // 手动引用计数
```

**优化**：
- 不需要PyObject_HEAD开销
- 不需要字典查找
- INCREF/DECREF可以被优化掉（编译器证明引用在函数内）
- 如果Shape是int且不逃逸，可以直接用C long类型！

### 2. Cell变量（堆上）——闭包变量

**条件**：变量被闭包引用。

```c
// Cell对象在堆上分配
struct Nuitka_CellObject *cell_y;
cell_y = Nuitka_Cell_EMPTY();
cell_y->ob_ref = y_value;

// 内部函数通过closure数组访问
PyObject *y_value = PyCell_GET(self->m_closed[0]);
```

### 3. 模块全局变量

**条件**：模块级变量。

```c
// 模块变量存储在模块对象的md_dict字典中
PyObject *module_dict = MODULE_DICT(module);
PyDict_SetItemString(module_dict, "global_var", value);
// 或通过Nuitka模块的globals数组（缓存）
PyObject *global_var = module->m_globals[GLOBAL_VAR_X_INDEX];
```

### 4. 参数变量

**条件**：函数参数。

```c
// 参数从args数组直接获取
PyObject *par_x = args[0];  // 第一个参数
// *args和**kwargs通过StarListVariable/StarDictVariable处理
```

### 5. 临时变量（TempVariable）

**条件**：编译器在C代码生成时需要的中间变量，不对应任何Python变量。

```c
// Context分配临时变量
PyObject *tmp_result_1;
tmp_result_1 = PyObject_Call(...);
// 使用...
Py_DECREF(tmp_result_1);
// 作用域结束后自动释放，可被后续代码复用
```

## TempVariable 管理

[TempVariable](file:///d:/spaces/SpecWeave/playground/chaos/libs/Nuitka/nuitka/variables/TempVariable.py)是C代码生成中使用最频繁的变量类型。Context对象维护临时变量池：

### 分配与释放

```python
# 分配临时变量
tmp = context.allocateTempVariable("object", "calc_result")
# 生成: PyObject *tmp_calc_result_1;

# 使用临时变量
emit("%s = PyObject_CallObject(func, args);", tmp)

# 释放（归还池，可复用）
context.releaseTempVariable(tmp)
```

### 临时变量作用域

```python
# 进入if块
context.pushTempScope()
tmp1 = context.allocateTempVariable("object", "if_temp")
# ...使用tmp1...
# 退出if块：自动释放块内所有临时变量
context.popTempScope()
# tmp1已被释放，后续分配可复用该变量名
```

### 临时变量类型

| 类型名 | C类型 | 用途 |
|--------|-------|------|
| `"object"` | `PyObject *` | Python对象引用 |
| `"bool"` | `int`（0/1） | 布尔结果 |
| `"void_ptr"` | `void *` | 通用指针 |
| `"char_ptr"` | `char *` | C字符串 |
| `"frame_ptr"` | `struct Nuitka_FrameObject *` | 帧对象 |
| `"cell_ptr"` | `struct Nuitka_CellObject *` | Cell对象 |
| `"module_ptr"` | `struct Nuitka_ModuleObject *` | 模块对象 |
| `"long"` | `long`/`Py_ssize_t` | C整数 |

### 变量复用策略

为了减少C函数的局部变量数量（过多会影响寄存器分配和栈大小），Context实现了智能复用：

1. 同一作用域内释放的变量优先复用
2. 不同类型的变量不互相复用
3. 嵌套作用域的变量在外层作用域结束后才能复用
4. 跨语句的临时变量不合并

## 变量引用计数

Nuitka生成的C代码手动管理引用计数。每个变量的INCREF/DECREF策略：

| 变量类型 | 持有引用 | DECREF位置 |
|---------|---------|-----------|
| 局部C变量 | 持有一个引用 | 函数返回前或变量不再使用时 |
| 参数变量 | 借用引用（不持有） | 不需要DECREF |
| 临时变量 | 持有一个引用 | 作用域结束时 |
| Cell变量 | Cell持有引用 | Cell释放时 |
| 模块全局变量 | 字典持有引用 | 模块卸载时 |

```c
// 正确的引用计数示例
static PyObject *impl_add(PyThreadState *tstate, PyObject *arg0, PyObject *arg1) {
    PyObject *result;
    PyObject *left = arg0;     // 借用引用，不INCREF
    PyObject *right = arg1;    // 借用引用
    result = PyNumber_Add(left, right);  // 返回新引用
    return result;  // 调用者负责DECREF
}
```

### 逃逸分析影响引用计数

如果变量**不逃逸**（不被返回、不存入容器、不被闭包捕获），Nuitka可以优化掉INCREF/DECREF：

```c
// 原始代码: y = x + 1; return y
// 优化后：直接返回加法结果，跳过临时变量
return PyNumber_Add(x, PyLong_FromLong(1));
```

## 变量名到C标识符的映射

Python变量名映射到C标识符时需遵循C命名规则：

| Python名 | C标识符 | 规则 |
|---------|---------|------|
| `x` | `par_x`（参数）/ `var_x`（局部） | 加前缀 |
| `my_var` | `var_my_var` | 下划线保留 |
| `class`（关键字） | `var_class` | 关键字加前缀 |
| `my-var`（非法C名） | `var_my_2d_var` | 特殊字符编码 |
| `临时`（Unicode） | `var_$uid` | Unicode使用uid |

临时变量使用计数器命名：`tmp_1`, `tmp_2`, `return_value_1`等。
