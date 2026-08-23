---
type: Facts
title: ipython 源码事实清单
description: R阶段产出：从零推测事实，每条事实指向具体源码位置
tags:
- facts
- source-code
- evidence
- verification
- ipython
- jupyter
- repl
generated:
  by: agent:source-code-to-okf-wiki
  at: '2026-08-22T00:00:00+08:00'
status: stable
stale_after: 2027-08-22
sources:
- ../../../../../external/libs/jupyter/ipython/pyproject.toml
- ../../../../../external/libs/jupyter/ipython/README.rst
- ../../../../../external/libs/jupyter/ipython/setup.py
- ../../../../../external/libs/jupyter/ipython/ipython/__init__.py
- ../../../../../external/libs/jupyter/ipython/ipython/__main__.py
- ../../../../../external/libs/jupyter/ipython/ipython/core/__init__.py
- ../../../../../external/libs/jupyter/ipython/ipython/core/_dunder_ops.py
- ../../../../../external/libs/jupyter/ipython/ipython/core/alias.py
- ../../../../../external/libs/jupyter/ipython/ipython/core/application.py
- ../../../../../external/libs/jupyter/ipython/ipython/core/async_helpers.py
- ../../../../../external/libs/jupyter/ipython/ipython/core/autocall.py
- ../../../../../external/libs/jupyter/ipython/ipython/core/builtin_trap.py
- ../../../../../external/libs/jupyter/ipython/ipython/core/compilerop.py
- ../../../../../external/libs/jupyter/ipython/ipython/core/completer.py
- ../../../../../external/libs/jupyter/ipython/ipython/core/completerlib.py
- ../../../../../external/libs/jupyter/ipython/ipython/core/crashhandler.py
- ../../../../../external/libs/jupyter/ipython/ipython/core/debugger.py
- ../../../../../external/libs/jupyter/ipython/ipython/core/debugger_backport.py
- ../../../../../external/libs/jupyter/ipython/ipython/core/display.py
- ../../../../../external/libs/jupyter/ipython/ipython/core/display_functions.py
- ../../../../../external/libs/jupyter/ipython/ipython/core/display_trap.py
- ../../../../../external/libs/jupyter/ipython/ipython/core/displayhook.py
- ../../../../../external/libs/jupyter/ipython/ipython/core/displaypub.py
okf_version: '0.2'
---

# IPython 源码事实清单

> R阶段产出：零推测事实，每条事实指向具体源码位置。禁止出现"用于"/"目的是"/"设计为"等推断词。

## 项目元数据

- F-001: 版本号 9.17.0.dev（release.py L17-20）
- F-002: License 为 BSD-3-Clause（release.py L35）
- F-003: 作者为 "The IPython Development Team"，邮箱 ipython-dev@python.org（release.py L42-43）
- F-004: 项目主页 https://ipython.org（__init__.py L5）
- F-005: `__main__.py` 从 `IPython` 导入 `start_ipython` 并调用（__main__.py L11-13）
- F-006: `IPython.__init__` 导入 `InteractiveShell`（from .core.interactiveshell）、`sys_info`（from .utils.sysinfo）、`extract_module_locals`（from .utils.frame）（__init__.py L64-66）
- F-007: `__init__` 中 `__all__ = ["start_ipython", "embed", "embed_kernel"]`（__init__.py L68）
- F-008: `embed` 和 `get_ipython` 通过 `__getattr__` 延迟导入（__init__.py L86-94）
- F-009: `Application` 属性访问触发 DeprecationWarning（__init__.py L95-109）
- F-010: `__version__` 从 release 模块获取，`version_info` 为 (9, 17, 0, '.dev') 元组（__init__.py L119-120, release.py L32）
- F-011: `start_ipython(argv, **kwargs)` 调用 `IPython.terminal.ipapp.launch_new_instance`（__init__.py L169-195）
- F-012: `embed_kernel` 是 ipykernel.embed.embed_kernel 的弃用别名（__init__.py L126-167）

## 顶层包结构

- F-020: IPython 包包含子包：core/、terminal/、utils/、extensions/、external/、lib/、testing/、sphinxext/
- F-021: IPython 包顶层文件：__init__.py、__main__.py、display.py、paths.py、py.typed
- F-022: core/ 目录包含 50+ 个 .py 文件，涵盖 interactiveshell、magic、compiler、history、display、completer 等核心模块
- F-023: core/magics/ 目录包含：__init__.py、_table.py、ast_mod.py、auto.py、basic.py、code.py、config.py、display.py、execution.py、extension.py、history.py、logging.py、namespace.py、osm.py、packaging.py、pylab.py、script.py
- F-024: terminal/ 目录包含：__init__.py、debugger.py、embed.py、interactiveshell.py、ipapp.py、magics.py、prompts.py、ptutils.py，以及 pt_inputhooks/、shortcuts/、tests/ 子目录
- F-025: terminal/pt_inputhooks/ 包含：__init__.py、asyncio.py、glut.py、gtk.py、gtk3.py、gtk4.py、osx.py、pyglet.py、qt.py、tk.py、wx.py
- F-026: extensions/ 目录包含：__init__.py、autoreload.py、storemagic.py、deduperreload/ 子目录
- F-027: utils/ 目录包含 30+ 个 .py 工具模块
- F-028: external/ 目录包含：__init__.py、pickleshare.py、qt_for_kernel.py、qt_loaders.py
- F-029: lib/ 目录包含：__init__.py、backgroundjobs.py、clipboard.py、deepreload.py、demo.py、display.py、editorhooks.py、guisupport.py、latextools.py、lexers.py、pretty.py
- F-030: testing/ 目录包含：__init__.py、decorators.py、globalipapp.py、ipunittest.py、skipdoctest.py、tools.py，以及 plugin/ 子目录

## TerminalIPythonApp 应用层 `terminal/ipapp.py`

- F-100: `TerminalIPythonApp` 继承 `BaseIPythonApplication` 和 `InteractiveShellApp`（ipapp.py L182）
- F-101: TerminalIPythonApp.name = "ipython"（L183）
- F-102: TerminalIPythonApp.crash_handler_class = IPAppCrashHandler（L185）
- F-103: TerminalIPythonApp.interactive_shell_class 默认值为 TerminalInteractiveShell（L192-196）
- F-104: `initialize(argv)` 方法调用顺序：super().initialize → init_path → init_shell → init_banner → init_gui_pylab → init_extensions → init_code（L275-292）
- F-105: `init_shell()` 方法通过 `self.interactive_shell_class.instance(parent=self, ...)` 创建 shell 实例（L294-303）
- F-106: `start()` 方法：若 self.interact 为 True 则调用 self.shell.mainloop()，否则非交互模式执行（L321-332）
- F-107: subcommands 包含：profile、kernel、locate、history（L220-233）
- F-108: flags 包含：autoedit-syntax、simple-prompt、banner、confirm-exit、tip、term-title、classic、quick、i（L91-158）
- F-109: `IPAppCrashHandler` 继承 CrashHandler，在崩溃报告中追加会话输入历史（L58-86）
- F-110: `LocateIPythonApp` 继承 BaseIPythonApplication，start() 打印 self.ipython_dir（L168-179）
- F-111: `launch_new_instance = TerminalIPythonApp.launch_instance`（L348）

## BaseIPythonApplication `core/application.py`

- F-120: `BaseIPythonApplication` 继承 traitlets 的 `Application`（application.py L132）
- F-121: 提供 IPython 目录、profile 目录、配置文件加载等基础设施
- F-122: `ProfileDir` 类管理 profile 目录位置和配置文件
- F-123: `ProfileAwareConfigLoader` 继承 PyFileConfigLoader，支持 profile 目录感知的配置加载

## InteractiveShell 核心类 `core/interactiveshell.py`

- F-200: `InteractiveShell` 继承 `SingletonConfigurable`（L430 附近，基于 traitlets）
- F-201: InteractiveShell 是 ABC 抽象基类（通过 InteractiveShellABC 注册）
- F-202: 构造函数 `__init__` 初始化顺序：init_ipython_dir → init_profile_dir → init_instance_attrs → init_environment → init_virtualenv → init_create_namespaces → save_sys_module_state → init_sys_modules → init_history → init_encoding → init_prefilter → init_syntax_highlighting → init_hooks → init_events → init_pushd_popd_magic → init_user_ns → init_builtins → init_completer → init_io → init_traceback_handlers → init_prompts → init_display_formatter → init_display_pub → init_data_pub → init_displayhook → init_magics → init_alias → init_logstart → init_pdb → init_extension_manager → init_payload → events.trigger('shell_initialized')（L621-680）
- F-203: 子组件属性：alias_manager、prefilter_manager、builtin_trap、display_trap、extension_manager、payload_manager、history_manager、magics_manager（L588-601）
- F-204: `input_transformer_manager` 为 TransformerManager 实例（L494-495）
- F-205: `compiler_class` 为 CachingCompiler 类型（L450）
- F-206: `inspector_class` 默认为 "IPython.core.oinspect.Inspector"（L451-455）
- F-207: `display_formatter` 为 DisplayFormatter 实例
- F-208: `display_pub` 为 DisplayPublisher 实例
- F-209: `displayhook` 为 DisplayHook 实例
- F-210: `events` 为 EventManager 实例
- F-211: `execution_count` 从 1 开始单调递增（L489）
- F-212: `ast_node_interactivity` 取值：'all'、'last'、'last_expr'、'none'、'last_expr_or_assign'，默认 'last_expr'（L562-568）
- F-213: `xmode` 异常模式取值：Context、Plain、Verbose、Minimal、Docs、Doctest，默认 Context（L581-585）
- F-214: `pdb` 为 Bool trait，控制异常后自动调用 pdb（L526-530）
- F-215: `auto_magic` 相关，通过 magics_manager.auto_magic 控制（magic.py L460-467）
- F-216: `run_cell(raw_cell, store_history=False, silent=False)` 方法位于 L3202
- F-217: `run_cell_async(raw_cell, ...)` 异步版本位于 L3364
- F-218: `should_run_async(raw_cell)` 方法位于 L3324，判断代码是否需要异步执行
- F-219: `transform_cell(raw_cell)` 方法位于 L3598
- F-220: `run_ast_nodes(nodes, cell_name, ...)` 方法位于 L3662
- F-221: `run_code(code_obj, result=None, *, async_=False)` 方法位于 L3786
- F-222: `run_line_magic(magic_name, line)` 方法
- F-223: `run_cell_magic(magic_name, line, cell)` 方法位于 L2604
- F-224: `mainloop()` 方法启动 REPL 主循环
- F-225: `show_banner()` 显示启动横幅
- F-226: `user_ns` 属性为用户命名空间 dict（L711-719）
- F-227: `db` 属性为延迟初始化的 PickleShareDB 键值存储（L692-709）
- F-228: `_user_ns`、`user_global_ns` 等内部命名空间
- F-229: `_last_input_line` 记录最后一行输入
- F-230: `last_execution_succeeded` Bool trait（L617）
- F-231: `last_execution_result` 为 ExecutionResult 实例（L619）
- F-232: 内置变量：_ih（输入历史列表）、_oh（输出历史dict）、In、Out、_、__、___ 等
- F-233: `exiter` 为 ExitAutocall 实例，输入 exit/quit 触发退出（L484-487）
- F-234: `trio_runner` 属性用于 Trio 事件循环集成（L687）

## TerminalInteractiveShell `terminal/interactiveshell.py`

- F-240: `TerminalInteractiveShell` 继承 InteractiveShell
- F-241: 提供终端特有的 prompts、autoindent、syntax highlighting、confirm_exit 等
- F-242: `simple_prompt` Bool trait 控制是否使用简单 prompt（禁用 prompt_toolkit）
- F-243: `autoedit_syntax` 控制语法错误时自动编辑文件
- F-244: `confirm_exit` 控制 Ctrl-D 退出时是否确认
- F-245: `term_title` 控制自动设置终端标题
- F-246: `prompts_class` 默认使用 "IPython.terminal.prompts.Prompts"，classic 模式使用 ClassicPrompts
- F-247: `enable_tip` 控制启动时显示提示

## MagicsManager 魔法命令管理器 `core/magic.py`

- F-300: `MagicsManager` 继承 Configurable（magic.py L410）
- F-301: MagicsManager.magics 为二级 dict：magics['line'][name] 和 magics['cell'][name] 存储可调用对象（L418）
- F-302: MagicsManager.lazy_magics 为 Dict trait，存储延迟加载魔法名到模块路径的映射（L419-451）
- F-303: MagicsManager.registry 为 _MagicsRegistry 实例，按类名存储 Magics 对象（L454, L388-407）
- F-304: MagicsManager.auto_magic 为 Bool trait，默认 True，控制是否自动调用行魔法（L460-467）
- F-305: `register(*magic_objects)` 方法注册一个或多个 Magics 类/实例（L628）
- F-306: `register_function(func, magic_kind, magic_name=None)` 注册独立函数为魔法（L666）
- F-307: `register_alias(alias_name, magic_name)` 注册魔法别名（L704）
- F-308: `register_lazy(name, fully_qualified_name, magic_kind='line_cell')` 延迟注册魔法（L538）
- F-309: `load_lazy(magic_name)` 导入并注册延迟魔法（L569-599）
- F-310: `load_all_lazy_magics()` 加载所有 "module:Class" 形式的延迟魔法（L601-609）
- F-311: `find(magic_kind, magic_name)` 查找魔法，必要时加载延迟魔法（L611-626）
- F-312: `lsmagic()` 返回 {'line': {...}, 'cell': {...}} 字典（L499-505）
- F-313: `lsmagic_docs(brief=False)` 返回魔法文档字符串字典（L507-536）
- F-314: `auto_status()` 返回 automagic 状态描述字符串（L495-497）
- F-315: `_MagicsRegistry` 继承 dict，__missing__ 方法自动加载 lazy 类（L388-407）
- F-316: `LazyMagic` 类占位未导入的魔法，__call__ 和 __getattr__ 触发解析（L349-385）

## Magics 基类与装饰器 `core/magic.py`

- F-320: `Magics` 类继承 Configurable，位于 L745
- F-321: Magics 类提供 shell、options 等属性，以及 named_params 等工具方法
- F-322: `magics_class` 类装饰器标记 Magics 子类，从模块级 magics dict 复制魔法注册到类（L110-132）
- F-323: `line_magic` 方法装饰器（_method_magic_marker("line")），标记行魔法方法（L334）
- F-324: `cell_magic` 方法装饰器（_method_magic_marker("cell")），标记单元魔法方法（L335）
- F-325: `line_cell_magic` 方法装饰器（_method_magic_marker("line_cell")），同时注册为行和单元魔法（L336）
- F-326: `register_line_magic`、`register_cell_magic`、`register_line_cell_magic` 函数装饰器，运行时立即注册（L340-342）
- F-327: `needs_local_scope(func)` 装饰器标记需要本地命名空间的魔法函数（L96-99）
- F-328: `no_var_expand(func)` 装饰器标记不进行变量展开的魔法（L304-317）
- F-329: `output_can_be_silenced(func)` 装饰器标记输出可被分号静默的魔法（L320-328）
- F-330: 魔法转义字符：行魔法 ESC_MAGIC = '%'，单元魔法 ESC_MAGIC2 = '%%'（inputtransformer2.py L66）
- F-331: magic_kinds = ("line", "cell")，magic_spec = ("line", "cell", "line_cell")（magic.py L52-53）
- F-332: `record_magic(dct, magic_kind, magic_name, func)` 工具函数将函数存入魔法字典（L135-157）

## 内置魔法类 `core/magics/`

- F-340: MAGICS_CLASSES 映射表（_table.py L26-43）：
  - AsyncMagics → IPython.core.magics.basic
  - AutoMagics → IPython.core.magics.auto
  - BasicMagics → IPython.core.magics.basic
  - CodeMagics → IPython.core.magics.code
  - ConfigMagics → IPython.core.magics.config
  - DisplayMagics → IPython.core.magics.display
  - ExecutionMagics → IPython.core.magics.execution
  - ExtensionMagics → IPython.core.magics.extension
  - HistoryMagics → IPython.core.magics.history
  - LoggingMagics → IPython.core.magics.logging
  - NamespaceMagics → IPython.core.magics.namespace
  - OSMagics → IPython.core.magics.osm
  - PackagingMagics → IPython.core.magics.packaging
  - PylabMagics → IPython.core.magics.pylab
  - ScriptMagics → IPython.core.magics.script
- F-341: BUILTIN_LAZY_MAGICS 声明内置行魔法：autocall、automagic、alias_magic、colors、doctest_mode、gui、lsmagic、magic、notebook、page、pprint、precision、quickref、xmode、edit、load、loadpy、pastebin、save、config、code_wrap、debug、macro、pdb、prun、run、tb、time、timeit、load_ext、reload_ext、unload_ext、history、recall、rerun、logoff、logon、logstart、logstate、logstop、pdef、pdoc、pfile、pinfo、pinfo2、psearch、psource、reset、reset_selective、who、who_ls、whos、xdel、alias、bookmark、cd、dhist、dirs、env、popd、pushd、pwd、pycat、rehashx、sc、set_env、sx、system、unalias、conda、mamba、micromamba、pip、uv、matplotlib、pylab、killbgscripts、autoawait（_table.py L50-142）
- F-342: BUILTIN_LAZY_MAGICS 声明内置单元魔法：html、javascript、js、latex、markdown、svg、capture、code_wrap、debug、prun、time、timeit、!、sx、system、writefile、script（_table.py L144-166）
- F-343: default_script_magics() 默认脚本魔法解释器：sh、bash、perl、ruby、python、python2、python3、pypy；Windows 额外添加 cmd（_table.py L170-193）
- F-344: UserMagics 类继承 Magics，作为用户自定义魔法的占位容器（magics/__init__.py L49-56）
- F-345: magics/__init__.py 使用 __getattr__ 实现惰性导入（PEP 562）（L59-67）

## 输入转换管线 `core/inputtransformer2.py`

- F-350: TransformerManager 管理输入转换管线
- F-351: ESC_MAGIC = '%'（行魔法前缀），ESC_MAGIC2 = '%%'（单元魔法前缀）（L66）
- F-352: PromptStripper 类移除输入提示符（>>>和...）（L51-100+）
- F-353: leading_empty_lines(lines) 移除前导空行（L27-38）
- F-354: leading_indent(lines) 移除公共前导缩进（L41-48）
- F-355: 输入转换包括：magic 命令转换、system 命令（!）转换、help（?）转换、prompt 剥离、IPython 特殊语法转换

## 事件系统 `core/events.py`

- F-360: `EventManager` 类管理事件回调注册和触发（L29）
- F-361: EventManager 构造接受 shell、available_events、print_on_error 参数（L40-61）
- F-362: `register(event, function)` 注册回调（L63-84）
- F-363: `unregister(event, function)` 取消注册（L86-91）
- F-364: `trigger(event, *args, **kwargs)` 触发事件，捕获回调异常（L93-109）
- F-365: available_events 字典存储可用事件原型（L112）
- F-366: `_define_event` 装饰器注册事件原型函数（L116-119）
- F-367: 预定义事件：pre_execute、pre_run_cell(info)、post_execute、post_run_cell(result)、shell_initialized(ip)（L128-180）

## Hooks 系统 `core/hooks.py`

- F-370: Hooks 是设计给用户覆盖的单函数定制点（hooks.py L1-28）
- F-371: 内置 hooks：editor、synchronize_with_editor、show_in_pager、clipboard_get（L51-56）
- F-372: `CommandChainDispatcher` 类实现命令链分发，按优先级调用链中函数直到成功（L91+）
- F-373: `set_hook(name, hook)` 方法设置 hook，支持 TryNext 异常链式尝试

## 显示与格式化系统

### DisplayFormatter `core/formatters.py`

- F-380: `DisplayFormatter` 继承 Configurable（formatters.py L88）
- F-381: DisplayFormatter 管理一组 active formatters，按 MIME 类型分发格式化
- F-382: `FormatterABC` 抽象基类（L296）
- F-383: `BaseFormatter` 继承 Configurable 和 FormatterABC（L347）
- F-384: 内置 formatter 类型：PlainTextFormatter（L630）、HTMLFormatter（L774）、MarkdownFormatter（L791）、SVGFormatter（L805）、PNGFormatter（L822）、JPEGFormatter（L840）、LatexFormatter（L858）、JSONFormatter（L875）、JavascriptFormatter（L913）、PDFFormatter（L929）、IPythonDisplayFormatter（L946）、MimeBundleFormatter（L987）
- F-385: PlainTextFormatter.pprint 控制是否使用 pretty printing

### DisplayPublisher `core/displaypub.py`

- F-390: `DisplayPublisher` 继承 Configurable（L35）
- F-391: DisplayPublisher.publish(data, metadata, source, *, transient=None, update=False) 发布显示数据
- F-392: `CapturingDisplayPublisher` 继承 DisplayPublisher，捕获输出到列表（L183）

### DisplayHook `core/displayhook.py`

- F-400: `DisplayHook` 继承 Configurable（L23）
- F-401: DisplayHook 实现 sys.displayhook，控制表达式结果的显示
- F-402: `CapturingDisplayHook` 捕获显示输出（L334）

### DisplayObject 层次 `core/display.py`

- F-410: `DisplayObject` 基类（L292）
- F-411: `TextDisplayObject` 继承 DisplayObject（L408）
- F-412: DisplayObject 子类：Pretty（L426）、HTML（L432）、Markdown（L463）、Math（L469）、Latex（L479）、SVG（L485）、ProgressBar（L525）、JSON（L583）、GeoJSON（L668）、Javascript（L737）、Image（L881）、Video（L1132）
- F-413: ImageFormat 枚举：png、jpeg、svg、pdf（L861）
- F-414: `DisplayHandle` 类在 display_functions.py L308，支持更新已显示内容
- F-415: 顶层 `IPython/display.py` 提供公共 API：display、display_pretty、display_html、display_markdown、display_svg、display_png、display_jpeg、display_latex、display_json、display_javascript、display_pdf、clear_output、publish_display_data、update_display、DisplayObject 类重导出

## 历史管理 `core/history.py`

- F-420: `HistoryAccessorBase` 继承 LoggingConfigurable（L232）
- F-421: `HistoryAccessor` 继承 HistoryAccessorBase（L271），提供历史读取接口
- F-422: `HistoryManager` 继承 HistoryAccessor（L705），提供完整的历史写入和管理
- F-423: HistoryManager 使用 SQLite 数据库存储历史
- F-424: `HistorySavingThread` 继承 threading.Thread（L1236），后台异步保存历史
- F-425: `HistoryOutput` 类（L698）
- F-426: `DummyDB` 类（L124），无历史时的空实现

## 扩展系统 `core/extensions.py`

- F-430: `ExtensionManager` 继承 Configurable（L23）
- F-431: `load_extension(module_name)` 加载扩展
- F-432: `unload_extension(module_name)` 卸载扩展
- F-433: `reload_extension(module_name)` 重新加载扩展
- F-434: 扩展通过 `load_ipython_extension(ipython)` 函数入口加载
- F-435: 卸载通过 `unload_ipython_extension(ipython)` 函数

## 补全系统 `core/completer.py`

- F-440: `IPCompleter` 继承 Completer（L1973）
- F-441: `Completer` 继承 Configurable（L976）
- F-442: `Completion` 类（L497）表示一个补全项
- F-443: `SimpleCompletion`（L571）、`SimpleMatcherResult`（L614）类型
- F-444: `CompletionContext`（L636）提供补全上下文
- F-445: `CompletionSplitter`（L925）分割补全文本
- F-446: 支持 Jedi 补全和字典键补全（_DictKeyState Flag，L1443）
- F-447: MatcherAPIv2 协议定义补全匹配器接口（L700）

## 编译器 `core/compilerop.py`

- F-450: `CachingCompiler` 继承 codeop.Compile（L73）
- F-451: CachingCompiler 缓存编译后的代码对象
- F-452: 提供文件名管理（anonymize、get_code_name）、AST 转换等功能

## Prefilter 系统 `core/prefilter.py`

- F-460: `PrefilterManager` 管理前置过滤器
- F-461: 处理 AutoMagic、Alias、ESC 命令等预处理

## Alias 系统 `core/alias.py`

- F-470: `Alias` 类表示系统命令别名（L121）
- F-471: `AliasManager` 继承 Configurable（L193），管理别名注册和展开
- F-472: `AliasError`、`InvalidAliasError` 异常类（L113-119）
- F-473: 默认别名：cat、cp、mv、rm、mkdir 等类 Unix 命令

## 异步支持 `core/async_helpers.py`

- F-480: `_should_be_async(cell)` 判断代码是否包含顶层 await
- F-481: `_asyncio_runner`、`_trio_runner`、`_curio_runner` 异步运行器
- F-482: `_pseudo_sync_runner` 伪同步运行器
- F-483: `_AsyncIORunner`、`_AsyncIOProxy` 类

## 错误与调试

- F-490: `Pdb` 类继承 OldPdb（debugger.py L209），提供 IPython 增强的调试器
- F-491: `InterruptiblePdb` 继承 Pdb（L1435），支持中断的调试器
- F-492: `CrashHandler` 类（crashhandler.py L95）处理崩溃报告
- F-493: `ultratb` 模块提供增强的 traceback 格式化（Verbose/Context/Plain/Minimal 模式）
- F-494: IPythonCoreError 异常基类（error.py L29）
- F-495: TryNext 异常用于 hooks 链（L33）
- F-496: UsageError 用于魔法命令参数错误（L40）
- F-497: StdinNotImplementedError 用于前端不支持 stdin（L47）
- F-498: InputRejected 用于输入验证失败（L54）

## 对象内省 `core/oinspect.py`

- F-500: `Inspector` 类提供对象内省功能
- F-501: `OInfo` namedtuple 包含对象信息
- F-502: 支持 pinfo（?）、pinfo2（??）、pdef、pdoc、psource、pfile 等

## 配置系统

- F-510: 基于 traitlets 框架：Configurable、SingletonConfigurable、Application
- F-511: 配置文件为 Python 文件（ipython_config.py）
- F-512: Profile 系统支持多配置文件
- F-513: InteractiveShellApp（core/shellapp.py）提供代码/文件/模块运行相关配置
- F-514: `paths.py` 提供 get_ipython_dir() 等路径函数

## 内置扩展 `extensions/`

- F-520: `autoreload.py` 提供 %autoreload 魔法，自动重新加载修改的模块
- F-521: `storemagic.py` 提供 %store 魔法，持久化变量
- F-522: `deduperreload/` 提供去重重载扩展

## 终端 UI `terminal/`

- F-530: TerminalInteractiveShell 使用 prompt_toolkit 提供富交互体验
- F-531: pt_inputhooks/ 提供各 GUI 框架的事件循环集成（asyncio、qt、gtk、tk、wx、osx、glut、pyglet）
- F-532: shortcuts/ 提供自动匹配、自动建议、过滤器等 prompt_toolkit 快捷键
- F-533: `prompts.py` 定义终端提示符类（Prompts、ClassicPrompts）
- F-534: `ptutils.py` 提供 prompt_toolkit 工具函数
- F-535: `embed.py` 提供 IPython.embed() 嵌入功能
- F-536: `magics.py` 提供终端特有的魔法命令
- F-537: `debugger.py` 提供终端调试器集成
