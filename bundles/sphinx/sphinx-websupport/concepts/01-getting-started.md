---
okf_version: "0.2"
type: "concept"
title: 5分钟快速上手
description: 从安装到构建文档再到Flask集成的最小可运行示例，快速体验sphinxcontrib-websupport的核心流程
tags: [sphinx-websupport, getting-started, quickstart, flask]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T15:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T17:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: websupport-source
    resource: /references/websupport-source.md
---

# 5分钟快速上手

本教程通过一个最小可运行示例，展示 sphinxcontrib-websupport 的完整使用流程：准备Sphinx文档 → 构建序列化数据 → 用Flask提供Web服务。

## 前置条件

- Python ≥ 3.9
- 已安装 `sphinxcontrib-websupport[whoosh]`（含SQLAlchemy和Whoosh）
- 已安装 Flask（Web框架示例用）

```bash
pip install "sphinxcontrib-websupport[whoosh]" flask
```

## 第一步：准备Sphinx文档

首先需要一个标准的 Sphinx 文档项目。如果已有 Sphinx 文档可跳过此步。

创建最小 Sphinx 项目结构：

```
mydocs/
├── conf.py
└── index.rst
```

**conf.py**：

```python
project = 'My Docs'
author = 'Me'
extensions = []
```

**index.rst**：

```rst
Welcome to My Docs
==================

This is a paragraph that can be commented on.

Another paragraph here.
```

## 第二步：构建文档

创建构建脚本 `build_docs.py`：

```python
from sphinxcontrib.websupport import WebSupport

# 创建 WebSupport 实例——构建模式
support = WebSupport(
    srcdir='mydocs',          # 文档源目录（含 conf.py）
    builddir='websupport_data',  # 构建输出目录
    search='whoosh',          # 启用 Whoosh 搜索引擎
)

# 执行构建
support.build()
print("Build complete!")
```

运行构建：

```bash
python build_docs.py
```

构建完成后，`websupport_data/` 目录结构如下：

```
websupport_data/
├── data/                    # pickle序列化文档
│   ├── pickles/             # 每页文档的 .fpickle 文件
│   ├── globalcontext.pickle # 全局上下文（CSS/JS等）
│   └── search/              # Whoosh搜索索引
├── static/                  # 静态资源
│   ├── _static/             # Sphinx主题静态文件 + websupport图标/JS
│   └── _sources/            # 文档源文件（"显示源码"链接用）
└── doctrees/                # Sphinx doctree缓存
```

同时在 `websupport_data/data/db/` 下会生成 `websupport.db`（SQLite数据库），存储评论节点元数据。

## 第三步：Flask Web 应用

创建 `app.py`，一个最小化的文档服务器：

```python
from flask import Flask, g, render_template_string, abort, request, jsonify
from sphinxcontrib.websupport import WebSupport

app = Flask(__name__)

# 创建 WebSupport 实例——运行时模式（不需要srcdir）
support = WebSupport(
    builddir='websupport_data',
    search='whoosh',
    docroot='/docs',          # URL路径前缀
    staticroot='/static',     # 静态文件URL前缀
)

# 简单的文档页面模板
DOC_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ document.title }}</title>
    {{ document.css|safe }}
</head>
<body>
    {{ document.relbar|safe }}
    <div class="body">{{ document.body|safe }}</div>
    {{ document.sidebar|safe }}
    {{ document.script|safe }}
</body>
</html>
"""

@app.route('/docs/')
@app.route('/docs/<path:docname>')
def doc_page(docname=''):
    username = 'guest'  # 实际应用中从session获取
    moderator = False

    try:
        document = support.get_document(docname, username, moderator)
    except Exception:  # DocumentNotFoundError
        abort(404)

    return render_template_string(DOC_TEMPLATE, document=document)

# 评论API端点
@app.route('/docs/_get_comments')
def get_comments():
    node_id = request.args.get('node', '')
    username = 'guest'
    data = support.get_data(node_id, username)
    return jsonify(**data)

@app.route('/docs/_add_comment', methods=['POST'])
def add_comment():
    comment = support.add_comment(
        text=request.form.get('text', ''),
        node_id=request.form.get('node', ''),
        parent_id=request.form.get('parent', ''),
        username='guest',
    )
    return jsonify(comment=comment)

@app.route('/docs/_process_vote', methods=['POST'])
def process_vote():
    support.process_vote(
        comment_id=request.form.get('comment_id', ''),
        username='guest',
        value=request.form.get('value', '0'),
    )
    return 'OK'

# 静态文件服务
@app.route('/static/<path:filename>')
def static_files(filename):
    from flask import send_from_directory
    return send_from_directory('websupport_data/static', filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

运行Web应用：

```bash
python app.py
```

打开浏览器访问 `http://localhost:5000/docs/`，你应该能看到渲染的文档页面，每个段落旁边会出现评论图标。点击评论图标可以展开评论弹窗，添加评论和投票。

## 关键API速览

| API方法 | 用途 | 阶段 |
|---------|------|------|
| `WebSupport(srcdir=..., builddir=..., search=...)` | 构建模式实例化 | 构建 |
| `support.build()` | 执行文档构建 | 构建 |
| `WebSupport(builddir=..., ...)` | 运行模式实例化（无srcdir） | 运行时 |
| `support.get_document(docname, username, moderator)` | 加载单页文档 | 运行时 |
| `support.get_data(node_id, username, moderator)` | 获取节点评论数据 | 运行时 |
| `support.add_comment(text, node_id, ...)` | 添加评论 | 运行时 |
| `support.process_vote(comment_id, username, value)` | 处理投票 | 运行时 |
| `support.get_search_results(q)` | 获取搜索结果 | 运行时 |

## 常见问题

**Q: 构建时提示"No srcdir associated with WebSupport object"？**
A: 构建模式必须传入 `srcdir` 参数（文档源目录路径）。运行时模式不需要。

**Q: 评论图标不显示？**
A: 确保静态文件路由正确指向 `builddir/static/` 目录，`websupport.js` 和评论图标 PNG 文件能被浏览器加载。

**Q: 搜索不工作？**
A: 确认构建时指定了 `search='whoosh'`（或 `'xapian'`），且安装了对应的搜索库。默认 `search=None` 使用 NullSearch（不索引也不查询）。

## 下一步

- 了解[架构总览](02-architecture-overview.md)深入理解双阶段设计
- 学习[WebSupport API](03-websupport-api.md)掌握所有公开方法
- 查看[Flask完整集成示例](../examples/flask-integration.md)获取生产级集成代码

## 相关概念

- [sphinxcontrib-websupport 简介](00-introduction.md)
- [架构总览](02-architecture-overview.md)
- [WebSupport API 详解](03-websupport-api.md)
- [Flask完整集成示例](../examples/flask-integration.md)
