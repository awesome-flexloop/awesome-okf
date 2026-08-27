---
okf_version: "0.2"
type: Concept
title: "模块导入系统"
description: "Nuitka模块导入——locateModule定位、recurseTo递归决策、ImportCache缓存、字节码降级机制"
tags: ["nuitka", "import", "module", "recursion", "cache", "bytecode"]
sources:
  - id: REF-IMP-001
    path: "nuitka/importing/Importing.py"
    description: "模块定位与递归核心"
  - id: REF-IMP-002
    path: "nuitka/importing/ImportCache.py"
    description: "模块缓存"
  - id: REF-IMP-003
    path: "nuitka/importing/Recursion.py"
    description: "递归决策逻辑"
  - id: REF-IMP-004
    path: "nuitka/ModuleRegistry.py"
    description: "模块注册表"
prerequisites:
  - "03-ast-tree-building"
  - "04-node-ir-system"
next:
  - "07-optimization-passes"
related:
  - "11-plugin-system"
  - "../references/main-control-entry.md"
verified: true
status: active
---

# 模块导入系统

Nuitka的模块导入系统负责发现和编译所有被依赖的Python模块。这是一个复杂的过程，因为Python的导入机制本身非常动态（支持`__import__()`、importlib、命名空间包、.pth文件、C扩展等），而Nuitka需要在编译时静态确定哪些模块需要被编译。

## 核心挑战

Python导入的动态特性给静态编译带来了挑战：
1. **动态导入**：`__import__(name)`、`importlib.import_module(name)`中name可能是运行时值
2. **隐式导入**：某些模块在导入时会自动加载其他模块（如C扩展的初始化函数）
3. **条件导入**：`if sys.platform == "win32": import winreg`
4. **命名空间包**：PEP 420命名空间包没有`__init__.py`
5. **C扩展模块**：.pyd/.so文件无法编译为C，需要作为二进制依赖
6. **标准库策略**：标准库模块默认不编译（使用字节码），减少编译时间

## locateModule：模块定位

locateModule()是模块发现的核心公共API：

```python
def locateModule(module_name, parent_package=None, level=0):
    """
    定位一个Python模块。
    
    返回四元组: (finding, module_filename, module_kind, source_ref)
    - finding: 查找结果状态
    """
```

### finding 结果类型

| finding值 | 含义 | 处理方式 |
|-----------|------|---------|
| `absolute` | 找到绝对导入的.py模块 | 编译为CompiledPythonModule |
| `relative` | 找到相对导入的.py模块 | 编译为CompiledPythonModule |
| `built-in` | 内置模块（如sys、os部分功能） | 标记为内置，不编译 |
| `not-found` | 模块不存在 | 编译错误或延迟到运行时 |
| `fake` | 由插件提供的假模块（用于接口stub） | 使用插件提供的实现 |
| `pth` | 通过.pth文件发现的模块 | 按普通模块处理 |

### 定位流程

```
locateModule(module_name)
  ├── 检查 ImportCache（是否已定位）
  │     └── 命中 → 返回缓存结果
  ├── 查询插件 onModuleEncountered() 钩子
  │     └── 插件决定是否处理
  ├── 搜索 sys.path（模拟Python导入路径搜索）
  │     ├── 查找 package/__init__.py（包）
  │     ├── 查找 module.py（单文件模块）
  │     ├── 查找 module/__init__.py（命名空间包→包）
  │     ├── 查找 module.pyd/module.so（C扩展）
  │     └── 查找内置模块表（sys.builtin_module_names）
  ├── 检查 .pth 文件（如site-packages中的路径配置）
  └── 结果存入 ImportCache
```

## recurseTo：递归编译决策

找到模块后，recurseTo()决定是否递归编译该模块：

```python
def recurseTo(module_name, parent_package=None, ...):
    """递归到指定模块，决定是否编译，并构建其IR树。"""
```

### decideRecursion 决策逻辑

decideRecursion()综合多个因素决定是否跟随导入：

1. **用户选项**：
   - `--follow-imports`：跟随所有导入（默认）
   - `--nofollow-imports`：不跟随任何导入
   - `--follow-import-to=mod1,mod2`：仅跟随指定模块
   - `--nofollow-import-to=mod1,mod2`：不跟随指定模块
   - `--follow-stdlib`：也编译标准库模块（默认不编译）
   - `--follow-no-test`：不跟随test/tests目录

2. **PGO（Profile-Guided Optimization）数据**：
   - 如果使用`--pgo`，根据实际运行时的模块使用记录决定
   - 运行时没用到的模块不编译

3. **插件决策**：
   - `Plugins.onModuleEncountered(module_name, module_filename)`
   - 插件可以返回True（跟随）、False（不跟随）或None（默认决策）

4. **标准库策略**：
   - 标准库模块默认**不编译**（使用Python原生字节码）
   - 原因：标准库模块代码量大、编译耗时长、且C扩展多
   - 使用`--follow-stdlib`可强制编译标准库

5. **编译模式决策**：
   - 决定跟随的模块进入`decideCompilationMode()`判断：
     - `"compiled"`：完整编译为C代码（CompiledPythonModule）
     - `"bytecode"`：保留为字节码（UncompiledPythonModule），不编译树

### 编译模式：Compiled vs Bytecode

| 模式 | 类 | 处理方式 | 用途 |
|------|-----|---------|------|
| compiled | CompiledPythonModule | 完整构建IR树→优化→生成C→编译 | 用户代码、第三方库 |
| bytecode | UncompiledPythonModule | 读取.pyc字节码→冻结到二进制 | 标准库、未跟随的模块 |

**字节码降级（BytecodeDemotion）**：在优化阶段，如果一个"compiled"模块被发现几乎没有性能收益（如纯数据模块、启动模块），可以通过`demoteCompiledModuleToBytecode()`动态降级为bytecode模式，节省编译时间。

## ImportCache：全局模块缓存

ImportCache维护两个全局字典：

```python
imported_modules = {}     # module_name → ModuleNode 实例
imported_by_name = {}     # (module_name, parent_package) → ModuleNode
```

缓存的作用：
1. **避免重复编译**：同一模块被多处import时只构建一次树
2. **循环导入处理**：检测和处理模块间的循环导入
3. **模块查找加速**：后续locateModule调用直接返回缓存结果

## ModuleRegistry：模块注册表

ModuleRegistry维护所有已完成构建的模块列表：

```python
# 核心API
ModuleRegistry.getDoneModules()      # 返回所有已完成构建的模块
ModuleRegistry.getRootModules()      # 返回根模块（非被导入的）
ModuleRegistry.getModuleFromName(name) # 按名称查找模块
ModuleRegistry.addModule(module)     # 添加模块到注册表
```

优化阶段遍历`getDoneModules()`对每个模块执行优化。

## 隐式导入检测

某些模块在CPython启动时自动加载，用户代码中没有显式的import语句。Nuitka通过freezer/ImportDetection.py处理这个问题：

1. 启动一个**子进程**运行Python解释器（`python -s -S -v`）
2. `-s -S`跳过site模块和用户site目录，`-v`输出导入信息
3. 解析stderr中的import日志，提取所有自动加载的模块
4. 这些"frozen stdlib"模块被标记为bytecode模式，嵌入到最终二进制中
5. 插件也可以通过`getImplicitImports()`提供模块的隐式导入列表

## 模块构建递归流程

```
_createMainModule(main_filename)
  └── locateModule("__main__")
        └── buildParseTree(main_module)
              ├── 遍历AST遇到import语句
              │     └── buildImportNode / buildImportFromNode
              │           └── locateModule(imported_name)
              │                 └── decideRecursion()?
              │                       ├── 是 → recurseTo()
              │                       │     └── buildParseTree(imported_module)
              │                       │           └── [递归]
              │                       └── 否 → 标记为runtime import
              └── 模块树构建完成
                    └── 添加到ModuleRegistry
```

## 插件对导入系统的干预

插件在导入系统的多个点可以干预：

| 钩子 | 作用 |
|------|------|
| `onModuleEncountered(module_name, filename)` | 决定是否跟随某模块 |
| `decideCompilation(module, module_name)` | 覆盖编译模式（compiled/bytecode） |
| `getImplicitImports(module)` | 提供模块的隐式导入列表 |
| `onModuleSourceCode(module_name, source_code)` | 修改模块源码（如打补丁） |
| `createPreLoadedModule(module_name, code)` | 提供fake模块（替换真实模块） |
| `onModuleDiscovered(module)` | 模块刚被发现时的回调 |

> 插件系统详见 [11-插件系统](11-plugin-system.md)。

## 设计要点

1. **延迟递归**：不是一次性扫描所有依赖，而是在树构建过程中按需触发递归，减少不必要的工作
2. **缓存优先**：ImportCache确保每个模块只处理一次
3. **两阶段决策**：先decideRecursion（是否跟随），再decideCompilation（compiled还是bytecode）
4. **动态降级**：BytecodeDemotion允许优化阶段改变编译决策
5. **子进程检测**：通过子进程获取CPython真实的模块加载行为，而非静态猜测
