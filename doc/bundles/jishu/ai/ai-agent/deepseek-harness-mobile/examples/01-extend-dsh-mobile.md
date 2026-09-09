---
type: Example
title: 扩展 DSH Mobile 开发入口
description: 四类扩展路径——新增 Host 方法、新增原生能力、新增页面、DSH 新事件上手机；附带边界判断（何时需改 DSH 本体）
tags: [DeepSeek Harness, DSH Mobile, Kuikly, 开发扩展, RPC, 原生桥接, KSP, @Page]
generated: { by: "process:blog-article-to-okf-bundle", at: "2026-09-09T00:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: article-source
    resource: /references/article-source.md
    title: 博文信源事实清单（F-001~F-045）
---

# 扩展 DSH Mobile 开发入口

> **操作基础**：以下扩展路径来自博文作者一手实测（F-042~F-044），面向"只想扩展 App"的开发者。若只做使用/连接，参考 [00-local-scan-connect](00-local-scan-connect.md)。本文命令与路径以 dsh-v0.1.1-rc.2 为背景（F-045）。

## 1. 新增 Host 方法（最轻量）

DSH 的 RPC 方法表按版本演进（F-020/F-042）。扩展 App 侧调用：

- 在 **`DshHostProtocol.kt`** 增加方法定义
- 复用现有 RPC 通道
- 只要不涉及新的系统能力，**三端不需要分别修改原生代码**

```
DshHostProtocol.kt（新增方法定义）→ 复用 RPC 通道 → 三端生效
```

> 参考协议层说明：[02-dsh-host-protocol](../concepts/02-dsh-host-protocol.md)（发消息即 HTTP RPC、方法表见 rpc-map.ts）。

## 2. 新增原生能力

跨端项目真正费时间的是 WebSocket、扫码、SSH、数据库这类系统能力（F-013）。接入新系统能力的步骤（F-043）：

1. 先在 **commonMain** 定义统一 Module 接口（业务语义：连接/发消息/收消息/断开等）
2. 再补三端实现：
   - **Android**：从 `KuiklyRenderActivity` 导出模块
   - **iOS**：实现放在 `KuiklyExpand/Modules`
   - **HarmonyOS**：实现放在 `kuikly/modules`

平台差异收敛在最底层，共享层页面不需要知道自己在哪个系统上（F-013）。架构细节见 [01-kuikly-cross-platform](../concepts/01-kuikly-cross-platform.md)。

## 3. 新增页面

创建带 **`@Page` 注解**的页面类，**KSP** 会生成路由（F-043）。

```
@Page 注解页面类 → KSP 生成路由 → 进入共享 UI
```

## 4. 让 DSH 内部新事件出现在手机上

如果要让 DSH 内部的新事件出现在手机上，需要三层配合（F-044）：

1. 写一个 **DSH 插件**监听对应事件
2. 通过 `host/remote-event` 转发
3. 具体事件仍要加入 **Host 侧允许转发的范围**；App 端对宽类型参数做容错

> App 端宽类型容错见 [02-dsh-host-protocol](../concepts/02-dsh-host-protocol.md) §5.2：保留未知字段、解析失败降级而非中断整条事件流。

## 5. 边界判断：何时需要改 DSH 本体

以下改动**不再属于 App 扩展**，而是需要改 DSH 本体（F-044）：

- 注册**新的官方 RPC 方法**
- 替换整套传输层

此类改动更适合**按上游项目的方式提交和维护**，而不是在移动客户端侧打补丁（F-044）。

## 6. 扩展决策速查

| 想做什么 | 入口 | 是否改 DSH 本体 |
|---------|------|:---:|
| 调用一个已有但未接的 Host 方法 | DshHostProtocol.kt | 否 |
| 用新系统能力（扫码/蓝牙/存储等） | commonMain Module + 三端实现 | 否 |
| 加一个页面 | @Page 注解 + KSP | 否 |
| DSH 内部新事件上手机 | DSH 插件 + host/remote-event | 否（需 Host 放行） |
| 注册官方新 RPC / 换传输层 | 上游 deepseek-harness | ✅ 是 |

> 记住：DSH 仍在 developer preview，协议与包结构都可能破坏性变化——开发时锁定已验证版本，逐步跟进上游（F-045）。
