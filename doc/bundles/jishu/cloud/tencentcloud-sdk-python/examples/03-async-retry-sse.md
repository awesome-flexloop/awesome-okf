---
type: Example
title: 异步并发、重试配置与 SSE 流式调用
description: httpx 异步栈三件套——async with 生命周期下用 asyncio.gather 并发扇出多地域调用；retry_async.StandardRetryer 的注入与可重试集合；混元 ChatCompletions Stream=True 的 SSE 异步生成器消费
tags: [示例, 异步, asyncio, httpx, 重试, SSE, hunyuan, 流式]
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
    title: 官方文档与工程元数据信源（README/examples/hunyuan）
---

# 异步并发、重试与 SSE 流式

异步机制（httpx 生命周期、RequestChain、异步重试器）见 [07 异步栈](../concepts/07-async-stack.md)。前置：`pip install 'tencentcloud-sdk-python-common[async]' tencentcloud-sdk-python-cvm tencentcloud-sdk-python-hunyuan`，Python 3.7+。

## 一、async with 与并发扇出

```python
import asyncio
import os
from tencentcloud.common import credential
from tencentcloud.cvm.v20170312 import cvm_client_async, models

async def query_region(cred, region):
    # 每个并发任务使用独立客户端（各自持有一个 httpx.AsyncClient）
    async with cvm_client_async.CvmClient(cred, region) as client:
        req = models.DescribeInstancesRequest()
        req.Limit = 5
        resp = await client.DescribeInstances(req)
        return region, resp.TotalCount

async def main():
    cred = credential.Credential(
        os.environ["TENCENTCLOUD_SECRET_ID"],
        os.environ["TENCENTCLOUD_SECRET_KEY"])
    regions = ["ap-shanghai", "ap-guangzhou", "ap-beijing"]
    results = await asyncio.gather(*(query_region(cred, r) for r in regions))
    for region, total in results:
        print(region, total)

asyncio.run(main())
```

要点：

- 客户端必须关闭：用 `async with` 或显式 `await client.close()`，否则 httpx 连接不释放（F-079）。
- 默认 keepAlive=False 对应 httpx `max_keepalive_connections=0`；同一客户端连续复用时可在 HttpProfile 打开 keepAlive。
- 方法签名带完整类型标注，opts 为运行时选项 dict（F-081）。

## 二、异步重试配置

异步栈使用独立的 `retry_async.StandardRetryer`（注入位置与同步相同）：

```python
from tencentcloud.common import retry_async
from tencentcloud.common.profile.client_profile import ClientProfile

cpf = ClientProfile()
# 最多 3 次重试（首次之外），默认退避 2^n 秒；可重试：
# httpx.TransportError 原生异常 + 5 个错误码
# （ClientNetworkError/ServerNetworkError/RequestLimitExceeded 及两个子码）
cpf.retryer = retry_async.StandardRetryer(max_attempts=3)
```

异步重试器与同步版两处差异（F-079、retry_async.py）：

1. `httpx.TransportError` 不经包装也直接判定可重试；
2. backoff_fn 支持协程函数（内部 `await backoff_fn(n)`）。

重试仍只建议用于查询/幂等接口；写接口需要业务幂等保证。

## 三、SSE 流式：混元 ChatCompletions

对应官方示例 examples/hunyuan/v20230901/chat_completions_async.py（F-094）。当请求 `Stream=True` 时，动作方法 await 的结果不是 Response 模型，而是一个**异步生成器**（Content-Type=text/event-stream 由反序列化拦截器自动识别）：

```python
import asyncio
import json
import os
import sys
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.hunyuan.v20230901 import hunyuan_client_async, models

async def main():
    cred = credential.Credential(
        os.environ["TENCENTCLOUD_SECRET_ID"],
        os.environ["TENCENTCLOUD_SECRET_KEY"])

    cpf = ClientProfile()
    cpf.httpProfile.reqTimeout = 400        # 流式接口耗时较长，官方示例设 400 秒

    async with hunyuan_client_async.HunyuanClient(cred, "ap-guangzhou", cpf) as client:
        client.set_stream_logger(sys.stdout)   # 可选：查看逐帧调试日志

        req = models.ChatCompletionsRequest()
        req.Model = "hunyuan-standard"
        req.Stream = True
        msg = models.Message()
        msg.Role = "user"
        msg.Content = "你好，可以讲个笑话吗"
        req.Messages = [msg]

        resp = await client.ChatCompletions(req)   # Stream=True 时 resp 是异步生成器

        full = ""
        async for event in resp:               # 每帧 dict：{'data': '...', 'event'?: ..., 'id'?: ...}
            data = json.loads(event["data"])   # data 才是业务 JSON
            for choice in data["Choices"]:
                full += choice["Delta"]["Content"]
        print(full)

try:
    asyncio.run(main())
except TencentCloudSDKException as err:
    print(err)
```

SSE 帧解析规则（同步/异步一致，F-040、F-083）：空行分隔事件；多 data 行以 `\n` 连接；event/id/retry 为可选元数据；冒号开头为注释心跳。业务侧只消费 `event["data"]` 并自行 json.loads。

## 四、异步 CommonClient

未安装产品包时，异步 CommonClient 提供同样的动态调用能力：入口统一是 `call_and_deserialize(action, params, headers=...)`，当响应为 text/event-stream 时返回值即异步生成器，可直接 `async for`（与产品客户端同一拦截器机制）；非流式时返回 dict。官方示例 examples/common_client/chat_completions_async.py 与 examples/cls/v20201016/uploadlog_common_async.py 覆盖了 SSE 对话与 CLS 日志上传两类场景（F-092、F-094）：

```python
async with CommonClient("hunyuan", "2023-09-01", cred, "ap-guangzhou", profile=cpf) as client:
    resp = await client.call_and_deserialize(
        "ChatCompletions", {"Model": "hunyuan-standard", "Messages": [...], "Stream": True})
    async for event in resp:        # SSE 响应：resp 是异步生成器
        ...
```

## 常见坑位

1. 忘记 await：动作方法是协程，IDE 的类型标注返回模型对象，但必须 `await` 后才能使用。
2. Stream=True 却按模型取属性：await 结果是异步生成器，需 `async for`；Stream=False 时才是 `resp.Choices[0].Message.Content`。
3. 客户端在循环内反复创建：优先「每区域/每任务一个客户端 + 同客户端多次调用」，让连接池发挥作用。
4. Python 3.6 的 httpx 上限为 0.22.0，存在空 query 参数被过滤的兼容处理；新环境直接用 3.7+ 与新版 httpx（F-084）。

## 相关概念

- [07 异步栈](../concepts/07-async-stack.md)——RequestChain 五拦截器与配置映射
- [06 重试与熔断](../concepts/06-retry-and-breaker.md)——重试白名单与熔断的同步对照
- [04 签名与传输](../concepts/04-signature-and-http.md)——SSE 同步侧解析规则
- [01 同步快速入门](01-sync-quickstart.md)
