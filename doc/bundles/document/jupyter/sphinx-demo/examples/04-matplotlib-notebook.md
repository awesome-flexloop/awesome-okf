---
type: Example
title: 嵌入可交互 Matplotlib 笔记本
description: 使用 notebooklite 指令嵌入带有 Matplotlib 可视化的可交互 Notebook，包含 strip_tagged_cells 用法和图表渲染
tags: [notebooklite, matplotlib, visualization, code-cell, strip]
difficulty: intermediate
estimated_time: 15min
prerequisites:
  - 完成 Pyodide 或 Xeus 配置示例
  - 了解 MyST Markdown 语法
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: matplotlib-demo
    resource: /references/conf-py-source.md
    title: matplotlib_demo.md 源码
---

## 目标

创建一个嵌入了可交互 Matplotlib 可视化的文档页面。读者可以直接在浏览器中修改绘图参数并实时查看结果。

## 前置配置

确保 conf.py 中启用以下配置：

```python
extensions = [
    "jupyterlite_sphinx",
    "myst_nb",
]

# 关键：启用单元格剥离
strip_tagged_cells = True

# Pyodide 内核无需预装（matplotlib 是 Pyodide 预置包）
# Xeus 内核需在 environment.yml 中添加 matplotlib-base
```

## 创建 Notebook 页面

在 `docs/source/` 下创建 `matplotlib_demo.md`：

````markdown
# Matplotlib 交互式绘图

本页面演示如何在文档中嵌入可交互的 Matplotlib 绘图环境。
点击按钮后，你可以在浏览器中直接修改代码并重新运行，实时查看图表变化。

+++ {"tags": ["jupyterlite_sphinx_strip"]}

:::{tip}
💡 这个提示框只在文档页面上可见，点击"打开为Notebook"按钮后不会出现在JupyterLite中。
:::

下面的单元格配置了 Matplotlib 的内联显示模式，并导入了必要的库。
在 Notebook 中这些代码是可见的，但在文档中通过 `remove-input` 标签隐藏了。

```{code-cell} ipython3
:tags: [remove-input]
%matplotlib inline
import matplotlib.pyplot as plt
import numpy as np
```

## 正弦波绘图

运行以下代码生成正弦波图像。尝试修改 `frequency` 和 `amplitude` 参数观察变化：

```{code-cell} ipython3
# 修改这些参数
frequency = 2.0  # 频率
amplitude = 1.0  # 振幅

x = np.linspace(0, 4 * np.pi, 500)
y = amplitude * np.sin(frequency * x)

plt.figure(figsize=(10, 4))
plt.plot(x, y, linewidth=2, color='#f37726')
plt.title(f'Sine Wave (freq={frequency}, amp={amplitude})')
plt.xlabel('x')
plt.ylabel('y')
plt.grid(True, alpha=0.3)
plt.axhline(y=0, color='k', linewidth=0.5)
plt.tight_layout()
plt.show()
```

## 多子图示例

```{code-cell} ipython3
fig, axes = plt.subplots(2, 2, figsize=(10, 8))

x = np.linspace(0, 2*np.pi, 200)

# 正弦
axes[0, 0].plot(x, np.sin(x), color='blue')
axes[0, 0].set_title('sin(x)')
axes[0, 0].grid(True, alpha=0.3)

# 余弦
axes[0, 1].plot(x, np.cos(x), color='red')
axes[0, 1].set_title('cos(x)')
axes[0, 1].grid(True, alpha=0.3)

# 正切（处理断点）
y_tan = np.tan(x)
y_tan[np.abs(y_tan) > 10] = np.nan
axes[1, 0].plot(x, y_tan, color='green')
axes[1, 0].set_title('tan(x)')
axes[1, 0].set_ylim(-5, 5)
axes[1, 0].grid(True, alpha=0.3)

# 阻尼振荡
axes[1, 1].plot(x, np.exp(-x/3) * np.sin(3*x), color='purple')
axes[1, 1].set_title('Damped oscillation')
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

## 打开为 Notebook

点击下方按钮在 JupyterLite 中打开此页面作为 Notebook：

```{notebooklite}
:width: 100%
:height: 600px
:new_tab_button_text: "在新标签页中打开 Notebook"
```
````

## 关键技术点解析

### 1. strip 标签的使用

```markdown
+++ {"tags": ["jupyterlite_sphinx_strip"]}
```

这个标记后面的单元格在文档中显示，但在 JupyterLite Notebook 中被移除。用于放置：
- 使用说明和提示
- notebooklite 指令本身
- 面向读者的引导文字

### 2. remove-input 标签

````markdown
```{code-cell} ipython3
:tags: [remove-input]
%matplotlib inline
import matplotlib.pyplot as plt
import numpy as np
```
````

`remove-input` 是 MyST-NB 的标签，在文档页面隐藏代码单元格的输入部分（只显示输出），但在 Notebook 中保留代码。这让文档页面更简洁，而 Notebook 中用户能看到完整的导入代码。

### 3. code-cell 语法

`{code-cell} ipython3` 声明一个 Python 代码单元格。在文档构建时：
- 若 `nb_execution_mode` 为 "auto" 或 "force"，Sphinx 会执行代码并嵌入输出
- 在 JupyterLite Notebook 中，用户可以编辑和重新运行

### 4. notebooklite 指令

````markdown
```{notebooklite}
:width: 100%
:height: 600px
:new_tab_button_text: "在新标签页中打开 Notebook"
```
````

这个指令在页面中嵌入 Notebook 视图，并提供新标签页打开按钮。当前页面中所有 `{code-cell}` 单元格会被组装成一个 Notebook 加载到 iframe 中。

## Pyodide vs Xeus 的差异

### Pyodide 内核

Matplotlib 是 Pyodide 的预置包，直接可用。如需其他包：

```python
import piplite
await piplite.install("seaborn")
import seaborn as sns
```

### Xeus 内核

需要在 `environment.yml` 中声明 matplotlib 依赖：

```yaml
dependencies:
  - numpy
  - matplotlib-base
```

注意使用 `matplotlib-base` 而非 `matplotlib`，后者包含 GUI 后端在 WASM 环境中不可用。

## 嵌入外部 .ipynb 文件

如果你已有现成的 Jupyter Notebook 文件（.ipynb），可以直接引用：

````markdown
```{notebooklite}
:notebook: ../custom_contents/my_notebook.ipynb
:width: 100%
:height: 500px
```
````

文件需要通过 `jupyterlite_contents` 配置包含：

```python
jupyterlite_contents = ["custom_contents/*"]
```

## 图表渲染注意事项

1. **使用 `%matplotlib inline`**：确保图表在 Notebook 输出中内联显示
2. **调用 `plt.show()`**：显式调用 show() 确保图表渲染
3. **避免 GUI 后端**：不要使用 `%matplotlib notebook` 或 `qt` 后端，浏览器中只支持 inline 和 ipympl
4. **使用 `plt.tight_layout()`**：防止标题/标签被截断
5. **设置合适的 figsize**：考虑 iframe 宽度，推荐 `figsize=(10, 4)` 或类似尺寸

## 进阶：交互式控件

结合 ipywidgets 创建真正的交互式图表（需要 Xeus 内核 + ipywidgets 包）：

```python
import ipywidgets as widgets
from IPython.display import display

def plot_sine(freq=1.0, amp=1.0):
    x = np.linspace(0, 4*np.pi, 500)
    plt.figure(figsize=(10, 3))
    plt.plot(x, amp * np.sin(freq * x))
    plt.ylim(-2, 2)
    plt.grid(True, alpha=0.3)
    plt.show()

widgets.interact(plot_sine, freq=(0.5, 5.0, 0.1), amp=(0.1, 2.0, 0.1))
```

在 Pyodide 中也可以通过 piplite 安装 ipywidgets 实现类似效果。

## 验证清单

- [ ] 构建成功，Notebook 页面正常渲染
- [ ] 文档页面上的 strip 单元格内容可见
- [ ] 点击 notebooklite 按钮后 Notebook 中没有 strip 单元格
- [ ] Matplotlib 图表在 iframe 中正确显示
- [ ] 修改代码重新运行后图表更新

## 相关内容

- [/concepts/07-notebook-embedding.md](/concepts/07-notebook-embedding.md)：NotebookLite 机制详解
- [/concepts/03-sphinx-conf.md](/concepts/03-sphinx-conf.md)：strip_tagged_cells 配置
- [/examples/02-pyodide-setup.md](/examples/02-pyodide-setup.md)：Pyodide 完整配置
