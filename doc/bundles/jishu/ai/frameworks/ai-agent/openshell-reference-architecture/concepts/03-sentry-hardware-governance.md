---
type: Concept
title: Sentry 的独立硬件治理
description: DOCA Flow、Tower、Argus 的分工，运行时证据与检测时序边界
source: ../references/article-source.md
sources:
  - id: ledger
    resource: ../references/article-source.md
  - id: sentry
    resource: https://developer.nvidia.com/blog/inside-nvidia-sentry-secure-ai-agents-at-runtime/
generated: {by: "process:okf-wiki-author", at: "2026-10-27"}
status: draft
stale_after: 2026-12-31
---

# Sentry 治理机制

Sentry 将网络执行与运行时观察放入 BlueField-4 的独立信任域。其主机独立保护主张以 Agent 通信经过受治理的唯一路径为前提，不能把“有一块 DPU”直接解释为“所有行为均无法绕行”（F-049、F-058）。[^sentry]

## 组件分工

| 组件 | 处理对象 | 工作方式及限制 |
|---|---|---|
| DOCA Flow | L4 网络目的地及连接 | 硅加速防火墙拒绝未授权连接，将允许流量送往 Tower |
| DOCA Tower | L7 应用请求与响应 | Envoy 透明代理；对配置检查的 TLS 连接终止解密，再检查内容和授权 |
| OPA / Rego | 策略输入与授权决策 | 本地内存评估；亚毫秒描述依赖策略复杂度与配置 |
| DOCA Argus | 选定易失主机内存区域 | 带外观察进程、容器、网络、库与哈希上下文 |
| 专用分类模型 | Agent 通信及可获得的推理痕迹 | 可在本地或远程 GPU 系统运行，inline 或 out-of-band 分析 |

依据 F-050～F-056。L4 允许一个目标不代表其全部 API 操作获准；L7 授权能够进一步区分请求内容与操作。Argus 的观察范围也不是无条件读取所有主机状态。

术语分开理解：OPA（Open Policy Agent）是策略评估引擎，Rego 是表达策略规则的语言，不是两套平行的防火墙。

## 授权所需的证据

Tower 将请求同 Argus 观察到的进程和运行环境关联。例如，可检查容器哈希是否在批准清单中、发起进程是否属于容器 SBOM（软件物料清单）、是否符合允许的路径与参数，再评估 API 操作权限（F-054）。

SPIFFE/SPIRE 提供可验证的工作负载身份，伙伴身份与 XDR/SIEM（扩展检测响应、安全信息事件管理）平台可加入身份上下文和调查流程（F-055）。身份回答“是谁”；策略回答“能做什么”；运行证据回答“当前环境是否满足条件”。这三类证据不能互相替代。

SPIFFE 是工作负载身份规范；SPIRE 是实现相关身份签发与证明流程的软件。两者不是身份名称与权限规则的同义词，支持集成也不证明本次部署已接通。

## 检测与响应时序

| 模式 | 何时作判断 | 可声称的结果 |
|---|---|---|
| Inline 分类 | 请求路径上、送达前 | 对被该路径覆盖且判定有害的内容可先阻断 |
| Out-of-band 分类 | 路径外持续观察、发现后 | 可触发响应，但已发生的动作可能需要业务补偿 |

这是 F-056 的时序区别。新闻稿的“毫秒级隔离”仍是厂商自述，且不等于检测零延迟、零漏报或业务副作用零发生（F-010、F-044）。

## 证据与信任条件

官方使用 `attested telemetry`（带证明的遥测）和 `tamper-evident records`（篡改可察觉的记录）描述证据（F-057）。后者不能拔高成绝对不可篡改，也不能单靠名词就推定审计已满足法规要求。

以下是由文档前提推导的部署验证问题，不是本次测试结果：

1. 所有目标通信是否确实经过受保护路径，是否存在旁路网卡或未纳管出口。
2. BlueField 管理权限是否独立于已失陷的主机。
3. 策略与身份变更是否实际生效，失联时如何处理。
4. TLS 检查是否覆盖所需连接，凭证、隐私与证书管理是否有责任人。
5. 遥测来源、完整性、保存与关联能否被验证。

Sentry 深潜的整产品可用性仍是计划 2027 年初，DOCA 部分库可作为提前实验基础（F-011、F-059）。采购与上线应以实际发布、支持矩阵、版本及实验结果重新确认。

基础设施准入还须明确平台负责人、安全策略负责人、事件响应执行者和隔离释放批准者；验证失效关闭、更新、回滚、恢复，以及重启或迁移后工作区与策略的绑定（F-065）。支持矩阵通过不等于运维准入通过，具体交付变化按[逐事实更新规则](../references/verification.md#更新与传播规则)处理。

[^sentry]: [Inside NVIDIA Sentry](https://developer.nvidia.com/blog/inside-nvidia-sentry-secure-ai-agents-at-runtime/)
