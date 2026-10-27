---
type: Concept
title: 企业工作区的七个逻辑平面
description: 从终端访问到企业服务的职责分工，以及隔离、策略生效和治理成熟度
source: ../references/article-source.md
sources:
  - id: ledger
    resource: ../references/article-source.md
  - id: architecture
    resource: https://docs.nvidia.com/enterprise-reference-architectures/secure-agent-workspace-reference-design/latest/reference-architecture.html
  - id: governance
    resource: https://docs.nvidia.com/enterprise-reference-architectures/secure-agent-workspace-reference-design/latest/security-and-governance-model.html
generated: {by: "process:okf-wiki-author", at: "2026-10-27"}
status: draft
stale_after: 2026-12-31
---

# 企业工作区模型

受管工作区把用户入口与 Agent 执行环境分开：终端连接工作区，Agent 与工具在工作区内运行；跨用户独立 guest kernel，不能将多个用户塞进普通共享内核容器就视为等价隔离（F-032、F-033、F-036）。[^architecture]

## 职责地图

下表是七平面的中文职责归纳，不表示七台物理机器，也不表示它们全部由一个 OpenShell Gateway 承担（F-031、F-038）。

| 平面 | 主要职责 | 应追问的边界 |
|---|---|---|
| 用户终端 | 用户发起连接、使用受管会话 | 谁能连接哪个工作区 |
| 控制平面 | 工作区资源与生命周期协调 | 谁能创建、重建、回收 |
| Bootstrap | 初始化工作区所需配置与引导 | 初始身份和配置是否可信 |
| 访问管理 | 身份、会话入口与授权 | Broker 的会话权限是否越界 |
| Agent 工作区 | 承载 Agent、工具和用户工作内容 | 用户之间是否共享 guest kernel |
| 安全运行时 | 执行策略、凭证中介及证据反馈 | 访问能否绕过中介 |
| 企业服务 | 模型、代码、数据与业务 API | 目标端是否落实最小权限 |

Trusted Access Broker 为用户提供受身份控制的连接；Credential mediator 管理 Agent 对目标服务的凭证（F-038）。能登录工作区不等于被允许调用所有业务 API，网络目的地可达也不等于该身份拥有全部操作权限。

模型推理与工作区分离。默认可以把模型调用路由到受管推理服务；本地 GPU 工具和本地模型各自需要理由（F-037）。该模型让 CPU 工作区、远端模型与企业服务形成清晰分工，而无需把模型显存需求强加给每个终端。

## 三种控制阶段

| 阶段 | 文档描述 | 不能据此宣称 |
|---|---|---|
| Phase 0 | 企业受管工作区基线 | 仅受管就已具备所有运行时控制 |
| Phase I | 外围身份、镜像、网络、生命周期、人工批准与审计 | 外围治理能约束全部工作区内部动作 |
| Phase II | 加入运行时约束、凭证代理、签名策略、任务委托、审计与撤销 | 只装 DPU 或只开 audit mode 即达到该阶段 |

阶段是文档中的控制模型（F-040～F-042），不是自动认证标签。硬件放置、VM 隔离与控制成熟度必须分别描述。

启用前还需发布数据分类政策（F-062）。人工批准按影响范围设置：受保护分支合并、发送、发布、删除和共享状态变更需批准，不能用网络请求获准替代业务复核（F-063）。具体证据目标见[部署与验收](04-deployment-and-acceptance.md)。

## 从策略到证据

GitOps 发布一份策略意图、把 YAML 挂进 VM、执行控制接受并应用策略、实际请求得到授权结果，是不同状态。OpenShift Virtualization 参考实现提供平台映射，但不能以配置文件存在代替生效反馈（F-039、F-048）。

评审时应保存策略标识、应用反馈和请求结果，并核对它们是否属于同一工作区及同一时点。这是教程作者的验收建议，未声明官方拥有某个固定名称的字段或 API。

## 失陷与撤销

guest root 失陷后，guest 内日志和控制不能继续无条件充当可信证据；独立管理的外部执行控制才有继续可信的基础（F-043）。[^governance]

“隔离”“停止”“撤权”应分别验收：网络断开可能不停止本地进程，进程终止可能不撤销下游 token，撤销未来访问也不会自动撤回已经被业务系统接受的订单或写入（F-044）。需要补偿的业务副作用应由目标业务系统处理，不能依靠一个“已隔离”状态一笔带过。

传播上界还须声明并测量，覆盖待批准动作、排队写入、子授权、缓存凭证和存活连接（F-064）。只测一个新请求被拒绝，不足以证明存量授权全部失效。

[^architecture]: [Reference Architecture](https://docs.nvidia.com/enterprise-reference-architectures/secure-agent-workspace-reference-design/latest/reference-architecture.html)
[^governance]: [Security and Governance Model](https://docs.nvidia.com/enterprise-reference-architectures/secure-agent-workspace-reference-design/latest/security-and-governance-model.html)
