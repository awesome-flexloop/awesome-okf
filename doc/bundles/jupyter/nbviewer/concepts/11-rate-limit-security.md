---
type: Concept
title: 速率限制与安全机制
description: RateLimiter的IP+UA限流算法、缓存后端复用、Content Security Policy、本地文件安全检查和目录遍历防护
tags:
  - jupyter
  - nbviewer
  - security
  - rate-limit
  - csp
  - localfile
generated:
  by: "reference_agent/trae-cn"
  at: "2026-08-22T10:00:00Z"
status: stable
stale_after: 2027-08-22
sources:
  - ../../../../../external/libs/jupyter/nbviewer/nbviewer/ratelimit.py
  - ../../../../../external/libs/jupyter/nbviewer/nbviewer/providers/local/handlers.py
  - ../../../../../external/libs/jupyter/nbviewer/nbviewer/app.py
---

# 速率限制与安全机制

nbviewer实现了多层安全防护：速率限制、Content Security Policy、本地文件安全检查、目录遍历防护和日志审计。

## 速率限制（RateLimiter）

### 算法（固定窗口计数器）

```python
class RateLimiter:
    def __init__(self, limit, interval, cache):
        self.limit = limit      # 默认60
        self.interval = interval  # 默认600秒（10分钟）
```

1. `cache.add(key, 1, interval)`：原子操作，key不存在时设为1
   - 返回True→首次访问，通过
2. `cache.incr(key)`：原子递增
   - count >= limit → HTTP 429

默认配置：每IP+UA每10分钟最多60次新渲染。

### 身份识别

使用`IP + MD5(User-Agent)`作为限流键，MD5避免存储原始UA字符串（隐私保护）。

### 限流时机

限流只在@cached装饰器中**缓存未命中时**执行。缓存命中不计入限流，频繁访问热门内容不受影响。

### 限流响应

HTTP 429 + "Rate limit exceeded for {ip} ({limit} req / {minutes} min). Try again later."

## Content Security Policy

默认CSP为`connect-src 'none'`，禁止渲染页面发起AJAX/fetch请求，防止Notebook中的恶意脚本向外发送数据。可通过`--content-security-policy`自定义。

## 本地文件安全（LocalFileHandler.can_show）

四层安全检查：

1. **目录遍历防护**：`fullpath.startswith(localfile_path)`确保路径在允许目录内
2. **存在性检查**：`os.path.exists(fullpath)`
3. **隐藏文件过滤**：以`.`或`_`开头的路径组件被拒绝（保护.git、__pycache__等）
4. **权限检查**：需要others-read权限（目录需others-execute），除非--localfile-any-user

符号链接默认不跟随（--localfile-follow-symlinks启用realpath解析）。权限不足时返回404而非403（不暴露文件存在信息）。启用本地文件时记录WARNING安全提醒。

## 上游请求安全

- SSL证书验证默认启用，--no-check-certificate禁用
- 支持HTTP代理（--proxy-host/--proxy-port）
- 连接超时10秒（connect_timeout）
- xheaders=True信任反向代理X-Real-IP/X-Forwarded-For

## 日志审计

log_request()定制请求日志：

| 状态码 | 级别 | 额外信息 |
|--------|------|----------|
| 304/静态2xx | DEBUG | 最小化噪音 |
| <400（重定向） | INFO | +Referer |
| <500（客户端错误） | WARNING | +Referer+User-Agent |
| >=500（服务端错误） | ERROR | +全部请求头（502/503除外） |

## 敏感参数过滤

`STRIP_PARAMS = ["client_id", "client_secret", "access_token"]`，在parse_header_links()中自动从URL参数中移除，防止token泄露到日志。

## 相关文档

- [缓存系统](/concepts/07-caching-system.md)
- [部署指南](/concepts/13-deployment.md)
- [GitHub客户端](/concepts/10-github-client.md)
