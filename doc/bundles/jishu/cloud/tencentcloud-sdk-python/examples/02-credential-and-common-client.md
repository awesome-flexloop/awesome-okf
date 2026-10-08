---
type: Example
title: 凭证提供链、STS 角色扮演与 CommonClient 泛调
description: EnvironmentVariableCredential 与 DefaultCredentialProvider 的零配置用法；STSAssumeRoleCredential 跨账号临时凭证自动刷新；只装 common 包用 CommonClient.call_json 泛调任意产品
tags: [示例, 凭证, DefaultCredentialProvider, STS, AssumeRole, CommonClient, 零配置]
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

# 凭证提供链、STS 与 CommonClient

凭证机制详解见 [05 凭证体系](../concepts/05-credential-chain.md)；本文给出三种生产常用装配方式与 CommonClient 泛调。

## 方式一：环境变量（本机/CI 推荐）

```python
from tencentcloud.common import credential
from tencentcloud.cvm.v20170312 import cvm_client, models

cred = credential.EnvironmentVariableCredential().get_credential()
client = cvm_client.CvmClient(cred, "ap-shanghai")
```

读取 `TENCENTCLOUD_SECRET_ID` / `TENCENTCLOUD_SECRET_KEY`；缺失返回 None（继续提供链回退），直接使用 None 构造 Credential 会触发非空校验（F-059、F-062）。

## 方式二：默认提供链（一套代码跑遍本机/CVM/TKE）

```python
from tencentcloud.common import credential
from tencentcloud.cvm.v20170312 import cvm_client, models
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException

try:
    # 顺序：环境变量 → ~/.tencentcloud/credentials → CVM 实例角色 → TKE OIDC
    cred = credential.DefaultCredentialProvider().get_credential()
except TencentCloudSDKException as e:
    # 四级全失败：code=ClientSideError，message="no valid credentail."（源码原文）
    raise

client = cvm_client.CvmClient(cred, "ap-shanghai")
```

对应官方示例 examples/cvm/v20170312/credential_providers.py。配置文件形态（ini）：

```ini
# ~/.tencentcloud/credentials（Windows: C:\Users\<NAME>\.tencentcloud\credentials）
[default]
secret_id = AKID...
secret_key = xxxx
```

部署在已绑定 CAM 角色的 CVM 或配置了 OIDC 的 TKE Pod 中时无需任何密钥文件——角色类凭证到期前自动刷新（CVM 提前 300 秒），长进程不会因临时密钥过期中断（F-060、F-065）。

## 方式三：STS 角色扮演（跨账号/临时授权）

对应官方示例 examples/cvm/v20170312/describe_instances_sts.py（F-061）：

```python
from tencentcloud.common import credential
from tencentcloud.cvm.v20170312 import cvm_client, models

# 用主账号（或子账号）长期密钥扮演目标角色
cred = credential.STSAssumeRoleCredential(
    "AKID...",                 # 主体 SecretId
    "xxxx",                    # 主体 SecretKey
    "qcs::cam::uin/100000000:roleName/JumpRole",  # 目标角色 RoleArn
    "ops-audit-session")       # RoleSessionName（会话标识）

client = cvm_client.CvmClient(cred, "ap-guangzhou")
resp = client.DescribeInstances(models.DescribeInstancesRequest())
```

内部行为：SDK 固定以 ap-guangzhou/sts/2018-08-13 调 AssumeRole 换取 TmpSecretId/TmpSecretKey/Token，默认有效期 7200 秒，在 `ExpiredTime - 7200×0.9` 时刻自动重新扮演（F-061）。请求自动带 X-TC-Token 头，调用方无感知。

## CommonClient：只装 common 包泛调任意产品

适用：不想为每个产品装分包、调用面在运行时才确定（如多租户平台、API 网关控制台）。对应官方示例 examples/common_client/describe_instances.py（F-077、F-078）：

```python
import os
from tencentcloud.common import credential
from tencentcloud.common.common_client import CommonClient
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException

cred = credential.Credential(
    os.environ["TENCENTCLOUD_SECRET_ID"],
    os.environ["TENCENTCLOUD_SECRET_KEY"])

httpProfile = HttpProfile()
# 域名首段必须与 CommonClient 第一个参数（service）严格匹配
httpProfile.endpoint = "cvm.tencentcloudapi.com"
profile = ClientProfile()
profile.httpProfile = httpProfile

# service, apiVersion, credential, region —— 前三个必填
cc = CommonClient("cvm", "2017-03-12", cred, "ap-shanghai", profile=profile)

# 参数直接传 dict，返回也是 dict（已解包 Response）；失败同样抛 TencentCloudSDKException
headers = {"X-TC-TraceId": "ffe0c072-8a5d-4e17-8887-a8a60252abca"}
data = cc.call_json("DescribeInstances", {"Limit": 10}, headers=headers)
for ins in data["InstanceSet"]:
    print(ins["InstanceId"])
```

要点：

- 端点默认按 `<service>.tencentcloudapi.com` 推导，也可显式 endpoint；版本号必须与官网 API 文档一致。
- 没有 Request/Response 模型——参数名错误、必填缺失只能在服务端暴露，建议在平台侧自行维护 schema 或对内部接口使用。
- CommonClient 同样支持 Profile 全套配置（代理、重试、语言、apigw 端点）与 call_sse 流式入口。

## 决策小结

| 场景 | 凭证 | 客户端 |
|------|------|--------|
| 本地脚本 | 环境变量 / Credential | 产品客户端 |
| CVM/TKE 部署 | DefaultCredentialProvider | 产品客户端 |
| 跨账号审计/运维 | STSAssumeRoleCredential | 产品客户端 |
| 动态服务名/极简依赖 | 任一凭证 | CommonClient |

## 相关概念

- [05 凭证体系](../concepts/05-credential-chain.md)——五级来源与刷新时刻全表
- [08 分包与遗留层](../concepts/08-packaging-and-legacy.md)——CommonClient 为何能脱离产品包工作
- [01 同步快速入门](01-sync-quickstart.md)
