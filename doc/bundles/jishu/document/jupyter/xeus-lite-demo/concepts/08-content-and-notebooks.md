---
type: Concept
title: 内容目录与 Notebook
description: content/ 目录的作用、Notebook 管理方法、静态资源组织和构建时内容处理
tags: [content, notebooks, ipynb, static-files, jupyter-lite-build]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:05:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: demo-nb
    resource: /references/demo-notebook-source.md
    title: 示例 Notebook 信源
  - id: deploy-wf
    resource: /references/deploy-workflow-source.md
    title: CI/CD 流水线信源
---

## content/ 目录的作用

`content/` 目录是 JupyterLite 站点的"文件系统"。放入此目录的所有文件（Notebook、数据文件、图片等）都会在构建时被打包到静态站点中，用户打开 JupyterLite 后可以在文件浏览器中看到并使用这些文件。

## 目录结构

默认情况下，仓库的 content 目录结构如下：

```
xeus-lite-demo/
├── content/
│   └── demo.ipynb    # 示例 Notebook（笑脸绘制）
├── environment.yml
├── README.md
└── .github/
```

构建时，README.md 也被复制到 content/ 中（由 CI 脚本 `cp README.md content` 完成），所以构建后的 content 包含：

```
content/
├── demo.ipynb
└── README.md
```

## 添加 Notebook

### 方法1：通过 GitHub 网页上传

1. 在仓库页面进入 `content/` 目录
2. 点击 **Add file** → **Upload files**
3. 拖拽或选择你的 `.ipynb` 文件
4. 填写 commit message，点击 **Commit changes**
5. 等待 GitHub Actions 重新部署

### 方法2：通过 Git 命令行

```bash
# 将 Notebook 复制到 content/ 目录
cp /path/to/your/notebook.ipynb content/

# 提交并推送
git add content/notebook.ipynb
git commit -m "add: custom notebook"
git push origin main
```

### 方法3：在 JupyterLite 中创建

用户也可以在部署的 JupyterLite 站点中直接创建新 Notebook，但这些 Notebook 默认保存在浏览器的本地存储（IndexedDB）中，不会同步回 GitHub 仓库。

## 添加数据文件

你可以将数据文件（CSV、JSON、图片等）放入 content/ 目录，在 Notebook 中通过相对路径访问：

```
content/
├── demo.ipynb
├── data/
│   └── dataset.csv
└── images/
    └── logo.png
```

在 Notebook 中引用：

```python
import pandas as pd
df = pd.read_csv('data/dataset.csv')
```

```python
from IPython.display import Image
Image('images/logo.png')
```

### 支持的文件类型

| 类型 | 扩展名 | 说明 |
|------|--------|------|
| Jupyter Notebook | `.ipynb` | Notebook 文件，可直接打开运行 |
| Markdown | `.md` | Markdown 文件，可在 JupyterLab 中预览 |
| 数据文件 | `.csv`, `.json`, `.txt`, `.tsv` | 可通过 pandas 等库读取 |
| 图片 | `.png`, `.jpg`, `.svg`, `.gif` | 可在 Notebook 或 Markdown 中显示 |
| Python 脚本 | `.py` | 可通过 `import` 或 `%run` 使用 |
| 其他 | 任意 | 可下载到浏览器使用 |

## 默认 demo.ipynb 解析

仓库自带的 `content/demo.ipynb` 是一个两格 Notebook，用于验证环境是否正常工作。

### Cell 0：Python 之禅

```python
import this
```

执行后显示 Python 之禅（The Zen of Python），这是一个快速验证 Python 内核正常工作的经典方法。

### Cell 1：ipycanvas 笑脸绘制

使用 `ipycanvas` 库绘制一个笑脸表情，演示：
- 第三方包导入（ipycanvas）
- Canvas 绘图 API 的使用（fill_style, fill_rect, fill_circle, stroke_arc 等）
- Jupyter 中可视化对象的显示

详细代码解析参见 [示例 Notebook 信源](../references/demo-notebook-source.md)。

## 构建时内容处理

理解 `jupyter lite build --contents content` 如何处理内容文件：

1. **复制文件**：content/ 目录中的所有文件被复制到构建输出中
2. **Notebook 处理**：.ipynb 文件保持原样（不执行，不预渲染输出）
3. **索引生成**：生成内容索引，供 JupyterLite 文件浏览器使用
4. **MIME 类型**：根据扩展名设置正确的 MIME 类型

> ⚠️ Notebook 中的代码输出（outputs）不会在构建时执行。用户打开 Notebook 时需要自己运行 cell。这确保了站点的静态特性——构建服务器不需要执行任意代码。

## 文件大小限制

由于是静态站点，所有 content/ 中的文件都会被下载到用户浏览器（或按需加载）。注意：

- 单个大文件（>10MB）会增加站点加载时间
- 大量小文件也会增加请求数
- 数据集建议使用外部 URL 加载（在 Notebook 中通过 pandas 读取 URL）
- GitHub 仓库有文件大小限制（单文件 100MB）

对于大型数据集，建议：
1. 托管在外部服务器（如 GitHub Releases、S3 等）
2. 在 Notebook 中通过 URL 加载：`pd.read_csv('https://example.com/data.csv')`
3. 或使用 JupyterLite 的远程内容提供功能（需额外配置）

## README.md 的特殊处理

在 CI 构建脚本中，README.md 被复制到 content/ 目录：

```bash
cp README.md content
```

这使得用户在 JupyterLite 中可以打开 README.md 查看项目说明。如果你不希望 README 出现在 JupyterLite 文件浏览器中，可以从构建命令中移除这一行。

## 自定义内容结构

你可以自由组织 content/ 目录结构，例如按主题分组：

```
content/
├── README.md
├── 01-getting-started/
│   ├── intro.ipynb
│   └── basics.ipynb
├── 02-data-analysis/
│   ├── pandas-basics.ipynb
│   └── visualization.ipynb
├── data/
│   └── sample-data.csv
└── images/
    └── diagram.png
```

## 相关概念

- [CI/CD 流水线](06-cicd-pipeline.md) — 理解构建命令如何处理 content/
- [运行时环境配置](04-runtime-env-config.md) — 确保需要的库已安装
- [创建第一个部署](../examples/01-first-deployment.md) — 包含上传 Notebook 的步骤
