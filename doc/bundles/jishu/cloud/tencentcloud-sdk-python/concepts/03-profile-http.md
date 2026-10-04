---
type: Concept
title: ClientProfile 与 HttpProfile——协议与传输两层配置
description: HttpProfile 全部参数默认值（POST/60s/https/根域名/代理/证书/预连接池/网关端点）与 ClientProfile（TC3 签名、zh-CN、重试器、熔断开关）；requests Session、代理发现、certifi、keep-alive、预连接池与日志 handler
tags: [tencentcloud-sdk-python, HttpProfile, ClientProfile, requests, 代理, 证书, keep-alive, 日志]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-10-04T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-04T00:00:00Z" }
status: stable
stale_after: 2027-10-04
sources:
  - id: source-1
    resource: /references/source-1.md
    title: 源码快照信源（3.1.185 运行时内核与 CVM 样本）
  - id: source-2
    resource: /references/source-2.md
    title: 官方文档与工程元数据信源
---

# ClientProfile 与 HttpProfile

配置分两层：**HttpProfile 管"怎么传"**（HTTP 方法、超时、协议、代理、域名、证书），**ClientProfile 管"怎么说协议"**（签名算法、语言、重试、熔断）。两者都是可选参数——不传时使用一套偏向安全的默认值。

## HttpProfile 参数表（F-057）

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `endpoint` | `None` | 显式端点主机；优先级最高，设置后忽略 service+rootDomain 推导 |
| `reqMethod` | `"POST"` | 请求方法；运行时只支持 GET 与 POST，其他抛 ClientParamsError |
| `reqTimeout` | `60` | 请求超时秒数；构造时 None 归一为 60 |
| `protocol`（scheme） | `"https"` | http/https |
| `keepAlive` | `False` | 是否复用连接（Session 长连接） |
| `proxy` | `None` | 显式代理；None 时回退环境变量发现 |
| `rootDomain` | `"tencentcloudapi.com"` | 端点推导的根域名：`<service>.<rootDomain>` |
| `certification` | `None` | None=用 certifi 证书；字符串=指定 CA 路径；`False`=跳过校验 |
| `apigw_endpoint` | `None` | API 网关接管端点（改 host 不改签名，见 [04 签名与传输](04-signature-and-http.md)） |
| `pre_conn_pool_size` | `0` | >0 时启用守护线程预建连接池 |

```python
httpProfile = HttpProfile()
httpProfile.protocol = "https"
httpProfile.endpoint = "cvm.tencentcloudapi.com"
httpProfile.reqMethod = "POST"
httpProfile.reqTimeout = 60
```

## ClientProfile 参数表（F-058、F-074）

| 参数 | 默认值 | 约束/说明 |
|------|--------|-----------|
| `signMethod` | `"TC3-HMAC-SHA256"` | 另支持 HmacSHA256/HmacSHA1；其他值调用时报 Invalid signature method |
| `language` | `"zh-CN"` | 仅接受 `zh-CN`/`en-US`，其他值构造即抛异常；进入 X-TC-Language 头 |
| `httpProfile` | 新建 HttpProfile | 传输层配置 |
| `disable_region_breaker` | `True` | **熔断默认关闭**；置 False 才创建 CircuitBreaker |
| `region_breaker_profile` | 新建 RegionBreakerProfile | 备份端点与熔断阈值 |
| `retryer` | `None` | None → 运行时用 NoopRetryer（不重试） |
| `request_client` | `None` | 自定义客户端标识，正则限 `[0-9a-zA-Z-_,;.]+`，截断 128 字符 |

RegionBreakerProfile 的默认熔断参数（F-074）：备份端点 `ap-guangzhou.tencentcloudapi.com`、窗口 300 秒、失败 ≥5 次且失败率 ≥75%（或连续 5 次失败）触发、OPEN 持续 60 秒、半开探测需连续 5 次成功。备份域名必须是 `tencentcloudapi.com` 或 `<region>.tencentcloudapi.com` 形态，否则 check_endpoint 报错。熔断机制详解见 [06 重试与熔断](06-retry-and-breaker.md)。

## requests 传输层行为（F-052 ~ F-056）

`ApiRequest` 内部持有一个 `requests.Session()`（经 ProxyConnection 子类），关键行为：

- **证书**：默认 `certification = certifi.where()`；显式传路径使用自定义 CA；传 `False` 关闭 SSL 校验。README 记载 macOS Python 3.6 证书问题需运行 Install Certificates.command（F-100）。
- **代理发现**：未显式传 proxy 时，依次读 `HTTPS_PROXY`/`HTTP_PROXY` 环境变量，并检查 `NO_PROXY` 是否覆盖目标主机。README 同时支持在 HttpProfile 中显式指定代理（F-093）。
- **连接复用**：keepAlive=False（默认）时每次请求独立连接并在请求头显式关闭；True 时复用 Session 连接池并发送 `Connection: Keep-Alive`。
- **预连接池**：pre_conn_pool_size > 0 时挂载自定义 PreConnAdapter——HTTPSPreConnPool/HTTPPreConnPool 启动 daemon 线程，循环预先 TCP/TLS 建连放入 urllib3 池（F-053），适合启动后立刻有高并发请求的长驻进程。
- **流式响应**：所有请求统一 `stream=True`，为 SSE 与大响应保留读取控制。
- **异常归一**：requests 层抛出的任何异常（DNS、连接拒绝、超时等）在 send_request 边界统一包装为 `TencentCloudSDKException("ClientNetworkError", str(e))`（F-054），该错误码在标准重试白名单内。
- **URL 补全**：`_handle_host` 对无 scheme 的端点按 is_http 补 `http://`/`https://`；GET 请求把参数拼 URL（body=None），POST 把参数放 body。

## 日志（F-024、F-041）

SDK 不配置任何输出 handler（挂的是 emit 为空的 EmptyHandler），默认静默。三种开启方式：

```python
client.set_stream_logger(stream=sys.stdout, level=logging.DEBUG)
client.set_file_logger(file_path="/tmp/tc.log", level=logging.DEBUG)
# 文件日志：RotatingFileHandler，单文件上限 512MB，保留 10 个滚动文件
client.set_default_logger()   # 清空全部 handler，恢复静默
```

默认格式：`%(asctime)s %(process)d %(filename)s L%(lineno)s %(levelname)s %(message)s`，可用 log_format 自定义。重试器也接受独立 logger（README 完整示例中用名为 "retry" 的 logger 打印重试过程，F-093）。

## 自定义请求头（F-093、F-096）

两种粒度：

- **每请求**：`req.headers = {"X-TC-TraceId": "...", "X-TC-Canary": "..."}`，headers 必须是 dict；未提供 TraceId 时 SDK 自动注入 uuid4。
- **客户端标识**：ClientProfile.request_client 影响 `X-TC-RequestClient` 头（默认 `SDK_PYTHON_3.1.185`）。

## 相关概念

- [04 签名与传输](04-signature-and-http.md)——endpoint/rootDomain/apigw_endpoint 如何参与请求构建
- [06 重试与熔断](06-retry-and-breaker.md)——retryer 字段与 RegionBreakerProfile 的完整语义
- [07 异步栈](07-async-stack.md)——同样配置在 httpx 传输层的对应项
