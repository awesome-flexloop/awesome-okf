---
type: Concept
title: 腾讯云 Python SDK 总览——定位、版本、安装形态与目录全景
description: tencentcloud-sdk-python 3.1.185 是什么；云 API 3.0 配套 SDK 的四种安装/调用形态、common 内核加生成产品层的双层结构、261 产品 300 版本包的目录全景
tags: [tencentcloud-sdk-python, 入门, 安装, 分包, 目录结构, 云API]
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

# 腾讯云 Python SDK 总览

## SDK 的定位

`tencentcloud-sdk-python` 是腾讯云官方维护的 Python SDK，配套腾讯云 **API 3.0**（产品独立端点 + TC3-HMAC-SHA256 签名 + 版本化 Action 协议）。它把"构造请求参数 → 签名 → HTTPS 调用 → 反序列化为对象"的全过程封装为本地方法调用：

```python
resp = client.DescribeInstances(req)          # 一次云 API 调用
print(resp.to_json_string(indent=2))           # 返回的是强类型 Response 对象
```

本知识包基于固定快照 **3.1.185**（commit `be50b26d`，2026-10-02 发布）逐字精读源码整理，版本指纹与行号信源见 [信源登记](../references/source-1.md)。

## 运行环境与依赖（F-001 ~ F-004）

| 项目 | 内容 |
|------|------|
| SDK 版本 | 3.1.185（`tencentcloud/__init__.py` 的 `__version__`） |
| Python 版本 | 2.7、3.6 ~ 3.12（tox 测试矩阵与 README 一致） |
| 同步栈依赖 | requests >= 2.16.0 |
| 异步栈依赖 | 安装 `[async]` extra 时引入 httpx >= 0.22.0 |
| 证书 | 默认使用 certifi 提供的 CA 包 |
| License | Apache 2.0 |

## 四种安装与调用形态（F-005 ~ F-008、F-077、F-085）

理解这个 SDK 的第一件事，是分清它在 PyPI 上的**四种形态**——它们对应不同的部署体积与类型体验：

1. **全产品包 `tencentcloud-sdk-python`**：包含全部 261 个产品、300 个版本包，并附带 QcloudApi 遗留 SDK。适合本地开发或对体积不敏感的环境。
2. **公共包 + 产品分包**：先装 `tencentcloud-sdk-python-common`（20 个运行时文件），再按需装 `tencentcloud-sdk-python-<产品缩写>`（如 `tencentcloud-sdk-python-cvm`）。产品包对 common 的版本约束是 `>=当前版本,<下一大版本`，由仓库自带的 package.py 在分包时生成。
3. **只装 common 包 + CommonClient**：从 3.0.396 起，仅安装 `tencentcloud-sdk-python-common` 就能用 `CommonClient(service, version, credential, region)` 泛调任意产品的任意 API——代价是没有请求/响应模型类与 IDE 补全。
4. **遗留 QcloudApi**：云 API v2 时代（`/v2/index.php` + HmacSHA1）的旧 SDK，仍随全产品包发布，仅供维护存量脚本。

两条关键安装纪律（README 原文注意事项，F-006）：

- 全产品包与产品分包**互斥，只能二选一**，混装会产生包冲突；
- 使用多个产品分包时，建议它们与 common 包**保持同一版本**。

```bash
# 形态一：全产品包
pip install tencentcloud-sdk-python

# 形态二：common + 按需产品（推荐用于服务端）
pip install tencentcloud-sdk-python-common tencentcloud-sdk-python-cvm

# 形态二 + 异步
pip install 'tencentcloud-sdk-python-common[async]'

# 形态三：只要 CommonClient
pip install tencentcloud-sdk-python-common
```

## 双层结构：极小内核 + 海量生成代码（F-012 ~ F-021）

整个 `tencentcloud/` 包共 1783 个 Python 文件，但它们分成性质完全不同的两层：

```
tencentcloud/
├── __init__.py              # 仅一行 __version__ = '3.1.185'
├── common/                  # 【手写内核】20 个文件，全部机制都在这里
│   ├── abstract_client.py        # 同步客户端基类
│   ├── abstract_client_async.py  # 异步客户端基类（httpx + 拦截器链）
│   ├── abstract_model.py         # 模型基类（序列化/反序列化）
│   ├── credential.py             # 6 类凭证 + 默认提供链
│   ├── sign.py                   # TC3 / HmacSHA1 / HmacSHA256
│   ├── retry.py / retry_async.py # 重试
│   ├── circuit_breaker.py        # 地域熔断器
│   ├── common_client.py          # 泛用客户端
│   ├── profile/                  # HttpProfile、ClientProfile
│   ├── http/                     # requests 封装、预连接池
│   └── exception/                # TencentCloudSDKException
├── cvm/                     # 【生成产品层】261 个产品目录之一
│   └── v20170312/
│       ├── cvm_client.py          # 106 个 Action 方法（2713 行）
│       ├── cvm_client_async.py    # 同名异步方法
│       ├── models.py              # 286 个 Request/Response/结构体类（23652 行）
│       └── errorcodes.py          # 417 个错误码常量
├── hunyuan/ ...             # 其余 260 个产品
└── config/                  # config 自身也是一个产品（v20220802）
```

规模数字（均由脚本复核，口径见 [facts.md](../facts.md) F-012 ~ F-019）：

| 指标 | 数值 |
|------|------|
| `tencentcloud/` 子目录 | 263（261 产品 + common + config） |
| products.md 登记产品 | 262 行（包名 `as` 对应目录名 `autoscaling`） |
| API 版本包（同步 client / 异步 client / models / errorcodes 各一份） | 300 套 |
| 拥有多个 API 版本的产品 | 34 个（其中 iotvideo、rce、thpc、vm 各有 3 个版本） |
| CVM v20170312 样本规模 | 106 个 Action、286 个模型类、417 个错误码 |

这组数字背后的学习含义是：**产品层是代码生成产物，动作方法与模型类同构度极高**（生成模式详见 [02 生成代码模式](02-generated-code-pattern.md)）。读这个 SDK 不需要翻 261 个产品目录——读懂 common/ 内核 + 任选一个产品（本知识包以 CVM 为样本）即可掌握全貌。

## 版本目录命名规则（F-014、F-015）

每个产品目录下按 API 版本日期组织一个或多个 `vYYYYMMDD` 子目录：

- `cvm/v20170312/`——CVM 只有一个 2017-03-12 版本；
- `monitor/v20180724/` + `monitor/v20230616/`——Monitor 有新旧两个版本并存；
- 34 个产品处于多版本并存状态，老版本不删除，新版本与老版本可在同一安装包内共存。

版本字符串同时作为请求头 `X-TC-Version` 与签名 credential scope 的一部分发送，因此"导入哪个版本包"直接决定线上路由到哪个 API 版本。

## 与云 API 协议的对应关系

| SDK 概念 | 云 API 3.0 协议概念 |
|----------|---------------------|
| 产品目录名（cvm、hunyuan） | 服务名 service，决定端点 `<service>.tencentcloudapi.com` |
| `v20170312` / `_apiVersion='2017-03-12'` | API 版本（X-TC-Version） |
| 客户端动作方法（DescribeInstances） | Action（X-TC-Action） |
| `models.XxxRequest` 及其属性 | 请求参数（嵌套结构序列化为点号键） |
| `models.XxxResponse` | Response 实体 |
| errorcodes.py 常量 | Response.Error.Code 错误码 |

## 相关概念

- [01 架构与一次同步调用链](01-architecture.md)——从 Credential 到 Response 的完整路径
- [02 生成代码模式](02-generated-code-pattern.md)——产品四件套与模型类的同构模板
- [08 分包与遗留层](08-packaging-and-legacy.md)——package.py 分包机制与 QcloudApi v2 旧 SDK
