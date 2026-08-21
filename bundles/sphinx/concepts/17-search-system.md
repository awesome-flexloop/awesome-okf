---
type: "concept"
title: "搜索系统"
description: "Sphinx内置全文搜索——搜索索引收集(searchindex.js)、snowball词干提取、客户端JavaScript搜索、searchtools.js、自定义搜索排序"
tags: [advanced, search, index, javascript, full-text-search]
generated: { by: "reference_agent/claude-opus-4", at: "2026-08-21T09:47:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T09:47:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - id: search-py
    resource: sphinx/search/
    title: "Sphinx search module"
---

# 搜索系统

Sphinx内置了**客户端全文搜索**功能，不需要服务端支持——搜索索引在构建时生成，搜索操作在用户浏览器中通过JavaScript执行。这使得静态托管的文档网站也能提供搜索功能。

## 搜索架构

Sphinx搜索采用"构建时索引+客户端搜索"的架构 [F-064]：

```
构建时（READING阶段）                构建时（FINISHING阶段）
┌─────────────────────┐          ┌──────────────────────┐
│ 收集搜索数据        │          │ 生成searchindex.js   │
│ ─ titles           │          │ ─ 词干提取(snowball) │
│ ─ 全文词频         │    →     │ ─ 序列化为JSON       │
│ ─ 对象索引         │          │ ─ 写入输出目录       │
│ ─ 术语表           │          └──────────────────────┘
└─────────────────────┘                      │
                                              ▼
                                    浏览器加载search.html
                                              │
                                              ▼
                                    searchtools.js执行搜索
                                    ─ 下载searchindex.js
                                    ─ 解析搜索查询
                                    ─ 词干提取查询词
                                    ─ 匹配并排序
                                    ─ 显示结果
```

## 搜索索引数据

BuildEnvironment在READING阶段收集搜索数据，存储在以下属性中：

| 属性 | 内容 |
|------|------|
| `_search_index_titles` | docname → 标题文本 |
| `_search_index_filenames` | docname → 文件名 |
| `_search_index_mapping` | 词干 → 包含该词的docname集合（正文匹配） |
| `_search_index_title_mapping` | 词干 → docname集合（标题匹配，权重更高） |
| `_search_index_all_titles` | docname → 所有子标题列表 |
| `_search_index_index_entries` | docname → 索引条目 |
| `_search_index_objtypes` | (domain, type) → 类型ID |
| `_search_index_objnames` | 类型ID → (domain, type, 本地化名称) |

### searchindex.js 输出格式

FINISHING阶段将搜索数据序列化为 `searchindex.js`：

```javascript
/* This is the search index for Sphinx documentation. */
Search.setIndex({
    // 配置
    config: {lang: ["en"]},
    
    // 文档信息
    docnames: ["index", "intro", "install"],
    filenames: ["index.rst", "intro.rst", "install.rst"],
    titles: ["Welcome", "Introduction", "Installation"],
    titleterms: {welcom:0, introduct:1, instal:2},
    
    // 全文索引（词干→文档映射）
    terms: {
        sphinx: [0, 1, 2],
        document: [0, 1],
        instal: [2],
        python: [2],
        // ...
    },
    
    // 对象索引
    objects: {
        "sphinx.application": [[0,0,1,"","Sphinx"]],
        // 格式: "fullname": [docid, objtypeid, priority, anchor, dispname]
    },
    objtypes: {
        "py:class": [[0, "class"], [1, "类"]],  // (id, [english, localized])
        "py:function": [[1, "function"], [2, "函数"]],
    },
    objnames: {
        "0": ["py", "class", "class"],
        "1": ["py", "function", "function"],
    },
    
    // 所有标题（用于结果预览）
    alltitles: {
        "0": [[0, "Welcome", "welcome"]],
        "1": [[1, "Introduction", "introduction"]],
    },
    
    // 索引条目
    indexentries: {
        "sphinx": [[0, "Sphinx", ""]],
    },
});
```

注意所有英文单词都经过**词干提取**（stemming），如"installing"→"instal"、"documentation"→"document"。这使得搜索"install"也能匹配"installing"和"installation"。

## 词干提取（Snowball Stemmer）

Sphinx使用Porter/Snowball词干提取算法来归一化词语 [F-065]：

- **英语**：内置Porter stemmer（`sphinx/search/en.py`）
- **其他语言**：通过snowballstemmer库支持
- **CJK语言**（中文/日文/韩文）：使用字符二元组（bigrams）而非词干提取

```python
# 英文词干提取示例
"installing"  → "instal"
"documentation" → "document"
"building" → "build"
"extensions" → "extens"
```

支持的语言对应关系由`sphinx/search/languages.py`中的`languages`字典定义。

## 配置项

| 配置项 | 默认值 | 说明 |
|--------|-------|------|
| `html_search_language` | `None` | 搜索语言（默认跟随language配置） |
| `html_search_options` | `{}` | 搜索选项（传递给词干提取器） |
| `html_search_scorer` | `None` | 自定义搜索评分器（JavaScript文件路径） |
| `html_search_index_url` | `None` | 搜索索引URL（用于从不同位置加载） |

## 搜索结果排序

客户端搜索的评分因素：

1. **标题匹配**：词出现在标题中，权重高于正文
2. **对象类型优先级**：searchprio=0的对象（模块/类名）优先于普通文本
3. **词频**：词在文档中出现频率越高排名越高（但有TF-IDF归一化）
4. **对象索引匹配**：匹配到具体对象（如函数名）时排名更高

### 自定义评分器

通过`html_search_scorer`配置自定义JavaScript评分函数：

```javascript
// scorer.js
Scorer = {
    score: function(result) {
        // 返回分数，分数越高排名越前
        var score = result[1];  // 默认分数
        // 自定义加权逻辑
        return score;
    }
};
```

## searchtools.js API

Sphinx内置的`searchtools.js`提供了客户端搜索功能，其核心API包括：

| 方法 | 说明 |
|------|------|
| `Search.setIndex(data)` | 加载搜索索引数据 |
| `Search.performSearch(query)` | 执行搜索，返回结果 |
| `Search.query(query)` | 执行搜索并显示结果 |
| `Search.hasModuleResults()` | 是否有对象索引结果 |
| `Search.makeSearchSummary(html, keywords, hlwords)` | 生成搜索结果摘要 |

### 搜索查询语法

Sphinx搜索支持简单的查询语法：

| 语法 | 说明 |
|------|------|
| `word1 word2` | 包含word1或word2（OR逻辑） |
| `"exact phrase"` | 精确短语匹配 |
| `word*` | 前缀匹配（以word开头的词） |
| `-word` | 排除包含word的文档 |

## 自定义搜索

### 禁用搜索

```python
html_use_search = False
```

### 自定义搜索模板

覆盖`search.html`模板可以定制搜索界面。

### 使用外部搜索引擎

对于大型文档集，客户端搜索可能不够快，可以考虑：
- 替换search.html模板，接入Algolia DocSearch
- 使用Sphinx的`html_search_index_url`加载远程索引
- 使用sphinxcontrib-httpexample等扩展集成外部搜索

## 设计洞察

1. **纯静态搜索**：Sphinx搜索完全在客户端执行，不需要数据库或后端服务，这是静态站点文档的理想选择。代价是索引大小随文档量线性增长，超大型文档（>1000页）可能需要外部搜索方案。

2. **词干提取而非分词**：对于西方语言，Snowball词干提取器效果好且实现简单；对于CJK语言使用bigram策略，无需词典支持即可工作，但准确性不如专用分词器。

3. **构建时索引**：索引在构建时预先生成并序列化，搜索时只需加载JSON数据，这意味着搜索速度取决于浏览器性能而非服务器。

4. **双索引策略**：terms（正文）和titleterms（标题）分开索引，标题匹配权重更高，提高了搜索相关性。

## 相关概念

- [HTML 构建器详解](11-html-builder.md)
- [构建环境](07-build-environment.md)
- [主题系统](13-theme-system.md)
