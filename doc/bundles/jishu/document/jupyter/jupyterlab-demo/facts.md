---
okf_version: '0.2'
generated: '2026-08-22'
source_root: d:\spaces\SpecWeave\external\libs\jupyter\jupyterlab-demo
tags:
- jupyterlab
- demo
- tutorial
- binder
- showcase
sources:
- ../../../../../external/libs/jupyter/jupyterlab-demo/README.md
- ../../../../../external/libs/jupyter/jupyterlab-demo/build.py
- ../../../../../external/libs/jupyter/jupyterlab-demo/talks.yml
- ../../../../../external/libs/jupyter/jupyterlab-demo/jupyter_notebook_config.py
- ../../../../../external/libs/jupyter/jupyterlab-demo/narrative/jupyterlab.md
- ../../../../../external/libs/jupyter/jupyterlab-demo/data/README.md
- ../../../../../external/libs/jupyter/jupyterlab-demo/notebooks/lorenz.py
- ../../../../../external/libs/jupyter/jupyterlab-demo/.binder/environment.yml
- ../../../../../external/libs/jupyter/jupyterlab-demo/.binder/workspace.json
- ../../../../../external/libs/jupyter/jupyterlab-demo/.github/workflows/main.yml
- ../../../../../external/libs/jupyter/jupyterlab-demo/data/bar.vl.json
type: Facts
title: jupyterlab-demo 源码事实清单
---

# jupyterlab-demo 事实清单

## 项目概况

- F-001: README.md:1-9 — 本仓库是 JupyterLab 下一代用户界面的演示仓库，由 Project Jupyter、Bloomberg、Continuum 合作发起
- F-002: README.md:5 — 提供 Binder 在线演示入口：https://mybinder.org/v2/gh/jupyterlab/jupyterlab-demo/master?urlpath=lab
- F-003: README.md:13-14 — 演示环境要求 mamba（Mambaforge 提供），依赖在 environment.yml 中声明
- F-004: README.md:20 — 演示指南位于 narrative/jupyterlab.md 文件中
- F-005: README.md:24-35 — build.py 会克隆 7 个外部仓库：PythonDataScienceHandbook、Urban-Data-Challenge、altair、QuantEcon.notebooks、TCGA、TensorFlow-Examples、bqplot

## 目录结构

- F-006: 目录结构 — 根目录包含 data/、narrative/、notebooks/、slides/、.binder/、.github/ 等子目录
- F-007: data/ 目录 — 存放演示数据文件，包含图片（Hubble星系图）、GeoJSON、CSV、Vega-Lite JSON、视频(jupiter.mp4)、音频(rocket.wav)、FASTA序列(zika_assembled_genomes.fasta)
- F-008: notebooks/ 目录 — 包含多语言演示 Notebook：Cpp.ipynb、Data.ipynb、Fasta.ipynb、Julia.ipynb、Lorenz.ipynb、R.ipynb，以及 lorenz.py 辅助脚本
- F-009: narrative/ 目录 — 包含演示讲解文档：QConAI.md、jupyterlab.md、markdown_python.md、scipy2017.md
- F-010: slides/ 目录 — 包含演讲幻灯片（Keynote 和 PDF 格式）：jupyterlab-slides.key、jupyterlab-slides.pdf、jupyterlab-slides_scipy19.pdf

## 构建脚本 build.py

- F-011: build.py:1-6 — 使用 Python 3，依赖 pathlib、subprocess、ruamel.yaml、shutil、os 模块
- F-012: build.py:10 — 定义 DEMO_FOLDER 常量为 "demofiles"
- F-013: build.py:12-61 — setup_talks() 函数读取 talks.yml，为每个演讲创建文件夹并复制/重命名文件
- F-014: build.py:38-39 — setup_talks() 使用 ruamel.yaml 加载 talks.yml 配置
- F-015: build.py:41 — 使用 Path(talk_name).mkdir(parents=True, exist_ok=True) 创建演讲目录
- F-016: build.py:43-47 — 处理 files 配置项：复制文件到目标目录，并断言文件复制成功
- F-017: build.py:49-53 — 处理 folders 配置项：使用 shutil.copytree 复制目录
- F-018: build.py:55-61 — 处理 rename 配置项：重命名已复制的文件，或从源路径直接复制并重命名
- F-019: build.py:63-88 — setup_demofiles() 函数创建 demofiles 目录并克隆外部仓库
- F-020: build.py:70-78 — 定义 7 个待克隆仓库列表：jakevdp/PythonDataScienceHandbook、swissnexSF/Urban-Data-Challenge、altair-viz/altair、QuantEcon/QuantEcon.notebooks、theandygross/TCGA、aymericdamien/TensorFlow-Examples、bloomberg/bqplot
- F-021: build.py:82-85 — 使用 git clone --depth 1 浅克隆仓库，仅当目标目录不存在时执行
- F-022: build.py:87-88 — 创建 move_this_file.txt 空文件和 move_it_here 目录，用于演示 JupyterLab 的拖拽功能
- F-023: build.py:90-96 — main() 函数依次调用 setup_demofiles() 和 setup_talks()

## 演示配置

- F-024: talks.yml:1-7 — test_talk 配置：复制 demofiles/TCGA 目录和 data/iris.csv 文件，并将 iris.csv 重命名为 iris_renamed.csv
- F-025: talks.yml:9-19 — scipy2017 配置：包含 iris.csv、Hubble图片、Museums GeoJSON、scipy2017.md 文档，以及多个文件重命名规则
- F-026: talks.yml:21-31 — jupytercon2017 配置：与 scipy2017 类似，使用 markdown_python.md 讲解文档
- F-027: talks.yml:33-50 — demo 配置：最完整配置，包含幻灯片、讲解文档、TCGA_Data 目录、notebooks 目录、data 目录，以及多个重命名规则（包括bqplot示例、Hubble图片重命名为hubble.jpg）
- F-028: jupyter_notebook_config.py:1 — 启用协作模式：c.LabApp.collaborative = True
- F-029: jupyter_notebook_config.py:2 — 允许访问隐藏文件：c.ContentsManager.allow_hidden = True

## Binder 环境配置

- F-030: .binder/environment.yml:1-3 — 使用 conda-forge 和 nodefaults 频道
- F-031: .binder/environment.yml:5 — 安装 ruamel.yaml 依赖（用于 build.py 解析 YAML）
- F-032: .binder/environment.yml:7-10 — 安装核心应用：jupyterlab、jupyter-collaboration、nbconvert、notebook
- F-033: .binder/environment.yml:12-14 — 安装扩展：jupyter-offlinenotebook、jupyterlab-fasta、jupyterlab-geojson
- F-034: .binder/environment.yml:16-17 — R 内核支持：r-irkernel、r-ggplot2
- F-035: .binder/environment.yml:19-34 — Python 生态：ipykernel、xeus-python、ipywidgets、ipyleaflet、altair、bqplot、dask、matplotlib-base、pandas、python=3.12、scikit-image、scikit-learn、seaborn-base、tensorflow、sympy、traittypes
- F-036: .binder/environment.yml:36-40 — C++ 内核相关包（xeus-cling、xtensor、xtensor-blas、xwidgets、xleaflet）被注释掉
- F-037: .binder/environment.yml:42-43 — CLI 工具：pip、vim
- F-038: .binder/postBuild:1-3 — postBuild 脚本使用 bash，启用 set -ex 严格模式
- F-039: .binder/postBuild:5 — 执行 python build.py 构建演示文件
- F-040: .binder/postBuild:7-11 — 清理 demofiles、notebooks、narrative、slides 目录，并删除 demo/notebooks/Julia.ipynb
- F-041: .binder/postBuild:13-16 — 使用 conda run -n notebook 导入 workspace.json 工作区配置

## 工作区配置

- F-042: .binder/workspace.json — 工作区布局为左右分屏（50:50），左侧打开 Lorenz.ipynb，右侧打开 JupyterLab 文档
- F-043: .binder/workspace.json — 左侧边栏展开文件浏览器，右侧边栏折叠
- F-044: .binder/workspace.json — 文件浏览器初始路径为 demo/ 目录
- F-045: .binder/workspace.json — 元数据中 id 为 "default"

## 演示讲解文档

- F-046: narrative/jupyterlab.md:1-5 — 演示文档标题为 "JupyterLab Demo"，注明由 Project Jupyter、Bloomberg、Continuum 合作发起
- F-047: narrative/jupyterlab.md:17-26 — 演示从 Launcher 开始，可打开 Notebook、Console、Editor、Terminal 四种活动
- F-048: narrative/jupyterlab.md:29-31 — Notebook 演示包含：打开示例Notebook、折叠输入/输出、拖拽单元格
- F-049: narrative/jupyterlab.md:33-37 — 左侧面板插件演示：文件浏览器（含拖拽）、运行中面板、命令面板（模糊搜索）
- F-050: narrative/jupyterlab.md:41-44 — Markdown 示例：打开 markdown_python.md，并排查看渲染效果，附加Kernel/Console按Shift+Enter运行代码
- F-051: narrative/jupyterlab.md:46-51 — Dock panel 支持任意布局排列，Tabs和单文档模式可聚焦
- F-052: narrative/jupyterlab.md:53-66 — 文件处理器支持多种格式：CSV（iris.csv、TCGA_Data、big.csv）、Images（hubble.png）、Vega-Lite（vega.vl.json）、GeoJSON（Museums_in_DC.geojson）、bqplot widgets
- F-053: narrative/jupyterlab.md:69-70 — Find and Replace 功能在 Notebook 和文本文件中一等支持
- F-054: narrative/jupyterlab.md:72-73 — Status Bar 已集成到核心发行版，扩展可添加自己的状态
- F-055: narrative/jupyterlab.md:76-77 — 打印系统允许扩展自定义文档和活动的打印方式
- F-056: narrative/jupyterlab.md:80-81 — JupyterHub 扩展已作为核心扩展包含，无需单独安装 @jupyterlab/hub-extension
- F-057: narrative/jupyterlab.md:83-97 — 插件架构说明：JupyterLab中一切皆扩展，扩展是带元数据的npm包，任何人可创建发布，可添加命令面板/菜单/文档查看器/其他控件

## CI/CD 配置

- F-058: .github/workflows/main.yml:1 — CI 工作流名称为 "CI"
- F-059: .github/workflows/main.yml:3-7 — 触发条件：push 到 master 分支，以及所有分支的 pull_request
- F-060: .github/workflows/main.yml:9-11 — 默认 shell 为 bash -el {0}（登录shell）
- F-061: .github/workflows/main.yml:14-15 — build 任务运行在 ubuntu-latest
- F-062: .github/workflows/main.yml:17-24 — 使用 mamba-org/setup-micromamba@v1 安装 mamba，micromamba 版本 1.5.1-0，环境文件 .binder/environment.yml，环境名 jupyterlab-demo，启用缓存
- F-063: .github/workflows/main.yml:25-30 — 输出 micromamba 诊断信息：info、list、config sources、config list、环境变量
- F-064: .github/workflows/main.yml:31-35 — 测试步骤：执行 nbconvert 运行 Data.ipynb、Fasta.ipynb、R.ipynb（60秒超时），然后执行 python build.py

## 演示数据

- F-065: data/README.md:4-26 — zika_assembled_genomes.fasta 包含 110 个寨卡病毒基因组，来自 10 个国家和地区的临床和蚊子样本，用于系统发育分析
- F-066: data/Museums_in_DC.geojson — 华盛顿特区博物馆位置数据，来自 OpenData DC
- F-067: data/iris.csv — 经典鸢尾花数据集，用于 CSV 查看器演示
- F-068: data/bar.vl.json — Vega-Lite 柱状图示例
- F-069: data/jupiter.mp4、rocket.wav — 来自 Public Domain Archive（CC0 1.0 许可）的音视频文件
- F-070: notebooks/lorenz.py:1-46 — Lorenz 吸引子可视化脚本，使用 matplotlib 3D绘图、numpy、scipy.integrate.odeint，默认参数 sigma=10.0、beta=8/3、rho=28.0，生成30条轨迹

## 许可证与媒体

- F-071: README.md:28-34 — 外部仓库许可证：PythonDataScienceHandbook 代码 MIT/文本 CC-BY-NC-ND-3.0、altair BSD-3、Urban-Data-Challenge CC-BY-NC-3.0、QuantEcon.notebooks BSD-3、TensorFlow-Examples MIT
- F-072: README.md:36-37 — jupiter.mp4 和 rocket.wav 来自 Public Domain Archive，采用 CC0 1.0 Universal 许可
