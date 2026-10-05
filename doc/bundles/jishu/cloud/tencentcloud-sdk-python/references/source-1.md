---
type: Reference
title: 信源：tencentcloud-sdk-python 3.1.185 源码快照（运行时内核与 CVM 样本）
description: 腾讯云 Python SDK tag 3.1.185 源码快照登记——版本指纹、common 运行时 20 文件路径职责表、CVM 生成层样本规模与逐文件事实编号映射
tags: [tencentcloud-sdk-python, source-code, 源码快照, 信源登记, 运行时内核]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-10-04T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-04T00:00:00Z" }
status: stable
stale_after: 2027-10-04
sources:
  - id: facts
    resource: /facts.md
    title: tencentcloud-sdk-python 事实清单（F-001 ~ F-100）
  - id: self
    resource: /references/source-1.md
    title: 源码快照信源（运行时内核与 CVM 样本）
---

# 信源：tencentcloud-sdk-python 3.1.185 源码快照（运行时内核与 CVM 样本）

本文档登记本知识包的一手信源——腾讯云官方 Python SDK（云 API 3.0）源码快照。全部概念文档中的类名、方法名、默认值、行号与计数均以此快照为准，事实编号对应 [facts.md](../facts.md)。

## 版本指纹

| 项目 | 内容 |
|------|------|
| 仓库 | TencentCloud/tencentcloud-sdk-python（GitHub） |
| tag | `3.1.185` |
| commit | `be50b26d4d997c5d8d9c07fc84c03ee5e05ece68` |
| 提交信息 | release 3.1.185 |
| 提交时间 | 2026-10-02 03:57:10 +0800 |
| 工作树状态 | clean（无本地修改） |
| SDK 版本声明 | `tencentcloud/__init__.py` 中 `__version__ = '3.1.185'`（F-001） |
| License | Apache License 2.0（F-003） |
| 支持 Python | 2.7、3.6 ~ 3.12（F-003、F-004） |
| 核心依赖 | requests>=2.16.0；异步 extra：httpx>=0.22.0（F-002） |

## 公共运行时文件索引（tencentcloud/common/，20 个文件）

公共运行时是全 SDK 唯一的手写逻辑层，300 个产品版本包共享（F-014、F-020）。

| 文件 | 职责 | 事实依据 |
|------|------|----------|
| `abstract_client.py` | 同步客户端基类：请求构建、签名分流、端点解析、发送、错误检查、SSE 解析、日志、熔断挂载点 | F-022 ~ F-041、F-051、F-075、F-076、F-096~F-098 |
| `abstract_client_async.py` | 异步客户端基类：httpx.AsyncClient 生命周期、RequestChain 拦截器链、异步 TC3 构建与 SSE | F-079 ~ F-084 |
| `abstract_model.py` | 模型基类：`_serialize`/`_deserialize`/`to_json_string` 与下划线属性名变换 | F-042、F-043 |
| `credential.py` | 6 类凭证 + 默认提供链：Credential、CVMRoleCredential、STSAssumeRoleCredential、EnvironmentVariableCredential、ProfileCredential、OIDCRoleArnCredential、DefaultCredentialProvider | F-059 ~ F-066、F-098 |
| `sign.py` | 旧版 HmacSHA1/HmacSHA256 与 TC3-HMAC-SHA256 三级派生密钥签名 | F-049、F-050 |
| `retry.py` | NoopRetryer、StandardRetryer（可重试错误码集合、指数退避） | F-067 ~ F-069 |
| `retry_async.py` | 异步重试器（配合 RequestChain 使用） | F-079、F-080 |
| `circuit_breaker.py` | 地域熔断器三态状态机（CLOSED/HALF_OPEN/OPEN）与滑动窗口计数 | F-071 ~ F-073 |
| `common_client.py` | CommonClient：不依赖产品包泛调任意云 API | F-077、F-078 |
| `common_client_async.py` | CommonClient 的异步版本 | F-081（异步栈同构） |
| `profile/http_profile.py` | HTTP 传输配置（方法/超时/协议/代理/根域名/证书/预连接池/网关端点） | F-057 |
| `profile/client_profile.py` | 客户端配置（签名算法/语言/重试器/地域熔断开关/RegionBreakerProfile） | F-058、F-074 |
| `http/request.py` | requests 封装：Session、代理发现、证书、keep-alive、预连接适配器、异常包装、RequestInternal、ResponsePrettyFormatter | F-052 ~ F-056 |
| `http/pre_conn.py` | 守护线程预建 TCP 连接的 urllib3 自定义连接池与 HTTPAdapter | F-053 |
| `exception/tencent_cloud_sdk_exception.py` | 统一异常类（code/message/requestId） | F-095 |

## 生成层样本：CVM v20170312 四件套

`tencentcloud/cvm/v20170312/` 是全部 300 个版本包的结构样本（F-019、F-044 ~ F-048）：

| 文件 | 规模（脚本计数） | 内容 |
|------|------------------|------|
| `cvm_client.py` | 2713 行 / 106 个动作方法 | 同步 `CvmClient`，类属性 `_apiVersion='2017-03-12'`、`_service='cvm'`、`_endpoint='cvm.tencentcloudapi.com'`；每个 Action 一个同构方法 |
| `cvm_client_async.py` | — | 异步 `CvmClient`，动作方法为 `async def` 并带完整类型标注 |
| `models.py` | 23652 行 / 286 个 class | 全部 Request/Response 与嵌套结构体，字段为 `_Name` + property，含 `_deserialize` |
| `errorcodes.py` | 417 个错误码常量 | `NAME = 'Dotted.Code'` + 中文注释 |
| `__init__.py` | — | 版本包标识 |

产品目录 `tencentcloud/cvm/__init__.py` 为空文件（F-021）。

## 采集方法与计数口径

- 全文事实均由逐文件精读取得，类名/方法名/常量名逐字照录，未做推断式重命名。
- 计数类事实（263 目录、300 版本包、261 产品、1783/52 个 .py、106 方法、286 class、417 错误码等）由 Python 脚本（os/glob/re/Counter）独立复核，口径记录见 [facts.md](../facts.md) B 面（F-012 ~ F-021）。
- 行号引用以 3.1.185 快照为准；后续版本行号可能漂移，应以类名/方法名检索为准。

## 覆盖事实编号

F-001 ~ F-004、F-012 ~ F-100（运行时与生成层事实）。
