---
type: Concept
title: 分包体系与 QcloudApi 遗留层——package.py、CommonClient 泛调与云 API v2
description: package.py 如何为 261 个产品生成独立发行包及 common 版本上界锁定；全产品包/分包互斥的根因；CommonClient 仅装 common 泛调任意产品的机制；QcloudApi v2 时代 SDK 的 /v2/index.php、硬编码 elif 工厂与 HmacSHA1
tags: [tencentcloud-sdk-python, package.py, 分包, CommonClient, QcloudApi, 遗留系统, 云API v2]
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

# 分包体系与 QcloudApi 遗留层

## 为什么有三套包（F-005 ~ F-009）

全量仓库 1783 个 Python 文件、覆盖 261 个产品，但大量使用场景只调一两个产品（典型如 SCF/Lambda 部署）。官方为此在 PyPI 上发布三类包：

| PyPI 包 | 内容 | 适用场景 |
|---------|------|----------|
| `tencentcloud-sdk-python` | common + 全部 300 个版本包 + QcloudApi | 本地开发、不关心体积 |
| `tencentcloud-sdk-python-common` | 仅 20 个运行时文件 + config 产品 | 配合分包；或仅用 CommonClient |
| `tencentcloud-sdk-python-<product>` | common 依赖 + 单个产品目录 | 服务端按产品安装 |

## package.py 分包机制（F-007、F-008、F-099）

仓库根的 package.py 是官方分包工具（`python package.py --services cvm cdb --upload`），工作流：

1. 在 temp-directory 中组装一个最小包：复制 `tencentcloud/__init__.py`（版本号）与选中的产品目录；
2. 按 SETUP 模板生成该产品的 setup.py——name 为 `tencentcloud-sdk-python-<product>`，依赖声明固定为：
   ```
   tencentcloud-sdk-python-common>=当前版本, <下一大版本
   ```
   上界由 get_highest_version() 算出（如 3.1.185 → `<4.0.0`），防止产品包意外拉入不兼容的未来 common；
3. 调用 `python3.8 -m build` 构建 universal wheel（setup.cfg `universal=1`，py2/py3 通用），`twine upload` 上传。

互斥安装（README 明文「两种方式只能选择其中一种」，F-006）的根因是：全产品包与每个产品分包都会在 site-packages 写入相同的 `tencentcloud/<product>/` 路径，混装会造成文件互相覆盖与版本错配。

## CommonClient：不装产品包也能调任意 API（F-077、F-078）

```python
from tencentcloud.common.common_client import CommonClient
client = CommonClient("cvm", "2017-03-12", cred, "ap-shanghai", profile)
resp = client.call_json("DescribeInstances", {"Limit": 10})
```

- 构造签名 `CommonClient(service, version, credential, region, profile=None)`，前三个参数必填（None 即抛异常）；它把传入的 version/service 写入 `_apiVersion`/`_service`，但**不覆盖 `_endpoint`**——端点由 `<service>.<rootDomain>` 动态推导（F-077）。
- 因此一个只装了 common 包的环境可以在运行时指定任意服务名与版本号调用云 API（3.0.396 起，F-078）。
- 代价：没有 XxxRequest/XxxResponse 模型类，参数靠 dict、错误只能在服务端暴露，也没有 IDE 补全。SDK 文档明确警告「必须明确知道接口所需参数，否则可能调用失败」。
- 内部用户：凭证体系本身也用 CommonClient 调 STS（AssumeRole/AssumeRoleWithWebIdentity），因为 credential.py 不能反向依赖具体产品包（见 [05 凭证链](05-credential-chain.md)）。

选型矩阵：

| 需求 | 选择 |
|------|------|
| 强类型、IDE 补全、固定产品 | common + 产品分包 |
| 部署体积极小、调用面动态（代理/网关/多租户） | common + CommonClient |
| 本地全量调试 | 全产品包 |
| 需要流式 SSE | 三者都支持，CommonClient 配合 call_sse/异步版本 |

## 遗留层 QcloudApi（云 API v2 时代）（F-085 ~ F-088）

仓库根的 `QcloudApi/`（52 个 .py）是与 3.0 运行时完全独立的旧 SDK，对应云 API v2 协议，仍随全产品包发布（MANIFEST.in 的 `recursive-include QcloudApi *`，F-088）。

### 入口工厂：硬编码 elif（F-085）

```python
service = QcloudApi("cvm", config)   # config 是 dict，不是 Profile 对象
```

`_factory` 用 1 个 if + 43 个 elif 共 **44 个具名分支**把模块名映射到 modules/ 下的 44 个产品模块类（cdb/account/cvm/image/lb/sec/.../sts/dc）；**未命中任何分支时不报错**，而是设置端点 `<module>.api.qcloud.com` 并回退到通用 `base.Base`。

### v2 协议特征（F-087）

| 维度 | QcloudApi v2 | SDK 3.0 |
|------|--------------|---------|
| 请求 URI | `/v2/index.php`（单入口） | `/`（产品独立端点 + X-TC-Action 头） |
| 端点 | `<module>.api.qcloud.com` | `<service>.tencentcloudapi.com` |
| 默认签名 | HmacSHA1（base64） | TC3-HMAC-SHA256（三级派生密钥） |
| 公共参数 | 混在业务参数中（Action/Nonce/Timestamp/SecretId/...） | X-TC-* 请求头 |
| 配置风格 | dict config + setSecretId/setRegion 等 setter | Credential + Profile 对象 |
| 调用方式 | `service.call(action, params)` / `generateUrl` | 强类型动作方法 |

旧 Sign 类（QcloudApi/common/sign.py）与 3.0 common/sign.py 的 HmacSHA1/HmacSHA256 是同一算法家族——3.0 ClientProfile 保留旧签名选项就是为了协议过渡期兼容（见 [04 签名与传输](04-signature-and-http.md)）。

### 使用建议

- **新代码不要使用 QcloudApi**：它停留在 v2 协议，端点域名与签名算法都是旧世代，新增云产品也不会进入 elif 工厂（只会静默回退 Base）。
- 维护存量脚本时注意：未知模块名不报错而是回退通用 Base + 猜测端点，"模块名拼错"不会在客户端侧失败，只会在服务端返回异常。
- QcloudApi 只存在于全产品包；产品分包不包含它。

## 版本升级实务

- 产品分包升级时 common 与产品包要同时升（版本约束的下一大版本上界会阻止跨大版本自动升级）。
- API 版本升级（如 monitor v20180724 → v20230616）与 SDK 包版本（3.1.185）是两件事：前者改 import 路径，后者 pip 更新（见 [02 生成代码模式](02-generated-code-pattern.md)）。
- CHANGELOG 显示 SDK 仍在高频发布（3.1.185 为 2026-10-02 快照），新错误码/新 Action 随代码生成持续进入产品包；锁版本部署时以 errorcodes.py 与 models.py 的实际内容为准。

## 相关概念

- [00 总览](00-overview.md)——四种形态与目录全景
- [05 凭证链](05-credential-chain.md)——CommonClient 在 STS 凭证刷新中的内部角色
- [04 签名与传输](04-signature-and-http.md)——新旧两代签名算法对照
- [02 CommonClient 与凭证示例](../examples/02-credential-and-common-client.md)
