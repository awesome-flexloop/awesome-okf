# sphinx-demo 事实清单

> R阶段产出：零推测事实，每条指向源码路径。

## 项目元信息

F-001: 项目名 `jupyterlite-sphinx-demo`，许可证为 BSD 3-Clause License，版权归 JupyterLite Contributors，定义于 `LICENSE:1-3`
F-002: 项目定位：展示如何将 JupyterLite 作为 Sphinx 文档站点的一部分静态部署到 GitHub Pages，使用 `jupyterlite-sphinx` 扩展，定义于 `README.md:1-3`
F-003: 项目包含两个并行示例目录：`pyodide-kernel-example/`（Pyodide 内核）和 `xeus-kernel-example/`（Xeus 内核），定义于 `README.md:24-27`
F-004: 两个示例均使用 PyData Sphinx Theme（`pydata_sphinx_theme`），定义于 `README.md:29`
F-005: 项目根目录包含入口页面 `index.html`（内核选择页）和版本切换器 `switcher.json`，定义于目录结构

## 根目录文件

F-006: `index.html` 是纯静态 HTML 落地页，包含 Pyodide 和 Xeus 两个内核的徽章链接表格，链接分别指向 `/pyodide/` 和 `/xeus/` 路径，定义于 `index.html:343-377`
F-007: `index.html` 内嵌 normalize.css 样式和 GitHub 风格的 markdown-body 样式，favicon 指向 Pyodide 站点的 favicon.ico，定义于 `index.html:8,10-336`
F-008: `switcher.json` 是 PyData 主题版本切换器配置，包含两个条目：name="pyodide" url=`/pyodide/`，name="xeus" url=`/xeus/`，定义于 `switcher.json:1-12`

## pyodide-kernel-example 目录结构

F-009: pyodide-kernel-example 目录包含 `README.md`、`requirements.txt` 和 `docs/` 子目录，定义于目录结构
F-010: `docs/Makefile` 是标准 Sphinx Makefile，SOURCEDIR=source，BUILDDIR=build，SPHINXBUILD=sphinx-build，定义于 `pyodide-kernel-example/docs/Makefile:1-20`
F-011: `docs/source/` 包含：conf.py, index.md, example.py, jupyter-lite.json, jupyter_lite_config.json, overrides.json, try_examples.json, apiref.md，定义于目录结构
F-012: `docs/source/_static/` 包含 button_styling.css, pypi.js, icon.svg，定义于目录结构
F-013: `docs/source/custom_contents/` 包含 matplotlib_demo.md（MyST Markdown notebook），定义于目录结构
F-014: `docs/source/disabled_examples/` 包含 demo.md 和 disabled_example.py，定义于目录结构

## xeus-kernel-example 目录结构

F-015: xeus-kernel-example 目录结构与 pyodide-kernel-example 基本相同，额外包含 `docs/source/environment.yml` 文件，定义于目录结构
F-016: xeus-kernel-example 的 requirements.txt 使用 `jupyterlite-xeus` 而非 `jupyterlite-pyodide-kernel`，定义于 `xeus-kernel-example/requirements.txt:13`
F-017: xeus-kernel-example 的 conf.py 中 switcher.version_match 设置为 "xeus"，pyodide 设为 "pyodide"，定义于 `pyodide-kernel-example/docs/source/conf.py:102` 和 `xeus-kernel-example/docs/source/conf.py:102`
F-018: xeus-kernel-example 的 conf.py 中 html_context.doc_path 设为 "xeus-kernel-example/docs/source/"，pyodide 设为 "pyodide-kernel-example/docs/source/"，定义于两个 conf.py:118

## conf.py 配置（Pyodide 版本，两个版本共有配置）

F-019: project 设为 "jupyterlite-sphinx-demo"，copyright 为 "2025, JupyterLite Contributors"，author 为 "JupyterLite Contributors"，release 为 "1.0.0"，定义于 `pyodide-kernel-example/docs/source/conf.py:13-16`
F-020: extensions 列表包含 8 个扩展：sphinx.ext.autodoc, sphinx.ext.mathjax, sphinx.ext.autosummary, sphinx.ext.doctest, jupyterlite_sphinx, sphinx_design, myst_nb, numpydoc，定义于 `pyodide-kernel-example/docs/source/conf.py:21-30`
F-021: sys.path 插入两个路径：当前目录 `"."` 和 `"disabled_examples"` 子目录，用于导入 example.py 和 disabled_example.py，定义于 `pyodide-kernel-example/docs/source/conf.py:33-34`
F-022: `jupyterlite_contents = ["custom_contents/*"]`，将 custom_contents 目录下的文件作为 JupyterLite 站点内容包含，定义于 `pyodide-kernel-example/docs/source/conf.py:43`
F-023: `jupyterlite_silence = True`，静默 JupyterLite 构建过程的详细输出，定义于 `pyodide-kernel-example/docs/source/conf.py:47`
F-024: `strip_tagged_cells = True`，从输出 HTML 中剥离带有 `jupyterlite_sphinx_strip` 标签的单元格内容，定义于 `pyodide-kernel-example/docs/source/conf.py:50`
F-025: `global_enable_try_examples = True`，自动为所有 numpydoc/sphinx.ext.napoleon 处理的 Examples 节插入 TryExamples 指令，定义于 `pyodide-kernel-example/docs/source/conf.py:54`
F-026: `try_examples_global_button_text = "Try it online"`，设置所有 TryExamples 按钮的全局文本，定义于 `pyodide-kernel-example/docs/source/conf.py:58`
F-027: `try_examples_global_warning_text` 设置实验性警告消息，内容为 Markdown 格式，包含指向 issue tracker 的链接，定义于 `pyodide-kernel-example/docs/source/conf.py:63-68`
F-028: `nb_execution_mode = "auto"`，MyST-NB 的笔记本执行模式设为自动，定义于 `pyodide-kernel-example/docs/source/conf.py:73`
F-029: html_theme 设为 "pydata_sphinx_theme"，html_logo 为 "_static/icon.svg"，定义于 `pyodide-kernel-example/docs/source/conf.py:78-79`
F-030: html_static_path 为 ["_static"]，html_css_files 为 ["button_styling.css"]，html_js_files 为 ["pypi.js"]，定义于 `pyodide-kernel-example/docs/source/conf.py:80-82`

## PyData 主题配置

F-031: html_theme_options.icon_links 包含两个图标链接：GitHub（fa-brands fa-github，指向仓库）和 PyPI（fa-custom fa-pypi，指向 jupyterlite-sphinx PyPI 页面），定义于 `pyodide-kernel-example/docs/source/conf.py:87-99`
F-032: html_theme_options.switcher.json_url 指向根目录的 switcher.json，version_match 区分 pyodide/xeus，定义于 `pyodide-kernel-example/docs/source/conf.py:100-103`
F-033: html_theme_options.navbar_end 为 ["theme-switcher", "version-switcher", "navbar-icon-links"]，定义于 `pyodide-kernel-example/docs/source/conf.py:104`
F-034: html_theme_options.secondary_sidebar_items 对所有页面显示 page-toc/sourcelink/edit-this-page，首页仅显示 page-toc，定义于 `pyodide-kernel-example/docs/source/conf.py:107-110`
F-035: html_context 配置 GitHub 编辑链接：github_url="https://github.com", github_user="jupyterlite", github_repo="sphinx-demo", github_version="main", doc_path 区分两个示例，定义于 `pyodide-kernel-example/docs/source/conf.py:113-119`

## JupyterLite 配置文件

F-036: jupyter-lite.json（Pyodide）中 jupyter-config-data 设置 appName="jupyterlite-sphinx-demo (Pyodide)"，defaultKernelName="python"，faviconUrl="./lab/favicon.ico"，定义于 `pyodide-kernel-example/docs/source/jupyter-lite.json:1-8`
F-037: jupyter-lite.json（Xeus）中 defaultKernelName="XPython"，appName="jupyterlite-sphinx-demo (Xeus)"，定义于 `xeus-kernel-example/docs/source/jupyter-lite.json:1-8`
F-038: jupyter_lite_config.json（两个版本相同）中 LiteBuildConfig 设置 no_sourcemaps=true，定义于 `pyodide-kernel-example/docs/source/jupyter_lite_config.json:1-5`
F-039: overrides.json（两个版本相同）配置 @jupyterlab/notebook-extension:panel 插件，在工具栏添加 Download 按钮（command="docmanager:download", icon="ui-components:download"），定义于 `pyodide-kernel-example/docs/source/overrides.json:1-14`
F-040: try_examples.json（两个版本相同）设置 global_min_height="400px"，ignore_patterns=["disabled_examples\\/demo.html"]，定义于 `pyodide-kernel-example/docs/source/try_examples.json:1-4`

## Xeus 特有配置

F-041: environment.yml（仅 xeus 有）name 为 "jupyterlite-wasm-env"，channels 包含 emscripten-forge（`https://repo.mamba.pm/emscripten-forge`）和 conda-forge，定义于 `xeus-kernel-example/docs/source/environment.yml:5-11`
F-042: environment.yml dependencies 包含 pandas、matplotlib、xeus-python，这些包预安装到 WASM 环境中，不能通过 pip 安装，定义于 `xeus-kernel-example/docs/source/environment.yml:15-21`

## 文档页面结构

F-043: index.md 使用 MyST 格式，包含 toctree 指令，maxdepth=1，包含 custom_contents/matplotlib_demo.md 和 apiref.md 两个页面，定义于 `pyodide-kernel-example/docs/source/index.md:14-20`
F-044: apiref.md 演示 numpydoc 风格 docstring 与 TryExamples 的自动集成，列出四个特性：按钮显示配置、数学公式渲染、逐docstring禁用按钮、try_examples.json配置，定义于 `pyodide-kernel-example/docs/source/apiref.md:9-21`
F-045: apiref.md 使用 `.. automodule:: example :members:` 指令自动生成 example 模块的 API 文档，定义于 `pyodide-kernel-example/docs/source/apiref.md:52-54`
F-046: apiref.md 使用 sphinx-design 的 dropdown 指令折叠显示 example.py 源码，定义于 `pyodide-kernel-example/docs/source/apiref.md:36-46`

## example.py 模块

F-047: example.py 导入 numpy、scipy.integrate.solve_ivp、pandas，定义于 `pyodide-kernel-example/docs/source/example.py:10-12`
F-048: `fibonacci_sequence(n)` 函数接受 int 参数 n，返回 list，包含 NumPy 绘图示例的 doctest，定义于 `pyodide-kernel-example/docs/source/example.py:15-63`
F-049: `analyze_data(data, column=None, bins=10)` 函数接受 array_like 或 DataFrame，返回统计字典（mean/median/std/min/max），定义于 `pyodide-kernel-example/docs/source/example.py:66-159`
F-050: `solve_pendulum_ode(theta0=np.pi/4, omega0=0, t_span=(0,10), g=9.8, L=1.0)` 函数演示 MathJax 数学公式渲染（`.. math::` 指令），使用 scipy.integrate.solve_ivp 求解微分方程，定义于 `pyodide-kernel-example/docs/source/example.py:162-255`
F-051: `image_processing(image)` 函数在 Examples 节开头使用 `.. disable_try_examples` 注释禁用 TryExamples 按钮，导入 skimage.color/filters，定义于 `pyodide-kernel-example/docs/source/example.py:258-332`

## custom_contents/matplotlib_demo.md

F-052: matplotlib_demo.md 是 MyST Markdown notebook（jupytext metadata: format_name=myst, format_version=0.13），定义于 `pyodide-kernel-example/docs/source/custom_contents/matplotlib_demo.md:1-8`
F-053: matplotlib_demo.md 第一个单元格使用 `+++ {"tags": ["jupyterlite_sphinx_strip"]}` 标签，配合 strip_tagged_cells=True 从 JupyterLite 部署中剥离该单元格，定义于 `pyodide-kernel-example/docs/source/custom_contents/matplotlib_demo.md:11`
F-054: matplotlib_demo.md 使用 `.. notebooklite:: matplotlib_demo.md :new_tab: True :new_tab_button_text: "Try it online!"` 指令嵌入新标签页按钮，定义于 `pyodide-kernel-example/docs/source/custom_contents/matplotlib_demo.md:32-36`
F-055: matplotlib_demo.md（Pyodide）说明 Pyodide 内核可根据 import 语句自动安装包（若包名与 PyPI/Pyodide 索引一致），也可使用 `import piplite; await piplite.install(...)` 或 `%pip install` 安装额外包，定义于 `pyodide-kernel-example/docs/source/custom_contents/matplotlib_demo.md:48-50`
F-056: matplotlib_demo.md（Xeus）说明包通过 environment.yml 从 emscripten-forge 预安装，不能通过 pip 安装额外包，定义于 `xeus-kernel-example/docs/source/custom_contents/matplotlib_demo.md:47-50`
F-057: matplotlib_demo.md 包含多个 {code-cell} 代码块，演示 matplotlib 折线图、柱状图、多系列图等，定义于两个版本的 matplotlib_demo.md

## disabled_examples/ 目录

F-058: disabled_examples/demo.md 使用 `orphan: true` frontmatter，说明如何通过 try_examples.json 的 ignore_patterns 逐页面禁用 TryExamples 按钮，定义于 `pyodide-kernel-example/docs/source/disabled_examples/demo.md:1-18`
F-059: disabled_examples/disabled_example.py 定义 `square_number(x)` 函数，其 docstring 包含 Examples 节但因页面被 ignore_patterns 匹配而不会显示 TryExamples 按钮，定义于 `pyodide-kernel-example/docs/source/disabled_examples/disabled_example.py:1-34`

## 静态资源

F-060: button_styling.css 定义 .try_examples_button 样式：白色文字（暗色模式黑色文字）、主题色背景、圆角、阴影、光泽悬停动画（@keyframes jupyterSheen）、悬停放大效果（scale 1.02），定义于 `pyodide-kernel-example/docs/source/_static/button_styling.css:1-70`
F-061: button_styling.css 定义 .try_examples_button_container 为 flex 布局，.try_examples_outer_iframe 设置上边距，定义于 `pyodide-kernel-example/docs/source/_static/button_styling.css:61-70`
F-062: pypi.js 使用 FontAwesome.library.add() 注册自定义 PyPI 图标（prefix="fa-custom", iconName="pypi"），SVG path 数据来自 simpleicons.org，定义于 `pyodide-kernel-example/docs/source/_static/pypi.js:1-16`
F-063: icon.svg 是 Jupyter 风格图标（黄色圆圈上的橙色"j"和"l"字母），尺寸 68x68，定义于 `pyodide-kernel-example/docs/source/_static/icon.svg`

## 依赖管理

F-064: Pyodide requirements.txt 固定 jupyterlite-sphinx>=0.20.0 和 jupyterlite-pyodide-kernel==0.5.2，定义于 `pyodide-kernel-example/requirements.txt:3-8`
F-065: Pyodide requirements.txt 包含 sphinx, pydata-sphinx-theme, myst-nb, matplotlib, numpy, scikit-image, scipy, pandas, numpydoc, sphinx-design，定义于 `pyodide-kernel-example/requirements.txt:13-30`
F-066: Xeus requirements.txt 使用 jupyterlite-xeus 替代 jupyterlite-pyodide-kernel，注释说明需要 micromamba 来解析 WASM 环境，定义于 `xeus-kernel-example/requirements.txt:1-13`

## GitHub Actions CI/CD

F-067: .github/workflows/pages.yml 定义 Build and Deploy 工作流，触发条件为 push 到 main、pull_request、workflow_dispatch 和每日定时（cron: "0 0 * * *"），定义于 `.github/workflows/pages.yml:1-10`
F-068: CI 使用 ubuntu-latest，Python 3.12，通过 astral-sh/setup-uv 安装 uv，定义于 `.github/workflows/pages.yml:25-45`
F-069: CI 矩阵策略构建两个站点：[pyodide-kernel-example, pyodide] 和 [xeus-kernel-example, xeus]，fail-fast=false，定义于 `.github/workflows/pages.yml:31-34`
F-070: Xeus 构建需要额外安装 mamba-org/setup-micromamba（条件：matrix.site[0] == 'xeus-kernel-example'），定义于 `.github/workflows/pages.yml:47-49`
F-071: 构建步骤：uv pip install -r requirements.txt → make html（工作目录为 {site}/docs），定义于 `.github/workflows/pages.yml:51-57`
F-072: SPHINXOPTS 环境变量设为 "-W --keep-going -j auto -D jupyterlite_silence=0"，将警告视为错误、并行构建、显示 JupyterLite 构建输出，定义于 `.github/workflows/pages.yml:20`
F-073: 构建产物上传为 artifact：name 为 matrix.site[1]，path 为 {site}/docs/build/html，保留 7 天，定义于 `.github/workflows/pages.yml:59-65`
F-074: Deploy 阶段仅在 push 到 main 或 workflow_dispatch 时运行，需要 build-sites 完成，定义于 `.github/workflows/pages.yml:67-75`
F-075: Deploy 步骤：下载 artifacts 到 dist/ → 移动根 index.html 和 switcher.json 到 dist/ → tree 验证 → peaceiris/actions-gh-pages 部署到 gh-pages 分支（force_orphan=true），定义于 `.github/workflows/pages.yml:82-103`
