# IPython 信源参考索引

本目录包含 IPython 交互式 Python Shell 的源码级 API 参考文档，按核心模块组织。所有参考文档直接对应 IPython 源码文件，提供类结构、方法签名和关键实现细节。

## 应用层

| 参考 | 说明 |
|------|------|
| [app-source.md](app-source.md) | TerminalIPythonApp 应用入口、BaseIPythonApplication 配置基础设施、InteractiveShellApp 代码运行配置、命令行 flags/aliases、子命令（profile/kernel/locate/history）、IPAppCrashHandler 崩溃处理 |

## 核心引擎

| 参考 | 说明 |
|------|------|
| [interactiveshell-source.md](interactiveshell-source.md) | InteractiveShell 核心类 API：初始化序列（31 个 init_* 方法）、run_cell/run_cell_async 执行入口、命名空间管理（user_ns/user_global_ns/builtins 注入）、mainloop 主循环、reset 重置、atexit_operations、ExecutionResult、ast_node_interactivity、xmode 异常模式、CachingCompiler 编译器、SingletonConfigurable 单例模式 |

## 子系统模块

| 参考 | 说明 |
|------|------|
| [magic-source.md](magic-source.md) | MagicsManager 魔法管理器（register/find/load_lazy/auto_magic）、Magics 基类、装饰器体系（@magics_class/@line_magic/@cell_magic/@line_cell_magic/@needs_local_scope/@no_var_expand/@output_can_be_silenced）、LazyMagic 延迟加载、_MagicsRegistry 注册表、BUILTIN_LAZY_MAGICS 内置魔法清单（15 个 Magics 类、80+ 魔法命令）、MAGICS_CLASSES 映射表 |
| [display-source.md](display-source.md) | 显示系统完整 API：DisplayFormatter（12 种 MIME formatter：PlainText/HTML/Markdown/SVG/PNG/JPEG/Latex/JSON/Javascript/PDF/IPython/MimeBundle）、DisplayPublisher/CapturingDisplayPublisher、DisplayHook/CapturingDisplayHook、DisplayObject 类层次（Pretty/HTML/Markdown/Math/Latex/SVG/ProgressBar/JSON/GeoJSON/Javascript/Image/Video）、display()/clear_output()/update_display()/DisplayHandle、富显示协议（_repr_html_ 等） |
| [inputtransformer-source.md](inputtransformer-source.md) | 输入转换管线：TransformerManager、ESC_MAGIC(%)/ESC_MAGIC2(%%) 魔法前缀、System 命令(!/!!)、Help 语法(?/??)、PromptStripper(>>>...) 提示符剥离、leading_empty_lines/leading_indent 预处理、PrefilterManager 前置过滤（AutoMagic/Alias 展开/ESC 命令） |
| [events-hooks-source.md](events-hooks-source.md) | EventManager 事件系统（register/unregister/trigger、5 个预定义事件：pre_execute/pre_run_cell/post_execute/post_run_cell/shell_initialized）、Hooks 钩子系统（set_hook、CommandChainDispatcher 职责链、TryNext 异常、4 个内置 hook：editor/synchronize_with_editor/show_in_pager/clipboard_get）、Events 与 Hooks 的设计区别 |
| [extension-source.md](extension-source.md) | ExtensionManager 扩展管理器（load_extension/unload_extension/reload_extension）、扩展入口点（load_ipython_extension/unload_ipython_extension）、内置扩展示例（autoreload 自动重载、storemagic 变量持久化、deduperreload 去重重载）、%load_ext/%unload_ext/%reload_ext 魔法 |
| [history-completer-source.md](history-completer-source.md) | HistoryManager 历史管理（SQLite 后端、HistorySavingThread 异步保存线程、HistoryAccessor 读取接口、DummyDB 空实现）、IPCompleter 补全系统（Jedi 补全、字典键补全、MatcherAPIv2 协议、Completion/CompletionContext/SimpleCompletion 类型）、AliasManager 别名管理（Alias 类、默认别名 cat/cp/mv/rm/mkdir、AliasError 异常） |

```{toctree}
:hidden:

app-source
display-source
events-hooks-source
extension-source
history-completer-source
inputtransformer-source
interactiveshell-source
magic-source
```
