---
type: Concept
title: 缓存系统
description: nbviewer三级缓存后端、分块压缩存储、页面缓存机制、HTTP客户端缓存和限流计数器
tags:
  - jupyter
  - nbviewer
  - cache
  - memcached
  - performance
generated:
  by: "reference_agent/trae-cn"
  at: "2026-08-22T10:00:00Z"
status: stable
stale_after: 2027-08-22
sources:
  - ../../../../../external/libs/jupyter/nbviewer/nbviewer/cache.py
  - ../../../../../external/libs/jupyter/nbviewer/nbviewer/providers/base.py
---

# 缓存系统

nbviewer实现了多级缓存体系：页面缓存（Memcached/内存）、HTTP客户端缓存（ETag/Last-Modified）和并发去重。

## 三级缓存后端

### MockCache（空操作）
`--no-cache`模式使用，所有方法不做任何操作，限流被禁用。

### DummyAsyncCache（内存LRU）
基于字典的FIFO-LRU缓存，默认容量仅10条，适合开发测试。多进程部署时各进程独立缓存。

### AsyncMultipartMemcache（Memcached+分块压缩，生产推荐）
继承AsyncMemcache（pylibmc异步封装，ThreadPoolExecutor后台线程），实现zlib压缩+分块存储以突破Memcached单条1MB限制：
- 压缩后按950KB分块，key格式`{key}.0`, `{key}.1`, ...
- set_multi批量写入，最多16块（约15MB压缩数据）
- get_multi批量读取，遇到不存在的key停止拼接
- 支持SASL认证（MemCachier）

### 后端选择
no_cache→MockCache → pylibmc+memcache URL→AsyncMultipartMemcache → 否则DummyAsyncCache。通过`MEMCACHIER_SERVERS`/`MEMCACHE_SERVERS`/`NBCACHE_PORT`环境变量配置。

## 页面缓存

### 缓存键
- BaseHandler：SHA1(request.uri)
- RenderingHandler：SHA1(request.path)（Notebook渲染与查询参数无关）
- LocalFileHandler：SHA1(request.uri)（区分?download）

### 缓存值
pickle序列化的`{"headers": {"Content-Type": "..."}, "body": "<html>..."}`。

### 动态TTL
`expiry = max(min(120 * request_time, cache_expiry_max), cache_expiry_min)`，默认10分钟-2小时，渲染越慢缓存越久。

### 并发去重（pending Future）
- 第一个请求创建Future并执行渲染
- 后续相同key的请求await同一Future
- 渲染完成后唤醒所有等待者，从缓存获取结果

### cache_and_finish()
先write+finish返回响应，再异步set缓存（不阻塞用户）。缓存命中时设置Cache-Control头。

## HTTP客户端缓存（NBViewerAsyncHTTPClient）

基于ETag/Last-Modified的304验证缓存：
- 缓存键：SHA256(full_url)
- 缓存命中时添加If-None-Match/If-Modified-Since头
- 304→使用缓存响应；200→更新缓存
- 错误+有缓存→使用缓存响应（容错降级）
- 缓存值为整个HTTPResponse（pickle序列化），永久缓存

## 限流计数器缓存

RateLimiter复用缓存后端：
- 键：`rate-limit:{ip}:{md5(ua)}`
- add(key, 1, interval)原子初始化
- incr(key)原子递增，超限抛429
- 固定窗口限流（默认60次/600秒）
- 仅缓存未命中时计数

## 相关文档

- [渲染与缓存源码分析](../references/render-cache-source.md)
- [Notebook渲染管线](06-render-pipeline.md)
- [速率限制与安全机制](11-rate-limit-security.md)
