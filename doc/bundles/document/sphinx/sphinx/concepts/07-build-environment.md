---
type: "concept"
title: "构建环境"
description: "BuildEnvironment详解——文档索引(all_docs/dependencies/included)、doctree缓存(pickle)、domaindata、TOC数据、搜索索引、增量构建机制、ENV_VERSION版本控制"
tags: [core, BuildEnvironment, cache, incremental-build, doctree]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T09:47:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T09:47:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: env-py
    resource: sphinx/environment/__init__.py
    title: "BuildEnvironment class"
  - id: app-init
    resource: /references/sphinx-app-init.md
    title: "Sphinx应用初始化源码"
---

# 构建环境

`BuildEnvironment`（定义在 sphinx/environment/__init__.py）是 Sphinx 构建过程中的核心数据容器。它存储所有文档的索引信息、依赖关系、域数据、TOC结构、搜索索引等，并通过 pickle 序列化到磁盘实现增量构建。理解 BuildEnvironment 是理解 Sphinx 如何"记住"上次构建结果并只重新处理变更文档的关键。

## 核心数据结构

### 文档索引

BuildEnvironment 维护三个核心文档索引字典 [F-025]：

| 属性 | 类型 | 说明 |
|------|------|------|
| `all_docs` | `dict[str, int]` | 所有已读取文档的 docname → 读取时间（微秒时间戳） |
| `dependencies` | `dict[str, set[_StrPath]]` | docname → 该文档依赖的文件集合（如include的文件、图片等） |
| `included` | `dict[str, set[str]]` | docname → 被该文档include的其他docname集合 |
| `reread_always` | `set[str]` | 每次构建都必须重新读取的文档名集合 |

**docname 规范**：所有文档名使用 `/` 分隔的相对路径，不包含源文件后缀。例如 `docs/tutorial.rst` 的 docname 是 `docs/tutorial`。

### doctree 缓存

BuildEnvironment 使用两级缓存来管理解析后的文档树（doctree）[F-026]：

| 属性 | 类型 | 说明 |
|------|------|------|
| `_pickled_doctree_cache` | `dict[str, bytes]` | 内存中pickle序列化的doctree缓存（字节） |
| `_write_doc_doctree_cache` | `dict[str, nodes.document]` | 写入阶段使用的反序列化doctree缓存（文档对象） |

doctree 的持久化路径：`{doctreedir}/{docname}.doctree`（pickle文件）。

- READING阶段：文档解析后pickle序列化到磁盘，同时缓存到内存
- WRITING阶段：从磁盘反序列化（优先从内存缓存获取），应用PostTransform后写入输出

### TOC 数据

| 属性 | 类型 | 说明 |
|------|------|------|
| `titles` | `dict[str, nodes.title]` | docname → 文档标题节点 |
| `longtitles` | `dict[str, nodes.title]` | docname → 长标题（可能通过title指令设置的不同值） |
| `tocs` | `dict[str, nodes.bullet_list]` | docname → 目录树（bullet_list节点） |
| `toc_num_entries` | `dict[str, int]` | docname → TOC中的实际条目数（用于决定是否显示侧边栏） |
| `toc_secnumbers` | `dict[str, dict[str, tuple[int, ...]]]` | docname → {sectionid → 章节编号元组} |
| `toc_fignumbers` | `dict[str, dict[str, dict[str, tuple[int, ...]]]]` | docname → {figtype → {figureid → 编号元组}} |
| `toctree_includes` | `dict[str, list[str]]` | docname → 该文档通过toctree包含的子文档列表 |
| `files_to_rebuild` | `dict[str, set[str]]` | docname → 依赖该文档的其他文档集合（反向依赖） |
| `glob_toctrees` | `set[str]` | 使用了 `:glob:` 选项的toctree所在文档 |
| `numbered_toctrees` | `set[str]` | 使用了 `:numbered:` 选项的toctree所在文档 |

### 域数据

| 属性 | 类型 | 说明 |
|------|------|------|
| `domaindata` | `dict[str, dict[str, Any]]` | domainname → 域专属数据字典（各Domain自行管理结构） |
| `domains` | `_DomainsContainer` | 所有已注册Domain的实例容器 |

每个 Domain 在 `domaindata[domain.name]` 中存储自己的交叉引用数据，例如 Python域存储所有 `py:func`、`py:class` 等对象的位置信息。

### 文件资源

| 属性 | 类型 | 说明 |
|------|------|------|
| `images` | `FilenameUniqDict` | 图片路径 → (引用文档集合, 唯一文件名) |
| `dlfiles` | `DownloadFiles` | 下载文件 → (引用文档集合, 目标路径) |
| `original_image_uri` | `dict[_StrPath, str]` | 图片原始URI映射 |
| `metadata` | `dict[str, dict[str, Any]]` | docname → 文档元数据（从文件开头的field_list提取） |

### 搜索索引

BuildEnvironment 内置全文搜索索引的数据收集 [F-027]：

| 属性 | 类型 | 说明 |
|------|------|------|
| `_search_index_titles` | `dict[str, str\|None]` | docname → 标题文本 |
| `_search_index_filenames` | `dict[str, str]` | docname → 文件名 |
| `_search_index_mapping` | `dict[str, set[str]]` | 词干 → 包含该词的docname集合 |
| `_search_index_title_mapping` | `dict[str, set[str]]` | 标题词干 → docname集合 |
| `_search_index_all_titles` | `dict[str, list[tuple[str, str\|None]]]` | docname → 所有子标题列表 |
| `_search_index_index_entries` | `dict[str, list[tuple[str,str,str]]]` | docname → 索引条目列表 |
| `_search_index_objtypes` | `dict[tuple[str,str], int]` | (domain, objtype) → 类型ID |
| `_search_index_objnames` | `dict[int, tuple[str,str,str]]` | 类型ID → (domain, type, 本地化名称) |

搜索索引在READING阶段收集数据，在Builder.finish()阶段序列化为 `searchindex.js`。

### 临时上下文

| 属性 | 类型 | 说明 |
|------|------|------|
| `current_document` | `_CurrentDocument` | 当前正在读取的文档上下文 |
| `ref_context` | `dict[str, Any]` | 交叉引用上下文（如当前模块/类名） |

## ENV_VERSION 与缓存失效

```python
ENV_VERSION = 66
```

`ENV_VERSION` 是环境数据结构版本号 [F-028]。每当 BuildEnvironment 的属性结构发生变化（新增/删除/修改字段），此版本号递增。加载pickle缓存时，如果版本号不匹配，旧缓存被丢弃，强制全量重建。

配置状态也会影响缓存判断，使用以下常量：

| 常量 | 值 | 含义 |
|------|---|------|
| `CONFIG_UNSET` | -1 | 未检查 |
| `CONFIG_OK` | 1 | 配置未变化，可使用缓存 |
| `CONFIG_NEW` | 2 | 新建配置（首次构建） |
| `CONFIG_CHANGED` | 3 | 配置项值变化 |
| `CONFIG_EXTENSIONS_CHANGED` | 4 | 扩展列表变化 |

`CONFIG_CHANGED_REASON` 字典提供了人类可读的原因文本。

## 生命周期

### 创建新环境

当 `freshenv=True` 或 pickle 文件不存在或版本不匹配时，创建全新的 BuildEnvironment：

```python
def __init__(self, app: Sphinx) -> None:
    self._app = app
    self.doctreedir = app.doctreedir
    self.srcdir = app.srcdir
    self.config = None  # 在_post_init_env中设置
    self.events = app.events
    self.project = app.project
    self.version = _get_env_version(app.extensions)
    self.settings = default_settings.copy()
    # ... 初始化所有字典/集合为空
    self.domains = _DomainsContainer._from_environment(self, registry=app.registry)
    self.setup(app)
```

`setup()` 方法验证版本一致性和源目录一致性，并恢复project状态。

### 加载现有环境

从pickle文件加载时，`__setstate__` 恢复所有数据，然后调用 `setup(app)` 进行验证。不可序列化的属性（`_app`、`domains`、`events`）在 `__getstate__` 中被清除，加载后重新绑定。

### 缓存检查流程

`Builder.build_update()` 中判断哪些文档需要重建：

1. 加载/创建 BuildEnvironment
2. 检查 config_status，如 CONFIG_CHANGED 且 rebuild级别为'env'，标记所有文档过时
3. emit('env-get-outdated', ...) 让扩展判断额外过时文档
4. 遍历所有文档，比对文件mtime和all_docs中的时间戳
5. 收集依赖链上需要重建的文档（dependencies/files_to_rebuild）

## 核心方法

### 文档读写

```python
def get_doctree(self, docname: str, condition=None) -> nodes.document:
    """获取文档的doctree，优先从缓存读取"""

def write_doctree(self, docname: str, doctree: nodes.document) -> None:
    """将doctree pickle序列化到磁盘"""

def get_and_resolve_doctree(self, docname: str, builder: Builder,
                            doctree: nodes.document | None = None,
                            prune_toctrees: bool = True,
                            includehidden: bool = False) -> nodes.document:
    """获取doctree并应用resolve阶段的处理（PostTransforms等）"""
```

### 文档发现

```python
def find_files(self, config: Config, builder: Builder) -> None:
    """发现所有源文件，更新all_docs"""

def get_outdated_files(self, config_changed: bool) -> tuple[set[str], set[str], set[str]]:
    """返回(added, changed, removed)文档集合"""
```

### 路径工具

```python
def doc2path(self, docname: str, suffix: str | None = None,
             base: bool = True) -> str:
    """将docname转换为文件系统路径"""

def relfn2path(self, filename: str, docname: str) -> tuple[str, str]:
    """将相对文件名转换为绝对路径和docname相对路径"""
```

## 序列化策略

BuildEnvironment 的pickle序列化策略 [F-029]：

1. `__getstate__` 移除不可序列化属性：`_app`、`domains`、`events`
2. 清除内存缓存：`_pickled_doctree_cache`、`_write_doc_doctree_cache`
3. 清除builder相关属性
4. 保留所有纯数据字典/集合
5. 加载后通过 `setup(app)` 重新绑定app/domains/events

Domain 的 `merge_domaindata()` 方法支持并行构建时合并子进程的domaindata。

## default_settings

BuildEnvironment 为 docutils 解析器预设了一组默认设置 [F-030]：

```python
default_settings = {
    'auto_id_prefix': 'id',
    'image_loading': 'link',
    'embed_stylesheet': False,
    'cloak_email_addresses': True,
    'pep_base_url': 'https://peps.python.org/',
    'rfc_base_url': 'https://datatracker.ietf.org/doc/html/',
    'input_encoding': 'utf-8-sig',
    'doctitle_xform': False,
    'sectsubtitle_xform': False,
    'section_self_link': False,
    'halt_level': 5,
    'file_insertion_enabled': True,
    'smartquotes_locales': [],
}
```

注意 `doctitle_xform` 和 `sectsubtitle_xform` 被设置为 `False`，因为 Sphinx 使用自己的 Transform 处理标题和章节，而不是 docutils 的默认行为。`halt_level=5` 意味着遇到SEVERE级别以上的错误才会停止构建。

## 设计洞察

1. **Pickle作为数据库**：BuildEnvironment 本质上是一个基于pickle文件的轻量级文档数据库，存储构建之间需要持久化的所有信息。这使得增量构建成为可能。

2. **版本号防御**：`ENV_VERSION` 是一个简单但有效的缓存失效机制——任何对数据结构的修改都通过递增版本号强制全量重建，避免了复杂的迁移逻辑。

3. **两级缓存**：磁盘缓存（pickle文件）+内存缓存（dict）的两级设计平衡了内存占用和构建速度。读取阶段将所有doctree加载到内存，写入阶段优先从内存获取。

4. **反向依赖追踪**：`files_to_rebuild` 和 `dependencies` 形成双向依赖图，当一个文件变更时，所有依赖它的文件也被标记为需要重建。

5. **Domain隔离**：各Domain的交叉引用数据隔离在 `domaindata` 字典中，Domain基类提供 `clear_doc()`、`merge_domaindata()`、`process_doc()` 等钩子供各语言域管理自己的数据生命周期。

## 相关概念

- [Sphinx应用类](03-application-class.md)
- [架构总览](02-architecture-overview.md)
- [Builder 构建器体系](10-builder-system.md)
- [Domain 域系统](09-domain-system.md)
