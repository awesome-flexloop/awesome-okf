---
type: Concept
title: Glue 变量粘贴
description: glue() 函数在代码中存储变量，{glue} 角色/指令在文档中粘贴，跨页面引用、NbGlueDomain
tags: [myst-nb, glue, variable, cross-reference, paste, scrapbook]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:30:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: mystnb-source
    resource: /references/mystnb-source.md
    title: MyST-NB 源码路径映射
---

## Glue 变量粘贴

Glue 是 MyST-NB 的变量粘贴系统，允许在代码 cell 中「粘贴」（存储）变量的显示值，然后在文档任意位置（包括其他页面）引用并渲染该变量。这实现了「计算一次，多处引用」的数据叙事模式。

## 基本用法

### 步骤 1：在代码中粘贴变量

```python
from myst_nb import glue
import matplotlib.pyplot as plt
import pandas as pd

# 创建数据
df = pd.DataFrame({"x": [1,2,3], "y": [4,5,6]})
glue("my_table", df)  # 粘贴 DataFrame

# 创建图表
fig, ax = plt.subplots()
ax.plot([1,2,3], [4,5,6])
glue("my_fig", fig, display=False)  # display=False 不立即显示
```

`glue(name, variable, display=True)` 参数：
- `name`：变量的唯一标识符（字符串），文档中通过此名引用
- `variable`：要存储的 Python 对象
- `display`：是否在代码 cell 输出中立即显示该对象（默认 True）

### 步骤 2：在文档中粘贴变量

#### 行内粘贴（角色）

```markdown
数据的平均值为 {glue}`mean_value`。
```

#### 指定格式粘贴

| 角色 | 说明 |
|------|------|
| `{glue}`key`` 或 `{glue:any}`key`` | 自动选择最佳 MIME 类型 |
| `{glue:text}`key`` | 纯文本格式 |
| `{glue:md}`key`` | Markdown 格式 |

#### 块级粘贴（指令）

````markdown
```{glue:figure} my_fig
:name: fig-my-plot

图标题：数据趋势图
```
````

| 指令 | 说明 |
|------|------|
| `{glue}` / `{glue:any}` | 自动选择格式块级粘贴 |
| `{glue:figure}` | 以 figure（带标题、可引用）形式粘贴图片 |
| `{glue:math}` | 以数学公式形式粘贴 |
| `{glue:md}` | 以 Markdown 形式粘贴 |

## 工作原理

1. **存储**：`glue()` 函数使用 IPython 的 `format_display_data()` 将变量格式化为 mimebundle，通过 `ipy_display(raw=True)` 输出带特殊 metadata 的 display 数据
2. **标记**：输出的 metadata 中包含 `scrapbook` 字段，记录 `name` 和 `mime_prefix`
3. **提取**：`extract_glue_data()` 在 notebook 转换阶段遍历所有 code cell 的 outputs，提取带 scrapbook 标记的数据
4. **存储**：提取的数据存入 `NbGlueDomain`（Sphinx Domain），按 key 索引
5. **解析**：{glue} 角色/指令创建 pending 引用节点
6. **替换**：`ReplacePendingGlueReferences` Post-Transform 在构建后期将 pending 节点替换为实际渲染内容

## display 参数

`display=True`（默认）：变量在代码 cell 输出中正常显示，同时被存储为 glue 数据。

`display=False`：变量不立即显示，但仍然存储。适用于只需要在文档其他位置引用，不需要在代码 cell 下方重复显示的情况。这通过在 MIME 类型前添加 `application/papermill.record/` 前缀实现（GLUE_PREFIX），渲染时自动跳过此前缀的类型。

## 跨页面引用

Glue 数据存储在 `NbGlueDomain` 中，支持跨页面引用。但要注意：
- glue 数据必须在引用它的页面**之前**被执行（即 toctree 中先出现）
- 跨文档引用需要文档已被 Sphinx 处理

## Glue 与 Papermill 的关系

Glue 机制借鉴了 [papermill](https://papermill.readthedocs.io/) 的 scrapbook 模式，使用 `application/papermill.record/` MIME 前缀。这意味着用 papermill 记录的数据也可以通过 MyST-NB 的 glue 引用。

## 重复 key 警告

如果多个 cell 使用相同的 glue name，会发出警告：

```
glue key 'my_var' duplicate [myst-nb.glue]
```

后一个会覆盖前一个。

## 使用场景

- **数值引用**：在正文中引用代码计算的统计值（如准确率、均值）
- **图表引用**：在正文中引用代码生成的图表，配合 {glue:figure} 实现带编号的图
- **表格引用**：在不同位置引用同一个 DataFrame
- **数学公式**：在代码中生成 LaTeX 公式，在正文中渲染
- **跨文档复用**：在 appendix 中计算结果，正文中引用

## 相关概念

- [Eval 内联求值](08-eval.md)
- [渲染与 MIME 类型](06-render-and-mime.md)
- [四阶段处理管线](03-processing-pipeline.md)
- [Glue 实战示例](/examples/03-glue-and-eval.md)
