---
type: Facts
title: jupyterlite-demo 源码事实清单
description: 基于 jupyterlite/demo 仓库源码采集的零推测事实清单，共90条事实，覆盖项目元信息、依赖配置、笔记本内容、数据文件、构建部署
generated:
  by: agent:source-code-to-okf-wiki
  at: '2026-08-22T18:00:00+08:00'
status: stable
sources:
- ../../../../../external/libs/jupyter/demo/requirements.txt
okf_version: '0.2'
tags:
- facts
---

# R 阶段：事实采集清单

> 基于 jupyterlite/demo 仓库源码采集，所有事实可通过源码路径验证。零推测。

## F-001 ~ F-010：项目元信息

| 编号 | 事实 | 信源 |
|------|------|------|
| F-001 | 仓库名称为 JupyterLite Demo，是部署到 GitHub Pages 的 JupyterLite 静态站点模板 | README.md:1-5 |
| F-002 | 在线演示地址为 https://jupyterlite.github.io/demo | README.md:9 |
| F-003 | 许可证为 BSD 3-Clause License，版权归 Project Jupyter 所有 | LICENSE:1-3 |
| F-004 | 支持浏览器：Firefox 90+、Chromium 89+ | README.md:15-18 |
| F-005 | 默认分支为 main，CI 在 push 到 main 和所有 PR 时触发 | .github/workflows/deploy.yml:3-9 |
| F-006 | 包含 .nojekyll 空文件，用于告诉 GitHub Pages 不要用 Jekyll 处理 | .nojekyll |
| F-007 | 仓库包含 repl/jupyter-lite.json 配置文件 | repl/jupyter-lite.json |
| F-008 | 仓库根目录有 content/ 目录存放笔记本和数据文件 | 目录结构 |
| F-009 | 核心构建命令为 `jupyter lite build --contents content --output-dir dist` | .github/workflows/deploy.yml:27 |
| F-010 | 部署流程：构建后通过 actions/upload-pages-artifact@v3 上传 dist/，再用 actions/deploy-pages@v4 部署到 GitHub Pages | .github/workflows/deploy.yml:28-47 |

## F-011 ~ F-020：依赖配置（requirements.txt）

| 编号 | 事实 | 信源 |
|------|------|------|
| F-011 | 核心模块：jupyterlite-core==0.8.0 | requirements.txt:2 |
| F-012 | JupyterLab 版本约束：jupyterlab~=4.6.0 | requirements.txt:3 |
| F-013 | Notebook 版本约束：notebook~=7.6.0 | requirements.txt:4 |
| F-014 | Python 内核：jupyterlite-pyodide-kernel==0.8.0 | requirements.txt:7 |
| F-015 | JavaScript 内核：jupyterlite-javascript-kernel==0.3.0 | requirements.txt:10 |
| F-016 | p5 内核：jupyterlite-p5-kernel==0.3.0 | requirements.txt:17 |
| F-017 | 语言包：jupyterlab-language-pack-fr-FR、jupyterlab-language-pack-zh-CN | requirements.txt:13-14 |
| F-018 | 文件渲染扩展：jupyterlab-fasta>=3.3.0,<4、jupyterlab-geojson>=3.4.0,<4 | requirements.txt:20-22 |
| F-019 | 主题扩展：jupyterlab-night、jupyterlab_miami_nights | requirements.txt:27-29 |
| F-020 | ipywidgets 相关：ipywidgets>=8.1.3,<9、ipyevents>=2.0.1、ipympl>=0.8.2、ipycanvas>=0.9.1、ipyleaflet（无版本约束） | requirements.txt:32-40 |

## F-021 ~ F-030：更多依赖

| 编号 | 事实 | 信源 |
|------|------|------|
| F-021 | 绘图库：plotly>=6,<7、bqplot（无版本约束） | requirements.txt:43-44 |
| F-022 | CI 使用 Python 3.11：actions/setup-python@v5 with python-version: '3.11' | .github/workflows/deploy.yml:18-20 |
| F-023 | 构建前执行 `cp README.md content` 将 README 复制到内容目录 | .github/workflows/deploy.yml:26 |
| F-024 | jupyter-lite.json 中 disabledExtensions 禁用了三个扩展：@jupyterlab/drawio-extension、jupyterlab-kernel-spy、jupyterlab-tour | repl/jupyter-lite.json:4-8 |
| F-025 | jupyter-lite.json 使用 schema version 0 | repl/jupyter-lite.json:2 |
| F-026 | 禁用 jupyterlab-tour 有 TODO 注释引用了 GitHub issue #82 | requirements.txt:25（注释） |
| F-027 | .gitignore 忽略 jupyterlite 构建产物：*.doit.db、_output | .gitignore:115-116 |
| F-028 | content/ 目录下有三个根级笔记本：python.ipynb、javascript.ipynb、p5.ipynb | 目录结构 |
| F-029 | content/ 目录下有 data/ 子目录存放数据文件 | 目录结构 |
| F-030 | content/ 目录下有 pyodide/ 子目录存放 Pyodide 内核示例笔记本 | 目录结构 |

## F-031 ~ F-045：根级笔记本内容

| 编号 | 事实 | 信源 |
|------|------|------|
| F-031 | python.ipynb 标题为 "A Python kernel backed by Pyodide"，演示 Pyodide 内核基础功能 | content/python.ipynb:cell-0 |
| F-032 | python.ipynb 演示了：简单代码执行、变量赋值与函数定义、stderr 重定向、错误处理（import missing_module） | content/python.ipynb:cells |
| F-033 | python.ipynb 演示了：代码补全（tab 键）、代码内省（?print、shift+tab） | content/python.ipynb:cells |
| F-034 | python.ipynb 演示了 input() 函数的 await 用法：`name = await input('Enter your name: ')` | content/python.ipynb:cell-21 |
| F-035 | python.ipynb 演示了 IPython.display 丰富输出：HTML、Markdown、Pandas DataFrame、update_display、clear_output | content/python.ipynb:cells |
| F-036 | python.ipynb 演示了 Math/Latex 公式渲染、ProgressBar、JSON、GeoJSON MIME 类型 | content/python.ipynb:cells |
| F-037 | python.ipynb 演示了通过 `from js import fetch` 使用浏览器 Fetch API 进行网络请求 | content/python.ipynb:cell-49 |
| F-038 | python.ipynb 演示了 SymPy 符号计算与 LaTeX 渲染 | content/python.ipynb:cells |
| F-039 | python.ipynb 演示了 IPython magics：%cd、%pwd、%writefile、%history、%%timeit | content/python.ipynb:cells |
| F-040 | python.ipynb 第一个代码单元为 `import pyodide_kernel; pyodide_kernel.__version__` | content/python.ipynb:cell-1 |
| F-041 | javascript.ipynb 标题为 "JavaScript in JupyterLite"，使用 javascript kernel | content/javascript.ipynb:cell-0 |
| F-042 | javascript.ipynb 演示了 console.log/console.error 标准流输出、setTimeout 异步操作、字符串 forEach | content/javascript.ipynb:cells |
| F-043 | javascript.ipynb 包含 Markdown 数学公式（Lorenz 微分方程组） | content/javascript.ipynb:cell-8 |
| F-044 | p5.ipynb 标题为 "p5 notebook"，语言为 p5js，是最小化的 p5.js 笔记本 UI | content/p5.ipynb:cell-0 |
| F-045 | p5.ipynb 演示了 setup() 函数（createCanvas、rectMode）、draw() 函数（background、translate、rotate、fill、rect） | content/p5.ipynb:cells |

## F-046 ~ F-055：p5 笔记本与数据文件

| 编号 | 事实 | 信源 |
|------|------|------|
| F-046 | p5.ipynb 使用 `%show` magic 命令渲染 p5 sketch | content/p5.ipynb:cell-8 |
| F-047 | p5.ipynb 支持在后续 cell 中修改变量值（speed=3, n=20）后重新 `%show` 更新渲染 | content/p5.ipynb:cells |
| F-048 | data/ 目录包含 Museums_in_DC.geojson（GeoJSON 数据文件） | content/data/ |
| F-049 | data/ 目录包含 bar.vl.json（Vega-Lite 条形图规范） | content/data/ |
| F-050 | data/ 目录包含 fasta-example.fasta（FASTA 序列文件） | content/data/ |
| F-051 | data/ 目录包含 iris.csv（鸢尾花数据集） | content/data/ |
| F-052 | data/ 目录包含 matplotlib.png（Matplotlib 示例图片） | content/data/ |
| F-053 | pyodide/ 子目录包含：altair.ipynb、folium.ipynb、interactive-widgets.ipynb、ipycanvas.ipynb、ipyleaflet.ipynb、matplotlib.ipynb、plotly.ipynb、renderers.ipynb | content/pyodide/ |
| F-054 | pyodide/pyb2d/ 子目录包含物理引擎示例：0_tutorial.ipynb、color_mixing.ipynb、gauss_machine.ipynb、newtons_cradle.ipynb | content/pyodide/pyb2d/ |
| F-055 | pyodide/pyb2d/games/ 子目录包含游戏示例：angry_shapes.ipynb、billiard.ipynb、goo.ipynb、rocket.ipynb | content/pyodide/pyb2d/games/ |

## F-056 ~ F-070：Pyodide 示例笔记本

| 编号 | 事实 | 信源 |
|------|------|------|
| F-056 | altair.ipynb 标题为 "Altair in JupyterLite"，使用 `%pip install -q altair` 安装 Altair | content/pyodide/altair.ipynb |
| F-057 | altair.ipynb 演示了：Simple Bar Chart、Simple Heatmap、Interactive Average（brush selection）、US Airports 地理可视化（topo_feature） | content/pyodide/altair.ipynb |
| F-058 | altair.ipynb 使用 `%pip install -q vega_datasets` 安装 Vega 数据集 | content/pyodide/altair.ipynb |
| F-059 | matplotlib.ipynb 演示了 numpy + matplotlib 基础绘图（plt.plot、plt.show）和 `%matplotlib widget` 交互式后端 | content/pyodide/matplotlib.ipynb |
| F-060 | matplotlib.ipynb 使用 `%pip install -q ipympl` 安装交互式 matplotlib 后端 | content/pyodide/matplotlib.ipynb |
| F-061 | plotly.ipynb 标题为 "Plotly in JupyterLite"，使用 `%pip install -q nbformat plotly` 安装 | content/pyodide/plotly.ipynb |
| F-062 | plotly.ipynb 演示了：go.Figure 基础图形（Scatter+Bar）、Pandas DataFrame 表格、Quiver Plot（矢量场+散点） | content/pyodide/plotly.ipynb |
| F-063 | plotly.ipynb 使用 `from js import fetch` 下载 CSV 数据，然后用 open() 写入文件，再用 pd.read_csv 读取 | content/pyodide/plotly.ipynb |
| F-064 | folium.ipynb 标题为 "folium Interactive Map Demo"，使用 `%pip install -q folium` 安装 | content/pyodide/folium.ipynb |
| F-065 | folium.ipynb 说明了 folium 的传递依赖：branca、certifi、chardet、idna、jinja2、markupsafe、numpy、pandas、requests、urllib3 等 | content/pyodide/folium.ipynb |
| F-066 | folium.ipynb 演示了 `folium.Map(location=[lat, lon], zoom_start=11)` 创建交互式地图 | content/pyodide/folium.ipynb |
| F-067 | ipycanvas.ipynb 标题为 "ipycanvas: John Conway's Game Of Life"，实现了康威生命游戏 | content/pyodide/ipycanvas.ipynb |
| F-068 | ipycanvas.ipynb 使用 RoughCanvas、hold_canvas 绘制生命游戏动画，通过 asyncio.sleep 控制帧率 | content/pyodide/ipycanvas.ipynb |
| F-069 | ipyleaflet.ipynb 结合 bqplot 和 ipyleaflet 实现了交互式地图+图表联动（hover 国家更新图表） | content/pyodide/ipyleaflet.ipynb |
| F-070 | ipyleaflet.ipynb 使用 WidgetControl 将 bqplot Figure 和 ipywidgets Dropdown 嵌入地图控件 | content/pyodide/ipyleaflet.ipynb |

## F-071 ~ F-082：Widgets 与渲染器

| 编号 | 事实 | 信源 |
|------|------|------|
| F-071 | interactive-widgets.ipynb 标题为 "ipywidgets Interactive Demo"，使用 `%pip install -q ipywidgets` 安装 | content/pyodide/interactive-widgets.ipynb |
| F-072 | interactive-widgets.ipynb 演示了 IntSlider 滑块控件的创建、显示、值读写 | content/pyodide/interactive-widgets.ipynb |
| F-073 | interactive-widgets.ipynb 演示了 IntText + link() 实现两个控件双向绑定 | content/pyodide/interactive-widgets.ipynb |
| F-074 | interactive-widgets.ipynb 还包含 bqplot 交互式图表演示（Lines、Bars、动画更新） | content/pyodide/interactive-widgets.ipynb |
| F-075 | bqplot 部分演示了：线性图（Lines）、条形图（Bars）、动态更新 y 数据、颜色/填充/标记属性修改 | content/pyodide/interactive-widgets.ipynb |
| F-076 | renderers.ipynb 标题为 "JupyterLab Renderers"，演示了自定义 MIME 渲染器 | content/pyodide/renderers.ipynb |
| F-077 | renderers.ipynb 演示 FASTA 渲染：构造 `application/vnd.fasta.fasta` MIME bundle，通过 `display(bundle, raw=True)` 输出 | content/pyodide/renderers.ipynb |
| F-078 | renderers.ipynb 演示 GeoJSON 渲染：构造 `application/geo+json` MIME bundle 输出 | content/pyodide/renderers.ipynb |
| F-079 | pyb2d/0_tutorial.ipynb 是 b2d（Box2D）物理引擎入门教程 | 文件名+目录位置 |
| F-080 | pyb2d/ 子目录包含 color_mixing、gauss_machine、newtons_cradle（牛顿摆）物理模拟示例 | 文件名 |
| F-081 | pyb2d/games/ 包含 angry_shapes（愤怒的小鸟类）、billiard（台球）、goo（粘粘世界类）、rocket（火箭）游戏示例 | 文件名 |
| F-082 | 所有 Pyodide 示例笔记本均使用 `%pip install -q <package>` 魔术命令在浏览器端安装 Python 包 | 所有 pyodide/*.ipynb |

## F-083 ~ F-090：构建与部署配置

| 编号 | 事实 | 信源 |
|------|------|------|
| F-083 | CI build job 在 ubuntu-latest 上运行 | .github/workflows/deploy.yml:13 |
| F-084 | deploy job 需要 build job 完成（needs: build），仅在 main 分支执行 | .github/workflows/deploy.yml:34-35 |
| F-085 | deploy job 设置 permissions: pages: write, id-token: write | .github/workflows/deploy.yml:37-38 |
| F-086 | deploy job 使用 github-pages environment，URL 从 deployment steps 输出 | .github/workflows/deploy.yml:40-42 |
| F-087 | requirements.txt 中提到 Xeus 内核模板在 jupyterlite/xeus-python-demo 仓库 | requirements.txt:35（注释） |
| F-088 | README.md 部署指南指向 jupyterlite.readthedocs.io/en/latest/quickstart/deploy.html | README.md:22 |
| F-089 | README.md 列出 How-to Guides 和 Reference 两个文档入口 | README.md:28-29 |
| F-090 | content/python.ipynb 中自定义类实现 `_repr_html_` 方法，通过 display(display_id=...) 和 update_display() 实现动态更新显示 | content/python.ipynb:cells |
