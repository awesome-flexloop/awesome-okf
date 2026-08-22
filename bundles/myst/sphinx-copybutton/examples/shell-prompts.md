---
type: Example
title: 多语言 REPL 提示符配置
description: Bash、Python REPL、IPython、PowerShell 等不同环境下的提示符剥离配置方案，正则表达式速查
tags: [sphinx, sphinx-extension, copybutton, example, prompt, regex, repl, myst]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T03:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: copybutton-source
    resource: /references/copybutton-source.md
    title: sphinx-copybutton 源码路径映射
---

# 多语言 REPL 提示符配置

不同编程语言和 Shell 环境有不同的提示符（prompt）。本文档提供常见环境的 sphinx-copybutton 配置方案。

## Bash / Shell

### 基础配置（仅 $ 提示符）

```python
copybutton_prompt_text = "$ "
```

适用于大多数 Bash 教程文档。

### 包含续接符（多行命令）

```python
copybutton_prompt_text = "$ "
copybutton_line_continuation_character = "\\"
```

这样以下代码块中的续接行也能正确复制：

```bash
$ echo "line 1" \
>   "line 2" \
>   "line 3"
```

### 包含 Root 提示符 #

```python
copybutton_prompt_text = r"\$ |# "
copybutton_prompt_is_regexp = True
```

### 完整 Bash 配置

```python
copybutton_prompt_text = r"\$ |> |# "
copybutton_prompt_is_regexp = True
copybutton_line_continuation_character = "\\"
copybutton_only_copy_prompt_lines = True
copybutton_remove_prompts = True
```

## Python REPL

### 基础配置（>>> 和 ...）

```python
copybutton_prompt_text = r">>> |\.\.\. "
copybutton_prompt_is_regexp = True
```

匹配标准 Python 交互式解释器：

```python
>>> def greet(name):
...     return f"Hello, {name}!"
>>> greet("World")
'Hello, World!'
```

复制后得到干净的代码：

```python
def greet(name):
    return f"Hello, {name}!"
greet("World")
```

## IPython / Jupyter

IPython 使用 `In [N]:` 和 `...:` 格式的提示符：

```python
copybutton_prompt_text = r"In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True
```

正则解析：
- `In \[\d*\]: ` — 匹配 `In [1]:`、`In [123]:` 等输入提示符
- ` {2,5}\.\.\.: ` — 匹配 2-5 个空格后跟 `...:`（续行提示符）
- ` {5,8}: ` — 匹配 5-8 个空格后跟 `:`（嵌套块续行）

## 混合环境配置

文档中同时包含多种 REPL 环境时，使用正则组合：

```python
# 综合配置：Bash + Python + IPython
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True
copybutton_line_continuation_character = "\\"
```

## PowerShell

```python
copybutton_prompt_text = r"PS> "
```

更完整的 PowerShell 提示符（可能包含路径）：

```python
copybutton_prompt_text = r"PS [A-Z]:\\.*?> "
copybutton_prompt_is_regexp = True
```

## 数据库客户端

### MySQL

```python
copybutton_prompt_text = r"mysql> "
```

### PostgreSQL (psql)

```python
copybutton_prompt_text = r"\w+=> |\w+-> "
copybutton_prompt_is_regexp = True
```

### SQLite

```python
copybutton_prompt_text = r"sqlite> "
```

## 其他语言 REPL

### Node.js

```python
copybutton_prompt_text = r"> "
```

注意：`> ` 过于宽泛，可能误匹配其他内容。建议在 Node.js 专用文档中使用。

### Ruby IRB

```python
copybutton_prompt_text = r"irb\(.*\)[>*] "
copybutton_prompt_is_regexp = True
```

### R

```python
copybutton_prompt_text = r"> "
```

### Julia

```python
copybutton_prompt_text = r"julia> "
```

## 含输出的代码块配置

当代码块同时包含命令和输出时，使用 `copybutton_only_copy_prompt_lines = True` 只复制命令行：

```python
copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_regexp = True
copybutton_only_copy_prompt_lines = True
copybutton_remove_prompts = True
```

效果：

```python
>>> print("Hello")
Hello
>>> x = 1 + 2
>>> x
3
```

复制时只复制 `print("Hello")`、`x = 1 + 2`、`x` 三行，跳过 `Hello` 和 `3` 输出行。

如果需要同时复制输出（如教程中需要展示完整交互），设置：

```python
copybutton_only_copy_prompt_lines = False
copybutton_remove_prompts = True
```

## 行号排除配置

使用 `linenos` 选项的代码块会显示行号，需要排除：

```python
# 默认值已包含 .linenos
copybutton_exclude = ".linenos"

# 如果主题添加了其他装饰元素，扩展选择器
copybutton_exclude = ".linenos, .gp, .go"
```

Pygments 生成的提示符相关 CSS 类：
- `.linenos` — 行号
- `.gp` — Generic.Prompt（提示符本身）
- `.go` — Generic.Output（命令输出）

## 正则表达式速查

| 模式 | 匹配 | 示例 |
|------|------|------|
| `\$ ` | Bash 普通用户提示符 | `$ ` |
| `# ` | Root 提示符 | `# ` |
| `>>> ` | Python REPL 主提示符 | `>>> ` |
| `\.\.\. ` | Python REPL 续行提示符 | `... ` |
| `In \[\d*\]: ` | IPython 输入提示符 | `In [1]: ` |
| `PS> ` | PowerShell 提示符 | `PS> ` |
| `mysql> ` | MySQL 提示符 | `mysql> ` |
| `sqlite> ` | SQLite 提示符 | `sqlite> ` |
| `julia> ` | Julia 提示符 | `julia> ` |
| ` {2,5}\.\.\.: ` | IPython 续行（2-5空格） | `  ...: ` |

## 完整多场景 conf.py 模板

```python
# conf.py — 多语言 REPL 文档通用配置
project = 'Polyglot Tutorial'
copyright = '2024, Your Name'
author = 'Your Name'
release = '1.0.0'
language = 'zh_CN'

extensions = [
    'sphinx_copybutton',
]

# -- sphinx-copybutton --------------------------------------------------
# 支持 Bash、Python、IPython 提示符
copybutton_prompt_text = (
    r">>> "                # Python 主提示符
    r"|\.\.\. "            # Python 续行
    r"|\$ "                # Bash 普通用户
    r"|# "                 # Bash root
    r"|In \[\d*\]: "       # IPython 输入
    r"| {2,5}\.\.\.: "     # IPython 续行
    r"| {5,8}: "           # IPython 深层续行
)
copybutton_prompt_is_regexp = True
copybutton_only_copy_prompt_lines = True
copybutton_remove_prompts = True
copybutton_copy_empty_lines = True
copybutton_line_continuation_character = "\\"
copybutton_exclude = ".linenos, .gp"

# HTML 输出
html_theme = 'sphinx_book_theme'
html_static_path = ['_static']
```

## 调试技巧

如果提示符剥离不生效，可以按以下步骤排查：

1. **检查正则是否正确**：在 Python 中测试正则表达式：
   ```python
   import re
   pattern = r">>> |\.\.\. |\$ "
   text = ">>> print('hello')"
   match = re.match('^(' + pattern + ')(.*)', text)
   print(match.groups() if match else "No match")
   ```

2. **检查实际 HTML 结构**：用浏览器开发者工具查看代码块中提示符的实际文本，可能包含不可见字符或额外空格。

3. **临时关闭 only_copy_prompt_lines**：设置 `copybutton_only_copy_prompt_lines = False`，观察是否有行被意外过滤。

## 相关概念

- [文本处理与提示符剥离](/concepts/03-text-processing.md)
- [基础配置示例](basic-setup.md)
