---
okf_version: "0.2"
type: "concept"
title: WebSupport API 详解
description: WebSupport类的完整API参考——构造参数、构建方法、文档获取、评论CRUD、投票、搜索、审核等所有公开方法
tags: [sphinx-websupport, api, websupport-class, public-methods]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T15:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T17:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: websupport-source
    resource: /references/websupport-source.md
---

# WebSupport API 详解

`WebSupport` 类是 sphinxcontrib-websupport 的唯一入口类，定义在 `sphinxcontrib.websupport.core` 模块中，通过 `sphinxcontrib.websupport` 包直接导出。所有与 websupport 的交互都通过这个类进行。

## 构造函数

```python
WebSupport(
    srcdir=None,              # 构建时必需：文档源目录
    builddir='',              # 构建输出根目录
    datadir=None,             # 数据目录，默认 builddir/data
    staticdir=None,           # 静态文件目录，默认 builddir/static
    doctreedir=None,          # doctree目录，默认 builddir/doctrees
    search=None,              # 搜索引擎：None/'null'/'whoosh'/'xapian'或BaseSearch实例
    storage=None,             # 存储后端：None(SQLite)/连接URI/StorageBackend实例
    buildername='websupport', # Sphinx builder名称
    confoverrides=None,       # Sphinx conf.py覆盖项
    status=sys.stdout,        # 构建状态输出流
    warning=sys.stderr,       # 构建警告输出流
    moderation_callback=None, # 审核回调函数
    allow_anonymous_comments=True,  # 是否允许匿名评论
    docroot='',               # Web文档URL前缀
    staticroot='static',      # Web静态文件URL前缀
)
```

### 参数分类

**目录参数**（影响文件系统路径）：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `srcdir` | `None` | 文档源目录（含conf.py），构建时必须提供 |
| `builddir` | `''` | 构建输出根目录，所有产物写入其子目录 |
| `datadir` | `builddir/data` | pickle数据和搜索索引存放目录 |
| `staticdir` | `builddir/static` | 静态资源（CSS/JS/图片）输出目录 |
| `doctreedir` | `builddir/doctrees` | Sphinx doctree缓存目录 |

**后端参数**（控制存储和搜索）：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `search` | `None`（即'null'） | 搜索适配器：字符串名或BaseSearch实例 |
| `storage` | `None`（即SQLite） | 存储后端：URI字符串或StorageBackend实例 |

**Web参数**（影响生成的URL）：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `docroot` | `''` | 文档页面URL前缀，如`'/docs'` |
| `staticroot` | `'static'` | 静态文件URL前缀，如`'/static'` |

**行为参数**：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `moderation_callback` | `None` | 新评论待审核时的回调函数 `callback(comment_dict)` |
| `allow_anonymous_comments` | `True` | 未提供username时是否允许评论（用户名设为'Anonymous'） |
| `confoverrides` | `None` | 传递给Sphinx的conf.py覆盖字典 |

### 两种初始化模式

**构建模式**（必须提供 `srcdir`）：
```python
support = WebSupport(srcdir='./docs', builddir='./websupport_data', search='whoosh')
support.build()  # 执行构建
```

**运行模式**（不需要 `srcdir`）：
```python
support = WebSupport(builddir='./websupport_data', docroot='/docs', staticroot='/static')
doc = support.get_document('index')  # 服务请求
```

## 构建方法

### build()

```python
support.build()
```

执行文档构建。要求 `srcdir` 已设置，否则抛出 `RuntimeError('No srcdir associated with WebSupport object')`。

构建流程：
1. 创建 `Sphinx(srcdir, srcdir, outdir, doctreedir, 'websupport', confoverrides, ...)` 实例
2. 调用 `app.builder.set_webinfo(staticdir, staticroot, search, storage)` 注入后端
3. 调用 `storage.pre_build()` 准备数据库会话
4. 调用 `app.build()` 执行Sphinx构建（序列化所有文档、注册节点、建立搜索索引）
5. 调用 `storage.post_build()` 提交事务、关闭会话

## 文档获取方法

### get_document(docname, username='', moderator=False)

```python
document = support.get_document('index', username='user1', moderator=False)
```

加载并返回一个文档字典。`docname` 通常从请求URL路径获取（如 `index`、`tutorial/intro`）。

**返回字典结构**：

| Key | 类型 | 说明 |
|-----|------|------|
| `body` | str | 文档主体HTML |
| `title` | str | 文档标题 |
| `sidebar` | str | 侧边栏HTML（从Sphinx模板渲染） |
| `relbar` | str | 导航栏HTML（相关文档链接） |
| `css` | str | CSS `<link>` 标签 |
| `script` | str | JavaScript标签（含COMMENT_OPTIONS + COMMENT_METADATA + 页面原有脚本） |

**异常**：文档不存在时抛出 `DocumentNotFoundError`。

**目录文档处理**：如果 `docpath` 是目录（如 `tutorial/`），自动加载 `tutorial/index.fpickle`。

### get_globalcontext()

```python
global_ctx = support.get_globalcontext()
```

加载并缓存全局上下文 pickle（`globalcontext.pickle`）。包含全局CSS/JS配置等。首次调用时从文件加载并缓存到 `self._globalcontext`，后续调用直接返回缓存。

### get_search_results(q)

```python
results = support.get_search_results('install guide')
```

执行搜索查询，返回与 `get_document()` 格式兼容的文档字典（可直接用于渲染搜索结果页）。内部调用 `self.search.query(q)` 获取结果，然后通过 `searchresults.html` Jinja2模板渲染为HTML。

## 评论方法

### add_comment(text, node_id='', parent_id='', displayed=True, username=None, time=None, proposal=None, moderator=False)

```python
comment = support.add_comment(
    text='This paragraph is confusing.',
    node_id='s123456',
    username='reader1',
    proposal=None,
)
```

添加一条评论。返回评论字典（与 `get_data()` 返回的评论格式相同）。

**参数说明**：
- `text`：评论文本（会通过docutils的 `publish_parts` 从reST转为HTML）
- `node_id`：评论所属的段落节点ID（顶级评论必填）
- `parent_id`：父评论ID（回复评论必填，与node_id二选一）
- `displayed`：是否立即可见（False表示需审核）
- `username`：用户名，None时若允许匿名则设为'Anonymous'，否则抛 `UserNotAuthorizedError`
- `time`：评论时间，默认当前时间
- `proposal`：提议修改文本（提供则生成HTML diff）
- `moderator`：是否为审核员操作

**行为细节**：
- 如果 `node_id` 和 `proposal` 都提供，会用 `CombinedHtmlDiff` 生成提议修改的HTML diff
- 如果回复的父评论 `displayed=False`，抛出 `CommentNotAllowedError`（不能回复未审核通过的评论）
- 如果 `displayed=False` 且设置了 `moderation_callback`，回调函数会被调用
- 返回的字典包含额外的 `original_text` 字段（原始reST文本）

### get_data(node_id, username=None, moderator=False)

```python
data = support.get_data('s123456', username='reader1', moderator=True)
# data = {'source': 'original paragraph text...', 'comments': [...]}
```

获取指定节点的原文和评论树。`source` 是段落的原始reST文本，`comments` 是嵌套评论列表。

**评论字典结构**（每个评论）：

| Key | 类型 | 说明 |
|-----|------|------|
| `text` | str | 评论HTML内容 |
| `username` | str | 评论者用户名 |
| `id` | int | 评论唯一ID |
| `rating` | int | 当前评分 |
| `age` | int | 评论年龄（秒） |
| `time` | dict | 时间信息（year/month/day/hour/minute/second/iso/delta） |
| `vote` | int | 当前用户投票值（1/-1/0），未提供username时为0 |
| `node` | str | 所属节点ID（顶级评论）或null |
| `parent` | str | 父评论ID或null |
| `children` | list | 子评论列表（递归嵌套） |
| `proposal_diff` | str | 提议修改的HTML diff |
| `displayed` | bool | 是否已通过审核 |

### delete_comment(comment_id, username='', moderator=False)

删除评论。有两种模式：

- **审核员模式**（`moderator=True`）：物理删除评论及其所有后代评论，返回 `True`
- **用户模式**（`moderator=False`）：软删除（username和text替换为`'[deleted]'`），仅当username匹配时成功，返回 `False`

用户模式下如果username不匹配，抛出 `UserNotAuthorizedError`。

### accept_comment(comment_id, moderator=False)

```python
support.accept_comment(comment_id, moderator=True)
```

审核通过一条待审核评论（将 `displayed` 设为True）。非审核员调用抛出 `UserNotAuthorizedError`。

## 投票方法

### process_vote(comment_id, username, value)

```python
support.process_vote(comment_id, 'user1', 1)   # 点赞
support.process_vote(comment_id, 'user1', -1)  # 点踩
support.process_vote(comment_id, 'user1', 0)   # 取消投票
```

处理用户投票。`value` 必须是 `-1`、`0` 或 `1`，否则抛出 `ValueError`。

投票逻辑：
- 如果用户首次投票：创建 `CommentVote` 记录，评论rating加上value
- 如果用户改投：rating加上新旧投票值的差（`value - old_vote`），更新投票记录
- 如果用户取消投票（value=0）：rating减去旧投票值，更新记录

## 工具方法

### update_username(old_username, new_username)

```python
support.update_username('old_name', 'new_name')
```

批量更新用户名。当Web应用的认证系统允许用户改名时，调用此方法同步更新评论和投票记录中的用户名。websupport自身不做用户认证，完全依赖调用方传入username。

## 异常类型

| 异常类 | 触发场景 |
|--------|---------|
| `DocumentNotFoundError` | 请求的docname对应pickle文件不存在 |
| `UserNotAuthorizedError` | 非评论作者尝试删除/审核评论 |
| `CommentNotAllowedError` | 尝试回复未通过审核的评论 |
| `NullSearchException` | 使用NullSearch时调用搜索功能 |

## 内部初始化流程

`__init__` 中的初始化顺序：
1. 设置目录路径（srcdir/builddir/datadir/staticdir/doctreedir）
2. 设置Web虚拟路径（docroot/staticroot，通过strip('/')规范化）
3. 初始化模板系统（`_init_templating`）：Jinja2 FileSystemLoader加载包内templates目录
4. 初始化搜索系统（`_init_search`）：根据search参数查找SEARCH_ADAPTERS注册表或使用传入实例
5. 初始化存储系统（`_init_storage`）：传入StorageBackend实例则直接使用，否则创建SQLAlchemyStorage
6. 初始化全局上下文缓存（`_globalcontext = None`）
7. 创建基础评论选项（`_make_base_comment_options`）：静态URL部分
8. 将 `'sphinxcontrib.websupport.builder'` 自动追加到 `confoverrides['extensions']`

## 相关概念

- [架构总览](02-architecture-overview.md)
- [Builder系统](04-builder-system.md)
- [评论系统](05-comment-system.md)
- [存储后端](06-storage-backend.md)
- [Flask完整集成示例](../examples/flask-integration.md)
