---
type: Concept
title: 生成代码模式——版本目录四件套、动作方法模板与模型序列化
description: tencentcloud/<product>/v<date>/ 四件套的生成规则；XxxClient 动作方法固定五步法；AbstractModel 下划线属性到 API 字段名的变换、嵌套递归序列化与 _deserialize 模式；errorcodes 常量
tags: [tencentcloud-sdk-python, 代码生成, AbstractModel, 序列化, models, errorcodes]
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

# 生成代码模式：版本目录四件套

300 个 API 版本包全部由代码生成，结构与代码形状高度同构。读懂任意一个包（本文以 CVM v20170312 为样本，规模见 F-019）即可类推其余 260 个产品。

## 四件套布局（F-014、F-021、F-046）

```
tencentcloud/cvm/
├── __init__.py                 # 空文件
└── v20170312/
    ├── __init__.py
    ├── cvm_client.py           # 同步客户端：106 个动作方法
    ├── cvm_client_async.py     # 异步客户端：106 个 async 动作方法
    ├── models.py               # 286 个类：Request / Response / 嵌套结构体
    └── errorcodes.py           # 417 个错误码常量
```

同步客户端只做两件事——声明服务身份、暴露动作方法：

```python
class CvmClient(abstract_client.AbstractClient):
    _apiVersion = '2017-03-12'
    _endpoint = 'cvm.tencentcloudapi.com'
    _service = 'cvm'
    _sdkVersion = 'SDK_PYTHON_3.1.185'
```

`_service` 参与 TC3 签名的 credential scope，`_apiVersion` 进入 X-TC-Version 头，`_endpoint` 是默认连接主机（F-046）。这三个常量是生成层与手写内核的唯一接口契约。

## 动作方法五步法（F-047）

每个 Action 对应一个大驼峰同名方法，方法体固定五步，以 AllocateHosts/DescribeInstances 为代表：

```python
def DescribeInstances(self, request, headers=None, options=None):
    try:
        params = request._serialize()                          # 1
        body = self.call("DescribeInstances", params,
                         headers=request.headers,
                         options=options or {})                # 2
        response = json.loads(body)                            # 3
        model = models.DescribeInstancesResponse()             # 4
        model._deserialize(response["Response"])               # 5
        return model
    except TencentCloudSDKException:
        raise
    except Exception as ex:
        raise TencentCloudSDKException(type(ex).__name__, str(ex))
```

要点：

1. **入参永远是 Request 模型对象**（`models.DescribeInstancesRequest`），不是 dict——这保证字段名与类型在客户端侧可检查。
2. **Action 名以字符串显式传入** self.call，与 X-TC-Action 头一致。
3. **返回永远是 Response 模型对象**；非 SDK 异常在边界统一包装为 TencentCloudSDKException，调用方只需 except 一种异常。
4. 异步版本同构，仅签名变为 `async def DescribeInstances(self, request: models.DescribeInstancesRequest, opts: Dict = None) -> models.DescribeInstancesResponse`，内部走 `call_and_deserialize`（F-081）。

## 模型类：下划线属性 + property（F-042 ~ F-045）

models.py 中每个类的字段采用「私有下划线属性 + 同名 property」对：

```python
class DescribeInstancesRequest(AbstractModel):
    def __init__(self):
        self._InstanceIds = None
        self._Filters = None
        self._Offset = None
        self._Limit = None

    @property
    def InstanceIds(self):
        return self._InstanceIds

    @InstanceIds.setter
    def InstanceIds(self, InstanceIds):
        self._InstanceIds = InstanceIds
```

docstring 同时承载三类信息：中文参数说明、Sphinx 风格类型标注（`:type Filters: list of Filter`）、从官网文档同步的 HTML 片段（F-045）。这解释了 models.py 为何异常庞大（CVM 23652 行）——大量篇幅是文档字符串。

嵌套结构体（如 AccountQuota、Filter）与 Request/Response 类结构完全相同，都继承 AbstractModel，区别只在用途。

## 序列化：_serialize 与键名变换（F-042）

基类 `AbstractModel._serialize(allow_none=False)` 遍历 `vars(self)`：

1. 跳过内部属性 `_headers`（它不是 API 参数，而是自定义请求头载体）；
2. 键名变换规则：去掉首字符下划线后把第二个字符大写——`_InstanceIds` → `InstanceIds`、`_Filters` → `Filters`；
3. 值为嵌套 AbstractModel → 递归 `_serialize`；
4. 值为 list/tuple → 逐项序列化；
5. None 值默认跳过（allow_none=True 时保留为 null）。

`to_json_string(indent)` 以 `ensure_ascii=False` 输出中文不转义的 JSON（F-043）。需要注意：`_serialize` 输出的是**嵌套 dict**，真正发往云 API 的点号扁平键（`Filters.0.Name` 形态）是 AbstractClient.\_format\_params 在构建请求时完成的第二步变换（F-026）：

```python
{"Placement": {"Zone": "ap-shanghai-1"}}
#   → _format_params →
{"Placement.Zone": "ap-shanghai-1"}
{"Filters": [{"Name": "zone"}]}
#   →
{"Filters.0.Name": "zone"}
```

## 反序列化：生成代码覆写 _deserialize（F-044）

AbstractModel 基类的 `_deserialize` 是空壳，每个生成类按自身字段表覆写，模式为「标量直取、对象递归、列表逐项」：

```python
def _deserialize(self, params):
    self.QuotaId = params.get("QuotaId")
    if params.get("AccountQuotaOverview") is not None:
        self.AccountQuotaOverview = AccountQuotaOverview()
        self.AccountQuotaOverview._deserialize(params.get("AccountQuotaOverview"))
    if params.get("QuotaList") is not None:
        self.QuotaList = [Quota()._deserialize(item) for item in params.get("QuotaList")]
```

这意味着反序列化严格按**响应模型的字段表**进行——服务端新增的未知字段不会出现在对象上（但不影响 `to_json_string` 之外的兼容）；字段类型在生成期固定，无运行时 schema 查询。

## 错误码常量（F-048）

errorcodes.py 把官网错误码表生成为大写常量：

```python
# CVM账号资格限制。
ACCOUNTQUALIFICATIONRESTRICTIONS = 'AccountQualificationRestrictions'
```

CVM 一个产品就有 417 个常量。它们**不参与运行时错误分支**（运行时只按返回的 Code 字符串构造异常），用途是让调用方写常量比对而非裸字符串：

```python
from tencentcloud.cvm.v20170312 import errorcodes
if err.get_code() == errorcodes.REQUESTLIMITEXCEEDED:
    ...
```

## 多版本并存的导入含义（F-015）

34 个产品有多个 `v*` 目录，彼此独立、可同时导入：

```python
from tencentcloud.monitor.v20180724 import monitor_client        # 旧版
from tencentcloud.monitor.v20230616 import monitor_client as mc2  # 新版
```

不同版本包的类同名但来自不同模块，升级 API 版本是一次显式的 import 路径迁移，不会被 pip 升级隐式改变。

## 实践建议

- 构造请求一律用 `models.XxxRequest()` + 属性赋值，获得 IDE 补全与 docstring 参数文档；不要手写扁平 dict。
- 查参数含义优先看 Request 类 docstring 或官网 API 文档，而不是通读 models.py。
- 需要动态、无模型的调用（如代理网关透传）才考虑 CommonClient（见 [08 分包与遗留层](08-packaging-and-legacy.md)）。

## 相关概念

- [01 架构与一次同步调用链](01-architecture.md)——五步法中 self.call 之后的全部机制
- [04 签名与传输](04-signature-and-http.md)——嵌套 dict 到点号键之后的签名与 HTTP 处理
- [07 异步栈](07-async-stack.md)——异步动作方法的类型标注与 call_and_deserialize
