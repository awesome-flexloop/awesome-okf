---
type: Concept
title: "数据文件与多格式查看器"
description: "深入了解 data/ 目录中每个数据文件的来源、许可证和对应的 JupyterLab 查看器，理解 JupyterLab 如何通过专用查看器支持多种科学数据格式"
tags: [data, csv, geojson, fasta, vega-lite, images, multimedia, file-viewers]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:25:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: narrative, resource: "/references/narrative-source.md", title: "Narrative演示脚本信源" }
  - { id: readme, resource: "/references/repo-readme.md", title: "README信源" }
---

# 数据文件与多格式查看器

JupyterLab 的核心设计理念之一是将各种数据格式作为"一等公民"对待——不是在 Notebook 中写代码加载数据才能查看，而是直接在文件浏览器中双击打开，使用专用查看器交互式浏览。`data/` 目录包含了覆盖多种格式的演示数据文件。

## 数据文件清单

| 文件 | 格式 | 大小 | 许可证 | 来源 | 查看器 |
|------|------|------|--------|------|--------|
| `iris.csv` | CSV | ~4KB | CC0 1.0 | UCI ML Repository (R.A. Fisher) | DataGrid 表格 |
| `Museums_in_DC.geojson` | GeoJSON | 小 | CC-BY 4.0 | OpenData DC | GeoJSON 地图 |
| `bar.vl.json` | Vega-Lite | 小 | BSD-3 | Altair 示例 | Vega-Lite 图表 |
| `zika_assembled_genomes.fasta` | FASTA | 中 | 公开数据 | Nature 2017论文 | FASTA 序列查看器 |
| `1024px-Hubble_*.jpg` | JPEG | ~1MB | NASA/ESA公共领域 | 哈勃太空望远镜 | 图片查看器 |
| `japan_meteorological_*.json` | JSON | - | CC-BY 4.0 | 日本气象厅 | JSON 编辑器 |
| `jupiter.mp4` | MP4 | - | CC0 1.0 | Public Domain Archive | HTML5 视频 |
| `rocket.wav` | WAV | - | CC0 1.0 | Public Domain Archive | HTML5 音频 |
| `Dockerfile` | Dockerfile | 小 | - | 仓库自带 | 代码编辑器 |

## CSV 文件与 DataGrid

### iris.csv — 经典数据集

Fisher 的鸢尾花数据集是机器学习和统计教学的"Hello World"：
- 150条记录，3类鸢尾花（setosa/versicolor/virginica）
- 4个特征：花萼长度/宽度、花瓣长度/宽度
- 用途：分类算法入门、数据表格基础操作

DataGrid（数据网格）查看器特性：
- 列排序（点击列头）
- 平滑滚动（即使大数据也流畅）
- 基于 Canvas 渲染（非 DOM 表格，高性能）

### big.csv vs smaller.csv — 大数据对比演示

通过 rename 映射从外部仓库引入：
- `big.csv`：来自 Urban-Data-Challenge 的日内瓦公共交通实时数据（200MB，约120万行）
- `smaller.csv`：来自 TCGA 数据集的基因符号数据（较小）

演示脚本中的对比叙事：
1. 先打开 `smaller.csv`——"这是一个普通大小的CSV，Excel也能打开"
2. 再打开 `big.csv`——"这是一个200MB、120万行的CSV，Excel和LibreOffice打不开或极其卡顿"
3. 展示 DataGrid 流畅滚动——"JupyterLab 的 DataGrid 基于 Lumino 的 Canvas 组件，秒开且滚动如丝般顺滑"
4. 提万亿行/列示例——"Chris Colbert 甚至做过一万亿行一万亿列的演示，依然流畅"

这种"对比震撼"是 demo 的经典手法：用 Excel 做不到的事情展示 JupyterLab 的能力。

### vega.vl.json — Vega-Lite 声明式可视化

源文件为 Altair 示例中的 `bar.vl.json`，重命名为 `vega.vl.json`。

Vega-Lite 是一种声明式可视化语法：
- 用 JSON 描述"数据是什么、怎么映射到视觉通道"
- 不需要写命令式绘图代码
- JupyterLab 直接渲染为交互式图表

**多视图同步演示**（QConAI.md）：
1. 右键 .vl.json 文件 → 同时打开 JSON 编辑器和 Vega-Lite 查看器
2. 并排布局，左侧修改 JSON（如将 mark 类型从 `bar` 改为 `line`）
3. 右侧图表实时更新——两边共享同一内存模型

这展示了 JupyterLab 的**模型-视图分离架构**：同一底层文件模型，可以同时用多个查看器打开，修改即时同步。

## GeoJSON 与地理数据

### Museums_in_DC.geojson

- 来源：华盛顿特区政府开放数据门户（OpenData DC）
- 内容：华盛顿 DC 博物馆的地理位置和属性
- 许可证：CC-BY 4.0
- 查看器：jupyterlab-geojson 扩展

jupyterlab-geojson 扩展提供：
- GeoJSON 数据在 Leaflet 地图上的交互式渲染
- 点/线/多边形等几何类型的支持
- 属性表的弹出查看
- 地图缩放、平移等基础交互

这展示了 JupyterLab 如何为特定领域（地理空间分析）提供专用的文件查看体验。

## FASTA 与生物信息学

### zika_assembled_genomes.fasta

- 内容：110条寨卡病毒全基因组序列
- 来源：2017年 Nature 论文 "Zika virus evolution and spread in the Americas"
- 数据来源：10个国家/地区的临床样本和蚊子样本
- 用途：系统发育分析推断病毒在美洲的传播进化

FASTA 格式是生物信息学的标准序列格式，jupyterlab-fasta 扩展提供：
- 序列的彩色可视化（不同碱基/氨基酸不同颜色）
- 多序列比对视图
- 序列搜索和高亮

FASTA 扩展的故事在演示中被反复引用（见 [演示能力维度](/concepts/04-demo-capabilities.md)）——"有人在 SciPy 上说需要FASTA支持，我们几十行代码几小时就做了一个扩展"。这是 JupyterLab 扩展性的活广告。

## 图片与多媒体

### Hubble 星系图片

- 文件：`1024px-Hubble_Interacting_Galaxy_AM_0500-620_(2008-04-24).jpg` → 重命名为 `hubble.jpg`
- 来源：NASA/ESA 哈勃太空望远镜
- 内容：交互星系 AM 0500-620
- 用途：演示图片查看器（缩放、全屏）
- 版权：哈勃遗产计划（STScI/AURA）-ESA/Hubble Collaboration

图片查看器支持：
- 缩放（鼠标滚轮/快捷键）
- 全屏模式
- 与其他面板并排布局

### 音视频文件

- `jupiter.mp4`：木星视频（Public Domain Archive，CC0）
- `rocket.wav`：火箭发射音频（Public Domain Archive，CC0）

HTML5 原生播放器：
- 播放/暂停/进度条
- 音量控制
- 无需额外插件

这些公共领域媒体文件展示了 JupyterLab 作为多媒体科学计算环境的能力——不仅能处理代码和数据，也能处理图像、音频、视频内容。

## 结构化数据格式

### 日本气象厅 JSON 数据

- 文件：`japan_meterological_agency_201707211555.json`
- 来源：日本气象厅（JMA）高分辨率降水临近预报
- 许可证：CC-BY 4.0
- 查看器：内置 JSON 编辑器（语法高亮、格式化）

JSON 编辑器支持：
- 语法高亮
- 折叠/展开节点
- 格式化（pretty-print）
- 与 Vega-Lite 查看器等配合实现实时预览

### Dockerfile

`data/Dockerfile` 是一个简单的 Dockerfile 示例，用于演示：
- 代码编辑器的语法高亮
- 多种编程语言/配置文件格式支持
- 文件编辑器的通用能力（查找替换、多光标等）

## 文件关联与查看器架构

JupyterLab 的文件处理遵循**模型-视图-注册**架构：

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ 文件模型      │────→│ 文档注册器    │────→│ 查看器/工厂   │
│ (FileModel)  │     │ (DocRegistry) │     │ (WidgetFactory)│
│ - 路径        │     │ - MIME类型映射│     │ - 渲染Widget  │
│ - 内容        │     │ - 文件扩展名  │     │ - 工具栏      │
│ - 脏状态      │     │ - 默认查看器  │     │ - 上下文菜单  │
└──────────────┘     └──────────────┘     └──────────────┘
```

每种文件格式的查看器通过 JupyterLab 扩展注册：
- jupyterlab-geojson 注册 `.geojson` 扩展名
- jupyterlab-fasta 注册 `.fasta` 扩展名
- 内置查看器注册 CSV/图片/PDF/Markdown 等

扩展开发者只需实现一个 WidgetFactory 并注册到 DocRegistry，就能让新格式在文件浏览器中"开箱即用"。

## 文件浏览器的隐藏文件配置

`jupyter_notebook_config.py` 中的配置：

```python
c.ContentsManager.allow_hidden = True
```

这允许文件浏览器显示和访问以 `.` 开头的隐藏文件（如 `.binder/`、`.gitignore`）。在演示中这很重要——否则观众无法看到 Binder 配置目录。

## 许可证合规

data/ 目录中的文件来自多个来源，各自遵循不同的许可证。LICENSE 文件中详细列出了每个数据文件的版权信息：

| 许可证 | 文件 | 使用要求 |
|--------|------|---------|
| CC0 1.0（公共领域） | iris.csv, jupiter.mp4, rocket.wav | 无限制使用 |
| CC-BY 4.0 | Museums_in_DC.geojson, JMA JSON | 署名即可 |
| NASA 公共领域 | Hubble 图片 | 无限制（NASA素材不版权保护） |
| BSD-3 | bar.vl.json | 保留版权声明 |
| Nature论文数据 | zika FASTA | 学术引用 |

这提醒我们：在创建自己的 demo 仓库时，注意数据文件的许可证合规性，避免将不允许再分发的数据包含在内。

## 相关概念

- [演示能力维度与多内核支持](/concepts/04-demo-capabilities.md)
- [Notebook 示例解析](/concepts/05-notebook-examples.md)
- [插件架构与扩展生态](/concepts/08-extension-demo.md)
