---
okf_version: "0.2"
type: "example"
title: "Flask Web 应用集成"
sources: ["sphinxcontrib/websupport/core.py", "sphinxcontrib/websupport/storage/sqlalchemystorage.py"]
---

# Flask Web 应用集成

本示例演示如何将 sphinxcontrib-websupport 集成到 Flask Web 应用中，实现文档浏览、评论发表、投票、提议修改等完整功能。对应概念：[WebSupport API](../concepts/03-websupport-api.md)、[评论系统](../concepts/05-comment-system.md)、[前端集成](../concepts/08-frontend-integration.md)。

## 完整示例：Flask 应用

```python
"""
Flask + sphinxcontrib-websupport 集成示例。

功能：
- 文档页面渲染
- RESTful 评论 API（GET/POST/DELETE）
- 评论投票（赞成/反对）
- 提议修改（proposal diff）
- 评论审核（accept/delete）

引用事实：
- add_comment() 支持 node_id/parent_id/proposal/displayed 参数
- process_vote() 投票值为 1（赞成）、-1（反对）、0（取消）
- get_data() 返回评论树结构，moderator=True 可看全部评论
- delete_comment() 用户仅能删除自己的评论，版主可删除任意评论
"""

from flask import Flask, request, jsonify, render_template_string, abort
from sphinxcontrib.websupport import WebSupport
from sphinxcontrib.websupport.errors import (
    CommentNotAllowedError,
    DocumentNotFoundError,
    UserNotAuthorizedError,
)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # 生产环境请使用安全密钥

# ============ 初始化 WebSupport ============
# 构建阶段一次性执行（通常在部署脚本中，不在 Flask 启动时）
# support = WebSupport(srcdir='/path/to/docs', builddir='/path/to/build')
# support.build()

# 运行阶段：仅需 builddir
support = WebSupport(
    builddir='/path/to/websupport-build',  # 替换为实际路径
    search='whoosh',                       # 启用 Whoosh 全文搜索
    # storage='postgresql://user:pass@localhost/websupport',  # PostgreSQL
    allow_anonymous_comments=True,
    docroot='/docs',
    staticroot='/static/websupport',
)


# ============ 简易用户认证（示例用，生产环境请替换） ============
def get_current_username():
    """获取当前登录用户名。实际应用应从 session/token 获取。"""
    return request.cookies.get('username', 'anonymous')


def is_moderator():
    """判断当前用户是否为版主。"""
    return request.cookies.get('is_moderator') == '1'


# ============ 页面路由 ============

PAGE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <link rel="stylesheet" href="/static/websupport/websupport.css">
</head>
<body>
    <h1>{{ title }}</h1>
    <div class="document">{{ body|safe }}</div>
    <div class="sidebar">{{ sidebar|safe }}</div>
    <div class="relbar">{{ relbar|safe }}</div>

    <!-- 评论区容器 -->
    <div id="comments"></div>

    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="/static/websupport/websupport.js"></script>
    <script>
        // 初始化评论插件
        $(document).ready(function() {
            COMMENT_OPTIONS = {
                url: "/docs/_comments",
                snapshot: "{{ docname }}",
                source: "/docs/_source",
            };
            // 绑定评论交互
            $('.sphinx-websupport').websupport(COMMENT_OPTIONS);
        });
    </script>
</body>
</html>
"""


@app.route('/docs/')
@app.route('/docs/<path:docname>')
def doc_page(docname='index'):
    """渲染文档页面。"""
    try:
        document = support.get_document(docname)
    except DocumentNotFoundError:
        abort(404)

    return render_template_string(
        PAGE_TEMPLATE,
        docname=docname,
        **document,
    )


# ============ 评论 API ============

@app.route('/docs/_comments/<node_id>', methods=['GET'])
def get_comments(node_id):
    """获取指定节点的评论数据。"""
    username = get_current_username()
    moderator = is_moderator()
    data = support.get_data(node_id, username=username, moderator=moderator)
    return jsonify(data)


@app.route('/docs/_comments', methods=['POST'])
def add_comment():
    """发表新评论或回复。

    请求体（JSON）：
    - parent_id: 父评论 ID（回复时提供，顶层评论提供 node_id）
    - node_id: 文档节点 ID（顶层评论必须提供）
    - text: 评论内容（Markdown/ReST 格式）
    - proposal: 提议修改的文本（可选，用于提议修改功能）
    """
    data = request.get_json()
    username = get_current_username()

    try:
        comment = support.add_comment(
            text=data['text'],
            node_id=data.get('node_id'),
            parent_id=data.get('parent_id'),
            username=username,
            proposal=data.get('proposal'),
        )
        return jsonify(comment), 201
    except CommentNotAllowedError:
        return jsonify({'error': '不允许在此处发表评论'}), 403


@app.route('/docs/_comments/<comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    """删除评论。用户只能删除自己的评论，版主可删除任意评论。"""
    username = get_current_username()
    moderator = is_moderator()

    try:
        support.delete_comment(comment_id, username=username, moderator=moderator)
        return jsonify({'status': 'deleted'})
    except UserNotAuthorizedError:
        return jsonify({'error': '无权删除此评论'}), 403


# ============ 投票 API ============

@app.route('/docs/_comments/<comment_id>/vote', methods=['PUT'])
def vote_comment(comment_id):
    """对评论进行投票。

    请求体（JSON）：
    - value: 投票值（1=赞成, -1=反对, 0=取消投票）
    """
    username = get_current_username()
    data = request.get_json()
    value = data.get('value', 0)

    try:
        support.process_vote(comment_id, username, value)
        # 获取更新后的评论数据
        return jsonify({'status': 'voted', 'value': value})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


# ============ 审核 API（仅版主） ============

@app.route('/docs/_comments/<comment_id>/accept', methods=['PUT'])
def accept_comment(comment_id):
    """审核通过评论（仅版主）。"""
    if not is_moderator():
        return jsonify({'error': '需要版主权限'}), 403
    support.accept_comment(comment_id, moderator=True)
    return jsonify({'status': 'accepted'})


# ============ 搜索 API ============

@app.route('/docs/search')
def search():
    """全文搜索。"""
    q = request.args.get('q', '')
    if not q:
        return jsonify({'results': []})

    results = support.get_search_results(q)
    return jsonify(results)


# ============ 源文本 API（用于提议修改） ============

@app.route('/docs/_source/<node_id>')
def get_source(node_id):
    """获取节点原始源文本（用于提议修改功能）。"""
    username = get_current_username()
    data = support.get_data(node_id, username=username)
    return jsonify({'source': data.get('source', '')})


# ============ 用户更名 ============

@app.route('/api/update-username', methods=['POST'])
def update_username():
    """用户更名时批量更新评论中的用户名。"""
    data = request.get_json()
    old_name = data.get('old_name')
    new_name = data.get('new_name')
    if old_name and new_name:
        support.update_username(old_name, new_name)
        return jsonify({'status': 'updated'})
    return jsonify({'error': '参数不完整'}), 400


if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

## 代码说明

1. **双阶段分离**：构建阶段（`support.build()`）在部署脚本中执行，Flask 应用启动时仅加载已构建的数据，避免每次启动都重新构建。

2. **RESTful API 设计**：评论、投票、审核操作都通过标准 HTTP 方法映射：
   - `GET /docs/_comments/<node_id>` → 获取评论
   - `POST /docs/_comments` → 发表评论
   - `DELETE /docs/_comments/<id>` → 删除评论
   - `PUT /docs/_comments/<id>/vote` → 投票

3. **权限控制**：
   - 普通用户只能删除自己的评论（`UserNotAuthorizedError` 保护）
   - 审核操作需要 `moderator=True` 参数
   - 匿名评论受 `allow_anonymous_comments` 配置控制

4. **前端集成**：通过 `websupport.js` jQuery 插件自动绑定评论弹窗、投票按钮、回复表单等交互，后端只需实现约定的 API 端点。

5. **数据库选择**：示例默认使用 SQLite，生产环境建议切换到 PostgreSQL：
   ```python
   support = WebSupport(
       builddir='/path/to/build',
       storage='postgresql://user:pass@localhost/websupport',
   )
   ```

## 部署注意事项

- 构建产物（`builddir/data/` 和 `builddir/static/`）应由 Web 服务器直接服务静态文件
- 数据库连接字符串支持 SQLAlchemy 所有后端（SQLite/MySQL/PostgreSQL）
- `process_vote()` 的投票值必须是 -1、0、1 之一，否则抛出 ValueError
- 删除评论是软删除（标记为 `[deleted]`），不会物理删除记录以保持评论树结构
