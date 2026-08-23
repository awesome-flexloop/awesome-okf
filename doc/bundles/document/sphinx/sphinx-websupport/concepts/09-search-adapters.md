---
okf_version: "0.2"
type: "concept"
title: 搜索适配器
description: BaseSearch抽象接口与三种内置实现——NullSearch空搜索、WhooshSearch纯Python搜索引擎、XapianSearch C++搜索引擎
tags: [sphinx-websupport, search, whoosh, xapian, fulltext-search, adapter]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T15:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T17:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: websupport-source
    resource: /references/websupport-source.md
---

# 搜索适配器

websupport的搜索系统通过 `BaseSearch` 抽象基类定义接口，提供三种内置实现：NullSearch（空搜索/默认）、WhooshSearch（纯Python引擎）、XapianSearch（C++引擎）。搜索在构建时建立索引，运行时执行查询。

## BaseSearch 抽象基类

定义在 `search/__init__.py` 中，是所有搜索适配器的基类。

### 核心方法

| 方法 | 签名 | 说明 |
|------|------|------|
| `__init__(path)` | `(path)` | 接收索引存储路径 |
| `init_indexing(changed=())` | `(changed)` | 构建开始时调用，准备索引；`changed`是需要重新索引的页面列表 |
| `finish_indexing()` | `()` | 构建结束时调用，提交/关闭索引 |
| `feed(pagename, filename, title, doctree)` | `(pagename, filename, title, doctree)` | Builder调用，将doctree喂给索引器 |
| `add_document(pagename, filename, title, text)` | `(pagename, filename, title, text)` | feed内部调用，添加单文档到索引（子类实现） |
| `query(q)` | `(q) -> list[(path, title, context)]` | 执行搜索查询（模板方法，编译正则后调用handle_query） |
| `handle_query(q)` | `(q) -> list[(path, title, context)]` | 实际查询逻辑（子类实现） |
| `extract_context(text, length=240)` | `(text, length) -> str` | 从文档文本中提取查询词周围的上下文片段 |

### feed方法：模板方法

```python
def feed(self, pagename, filename, title, doctree):
    self.add_document(pagename, filename, title, doctree.astext())
```

feed方法将doctree节点转为纯文本（`doctree.astext()`），然后调用 `add_document`。子类可以覆盖feed方法获取原始doctree对象（如需保留结构信息），通常只需要实现add_document。

### query方法：模板方法

```python
def query(self, q):
    self.context_re = re.compile('|'.join(q.split()), re.IGNORECASE)
    return self.handle_query(q)
```

query方法在执行查询前先编译一个正则表达式，用于后续 `extract_context` 提取搜索词周围的上下文。`'|'.join(q.split())` 将查询按空格分词后用 `|` 连接，形成OR匹配模式。子类通常不需要覆盖query，只需实现handle_query。

### extract_context方法：上下文提取

```python
def extract_context(self, text, length=240):
    res = self.context_re.search(text)
    if res is None:
        return ''
    context_start = max(res.start() - int(length / 2), 0)
    context_end = context_start + length
    context = ''.join([
        context_start > 0 and '...' or '',
        text[context_start:context_end],
        context_end < len(text) and '...' or ''
    ])
    return context
```

从文档全文中找到第一个匹配搜索词的位置，取前后各120字符（共240字符）作为摘要上下文。如果匹配词在文本开头则不加前缀"..."，在末尾则不加后缀"..."。

### 适配器注册表

```python
SEARCH_ADAPTERS = {
    'xapian': ('xapiansearch', 'XapianSearch'),
    'whoosh': ('whooshsearch', 'WhooshSearch'),
    'null':   ('nullsearch', 'NullSearch'),
}
```

WebSupport._init_search通过这个注册表动态导入对应的模块和类：

```python
mod, cls = SEARCH_ADAPTERS[search or 'null']
mod = 'sphinxcontrib.websupport.search.' + mod
SearchClass = getattr(importlib.import_module(mod), cls)
self.search = SearchClass(search_path)
```

也可以直接传入BaseSearch实例绕过注册表。

## NullSearch：空搜索适配器

```python
class NullSearch(BaseSearch):
    def feed(self, pagename, filename, title, doctree):
        pass
    def query(self, q):
        raise NullSearchException('No search adapter specified.')
```

默认搜索适配器，什么都不做。feed方法是空操作（不建索引），query方法抛出NullSearchException。如果WebSupport初始化时不指定search参数或显式指定 `search='null'`，就使用NullSearch——此时搜索功能完全禁用。

## WhooshSearch：纯Python搜索引擎

```python
class WhooshSearch(BaseSearch):
    schema = Schema(
        path=ID(stored=True, unique=True),
        title=TEXT(field_boost=2.0, stored=True),
        text=TEXT(analyzer=StemmingAnalyzer(), stored=True)
    )
```

### Schema设计

| 字段 | 类型 | 属性 | 说明 |
|------|------|------|------|
| path | ID | stored=True, unique=True | 文档路径（主键，唯一） |
| title | TEXT | field_boost=2.0, stored=True | 文档标题（权重加倍） |
| text | TEXT | StemmingAnalyzer, stored=True | 文档全文（词干分析） |

**field_boost=2.0** 表示标题匹配的权重是正文中匹配的2倍。StemmingAnalyzer对英文进行词干提取（如"running"→"run"），提高搜索召回率。

### 初始化

```python
def __init__(self, db_path):
    ensuredir(db_path)
    if index.exists_in(db_path):
        self.index = index.open_dir(db_path)
    else:
        self.index = index.create_in(db_path, schema=self.schema)
    self.qparser = QueryParser('text', self.schema)
```

如果索引目录已存在则打开，否则创建新索引。QueryParser配置为搜索text字段。

### 索引方法

```python
def init_indexing(self, changed=()):
    for changed_path in changed:
        self.index.delete_by_term('path', changed_path)
    self.index_writer = self.index.writer()

def finish_indexing(self):
    self.index_writer.commit()

def add_document(self, pagename, filename, title, text):
    self.index_writer.add_document(path=pagename, title=title, text=text)
```

增量构建时先删除已变更文档的旧索引，再在finish_indexing时统一提交。

### 查询方法

```python
def handle_query(self, q):
    searcher = self.index.searcher()
    whoosh_results = searcher.search(self.qparser.parse(q))
    results = []
    for result in whoosh_results:
        context = self.extract_context(result['text'])
        results.append((result['path'], result.get('title', ''), context))
    return results
```

使用Whoosh的searcher执行查询，对每条结果调用extract_context生成摘要。返回三元组列表 `(path, title, context)`。

Whoosh是纯Python实现，pip安装即可使用，无需编译C扩展，是最容易上手的搜索后端。

## XapianSearch：C++搜索引擎

```python
class XapianSearch(BaseSearch):
    DOC_PATH = 0  # Value slot 0: 文档路径
    DOC_TITLE = 1  # Value slot 1: 文档标题
```

Xapian是高性能C++搜索引擎，需要系统级安装libxapian和Python bindings。

### 索引方法

```python
def init_indexing(self, changed=()):
    ensuredir(self.db_path)
    self.database = xapian.WritableDatabase(self.db_path, xapian.DB_CREATE_OR_OPEN)
    self.indexer = xapian.TermGenerator()
    stemmer = xapian.Stem("english")
    self.indexer.set_stemmer(stemmer)

def add_document(self, pagename, filename, title, text):
    self.database.begin_transaction()
    # 特殊term用于按路径删除旧文档
    sphinx_page_path = f'"sphinxpagepath{pagename.replace("/", "_")}"'
    self.database.delete_document(sphinx_page_path)
    
    doc = xapian.Document()
    doc.set_data(text)
    doc.add_value(self.DOC_PATH, pagename)
    doc.add_value(self.DOC_TITLE, title)
    self.indexer.set_document(doc)
    self.indexer.index_text(text)
    doc.add_term(sphinx_page_path)
    for word in text.split():
        doc.add_posting(word, 1)
    self.database.add_document(doc)
    self.database.commit_transaction()
```

Xapian使用Value slot存储文档路径和标题（slot 0/1），使用TermGenerator+Stem("english")进行词干索引。每个文档添加一个特殊term `sphinxpagepath{path}` 用于按路径删除旧文档。

### 查询方法

```python
def handle_query(self, q):
    database = xapian.Database(self.db_path)
    enquire = xapian.Enquire(database)
    qp = xapian.QueryParser()
    stemmer = xapian.Stem("english")
    qp.set_stemmer(stemmer)
    qp.set_database(database)
    qp.set_stemming_strategy(xapian.QueryParser.STEM_SOME)
    query = qp.parse_query(q)
    
    enquire.set_query(query)
    matches = enquire.get_mset(0, 100)  # top 100结果
    
    results = []
    for m in matches:
        data = m.document.get_data()
        if not isinstance(data, str):
            data = data.decode("utf-8")
        context = self.extract_context(data)
        results.append((
            m.document.get_value(self.DOC_PATH),
            m.document.get_value(self.DOC_TITLE),
            ''.join(context)
        ))
    return results
```

Xapian查询返回最多100条结果。使用QueryParser解析查询字符串，STEM_SOME策略对部分词进行词干化。

### 资源释放

```python
def finish_indexing(self):
    del self.database  # 确保数据库锁被移除
```

Xapian需要显式删除数据库对象来释放文件锁。

## Builder集成

WebSupportBuilder在构建过程中与搜索适配器交互：

1. **load_indexer(docnames)**：将 `self.indexer` 设为search适配器，调用 `search.init_indexing(changed=list(docnames))`
2. **write_doc_serialized**：处理图片路径后调用 `self.index_page(docname, doctree, title)`，最终调用 `search.feed()` 添加文档
3. **dump_search_index()**：构建结束时调用 `search.finish_indexing()` 提交索引

## 搜索结果渲染

搜索结果通过Jinja2模板 `templates/searchresults.html` 渲染：

```html
{% for href, caption, context in search_results %}
<li><a href="{{ docroot }}{{ href }}/?highlight={{ q }}">{{ caption }}</a>
  <div class="context">{{ context|e }}</div>
</li>
{% endfor %}
```

结果链接指向 `{docroot}{path}/?highlight={query}`，前端JS根据URL参数 `highlight` 高亮搜索词。

`get_search_results(q)` 方法将搜索结果包装为与get_document兼容的字典格式：

```python
def get_search_results(self, q):
    results = self.search.query(q)
    ctx = {'q': q, 'search_performed': True, 'search_results': results, 'docroot': '../', '_': _}
    document = {
        'body': self.results_template.render(ctx),
        'title': 'Search Results',
        'sidebar': '',
        'relbar': '',
    }
    return document
```

## 选择搜索后端

| 后端 | 安装难度 | 性能 | 适合场景 |
|------|---------|------|---------|
| NullSearch | 无需安装 | 无（禁用搜索） | 不需要搜索功能的文档站 |
| WhooshSearch | `pip install whoosh` | 中等（纯Python） | 中小规模文档（<1000页），快速部署 |
| XapianSearch | 需编译C++库 | 高性能 | 大规模文档站，生产环境 |

## 实现自定义搜索适配器

继承BaseSearch，实现 `add_document()` 和 `handle_query()` 即可：

```python
from sphinxcontrib.websupport.search import BaseSearch

class SimpleSearch(BaseSearch):
    def __init__(self, path):
        super().__init__(path)
        self.docs = {}
    
    def add_document(self, pagename, filename, title, text):
        self.docs[pagename] = {'title': title, 'text': text}
    
    def handle_query(self, q):
        results = []
        keywords = q.lower().split()
        for path, doc in self.docs.items():
            if any(kw in doc['text'].lower() for kw in keywords):
                context = self.extract_context(doc['text'])
                results.append((path, doc['title'], context))
        return results
```

## 相关概念

- [架构总览](02-architecture-overview.md)
- [Builder系统](04-builder-system.md)
- [WebSupport API 详解](03-websupport-api.md)
