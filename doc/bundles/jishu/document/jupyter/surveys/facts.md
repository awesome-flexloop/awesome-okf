---
type: Facts
okf_version: "0.2"
title: "surveys 源码事实清单"
generated: "2026-08-22"
tags: [jupyter, surveys, community, documentation]
sources:
  - ../../../../../external/libs/jupyter/surveys/README.md
  - ../../../../../external/libs/jupyter/surveys/noxfile.py
  - ../../../../../external/libs/jupyter/surveys/docs/myst.yml
  - ../../../../../external/libs/jupyter/surveys/docs/index.md
  - ../../../../../external/libs/jupyter/surveys/.github/workflows/deploy.yml
  - ../../../../../external/libs/jupyter/surveys/surveys/2020-12-jupyter-survey/README.md
  - ../../../../../external/libs/jupyter/surveys/surveys/2015-12-notebook-ux/README.md
---
# surveys 源码事实清单

> R 阶段产出：零推测事实，每条事实指向具体源码文件与行号。

## 项目元数据与许可

- F-001: README.md:1,5,29-44 — 一级标题 `# Jupyter Surveys`，定位为 "This repository contains datasets and surveys collected by Project Jupyter and IPython."；README 分节说明 Jupyter user surveys 位于 `surveys/`（浏览入口 jupyter.github.io/surveys），并记录 IPython 2011/2013 用户调查结果及 writeup 链接（ipython.org/usersurvey2011.html 与 usersurvey2013.html）
- F-002: README.md:3 — 顶部含 Binder badge，链接 `https://mybinder.org/v2/gh/jupyter/surveys/master`，支持在 Binder 中直接运行仓库
- F-003: LICENSE:1 + README.md:46-48 — 仓库默认许可是 CC0 1.0 Universal；README 声明若某数据集使用不同许可，须在其子目录内包含该许可文件，且子目录许可优先于仓库许可

## 数据贡献约定（README）

- F-004: README.md:9-11 — 新增数据集的约定：在相关顶层目录下创建 `YYYY-MM-short-description` 命名的子目录，调查类数据放在 `surveys` 顶层目录下
- F-005: README.md:11-17 — 每个新子目录须创建 `README.md`，内容须含：数据收集日期、收集者、population 说明（人类数据）/代码位置（模拟数据）等来源信息；可补充引用信息如 DOI，无 DOI 时可上传到 Zenodo 等平台获取

## 文档构建系统（nox + MyST）

- F-006: noxfile.py:1,3,5 — 文件 docstring 为 "Nox sessions for the Jupyter Surveys documentation."，`import nox`，并设置 `nox.options.default_venv_backend = "uv|virtualenv"`
- F-007: noxfile.py:8-13 — `docs` session：`session.chdir("docs")`、`session.install("mystmd")`、`session.run("myst", "build", "--html")`，构建静态 HTML
- F-008: noxfile.py:16-21 — `docs-live` session：`session.chdir("docs")`、`session.install("mystmd")`、`session.run("myst", "start")`，启动 live-reload 开发服务器
- F-009: docs/myst.yml:1-4 — `version: 1`；`project.title` 为 "Jupyter Surveys"；`project.description` 为 "Datasets and surveys collected by Project Jupyter and IPython."
- F-010: docs/myst.yml:5-9 — `project.keywords` 为 [Jupyter, IPython, surveys]；`project.github` 指向 https://github.com/jupyter/surveys
- F-011: docs/myst.yml:10-12 — `project.plugins` 引入 myst-contrib 的 `myst-listing` 插件（plugin.mjs），用于在站点中列出 surveys
- F-012: docs/myst.yml:13-17 — `project.toc`：根为 `index.md`，标题 "Surveys" 组下 children 用 `pattern: surveys/**/README.md` 递归包含所有调查 README
- F-013: docs/myst.yml:18-25 — `site.template` 为 `book-theme`；`site.options` 含 analytics_plausible: jupyter.org、logo_text "Jupyter Surveys"、logo/logo_dark/favicon 均指向 docs/images/
- F-014: docs/index.md:1-4,6-9 — 页面标题 `# Jupyter Surveys`，正文链接到仓库 README；使用 `:::{listing}` directive，`:path: surveys/*/README.md`、`:columns: title,date` 自动列出各调查
- F-015: docs/surveys:1 + git ls-files -s — `docs/surveys` 是内容为 `../surveys` 的 git 符号链接（mode 120000），指向顶层 `surveys/` 数据目录，使 myst.yml 与 index.md 中的 `surveys/**/README.md` 模式能解析到实际数据目录

## 持续部署（.github/workflows/deploy.yml）

- F-016: deploy.yml:2-6 — workflow name 为 `Deploy`；触发条件为 push 到 `master` 分支及 `workflow_dispatch` 手动触发
- F-017: deploy.yml:8-11 — `permissions`：contents: read、pages: write、id-token: write
- F-018: deploy.yml:13-22 — job `deploy`：environment `github-pages`、runs-on ubuntu-latest；步骤为 actions/checkout@v4、actions/configure-pages@v3、actions/setup-node@v4（node-version 20.x）
- F-019: deploy.yml:23-28 — 安装 MyST：`npm install -g mystmd`；构建：`cd docs && myst build --html`，并设置 `env.BASE_URL: /surveys` 用于 GitHub Pages 子路径部署
- F-020: deploy.yml:29-34 — actions/upload-pages-artifact@v3 上传 `./docs/_build/html`，actions/deploy-pages@v4 部署到 GitHub Pages

## 环境与忽略规则

- F-021: binder/requirements.txt:1-7 + .gitignore:1-4,41,68,74 — Binder 环境依赖锁定为 jupyter_cms、gensim==3.6.*、matplotlib==3.0.*、pandas==0.23.*、scikit-learn==0.19.*、scipy==1.1.*、seaborn==0.9.*；.gitignore 忽略 `__pycache__/`、`*.py[cod]`、`.nox/`、`docs/_build/`、`.ipynb_checkpoints`

## 2015-12 Notebook UX 调查

- F-022: surveys/2015-12-notebook-ux/README.md:2 — frontmatter 含 `date: 2015-12-21`
- F-023: surveys/2015-12-notebook-ux/README.md:5-7 — 16 问 Jupyter Notebook 用户体验调查，运行于 SurveyGizmo，时间 2015-12-21 至 2016-01-15；通过 Project Jupyter Google Group、Jupyter blog、@ProjectJupyter Twitter 分发
- F-024: surveys/2015-12-notebook-ux/README.md:19-21 — 数据文件 `20160115235816-SurveyExport.csv` 含 1706 行 37 列，为调查工具直接导出、未做预处理
- F-025: surveys/2015-12-notebook-ux/README.md:23-28 — CSV 每行代表一次参与者 session（从首次访问到提交或离开）；其中 927 个 partial（54%）、779 个 complete（46%）
- F-026: surveys/2015-12-notebook-ux/README.md:30-38 — 前 3 列为 session 元数据：Time Started（GMT-06:00）、Date Submitted、Status（Complete/Partial）
- F-027: surveys/2015-12-notebook-ux/README.md:40-57 — 其余 34 列对应 16 个问题，含 Choice、Text、多选题多列重复、选择+write-in 等类型；缺失值表示未填写
- F-028: surveys/2015-12-notebook-ux/README.md:59-61 — Credits：Julie Santilli、@parente、@ellisonbg、@fperez、@jasongrout、@minrk、@carreau
- F-029: surveys/2015-12-notebook-ux/analysis/README.md:1-8 + analysis/prep/ — `analysis/` 是 @parente 与 @jtyberg 对 UX 调查数据的分析，入口为 `report_dashboard.ipynb`，交互版由 @peller/@aluu317 完成；`analysis/prep/` 含 12 个处理 notebook（1_ux_survey_review、2_clean_survey、3a~3h 八个主题、4_primary_roles、5_utils）、10 个主题 CSV（如 hinderances_themes.csv、integrations_themes.csv、roles.csv）及 widgets/survey-explorer/survey-explorer.html

## 2016-05 教育调查

- F-030: surveys/2016-05-education-survey/README.md:2 — frontmatter 含 `date: 2016-04-22`，顶部含 Zenodo DOI badge（10.5281/zenodo.51701，README.md:7）
- F-031: surveys/2016-05-education-survey/README.md:9-17 — 数据文件含 `questions.pdf`（问题 PDF）与 `responses.csv`（响应 CSV）；调查由 Jessica Hamrick（@jhamrick）设计，来源主要为 Jupyter、Jupyter Education、Software Carpentry 邮件列表，2016-04-22 至 05-07 间收集
- F-032: surveys/2016-05-education-survey/README.md:19-30 — README 末尾含完整 BibTeX 引用条目 `Hamrick2016`（author/doi/url 等字段）

## 2018-09 JupyterCon 调查

- F-033: surveys/2018-09-jupytercon-2018/README.md:2,5-9 — frontmatter `date: 2018-08-21`；为 JupyterCon 2018（2018-08）由 Cal Poly 实习生与 Tim George（@tgeorgeux）收集的 JupyterLab UX 用户测试数据；分析入口为 `analysis/questions-to-answer.ipynb`
- F-034: surveys/2018-09-jupytercon-2018/README.md:11-19 — 运行方式：clone → 进入目录 → `pipenv install`（或 `pip install -r requirements.txt`）→ 打开并运行 `questions-to-answer.ipynb`
- F-035: surveys/2018-09-jupytercon-2018/README.md:22-55 — 数据分两部分：`phosphor test`（18 个字段：Code/Test/Tab/Center/L/B/Task/ST/CT/ToT/Init/CFA/aCFA/CEDZ/FS/Notes/source/target/position）与 `jupyterlab test`（Code Name/Subtask #/Correct Path/Time User Started/First Action/First Success/Second success/Eventual success/Notes）
- F-036: surveys/2018-09-jupytercon-2018/requirements.txt:1,23 — 首行指定 `-i https://pypi.org/simple/` 索引，依赖锁定版本（含 jupyterlab==0.34.12、pandas==0.23.4、seaborn==0.9.0 等）
- F-037: surveys/2018-09-jupytercon-2018/jupyterlab_test/analysis_utils.py:9-32,35-63 — `convert_time_to_int()` 解析 mm:ss / hh:mm:ss 为秒、`diff_times()` 求两时间差；`load_data()` 读取 `jupyterlab-ux-data.csv`（header=1），按 Code Name 分组排序计算 "Time on task" 与 "Start time"
- F-038: surveys/2018-09-jupytercon-2018/phosphor_test/user_testing_data.py:9-17,20-81 — `load_data()` 读取 `phosphor-ux-data.csv`；`reload_data()` 从 Google Sheets（docs.google.com/spreadsheet key=1TCWnKucs25...）下载 CSV；`cleaner()` 通过 `target_encoding` 字典解析 Init 移动（source/target/position）、将 ToT 转为秒

## 2020-12 Jupyter 调查

- F-039: surveys/2020-12-jupyter-survey/README.md:2,5-6 — frontmatter `date: 2020-12-01`；由 Layne Sadler（@layne-sadler）主导的 2020 Jupyter Survey
- F-040: surveys/2020-12-jupyter-survey/README.md:7-13 — 文件：`data/all_responses.csv`（多选/矩阵题响应）、`data/text_fields.csv`（文本题响应）、`all_responses.ipynb`（可视化分析，需 Python 3.7+ 与 pandas、plotly_express、jupyterlab-plotly）、`all_responses.html`；数据经 SurveyMonkey 收集，2020-12 至 2021-02
- F-041: surveys/2020-12-jupyter-survey/README.md:15-16 — 背景：为回应 jupyterlab/team-compass#80 讨论而发起，旨在了解开发会议之外的社区，并为 JupyterLab 4.0 路线图提供参考
- F-042: surveys/2020-12-jupyter-survey/all_responses.ipynb — notebook 共 350 个 cell（jq 验证）；首个 code cell 使用 plotly express（`px.bar`）绘制标题为 "Weighted Pain Points" 的条形图

## 2022/2023 无障碍测试

- F-043: surveys/2022-08-notebooks-for-all/README.md:2,5-12 — frontmatter `date: 2022-08-01`；链接 Iota-School/notebooks-for-all 仓库中 2022-2023 两次 nbconvert HTML 输出无障碍用户测试结果（test 1 导航/结构、test 2 内容访问）；测试在 Zoom 小规模同步进行，每次 1 名参与者 + 1 名引导者 + 1 名记录者
- F-044: surveys/2023-05-jupyterlab-accessibility/README.md:2,5-9 — frontmatter `date: 2023-05-01`；2023-05 在 JupyterLab 3.6.1（JupyterHub 托管）上进行的无障碍可用性研究，结果与测试脚本位于 Quansight-Labs/JupyterLab-user-testing 仓库
- F-045: surveys/2023-05-jupyterlab-accessibility/README.md:15-17 — 背景：作为 JupyterLab 无障碍工作的基线测试，聚焦常见任务与 JupyterLab 各主要区域导航；由 Chan Zuckerberg Initiative EOSS 科学软件资助
