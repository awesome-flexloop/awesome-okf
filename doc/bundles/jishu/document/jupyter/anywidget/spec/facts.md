---
source: anywidget
package: anywidget
package_version_source: packages/anywidget/package.json
phase: R (Retrospective/Fact Collection)
type: spec
title: Anywidget Facts - R阶段采集事实
description: R阶段源码事实采集记录，用于支撑概念文档的事实依据。
---


# anywidget 事实清单

## Source Files Analyzed

| # | 文件路径 | 类型 |
|---|---------|------|
| 1 | `anywidget/_version.py` | Python 版本模块 |
| 2 | `anywidget/widget.py` | Python 主 AnyWidget 基类 |
| 3 | `anywidget/_descriptor.py` | Python 描述符协议实现 |
| 4 | `anywidget/_protocols.py` | Python 协议/接口定义 |
| 5 | `anywidget/_traits.py` | Python trait 同步 |
| 6 | `anywidget/_file_contents.py` | Python 文件内容管理（ESM/CSS 加载） |
| 7 | `anywidget/_util.py` | Python 工具函数 |
| 8 | `anywidget/_cellmagic.py` | Python Jupyter cell magic |
| 9 | `anywidget/experimental.py` | Python 实验性功能 |
| 10 | `anywidget/__init__.py` | Python 公共 API 导出 |
| 11 | `anywidget/nbextension/extension.js` | Jupyter Notebook 扩展入口 |
| 12 | `anywidget.json` | Jupyter nbextension 配置 |
| 13 | `packages/types/index.ts` | TypeScript 类型定义 |
| 14 | `packages/anywidget/src/index.js` | JS 入口点（AMD define） |
| 15 | `packages/anywidget/src/widget.ts` | JS widget 工厂（AnyModel/AnyView） |
| 16 | `packages/anywidget/src/runtime.ts` | JS Runtime 类 |
| 17 | `packages/anywidget/src/binding.ts` | JS WidgetBinding 类 |
| 18 | `packages/anywidget/src/load.ts` | JS ESM/CSS 加载模块 |
| 19 | `packages/anywidget/src/observe.ts` | JS SolidJS 响应式观察工具 |
| 20 | `packages/anywidget/src/host.ts` | JS Host API 实现 |
| 21 | `packages/anywidget/src/invoke.ts` | JS 命令调用实现 |
| 22 | `packages/anywidget/src/util.ts` | JS 工具函数 |
| 23 | `packages/anywidget/src/widget-ref.ts` | JS Widget 引用解析 |
| 24 | `packages/anywidget/src/model-proxy.ts` | JS Model 代理 |
| 25 | `packages/anywidget/src/plugin.js` | JupyterLab 插件注册 |
| 26 | `packages/vite/index.js` | Vite 插件 |
| 27 | `packages/vite/hmr.js` | Vite HMR 运行时 |
| 28 | `pyproject.toml` | Python 包配置 |
| 29 | `README.md` | 项目 README |
| 30 | `tests/test_widget.py` | 测试文件 - Widget 测试 |
| 31 | `tests/test_descriptor.py` | 测试文件 - 描述符测试 |
| 32 | `tests/test_experimental.py` | 测试文件 - 实验性功能测试 |

> 注：`anywidget/_serve.py` 文件在当前版本中不存在。

---

## F-001 ~ F-050: Python 包结构与版本

### F-001: 包基本信息
- **来源**: `pyproject.toml` L1-L6
- **事实**: 包名为 `anywidget`，描述为 `custom jupyter widgets made easy`，要求 Python >= 3.10，许可证 MIT，作者 Trevor Manz。

### F-002: 核心依赖
- **来源**: `pyproject.toml` L18
- **事实**: 运行时依赖为 `ipywidgets>=7.6.0`、`psygnal>=0.8.1`、`typing-extensions>=4.2.0`。

### F-003: 可选依赖
- **来源**: `pyproject.toml` L24-L25
- **事实**: `dev` 可选依赖组包含 `watchfiles>=1.1.0`。

### F-004: 开发依赖组
- **来源**: `pyproject.toml` L27-L37
- **事实**: dev dependency-group 包含 `comm>=0.1.4`, `jupyterlab>=4.2.4`, `msgspec>=0.20.0`, `pydantic>=2.5.3`, `pytest>=7.4.4`, `ruff>=0.15.9`, `ty>=0.0.29`, `watchfiles>=0.23.0`。

### F-005: 构建系统
- **来源**: `pyproject.toml` L39-L41
- **事实**: 使用 `hatchling` 作为构建后端。

### F-006: 版本管理
- **来源**: `pyproject.toml` L66-L68
- **事实**: 版本号从 `packages/anywidget/package.json` 中通过正则 `"version": "(?P<version>.+?)"` 提取。

### F-007: __version__ 定义
- **来源**: `anywidget/_version.py` L1-L6
- **事实**: `__version__` 通过 `importlib.metadata.version("anywidget")` 获取；若包未安装则设为 `"uninstalled"`。

### F-008: get_semver_version 函数
- **来源**: `anywidget/_version.py` L9-L15
- **事实**: `get_semver_version(version: str) -> str` 将版本号按 `"."` 分割（最多2次），若第3段包含 `"a"` 或 `"b"`（预发布版本）则返回原版本号，否则返回 `~<major>.<minor>.*` 格式的 semver 范围字符串。

### F-009: _ANYWIDGET_SEMVER_VERSION 常量
- **来源**: `anywidget/_version.py` L18
- **事实**: `_ANYWIDGET_SEMVER_VERSION = get_semver_version(__version__)`，为模块级常量。

### F-010: 公共 API 导出
- **来源**: `anywidget/__init__.py` L1-L10
- **事实**: `__all__ = ["AnyWidget", "Widget", "WidgetTrait", "__version__"]`。其中 `Widget` 是从 `_protocols` 导入的 `AnywidgetProtocol` 别名。

### F-011: _jupyter_labextension_paths
- **来源**: `anywidget/__init__.py` L13-L14
- **事实**: `_jupyter_labextension_paths()` 返回 `[{"src": "labextension", "dest": "anywidget"}]`。

### F-012: _jupyter_nbextension_paths
- **来源**: `anywidget/__init__.py` L17-L25
- **事实**: `_jupyter_nbextension_paths()` 返回一个列表，包含一个字典：`{"section": "notebook", "src": "nbextension", "dest": "anywidget", "require": "anywidget/extension"}`。

### F-013: load_ipython_extension
- **来源**: `anywidget/__init__.py` L28-L31
- **事实**: `load_ipython_extension(ipython)` 延迟导入并调用 `_cellmagic.load_ipython_extension(ipython)`。

### F-014: nbextension 配置文件
- **来源**: `anywidget.json` L1-L5
- **事实**: 内容为 `{"load_extensions": {"anywidget/extension": true}}`，用于自动加载 notebook 扩展。

### F-015: nbextension 入口 JS
- **来源**: `anywidget/nbextension/extension.js` L1-L15
- **事实**: 通过 RequireJS config 将 `anywidget` 模块映射到 `nbextensions/anywidget/index`，并导出空的 `load_ipython_extension` 函数。

---

## F-051 ~ F-120: 核心常量与工具函数

### F-051: 二进制类型常量
- **来源**: `anywidget/_util.py` L12
- **事实**: `_BINARY_TYPES = (memoryview, bytearray, bytes)`。

### F-052: Widget MIME 类型
- **来源**: `anywidget/_util.py` L13
- **事实**: `_WIDGET_MIME_TYPE = "application/vnd.jupyter.widget-view+json"`。

### F-053: 协议版本
- **来源**: `anywidget/_util.py` L14-L16
- **事实**: `_PROTOCOL_VERSION_MAJOR = 2`，`_PROTOCOL_VERSION_MINOR = 1`，`_PROTOCOL_VERSION = "2.1.0"`。

### F-054: 特殊 Trait Key 常量
- **来源**: `anywidget/_util.py` L17-L19
- **事实**: `_ANYWIDGET_ID_KEY = "_anywidget_id"`，`_ESM_KEY = "_esm"`，`_CSS_KEY = "_css"`。

### F-055: 默认 ESM 内容
- **来源**: `anywidget/_util.py` L20-L32
- **事实**: `_DEFAULT_ESM` 是一个多行字符串，包含一个默认的 `render` 函数，在未定义 `_esm` 时显示开发提示信息，包含一个链接到 anywidget 入门文档的 `<p>` 元素。导出形式为 `export default { render }`。

### F-056: _separate_buffers 函数
- **来源**: `anywidget/_util.py` L40-L93
- **事实**: `_separate_buffers(substate, path, buffer_paths, buffers)` 递归遍历 dict/list/tuple 结构，将 `memoryview`/`bytearray`/`bytes` 类型的值提取到 `buffers` 列表，记录其路径到 `buffer_paths`，并在原结构中替换为 `None`（list 位置）或删除（dict 键）。遇到非 list/dict 类型抛出 `TypeError`。

### F-057: remove_buffers 函数
- **来源**: `anywidget/_util.py` L96-L124
- **事实**: `remove_buffers(state) -> tuple[Any, list[list], list[memoryview]]` 调用 `_separate_buffers` 返回去除二进制数据后的 state、buffer_paths 和 buffers 列表。

### F-058: put_buffers 函数
- **来源**: `anywidget/_util.py` L127-L143
- **事实**: `put_buffers(state, buffer_paths, buffers)` 将 buffers 中的二进制数据按 buffer_paths 指定的路径放回 state 字典中（直接修改传入的 state）。

### F-059: in_colab 函数
- **来源**: `anywidget/_util.py` L146-L148
- **事实**: `in_colab() -> bool` 检查 `"google.colab.output"` 是否在 `sys.modules` 中。

### F-060: enable_custom_widget_manager_once 函数
- **来源**: `anywidget/_util.py` L151-L157
- **事实**: 使用 `@cache` 装饰器缓存，调用 `sys.modules["google.colab.output"].enable_custom_widget_manager()` 启用 Colab 自定义 widget 管理器。

### F-061: get_repr_metadata 函数
- **来源**: `anywidget/_util.py` L160-L178
- **事实**: `get_repr_metadata() -> dict` 在 Colab 环境中返回包含 `_WIDGET_MIME_TYPE` 的 metadata dict，包含 colab custom_widget_manager URL；非 Colab 环境返回空 dict。

### F-062: _is_hmr_enabled 函数
- **来源**: `anywidget/_util.py` L181-L182
- **事实**: `_is_hmr_enabled() -> bool` 检查环境变量 `ANYWIDGET_HMR` 是否等于 `"1"`。

### F-063: _should_start_thread 函数
- **来源**: `anywidget/_util.py` L185-L211
- **事实**: `_should_start_thread(path: pathlib.Path) -> bool` 判断逻辑：(1) 路径包含 `site-packages` 或 `dist-packages` 返回 False；(2) HMR 未启用（`ANYWIDGET_HMR != "1"`）返回 False；(3) 无法导入 `watchfiles` 发出警告并返回 False；否则返回 True。

### F-064: try_file_path 函数
- **来源**: `anywidget/_util.py` L214-L259
- **事实**: `try_file_path(x: object) -> pathlib.Path | None` 尝试将 x 转为 pathlib.Path：(1) 已是 Path 直接返回；(2) 非字符串返回 None；(3) 以 `http://` 或 `https://` 开头返回 None；(4) 多行字符串（含 `\n` 或 `\r`）返回 None；(5) 单行字符串有文件扩展名后缀（正则 `[a-zA-Z0-9]\.[a-zA-Z0-9]+$`）返回 resolve 后的绝对路径；否则返回 None。

### F-065: try_file_contents 函数
- **来源**: `anywidget/_util.py` L262-L284
- **事实**: `try_file_contents(x: object) -> FileContents | VirtualFileContents | None`：(1) 若 x 是字符串且在 `_VIRTUAL_FILES` 中返回对应的 VirtualFileContents；(2) 调用 `try_file_path(x)` 获取路径，若为 None 返回 None；(3) 路径不存在抛出 FileNotFoundError；(4) 返回 `FileContents(path, start_thread=_should_start_thread(path))`。

### F-066: repr_mimebundle 函数
- **来源**: `anywidget/_util.py` L287-L300
- **事实**: `repr_mimebundle(model_id: str, repr_text: str) -> tuple[dict, dict]` 返回 MIME bundle 数据字典和 metadata。数据字典包含 `text/plain`（repr_text）和 `_WIDGET_MIME_TYPE`（含 version_major=2, version_minor=1, model_id）。metadata 来自 `get_repr_metadata()`。

### F-067: _PLAIN_TEXT_MAX_LEN 常量
- **来源**: `anywidget/widget.py` L22
- **事实**: `_PLAIN_TEXT_MAX_LEN = 110`。

---

## F-121 ~ F-180: AnyWidget 主类

### F-121: AnyWidget 类定义
- **来源**: `anywidget/widget.py` L25-L83
- **事实**: `class AnyWidget(ipywidgets.DOMWidget)` 继承自 `ipywidgets.DOMWidget`。

### F-122: AnyWidget 类级别 traits
- **来源**: `anywidget/widget.py` L28-L34
- **事实**:
  - `_model_name = t.Unicode("AnyModel").tag(sync=True)`
  - `_model_module = t.Unicode("anywidget").tag(sync=True)`
  - `_model_module_version = t.Unicode(_ANYWIDGET_SEMVER_VERSION).tag(sync=True)`
  - `_view_name = t.Unicode("AnyView").tag(sync=True)`
  - `_view_module = t.Unicode("anywidget").tag(sync=True)`
  - `_view_module_version = t.Unicode(_ANYWIDGET_SEMVER_VERSION).tag(sync=True)`

### F-123: AnyWidget.__init__ 方法签名
- **来源**: `anywidget/widget.py` L36-L63
- **事实**: `def __init__(self, *args: object, **kwargs: object) -> None`。

### F-124: AnyWidget.__init__ Colab 处理
- **来源**: `anywidget/widget.py` L37-L38
- **事实**: 若 `in_colab()` 返回 True，调用 `enable_custom_widget_manager_once()`。

### F-125: AnyWidget.__init__ _esm/_css trait 自动推断
- **来源**: `anywidget/widget.py` L40-L48
- **事实**: 遍历 `(_ESM_KEY, _CSS_KEY)`，若实例有该属性但未定义为 trait，则创建 `t.Unicode(str(value)).tag(sync=True)` trait；若值为 `VirtualFileContents` 或 `FileContents` 实例，连接其 `changed` 信号以在文件变更时更新 trait 值。

### F-126: AnyWidget.__init__ 默认 ESM
- **来源**: `anywidget/widget.py` L51-L52
- **事实**: 若实例没有 `_ESM_KEY` 属性，添加 `_esm` trait 为 `t.Unicode(_DEFAULT_ESM).tag(sync=True)`。

### F-127: AnyWidget.__init__ _anywidget_id
- **来源**: `anywidget/widget.py` L57-L59
- **事实**: 添加 `_anywidget_id` trait，值为 `f"{self.__class__.__module__}.{self.__class__.__name__}"`（完全限定类名）。

### F-128: AnyWidget.__init__ trait 添加与父类初始化
- **来源**: `anywidget/widget.py` L61-L63
- **事实**: 调用 `self.add_traits(**anywidget_traits)` 添加动态 trait，调用 `super().__init__(*args, **kwargs)`，最后调用 `_register_anywidget_commands(self)`。

### F-129: AnyWidget.__init_subclass__ 方法
- **来源**: `anywidget/widget.py` L65-L74
- **事实**: `def __init_subclass__(cls, **kwargs: dict) -> None`：(1) 调用 `super().__init_subclass__(**kwargs)`；(2) 遍历 `(_ESM_KEY, _CSS_KEY) & cls.__dict__.keys()`，对每个值调用 `try_file_contents()`，若返回 FileContents/VirtualFileContents 则替换类属性；(3) 调用 `_collect_anywidget_commands(cls)`。

### F-130: AnyWidget.__repr__ 方法
- **来源**: `anywidget/widget.py` L76-L78
- **事实**: `def __repr__(self) -> str` 返回 `object.__repr__(self)`，避免 ipywidgets 的昂贵 trait 序列化。子类可覆盖此方法。

### F-131: AnyWidget._repr_mimebundle_ 方法
- **来源**: `anywidget/widget.py` L80-L83
- **事实**: `def _repr_mimebundle_(self, **kwargs: dict) -> tuple[dict, dict] | None`：若 `self._view_name is None` 返回 None（DOM-less widget），否则返回 `repr_mimebundle(model_id=self.model_id, repr_text=repr(self))`。

---

## F-181 ~ F-280: 描述符协议（MimeBundleDescriptor / ReprMimeBundle）

### F-181: 描述符模块常量
- **来源**: `anywidget/_descriptor.py` L67-L70
- **事实**:
  - `_REPR_ATTR = "_repr_mimebundle_"`
  - `_STATE_GETTER_NAME = "_get_anywidget_state"`
  - `_STATE_SETTER_NAME = "_set_anywidget_state"`
  - `_WIDGET_REF_PREFIX = "anywidget:"`

### F-182: 模块导出
- **来源**: `anywidget/_descriptor.py` L65
- **事实**: `__all__ = ["MimeBundleDescriptor", "ReprMimeBundle"]`。

### F-183: _try_get_model_id 函数
- **来源**: `anywidget/_descriptor.py` L73-L97
- **事实**: `_try_get_model_id(obj: object) -> str | None`：(1) 若 obj 有 `model_id` 属性且为字符串，直接返回；(2) 否则获取 `_repr_mimebundle_` 属性，若为 `MimeBundleDescriptor` 则调用 `__get__` 创建 `ReprMimeBundle`（副作用：打开 comm）；(3) 若为 `ReprMimeBundle` 返回其 `model_id`；(4) 否则返回 None。

### F-184: _replace_widget_refs 函数
- **来源**: `anywidget/_descriptor.py` L100-L115
- **事实**: `_replace_widget_refs(obj: dict) -> dict` 递归遍历 dict/list/tuple 结构，将 anywidget 对象替换为 `"anywidget:<model_id>"` 字符串。

### F-185: open_comm 函数
- **来源**: `anywidget/_descriptor.py` L118-L144
- **事实**: `open_comm(initial_state: dict, version: str = _PROTOCOL_VERSION) -> comm.base_comm.BaseComm`：(1) 对 initial_state 调用 `_replace_widget_refs`；(2) 调用 `remove_buffers` 分离二进制数据；(3) 调用 `comm.create_comm` 创建 target_name 为 `"jupyter.widget"` 的 comm，metadata 包含 version，data 包含 state（固定字段 `_model_module="anywidget"`, `_model_name="AnyModel"`, `_model_module_version=_ANYWIDGET_SEMVER_VERSION`, `_view_module="anywidget"`, `_view_name="AnyView"`, `_view_module_version=_ANYWIDGET_SEMVER_VERSION`, `_view_count=None` 加上传入 state）和 buffer_paths，buffers 为分离出的二进制数据。

### F-186: _COMMS 缓存
- **来源**: `anywidget/_descriptor.py` L147-L150
- **事实**: `_COMMS: dict[int, comm.base_comm.BaseComm] = {}`，以 `id(obj)` 为键缓存 comm 对象。使用 `id(obj)` 而非 WeakKeyDictionary 因为对象可能不可哈希。

### F-187: _get_or_create_comm 函数
- **来源**: `anywidget/_descriptor.py` L153-L173
- **事实**: `_get_or_create_comm(obj, get_state) -> comm.base_comm.BaseComm`：(1) 以 `id(obj)` 为键在 `_COMMS` 中查找；(2) 若不存在则调用 `open_comm(initial_state=get_state())` 创建，并注册 `weakref.finalize(obj, _COMMS.pop, obj_id)` 在对象被 GC 时清理缓存；(3) 返回 comm。

### F-188: MimeBundleDescriptor 类
- **来源**: `anywidget/_descriptor.py` L176-L310
- **事实**: `class MimeBundleDescriptor` 是一个 Python 描述符类。

### F-189: MimeBundleDescriptor.__init__ 签名
- **来源**: `anywidget/_descriptor.py` L224-L244
- **事实**: `def __init__(self, *, follow_changes: bool = True, autodetect_observer: bool = True, no_view: bool = False, **extra_state: object) -> None`。extra_state 默认包含 `{_ESM_KEY: _DEFAULT_ESM}`。对 extra_state 中的每个值调用 `try_file_contents()`，若返回 FileContents 则替换。

### F-190: MimeBundleDescriptor.__set_name__ 方法
- **来源**: `anywidget/_descriptor.py` L246-L253
- **事实**: `def __set_name__(self, owner: type, name: str) -> None` 将 `self._name` 设为属性名（通常为 `"_repr_mimebundle_"`）。

### F-191: MimeBundleDescriptor.__get__ 方法
- **来源**: `anywidget/_descriptor.py` L255-L310
- **事实**: 两个重载：(1) instance=None 时返回描述符自身（类访问）；(2) instance 不为 None 时创建 `ReprMimeBundle` 实例，若 `follow_changes=True` 调用 `repr_obj.sync_object_with_view()`，然后通过 `setattr(instance, self._name, repr_obj)` 将 ReprMimeBundle 缓存在实例上（捕获 AttributeError/ValueError 以兼容 `__slots__`）。异常时发出 warnings。

### F-192: ReprMimeBundle 类
- **来源**: `anywidget/_descriptor.py` L313-L553
- **事实**: `class ReprMimeBundle` 是一个可调用对象，实现 `_repr_mimebundle_` 协议并管理 comm 通道。

### F-193: ReprMimeBundle.__init__ 签名
- **来源**: `anywidget/_descriptor.py` L345-L394
- **事实**: `def __init__(self, obj: object, autodetect_observer: bool = True, extra_state: dict[str, object] | None = None, no_view: bool = False) -> None`。

### F-194: ReprMimeBundle.__init__ 初始化逻辑
- **来源**: `anywidget/_descriptor.py` L352-L394
- **事实**:
  - extra_state 默认包含 `{_ANYWIDGET_ID_KEY: _anywidget_id(obj)}`
  - 尝试对 obj 创建 weakref，失败则持有强引用并发出警告（建议添加 `__slots__ = ('__weakref__',)`）
  - 初始化 `self._disconnectors: set[Callable] = set()`
  - 调用 `determine_state_getter(obj)` 和 `determine_state_setter(obj)` 确定状态获取/设置方法
  - 对 extra_state 中的 FileContents/VirtualFileContents 值，将其转为字符串并连接 changed 信号以在变更时调用 `self.send_state(key)`
  - 调用 `_get_or_create_comm` 创建/获取 comm

### F-195: ReprMimeBundle._on_obj_deleted 方法
- **来源**: `anywidget/_descriptor.py` L396-L400
- **事实**: `def _on_obj_deleted(self, ref=None) -> None` 调用 `self.unsync_object_with_view()` 和 `self._comm.close()`。

### F-196: ReprMimeBundle.send_state 方法
- **来源**: `anywidget/_descriptor.py` L402-L434
- **事实**: `def send_state(self, include: str | Iterable[str] | None = None) -> None`：(1) 获取 obj 弱引用，若为 None 直接返回；(2) include 参数过滤要发送的 key；(3) 合并 `_get_state` 和 `_extra_state`；(4) 调用 `_replace_widget_refs`；(5) 调用 `remove_buffers` 分离二进制；(6) 若 comm 有 kernel，通过 `self._comm.send()` 发送 `{"method": "update", "state": state, "buffer_paths": buffer_paths}` 消息。

### F-197: ReprMimeBundle._handle_msg 方法
- **来源**: `anywidget/_descriptor.py` L436-L470
- **事实**: `def _handle_msg(self, msg: CommMessage) -> None` 处理前端消息：
  - `method == "update"`：从 data 中取出 state，若有 buffer_paths 则调用 `put_buffers` 还原二进制数据，然后调用 `self._set_state(obj, state)`
  - `method == "request_state"`：调用 `self.send_state()`
  - 其他 method 抛出 ValueError

### F-198: ReprMimeBundle.model_id 属性
- **来源**: `anywidget/_descriptor.py` L477-L480
- **事实**: `@property def model_id(self) -> str` 返回 `self._comm.comm_id`。

### F-199: ReprMimeBundle.__call__ 方法
- **来源**: `anywidget/_descriptor.py` L482-L488
- **事实**: `def __call__(self, **kwargs) -> tuple[dict, dict] | None`：若 `self._no_view` 为 True 返回 None，否则返回 `repr_mimebundle(model_id=self._comm.comm_id, repr_text=repr(self._obj()))`。

### F-200: ReprMimeBundle.sync_object_with_view 方法
- **来源**: `anywidget/_descriptor.py` L490-L544
- **事实**: `def sync_object_with_view(self, py_to_js: bool = True, js_to_py: bool = True) -> None`：
  - js_to_py=True 时：注册 `self._comm.on_msg(self._handle_msg)` 并调用 `self.send_state()`
  - py_to_js=True 且 autodetect_observer=True 时：依次尝试 `_connect_psygnal` 和 `_connect_traitlets`，成功则将 disconnect 函数加入 `_disconnectors` 集合；若都失败发出 UserWarning
  - 若已 sync（`_disconnectors` 非空）发出警告并返回

### F-201: ReprMimeBundle.unsync_object_with_view 方法
- **来源**: `anywidget/_descriptor.py` L546-L552
- **事实**: `def unsync_object_with_view(self) -> None`：调用 `self._comm.on_msg(None)` 取消消息监听，然后调用所有 disconnector 并清空集合。

---

## F-202 ~ F-260: 状态获取/设置与观察者连接

### F-202: _anywidget_id 函数
- **来源**: `anywidget/_descriptor.py` L558-L560
- **事实**: `_anywidget_id(obj: object) -> str` 返回 `f"{type(obj).__module__}.{type(obj).__name__}"`。

### F-203: determine_state_getter 函数
- **来源**: `anywidget/_descriptor.py` L563-L614
- **事实**: `determine_state_getter(obj: object) -> _GetState` 按以下优先级自动检测状态获取方法：
  1. 类有 `_get_anywidget_state` 方法 → 返回该未绑定方法
  2. `is_dataclass(obj)` 为 True → 返回 `lambda obj, include: asdict(obj)`
  3. `_is_traitlets_object(obj)` 为 True → 返回 `_get_traitlets_state`
  4. `_is_pydantic_model(obj)` 为 True：有 `model_dump` 方法返回 `_get_pydantic_state_v2`，否则返回 `_get_pydantic_state_v1`
  5. `_is_msgspec_struct(obj)` 为 True → 返回 `_get_msgspec_state`
  6. 以上都不满足 → 抛出 TypeError

### F-204: _default_set_state 函数
- **来源**: `anywidget/_descriptor.py` L617-L620
- **事实**: `_default_set_state(obj: object, state: dict) -> None` 遍历 state 字典，对每个 key 调用 `setattr(obj, key, val)`。

### F-205: determine_state_setter 函数
- **来源**: `anywidget/_descriptor.py` L623-L637
- **事实**: `determine_state_setter(obj: object) -> Callable`：若类有 `_set_anywidget_state` 方法返回该方法，否则返回 `_default_set_state`。

### F-206: _TRAITLETS_SYNC_FLAG 常量
- **来源**: `anywidget/_descriptor.py` L705
- **事实**: `_TRAITLETS_SYNC_FLAG = "sync"`，标记需要同步的 traitlet。

### F-207: _is_traitlets_object 函数
- **来源**: `anywidget/_descriptor.py` L697-L700
- **事实**: 检查 `sys.modules` 中是否有 traitlets，然后 `isinstance(obj, traitlets.HasTraits)`。

### F-208: _get_traitlets_state 函数
- **来源**: `anywidget/_descriptor.py` L713-L725
- **事实**: `_get_traitlets_state(obj, include)` 调用 `obj.trait_values(sync=True)` 返回标记了 sync=True 的所有 trait 值。

### F-209: _connect_traitlets 函数
- **来源**: `anywidget/_descriptor.py` L728-L754
- **事实**: `_connect_traitlets(obj, send_state) -> Callable | None`：对 `obj.traits(sync=True)` 的所有 trait 注册 `observe` 回调，变更时调用 `send_state({change["name"]})`；返回 disconnect 函数（调用 `unobserve`）。

### F-210: _get_psygnal_signal_group 函数
- **来源**: `anywidget/_descriptor.py` L643-L667
- **事实**: 查找 obj 上的 psygnal.SignalGroup：先检查 `obj.events`，若不是则遍历 `vars(obj)` 查找。

### F-211: _connect_psygnal 函数
- **来源**: `anywidget/_descriptor.py` L670-L691
- **事实**: `_connect_psygnal(obj, send_state) -> Callable | None`：若找到 SignalGroup，连接其事件以在信号发射时调用 `send_state({event.signal.name})`；返回 disconnect 函数。

### F-212: _is_pydantic_model 函数
- **来源**: `anywidget/_descriptor.py` L760-L768
- **事实**: 检查 sys.modules 中是否有 pydantic，然后 `isinstance(obj, pydantic.BaseModel)`。

### F-213: _get_pydantic_state_v1 函数
- **来源**: `anywidget/_descriptor.py` L771-L786
- **事实**: 调用 `obj.json(include=include)` 然后 `json.loads()` 转回 dict（支持 pydantic v1 的自定义编码器）。

### F-214: _get_pydantic_state_v2 函数
- **来源**: `anywidget/_descriptor.py` L789-L794
- **事实**: 调用 `obj.model_dump(mode="json", include=include)`。

### F-215: _is_msgspec_struct 函数
- **来源**: `anywidget/_descriptor.py` L800-L803
- **事实**: 检查 sys.modules 中是否有 msgspec，然后 `isinstance(obj, msgspec.Struct)`。

### F-216: _get_msgspec_state 函数
- **来源**: `anywidget/_descriptor.py` L806-L812
- **事实**: 调用 `msgspec.to_builtins(obj)` 转为内置类型。

---

## F-217 ~ F-250: 协议定义（_protocols.py）

### F-217: UpdateData TypedDict
- **来源**: `anywidget/_protocols.py` L13-L16
- **事实**: 字段：`method: Literal["update"]`，`state: dict`，`buffer_paths: list[list[int | str]]`。

### F-218: RequestStateData TypedDict
- **来源**: `anywidget/_protocols.py` L19-L21
- **事实**: 字段：`method: Literal["request_state"]`。

### F-219: CustomData TypedDict
- **来源**: `anywidget/_protocols.py` L23-L26
- **事实**: 字段：`method: Literal["custom"]`，`content: dict`。

### F-220: JupyterWidgetContent TypedDict
- **来源**: `anywidget/_protocols.py` L28-L31
- **事实**: 字段：`comm_id: str`，`data: UpdateData | RequestStateData | CustomData`。

### F-221: CommMessage TypedDict
- **来源**: `anywidget/_protocols.py` L33-L41
- **事实**: 字段：`header: dict`，`msg_id: str`，`msg_type: str`，`parent_header: dict`，`metadata: dict`，`content: JupyterWidgetContent`，`buffers: list[memoryview]`。

### F-222: MimeReprCallable Protocol
- **来源**: `anywidget/_protocols.py` L44-L59
- **事实**: 定义 `_repr_mimebundle_` 协议，`__call__(self, include, exclude) -> dict | tuple[dict, dict]`。

### F-223: AnywidgetProtocol Protocol
- **来源**: `anywidget/_protocols.py` L62-L65
- **事实**: 要求类具有 `_repr_mimebundle_: MimeBundleDescriptor` 属性。

### F-224: WidgetBase Protocol
- **来源**: `anywidget/_protocols.py` L68-L76
- **事实**: 定义 `send(msg, buffers)` 和 `on_msg(callback)` 方法。

---

## F-251 ~ F-280: WidgetTrait 与文件内容管理

### F-251: _widget_to_json 函数
- **来源**: `anywidget/_traits.py` L10-L17
- **事实**: `_widget_to_json(value, _obj) -> object`：若 value 为 None 返回 None；调用 `_try_get_model_id(value)` 获取 model_id，若有则返回 `"anywidget:<model_id>"`，否则返回 value 本身。

### F-252: _widget_from_json 函数
- **来源**: `anywidget/_traits.py` L20-L22
- **事实**: `_widget_from_json(value, _obj) -> object` 直接返回 value（透传，JS 发送 ref 字符串原样传递）。

### F-253: WidgetTrait 类
- **来源**: `anywidget/_traits.py` L25-L66
- **事实**: `class WidgetTrait(t.TraitType)` 继承自 `traitlets.TraitType`。

### F-254: WidgetTrait 类属性
- **来源**: `anywidget/_traits.py` L51-L53
- **事实**: `default_value = None`，`info_text = "an anywidget-compatible object or None"`，`allow_none = True`。

### F-255: WidgetTrait.__init__ 方法
- **来源**: `anywidget/_traits.py` L55-L58
- **事实**: 设置 metadata 中的 `to_json` 为 `_widget_to_json`，`from_json` 为 `_widget_from_json`。

### F-256: WidgetTrait.validate 方法
- **来源**: `anywidget/_traits.py` L60-L65
- **事实**: `validate(self, obj, value) -> object`：None 通过；`_try_get_model_id(value)` 不返回 None 则通过；否则调用 `self.error(obj, value)` 抛出 TraitError。

### F-257: _VIRTUAL_FILES 全局注册表
- **来源**: `anywidget/_file_contents.py` L16-L18
- **事实**: `_VIRTUAL_FILES: weakref.WeakValueDictionary[str, VirtualFileContents] = weakref.WeakValueDictionary()`，使用 WeakValueDictionary 以允许虚拟文件在无引用时被 GC。

### F-258: 模块导出
- **来源**: `anywidget/_file_contents.py` L14
- **事实**: `__all__ = ["_VIRTUAL_FILES", "FileContents", "VirtualFileContents"]`。

### F-259: VirtualFileContents 类
- **来源**: `anywidget/_file_contents.py` L21-L47
- **事实**: `class VirtualFileContents` 在内存中存储文本文件内容，内容变更时发射信号。

### F-260: VirtualFileContents.changed 信号
- **来源**: `anywidget/_file_contents.py` L32
- **事实**: `changed = Signal(str)`（psygnal.Signal），在内容变更时发射新内容字符串。

### F-261: VirtualFileContents.__init__
- **来源**: `anywidget/_file_contents.py` L34-L35
- **事实**: `def __init__(self, contents: str = "") -> None`，初始化 `self._contents = contents`。

### F-262: VirtualFileContents.contents 属性
- **来源**: `anywidget/_file_contents.py` L37-L44
- **事实**: getter 返回 `self._contents`；setter 设置 `self._contents = value` 并调用 `self.changed.emit(value)`。

### F-263: VirtualFileContents.__str__
- **来源**: `anywidget/_file_contents.py` L46-L47
- **事实**: 返回 `self.contents`。

### F-264: FileContents 类
- **来源**: `anywidget/_file_contents.py` L50-L136
- **事实**: `class FileContents` 监视文件系统上的文件变更，变更时发射信号。

### F-265: FileContents.changed 和 deleted 信号
- **来源**: `anywidget/_file_contents.py` L64-L65
- **事实**: `changed = Signal(str)`，`deleted = Signal()`。

### F-266: FileContents.__init__
- **来源**: `anywidget/_file_contents.py` L67-L76
- **事实**: `def __init__(self, path: str | pathlib.Path, start_thread: bool = True) -> None`：(1) 将路径转为绝对路径并 expanduser；(2) 检查文件是否存在，不存在抛出 ValueError；(3) 初始化 `self._contents = None`，`self._stop_event = threading.Event()`，`self._background_thread = None`；(4) 若 start_thread=True 调用 `self.watch_in_thread()`。

### F-267: FileContents.watch_in_thread 方法
- **来源**: `anywidget/_file_contents.py` L78-L90
- **事实**: 若已有后台线程则直接返回；清除 stop_event，创建 daemon 线程运行 `deque(self.watch(), maxlen=0)` 以消费 watch generator。

### F-268: FileContents.stop_thread 方法
- **来源**: `anywidget/_file_contents.py` L92-L98
- **事实**: 设置 stop_event，join 后台线程，置 `_background_thread = None`。

### F-269: FileContents.watch 方法
- **来源**: `anywidget/_file_contents.py` L100-L131
- **事实**: `def watch(self) -> Iterator[tuple[int, str]]` 使用 watchfiles 库监视文件变更：(1) 导入 watchfiles，失败抛出 ImportError 提示安装 watchfiles；(2) 文件被删除时发射 `deleted` 信号并返回；(3) 文件被修改/添加时清空缓存 `self._contents = None`，发射 `changed.emit(str(self))`，yield 变更事件。

### F-270: FileContents.__str__
- **来源**: `anywidget/_file_contents.py` L133-L136
- **事实**: 若 `self._contents is None` 则读取文件内容（UTF-8 编码）并缓存，返回 `self._contents`。

---

## F-271 ~ F-300: Cell Magic 与实验性功能

### F-271: AnyWidgetMagics 类
- **来源**: `anywidget/_cellmagic.py` L14-L43
- **事实**: `@magics_class class AnyWidgetMagics(Magics)` 继承自 IPython 的 Magics。

### F-272: AnyWidgetMagics.__init__
- **来源**: `anywidget/_cellmagic.py` L18-L22
- **事实**: 调用 `super().__init__(shell)`，初始化 `self._files: dict[str, VirtualFileContents] = {}` 以保持对虚拟文件的强引用（因为 `_VIRTUAL_FILES` 是 WeakValueDictionary）。

### F-273: AnyWidgetMagics.vfile cell magic
- **来源**: `anywidget/_cellmagic.py` L24-L38
- **事实**: `@cell_magic def vfile(self, line: str, cell: str) -> None`：接受一个 file_name 参数，创建名为 `"vfile:<file_name>"` 的 VirtualFileContents，将 cell 内容（经过 IPython transform_cell）存入其中，并注册到 `self._files` 和 `_VIRTUAL_FILES`。若文件已存在则更新内容。

### F-274: AnyWidgetMagics.clear_vfiles line magic
- **来源**: `anywidget/_cellmagic.py` L40-L43
- **事实**: `@line_magic def clear_vfiles(self, line) -> None` 清空 `self._files` 字典。

### F-275: load_ipython_extension（cellmagic 模块）
- **来源**: `anywidget/_cellmagic.py` L46-L54
- **事实**: `def load_ipython_extension(ipython: InteractiveShell) -> None` 调用 `ipython.register_magics(AnyWidgetMagics)`。

### F-276: experimental 模块导出
- **来源**: `anywidget/experimental.py` L17
- **事实**: `__all__ = ["MimeBundleDescriptor", "dataclass", "widget"]`。注意 MimeBundleDescriptor 从 `_descriptor` 重新导出。

### F-277: experimental.widget 装饰器
- **来源**: `anywidget/experimental.py` L22-L52
- **事实**: `def widget(*, esm: str | pathlib.Path, css: None | str | pathlib.Path = None, **kwargs) -> Callable[[T], T]`：将 esm/css 放入 kwargs（键为 `"_esm"`/`"_css"`），返回装饰器，装饰器在类上设置 `_repr_mimebundle_ = MimeBundleDescriptor(**kwargs)`。

### F-278: experimental.dataclass 装饰器
- **来源**: `anywidget/experimental.py` L67-L111
- **事实**: `def dataclass(cls=None, *, esm, css=None, **dataclass_kwargs) -> Callable[[T], T]`：依次应用 `dataclasses.dataclass(cls, **dataclass_kwargs)` → `psygnal.evented(cls)` → `widget(esm=esm, css=css)(cls)`。支持无括号调用（直接 `@dataclass(esm=...)`）和有括号调用。

### F-279: experimental.command 装饰器
- **来源**: `anywidget/experimental.py` L123-L138
- **事实**: `def command(cmd: T) -> T` 在函数上设置 `_ANYWIDGET_COMMAND` 属性为 True，标记为 anywidget 命令。

### F-280: 命令相关常量
- **来源**: `anywidget/experimental.py` L114-L120
- **事实**: `_ANYWIDGET_COMMAND = "_anywidget_command"`，`_ANYWIDGET_COMMANDS = "_anywidget_commands"`，`_AnyWidgetCommand = typing.Callable[[object, object, list[bytes]], tuple[object, list[bytes]]]`。

### F-281: _collect_anywidget_commands 函数
- **来源**: `anywidget/experimental.py` L141-L150
- **事实**: `_collect_anywidget_commands(widget_cls: type) -> None` 遍历 MRO 中所有基类的 `__dict__`，收集带有 `_ANYWIDGET_COMMAND` 标记的可调用属性到 `cmds: dict[str, _AnyWidgetCommand]`，设置到类的 `_ANYWIDGET_COMMANDS` 属性。

### F-282: _register_anywidget_commands 函数
- **来源**: `anywidget/experimental.py` L153-L181
- **事实**: `_register_anywidget_commands(widget: WidgetBase) -> None`：若 widget 类型有 `_ANYWIDGET_COMMANDS` 字典（非空），注册 `on_msg` 回调处理 `"anywidget-command"` 类型的自定义消息：根据 msg["name"] 查找对应命令函数，调用 `cmd(widget, msg["msg"], buffers)` 获取响应和 buffers，然后通过 `self.send()` 发回 `"anywidget-command-response"` 消息（包含 id、response）。

---

## F-301 ~ F-380: TypeScript 类型定义（packages/types/index.ts）

### F-301: 基础类型别名
- **来源**: `packages/types/index.ts` L1-L3
- **事实**:
  - `type Awaitable<T> = T | Promise<T>`
  - `type ObjectHash = Record<string, any>`
  - `type EventHandler = (...args: any[]) => void`

### F-302: LiteralUnion 类型
- **来源**: `packages/types/index.ts` L11
- **事实**: `type LiteralUnion<T, U = string> = T | (U & {})`，用于提供字面量自动补全同时允许任意字符串。

### F-303: WidgetManager 接口
- **来源**: `packages/types/index.ts` L13-L18
- **事实**: 包含方法 `get_model<T extends ObjectHash>(model_id: string): Promise<AnyModel<T>>`。

### F-304: AnyModel 接口
- **来源**: `packages/types/index.ts` L20-L34
- **事实**: 泛型接口 `AnyModel<T extends ObjectHash = ObjectHash>`，方法/属性：
  - `get<K extends keyof T>(key: K): T[K]`
  - `set<K extends keyof T>(key: K, value: T[K]): void`
  - `off<K>(eventName?, callback?): void`
  - `on(eventName: "msg:custom", callback: (msg: any, buffers: DataView[]) => void): void`
  - `on(eventName: \`change:${string}\`, callback: () => void): void`
  - `on(eventName: string, callback: EventHandler): void`
  - `save_changes(): void`
  - `send(content: any, callbacks?: any, buffers?: ArrayBuffer[] | ArrayBufferView[]): void`
  - `widget_manager: WidgetManager`

### F-305: Experimental 类型
- **来源**: `packages/types/index.ts` L36-L45
- **事实**: `type Experimental = { invoke: <T>(name: string, msg?: any, options?: { buffers?: DataView[]; signal?: AbortSignal }) => Promise<[T, DataView[]]> }`。

### F-306: ResolvedWidget 接口
- **来源**: `packages/types/index.ts` L47-L50
- **事实**: `interface ResolvedWidget<T = unknown>` 包含 `exports: T` 和 `render(opts: { el: HTMLElement; signal?: AbortSignal }): Promise<void>`。

### F-307: Host 接口
- **来源**: `packages/types/index.ts` L52-L55
- **事实**: `interface Host` 包含 `getWidget<T = unknown>(ref: string): Promise<ResolvedWidget<T>>` 和 `getModel<T extends ObjectHash = ObjectHash>(ref: string): Promise<AnyModel<T>>`。

### F-308: RenderProps 接口
- **来源**: `packages/types/index.ts` L57-L63
- **事实**: `interface RenderProps<T extends ObjectHash = ObjectHash>` 包含 `model: AnyModel<T>`、`el: HTMLElement`、`signal: AbortSignal`、`host: Host`、`experimental: Experimental`。

### F-309: Render 类型
- **来源**: `packages/types/index.ts` L65-L67
- **事实**: `type Render<T extends ObjectHash = ObjectHash> = (props: RenderProps<T>) => Awaitable<void | (() => Awaitable<void>)>`，返回值可选为 cleanup 函数。

### F-310: InitializeProps 接口
- **来源**: `packages/types/index.ts` L69-L73
- **事实**: `interface InitializeProps<T extends ObjectHash = ObjectHash>` 包含 `model: AnyModel<T>`、`signal: AbortSignal`、`experimental: Experimental`（无 el 和 host）。

### F-311: Initialize 类型
- **来源**: `packages/types/index.ts` L75-L77
- **事实**: `type Initialize<T extends ObjectHash = ObjectHash> = (props: InitializeProps<T>) => Awaitable<void | (() => Awaitable<void>) | object>`，返回值可为 cleanup 函数或 exports 对象。

### F-312: WidgetDef 接口
- **来源**: `packages/types/index.ts` L79-L82
- **事实**: `interface WidgetDef<T extends ObjectHash = ObjectHash>` 包含可选的 `initialize?: Initialize<T>` 和 `render?: Render<T>`。

### F-313: AnyWidget 类型
- **来源**: `packages/types/index.ts` L84-L86
- **事实**: `type AnyWidget<T extends ObjectHash = ObjectHash> = WidgetDef<T> | (() => Awaitable<WidgetDef<T>>)`，可以是 WidgetDef 对象或返回 Promise<WidgetDef> 的函数。

---

## F-381 ~ F-460: JavaScript 核心运行时

### F-381: JS 入口点 index.js
- **来源**: `packages/anywidget/src/index.js` L1-L4
- **事实**: `import create from "./widget.ts"`，通过 AMD `define(["@jupyter-widgets/base"], create)` 注册。

### F-382: JupyterLab 插件 plugin.js
- **来源**: `packages/anywidget/src/plugin.js` L1-L23
- **事实**: 插件 id 为 `"anywidget:plugin"`，依赖 `@jupyter-widgets/base` 的 `IJupyterWidgetRegistry`，在 activate 中调用 `create(base)` 并通过 `registry.registerWidget({name: "anywidget", version: globalThis.VERSION, exports})` 注册。autoStart 为 true。

### F-383: widget.ts 工厂函数
- **来源**: `packages/anywidget/src/widget.ts` L18-L98
- **事实**: 默认导出函数接收 `{DOMWidgetModel, DOMWidgetView}` 参数，返回 `{AnyModel, AnyView}`。

### F-384: RUNTIMES WeakMap
- **来源**: `packages/anywidget/src/widget.ts` L22
- **事实**: `let RUNTIMES = new WeakMap<InstanceType<typeof DOMWidgetModel>, Runtime>()`，以 model 实例为键缓存 Runtime 实例。

### F-385: AnyModel 类（JS）
- **来源**: `packages/anywidget/src/widget.ts` L24-L82
- **事实**: 继承自 DOMWidgetModel，静态属性：`model_name = "AnyModel"`、`model_module = "anywidget"`、`model_module_version = version`、`view_name = "AnyView"`、`view_module = "anywidget"`、`view_module_version = version`。version 从 `globalThis.VERSION` 注入。

### F-386: AnyModel.initialize 方法
- **来源**: `packages/anywidget/src/widget.ts` L33-L42
- **事实**: 调用 `super.initialize(...args)`，创建 AbortController，监听 "destroy" 事件以 abort controller、销毁 BINDINGS、删除 RUNTIMES 缓存，然后 `RUNTIMES.set(this, new Runtime(this, {signal: controller.signal}))`。

### F-387: AnyModel._handle_comm_msg 方法
- **来源**: `packages/anywidget/src/widget.ts` L44-L50
- **事实**: 获取 runtime，等待 `runtime?.ready`，然后调用 `super._handle_comm_msg(...msg)`。确保 runtime 初始化完成后再处理 comm 消息。

### F-388: AnyModel.serialize 方法
- **来源**: `packages/anywidget/src/widget.ts` L58-L81
- **事实**: 重写 serialize 以正确处理二进制数据（JSON.parse(JSON.stringify()) 无法克隆二进制数据）：使用 serializer 的 serialize 方法，layout/style 用 JSON trick，其他用 structuredClone，最后检查 toJSON 方法。

### F-389: AnyView 类（JS）
- **来源**: `packages/anywidget/src/widget.ts` L84-L95
- **事实**: 继承自 DOMWidgetView，`#controller = new AbortController()`；render 方法获取 runtime，调用 `runtime.createView(this, {signal: this.#controller.signal})`；remove 方法 abort controller 并调用 super.remove()。

### F-390: Runtime 类
- **来源**: `packages/anywidget/src/runtime.ts` L19-L123
- **事实**: `export class Runtime` 管理 widget 的 ESM 加载、CSS 加载和视图创建，使用 SolidJS 响应式系统。

### F-391: Runtime 构造函数
- **来源**: `packages/anywidget/src/runtime.ts` L25-L82
- **事实**:
  - 创建 promiseWithResolvers 用于 ready 状态，2秒超时
  - 获取或创建 BINDINGS binding
  - 创建 experimental 对象（invoke 方法）
  - 在 solid.createRoot 中：
    - 观察 model 的 `_css` 和 `_esm` 变化（observe 函数创建 SolidJS signal）
    - createEffect 响应 CSS 变化（debug log）
    - createEffect 响应 ESM 变化（debug log）
    - createEffect 调用 loadCss(css(), id)
    - createEffect 调用 loadWidget(esm(), id)，加载成功后调用 binding.bind(widget, {experimental})，resolve ready promise
    - 每次 ESM 变化时创建新 AbortController 以取消前一次加载

### F-392: Runtime.createView 方法
- **来源**: `packages/anywidget/src/runtime.ts` L84-L123
- **事实**:
  - 组合 model 和 view 的 AbortSignal
  - 获取 binding，创建 host（createHost）和 experimental
  - 在 solid.createRoot 中 createEffect：清除之前的事件监听和 DOM 内容，等待 widgetResult ready，然后调用 `binding.createView(view, {signal, experimental, host})`

### F-393: WidgetBinding 类
- **来源**: `packages/anywidget/src/binding.ts` L21-L121
- **事实**: `export class WidgetBinding` 管理 widget 定义与 model 的绑定。

### F-394: WidgetBinding.bind 方法
- **来源**: `packages/anywidget/src/binding.ts` L35-L81
- **事实**:
  - 若 widgetDef 未变直接返回
  - 重新绑定时 abort 之前的 controller，reject 之前的 ready promise
  - 清除 INITIALIZE_MARKER 上下文的监听器
  - 调用 `widgetDef.initialize({model: modelProxy(model, INITIALIZE_MARKER), signal, experimental})`
  - 若 initialize 返回函数，注册为 cleanup 并重置 exports；若返回对象则设为 exports；否则 exports 为 undefined
  - resolve ready promise 为 exports

### F-395: WidgetBinding.createView 方法
- **来源**: `packages/anywidget/src/binding.ts` L83-L110
- **事实**:
  - 等待 ready promise
  - 若 widgetDef 无 render 方法直接返回
  - 创建 AbortController 组合 signal
  - 调用 `widgetDef.render({model: modelProxy(model, target), el: target.el, signal: combined, host, experimental})`
  - cleanup 函数：清除 target 上下文的监听器，执行 safeCleanup

### F-396: WidgetBinding.ready 属性
- **来源**: `packages/anywidget/src/binding.ts` L27
- **事实**: `ready: Promise<unknown>`，在 initialize 完成后 resolve 为 exports 值。

### F-397: WidgetBinding.exports 属性
- **来源**: `packages/anywidget/src/binding.ts` L112-L114
- **事实**: `get exports(): unknown` 返回 `this.#exports`。

### F-398: WidgetBinding.destroy 方法
- **来源**: `packages/anywidget/src/binding.ts` L116-L120
- **事实**: abort controller，置空 widgetDef 和 controller。

### F-399: BindingManager 类
- **来源**: `packages/anywidget/src/binding.ts` L123-L146
- **事实**: 使用 `Map<DOMWidgetModel, WidgetBinding>` 管理 bindings，提供 getOrCreate、get、destroy 方法。

### F-400: BINDINGS 单例
- **来源**: `packages/anywidget/src/binding.ts` L148
- **事实**: `export let BINDINGS = new BindingManager()`。

### F-401: modelProxy 函数
- **来源**: `packages/anywidget/src/model-proxy.ts` L17-L35
- **事实**: `modelProxy(model: DOMWidgetModel, context: unknown): AnyModel` 返回一个代理对象，将 get/set/save_changes/send 绑定到 model，on/off 方法使用 context 参数注册监听器（便于后续按 context 清理）。

### F-402: INITIALIZE_MARKER
- **来源**: `packages/anywidget/src/model-proxy.ts` L8
- **事实**: `export let INITIALIZE_MARKER = Symbol("anywidget.initialize")`，用作 initialize 阶段监听器的上下文标记。

---

## F-461 ~ F-520: JS 模块加载、观察、Host、Invoke

### F-403: observe 函数
- **来源**: `packages/anywidget/src/observe.ts` L4-L16
- **事实**: `observe<T, K>(model, name, {signal}): solid.Accessor<T[K]>` 创建 SolidJS signal，初始值为 `model.get(name)`，监听 `change:${name}` 事件更新 signal，signal abort 时移除监听器，返回 signal getter。

### F-404: load.ts - AnyWidget 接口
- **来源**: `packages/anywidget/src/load.ts` L5-L8
- **事实**: `interface AnyWidget { initialize?: Initialize; render?: Render }`。

### F-405: load.ts - AnyWidgetModule 接口
- **来源**: `packages/anywidget/src/load.ts` L10-L13
- **事实**: `interface AnyWidgetModule { render?: Render; default?: AnyWidget | (() => AnyWidget | Promise<AnyWidget>) }`。

### F-406: isHref 函数
- **来源**: `packages/anywidget/src/load.ts` L15-L17
- **事实**: 判断字符串是否以 `http://` 或 `https://` 开头。

### F-407: loadCss 函数
- **来源**: `packages/anywidget/src/load.ts` L60-L64
- **事实**: `loadCss(css: string | undefined, anywidgetId: string): Promise<void>`：css 为空或无 id 直接返回；URL 调用 loadCssHref，文本调用 loadCssText。

### F-408: loadCssHref 函数
- **来源**: `packages/anywidget/src/load.ts` L19-L43
- **事实**: 通过克隆现有 `<link>` 元素并替换 href 的方式热更新 CSS（避免 FOUC）；新 link 加载完成/出错后移除旧 link；首次加载创建新 link 元素添加到 document.head。

### F-409: loadCssText 函数
- **来源**: `packages/anywidget/src/load.ts` L45-L58
- **事实**: 查找 `<style id='anywidgetId'>` 元素，存在则替换 textContent，否则创建新 style 元素添加到 document.head。

### F-410: loadEsm 函数
- **来源**: `packages/anywidget/src/load.ts` L66-L74
- **事实**: URL 字符串直接调用 `import(esm)`（webpackIgnore 和 vite-ignore 注释）；字符串内容通过 `Blob` + `URL.createObjectURL` 创建 Blob URL 后动态 import，然后 `revokeObjectURL`。

### F-411: loadWidget 函数
- **来源**: `packages/anywidget/src/load.ts` L103-L115
- **事实**: `loadWidget(esm: string, anywidgetId: string): Promise<AnyWidget>`：调用 loadEsm 加载模块；若 mod 有直接导出的 render，发出弃用警告并返回 `{async initialize() {}, render: mod.render}`；否则断言 mod.default 存在，若为函数则 await 调用结果，否则直接使用 default。

### F-412: warnRenderDeprecation 函数
- **来源**: `packages/anywidget/src/load.ts` L76-L101
- **事实**: 控制台警告，提示直接导出 render 将被弃用，应改用 `export default { render }` 形式。

### F-413: createHost 函数
- **来源**: `packages/anywidget/src/host.ts` L9-L56
- **事实**: 创建 Host 对象：
  - `getModel(ref)`：解析 widget ref 获取 modelId，通过 `widget_manager.get_model(modelId)` 获取子 model，返回 modelProxy 包装，signal abort 时清理监听器
  - `getWidget(ref)`：解析 ref 获取子 model 和 childBinding，等待 childBinding.ready（10秒超时），返回 `{exports, render({el, signal})}`，render 调用 childBinding.createView

### F-414: parseWidgetRef 函数
- **来源**: `packages/anywidget/src/widget-ref.ts` L3-L8
- **事实**: `parseWidgetRef(ref: unknown): string`：若 ref 是以 `"anywidget:"` 开头的字符串，返回前缀之后的部分；否则抛出 Error。WIDGET_REF_PREFIX 为 `"anywidget:"`。

### F-415: invoke 函数
- **来源**: `packages/anywidget/src/invoke.ts` L9-L40
- **事实**: `invoke<T>(model, name, msg?, options?): Promise<[T, DataView[]]>`：
  - 使用 @lukeed/uuid 生成唯一 id
  - 默认 3 秒超时（AbortSignal.timeout）
  - 监听 "msg:custom" 事件，匹配响应 id 后 resolve 并移除监听器
  - 通过 model.send 发送 `{id, kind: "anywidget-command", name, msg}` 消息

### F-416: JS 工具函数
- **来源**: `packages/anywidget/src/util.ts`
- **事实**:
  - `assert(condition, message)`：条件不成立抛出 Error
  - `safeCleanup(fn, kind)`：安全执行 cleanup 函数，catch 异常并 warn
  - `throwAnywidgetError(source)`：清理错误堆栈（在 anywidget 边界截断）后抛出
  - `promiseWithResolvers<T>()`：Promise.withResolvers polyfill

---

## F-521 ~ F-560: Vite 插件与 HMR

### F-417: Vite 插件查询参数和命名空间
- **来源**: `packages/vite/index.js` L5-L7
- **事实**: `const query = "?anywidget"`，`const namespace = "anywidget:"`，`const resolvedNamespace = "\0anywidget:"`。

### F-418: Vite 插件默认导出
- **来源**: `packages/vite/index.js` L15-L43
- **事实**: 返回 Vite 插件对象：
  - `name: "anywidget"`
  - `apply: "serve"`（仅在 dev serve 模式下生效）
  - `resolveId(id)`：id 以 namespace 开头时返回 `\0${id}`
  - `load(id)`：id 以 resolvedNamespace 开头时，读取 hmr.js 模板，将 `__ANYWIDGET_HMR_SRC__` 替换为源文件路径
  - `configureServer(server)`：中间件拦截以 `?anywidget` 结尾的 URL，将路径转换为 namespace 前缀的 bare identifier

### F-419: HMR 运行时 hmr.js
- **来源**: `packages/vite/hmr.js` L1-L124
- **事实**:
  - `noop()` 空函数
  - `emptyElement(el)` 清空元素所有子节点
  - `showErrorOverlay(err)` 显示 Vite 错误遮罩层
  - 监听 window error 和 unhandledrejection 显示错误遮罩
  - `getAFM(newModule)` 标准化 AFM 输入（支持多种导出格式，含弃用警告）
  - `import.meta.hot.accept("__ANYWIDGET_HMR_SRC__", ...)` 接受 HMR 更新，重新获取 AFM 并刷新
  - `render({model, el, signal, host})` 首次渲染时导入模块、获取 AFM、保存上下文并刷新
  - `refresh()` 遍历所有上下文：执行 cleanup、model.off()、清空 DOM、创建新 AbortController、调用 initialize 和 render，保存 cleanup 函数

---

## F-561 ~ F-600: Python-JS 通信协议

### F-501: Comm 通道
- **来源**: `anywidget/_descriptor.py` L118-L144（open_comm）；`packages/anywidget/src/widget.ts` L44-L50（_handle_comm_msg）
- **事实**: Python 端通过 `comm.create_comm(target_name="jupyter.widget", metadata={"version": "2.1.0"})` 创建 Jupyter Widgets 标准 comm 通道。

### F-502: 初始状态消息
- **来源**: `anywidget/_descriptor.py` L127-L143
- **事实**: comm 创建时发送的 data 包含固定字段：
  - `_model_module: "anywidget"`
  - `_model_name: "AnyModel"`
  - `_model_module_version: _ANYWIDGET_SEMVER_VERSION`
  - `_view_module: "anywidget"`
  - `_view_name: "AnyView"`
  - `_view_module_version: _ANYWIDGET_SEMVER_VERSION`
  - `_view_count: null`
  - 加上用户 state 和 buffer_paths

### F-503: Python → JS 更新消息
- **来源**: `anywidget/_descriptor.py` L429-L434
- **事实**: Python 端状态变更时发送 `{"method": "update", "state": {...}, "buffer_paths": [...]}` 消息，附带 buffers。

### F-504: JS → Python 更新消息
- **来源**: `anywidget/_descriptor.py` L451-L456
- **事实**: JS 端调用 `model.set()` + `model.save_changes()` 发送 `{"method": "update", "state": {...}, "buffer_paths": [...]}` 消息，Python 端在 `_handle_msg` 中接收并调用 `_set_state(obj, state)`。

### F-505: request_state 消息
- **来源**: `anywidget/_descriptor.py` L458-L459
- **事实**: JS 端可发送 `{"method": "request_state"}` 消息，Python 端收到后调用 `self.send_state()` 发送完整状态。

### F-506: 自定义命令协议
- **来源**: `anywidget/experimental.py` L163-L179；`packages/anywidget/src/invoke.ts` L29-L39
- **事实**:
  - JS 端通过 `experimental.invoke(name, msg, options)` 调用：发送 `{id: uuid, kind: "anywidget-command", name, msg}` 自定义消息
  - Python 端在 `_register_anywidget_commands` 中注册 on_msg 回调，匹配 `kind === "anywidget-command"` 后调用对应命令函数，发送 `{id, kind: "anywidget-command-response", response}` 响应
  - invoke 使用 uuid 匹配请求和响应，默认 3 秒超时

### F-507: 二进制数据传输
- **来源**: `anywidget/_util.py` L40-L143
- **事实**: 二进制数据（memoryview/bytearray/bytes）在发送前通过 `remove_buffers` 从 state 中分离为独立的 buffers 列表和 buffer_paths，接收端通过 `put_buffers` 按路径还原。JS 端在 serialize 方法中使用 structuredClone 处理二进制数据。

### F-508: Widget 引用序列化
- **来源**: `anywidget/_traits.py` L10-L22；`anywidget/_descriptor.py` L100-L115；`packages/anywidget/src/widget-ref.ts` L1-L8
- **事实**: WidgetTrait 类型的值在序列化时转换为 `"anywidget:<model_id>"` 字符串格式；JS 端通过 `parseWidgetRef` 解析前缀获取 model_id，再通过 `widget_manager.get_model()` 获取子 model 实例。

### F-509: MIME Bundle 格式
- **来源**: `anywidget/_util.py` L287-L300
- **事实**: `_repr_mimebundle_` 返回的 data 包含：
  - `text/plain`: repr 文本
  - `application/vnd.jupyter.widget-view+json`: `{"version_major": 2, "version_minor": 1, "model_id": "<comm_id>"}`

---

## F-601 ~ F-630: ESM 模块系统

### F-551: _esm 属性
- **来源**: `anywidget/widget.py` L41-L52
- **事实**: 子类可通过 `_esm` 类属性指定 ESM 模块内容。支持三种形式：(1) 内联字符串（ESM 代码）；(2) 路径字符串（单行带文件后缀）；(3) pathlib.Path 对象；(4) FileContents/VirtualFileContents 实例。

### F-552: _css 属性
- **来源**: `anywidget/widget.py` L41-L48
- **事实**: 子类可通过 `_css` 类属性指定 CSS 内容，格式与 _esm 相同。CSS 通过 `<style>` 标签（文本）或 `<link>` 标签（URL）注入到 document.head。

### F-553: __init_subclass__ 文件路径自动转换
- **来源**: `anywidget/widget.py` L65-L74
- **事实**: 子类定义时，`__init_subclass__` 对 `_esm` 和 `_css` 类属性调用 `try_file_contents()`，将文件路径自动转换为 FileContents 实例。

### F-554: 文件监视与热更新
- **来源**: `anywidget/_file_contents.py` L78-L131；`anywidget/_util.py` L185-L211
- **事实**: 当 ANYWIDGET_HMR=1 环境变量设置且文件不在 site-packages/dist-packages 中时，FileContents 启动后台线程使用 watchfiles 监视文件变更。文件变更时清空内容缓存并发射 changed 信号，信号连接到 trait 更新（Python 端），最终通过 comm 发送 update 消息到 JS 端。

### F-555: JS 端 ESM 热更新
- **来源**: `packages/anywidget/src/runtime.ts` L57-L78
- **事实**: Runtime 使用 SolidJS createEffect 响应 `_esm` signal 的变化。ESM 变更时：(1) 创建新的 AbortController 取消前一次加载；(2) 重新调用 loadWidget 加载新模块；(3) binding.bind 中止旧 binding 并重新执行 initialize；(4) createView 中 re-render 视图（清空 DOM、移除旧监听器、调用新 render）。

### F-556: JS 端 CSS 热更新
- **来源**: `packages/anywidget/src/runtime.ts` L54-L59；`packages/anywidget/src/load.ts` L19-L64
- **事实**: Runtime 使用 createEffect 响应 `_css` signal 变化，调用 loadCss 更新样式。CSS 文本通过替换 `<style>` 元素 textContent 热更新；CSS URL 通过克隆 `<link>` 元素替换 href 实现无闪烁更新。

### F-557: ESM 默认导出格式
- **来源**: `packages/types/index.ts` L79-L86；`packages/anywidget/src/load.ts` L103-L115
- **事实**: ESM 模块需 `export default` 一个对象（含可选 initialize 和 render）或一个返回 Promise<该对象> 的函数。直接导出 render 函数已被标记为弃用。

### F-558: initialize 生命周期
- **来源**: `packages/types/index.ts` L69-L77；`packages/anywidget/src/binding.ts` L60-L64
- **事实**: initialize 在 model 绑定到 widget 定义时调用（每次 ESM 重新加载都会调用），接收 `{model, signal, experimental}`，返回值可以是 cleanup 函数或 exports 对象（通过 host.getWidget 访问）。initialize 阶段没有 el 和 host。

### F-559: render 生命周期
- **来源**: `packages/types/index.ts` L57-L67；`packages/anywidget/src/binding.ts` L92-L98
- **事实**: render 在视图创建时调用（每个视图实例调用一次），接收 `{model, el, signal, host, experimental}`，返回值可选 cleanup 函数。视图销毁时 signal 被 abort。

### F-560: AbortSignal 生命周期管理
- **来源**: `packages/anywidget/src/binding.ts` L89-L109；`packages/anywidget/src/runtime.ts` L86-L88
- **事实**: 每个 initialize 和 render 调用都接收 AbortSignal，signal 在 ESM 重新加载、视图销毁或 model 销毁时 abort。cleanup 函数在 abort 时执行。

---

## API Table

| Type | Name | Signature/Type | File | Line |
|------|------|----------------|------|------|
| constant | `__version__` | `str` | `anywidget/_version.py` | L4 |
| function | `get_semver_version` | `(version: str) -> str` | `anywidget/_version.py` | L9-L15 |
| constant | `_ANYWIDGET_SEMVER_VERSION` | `str` | `anywidget/_version.py` | L18 |
| class | `AnyWidget` | `(ipywidgets.DOMWidget)` | `anywidget/widget.py` | L25-L83 |
| method | `AnyWidget.__init__` | `(self, *args: object, **kwargs: object) -> None` | `anywidget/widget.py` | L36-L63 |
| method | `AnyWidget.__init_subclass__` | `(cls, **kwargs: dict) -> None` | `anywidget/widget.py` | L65-L74 |
| method | `AnyWidget.__repr__` | `(self) -> str` | `anywidget/widget.py` | L76-L78 |
| method | `AnyWidget._repr_mimebundle_` | `(self, **kwargs: dict) -> tuple[dict, dict] \| None` | `anywidget/widget.py` | L80-L83 |
| class | `MimeBundleDescriptor` | `(object)` | `anywidget/_descriptor.py` | L176-L310 |
| method | `MimeBundleDescriptor.__init__` | `(self, *, follow_changes: bool=True, autodetect_observer: bool=True, no_view: bool=False, **extra_state: object) -> None` | `anywidget/_descriptor.py` | L224-L244 |
| method | `MimeBundleDescriptor.__set_name__` | `(self, owner: type, name: str) -> None` | `anywidget/_descriptor.py` | L246-L253 |
| method | `MimeBundleDescriptor.__get__` | `(self, instance: object \| None, owner: type) -> ReprMimeBundle \| MimeBundleDescriptor` | `anywidget/_descriptor.py` | L261-L310 |
| class | `ReprMimeBundle` | `(object)` | `anywidget/_descriptor.py` | L313-L553 |
| method | `ReprMimeBundle.__init__` | `(self, obj: object, autodetect_observer: bool=True, extra_state: dict \| None=None, no_view: bool=False) -> None` | `anywidget/_descriptor.py` | L345-L394 |
| method | `ReprMimeBundle.send_state` | `(self, include: str \| Iterable[str] \| None=None) -> None` | `anywidget/_descriptor.py` | L402-L434 |
| method | `ReprMimeBundle._handle_msg` | `(self, msg: CommMessage) -> None` | `anywidget/_descriptor.py` | L436-L470 |
| property | `ReprMimeBundle.model_id` | `str` | `anywidget/_descriptor.py` | L477-L480 |
| method | `ReprMimeBundle.__call__` | `(self, **kwargs) -> tuple[dict, dict] \| None` | `anywidget/_descriptor.py` | L482-L488 |
| method | `ReprMimeBundle.sync_object_with_view` | `(self, py_to_js: bool=True, js_to_py: bool=True) -> None` | `anywidget/_descriptor.py` | L490-L544 |
| method | `ReprMimeBundle.unsync_object_with_view` | `(self) -> None` | `anywidget/_descriptor.py` | L546-L552 |
| function | `open_comm` | `(initial_state: dict, version: str="2.1.0") -> comm.base_comm.BaseComm` | `anywidget/_descriptor.py` | L118-L144 |
| function | `determine_state_getter` | `(obj: object) -> Callable` | `anywidget/_descriptor.py` | L563-L614 |
| function | `determine_state_setter` | `(obj: object) -> Callable` | `anywidget/_descriptor.py` | L623-L637 |
| class | `WidgetTrait` | `(t.TraitType)` | `anywidget/_traits.py` | L25-L66 |
| method | `WidgetTrait.__init__` | `(self) -> None` | `anywidget/_traits.py` | L55-L58 |
| method | `WidgetTrait.validate` | `(self, obj: object, value: object) -> object` | `anywidget/_traits.py` | L60-L65 |
| class | `VirtualFileContents` | `(object)` | `anywidget/_file_contents.py` | L21-L47 |
| class | `FileContents` | `(object)` | `anywidget/_file_contents.py` | L50-L136 |
| class | `AnyWidgetMagics` | `(Magics)` | `anywidget/_cellmagic.py` | L14-L43 |
| function | `widget` (experimental) | `(*, esm, css=None, **kwargs) -> Callable[[T], T]` | `anywidget/experimental.py` | L22-L52 |
| function | `dataclass` (experimental) | `(cls=None, *, esm, css=None, **dataclass_kwargs) -> Callable[[T], T]` | `anywidget/experimental.py` | L68-L111 |
| function | `command` (experimental) | `(cmd: T) -> T` | `anywidget/experimental.py` | L123-L138 |
| constant | `_BINARY_TYPES` | `(memoryview, bytearray, bytes)` | `anywidget/_util.py` | L12 |
| constant | `_WIDGET_MIME_TYPE` | `"application/vnd.jupyter.widget-view+json"` | `anywidget/_util.py` | L13 |
| constant | `_PROTOCOL_VERSION` | `"2.1.0"` | `anywidget/_util.py` | L14-L16 |
| constant | `_ESM_KEY` | `"_esm"` | `anywidget/_util.py` | L18 |
| constant | `_CSS_KEY` | `"_css"` | `anywidget/_util.py` | L19 |
| constant | `_ANYWIDGET_ID_KEY` | `"_anywidget_id"` | `anywidget/_util.py` | L17 |
| constant | `_DEFAULT_ESM` | `str` (多行 ESM 字符串) | `anywidget/_util.py` | L20-L32 |
| function | `remove_buffers` | `(state: object) -> tuple[Any, list[list], list[memoryview]]` | `anywidget/_util.py` | L96-L124 |
| function | `put_buffers` | `(state: dict, buffer_paths: list, buffers: list[memoryview]) -> None` | `anywidget/_util.py` | L127-L143 |
| function | `in_colab` | `() -> bool` | `anywidget/_util.py` | L146-L148 |
| function | `repr_mimebundle` | `(model_id: str, repr_text: str) -> tuple[dict, dict]` | `anywidget/_util.py` | L287-L300 |
| function | `try_file_contents` | `(x: object) -> FileContents \| VirtualFileContents \| None` | `anywidget/_util.py` | L262-L284 |
| interface | `AnyModel` | `(TS)` | `packages/types/index.ts` | L20-L34 |
| interface | `RenderProps` | `(TS)` | `packages/types/index.ts` | L57-L63 |
| interface | `InitializeProps` | `(TS)` | `packages/types/index.ts` | L69-L73 |
| type | `AnyWidget` | `WidgetDef \| (() => Awaitable<WidgetDef>)` | `packages/types/index.ts` | L84-L86 |
| type | `Experimental` | `{ invoke: <T>(...) => Promise<[T, DataView[]]> }` | `packages/types/index.ts` | L36-L45 |
| interface | `Host` | `(TS)` | `packages/types/index.ts` | L52-L55 |
| class | `Runtime` | `(TS)` | `packages/anywidget/src/runtime.ts` | L19-L123 |
| class | `WidgetBinding` | `(TS)` | `packages/anywidget/src/binding.ts` | L21-L121 |
| function | `modelProxy` | `(model, context) => AnyModel` | `packages/anywidget/src/model-proxy.ts` | L17-L35 |
| function | `observe` | `(model, name, {signal}) => Accessor` | `packages/anywidget/src/observe.ts` | L4-L16 |
| function | `loadCss` | `(css, anywidgetId) => Promise<void>` | `packages/anywidget/src/load.ts` | L60-L64 |
| function | `loadWidget` | `(esm, anywidgetId) => Promise<AnyWidget>` | `packages/anywidget/src/load.ts` | L103-L115 |
| function | `createHost` | `(model, {signal}) => Host` | `packages/anywidget/src/host.ts` | L9-L56 |
| function | `invoke` | `<T>(model, name, msg?, options?) => Promise<[T, DataView[]]>` | `packages/anywidget/src/invoke.ts` | L9-L40 |

---

## Directory Structure

### Python 包 `anywidget/`

```text
anywidget/
├── __init__.py              # 公共 API 导出
├── _version.py              # 版本信息
├── widget.py                # AnyWidget 基类（ipywidgets.DOMWidget 子类）
├── _descriptor.py           # MimeBundleDescriptor + ReprMimeBundle（协议层核心）
├── _protocols.py            # TypedDict 和 Protocol 定义
├── _traits.py               # WidgetTrait（widget 组合支持）
├── _file_contents.py        # FileContents + VirtualFileContents（文件监视）
├── _util.py                 # 工具函数、常量、buffer 处理、mimebundle
├── _cellmagic.py            # %%vfile cell magic
├── experimental.py          # @widget、@dataclass、@command 装饰器
├── py.typed                 # PEP 561 标记
└── nbextension/
    └── extension.js         # Jupyter Notebook 扩展入口（RequireJS 配置）
```

### TypeScript 类型包 `packages/types/`

```text
packages/types/
├── index.ts                 # 唯一源文件，所有类型定义
├── index.test-d.ts          # 类型测试
├── package.json
├── tsconfig.json
├── README.md
├── LICENSE
└── CHANGELOG.md
```

> 注：`packages/types/` 没有 `src/` 子目录，`index.ts` 直接位于包根目录。

### JS 核心运行时 `packages/anywidget/src/`

```text
packages/anywidget/src/
├── index.js                 # AMD 入口：define(["@jupyter-widgets/base"], create)
├── plugin.js                # JupyterLab 插件注册
├── widget.ts                # 工厂函数：创建 AnyModel/AnyView 类
├── runtime.ts               # Runtime 类：ESM/CSS 加载、响应式更新、视图管理
├── binding.ts               # WidgetBinding 类 + BindingManager（widget 定义绑定）
├── model-proxy.ts            # modelProxy 函数 + INITIALIZE_MARKER
├── load.ts                  # ESM/CSS 加载（loadCss, loadWidget, loadEsm）
├── observe.ts               # SolidJS 响应式 observe 工具
├── host.ts                  # Host API 实现（getWidget/getModel）
├── invoke.ts                # 命令调用（experimental.invoke）
├── widget-ref.ts            # Widget 引用字符串解析
└── util.ts                  # 工具函数（assert, safeCleanup, promiseWithResolvers）
```

### Vite 插件 `packages/vite/`

```text
packages/vite/
├── index.js                 # Vite 插件主体（dev serve 模式）
├── hmr.js                   # HMR 运行时模板
├── package.json
├── tsconfig.json
├── README.md
├── LICENSE
└── CHANGELOG.md
```

---

## Python-JS Communication Protocol

### 通道建立

1. Python 端通过 `comm.create_comm(target_name="jupyter.widget")` 创建标准 Jupyter Widget comm 通道（`anywidget/_descriptor.py#L127`）。
2. Comm 创建时 metadata 包含 `{"version": "2.1.0"}`（`anywidget/_descriptor.py#L129`）。
3. 初始 data 包含固定字段（model/view 名称、模块、版本）加上用户 state 和 buffer_paths（`anywidget/_descriptor.py#L130-L142`）。

### 消息类型

| method | 方向 | 说明 |
|--------|------|------|
| `"update"` | Python↔JS | 同步状态变更，包含 `state` 和可选 `buffer_paths`/`buffers` |
| `"request_state"` | JS→Python | 请求 Python 端发送完整状态 |
| `"anywidget-command"` (custom) | JS→Python | 通过 `experimental.invoke()` 调用 Python 端 @command 标记的函数 |
| `"anywidget-command-response"` (custom) | Python→JS | 命令调用响应，包含 `id` 和 `response` |

### 状态同步流程

**Python → JS（trait 变更）**：
1. 用户修改 Python trait 值（如 `widget.value = 42`）
2. ipywidgets/psygnal/traitlets 观察者触发 send_state（`anywidget/_descriptor.py#L533`）
3. send_state 调用 `_get_state()` 获取当前状态，`_replace_widget_refs()` 序列化 widget 引用，`remove_buffers()` 分离二进制数据（`anywidget/_descriptor.py#L427`）
4. 通过 `comm.send({method: "update", state, buffer_paths}, buffers)` 发送
5. JS 端 ipywidgets 基础框架接收并更新 model 属性，触发 `change:` 事件

**JS → Python（model.set + save_changes）**：
1. JS 端调用 `model.set("key", value); model.save_changes()`
2. ipywidgets JS 框架通过 comm 发送 `{method: "update", state: {...}}`
3. Python 端 `_handle_msg` 接收，`put_buffers()` 还原二进制数据，调用 `_set_state(obj, state)`（`anywidget/_descriptor.py#L451`）
4. 默认的 `_default_set_state` 通过 `setattr` 设置属性；对于 ipywidgets AnyWidget，traitlets 自动处理

### 二进制数据处理

- 发送端：`_separate_buffers` 递归遍历 state，将 memoryview/bytearray/bytes 移至独立 buffers 列表，原位置替换为 None（list）或删除键（dict），记录 buffer_paths（`anywidget/_util.py#L40`）
- 接收端：`put_buffers` 按 buffer_paths 逐层遍历，将 buffers 放回对应位置（`anywidget/_util.py#L127`）
- JS 端 serialize 使用 `structuredClone()` 处理二进制（`packages/anywidget/src/widget.ts#L58`）

### Widget 组合引用

- WidgetTrait 值在同步时序列化为 `"anywidget:<model_id>"` 字符串（`anywidget/_traits.py#L10`）
- JS 端通过 `parseWidgetRef` 解析前缀获取 model_id（`packages/anywidget/src/widget-ref.ts#L3`）
- 通过 `model.widget_manager.get_model(modelId)` 获取子 model 实例（`packages/anywidget/src/host.ts#L14`）

---

## ESM Module System

### _esm/_css 属性解析

`_esm` 和 `_css` 支持四种输入形式，解析优先级（`anywidget/widget.py#L65`，`anywidget/_util.py#L214`）：
1. **虚拟文件字符串**（`vfile:<name>`）：从 `_VIRTUAL_FILES` WeakValueDictionary 查找 VirtualFileContents
2. **pathlib.Path 对象**：直接作为文件路径
3. **单行带后缀的字符串**：正则匹配 `[a-zA-Z0-9]\.[a-zA-Z0-9]+$` 判定为文件路径，转为绝对 Path
4. **URL 字符串**（http:// 或 https:// 开头）：返回 None，作为远程 URL 处理
5. **多行字符串**（含换行符）：返回 None，作为内联 ESM/CSS 代码

### 文件监视与 HMR

- 环境变量 `ANYWIDGET_HMR=1` 启用热更新（`anywidget/_util.py#L181`）
- site-packages/dist-packages 中的文件不启动监视线程（`anywidget/_util.py#L186`）
- 需要 `watchfiles` 包（`anywidget/_util.py#L198`）
- FileContents 在后台线程中使用 watchfiles.watch() 监视文件变更，变更时发射 `changed` 信号（`anywidget/_file_contents.py#L100`）
- changed 信号连接到 ReprMimeBundle.send_state(key)，通过 comm 发送 update 消息到 JS（`anywidget/_descriptor.py#L381`）

### JS 端模块加载

- **内联 ESM**：通过 `Blob + URL.createObjectURL` 创建 Blob URL，使用动态 `import()` 加载后 revokeObjectURL（`packages/anywidget/src/load.ts#L70`）
- **远程 URL**：直接 `import(esm)`（webpackIgnore/vite-ignore 注释）（`packages/anywidget/src/load.ts#L67`）
- **Vite 开发模式**：Vite 插件将 `?anywidget` 查询参数的请求转换为 HMR 模板，使用 `import.meta.hot.accept()` 实现热更新（`packages/vite/index.js`，`packages/vite/hmr.js`）

### JS 端响应式更新

Runtime 使用 SolidJS 响应式系统实现 ESM/CSS 热更新（`packages/anywidget/src/runtime.ts#L44`）：
- `observe()` 将 model trait 包装为 SolidJS Accessor（signal），监听 `change:key` 事件自动更新
- `createEffect` 自动追踪依赖，CSS/ESM 变更时重新执行
- ESM 变更时：AbortController 取消前一次加载 → loadWidget 加载新模块 → binding.bind 重新执行 initialize → createView 重新渲染
- 每次 render 调用时清空旧 DOM（`view.$el.empty()`），移除旧监听器（`model.off(null, null, view)`），创建新 AbortController

### ESM 默认导出格式约定

ESM 模块需满足以下格式之一（`packages/types/index.ts#L79`，`packages/anywidget/src/load.ts#L103`）：

```javascript
// 格式1（推荐）：export default 对象
export default {
  async initialize({ model, signal, experimental }) { /* 可选，返回 cleanup 或 exports */ },
  async render({ model, el, signal, host, experimental }) { /* 必需，返回 cleanup */ }
}

// 格式2：export default 函数（返回 Promise<WidgetDef>）
export default async function() {
  return { initialize, render };
}
```

### CSS 加载方式

- **CSS 文本**：注入 `<style id="_anywidget_id">` 标签到 document.head，热更新时替换 textContent（`packages/anywidget/src/load.ts#L45`）
- **CSS URL**：注入 `<link rel="stylesheet" href="...">` 标签，热更新时克隆节点替换 href 避免闪烁（`packages/anywidget/src/load.ts#L19`）

---

## 关键导入关系

### Python 模块依赖图

```text
__init__.py
├── widget.py
│   ├── _file_contents.py → psygnal.Signal
│   ├── _util.py
│   ├── _version.py
│   └── experimental.py
│       ├── _descriptor.py
│       │   ├── _file_contents.py
│       │   ├── _util.py
│       │   └── _version.py
│       └── psygnal
├── _protocols.py
│   └── _descriptor.py (TYPE_CHECKING)
├── _traits.py
│   └── _descriptor.py (_try_get_model_id, _WIDGET_REF_PREFIX)
└── _cellmagic.py
    └── _file_contents.py (_VIRTUAL_FILES, VirtualFileContents)
```

### JS 模块依赖图

```text
index.js → widget.ts
           ├── binding.ts → model-proxy.ts, util.ts
           ├── runtime.ts → binding.ts, host.ts, invoke.ts, load.ts, observe.ts, util.ts
           │              ├── host.ts → binding.ts, invoke.ts, model-proxy.ts, widget-ref.ts
           │              ├── invoke.ts (uuid)
           │              ├── load.ts → util.ts (assert)
           │              └── observe.ts (solid-js)
           └── util.ts

plugin.js → widget.ts
```
