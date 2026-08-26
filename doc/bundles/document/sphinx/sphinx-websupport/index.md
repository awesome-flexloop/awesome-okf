---
okf_version: "0.2"
---

# sphinxcontrib-websupport 知识库

本知识包是 Sphinx 官方 Web 集成扩展 [sphinxcontrib-websupport](https://github.com/sphinx-doc/sphinxcontrib-websupport)（BSD-2-Clause 许可证）的系统化中文源码教程，基于 sphinxcontrib-websupport v2.0.0 源码深度阅读生成，覆盖从快速上手到自定义存储后端开发的完整知识体系。所有内容均溯源至 sphinxcontrib-websupport 源码（`sphinxcontrib/websupport/` 包核心模块），遵循 [OKF v0.2 规范](concepts/00-introduction.md)。

## 入门篇（concepts/）

* [sphinxcontrib-websupport 简介](concepts/00-introduction.md) — 什么是 websupport，核心功能（评论/投票/提议/搜索），适用场景，版本 2.0.0，依赖关系。
* [5分钟快速上手](concepts/01-getting-started.md) — 安装、conf.py 配置、构建命令、最小集成示例、前端脚本引入。
* [架构总览](concepts/02-architecture-overview.md) — 双阶段架构（构建期 vs 运行期）、核心类协作、目录结构、数据流。

## 核心 API 篇（concepts/）

* [WebSupport API](concepts/03-websupport-api.md) — 唯一入口类完整 API 参考：构造参数、build()、get_document()、get_data()、add_comment()、process_vote()、accept_comment()、delete_comment()、get_search_results()、update_username()。
* [Builder 系统](concepts/04-builder-system.md) — WebSupportBuilder 继承链、文档序列化、节点标注（sphinx-websupport 锚点）、静态文件管理。

## 评论与存储篇（concepts/）

* [评论系统](concepts/05-comment-system.md) — 评论数据模型、权限控制、软删除、moderation_callback、ReST→HTML 渲染、proposal diff。
* [存储后端抽象](concepts/06-storage-backend.md) — StorageBackend 11 个接口方法、SQLAlchemyStorage 默认实现、ORM 模型、自定义后端开发。
* [物化路径评论树](concepts/07-materialized-path.md) — Materialized Path 模式（node_id.cid.cid）、树构建算法、排序规则、级联删除。

## 前端与扩展篇（concepts/）

* [前端集成](concepts/08-frontend-integration.md) — websupport.js jQuery 插件、COMMENT_OPTIONS、AJAX API 约定、UI 交互、样式定制。
* [搜索适配器](concepts/09-search-adapters.md) — BaseSearch 接口、NullSearch/WhooshSearch/XapianSearch 三种实现、索引构建与查询。

## 实战示例（examples/）

* [基本构建与文档服务](examples/basic-build-and-serve.md) — 初始化 WebSupport、构建文档、获取文档数据的完整入门流程。
* [Flask Web 应用集成](examples/flask-integration.md) — 完整 Flask 集成：文档页面、RESTful 评论 API、投票、搜索、审核。
* [自定义存储后端](examples/custom-storage-backend.md) — InMemoryStorage 和 RedisStorage 骨架实现，11 个接口方法完整说明。
* [评论审核与提议修改工作流](examples/comment-moderation-workflow.md) — moderation_callback、审核队列、投票、proposal diff、用户管理完整演示。

## 信源登记簿（references/）

* [sphinxcontrib-websupport 源码信源登记](references/websupport-source.md) — 项目信息、依赖清单、模块清单、数据库模型、搜索适配器注册表。

## 信任与生命周期说明

* **status 判定依据**：全部 16 个内容文档（10 个概念 + 4 个示例 + 1 个信源登记 + 1 个概念索引）均 `status: stable`。内容基于对 sphinxcontrib-websupport v2.0.0 源码（`external/libs/docs/sphinxcontrib-websupport/sphinxcontrib/websupport/` 目录）的逐模块阅读与事实提取，经 seven-concepts 方法论 R→I→E→V→C 五阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-12-31`。sphinxcontrib-websupport 核心架构（WebSupport 入口类/Builder/StorageBackend/BaseSearch）自 1.x 以来相对稳定，2.0.0 主要是依赖升级和清理；该日期作为针对未来大版本的保守重新评估节点。
* **核验链路**：`generated.at` 记录各文档原始生成时刻（2026-08-21）；`verified.at` 记录 V 阶段对抗审查核验事件，两者分离、可追溯。

本知识包共收录 16 个内容文档（10 个概念 + 4 个示例 + 1 个信源登记 + 1 个概念索引），另含 3 个子目录 index.md 与根 index.md、log.md。

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
