---
type: Reference
title: JupyterLite Demo 仓库元信源
description: JupyterLite Demo 仓库的版本、许可证、目录结构、核心文件清单等元信息登记
tags: [metasource, jupyterlite-demo, jupyterlite, metadata, repository]
source_type: repository-root
source_path: ./
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T18:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: readme
    resource: https://github.com/jupyterlite/demo/blob/main/README.md
    title: README.md
  - id: license
    resource: https://github.com/jupyterlite/demo/blob/main/LICENSE
    title: LICENSE
---

## 项目基本信息

| 属性 | 值 |
|------|-----|
| 项目名 | JupyterLite Demo |
| GitHub | https://github.com/jupyterlite/demo |
| 在线演示 | https://jupyterlite.github.io/demo |
| 许可证 | BSD 3-Clause (Project Jupyter) |
| 仓库性质 | 部署模板（非代码库），静态站点模板 |
| 核心组件版本 | jupyterlite-core==0.8.0, jupyterlab~=4.6.0, notebook~=7.6.0 |
| Pyodide 内核 | jupyterlite-pyodide-kernel==0.8.0 |
| JS 内核 | jupyterlite-javascript-kernel==0.3.0 |
| p5 内核 | jupyterlite-p5-kernel==0.3.0 |
| CI Python 版本 | 3.11 |
| 支持浏览器 | Firefox 90+, Chromium 89+ |

## 目录结构

```
demo/
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Pages CI/CD 流水线
├── content/                    # 站点内容目录（笔记本+数据）
│   ├── data/                   # 数据文件
│   │   ├── Museums_in_DC.geojson
│   │   ├── bar.vl.json
│   │   ├── fasta-example.fasta
│   │   ├── iris.csv
│   │   └── matplotlib.png
│   ├── pyodide/                # Pyodide 内核示例
│   │   ├── pyb2d/              # Box2D 物理引擎示例
│   │   │   ├── games/          # 游戏示例（angry_shapes/billiard/goo/rocket）
│   │   │   ├── 0_tutorial.ipynb
│   │   │   ├── color_mixing.ipynb
│   │   │   ├── gauss_machine.ipynb
│   │   │   └── newtons_cradle.ipynb
│   │   ├── altair.ipynb
│   │   ├── folium.ipynb
│   │   ├── interactive-widgets.ipynb
│   │   ├── ipycanvas.ipynb
│   │   ├── ipyleaflet.ipynb
│   │   ├── matplotlib.ipynb
│   │   ├── plotly.ipynb
│   │   └── renderers.ipynb
│   ├── javascript.ipynb        # JavaScript 内核示例
│   ├── p5.ipynb                # p5.js 内核示例
│   └── python.ipynb            # Pyodide 内核基础示例
├── repl/
│   └── jupyter-lite.json       # 站点配置文件
├── .gitignore
├── .nojekyll                   # GitHub Pages Jekyll 禁用标记
├── LICENSE                     # BSD 3-Clause
├── README.md
└── requirements.txt            # Python 依赖声明
```

## 核心文件清单与用途

| 文件 | 用途 | 必要性 |
|------|------|--------|
| requirements.txt | 声明 jupyterlite 构建依赖和预装扩展 | 必须 |
| content/ | 随站点分发的笔记本和数据文件 | 必须 |
| repl/jupyter-lite.json | JupyterLite 站点配置（扩展禁用等） | 推荐 |
| .github/workflows/deploy.yml | GitHub Pages 自动构建部署 | 部署到 GH Pages 时需要 |
| .nojekyll | 防止 GitHub Pages 用 Jekyll 处理静态文件 | GH Pages 部署时需要 |
| README.md | 项目说明（构建时复制到 content/ 目录） | 推荐 |
