---
type: example
title: "Inline Expression 高级工作流"
description: "在 JupyterLab 中高效使用 inline expression 的技巧：表达式类型、错误处理、格式化输出、跨单元格引用和最佳实践"
tags: [jupyterlab-myst, inline-expression, eval, kernel, workflow, tips]
generated: 2026-08-23
verified: true
status: stable
stale_after: 2027-12-31
sources:
  - path: "/references/execution-components-src.md"
    facts: [F-030, F-031, F-032, F-033, F-034, F-035, F-036, F-041]
related_concepts:
  - /concepts/03-inline-expressions.md
  - /concepts/02-myst-markdown-cell.md
---

# Inline Expression 高级工作流

Inline expression 是 jupyterlab-myst 最强大的特性之一，让 Markdown 文本中的数据值随代码执行自动更新。本示例介绍高级用法和最佳实践。

## 工作原理回顾

```
代码单元格执行 (Shift+Enter)
  → NotebookActions.executed 信号
  → notebookCellExecuted()
  → executeUserExpressions()
  → kernel.requestExecute({ code: '', user_expressions: {...} })
  → 内核在当前命名空间求值表达式
  → 结果写入 cell metadata['user_expressions']
  → MySTWidget 重渲染显示结果
```

关键点：表达式在**当前内核的用户命名空间**中求值，可以访问之前代码单元格定义的所有变量。

## 表达式类型

### 数值输出

```python
# 代码单元格
accuracy = 0.9432
n_samples = 1500
```

```markdown
模型准确率: {eval}`accuracy:.2%`
样本数量: {eval}`n_samples`
```

### 字符串输出

```python
model_name = "ResNet-50"
dataset = "ImageNet"
```

```markdown
使用 {eval}`model_name` 在 {eval}`dataset` 上训练。
```

### 布尔输出

```python
is_converged = True
```

```markdown
模型收敛状态: {eval}`is_converged`
```

### 复杂对象

对于 DataFrame、数组等复杂对象，内核返回 text/plain 表示：

```python
import pandas as pd
df = pd.DataFrame({'a': [1,2,3], 'b': [4,5,6]})
summary = df.describe()
```

```markdown
数据摘要:

{eval}`summary`
```

> **注意**：复杂对象的 text/plain 表示可能很长，不适合内联显示。建议在代码单元格中做格式化，或使用简单标量值。

## 实用技巧

### 技巧1：在代码中预先格式化

与其在 eval 中做复杂格式化，不如在代码中计算标量值：

```python
# 代码单元格
import numpy as np
data = np.random.randn(1000)

# 预先计算需要展示的统计量
mean_val = data.mean()
std_val = data.std()
min_val = data.min()
max_val = data.max()
```

```markdown
数据统计:
- 均值: {eval}`mean_val:.4f`
- 标准差: {eval}`std_val:.4f`
- 范围: [{eval}`min_val:.2f`, {eval}`max_val:.2f`]
```

### 技巧2：使用 f-string 风格的计算表达式

表达式可以是任意有效的 Python 表达式，包括运算和函数调用：

```markdown
总样本数: {eval}`len(train_df) + len(test_df)`
信噪比: {eval}`signal_power / noise_power:.1f` dB
```

### 技巧3：条件输出

```python
status = "pass" if accuracy > 0.9 else "fail"
```

```markdown
测试结果: {eval}`status`
```

或直接在表达式中使用条件：

```markdown
模型状态: {eval}`"✅ 通过" if accuracy > 0.9 else "❌ 未通过"`
```

### 技巧4：引用前面单元格的变量

所有之前执行过的代码单元格定义的变量都可访问：

```python
# Cell 1
import numpy as np
x = np.linspace(0, 2*np.pi, 100)
```

```python
# Cell 2
y = np.sin(x)
```

```markdown
<!-- Cell 3 (Markdown) -->
x 的范围是 [{eval}`x.min():.2f`, {eval}`x.max():.2f`]，
y 的最大值是 {eval}`y.max():.4f`。
```

## 错误处理

### 变量未定义

如果表达式引用了未定义的变量，内核返回 error：

```markdown
未定义变量: {eval}`undefined_var`
```

显示：`NameError: name 'undefined_var' is not defined`

### 表达式语法错误

```markdown
语法错误: {eval}`1 +`
```

显示：`SyntaxError: invalid syntax`

### 处理错误的方法

1. **执行对应的代码单元格**：确保变量已定义
2. **重新执行 Markdown 单元格**：代码执行后，需要 Shift+Enter 重新执行 Markdown 单元格来刷新表达式
3. **检查内核状态**：如果内核重启过，所有变量都丢失，需要从头执行

## 刷新机制

### 自动刷新

执行代码单元格后，后续的 Markdown 单元格中的 inline expression **不会自动刷新**。需要手动 Shift+Enter 执行 Markdown 单元格来触发重新求值。

这是设计选择——避免频繁的内核请求影响性能。

### 推荐工作流

```
1. 执行所有代码单元格（Cell → Run All）
2. 从上到下逐个执行 Markdown 单元格（Shift+Enter）
3. 如果修改了某个代码单元格：
   a. 重新执行该代码单元格
   b. 重新执行引用了该代码输出的 Markdown 单元格
```

### 重启内核后

重启内核后所有变量丢失，inline expression 结果变为之前缓存的值（metadata 中的旧结果）。如果 Notebook 被标记为受信任，旧结果仍然显示但可能不正确。建议：

1. 重启内核后执行 Cell → Run All Cells
2. 所有 inline expression 重新求值

## MIME 类型支持

Inline expression 的结果可以是多种 MIME 类型，jupyterlab-myst 使用 JupyterLab 的 IRenderMimeRegistry 渲染：

| MIME 类型 | 渲染方式 |
|-----------|---------|
| `text/plain` | 纯文本 |
| `text/html` | HTML（经过 sanitizer 清洗）|
| `text/markdown` | Markdown 渲染 |
| `image/png` | PNG 图片 |
| `image/svg+xml` | SVG 图片 |
| `application/vnd.plotly.v1+json` | Plotly 图表 |
| `application/vnd.jupyter.widget-view+json` | Jupyter Widget |

这意味着表达式可以返回富输出（如图表、小部件），但注意：
- 富输出通常需要更多空间，不适合内联
- 建议代码单元格中生成图表，Markdown 中只放数值摘要
- Widget 输出需要 ipywidgets 支持

## 安全注意事项

1. **不要打开不受信任的 Notebook 并执行 Markdown 单元格**：inline expression 会在内核中执行代码，虽然表达式来自 Notebook 作者而非外部注入，但不受信任的 Notebook 可能包含恶意表达式。

2. **结果中的 HTML 会被清洗**：SanitizerProvider 确保 HTML 输出中不包含危险脚本。

3. **metadata 可被伪造**：.ipynb 文件中的 user_expressions metadata 可以被手动编辑，不受信任的 Notebook 可能包含伪造的结果文本。jupyterlab-myst 通过 trust 模型控制是否渲染。

## 常见陷阱

### 陷阱1：忘记执行代码单元格

如果代码单元格未执行，变量未定义，表达式显示错误。养成执行代码后再执行 Markdown 单元格的习惯。

### 陷阱2：修改代码后忘记刷新 Markdown

修改了代码单元格中的计算逻辑但忘记重新执行 Markdown 单元格，显示的是旧值。

### 陷阱3：内核状态不一致

执行了部分单元格导致内核状态线性不一致（如执行了 Cell 3 但未执行 Cell 2），表达式可能报错或显示意外值。建议使用 "Run All Cells" 确保一致性。

### 陷阱4：路径问题

```python
# 如果文件路径是相对路径，在不同工作目录下可能失败
df = pd.read_csv('data.csv')
```

确保 JupyterLab 的工作目录与数据文件位置一致。

### 陷阱5：大对象内联

```markdown
<!-- 不推荐：会输出整个 DataFrame -->
{eval}`df`

<!-- 推荐：只输出标量值 -->
共 {eval}`len(df)` 行，{eval}`df.shape[1]` 列。
```

## 完整示例

### 机器学习实验报告

````markdown
---
title: "分类模型对比实验"
---

# 分类模型对比实验

````

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

data = load_iris()
X_train, X_test, y_train, y_test = train_test_split(
    data.data, data.target, test_size=0.2, random_state=42
)

# 模型训练
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)
rf_acc = accuracy_score(y_test, rf.predict(X_test))

lr = LogisticRegression(max_iter=200)
lr.fit(X_train, y_train)
lr_acc = accuracy_score(y_test, lr.predict(X_test))

best_model = "RandomForest" if rf_acc > lr_acc else "LogisticRegression"
best_acc = max(rf_acc, lr_acc)
```

## 实验结果

| 模型 | 准确率 |
|------|--------|
| Random Forest | \{eval}`rf_acc:.2%` |
| Logistic Regression | \{eval}`lr_acc:.2%` |

**最佳模型**: \{eval}`best_model`（准确率 \{eval}`best_acc:.2%`）

数据集: \{eval}`data.feature_names` 共 \{eval}`len(data.data)` 个样本，
训练集 \{eval}`len(X_train)` 个，测试集 \{eval}`len(X_test)` 个。

## 相关文档

- [01-using-jupyterlab-myst.md](/examples/01-using-jupyterlab-myst.md)：基本使用
- [02-integrating-with-myst.md](/examples/02-integrating-with-myst.md)：与 myst-execute 集成
- [03-inline-expressions.md](/concepts/03-inline-expressions.md)：技术实现细节
