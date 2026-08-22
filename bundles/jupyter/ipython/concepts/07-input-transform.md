---
type: concept
title: "07 - 输入转换与特殊语法"
description: IPython InputTransformer2 基于 tokenize 的 AST 感知转换管线，处理魔法前缀、系统命令、帮助语法、提示符剥离等 IPython 特殊语法
tags: [input-transform, tokenize, transformer, magic-escape, system-command, help-syntax, prefilter]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T00:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T00:00:00+08:00" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: ipython-inputtransformer
    title: IPython/core/inputtransformer2.py
  - id: ipython-prefilter
    title: IPython/core/prefilter.py
---

## InputTransformer2 转换管线概述

IPython 7.0 引入的 `InputTransformer2` 系统（位于 `core/inputtransformer2.py`）使用基于 Python `tokenize` 模块的 AST 感知转换，将 IPython 特殊语法转换为标准 Python 代码 [F-350]。这不是简单的字符串替换——它能够正确处理字符串字面量中出现的 `%`、`!`、`?` 等字符，不会将字符串 `"%cd"` 误转换为魔法调用。

TransformerManager 管理整个转换管线，执行顺序如下：

```
原始输入行列表
  │
  ├── 1. leading_empty_lines()     → 移除前导空行 [F-353]
  ├── 2. leading_indent()          → 移除公共前导缩进 [F-354]
  ├── 3. PromptStripper            → 剥离 >>> 和 ... 提示符 [F-352]
  ├── 4. Magic 转换                → %/%% 前缀 → run_line_magic/run_cell_magic 调用
  ├── 5. System 命令转换           → !/!! → system()/getoutput() 调用
  ├── 6. Help 语法转换             → ?/?? → pinfo()/pinfo2() 调用
  └── 7. IPython 特殊语法处理      → 赋值等特殊处理
  │
  ▼
标准 Python 代码字符串（可被 compile() 编译）
```

### ESC 转义前缀

IPython 定义了两个魔法转义前缀常量 [F-330][F-351]：

```python
ESC_MAGIC = '%'    # 行魔法前缀
ESC_MAGIC2 = '%%'  # 单元魔法前缀
```

## 预处理工具函数

### leading_empty_lines

移除输入开头的空行（只含空白字符的行）[F-353]。这在粘贴代码时很有用，避免前导空行导致 IndentationError。

```python
def leading_empty_lines(lines):
    """如果前导行是空行或仅含空白，移除它们"""
    for i, line in enumerate(lines):
        if line and not line.isspace():
            return lines[i:]
    return lines
```

### leading_indent

使用 `textwrap.dedent` 移除所有行的公共前导缩进 [F-354]。这允许用户粘贴缩进的代码块（如来自函数或类内部）而无需手动取消缩进。

```python
def leading_indent(lines):
    """移除最小公共前导缩进"""
    return dedent("".join(lines)).splitlines(keepends=True)
```

## PromptStripper 提示符剥离

`PromptStripper` 类从粘贴的输入中移除 Python REPL 提示符（`>>>` 和 `...`）[F-352]：

```python
class PromptStripper:
    def __init__(self, prompt_re, initial_re=None, *, doctest=False):
        self.prompt_re = prompt_re     # 匹配所有提示符（包括续行 ...）
        self.initial_re = initial_re   # 仅匹配初始提示符（>>>）
        self.doctest = doctest         # doctest 模式
```

这使得从文档或教程中复制粘贴带提示符的代码成为可能：

```python
# 粘贴以下代码会自动剥离 >>> 和 ...
>>> def hello():
...     print("Hello, world!")
...
>>> hello()
Hello, world!

# PromptStripper 转换后：
def hello():
    print("Hello, world!")

hello()
```

PromptStripper 还能正确处理三引号字符串内的提示符（不会误剥离字符串中的 `>>>` 文本）[F-352 源码]。

## 魔法命令转换

### 行魔法转换（%）

以 `%` 开头的行被转换为 `get_ipython().run_line_magic()` 调用：

```python
# 输入:
%timeit sum(range(1000))

# 转换后:
get_ipython().run_line_magic('timeit', 'sum(range(1000))')
```

### 单元魔法转换（%%）

以 `%%` 开头的首行被转换为 `get_ipython().run_cell_magic()` 调用，后续行作为 cell 体：

```python
# 输入:
%%timeit
s = 0
for i in range(1000):
    s += i

# 转换后:
get_ipython().run_cell_magic('timeit', '', "s = 0\nfor i in range(1000):\n    s += i\n")
```

### 自动魔法（Automagic）前缀检测

在 automagic 模式下（默认开启 [F-304]），PrefilterManager 会检测不以前缀开头但匹配已知行魔法名的输入，自动添加 `%` 前缀：

```python
# automagic 开启时，直接输入 pwd 即可
pwd
# PrefilterManager 检测到 pwd 是已知行魔法
# 转换为: get_ipython().run_line_magic('pwd', '')
```

这由 PrefilterManager 的 AutoMagic 检查器处理 [F-460][F-461]，而非 InputTransformer2。InputTransformer2 只处理显式的 `%`/`%%` 前缀。

## System 命令转换（! 和 !!）

### 单感叹号 !

以 `!` 开头的行被转换为系统命令调用：

```python
# 输入:
!ls -la

# 转换后:
get_ipython().system('ls -la')

# 赋值形式:
files = !ls *.py
# 转换后:
files = get_ipython().getoutput('ls *.py')
```

`!` 命令的输出默认直接打印到 stdout，而 `var = !cmd` 形式通过 `getoutput()` 返回结果列表（SList 类型）。

### 双感叹号 !!

`!!` 命令始终返回输出列表（不自动打印）：

```python
# 输入:
!!ls -la

# 转换后:
get_ipython().getoutput('ls -la')
```

## Help 语法转换（? 和 ??）

IPython 提供两种帮助语法，由 InputTransformer2 转换为内省调用：

### 单问号 ?

单个 `?` 在对象名后触发 pinfo（文档查看）：

```python
# 输入:
print?
# 或:
?print

# 转换后:
get_ipython().run_line_magic('pinfo', 'print')
```

### 双问号 ??

双 `?` 触发 pinfo2（查看源代码）：

```python
# 输入:
print??
# 或:
??print

# 转换后:
get_ipython().run_line_magic('pinfo2', 'print')
```

Help 语法支持多种位置形式：
- `obj?` — 对象后跟问号
- `?obj` — 问号后跟对象
- `obj??` / `??obj` — 双问号查源码
- `obj.attr?` — 属性访问链后跟问号

## PrefilterManager 前置过滤

`PrefilterManager` 在 InputTransformer2 转换之后、编译之前执行额外的预处理 [F-460][F-461]：

```
transformed_cell（来自 InputTransformer2）
  │
  ▼
PrefilterManager.check_user_conditions()
  ├── AutoMagic 检查：无前缀的行魔法自动添加 %
  ├── Alias 展开：系统命令别名替换（如 ll → ls -la）
  └── ESC 命令处理：其他转义序列处理
  │
  ▼
最终可编译代码
```

### AutoMagic 处理器

当 automagic 模式开启时 [F-304]，PrefilterManager 检查行首单词是否匹配已知行魔法名。如果匹配且该行在 Python 语法下无效（或作为魔法有效），则自动添加 `%` 前缀：

```python
# 输入:
cd /tmp
# AutoMagic 检测到 cd 是行魔法
# 转换为: %cd /tmp

# 但以下不会被转换（因为 cd 在当前命名空间中是变量）:
cd = 42
cd  # 这是 Python 变量引用，不会被自动魔法转换
```

### Alias 展开

AliasManager 注册的系统命令别名在 Prefilter 阶段展开 [F-471]：

```python
# 默认别名（Unix 系统）:
# cat → cat
# cp → cp
# mv → mv
# rm → rm
# mkdir → mkdir

# 用户定义:
alias ll ls -la

# 输入:
ll
# Alias 展开为:
!ls -la
```

## 基于 tokenize 的 AST 感知转换

InputTransformer2 使用 Python `tokenize` 模块实现转换，这是 IPython 7.0 相对于旧版 inputsplitter 的核心改进：

- **不会误转换字符串中的特殊字符**：`"%cd is not magic"` 中的 `%cd` 不会被转换为魔法调用，因为 tokenize 能识别它在字符串字面量内。
- **正确处理注释**：`# %notmagic` 中的 `%` 不会被转换。
- **区分运算符和魔法前缀**：`x % y`（取模运算）不会被误认为魔法调用。

```python
# 这些都不会被误转换:
s = "50% complete"          # % 在字符串中
x = 100 % 30                # % 作为运算符
# %timeit print("hi")       # % 在注释中

# 这些会被正确转换:
%timeit sum(range(100))     # 行首 % → 魔法
!ls                         # 行首 ! → 系统命令
result = !ls                # 赋值 + ! → getoutput
```

## 自定义输入转换

用户可以通过 `shell.input_transformers_cleanup` 和 `shell.input_transformers_post` 添加自定义转换：

```python
ip = get_ipython()

# 添加 cleanup 转换器（在内置转换之前执行）
def my_cleanup(lines):
    """自定义预处理：移除特定标记"""
    return [line.replace('#!ipython', '') for line in lines]

ip.input_transformers_cleanup.append(my_cleanup)

# 添加 post 转换器（在内置转换之后执行）
def my_post(lines):
    """自定义后处理"""
    return lines

ip.input_transformers_post.append(my_post)
```

转换执行顺序：
1. `input_transformers_cleanup`（用户自定义预处理）
2. 内置转换（magic、system、help、prompt stripping）
3. `input_transformers_post`（用户自定义后处理）

## IPython 特殊语法汇总

| 语法 | 类型 | 转换结果 | 说明 |
|------|------|---------|------|
| `%magic args` | 行魔法 | `run_line_magic('magic', 'args')` | 显式行魔法 |
| `magic args` | 自动魔法 | `%magic args`（Prefilter 转换） | automagic 开启时可用 |
| `%%magic args\nbody` | 单元魔法 | `run_cell_magic('magic', 'args', 'body')` | 必须在首行 |
| `!command` | 系统命令 | `system('command')` | 输出到 stdout |
| `!!command` | 系统命令 | `getoutput('command')` | 返回结果列表 |
| `var = !command` | 捕获输出 | `var = getoutput('command')` | SList 结果 |
| `obj?` | 帮助 | `run_line_magic('pinfo', 'obj')` | 查看文档 |
| `obj??` | 帮助 | `run_line_magic('pinfo2', 'obj')` | 查看源码 |
| `>>>`/`...` | 提示符 | 移除 | PromptStripper 处理 |

## 相关概念

- [代码执行管线](/concepts/05-execution-pipeline.md)
- [魔法命令系统](/concepts/04-magic-system.md)
- [补全、历史与别名](/concepts/08-completer-history.md)
- [信源参考 - 输入转换](/references/inputtransformer-source.md)
