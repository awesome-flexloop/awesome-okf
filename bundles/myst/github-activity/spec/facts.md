---
type: spec
title: github-activity 源码事实清单
description: github-activity 源码事实清单
tags:
- github-activity
- spec
- facts
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
verified: grep-verified
status: stable
stale_after: '2027-08-23'
sources:
- id: github-activity-source
  resource: /references/activity-source.md
  title: github-activity activity-source
---

# github-activity 源码事实清单

> R 阶段采集的零推测事实，每个事实可通过源码路径验证。

## 项目元数据

- F-001: 包名为 `github-activity`，通过GitHub GraphQL API生成仓库活动变更日志
- F-002: 核心Python文件7个：`__init__.py`、`cli.py`、`github_activity.py`（核心逻辑）、`graphql.py`（GraphQL客户端）、`auth.py`（认证）、`cache.py`（缓存）、`git.py`（Git操作）
- F-003: 使用 pandas + numpy 处理活动数据，使用 requests 调用GitHub API
- F-004: 使用 dateutil.parser 解析日期，pytz 处理时区

## PR分类标签（TAGS_METADATA_BASE）

- F-005: 内置8种PR分类，按优先级排列：api_change、new、deprecate、enhancement、bug、maintenance、documentation、ci
- F-006: 每种分类包含tags（标签匹配列表）和pre（标题前缀匹配列表）
- F-007: api_change类匹配标签：api-change/apichange/breaking，前缀：BREAK/BREAKING/BRK/UPGRADE
- F-008: new类匹配标签：feature/new，前缀：NEW/FEAT/FEATURE
- F-009: deprecate类匹配标签：deprecation/deprecate，前缀：DEPRECATE/DEPRECATION/DEP
- F-010: enhancement类匹配标签：enhancement/enhancements，前缀：ENH/ENHANCEMENT/IMPROVE/IMP
- F-011: bug类匹配标签：bug/bugfix/bugs，前缀：FIX/BUG
- F-012: maintenance类匹配标签：maintenance/maint，前缀：MAINT/MNT
- F-013: documentation类匹配标签：documentation/docs/doc，前缀：DOC/DOCS
- F-014: ci类匹配标签：ci/continuous-integration，前缀：CI

## 核心API

- F-015: `get_activity()` 是核心函数，获取指定仓库/组织的活动数据
- F-016: 返回 pandas DataFrame，包含PR/issue的详细信息
- F-017: 支持按时间范围、标签、分支等过滤
- F-018: `generate_activity_markdown()` 将活动数据转换为Markdown变更日志
- F-019: `generate_all_activity_md()` 生成完整的变更日志文档

## GraphQL客户端（graphql.py）

- F-020: `GitHubGraphQlQuery` 类封装GraphQL API调用
- F-021: 使用GitHub v4 GraphQL API端点：`https://api.github.com/graphql`
- F-022: 通过Bearer token认证
- F-023: 支持分页查询（pageInfo.hasNextPage/endCursor）
- F-024: 查询PR列表字段：title/number/url/author/labels/mergedAt/closedAt等

## 认证（auth.py）

- F-025: `TokenAuth` 类实现 requests.auth.AuthBase 接口
- F-026: Token从环境变量 `GITHUB_TOKEN` 获取
- F-027: 支持通过参数传入token

## 缓存（cache.py）

- F-028: `_cache_data` 装饰器提供API响应缓存
- F-029: 缓存存储在临时目录中
- F-030: 减少重复API调用，避免速率限制

## CLI（cli.py）

- F-031: CLI基于Click框架，入口命令为 `github-activity`
- F-032: 主要参数：仓库名（如 `executablebooks/github-activity`）、`--since`/`--until`（时间范围）、`--kind`（pr/issue）、`--auth`（token）、`--output`（输出文件）、`--cache`（缓存）、`--tags`（标签分类配置）
- F-033: 支持生成Markdown格式的变更日志

## Git集成（git.py）

- F-034: 使用subprocess调用git命令
- F-035: 可自动检测仓库的标签/分支作为时间范围
- F-036: `TemporaryDirectory` 用于临时克隆仓库获取标签信息
