---
type: Concept
title: 速率限制与配额
description: AgnesAI API速率限制（RPM）机制、订阅计划配额、限流错误处理与最佳实践
tags: [速率限制, RPM, 配额, 订阅计划, 429错误, 限流]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T21:40:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T21:40:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: official-readme
    resource: /references/readme.md
    title: Agnes AI 官方README
  - id: model-catalog
    resource: /references/model-catalog.md
    title: Agnes AI 模型目录
---

# 速率限制与配额

AgnesAI API采用基于用户计划的速率限制（Rate Limiting）和配额（Quota）机制，防止滥用并保证服务稳定性。

## 速率限制（RPM）

RPM（Requests Per Minute）表示每分钟允许发起的请求数。AgnesAI区分两种RPM值：

| 字段 | 含义 |
|------|------|
| **Public Request RPM** | 用户端被允许发起的请求数（含被调度排队的请求） |
| **Actual Executable RPM** | 服务端实际可执行的请求数（考虑调度和容量约束后的有效值） |

实际开发中应参考 **Actual Executable RPM** 来设计并发策略。

> 事实溯源：F-014、F-025、F-115~F-117

## 按模型类型的RPM限制

### 文本模型（Chat Completions）

| 用户类型 | Public Request RPM | Actual Executable RPM |
|---------|-------------------|----------------------|
| Free / 默认 | 30 | 20 |
| Enterprise | 60 | 40 |
| Token Plan | 1,000 | 1,000 |

> 事实溯源：F-014、F-083~F-085

### 图像模型（Image Generation）

图像模型RPM按分辨率区分：

| 用户类型 | 分辨率 | Public Request RPM | Actual Executable RPM |
|---------|--------|-------------------|----------------------|
| Free / 默认 | 1K | 30 | 20 |
| Free / 默认 | 2K | 20 | 10 |
| Free / 默认 | 3K | 2 | 1 |
| Free / 默认 | 4K | 1 | 1 |
| Token Plan | 1K | 120 | 100 |
| Token Plan | 2K | 120 | 80 |
| Token Plan | 3K/4K | 2 | 1 |

> 事实溯源：F-026、F-027、F-089~F-102

### 视频模型（Video Generation）

| 用户类型 | Public Request RPM | Actual Executable RPM |
|---------|-------------------|----------------------|
| Free / 默认 | 2 | 1 |
| Enterprise | 2 | 2 |
| Token Plan | 6 | 5 |

> 事实溯源：F-025、F-108~F-110

⚠️ **重要**：视频生成是最受限的API，Free用户每分钟只能成功发起1个请求。

## 订阅计划与配额

除了RPM速率限制，各订阅计划还有周期配额：

| 计划 | 价格 | 文本模型配额 | 图像配额 | 视频配额 |
|------|------|------------|---------|---------|
| Starter | $4/月 | 1,500请求/5小时；15,000请求/周 | 4,000张/天 | 500秒/天 |
| Plus | $10/月 | 7,500请求/5小时；75,000请求/周 | 4,000张/天 | 500秒/天 |
| Pro | $50/月 | 30,000请求/5小时；300,000请求/周 | 4,000张/天 | 500秒/天 |

> 事实溯源：F-028~F-030、F-123~F-127

**注意**：所有计划的视频日配额都是500秒生成时长，高等级计划主要提升文本模型RPM和周期请求配额。

## 429 限流错误处理

当触发速率限制时，API返回 `429 Too Many Requests` 状态码。

### 最佳实践：指数退避重试

```python
import time
import random
from openai import RateLimitError, APIError

def call_with_retry(func, max_retries=5, base_delay=1):
    """
    带指数退避的API调用封装
    """
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError:
            if attempt == max_retries - 1:
                raise  # 最后一次重试失败，抛出异常
            
            # 指数退避 + 随机抖动（防止惊群效应）
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            print(f"触发限流，{delay:.1f}秒后重试（第{attempt+1}次）...")
            time.sleep(delay)
        except (APIError, TimeoutError) as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)
            time.sleep(delay)
    
    raise Exception("超过最大重试次数")

# 使用示例
response = call_with_retry(
    lambda: client.chat.completions.create(
        model="agnes-2.5-flash",
        messages=[{"role": "user", "content": "Hello"}]
    )
)
```

### 限流响应头（Retry-After）

理想情况下，429响应会包含 `Retry-After` 头，告知需要等待多少秒：

```python
except RateLimitError as e:
    retry_after = e.response.headers.get("Retry-After")
    if retry_after:
        time.sleep(int(retry_after))
    else:
        # 没有Retry-After头时使用指数退避
        time.sleep(base_delay * (2 ** attempt))
```

> 事实溯源：F-034

## 高并发最佳实践

1. **客户端限流**：在客户端主动控制请求速率，不要等到429才减速
2. **批量请求**：合理利用批量接口（如果支持），减少请求次数
3. **请求合并**：相似请求合并，避免重复调用
4. **缓存结果**：对相同输入的响应进行本地缓存（注意缓存有效期）
5. **异步队列**：大量任务使用任务队列削峰填谷，控制并发数
6. **监控告警**：监控429错误率，及时调整并发策略

### 简单的令牌桶限流实现

```python
import time
import threading

class TokenBucket:
    def __init__(self, rate, capacity):
        self.rate = rate          # 每秒生成令牌数
        self.capacity = capacity  # 桶容量
        self.tokens = capacity
        self.last_update = time.time()
        self.lock = threading.Lock()
    
    def acquire(self, tokens=1):
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_update = now
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def wait_for_token(self, tokens=1):
        while not self.acquire(tokens):
            time.sleep(0.1)

# Free用户文本模型：20 RPM ≈ 0.33 RPS
limiter = TokenBucket(rate=0.3, capacity=5)
limiter.wait_for_token()  # 获取令牌后再发起请求
```

## 配额耗尽处理

当周期配额（日/周配额）耗尽时：
1. API会返回429或配额不足错误
2. 需要等待配额周期重置（日配额次日重置，周配额下周重置）
3. 或升级到更高等级的订阅计划
4. 在控制台监控配额使用情况，提前规划

## 相关概念

- [API认证与安全](/concepts/02-api-authentication.md)
- [错误处理与重试](/concepts/07-error-handling.md)
- [OpenAI兼容客户端配置](/examples/openai-compatible.md)
