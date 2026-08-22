---
type: Concept
title: Ruler 规则管理
description: Ruler 类管理解析规则的添加、启用、禁用、排序和缓存编译，是插件扩展解析器的核心接口
tags:
- markdown-it-py
- ruler
- rules
- plugin
- chain-of-responsibility
difficulty: 核心
estimated_time: 20分钟
prerequisites:
- 04-parsing-pipeline
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
verified: grep-verified
status: stable
stale_after: '2027-08-23'
sources:
- id: markdown-it-py-source
  resource: /references/markdown-it-py-source.md
  title: markdown-it-py 源码路径映射
---

# Ruler 规则管理

Ruler 是 markdown-it-py 规则系统的核心管理类。Core、Block、Inline 各有一个或多个 Ruler 实例，负责维护规则列表、控制启用状态、按优先级排序，并将规则编译为优化后的函数列表。

## Ruler 的职责

1. **注册规则**：通过 `push()`/`before()`/`after()`/`at()` 添加规则到链中
2. **控制启用状态**：`enable()`/`disable()`/`enableOnly()` 控制哪些规则参与解析
3. **规则排序**：维护规则的执行顺序（before/after/at 可精确插入位置）
4. **缓存编译**：`getRules()` 返回优化后的函数列表，启用状态变化时缓存失效重编译

## 规则对象（Rule）

每条规则由 `Rule` dataclass 表示：

```python
@dataclass
class Rule:
    name: str        # 规则名称（唯一标识）
    enabled: bool    # 是否启用
    alt: list[str]   # 可替代/终止此规则的规则名列表
    fn: Callable     # 规则处理函数
```

## 添加规则的四种方法

### push(name, fn, options)——追加到末尾

```python
ruler.push("my_rule", my_rule_function)
ruler.push("my_rule", my_rule_function, {"alt": ["paragraph"]})
```

### before(anchorName, ruleName, fn, options)——插入到指定规则之前

```python
# 在 "paragraph" 规则之前插入自定义块规则
ruler.before("paragraph", "my_block", my_block_function)
```

### after(anchorName, ruleName, fn, options)——插入到指定规则之后

```python
# 在 "emphasis" 规则之后插入行内规则
ruler.after("emphasis", "my_inline", my_inline_function)
```

### at(name, fn, options)——替换已有规则

```python
# 替换 "paragraph" 规则的实现
ruler.at("paragraph", my_paragraph_function)
```

## 控制规则启用状态

### enable(list, ignoreInvalid)——启用指定规则

```python
ruler.enable(["table", "strikethrough"])
ruler.enable("emphasis")  # 单条也可以
ruler.enable(["unknown"], ignoreInvalid=True)  # 不存在时不抛异常
```

### disable(list, ignoreInvalid)——禁用指定规则

```python
ruler.disable("html_inline")
ruler.disable(["html_block", "html_inline"])
```

### enableOnly(list, ignoreInvalid)——只启用指定规则（禁用其他所有）

```python
# 仅启用段落和文本规则（zero预设的做法）
ruler.enableOnly(["paragraph", "text"], True)
```

这是预设配置的核心方法——`configure()` 对每个 component 的 ruler 调用 `enableOnly()` 精确控制规则集。

## 缓存编译机制

Ruler 内部维护 `__cache__` 字典，缓存已编译的规则函数列表：

1. 初始状态：`__cache__ = None`
2. `getRules(name)` 被调用时：
   - 如果 `__cache__` 为 None，遍历所有 `__rules__`，将 enabled=True 的规则的 `fn` 加入列表，存入缓存
   - 返回 `__cache__[name]`
3. 任何修改操作（push/before/after/enable/disable 等）将 `__cache__` 重置为 None，下次 getRules 时重新编译

```python
# 获取核心链规则（返回函数列表）
rules = md.core.ruler.getRules("")
# 返回 [normalize_fn, block_fn, inline_fn, linkify_fn, ...]

# 获取块级链规则
block_rules = md.block.ruler.getRules("")
```

## 三个内置 Ruler 实例

| Ruler 实例 | 位置 | 规则数 | 说明 |
|------------|------|--------|------|
| `md.core.ruler` | parser_core.py | 7 | 核心规则链 |
| `md.block.ruler` | parser_block.py | 11 | 块级规则链 |
| `md.inline.ruler` | parser_inline.py | 12 | 行内主规则链 |
| `md.inline.ruler2` | parser_inline.py | 4 | 行内后置规则链 |

### Inline 双 Ruler

Inline 解析器有两个 Ruler：
- `ruler`（主链）：tokenize 阶段执行，产出初步的 tokens 和 delimiters
- `ruler2`（后置链）：tokenize 之后执行，处理分隔符配对、片段合并等后处理

这是因为强调和删除线的解析需要"先收集所有标记位置，再统一配对"的两阶段处理。

## 规则函数签名

### Block 规则函数

```python
def block_rule(state: StateBlock, startLine: int, endLine: int, silent: bool) -> bool:
    """
    Args:
        state: 块级解析状态
        startLine: 起始行号
        endLine: 结束行号
        silent: 为True时仅检查是否匹配，不输出Token（用于预判）
    Returns:
        True: 规则成功匹配并消费了行
        False: 规则不匹配，尝试下一条规则
    """
```

### Inline 规则函数

```python
def inline_rule(state: StateInline, silent: bool) -> bool:
    """
    Args:
        state: 行内解析状态（state.pos 是当前位置）
        silent: 为True时仅检查，不输出Token
    Returns:
        True: 规则成功匹配，state.pos 已移动到匹配结束位置
        False: 不匹配
    """
```

### Core 规则函数

```python
def core_rule(state: StateCore) -> None:
    """Core 规则无返回值，直接修改 state.tokens"""
```

## alt 列表详解

Block 规则的 `alt` 选项定义了"哪些规则可以终止当前规则"。这在 paragraph 规则中最典型：

```python
# paragraph 规则的 alt
ruler.push("paragraph", paragraph, {"alt": ["paragraph", "reference", "blockquote", "list"]})
```

当 paragraph 正在消费连续文本行时，如果某一行看起来像是 reference、blockquote 或 list 的起始，paragraph 终止，让其他规则处理该行。

这实现了规则间的协作——高优先级规则先尝试，低优先级规则知道何时让出。

## 在插件中使用 Ruler

编写插件时，Ruler 是添加新语法的主要接口：

```python
def my_plugin(md, options):
    # 添加块级规则（在 paragraph 之前）
    md.block.ruler.before("paragraph", "my_block", my_block_rule)
    
    # 添加行内规则（在 emphasis 之后）
    md.inline.ruler.after("emphasis", "my_inline", my_inline_rule)
    
    # 添加后置处理规则
    md.inline.ruler2.push("my_post", my_post_rule)
    
    # 添加自定义渲染规则
    md.add_render_rule("my_token_open", render_my_token)
```

## 查看规则信息

```python
# 遍历所有规则
for rule in md.block.ruler.__rules__:
    print(f"{rule.name}: enabled={rule.enabled}, alt={rule.alt}")

# 获取所有规则名
all_block_rules = [r.name for r in md.block.ruler.__rules__]

# 获取当前启用的规则函数
active_fns = md.block.ruler.getRules("")
```

## 下一步

- [StateBlock 块级解析状态](06-state-block.md)：块级规则操作的状态对象
- [StateInline 行内解析状态](07-state-inline.md)：行内规则操作的状态对象
- [块级规则详解](08-block-rules.md)：11 条块级规则的具体功能
- [插件系统](12-plugin-system.md)：完整插件开发示例
