---
type: Example
title: 同步调用快速入门——从最小示例到完整配置（CVM）
description: 使用 tencentcloud-sdk-python 同步栈调用 CVM DescribeInstances；最小四行版本、HttpProfile/ClientProfile 完整配置、Filter 嵌套参数、自定义 TraceId、异常处理与日志开启
tags: [示例, 快速入门, CVM, 同步, DescribeInstances, 配置]
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
    title: 官方文档与工程元数据信源（README/examples）
---

# 同步调用快速入门（CVM）

## 场景与前置条件

- 已安装：`pip install tencentcloud-sdk-python-common tencentcloud-sdk-python-cvm`（或全产品包）。
- 已有一对 API 密钥（SecretId/SecretKey），建议通过环境变量 `TENCENTCLOUD_SECRET_ID`/`TENCENTCLOUD_SECRET_KEY` 提供。
- 本文代码对应 3.1.185 快照的 CVM v20170312 版本包，API 机制说明见 [01 架构与一次同步调用链](../concepts/01-architecture.md)。

## 最小可运行版本

```python
import os
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.cvm.v20170312 import cvm_client, models

try:
    cred = credential.Credential(
        os.environ["TENCENTCLOUD_SECRET_ID"],
        os.environ["TENCENTCLOUD_SECRET_KEY"])

    client = cvm_client.CvmClient(cred, "ap-shanghai")

    req = models.DescribeInstancesRequest()
    req.Limit = 10

    resp = client.DescribeInstances(req)
    print(resp.TotalCount)                 # 强类型字段直接取
    print(resp.to_json_string(indent=2))   # 整包 JSON（中文不转义）
except TencentCloudSDKException as err:
    print(err)                             # code/message/requestId
```

四步固定套路：**凭证 → 客户端（服务+地域）→ 请求对象 → 动作方法**。Profile 全部省略时走默认值（POST、60 秒超时、TC3 签名、zh-CN、不重试、不熔断）。

## 完整配置版本

对照官方 README/examples/cvm/v20170312/describe_instances.py 的配置项（F-093）：

```python
import sys
import logging
import os
from tencentcloud.common import credential, retry
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.cvm.v20170312 import cvm_client, models

cred = credential.Credential(
    os.environ["TENCENTCLOUD_SECRET_ID"],
    os.environ["TENCENTCLOUD_SECRET_KEY"])

httpProfile = HttpProfile()
httpProfile.protocol = "https"
httpProfile.keepAlive = True
httpProfile.reqMethod = "POST"
httpProfile.reqTimeout = 60
httpProfile.endpoint = "cvm.tencentcloudapi.com"   # 不设则由 service+rootDomain 推导
# httpProfile.proxy = "http://127.0.0.1:8080"      # 或直接用 HTTPS_PROXY 环境变量
# httpProfile.certification = False               # 跳过证书校验（仅排障用）

clientProfile = ClientProfile()
clientProfile.httpProfile = httpProfile
clientProfile.signMethod = "TC3-HMAC-SHA256"       # 默认值，可显式写出
clientProfile.language = "en-US"                   # zh-CN（默认）/ en-US

# 显式开启重试：网络错误/限频时最多再试 3 次，退避 2^n 秒
# retry_logger = logging.getLogger("retry")
# retry_logger.setLevel(logging.DEBUG)
# retry_logger.addHandler(logging.StreamHandler(sys.stderr))
# clientProfile.retryer = retry.StandardRetryer(max_attempts=3, logger=retry_logger)

client = cvm_client.CvmClient(cred, "ap-shanghai", clientProfile)
# client.set_stream_logger(stream=sys.stdout, level=logging.DEBUG)  # 全量调试日志
```

## 嵌套参数：Filter 对象列表

复杂参数不用手写点号键——SDK 的 `_serialize` + `_format_params` 会自动把嵌套对象转成 `Filters.0.Name` 形态（F-026、F-042）：

```python
req = models.DescribeInstancesRequest()
f = models.Filter()
f.Name = "zone"
f.Values = ["ap-shanghai-1", "ap-shanghai-2"]
req.Filters = [f]
req.Offset = 0
req.Limit = 20

# 每请求自定义头（必须是 dict）
req.headers = {"X-TC-TraceId": "ffe0c072-8a5d-4e17-8887-a8a60252abca"}
# 不传 X-TC-TraceId 时 SDK 自动生成 uuid4

resp = client.DescribeInstances(req)
for inst in resp.InstanceSet:
    print(inst.InstanceId, inst.InstanceType, inst.Placement.Zone)
```

## 异常处理：只需 except 一种异常

所有错误（网络层、服务端、客户端参数）在动作方法边界统一为 TencentCloudSDKException（F-047、F-095）：

```python
try:
    resp = client.DescribeInstances(req)
except TencentCloudSDKException as err:
    code = err.get_code()
    if code == "RequestLimitExceeded":
        ...                          # 限频：考虑 StandardRetryer（仅查询/幂等接口）
    elif code in ("ServerNetworkError", "ClientNetworkError"):
        ...                          # 传输层问题：代理/证书/网络
    else:
        print(err.get_request_id())  # 工单排查必带 RequestId
```

错误码字符串可与生成的 errorcodes.py 常量比对：

```python
from tencentcloud.cvm.v20170312 import errorcodes
err.get_code() == errorcodes.UNSUPPORTEDOPERATION
```

## 常见坑位

1. **地域参数是构造客户端时传的**（第二个位置参数），不在 Request 对象上；X-TC-Region 头由此而来。
2. **字段名大小写敏感**：Python 属性是大驼峰（`req.Limit`），对应下划线属性 `_Limit`，序列化后仍是 `Limit`。
3. **重试默认关闭**：限频不会自动恢复，需要显式注入 StandardRetryer，且写接口先确认幂等（见 [06 重试与熔断](../concepts/06-retry-and-breaker.md)）。
4. **代理环境**：容器内报连接超时先查 `HTTPS_PROXY`/`NO_PROXY`，无需改代码。

## 相关概念

- [01 架构与一次同步调用链](../concepts/01-architecture.md)
- [03 Profile 与 HTTP 配置](../concepts/03-profile-http.md)
- [02 凭证与 CommonClient 示例](02-credential-and-common-client.md)
- [03 异步、重试与 SSE 示例](03-async-retry-sse.md)
