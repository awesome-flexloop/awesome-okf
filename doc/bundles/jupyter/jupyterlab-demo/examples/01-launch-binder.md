---
type: Example
title: "在 Binder 启动 JupyterLab 演示环境"
description: "通过 Binder 链接一键启动 jupyterlab-demo 演示环境，体验预设的 JupyterLab 工作区，从打开第一个 Notebook 到探索各种功能的完整上手指南"
tags: [binder, getting-started, quickstart, first-notebook, walkthrough]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:30:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: readme, resource: "/references/repo-readme.md", title: "README信源" }
  - { id: narrative, resource: "/references/narrative-source.md", title: "Narrative演示脚本信源" }
---

# 在 Binder 启动 JupyterLab 演示环境

本示例指导你通过 Binder 一键启动 jupyterlab-demo 的演示环境，并完整体验 JupyterLab 的核心功能。

## 前置条件

- 一个现代浏览器（Chrome/Firefox/Edge/Safari）
- 网络连接（Binder 服务在云端）
- **不需要**安装 Python、Jupyter 或任何软件

## 步骤一：点击 Binder 链接

点击以下链接启动演示环境：

🔗 **https://mybinder.org/v2/gh/jupyterlab/jupyterlab-demo/master?urlpath=lab**

首次加载需要等待几分钟——Binder 需要在云端构建 Conda 环境（安装30+个包）。加载过程中你会看到构建日志。

> 💡 **Binder 是什么？** Binder 是一个免费云服务，可以将 GitHub 仓库转变为可交互的 Jupyter 环境。点击链接后，Binder 在云端服务器上启动一个容器，你通过浏览器访问这个容器中的 JupyterLab。会话结束后环境自动销毁。

## 步骤二：认识预设布局

启动后你会看到预设的工作区布局：

```
┌─────────────────────────────────────────────────┐
│ 左侧(15%)  │         主区域(85%)                 │
│            │ ┌────────────┬───────────────────┐  │
│ 📁 文件     │ │            │                   │  │
│   浏览器    │ │  Lorenz    │  JupyterLab 文档  │  │
│ 🔄 运行     │ │  Notebook  │  （帮助参考）      │  │
│ 📑 目录(TOC)│ │  (代码可    │                   │  │
│ 🧩 扩展     │ │   运行)     │                   │  │
│            │ └────────────┴───────────────────┘  │
└─────────────────────────────────────────────────┘
```

### 你看到的是什么？

1. **Lorenz.ipynb**（左侧面板）：一个3D洛伦兹吸引子可视化Notebook，视觉效果震撼
2. **JupyterLab 文档**（右侧面板）：JupyterLab 官方使用文档，可以随时查阅
3. **文件浏览器**（左侧边栏）：已经定位在 `demo/` 目录
4. **demo/ 目录**：包含所有演示材料

## 步骤三：运行第一个 Notebook

1. 点击左侧的 Lorenz.ipynb 面板，使其成为焦点
2. 点击顶部工具栏的 **Run（▶▶）** 按钮运行所有单元格，或者按 **Shift+Enter** 逐格执行
3. 你会看到洛伦兹微分方程组被求解，最终渲染出一个美丽的3D蝴蝶形状轨迹

> 🎯 **这演示了什么？** Jupyter Notebook 中代码执行、matplotlib 3D 可视化、科学计算（scipy.integrate）的无缝集成。

## 步骤四：探索文件浏览器

在左侧文件浏览器中浏览 `demo/` 目录，尝试双击打开不同类型的文件：

### 体验1：CSV 表格查看器

1. 双击打开 `data/iris.csv`（小数据集）
2. 再双击打开 `smaller.csv`（中等数据）
3. 体验 DataGrid 组件的表格渲染和排序功能

### 体验2：图片查看器

1. 双击打开 `hubble.jpg`
2. 尝试鼠标滚轮缩放图片
3. 将图片面板拖拽到不同位置（和Notebook并排、换到右侧等）

### 体验3：GeoJSON 地图

1. 双击打开 `data/Museums_in_DC.geojson`
2. 你会看到华盛顿 DC 的博物馆分布在交互式地图上
3. 尝试缩放和平移地图

### 体验4：Vega-Lite 可视化

1. 双击打开 `vega.vl.json`
2. 这是一个 Vega-Lite 声明式图表，JupyterLab 直接渲染为可视化图表
3. **进阶**：右键文件 → "Open With" → "Editor"，在 JSON 编辑器中修改 mark 类型（如 `"bar"` 改为 `"line"`），观察图表实时更新

## 步骤五：使用 Markdown+Python 混编

1. 在文件浏览器中双击打开 `markdown_python.md`
2. 注意这是一个 Markdown 文件，不是 Notebook
3. 在编辑器中点击右键 → "Create Console for Editor"
4. 选择 Python 3 内核
5. 将 Console 和编辑器并排排列
6. 在 Markdown 文件中选中 Python 代码块（```python ... ```之间的部分）
7. 按 **Shift+Enter** 将代码发送到 Console 执行
8. 观察 matplotlib 散点图在 Console 中渲染

> 🎯 **这演示了什么？** JupyterLab 不限于 Notebook——你可以将任意文本文件（Markdown/Python脚本/R脚本）连接到一个运行的内核，实现"文档驱动"的交互式编程。

## 步骤六：尝试单文档模式

1. 点击任意面板（如 Lorenz.ipynb）使其活跃
2. 按 **Shift+Cmd+Enter**（Mac）或通过菜单 View → Single-Document Mode
3. 观察界面切换到单文档聚焦模式
4. 再次按快捷键恢复多面板布局

## 步骤七：探索命令面板

1. 按 **Ctrl/Cmd+Shift+C** 打开命令面板
2. 输入 "new" 搜索与新建相关的命令
3. 尝试 "New Notebook"、"New Terminal"、"New Console" 等命令
4. 命令面板是 JupyterLab 的万能入口——所有功能都可以通过搜索找到

## 步骤八：打开更多 Notebook

在 `notebooks/` 目录下尝试：

| Notebook | 内容 |
|----------|------|
| `pandas.ipynb` | Python Data Science Handbook 的 Pandas 教程（外部引入） |
| `bqplot.ipynb` | bqplot 交互式可视化示例 |
| `Data.ipynb` | 基础数据处理示例 |
| `Fasta.ipynb` | FASTA 生物序列查看（如果Fasta扩展可用） |
| `R.ipynb` | R 语言示例（如果R内核可用） |

## 常见问题

### Q: Binder 启动很慢怎么办？
A: 首次启动需要构建环境，通常需要3-7分钟。后续启动（同一版本）会使用缓存镜像，速度快很多。

### Q: 我的修改会保存吗？
A: Binder 是临时环境，关闭浏览器后环境会被回收。如果需要保存工作，请使用 File → Download 下载文件。

### Q: 可以上传自己的文件吗？
A: 可以！拖拽文件到文件浏览器即可上传。但注意环境销毁后文件会丢失。

### Q: 为什么看不到 Julia Notebook？
A: 为避免"找不到内核"错误，postBuild 脚本在构建时删除了 Julia.ipynb。Julia 内核安装会显著增加环境体积和构建时间。

### Q: 终端在哪里？
A: File → New → Terminal，或通过命令面板搜索 "terminal"。

## 下一步

- 阅读 [项目定位与设计理念](/concepts/00-introduction.md) 理解为什么这样设计
- 尝试 [本地搭建演示环境](/examples/03-local-setup.md) 在自己的机器上运行
- 学习 [创建自定义演讲配置](/examples/02-custom-demo-talk.md) 定制自己的演示
