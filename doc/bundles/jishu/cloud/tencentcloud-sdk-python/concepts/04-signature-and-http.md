---
type: Concept
title: 签名与 HTTP 传输——TC3 三级派生密钥、端点解析与特殊载荷
description: 三条签名路径（免签/TC3-HMAC-SHA256/旧版 Hmac）的分流条件；TC3 规范请求六段与 date-service-tc3_request 三级密钥派生；X-TC 请求头集；GET/POST、multipart、octet-stream、UNSIGNED-PAYLOAD 与 SSE 流式协议解析
tags: [tencentcloud-sdk-python, TC3-HMAC-SHA256, 签名, endpoint, multipart, SSE, X-TC]
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

# 签名与 HTTP 传输

## 三条签名路径的分流（F-025）

`_build_req_inter` 在每次请求构建时按以下顺序选择签名方式：

| 条件 | 路径 | Authorization |
|------|------|---------------|
| `options['SkipSign']` 为真 | 免签（仅内部凭证刷新等场景） | `SKIP` |
| signMethod == TC3-HMAC-SHA256（默认），或 `options['IsMultipart']` | TC3 | `TC3-HMAC-SHA256 Credential=..., SignedHeaders=..., Signature=...` |
| signMethod == HmacSHA1 / HmacSHA256 | 旧版签名 | base64 HMAC，公共参数混在 body 中 |
| 其他 signMethod | 直接抛 TencentCloudSDKException("ClientError", "Invalid signature method.") | — |

注意 multipart 上传**强制走 TC3**，即使 ClientProfile 配的是旧签名；而 octet-stream 进一步强制 TC3 + POST（F-038）。

## TC3-HMAC-SHA256 详解（F-028 ~ F-031、F-049、F-050）

### 请求头集

TC3 请求不再把公共参数放进 body，而是全部进 HTTP 头：

| 头 | 来源 |
|----|------|
| `Host` | 端点主机 |
| `X-TC-Action` | 动作方法名 |
| `X-TC-Version` | 版本包日期（如 2017-03-12） |
| `X-TC-Timestamp` | 当前 Unix 时间戳（**参与签名**） |
| `X-TC-Region` | 客户端构造时传入的 region |
| `X-TC-Token` | 仅临时凭证存在时发送 |
| `X-TC-Language` | zh-CN / en-US |
| `X-TC-RequestClient` | SDK_PYTHON_3.1.185（可被 request_client 改写） |
| `X-TC-Content-SHA256` | 仅 UNSIGNED-PAYLOAD 时发送 |

### 三级派生密钥（Sign.sign_tc3）

签名密钥不是 secretKey 本身，而是逐级 HMAC-SHA256 派生：

```
SecretDate    = HMAC("TC3" + SecretKey, Date)           # Date = UTC 日期 yyyy-mm-dd
SecretService = HMAC(SecretDate,    Service)            # Service 如 "cvm"
SecretSigning = HMAC(SecretService, "tc3_request")
Signature     = hex(HMAC(SecretSigning, StringToSign))
```

日期来自 X-TC-Timestamp 的 UTC 当日，**本机时钟偏差会直接导致签名失败**——这是 TC3 排障第一检查项。

### 规范请求与二次哈希

CanonicalRequest 六段以换行连接（F-031）：

```
HTTPRequestMethod            # POST / GET
CanonicalURI                 # /
CanonicalQueryString         # GET 时为参数串，POST 为空
CanonicalHeaders             # content-type:...\nhost:...\n（小写键、trim 值）
SignedHeaders                # content-type;host
HashedRequestPayload         # sha256(body) 的 hex；UNSIGNED-PAYLOAD 时为字面量
```

StringToSign：

```
TC3-HMAC-SHA256
<X-TC-Timestamp>
<Date>/<Service>/tc3_request
sha256(CanonicalRequest)的 hex
```

最终 Authorization 头：

```
TC3-HMAC-SHA256 Credential=<SecretId>/<Date>/<Service>/tc3_request,
SignedHeaders=content-type;host, Signature=<hex>
```

关键点：签名对"方法 + URI + query + 两个头 + 载荷摘要"负责，**只签 content-type 与 host 两个头**——X-TC-Token、X-TC-Region 等头不在签名覆盖范围内。

## 旧版签名（HmacSHA1/HmacSHA256）（F-027、F-049、F-051）

旧路径把公共参数（Action、Nonce=随机整数、Timestamp、Version、Region、Token、SecretId、SignatureMethod、Language）与业务参数一起 urlencode 进 body，Content-Type 固定 application/x-www-form-urlencoded。

签名串构造：参数键中的 `_` 替换为 `.`，按键排序拼为 `key1=value1&key2=value2`，前缀为 `<Method><endpoint>/?<params>`；再以 secretKey 做 HmacSHA1 或 HmacSHA256，base64 输出。这是与遗留 QcloudApi 同一时代的算法，仅为兼容保留。

## 端点解析的三层优先级（F-033、F-097）

实际连接主机按以下优先级确定：

1. `httpProfile.endpoint`（显式指定，原值直接用）；
2. `options["Endpoint"]`——经 urlparse 取 hostname（允许传入带 scheme/路径的完整 URL）；
3. `<service>.<rootDomain>`——默认即 `cvm.tencentcloudapi.com`。

此外两个改写机制只动**网络目标**，不动签名（见洞察四）：

- **API 网关**：httpProfile.apigw_endpoint 非空时，host 与 Host 头改写为网关地址，签名仍按原端点/服务计算（F-097）。典型用法是经 apigw 代理统一鉴权/审计。
- **熔断备份端点**：熔断器打开时改写为 `<service>.<backup_endpoint>`（默认 `cvm.ap-guangzhou.tencentcloudapi.com`），见 [06 重试与熔断](06-retry-and-breaker.md)。

## 请求方法与载荷形态（F-029、F-032、F-038）

| 形态 | 方法 | Content-Type | body | 签名要求 |
|------|------|--------------|------|----------|
| 标准 JSON（默认 POST） | POST | application/json | `json.dumps(params)` | TC3 |
| 标准 GET | GET | — | 参数 urlencode 拼到 URL | TC3 |
| 表单（旧签名） | POST | application/x-www-form-urlencoded | urlencode 公共+业务参数 | HmacSHA1/256 |
| multipart 上传 | POST | multipart/form-data; boundary=uuid hex | 手工拼装字节流 | **强制 TC3**；GET 组合直接报错 |
| 二进制流（call_octet_stream） | POST（强制） | application/octet-stream | 原始 bytes | 强制 TC3 |

multipart body 由 `_get_multipart_body` 手工拼装：每个参数一段，`options['BinaryParams']` 声明的键加 `filename=` 头；list/dict 值先 json.dumps 并标 application/json；收尾 boundary 带 `--`（F-032）。

对大载荷还存在 `X-TC-Content-SHA256: UNSIGNED-PAYLOAD` 选项（F-028）：此时规范请求的载荷摘要不计算真实哈希，服务端按流式处理。

## 响应处理与错误模型（F-034、F-035、F-095）

- HTTP 状态码非 200 → `TencentCloudSDKException("ServerNetworkError", content)`。
- Content-Type 为 text/plain 或 application/json 才解析错误体；JSON 中 `Response.Error` 存在时，取其中 Code/Message 连同 `Response.RequestId` 抛统一异常；异常字符串形如 `[TencentCloudSDKException] code:X message:Y requestId:Z`（F-095）。
- `Response.DeprecatedWarning` 存在时发 Python DeprecationWarning（接口弃用提示），不中断调用。

## SSE 流式响应（F-038、F-040）

AI 类接口（如混元 ChatCompletions）返回 `Content-Type: text/event-stream`。`call_sse` 返回生成器，`_process_response_sse` 按 SSE 规范逐行解析：

- 空行：产出一帧 dict 并重置缓冲；
- `data:`：数据行，连续多行以 `\n` 连接；
- `event:` / `id:` / `retry:`：事件类型、事件 id、重连等待毫秒（retry 转 int）；
- 冒号开头：注释行（心跳），丢弃；其他未知键忽略。

异步侧用 httpx 的 aiter_lines 实现等价的异步生成器（见 [07 异步栈](07-async-stack.md)）。每帧仍是含 RequestId 的 JSON 业务负载，调用方自行 json.loads。

## 排障速查

| 现象 | 检查顺序 |
|------|----------|
| SignatureFailure / 签名过期 | 本机时间（X-TC-Timestamp/UTC 日期）→ secretId 是否对应环境 → service 名 |
| 签名错误但走了网关 | 确认 apigw 改写不影响签名；核对 content-type 是否被中间件改动 |
| ClientNetworkError | 代理（HTTPS_PROXY/NO_PROXY）、证书、安全组；该错误码在重试白名单内 |
| 上传接口签名失败 | multipart/octet-stream 强制 TC3，检查 signMethod 与 BinaryParams 声明 |
| 接口返回 DeprecatedWarning | 该 Action 已弃用，查官网迁移到新版本包 |

## 相关概念

- [01 架构与一次同步调用链](01-architecture.md)——签名在调用链中的位置
- [03 Profile 与 HTTP 配置](03-profile-http.md)——signMethod、rootDomain、endpoint 与证书配置
- [05 凭证链](05-credential-chain.md)——临时凭证的 X-TC-Token 与免签刷新
- [08 分包与遗留层](08-packaging-and-legacy.md)——旧签名与 QcloudApi v2 的对应关系
