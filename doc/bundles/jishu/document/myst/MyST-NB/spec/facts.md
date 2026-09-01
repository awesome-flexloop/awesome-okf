---
type: spec
title: MyST-NB 源码事实集（spec/facts.md）
description: MyST-NB 源码事实清单
tags:
- myst-nb
- spec
- facts
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
verified: grep-verified
status: stable
stale_after: '2027-08-23'
sources:
- id: myst-nb-source
  resource: /references/mystnb-source.md
  title: MyST-NB mystnb-source
- id: myst-nb-source-1
  resource: /references/notebook-cheatsheet.md
  title: MyST-NB notebook-cheatsheet
---

# MyST-NB 源码事实集（spec/facts.md）

> R 阶段产出：从 MyST-NB 源码中提取的可验证事实，零推论。
> 源码版本：v1.5.0.dev（myst_nb/__init__.py L3）
> 源码路径：d:/spaces/SpecWeave/external/libs/ai/executablebooks/MyST-NB/

## 1. 项目元信息

1. **版本**：`__version__ = "1.5.0.dev"`（myst_nb/__init__.py L3）
2. **Python 要求**：`requires-python = ">=3.10"`（pyproject.toml L37），支持 3.10/3.11/3.12/3.13/PyPy
3. **许可证**：BSD-3-Clause（pyproject.toml L12）
4. **构建后端**：flit_core >=3.11,<4（pyproject.toml L2）
5. **核心依赖**（pyproject.toml L38-51）：
   - importlib_metadata
   - ipython
   - jupyter-cache>=0.5
   - nbclient
   - myst-parser>=1.0.0
   - nbformat>=5.0
   - pyyaml
   - sphinx>=5
   - typing-extensions
   - ipykernel（常用依赖，注册 python3 kernel）
6. **入口点 - 渲染器**：`myst_nb.renderers` 组：`default = myst_nb.core.render:NbElementRenderer`（pyproject.toml L57-58）
7. **入口点 - MIME 渲染插件**：`myst_nb.mime_renderers` 组：`example = myst_nb.core.render:ExampleMimeRenderPlugin`（pyproject.toml L60-61）
8. **入口点 - Pygments Lexer**（pyproject.toml L63-65）：
   - `myst-ansi = myst_nb.core.lexers:AnsiColorLexer`
   - `ipythontb = myst_nb.core.lexers:IPythonTracebackLexer`
9. **入口点 - jcache reader**：`jcache.readers` 组：`myst_nb_md = myst_nb.core.read:myst_nb_reader_plugin`（pyproject.toml L67-68）
10. **CLI 入口点**（pyproject.toml L112-119）：
    - `mystnb-quickstart = myst_nb.cli:quickstart`
    - `mystnb-to-jupyter = myst_nb.cli:md_to_nb`
    - `mystnb-docutils-html = myst_nb.docutils_:cli_html`
    - `mystnb-docutils-html5 = myst_nb.docutils_:cli_html5`
    - `mystnb-docutils-latex = myst_nb.docutils_:cli_latex`
    - `mystnb-docutils-xml = myst_nb.docutils_:cli_xml`
    - `mystnb-docutils-pseudoxml = myst_nb.docutils_:cli_pseudoxml`

## 2. 核心目录结构

11. **myst_nb/__init__.py**：包入口，导出 `__version__`、`setup()`、`glue()` 函数
12. **myst_nb/core/config.py**：NbParserConfig 配置数据类，核心配置中心
13. **myst_nb/core/read.py**：Notebook 读取层——ipynb/mystnb 文本格式解析
14. **myst_nb/core/execute/**：执行引擎层（base/cache/direct/inline 四种客户端）
15. **myst_nb/core/render.py**：渲染层——MIME 类型选择、docutils 节点生成
16. **myst_nb/core/nb_to_tokens.py**：Notebook→markdown-it Token 转换
17. **myst_nb/core/loggers.py**：日志系统（Sphinx/Docutils 双模式）
18. **myst_nb/core/lexers.py**：Pygments 自定义 Lexer（ANSI 彩色、IPython traceback）
19. **myst_nb/core/variables.py**：变量输出渲染（eval/glue 共用）
20. **myst_nb/core/utils.py**：工具函数（流合并等）
21. **myst_nb/sphinx_ext.py**：Sphinx 扩展注册主入口（sphinx_setup）
22. **myst_nb/sphinx_.py**：Sphinx 解析器实现（Parser、Renderer、Post-Transforms）
23. **myst_nb/docutils_.py**：Docutils 独立模式解析器实现
24. **myst_nb/cli.py**：CLI 工具（quickstart、md_to_nb）
25. **myst_nb/warnings_.py**：警告系统（MystNBWarnings 枚举）
26. **myst_nb/ext/glue/**：Glue 扩展——变量粘贴（domain/roles/directives/crossref）
27. **myst_nb/ext/eval/**：Eval 扩展——内联变量求值
28. **myst_nb/ext/download.py**：nb-download 角色（下载执行后的 notebook）
29. **myst_nb/ext/execution_tables.py**：执行统计表扩展
30. **myst_nb/ext/utils.py**：扩展工具基类（DirectiveBase、RoleBase）
31. **myst_nb/static/mystnb.css**：默认 CSS 样式

## 3. NbParserConfig 配置系统

32. **配置类**：`NbParserConfig` 是一个 `@dc.dataclass()`，定义于 myst_nb/core/config.py L118
33. **配置前缀**：在 Sphinx 配置中，所有选项名以 `nb_` 为前缀（config.py L122 注释）
34. **配置段标签**：Section 枚举定义 6 个段（config.py L98-114）：
    - `global_lvl = "global"`：全局级配置
    - `file_lvl = "notebook"`：文件级配置
    - `cell_lvl = "cell"`：Cell 级配置
    - `config = "config"`：元配置
    - `read = "read"`：读取配置
    - `execute = "execute"`：执行配置
    - `render = "render"`：渲染配置
35. **custom_formats**：Dict[str, Tuple[str, dict, bool]]，默认空 dict，自定义文件格式读取器
36. **metadata_key**：str，默认 `"mystnb"`，Notebook 级元数据键名
37. **cell_metadata_key**：str，默认 `"mystnb"`，Cell 级元数据键名，legacy_name 为 `"nb_render_key"`
38. **kernel_rgx_aliases**：Dict[str, str]，默认空 dict，kernel 名称正则映射
39. **eval_name_regex**：str，默认 `r"^[a-zA-Z_][a-zA-Z0-9_]*$"`，eval 表达式名称正则
40. **execution_mode**：Literal["off","force","auto","cache","inline"]，默认 `"auto"`，legacy_name 为 `"jupyter_execute_notebooks"`
41. **execution_cache_path**：str，默认 `""`（空时使用 outdir/.jupyter_cache），legacy_name 为 `"jupyter_cache"`
42. **execution_excludepatterns**：Sequence[str]，默认空元组，排除执行的 POSIX glob 模式
43. **execution_timeout**：int，默认 30 秒，legacy_name 为 `"execution_timeout"`
44. **execution_in_temp**：bool，默认 False，是否在临时目录执行
45. **execution_allow_errors**：bool，默认 False，是否允许执行错误
46. **execution_raise_on_error**：bool，默认 False，执行失败时抛异常而非警告
47. **execution_show_tb**：bool，默认 False，执行错误时是否打印 traceback 到 stderr
48. **merge_streams**：bool，默认 False，是否合并所有 stdout/stderr 流
49. **render_plugin**：str，默认 `"default"`，渲染器入口点名
50. **remove_code_source**：bool，默认 False，移除代码 cell 源码
51. **remove_code_outputs**：bool，默认 False，移除代码 cell 输出
52. **scroll_outputs**：bool，默认 False，长输出滚动显示
53. **code_prompt_show**：str，默认 `"Show code cell {type}"`，展开隐藏代码提示
54. **code_prompt_hide**：str，默认 `"Hide code cell {type}"`，折叠隐藏代码提示
55. **number_source_lines**：bool，默认 False，代码行号
56. **builder_name**：str，默认 `"html"`，builder 名称（用于 MIME 优先级选择），sphinx_exclude=True
57. **mime_priority_overrides**：Sequence[Tuple[str,str,Optional[int]]]，默认空元组
58. **output_stderr**：Literal["show","remove","remove-warn","warn","error","severe"]，默认 `"show"`
59. **render_text_lexer**：str，默认 `"myst-ansi"`，stdout/stderr 的 Pygments lexer
60. **render_error_lexer**：str，默认 `"ipythontb"`，error/traceback 的 Pygments lexer
61. **render_image_options**：Dict[str,str]，默认空 dict，图片输出选项（class/alt/height/width等）
62. **render_figure_options**：Dict[str,str]，默认空 dict，figure 输出选项（classes/name/caption等）
63. **render_markdown_format**：Literal["commonmark","gfm","myst"]，默认 `"commonmark"`，text/markdown 渲染格式
64. **ipywidgets_js**：Dict[str,Dict[str,str]]，默认 factory 函数返回 RequireJS + Jupyter Widgets CDN
65. **output_folder**：str，默认 `"build"`，外部输出文件夹（docutils 模式），sphinx_exclude=True
66. **append_css**：bool，默认 True，添加默认 CSS（docutils 模式），sphinx_exclude=True
67. **metadata_to_fm**：bool，默认 False，未处理元数据转 frontmatter（docutils 模式），sphinx_exclude=True
68. **字段元数据属性**：每个 dc.field 支持 `help`、`validator`、`sections`、`sphinx_exclude`、`omit`、`legacy_name`、`cell_key`
69. **三层优先级**：cell > document > global > default（get_cell_level_config 方法，config.py L590-644）
70. **custom_formats_converter**：将自定义格式配置转换为标准 Tuple 格式（config.py L20-56）

## 4. Notebook 读取层

71. **NbReader 数据类**（read.py L25-34）：包含 read 函数、md_config、read_fmt
72. **standard_nb_read()**（read.py L37-39）：使用 nbformat.reads() 读取标准 .ipynb
73. **create_nb_reader()**（read.py L42-99）：根据文件路径后缀选择读取器
74. **自定义格式加载**：通过 sphinx.util.import_object 动态加载（read.py L63-65/76-78）
75. **后缀匹配**：按长度降序排列后缀，优先最长匹配（read.py L73）
76. **is_myst_markdown_notebook()**（read.py L102-151）：检测 .md 文件是否为 MyST notebook：
    - frontmatter 含 `file_format: mystnb` → 是
    - frontmatter 含 `jupytext.text_representation.format_name: myst` → 是
77. **read_myst_markdown_notebook()**（read.py L176-293）：将 myst 格式文本转为 NotebookNode：
    - 使用 markdown-it 解析到 block 级别
    - 识别 `{code-cell}` 围栏 → 代码 cell
    - 识别 `{raw-cell}` 围栏 → raw cell
    - 识别 `+++` block break → markdown cell 分隔符（含 JSON 元数据）
    - 支持 `:load:` 选项从外部文件加载代码
    - 可选生成 source_map 元数据
78. **code-cell 指令**：```{code-cell} python3\n...``` 格式，支持参数、选项、:load:
79. **raw-cell 指令**：```{raw-cell} format\n...``` 格式
80. **UnexpectedCellDirective**（read.py L380-411）：当 code-cell/raw-cell 被遗留到渲染阶段时发出警告（通常是因为嵌套或缺少 jupytext header）
81. **NOTEBOOK_VERSION**：常量 4（read.py L21），nbformat v4
82. **myst_nb_reader_plugin**（read.py L166-173）：jupyter-cache 的读取插件入口

## 5. 执行引擎层

83. **create_client()** 工厂函数（execute/__init__.py L19-81）：根据 execution_mode 创建执行客户端
84. **执行模式映射**（execute/__init__.py L64-79）：
    - `"off"` / 默认 → NotebookClientBase（不执行，返回空客户端）
    - `"auto"`（输出完整则跳过）/ `"force"` → NotebookClientDirect（直接 nbclient 执行）
    - `"cache"` → NotebookClientCache（jupyter-cache 缓存执行）
    - `"inline"` → NotebookClientInline（内联执行，用于 eval 角色）
85. **NotebookClientBase**（execute/base.py）：基类，不执行 notebook
86. **NotebookClientDirect**（execute/direct.py）：直接使用 nbclient 执行 notebook
87. **NotebookClientCache**（execute/cache.py）：使用 jupyter-cache 缓存执行结果
88. **NotebookClientInline**（execute/inline.py）：启动 kernel 进行内联变量求值
89. **auto 模式逻辑**：检查所有代码 cell 是否有输出，全部有输出则跳过执行（execute/__init__.py L57-62）
90. **排除模式**：通过 execution_excludepatterns 使用 POSIX glob 匹配（execute/__init__.py L49-54）

## 6. 渲染层

91. **NbElementRenderer**（render.py）：核心渲染器类，通过 entry point 加载
92. **RENDER_ENTRY_GROUP**：`"myst_nb.renderers"`（render.py L48）
93. **MIME_RENDER_ENTRY_GROUP**：`"myst_nb.mime_renderers"`（render.py L49）
94. **load_renderer()**：通过 entry_points 加载渲染器
95. **MIME 类型优先级**：get_mime_priority() 根据 builder_name 选择 MIME 渲染优先级
96. **MIME 类型常量**（render.py L46-59）：
    - WIDGET_STATE_MIMETYPE = "application/vnd.jupyter.widget-state+json"
    - WIDGET_VIEW_MIMETYPE = "application/vnd.jupyter.widget-view+json"
    - _BINARY_IMAGE_MIMES = {image/png, image/jpeg, image/gif, image/webp, application/pdf}
    - _IMAGE_MIMES = _BINARY_IMAGE_MIMES ∪ {image/svg+xml}
97. **MditRenderMixin**（render.py L62-）：DocutilsRenderer 和 SphinxRenderer 的共享 Mixin
98. **nb_config 属性**：从 md_options["nb_config"] 获取 NbParserConfig
99. **nb_client 属性**：从 md_options["nb_client"] 获取执行客户端
100. **nb_renderer 属性**：从 document["nb_renderer"] 获取 NbElementRenderer
101. **图片输出处理**：二进制图片 MIME 类型写入 output_folder，生成 image 节点
102. **stderr 处理**：output_stderr 配置控制 show/remove/remove-warn/warn/error/severe
103. **Pygments 高亮**：stdout/stderr 使用 myst-ansi lexer，错误使用 ipythontb lexer

## 7. Sphinx 集成

104. **sphinx_setup()**（sphinx_ext.py L43-123）：Sphinx 扩展初始化
105. **MyST-Parser 初始化**：先调用 `setup_myst_parser(app)` 初始化 MyST-Parser 配置和 transforms（但不添加 parser）（sphinx_ext.py L49）
106. **配置注册**：遍历 NbParserConfig 字段，通过 app.add_config_value() 注册 `nb_*` 配置（sphinx_ext.py L52-62）
107. **遗留配置名**：通过 `legacy_name` 元数据注册旧版配置名，并在 create_mystnb_config 中发出弃用警告（sphinx_ext.py L56-62, L142-152）
108. **builder-inited 事件**：连接 create_mystnb_config，验证配置并创建 NbParserConfig 实例存入 app.env.mystnb_config
109. **源解析器注册**：app.add_source_parser(Parser)，添加 .md 和 .ipynb 后缀为 myst-nb
110. **自定义格式后缀**：config-inited 事件中通过 add_nb_custom_formats() 添加
111. **排除模式**：config-inited 事件中添加 `**.ipynb_checkpoints`
112. **环境收集器**：NbMetadataCollector（收集每页 JS 资源等）
113. **指令注册**：code-cell、raw-cell 注册为 UnexpectedCellDirective（仅作警告用）
114. **角色注册**：{nb-download} 角色（NbDownloadRole）
115. **扩展加载**：load_eval_sphinx(app)、load_glue_sphinx(app)
116. **Post-Transforms**：SelectMimeType、ReplacePendingGlueReferences、HideInputCells
117. **CSS 加载**：add_css() 注册带 hash 的 mystnb.css，build-finished 事件复制 CSS 文件
118. **JS 加载**：html-page-context 事件按页添加 ipywidgets JS
119. **execution_tables 扩展**：setup_exec_table_extension(app)
120. **OUTPUT_FOLDER**：常量 "jupyter_execute"（sphinx_ext.py L36）
121. **缓存路径**：默认 <outdir>/../.jupyter_cache（sphinx_ext.py L176）
122. **并行安全**：parallel_read_safe=True, parallel_write_safe=True（sphinx_ext.py L121-122）

## 8. Sphinx 解析器

123. **Parser 类**（sphinx_.py L60-）：继承 MystParser，supported = ("myst-nb",)
124. **parse() 方法**：重写解析流程：读取 notebook → 执行 → 转换为 tokens → MyST 渲染
125. **SphinxRenderer**：继承 myst_parser 的 SphinxRenderer，混入 MditRenderMixin
126. **NbMetadataCollector**：EnvironmentCollector，收集 nb_metadata（每页 JS 文件等）
127. **SelectMimeType**：SphinxPostTransform，从 MIME bundle 中选择最终渲染类型
128. **HideInputCells**：SphinxPostTransform，处理代码折叠/隐藏
129. **HideCodeCellNode**：自定义节点类型，可折叠代码块

## 9. Docutils 独立模式

130. **Parser 类**（docutils_.py L74-）：继承 myst_parser 的 DocutilsParser，supported = ("mystnb", "ipynb")
131. **DocutilsApp**（docutils_.py L58-61）：模拟 Sphinx app 的简单容器，存储 roles 和 directives
132. **get_nb_roles_directives()**（docutils_.py L64-71）：缓存加载所有指令和角色（code-cell/raw-cell/eval/glue）
133. **CLI 命令**：mystnb-docutils-html/html5/latex/xml/pseudoxml
134. **DocutilsNbRenderer**：继承 myst_parser 的 DocutilsRenderer，混入 MditRenderMixin

## 10. Glue 扩展

135. **glue() 函数**（__init__.py L14-32 / ext/glue/__init__.py L63-84）：将变量的显示数据存入 cell 输出
136. **GLUE_PREFIX**：`"application/papermill.record/"`（ext/glue/__init__.py L20）
137. **glue 实现**：使用 IPython.formatters.format_display_data() 格式化变量，通过 ipy_display(raw=True) 输出带 scrapbook 元数据的 mimebundle
138. **extract_glue_data()**（ext/glue/__init__.py L87-107）：从 notebook cell 输出中提取 glue 数据
139. **Sphinx glue 加载**：load_glue_sphinx() 注册 {glue} 指令/角色、NbGlueDomain
140. **Docutils glue 加载**：load_glue_docutils() 注册 {glue:any}/{glue:text}/{glue:md}/{glue:figure}/{glue:math}
141. **glue 指令**：PasteAnyDirective/PasteFigureDirective/PasteMarkdownDirective/PasteMathDirective
142. **glue 角色**：PasteRoleAny/PasteTextRole/PasteMarkdownRole
143. **NbGlueDomain**：Sphinx Domain，存储跨页面 glue 数据
144. **ReplacePendingGlueReferences**：Post-Transform，替换 pending 的 glue 引用
145. **crossref.py**：Glue 交叉引用解析

## 11. Eval 扩展

146. **Eval 功能**：在文档正文中通过 {eval} 角色/指令内联求值 kernel 变量
147. **EvalNameError**：变量名不匹配 eval_name_regex 时抛出（core/execute/base.py）
148. **EvalRoleAny**（ext/eval/__init__.py L75-）：角色，按 MIME 优先级渲染变量输出
149. **retrieve_eval_data()**（ext/eval/__init__.py L35-72）：从 nb_client.eval_variable() 获取变量输出
150. **VariableOutput**（core/variables.py）：变量输出数据类
151. **render_variable_outputs()**（core/variables.py）：渲染变量输出为 docutils 节点

## 12. 警告系统

152. **MystNBWarnings 枚举**（warnings_.py L19-36）：6 种警告类型：
    - LEXER = "lexer"：Lexer 解析问题
    - FIG_CAPTION = "fig_caption"：图标题问题
    - MIME_TYPE = "mime_type"：MIME 类型问题
    - OUTPUT_TYPE = "output_type"：输出类型问题
    - CELL_METADATA_KEY = "cell_metadata_key"：cell metadata 键问题
    - CELL_CONFIG = "cell_config"：cell 配置/元数据问题
153. **create_warning()**（warnings_.py L64-104）：统一警告创建，自动转发 MyST-Parser 警告
154. **警告类型**：所有 MyST-NB 警告类型为 "myst-nb"
155. **警告抑制**：通过 suppress_warnings = ["myst-nb"] 或 ["myst-nb.<subtype>"] 抑制

## 13. CLI 工具

156. **mystnb-quickstart**（cli.py L15-41）：创建模板项目（conf.py、index.md、notebook1.ipynb、notebook2.md）
157. **quickstart 选项**：PATH（位置参数）、-o/--overwrite、-v/--verbose
158. **mystnb-to-jupyter**（cli.py L146-163）：将文本格式 notebook 转为 .ipynb
159. **md_to_nb 选项**：PATH_IN、PATH_OUT（可选）、-o/--overwrite、-v/--verbose
160. **generate_conf_py()**（cli.py L56-89）：生成包含所有 nb_* 默认配置的 conf.py 模板
161. **generate_text_notebook()**（cli.py L125-143）：生成 mystnb 格式的文本 notebook 模板

## 14. Notebook→Token 转换

162. **notebook_to_tokens()**（core/nb_to_tokens.py）：将执行后的 NotebookNode 转换为 markdown-it Token 流
163. **nb_node_to_dict()**：将 NotebookNode 转为 dict

## 15. 其他关键事实

164. **与 MyST-Parser 关系**：MyST-NB 建立在 MyST-Parser 之上，Parser 类继承 MystParser，先调用 setup_myst_parser 初始化
165. **.md 文件特殊处理**：.md 文件只有在 frontmatter 含 `file_format: mystnb` 或 jupytext myst 标记时才作为 notebook 处理
166. **ipywidgets 支持**：内置 RequireJS + @jupyter-widgets/html-manager CDN 配置
167. **CSS 静态文件**：mystnb.css 通过 content hash 命名以支持缓存
168. **代码 cell 标签支持**：支持 `remove_cell`/`remove-input`/`remove-output`/`remove-stderr`/`skip-execution`/`raises-exception` 等 cell tags
169. **Cell metadata key**：默认为 mystnb，旧版 render 键自动迁移并发出弃用警告
170. **文本 notebook 分隔符**：`+++` 行分隔 markdown cells，后跟可选 JSON metadata
