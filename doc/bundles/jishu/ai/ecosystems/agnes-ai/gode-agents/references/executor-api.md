---
type: Reference
title: Executor API 参考
description: codified-smolagents Python代码执行器API参考，包含PythonExecutor抽象基类、LocalPythonExecutor、E2BExecutor和DockerExecutor
tags: [Executor, PythonExecutor, LocalPythonExecutor, E2BExecutor, DockerExecutor, 沙箱执行, API参考]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T22:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T22:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: local-executor-source
    resource: ../../../../../../external/libs/models/AgnesAI/GodeAgents/Multi-Agent-Task/src/codified-smolagents/local_python_executor.py
    title: codified-smolagents/local_python_executor.py
  - id: remote-executors-source
    resource: ../../../../../../external/libs/models/AgnesAI/GodeAgents/Multi-Agent-Task/src/codified-smolagents/remote_executors.py
    title: codified-smolagents/remote_executors.py
---

# Executor API 参考

本文件记录 `local_python_executor.py` 和 `remote_executors.py` 模块中的Python代码执行器体系，基于源码零推测事实 F-105 ~ F-119 和 F-148 ~ F-150。

## 概述

代码执行器是CodeAgent的核心组件，负责在受控环境中安全执行LLM生成的Python代码。执行器体系包含三层：抽象基类`PythonExecutor`定义统一接口，`LocalPythonExecutor`在本地进程中通过AST分析和受限命名空间实现沙箱执行，`E2BExecutor`和`DockerExecutor`（均继承`RemotePythonExecutor`）在远程隔离环境中执行代码。所有执行器统一返回`(output, execution_logs, is_final_answer)`三元组。

> 事实溯源：F-110、F-112、F-148、F-149、F-150

## 安全常量

### BASE_BUILTIN_MODULES

```python
BASE_BUILTIN_MODULES: set
```

Python标准库模块名集合（从`sys.stdlib_module_names`衍生），作为CodeAgent默认授权导入列表的基础。

> 事实溯源：F-105、F-130

### 执行限制常量

```python
DEFAULT_MAX_LEN_OUTPUT = 50000  # print输出最大字符数
MAX_OPERATIONS = 10000000       # 最大操作数（防无限循环）
MAX_WHILE_ITERATIONS = 1000000  # while循环最大迭代次数
```

> 事实溯源：F-105

### 危险模块与函数黑名单

```python
DANGEROUS_MODULES = [
    "builtins", "io", "multiprocessing", "os", "pathlib",
    "pty", "shutil", "socket", "subprocess", "sys",
]

DANGEROUS_FUNCTIONS = [
    "builtins.compile", "builtins.eval", "builtins.exec",
    "builtins.globals", "builtins.locals", "builtins.__import__",
    "os.popen", "os.system", "posix.system",
]
```

禁止在沙箱中导入/调用的危险模块和函数列表。

> 事实溯源：F-106、F-107

### 安全内置工具

```python
BASE_PYTHON_TOOLS: dict
```

沙箱中可用的安全Python内置函数集合，包括：print（自定义空实现）、isinstance、range、类型转换函数（float/int/bool/str/set/list/dict/tuple/complex）、数学函数（ceil/floor/log/exp/sin/cos/tan等）、聚合函数（len/sum/max/min/abs/all/any）、迭代工具（enumerate/zip/reversed/sorted/map/filter）、其他工具（ord/chr/next/iter/divmod/callable/getattr/hasattr/setattr/issubclass/type/round/pow/sqrt）。

> 事实溯源：F-108

## 异常类

### InterpreterError

```python
class InterpreterError(ValueError)
```

解释器错误，当Python表达式无法求值时（语法错误或不支持的操作）抛出。

> 事实溯源：F-109

### FinalAnswerException

```python
class FinalAnswerException(Exception)
```

最终答案异常，用于在代码执行中通过`final_answer()`函数中断执行并返回结果。

**构造函数：**
```python
def __init__(self, value)
```
存储最终答案值在`self.value`中。

> 事实溯源：F-109（相关，从LocalPythonExecutor state中注入）

### 控制流异常

- `BreakException(Exception)`: 模拟break语句
- `ContinueException(Exception)`: 模拟continue语句
- `ReturnException(Exception)`: 模拟return语句，通过`self.value`存储返回值

## 辅助类

### PrintContainer

```python
class PrintContainer
```

在沙箱中捕获print输出的容器类，提供`append()`、`__iadd__`（+=运算符）、`__str__`、`__repr__`、`__len__`方法。

## PythonExecutor 抽象基类

```python
class PythonExecutor
```

Python代码执行器的抽象基类，定义统一的调用接口。

> 事实溯源：F-110

### 属性

- `final_answer_pattern`: 正则表达式`re.compile(r"^final_answer\((.*)\)$", re.M)`，用于检测代码中的`final_answer()`调用
- `state`: 执行命名空间状态字典
- `additional_imports`: 额外授权导入列表
- `logger`: 日志记录器
- `installed_packages`: 已安装包列表

### 核心方法

#### __call__

```python
def __call__(self, code_action: str) -> Tuple[Any, str, bool]
```

执行代码的统一入口。检测代码是否匹配`final_answer_pattern`，调用`run_code_raise_errors`执行代码。

**返回：** `Tuple[Any, str, bool]` — (输出值, 执行日志, 是否为最终答案)

> 事实溯源：F-111

#### run_code_raise_errors（抽象方法）

```python
def run_code_raise_errors(self, code: str, return_final_answer: bool = False) -> Tuple[Any, str]
```

执行代码并抛出异常的抽象方法，子类必须实现。

**参数：**
- `code` (`str`): 要执行的Python代码
- `return_final_answer` (`bool`): 是否需要提取final_answer返回值

**返回：** `Tuple[Any, str]` — (输出值, 执行日志)

#### send_tools

```python
def send_tools(self, tools: Dict[str, Tool])
```

将工具注入到执行环境中。使用`get_tools_definition_code`生成工具代码并在执行环境中定义。远程执行器还会自动安装工具依赖的包。

> 事实溯源：F-116

#### send_variables

```python
def send_variables(self, variables: dict)
```

将变量字典注入到执行环境的命名空间中。

> 事实溯源：F-117（LocalPythonExecutor）；F-148（RemotePythonExecutor使用pickle+base64）

## LocalPythonExecutor

```python
class LocalPythonExecutor(PythonExecutor)
```

本地Python代码执行器，通过AST静态分析和受限命名空间在当前进程中实现安全沙箱执行。

> 事实溯源：F-112

### 构造函数

```python
def __init__(
    self,
    additional_imports: List[str] | None = None,
    max_print_outputs_length: int | None = None,
)
```

**参数：**
- `additional_imports` (`List[str] | None`): 额外授权导入的模块列表
- `max_print_outputs_length` (`int | None`): print输出最大长度限制

**初始化state字典包含：**
- 安全的builtins（基于BASE_PYTHON_TOOLS，排除危险函数）
- 授权导入的模块（BASE_BUILTIN_MODULES + additional_imports）
- 自定义`final_answer`函数，调用时抛出`FinalAnswerException`
- `_print_outputs` PrintContainer用于捕获print输出

> 事实溯源：F-113、F-115

### 核心方法

#### run_code_raise_errors

```python
def run_code_raise_errors(self, code: str, return_final_answer: bool = False) -> Tuple[Any, str]
```

执行代码的核心方法：
1. 使用`ast.parse`解析代码
2. 通过`_check_imports` AST访问器验证import安全性（禁止DANGEROUS_MODULES和未授权模块）
3. 使用`compile`编译代码
4. 在受限命名空间（self.state）中通过`exec`执行
5. 捕获`FinalAnswerException`返回最终答案
6. 返回`(output, execution_logs)`元组

> 事实溯源：F-114

#### send_tools

```python
def send_tools(self, tools: Dict[str, Tool])
```

通过`get_tools_definition_code`生成工具定义代码，在沙箱命名空间中exec执行以注入工具实例。

> 事实溯源：F-116

#### send_variables

```python
def send_variables(self, variables: dict)
```

将variables字典更新到`self.state`中。

> 事实溯源：F-117

### AST安全机制

LocalPythonExecutor使用AST访问器进行静态安全检查：
- `_check_imports`: 遍历AST，验证所有import语句引用的模块在授权列表中
- `evaluate_ast`: 核心AST求值器，通过`@safer_eval`装饰器添加返回值安全检查，支持大部分Python语法节点（字面量、运算、控制流、函数调用、属性访问等），操作计数超限时抛出异常

> 事实溯源：F-119（evaluate_ast函数）

## RemotePythonExecutor

```python
class RemotePythonExecutor(PythonExecutor)
```

远程Python执行器抽象基类，为E2B和Docker执行器提供通用功能。

> 事实溯源：F-148

### 构造函数

```python
def __init__(self, additional_imports: List[str], logger)
```

初始化additional_imports、logger、final_answer_pattern、installed_packages。

### 核心方法

#### send_variables

```python
def send_variables(self, variables: dict)
```

使用pickle序列化+base64编码变量，生成代码在远程内核中反序列化并注入到locals命名空间。

> 事实溯源：F-148

#### send_tools

```python
def send_tools(self, tools: Dict[str, Tool])
```

生成工具定义代码，自动pip install工具依赖的包（未安装过的），然后在远程执行工具代码。

#### install_packages

```python
def install_packages(self, additional_imports: List[str]) -> List[str]
```

在远程环境中pip安装额外依赖包（包含smolagents）。

## E2BExecutor

```python
class E2BExecutor(RemotePythonExecutor)
```

使用E2B（e2b_code_interpreter.Sandbox）云沙箱执行Python代码。

> 事实溯源：F-149

### 构造函数

```python
def __init__(self, additional_imports: List[str], logger, **kwargs)
```

**参数：**
- `additional_imports` (`List[str]`): 额外需要安装的包
- `logger`: 日志记录器
- `**kwargs`: 传递给E2B Sandbox的额外参数

需要安装`smolagents[e2b]`扩展。初始化时创建E2B Sandbox实例，安装依赖包。

### run_code_raise_errors

```python
def run_code_raise_errors(self, code: str, return_final_answer: bool = False) -> Tuple[Any, str]
```

通过`self.sandbox.run_code(code)`执行代码。处理错误（error.name/value/traceback），解析执行结果（支持jpeg/png图像、chart/data/html/javascript/json/latex/markdown/pdf/svg/text等多种结果类型）。

## DockerExecutor

```python
class DockerExecutor(RemotePythonExecutor)
```

通过Jupyter Kernel Gateway在Docker容器中执行Python代码，使用WebSocket通信。

> 事实溯源：F-150

### 构造函数

```python
def __init__(
    self,
    additional_imports: List[str],
    logger,
    host: str = "127.0.0.1",
    port: int = 8888,
)
```

**参数：**
- `additional_imports` (`List[str]`): 额外需要安装的包
- `logger`: 日志记录器
- `host` (`str`, 默认`"127.0.0.1"`): Jupyter Kernel Gateway主机地址
- `port` (`int`, 默认`8888`): Jupyter Kernel Gateway端口

需要安装`smolagents[docker]`扩展（docker和websocket-client包）。初始化流程：
1. 连接Docker daemon
2. 构建jupyter-kernel镜像（如不存在Dockerfile则自动生成基于python:3.12-slim的镜像）
3. 启动容器并映射端口
4. 通过HTTP API创建Jupyter kernel
5. 建立WebSocket连接到kernel的channels端点
6. 安装依赖包

### 核心方法

#### run_code_raise_errors

```python
def run_code_raise_errors(self, code_action: str, return_final_answer: bool = False) -> Tuple[Any, str]
```

通过WebSocket发送execute_request消息，循环接收响应消息：
- `stream`消息：收集文本输出，检测"RESULT_PICKLE:"前缀提取pickle序列化结果
- `error`消息：拼接traceback抛出AgentError
- `status idle`消息：执行完成，退出循环

对于final_answer，代码被包装为pickle序列化结果并通过print输出。

#### cleanup

```python
def cleanup(self)
```

停止并删除Docker容器。在析构时（`__del__`/`delete`）自动调用。

## 辅助函数

### fix_final_answer_code

```python
def fix_final_answer_code(code: str) -> str
```

修复LLM对`final_answer`的错误使用：将直接赋值`final_answer = ...`替换为`final_answer_variable = ...`，保留`final_answer()`函数调用形式。使用正则`r"(?<!\.)(?<!\w)\bfinal_answer\s*="`匹配赋值语句。

> 事实溯源：F-118

### evaluate_ast

```python
def evaluate_ast(node, state, operations_counter)
```

核心AST求值器函数（@safer_eval装饰器），在受限环境中安全求值Python AST节点。支持：字面量、二元/一元运算、比较、布尔运算、条件表达式、控制流（if/for/while/break/continue/return）、函数定义与调用、属性访问、下标访问、列表/字典/集合推导式等。操作计数超限、未定义名称访问、危险操作都会抛出InterpreterError。

> 事实溯源：F-119

### 其他辅助函数

- `custom_print(*args)`: 沙箱中替换print的空函数（输出通过PrintContainer捕获）
- `get_iterable(obj)`: 安全获取可迭代对象
- `safer_eval(func)`: 装饰器，为AST求值函数添加返回值安全检查和操作计数限制

## 相关概念

- 代码执行智能体 — CodeAgent如何使用PythonExecutor
- 代码安全沙箱 — 执行安全机制与导入控制
- [智能体API参考](agents-api.md) — CodeAgent.create_python_executor方法
- [工具API参考](tools-api.md) — get_tools_definition_code工具注入
