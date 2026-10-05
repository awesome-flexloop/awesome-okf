---
type: Reference
title: 信源：tencentcloud-sdk-python 3.1.185 官方文档与工程元数据
description: README、setup.py/package.py/products.md/CHANGELOG/tox.ini、examples 与 QcloudApi 遗留层的信源登记——安装形态、分包机制、凭证管理文档、版本演进与示例索引
tags: [tencentcloud-sdk-python, README, packaging, 元数据, QcloudApi, 信源登记]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-10-04T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-04T00:00:00Z" }
status: stable
stale_after: 2027-10-04
sources:
  - id: facts
    resource: /facts.md
    title: tencentcloud-sdk-python 事实清单（F-001 ~ F-100）
  - id: self
    resource: /references/source-2.md
    title: 官方文档与工程元数据信源
---

# 信源：tencentcloud-sdk-python 3.1.185 官方文档与工程元数据

本文档登记本知识包引用的第二类信源——随仓库分发的官方中文 README、打包/测试工程文件、示例目录与遗留 QcloudApi 目录。版本指纹同 [source-1.md](source-1.md)（tag 3.1.185）。

## 工程文件索引

| 文件 | 关键内容 | 事实依据 |
|------|----------|----------|
| `README.md`（375 行，中文） | 依赖环境、安装（全产品包/指定产品包/common 分包）、快速入门、完整配置示例、Common Client、异步调用、代理/证书、凭证管理 5 方式 | F-004 ~ F-006、F-066、F-078、F-082、F-093、F-094、F-100 |
| `setup.py` | 全产品包元数据：name、requests>=2.16.0、`[async]→httpx>=0.22.0`、classifiers、Apache-2.0 | F-002、F-003 |
| `setup.cfg` | `[bdist_wheel] universal=1`（py2/py3 通用 wheel） | F-009、F-099 |
| `MANIFEST.in` | README.rst/LICENSE 与 `recursive-include QcloudApi *`（遗留 SDK 随包发布） | F-009、F-088 |
| `tox.ini` | py27/py36~py312 测试矩阵、pytest-asyncio、py27 忽略 `*_async.py`、passenv 凭证变量 | F-010 |
| `package.py` | 分包打包工具：按产品生成独立 setup.py 并 build/twine 上传；产品包依赖 `common>=当前,<下一大版本` | F-007、F-008、F-099 |
| `products.md` | 产品包名缩写登记表，262 个数据行；`as` 行对应目录名 `autoscaling` | F-011、F-013 |
| `CHANGELOG.md`（105 行） | 最早条目 `[3.0.1317] - 2025-02-12`「支持重试功能」 | F-070 |

## 官方 README 关键时点记载

- Common Client 调用方式从 **3.0.396** 开始支持；只需安装 `tencentcloud-sdk-python-common` 包即可向任何产品发起调用（F-078）。
- 异步调用从 **3.1.0** 开始支持；需安装 `tencentcloud-sdk-python-common[async]`，使用 `*_client_async` 模块，建议 `async with`（F-082）。
- 凭证管理章明确提供链顺序为「环境变量 -> 配置文件 -> 实例角色 -> TKE OIDC 凭证」（F-066）。
- 安装注意：全产品 SDK 与指定产品 SDK「两种方式只能选择其中一种」；多产品包建议与 common 包保持同一版本（F-006）。

## 示例目录索引（examples/，49 个 .py）

| 路径 | 演示主题 |
|------|----------|
| `examples/cvm/v20170312/describe_instances.py` | 同步标准调用（Credential + HttpProfile + ClientProfile + Filter） |
| `examples/cvm/v20170312/describe_instances_async.py` | 异步标准调用 |
| `examples/cvm/v20170312/describe_instances_sts.py` | STSAssumeRoleCredential 角色扮演 |
| `examples/cvm/v20170312/credential_providers.py` | DefaultCredentialProvider 凭证提供链 |
| `examples/common_client/describe_instances.py` | CommonClient 泛调 CVM（同步） |
| `examples/common_client/describe_instances_async.py` | CommonClient 泛调（异步） |
| `examples/common_client/chat_completions_async.py` | CommonClient 调 AI 流式接口（SSE） |
| `examples/common_client/cls_upload_log.py`、`examples/cls/v20201016/uploadlog*.py` | CLS 日志上传（含 protobuf 与二进制上传） |
| `examples/hunyuan/v20230901/chat_completions_async.py` | AI 流式接口 SSE 消费（README 索引，F-094） |
| `examples/apigateway_proxy/describe_instances.py` | 经 API 网关代理调用 |

完整文件清单与计数口径见 F-018、F-092 ~ F-094。

## 遗留层索引（QcloudApi/，52 个 .py）

云 API v2 时代 SDK，随全产品包发布但与 3.0 运行时完全独立（F-085 ~ F-088）：

| 路径 | 内容 |
|------|------|
| `QcloudApi/qcloudapi.py` | `QcloudApi(module, config)` 入口：44 个具名分支（1 个 if + 43 个 elif）的硬编码模块工厂，未知模块回退 base.Base + `<module>.api.qcloud.com` 端点 |
| `QcloudApi/modules/base.py` | `Base`：`requestUri='/v2/index.php'`、默认 HmacSHA1、公共参数拼装、generateUrl/call |
| `QcloudApi/modules/` | 46 个 .py（含 `__init__.py`、`base.py` 与 44 个产品模块：cvm/cdb/lb/image/sec/.../sts/dc） |
| `QcloudApi/common/` | api_exception、request、sign（HmacSHA1/HmacSHA256 旧实现） |

## 覆盖事实编号

F-002 ~ F-013、F-017、F-018、F-066、F-070、F-078、F-082、F-085 ~ F-094、F-099、F-100。
