---
okf_version: "0.2"
type: "concept"
title: 存储后端
description: StorageBackend抽象接口与SQLAlchemy默认实现——11个接口方法、ORM数据模型、Session管理、自定义后端开发
tags: [sphinx-websupport, storage, sqlalchemy, database, orm, backend]
generated: { by: "reference_agent/trae-glm", at: "2026-08-21T15:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T17:00:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: websupport-source
    resource: /references/websupport-source.md
---

# 存储后端

存储后端负责websupport中所有持久化数据的存取，包括文档节点、评论、投票记录。系统通过抽象基类 `StorageBackend` 定义接口，默认提供基于SQLAlchemy的实现。

## StorageBackend 抽象基类

定义在 `sphinxcontrib.websupport.storage` 模块中，是所有存储后端必须实现的接口。共11个方法：

### 构建阶段方法

| 方法 | 签名 | 说明 |
|------|------|------|
| `pre_build()` | `()` | 构建开始前调用，准备数据库（创建会话等） |
| `has_node(id)` | `(id) -> bool` | 检查节点是否已存在（增量构建去重） |
| `add_node(id, document, source)` | `(id, document, source)` | 添加文档节点到存储 |
| `post_build()` | `()` | 构建结束后调用（提交事务、关闭会话等） |

### 运行时CRUD方法

| 方法 | 签名 | 说明 |
|------|------|------|
| `add_comment(text, displayed, username, time, proposal, node_id, parent_id, moderator)` | 返回评论dict | 添加评论（含提议diff） |
| `delete_comment(comment_id, username, moderator)` | 返回bool | 删除评论（软删/硬删） |
| `get_metadata(docname, moderator)` | 返回 `{node_id: count}` | 获取文档的节点评论计数 |
| `get_data(node_id, username, moderator)` | 返回 `{source, comments}` | 获取节点原文和嵌套评论树 |
| `process_vote(comment_id, username, value)` | `()` | 处理用户投票（-1/0/1） |
| `update_username(old_username, new_username)` | `()` | 批量更新用户名 |
| `accept_comment(comment_id)` | `()` | 审核通过评论（设displayed=True） |

所有方法默认抛出 `NotImplementedError`，自定义后端必须实现这些方法。

## SQLAlchemyStorage 默认实现

`SQLAlchemyStorage` 定义在 `storage/sqlalchemystorage.py`，是默认存储后端。

### 初始化

```python
class SQLAlchemyStorage(StorageBackend):
    def __init__(self, uri):
        self.engine = sqlalchemy.create_engine(uri)
        Base.metadata.bind = self.engine
        Base.metadata.create_all(bind=self.engine)
        Session.configure(bind=self.engine)
```

初始化时：
1. 创建SQLAlchemy引擎（支持SQLite/MySQL/PostgreSQL等）
2. 将MetaData绑定到引擎
3. 自动创建所有表（`create_all`是幂等操作，已有表不会重建）
4. 配置Session工厂

要求SQLAlchemy版本 ≥ 1.4，导入时检查版本。

### 默认数据库路径

当 `WebSupport(storage=None)` 时，自动创建SQLite数据库：

```python
db_path = path.join(self.datadir, 'db', 'websupport.db')
storage = 'sqlite:///' + db_path
```

即默认数据库文件位于 `builddir/data/db/websupport.db`。

### Session管理模式

SQLAlchemyStorage采用**会话分离**模式：

- **构建阶段**：`pre_build()` 创建一个持久的 `build_session`，`add_node()` 在构建过程中复用同一会话，`post_build()` 时commit并close
- **运行时**：每个API方法（add_comment/delete_comment/get_data等）都独立创建新Session，操作完成后commit并close

这种设计避免了多线程环境下Session共享的问题（Web应用中每个请求在不同线程执行）。

## ORM数据模型

定义在 `storage/sqlalchemy_db.py` 中。

### Base与Session

```python
Base = declarative_base()
Session = sessionmaker()
db_prefix = "sphinx_"
```

所有表名以 `sphinx_` 为前缀，避免与应用中其他表冲突。

### Node模型

```python
class Node(Base):
    __tablename__ = "sphinx_nodes"
    id = Column(String(32), primary_key=True)       # 节点UUID
    document = Column(String(256), nullable=False)   # 所属文档名
    source = Column(Text, nullable=False)            # 原始reST文本
```

Node代表文档中一个可评论的段落。主要方法：

**nested_comments(username, moderator)**：查询该节点下的所有评论并构建为嵌套树结构。

```python
def nested_comments(self, username, moderator):
    session = Session()
    if username:
        # 带投票信息查询：outerjoin CommentVote表
        sq = session.query(CommentVote).filter(CommentVote.username == username).subquery()
        cvalias = aliased(CommentVote, sq)
        q = session.query(Comment, cvalias.value).outerjoin(cvalias)
    else:
        q = session.query(Comment)
    
    # 物化路径查询：所有后代评论的path以"{node_id}."开头
    q = q.filter(Comment.path.like(str(self.id) + ".%"))
    if not moderator:
        q = q.filter(Comment.displayed == true())
    results = q.order_by(Comment.path).all()
    session.close()
    return self._nest_comments(results, username)
```

**_nest_comments(results, username)**：将按path排序的扁平评论列表转换为嵌套树，使用list_stack算法（详见[物化路径评论树](07-materialized-path.md)）。

### Comment模型

```python
class Comment(Base):
    __tablename__ = "sphinx_comments"
    id = Column(Integer, primary_key=True)            # 自增ID
    rating = Column(Integer, nullable=False)          # 评分
    time = Column(DateTime, nullable=False)           # 创建时间
    text = Column(Text, nullable=False)               # 评论HTML内容
    displayed = Column(Boolean, index=True, default=False)  # 审核状态
    username = Column(String(64))                     # 评论者
    proposal = Column(Text)                           # 提议修改原文
    proposal_diff = Column(Text)                      # 提议修改HTML diff
    path = Column(String(256), index=True)            # 物化路径
    node_id = Column(String(32), ForeignKey("sphinx_nodes.id"))
    node = relationship(Node, backref="comments")
    votes = relationship(CommentVote, backref="comment", cascade="all")
```

关键方法：

**set_path(node_id, parent_id)**：设置物化路径。评论flush到数据库获得自增ID后才能调用：
- 节点评论（顶级）：`path = "{node_id}.{comment_id}"`
- 回复评论：查询父评论的path，`path = "{parent_path}.{comment_id}"`；同时从父path解析root node_id

**serializable(vote=0)**：转换为可JSON序列化的字典，包含text/username/id/rating/age/time/vote/node/parent/proposal_diff/children/displayed字段。

**pretty_delta(delta)**：将timedelta格式化为人类可读字符串（如"3 minutes ago"、"2 hours ago"、"1 day ago"）。

### CommentVote模型

```python
class CommentVote(Base):
    __tablename__ = "sphinx_commentvote"
    username = Column(String(64), primary_key=True)       # 联合主键
    comment_id = Column(Integer, ForeignKey("sphinx_comments.id"), primary_key=True)
    value = Column(Integer, nullable=False)                # -1/0/1
```

使用联合主键（username + comment_id）确保每个用户对每条评论只有一条投票记录。

## 关键实现细节

### 评论添加流程

```python
def add_comment(self, text, displayed, username, time, proposal, node_id, parent_id, moderator):
    session = Session()
    proposal_diff = None
    proposal_diff_text = None
    
    if node_id and proposal:
        # 有提议修改：查询节点原文，生成HTML diff
        node = session.query(Node).filter(Node.id == node_id).one()
        differ = CombinedHtmlDiff(node.source, proposal)
        proposal_diff = differ.make_html()
        proposal_diff_text = differ.make_text()
    elif parent_id:
        # 回复评论：检查父评论是否已显示
        parent = session.query(Comment.displayed).filter(Comment.id == parent_id).one()
        if not parent.displayed:
            raise CommentNotAllowedError("Can't add child to a parent that is not displayed")
    
    comment = Comment(text, displayed, username, 0, time or datetime.now(), proposal, proposal_diff)
    session.add(comment)
    session.flush()  # 获取自增ID
    comment.set_path(node_id, parent_id)  # 设置物化路径（需要ID）
    session.commit()
    d = comment.serializable()
    d['document'] = comment.node.document
    d['proposal_diff_text'] = proposal_diff_text
    session.close()
    return d
```

关键步骤：
1. 提议diff在事务内生成（需要查询Node.source）
2. 父评论displayed检查防止对未审核评论回复（否则会破坏树结构）
3. 先flush获取自增ID，再set_path（物化路径需要评论ID）
4. 返回的字典额外包含document（文档名）和proposal_diff_text（纯文本diff）

### 评论删除逻辑

```python
def delete_comment(self, comment_id, username, moderator):
    session = Session()
    comment = session.query(Comment).filter(Comment.id == comment_id).one()
    if moderator:
        # 硬删除：通过物化路径级联删除所有后代
        session.query(Comment).filter(Comment.path.like(comment.path + '.%')).delete(False)
        session.delete(comment)
        session.commit()
        session.close()
        return True
    elif comment.username == username:
        # 软删除：标记为[deleted]，保留记录防止孤儿评论
        comment.username = '[deleted]'
        comment.text = '[deleted]'
        comment.proposal = ''
        session.commit()
        session.close()
        return False
    else:
        session.close()
        raise UserNotAuthorizedError()
```

硬删除使用 `path LIKE 'comment.path.%'` 匹配所有后代（物化路径的特性：子节点路径以父节点路径+"."开头）。`delete(False)` 的False参数表示不使用fetch先加载再删除，直接执行SQL DELETE。

### 投票处理

```python
def process_vote(self, comment_id, username, value):
    session = Session()
    # outerjoin查询：获取评论和用户已有投票（可能不存在）
    subquery = session.query(CommentVote).filter(CommentVote.username == username).subquery()
    vote_alias = aliased(CommentVote, subquery)
    q = session.query(Comment, vote_alias).outerjoin(vote_alias).filter(Comment.id == comment_id)
    comment, vote = q.one()
    
    if vote is None:
        # 首次投票
        vote = CommentVote(comment_id, username, value)
        comment.rating += value
    else:
        # 改票：评分差值调整
        comment.rating += value - vote.value
        vote.value = value
    
    session.add(vote)
    session.commit()
    session.close()
```

使用outerjoin处理"首次投票"（vote为None）和"改票"（vote已存在）两种情况，避免了先查询再判断的两次数据库访问。

### 元数据查询

```python
def get_metadata(self, docname, moderator):
    session = Session()
    # 子查询：按node_id分组统计评论数
    subquery = session.query(
        Comment.node_id, func.count('*').label('comment_count')
    ).group_by(Comment.node_id).subquery()
    # outerjoin：无评论的节点也返回（count=0）
    nodes = session.query(Node.id, subquery.c.comment_count).outerjoin(
        subquery, Node.id == subquery.c.node_id
    ).filter(Node.document == docname)
    session.close()
    session.commit()
    return {k: v or 0 for k, v in nodes}  # None转0
```

使用outerjoin确保没有评论的节点也在结果中（评论数为0），前端据此显示"0 comments"。

## 自定义存储后端

要实现自定义存储后端（如MongoDB、Redis、REST API等），继承 `StorageBackend` 并实现所有11个方法。

### 最小实现示例

```python
from sphinxcontrib.websupport.storage import StorageBackend

class MemoryStorage(StorageBackend):
    """简单的内存存储后端（仅用于测试）"""
    
    def __init__(self):
        self.nodes = {}  # id -> {document, source}
        self.comments = {}  # id -> comment_dict
        self.votes = {}  # (username, comment_id) -> value
        self._next_id = 1
    
    def pre_build(self):
        pass
    
    def has_node(self, id):
        return id in self.nodes
    
    def add_node(self, id, document, source):
        self.nodes[id] = {'document': document, 'source': source}
    
    def post_build(self):
        pass
    
    def add_comment(self, text, displayed, username, time, proposal, node_id, parent_id, moderator):
        cid = str(self._next_id)
        self._next_id += 1
        comment = {
            'id': cid, 'text': text, 'username': username,
            'rating': 0, 'displayed': displayed,
            'proposal_diff': None, 'children': [],
        }
        self.comments[cid] = comment
        return comment
    
    # ... 实现其他方法 ...

# 使用自定义后端
support = WebSupport(builddir='./data', storage=MemoryStorage())
```

### 自定义后端注意事项

1. **构建/运行会话分离**：`pre_build`/`add_node`/`post_build` 在构建阶段调用（单线程），其他方法在运行时调用（多线程），需注意线程安全
2. **物化路径**：如果自定义后端需要支持嵌套评论，建议复用物化路径模式（`{node_id}.{comment_id}.{child_id}...`），便于按路径前缀查询子树
3. **nested_comments逻辑**：`get_data` 返回的comments必须是嵌套树结构（children字段递归嵌套），前端JS依赖此结构
4. **displayed过滤**：非moderator请求必须过滤掉displayed=False的评论
5. **软删除vs硬删除**：用户自删应软删除（标记[deleted]），审核员删除可以硬删除

## 相关概念

- [评论系统](05-comment-system.md)
- [物化路径评论树](07-materialized-path.md)
- [自定义存储后端](../examples/custom-storage-backend.md)
- [Flask完整集成示例](../examples/flask-integration.md)
