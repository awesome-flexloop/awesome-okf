---
okf_version: "0.2"
type: index
title: "sphinxcontrib-websupport 实战示例"
---

# 实战示例

本目录包含 4 个完整的可运行示例，覆盖从基础构建到高级扩展的渐进式学习路径。

* [基本构建与文档服务](basic-build-and-serve.md) — 初始化 WebSupport、构建文档、获取文档数据的完整入门流程。对应概念：[WebSupport API](../concepts/03-websupport-api.md)、[Builder 系统](../concepts/04-builder-system.md)。
* [Flask Web 应用集成](flask-integration.md) — 将 sphinxcontrib-websupport 集成到 Flask 应用，实现文档浏览、评论、投票、搜索、审核的完整 RESTful API。对应概念：[WebSupport API](../concepts/03-websupport-api.md)、[评论系统](../concepts/05-comment-system.md)、[前端集成](../concepts/08-frontend-integration.md)。
* [自定义存储后端](custom-storage-backend.md) — 继承 StorageBackend 抽象基类实现内存存储和 Redis 存储骨架，涵盖 11 个接口方法的完整实现要点。对应概念：[存储后端抽象](../concepts/06-storage-backend.md)。
* [评论审核与提议修改工作流](comment-moderation-workflow.md) — moderation_callback 配置、版主审核队列、投票系统、proposal diff 展示、用户删除与更名的完整工作流演示。对应概念：[评论系统](../concepts/05-comment-system.md)、[物化路径评论树](../concepts/07-materialized-path.md)。
