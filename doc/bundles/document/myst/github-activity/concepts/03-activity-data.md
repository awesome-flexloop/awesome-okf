---
type: Concept
title: 数据获取与处理
description: github-activity的GraphQL查询、分页机制、pandas DataFrame数据流和Markdown渲染
tags: [github, graphql, pandas, data, api, pagination]
generated: { by: "reference_agent/trae-cn", at: "2026-08-23T05:08:00Z" }
verified: grep-verified
status: stable
stale_after: 2027-08-23
sources:
  - id: ga-source
    resource: /references/activity-source.md
    title: github-activity 源码路径映射
---

# 数据获取与处理

## GitHub GraphQL API

github-activity 使用 GitHub v4 GraphQL API（`https://api.github.com/graphql`）而非 REST API v3。

### GraphQL vs REST

对比两种API获取PR列表的差异：

| 方面 | REST API v3 | GraphQL v4 |
|------|-------------|------------|
| 获取PR列表 | 1次请求（无详情） | 1次请求（指定字段） |
| 获取标签 | 每PR额外1次 | 同一请求中获取 |
| 获取作者 | 每PR额外1次 | 同一请求中获取 |
| 100个PR总请求数 | ~300+次 | 1次（分页后2-3次） |
| 速率限制消耗 | 高 | 低 |

### 查询字段

GraphQL查询获取每个PR/Issue的以下字段：
- `number`：编号
- `title`：标题
- `url`：链接
- `author.login`：作者用户名
- `labels.edges.node.name`：标签列表
- `mergedAt`/`closedAt`：合并/关闭时间
- `state`：状态（OPEN/CLOSED/MERGED）
- `isCrossRepository`：是否跨仓库PR

## 分页机制

GitHub GraphQL API使用基于游标的分页（Relay风格）：

1. 首次请求不带cursor，获取第一页（默认100条）
2. 响应中包含 `pageInfo`：
   - `hasNextPage`：是否有下一页
   - `endCursor`：下一页的游标
3. 如果 `hasNextPage` 为 true，使用 `after: endCursor` 请求下一页
4. 重复直到获取所有数据

```python
# 伪代码
has_next = True
cursor = None
all_prs = []
while has_next:
    result = graphql_query(after=cursor)
    all_prs.extend(result["pullRequests"]["nodes"])
    page_info = result["pullRequests"]["pageInfo"]
    has_next = page_info["hasNextPage"]
    cursor = page_info["endCursor"]
```

## 认证

### TokenAuth类

`auth.py` 中的 `TokenAuth` 实现了 `requests.auth.AuthBase` 接口：

```python
class TokenAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["Authorization"] = f"Bearer {self.token}"
        return r
```

### 认证方式

1. **环境变量**：`GITHUB_TOKEN` 环境变量
2. **CLI参数**：`--auth` 选项
3. **默认匿名**：无Token时匿名访问（低速率限制）

## 数据处理流水线

```
GitHub GraphQL API
       │
       ▼
  原始JSON响应
       │
       ▼ (pandas DataFrame)
  数据清洗与规范化
       │
       ▼
  PR分类（tags+pre双模式匹配）
       │
       ▼
  按类型分组聚合
       │
       ▼
  Markdown渲染输出
```

### DataFrame结构

`get_activity()` 返回的DataFrame包含以下列：

| 列名 | 说明 |
|------|------|
| `number` | PR/Issue编号 |
| `title` | 标题 |
| `url` | GitHub链接 |
| `author` | 作者用户名 |
| `labels` | 标签列表 |
| `mergedAt`/`closedAt` | 时间戳 |
| `category` | 分类结果（api_change/new/bug等） |
| `is_pr` | 是否为PR（vs Issue） |

### PR分类算法

对每个合并的PR：
1. 遍历8个分类（按优先级顺序）
2. 检查PR的labels是否匹配该分类的 `tags` 列表
3. 检查PR标题是否以该分类的 `pre` 前缀开头（如"BREAK:"、"FIX:"）
4. 如果任一匹配，归入该分类
5. 如果没有匹配，归入"其他合并PR"

### 前缀匹配实现

前缀匹配使用正则表达式检查标题开头是否包含指定前缀（不区分大小写），支持冒号分隔：

```
标题"FIX: resolve crash in parser" → 匹配bug类（前缀"FIX"）
标题"ENH add new option" → 匹配enhancement类（前缀"ENH"）
标题"BREAKING CHANGE: remove old API" → 匹配api_change类（前缀"BREAKING"）
```

## 缓存机制

`_cache_data` 装饰器缓存API响应：
- 缓存key基于查询参数（仓库、时间范围等）
- 存储在临时目录中
- 避免短时间内重复相同查询触发速率限制

## Git集成

`git.py` 模块通过subprocess调用git命令：
- 检测当前目录是否为git仓库
- 获取远程仓库URL（自动识别TARGET）
- 获取标签列表作为时间边界
- 在临时目录中克隆仓库以获取标签信息（如果需要）

## Markdown生成

`generate_activity_markdown()` 生成格式化输出：
1. 按分类分组PR
2. 每个分类生成二级标题
3. 每个PR生成列表项：`- 标题 ``#编号`` (@作者)`
4. 合并者信息可选包含

## 相关概念

- [CLI命令详解](02-cli-usage.md)
- [标签分类配置](04-configuration.md)
- [变更日志生成示例](../examples/changelog-generation.md)
