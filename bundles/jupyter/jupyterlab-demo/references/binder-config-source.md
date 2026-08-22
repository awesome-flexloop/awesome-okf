---
type: Reference
title: "Binder 配置文件源码解析"
description: ".binder/ 目录下三个核心配置文件（environment.yml、postBuild、workspace.json）的源码级信源"
tags: [binder, environment, conda, postbuild, workspace, jupyterlab-config]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:20:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: binder-env, resource: "https://github.com/jupyterlab/jupyterlab-demo/blob/master/.binder/environment.yml", title: "environment.yml" }
  - { id: binder-postbuild, resource: "https://github.com/jupyterlab/jupyterlab-demo/blob/master/.binder/postBuild", title: "postBuild script" }
  - { id: binder-workspace, resource: "https://github.com/jupyterlab/jupyterlab-demo/blob/master/.binder/workspace.json", title: "workspace.json" }
---

# Binder 配置文件源码信源

## 源码路径

- `external/libs/jupyter/jupyterlab-demo/.binder/environment.yml`
- `external/libs/jupyter/jupyterlab-demo/.binder/postBuild`
- `external/libs/jupyter/jupyterlab-demo/.binder/workspace.json`

## environment.yml

### 频道配置

```yaml
channels:
- conda-forge
- nodefaults
```

### 依赖分组

| 分组 | 包名 | 用途 |
|------|------|------|
| 构建工具 | ruamel.yaml | Python YAML 解析（build.py使用） |
| 核心应用 | jupyterlab | JupyterLab 主程序 |
| 核心应用 | jupyter-collaboration | 实时协作扩展 |
| 核心应用 | nbconvert | Notebook 格式转换 |
| 核心应用 | notebook | Jupyter Notebook v7 |
| JupyterLab扩展 | jupyter-offlinenotebook | 离线Notebook支持 |
| JupyterLab扩展 | jupyterlab-fasta | FASTA序列查看器 |
| JupyterLab扩展 | jupyterlab-geojson | GeoJSON地图查看器 |
| R内核 | r-irkernel | R语言内核 |
| R内核 | r-ggplot2 | R绘图库 |
| Python内核 | ipykernel | IPython Python内核 |
| Python内核 | xeus-python | 替代Python内核（C++实现） |
| Python数据科学 | ipywidgets, ipyleaflet, altair, bqplot, dask, matplotlib-base, pandas, scikit-image, scikit-learn, seaborn-base, tensorflow, sympy, traittypes | 数据科学生态包 |
| Python版本 | python=3.12 | 锁定Python 3.12 |
| C++内核 | xeus-cling, xtensor, xtensor-blas, xwidgets, xleaflet | 已注释掉（不稳定） |
| CLI工具 | pip, vim | 命令行工具 |

## postBuild（Bash脚本）

```bash
#!/bin/bash
set -ex
python build.py              # 运行构建脚本
rm -rf demofiles             # 清理构建中间目录
rm -rf notebooks             # 清理原始notebooks目录
rm -rf narrative             # 清理narrative源文件
rm -rf slides                # 清理slides源文件
rm demo/notebooks/Julia.ipynb  # 删除Julia内核notebook（避免环境中无Julia报错）
conda run -n notebook jupyter lab workspaces import .binder/workspace.json  # 导入工作区布局
```

关键细节：
- `set -ex`：遇到错误退出（e）并打印执行的命令（x）
- 构建后清理源代码目录，只保留组装好的 `demo/` 目录
- 使用 `conda run -n notebook` 导入工作区（Binder默认环境名为 `notebook`）
- 需要激活环境后导入，否则工作区会导入到用户home而非prefix路径

## workspace.json（工作区布局）

布局结构：
- **主区域**：水平分屏（左右各50%），左侧打开 Lorenz.ipynb，右侧打开 JupyterLab 文档（help-doc）
- **左侧面板**：展开状态，当前活动为文件浏览器（filebrowser），包含 widgets：filebrowser、running-sessions、toc（目录）、extensionmanager
- **右侧面板**：折叠状态，包含 property-inspector 和 debugger-sidebar
- **文件浏览器**：初始路径为 `demo/`
- **Notebook**：以 Notebook factory 打开 `demo/Lorenz.ipynb`
- **帮助文档**：URL 指向 `https://jupyterlab.readthedocs.io/en/stable/`
- 元数据：id 为 "default"
