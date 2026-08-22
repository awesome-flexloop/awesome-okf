---
type: Example
title: "运行分析Notebook"
description: "在Binder和本地环境中运行Jupyter Surveys的分析notebooks：启动环境、导航notebook、执行分析、处理常见错误、保存结果。"
tags: ["notebook", "binder", "jupyter", "数据分析", "pandas", "运行"]
generated: "2026-08-22"
status: "stable"
stale_after: "2027-08-22"
prerequisites:
  - Binder方式：现代浏览器
  - 本地方式：Python 3.8+、Jupyter、pandas、matplotlib
sources:
  - resource: "/concepts/05-survey-analysis-pipeline.md"
    description: "调查分析Pipeline概念"
  - resource: "/concepts/09-binder-reproducibility.md"
    description: "Binder可复现性"
  - resource: "/references/analysis-utils-source.md"
    description: "分析工具函数解析"
---

# 运行分析Notebook

本示例指导你在Binder（云端）或本地环境中运行Jupyter Surveys的分析notebooks，以2018年JupyterCon用户测试数据集为例。

## 方式一：Binder零配置运行（推荐快速体验）

### 步骤1：打开Binder

点击链接：https://mybinder.org/v2/gh/jupyter/surveys/master

等待环境构建：
- 首次加载：约2-5分钟（构建Docker镜像）
- 后续加载：约10-30秒（命中缓存）

你会看到Jupyter Notebook的文件浏览器界面。

### 步骤2：导航到Notebook

在文件浏览器中：
1. 点击进入`surveys/`目录
2. 点击进入`2018-09-jupytercon-2018/`目录
3. 点击进入`notebooks/`目录
4. 点击打开`.ipynb`文件（如`01-data-exploration.ipynb`）

### 步骤3：运行Notebook

在Notebook界面中：
1. 点击菜单栏 **Kernel → Restart & Run All**
2. 等待所有cell执行完成
3. 查看输出结果（表格、图表等）

或者逐个执行cell：选中cell按`Shift+Enter`。

### 步骤4：交互式探索

运行完所有cell后，你可以：
- 修改代码cell中的参数（如过滤条件），重新运行
- 添加新的cell进行自定义分析
- 使用`File → Download as → Notebook (.ipynb)`保存你的修改

> ⚠️ **注意**：Binder环境是临时的，关闭浏览器后修改会丢失。请及时下载需要保存的notebook。

## 方式二：本地运行（推荐深度分析）

### 步骤1：克隆仓库并安装依赖

```bash
git clone https://github.com/jupyter/surveys.git
cd surveys

# 创建虚拟环境（推荐）
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate

# 安装依赖（使用binder配置）
pip install -r binder/requirements.txt

# 额外安装Jupyter（如果requirements.txt中没有）
pip install jupyterlab
```

### 步骤2：启动Jupyter

```bash
jupyter lab
# 或经典界面
jupyter notebook
```

浏览器会自动打开Jupyter界面。

### 步骤3：打开并运行Notebook

1. 导航到`surveys/2018-09-jupytercon-2018/notebooks/`
2. 打开notebook文件
3. **Kernel → Restart & Run All**

### 步骤4：安装额外依赖（如需要）

如果遇到`ModuleNotFoundError`：

```bash
# 在终端中安装缺失的包
pip install seaborn plotly  # 额外的可视化库
```

## 分析Notebook结构（2018 JupyterCon数据集）

2018年JupyterCon数据集的分析notebooks通常遵循以下结构：

| Notebook | 内容 |
|----------|------|
| `01-data-exploration.ipynb` | 加载CSV、基本统计、分布图、时间线 |
| `02-qualitative-coding.ipynb` | 主题编码过程、编码分布、共识检查 |
| `03-quantitative-analysis.ipynb` | 交叉分析、统计检验、可视化 |

运行顺序建议：从01开始按编号顺序运行。

## 使用analysis_utils.py工具函数

notebooks目录中的`analysis_utils.py`提供了常用的数据处理函数：

```python
# 在notebook中导入
from analysis_utils import dt, load_data, cleaner, classify_feedback

# 加载数据
df = load_data('../user_testing_data.csv')

# 清洗数据
df = cleaner(df)

# 自动分类反馈
df['category'] = df['feedback'].apply(classify_feedback)

# 查看分类结果
df['category'].value_counts().plot(kind='bar')
```

详见：[分析工具函数源码解析](../references/analysis-utils-source.md)

## 常见问题

### Binder相关

#### Q: Binder构建失败，显示"ResolveConflict"

**原因**：依赖版本冲突。

**解决**：等待几分钟重试，或检查仓库master分支是否有最近的修复。

#### Q: Notebook连接断开

**原因**：闲置超时（~10分钟无活动）或网络问题。

**解决**：
- 重新打开Binder链接（如果session未过期可恢复）
- 长时间计算建议使用本地环境

#### Q: 内存不足（Kernel死掉）

**原因**：Binder环境内存有限（约2GB）。

**解决**：
- 减少数据加载量（分批处理）
- 切换到本地环境运行

### 本地运行相关

#### Q: Kernel Error / Kernel无法启动

**原因**：Jupyter与Python环境不匹配。

**解决**：
```bash
# 确认使用正确的Python环境
python -m ipykernel install --user --name=surveys-env
# 在Jupyter中选择 Kernel → Change Kernel → surveys-env
```

#### Q: ModuleNotFoundError: No module named 'pandas'

**原因**：未安装依赖或使用了错误的Python环境。

**解决**：
```bash
# 确认虚拟环境已激活
which python  # Linux/macOS
where python  # Windows
# 安装依赖
pip install -r binder/requirements.txt
```

#### Q: FileNotFoundError: CSV文件找不到

**原因**：notebook中的相对路径错误。

**解决**：
- 确认当前工作目录正确（notebook所在目录）
- 使用`!pwd`（Linux/macOS）或`!cd`（Windows）查看当前目录
- 使用绝对路径或修正相对路径

#### Q: 图表不显示

**原因**：matplotlib后端问题。

**解决**：在notebook第一个cell添加：
```python
%matplotlib inline
import matplotlib.pyplot as plt
```

## 保存和分享你的分析

### 保存Notebook

- **Binder**：File → Download → Notebook (.ipynb)
- **本地**：Ctrl+S 自动保存

### 分享分析结果

1. **HTML导出**：File → Export as → HTML
2. **PDF导出**：File → Export as → PDF（需要LaTeX）
3. **贡献回仓库**：如果你做了有价值的分析，考虑提交PR到原仓库

## 自定义分析建议

运行完示例notebook后，你可以尝试：

1. **时间趋势分析**：按日期聚合反馈数量，查看调查期间的趋势
2. **词云生成**：对开放文本反馈生成词云（需要`wordcloud`包）
3. **情感分析**：使用NLP库（如nltk、transformers）分析反馈情感
4. **跨数据集对比**：加载多个数据集，对比2018-2023年的主题变化

## 相关内容

- [调查分析Pipeline](../concepts/05-survey-analysis-pipeline.md)：分析方法论
- [Binder可复现性](../concepts/09-binder-reproducibility.md)：Binder工作原理
- [分析工具函数](../references/analysis-utils-source.md)：工具函数API
- [数据集目录](../concepts/06-dataset-catalog.md)：选择感兴趣的数据集
