---
type: Pattern
title: 双层LRU缓存模式
description: 对成功结果使用带ETag验证的长TTL缓存，对404等否定结果使用短TTL缓存，平衡API调用频率与数据新鲜度
tags: [lru-cache, dual-layer, etag, negative-caching, rate-limit, api-client]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T16:30:00+08:00" }
status: stable
source: repo2jupyterlite
applicability: 第三方API客户端、Git引用解析、URL元数据获取、任何有速率限制的API调用
---

# 双层LRU缓存模式

## 问题

调用第三方API（如GitHub API）时有速率限制（匿名60次/小时，认证5000次/小时）。需要缓存API响应以减少调用次数，但不同类型的响应需要不同的缓存策略：

- **成功响应**：数据相对稳定（如commit SHA一旦创建永不改变），可以长期缓存，但仍需条件验证（ETag）
- **否定响应（404）**：仓库不存在或分支不存在是暂时状态（仓库可能之后被创建），只能短时间缓存

如果只使用统一TTL，要么TTL太长导致否定结果过期不及时，要么TTL太短导致成功结果频繁重验证。

## 解决方案

使用两个独立的LRU缓存，分别缓存成功结果和否定结果：

```python
class GitHubRepoProvider(LoggingConfigurable):
    # 成功结果缓存：1024条，默认不过期（使用ETag条件验证）
    cache = Cache(1024)
    # 404结果缓存：1024条，5分钟TTL
    cache_404 = Cache(1024, max_age=300)

    async def get_resolved_ref(self):
        api_url = f"https://api.github.com/repos/{user}/{repo}/commits/{ref}"
        
        # 先查成功缓存
        cached = self.cache.get(api_url)
        if cached:
            etag = cached["etag"]
        else:
            # 查404缓存
            cache_404 = self.cache_404.get(api_url)
            if cache_404:
                return None  # 最近确认404，直接返回None
            etag = None
        
        # 发起API请求，携带ETag
        resp = await self._github_api_request(api_url, etag=etag)
        
        if resp is None:  # 404
            self.cache_404.set(api_url, True)
            return None
        
        if resp.code == 304:  # Not Modified
            return self.cache.get(api_url)["sha"]
        
        # 200 OK：缓存结果和ETag
        sha = json.loads(resp.body)["sha"]
        self.cache.set(api_url, {"etag": resp.headers.get("ETag"), "sha": sha})
        return sha
```

## LRU Cache实现

```python
class Cache(OrderedDict):
    def __init__(self, max_size=1024, max_age=0):
        self.max_size = max_size
        self.max_age = max_age
        self._ages = {}

    def get(self, key, default=None):
        if key in self and not self._check_expired(key):
            self.move_to_end(key)  # LRU：访问后置为最新
        return super().get(key, default)

    def set(self, key, value):
        self[key] = value
        self._ages[key] = time.perf_counter()
        self.move_to_end(key)
        if len(self) > self.max_size:
            self.pop(next(iter(self)))  # 淘汰最旧条目
```

## 关键原则

1. **成功缓存+ETag**：缓存ETag值，后续请求携带`If-None-Match`头。GitHub返回304 Not Modified时直接使用缓存值，不消耗rate limit配额
2. **否定缓存短TTL**：404结果缓存5分钟（300秒），避免对不存在的仓库频繁调用API
3. **OrderedDict实现LRU**：使用`move_to_end`和`popitem(last=False)`实现LRU淘汰
4. **基于时间的过期**：`_ages`字典记录每个key的设置时间，`max_age`控制自动过期
5. **先查成功缓存再查否定缓存**：成功缓存优先，否定缓存作为快速失败路径

## ETag机制详解

GitHub API支持条件请求：
1. 首次请求：不带ETag，服务器返回200 + 数据 + ETag头
2. 后续请求：携带`If-None-Match: <etag>`头
3. 数据未变：服务器返回304 Not Modified（无响应体，不计入rate limit）
4. 数据已变：服务器返回200 + 新数据 + 新ETag

对于commit SHA查询，SHA永远不变（Git内容寻址），因此304几乎总是命中，有效实现"永久缓存+零API消耗"。

## 反模式

- ❌ 统一TTL缓存所有响应（要么数据过期不及时，要么缓存命中率低）
- ❌ 不缓存否定结果（不存在的仓库每次都触发API调用）
- ❌ 成功结果设置短TTL而不使用ETag（不必要地消耗rate limit）
- ❌ 缓存不设上限（内存泄漏风险）
- ❌ 否定缓存TTL过长（仓库创建后用户长时间看到404）

## 适用场景

- GitHub/GitLab/Git API客户端
- 任何有速率限制的REST API调用
- URL元数据获取（如oEmbed、Open Graph解析）
- DNS缓存（成功响应长缓存，NXDOMAIN短缓存是同类思想）
- 引用/别名解析（分支名→commit SHA、短链接→长链接）
