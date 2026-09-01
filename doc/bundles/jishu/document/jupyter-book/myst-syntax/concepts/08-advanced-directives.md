---
type: concept
title: "高级指令与角色"
description: "Mermaid图表、TOC目录、Raw原始内容、索引、化学式、SI单位、键盘按键等高级语法扩展"
tags: [myst-syntax, mermaid, toc, raw, index, chemistry, si-units, keyboard]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/mermaid.ts"
    facts: [F-S024]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/toc.ts"
    facts: [F-S029]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/raw.ts"
    facts: [F-S036]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-directives/src/indices.ts"
    facts: [F-S030, F-S031]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-roles/src/chem.ts"
    facts: [F-S051]
  - path: "external/libs/ai/jupyter-book/mystmd/packages/myst-roles/src/si.ts"
    facts: [F-S052]
---

# 高级指令与角色

本文档介绍 Mermaid 图表、目录、原始内容、索引、化学式、SI 单位、键盘按键等高级语法扩展。

## Mermaid 图表

`mermaid` 指令嵌入 Mermaid 图表（流程图、时序图、类图等）：

````markdown
```{mermaid}
flowchart LR
    A[开始] --> B{判断}
    B -->|是| C[处理]
    B -->|否| D[结束]
    C --> D
```
````

body 为 Mermaid DSL 文本（String，必填），输出为 `mermaid` 节点，由前端渲染为 SVG 图表。支持通用选项（class/label）。

### 常用图表类型

- `flowchart`：流程图（LR/TD/TB/RL 方向）
- `sequenceDiagram`：时序图
- `classDiagram`：类图
- `stateDiagram-v2`：状态图
- `erDiagram`：ER 图
- `gantt`：甘特图
- `pie`：饼图
- `graph`（旧语法）：同 flowchart

## TOC 目录

`toc` 指令插入自动生成的目录：

```markdown
:::{toc}
:context: project
:depth: 3
:::
```

### 别名

`tableofcontents`、`table-of-contents`、`toctree`（Sphinx 兼容）、`contents`（Docutils 兼容）

### 选项

| 选项 | 别名 | 类型 | 说明 |
|------|------|------|------|
| `:context:` | `:kind:` | String | 目录范围：project/children/page/section |
| `:depth:` | `:maxdepth:` | Number | 标题层级深度（≥1） |

### Context 范围

| Context | 默认触发 | 说明 |
|---------|----------|------|
| `project` | toc/toctree 默认 | 整个项目所有页面的目录 |
| `children` | - | 当前页面的子页面 |
| `page` | - | 当前页面内的所有标题 |
| `section` | contents 默认 | 当前章节内的标题 |

```markdown
:::{contents} 本节目录
:depth: 2
:::
```

无效 context 产生错误并回退到 `project`。depth < 1 产生错误并忽略。

## Raw 原始内容

`raw` 指令和对应的 raw 角色插入特定格式的原始内容，仅在对应导出格式中包含。

### 块级 Raw

```markdown
:::{raw} latex
\vspace{10pt}
:::
```

- 参数指定格式：`latex`/`tex`、`typst`/`typ`
- body 为原始内容
- 对应格式导出时原样插入，其他格式忽略

快捷指令（无需参数）：

```markdown
:::{raw:latex}
\textbf{仅在PDF中显示}
:::

:::{raw:typst}
#text(weight: "bold")[仅在Typst中显示]
:::
```

别名：`raw:tex`（raw:latex 的别名）、`raw:typ`（raw:typst 的别名）

### 行内 Raw

```markdown
这是普通文本 {raw:latex}`\LaTeX{}` 这也是普通文本。
```

- `{raw:latex}` 或 `{raw:tex}`：行内 LaTeX 命令
- `{raw:typst}` 或 `{raw:typ}`：行内 Typst 命令

## 索引

MyST 支持书后索引（back-of-book index），通过两个指令配合使用。

### 定义索引条目：index 指令

```markdown
:::{index}
single: MyST
pair: Markdown; MyST
triple: 语法; 扩展; MyST
see: MyST; Markedly Structured Text
seealso: Sphinx; reStructuredText
:::
```

支持五种索引条目类型：
- `single`：单词条（术语 → 当前位置）
- `pair`：主/副条目对（主术语; 修饰语）
- `triple`：三级条目
- `see`：交叉引用（指向其他术语，不产生页码）
- `seealso`：另见（同时有页码和交叉引用）

也可以通过参数或选项定义（不推荐，会产生选项语法警告）：

```markdown
:::{index}
:single: MyST
:pair: Markdown; MyST
:::
```

索引指令生成 `mystTarget` 节点，包含 indexEntries 数组。`:label:` 选项可为索引点添加标签。

### 显示索引：show-index 指令

```markdown
:::{show-index} 索引
:::
```

别名：`genindex`。在该位置插入生成的索引（按字母排序的索引条目列表，含页码链接）。arg 为可选标题。

## 化学式（Chem 角色）

`{chem}` 角色（别名 `chemicalFormula`）插入化学式：

```markdown
水的化学式是 {chem}`H2O`，葡萄糖是 {chem}`C6H12O6`。
```

生成 `chemicalFormula` 节点，由前端/转换器渲染为正确的化学式格式（下标数字等）。

## SI 单位（Si 角色）

`{si}` 角色插入 SI 单位，支持 LaTeX siunitx 风格语法：

```markdown
光速约为 {si}`3e8<\meter\per\second>`，即 {si}`300<\mega\meter\per\second>`。
```

### 语法格式

```
{si}`数值<\单位命令序列>`
```

格式：`<数字><\unit1\unit2...>`，正则匹配 `/([0-9.,eE-]+)\s?<([\\a-zA-Z\s]+)>/`。

不匹配时返回 `error:true` 的节点。

### 单位映射表

si 角色内置了完整的 SI 单位映射：

| 类别 | 命令 | 符号 |
|------|------|------|
| 基本单位 | \ampere / \candela / \kelvin / \kilogram / \metre / \mole / \second | A / cd / K / kg / m / mol / s |
| 导出单位 | \newton / \pascal / \joule / \watt / \volt / \ohm / \hertz | N / Pa / J / W / V / Ω / Hz |
| 其他单位 | \degreeCelsius / \degree / \electronvolt / \angstrom / \liter | °C / ° / eV / Å / L |
| 时间 | \day / \hour / \minute / \second | d / h / min / s |
| 词头 | \yocto~\yotta | y~Y（10⁻²⁴~10²⁴） |
| 特殊 | \micro | µ |

```markdown
{si}`10<\kilo\gram>` → 10kg
{si}`25<\degreeCelsius>` → 25°C
{si}`100<\micro\meter>` → 100µm
{si}`3600<\second>` → 3600s
```

## 键盘按键（Keyboard 角色）

`{kbd}` 或 `{keyboard}` 角色表示键盘按键：

```markdown
按 {kbd}`Ctrl+C` 中断程序，{kbd}`Enter` 确认。
```

生成键盘样式的 `<kbd>` 元素。

## 文本格式化角色

| 角色 | 效果 | 示例 |
|------|------|------|
| `{subscript}` / `{sub}` | 下标 | H{sub}`2`O |
| `{superscript}` / `{sup}` | 上标 | x{sup}`2` |
| `{underline}` / `{u}` | 下划线 | \{u}`重要` |
| `{delete}` / `{del}` | 删除线 | \{del}`过时内容` |
| `{smallcaps}` | 小型大写 | \{smallcaps}`MyST` |
| `{span}` | 通用行内容器（加CSS类） | \{span}`text` |

## 行内表达式（Eval 角色）

`{eval}` 角色（inlineExpression）支持行内表达式计算，在支持执行的环境中动态计算值。

## 指令速查表

| 指令 | 用途 | body类型 |
|------|------|----------|
| `mermaid` | 图表 | String（Mermaid DSL） |
| `toc` | 目录 | 无 |
| `raw` / `raw:latex` / `raw:typst` | 格式特定原始内容 | String |
| `index` | 定义索引条目 | String（索引行） |
| `show-index` / `genindex` | 显示生成的索引 | 无 |
| `div` | 通用块容器 | myst |
| `glossary` | 术语表 | myst |
| `bibliography` | 参考文献列表 | 无 |
| `blockquote` | 块引用 | myst |
| `anywidget`/`widget` | Jupyter 小部件 | - |

## 角色速查表

| 角色 | 用途 | 输出节点 |
|------|------|----------|
| `math` | 行内数学 | inlineMath |
| `chem`/`chemicalFormula` | 化学式 | chemicalFormula |
| `si` | SI单位 | si |
| `cite`/`cite:p`/`cite:t`... | 文献引用 | cite / citeGroup |
| `ref`/`eq`/`numref` | 交叉引用 | crossReference |
| `abbr`/`abbreviation` | 缩写 | abbreviation |
| `term` | 术语引用 | - |
| `doc` | 文档引用 | - |
| `download` | 下载链接 | - |
| `kbd`/`keyboard` | 键盘按键 | kbd |
| `sub`/`subscript` | 下标 | subscript |
| `sup`/`superscript` | 上标 | superscript |
| `u`/`underline` | 下划线 | underline |
| `del`/`delete` | 删除线 | delete |
| `smallcaps` | 小型大写 | smallcaps |
| `raw:latex`/`raw:typst` | 行内原始内容 | raw |
| `span` | 通用行内容器 | span |
| `eval` | 行内表达式 | - |

## 相关概念

- [指令与角色基础](00-directive-role-basics.md)
- [数学公式](05-math.md)
- [交叉引用与引用](06-cross-references-citations.md)
