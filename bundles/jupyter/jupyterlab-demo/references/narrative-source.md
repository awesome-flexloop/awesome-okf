---
type: Reference
title: "Narrative 演示脚本文档解析"
description: "narrative/ 目录下四份演示脚本（jupyterlab.md/markdown_python.md/scipy2017.md/QConAI.md）的内容要点与演示流程"
tags: [narrative, demo-script, presentation, jupyterlab-demo, markdown-python]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:20:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: narrative-jupyterlab, resource: "https://github.com/jupyterlab/jupyterlab-demo/blob/master/narrative/jupyterlab.md", title: "jupyterlab.md demo script" }
  - { id: narrative-markdown, resource: "https://github.com/jupyterlab/jupyterlab-demo/blob/master/narrative/markdown_python.md", title: "markdown_python.md example" }
  - { id: narrative-scipy, resource: "https://github.com/jupyterlab/jupyterlab-demo/blob/master/narrative/scipy2017.md", title: "scipy2017.md script" }
  - { id: narrative-qconai, resource: "https://github.com/jupyterlab/jupyterlab-demo/blob/master/narrative/QConAI.md", title: "QConAI.md script" }
---

# Narrative 演示脚本文档信源

## 源码路径

- `external/libs/jupyter/jupyterlab-demo/narrative/jupyterlab.md`
- `external/libs/jupyter/jupyterlab-demo/narrative/markdown_python.md`
- `external/libs/jupyter/jupyterlab-demo/narrative/scipy2017.md`
- `external/libs/jupyter/jupyterlab-demo/narrative/QConAI.md`

## jupyterlab.md — 核心演示脚本

### 项目背景

JupyterLab 由 Project Jupyter、Bloomberg 和 Continuum 合作启动，后发展为多方参与的开源项目。

### 演示流程（9个章节）

1. **Building blocks of interactive computing**（交互式计算构建块）
   - Launcher：打开 Notebook/Console/Editor/Terminal
   - Notebooks：折叠输入输出、拖放单元格
   - 左侧面板：File Browser（文件操作/拖放）、Running Sessions、Command Palette（模糊搜索）
   - Markdown 示例：markdown_python.md 在编辑器中打开，绑定 Kernel/Console 执行代码块
   - Dock Panel：任意布局排列、标签页、单文档模式

2. **File handlers**（文件处理器）
   - CSV：iris.csv（小）、TCGA_Data（中小）、big.csv（大数据）
   - Images：hubble.jpg
   - Vega-Lite：vega.vl.json
   - GeoJSON：Museums_in_DC.geojson
   - bqplot widgets：notebooks/bqplot.ipynb

3. **Find and Replace**（查找替换）：Notebook 和文本文件原生支持

4. **Status Bar**（状态栏）：JupyterLab Status Bar 已集成到核心，扩展可添加自定义状态

5. **Printing**（打印）：扩展可自定义文档和活动的打印方式

6. **JupyterHub**（多用户）：JupyterHub 扩展已作为核心扩展包含，无需单独安装 @jupyterlab/hub-extension

7. **Plugin architecture**（插件架构）
   - JupyterLab 中一切皆扩展
   - 扩展就是带元数据的 npm 包
   - 任何人都可以创建和分发插件
   - 扩展能力：添加命令面板/菜单项、添加文档查看器、暴露其他控件、提供系统能力

## markdown_python.md — Markdown+Python 混编示例

演示 JupyterLab 的 Markdown 编辑器与 Kernel 绑定功能：

- 普通 Markdown 文件，可在编辑器中编辑或在 Markdown 查看器中预览
- 编辑时渲染自动更新
- 包含 Python 代码块：
  - 基础变量赋值：`a = 10`
  - 数据科学示例：matplotlib + numpy + pandas 散点图
    - 使用 `%matplotlib inline` 魔法命令
    - 创建 DataFrame（x/y/color/size列）
    - 使用 seaborn-whitegrid 样式绘制散点图
- 绑定 Python 3 Kernel 和 Console 后，选中代码按 Shift+Enter 执行
- 所有 Python 对象在 Console 中存活，可继续探索

## scipy2017.md — SciPy 2017 会议脚本

面向 SciPy 2017 会议的演示，强调 beta 版本即将发布。

演示亮点：
- Notebook 完全重写，支持可折叠/可拖放单元格、更好的扩展机制
- 多工具共享同一 Kernel：Notebook + Console 并排，执行日志实时显示
- Editor 绑定 Console：Markdown/代码文件中按 Shift+Enter 发送到 Console
- 单文档模式：Shift+Cmd+Enter 切换
- 文件类型：图片、GeoJSON、Vega/VegaLite
- FASTA 查看器：几十个代码行半小时实现
- Data Grid：200MB/1.2百万行CSV流畅滚动（PhosphorJS组件）
- 可扩展性：一切皆插件，扩展与内置功能地位平等

## QConAI.md — QCon AI 会议脚本

面向 QCon AI 大会的演示（更完整版本）。

新增内容（相比 scipy2017.md）：
- 文件多视图：右键标签页创建新视图，支持同时查看不同部分
- Notebook 输出分离：右键创建输出的新视图（dashboard 原型）
- Markdown 实时预览：多视图共享同一内存模型，输入即时反映
- Terminal：完整终端（可运行emacs/vi）
- 自定义设置：主题、编辑器键盘处理、高级设置中的快捷键
- Vega-Lite 多视图同步：JSON编辑器 + Vega查看器共享模型，修改即时更新
- FASTA 扩展同时支持文件查看和Notebook内联渲染
- draw.io 图编辑器插件（Wolf Vollprecht/QuantStack实现）
- GitHub 文件浏览器：浏览GitHub组织，直接运行bqplot示例，一键启动Binder
