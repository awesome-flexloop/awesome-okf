---
okf_version: '0.2'
generated: '2026-08-22'
tags:
- jupyter
- nbconvert
- notebook
- converter
- template
sources:
- ../../../../../external/libs/jupyter/nbconvert/pyproject.toml
- ../../../../../external/libs/jupyter/nbconvert/nbconvert/__init__.py
- ../../../../../external/libs/jupyter/nbconvert/share/templates/lab/conf.json
type: Facts
title: nbconvert 源码事实清单
---

# nbconvert Facts

## 项目元数据与构建

- F-001: pyproject.toml:6 — 包名为 "nbconvert"，作者为 Jupyter Development Team
- F-002: pyproject.toml:9 — 包描述为 "Convert Jupyter Notebooks (.ipynb files) to other formats."
- F-003: pyproject.toml:21 — 要求 Python 版本 >=3.9
- F-004: pyproject.toml:2 — 使用 hatchling >=1.5 作为构建后端
- F-005: pyproject.toml:22-38 — 核心依赖包括 beautifulsoup4、bleach、defusedxml、jinja2>=3.0、jupyter_core>=4.7、jupyterlab_pygments、mistune>=2.0.3、nbclient>=0.5.0、nbformat>=5.7、packaging、pandocfilters>=1.4.1、pygments>=2.4.1、traitlets>=5.1
- F-006: pyproject.toml:41-55 — 通过 entry_points "nbconvert.exporters" 注册 14 个导出器：custom、html、slides、latex、pdf、qtpdf、qtpng、webpdf、markdown、python、rst、notebook、asciidoc、script
- F-007: pyproject.toml:80-82 — 提供两个命令行入口：jupyter-nbconvert（主入口）和 jupyter-dejavu
- F-008: pyproject.toml:91-94 — sdist 构建包含 share/templates 和 tests/；wheel 安装时将 share/templates 映射到 share/jupyter/nbconvert/templates

## 包结构与初始化

- F-009: nbconvert/__init__.py:1 — 模块 docstring 为 "Utilities for converting notebooks to and from different formats."
- F-010: nbconvert/__init__.py:6-7 — 顶层导出 filters、postprocessors、preprocessors、writers 子模块
- F-011: nbconvert/__init__.py:7-28 — 导出 16 个 Exporter 类：ASCIIDocExporter、Exporter、HTMLExporter、LatexExporter、MarkdownExporter、NotebookExporter、PDFExporter、PythonExporter、QtPDFExporter、QtPNGExporter、RSTExporter、ScriptExporter、SlidesExporter、TemplateExporter、WebPDFExporter
- F-012: nbconvert/__init__.py:25-27 — 导出三个工厂函数：export、get_export_names、get_exporter
- F-013: nbconvert/__init__.py:29-31 — 使用 try/except ModuleNotFoundError 处理未完全安装时的导入失败

## Exporter 基类架构

- F-014: exporters/exporter.py:51 — Exporter 类继承自 LoggingConfigurable（traitlets 配置体系）
- F-015: exporters/exporter.py:24-29 — ResourcesDict 类继承自 collections.defaultdict，__missing__ 方法返回空字符串
- F-016: exporters/exporter.py:32-48 — FilenameExtension 是自定义 Unicode trait，验证值必须以点号开头
- F-017: exporters/exporter.py:58-60 — Exporter.enabled 为 Bool trait，可通过配置禁用导出器
- F-018: exporters/exporter.py:62-64 — Exporter.file_extension 为 FilenameExtension 类型，配置输出文件扩展名
- F-019: exporters/exporter.py:66-69 — Exporter.optimistic_validation 为 Bool trait，控制是否在所有 preprocessor 运行后才做验证
- F-020: exporters/exporter.py:74 — Exporter.output_mimetype 为类属性字符串（非 trait），用于 HTTP 响应头
- F-021: exporters/exporter.py:78 — Exporter.export_from_notebook 为类属性，标记是否可从 notebook 前端直接导出
- F-022: exporters/exporter.py:81-83 — Exporter.preprocessors 为 List trait，用户可配置启用的 preprocessor 列表
- F-023: exporters/exporter.py:87-103 — Exporter.default_preprocessors 列出 11 个默认 preprocessor：TagRemovePreprocessor、RegexRemovePreprocessor、ClearOutputPreprocessor、CoalesceStreamsPreprocessor、ExecutePreprocessor、SVG2PDFPreprocessor、LatexPreprocessor、HighlightMagicsPreprocessor、ExtractOutputPreprocessor、ExtractAttachmentsPreprocessor、ClearMetadataPreprocessor
- F-024: exporters/exporter.py:123 — __init__ 中调用 _init_preprocessors() 初始化 preprocessor 管道
- F-025: exporters/exporter.py:130-161 — from_notebook_node() 方法：深拷贝 notebook → 初始化 resources → 提取 language 元数据 → 调用 _preprocess() → 返回 (nb_copy, resources)
- F-026: exporters/exporter.py:163-201 — from_filename() 方法：从文件路径读取 notebook，设置 metadata.name/path/modified_date，调用 from_file()
- F-027: exporters/exporter.py:203-222 — from_file() 方法：使用 nbformat.read(as_version=4) 读取文件流，委托给 from_notebook_node()
- F-028: exporters/exporter.py:224-279 — register_preprocessor() 方法支持四种注册方式：字符串（import_item 导入）、callable（函数）、HasTraits 子类（实例化并传入 parent=self）、普通类（直接实例化）
- F-029: exporters/exporter.py:281-294 — _init_preprocessors()：先注册 default_preprocessors（默认禁用），再注册用户指定的 preprocessors（默认启用）
- F-030: exporters/exporter.py:296-318 — _init_resources()：确保 resources 为 ResourcesDict 类型，初始化 metadata 子字典，设置 output_extension
- F-031: exporters/exporter.py:327-359 — _preprocess()：深拷贝 nb 和 resources，依次调用每个已启用 preprocessor，每次调用后可选验证 notebook 有效性
- F-032: exporters/exporter.py:320-325 — _validate_preprocessor() 使用 nbformat.validate(relax_add_props=True) 验证 notebook

## TemplateExporter 模板引擎

- F-033: exporters/templateexporter.py:139 — TemplateExporter 继承自 Exporter，是基于 Jinja2 的高度可配置导出器
- F-034: exporters/templateexporter.py:36 — JINJA_EXTENSIONS 加载 "jinja2.ext.loopcontrols" 扩展
- F-035: exporters/templateexporter.py:39 — DEV_MODE 通过检测 ../../.git 目录判断开发模式
- F-036: exporters/templateexporter.py:42-80 — default_filters 字典定义 38 个默认 Jinja filter：indent、markdown2html、markdown2asciidoc、ansi2html、filter_data_type、get_lines、highlight2html、highlight2latex、ipython2python、posix_path、markdown2latex、markdown2rst、comment_lines、strip_ansi、strip_dollars、strip_files_prefix、html2text、add_anchor、ansi2latex、wrap_text、escape_latex、citation2latex、path2url、add_prompts、ascii_only、prevent_list_blocks、get_metadata、convert_pandoc、json_dumps、escape_html、escape_html_keep_quotes、escape_html_script、clean_html、strip_trailing_newline、text_base64
- F-037: exporters/templateexporter.py:84-102 — recursive_update() 函数递归合并字典，None 值删除对应键，空字典自动清理
- F-038: exporters/templateexporter.py:111-136 — ExtensionTolerantLoader 包装 Jinja Loader，模板查找失败时自动追加扩展名重试
- F-039: exporters/templateexporter.py:160-169 — 使用 _template_cached 缓存 Jinja Template 对象，通过 _invalidate_template_cache() 失效
- F-040: exporters/templateexporter.py:171-181 — 使用 _environment_cached 缓存 Jinja Environment 对象，trait 变化时自动失效
- F-041: exporters/templateexporter.py:184-195 — default_config 预启用 RegexRemovePreprocessor 和 TagRemovePreprocessor
- F-042: exporters/templateexporter.py:197-199 — template_name 为 Unicode trait（config=True），指定使用的模板目录名
- F-043: exporters/templateexporter.py:201-203 — template_file 为 Unicode trait（config=True），指定模板文件名
- F-044: exporters/templateexporter.py:205 — raw_template 为 Unicode trait，支持直接传入模板字符串
- F-045: exporters/templateexporter.py:207-209 — enable_async 为 Bool trait，控制 Jinja 异步模板执行
- F-046: exporters/templateexporter.py:262-264 — 定义三个模板路径 List trait：template_paths（默认 ["."]）、extra_template_basedirs、extra_template_paths
- F-047: exporters/templateexporter.py:271 — template_extension 为 Unicode trait，模板文件扩展名
- F-048: exporters/templateexporter.py:273-275 — template_data_paths 使用 jupyter_path("nbconvert", "templates") 获取 Jupyter 数据路径中的模板
- F-049: exporters/templateexporter.py:277-281 — _template_extension_default：file_extension 存在时返回 file_extension + ".j2"
- F-050: exporters/templateexporter.py:283-319 — 提供 9 个内容过滤 Bool trait：exclude_input、exclude_input_prompt、exclude_output、exclude_output_prompt、exclude_output_stdin（默认 True）、exclude_code_cell、exclude_markdown、exclude_raw、exclude_unknown
- F-051: exporters/templateexporter.py:321-324 — extra_loaders 为 List trait，允许插入自定义 Jinja Loader
- F-052: exporters/templateexporter.py:326-329 — filters 为 Dict trait（config=True），用户可添加自定义 Jinja filter
- F-053: exporters/templateexporter.py:331-337 — raw_mimetypes 为 List trait，默认包含 output_mimetype 和空字符串
- F-054: exporters/templateexporter.py:356-359 — __init__ 中使用 observe() 监听 affects_environment 和 affects_template 的 trait 变化，自动失效缓存
- F-055: exporters/templateexporter.py:361-384 — _load_template()：raw_template 优先于 template_file，通过 environment.get_template() 加载模板
- F-056: exporters/templateexporter.py:398-431 — from_notebook_node()：调用父类预处理后设置 global_content_filter 字典，通过 self.template.render(nb=nb_copy, resources=resources) 渲染输出
- F-057: exporters/templateexporter.py:433-479 — _register_filter() 支持四种 filter 注册方式：字符串导入、callable、HasTraits 实例、普通类实例
- F-058: exporters/templateexporter.py:507-536 — _create_environment()：构建 ChoiceLoader（extra_loaders + ExtensionTolerantLoader(FileSystemLoader) + DictLoader），创建 Jinja Environment，注册默认和用户 filter
- F-059: exporters/templateexporter.py:538-554 — _init_preprocessors()：从 conf.json 读取 preprocessor 配置，按数字前缀排序后注册
- F-060: exporters/templateexporter.py:556-569 — _get_conf()：遍历 template_paths 读取 conf.json 文件，使用 recursive_update 合并配置
- F-061: exporters/templateexporter.py:571-610 — _template_paths()：按 template_name 继承链收集模板目录，包含 root_dir、base_dir、compatibility_dir 三种路径
- F-062: exporters/templateexporter.py:622-678 — get_template_names()：沿 base_template 链递归查找模板目录，支持 5.x .tpl 兼容模板
- F-063: exporters/templateexporter.py:680-688 — get_prefix_root_dirs()：开发模式优先使用本地 share/jupyter 路径，然后追加 jupyter_path()
- F-064: exporters/templateexporter.py:214-228 — _template_name_validate()：检测 .tpl 后缀的旧模板名，发出 DeprecationWarning 并自动拆分路径

## Preprocessor 体系

- F-065: preprocessors/base.py:11 — Preprocessor 类继承自 NbConvertBase
- F-066: preprocessors/base.py:28 — Preprocessor.enabled 默认 False（禁用状态），需配置启用
- F-067: preprocessors/base.py:44-49 — __call__() 方法：若 enabled 为 True 则调用 preprocess()，否则原样返回 (nb, resources)
- F-068: preprocessors/base.py:51-70 — preprocess() 默认实现遍历 nb.cells，对每个 cell 调用 preprocess_cell()
- F-069: preprocessors/base.py:72-88 — preprocess_cell() 为抽象方法，子类必须实现，否则抛出 NotImplementedError
- F-070: preprocessors/ 目录包含 15 个预处理器：base、clearmetadata、clearoutput、coalescestreams、convertfigures、csshtmlheader、execute、extractattachments、extractoutput、highlightmagics、latex、regexremove、sanitize、svg2pdf、tagremove

## 导出器注册与工厂

- F-071: exporters/__init__.py:1-16 — 导入 13 个具体 Exporter 类及工厂函数
- F-072: exporters/base.py:33-38 — 定义两个异常类：ExporterNameError(NameError) 和 ExporterDisabledError(ValueError)
- F-073: exporters/base.py:41-91 — export() 工厂函数：接受 Exporter 类/实例，支持 NotebookNode/文件名/文件流输入
- F-074: exporters/base.py:94-129 — get_exporter()：先查 entry_points，再尝试 import_item 导入点分路径，检查 enabled 状态
- F-075: exporters/base.py:103-104 — "ipynb" 别名自动映射到 "notebook" 导出器
- F-076: exporters/base.py:132-157 — get_export_names()：遍历 entry points 并过滤 enabled 的导出器；NBCONVERT_DISABLE_CONFIG_EXPORTERS 环境变量可禁用配置加载

## Writer 与 Postprocessor

- F-077: writers/base.py:14 — WriterBase 继承自 NbConvertBase
- F-078: writers/base.py:18-23 — WriterBase.files 为 List trait，记录 notebook 引用的文件列表
- F-079: writers/base.py:31-46 — WriterBase.write() 为抽象方法，子类实现输出写入逻辑
- F-080: writers/ 目录包含 4 个 writer：base、debug、files、stdout
- F-081: postprocessors/ 目录包含 3 个模块：base、serve（Tornado 服务后处理器）

## CLI 应用

- F-082: nbconvertapp.py:193 — NbConvertApp 继承自 JupyterApp，是命令行主应用
- F-083: nbconvertapp.py:51-67 — nbconvert_aliases 定义命令行短选项映射：--to、--template、--template-file、--theme、--sanitize_html、--writer、--post、--output、--output-dir、--reveal-prefix、--nbformat
- F-084: nbconvertapp.py:69-189 — nbconvert_flags 定义 14 个命令行 flag：--execute、--allow-errors、--stdin、--stdout、--inplace、--clear-output、--coalesce-streams、--no-prompt、--no-input、--allow-chromium-download、--disable-chromium-sandbox、--show-input、--embed-images、--sanitize-html

## Filter 系统

- F-085: filters/__init__.py:1-35 — 从各子模块导入 30+ 个 filter 函数/类
- F-086: filters/ 目录包含 11 个模块：ansi、citation、datatypefilter、filter_links、highlight、latex、markdown、markdown_mistune、metadata、pandoc、strings、widgetsdatatypefilter

## 内置模板

- F-087: share/templates/ 目录包含 12 个内置模板：asciidoc、base、basic、classic、compatibility、lab、latex、markdown、python、reveal、rst、script、webpdf
- F-088: share/templates/lab/conf.json:2 — lab 模板继承自 base 模板
- F-089: share/templates/lab/conf.json:3-5 — lab 模板支持 text/html mimetype
- F-090: share/templates/lab/conf.json:6-11 — lab 模板通过 conf.json 启用 CSSHTMLHeaderPreprocessor（100-pygments）
- F-091: share/templates/base/ 目录包含 6 个基础 Jinja 片段：cell_id_anchor.j2、celltags.j2、display_priority.j2、jupyter_widgets.html.j2、mathjax.html.j2、null.j2
- F-092: share/templates/latex/ 目录包含 10 个 LaTeX 模板文件，支持 report/article 风格和多种代码高亮样式
- F-093: share/templates/reveal/ 目录包含 reveal.js 幻灯片模板及 custom_reveal.css
- F-094: share/templates/ 模板文件统一使用 .j2 扩展名（Jinja2）

## 工具模块

- F-095: utils/ 目录包含 8 个模块：_contextlib_chdir、base、exceptions、io、iso639_1、lexers、pandoc、text、version
- F-096: utils/exceptions.py 定义 ConversionException 等异常类
- F-097: utils/pandoc.py 处理 Pandoc 集成逻辑

## Exporter 具体实现

- F-098: exporters/html.py — HTMLExporter 实现 HTML 导出，支持 theme 和 sanitize_html
- F-099: exporters/latex.py — LatexExporter 实现 LaTeX 导出
- F-100: exporters/pdf.py — PDFExporter 通过 LaTeX 生成 PDF
- F-101: exporters/webpdf.py — WebPDFExporter 通过 Playwright/Chromium 生成 PDF
- F-102: exporters/slides.py — SlidesExporter 生成 reveal.js 幻灯片
- F-103: exporters/markdown.py — MarkdownExporter 导出 Markdown
- F-104: exporters/python.py — PythonExporter 导出 Python 脚本
- F-105: exporters/notebook.py — NotebookExporter 导出 .ipynb 格式
- F-106: exporters/asciidoc.py — ASCIIDocExporter 导出 AsciiDoc
- F-107: exporters/rst.py — RSTExporter 导出 reStructuredText
- F-108: exporters/script.py — ScriptExporter 为脚本导出基类
- F-109: exporters/qt_exporter.py、qt_screenshot.py、qtpdf.py、qtpng.py — Qt 相关导出器，依赖 pyqtwebengine
