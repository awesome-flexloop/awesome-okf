---
okf_version: "0.2"
type: "concept"
title: 架构总览
description: sphinxcontrib-websupport的双阶段架构——构建时序列化与运行时API的分层设计、核心模块协作关系与数据流
tags: [sphinx-websupport, architecture, builder, storage, search]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T15:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T17:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: websupport-source
    resource: /references/websupport-source.md
---

# 架构总览

## 双阶段架构

sphinxcontrib-websupport 的核心架构是**双阶段（two-phase）设计**：构建阶段（Build Phase）和运行阶段（Runtime Phase）。这两个阶段使用同一个 `WebSupport` 类，但通过不同的参数初始化，执行完全不同的代码路径。

```
┌─────────────────────────────────────────────────────────┐
│                    构建阶段 (build())                    │
│                                                         │
│  ┌──────────┐   ┌──────────────────┐   ┌─────────────┐ │
│  │ reST源文件│──▶│  Sphinx构建引擎   │──▶│ pickle文件  │ │
│  │ (srcdir) │   │  +WebSupportBuilder  │  (.fpickle)  │ │
│  └──────────┘   │  +WebSupportTranslator│  静态资源    │ │
│                 └────────┬─────────┘   │  搜索索引    │ │
│                          │             └─────────────┘ │
│                          ▼                             │
│                 ┌──────────────────┐                   │
│                 │  StorageBackend  │──▶ SQLite数据库    │
│                 │  (SQLAlchemy)    │    (节点元数据)    │
│                 └──────────────────┘                   │
└─────────────────────────────────────────────────────────┘
                           │
                    构建产物（文件+DB）
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  运行阶段 (Web请求处理)                   │
│                                                         │
│  HTTP请求 ──▶ WebSupport API ──▶ pickle加载+DB查询       │
│     │              │                    │                │
│     │              ▼                    ▼                │
│     │         模板上下文           评论/投票数据          │
│     │              │                    │                │
│     │              └──────┬─────────────┘                │
│     │                     ▼                              │
│     │              JSON/HTML响应                          │
│     │                                                   │
│     └──▶ 静态文件 ──▶ static/目录                         │
└─────────────────────────────────────────────────────────┘
```

### 构建阶段详解

构建阶段由 `WebSupport.build()` 触发，执行以下步骤：

1. **创建Sphinx应用实例**：以 `'websupport'` 为builder名称创建 `Sphinx(srcdir, srcdir, outdir, doctreedir, 'websupport', ...)`
2. **注入Web信息**：调用 `app.builder.set_webinfo(staticdir, staticroot, search, storage)` 将存储后端和搜索适配器传递给builder
3. **存储预处理**：调用 `storage.pre_build()` 创建数据库会话
4. **执行Sphinx构建**：`app.build()` 内部遍历所有文档：
   - `WebSupportBuilder.write_doc()` 将每页文档序列化为上下文dict
   - `WebSupportTranslator.dispatch_visit()` 为可评论段落注入注释标记
   - `add_db_node()` 将可评论节点（id, document, source）写入数据库
   - `search.feed()` 将文档文本喂给搜索引擎建索引
5. **存储后处理**：调用 `storage.post_build()` 提交事务、关闭会话
6. **静态文件整理**：`handle_finish()` 将图片/CSS/JS从data目录移动到static目录，拷贝websupport自带的图标和JS文件

构建阶段的关键产出是：
- `data/pickles/*.fpickle`：每页文档的序列化上下文
- `data/globalcontext.pickle`：全局CSS/JS等
- `data/search/`：搜索索引（Whoosh/Xapian）
- `static/`：静态资源目录
- `data/db/websupport.db`：SQLite数据库（节点+评论+投票）

### 运行阶段详解

运行阶段由Web应用对每个HTTP请求调用WebSupport API方法触发：

1. **文档请求**：`get_document(docname, username, moderator)` 加载对应 `.fpickle`，注入评论选项JS和评论元数据JS，返回渲染上下文字典
2. **评论请求**：`get_data(node_id, username, moderator)` 查询数据库，返回节点原文和嵌套评论树
3. **写操作**：`add_comment()`/`process_vote()`/`delete_comment()`/`accept_comment()` 通过StorageBackend操作数据库
4. **搜索请求**：`get_search_results(q)` 委托给Search适配器查询索引，用Jinja2模板渲染搜索结果HTML

## 核心类协作关系

```
                    ┌─────────────┐
                    │  WebSupport  │ (核心门面类)
                    │   (core.py)  │
                    └──────┬──────┘
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │  Storage   │  │   Search   │  │  Templating│
    │  Backend   │  │  Adapter   │  │  (Jinja2)  │
    └─────┬──────┘  └─────┬──────┘  └────────────┘
          │               │
    ┌─────┴──────┐  ┌─────┴──────┐
    │SQLAlchemy  │  │WhooshSearch│
    │Storage     │  │XapianSearch│
    │(默认)      │  │NullSearch  │
    └─────┬──────┘  │(默认)      │
          │         └────────────┘
    ┌─────┴──────┐
    │Node/Comment│  (ORM模型)
    │CommentVote │
    └────────────┘

    ┌──────────────────────────────────────┐
    │        WebSupportBuilder              │ (Sphinx扩展)
    │        (builder.py)                  │
    │  ┌────────────────────────────┐      │
    │  │   WebSupportTranslator     │      │
    │  │   (writer.py)              │      │
    │  └────────────────────────────┘      │
    └──────────────────────────────────────┘
```

### WebSupport 类的三个子系统

`WebSupport.__init__()` 初始化三个核心子系统：

1. **模板系统**（`_init_templating`）：创建 Jinja2 Environment，加载包内 `templates/` 目录中的 `searchresults.html` 模板
2. **搜索系统**（`_init_search`）：根据 `search` 参数查找 SEARCH_ADAPTERS 注册表，动态导入对应的搜索类；默认 `'null'`（NullSearch）
3. **存储系统**（`_init_storage`）：如果传入 StorageBackend 实例则直接使用，否则创建默认的 SQLAlchemyStorage（SQLite数据库）

此外，`__init__` 还自动将 `'sphinxcontrib.websupport.builder'` 添加到 `confoverrides['extensions']` 列表，确保 Sphinx 构建时能发现 WebSupportBuilder。

## 目录结构约定

WebSupport 使用以下目录结构（相对于 builddir）：

```
builddir/
├── data/                    ← outdir（文档数据输出）
│   ├── pickles/             ← 每页 .fpickle 文件
│   ├── globalcontext.pickle ← 全局上下文
│   ├── search/              ← 搜索索引
│   └── db/
│       └── websupport.db    ← SQLite数据库（默认路径）
├── static/                  ← Web可访问的静态资源
│   ├── _static/             ← Sphinx主题CSS/JS/图片 + websupport资源
│   └── _sources/            ← 文档源文件副本
└── doctrees/                ← Sphinx doctree缓存（Web不可访问）
```

各目录路径可在构造函数中自定义：
- `datadir`：覆盖默认 `builddir/data`
- `staticdir`：覆盖默认 `builddir/static`
- `doctreedir`：覆盖默认 `builddir/doctrees`

## Web虚拟路径

除了物理目录路径，WebSupport 还使用两个Web虚拟路径（URL前缀）：

- `docroot`（默认 `''`）：文档页面的URL路径前缀，用于生成评论API端点URL
- `staticroot`（默认 `'static'`）：静态文件的URL路径前缀，用于生成静态资源URL

这两个参数通过 `.strip('/')` 规范化，然后在 `_make_base_comment_options()` 中用于构建：
- 评论API端点URL：`/{docroot}/_add_comment`、`/{docroot}/_get_comments` 等
- 静态资源URL：`/{staticroot}/_static/comment.png` 等

最终这些URL被序列化为 `COMMENT_OPTIONS` JavaScript对象，注入到每个文档页面的 `<script>` 标签中。

## 数据流：一次页面请求

以用户访问 `http://example.com/docs/index` 为例：

1. Web框架（如Flask）路由匹配，调用 `support.get_document('index', username, moderator)`
2. `get_document()` 拼接pickle路径：`datadir/pickles/index.fpickle`
3. 用 `pickle.load()` 反序列化文档上下文字典（body/title/css/script/sidebar/relbar）
4. 调用 `_make_comment_options(username, moderator)` 生成 COMMENT_OPTIONS 的 `<script>` 块
5. 调用 `storage.get_metadata('index', moderator)` 获取该页每个节点的评论数，生成 COMMENT_METADATA 的 `<script>` 块
6. 将两个 `<script>` 块拼接到 `document['script']` 中
7. 返回完整的document字典给Web框架渲染

浏览器加载页面后，`websupport.js`（jQuery插件）：
1. 读取页面中的 `COMMENT_OPTIONS` 和 `COMMENT_METADATA` 全局变量
2. 为每个 `.sphinx-has-comment` 元素（可评论段落）添加评论图标链接
3. 用户点击评论图标时，AJAX请求 `_get_comments?node=s{uid}` 获取评论数据
4. 评论弹窗展示后，用户可以添加评论、投票、回复等

## 前端-后端契约

后端与前端之间通过两个内联 `<script>` 标签传递配置：

**COMMENT_OPTIONS**（请求级，每个用户可能不同）：
```javascript
var COMMENT_OPTIONS = {
    addCommentURL: "/docs/_add_comment",
    getCommentsURL: "/docs/_get_comments",
    processVoteURL: "/docs/_process_vote",
    acceptCommentURL: "/docs/_accept_comment",
    deleteCommentURL: "/docs/_delete_comment",
    commentImage: "/static/_static/comment.png",
    // ... 其他图片URL
    voting: true,
    username: "guest",
    moderator: false
};
```

**COMMENT_METADATA**（文档级，对所有用户相同）：
```javascript
var COMMENT_METADATA = {"s123456": 3, "s123457": 0, ...};
// key是节点DOM id（s{uid}），value是评论数量
```

## 扩展点设计

websupport 提供两个主要扩展点：

### 自定义存储后端

继承 `StorageBackend` 抽象基类，实现11个接口方法，即可接入任何数据库（MongoDB、Redis、PostgreSQL等）。在WebSupport构造时传入实例：

```python
support = WebSupport(builddir='...', storage=MyCustomStorage())
```

### 自定义搜索适配器

继承 `BaseSearch` 抽象基类，实现 `add_document()` 和 `handle_query()` 方法，然后注册到 SEARCH_ADAPTERS 字典，或直接传入实例。

## 相关概念

- [5分钟快速上手](01-getting-started.md)
- [WebSupport API 详解](03-websupport-api.md)
- [Builder系统](04-builder-system.md)
- [评论系统](05-comment-system.md)
- [存储后端](06-storage-backend.md)
