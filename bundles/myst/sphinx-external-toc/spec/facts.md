---
type: spec
title: sphinx-external-toc 源码事实清单
description: sphinx-external-toc 源码事实清单
tags:
- sphinx-external-toc
- spec
- facts
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
status: stable
stale_after: '2027-08-23'
sources:
- id: sphinx-external-toc-source
  resource: /references/etoc-source.md
  title: sphinx-external-toc etoc-source
---

# sphinx-external-toc 源码事实清单

> R 阶段采集的零推测事实，每个事实可通过源码路径验证。

## 项目元数据

- F-001: `__version__ = "1.1.0"` 定义于 `sphinx_external_toc/__init__.py` L8
- F-002: `setup(app)` 首先调用 `app.setup_extension("sphinx_multitoc_numbering")` 依赖另一扩展
- F-003: `setup(app)` 返回字典 `{"version": __version__, "parallel_read_safe": True}`（无 parallel_write_safe）
- F-004: 通过 `extensions = ['sphinx_external_toc']` 方式注册（非 entry point）

## 核心配置项

- F-005: `external_toc_path` 默认值 `"_toc.yml"`，重建条件 `"env"`
- F-006: `external_toc_exclude_missing` 默认值 `False`，重建条件 `"env"`
- F-007: `use_multitoc_numbering` 默认值 `True`，重建条件 `"env"`（try-except 注册，兼容 JupyterBook 已注册情况）

## 事件钩子连接

- F-008: `config-inited` 事件连接 `parse_toc_to_env`，priority=900（在 merge_source_suffix priority 800 之后）
- F-009: `env-get-outdated` 事件连接 `add_changed_toctrees`
- F-010: `build-finished` 事件连接 `ensure_index_file`
- F-011: 通过 `app.add_directive("tableofcontents", TableofContents)` 注册自定义指令
- F-012: 通过 `app.add_transform(InsertToctrees)` 注册文档树变换（Transform），default_priority=100

## Collector 机制

- F-013: `disable_builtin_toctree_collector(app)` 通过 `gc.get_objects()` 遍历所有对象，找到 `TocTreeCollector` 实例并调用 `obj.disable(app)` 禁用内置 toctree collector
- F-014: 禁用逻辑检查 `obj.listener_ids is None` 避免重复禁用（sphinx-autobuild 场景）
- F-015: 通过 `app.add_env_collector(TocTreeCollectorWithStyles)` 注册自定义 collector
- F-016: `TocTreeCollectorWithStyles` 继承自 `TocTreeCollector`，覆写 `assign_section_numbers()` 方法

## 编号样式（TocTreeCollectorWithStyles）

- F-017: 支持 5 种编号样式：`numerical`（数字）、`romanupper`（大写罗马）、`romanlower`（小写罗马）、`alphaupper`（大写字母）、`alphalower`（小写字母）
- F-018: 每种样式有独立计数器：`__numerical_count`、`__romanupper_count`、`__romanlower_count`、`__alphaupper_count`、`__alphalower_count`
- F-019: `restart_numbering` 选项控制是否重置编号计数器，默认值 `None`（根据 `use_multitoc_numbering` 配置决定）
- F-020: `style` 字段可以是字符串或列表（多级编号样式），由 `validate_style` 验证器验证

## 数据模型（api.py）

- F-021: `FileItem(str)` — 文件路径项，POSIX 格式，相对于源目录，可带或不带扩展名
- F-022: `GlobItem(str)` — glob 模式项
- F-023: `UrlItem` 是 dataclass，包含字段 `url: str`（验证匹配 `URL_PATTERN = r".+://.*"`）和 `title: Optional[str]`
- F-024: `TocTree` 是 dataclass，字段包括：
  - `items: List[Union[GlobItem, FileItem, UrlItem]]`
  - `caption: Optional[str]`（kw_only）
  - `hidden: bool = True`（kw_only，默认隐藏）
  - `maxdepth: int = -1`（kw_only）
  - `numbered: Union[bool, int] = False`（kw_only）
  - `reversed: bool = False`（kw_only）
  - `titlesonly: bool = False`（kw_only）
  - `style: Union[List[str], str] = "numerical"`（kw_only）
  - `restart_numbering: Optional[bool] = None`（kw_only）
- F-025: `Document` 是 dataclass，字段：`docname: str`、`subtrees: List[TocTree]`、`title: Optional[str]`
- F-026: `Document.child_files()` 返回所有子文件项（排除glob/url）
- F-027: `Document.child_globs()` 返回所有子glob项
- F-028: `SiteMap(MutableMapping)` 是文档名到 Document 的映射，以 `_docs: Dict[str, Document]` 存储
- F-029: `SiteMap.root` 属性返回根文档
- F-030: `SiteMap.meta` 属性返回元数据字典
- F-031: `SiteMap.__delitem__` 禁止删除根文档（断言 `docname != self._root.docname`）
- F-032: `SiteMap.as_json()` 序列化为 JSON 字典，包含 `root`、`documents`、`meta`、可选 `file_format`
- F-033: `SiteMap.get_changed(previous)` 对比两个 sitemap 返回变更文档集合

## 解析器（parsing.py）

- F-034: YAML 键名常量：`ROOT_KEY = "root"`、`FILE_KEY = "file"`、`GLOB_KEY = "glob"`、`URL_KEY = "url"`、`FILE_FORMAT_KEY = "format"`
- F-035: 默认子树键 `DEFAULT_SUBTREES_KEY = "subtrees"`，默认条目键 `DEFAULT_ITEMS_KEY = "entries"`
- F-036: `TOCTREE_OPTIONS` 元组包含 8 个选项：caption、hidden、maxdepth、numbered、reversed、titlesonly、style、restart_numbering
- F-037: `FileFormat` dataclass 定义不同格式的键名映射：`toc_defaults`、`subtrees_keys`、`items_keys`、`default_subtrees_key`、`default_items_key`
- F-038: 预定义三种文件格式：
  - `default`：使用 subtrees/entries 键名
  - `jb-book`：subtrees_keys=("parts",)、items_keys=("chapters",)、default_items_key="sections"、toc_defaults={"titlesonly": True}
  - `jb-article`：default_items_key="sections"、toc_defaults={"titlesonly": True}
- F-039: `parse_toc_yaml(path, encoding)` 读取 YAML 文件并调用 `parse_toc_data()`
- F-040: `parse_toc_data(data)` 验证顶层为 Mapping，根据 `format` 键选择 FileFormat，合并 defaults，递归解析文档树
- F-041: `_parse_doc_item()` 解析单个文档项，支持 shorthand 语法（直接写 items 键而非包在 subtrees 中）
- F-042: 验证规则：每个条目必须且只能包含 file/glob/url 三者之一；glob 和 url 条目不能包含子树
- F-043: `_parse_docs_list()` 递归解析子文档列表，检测文档重复使用
- F-044: `create_toc_dict(site_map, skip_defaults=True)` 将 SiteMap 序列化为 YAML 字典（反向操作）
- F-045: `MalformedError(Exception)` — ToC 文件格式错误异常

## 事件处理（events.py）

- F-046: `parse_toc_to_env(app, config)` 在 config-inited 时解析 _toc.yml：
  - 解析 YAML 为 SiteMap 存入 `config.external_site_map`
  - 将 `master_doc` 改为 sitemap 根文档
  - 若 `external_toc_exclude_missing=True`，将不在 ToC 中的源文件加入 `exclude_patterns`
- F-047: `add_changed_toctrees(app, env, added, changed, removed)` 对比新旧 sitemap，返回变更文档集合
- F-048: `TableOfContentsNode(nodes.Element)` — toctree 插入占位节点
- F-049: `TableofContents(SphinxDirective)` 指令，run() 返回单个 TableOfContentsNode
- F-050: `insert_toctrees(app, doctree)` 核心变换函数：
  - 检测文档中是否有原生 toctree 指令，发出警告
  - 查找 TableOfContentsNode 占位符
  - 根据 SiteMap 为当前文档创建 toctree 节点
  - 处理 FileItem、GlobItem（patfilter）、UrlItem 三种条目类型
  - numbered 值：False→0、True→999、整数→int
  - 若有占位符则替换占位符，否则追加到最后一个 section 或 doctree
  - reversed 选项反转条目顺序
- F-051: `InsertToctrees(SphinxTransform)` default_priority=100（在 DoctreeReadEvent priority 880 之前）
- F-052: `ensure_index_file(app, exception)` 在 build-finished 时，若 master_doc 不是 "index"，生成重定向 index.html
- F-053: `remove_suffix(docname, suffixes)` 移除文档名的文件后缀
- F-054: `create_warning()` 生成支持 suppress_warnings 的警告节点，警告类型前缀为 "etoc"

## CLI 工具（cli.py）

- F-055: 使用 click 库构建 CLI，入口函数 `main()`，version_option 显示版本
- F-056: `parse` 子命令：解析 ToC 文件并输出 JSON 格式的 sitemap
- F-057: `to-project` 子命令：从 ToC 文件生成项目骨架文件（支持 -p 路径、-e 扩展名、-o 覆盖选项）
- F-058: CLI 还使用 `tools.py` 中的 `create_site_from_toc`、`create_site_map_from_path`、`migrate_jupyter_book` 函数

## 默认 _toc.yml 结构（default 格式）

- F-059: 根级别使用 `root:` 指定根文档
- F-060: 文档子树使用 `subtrees:` 列表，每个子树包含 `entries:` 列表和可选选项（caption、hidden 等）
- F-061: Shorthand 语法：文档直接使用 `entries:` 键（省略 subtrees 包裹），选项放入 `options:`
- F-062: 条目格式：`{file: path}`、`{glob: pattern}`、`{url: https://..., title: Text}`
- F-063: 顶层可选 `defaults:` 键设置所有 toctree 的默认选项
- F-064: 顶层可选 `meta:` 键存储元数据
- F-065: 顶层可选 `format:` 键指定格式（default/jb-book/jb-article）
