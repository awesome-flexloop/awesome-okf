---
okf_version: "0.2"
type: "concept"
title: 评论系统
description: sphinxcontrib-websupport的评论机制——可评论节点判定、Translator注释注入、评论生命周期、投票与审核流程
tags: [sphinx-websupport, comments, translator, voting, moderation, proposal-diff]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T15:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T17:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: websupport-source
    resource: /references/websupport-source.md
---

# 评论系统

评论系统是websupport最核心的功能模块，它允许用户对文档中的段落添加评论、回复、投票和提议修改。整个系统由构建时的节点标注和运行时的CRUD API两部分组成。

## 可评论节点判定

### is_commentable 函数

```python
def is_commentable(node):
    return node.__class__.__name__ == 'paragraph'
```

定义在 `utils.py` 中，当前版本**只有段落（paragraph）节点**可以被评论。注释中的代码显示曾经考虑过支持 `literal_block`（代码块），但最终只保留了paragraph。

这个函数被两个地方使用：
1. `WebSupportTranslator.dispatch_visit()` 中判断是否给节点添加评论标记
2. `WebSupportBuilder.versioning_method` 属性中，告诉Sphinx版本比较机制哪些节点需要保持UUID稳定

## WebSupportTranslator：构建时的注释注入

`WebSupportTranslator` 继承自Sphinx的 `HTMLTranslator`，在文档树遍历过程中为可评论节点注入特殊的HTML属性。

### dispatch_visit 方法

```python
def dispatch_visit(self, node):
    if is_commentable(node) and hasattr(node, 'uid'):
        self.handle_visit_commentable(node)
    HTMLTranslator.dispatch_visit(self, node)
```

在访问每个节点时：
1. 检查节点是否可评论（paragraph类型）且有uid（Sphinx的版本UUID）
2. 如果是，调用 `handle_visit_commentable()` 注入评论标记
3. 继续执行标准HTML翻译

### handle_visit_commentable 方法

```python
def handle_visit_commentable(self, node):
    self.add_db_node(node)
    if node.attributes['ids']:
        self.body.append(f'<span id="{node.attributes["ids"][0]}"></span>')
    node.attributes['ids'] = [f's{node.uid}']
    node.attributes['classes'].append(self.comment_class)  # 'sphinx-has-comment'
```

这个方法做了三件关键的事：

1. **注册节点到数据库**：调用 `add_db_node(node)` 将节点（uid、文档名、原始文本）写入数据库
2. **保留原有锚点**：如果节点已有id（用于Sphinx内部索引），在其HTML前插入一个空 `<span>` 保留该id
3. **替换节点id**：将节点的DOM id设为 `s{uid}` 格式（如 `s123456`），前端JS通过这个id定位评论
4. **添加CSS类**：为节点添加 `sphinx-has-comment` CSS类，jQuery选择器用它找到可评论段落

### add_db_node 方法

```python
def add_db_node(self, node):
    storage = self.builder.storage
    if not storage.has_node(node.uid):
        storage.add_node(id=node.uid,
                         document=self.builder.current_docname,
                         source=node.rawsource or node.astext())
```

将可评论节点注册到数据库。使用 `has_node` 检查避免重复添加（增量构建场景）。source字段优先使用 `rawsource`（原始reST文本），fallback到 `astext()`（提取的纯文本）。

## 前端评论交互

构建完成后，每个段落都带有 `id="s{uid}"` 和 `class="sphinx-has-comment"`。前端 `websupport.js` 在页面加载后执行：

```javascript
$('.sphinx-has-comment').comment();
```

`.comment()` 是jQuery插件方法，为每个可评论段落添加：
- 评论打开链接（`#ao{uid}`）：显示评论数图标
- 评论关闭链接（`#ah{uid}`）：默认隐藏
- 根据COMMENT_METADATA中的评论数选择图标（有评论用亮色图标，无评论用灰色图标）

## 评论数据结构

### 评论字典格式

API返回的每个评论是一个字典：

```python
{
    'text': '<p>评论的HTML内容</p>\n',    # docutils渲染后的HTML
    'username': 'reader1',                  # 评论者
    'id': 42,                               # 评论ID（数据库自增整数）
    'rating': 3,                            # 当前评分
    'age': 3600,                            # 评论年龄（秒）
    'time': {
        'year': 2026, 'month': 8, 'day': 21,
        'hour': 15, 'minute': 30, 'second': 0,
        'iso': '2026-08-21T15:30:00',
        'delta': '1 hour ago',              # 人类可读时间差
    },
    'vote': 1,                              # 当前用户投票值（-1/0/1）
    'node': 's123456',                      # 所属节点ID（顶级评论）
    'parent': '41',                         # 父评论ID（回复），顶级评论为None
    'children': [...],                      # 子评论列表（递归嵌套）
    'proposal_diff': '<span class="prop-added">...</span>',  # 提议修改diff
    'displayed': True,                      # 是否已审核通过
}
```

### 节点数据格式

`get_data(node_id)` 返回：

```python
{
    'source': 'This is the original paragraph text.',  # 段落原文（用于提议修改）
    'comments': [...]  # 嵌套评论树
}
```

## 评论生命周期

### 1. 添加评论

```python
comment = support.add_comment(
    text='这里写得不清楚',
    node_id='s123456',       # 顶级评论：节点ID
    # parent_id='42',        # 回复评论：父评论ID
    username='reader1',
    proposal=None,           # 可选：提议修改文本
    displayed=True,          # 是否直接显示（False需审核）
)
```

处理流程：
1. **文本解析**：用docutils `publish_parts(writer_name='html')` 将reST格式的评论转为HTML；如果解析失败则 fallback 到 `html.escape(text)`
2. **权限检查**：如果username为None且不允许匿名评论，抛 `UserNotAuthorizedError`
3. **提议diff**：如果提供了node_id和proposal，用CombinedHtmlDiff生成HTML差异
4. **父评论检查**：如果是回复（parent_id），检查父评论的displayed状态，回复未审核评论抛 `CommentNotAllowedError`
5. **存储评论**：调用storage添加评论，设置物化路径
6. **审核回调**：如果displayed=False且设置了moderation_callback，调用回调函数

### 2. 获取评论

```python
data = support.get_data('s123456', username='reader1', moderator=False)
```

处理流程：
1. 查询数据库获取节点
2. 调用 `node.nested_comments(username, moderator)` 获取嵌套评论树
3. 非审核员只能看到displayed=True的评论
4. 提供username时，外层join查询CommentVote获取该用户的投票状态

### 3. 投票

```python
support.process_vote(comment_id, 'reader1', 1)  # 1=点赞, -1=点踩, 0=取消
```

投票规则：
- value必须是-1、0、1，否则抛ValueError
- 同一用户对同一评论只能投一票（CommentVote表联合主键：username+comment_id）
- 改票时评分差值调整（如从-1改为+1，rating += 2）
- 取消投票时减去原有投票值

### 4. 删除评论

两种删除模式：

**用户自删**（`moderator=False`）：软删除，username和text替换为`'[deleted]'`，proposal清空。只能删除自己的评论，否则抛 `UserNotAuthorizedError`。

**审核员删除**（`moderator=True`）：硬删除，通过物化路径 `path LIKE 'comment.path.%'` 删除评论及其所有后代。

### 5. 审核通过

```python
support.accept_comment(comment_id, moderator=True)
```

将评论的displayed字段设为True。非审核员调用抛 `UserNotAuthorizedError`。

## 提议修改（Proposal Diff）

用户可以在评论中附带对段落原文的修改建议。系统使用 `CombinedHtmlDiff` 生成差异展示：

```python
support.add_comment(
    text='建议修改这里的表述',
    node_id='s123456',
    username='reader1',
    proposal='这是修改后的段落文本...',  # 提议的新文本
)
```

CombinedHtmlDiff基于Python标准库 `difflib.Differ`：
1. 对原文和提议文本按行进行diff比较
2. 生成HTML输出：删除内容用 `<span class="prop-removed">`，新增内容用 `<span class="prop-added">`
3. 行间的精细差异用 `<del>` 和 `<ins>` 标签标记（通过`?`提示行）

前端通过"proposal ▹"链接展开/折叠查看差异。

## 评论文本格式

评论文本支持reStructuredText格式：
- `*emph*` → 斜体
- `**strong**` → 粗体
- ` ``code`` ` → 行内代码
- `::` + 缩进块 → 代码块

解析通过docutils的 `publish_parts` 实现，禁用了file_insertion和raw指令以防止安全问题：

```python
settings = {'file_insertion_enabled': False, 'raw_enabled': False, 'output_encoding': 'unicode'}
ret = publish_parts(text, writer_name='html', settings_overrides=settings)['fragment']
```

## 评论注入机制

构建完成的pickle文件中不包含任何评论内容。评论是在**运行时动态注入**的：

1. `get_document()` 加载pickle后，调用 `_make_comment_options()` 生成COMMENT_OPTIONS的 `<script>` 块
2. 调用 `storage.get_metadata(docname)` 获取该页所有节点的评论计数，生成COMMENT_METADATA的 `<script>` 块
3. 将两个 `<script>` 块追加到 `document['script']` 中
4. 浏览器端 `websupport.js` 根据COMMENT_METADATA显示评论数，用户点击时AJAX加载实际评论

这种设计使得评论数据与文档内容完全分离：更新评论不需要重新构建文档。

## JavaScript配置注入

### COMMENT_OPTIONS（请求级）

```javascript
var COMMENT_OPTIONS = {
    addCommentURL: "/docs/_add_comment",
    getCommentsURL: "/docs/_get_comments",
    processVoteURL: "/docs/_process_vote",
    acceptCommentURL: "/docs/_accept_comment",
    deleteCommentURL: "/docs/_delete_comment",
    commentImage: "/static/_static/comment.png",
    closeCommentImage: "/static/_static/comment-close.png",
    loadingImage: "/static/_static/ajax-loader.gif",
    commentBrightImage: "/static/_static/comment-bright.png",
    upArrow: "/static/_static/up.png",
    upArrowPressed: "/static/_static/up-pressed.png",
    downArrow: "/static/_static/down.png",
    downArrowPressed: "/static/_static/down-pressed.png",
    voting: true,
    username: "reader1",
    moderator: false
};
```

URL部分（`_make_base_comment_options`中创建）在WebSupport实例生命周期内不变，用户信息部分（`_make_comment_options`中添加）每个请求不同。

### COMMENT_METADATA（文档级）

```javascript
var COMMENT_METADATA = {"s123456": 3, "s123457": 0, "s123458": 1};
```

键是节点DOM id，值是该节点的评论总数。用于在页面加载时显示评论计数图标。

## 相关概念

- [Builder系统](04-builder-system.md)
- [存储后端](06-storage-backend.md)
- [物化路径评论树](07-materialized-path.md)
- [前端集成](08-frontend-integration.md)
- [搜索适配器](09-search-adapters.md)
