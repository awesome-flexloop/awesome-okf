# sphinx-demo 架构洞察与知识地图

> I阶段产出：核心洞察四元组 + 知识地图 + 文档清单

## 核心架构洞察

### 洞察 I-01：双内核平行示范——Pyodide 与 Xeus 的配置差异点仅在5处

- **陈述**：sphinx-demo 通过两个几乎完全相同的目录结构并行展示 Pyodide 和 Xeus 两种内核的集成方式，两者的 conf.py 差异仅为 version_match、doc_path 和 requirements.txt 中的内核包名，Xeus 额外需要 environment.yml 和 micromamba。
- **证据**：F-003（两个并行示例目录），F-016（requirements.txt 差异：jupyterlite-pyodide-kernel vs jupyterlite-xeus），F-017（switcher.version_match 差异），F-018（doc_path 差异），F-036/F-037（jupyter-lite.json 中 defaultKernelName 差异："python" vs "XPython"），F-041/F-042（Xeus 独有的 environment.yml），F-070（CI 中 Xeus 需要 micromamba）。
- **反常识**：初学者可能认为 Pyodide 和 Xeus 的配置差异很大，实际上95%以上的配置完全相同——关键差异在于包管理方式（Pyodide 运行时 piplite 安装 vs Xeus 构建时 environment.yml 预安装）和内核名称（python vs XPython），而不是 Sphinx 配置层面。
- **行动**：文档中采用"公共配置+内核差异"的组织方式，先讲通用 conf.py 配置，再单独对比两种内核的差异点。

### 洞察 I-02：四层配置文件体系——构建时/运行时/插件/交互行为分层管理

- **陈述**：JupyterLite Sphinx 集成涉及四层 JSON 配置文件，每层管控不同阶段的行为：jupyter_lite_config.json（构建时）、jupyter-lite.json（运行时）、overrides.json（JupyterLab 插件设置）、try_examples.json（TryExamples 交互行为），加上 conf.py 中的 Sphinx 扩展配置形成完整配置体系。
- **证据**：F-036/F-037（jupyter-lite.json 运行时配置：appName、defaultKernelName、faviconUrl），F-038（jupyter_lite_config.json 构建配置：no_sourcemaps），F-039（overrides.json 插件配置：Download 按钮），F-040（try_examples.json 交互配置：min_height、ignore_patterns），F-022~F-027（conf.py 中 jupyterlite_sphinx 扩展配置项）。
- **反常识**：try_examples.json 是运行时热加载配置——Sphinx 构建后修改此文件不需要重新构建文档，JS 端 ConfigLoader 每次页面加载时 fetch 最新配置（参见 jupyterlite-sphinx 扩展的 F-094）。其他三个 JSON 文件则在构建时被复制到输出目录，修改后需要重新构建。
- **行动**：配置文档按四层体系分节讲解，重点标注 try_examples.json 的热加载特性。

### 洞察 I-03：TryExamples 三级控制粒度——全局/页面/函数级禁用

- **陈述**：TryExamples 按钮的启用/禁用提供三级控制粒度：全局通过 `global_enable_try_examples=True` 开启，页面级通过 `try_examples.json` 的 `ignore_patterns` 正则排除，函数级通过 docstring 中的 `.. disable_try_examples` 注释禁用。
- **证据**：F-025（global_enable_try_examples=True 全局开启），F-040（ignore_patterns 排除 disabled_examples/demo.html 页面），F-051（image_processing 函数 docstring 中的 `.. disable_try_examples` 注释），F-058/F-059（disabled_examples 页面被 ignore_patterns 排除的示例）。
- **反常识**：`.. disable_try_examples` 不是 RST 指令，而是一个特殊注释标记——它不出现在渲染后的文档中，仅被 `insert_try_examples_directive()` 函数在处理 docstring 时检测到后跳过插入按钮。初学者容易将其误认为需要 `::` 的正式指令。
- **行动**：TryExamples 文档中明确展示三级控制的代码示例，特别说明 `.. disable_try_examples` 是注释而非指令。

### 洞察 I-04：strip_tagged_cells 实现文档页与Notebook内容的条件分离

- **陈述**：`strip_tagged_cells=True` 配合 MyST notebook 单元格的 `jupyterlite_sphinx_strip` 标签，实现同一文件中"Sphinx 文档页可见内容"与"JupyterLite Notebook 内容"的条件分离——被标记的单元格在 Sphinx HTML 输出中保留（用于展示 directive 代码），但在 JupyterLite Notebook 中被剥离。
- **证据**：F-024（strip_tagged_cells=True 启用剥离），F-053（matplotlib_demo.md 第一个单元格使用 `+++ {"tags": ["jupyterlite_sphinx_strip"]}` 标签），F-054（该单元格包含 notebooklite directive 的说明和按钮代码）。
- **反常识**：被 strip 的单元格在 Sphinx 渲染的文档页面上是可见的（用户能看到解释文字和按钮），但在点击按钮打开的 JupyterLite Notebook 中这些单元格被移除了——这意味着文档作者可以在 notebook 开头放"说明性单元格"而不会干扰用户的实际代码执行。初学者可能以为 strip 是从文档页面中移除内容。
- **行动**：在 NotebookLite 概念文档中用图示说明 strip 机制的方向（文档中保留→Notebook 中移除）。

### 洞察 I-05：CI/CD 采用"双站点并行构建+根页面聚合"的部署模式

- **陈述**：GitHub Actions 通过矩阵策略并行构建 Pyodide 和 Xeus 两个 Sphinx 站点，各自上传为独立 artifact，部署阶段下载所有 artifact 后添加根 index.html 和 switcher.json 聚合为统一站点，实现 `/pyodide/` 和 `/xeus/` 双路径访问。
- **证据**：F-067~F-075（CI 工作流完整定义），F-069（matrix 策略并行构建），F-073（artifact 命名为 pyodide/xeus），F-075（部署时 mv index.html 和 switcher.json 到 dist/），F-006/F-008（根 index.html 为内核选择页，switcher.json 为版本切换器配置）。
- **反常识**：两个站点的构建是完全独立的（各自的 requirements.txt、conf.py、make html），部署时只是将两个构建产物目录和根页面放在一起。版本切换不是通过 JavaScript 动态切换内容实现的，而是通过 PyData 主题的 version-switcher 组件跳转到不同的 URL 路径（/pyodide/ vs /xeus/）——本质上是两个独立的静态站点共享同一个域名。
- **行动**：部署文档中画清楚 CI 流程的并行构建→聚合部署模型，说明版本切换器的工作原理是 URL 跳转而非单页应用切换。

## 知识地图

### 文档分组与学习路径

```
入门篇（快速上手）
├── 00-introduction.md      → F-001~F-005（项目是什么、能做什么）
├── 01-project-structure.md → F-009~F-018（目录结构与文件组织）
└── 02-quick-start.md       → F-064~F-065, F-022~F-030（从零搭建最小站点）

核心篇（配置与使用）
├── 03-sphinx-conf.md       → F-019~F-035（conf.py 完整配置解析）
├── 04-kernel-comparison.md → F-036~F-037, F-041~F-042, F-055~F-056（Pyodide vs Xeus 内核对比）
├── 05-config-files.md      → F-036~F-040（四层JSON配置文件详解）
├── 06-try-examples.md      → F-025~F-027, F-040, F-047~F-051, F-058~F-059（TryExamples 交互按钮）
└── 07-notebook-embedding.md → F-052~F-057（NotebookLite 嵌入与 strip 机制）

高级篇（定制与部署）
├── 08-customization.md     → F-060~F-063（CSS样式定制与自定义图标）
├── 09-ci-deployment.md     → F-067~F-075（GitHub Actions 自动构建与 Pages 部署）
└── 10-disabling-examples.md → F-040, F-051, F-058~F-059（三级禁用机制详解）
```

### 文档依赖关系

```
00-introduction → 01-structure → 02-quick-start
                                     ↓
                              03-sphinx-conf
                             ↙    ↓    ↘
                     04-kernel  05-config  06-try-examples
                        ↓         ↓          ↓
                   07-notebook-embedding   10-disabling
                             ↓
                        08-customization
                             ↓
                        09-ci-deployment
```

## 文档清单

### concepts/ （10个概念文档）

| 文件 | type | title | 覆盖事实 |
|------|------|-------|---------|
| 00-introduction.md | Concept | sphinx-demo 与 jupyterlite-sphinx 简介 | F-001~F-005 |
| 01-project-structure.md | Concept | 项目目录结构解析 | F-006~F-018 |
| 02-quick-start.md | Concept | 快速开始：搭建你的第一个交互文档站点 | F-022~F-030, F-064~F-065 |
| 03-sphinx-conf.md | Concept | Sphinx conf.py 配置详解 | F-019~F-035 |
| 04-kernel-comparison.md | Concept | Pyodide 与 Xeus 内核对比选型 | F-016~F-018, F-036~F-037, F-041~F-042, F-055~F-056, F-066, F-070 |
| 05-config-files.md | Concept | JupyterLite 四层配置文件体系 | F-036~F-040 |
| 06-try-examples.md | Concept | TryExamples 交互示例系统 | F-025~F-027, F-040, F-047~F-051 |
| 07-notebook-embedding.md | Concept | NotebookLite 嵌入与单元格剥离 | F-052~F-057 |
| 08-customization.md | Concept | 样式定制与主题扩展 | F-060~F-063 |
| 09-ci-deployment.md | Concept | CI/CD 与 GitHub Pages 部署 | F-067~F-075 |
| 10-disabling-examples.md | Concept | 禁用交互示例的三级控制 | F-040, F-051, F-058~F-059 |

### examples/ （4个示例文档）

| 文件 | type | title | 覆盖事实 |
|------|------|-------|---------|
| 01-minimal-site.md | Example | 最小可运行站点：从安装到构建 | F-064~F-065, F-019~F-030 |
| 02-pyodide-setup.md | Example | Pyodide 内核完整配置示例 | F-022~F-030, F-036, F-064 |
| 03-xeus-setup.md | Example | Xeus 内核完整配置示例 | F-041~F-042, F-037, F-066, F-070 |
| 04-matplotlib-notebook.md | Example | 嵌入可交互 Matplotlib 笔记本 | F-052~F-057 |

### references/ （3个信源文档）

| 文件 | type | title | 覆盖事实 |
|------|------|-------|---------|
| conf-py-source.md | Reference | conf.py 配置项完整速查 | F-019~F-035 |
| json-config-source.md | Reference | JSON 配置文件字段速查 | F-036~F-040 |
| ci-workflow-source.md | Reference | GitHub Actions 工作流解析 | F-067~F-075 |
