---
type: Example
title: "为演示添加自定义内容"
description: "学习如何向 jupyterlab-demo 添加自己的 Notebook、数据文件和 narrative 脚本，并通过 talks.yml 配置将其纳入演示流程"
tags: [custom-content, notebooks, data, narrative, tutorial, extend]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:30:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: narrative, resource: "/references/narrative-source.md", title: "Narrative演示脚本信源" }
  - { id: build, resource: "/references/build-py-source.md", title: "build.py源码信源" }
---

# 为演示添加自定义内容

jupyterlab-demo 不只是 Jupyter 团队的演示——它是一个可扩展的框架，任何人都可以添加自己的 Notebook、数据、演示脚本来定制演示内容。本示例演示如何从零开始添加一套完整的自定义演示内容。

## 你可以添加什么？

| 内容类型 | 放置目录 | 说明 |
|---------|---------|------|
| Jupyter Notebook | `notebooks/` | 交互式代码+文档+可视化 |
| 数据文件 | `data/` | CSV/JSON/GeoJSON/图片/音视频等 |
| 演示脚本 | `narrative/` | Markdown 格式的演讲步骤 |
| Binder 配置修改 | `.binder/` | 新依赖、postBuild 脚本 |

## 示例：添加一个 scikit-learn 机器学习演示

假设你要添加一个 scikit-learn 机器学习入门演示，包含：
1. 一个 scikit-learn 基础 Notebook
2. 示例数据集（breast cancer 数据集已内置sklearn，不需要额外文件）
3. 一个配套的演示脚本

### 步骤一：创建 Notebook

在 `notebooks/` 目录创建 `sklearn-intro.ipynb`：

你可以通过 JupyterLab 界面创建：
1. 启动 JupyterLab（本地）
2. File → New → Notebook → Python 3
3. 添加内容后保存为 `sklearn-intro.ipynb`

或者直接创建 JSON 文件。以下是一个最小化的 Notebook 内容框架：

```json
{
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": ["# scikit-learn 机器学习入门\n", "\n", "本Notebook演示使用scikit-learn进行经典机器学习任务。"]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {},
      "outputs": [],
      "source": [
        "from sklearn.datasets import load_breast_cancer\n",
        "from sklearn.model_selection import train_test_split\n",
        "from sklearn.ensemble import RandomForestClassifier\n",
        "from sklearn.metrics import accuracy_score, classification_report\n",
        "import pandas as pd"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {},
      "outputs": [],
      "source": [
        "# 加载数据\n",
        "data = load_breast_cancer()\n",
        "X = pd.DataFrame(data.data, columns=data.feature_names)\n",
        "y = pd.Series(data.target, name='target')\n",
        "print(f\"数据集形状: {X.shape}\")\n",
        "print(f\"特征数量: {len(data.feature_names)}\")\n",
        "X.head()"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {},
      "outputs": [],
      "source": [
        "# 划分训练/测试集\n",
        "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)\n",
        "\n",
        "# 训练随机森林\n",
        "clf = RandomForestClassifier(n_estimators=100, random_state=42)\n",
        "clf.fit(X_train, y_train)\n",
        "\n",
        "# 预测\n",
        "y_pred = clf.predict(X_test)\n",
        "print(f\"准确率: {accuracy_score(y_test, y_pred):.4f}\")\n",
        "print(classification_report(y_test, y_pred, target_names=['恶性', '良性']))"
      ]
    }
  ],
  "metadata": {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python"}
  },
  "nbformat": 4,
  "nbformat_minor:": 4
}
```

### 步骤二：确保依赖包含

scikit-learn 和 pandas 已经在 environment.yml 中（通过 `scikit-learn` 包和 pandas 依赖链）。如果要添加新的 Python 包，编辑 `.binder/environment.yml` 的 dependencies 部分：

```yaml
dependencies:
  - python=3.6
  - jupyterlab=0.27
  # ... 现有依赖 ...
  - scikit-learn       # 已存在
  - your-new-package   # 添加你的新包
```

> ⚠️ 注意：添加新依赖后，Binder 需要重新构建环境，本地需要 `conda env update`。

### 步骤三：添加演示脚本

在 `narrative/` 目录创建 `sklearn-demo.md`：

```markdown
# scikit-learn 演示脚本

## 开场（2分钟）
- JupyterLab 不仅是 Notebook 工具，更是完整的数据科学 IDE
- 今天演示用 scikit-learn 进行机器学习建模的完整流程
- 同时展示 JupyterLab 的多面板、数据查看、可视化能力

## 1. 数据加载与探索（3分钟）
- 打开 notebooks/sklearn-intro.ipynb
- 运行前两个代码单元格
- 展示 breast cancer 数据集的 DataFrame 输出
- 右键 DataFrame 输出 → "Create New View for Output"，将表格拖到右侧面板

## 2. 模型训练（3分钟）
- 运行模型训练单元格
- 展示准确率和分类报告
- 打开命令面板，演示可以边运行Notebook边搜索命令

## 3. 交互式调整（3分钟）
- 修改 n_estimators 参数从100改为200
- 重新运行，观察准确率变化
- 展示 JupyterLab 的代码补全和即时反馈

## 结尾（2分钟）
- 总结：数据加载→探索→建模→评估→调优，全流程在JupyterLab中完成
- 强调：可以在同一环境中处理代码、数据、文档、可视化
- Q&A
```

### 步骤四：配置 talks.yml

在 `talks.yml` 中添加新的演讲配置：

```yaml
sklearn-meetup:
    files:
        - narrative/sklearn-demo.md
        - data/iris.csv
    folders:
        notebooks: notebooks
    rename:
        notebooks/sklearn-intro.ipynb: notebooks/01-sklearn-intro.ipynb
        notebooks/Data.ipynb: notebooks/02-data-processing.ipynb
        notebooks/bqplot.ipynb: notebooks/03-interactive-viz.ipynb
        data/iris.csv: iris-dataset.csv
```

### 步骤五：重新构建

```bash
python build.py
```

构建输出目录 `sklearn-meetup/` 将包含你的自定义 Notebook 和演示脚本。

### 步骤六：本地测试

```bash
jupyter lab --notebook-dir=sklearn-meetup/
```

在 JupyterLab 中：
1. 验证 sklearn-intro.ipynb 可以正常运行
2. 验证所有数据文件可以打开
3. 验证演示脚本在 Markdown 预览中显示正确

## 进阶：添加自定义数据文件

如果你的演示需要自己的数据文件：

### 添加 CSV 数据

将文件放入 `data/` 目录：

```
data/
├── my-custom-data.csv    ← 你的CSV文件
└── ...
```

然后在 talks.yml 的 files 中引用：
```yaml
files:
    - data/my-custom-data.csv
```

### 添加 GeoJSON 数据

GeoJSON 文件直接放入 data/ 目录，jupyterlab-geojson 扩展会自动识别。

### 添加自定义格式数据

如果你的数据格式不在 JupyterLab 默认支持的范围内，有两种选择：

1. **使用代码加载**：在 Notebook 中用 pandas/json 等库加载，不需要专用查看器
2. **开发扩展**：为该格式开发专用查看器扩展（见 [开发 JupyterLab 扩展入门](05-extension-dev.md)）

## 进阶：添加图片和多媒体

### 截图和示意图

将图片放入 `data/` 目录：

```
data/
└── architecture-diagram.png
```

在 Notebook 或 Markdown 中引用：
```markdown
![架构图](../data/architecture-diagram.png)
```

### 视频和音频

MP4/WAV 文件放入 data/ 目录，JupyterLab 内置 HTML5 播放器支持直接播放。注意文件大小——大文件会减慢 git clone 和 Binder 构建。

## 文件命名最佳实践

1. **Notebook 编号**：使用数字前缀引导学习顺序（01-xxx, 02-xxx）
2. **简短文件名**：演示场景下使用简短友好的名称（通过 rename 实现）
3. **描述性名称**：文件名应能反映内容（不是 `Untitled.ipynb`）
4. **避免特殊字符**：文件名中避免空格、中文（在URL中可能出问题）

## 测试清单

添加内容后，逐项验证：

- [ ] 所有 Notebook 在 Python/R 内核中可以无错误运行
- [ ] 所有数据文件可以在对应查看器中打开
- [ ] Notebook 之间的引用路径正确（相对路径）
- [ ] 新依赖已添加到 environment.yml
- [ ] narrative 脚本中的文件名和路径与实际一致
- [ ] Binder 构建成功（通过 Binder 链接测试）
- [ ] 文件浏览器中的文件排列符合演示流程

## 常见问题

### Q: 我的 Notebook 引用了外部数据URL，离线时怎么办？
A: 将数据下载到 data/ 目录，修改 Notebook 引用本地路径。或者在 postBuild 中添加 wget 命令预先下载。

### Q: 可以添加 R Notebook 吗？
A: 可以。创建 Notebook 时选择 R 内核，Notebook 的 kernelspec metadata 会自动设为 R。

### Q: 大文件如何处理？
A: Git 不适合大文件。对于大文件：
- 使用 Git LFS（Large File Storage）
- 在 postBuild 中通过 wget/curl 下载
- 或者不纳入仓库，在演示时手动上传

### Q: 如何让我的 Binder 演示默认打开某个 Notebook？
A: 修改 Binder URL 的 `urlpath` 参数：
```
https://mybinder.org/v2/gh/your-username/your-repo/master?urlpath=lab/tree/notebooks/01-sklearn-intro.ipynb
```
或修改 workspace.json，在 initial 布局中打开特定文件。

## 相关概念

- [Notebook 示例解析](../concepts/05-notebook-examples.md)
- [数据文件与多格式查看器](../concepts/06-data-files.md)
- [创建自定义演讲配置](02-custom-demo-talk.md)
- [开发 JupyterLab 扩展入门](05-extension-dev.md)
