---
type: concept
title: "05 - 代码执行管线"
description: IPython 六阶段代码执行管线——输入转换、预过滤、编译、执行、显示、历史与事件，同步/异步双路径
tags: [execution, pipeline, run-cell, compile, async, display-hook, ast]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: ipython-interactiveshell
    title: IPython/core/interactiveshell.py
  - id: ipython-inputtransformer
    title: IPython/core/inputtransformer2.py
  - id: ipython-compilerop
    title: IPython/core/compilerop.py
---

## 六阶段执行管线概述

`run_cell()` 是 IPython 代码执行的核心入口 [F-216]。用户输入的原始代码从字符串到最终显示结果，经过六个有序阶段。同步路径通过 `run_cell()` 入口，异步路径通过 `run_cell_async()` 入口，两者共享大部分管线逻辑。

```
用户输入 (raw_cell: str)
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ 阶段 1: 输入转换 (Input Transformation)                       │
│                                                             │
│ transform_cell(raw_cell) → TransformerManager [F-219]      │
│ ├── 剥离前导空行 (leading_empty_lines)                       │
│ ├── 移除公共前导缩进 (leading_indent)                        │
│ ├── ESC_MAGIC(%)  → get_ipython().run_line_magic()          │
│ ├── ESC_MAGIC2(%%) → get_ipython().run_cell_magic()         │
│ ├── System(!/!!)  → get_ipython().system()                  │
│ ├── Help(?/??)    → pinfo()/pinfo2()                        │
│ └── PromptStripper → 移除 >>> 和 ... 提示符                 │
│                                                             │
│ 输出: 可被 Python 编译器接受的标准 Python 代码字符串           │
└─────────────────────────┬───────────────────────────────────┘
                          │ transformed_cell (str)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 阶段 2: 预过滤 (Prefilter)                                   │
│                                                             │
│ PrefilterManager [F-460]                                   │
│ ├── AutoMagic 检测与转换（automagic 模式下无前缀行魔法）       │
│ ├── Alias 展开（系统命令别名替换）                            │
│ └── ESC 命令处理                                             │
│                                                             │
│ 注意：InputTransformer2 已处理大部分语法转换，                 │
│       PrefilterManager 主要处理 automagic 和 alias           │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 阶段 3: 异步检测 (Async Detection)                           │
│                                                             │
│ should_run_async(raw_cell) [F-218][F-480]                  │
│ ├── _should_be_async(cell) → 编译代码检查 CO_COROUTINE 标志  │
│ ├── 检测顶层 await/async for/async with                     │
│ └── 决定走同步路径还是异步路径                                │
│                                                             │
│ 同步路径 → run_ast_nodes → run_code (sync)                  │
│ 异步路径 → run_cell_async → 包装为 async def + runner       │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 阶段 4: 编译 (Compile)                                       │
│                                                             │
│ CachingCompiler [F-450][F-451]                             │
│ ├── 继承 codeop.Compile                                     │
│ ├── 将源码编译为 AST                                        │
│ ├── 将 AST 编译为 code object                                │
│ ├── 缓存编译结果（文件名+源码 → code object）                │
│ ├── 文件名管理: <ipython-input-N-hash> [F-452]              │
│ └── 支持增量编译（多行 cell 逐行编译）                        │
│                                                             │
│ 编译失败 → SyntaxError，不进入执行阶段                        │
└─────────────────────────┬───────────────────────────────────┘
                          │ code object
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 阶段 5: 事件通知 + 执行 (Events + Execute)                   │
│                                                             │
│ events.trigger('pre_run_cell', info) [F-367]               │
│ events.trigger('pre_execute')                              │
│                                                             │
│ run_ast_nodes(nodes, cell_name) [F-220]                    │
│ ├── 遍历 AST 节点                                           │
│ ├── 根据 ast_node_interactivity 决定显示哪些节点 [F-212]    │
│ ├── 调用 exec(code, user_globals, user_ns)                  │
│ │                                                           │
│ ├── [同步] run_code(code_obj, async_=False) [F-221]        │
│ └── [异步] run_code(code_obj, async_=True)                 │
│     ├── 包装为 async def __async_exec(): ...                 │
│     ├── 通过 _asyncio_runner/_trio_runner/_curio_runner    │
│     │   或 _pseudo_sync_runner 执行 [F-481][F-482]         │
│     └── 支持顶层 await                                      │
│                                                             │
│ events.trigger('post_execute')                             │
│ events.trigger('post_run_cell', result) [F-367]            │
└─────────────────────────┬───────────────────────────────────┘
                          │ execution result
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ 阶段 6: 显示 + 历史 (Display + History)                      │
│                                                             │
│ DisplayHook (sys.displayhook) [F-400]                      │
│ ├── 接收表达式结果                                          │
│ ├── 调用 DisplayFormatter 格式化 [F-380]                    │
│ ├── 调用 DisplayPublisher.publish() 发布 [F-390]           │
│ │   ├── 终端: 写入 stdout                                   │
│ │   └── Jupyter: 发送 display_data 消息                     │
│ ├── 更新 Out[N] / _ / __ / ___                             │
│ └── 更新 execution_count                                   │
│                                                             │
│ HistoryManager [F-422]                                     │
│ ├── 将输入/输出写入 SQLite（异步线程）[F-424]               │
│ └── 更新 In[N] / _ih                                       │
└─────────────────────────────────────────────────────────────┘
```

## 核心入口方法

### run_cell() 同步入口

```python
def run_cell(self, raw_cell, store_history=False, silent=False):
    """执行一个代码单元 [F-216]"""
    # 1. 输入转换
    cell = self.transform_cell(raw_cell)
    # 2. 异步检测
    if self.should_run_async(raw_cell):
        # 委托给异步路径
        return self.run_cell_async(raw_cell, store_history, silent)
    # 3. 编译 + 执行 + 显示
    result = self._run_cell(cell, raw_cell, store_history, silent)
    return result
```

### run_cell_async() 异步入口

```python
async def run_cell_async(self, raw_cell, store_history=False, silent=False, 
                         shell_futures=True):
    """异步执行一个代码单元 [F-217]"""
    # 与 run_cell 类似，但使用 await 执行异步代码
    # 支持顶层 await、async for、async with
    ...
```

### should_run_async() 异步检测

```python
def should_run_async(self, raw_cell):
    """判断代码是否需要异步执行 [F-218]"""
    # 内部调用 _should_be_async(cell) [F-480]
    # 通过编译代码并检查 CO_COROUTINE 标志来检测
    # 处理顶层 return/yield 的特殊情况
```

`_should_be_async()` 使用 Python 编译器的 `PyCF_ALLOW_TOP_LEVEL_AWAIT` 标志编译代码，然后检查 `co_flags` 中是否设置了 `CO_COROUTINE` 位 [F-480]：

```python
def _should_be_async(cell: str) -> bool:
    code = compile(cell, "<>", "exec", 
                   flags=getattr(ast, "PyCF_ALLOW_TOP_LEVEL_AWAIT", 0x0))
    return inspect.CO_COROUTINE & code.co_flags == inspect.CO_COROUTINE
```

### transform_cell() 输入转换

```python
def transform_cell(self, raw_cell):
    """转换原始输入为标准 Python 代码 [F-219]"""
    # 委托给 input_transformer_manager
    return self.input_transformer_manager.transform_cell(raw_cell)
```

### run_ast_nodes() 与 run_code()

```python
def run_ast_nodes(self, nodelist, cell_name, interactivity="last_expr", ...):
    """执行 AST 节点列表 [F-220]"""
    # 遍历节点，根据 interactivity（即 ast_node_interactivity）
    # 决定哪些节点的结果需要显示
    for node in nodelist:
        # 编译节点
        code = self.compile(ast_mod, cell_name, "exec" if ... else "eval")
        # 执行
        self.run_code(code, result, async_=self.autoawait)

def run_code(self, code_obj, result=None, *, async_=False):
    """执行编译后的 code object [F-221]"""
    # 在 user_ns/user_global_ns 中 exec code_obj
    # 处理异常、显示结果
```

## CachingCompiler 缓存编译器

`CachingCompiler` 继承自 `codeop.Compile`，提供编译结果缓存 [F-450][F-451]：

```python
class CachingCompiler(codeop.Compile):
    """缓存编译结果的编译器"""
    
    def __init__(self):
        self._filename_cache = {}  # 源码 hash → 文件名映射
        self._code_cache = {}      # (filename, source) → code object
    
    def get_code_name(self, code_name, code):
        """生成带 hash 的文件名: <ipython-input-N-hash> [F-452]"""
        ...
    
    def anonymize(self, code_name):
        """匿名化文件名（用于错误报告）"""
        ...
```

缓存带来的好处：
- 重复执行相同代码时跳过编译步骤
- 文件名包含 hash，便于缓存失效判断
- 正确处理 IPython 的错误行号映射

## ast_node_interactivity 显示策略

`ast_node_interactivity` 控制哪些 AST 节点的结果会被自动显示 [F-212]：

```python
# 'last_expr'（默认）：仅最后一个表达式语句
# 输入: x = 1; y = 2; x + y
# 显示: 3（只显示最后一个表达式）

# 'all'：所有表达式语句
# 输入: x = 1; y = 2; x + y
# 显示: 1, 2, 3

# 'last_expr_or_assign'：最后表达式或赋值的右值
# 输入: x = 42
# 显示: 42

# 'none'：不自动显示任何结果
# 'last'：最后一个语句
```

## 异步执行机制

当 `should_run_async()` 返回 True 时，IPython 将整个代码单元包装在一个 async 函数中执行 [F-481][F-482]：

```
异步代码:
  await some_coroutine()
  │
  ▼ IPython AST 改写
async def __async_exec_cell():
    await some_coroutine()
  │
  ▼ 通过异步运行器执行
runner(__async_exec_cell())
```

### 异步运行器

IPython 支持三种异步运行器 [F-481]：

```python
# 1. asyncio 运行器（默认）[F-483]
class _AsyncIORunner:
    def __call__(self, coro):
        return get_asyncio_loop().run_until_complete(coro)

_asyncio_runner = _AsyncIORunner()

# 2. Trio 运行器
def _trio_runner(async_fn):
    import trio
    async def loc(coro):
        return await coro
    return trio.run(loc, async_fn)

# 3. Curio 运行器
def _curio_runner(coroutine):
    import curio
    return curio.run(coroutine)

# 4. 伪同步运行器（无事件循环环境）
def _pseudo_sync_runner(coro):
    """不真正运行事件循环，仅推进 coroutine 一步 [F-482]"""
    try:
        coro.send(None)
    except StopIteration as exc:
        return exc.value
    else:
        raise RuntimeError(f"{coro.__name__!r} needs a real async loop")
```

运行器通过 `shell.loop_runner` 或 `%autoawait` 魔法切换。`_pseudo_sync_runner` 只能执行不真正 await 的协程，遇到实际异步操作会抛出 RuntimeError。

### _AsyncIOProxy

`_AsyncIOProxy` 用于在线程安全地调用异步方法 [F-483]，通过 `asyncio.run_coroutine_threadsafe` 将协程调度到事件循环线程。

## 异常处理

执行过程中的异常被捕获并通过 ultratb 模块格式化 [F-493]：

```python
try:
    exec(code, self.user_global_ns, self.user_ns)
except:
    self.showtraceback()
    # 根据 xmode 设置格式化 traceback
    # 如果 pdb=True，自动启动调试器
    result.error_in_exec = sys.exc_info()
```

异常信息存入 `ExecutionResult.error_in_exec`，并设置 `last_execution_succeeded = False` [F-230]。

## ExecutionResult 执行结果

每次 run_cell() 返回一个 ExecutionResult 对象：

```python
class ExecutionResult:
    """代码执行结果"""
    success: bool           # 编译和执行是否都成功
    error_before_exec: Any  # 编译阶段错误（SyntaxError 等）
    error_in_exec: Any      # 执行阶段错误（异常信息）
    info: ExecutionInfo     # 执行元信息（原始代码、cell 名等）
    result: Any             # 最后一个表达式的返回值
```

## 魔法命令的执行路径

魔法命令在阶段 1（输入转换）就被转换为函数调用：

```
原始输入: "%timeit sum(range(1000))"
  │
  ▼ InputTransformer 转换
"get_ipython().run_line_magic('timeit', 'sum(range(1000))')"
  │
  ▼ 编译 + exec
run_line_magic("timeit", "sum(range(1000))")  [F-222]
  │
  ▼ MagicsManager.find("line", "timeit") → LazyMagic 解析 [F-311]
  │
  ▼ 调用实际魔法函数
```

单元魔法的转换类似，但使用 `run_cell_magic("name", "line_args", "cell_body")` [F-223]。

## 相关概念

- [Shell 生命周期](/concepts/03-shell-lifecycle.md)
- [魔法命令系统](/concepts/04-magic-system.md)
- [输入转换与特殊语法](/concepts/07-input-transform.md)
- [显示系统](/concepts/06-display-system.md)
- [异步支持](/concepts/12-async-support.md)
- [信源参考 - 核心引擎](/references/interactiveshell-source.md)
