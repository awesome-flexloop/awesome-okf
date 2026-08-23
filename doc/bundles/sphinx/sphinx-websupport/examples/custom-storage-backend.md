---
okf_version: "0.2"
type: "example"
title: "自定义存储后端"
sources: ["sphinxcontrib/websupport/storage/__init__.py", "sphinxcontrib/websupport/storage/sqlalchemystorage.py"]
---

# 自定义存储后端

本示例演示如何实现自定义 StorageBackend，将评论数据存储到非 SQLAlchemy 后端（如 MongoDB、Redis 或纯内存）。对应概念：[存储后端抽象](../concepts/06-storage-backend.md)。

## StorageBackend 接口契约

StorageBackend 定义了 11 个必须实现的方法，分为构建期和运行期两组：

| 方法 | 调用时机 | 用途 |
|------|----------|------|
| `pre_build()` | 构建开始前 | 准备存储（建表、清空缓存等） |
| `add_node(id, document, source)` | 每个文档节点 | 注册可评论节点 |
| `post_build()` | 构建完成后 | 提交事务、清理临时数据 |
| `has_node(id)` | 运行期 | 检查节点是否存在 |
| `add_comment(...)` | 发表评论 | 存储新评论 |
| `delete_comment(...)` | 删除评论 | 软删除评论 |
| `get_metadata(docname, moderator)` | 获取文档 | 返回节点→评论数映射 |
| `get_data(node_id, username, moderator)` | 获取评论 | 返回评论树+源文本 |
| `process_vote(comment_id, username, value)` | 投票 | 记录投票 |
| `accept_comment(comment_id)` | 审核通过 | 将待审核评论标记为显示 |
| `update_username(old, new)` | 用户更名 | 批量更新用户名 |

## 完整示例：内存存储后端

```python
"""
自定义内存存储后端示例。

实现一个基于 Python dict 的 StorageBackend，适用于测试和演示。
生产环境建议使用 Redis/MongoDB 等持久化存储。

引用事实：
- StorageBackend 是抽象基类，11个方法必须全部实现
- add_comment 返回值需包含 id、username、text、time、vote、rating 等字段
- get_data 返回 {"source": str, "comments": list[dict]} 结构
- 评论使用物化路径（node_id.comment_id.child_id）构建树
- 非版主只能看到 displayed=True 的评论
"""

import time
from datetime import datetime
from sphinxcontrib.websupport.storage import StorageBackend
from sphinxcontrib.websupport.errors import UserNotAuthorizedError


class InMemoryStorage(StorageBackend):
    """纯内存存储后端，所有数据保存在 Python dict 中。

    适用于：
    - 单元测试（无需数据库）
    - 单进程演示环境
    - 原型开发快速验证

    不适用于：
    - 多进程/多实例部署
    - 需要数据持久化的生产环境
    """

    def __init__(self):
        self.nodes = {}           # node_id -> {"document", "source"}
        self.comments = {}        # comment_id -> comment_dict
        self.votes = {}           # (comment_id, username) -> vote_value
        self._next_comment_id = 1
        self._building = False

    # ============ 构建期方法 ============

    def pre_build(self):
        """构建开始前调用。重建时清空旧节点数据（保留评论）。"""
        self.nodes.clear()
        self._building = True

    def add_node(self, id, document, source):
        """注册一个可评论的文档节点。

        参数:
            id: 节点唯一标识符（Sphinx 生成的锚点 ID）
            document: 所属文档名（如 'index'、'tutorial/install'）
            source: 节点对应的源文本（reStructuredText）
        """
        self.nodes[id] = {
            'document': document,
            'source': source,
        }

    def post_build(self):
        """构建完成后调用。清理被删除节点的孤立评论。"""
        self._building = False
        # 清理指向不存在节点的顶层评论
        to_delete = []
        for cid, comment in self.comments.items():
            if comment['node_id'] not in self.nodes:
                to_delete.append(cid)
        for cid in to_delete:
            del self.comments[cid]

    def has_node(self, id):
        """检查节点是否存在。"""
        return id in self.nodes

    # ============ 运行期方法 ============

    def add_comment(self, text, displayed, username, time_,
                    proposal, node_id, parent_id, moderator):
        """添加一条评论。

        返回值必须是包含以下键的字典：
        - id: 评论唯一标识
        - username: 用户名（匿名评论为 'anonymous'）
        - text: 渲染后的 HTML 文本
        - time: 时间戳
        - vote: 当前用户的投票值（新增时为 0）
        - rating: 评论总评分（新增时为 0）
        - displayed: 是否可见
        - proposal_diff: 修改提议的 HTML diff（如有 proposal）
        - children: 子评论列表（顶层为空列表，树由 WebSupport 组装）
        """
        comment_id = str(self._next_comment_id)
        self._next_comment_id += 1

        # 物化路径：父评论的 path 加上当前 ID
        if parent_id:
            parent = self.comments.get(parent_id)
            if not parent:
                raise ValueError(f"Parent comment {parent_id} not found")
            # 不能回复隐藏评论，否则破坏树结构
            if not parent['displayed'] and not moderator:
                from sphinxcontrib.websupport.errors import CommentNotAllowedError
                raise CommentNotAllowedError(
                    "Cannot reply to a hidden comment"
                )
            path = f"{parent['path']}.{comment_id}"
        else:
            path = f"{node_id}.{comment_id}"

        comment = {
            'id': comment_id,
            'node_id': node_id,
            'parent_id': parent_id,
            'path': path,
            'username': username or 'anonymous',
            'text': text,           # WebSupport 内部会做 rst->html 渲染
            'proposal': proposal,
            'proposal_diff': '',    # 由 WebSupport 填充
            'time': time_,
            'displayed': displayed,
            'moderator': moderator,
            'rating': 0,
            'children': [],
        }
        self.comments[comment_id] = comment
        return comment

    def delete_comment(self, comment_id, username, moderator):
        """删除评论（软删除）。

        权限规则：
        - 版主（moderator=True）可删除任意评论
        - 普通用户只能删除自己的评论
        - 删除后评论内容和用户名替换为 '[deleted]'
        """
        comment = self.comments.get(comment_id)
        if not comment:
            return

        if not moderator and comment['username'] != username:
            raise UserNotAuthorizedError(
                "You are not authorized to delete this comment"
            )

        comment['text'] = '[deleted]'
        comment['username'] = '[deleted]'
        comment['displayed'] = False

    def get_metadata(self, docname, moderator):
        """获取文档的评论元数据。

        返回 {node_id: comment_count} 字典，用于显示评论数徽章。
        非版主只统计 displayed=True 的评论。
        """
        metadata = {}
        for node_id, node in self.nodes.items():
            if node['document'] != docname:
                continue
            count = 0
            for c in self.comments.values():
                if c['node_id'] == node_id:
                    if moderator or c['displayed']:
                        count += 1
            if count > 0:
                metadata[node_id] = count
        return metadata

    def get_data(self, node_id, username, moderator):
        """获取节点的源文本和评论树。

        返回 {"source": str, "comments": list}，其中 comments 是
        嵌套的树结构，每个评论包含 children 列表。
        """
        node = self.nodes.get(node_id)
        if not node:
            return {"source": "", "comments": []}

        # 收集该节点的所有顶层评论和回复
        all_comments = []
        for c in self.comments.values():
            if c['node_id'] == node_id:
                if moderator or c['displayed']:
                    all_comments.append(c)

        # 按物化路径排序并构建树
        all_comments.sort(key=lambda c: c['path'])

        # 构建树：path 格式为 node_id.c1.c2.c3
        # 顶层评论的 path 中只有一个点后的 ID（node_id.cid）
        tree = []
        comment_map = {c['id']: dict(c, children=[]) for c in all_comments}

        for c in all_comments:
            c_copy = comment_map[c['id']]
            # 附加当前用户的投票状态
            c_copy['vote'] = self.votes.get((c['id'], username), 0)

            if c['parent_id'] and c['parent_id'] in comment_map:
                comment_map[c['parent_id']]['children'].append(c_copy)
            else:
                tree.append(c_copy)

        return {
            "source": node['source'],
            "comments": tree,
        }

    def process_vote(self, comment_id, username, value):
        """处理投票。

        value 只能是 -1（反对）、0（取消）、1（赞成）。
        同一用户对同一评论只能投一票，重复投票会覆盖。
        """
        if value not in (-1, 0, 1):
            raise ValueError(
                f"vote value {value} out of range (-1, 1)"
            )

        comment = self.comments.get(comment_id)
        if not comment:
            return

        # 取消旧投票
        old_value = self.votes.get((comment_id, username), 0)
        comment['rating'] -= old_value

        # 记录新投票
        if value == 0:
            self.votes.pop((comment_id, username), None)
        else:
            self.votes[(comment_id, username)] = value
            comment['rating'] += value

    def update_username(self, old_username, new_username):
        """用户更名时批量更新评论和投票中的用户名。"""
        for comment in self.comments.values():
            if comment['username'] == old_username:
                comment['username'] = new_username

        # 更新投票记录的 key（需要重建）
        old_keys = [k for k in self.votes if k[1] == old_username]
        for cid, uname in old_keys:
            value = self.votes.pop((cid, uname))
            self.votes[(cid, new_username)] = value

    def accept_comment(self, comment_id):
        """版主审核通过评论，将其标记为可见。"""
        comment = self.comments.get(comment_id)
        if comment:
            comment['displayed'] = True


# ============ 使用示例 ============

def demo_inmemory_storage():
    """演示 InMemoryStorage 的使用。"""
    from sphinxcontrib.websupport import WebSupport

    # 使用自定义存储后端
    storage = InMemoryStorage()
    support = WebSupport(
        srcdir='/path/to/docs',
        builddir='/path/to/build',
        storage=storage,  # 传入实例而非连接字符串
    )

    # 构建文档
    support.build()

    # 发表评论
    comment = support.add_comment(
        text='这是一条测试评论',
        node_id='document-nodes-id',  # 从 get_data 获取实际 node_id
        username='testuser',
    )
    print(f"评论已创建: ID={comment['id']}")

    # 投票
    support.process_vote(comment['id'], 'user1', '1')

    # 获取评论
    data = support.get_data('document-nodes-id', username='user1')
    print(f"评论数: {len(data['comments'])}")


if __name__ == '__main__':
    demo_inmemory_storage()
```

## Redis 存储后端骨架（生产级参考）

```python
"""Redis 存储后端骨架（需要 redis-py 客户端）。"""

import json
from sphinxcontrib.websupport.storage import StorageBackend


class RedisStorage(StorageBackend):
    """基于 Redis 的存储后端。

    Key 设计：
    - nodes:{docname} -> Hash(node_id -> source)
    - comment:{id} -> JSON(comment_dict)
    - node_comments:{node_id} -> Sorted Set(comment_ids by time)
    - comment_children:{parent_id} -> List(child_ids)
    - votes:{comment_id} -> Hash(username -> value)
    - comment_path:{id} -> String(materialized path)
    """

    def __init__(self, redis_url='redis://localhost:6379/0'):
        import redis
        self.r = redis.from_url(redis_url, decode_responses=True)

    def add_node(self, id, document, source):
        self.r.hset(f'nodes:{document}', id, source)

    def add_comment(self, text, displayed, username, time_,
                    proposal, node_id, parent_id, moderator):
        import uuid
        comment_id = str(uuid.uuid4())
        if parent_id:
            parent_path = self.r.get(f'comment_path:{parent_id}')
            path = f'{parent_path}.{comment_id}'
            self.r.rpush(f'comment_children:{parent_id}', comment_id)
        else:
            path = f'{node_id}.{comment_id}'
        comment = {
            'id': comment_id, 'text': text, 'username': username,
            'time': time_, 'displayed': displayed, 'rating': 0,
            'node_id': node_id, 'parent_id': parent_id,
        }
        self.r.set(f'comment:{comment_id}', json.dumps(comment))
        self.r.set(f'comment_path:{comment_id}', path)
        self.r.zadd(f'node_comments:{node_id}', {comment_id: time_})
        return {**comment, 'children': []}

    # ... 其余方法按接口实现
```

## 关键实现要点

1. **物化路径构建**：评论的 `path` 字段格式为 `{node_id}.{c1_id}.{c2_id}...`，构建树时按路径排序即可还原层级关系。

2. **权限检查**：`delete_comment` 必须校验用户权限——非版主只能删除自己的评论，否则抛 `UserNotAuthorizedError`。

3. **软删除策略**：删除不做物理删除，而是将 text/username 标记为 `[deleted]`，保持评论树结构完整。

4. **投票幂等性**：同一用户对同一评论重复投票，应先撤销旧投票再记录新投票，确保 rating 计算正确。

5. **审核流程**：新评论的 `displayed` 默认取决于 `moderation_callback` 返回值——若设置了回调且用户非版主，评论初始为 `displayed=False`，需版主 `accept_comment()` 后才可见。
