---
okf_version: "0.2"
type: group
title: "☁️ 云厂商开放 API SDK"
description: "云厂商开放 API 的官方 SDK 源码级教程——腾讯云 Python SDK（tencentcloud-sdk-python）：云 API 3.0 协议、TC3 签名、凭证提供链、重试熔断、异步栈与产品分包体系"
---

# ☁️ 云厂商开放 API SDK

本分组收录主流云厂商开放 API 官方 SDK 的源码精读束，重点拆解「少量手写运行时 + 海量代码生成产品层」的工程模式、签名协议、凭证体系与弹性机制，遵循 [OKF v0.2 规范](https://github.com/awesome-flexloop/awesome-okf)。

## 束清单

| 束 | 简介 | 入口 |
|----|------|------|
| **tencentcloud-sdk-python** | 腾讯云 Python SDK 3.1.185 源码精读：20 个手写内核文件驱动 300 个生成版本包；TC3-HMAC-SHA256 签名、五级凭证链、默认关闭的重试/熔断、httpx 异步 RequestChain、SSE、CommonClient 与 QcloudApi v2 遗留层 | [tencentcloud-sdk-python/](tencentcloud-sdk-python/index.md) |

## 学习路径建议

1. **协议层**：先理解云 API 3.0 的服务/版本/Action 三元组与 TC3 签名，再进入具体语言 SDK。
2. **架构层**：沿「生成代码模式 → 调用链 → 凭证 → 弹性 → 异步」顺序阅读，掌握一个 SDK 后可类推其他云厂商同代 SDK。
3. **实战层**：从同步快速入门到异步流式（SSE）与动态泛调（CommonClient），按 examples 目录照抄落地。

```{toctree}
:hidden:
:maxdepth: 7

tencentcloud-sdk-python/index
```
