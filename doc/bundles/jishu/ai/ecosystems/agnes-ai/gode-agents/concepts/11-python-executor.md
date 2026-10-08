---
type: Concept
title: Python 执行器与安全沙箱
description: LocalPythonExecutor的AST安全执行机制、禁止模块/函数列表、final_answer异常机制、远程执行器
tags: [执行器, 沙箱, 安全, Python, AST, E2B, Docker]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T12:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: F-105
    resource: /references/executor-api.md
    title: Executor API 参考
---

# Python 执行器与安全沙箱

## 概述

Python 执行器（Executor）是 CodeAgent 的核心运行时组件，负责在受控环境中安全执行 LLM 生成的 Python 代码。框架定义了 `PythonExecutor` 抽象基类，并提供三种具体实现：`LocalPythonExecutor`（本地受限沙箱）、`E2BExecutor`（E2B 云沙箱）和 `DockerExecutor`（Docker 容器沙箱）。本地执行器通过 AST 静态分析、模块/函数黑名单、受限命名空间三重机制保障代码安全，同时通过异常机制实现 `final_answer()` 提前返回和工具注入。理解执行器的安全机制和配置方式，是安全使用 CodeAgent 的前提。

> 事实溯源：F-105~F-119、F-148~F-150

## 核心概念

### 执行器层次结构

```
PythonExecutor（抽象基类）
├── LocalPythonExecutor（本地受限沙箱）
└── RemotePythonExecutor（远程执行抽象类）
    ├── E2BExecutor（E2B云沙箱）
    └── DockerExecutor（Docker容器沙箱）
```

- **LocalPythonExecutor**：在本地进程中通过 AST 检查 + 受限命名空间执行代码，默认安全选项
- **E2BExecutor**：通过 `e2b_code_interpreter.Sandbox` 在云端沙箱中执行
- **DockerExecutor**：通过 Jupyter Kernel Gateway 在 Docker 容器中执行，WebSocket 通信

> 事实溯源：F-110、F-112、F-148~F-150

### 安全执行三阶段（LocalPythonExecutor）

`LocalPythonExecutor.run_code_raise_errors()` 执行代码时经过三个安全关卡：

1. **AST 解析**（`ast.parse`）：将代码解析为抽象语法树，不执行任何代码
2. **Import 检查**（`_check_imports` AST 访问器）：遍历 AST 中所有 import 语句，对照黑名单和白名单验证
3. **受限执行**（`compile` + `exec`）：在仅包含安全内置函数和授权模块的受限命名空间中执行

任何阶段失败都会抛出异常，代码不会被执行。

> 事实溯源：F-114

### final_answer() 异常返回机制

在执行器的 state 字典中，`final_answer` 被定义为一个特殊函数，调用时抛出 `FinalAnswerException` 异常。执行器的 `__call__` 方法捕获此异常，将传入的值作为最终答案返回。这种异常驱动的机制使得 LLM 生成的代码可以在任意位置通过 `final_answer(result)` 提前终止执行并返回结果，无需走完所有步骤。

> 事实溯源：F-111、F-115

## API 要点

### PythonExecutor 抽象基类

```python
class PythonExecutor:
    """Python 代码执行器抽象基类"""

    # 正则模式：匹配 final_answer() 调用
    final_answer_pattern: re.Pattern

    # 执行状态字典
    state: dict

    # 额外授权导入的模块
    additional_imports: Optional[List[str]]

    # 日志记录器
    logger: Any

    # 已安装包集合
    installed_packages: set

    def __call__(self, code_action: str, **kwargs) -> Tuple[Any, str, bool]:
        """
        执行代码，返回三元组：
        (output, execution_logs, is_final_answer)
        - output: 执行结果或final_answer的值
        - execution_logs: 执行日志字符串
        - is_final_answer: 是否通过final_answer()返回
        """
        ...

    def run_code_raise_errors(self, code: str):
        """抽象方法：执行代码，出错时抛异常"""
        raise NotImplementedError
```

> 事实溯源：F-110~F-111

### 安全常量

```python
# 安全内置模块集合（Python标准库）
BASE_BUILTIN_MODULES: set

# 输出截断最大长度
DEFAULT_MAX_LEN_OUTPUT = 50000

# AST求值器最大操作数（防止无限计算）
MAX_OPERATIONS = 10000000

# while循环最大迭代次数（防止无限循环）
MAX_WHILE_ITERATIONS = 1000000
```

> 事实溯源：F-105

### 危险模块黑名单（DANGEROUS_MODULES）

以下模块被禁止导入，因为它们可用于绕过沙箱限制、访问文件系统或执行系统命令：

```python
DANGEROUS_MODULES = [
    "builtins",       # 内置模块（可直接访问所有Python内置）
    "io",             # 底层IO操作
    "multiprocessing",# 多进程（绕过GIL限制）
    "os",             # 操作系统接口
    "pathlib",        # 文件系统路径操作
    "pty",            # 伪终端
    "shutil",         # 高级文件操作
    "socket",         # 网络通信
    "subprocess",     # 子进程执行
    "sys",            # 系统相关参数和函数
]
```

> 事实溯源：F-106

### 危险函数黑名单（DANGEROUS_FUNCTIONS）

以下函数被显式禁止调用：

```python
DANGEROUS_FUNCTIONS = [
    "builtins.compile",      # 动态编译代码
    "builtins.eval",         # 动态求值表达式
    "builtins.exec",         # 动态执行代码
    "builtins.globals",      # 访问全局命名空间
    "builtins.locals",       # 访问局部命名空间
    "builtins.__import__",   # 底层导入函数
    "os.popen",              # 执行系统命令（管道）
    "os.system",             # 执行系统命令
    "posix.system",          # POSIX系统命令
]
```

> 事实溯源：F-107

### 安全内置函数集合（BASE_PYTHON_TOOLS）

执行器的受限命名空间中只包含以下安全内置函数：

| 函数 | 说明 |
|------|------|
| `print` | 被替换为 `custom_print`（返回 None，日志收集） |
| `isinstance` | 类型检查 |
| `range` | 范围生成 |
| `str`, `int`, `float`, `bool`, `bytes` | 类型构造/转换 |
| `list`, `dict`, `set`, `tuple` | 容器构造 |
| `len`, `sum`, `max`, `min`, `abs`, `round` | 基础数学/统计 |
| `enumerate`, `zip` | 迭代工具 |
| `sorted`, `reversed` | 排序/反转 |
| `filter`, `map` | 函数式工具 |
| `any`, `all` | 逻辑聚合 |

注意：`print` 被替换为 `custom_print`，其返回值为 `None`（原生 print 返回 None，但 custom_print 额外将输出收集到日志中）。

> 事实溯源：F-108

### 异常类层次

```python
class InterpreterError(ValueError):
    """代码解释/执行错误"""

class FinalAnswerException(Exception):
    """final_answer()调用，用于提前返回最终答案"""

class BreakException(Exception):
    """模拟Python的break语句"""

class ContinueException(Exception):
    """模拟Python的continue语句"""

class ReturnException(Exception):
    """模拟Python的return语句（在evaluate_ast中使用）"""
```

`BreakException`、`ContinueException`、`ReturnException` 是 `evaluate_ast` AST 求值器内部使用的控制流异常，用于在 AST 解释执行中模拟 Python 的控制流语句。

> 事实溯源：F-109

### LocalPythonExecutor

```python
class LocalPythonExecutor(PythonExecutor):
    """本地Python代码执行器（安全沙箱）"""

    def __init__(
        self,
        additional_authorized_imports: Optional[List[str]] = None,
        max_operations: int = MAX_OPERATIONS,
        max_while_iterations: int = MAX_WHILE_ITERATIONS,
    ):
        """
        初始化执行器：
        - 创建 state 字典，包含：
          - final_answer 函数（抛FinalAnswerException）
          - 安全builtins（BASE_PYTHON_TOOLS）
          - authorized_imports（授权导入集合）
        - print 被替换为 custom_print（返回None）
        """
        ...

    def run_code_raise_errors(self, code: str):
        """
        安全执行代码：
        1. ast.parse(code) → 解析为AST
        2. _check_imports AST访问器 → 验证import安全
        3. compile(code, '<>', 'exec') → 编译
        4. exec(compiled, self.state) → 在受限命名空间执行
        """
        ...

    def send_tools(self, tools: Dict[str, Tool]):
        """
        通过get_tools_definition_code生成工具代码，
        在命名空间中exec执行，将工具实例注入为可调用函数。
        """
        ...

    def send_variables(self, variables: dict):
        """将variables字典更新到self.state"""
        self.state.update(variables)
```

> 事实溯源：F-112~F-117

### fix_final_answer_code()

```python
def fix_final_answer_code(code: str) -> str:
    """
    修复LLM常见错误：将 final_answer = ... （赋值）
    替换为 final_answer_variable = ...
    防止覆盖state中的final_answer函数。
    """
    ...
```

LLM 有时会错误地将 `final_answer(result)` 生成为 `final_answer = result`，这会覆盖 state 中的 `final_answer` 函数，导致后续无法正常返回答案。`fix_final_answer_code()` 在执行前修复此问题。

> 事实溯源：F-118

### evaluate_ast：核心AST求值器

```python
@safer_eval
def evaluate_ast(node, state, ...):
    """
    核心AST求值器，@safer_eval装饰器添加返回值安全检查。
    支持大部分Python语法节点的解释执行：
    - 表达式、赋值、函数调用
    - 控制流（if/for/while/break/continue/return）
    - 函数定义、类定义
    - 运算、比较、布尔运算
    - 列表/字典/集合推导式
    受MAX_OPERATIONS和MAX_WHILE_ITERATIONS限制。
    """
    ...
```

`@safer_eval` 装饰器在求值完成后对返回值进行安全检查，防止返回危险对象（如模块引用、内部对象等）。

> 事实溯源：F-119

### 远程执行器

```python
class RemotePythonExecutor(PythonExecutor):
    """远程Python执行器抽象基类"""

    def send_variables(self, variables: dict):
        """使用pickle+base64序列化变量后发送到远程环境"""
        ...

class E2BExecutor(RemotePythonExecutor):
    """使用e2b_code_interpreter.Sandbox在E2B云沙箱中执行代码"""
    def __init__(self, ...):
        # 初始化E2B Sandbox
        ...

class DockerExecutor(RemotePythonExecutor):
    """通过Jupyter Kernel Gateway在Docker容器中执行，WebSocket通信"""
    def __init__(self, ...):
        # 连接Docker容器中的Jupyter Kernel
        ...
```

远程执行器的 `send_variables()` 使用 pickle 序列化 + base64 编码将变量传输到远程执行环境。

> 事实溯源：F-148~F-150

## 代码示例

### 使用 LocalPythonExecutor 执行安全代码

```python
from codified_smolagents import LocalPythonExecutor

# 创建执行器，授权导入math模块
executor = LocalPythonExecutor(
    additional_authorized_imports=['math', 'random'],
)

# 注入变量
executor.send_variables({"x": 10, "y": 20})

# 执行代码
code = """
import math
result = math.sqrt(x**2 + y**2)
print(f"斜边长度: {result}")
final_answer(result)
"""

output, logs, is_final = executor(code)
print(f"输出: {output}")      # 22.360679775...
print(f"日志: {logs}")        # "斜边长度: 22.360679775..."
print(f"是否最终答案: {is_final}")  # True
```

### 注入工具到执行器

```python
from codified_smolagents import LocalPythonExecutor, tool

@tool
def add(a: int, b: int) -> int:
    """计算两个整数的和。

    Args:
        a: 第一个整数
        b: 第二个整数

    Returns:
        两数之和
    """
    return a + b

@tool
def multiply(a: int, b: int) -> int:
    """计算两个整数的乘积。

    Args:
        a: 第一个整数
        b: 第二个整数

    Returns:
        两数乘积
    """
    return a * b

executor = LocalPythonExecutor(additional_authorized_imports=[])

# 注入工具（工具将作为函数在代码中可直接调用）
executor.send_tools({"add": add, "multiply": multiply})

# 执行使用工具的代码
code = """
result1 = add(3, 4)
result2 = multiply(result1, 5)
final_answer(f"3+4={result1}, 乘以5={result2}")
"""

output, logs, is_final = executor(code)
print(output)  # "3+4=7, 乘以5=35"
```

### 安全限制演示

```python
from codified_smolagents import LocalPythonExecutor

executor = LocalPythonExecutor(additional_authorized_imports=[])

# 尝试导入危险模块 → 抛出异常
try:
    executor("import os\nos.system('echo hacked')")
except Exception as e:
    print(f"被安全机制拦截: {type(e).__name__}")

# 尝试调用eval → 被拦截
try:
    executor("result = eval('1+1')")
except Exception as e:
    print(f"eval被拦截: {type(e).__name__}")

# 尝试使用__import__ → 被拦截
try:
    executor("os_mod = __import__('os')")
except Exception as e:
    print(f"__import__被拦截: {type(e).__name__}")

# 授权导入可以正常使用
executor2 = LocalPythonExecutor(additional_authorized_imports=['math'])
output, _, _ = executor2("""
import math
final_answer(math.pi)
""")
print(f"授权导入math: pi = {output}")
```

### fix_final_answer_code 修复LLM错误

```python
from codified_smolagents import LocalPythonExecutor
from codified_smolagents.utils import fix_final_answer_code

# LLM可能生成的错误代码（将final_answer当作变量赋值）
bad_code = """
result = 42
final_answer = result  # 错误！这会覆盖final_answer函数
"""

# 修复后
fixed_code = fix_final_answer_code(bad_code)
print(fixed_code)
# 输出:
# result = 42
# final_answer_variable = result  # 变量名被替换

# 正确的代码（函数调用方式）
good_code = """
result = 42
final_answer(result)  # 正确：调用final_answer函数
"""

executor = LocalPythonExecutor()
output, logs, is_final = executor(good_code)
print(f"结果: {output}, is_final: {is_final}")  # 42, True
```

### 使用 E2BExecutor 远程执行

```python
from codified_smolagents import E2BExecutor

# 创建E2B远程执行器（需要E2B API Key）
# executor = E2BExecutor(
#     additional_authorized_imports=['numpy', 'pandas'],
# )
# 
# # 远程执行代码
# output, logs, is_final = executor("""
# import numpy as np
# arr = np.array([1, 2, 3, 4, 5])
# final_answer(arr.mean())
# """)
# print(output)  # 3.0
```

### 使用 DockerExecutor 容器执行

```python
from codified_smolagents import DockerExecutor

# 创建Docker执行器（需要Docker环境和Jupyter Kernel Gateway镜像）
# executor = DockerExecutor(
#     additional_authorized_imports=['numpy', 'matplotlib'],
#     image="jupyter/scipy-notebook",  # Docker镜像
# )
# 
# output, logs, is_final = executor("""
# import numpy as np
# data = np.random.randn(1000)
# final_answer({"mean": float(data.mean()), "std": float(data.std())})
# """)
```

### CodeAgent 中配置执行器

```python
from codified_smolagents import CodeAgent, HfApiModel, LocalPythonExecutor

# 默认使用LocalPythonExecutor
model = HfApiModel()
agent = CodeAgent(
    tools=[],
    model=model,
    additional_authorized_imports=['math', 'datetime', 'collections'],
    max_steps=5,
)
# CodeAgent内部自动创建LocalPythonExecutor并管理其生命周期
result = agent.run("计算1到100所有质数的和")
print(result)
```

> 事实溯源：F-105~F-119、F-148~F-150

## 注意事项

### additional_authorized_imports 是白名单机制

只有在 `additional_authorized_imports` 中列出的模块才能被导入，且必须属于 `BASE_BUILTIN_MODULES`（Python 标准库）或已安装的第三方包。未列出的模块在 AST 检查阶段就会被拒绝，代码不会被执行。每次授权新模块时应评估其安全性。

### print 被替换为 custom_print

在执行器的 state 中，`print` 函数被替换为 `custom_print`，它将输出收集到日志字符串中并返回 `None`。这意味着代码中 `result = print("hello")` 会得到 `result = None`，这是正常行为。

### final_answer() 不是 return

`final_answer()` 通过抛异常实现提前返回，不是 Python 的 `return` 语句。它只能在执行器的代码中直接调用，不能在自定义函数内部替代 return——在自定义函数中调用 `final_answer()` 仍然会直接终止整个代码执行。

### MAX_OPERATIONS 和 MAX_WHILE_ITERATIONS 防止拒绝服务

- `MAX_OPERATIONS = 10000000`：限制 AST 求值器执行的操作总数，防止恶意代码进行超大计算量操作
- `MAX_WHILE_ITERATIONS = 1000000`：限制 while 循环最大迭代次数，防止无限循环
超出限制会抛出异常终止执行。在 LocalPythonExecutor 构造时可自定义这两个值。

### 远程执行器依赖外部环境

- **E2BExecutor**：需要 `e2b_code_interpreter` 包和有效的 E2B API Key，代码在 E2B 云端沙箱中运行
- **DockerExecutor**：需要本地 Docker 环境、Jupyter Kernel Gateway 镜像，通过 WebSocket 与容器通信
远程执行器在网络不可用或依赖缺失时无法使用。

### evaluate_ast 与 exec 是两条执行路径

LocalPythonExecutor 使用 `compile` + `exec` 执行代码，而 `evaluate_ast` 是框架内部使用的 AST 解释器（用于工具返回值等场景的安全求值），带有 `@safer_eval` 装饰器做额外的返回值检查。两者都有资源限制保护。

### 危险模块/函数列表是黑名单而非白名单

安全策略采用"默认拒绝 + 白名单授权"模式：除了 `BASE_PYTHON_TOOLS` 中的安全函数和 `additional_authorized_imports` 中授权的模块，其他都不可用。`DANGEROUS_MODULES` 和 `DANGEROUS_FUNCTIONS` 是已知危险项的显式列表，但不是完整列表——安全机制不仅依赖黑名单，还依赖受限命名空间和 AST 检查。

## 相关链接

- [CodeAgent：代码执行范式](06-code-agent.md) — CodeAgent如何使用PythonExecutor
- [工具系统：@tool装饰器与Tool基类](07-tool-system.md) — get_tools_definition_code与send_tools
- [AgentType 多模态类型系统](10-agent-types.md) — 多模态数据在执行器中的传递
- [监控与日志](13-monitoring-logging.md) — 执行日志与错误处理
- [Executor API 参考](../references/executor-api.md) — 执行器完整API
