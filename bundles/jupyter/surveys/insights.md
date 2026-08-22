---
type: Insights
okf_version: "0.2"
title: "surveys 架构洞察"
generated: "2026-08-22"
tags: [jupyter, surveys, community, documentation]
sources:
  - facts.md
  - ../../../../../external/libs/jupyter/surveys/README.md
  - ../../../../../external/libs/jupyter/surveys/docs/myst.yml
  - ../../../../../external/libs/jupyter/surveys/noxfile.py
  - ../../../../../external/libs/jupyter/surveys/.github/workflows/deploy.yml
---
# surveys 架构洞察

> I 阶段产出：基于 facts.md 事实推导的架构洞察，每个洞察引用真实 F 编号。

## I-001：数据目录即文档——"内容即数据 + 元数据驱动索引"的文档化数据集仓库

**类型**：架构模式（Content-as-Data / Metadata-driven Indexing）

**关联事实**：F-001, F-004, F-005, F-012, F-014, F-015

**洞察**：surveys 仓库把"数据目录"同时当作"文档内容源"——每个调查是一个 `YYYY-MM-short-description` 子目录，其 `README.md` 既是人类可读的数据说明，也是 MyST 文档站自动索引进来的页面（F-004/F-005）。文档站不维护任何手工索引，全部由 glob 模式在构建期发现。

源码逐层拆解：

1. **统一目录约定**：所有数据集按 `YYYY-MM-short-description` 命名（F-004），README 强制包含日期/收集者/population 等元数据（F-005）——目录名提供时间序，README frontmatter 的 `date` 字段提供排序键（如 F-022/F-030）。
2. **MyST 自动索引**：`docs/myst.yml` 的 TOC 用 `pattern: surveys/**/README.md` 递归纳入所有调查（F-012）；`docs/index.md` 用 `:::{listing}` directive（`:columns: title,date`）自动生成调查列表（F-014）——新增一个调查目录即自动出现在站点中，无需改任何文档。
3. **符号链接打通目录**：`docs/surveys` 是 git symlink（mode 120000）指向顶层 `surveys/`（F-015），使 docs 构建能越过目录边界解析 `surveys/**/README.md` 模式——这是"把数据目录映射进文档空间"的关键技巧。

```
  仓库根                                        MyST 构建 → jupyter.github.io/surveys
  ┌────────────────────────────────────┐        ┌────────────────────────────────┐
  │ surveys/                           │        │ index.md  :::{listing}         │
  │  ├─ 2015-12-notebook-ux/README.md  │──┐     │   (surveys/*/README.md 列表)    │
  │  ├─ 2016-05-education-survey/…     │  │     │ TOC pattern: surveys/**/README │
  │  ├─ 2018-09-jupytercon-2018/…      │  │     │   ├─ 2015-12-notebook-ux       │
  │  └─ 2020-12-jupyter-survey/…       │  │     │   ├─ 2016-05-education-survey  │
  │                                    │  │     │   └─ … (自动发现)               │
  │ docs/surveys ──symlink(120000)──▶ ../surveys │                              │
  └────────────────────────────────────┘  │     └────────────────────────────────┘
                                          └────▶ myst build --html 扫描 README
```

**复用价值**：面向"数据集/资源集合"类仓库，用"README 即页面 + glob 模式发现 + listing 指令"可以零维护地构建浏览站点。核心前提是强制统一元数据格式（frontmatter `date` 字段），这样自动索引才能正确排序。git 符号链接（docs/surveys）解决了"数据目录与文档目录物理分离但逻辑合一"的经典问题，在 Windows 检出时它会退化为含目标路径的普通文件（core.symlinks=false），跨平台团队需知晓此行为。

---

## I-002：双环境构建链——本地与 CI 各自安装 MyST，却在同一个命令上汇合

**类型**：设计决策（Single Command, Dual Provisioning）

**关联事实**：F-006, F-007, F-008, F-018, F-019, F-020

**洞察**：仓库为同一份文档提供了两条互不相同的构建路径：本地开发者用 nox + `uv|virtualenv` 后端创建 session 虚拟环境并安装 `mystmd`（F-006/F-007/F-008）；CI 则用 setup-node 装 Node 20.x 后 `npm install -g mystmd` 全局安装（F-018/F-019）。两条路径安装方式完全不同，但最终都在 `myst build --html` 这个命令上汇合，保证本地与线上产物一致。

源码逐层拆解：

1. **本地路径（nox）**：`default_venv_backend = "uv|virtualenv"`（F-006）声明环境创建偏好；`docs` session 在 session 虚拟环境内 `install("mystmd")` 后运行 `myst build --html`（F-007），`docs-live` 运行 `myst start` 提供 live-reload（F-008）。
2. **CI 路径（GitHub Actions）**：触发为 push master + 手动（F-016），权限含 pages/id-token（F-017），steps 用 checkout@v4 + configure-pages@v3 + setup-node@v4（20.x）（F-018）。
3. **汇合点与部署参数**：CI 同样执行 `cd docs && myst build --html`，但额外设置 `BASE_URL: /surveys` 环境变量（F-019），使站点部署在 GitHub Pages 的 `/surveys` 子路径下；产物 `./docs/_build/html` 经 upload-pages-artifact 交给 deploy-pages（F-020）。

```
   本地开发                              持续集成（GitHub Actions）
   ┌──────────────────────┐              ┌──────────────────────────────┐
   │ nox -s docs          │              │ push master / manual        │
   │  └ uv/virtualenv venv │              │  └ setup-node 20.x          │
   │     └ install mystmd │              │     └ npm install -g mystmd │
   └──────────┬───────────┘              └──────────────┬───────────────┘
              │                                        │
              └──────────►  myst build --html ◄────────┘
                           （CI 额外 BASE_URL=/surveys）
                                    │
                                    ▼
                          GitHub Pages（/surveys 子路径）
```

**复用价值**：这是"工具链双轨、命令单点"的通用文档站模式——开发者本地体验由轻量 session 工具（nox/uv）保证，CI 的产物一致性由"同样的最终命令"保证。若工具本身跨语言生态（mystmd 是 npm 包，被 Python 侧 nox 调用），需明确记录两条安装路径的等价命令，避免开发者与 CI 因安装方式差异产生行为漂移。`BASE_URL` 环境变量是 MyST 针对子路径部署的官方约定，任何部署到 Pages 子目录的站点都应设置。

---

## I-003：纵向切片式数据集治理——每个调查自包含"元数据 + 原始数据 + 分析代码"

**类型**：架构模式（Vertical Slice Data Governance）

**关联事实**：F-023~F-029, F-033~F-038, F-040~F-042

**洞察**：仓库按"一次调查 = 一个纵向切片"组织数据：每个子目录内同时承载元数据（README）、原始数据（CSV）、分析代码（notebook/脚本），必要时还有交互组件。纵向切片使不同调查的分析深度可以独立演进——2015 调查展示了完整的主题分析管线，2020 调查则直接携带可视化 notebook，2018 调查的 JupyterCon 测试数据配套 Python 解析脚本。

源码逐层拆解：

1. **2015 全管线示例（最完整切片）**：原始导出 `20160115235816-SurveyExport.csv`（1706×37，无预处理，F-024）→ 会话统计（partial/complete 比例，F-025/F-026）→ `analysis/prep/` 中 1_ux_survey_review、2_clean_survey、3a~3h 八个主题抽取、4_primary_roles、5_utils 共 12 个 notebook（F-029）→ `report_dashboard.ipynb` 汇总报告与 `survey-explorer.html` 交互组件（F-029）。
2. **2018 脚本化数据清洗**：`analysis_utils.py` 提供时间解析（`convert_time_to_int`/`diff_times`）与 `load_data()` 预处理（F-037）；`user_testing_data.py` 的 `cleaner()` 用 `target_encoding` 字典把 "Init" 移动文本解析为 source/target/position 结构化字段，甚至能从 Google Sheets 在线重载数据（F-038）——把"调查工具导出格式"清洗成"可分析结构"。
3. **2020 可视化切片**：`all_responses.ipynb`（350 cells，plotly express 的 "Weighted Pain Points" 图，F-042）与 `all_responses.html` 静态版随数据一起提交（F-040），读者无需重跑即可查看结果。

```
  2015-12-notebook-ux（完整管线）
  ┌──────────────────────────────────────────────────────────────┐
  │ README.md（元数据: date/credits）                            │
  │ SurveyExport.csv（1706×37 原始导出）                         │
  │ analysis/prep/                                               │
  │  1_review → 2_clean → 3a..3h 主题 → 4_roles → 5_utils        │
  │   └─ 10 个主题 CSV（hinderances/integrations/roles…）        │
  │ report_dashboard.ipynb + widgets/survey-explorer.html        │
  └──────────────────────────────────────────────────────────────┘

  2018-09-jupytercon-2018（脚本化切片）  2020-12-jupyter-survey（可视化切片）
  ┌─────────────────────────────┐      ┌─────────────────────────────┐
  │ phosphor_ux_data.csv        │      │ data/all_responses.csv      │
  │  + user_testing_data.py     │      │ data/text_fields.csv        │
  │ jupyterlab_ux_data.csv      │      │ all_responses.ipynb (350c)  │
  │  + analysis_utils.py        │      │ all_responses.html          │
  └─────────────────────────────┘      └─────────────────────────────┘
```

**复用价值**：纵向切片是数据集仓库的最佳组织方式——新调查可独立引入分析栈，不要求所有调查统一深度；但代价是需要每个切片自己维护 README 元数据与 frontmatter 的 `date` 字段（这是自动索引的依赖，见 I-001）。对"原始 CSV → 结构化分析"的清洗需求，`target_encoding` 字典 + 逐行 try/except 解析（F-038）是处理脏调查导出的轻量可移植手法，可直接复用于任意"编码字符串字段"的解析场景。
