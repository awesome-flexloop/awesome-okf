---
okf_version: "0.2"
type: index
title: "sphinxcontrib-websupport 概念文档"
---

# 概念文档

本目录包含 sphinxcontrib-websupport 的 10 个核心概念文档，按学习路径排列：从入门到高级主题逐步深入。

## 入门篇

* [00-sphinxcontrib-websupport 简介](00-introduction.md) — 什么是 sphinxcontrib-websupport，核心功能（评论/投票/提议/搜索），适用场景，版本 2.0.0，依赖关系。
* [01-5分钟快速上手](01-getting-started.md) — 安装、conf.py 配置、构建命令、Flask 集成最小示例、前端脚本引入。
* [02-架构总览](02-architecture-overview.md) — 双阶段架构（构建期 vs 运行期）、核心类协作关系、目录结构、数据流。

## 核心 API 篇

* [03-WebSupport API](03-websupport-api.md) — WebSupport 类完整 API 参考：构造参数、build()、get_document()、get_data()、add_comment()、process_vote()、accept_comment()、delete_comment()、get_search_results()、update_username()。
* [04-Builder 系统](04-builder-system.md) — WebSupportBuilder 继承链、序列化机制、节点标注（sphinx-websupport 锚点）、静态文件管理、构建产物结构。

## 评论与存储篇

* [05-评论系统](05-comment-system.md) — 评论数据模型、权限控制、软删除策略、moderation_callback 回调、评论渲染（ReST→HTML）、提议修改 diff 生成。
* [06-存储后端抽象](06-storage-backend.md) — StorageBackend 抽象基类 11 个接口方法、SQLAlchemyStorage 默认实现、数据库 ORM 模型（Comment/CommentVote/Node）、自定义后端开发指南。
* [07-物化路径评论树](07-materialized-path.md) — Materialized Path 模式（node_id.cid.cid）、树构建算法、排序规则、级联删除策略、与邻接表/嵌套集的对比。

## 前端与扩展篇

* [08-前端集成](08-frontend-integration.md) — websupport.js jQuery 插件、COMMENT_OPTIONS 配置、评论弹窗/投票/回复/提议 UI 交互、AJAX API 端点约定、CSS 样式定制。
* [09-搜索适配器](09-search-adapters.md) — BaseSearch 抽象接口、NullSearch（无搜索）、WhooshSearch（纯 Python 全文检索）、XapianSearch（高性能 C++ 引擎）、搜索索引构建与查询流程。

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-getting-started
02-architecture-overview
03-websupport-api
04-builder-system
05-comment-system
06-storage-backend
07-materialized-path
08-frontend-integration
09-search-adapters
```
