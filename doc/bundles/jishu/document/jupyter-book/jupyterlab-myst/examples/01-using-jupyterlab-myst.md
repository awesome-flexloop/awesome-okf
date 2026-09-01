---
type: example
title: "安装与基本使用"
description: "jupyterlab-myst 的安装方法、在 Notebook 中使用 MyST Markdown 的完整指南，包括 directives、inline expression、任务列表等特性"
tags: [jupyterlab-myst, install, usage, notebook, quickstart]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/plugin-entry-src.md"
    facts: [F-003, F-004, F-005, F-006]
  - path: "/references/execution-components-src.md"
    facts: [F-030, F-034, F-035]
related_concepts:
  - /concepts/00-architecture-plugins.md
  - /concepts/05-syntax-security.md
  - /concepts/03-inline-expressions.md
---

# 安装与基本使用

本示例展示如何安装 jupyterlab-myst 扩展并在 JupyterLab 中使用 MyST Markdown 增强功能。

## 安装

### 前提条件

- JupyterLab 4.0+
- Python 3.8+
- Node.js（从源码安装时需要）

### 使用 pip 安装

```bash
pip install jupyterlab-myst
```

安装后启动 JupyterLab：

```bash
jupyter lab
```

扩展自动激活（三个插件均设置 autoStart: true），无需手动启用。

### 使用 conda 安装

```bash
conda install -c conda-forge jupyterlab-myst
```

### 验证安装

在 JupyterLab 中：
1. 创建新 Notebook 或打开现有 .ipynb 文件
2. 创建 Markdown 单元格
3. 输入以下内容并 Shift+Enter：

```markdown
# 标题

这是 **MyST** Markdown 测试。

- [x] 已完成任务
- [ ] 待办任务
```

如果渲染出复选框（而非显示 `[x]` 文本），说明 jupyterlab-myst 已成功安装。

## 基本 Markdown 增强

### 任务列表

在 Markdown 单元格中输入：

```markdown
## 待办事项

- [x] 完成数据加载
- [x] 数据清洗
- [ ] 模型训练
- [ ] 结果可视化
```

渲染后显示交互式复选框，点击可以切换勾选状态（自动更新 Markdown 源码）。

### 数学公式

支持 LaTeX 数学公式：

```markdown
行内公式：$E = mc^2$

块级公式：

$$
\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
$$
```

可在 frontmatter 中定义宏：

```markdown
---
math:
  R: '\mathbb{R}'
---

实数集合 $\R$ 是所有实数的集合。
```

### 脚注

```markdown
这是一个带脚注的句子[^1]。

[^1]: 这是脚注内容。
```

## 使用 Directives

### 卡片（card）

````markdown
```{card} 提示
:class-header: bg-light
**注意**：这是一条重要提示。
- 第一点
- 第二点
```
````

### 网格布局（grid）

````markdown
::::{grid} 2
:::{grid-item}
**列 1**

这是第一列的内容。
:::
:::{grid-item}
**列 2**

这是第二列的内容。
:::
::::
````

### 标签页（tab-set）

````markdown
::::{tab-set}
:::{tab-item} Python
```python
print("Hello from Python")
```
:::
:::{tab-item} R
```r
print("Hello from R")
```
:::
::::
````

### 证明/定理环境

````markdown
```{theorem} 毕达哥拉斯定理
在直角三角形中，斜边的平方等于两直角边的平方和：

$$a^2 + b^2 = c^2$$
```
````

## Inline Expression（内联表达式）

### 基本用法

1. 创建代码单元格并执行：

```python
import pandas as pd
import numpy as np

df = pd.DataFrame({
    'value': np.random.randn(100)
})
mean_val = df['value'].mean()
```

2. 在后续的 Markdown 单元格中使用 `{eval}` role：

```markdown
## 数据分析结果

数据集共有 {eval}`len(df)` 条记录，
均值为 {eval}`mean_val:.4f`，
标准差为 {eval}`df['value'].std():.4f`。
```

3. Shift+Enter 执行该 Markdown 单元格后，表达式自动求值并显示结果。

### 注意事项

- 表达式必须在当前内核命名空间中有效（前面代码单元格已定义的变量）
- 代码单元格执行后，Markdown 单元格中的表达式不会自动刷新——需要重新执行 Markdown 单元格（Shift+Enter）
- 表达式结果保存在 Notebook metadata 中，保存后重新打开仍然可见（需受信任）
- 如果变量不存在或表达式出错，会显示错误信息

### 格式化输出

内联表达式支持 Python 格式化语法：

```markdown
- 百分比：{eval}`accuracy:.1%`
- 科学计数法：{eval}`large_number:.2e`
- 日期：{eval}`df['date'].min()`（直接输出对象的 __repr__）
```

> **注意**：格式化语法（如 `:.2f`）不是 Python f-string 语法，而是 MyST 的 eval role 格式化。内核返回的是 MIME bundle（通常是 `text/plain`），格式化可能不总是按预期工作。复杂格式化建议在代码单元格中完成。

## Frontmatter

在 Markdown 单元格开头使用 YAML frontmatter：

```markdown
---
title: "数据分析报告"
authors:
  - name: "张三"
    affiliations: "数据科学部"
date: 2024-01-15
---

# 数据分析报告

报告正文...
```

Frontmatter 渲染为标题块（FrontmatterBlock），包含标题、作者、日期等元数据。

## 交叉引用

```markdown
```{figure} https://example.com/chart.png
:name: fig-chart
数据图表
```

如图 [](fig-chart) 所示...
```

使用 `{ref}` role 或 `[](#label)` 语法引用带 label 的对象。

## 在 Markdown Viewer 中使用

jupyterlab-myst 也支持 JupyterLab 的 Markdown Viewer（打开独立 .md 文件）：

1. 在 JupyterLab 中打开 .md 文件
2. 文件自动使用 MyST 渲染
3. 支持所有 directives、脚注、交叉引用等特性
4. Frontmatter 默认显示（jupyterlab-myst 自动设置 hideFrontMatter=false）

## 故障排除

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| Markdown 显示为原始文本 | 扩展未启用 | 检查 Extension Manager 中 jupyterlab-myst 是否启用 |
| 内联表达式不显示结果 | 内核未启动/Notebook 不受信任 | 执行代码单元格建立信任；确认内核运行中 |
| 复选框不可点击 | 单元格处于编辑模式 | Shift+Enter 切换到渲染模式 |
| 图片不显示 | 相对路径解析问题 | 使用绝对路径或 JupyterLab 附件功能 |
| 数学公式不渲染 | MathJax 未加载 | 检查 JupyterLab 数学渲染设置 |
|  directives 显示为原始代码 | 语法错误 | 检查 backtick 数量和嵌套缩进 |

## 相关文档

- [02-integrating-with-myst.md](02-integrating-with-myst.md)：与 MyST 构建流程集成
- [03-inline-expression-workflow.md](03-inline-expression-workflow.md)：内联表达式高级工作流
- [00-architecture-plugins.md](../concepts/00-architecture-plugins.md)：插件架构详解
- [05-syntax-security.md](../concepts/05-syntax-security.md)：完整语法特性列表
