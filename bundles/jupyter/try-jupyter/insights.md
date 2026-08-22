---
type: Insights
okf_version: "0.2"
title: "try-jupyter 架构洞察"
generated: "2026-08-22"
tags: [jupyter, try-jupyter, jupyterlite, demo, deployment]
sources:
  - facts.md
  - ../../../../../external/libs/jupyter/try-jupyter/jupyter_lite_config.json
  - ../../../../../external/libs/jupyter/try-jupyter/pyproject.toml
  - ../../../../../external/libs/jupyter/try-jupyter/scripts/filter_xeus_kernels.py
  - ../../../../../external/libs/jupyter/try-jupyter/.readthedocs.yml
---
# try-jupyter 架构洞察

## I-001：多内核 WASM 环境的声明式构建矩阵

**类型**：架构模式

**关联事实**：F-009, F-010, F-011, F-016, F-017, F-018, F-019, F-020, F-021, F-022, F-023, F-024

**洞察**：try-jupyter 用单个 `jupyter_lite_config.json` 文件声明了整个多内核演示站的构建矩阵，而非为每种语言维护独立构建流程。

配置文件将构建分成两个正交维度（F-009/F-010 与 F-011）：
- **内容维度**：`LiteBuildConfig.contents = ["content"]` 声明站点内容来源（F-010）；
- **内核维度**：`XeusAddon.environment_file` 声明 4 个 WASM 内核环境（F-011），每个 `environment-*.yml` 是一个独立的 xeus kernel 描述（F-016~F-024），分别覆盖 C++（xeus-cpp + symengine/xtensor-blas/xsimd，F-018）、Python（xeus-python + numpy/matplotlib/ipywidgets/ipyleaflet/scipy，F-020）、R（xeus-r + r-ggplot2，F-022）、SQLite（xeus-sqlite，F-024）。

值得注意的是 Python 语言出现了双内核：Pyodide kernel 由 `jupyterlite-pyodide-kernel` 依赖提供（对应 Intro.ipynb 的 "Python (Pyodide)"，F-025），而 xeus-python 通过 environment-python.yml 提供（对应 Lorenz.ipynb 的 "Python (XPython)"，F-026）。这使同一语言在不同 notebook 中可选用不同运行时，是演示站展示"内核对比"的手段。

```
┌───────────────────────────────────────────────────────────┐
│              jupyter_lite_config.json（构建声明）           │
│  LiteBuildConfig: contents=["content"]        (F-009/010) │
│  XeusAddon: environment_file = [4 × *.yml]      (F-011)  │
└──────────────┬────────────────────────────────────────────┘
               │ 注入
   ┌───────────▼────────────┐      ┌──────────────────────────┐
   │ environment-cpp.yml    │      │ environment-python.yml   │
   │  xeus-cpp / symengine  │      │  xeus-python / numpy ... │
   └────────────────────────┘      └──────────────────────────┘
   ┌────────────────────────┐      ┌──────────────────────────┐
   │ environment-r.yml      │      │ environment-sqlite.yml   │
   │  xeus-r / r-ggplot2    │      │  xeus-sqlite             │
   └────────────────────────┘      └──────────────────────────┘
```

**复用价值**：多语言演示站（或产品文档）可将"每个语言内核"收敛为单个 environment 文件，再用一个 XeusAddon 配置聚合，实现内核矩阵的声明式扩展——新增语言只需新增一个 yml 文件并追加到列表，无需改动构建逻辑。

## I-002：pixi 任务驱动的构建后处理流水线

**类型**：设计决策

**关联事实**：F-004, F-005, F-006, F-007, F-008, F-032, F-033, F-034, F-035, F-036, F-037, F-038, F-039, F-040

**洞察**：try-jupyter 将"构建 → 内核裁剪 → 分析注入 → 部署归档"整条流水线统一封装为 pixi tasks（F-004~F-008），成为本地、GitHub Actions、ReadTheDocs 三条路径共用的唯一入口。

流水线的两次后处理各司其职：
- **filter-kernels**（F-006, F-032, F-033）：`jupyter lite build` 产出的 `dist/xeus/kernels.json` 会包含比演示站所需更多的 xeus kernels，脚本以白名单 `KERNELS_TO_KEEP = {xcpp23, xc23, xr, xpython, xsqlite}` 就地过滤该 JSON（F-032），缩小产物规模；
- **add-plausible**（F-007, F-034, F-035）：用 BeautifulSoup 遍历 `dist` 下所有 HTML（F-035），在 `<head>` 注入 Plausible 分析脚本（F-034），实现静态站点的无后端访问统计。

三个消费方复用同一组任务：`.readthedocs.yml` 的 commands 依次调用 `pixi install / pixi run build / pixi run filter-kernels / pixi run readthedocs`（F-037），与 deploy.yml 的 `pixi run build / filter-kernels / add-plausible`（F-038/F-039）形成镜像，保证 RTD 预览与 GitHub Pages 正式站行为一致。

```
 pyproject.toml [tool.pixi.tasks]  ── 唯一构建入口
   │  clean / build / filter-kernels / add-plausible / readthedocs
   │        (F-004 ~ F-008)
   ▼
 jupyter lite build ──► dist/  ──► filter_xeus_kernels.py（白名单裁剪 kernels.json）
                                      │                     (F-032/033)
                                      ▼
                              add_plausible.py（BeautifulSoup 注入 analytics）
                                      │                     (F-034/035)
                ┌─────────────────────┼──────────────────────┐
                ▼                     ▼                      ▼
       deploy.yml（GitHub Pages）   .readthedocs.yml（RTD 预览）
       F-038/F-039/F-040            F-036/F-037
```

**复用价值**：把"构建产物后处理"做成命名任务并让 CI 与文档平台共享，可保证多部署通道产物一致；静态站点的轻量分析（无 cookie/无服务端）可参考 add-plausible 的 HTML 注入模式。

## I-003：content/ 与 kernelspec 驱动的演示内容组织

**类型**：架构约束

**关联事实**：F-010, F-025, F-026, F-027, F-028, F-029, F-030, F-031

**洞察**：演示内容与构建配置严格分离——`LiteBuildConfig.contents = ["content"]`（F-010）把 `content/` 目录整体挂载为 JupyterLite 文件浏览器内容，notebook 与数据文件无需任何注册即可进入站点。

内容组织遵循一条隐式契约：**每个 notebook 通过自身 kernelspec 元数据声明运行时**，从而与 F-011 的 xeus 内核矩阵及 Pyodide kernel 自动关联。7 个 notebook 覆盖 4 类内核：Pyodide Python（Intro.ipynb，F-025）、XPython Python（Lorenz.ipynb，F-026）、R（r.ipynb "R 4.4.3 (xr)"，F-027）、SQLite（sqlite.ipynb "xsqlite"，F-028）、C++23（cpp.ipynb 等，F-029）。`content/data/` 存放演示素材（如 bar.vl.json 的 Vega-Lite 图表，F-030），被 notebook 引用；ui-tests 通过 glob 自动发现 notebook 逐一执行（F-031），同样依赖目录约定的稳定性。

```
                    content/  （唯一内容来源，F-010）
   ┌────────────────────┼─────────────────────┐
 notebooks/                                   data/
  Intro.ipynb  → Pyodide        bar.vl.json / iris.csv /
  Lorenz.ipynb → XPython        Museums_in_DC.geojson /
  r.ipynb      → R (xr)         audio.wav / fasta-example.fasta ...
  sqlite.ipynb → xsqlite                     (F-030)
  cpp.ipynb    → C++23
   │ (kernelspec 声明运行时, F-025~F-029)
   ▼
 JupyterLite 文件浏览器（kernels 由 F-011 矩阵提供）
```

**复用价值**：演示类 JupyterLite 站点应保持"内容目录 + kernelspec 元数据"的自组织方式，避免为每个 notebook 编写注册表；新增演示只需在 `content/notebooks/` 落一个 notebook 并在 kernelspec 中声明内核，新增数据则直接放入 `content/data/`。
