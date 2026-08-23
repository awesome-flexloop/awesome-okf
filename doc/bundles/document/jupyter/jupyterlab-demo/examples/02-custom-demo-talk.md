---
type: Example
title: "创建自定义演讲配置"
description: "学习如何在 talks.yml 中添加自己的演讲配置，从共享素材库选择文件、定义重命名映射，为特定会议或受众定制演示材料"
tags: [talks.yml, customization, configuration, build, demo-talk, yaml]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:30:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: build, resource: "/references/build-py-source.md", title: "build.py源码信源" }
  - { id: talks, resource: "/references/talks-yml-source.md", title: "talks.yml信源" }
---

# 创建自定义演讲配置

本示例教你如何在 `talks.yml` 中添加自己的演讲配置，根据特定会议或受众定制演示内容。build.py 的配置化组装系统让你只需写几行 YAML，就能从共享素材库自动组装一个完整的演示目录。

## 前置知识

理解三种配置操作（详见 [build.py 与 talks.yml 配置化组装系统](/concepts/03-build-system.md)）：

| 操作 | YAML 键 | 用途 |
|------|---------|------|
| 复制文件 | `files` | 列出要复制的文件路径 |
| 复制文件夹 | `folders` | 映射源文件夹到目标文件夹名 |
| 重命名/复制 | `rename` | 将文件从源路径复制到友好命名 |

## 示例场景：为内部技术分享定制演示

假设你需要在团队内部做一次"JupyterLab 数据科学入门"分享，受众是 Python 初学者。你需要：
- 包含基础数据处理示例（iris.csv + Data.ipynb）
- 包含 pandas 教程（来自 PythonDataScienceHandbook）
- 包含 matplotlib 可视化（Lorenz 吸引子太复杂，用简单散点图）
- 不需要 R、C++、FASTA 等高级内容
- 需要一个友好的入门指引 Markdown 文件

## 步骤一：创建配置

在 `talks.yml` 末尾添加以下配置：

```yaml
internal-datasci-101:
    files:
        - data/iris.csv
        - data/1024px-Hubble_Interacting_Galaxy_AM_0500-620_(2008-04-24).jpg
        - narrative/markdown_python.md
    folders:
        notebooks: notebooks
    rename:
        demofiles/PythonDataScienceHandbook/notebooks/03.08-Aggregation-and-Grouping.ipynb: notebooks/pandas-tutorial.ipynb
        "1024px-Hubble_Interacting_Galaxy_AM_0500-620_(2008-04-24).jpg": galaxy.jpg
        notebooks/Data.ipynb: notebooks/01-getting-started.ipynb
        notebooks/Lorenz.ipynb: notebooks/02-visualization.ipynb
```

### 配置解析

**files 部分**（直接复制的文件）：
- `data/iris.csv` → 经典鸢尾花数据集
- 哈勃星系图片 → 展示图片查看器
- `narrative/markdown_python.md` → Markdown+Python 入门示例

**folders 部分**（复制整个目录）：
- `notebooks` → `notebooks/`：复制所有 Notebook 示例（后续通过 rename 重命名关键文件）

**rename 部分**（友好命名）：
- Pandas 教程 → `notebooks/pandas-tutorial.ipynb`（清晰的名字）
- 星系图片 → `galaxy.jpg`（简短的文件名）
- Data.ipynb → `notebooks/01-getting-started.ipynb`（带编号，引导学习顺序）
- Lorenz.ipynb → `notebooks/02-visualization.ipynb`（编号引导）

## 步骤二：运行构建

```bash
cd external/libs/jupyter/jupyterlab-demo
python build.py
```

build.py 将：
1. 克隆7个外部仓库到 `demofiles/`（如果尚不存在）
2. 创建 `internal-datasci-101/` 目录
3. 复制 files 列表中的文件
4. 复制 notebooks 文件夹
5. 执行 rename 操作重命名文件

## 步骤三：检查输出

构建完成后，检查输出目录：

```bash
ls internal-datasci-101/
```

预期输出结构：

```
internal-datasci-101/
├── iris.csv
├── galaxy.jpg
├── markdown_python.md
└── notebooks/
    ├── 01-getting-started.ipynb    (原 Data.ipynb)
    ├── 02-visualization.ipynb     (原 Lorenz.ipynb)
    ├── pandas-tutorial.ipynb      (来自外部仓库)
    ├── Cpp.ipynb
    ├── Fasta.ipynb
    ├── R.ipynb
    └── ... (其他 notebooks)
```

## 进阶技巧

### 技巧一：不复制整个 notebooks 目录

如果你不想复制所有 Notebook（比如只需要2-3个），不要使用 `folders`，而是通过 `rename` 逐个引入：

```yaml
minimal-demo:
    files:
        - data/iris.csv
        - narrative/markdown_python.md
    rename:
        notebooks/Data.ipynb: data-tutorial.ipynb
        demofiles/PythonDataScienceHandbook/notebooks/03.08-Aggregation-and-Grouping.ipynb: pandas.ipynb
```

### 技巧二：添加自己的 narrative 脚本

在 `narrative/` 目录创建自定义演示脚本 `my-talk.md`：

```markdown
# 我的 JupyterLab 演示脚本

## 1. 欢迎和介绍
- 打开 Binder 链接
- 介绍界面布局

## 2. 数据处理基础
- 打开 iris.csv
- 运行 01-getting-started.ipynb
- 展示 DataFrame 操作

## 3. 可视化
- 打开 02-visualization.ipynb
- 展示 matplotlib 图表
```

然后在 talks.yml 中引用：

```yaml
my-talk:
    files:
        - narrative/my-talk.md
        - data/iris.csv
    folders:
        notebooks: notebooks
```

### 技巧三：条件性包含外部仓库

build.py 会自动克隆7个外部仓库。如果你只需要其中一部分，可以修改 build.py 的 `reponames` 列表来减少构建时间：

```python
reponames = [
    "jakevdp/PythonDataScienceHandbook",  # 只保留需要的
    # "swissnexSF/Urban-Data-Challenge",  # 注释掉不需要的
    # ...
]
```

> ⚠️ 注意：修改 build.py 后确保 talks.yml 中不会引用被移除仓库的文件，否则 rename 操作会失败（源文件不存在）。

### 技巧四：编号文件引导学习顺序

通过 rename 将文件名加上数字前缀，可以在文件浏览器中自然形成学习顺序：

```yaml
rename:
    notebooks/Data.ipynb: notebooks/01-intro.ipynb
    notebooks/Lorenz.ipynb: notebooks/02-visualization.ipynb
    demofiles/.../pandas.ipynb: notebooks/03-pandas.ipynb
    notebooks/bqplot.ipynb: notebooks/04-interactive.ipynb
```

文件浏览器按字母序排列时，会自动按 01→02→03→04 顺序显示。

## 测试和验证

### 本地验证

```bash
# 构建
python build.py

# 启动 JupyterLab 查看效果
jupyter lab --notebook-dir=internal-datasci-101/
```

在浏览器中打开 JupyterLab，验证：
- 所有需要的文件都存在
- 文件名符合预期
- Notebook 可以正常打开和执行
- 数据文件可以在查看器中打开

### CI 验证

如果需要将自定义配置纳入 CI，可以在 `.github/workflows/main.yml` 中添加验证步骤：

```yaml
- run: |
    python build.py
    # 检查输出目录非空
    test -d internal-datasci-101/notebooks
    test -f internal-datasci-101/iris.csv
```

## 常见问题

### Q: files 和 rename 有什么区别？
A: `files` 将文件复制到输出目录时保留原文件名（basename），`rename` 可以指定新文件名。如果需要友好命名就用 rename。

### Q: 为什么 rename 中有些路径来自 demofiles/？
A: 外部仓库克隆到 demofiles/ 目录，所以引用外部文件时路径以 `demofiles/` 开头。

### Q: 可以引用自己仓库以外的文件吗？
A: 不可以。build.py 只能处理本地文件。如果需要外部文件，要么在 setup_demofiles() 中添加 git clone，要么手动下载到 data/ 目录。

### Q: 如何清理构建输出？
A: `.gitignore` 已经配置了忽略演讲目录。手动清理：`rm -rf internal-datasci-101/ demofiles/`

## 相关概念

- [build.py 与 talks.yml 配置化组装系统](/concepts/03-build-system.md)
- [Binder 环境配置三要素](/concepts/02-binder-config.md)
- [本地搭建演示环境](/examples/03-local-setup.md)
