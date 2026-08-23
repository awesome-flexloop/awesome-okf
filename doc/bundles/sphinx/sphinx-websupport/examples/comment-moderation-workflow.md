---
okf_version: "0.2"
type: "example"
title: "评论审核与提议修改工作流"
sources: ["sphinxcontrib/websupport/core.py", "sphinxcontrib/websupport/storage/sqlalchemystorage.py", "tests/test_websupport.py"]
---

# 评论审核与提议修改工作流

本示例演示 sphinxcontrib-websupport 的完整评论工作流：匿名评论控制、版主审核、提议修改与 diff 展示、投票系统。对应概念：[评论系统](../concepts/05-comment-system.md)、[物化路径评论树](../concepts/07-materialized-path.md)、[搜索适配器](../concepts/09-search-adapters.md)。

## 示例场景：文档站评论管理后台

```python
"""
评论审核与提议修改完整工作流示例。

功能演示：
1. 配置 moderation_callback 实现自动审核
2. 匿名评论控制
3. 版主审核队列处理（accept/delete）
4. 用户投票系统
5. 提议修改（proposal）与 HTML diff 展示
6. 用户更名后的评论迁移

引用事实：
- moderation_callback 在评论添加时被调用，可控制 displayed 状态
- 非版主 get_data() 只返回 displayed=True 的评论
- 版主 get_data(moderator=True) 返回所有评论，包括待审核和已删除
- 不能回复 displayed=False 的评论（避免树结构破坏）
- process_vote() 支持投票值 -1/0/1，超出范围抛 ValueError
- proposal 参数传入修改文本，WebSupport 自动生成 HTML diff
- update_username() 批量更新评论和投票记录中的用户名
"""

from datetime import datetime
from sphinxcontrib.websupport import WebSupport
from sphinxcontrib.websupport.errors import (
    CommentNotAllowedError,
    UserNotAuthorizedError,
)


# ============ 审核回调函数 ============

def moderation_callback(comment):
    """评论审核回调。在评论添加时被调用。

    参数 comment 是一个字典，包含：
    - text: 评论内容
    - username: 用户名
    - node_id: 所属节点
    - proposal: 修改提议（如有）
    - time: 时间戳

    返回值不影响流程，但可以用于：
    - 发送通知（邮件/消息队列）
    - 内容审核（敏感词检测）
    - 日志记录
    - 自动批准规则
    """
    username = comment.get('username', 'anonymous')
    text = comment.get('text', '')

    # 规则1：信任用户自动通过
    trusted_users = {'admin', 'maintainer', 'doc_editor'}
    if username in trusted_users:
        print(f"[AUTO-APPROVE] Trusted user '{username}': {text[:50]}")
        return

    # 规则2：包含敏感词的评论标记为待审核（displayed=False）
    spam_keywords = {'spam', '广告', 'viagra', 'casino'}
    if any(kw in text.lower() for kw in spam_keywords):
        print(f"[FLAG-SPAM] Suspicious comment from '{username}': {text[:50]}")
        # 注意：回调不能直接修改评论的 displayed 状态
        # 实际审核通过 WebSupport 配置和 accept_comment/delete_comment 控制
        return

    # 规则3：普通评论发送通知，等待人工审核
    print(f"[NOTIFY] New comment from '{username}' awaiting moderation: {text[:50]}")


# ============ 初始化 ============

def create_support(builddir: str, srcdir: str = None, build: bool = False):
    """创建 WebSupport 实例。"""
    kwargs = {
        'builddir': builddir,
        'search': 'whoosh',
        'moderation_callback': moderation_callback,
        'allow_anonymous_comments': False,  # 禁止匿名评论
    }
    if srcdir:
        kwargs['srcdir'] = srcdir
    support = WebSupport(**kwargs)
    if build and srcdir:
        support.build()
    return support


# ============ 工作流 1：发表评论与自动审核 ============

def workflow_add_comments(support: WebSupport, node_id: str):
    """演示不同用户发表评论的场景。"""
    print("=" * 60)
    print("工作流 1：发表评论")
    print("=" * 60)

    # 场景 A：信任用户发表评论 → 自动显示
    comment1 = support.add_comment(
        text='这个函数的参数说明很清晰，谢谢！',
        node_id=node_id,
        username='admin',
    )
    print(f"[信任用户评论] ID={comment1['id']}, displayed=True")

    # 场景 B：普通用户发表评论 → 待审核（displayed=False）
    comment2 = support.add_comment(
        text='我觉得这里应该加一个示例代码。',
        node_id=node_id,
        username='new_user',
        displayed=False,  # 普通用户评论默认待审核
    )
    print(f"[普通用户评论] ID={comment2['id']}, displayed=False (待审核)")

    # 场景 C：在已有评论下回复
    reply = support.add_comment(
        text='同意，示例代码确实有帮助！',
        parent_id=str(comment1['id']),  # 回复评论1
        username='reader1',
        displayed=False,
    )
    print(f"[回复评论] ID={reply['id']}, parent={comment1['id']}")

    # 场景 D：尝试回复隐藏评论 → 应该抛出异常
    try:
        support.add_comment(
            text='试图回复待审核评论',
            parent_id=str(comment2['id']),  # comment2 是 displayed=False
            username='bad_user',
        )
        print("[错误] 应该抛出 CommentNotAllowedError!")
    except CommentNotAllowedError:
        print("[正确] 回复待审核评论被拒绝（防止树结构破坏）")

    return comment1, comment2, reply


# ============ 工作流 2：版主审核队列 ============

def workflow_moderation(support: WebSupport, node_id: str, pending_comment: dict):
    """版主审核待审核评论。"""
    print("\n" + "=" * 60)
    print("工作流 2：版主审核")
    print("=" * 60)

    # 普通用户视角：只能看到已通过的评论
    user_data = support.get_data(node_id, username='random_user')
    print(f"[普通用户视角] 可见评论数: {len(user_data['comments'])}")
    for c in user_data['comments']:
        print(f"  - [{c['username']}] {c['text'][:40]}")

    # 版主视角：看到所有评论（包括待审核和已删除）
    mod_data = support.get_data(node_id, moderator=True)
    print(f"\n[版主视角] 所有评论数: {len(mod_data['comments'])}")
    for c in mod_data['comments']:
        status = "✅已通过" if c['displayed'] else "⏳待审核"
        print(f"  - {status} [{c['username']}] {c['text'][:40]}")

    # 审核通过：将 pending_comment 标记为 displayed
    support.accept_comment(pending_comment['id'], moderator=True)
    print(f"\n[审核通过] 评论 {pending_comment['id']} 已发布")

    # 审核后普通用户可见
    user_data = support.get_data(node_id, username='random_user')
    print(f"[审核后普通用户] 可见评论数: {len(user_data['comments'])}")


# ============ 工作流 3：投票系统 ============

def workflow_voting(support: WebSupport, node_id: str, comment_id: str):
    """演示评论投票。"""
    print("\n" + "=" * 60)
    print("工作流 3：评论投票")
    print("=" * 60)

    # 三个用户投赞成票
    for user in ['alice', 'bob', 'charlie']:
        support.process_vote(comment_id, user, '1')

    data = support.get_data(node_id, username='alice')
    rating = data['comments'][0]['rating']
    alice_vote = data['comments'][0]['vote']
    print(f"[三票赞成后] 评分: {rating}, alice的投票: {alice_vote}")

    # alice 改投反对票
    support.process_vote(comment_id, 'alice', '-1')
    data = support.get_data(node_id, username='alice')
    print(f"[alice改反对后] 评分: {data['comments'][0]['rating']}")

    # alice 取消投票
    support.process_vote(comment_id, 'alice', '0')
    data = support.get_data(node_id, username='alice')
    print(f"[alice取消后] 评分: {data['comments'][0]['rating']}, alice投票: {data['comments'][0]['vote']}")

    # 非法投票值
    try:
        support.process_vote(comment_id, 'bad_user', '2')
    except ValueError as e:
        print(f"[非法投票] 捕获异常: {e}")


# ============ 工作流 4：提议修改 ============

def workflow_proposal(support: WebSupport, node_id: str):
    """演示提议修改功能。"""
    print("\n" + "=" * 60)
    print("工作流 4：提议修改（Proposal）")
    print("=" * 60)

    # 获取节点源文本
    data = support.get_data(node_id)
    source = data.get('source', '')
    print(f"原始文本长度: {len(source)} 字符")

    if source:
        # 构造修改提议：对源文本进行编辑
        # 实际应用中，前端提供 diff 编辑器让用户修改源文本
        modified = source[:len(source)//2] + "【建议修改】" + source[len(source)//2:]

        proposal_comment = support.add_comment(
            text='建议更新这段描述，使其更准确。',
            node_id=node_id,
            username='contributor',
            proposal=modified,  # 传入修改后的完整文本
            displayed=False,
        )
        print(f"[修改提议] 评论 ID={proposal_comment['id']}")
        print(f"  proposal_diff 由 WebSupport 自动生成 HTML diff")

        # 版主审核提议
        support.accept_comment(proposal_comment['id'], moderator=True)
        print("[修改提议已通过] 其他用户现在可以看到此提议和 diff")


# ============ 工作流 5：用户删除与更名 ============

def workflow_user_management(support: WebSupport, node_id: str, comment_id: str):
    """演示用户删除自己的评论和用户更名。"""
    print("\n" + "=" * 60)
    print("工作流 5：用户删除与更名")
    print("=" * 60)

    # 用户删除自己的评论
    support.delete_comment(comment_id, username='reader1')
    data = support.get_data(node_id, moderator=True)
    for c in data['comments']:
        for child in c.get('children', []):
            if child['id'] == comment_id:
                print(f"[自删后] 评论内容: {child['text']}, 用户名: {child['username']}")

    # 其他用户试图删除评论 → 被拒绝
    try:
        support.delete_comment(comment_id, username='stranger', moderator=False)
    except UserNotAuthorizedError:
        print("[正确] 普通用户无法删除他人评论")

    # 版主强制删除
    # support.delete_comment(comment_id, username='mod', moderator=True)

    # 用户更名：批量更新所有评论中的用户名
    support.update_username('new_user', 'experienced_user')
    print("[用户更名] 'new_user' → 'experienced_user'，所有评论/投票已更新")


# ============ 完整运行 ============

def run_demo():
    """运行完整工作流演示。"""
    import tempfile
    import os

    # 使用测试文档目录（需要实际存在的 Sphinx 项目）
    # 此处演示 API 调用流程，实际使用时替换为真实路径
    builddir = tempfile.mkdtemp(prefix='websupport-demo-')
    print(f"演示构建目录: {builddir}")
    print("注意：完整演示需要真实的 Sphinx srcdir 来构建文档")
    print("以下演示 API 调用流程和逻辑，不实际执行 build()\n")

    # 实际使用时：
    # support = create_support(builddir, srcdir='/path/to/docs', build=True)
    # nodes = ...  # 从数据库查询可用的 node_id
    # comment1, comment2, reply = workflow_add_comments(support, node_id)
    # workflow_moderation(support, node_id, comment2)
    # workflow_voting(support, node_id, comment1['id'])
    # workflow_proposal(support, node_id)
    # workflow_user_management(support, node_id, reply['id'])

    print("工作流演示逻辑说明：")
    print("1. moderation_callback 在每条评论添加时触发，用于通知/日志")
    print("2. allow_anonymous_comments=False 要求用户必须登录才能评论")
    print("3. 普通用户评论默认 displayed=False，需版主 accept_comment() 通过")
    print("4. 不能回复待审核评论（displayed=False），否则抛 CommentNotAllowedError")
    print("5. 版主 get_data(moderator=True) 可看到所有评论（含待审核/已删除）")
    print("6. 投票值范围 -1/0/1，超出抛 ValueError")
    print("7. proposal 参数传入修改文本，WebSupport 自动生成 CombinedHtmlDiff")
    print("8. 删除评论是软删除（text/username 标记为 [deleted]）")
    print("9. update_username() 批量更新评论和投票记录中的用户名")


if __name__ == '__main__':
    run_demo()
```

## 审核状态机

```
                    ┌──────────────┐
                    │  新评论提交   │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
     ┌────────────┐ ┌────────────┐ ┌────────────┐
     │ 信任用户    │ │ 匿名/普通   │ │ 垃圾评论    │
     │ displayed=T │ │ displayed=F │ │ displayed=F │
     └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
           │              │              │
           │              ▼              │
           │     ┌──────────────┐        │
           │     │  版主审核队列  │        │
           │     └──────┬───────┘        │
           │       ┌────┴────┐           │
           │       ▼         ▼           │
           │  ┌────────┐ ┌────────┐      │
           │  │ accept │ │ delete │      │
           │  │  通过   │ │  删除   │      │
           │  └───┬────┘ └───┬────┘      │
           │      ▼          ▼           │
           └─→┌────────┐ ┌────────┐←─────┘
              │ 可见   │ │[deleted]│
              │ 所有人  │ │ 软删除   │
              └────────┘ └────────┘
```

## 权限矩阵

| 操作 | 匿名用户 | 普通用户 | 版主 |
|------|---------|---------|------|
| 发表顶层评论 | 受 `allow_anonymous_comments` 控制 | ✅ | ✅ |
| 回复已显示评论 | 受配置控制 | ✅ | ✅ |
| 回复待审核评论 | ❌ | ❌ | ❌ |
| 查看已通过评论 | ✅ | ✅ | ✅ |
| 查看待审核评论 | ❌ | ❌ | ✅ |
| 删除自己的评论 | ❌ | ✅ | ✅ |
| 删除他人评论 | ❌ | ❌ | ✅ |
| 审核通过评论 | ❌ | ❌ | ✅ |
| 投票 | ✅ | ✅ | ✅ |
| 提议修改 | ✅ | ✅ | ✅ |
