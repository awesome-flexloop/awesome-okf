---
okf_version: "0.2"
type: Concept
title: "AST 树构建"
description: "从CPython AST到Nuitka内部节点树——buildParseTree、dispatch_dict调度、模块递归构建"
tags: ["nuitka", "ast", "parsing", "tree-building", "dispatch"]
sources:
  - id: REF-AST-001
    path: "nuitka/tree/Building.py"
    description: "AST→IR树构建核心"
  - id: REF-AST-002
    path: "nuitka/tree/SourceReferences.py"
    description: "源码位置引用"
  - id: REF-AST-003
    path: "nuitka/tree/Recursion.py"
    description: "递归导入控制"
prerequisites:
  - "00-introduction"
  - "01-compilation-pipeline"
  - "02-architecture-overview"
next:
  - "04-node-ir-system"
related:
  - "06-module-import-system"
  - "../references/node-base-api.md"
verified: true
status: active
---

# AST 树构建

Nuitka不自己实现Python语法解析器，而是**复用CPython的`ast`模块**将源码解析为标准AST，然后通过`tree/Building.py`中的调度机制将CPython AST节点转换为Nuitka自己的节点IR树。

## 构建入口

核心函数：buildParseTree()

```python
def buildParseTree(provider, source_code, source_ref, source_path, is_module, is_main):
    """
    provider:    变量提供者（通常是CompiledPythonModule）
    source_code: Python源代码字符串
    source_ref:  源码位置引用（SourceReference对象）
    source_path: 源文件路径
    is_module:   是否为模块顶层
    is_main:     是否为主脚本（__main__）
    """
    # 1. 使用CPython的ast.parse()解析源码
    try:
        ast_root = ast.parse(source_code, source_path)
    except SyntaxError as e:
        # ...错误处理...

    # 2. 设置__future__标志
    future_specs = _readFutureSpecs(ast_root)

    # 3. 构建模块体节点
    body = buildStatementsNode(provider, ast_root.body, source_ref)

    # 4. 如果是模块，创建ModuleNode
    if is_module:
        module = buildModuleNode(provider, body, is_main, source_ref, future_specs)
        return module

    return body
```

## dispatch_dict 调度机制

CPython AST有50+种节点类型（`ast.FunctionDef`, `ast.Call`, `ast.BinOp`, `ast.If`等），Nuitka通过一个全局`dispatch_dict`字典将AST节点类型映射到对应的构建函数：

```python
dispatch_dict = {
    "FunctionDef":      buildFunctionNode,
    "AsyncFunctionDef": buildAsyncFunctionNode,
    "ClassDef":         buildClassNode,
    "Return":           buildReturnNode,
    "Delete":           buildDeleteNode,
    "Assign":           buildAssignNode,
    "AugAssign":        buildAugAssignNode,
    "AnnAssign":        buildAnnAssignNode,
    "For":              buildForLoopNode,
    "AsyncFor":         buildAsyncForLoopNode,
    "While":            buildWhileLoopNode,
    "If":               buildIfNode,
    "With":             buildWithNode,
    "AsyncWith":        buildAsyncWithNode,
    "Raise":            buildRaiseNode,
    "Try":              buildTryNode,
    "Assert":           buildAssertNode,
    "Import":           buildImportNode,
    "ImportFrom":       buildImportFromNode,
    "Global":           buildGlobalNode,
    "Nonlocal":         buildNonlocalNode,
    "Expr":             buildExprNode,
    "Pass":             buildPassNode,
    "Break":            buildBreakNode,
    "Continue":         buildContinueNode,
    "Call":             buildCallNode,
    "Name":             buildNameNode,
    "Constant":         buildConstantNode,
    "Attribute":        buildAttributeNode,
    "Subscript":        buildSubscriptNode,
    "BinOp":            buildBinOpNode,
    "UnaryOp":          buildUnaryOpNode,
    "BoolOp":           buildBoolOpNode,
    "Compare":          buildCompareNode,
    "List":             buildListNode,
    "Tuple":            buildTupleNode,
    "Set":              buildSetNode,
    "Dict":             buildDictNode,
    "ListComp":         buildListCompNode,
    "SetComp":          buildSetCompNode,
    "DictComp":         buildDictCompNode,
    "GeneratorExp":     buildGeneratorExpressionNode,
    "Yield":            buildYieldNode,
    "YieldFrom":        buildYieldFromNode,
    "Await":            buildAwaitNode,
    "Lambda":           buildLambdaNode,
    "Slice":            buildSliceNode,
    "Starred":          buildStarredNode,
    "JoinedStr":        buildJoinedStrNode,
    "FormattedValue":   buildFormattedValueNode,
    "NamedExpr":        buildNamedExprNode,   # := 海象运算符
    "Match":            buildMatchNode,       # Python 3.10+ match
    # ...约50+种
}
```

`buildNode(ast_node, source_ref)`函数就是查表分发：

```python
def buildNode(provider, ast_node, source_ref, ...):
    kind = type(ast_node).__name__
    builder = dispatch_dict[kind]
    return builder(provider, ast_node, source_ref, ...)
```

## SourceReference 源码引用

每个Nuitka节点都携带一个SourceReference对象，记录该节点对应的源码位置：

- `filename`：源文件路径
- `line`：行号
- `column`：列号
- `future_spec`：`__future__`导入标志

SourceReference的作用：
1. **错误报告**：编译错误和运行时异常指向正确的源码位置
2. **调试信息**：C代码中生成`//`行号注释，调试器可映射回Python源码
3. **`__line__`/`__file__`**：支持代码中的行号和文件名引用
4. **Coverage**：代码覆盖率工具使用

## 递归构建过程

构建AST树是一个递归过程。以`def f(x): return x + 1`为例：

```
CPython AST:
Module(
  body=[
    FunctionDef(
      name='f',
      args=arguments(args=[arg(arg='x')]),
      body=[
        Return(
          value=BinOp(
            left=Name(id='x'),
            op=Add(),
            right=Constant(value=1)
          )
        )
      ]
    )
  ]
)
```

经过dispatch_dict转换后，构建出Nuitka节点树：

```
CompiledPythonModule
  └── ExpressionFunctionBody(name='f')
        ├── Parameter('x')
        └── StatementReturn
              └── ExpressionBinaryOperation(ADD)
                    ├── ExpressionVariableRef('x')
                    └── ExpressionConstantRef(1)
```

## 模块递归构建

当构建过程中遇到`import`或`from...import`语句时（`buildImportNode`/`buildImportFromNode`），会触发模块递归：

1. 调用importing.Importing.locateModule()定位被导入的模块文件
2. 根据`--follow-imports`选项和插件`onModuleEncountered`钩子，决定是否递归编译该模块
3. 如果决定跟随（recurseTo），则为该模块递归调用`buildParseTree()`构建其IR树
4. 已构建的模块存入ImportCache，避免重复构建

> 模块递归决策的详细逻辑见 [06-模块导入系统](06-module-import-system.md)。

## 构建时特殊处理

### __future__ 导入

Nuitka在构建树时解析`from __future__ import ...`语句，设置相应的编译标志：
- `annotations`：PEP 563延迟注解求值
- `generator_stop`：PEP 479生成器StopIteration处理
- 等

### 编码声明

处理`# -*- coding: utf-8 -*-`等PEP 263编码声明。

### 行号修正

处理装饰器、多行表达式等行号偏移问题，确保每个节点的source_ref指向正确的源码行。

### assert语句优化

`assert condition, message`在`--python-flag=-O`（优化模式）下会被跳过（不生成节点）。

## 设计模式总结

| 模式 | 应用 |
|------|------|
| **Dispatch字典** | `dispatch_dict`按kind字符串映射构建函数，比visitor模式更灵活 |
| **递归下降** | `buildNode`递归遍历CPython AST |
| **Builder模式** | 每种AST节点有独立的build*Node函数 |
| **SourceReference不可变** | 源码引用对象是不可变的，确保位置信息不会被意外修改 |
| **缓存机制** | ImportCache避免重复构建同一模块 |
