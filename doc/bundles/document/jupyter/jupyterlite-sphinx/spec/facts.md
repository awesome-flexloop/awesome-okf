# jupyterlite-sphinx 事实清单

> R阶段产出：零推测事实，每条指向源码路径。

## 包元信息

F-001: 包名 `jupyterlite-sphinx`，版本号 `__version__ = "0.23.0"`，定义于 `jupyterlite_sphinx/__init__.py:3`
F-002: 构建系统使用 hatchling（`[build-system] requires = ["hatchling"]`），定义于 `pyproject.toml:1-3`
F-003: Python 版本要求 `>=3.10`，定义于 `pyproject.toml:11`
F-004: 核心运行时依赖：docutils, jupyter_server, jupyterlab_server, jupyterlite-core >=0.2,<0.9, nbformat, sphinx>=4，定义于 `pyproject.toml:15-22`
F-005: 可选依赖组 `markdown` 包含 jupytext，定义于 `pyproject.toml:25`
F-006: `__init__.py` 从 `.jupyterlite_sphinx` 导入 `setup` 函数，定义于 `jupyterlite_sphinx/__init__.py:1`

## 模块级常量

F-007: `CONTENT_DIR = "_contents"`，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:40`
F-008: `JUPYTERLITE_DIR = "lite"`，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:41`
F-009: `HERE = Path(__file__).parent`，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:38`

## 工具函数

F-010: `skip(self, node)` 函数抛出 `SkipNode` 异常，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:45-46`
F-011: `visit_element_html(self, node)` 函数将 `node.html()` 追加到 `self.body` 后抛出 `SkipNode`，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:50-52`
F-012: `_build_options(lite_options: dict[str, str]) -> str` 函数将选项字典拼接为 URL 查询参数字符串，将 `showbanner` 替换为 `showBanner`，对值进行 URL 编码，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:55-68`
F-013: `search_params_parser(search_params: str) -> str` 函数解析 search_params 参数：接受 `True`/`False`/`["param1","param2"]` 格式，返回小写布尔或 JSON 数组字符串 `"false"`，非法值抛出 ValueError，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:1356-1368`

## HTML 节点类层次

### _PromptedIframe（基类节点）

F-014: `_PromptedIframe(Element)` 类，`__init__` 接受 rawsource, iframe_src, width, height, prompt, prompt_color, search_params 参数，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:71-92`
F-015: `_PromptedIframe.html()` 方法：当 `prompt` 为真值时生成带点击按钮的 div 容器（class=`jupyterlite_sphinx_iframe_container`），按钮默认文本 `"Try It Live!"`，默认颜色 `#f7dc1e`；否则生成普通 iframe（class=`jupyterlite_sphinx_raw_iframe`），定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:94-131`

### _InTab（新标签页按钮基类）

F-016: `_InTab(Element)` 类，`__init__` 接受 prefix, notebook, lite_options, button_text 参数，根据 notebook 是否存在构造 `self.lab_src` URL，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:134-161`
F-017: `_InTab.html()` 方法生成 `<button class="try_examples_button" onclick="window.open('...')">` 按钮，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:163-168`

### _LiteIframe（Lite iframe 节点）

F-018: `_LiteIframe(_PromptedIframe)` 类，`__init__` 额外接受 prefix, content, notebook, lite_options 参数；当 content 存在时将代码行（空行保留空串）拼接后存入 `lite_options["code"]`；当 notebook 存在时存入 `lite_options["path"]` 并设置 app_path，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:171-205`
F-019: `_LiteIframe.__init__` 对重复传入的 `iframe_src` 属性值进行一致性检查，不一致时抛出 ValueError 并提示升级 Sphinx 到 7.2.0+，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:198-203`

### 具体 iframe 节点类

F-020: `RepliteIframe(_LiteIframe)` 类，类属性 `lite_app = "repl/"`，`notebooks_path = ""`，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:208-215`
F-021: `JupyterLiteIframe(_LiteIframe)` 类，类属性 `lite_app = "lab/"`，`notebooks_path = ""`，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:218-225`
F-022: `NotebookLiteIframe(_LiteIframe)` 类，类属性 `lite_app = "tree/"`，`notebooks_path = "../notebooks/"`，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:338-345`

### Tab 节点类

F-023: `BaseNotebookTab(_InTab)` 类，类属性 `lite_app = None`，`notebooks_path = None`，`default_button_text = "Open as a notebook"`，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:228-234`
F-024: `JupyterLiteTab(BaseNotebookTab)` 类，`lite_app = "lab/"`，`notebooks_path = ""`，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:237-244`
F-025: `NotebookLiteTab(BaseNotebookTab)` 类，`lite_app = "tree/"`，`notebooks_path = "../notebooks/"`，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:247-254`
F-026: `RepliteTab(Element)` 类（不继承 _InTab），`lite_app = "repl/"`，`notebooks_path = ""`；`__init__` 独立处理 content→code 编码和 REPL 特定 URL 参数（execute, clearCellsOnExecute, clearCodeContentOnExecute, hideCodeInput, showBanner, promptCellPosition），其中 promptCellPosition 验证值在 {bottom, top, left, right} 集合内，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:260-335`

### Voici 节点类

F-027: `VoiciBase` 类，类属性 `lite_app = "voici/"`；类方法 `get_full_path(cls, notebook=None)`：notebook 存在时返回 `voici/render/{name}.html`，否则返回 `voici/tree`，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:348-360`
F-028: `VoiciIframe(_PromptedIframe)` 类，`__init__` 使用 `VoiciBase.get_full_path(notebook)` 构造 iframe_src，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:363-385`
F-029: `VoiciTab(Element)` 类（不继承 BaseNotebookTab），使用 `VoiciBase.get_full_path(notebook)` 构造 self.lab_src，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:390-425`

## Sphinx 指令类

### RepliteDirective

F-030: `RepliteDirective(SphinxDirective)` 类，`has_content = True`，`required_arguments = 0`，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:428-571`
F-031: `RepliteDirective.option_spec` 包含：width, height, kernel, execute, clear_cells_on_execute, clear_code_content_on_execute, hide_code_input, prompt_cell_position, show_banner, toolbar, theme, prompt, prompt_color, search_params, new_tab, new_tab_button_text, showbanner，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:436-454`
F-032: `RepliteDirective.run()` 方法：从 self.options 弹出 width/height/prompt/prompt_color/search_params；将 snake_case 选项映射为 camelCase URL 参数（execute, clearCellsOnExecute, clearCodeContentOnExecute, hideCodeInput, showBanner, promptCellPosition），布尔值转为 "0"/"1" 字符串；根据 new_tab 返回 RepliteTab 或 RepliteIframe 节点列表，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:456-571`
F-033: RepliteDirective 的 prefix 通过 `os.path.relpath` 从源文件位置计算到 JUPYTERLITE_DIR 的相对路径，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:533-536`

### _LiteDirective（笔记本嵌入基类指令）

F-034: `_LiteDirective(SphinxDirective)` 类，`has_content = False`，`optional_arguments = 1`，`final_argument_whitespace = True`，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:574-746`
F-035: `_LiteDirective.option_spec` 包含：width, height, theme, prompt, prompt_color, search_params, new_tab, new_tab_button_text，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:578-587`
F-036: `_LiteDirective._target_is_stale(source_path, target_path)` 方法：target 不存在返回 True，否则比较 source mtime > target mtime，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:589-595`
F-037: `_LiteDirective._strip_notebook_cells(nb)` 方法：返回 cells 列表的过滤结果，排除 metadata.tags 中含 `jupyterlite_sphinx_strip` 的单元格，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:597-620`
F-038: `_LiteDirective.run()` 方法：处理 self.arguments[0] 作为 notebook 路径；使用 `self.env.relfn2path()` 解析路径（绝对路径相对于文档根，相对路径相对于源文件），调用 `self.env.note_dependency()`；将路径添加到 `self.env.jupyterlite_notebooks` 集合；对 .md 文件使用 jupytext 转换为 .ipynb（需要 markdown 可选依赖）；对 .ipynb 文件根据 strip_tagged_cells 配置决定是否剥离单元格后复制；最终根据 new_tab 返回 self.newtab_cls 或 self.iframe_cls 实例，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:622-746`
F-039: _LiteDirective.run() 中 notebook 目标目录为 `Path(self.env.app.srcdir) / self.env.config.jupyterlite_content_dir`，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:659-661`

### 具体 Lite 指令类

F-040: `BaseJupyterViewDirective(_LiteDirective)` 类，定义 `iframe_cls = None` 和 `newtab_cls = None` 类属性供子类覆盖，option_spec 与 _LiteDirective 相同，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:749-766`
F-041: `JupyterLiteDirective(BaseJupyterViewDirective)` 类，`iframe_cls = JupyterLiteIframe`，`newtab_cls = JupyterLiteTab`，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:769-776`
F-042: `NotebookLiteDirective(BaseJupyterViewDirective)` 类，`iframe_cls = NotebookLiteIframe`，`newtab_cls = NotebookLiteTab`，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:779-786`
F-043: `VoiciDirective(BaseJupyterViewDirective)` 类，`iframe_cls = VoiciIframe`，`newtab_cls = VoiciTab`；`run()` 方法先检查 voici 是否为 None，若为 None 抛出 RuntimeError，然后调用 `super().run()`，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:789-804`

### NotebookLiteParser（.ipynb 源解析器）

F-044: `NotebookLiteParser(RSTParser)` 类，`supported = ("jupyterlite_notebook",)`，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:807-821`
F-045: `NotebookLiteParser.parse(inputstring, document)` 方法：提取文件名作为标题，将当前源路径转为相对于 srcdir 的绝对路径（以 `/` 开头），然后解析 RST 字符串 `f"{title}\n{'=' * len(title)}\n.. notebooklite:: {filename}"`，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:814-821`

### TryExamplesDirective

F-046: `TryExamplesDirective(SphinxDirective)` 类，`has_content = True`，`required_arguments = 0`，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:824-984`
F-047: `TryExamplesDirective.option_spec` 包含：height, theme, button_text, example_class, warning_text，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:829-835`
F-048: `TryExamplesDirective.run()` 方法：使用 `self.env.temp_data["generated_notebooks"]` 字典缓存已生成的 notebook（key 为 `{docname}-{lineno}`）；调用 `examples_to_notebook()` 将 content 转为 notebook JSON；支持通过 `try_examples_preamble` 配置插入预导入代码单元格；生成唯一 UUID 文件名（`{uuid4().replace('-', '_')}.ipynb`）保存到 jupyterlite_content_dir；生成包含 Try it 按钮、Go Back 按钮、Open In Tab 按钮的 HTML 容器和 iframe 容器；加载 try_examples.json 配置脚本，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:837-984`
F-049: TryExamplesDirective 使用 lite_app="tree/" 和 notebooks_path="../notebooks/" 构造 URL，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:873-874`

## Sphinx 事件处理函数

F-050: `_process_docstring_examples(app: Sphinx, docname: str, source: list[str])` 函数：当源文件后缀为 .py 时，调用 `insert_try_examples_directive(source[0])` 修改源码，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:987-990`
F-051: `_process_autodoc_docstrings(app, what, name, obj, options, lines)` 函数：从 app.config 读取 try_examples 全局配置，过滤掉 None 值后调用 `insert_try_examples_directive(lines, **options)` 替换 lines 内容，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:993-1004`
F-052: `conditional_process_examples(app, config)` 函数：当 `config.global_enable_try_examples` 为 True 时，连接 `source-read` 事件到 `_process_docstring_examples`，连接 `autodoc-process-docstring` 到 `_process_autodoc_docstrings`，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:1007-1010`
F-053: `inited(app: Sphinx, config)` 函数：验证 jupyterlite_content_dir 非空；`shutil.rmtree(content_dir, ignore_errors=True)` 清空内容目录后重建；当 jupyterlite_bind_ipynb_suffix 为 True 且 .ipynb 未注册为源后缀时，调用 `app.add_source_suffix(".ipynb", "jupyterlite_notebook")`，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:1013-1027`
F-054: `jupyterlite_ignore_contents_args(ignore_contents)` 函数：None 返回空列表，字符串转为单元素列表，为每个 pattern 生成 `["--ignore-contents", pattern]` 参数对，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:1030-1043`
F-055: `jupyterlite_build(app: Sphinx, error)` 函数：仅在 error 为 None 且 builder.format == "html" 时执行；构造 `jupyter lite build` 命令行：包含 --debug, --config, --settings-overrides, --contents（展开 glob）, --ignore-contents, --output-dir, --apps, --lite-dir；apps 默认包含 notebooks, edit, lab, repl, tree, consoles，voici 可用时追加 voici；执行 subprocess.run()；构建完成后删除 `.jupyterlite.doit.db` 文件，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:1046-1210`
F-056: jupyterlite_build 中目录内容处理：glob 匹配到目录时使用 `shutil.copytree` 复制到 _contents 目录下保留目录名；匹配到文件时直接传递 --contents 参数，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:1102-1121`
F-057: jupyterlite_build 中 jupyterlite_silence 为 True（默认）时将 stdout/stderr 设为 PIPE，构建失败时打印捕获的输出，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:1173-1202`
F-058: jupyterlite_build 禁止通过 jupyterlite_build_command_options 覆盖 contents/output-dir/lite-dir 三个选项，违反时抛出 RuntimeError，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:1154-1167`
F-059: jupyterlite_build 中 jupyterlite_overrides 路径会验证文件存在性（相对于 app.srcdir），不存在时抛出 FileNotFoundError，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:1072-1078`

## setup() 函数注册

F-060: `setup(app)` 调用 `app.add_source_parser(NotebookLiteParser)`，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:1215`
F-061: `setup(app)` 连接事件：`config-inited` → `inited`，`build-finished` → `jupyterlite_build`，`config-inited` → `conditional_process_examples`，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:1217-1219,1337`
F-062: `setup(app)` 通过 `app.add_config_value()` 注册 JupyterLite 核心配置项：jupyterlite_config(default=None), jupyterlite_overrides(default=None), jupyterlite_dir(default=str(app.srcdir)), jupyterlite_contents(default=None), jupyterlite_ignore_contents(default=None), jupyterlite_bind_ipynb_suffix(default=True), jupyterlite_silence(default=True), strip_tagged_cells(default=False), jupyterlite_build_command_options(default=None)，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:1222-1232`
F-063: `setup(app)` 注册 TryExamples 配置：global_enable_try_examples(default=False), try_examples_global_theme(default=None), try_examples_global_warning_text(default=None), try_examples_global_button_text(default=None), try_examples_preamble(default=None), jupyterlite_content_dir(default=CONTENT_DIR)，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:1234-1243`
F-064: `setup(app)` 注册按钮文本配置：jupyterlite_new_tab_button_text(default="Open as a notebook"), notebooklite_new_tab_button_text(default="Open as a notebook"), voici_new_tab_button_text(default="Open with Voici"), replite_new_tab_button_text(default="Open in a REPL")，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:1247-1256`
F-065: `setup(app)` 注册 REPL 配置：replite_auto_execute(default=True), replite_clear_cells_on_execute(default=False), replite_clear_code_content_on_execute(default=False), replite_hide_code_input(default=False), replite_prompt_cell_position(default="bottom"), replite_show_banner(default=True)，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:1259-1264`
F-066: `setup(app)` 通过 `app.add_node()` 注册所有自定义节点（NotebookLiteIframe, JupyterLiteIframe, NotebookLiteTab, JupyterLiteTab, RepliteIframe, RepliteTab, VoiciIframe, VoiciTab），HTML 访问器为 `visit_element_html`，非 HTML 格式（latex/textinfo/text/man）使用 `skip`，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:1267-1332`
F-067: `setup(app)` 通过 `app.add_directive()` 注册指令：notebooklite（retrolite 作为别名指向同一类）, jupyterlite, replite, voici, try_examples，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:1275-1336`
F-068: `setup(app)` 使用 `copy_asset()` 将 jupyterlite_sphinx.css 和 jupyterlite_sphinx.js 复制到输出目录的 `_static/` 子目录，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:1340-1341`
F-069: `setup(app)` 注册 CSS/JS：添加 Google Fonts Vibur 字体 CSS，添加 jupyterlite_sphinx.css，添加 jupyterlite_sphinx.js，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:1343-1346`
F-070: `setup(app)` 检查 srcdir 下是否存在 `try_examples.json`，存在则 copy_asset 到输出目录，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:1349-1351`
F-071: `setup(app)` 返回 `{"parallel_read_safe": True}`，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:1353`

## _try_examples.py 模块

F-072: `examples_to_notebook(input_lines, *, warning_text=None)` 函数：解析 doctest 格式行列表，返回 nbformat.v4 notebook JSON 字典；warning_text 不为 None 时在顶部添加带 `alert alert-warning` class 的 Markdown 警告单元格，定义于 `jupyterlite_sphinx/_try_examples.py:7-124`
F-073: examples_to_notebook 解析规则：`>>>` 开头行为代码行（去除前缀），`...` 开头且在代码块中为续行，空行结束代码块，非空非前缀行在代码块后为输出文本，其余行为 Markdown 文本，定义于 `jupyterlite_sphinx/_try_examples.py:66-112`
F-074: examples_to_notebook 忽略 `.. plot::` 和 `.. only::` 指令及其缩进内容，定义于 `jupyterlite_sphinx/_try_examples.py:63-77`
F-075: examples_to_notebook 输出 notebook metadata：kernelspec display_name="Python", language="python", name="python"；language_info name="python"，定义于 `jupyterlite_sphinx/_try_examples.py:114-123`
F-076: `_append_code_cell_and_clear_lines(code_lines, output_lines, notebook)` 函数：拼接 code_lines 为代码文本创建 new_code_cell，若 output_lines 非空则添加 execute_result 类型 output（data={"text/plain": combined_output}），追加到 notebook.cells 后清空两个列表，定义于 `jupyterlite_sphinx/_try_examples.py:127-141`
F-077: `_append_markdown_cell_and_clear_lines(markdown_lines, notebook)` 函数：拼接 markdown_lines，依次调用 _process_latex、_process_literal_blocks、_strip_ref_identifiers、_convert_links 处理，创建 new_markdown_cell 追加后清空列表，定义于 `jupyterlite_sphinx/_try_examples.py:144-152`
F-078: `_convert_links(md_text)` 函数：使用正则 `` `(?P<link_text>[^`<]+)<(?P<url>[^`>]+)>`_ `` 将 Sphinx 风格链接转换为 Markdown 格式 `[link_text](url)`，定义于 `jupyterlite_sphinx/_try_examples.py:159-171`
F-079: `_strip_ref_identifiers(md_text)` 函数：使用正则 `\[R[a-f0-9]+-(?P<ref_num>\d+)\]_` 匹配 Sphinx 引用标识符，替换为 `[\g<ref_num>]`，定义于 `jupyterlite_sphinx/_try_examples.py:174-183`
F-080: `_process_latex(md_text)` 函数：将 `:math:`...`` 替换为 `$...$`；将 `.. math::` 指令块（后续缩进行）替换为 `$$ ... $$` 块级公式，定义于 `jupyterlite_sphinx/_try_examples.py:186-225`
F-081: `_process_literal_blocks(md_text)` 函数：将 RST `::` 开头的 literal block（后续缩进行）转换为 Markdown ```` ``` ```` 围栏代码块，定义于 `jupyterlite_sphinx/_try_examples.py:228-269`
F-082: `_examples_start_pattern = re.compile(r".. (rubric|admonition):: Examples")`，匹配 numpydoc/napoleon 处理后的 Examples 节标题，定义于 `jupyterlite_sphinx/_try_examples.py:284`
F-083: `_next_section_headers` 列表包含 numpydoc 和 sphinx.ext.napoleon 可能生成的各种节标题正则（Notes, References, Attributes, Methods, Parameters, Returns 等），定义于 `jupyterlite_sphinx/_try_examples.py:292-330`
F-084: `_next_section_pattern = re.compile("|".join(_next_section_headers))`，定义于 `jupyterlite_sphinx/_try_examples.py:331`
F-085: `insert_try_examples_directive(lines, **options)` 函数：在处理后的 docstring lines 中查找 Examples 节起始位置；跳过空行后检查首行是否为 `.. disable_try_examples`（禁用）或已有 `.. try_examples::`（跳过）；查找节结束位置（下一节标题或文档结束）；在 Examples 内容前插入 `.. try_examples::` 指令和选项行，将内容缩进 4 空格，定义于 `jupyterlite_sphinx/_try_examples.py:334-416`

## 前端 JavaScript（jupyterlite_sphinx.js）

F-086: `window.jupyterliteShowIframe(tryItButtonId, iframeSrc)` 函数：隐藏按钮，创建 50x50 spinner（class=`jupyterlite_sphinx_spinner`）和 100% 宽高 iframe（class=`jupyterlite_sphinx_iframe`），追加到按钮父节点，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.js:1-25`
F-087: `window.jupyterliteConcatSearchParams(iframeSrc, params)` 函数：基于当前页面 URL 创建 URL 对象；params 为 true 时传递所有页面搜索参数，为数组时传递指定参数，为 false 时不传；将选中的参数 append 到 iframe URL，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.js:27-53`
F-088: `window.tryExamplesShowIframe(examplesContainerId, iframeContainerId, iframeParentContainerId, iframeSrc, iframeHeight)` 函数：隐藏 examples 内容（添加 hidden class），显示 iframe 容器（移除 hidden class）；首次调用时创建 spinner 和 iframe，iframe 高度取 max(tryExamplesGlobalMinHeight, examples.offsetHeight) 或指定值；spinner 位置根据视口计算，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.js:55-113`
F-089: `window.tryExamplesHideIframe(examplesContainerId, iframeParentContainerId)` 函数：隐藏 iframe 父容器（添加 hidden class），显示 examples 内容（移除 hidden class），定义于 `jupyterlite_sphinx/jupyterlite_sphinx.js:115-126`
F-090: `window.openInNewTab(examplesContainerId, iframeParentContainerId)` 函数：获取 iframe 的 src 属性，window.open 打开新标签页，然后调用 tryExamplesHideIframe 切回 examples 视图，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.js:130-142`
F-091: `var tryExamplesGlobalMinHeight = 0` 全局变量，可通过 try_examples.json 的 global_min_height 配置修改，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.js:146`
F-092: `var tryExamplesConfigLoaded = false` 全局变量，防止配置重复加载，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.js:150`
F-093: `window.isMobileDevice` 为 IIFE 实现的单例检测函数：使用 14 种移动设备 UA 正则模式检测 + 屏幕尺寸兜底（宽或高 ≤480px）；检测到移动设备时隐藏所有 try_examples_button 并 console.log 提示，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.js:155-201`
F-094: `ConfigLoader` 为 IIFE 模块，提供 `loadConfig(configFilePath)` 方法：先检查 isMobileDevice 直接隐藏按钮返回；使用 Promise 去重（同一时刻多个指令共享同一个请求）；fetch 配置文件（添加时间戳 cb 参数防缓存）；解析 JSON 设置 global_min_height 和按 ignore_patterns 正则隐藏匹配页面的按钮；提供 resetState() 方法仅供测试/调试，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.js:204-290`
F-095: window resize 事件监听器（250ms debounce）：配置加载完成后，根据 isMobileDevice() 结果切换按钮 hidden class，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.js:294-311`
F-096: `window.loadTryExamplesConfig = ConfigLoader.loadConfig`，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.js:313`
F-097: `window.toggleTryExamplesButtons()` 函数：切换所有 try_examples_button 的 hidden class，供控制台调试使用，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.js:315-323`

## 条件导入

F-098: `try: import jupytext except ImportError: jupytext = None`，jupytext 为可选依赖用于 Markdown notebook 支持，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:28-31`
F-099: `try: import voici except ImportError: voici = None`，voici 为可选依赖用于 Voici dashboard 指令，定义于 `jupyterlite_sphinx/jupyterlite_sphinx.py:33-36`
