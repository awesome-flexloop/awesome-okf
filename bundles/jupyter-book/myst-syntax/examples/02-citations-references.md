---
type: example
title: "引用与交叉引用实�?
description: "cite角色的文献引用、ref交叉引用、缩写、术语表、参考文献列表的完整示例"
tags: [example, citation, cross-reference, bibliography, glossary, abbr]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "mystmd/packages/myst-directives/src/"
  - path: "mystmd/packages/myst-roles/src/"
---

# 引用与交叉引用实�?
本文档提�?MyST 引用系统的完整可运行示例�?
## 交叉引用（Ref�?
### 引用图表

首先给图表添加标签：

````markdown
:::{figure} images/result.png
:label: fig-result
:width: 80%

实验结果图�?:::
````

然后在正文中引用�?
```markdown
�?{ref}`fig-result` 所示，实验结果验证了我们的假设�?
�?{ref}`结果�?<fig-result>` 所�?..  <!-- 自定义显示文�?-->
```

### 引用表格

````markdown
:::{table} 实验数据
:label: tbl-data

| 组别 | 准确�?|
|------|--------|
| A | 95.2% |
| B | 87.4% |
:::

数据�?{ref}`tbl-data`�?```

### 引用公式

````markdown
```{math}
:label: eq-bayes

P(A|B) = \frac{P(B|A)P(A)}{P(B)}
```

根据贝叶斯定理（{eq}`eq-bayes`�?..
```

### 引用代码�?
````markdown
```{code} python
:label: code-train
:caption: 模型训练函数

def train(model, data):
    model.fit(data)
```

训练函数�?{ref}`code-train`�?```

## 文献引用（Cite�?
### 基础引用

首先�?myst.yml 中配置参考文献：

```yaml
project:
  bibliography:
    - references.bib
```

references.bib 示例�?
```bibtex
@book{knuth1984texbook,
  author = {Knuth, Donald E.},
  title = {The TeXbook},
  year = {1984},
  publisher = {Addison-Wesley}
}

@article{vaswani2017attention,
  author = {Vaswani, Ashish and others},
  title = {Attention is All You Need},
  journal = {NeurIPS},
  year = {2017}
}
```

### 叙述�?vs 括号式引�?
```markdown
% 叙述式（narrative）：Knuth (1984)
{cite:t}`knuth1984texbook` 提出�?TeX 排版系统�?
% 括号式（parenthetical）：(Knuth 1984)
这一问题在早期已有讨�?{cite:p}`knuth1984texbook`�?
% 默认 cite 等同�?cite:t
Transformer 架构 {cite}`vaswani2017attention` 改变了NLP领域�?```

### 多引�?
```markdown
多项工作 {cite:p}`knuth1984texbook, vaswani2017attention` 都采用了...
```

### 部分引用（仅年份/仅作者）

```markdown
% 仅年�?�?{cite:year}`vaswani2017attention` 年，Transformer 被提出�?
% 仅作�?{cite:author}`vaswani2017attention` 等人提出了注意力机制�?```

### 引用前后缀

```markdown
�?{cite:p}`{see}knuth1984texbook{p. 100-120}` 所�?..
% 输出�?see Knuth 1984, p. 100-120)
```

### Alpha 风格引用

```markdown
�?{cite:alp}`knuth1984texbook` 所�?..
% 输出：[Knu84]
```

### 参考文献列�?
在文档末尾插入参考文献列表：

```markdown
## 参考文�?
:::{bibliography}
:::
```

过滤参考文献（可选）�?
```markdown
:::{bibliography}
:filter: type == "article"
:::
```

## 缩写（Abbr�?
```markdown
{abbr}`HTML (HyperText Markup Language)` 是网页的标准标记语言�?
{abbr}`CSS (Cascading Style Sheets)` 用于样式控制�?
{abbr}`API (Application Programming Interface)` 提供了程序间通信的方式�?```

鼠标悬停在缩写上会显示全称�?
## 术语表（Glossary�?
### 定义术语

```markdown
:::{glossary}
MyST
  Markedly Structured Text，一种基�?Markdown 的扩展标记语言�?  支持科学写作所需的指令、角色和交叉引用等功能�?
Directive（指令）
  MyST 中的块级扩展元素，使�?:::{name}::: 语法定义�?  用于创建提示框、代码块、图表、表格等富内容�?
Role（角色）
  MyST 中的行内扩展元素，使�?{name}`content` 语法定义�?  用于创建引用、数学公式、缩写等行内容器�?:::
```

### 引用术语

```markdown
使用 {term}`Directive（指令）` 可以创建块级扩展元素�?{term}`MyST` 提供了丰富的写作功能�?```

## 边栏（Aside/Sidebar�?
```markdown
:::{sidebar} 快速提�?:class: tip

**快捷�?*：按 `Ctrl+S` 保存，`Ctrl+Z` 撤销�?:::
```

```markdown
:::{margin}
这是页边注，显示在正文旁边�?:::
```

## 目录（TOC�?
```markdown
:::{toc}
:context: page
:depth: 3
:::
```

不同 context 选项�?- `:context: project`：整个项目的所有页�?- `:context: section`：当前章节（`contents` 别名默认�?- `:context: page`：当前页面的标题
- `:context: children`：子页面

## 综合示例：学术论文片�?
````markdown
---
title: 基于Transformer的文本分类研�?authors:
  - name: 张三
---

# 引言

�?{cite:t}`vaswani2017attention` 提出 Transformer 架构以来�?自然语言处理领域发生了重大变革。{abbr}`NLP (Natural Language Processing)`
任务的性能得到了显著提升�?
## 方法

模型结构�?{ref}`fig-model` 所示�?
:::{figure} images/model.png
:label: fig-model
:width: 90%

Transformer 文本分类模型架构�?:::

注意力计算公式如下：

```{math}
:label: eq-attention

\text{Attention}(Q,K,V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
```

�?{eq}`eq-attention` 所�?..

## 实验

实验结果�?{ref}`tbl-results`�?
:::{table} 实验结果对比
:label: tbl-results

| 模型 | 准确�?| F1�?|
|------|--------|------|
| LSTM | 82.3% | 0.81 |
| BERT | 91.5% | 0.91 |
| Ours | **93.2%** | **0.93** |
:::

训练代码�?{ref}`code-train`�?
## 参考文�?
:::{bibliography}
:::

## 术语�?
:::{glossary}
Transformer
  一种基于自注意力机制的神经网络架构�?
Attention（注意力机制�?  让模型能够关注输入序列中重要部分的机制�?:::

:::{show-index} 索引
:::
````
