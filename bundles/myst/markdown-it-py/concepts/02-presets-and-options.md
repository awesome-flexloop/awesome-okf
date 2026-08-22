---
type: Concept
title: 预设与选项
description: markdown-it-py 的五种内置预设（zero/commonmark/default/gfm-like/gfm-like2）对比，OptionsDict 选项详解，规则的启用与禁用
tags:
- markdown-it-py
- preset
- options
- configuration
difficulty: 入门
estimated_time: 15分钟
prerequisites:
- 01-getting-started
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
status: stable
stale_after: '2027-08-23'
sources:
- id: markdown-it-py-source
  resource: /references/markdown-it-py-source.md
  title: markdown-it-py 源码路径映射
---

# 预设与选项

markdown-it-py 通过预设系统快速配置解析行为。每个预设定义了一组选项（options）和规则组合（components）。

## 五种内置预设

| 预设名 | 别名 | 特点 | 适用场景 |
|--------|------|------|---------|
| `commonmark` | - | **默认预设**，严格 CommonMark，html=True，maxNesting=20，不含表格/删除线 | 需要严格 CommonMark 合规性 |
| `zero` | - | 最小配置，仅保留 paragraph + text，所有选项关闭 | 作为自定义配置的起点 |
| `default` / `js-default` | - | 全规则启用（含所有块级和行内规则），html=False，maxNesting=100，xhtmlOut=False | 想要所有内置语法但不允许HTML |
| `gfm-like` | `default`（注意名冲突） | commonmark + table + strikethrough + linkify，html=True | GitHub Flavored Markdown 风格 |
| `gfm-like2` | - | gfm-like + tasklists + alerts + single_tilde_strikethrough | 最新 GitHub 风格（含任务列表、告警块） |

> ⚠️ **注意**：`gfm-like` 预设的 key 也是 `"default"`（见 presets/__init__.py），这与 `js-default` 的含义不同。推荐显式使用 `"gfm-like"` 或 `"js-default"` 避免歧义。

## 选项详解

所有选项通过 `OptionsType` TypedDict 定义，构造时传入 `options_update` 参数，或通过 `md.set()` 方法设置。

### 核心选项

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `maxNesting` | int | 20（commonmark）/ 100（default） | 递归深度保护，防止恶意输入导致栈溢出 |
| `html` | bool | True（commonmark）/ False（default） | 是否允许源码中的 HTML 标签通过。False 时 HTML 标签被转义为文本 |
| `xhtmlOut` | bool | True（commonmark）/ False（default） | 自闭合标签输出格式：`<br/>` vs `<br>` |
| `breaks` | bool | False | True 时段落内的 `\n` 转为 `<br>`；False 时与 CommonMark 一致（需两个换行+空格才是硬换行） |
| `langPrefix` | str | `"language-"` | 围栏代码块的 CSS class 前缀，如 `language-python` |

### 排版选项

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `typographer` | bool | False | 启用排版增强（替换+智能引号） |
| `quotes` | str | `"\u201c\u201d\u2018\u2019"` | 智能引号替换字符，默认是中文弯引号""''。可设为其他语言的引号 |
| `linkify` | bool | False | 自动将纯文本 URL 转为链接（需安装 linkify-it-py） |

### 高级选项

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `highlight` | Callable\|None | None | 代码高亮函数，签名 `(content, lang, attrs) -> str`，返回高亮后的 HTML |
| `store_labels` | bool | False | Python特有，在 token.meta 中存储链接标签文本 |

### GFM 扩展选项（gfm-like2）

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `tasklists` | bool | False | 启用任务列表复选框（`- [x] task`） |
| `tasklists_editable` | bool | False | 任务列表复选框是否可交互 |
| `alerts` | bool | False | GitHub 告警块（`> [!NOTE]` 等） |
| `strikethrough_single_tilde` | bool | False | 允许单波浪线 `~text~` 作为删除线 |

## 设置选项

### 构造时设置

```python
from markdown_it import MarkdownIt

md = MarkdownIt("commonmark", {
    "html": False,       # 禁用 HTML
    "breaks": True,      # 换行转 <br>
    "linkify": True,     # 自动链接
    "typographer": True,  # 排版增强
})
```

### 运行时设置

```python
md = MarkdownIt()
md.set({"html": False, "breaks": True})
```

### 配置预设

```python
md = MarkdownIt("zero")  # 最小配置
md.configure("commonmark")  # 切换到 commonmark 预设
```

`configure(presets)` 方法的逻辑：
1. 如果 presets 是字符串，从 presets/ 目录查找对应预设字典
2. 合并 options 到当前 options（dict merge）
3. 对每个 component（core/block/inline/inline2），调用对应 Ruler 的 enableOnly()，精确启用预设指定的规则

## 规则的启用与禁用

### 按名禁用

```python
md.disable("emphasis")  # 禁用强调
md.disable(["link", "image"])  # 批量禁用
md.disable("emphasis", ignoreInvalid=True)  # 规则不存在时不报错
```

### 按名启用

```python
md.enable("strikethrough")  # 启用删除线
md.enable(["table", "strikethrough"])
```

`enable()`/`disable()` 返回 MarkdownIt 实例本身，支持链式调用：
```python
html = (MarkdownIt("commonmark")
        .disable("html_inline")
        .enable("table")
        .render(md_text))
```

### 查看规则状态

```python
all_rules = md.get_all_rules()      # {"core": [...], "block": [...], "inline": [...], "inline2": [...]}
active_rules = md.get_active_rules()  # 当前各链启用的规则

# 查看某条规则的定义
rule = md.block.ruler.__rules__[0]
# rule.name, rule.enabled, rule.alt, rule.fat
```

## 从 zero 自定义配置示例

```python
from markdown_it import MarkdownIt

md = (MarkdownIt("zero", {"html": False, "breaks": True})
      .enable(["heading", "paragraph", "emphasis", "strong", "code", "fence",
               "blockquote", "list", "link", "image", "text", "newline", "escape",
               "backticks", "entity"]))

html = md.render("# Custom Config\n\nOnly **enabled** rules work.")
```

## 临时修改规则（上下文管理器）

```python
from markdown_it import MarkdownIt

md = MarkdownIt("commonmark")
with md.reset_rules():
    md.disable("emphasis")
    html_no_emphasis = md.render("**bold**")  # <p>**bold**</p>
# 退出 with 块后规则恢复
html = md.render("**bold**")  # <p><strong>bold</strong></p>
```

## 代码高亮集成

```python
from markdown_it import MarkdownIt
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

def highlight_code(code, lang, attrs):
    if not lang:
        return f'<pre><code>{code}</code></pre>'
    try:
        lexer = get_lexer_by_name(lang)
    except ValueError:
        return f'<pre><code>{code}</code></pre>'
    return highlight(code, lexer, HtmlFormatter())

md = MarkdownIt("commonmark", {"highlight": highlight_code})
html = md.render("```python\nprint('hello')\n```")
```

## 下一步

- [Token 流模型](03-token-stream.md)：理解解析结果的数据结构
- [解析管线架构](04-parsing-pipeline.md)：Core→Block→Inline 三链如何协作
- [Ruler 规则管理](05-ruler.md)：规则系统的内部实现
