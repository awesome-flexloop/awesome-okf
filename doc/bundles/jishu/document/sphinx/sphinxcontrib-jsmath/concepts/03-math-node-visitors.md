---
type: Concept
title: 数学节点访问者
description: html_visit_math 和 html_visit_displaymath 函数详解、docutils visitor 模式、HTML 输出结构
tags: [sphinxcontrib-jsmath, visitor, html, math, docutils, nodes, SkipNode]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T15:30:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:30:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: jsmath-source
    resource: /references/jsmath-source.md
    title: sphinxcontrib-jsmath 源码信源登记
---

# 数学节点访问者

## docutils Visitor 模式

Sphinx 基于 docutils 构建，docutils 使用 **Visitor 模式**（访问者模式）将文档树（doctree）转换为输出格式（HTML、LaTeX 等）。其核心机制是：

1. 文档被解析为**节点树**（doctree），每个节点代表一个文档元素（段落、标题、数学公式等）
2. **Translator**（翻译器/写入器）遍历节点树，对每种节点类型调用对应的 `visit_xxx` 方法
3. `visit_xxx` 方法将节点内容写入输出缓冲区（如 HTML 字符串）
4. 遍历完子节点后调用 `depart_xxx` 方法（用于闭合标签等）

sphinxcontrib-jsmath 注册了两个 visit 函数来定制数学节点的 HTML 输出：
- `html_visit_math`：处理行内数学（`nodes.math`）
- `html_visit_displaymath`：处理块级数学（`nodes.math_block`）

这两个函数通过 `add_html_math_renderer` 注册，替代了 Sphinx 默认的数学渲染逻辑。

## html_visit_math：行内数学渲染

行内数学节点访问者处理 `` :math:`...` `` 角色生成的 `nodes.math` 节点：

```python
def html_visit_math(self: HTMLTranslator, node: nodes.math) -> None:
    self.body.append(self.starttag(node, 'span', '', CLASS='math notranslate nohighlight'))
    self.body.append(self.encode(node.astext()) + '</span>')
    raise nodes.SkipNode
```

### 逐行解析

**第1行**：写入开始标签

```python
self.body.append(self.starttag(node, 'span', '', CLASS='math notranslate nohighlight'))
```

- `self.body` 是 HTMLTranslator 的输出缓冲区（一个字符串列表）
- `self.starttag(node, tagname, suffix, **attributes)` 是 docutils 提供的辅助方法，生成 HTML 开始标签
- `node` 参数用于生成 `id` 等节点相关属性
- `'span'` 指定标签类型
- `''` 是 suffix（标签后的文本，如换行）
- `CLASS='math notranslate nohighlight'` 设置 CSS class：
  - `math`：jsMath 脚本的选择器，用于识别需要渲染的数学内容
  - `notranslate`：告诉 Google 翻译等工具不要翻译此元素（翻译会破坏 LaTeX 源码）
  - `nohighlight`：告诉代码高亮工具不要处理此元素

生成的 HTML 类似：
```html
<span class="math notranslate nohighlight">
```

**第2行**：写入编码后的公式文本和结束标签

```python
self.body.append(self.encode(node.astext()) + '</span>')
```

- `node.astext()` 提取节点的纯文本内容，即 LaTeX 源码（如 `E = mc^2`）
- `self.encode(text)` 对特殊字符进行 HTML 实体编码（`>` → `&gt;`，`<` → `&lt;`，`&` → `&amp;`）
- 追加 `'</span>'` 闭合标签

**第3行**：跳过默认处理

```python
raise nodes.SkipNode
```

`nodes.SkipNode` 是 docutils 的流控制异常。当 visit 函数抛出此异常时，docutils 会：
1. 跳过该节点的子节点遍历（math 节点是叶子节点，无子节点）
2. 跳过对应的 `depart_xxx` 函数调用
3. 继续处理下一个兄弟节点

这意味着 visit 函数必须自行输出完整的 HTML（包括开始和结束标签），因为 depart 不会被调用。

### 输出示例

输入 rst：
```rst
质能方程 :math:`E = mc^2` 是著名公式。
```

输出 HTML：
```html
<p>质能方程 <span class="math notranslate nohighlight">E = mc^2</span> 是著名公式。</p>
```

## html_visit_displaymath：块级数学渲染

块级数学访问者处理 `.. math::` 指令生成的 `nodes.math_block` 节点，逻辑比行内数学复杂得多，因为需要处理：
- nowrap 模式
- 公式编号和永久链接
- 多行公式（split 环境）
- 多段落分隔

```python
def html_visit_displaymath(self: HTMLTranslator, node: nodes.math_block) -> None:
    if node['nowrap']:
        self.body.append(self.starttag(node, 'div', CLASS='math notranslate nohighlight'))
        self.body.append(self.encode(node.astext()))
        self.body.append('</div>')
        raise nodes.SkipNode
    for i, part in enumerate(node.astext().split('\n\n')):
        part = self.encode(part)
        if i == 0:
            if node['number']:
                number = get_node_equation_number(self, node)
                self.body.append(f'<span class="eqno">({number})')
                self.add_permalink_ref(node, _('Permalink to this equation'))
                self.body.append('</span>')
            self.body.append(self.starttag(node, 'div', CLASS='math notranslate nohighlight'))
        else:
            self.body.append('<div class="math">')
        if '&' in part or '\\\\' in part:
            self.body.append('\\begin{split}' + part + '\\end{split}')
        else:
            self.body.append(part)
        self.body.append('</div>\n')
    raise nodes.SkipNode
```

### 分支1：nowrap 模式

```python
if node['nowrap']:
    self.body.append(self.starttag(node, 'div', CLASS='math notranslate nohighlight'))
    self.body.append(self.encode(node.astext()))
    self.body.append('</div>')
    raise nodes.SkipNode
```

当 `.. math::` 指令设置了 `:nowrap:` 选项时，`node['nowrap']` 为 `True`。nowrap 模式直接输出公式内容，不添加编号、不处理换行分段、不自动包裹 split 环境。这是最简单的块级数学输出路径。

输出结构：
```html
<div class="math notranslate nohighlight">公式内容</div>
```

### 分支2：标准模式（主循环）

标准模式将公式文本按双换行 `\n\n` 分割为多个段落，逐段处理：

#### 第一段（i == 0）

第一段需要特殊处理：设置 id 属性、处理编号和永久链接。

```python
if node['number']:
    number = get_node_equation_number(self, node)
    self.body.append(f'<span class="eqno">({number})')
    self.add_permalink_ref(node, _('Permalink to this equation'))
    self.body.append('</span>')
self.body.append(self.starttag(node, 'div', CLASS='math notranslate nohighlight'))
```

- `node['number']`：布尔值，表示该公式是否需要编号。仅当公式有 `:label:` 标签或 `math_number_all=True` 时为 True
- `get_node_equation_number(self, node)`：从 Sphinx 工具函数获取公式的编号字符串（如 `'1'`、`'1.1'`、`'2'` 等）
- `self.add_permalink_ref(node, title_text)`：添加一个段落链接（¶ 符号），点击可跳转到该公式
- 第一段的 `<div>` 使用 `self.starttag` 生成，因为需要包含 `id` 属性（用于锚点跳转）

编号公式输出结构：
```html
<span class="eqno">(1)<a class="headerlink" href="#equation-pythagorean" title="Permalink to this equation">¶</a></span>
<div class="math notranslate nohighlight" id="equation-pythagorean">
公式内容
</div>
```

无编号公式输出结构：
```html
<div class="math notranslate nohighlight">
公式内容
</div>
```

#### 后续段落（i > 0）

```python
else:
    self.body.append('<div class="math">')
```

后续段落的 `<div>` 使用普通的 `class="math"`（不带 `notranslate nohighlight`），且不包含 `id` 属性——注释中说 "but only once!"，表示 `notranslate nohighlight` 和 id 只在第一个 div 上设置。

#### split 环境自动检测

```python
if '&' in part or '\\\\' in part:
    self.body.append('\\begin{split}' + part + '\\end{split}')
else:
    self.body.append(part)
```

当段落文本包含 `&`（对齐标记）或 `\\`（换行符）时，自动用 `\begin{split}...\end{split}` 包裹。这是 LaTeX amsmath 包的 split 环境，用于多行对齐公式。

为什么需要自动检测？因为 rst 源文件中的多行公式：

```rst
.. math::

   (a + b)^2 &= a^2 + 2ab + b^2 \\
   (a - b)^2 &= a^2 - 2ab + b^2
```

在 HTML 中需要被正确包裹为：

```latex
\begin{split}(a + b)^2 &= a^2 + 2ab + b^2 \\
   (a - b)^2 &= a^2 - 2ab + b^2\end{split}
```

这样 jsMath 才能正确识别和渲染多行对齐公式。

### 输出示例汇总

| 场景 | HTML 输出 |
|------|----------|
| 行内公式 `` :math:`x^2` `` | `<span class="math notranslate nohighlight">x^2</span>` |
| 无编号块公式 | `<div class="math notranslate nohighlight">\nE = mc^2</div>` |
| 带编号块公式 | `<span class="eqno">(1)<a ...>¶</a></span><div class="math notranslate nohighlight" id="equation-xxx">\n...</div>` |
| nowrap 块公式 | `<div class="math notranslate nohighlight">...</div>`（同无编号，但无换行处理） |
| 多行split公式 | `<div class="math notranslate nohighlight">\n\\begin{split}...\\end{split}</div>` |
| numfig 编号公式 | `<span class="eqno">(1.1)<a ...>¶</a></span>...`（章号.序号格式） |

## CSS 类名说明

| 类名 | 作用 |
|------|------|
| `math` | jsMath 和其他数学渲染器的核心选择器，标识需要数学渲染的元素 |
| `notranslate` | Google Translate 等翻译工具跳过此元素，防止 LaTeX 代码被翻译破坏 |
| `nohighlight` | 代码高亮工具（如 highlight.js）跳过此元素 |
| `eqno` | 公式编号容器的类名，用于右对齐编号 |

## HTMLTranslator.body 操作模式

理解 visit 函数的关键是理解 HTMLTranslator 的输出模式：

1. **非字符串拼接，而是列表追加**：`self.body` 是一个字符串列表，通过 `append` 添加片段，最后 `''.join(self.body)` 生成完整 HTML。这种方式比字符串拼接更高效。
2. **直接写入而非返回**：visit 函数不返回 HTML 字符串，而是直接操作 `self.body`。这是 docutils visitor 模式的设计。
3. **异常控制流**：通过 `raise nodes.SkipNode` 替代返回值来控制遍历流程。

## 相关概念

- [扩展注册与 setup 函数](02-setup-and-registration.md)
- [智能JS加载机制](04-smart-js-loading.md)
- [基础使用示例](../examples/basic-usage.md)
- [公式编号与引用](../examples/equation-numbering.md)
- [源码信源登记](../references/jsmath-source.md)
