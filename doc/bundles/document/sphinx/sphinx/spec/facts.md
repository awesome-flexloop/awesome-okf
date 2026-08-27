# Sphinx 源码事实清单

> R阶段产出：从零推测的源码采集事实，编号F-xxx。

## 版本与位置

- F-001: Sphinx版本为9.1.1(beta)，`__version__ = '9.1.1'`，`version_info = (9, 1, 1, 'beta', 0)`，位于sphinx/__init__.py
- F-002: 源码根包目录为`sphinx/`，核心模块直接位于该包下

## 核心类：Sphinx (application.py)

- F-003: Sphinx类定义在sphinx/application.py，是主应用类和扩展接口
- F-004: Sphinx类的路径属性：srcdir、confdir、outdir、doctreedir，均为_StrPathProperty类型
- F-005: Sphinx.__init__参数：srcdir, confdir(可选,默认同srcdir), outdir, doctreedir, buildername, confoverrides(可选), status(默认sys.stdout), warning(默认sys.stderr), freshenv(默认False), warningiserror(默认False), tags(默认()), verbosity(默认0), parallel(默认0), keep_going(默认False), pdb(默认False), exception_on_warning(默认False)
- F-006: Sphinx.extensions类型为dict[str, Extension]，存储已加载扩展
- F-007: Sphinx.registry类型为SphinxComponentRegistry实例
- F-008: Sphinx.events类型为EventManager实例
- F-009: Sphinx.config类型为Config实例
- F-010: Sphinx.env类型为BuildEnvironment实例
- F-011: Sphinx.builder类型为Builder实例
- F-012: Sphinx.project类型为Project实例
- F-013: Sphinx.tags类型为Tags实例

## 初始化流程 (Sphinx.__init__)

- F-014: 初始化顺序：设置verbosity→创建extensions字典→创建registry→验证目录(srcdir必须存在,outdir不能是文件,srcdir≠outdir)→设置parallel→设置status/warning IO→设置日志→创建EventManager→读取Config→初始化i18n→检查needs_sphinx版本→加载builtin_extensions→加载用户extensions(config.extensions)→preload_builder→创建输出目录→执行config.setup(如果是callable)→emit('config-inited', config)→创建Project→初始化BuildEnvironment→创建Builder→post_init_env→初始化Builder
- F-015: ENV_PICKLE_FILENAME常量值为'environment.pickle'
- F-016: 环境初始化逻辑：freshenv=True或pickle文件不存在时_create_fresh_env()，否则尝试_load_existing_env()，失败则回退到fresh
- F-017: Config.read(confdir, overrides, tags)从conf.py读取配置

## 内置扩展列表 (builtin_extensions)

- F-018: builtin_extensions是一个tuple，包含sphinx.addnodes, sphinx.builders.changes/dirhtml/dummy/epub3/gettext/html/latex/linkcheck/manpage/singlehtml/texinfo/text/xml, sphinx.config, sphinx.domains.c/changeset/citation/cpp/index/javascript/math/python/rst/std, sphinx.directives, sphinx.directives.admonitions/code/other/patches, sphinx.extension, sphinx.parsers, sphinx.registry, sphinx.roles, sphinx.transforms, sphinx.transforms.compact_bullet_list/i18n/references/post_transforms/post_transforms.code/post_transforms.images, sphinx.versioning, sphinx.environment.collectors.dependencies/asset/metadata/title/toctree
- F-019: _first_party_extensions: sphinxcontrib.applehelp, sphinxcontrib.devhelp, sphinxcontrib.htmlhelp, sphinxcontrib.serializinghtml, sphinxcontrib.qthelp
- F-020: _first_party_themes: alabaster（作为默认主题自动加载）

## 事件系统 (events.py)

- F-021: EventManager类定义在sphinx/events.py
- F-022: EventManager.__init__(app)接收Sphinx实例，初始化events=core_events.copy(), listeners=defaultdict(list), next_listener_id=0
- F-023: EventListener是NamedTuple，字段为id(int), handler(Callable), priority(int)
- F-024: EventManager.add(name)注册自定义事件，重复注册抛ExtensionError
- F-025: EventManager.connect(name, callback, priority)注册监听器，返回listener_id，回调按priority升序调用
- F-026: EventManager.disconnect(listener_id)移除监听器
- F-027: EventManager.emit(name, *args, allowed_exceptions)触发事件，返回所有回调返回值的list；异常处理：allowed_exceptions透传，SphinxError直接抛出，其他异常包装为ExtensionError
- F-028: EventManager.emit_firstresult(name, *args, allowed_exceptions)触发事件并返回第一个非None结果
- F-029: core_events字典定义17个核心事件：config-inited(config), builder-inited(), env-get-outdated(env,added,changed,removed), env-before-read-docs(env,docnames), env-purge-doc(env,docname), source-read(docname,source_text), include-read(relative_path,parent_docname,source_text), doctree-read(doctree), env-merge-info(env,read_docnames,other_env), env-updated(env), env-get-updated(env), env-check-consistency(env), write-started(builder), doctree-resolved(doctree,docname), missing-reference(env,node,contnode), warn-missing-reference(domain,node), build-finished(exception)
- F-030: HTML构建器事件：html-collect-pages(), html-page-context(pagename,templatename,ctx,doctree), linkcheck-process-uri(uri)
- F-031: autodoc事件：autodoc-process-docstring, autodoc-before-process-signature, autodoc-process-signature, autodoc-process-bases, autodoc-skip-member

## 配置系统 (config.py)

- F-032: Config类定义在sphinx/config.py，CONFIG_FILENAME='conf.py'
- F-033: ConfigValue是NamedTuple(name, value, rebuild)
- F-034: _Opt类使用__slots__：default, rebuild, valid_types, description；immutable设计
- F-035: _ConfigRebuild字面量类型：'', 'env', 'epub', 'gettext', 'html', 'applehelp', 'devhelp'
- F-036: ENUM类用于枚举值验证，__init__(*candidates)，match(value)检查值是否在候选集中
- F-037: Config.add(name, default, rebuild, types, description)注册配置值；default为callable时会以config为参数调用获取动态默认值
- F-038: UNSERIALIZABLE_TYPES = (type, types.ModuleType, types.FunctionType)

## 扩展类 (extension.py)

- F-039: Extension类定义在sphinx/extension.py，__init__(name, module, **kwargs)
- F-040: Extension属性：name, module, metadata(ExtensionMetadata类型即kwargs), version(默认'unknown version'), parallel_read_safe(默认None), parallel_write_safe(默认True)
- F-041: 扩展模块必须实现setup(app)函数，返回字典含version/parallel_read_safe/parallel_write_safe
- F-042: verify_needs_extensions(app, config)检查needs_extensions中指定的扩展版本要求

## 组件注册表 (registry.py)

- F-043: SphinxComponentRegistry类定义在sphinx/registry.py
- F-044: 注册表维护的字典属性：autodoc_attrgetters, builders(dict[str,type[Builder]]), documenters, css_files(list[tuple[str,dict]]), domains(dict[str,type[Domain]]), domain_directives, domain_indices, domain_object_types, domain_roles, enumerable_nodes, html_inline_math_renderers, html_block_math_renderers, html_themes, js_files(list[tuple[str|None,dict]]), static_dirs, latex_packages, latex_packages_after_hyperref, post_transforms(list[type[Transform]]), source_parsers(dict[str,type[Parser]]), source_suffix(dict[str,str]), translators, translation_handlers, transforms(list[type[Transform]])
- F-045: add_builder(builder, override)注册构建器，builder必须有name属性
- F-046: create_builder(app, name, env)实例化构建器：buildersname
- F-047: preload_builder通过entry_points(group='sphinx.builders')发现第三方builder
- F-048: load_extension(app, extname)通过import_module加载扩展模块，调用setup(app)
- F-049: EXTENSION_BLACKLIST字典记录已废弃的扩展名及合并版本

## 构建器基类 (builders/__init__.py)

- F-050: Builder类定义在sphinx/builders/__init__.py
- F-051: Builder类属性：name(ClassVar[str],用于CLI选择), format(ClassVar[str],输出格式/扩展名), epilog(ClassVar[str],完成消息模板), default_translator_class, versioning_method(默认'none'), versioning_compare(默认False), allow_parallel(默认False), use_message_catalog(默认True), supported_image_types(list[str]), supported_remote_images(默认False), supported_data_uri_images(默认False), phase(BuildPhase)
- F-052: Builder.__init__(app, env)设置srcdir/confdir/outdir/doctreedir，保存app/env/events/config/tags引用，初始化images/imagedir/imgpath
- F-053: Builder持有_app(Sphinx), env(BuildEnvironment), events(EventManager), config(Config), tags(Tags), _registry引用
- F-054: 构建阶段通过BuildPhase枚举管理：INITIALIZATION, READING, WRITING等

## Sphinx扩展API方法

- F-055: app.add_builder(builder, override) - 注册构建器，委托给registry
- F-056: app.add_config_value(name, default, rebuild, types, description) - 注册配置值
- F-057: app.add_event(name) - 注册自定义事件，委托给events.add
- F-058: app.set_translator(name, translator_class, override) - 注册/覆盖Docutils Translator
- F-059: app.add_node(node, override, **kwargs) - 注册Docutils节点类，kwargs为各builder的(visit,depart)处理器对
- F-060: app.add_enumerable_node(node, figtype, title_getter, override, **kwargs) - 注册可编号节点（支持numref）
- F-061: app.add_directive(name, cls, override) - 注册Docutils指令
- F-062: app.add_role(name, role, override) - 注册角色
- F-063: app.add_domain(domain, override) - 注册Domain
- F-064: app.add_directive_to_domain(domain, name, cls, override) - 向指定Domain添加指令
- F-065: app.add_role_to_domain(domain, name, role, override) - 向指定Domain添加角色
- F-066: app.add_crossref_type(directivename, rolename, indextemplate, objtype, override) - 注册交叉引用类型
- F-067: app.add_transform(transform) - 添加文档转换器
- F-068: app.add_post_transform(transform) - 添加后转换器（解析后执行）
- F-069: app.add_js_file(filename, priority, **kwargs) - 注册JS文件
- F-070: app.add_css_file(filename, priority, **kwargs) - 注册CSS文件
- F-071: app.add_lexer(alias, lexer) - 注册Pygments词法分析器
- F-072: app.add_autodocumenter(cls, override) - 注册autodoc文档生成器
- F-073: app.add_autodoc_attrgetter(type, getter) - 为类型注册自定义属性获取器
- F-074: app.add_source_suffix(suffix, filetype) - 注册源文件后缀
- F-075: app.add_source_parser(parser, override) - 注册源解析器
- F-076: app.require_sphinx(version) - 检查Sphinx版本要求
- F-077: app.setup_extension(extname) - 导入并设置扩展模块（幂等）

## 构建流程

- F-078: Sphinx.build(force_all, filenames)设置builder.phase=READING，然后根据参数调用builder.build_all()/build_specific(filenames)/build_update()，最后emit('build-finished', None或exception)，builder.cleanup()
- F-079: 构建异常时删除environment.pickle强制下次全新构建
- F-080: 构建完成后根据_warncount和_fail_on_warnings输出不同的完成消息

## 源码目录结构

- F-081: sphinx/_cli/ - CLI工具
- F-082: sphinx/builders/ - 构建器（html/, latex/等子目录+各输出格式builder）
- F-083: sphinx/cmd/ - 命令行入口(build.py, make_mode.py, quickstart.py)
- F-084: sphinx/directives/ - 指令实现(admonitions/code/other/patches)
- F-085: sphinx/domains/ - 领域实现(c/, cpp/, python/, std/, javascript/, math/, rst/等)
- F-086: sphinx/environment/ - 构建环境
- F-087: sphinx/ext/ - 内置扩展(apidoc/, autodoc/, intersphinx/, napoleon/等)
- F-088: sphinx/pycode/ - Python代码解析(ast.py, parser.py)
- F-089: sphinx/search/ - 搜索（多语言停用词）
- F-090: sphinx/themes/ - 内置主题(agogo/basic/bizstyle/classic/default/epub/haiku/nature/nonav/pyramid/scrolls)
- F-091: sphinx/transforms/ - 文档转换器(i18n/references)
- F-092: sphinx/util/ - 工具函数（约50个模块）
- F-093: sphinx/writers/ - 输出写入器(html, html5, latex, manpage, texinfo, text, xml)
- F-094: Sphinx基于docutils库，使用docutils的parsers.rst.Directive, docutils.transforms.Transform, docutils.nodes等基类
