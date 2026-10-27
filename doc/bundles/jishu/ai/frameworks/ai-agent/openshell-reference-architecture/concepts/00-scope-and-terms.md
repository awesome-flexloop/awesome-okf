---
type: Concept
title: OpenShell 软件、参考架构与 Sentry 的分工
description: 从 Agent 执行风险出发，区分软件运行时、企业工作区设计和硬件独立治理
source: ../references/article-source.md
sources:
  - id: ledger
    resource: ../references/article-source.md
  - id: blog
    resource: https://blogs.nvidia.cn/blog/openshell-reference-architecture/
  - id: scope
    resource: https://docs.nvidia.com/enterprise-reference-architectures/secure-agent-workspace-reference-design/latest/what-it-is-not.html
generated: {by: "process:okf-wiki-author", at: "2026-10-27"}
status: draft
stale_after: 2026-12-31
---

# 产品与架构范围

一个能执行 shell、读取仓库并调用企业 API 的 Agent 同时拥有文件、进程、网络和业务权限。参考架构将这些访问的治理放入计算基础设施，而不只依赖模型遵守提示词。NVIDIA 的发布主张把模型推理、Harness 执行和治理分别放在 Rubin、Vera 与 BlueField 上；这是全栈设计叙述，不是所有部署都必须购买该硬件组合的要求（F-003、F-035～F-037）。[^ledger]

## 三个实体

| 实体 | 关注的问题 | 阅读时不能混同 |
|---|---|---|
| OpenShell 软件 | 不可信 Agent 可以接触哪些文件、进程、网络和凭证 | 声明式安全运行时，不是业务 Agent 框架 |
| OpenShell 参考架构 | 企业如何组织工作区、身份、镜像、访问、运行时与基础设施 | 公开参考设计，不是可直接等同全产品 GA 的安装包 |
| NVIDIA Sentry | 主机边界失陷后，如何从独立硬件域观察和约束受保护路径 | DOCA/BlueField-4 上的治理框架，仍有交付计划与路径前提 |

对应事实为 F-002、F-013～F-018、F-049、F-058。术语“安全运行时”泛指执行约束层；不能把企业设计中的整个安全平面只理解成 OpenShell 的某一个进程。

## 阅读前置词汇

| 术语 | 在本教程中的含义 |
|---|---|
| Agent Harness | 驱动模型、上下文、工具调用与执行循环的软件 |
| Workload | 驱动分配给不可信执行的工作负载环境 |
| Sandbox | OpenShell 内部拥有 Agent 进程并转发请求的组件；不是整套企业工作区 |
| Supervisor | 位于隔离边界可信侧的授权与连接执行组件 |
| Gateway | 协调生命周期、策略、凭证、身份与会话的控制平面 |
| VM / microVM | 独立 guest kernel 的虚拟机边界，不等同普通共享内核容器 |
| DPU | 专用基础设施处理器；此处用于 BlueField 独立治理域 |
| Inline / out-of-band | 前者在请求路径上处理，后者在路径外观察与响应 |

OpenShell 软件的 Docker/Podman 驱动可以隔离网络并以 Supervisor 中介访问（F-022）。企业 Secure Agent Workspace 又要求跨用户不共享 guest kernel（F-033、F-036）。这两条描述不同层级：软件驱动可用，不自动证明多用户企业隔离合格。

## 发布状态

2026-10-21 新闻稿的“现已推出”链接对应已开放的设计文档；Sentry 深潜写的是计划次年年初可用，即该文章语境中的 2027 年初。新闻稿末尾还说明产品与功能处于不同阶段（F-001、F-002、F-011、F-012）。[^blog]

性能数据同样需要限定。Vera 的最高 2 倍、容量最高提升 20% 与毫秒级隔离都是厂商声明，不能作为本次已验证成效。[核验页](../references/verification.md)保留原始口径和缺口（F-009、F-010）。

## 适用和排除范围

参考设计面向受管、单用户 Agent 工作区。用户终端连接进入，Agent 与工具在工作区运行。它不替代 IdP（身份提供方）、安全审查或生产 API 托管平台；“Agent 在外部、仅工具在独立 sandbox”的形态不在本文档范围内（F-032～F-035）。[^scope]

学习后应能把现有系统中的身份入口、工作区、凭证代理和网络授权分别定位。实际部署仍需选择已交付组件、固定版本并验证隔离边界。

[^ledger]: [事实台账 F-001～F-066](../references/article-source.md)
[^blog]: [NVIDIA 中文原稿](https://blogs.nvidia.cn/blog/openshell-reference-architecture/)
[^scope]: [参考设计的排除范围](https://docs.nvidia.com/enterprise-reference-architectures/secure-agent-workspace-reference-design/latest/what-it-is-not.html)
