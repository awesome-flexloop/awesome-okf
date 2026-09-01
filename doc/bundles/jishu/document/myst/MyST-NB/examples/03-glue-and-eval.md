---
type: Example
title: Glue 与 Eval 变量使用
description: glue() 粘贴变量、{glue} 引用、{eval} 内联求值的完整示例
tags: [myst-nb, glue, eval, variable, cross-reference]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T02:30:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: mystnb-source
    resource: /references/mystnb-source.md
    title: MyST-NB 源码路径映射
---

## Glue 与 Eval 变量使用

本示例展示如何使用 Glue 粘贴变量和 Eval 内联求值实现数据叙事。

## conf.py 配置

```python
extensions = ["myst_nb"]
nb_execution_mode = "cache"  # glue 在任何模式下都可用
# eval 需要 inline 模式才能在正文中实时求值
# 注意：glue 不需要 inline 模式
```

如果需要使用 eval，设置：
```python
nb_execution_mode = "inline"
```

## Glue 基本用法

### 1. 在代码中粘贴变量

````markdown
---
file_format: mystnb
kernelspec:
  name: python3
---

# 数据分析报告

```{code-cell}
import numpy as np
import pandas as pd
from myst_nb import glue
import matplotlib.pyplot as plt

# 生成数据
np.random.seed(42)
n = 100
x = np.random.randn(n)
y = 2 * x + np.random.randn(n) * 0.5

# 计算统计量
mean_x = x.mean()
std_x = x.std()
corr = np.corrcoef(x, y)[0, 1]

# 粘贴数值变量
glue("n_samples", n)
glue("mean_x", mean_x)
glue("std_x", std_x)
glue("correlation", corr)

# 创建图表并粘贴
fig, ax = plt.subplots(figsize=(6, 4))
ax.scatter(x, y, alpha=0.6)
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_title("Scatter Plot")
glue("scatter_fig", fig, display=False)  # display=False 不立即显示
```

### 2. 在正文中引用 Glue 变量

我们生成了 {glue:text}`n_samples` 个样本，
X 的均值为 {glue:text}`mean_x:.3f`，
标准差为 {glue:text}`std_x:.3f`，
X 与 Y 的相关系数为 {glue:text}`correlation:.3f`。

### 3. 以 Figure 形式粘贴图片

```{glue:figure} scatter_fig
:name: fig-scatter
:figwidth: 400px

X-Y 散点图，数据具有明显的线性关系。
```

图 {ref}`fig-scatter` 展示了 X 和 Y 的散点关系。
````

## 输出效果

在构建后的文档中：
- `{glue:text}`n_samples`` → 显示为 `100`
- `{glue:text}`mean_x:.3f`` → 显示为均值的三位小数值
- `{glue:figure}` 插入完整的图，带标题和编号
- `{ref}`fig-scatter`` → 交叉引用为"图 1"

## Glue 粘贴不同类型数据

### 粘贴 DataFrame

````markdown
```{code-cell}
import pandas as pd
df = pd.DataFrame({
    "指标": ["准确率", "精确率", "召回率", "F1"],
    "模型A": [0.92, 0.89, 0.91, 0.90],
    "模型B": [0.95, 0.94, 0.93, 0.93],
})
glue("results_table", df)
```

模型结果对比：

```{glue}
results_table
```
````

### 粘贴数学公式

````markdown
```{code-cell}
from IPython.display import Latex
formula = Latex(r"R^2 = 1 - \frac{\sum(y_i - \hat{y}_i)^2}{\sum(y_i - \bar{y})^2}")
glue("r2_formula", formula, display=False)
```

决定系数定义为：{glue:math}`r2_formula`
````

### 粘贴 Markdown

````markdown
```{code-cell}
from IPython.display import Markdown
md_text = Markdown("**加粗文字**和*斜体文字*")
glue("md_output", md_text)
```

{glue:md}`md_output`
````

## Eval 内联求值

Eval 需要 `nb_execution_mode = "inline"`。

````markdown
---
file_format: mystnb
kernelspec:
  name: python3
---

# Eval 示例

```{code-cell}
import numpy as np
data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
n = len(data)
mean_val = data.mean()
```

数据共有 {eval}`n` 个值，平均值为 {eval}`mean_val`。
总和为 {eval}`data.sum()`，最大值为 {eval}`data.max()`。

### 块级 Eval

统计摘要：

```{eval}
data.describe() if hasattr(data, 'describe') else f"mean={data.mean()}, std={data.std():.3f}"
```
````

> 注意：默认情况下 `eval_name_regex` 只允许简单变量名。如果需要方法调用（如 `data.sum()`），需要放宽正则：
> ```python
> nb_eval_name_regex = r"^[a-zA-Z_][a-zA-Z0-9_.\[\]()'\"]*$"
> ```

## Glue vs Eval 选择

| 需求 | 使用 |
|------|------|
| 在正文中引用代码计算的数值 | Glue（稳定，不需 inline 模式） |
| 在正文任意位置插入图表 | Glue + {glue:figure} |
| 跨页面引用变量 | Glue（NbGlueDomain） |
| 句子中实时求值简单变量 | Eval（需要 inline 模式） |
| 块级显示计算结果 | Glue 或 Eval |

## 注意事项

1. Glue 变量名全局唯一，重复定义会覆盖并发出警告
2. Glue 的 {glue:figure} 需要先 `display=False` 避免重复显示
3. Eval 仅在 `inline` 模式下工作，需要持久 kernel
4. Eval 表达式受 `nb_eval_name_regex` 限制，注意安全
5. 跨页面 Glue 引用需要被引用页面先执行（按 toctree 顺序）

## 相关概念

- [Glue 变量粘贴](../concepts/07-glue.md)
- [Eval 内联求值](../concepts/08-eval.md)
- [执行模式与缓存](../concepts/05-execution-modes.md)
- [渲染与 MIME 类型](../concepts/06-render-and-mime.md)
