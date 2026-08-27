---
type: Reference
title: Input Transformer API 参考
description: IPython 输入转换系统完整 API 参考，包括 TransformerManager 管线、TokenTransformBase 基类、各类特殊语法转换器和转义常量
tags: [api, input, transformer, magic, system, reference, core]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: ipython-inputtransformer2
    resource: /references/inputtransformer-source.md
    title: IPython/core/inputtransformer2.py Input Transformation System
---

# Input Transformer API 参考

IPython 输入转换系统负责将用户输入中的特殊语法（`%magic`、`!system`、`?help`、`%%cell_magic` 等）转换为标准 Python 代码。定义在 `IPython/core/inputtransformer2.py`，是 IPython 7.0+ 引入的第二代转换器（替代已废弃的 inputsplitter 和 inputtransformer）。

---

## TransformerManager

### 类定义

```python
class TransformerManager:
    """对代码单元格应用各种转换的管理器

    主要对外方法: transform_cell() 和 check_complete()
    """
```

### 构造函数与转换管线

```python
def __init__(self):
    self.cleanup_transforms = [
        leading_empty_lines,   # 移除前导空行
        leading_indent,        # 移除公共前导缩进
        classic_prompt,        # 剥离 >>> / ... 提示符
        ipython_prompt,        # 剥离 In[n]: / ...: 提示符
    ]
    self.line_transforms = [
        cell_magic,            # 转换 %%cell_magic
    ]
    self.token_transformers = [
        MagicAssign,           # a = %foo 魔法赋值
        SystemAssign,          # a = !foo 系统命令赋值
        EscapedCommand,        # %foo, !foo, ?foo, /foo, ,foo, ;foo
        HelpEnd,               # obj?, obj?? 后缀帮助
    ]
```

### 转换执行顺序

```
原始单元格文本
    │
    ▼
[cleanup_transforms] ─── 前导清理（纯文本变换）
    │  1. leading_empty_lines  移除前导空行
    │  2. leading_indent       移除公共缩进
    │  3. classic_prompt       剥离 >>> / ...
    │  4. ipython_prompt       剥离 In[n]: / ...:
    ▼
[line_transforms] ─── 行级变换
    │  1. cell_magic           转换 %%cell_magic 整行
    ▼
[do_token_transforms] ─── Token 级变换（循环直到无变化）
    │  循环: make_tokens_by_line → find → transform → 重新 tokenize
    │  按 (start_line, start_col, priority) 排序优先级
    │  最多 TRANSFORM_LOOP_LIMIT=500 次迭代
    ▼
标准 Python 代码
```

### 核心方法

#### transform_cell()

```python
def transform_cell(self, cell: str) -> str:
    """转换用户输入的单元格代码为标准 Python

    Parameters
    ----------
    cell : str — 用户输入的源代码（可能包含 IPython 特殊语法）

    Returns
    -------
    str — 转换后的标准 Python 代码

    处理流程:
    1. 确保末尾有换行符
    2. 逐行应用 cleanup_transforms
    3. 逐行应用 line_transforms
    4. 循环执行 token 级转换直到无变化
    """
```

#### check_complete()

```python
def check_complete(self, cell: str):
    """判断代码块是否完整、需要续行或语法无效

    Parameters
    ----------
    cell : str — 待检查的代码

    Returns
    -------
    (status, indent_spaces) : tuple
        status: 'complete' — 代码完整可执行
                'incomplete' — 需要更多输入（多行未结束）
                'invalid' — 语法错误
        indent_spaces: int 或 None — incomplete 时建议下一行缩进空格数
    """
```

**check_complete 判断逻辑**：
1. 检查续行符 `\` → incomplete
2. 应用无副作用的 cleanup transforms
3. `%%` 开头的 cell magic → 以空行结束判断完整
4. 应用无副作用的 line transforms 和 token transforms
5. Tokenize 检查括号匹配、多行字符串、`:` 结尾的代码块
6. 最终用 `codeop.compile_command` 做完整语法验证

#### do_token_transforms()

```python
def do_token_transforms(self, lines):
    """循环执行 token 级转换，最多 TRANSFORM_LOOP_LIMIT 次

    每次迭代:
    1. make_tokens_by_line(lines) 重新分词
    2. 所有 token_transformers 查找匹配
    3. 按 sortby() 排序（行号→列号→优先级）
    4. 执行最先匹配的 transform
    5. 重复直到无转换可做
    """
```

---

## 转义字符常量

```python
ESC_SHELL  = "!"     # 发送到系统 shell
ESC_SH_CAP = "!!"    # 发送到系统 shell 并捕获输出
ESC_HELP   = "?"     # 对象信息查询
ESC_HELP2  = "??"    # 对象详细信息查询（含源码）
ESC_MAGIC  = "%"     # 调用行魔法
ESC_MAGIC2 = "%%"    # 调用单元格魔法
ESC_QUOTE  = ","     # 参数按空白拆分，逐个加引号调用
ESC_QUOTE2 = ";"     # 所有参数作为单个字符串加引号调用
ESC_PAREN  = "/"     # 第一个参数作为函数名，其余作为参数调用

ESCAPE_SINGLES = {"!", "?", "%", ",", ";", "/"}
ESCAPE_DOUBLES = {"!!", "??"}  # %% 由 cell_magic 单独处理
```

### tr 转译映射表

```python
tr = {
    ESC_SHELL:  "get_ipython().system({!r})".format,     # !cmd
    ESC_SH_CAP: "get_ipython().getoutput({!r})".format,  # !!cmd
    ESC_HELP:   _tr_help,                                 # ?obj 或 ?
    ESC_HELP2:  _tr_help2,                                # ??obj 或 ??
    ESC_MAGIC:  _tr_magic,                                # %name args
    ESC_QUOTE:  _tr_quote,                                # ,name arg1 arg2
    ESC_QUOTE2: _tr_quote2,                               # ;name args
    ESC_PAREN:  _tr_paren,                                # /name arg1 arg2
}
```

### 转译函数

| 函数 | 转义符 | 转换示例 |
|------|--------|---------|
| `_tr_magic(content)` | `%` | `%timeit foo()` → `get_ipython().run_line_magic('timeit', 'foo()')` |
| `_tr_help(content)` | `?` | `?obj` → `get_ipython().run_line_magic('pinfo', 'obj')` |
| `_tr_help2(content)` | `??` | `??obj` → `get_ipython().run_line_magic('pinfo2', 'obj')` |
| `_tr_quote(content)` | `,` | `,func a b c` → `func("a", "b", "c")` |
| `_tr_quote2(content)` | `;` | `;func a b c` → `func("a b c")` |
| `_tr_paren(content)` | `/` | `/func a b c` → `func(a, b, c)` |

> ⚠️ 空内容的 `?` 或 `??` → `get_ipython().show_usage()`（显示帮助屏幕）。
> `_tr_help` 中含 `*` 通配符时使用 `psearch` 而非 `pinfo`。

---

## Cleanup 转换器（纯文本）

### leading_empty_lines()

```python
def leading_empty_lines(lines):
    """移除前导空行或仅含空白的行"""
```

### leading_indent()

```python
def leading_indent(lines):
    """移除所有行的最小公共前导缩进（使用 textwrap.dedent）"""
```

### PromptStripper 类

```python
class PromptStripper:
    """从输入块中剥离匹配的提示符

    Parameters
    ----------
    prompt_re : regex — 匹配所有提示符（包括续行）
    initial_re : regex, optional — 仅匹配首行提示符
    doctest : bool — 是否启用 doctest 模式（支持缩进提示符和三引号保护）
    """
```

**预置 PromptStripper 实例**：

```python
classic_prompt = PromptStripper(
    prompt_re=re.compile(r"^(>>>|\.\.\.)( |$)"),
    initial_re=re.compile(r"^>>>( |$)"),
    doctest=True,   # 支持三引号内保护、缩进提示符
)

ipython_prompt = PromptStripper(
    re.compile(r"""
    ^(
        ((\[nav\]|\[ins\])?\ )?   # Vi 模式前缀
        In\ \[\d+\]:\             # In[N]: 提示符
        |
        \s*\.{3,}:\ ?             # 多行续行提示符 ...:
    )
    """, re.VERBOSE)
)
```

#### PromptStripper 核心方法

```python
def __call__(self, lines):
    """剥离提示符

    非 doctest 模式：首行匹配 initial_re 或第二行匹配 prompt_re 时才剥离
    doctest 模式：检测 >>> 行，剥离 >>> / ...，分段 dedent，保护三引号内内容
    """
```

---

## Line 转换器

### cell_magic()

```python
def cell_magic(lines):
    """转换单元格魔法（以 %% 开头）

    转换示例:
        %%timeit -n 100
        x = sum(range(1000))
    →
        get_ipython().run_cell_magic('timeit', '-n 100', 'x = sum(range(1000))\n')

    注意: %%magic? 形式不由本函数处理，交给 HelpEnd
    """
```

---

## TokenTransformBase 基类

```python
class TokenTransformBase:
    """基于 Token 的转换器基类

    IPython 特殊语法在字符串和注释内不应被转换，纯正则难以可靠处理。
    解决方案：将代码 tokenize 为 Python tokens，在 token 流中识别特殊语法，
    每次转换一个实例后重新 tokenize，循环直到无特殊语法。

    子类需实现:
      - find(tokens_by_line) 类方法：查找并返回实例或 None
      - transform(lines) 方法：执行转换返回新的行列表
    """

    priority = 10  # 数字越小优先级越高（同一位置匹配时）
```

### 核心属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `priority` | int | 优先级，数字越小优先级越高 |
| `start_line` | int | 匹配起始行（0-indexed） |
| `start_col` | int | 匹配起始列 |

### 子类必须实现的方法

#### find() (classmethod)

```python
@classmethod
def find(cls, tokens_by_line):
    """在 tokens_by_line 中查找一个特殊语法实例

    Parameters
    ----------
    tokens_by_line : list[list[TokenInfo]]
        按逻辑行分组的 token 列表

    Returns
    -------
    子类实例 或 None — 找到则返回指向起始位置的实例
    """
```

#### transform()

```python
def transform(self, lines: list[str]):
    """转换 find() 找到的特殊语法实例

    Parameters
    ----------
    lines : list[str] — 原始代码行列表

    Returns
    -------
    list[str] — 转换后的代码行列表
    """
```

### 排序方法

```python
def sortby(self):
    """返回排序键 (start_line, start_col, priority)"""
    return self.start_line, self.start_col, self.priority
```

---

## 具体 Token 转换器

### MagicAssign

```python
class MagicAssign(TokenTransformBase):
    """处理魔法赋值: a = %foo 或 a = %foo args

    优先级: 默认 10

    匹配条件:
    - 行中存在顶层 '='（括号外）
    - '=' 后第一个 token 是 '%'
    - '%' 后是 NAME token（魔法名）

    转换示例:
        result = %timeit -n 100 some_code()
    →
        result = get_ipython().run_line_magic('timeit', '-n 100 some_code()')
    """
```

### SystemAssign

```python
class SystemAssign(TokenTransformBase):
    """处理系统命令赋值: a = !foo

    Python 版本兼容:
    - 3.12 之前: '!' 被 tokenizer 标记为 ERRORTOKEN
    - 3.12+: '!' 被标记为 OP

    转换示例:
        files = !ls -la
    →
        files = get_ipython().getoutput('ls -la')
    """
```

### EscapedCommand

```python
class EscapedCommand(TokenTransformBase):
    """处理行首转义命令: %foo, !foo, !!cmd, ?obj, ??obj, /foo, ,foo, ;foo

    匹配条件: 行首第一个有效 token（跳过 INDENT/DEDENT）是 ESCAPE_SINGLES 中的字符

    处理续行: 支持反斜杠 \ 续行的多行命令

    转换优先级顺序（同一位置）:
    1. 双字符转义（!!、??）优先
    2. 单字符转义（!、?、%、,、;、/）
    3. 使用 tr 映射表查找对应的转译函数

    转换示例:
        %matplotlib inline
        !pip install numpy
        ??some_function
        /print hello world
    """
```

### HelpEnd

```python
class HelpEnd(TokenTransformBase):
    """处理后缀帮助语法: obj? 和 obj??

    优先级: 5（高于 EscapedCommand 的 10，确保 %magic? 走帮助而非魔法调用）

    匹配条件: 行倒数第二个 token 是 '?'（最后一个是 NEWLINE）

    正则匹配目标:
        _help_end_re = re.compile(r"""
            (%{0,2}                     # 可选 % 或 %%
            (?!\d)[\w*]+               # 变量名（不以数字开头）
            (\.(?!\d)[\w*]+|\[-?\d+\])*  # 属性访问 .attr 或索引 [0]
            )
            (\?\??)$                   # 结尾 ? 或 ??
        """, re.VERBOSE)

    转换示例:
        some_object?
        some_object??
        %magic?
        %%cellmagic?
    """
```

---

## 辅助函数

### make_tokens_by_line()

```python
def make_tokens_by_line(lines: list[str]):
    """将代码行 tokenize 并按逻辑行分组

    使用括号层级追踪，将多行表达式中的 token 合并到同一逻辑行。
    多行字符串或表达式未结束时，TokenError 被静默捕获（这是预期行为）。

    Parameters
    ----------
    lines : list[str]
        代码行列表，每行保留行尾符（\\n）

    Returns
    -------
    list[list[TokenInfo]] — 按逻辑行分组的 token 列表
    """
```

### find_end_of_continued_line()

```python
def find_end_of_continued_line(lines, start_line: int):
    """查找以反斜杠 \\ 续行的最后一行（0-indexed）"""
```

### assemble_continued_line()

```python
def assemble_continued_line(lines, start: tuple[int, int], end_line: int):
    """将多行续行片段组装为单行

    去除每行末尾的反斜杠和换行符，用空格连接各片段。

    用于支持 %magic 和 !command 跨多行续行。
    """
```

### has_sunken_brackets()

```python
def has_sunken_brackets(tokens: list[TokenInfo]):
    """检查括号深度是否降到 0 以下（右括号多于左括号）

    用于 check_complete 检测无效代码
    """
```

### find_last_indent()

```python
def find_last_indent(lines):
    """返回最后一行的缩进空格数（tab 视为 4 个空格）"""
```

### _find_assign_op()

```python
def _find_assign_op(token_line) -> int | None:
    """查找行中第一个顶层赋值操作符 '=' 的索引

    跳过括号内的 '='，不支持多重赋值 (a = b = %foo)
    """
```

### _make_help_call()

```python
def _make_help_call(target, esc):
    """生成帮助调用代码

    - esc == '??' → pinfo2（详细帮助，含源码）
    - target 含 '*' → psearch（通配符搜索）
    - 其他 → pinfo（普通帮助）
    """
```

---

## 常量

```python
TRANSFORM_LOOP_LIMIT = 500
"""Token 转换最大循环次数，防止无限循环"""
```

---

## MaybeAsync 编译支持

```python
class MaybeAsyncCompile(Compile):
    """支持顶层 await 的编译器"""
    def __init__(self, extra_flags=0):
        self.flags |= extra_flags  # ast.PyCF_ALLOW_TOP_LEVEL_AWAIT

class MaybeAsyncCommandCompiler(CommandCompiler):
    """支持顶层 await 的命令编译器"""

_extra_flags = ast.PyCF_ALLOW_TOP_LEVEL_AWAIT
compile_command = MaybeAsyncCommandCompiler(extra_flags=_extra_flags)
```

> TransformerManager.check_complete() 使用此 compile_command 实例进行最终语法验证，支持 IPython 的顶层 `await` 语法。

---

## 转换示例

### 输入到输出的映射

| 用户输入 | 转换后 Python 代码 |
|---------|-------------------|
| `%timeit x = 1` | `get_ipython().run_line_magic('timeit', 'x = 1')` |
| `%%bash` (cell) | `get_ipython().run_cell_magic('bash', '', '<cell body>')` |
| `!ls -la` | `get_ipython().system('ls -la')` |
| `!!ls -la` | `get_ipython().getoutput('ls -la')` |
| `result = !ls` | `result = get_ipython().getoutput('ls')` |
| `obj?` | `get_ipython().run_line_magic('pinfo', 'obj')` |
| `obj??` | `get_ipython().run_line_magic('pinfo2', 'obj')` |
| `?` | `get_ipython().show_usage()` |
| `,func a b c` | `func("a", "b", "c")` |
| `;func a b c` | `func("a b c")` |
| `/func a b c` | `func(a, b, c)` |
| `a = %magic args` | `a = get_ipython().run_line_magic('magic', 'args')` |

### 多行续行支持

```python
# 输入
files = !ls -la \
        | grep py \
        | head -10

# 转换后
files = get_ipython().getoutput('ls -la | grep py | head -10')
```

### 提示符剥离

```python
# 粘贴的代码带提示符
# >>> def foo():
# ...     return 42
# 剥离后:
def foo():
    return 42
```

---

## 相关概念

- **[魔法命令系统](magic-source.md)**：`%magic` 和 `%%cell_magic` 的注册与执行机制
- **[InteractiveShell](interactiveshell-source.md)**：`input_transformer_manager` 属性和初始化流程
- **Prefilter 系统**：旧版预过滤机制与新版 transformer 的关系
- **特殊语法**：IPython 扩展语法完整列表
