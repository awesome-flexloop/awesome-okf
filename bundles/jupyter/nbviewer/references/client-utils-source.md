---
type: Reference
title: 客户端与工具源码分析
description: nbviewer client.py、ratelimit.py、utils.py、log.py、formats.py模块深度分析，包括HTTP缓存客户端、限流计数器、工具函数、日志定制和输出格式定义
tags:
  - jupyter
  - nbviewer
  - client
  - ratelimit
  - utils
  - log
  - formats
  - source-analysis
generated:
  by: "reference_agent/trae-cn"
  at: "2026-08-22T10:00:00Z"
status: stable
stale_after: 2027-08-22
sources:
  - ../../../../../external/libs/jupyter/nbviewer/nbviewer/client.py
  - ../../../../../external/libs/jupyter/nbviewer/nbviewer/ratelimit.py
  - ../../../../../external/libs/jupyter/nbviewer/nbviewer/utils.py
  - ../../../../../external/libs/jupyter/nbviewer/nbviewer/log.py
  - ../../../../../external/libs/jupyter/nbviewer/nbviewer/formats.py
---

# 客户端与工具源码分析

本文档对 nbviewer 的客户端、限流、工具函数、日志和格式模块进行深度源码分析。

## client.py - HTTP客户端

### NBViewerAsyncHTTPClient 类

封装Tornado AsyncHTTPClient，增加缓存和日志功能。

**构造**：
```python
def __init__(self, log, client=None):
    self.log = log
    self.client = client or CurlAsyncHTTPClient()
```
默认使用CurlAsyncHTTPClient（基于pycurl，性能更好），也可传入自定义client。

**cache_headers映射**：
```python
cache_headers = {"ETag": "If-None-Match", "Last-Modified": "If-Modified-Since"}
```
缓存响应头到请求验证头的映射。

### smart_fetch() 方法 - HTTP缓存逻辑

```python
async def smart_fetch(self, request):
```

核心缓存流程：
1. 生成缓存键：`hashlib.sha256(request.url.encode("utf8")).hexdigest()`
2. 查缓存：如果命中，提取ETag/Last-Modified，添加If-None-Match/If-Modified-Since头
3. 发送请求
4. 304 Not Modified → 使用缓存响应
5. 200 OK → 使用新响应并更新缓存
6. 错误+有缓存 → 使用缓存响应（容错降级）
7. 新响应缓存：pickle序列化后存入缓存

**缓存值**：整个HTTPResponse对象（pickle序列化），永久缓存（不设TTL）。

**与页面缓存的区别**：
| 特性 | 页面缓存 | HTTP客户端缓存 |
|------|----------|----------------|
| 对象 | 最终HTML页面 | 上游HTTP响应 |
| 键 | SHA1(path/uri) | SHA256(full_url) |
| TTL | 动态TTL（10min-2h） | 永久，通过304验证 |
| 目的 | 避免重复渲染 | 避免重复上游请求 |

## ratelimit.py - 速率限制器

### RateLimiter 类

基于缓存后端的固定窗口限流实现。

**构造**：
```python
def __init__(self, limit, interval, cache):
    self.limit = limit  # 最大请求数
    self.interval = interval  # 时间窗口（秒）
    self.cache = cache  # 缓存后端
```

### key_for_handler() - 用户标识

```python
def key_for_handler(self, handler):
    agent = handler.request.headers.get("User-Agent", "")
    return "rate-limit:{}:{}".format(
        handler.request.remote_ip,
        hashlib.md5(agent.encode("utf8", "replace")).hexdigest(),
    )
```
- 使用IP + User-Agent MD5作为限流键
- MD5避免存储原始UA字符串（隐私保护）
- encode("utf8", "replace")确保非UTF8字符不报错

### check() - 限流检查

```python
async def check(self, handler):
```

算法：
1. `cache.add(key, 1, interval)`：原子操作，key不存在时设为1，TTL=interval
   - 返回True → 首次访问，通过
2. `cache.incr(key)`：原子递增
3. count >= limit → 抛HTTPError(429)

默认配置：60次/600秒（10分钟60次）。limit=0时禁用限流。

**关键设计**：限流只在缓存未命中时检查（在@cached装饰器中），缓存命中不计入限流。

## utils.py - 工具函数

### EmptyClass

空对象模式，用于mock statsd客户端：
- 所有方法调用返回自身
- 链式调用不会报错
- 未配置statsd时使用

### quote(s)

Unicode安全的URL编码：
- 接受str类型
- 始终返回str
- Python2/3兼容

### clean_filename(fn)

GitHub Gist文件名清理：
- 非字母数字字符替换为`-`
- 复现GitHub的permalink生成逻辑

### url_path_join(*pieces)

安全的URL路径拼接：
- 防止双斜杠
- 保留开头/结尾的斜杠
- 处理空段
- `//`退化为`/`

### transform_ipynb_uri(uri, uri_rewrite_list)

URI重写核心函数：
- 按顺序遍历(regex, template)规则
- 首次匹配生效，format(*groups)替换
- 查询参数编码为最后路径段
- CreateHandler表单提交时调用

### get_encoding_from_headers(headers)

从HTTP响应头提取编码：
- 解析Content-Type的charset参数
- text/*默认utf-8（覆盖ISO-8859-1默认值）
- application/json默认utf-8（RFC 4627）

### response_text(response, encoding=None)

模拟requests.text属性，解码Tornado HTTPResponse body。

### parse_header_links(value)

解析HTTP Link头（用于GitHub API分页）：
- 返回dict，key为rel值
- 自动剥离client_id/client_secret/access_token等敏感参数

### git_info(path) / jupyter_info()

获取Git版本信息和nbconvert版本，注入模板页脚。

### base64_decode/encode(s)

Unicode安全的base64编解码（base64 API只处理bytes）。

### time_block(message, logger, debug_limit=1)

计时上下文管理器：
- 记录代码块执行时间（毫秒）
- 超过debug_limit（默认1秒）使用INFO级别，否则DEBUG

### STRIP_PARAMS

```python
STRIP_PARAMS = ["client_id", "client_secret", "access_token"]
```
parse_header_links中过滤的敏感参数列表。

## log.py - 定制日志

### log_request(handler)

自定义Tornado请求日志函数：

**日志级别策略**：
| 状态码 | 级别 | 额外信息 |
|--------|------|----------|
| 304 或 静态文件2xx | DEBUG | 最小化噪音 |
| < 400（重定向） | INFO | +Referer |
| < 500（客户端错误） | WARNING | +Referer +User-Agent |
| >= 500（服务端错误） | ERROR | +全部请求头（502/503除外） |

**默认消息格式**：`{status} {method} {uri} ({ip}) {request_time:.2f}ms`

## formats.py - 输出格式定义

### default_formats()

返回默认格式字典：

```python
{
    "html": {
        "nbconvert_template": "lab",
        "label": "Notebook",
        "icon": "book"
    },
    "slides": {
        "label": "Slides",
        "icon": "gift",
        "test": test_slides
    },
    "script": {
        "label": "Code",
        "icon": "code",
        "content_type": "text/plain; charset=UTF-8"
    }
}
```

### 格式字典字段

| 字段 | 说明 |
|------|------|
| exporter | nbconvert Exporter类/实例（configure_formats填充） |
| nbconvert_template | nbconvert模板名 |
| label | 显示名称 |
| icon | CSS图标类 |
| content_type | 响应Content-Type（默认text/html） |
| test | 条件可用性函数(nb, json)→bool |
| postprocess | 渲染后处理函数 |

### test_slides(nb, json)

检查Notebook是否包含幻灯片标记：
- 遍历所有cell
- 检查metadata.slideshow.slide_type是否为非"-"值
- 存在则slides格式可用
