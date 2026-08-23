---
type: Example
title: Notebook AI 辅助工作流
description: 使用 Jupyter AI 在 Notebook 中完成数据加载、分析、可视化、调试的完整工作流
tags: [example, notebook, workflow, data-analysis, debugging, visualization]
sources:
  - id: user-guide
    resource: external/libs/jupyter/jupyter-ai/docs/source/users/index.md
    title: users/index.md
  - id: magics
    resource: external/libs/jupyter/jupyter-ai/docs/source/users/magics.md
    title: magics.md
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2026-08-22
---

# Notebook AI 辅助工作流

本示例展示如何使用 Jupyter AI 在真实数据分析场景中高效工作——从数据加载到可视化，再到调试和文档生成。

## 工作流概览

典型的 AI 辅助 Notebook 工作流：

```
数据加载 → 数据探索 → 数据清洗 → 分析建模 → 可视化 → 调试修复 → 文档生成
   ↑          ↑          ↑          ↑          ↑        ↑          ↑
   └──────────┴──────────┴──────────┴──────────┴────────┴──────────┘
                         AI 在每个环节辅助
```

## 场景：分析小费数据集

我们使用经典的 tips 数据集，演示 AI 辅助的完整分析流程。

### 步骤 1：加载数据并初始化

在聊天面板中发送：

> 帮我创建一个新的 Notebook，加载 seaborn 的 tips 数据集，展示数据的基本信息（列名、数据类型、缺失值统计）。

Jupyternaut 会生成代码并通过 MCP 工具直接在 Notebook 中创建单元格：

```python
import pandas as pd
import seaborn as sns

# 加载数据集
df = sns.load_dataset('tips')

# 基本信息
print("数据集形状:", df.shape)
print("\n列名和数据类型:")
print(df.dtypes)
print("\n缺失值统计:")
print(df.isnull().sum())
print("\n前5行:")
df.head()
```

**操作**：当弹出权限对话框时点击"允许"，代码会自动运行。

### 步骤 2：数据探索

发送：

> 对这个数据集做探索性分析：统计每餐的人数分布、账单金额和小费的统计摘要，以及性别和是否吸烟的分布。

AI 会生成多个分析单元格：

```python
# 基本统计
df.describe()

# 各列分布
import matplotlib.pyplot as plt
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
df['size'].value_counts().sort_index().plot(kind='bar', ax=axes[0,0], title='Party Size')
df['sex'].value_counts().plot(kind='bar', ax=axes[0,1], title='Gender')
df['smoker'].value_counts().plot(kind='bar', ax=axes[1,0], title='Smoker')
df['day'].value_counts().plot(kind='bar', ax=axes[1,1], title='Day')
plt.tight_layout()
plt.show()
```

### 步骤 3：特征工程

发送：

> 创建一个新列 tip_percentage 表示小费占账单的百分比，然后分析哪些因素影响小费比例最高。

AI 生成：

```python
# 创建小费比例列
df['tip_percentage'] = (df['tip'] / df['total_bill'] * 100).round(2)

# 按不同维度分析小费比例
print("按性别:")
print(df.groupby('sex')['tip_percentage'].mean())
print("\n按是否吸烟:")
print(df.groupby('smoker')['tip_percentage'].mean())
print("\n按日期:")
print(df.groupby('day')['tip_percentage'].mean())
print("\n按用餐时间:")
print(df.groupby('time')['tip_percentage'].mean())
```

### 步骤 4：可视化

发送：

> 创建一个有信息量的可视化，展示小费比例和总账单金额的关系，按是否吸烟区分颜色，用不同的形状区分用餐时间。添加回归线。

AI 生成 seaborn 可视化代码：

```python
import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='total_bill', y='tip_percentage',
                hue='smoker', style='time', s=100, alpha=0.7)
sns.regplot(data=df, x='total_bill', y='tip_percentage',
            scatter=False, color='gray', line_kws={'linestyle':'--'})
plt.title('Tip Percentage vs Total Bill')
plt.xlabel('Total Bill ($)')
plt.ylabel('Tip Percentage (%)')
plt.legend(title='Smoker / Time')
plt.show()
```

### 步骤 5：调试错误

假设你手动修改了代码但出错了（例如列名拼写错误）：

```python
# 错误代码
df.groupby('gender')['tip_percent'].mean()  # 列名错了：应该是 sex 和 tip_percentage
```

运行后报错，把错误信息或单元格拖入聊天：

> 这个单元格报错了：KeyError: 'gender'，请修复

AI 会识别列名错误，生成修复后的代码：

```python
# 修复：正确的列名是 'sex' 和 'tip_percentage'
df.groupby('sex')['tip_percentage'].mean()
```

### 步骤 6：生成总结

最后发送：

> 根据上面的分析，帮我生成一个 Markdown 单元格总结主要发现。包括：1) 小费比例的平均值和范围 2) 影响小费比例的关键因素 3) 一个有趣的发现。

AI 会生成 Markdown 内容：

```markdown
## Tips 数据集分析总结

### 关键发现
1. **平均小费比例**约为 16%，范围在 3% 到 71% 之间，标准差约 6%
2. **关键影响因素**：
   - 用餐时间：晚餐（Dinner）的小费比例略高于午餐（Lunch）
   - 日期：周日（Sun）和周六（Sat）的小费比例最高
   - 吸烟者与非吸烟者的平均小费比例差异不大
3. **有趣发现**：虽然账单金额越大小费绝对值越高，但小费比例反而略有下降趋势，说明大额账单的顾客倾向于按较低比例给小费。
```

使用代码块工具栏的"插入到活动单元格上方"按钮，将 Markdown 内容插入为 Markdown 单元格。

## 高效使用技巧

### 拖拽单元格作为上下文

将任何单元格拖入聊天输入框，AI 会自动读取该单元格的代码和输出作为上下文。这比复制粘贴高效得多。

### @file 引用文件

```
帮我分析 @file:data.csv 中的数据分布
```

### 包含选中内容

在 Notebook 中选中代码，勾选"包含选中内容"选项后发送消息，选中的代码自动作为上下文。

### 使用 Magic Commands 快速提问

安装 Magic Commands 后，在单元格中快速提问：

```python
%load_ext jupyter_ai_magic_commands
%ai "这段代码如何优化？"
```

### 多 AI 对比

在多 Persona 场景中 @多个 AI：

```
@Jupyternaut @Claude 请分别解释这段代码的时间复杂度
```

## 权限管理最佳实践

| 场景 | 建议权限模式 |
|---|---|
| 初始探索 | 允许一次（逐个审批） |
| 可信任的 AI 辅助编码 | 始终允许（本会话） |
| 危险操作（删除文件等） | 始终拒绝，手动执行 |

## 相关示例

- [首次聊天快速上手](first-chat.md)
- [Magic Commands 使用](magic-commands-usage.md)
- [配置自定义 MCP 服务器](custom-mcp-server.md)
