---
type: Concept
title: 内容目录与数据文件组织
description: JupyterLite 站点 content/ 目录的作用、文件布局策略、数据文件共享机制，以及如何组织笔记本和资源
tags: [content-directory, data-files, notebook-organization, file-layout, resources]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T18:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: meta
    resource: /references/repo-readme.md
    title: JupyterLite Demo 仓库元信源
  - id: notebook-catalog
    resource: /references/notebook-catalog.md
    title: 笔记本目录信源
---

## content/ 目录的作用

`content/` 目录是 JupyterLite 站点的「内容源」。构建时，`jupyter lite build --contents content` 命令会将该目录下的所有文件复制到生成的静态站点中，用户打开 JupyterLite 后可以在文件浏览器中看到这些文件。

```bash
jupyter lite build --contents content --output-dir dist
#                        ^^^^^^^
#                        内容源目录
```

这些文件在站点中可通过 JupyterLab 文件浏览器直接访问，也可以在笔记本中通过相对路径读取。

## Demo 的内容布局策略

Demo 的 content/ 目录采用「根级入门 + 子目录分类」的布局：

```
content/
├── data/                           # 共享数据文件
│   ├── Museums_in_DC.geojson
│   ├── bar.vl.json
│   ├── fasta-example.fasta
│   ├── iris.csv
│   └── matplotlib.png
├── pyodide/                        # Pyodide 内核示例（分类存放）
│   ├── pyb2d/                      # 物理引擎子分类
│   │   ├── games/                  # 游戏示例
│   │   └── *.ipynb
│   └── *.ipynb
├── javascript.ipynb                # 根级：JS 内核入门
├── p5.ipynb                        # 根级：p5 内核入门
└── python.ipynb                    # 根级：Python 内核入门
```

### 布局原则

1. **根级放内核入门**：每种内核的入门笔记本放在 content/ 根目录，用户首次打开即可看到
2. **子目录分类组织**：按主题（pyodide/）和子主题（pyb2d/）创建子目录，避免根目录过于拥挤
3. **共享数据集中存放**：data/ 目录集中存放所有笔记本可能用到的数据文件
4. **README 动态注入**：CI 构建时将 README.md 复制到 content/，让用户也能阅读项目说明

## 数据文件类型与使用

Demo 的 data/ 目录包含 5 种格式的数据文件，展示了 JupyterLite 对不同数据类型的支持：

| 文件 | 格式 | 大小 | 典型用途 |
|------|------|------|----------|
| iris.csv | CSV (逗号分隔值) | 小 | pandas 读取、数据分析入门 |
| Museums_in_DC.geojson | GeoJSON | 中 | 地图可视化（ipyleaflet/GeoJSON 渲染） |
| fasta-example.fasta | FASTA | 小 | 生物信息学序列数据、FASTA 渲染器演示 |
| bar.vl.json | Vega-Lite JSON | 小 | Altair/Vega-Lite 声明式可视化规范 |
| matplotlib.png | PNG 图片 | 小 | 图片显示、IPython.display.Image 演示 |

### 在笔记本中读取数据文件

在 Pyodide 内核中，数据文件可以通过相对路径直接读取：

```python
import pandas as pd

# 读取 CSV（假设笔记本在 content/ 根目录）
df = pd.read_csv('data/iris.csv')

# 如果笔记本在 content/pyodide/ 子目录
df = pd.read_csv('../data/iris.csv')
```

对于通过网络获取的数据（演示中常见的模式），可以使用浏览器 Fetch API：

```python
from js import fetch
import pandas as pd
from io import StringIO

URL = "https://example.com/data.csv"
res = await fetch(URL)
text = await res.text()
df = pd.read_csv(StringIO(text))
```

## 支持的文件类型与渲染

JupyterLite 预装了多个文件渲染器，可以在文件浏览器中直接预览特定格式：

| 文件类型 | 渲染器 | 渲染方式 |
|----------|--------|----------|
| .ipynb | JupyterLab Notebook | 笔记本编辑器打开 |
| .csv | JupyterLab CSV Viewer | 表格视图 |
| .json | JupyterLab JSON Viewer | 可折叠树视图 |
| .geojson | jupyterlab-geojson | 地图视图（需安装扩展） |
| .fasta | jupyterlab-fasta | 序列视图（需安装扩展） |
| .png/.jpg/.svg | JupyterLab Image Viewer | 图片预览 |
| .md | JupyterLab Markdown Viewer | Markdown 渲染 |
| .py | JupyterLab Editor | 代码编辑器 |

Demo 预装了 `jupyterlab-fasta` 和 `jupyterlab-geojson` 两个渲染扩展。

## 自定义 MIME 渲染

除了预装的渲染器，用户还可以在笔记本中通过自定义 MIME bundle 渲染任意格式。renderers.ipynb 演示了这一机制：

```python
from IPython.display import display

def Fasta(data=''):
    bundle = {}
    bundle['application/vnd.fasta.fasta'] = data
    bundle['text/plain'] = data
    display(bundle, raw=True)

Fasta(""">SEQUENCE_1
MTEITAAMVKELRESTGAGMMDCKNALSETNGDFDKAVQLLREKGLGKAAKKADRLAAEG""")
```

关键点：
- 构造包含 MIME 类型键（如 `application/vnd.fasta.fasta`）的字典
- 使用 `display(bundle, raw=True)` 输出原始 MIME bundle
- 如果安装了对应 MIME 类型的渲染器，JupyterLab 会自动渲染
- 未安装渲染器时，显示 `text/plain` 降级内容

## 构建时文件处理

构建过程中，content/ 目录的文件被复制到站点的 `files/` 目录。用户创建或修改的文件存储在浏览器 IndexedDB 中，与原始文件分层管理：

```
┌─────────────────────────────────────────────┐
│ 浏览器存储层（IndexedDB）                    │
│ 用户创建/修改的文件（持久化）                 │
├─────────────────────────────────────────────┤
│ 服务器文件层（构建产物 files/）              │
│ 从 content/ 复制的原始文件（只读）           │
└─────────────────────────────────────────────┘
```

用户对服务器文件的修改不会写回服务器，而是保存在浏览器本地存储中。重置浏览器数据会丢失用户修改。

## 相关概念

- [Demo 仓库结构与三件套模式](01-demo-overview.md)
- [三大内核生态对比](03-kernel-ecosystem.md)
- [Pyodide 生态库与 %pip 安装](05-pyodide-libraries.md)
- [从零部署到 GitHub Pages](../examples/01-first-deployment.md)
- [自定义 Demo 站点指南](07-customization-guide.md)
