---
okf_version: "0.2"
type: "reference"
type: Reference
title: sphinxcontrib-websupport 源码信源登记
description: sphinxcontrib-websupport v2.0.0 源码路径、版本信息、核心模块清单与公开 API
tags: [sphinx-websupport, source, reference, v2.0.0]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T15:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T17:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: websupport-github
    resource: https://github.com/sphinx-doc/sphinxcontrib-websupport
    title: sphinxcontrib-websupport GitHub 仓库
    author: human:Georg Brandl
  - id: websupport-pypi
    resource: https://pypi.org/project/sphinxcontrib-websupport/
    title: sphinxcontrib-websupport on PyPI
---

# sphinxcontrib-websupport 源码信源登记

## 基本信息

| 属性 | 值 |
|------|-----|
| 项目名 | sphinxcontrib-websupport |
| 版本 | **2.0.0** |
| 描述 | Sphinx 文档的 Web 集成 API——将 Sphinx 文档嵌入 Web 应用，支持评论、投票、搜索 |
| 作者 | Georg Brandl (georg@python.org) |
| 许可证 | BSD-2-Clause |
| Python 要求 | ≥ 3.9 |
| 构建系统 | flit_core (≥3.7) |
| Sphinx 要求 | ≥ 5.0 |
| 官方文档 | <https://www.sphinx-doc.org/> |
| 源码仓库 | <https://github.com/sphinx-doc/sphinxcontrib-websupport> |
| PyPI | <https://pypi.org/project/sphinxcontrib-websupport/> |

## 依赖关系

### 核心依赖

| 依赖 | 用途 |
|------|------|
| jinja2 | 模板引擎，用于搜索结果页面渲染 |
| Sphinx (≥5) | 文档构建引擎 |
| sphinxcontrib-serializinghtml | 提供 PickleHTMLBuilder 基类 |

### 可选依赖

| extra | 依赖 | 用途 |
|-------|------|------|
| whoosh | whoosh + sqlalchemy | Whoosh 全文搜索引擎支持 |
| test | pytest | 测试框架 |

## 源码位置

sphinxcontrib-websupport 源码位于 SpecWeave 仓库的外部依赖目录：

```
external/libs/docs/sphinxcontrib-websupport/sphinxcontrib/websupport/
```

## 入口点

`pyproject.toml` 定义了 Sphinx builder 入口点：

```toml
[project.entry-points]
"sphinx.builders".websupport = "sphinxcontrib.websupport.builder:WebSupportBuilder"
```

包入口 `__init__.py` 导出 `WebSupport` 类和版本信息：

```python
__version__ = '2.0.0'
__version_info__ = (2, 0, 0)
from sphinxcontrib.websupport.core import WebSupport as WebSupport
```

## 核心模块清单

### 核心模块（sphinxcontrib/websupport/）

| 模块 | 文件 | 说明 |
|------|------|------|
| 包入口 | `__init__.py` | 定义 `__version__`、`__version_info__`、`package_dir`，导出 `WebSupport` 类 |
| 核心API | `core.py` | `WebSupport` 主类——构建文档、获取文档、评论CRUD、投票、搜索、用户名更新、审核回调；内部初始化模板/搜索/存储三大子系统 |
| Builder | `builder.py` | `WebSupportBuilder`（继承 `PickleHTMLBuilder`）——序列化文档为 pickle、注入评论节点标注、拷贝静态资源；`setup()` 函数注册 builder |
| Writer/Translator | `writer.py` | `WebSupportTranslator`（继承 `HTMLTranslator`）——在可评论段落节点上添加 `sphinx-has-comment` CSS类和 `s{uid}` DOM id，调用 storage 注册节点 |
| 工具函数 | `utils.py` | `is_commentable(node)` 函数——判断节点是否可评论（当前仅 `paragraph` 类型节点） |
| 异常定义 | `errors.py` | 4个异常类：`DocumentNotFoundError`、`UserNotAuthorizedError`、`CommentNotAllowedError`、`NullSearchException` |

### 存储子系统（storage/）

| 模块 | 文件 | 说明 |
|------|------|------|
| 存储抽象 | `storage/__init__.py` | `StorageBackend` 抽象基类——定义11个接口方法：`pre_build`/`has_node`/`add_node`/`post_build`/`add_comment`/`delete_comment`/`get_metadata`/`get_data`/`process_vote`/`update_username`/`accept_comment` |
| SQLAlchemy实现 | `storage/sqlalchemystorage.py` | `SQLAlchemyStorage`——基于SQLAlchemy ORM的存储后端，要求SQLAlchemy ≥ 1.4；支持SQLite（默认）、MySQL、PostgreSQL等 |
| 数据模型 | `storage/sqlalchemy_db.py` | SQLAlchemy ORM模型：`Node`（文档节点）、`Comment`（评论，含物化路径`path`）、`CommentVote`（投票，联合主键 username+comment_id）；`Base`（declarative_base）、`Session`（sessionmaker） |
| 差异比较 | `storage/differ.py` | `CombinedHtmlDiff`——基于 `difflib.Differ` 的HTML差异生成器，为"提议修改"功能生成带 `<ins>`/`<del>`/`<span class="prop-added/removed">` 标记的HTML diff |

### 搜索子系统（search/）

| 模块 | 文件 | 说明 |
|------|------|------|
| 搜索抽象 | `search/__init__.py` | `BaseSearch` 抽象基类+`SEARCH_ADAPTERS`注册表（内置 null/whoosh/xapian 三种适配器）；`feed()`方法从doctree提取文本调用`add_document()`；`query()`编译正则上下文提取后调用`handle_query()` |
| 空搜索 | `search/nullsearch.py` | `NullSearch`——默认空实现，`feed()`无操作，`query()`抛出 `NullSearchException` |
| Whoosh搜索 | `search/whooshsearch.py` | `WhooshSearch`——基于Whoosh纯Python搜索引擎，Schema含path(ID唯一)、title(TEXT field_boost=2.0)、text(TEXT+StemmingAnalyzer) |
| Xapian搜索 | `search/xapiansearch.py` | `XapianSearch`——基于Xapian C++搜索引擎，使用TermGenerator+Stemmer建索引，QueryParser解析查询，返回top 100结果 |

### 模板与静态资源

| 资源 | 路径 | 说明 |
|------|------|------|
| 搜索结果模板 | `templates/searchresults.html` | Jinja2模板，渲染搜索结果列表，支持搜索表单和结果高亮 |
| 前端JS | `files/websupport.js` | jQuery插件——提供评论弹窗、投票、回复、提议修改、审核、排序（按评分/时间）等完整前端交互 |
| 静态图片 | `files/*.png/*.gif` | 评论图标（comment.png/comment-bright.png/comment-close.png）、投票箭头（up/down/up-pressed/down-pressed.png）、加载动画（ajax-loader.gif） |

## 数据库表结构

SQLAlchemy后端自动创建3张表（表名前缀 `sphinx_`）：

| 表名 | 模型 | 主键 | 核心字段 |
|------|------|------|---------|
| `sphinx_nodes` | `Node` | `id` (String(32)) | `document` (String(256)), `source` (Text) |
| `sphinx_comments` | `Comment` | `id` (Integer, 自增) | `rating`, `time` (DateTime), `text` (Text), `displayed` (Boolean), `username`, `proposal`, `proposal_diff`, `path` (String(256), 物化路径), `node_id` (FK→nodes) |
| `sphinx_commentvote` | `CommentVote` | `username`+`comment_id` (联合主键) | `value` (Integer: -1/0/1) |

## 前端JS API（websupport.js）

`websupport.js` 是一个jQuery插件，通过两个全局变量与后端通信：
- `COMMENT_OPTIONS`：后端注入的配置（URL端点、静态资源路径、用户信息、是否允许投票）
- `COMMENT_METADATA`：后端注入的节点评论计数

核心功能：
- `.comment()` jQuery方法：为 `.sphinx-has-comment` 元素添加评论打开/关闭链接
- 评论CRUD：AJAX调用 `_get_comments`/`_add_comment`/`_delete_comment` 端点
- 投票：AJAX调用 `_process_vote` 端点
- 审核：AJAX调用 `_accept_comment` 端点（仅moderator可见）
- 提议修改：显示proposal_diff差异、提交修改建议
- 排序：按评分/最新/最旧排序，sortBy cookie持久化偏好
- 模板引擎：`renderTemplate()` 使用 `<%...%>`（转义）和 `<#...#>`（不转义）占位符

[^websupport-github]: sphinxcontrib-websupport 源码仓库：<https://github.com/sphinx-doc/sphinxcontrib-websupport>
[^websupport-pypi]: sphinxcontrib-websupport on PyPI：<https://pypi.org/project/sphinxcontrib-websupport/>
