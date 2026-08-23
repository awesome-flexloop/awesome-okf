---
type: Concept
title: 错误处理与调试
description: AgnesAI API常见HTTP状态码、错误类型、排查流程与重试策略
tags: [错误处理, HTTP状态码, 调试, 重试, 故障排查]
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

# 错误处理与调试

本文档介绍AgnesAI API常见的HTTP状态码、错误类型、排查流程和重试策略，帮助你快速定位和解决API调用问题。

## HTTP状态码速查表

| 状态码 | 含义 | 错误类别 | 处理方式 |
|--------|------|---------|---------|
| **200** | 请求成功 | - | 正常处理响应 |
| **400** | 无效请求 | 客户端错误 | 检查参数，不要重试相同请求 |
| **401** | 认证失败 | 客户端错误 | 检查API密钥，修复后重试 |
| **404** | 资源不存在 | 客户端错误 | 检查端点URL、模型名、资源ID |
| **429** | 速率限制 | 限流错误 | 退避重试，降低请求速率 |
| **500** | 服务器内部错误 | 服务端错误 | 指数退避重试 |
| **502** | 上游网关错误 | 服务端错误 | 指数退避重试 |
| **503** | 服务不可用 | 服务端错误 | 稍后重试，降低并发 |
| **520** | 未知上游错误 | 服务端错误 | 退避重试，记录请求详情 |

> 事实溯源：F-031~F-038

## 客户端错误（4xx）排查

### 400 Bad Request

**原因**：请求格式错误、参数缺失或无效。

**排查清单**：
1. ✅ JSON格式是否正确（逗号、引号、括号是否匹配）
2. ✅ 必填字段是否都提供了（model、messages等）
3. ✅ 参数类型是否正确（如temperature应该是数字而非字符串）
4. ✅ 图像URL是否可公开访问（私有URL服务端无法下载）
5. ✅ 模型是否支持请求的参数（如视频参数用于文本模型）
6. ✅ messages格式是否正确（role字段是否合法、content不为空）

**常见错误示例**：
```json
// ❌ 错误：temperature是字符串
{"temperature": "0.7"}
// ✅ 正确：temperature是数字
{"temperature": 0.7}
```

> 事实溯源：F-031

### 401 Unauthorized

**原因**：API密钥无效、缺失或格式错误。

**排查清单**：
1. ✅ API密钥是否正确复制（没有多复制空格或换行）
2. ✅ Authorization头格式是否为 `Bearer <key>`（注意Bearer后有空格）
3. ✅ 环境变量是否正确加载（打印出来确认）
4. ✅ 账户状态是否正常（是否欠费、被禁用）
5. ✅ 密钥是否有对应模型的访问权限

```python
# 调试：打印密钥前几位确认是否加载正确
api_key = os.getenv("AGNES_API_KEY")
print(f"API Key前缀: {api_key[:8]}..." if api_key else "API Key未加载！")
```

> 事实溯源：F-032

### 404 Not Found

**原因**：请求的URL端点错误或资源不存在。

**排查清单**：
1. ✅ Base URL是否正确：`https://apihub.agnes-ai.com/v1`
2. ✅ 端点路径是否正确（如 `/chat/completions` 而非 `/chat`）
3. ✅ 模型名是否拼写正确（如 `agnes-2.5-flash` 而非 `agnes2.5`）
4. ✅ video_id/image_id等资源ID是否存在且未过期

> 事实溯源：F-033

### 429 Too Many Requests

**原因**：触发速率限制或配额耗尽。

**处理方式**：
1. 使用指数退避算法重试（参考[速率限制文档](/concepts/06-rate-limits.md)）
2. 检查Retry-After响应头
3. 降低并发请求数
4. 检查账户配额是否已耗尽
5. 考虑升级到更高等级计划

> 事实溯源：F-034

## 服务端错误（5xx）处理

5xx错误是服务端问题，客户端可以重试，但需要注意策略：

| 状态码 | 建议重试策略 |
|--------|------------|
| 500 | 指数退避重试，最多3-5次，简化payload测试 |
| 502 | 指数退避重试，检查服务状态页 |
| 503 | 等待较长时间后重试（如30秒），降低并发，避免立即轮询 |
| 520 | 退避重试，捕获完整请求元数据用于排查 |

> 事实溯源：F-035~F-038

### 通用重试装饰器

```python
import time
import random
import functools
from openai import APIError, RateLimitError, APIConnectionError, Timeout

def retry_on_error(max_retries=3, base_delay=1):
    """API调用错误重试装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except RateLimitError as e:
                    last_exception = e
                    if attempt == max_retries:
                        break
                    retry_after = None
                    if hasattr(e, 'response') and e.response:
                        retry_after = e.response.headers.get('Retry-After')
                    delay = int(retry_after) if retry_after else base_delay * (2 ** attempt) + random.uniform(0, 1)
                    print(f"[429] 限流，{delay:.1f}秒后重试 (尝试{attempt+1}/{max_retries})")
                    time.sleep(delay)
                except (APIError, APIConnectionError, Timeout) as e:
                    last_exception = e
                    if attempt == max_retries:
                        break
                    # 5xx错误使用更长退避
                    delay = base_delay * (2 ** attempt) * 2 + random.uniform(0, 1)
                    print(f"[{type(e).__name__}] 错误，{delay:.1f}秒后重试 (尝试{attempt+1}/{max_retries})")
                    time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator

# 使用示例
@retry_on_error(max_retries=3, base_delay=2)
def chat(message):
    return client.chat.completions.create(
        model="agnes-2.5-flash",
        messages=[{"role": "user", "content": message}]
    )
```

## 调试技巧

### 1. 开启请求日志

```python
import logging
import httpx

# 开启HTTP请求日志
logging.basicConfig(level=logging.DEBUG)
httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.DEBUG)
```

### 2. 最小请求复现

遇到问题时，先用最小请求测试是否可以复现：

```python
# 最小可复现请求
response = client.chat.completions.create(
    model="agnes-2.5-flash",
    messages=[{"role": "user", "content": "Hi"}],
    max_tokens=10,
)
print(response)
```

如果最小请求成功，说明问题出在复杂参数上，逐步添加参数定位问题。

### 3. 检查响应详情

```python
try:
    response = client.chat.completions.create(...)
except APIError as e:
    print(f"状态码: {e.status_code}")
    print(f"错误信息: {e.message}")
    print(f"请求ID: {e.request_id if hasattr(e, 'request_id') else 'N/A'}")
    print(f"响应体: {e.response.text if e.response else 'N/A'}")
```

### 4. 网络连通性测试

```bash
# 测试是否能访问API端点
curl -I https://apihub.agnes-ai.com/v1/models

# 测试DNS解析
nslookup apihub.agnes-ai.com
```

## 常见问题快速诊断表

| 现象 | 可能原因 | 快速诊断 |
|------|---------|---------|
| 所有请求都401 | API密钥错误或未加载 | 打印环境变量确认 |
| 第一个请求就429 | 密钥被多人共用、并发过高 | 检查是否有其他程序使用同一密钥 |
| 图像生成总是500 | 图像URL不可访问、提示词违规 | 换一个公开可访问的图片URL测试 |
| 视频一直queued | 服务繁忙 | 降低分辨率，或错峰使用 |
| 流式输出中断 | 网络不稳定、超时设置过短 | 增加timeout参数，实现断点续传 |
| 响应内容被截断 | max_tokens设置过小 | 调大max_tokens参数 |
| Python SDK导入错误 | SDK版本过低 | 升级openai: `pip install -U openai` |

## 相关概念

- [API认证与安全](/concepts/02-api-authentication.md)
- [速率限制与配额](/concepts/06-rate-limits.md)
- [对话补全API](/concepts/03-chat-completions.md)
