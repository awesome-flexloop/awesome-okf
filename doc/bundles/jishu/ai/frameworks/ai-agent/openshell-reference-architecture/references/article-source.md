---
type: Reference
title: OpenShell 参考架构信源与事实登记
description: 公开新闻稿与官方技术文档的编号事实台账，区分设计要求、发布计划与厂商成效自述
source: https://blogs.nvidia.cn/blog/openshell-reference-architecture/
sources:
  - id: cn
    resource: https://blogs.nvidia.cn/blog/openshell-reference-architecture/
  - id: news
    resource: https://nvidianews.nvidia.com/news/openshell-reference-architecture
  - id: design
    resource: https://docs.nvidia.com/enterprise-reference-architectures/secure-agent-workspace-reference-design/latest/index.html
  - id: architecture
    resource: https://docs.nvidia.com/enterprise-reference-architectures/secure-agent-workspace-reference-design/latest/reference-architecture.html
  - id: tiers
    resource: https://docs.nvidia.com/enterprise-reference-architectures/secure-agent-workspace-reference-design/latest/deployment-tiers.html
  - id: governance
    resource: https://docs.nvidia.com/enterprise-reference-architectures/secure-agent-workspace-reference-design/latest/security-and-governance-model.html
  - id: scope
    resource: https://docs.nvidia.com/enterprise-reference-architectures/secure-agent-workspace-reference-design/latest/what-it-is-not.html
  - id: openshift
    resource: https://docs.nvidia.com/enterprise-reference-architectures/secure-agent-workspace-reference-design/latest/openshift-virtualization-reference-implementation.html
  - id: overview
    resource: https://docs.nvidia.com/openshell/latest/about/overview.html
  - id: runtime
    resource: https://docs.nvidia.com/openshell/latest/about/architecture.html
  - id: technical
    resource: https://developer.nvidia.com/blog/how-nvidia-openshell-reference-architecture-secures-and-governs-ai-agent-workloads-at-scale/
  - id: sentry
    resource: https://developer.nvidia.com/blog/inside-nvidia-sentry-secure-ai-agents-at-runtime/
  - id: product
    resource: https://www.nvidia.com/en-us/networking/products/software/sentry/
  - id: operations
    resource: https://docs.nvidia.com/enterprise-reference-architectures/secure-agent-workspace-reference-design/latest/operating-properties.html
generated: {by: "process:okf-wiki-author", at: "2026-10-27"}
status: draft
stale_after: 2026-12-31
---

# 信源与事实登记

检索时点为 2026-10-27。中文新闻稿、英文新闻稿、参考设计及软件文档、两篇技术博客和 Sentry 产品页共 14 个公开页面已读取。`latest` 是滚动文档路径，以下内容记录阅读时点，不代表固定软件版本的行为承诺。关键机制的章节及短引文保存在[核验记录](verification.md)，供上游变化后对照；未保存完整网页快照或固定 release/commit。

URL 中的营销追踪和用户标识参数已删除。公开可访问性不依赖这些参数。这里保存原创归纳与短引文，不复制新闻稿全文，也不声称持有网页归档快照。

## 信源地图

| ID | 页面 | 用途及独立性 |
|---|---|---|
| cn | [中文原稿](https://blogs.nvidia.cn/blog/openshell-reference-architecture/) | 用户指定入口，厂商发布及自述 |
| news | [英文新闻稿](https://nvidianews.nvidia.com/news/openshell-reference-architecture) | 发布事件与前瞻声明；与 cn 同源 |
| design | [Secure Agent Workspace 设计入口](https://docs.nvidia.com/enterprise-reference-architectures/secure-agent-workspace-reference-design/latest/index.html) | 参考设计范围与阅读顺序 |
| architecture | [逻辑参考架构](https://docs.nvidia.com/enterprise-reference-architectures/secure-agent-workspace-reference-design/latest/reference-architecture.html) | 平面、身份、网络与执行路径 |
| tiers | [部署层级](https://docs.nvidia.com/enterprise-reference-architectures/secure-agent-workspace-reference-design/latest/deployment-tiers.html) | 放置、设备与回收 |
| governance | [安全与治理模型](https://docs.nvidia.com/enterprise-reference-architectures/secure-agent-workspace-reference-design/latest/security-and-governance-model.html) | Phase 0/I/II、威胁与验收边界 |
| scope | [排除范围](https://docs.nvidia.com/enterprise-reference-architectures/secure-agent-workspace-reference-design/latest/what-it-is-not.html) | 单用户工作区、非目标 |
| openshift | [OpenShift Virtualization 参考实现](https://docs.nvidia.com/enterprise-reference-architectures/secure-agent-workspace-reference-design/latest/openshift-virtualization-reference-implementation.html) | 平台映射，非本次部署实测 |
| overview | [OpenShell 软件概览](https://docs.nvidia.com/openshell/latest/about/overview.html) | 产品定位与策略可变性 |
| runtime | [OpenShell 软件架构](https://docs.nvidia.com/openshell/latest/about/architecture.html) | Supervisor、驱动与认证边界 |
| technical | [参考架构技术博客](https://developer.nvidia.com/blog/how-nvidia-openshell-reference-architecture-secures-and-governs-ai-agent-workloads-at-scale/) | 工作负载与性能限定 |
| sentry | [Sentry 技术深潜](https://developer.nvidia.com/blog/inside-nvidia-sentry-secure-ai-agents-at-runtime/) | DOCA 组件、检测与计划可用性 |
| product | [Sentry 产品页](https://www.nvidia.com/en-us/networking/products/software/sentry/) | 产品定位，非独立成效证据 |
| operations | [运行属性](https://docs.nvidia.com/enterprise-reference-architectures/secure-agent-workspace-reference-design/latest/operating-properties.html) | 人工批准、基础设施责任与运维准入 |

这些页面均由 NVIDIA 发布。多页面一致只能证明厂商文档口径一致，不能记作多家独立来源验证。SAP 伙伴原文读取返回 403，未作为已读信源；其他伙伴生产落地情况亦未逐家回源。

## 编号事实

“文档要求”表示参考设计中的规范条件；“机制”表示官方描述，未在本机复现；“自述”仅证明厂商作出该声明。正文中的 F 编号均指向本表。

| 编号 | 陈述 | 来源 ID | 证据性质 |
|---|---|---|---|
| F-001 | NVIDIA 在 GTC 柏林发布 OpenShell 参考架构；英文新闻稿日期为 2026-10-21。 | news、cn | 发布事实 |
| F-002 | 中文原稿的“现已推出”链接指向公开的 Secure Agent Workspace 参考设计文档。 | cn、design | 可用性范围 |
| F-003 | 原稿列出 Rubin 运行模型、Vera 运行 Agent Harness、BlueField 运行治理的分工。 | cn | 厂商设计叙述 |
| F-004 | 原稿列出 RTX Spark、DGX Spark、DGX Station 作为边缘扩展系统。 | cn | 厂商设计叙述 |
| F-005 | 原稿列出 Linux、Kubernetes、Windows/MXC 及云平台的运行或集成方向。 | cn | 厂商生态声明 |
| F-006 | 安全伙伴的表述为正在集成支持；BBVA、Santander 的表述为协作探索。 | cn | 合作阶段 |
| F-007 | 原稿称 SAP 正将架构与 Joule Studio 运行时集成；ServiceNow 宣布 Arc 全面推出并描述 AI Passport 撤销权限。 | cn | 未独立核验的伙伴转述 |
| F-008 | 原稿称系统制造商构建基础设施、云商协作部署、推理与后训练服务商正在集成。 | cn | 合作阶段 |
| F-009 | 原稿将 Vera 表述为 x86 的 2 倍性能；技术博客限定为关键 Agent 工作负载上最高 2 倍。 | cn、technical | 厂商成效自述 |
| F-010 | 原稿称 BlueField-4/Sentry 可在毫秒内隔离阻断，并将 Agent 容量提升高达 20%。 | cn | 厂商成效自述 |
| F-011 | Sentry 技术深潜将可用性写为 planned availability early next year。 | sentry | 产品计划，按 2026 语境为 2027 年初 |
| F-012 | 新闻稿末尾说明所述产品功能处于不同阶段，时间安排可能变化，声明不是交付保证。 | cn、news | 前瞻声明 |
| F-013 | OpenShell 软件定位为开源自主 Agent 安全运行时。 | overview | 官方定位 |
| F-014 | OpenShell 声明式策略描述文件、进程、网络、API 与提供商凭证访问边界。 | overview、runtime | 官方机制 |
| F-015 | Gateway 管理 sandbox 生命周期、用户及操作者连接、策略、凭证、身份和会话协调。 | runtime | 官方机制 |
| F-016 | Compute runtime 建立 workload、独立 Supervisor、受保护通道和外围网络 fence。 | runtime | 官方机制 |
| F-017 | Sandbox 与不可信 Agent 同侧，拥有子进程及终端状态，不作策略决定。 | runtime | 官方机制 |
| F-018 | Supervisor 在可信侧授权请求、解析 DNS、提供获准凭证、打开获准连接并连接 Gateway。 | runtime | 官方机制 |
| F-019 | 当前 Linux backend 使用一个非 root 身份、无 Linux capabilities，Landlock 限制文件访问，seccomp user notification 暂挂网络操作。 | runtime | 后端限定 |
| F-020 | Workload 唯一允许出口为到 Supervisor 的受保护连接；fence 拒绝其余直连。 | runtime | 官方机制 |
| F-021 | Sandbox Protocol 使用相互认证的 HTTP/2 连接承载独立多流。 | runtime | 官方机制 |
| F-022 | Docker/Podman 将 Supervisor 放独立容器，使用认证 Unix socket，关闭 workload 容器网络。 | runtime | 驱动机制 |
| F-023 | Kubernetes 将 Supervisor 放独立 pod，使用 mTLS service 与限定出口的 NetworkPolicy。 | runtime | 驱动机制 |
| F-024 | VM 驱动将 Supervisor 放宿主进程，使用认证 vsock，guest 不设网络设备。 | runtime | 驱动机制 |
| F-025 | Policy prover 位于 Gateway，检查 Agent 提议的网络规则；发现新的凭证可达域、HTTP 方法或 metadata 访问等风险时阻断自动批准。 | runtime | 形式验证的限定用途 |
| F-026 | `openshell-prover` 可独立用于 CI 中的策略与边界核对。 | runtime | 官方工具声明 |
| F-027 | Gateway 是凭证签发方；Gateway JWT 与 Sandbox JWT 绑定一个 sandbox 和一个 generation，重启更新 token 与 TLS 证书。 | runtime | 认证机制 |
| F-028 | Sandbox 不持有 Gateway 签名密钥、Gateway JWT 或提供商凭证。 | runtime | 凭证边界 |
| F-029 | Supervisor 断连后 Sandbox 冻结 Agent；只有同一个 Supervisor 进程可重新连接并恢复。 | runtime | 故障行为 |
| F-030 | 文件系统和进程策略在创建时锁定；网络策略可热更新；凭证附件、轮转和撤销可运行时更新，新环境变量需新进程。 | overview | 策略生命周期 |
| F-031 | 企业参考设计划分终端、控制、Bootstrap、访问管理、Agent 工作区、安全运行时、企业服务七个逻辑平面。 | architecture | 文档模型 |
| F-032 | 终端负责连接；Agent 及其工具在工作区内执行。 | architecture、scope | 文档模型 |
| F-033 | 每个工作区是单用户环境；不同用户不得共享 guest kernel。 | scope | 文档要求 |
| F-034 | 外部 Agent 配独立工具 sandbox 不在该参考设计范围内。 | scope | 范围边界 |
| F-035 | 该设计不是生产 API 托管平台、IdP 或安全审查替代品，也不限定唯一云厂商或 Agent 框架。 | scope | 范围边界 |
| F-036 | VM/microVM 隔离边界、控制成熟度与硬件放置是独立设计维度；普通共享内核容器不是该工作区隔离基线。 | tiers、scope、governance | 文档要求 |
| F-037 | 模型推理是外部或独立依赖；默认 routed inference，GPU 工具加速与本地推理分别选择。 | architecture、tiers | 文档模型 |
| F-038 | Trusted Access Broker 处理受身份控制的会话连接；Credential mediator 处理目标服务凭证。 | architecture | 职责分工 |
| F-039 | 策略意图的发布和执行面应用是不同状态；仅改挂载 YAML 不代表运行时已应用策略。 | architecture、openshift | 生效边界 |
| F-040 | Phase 0 为企业受管工作区基线，Phase I 加入外围身份、镜像、网络、生命周期、人工批准和审计控制。 | governance | 文档模型 |
| F-041 | Phase II 加入运行时约束、凭证代理、签名策略、任务委托、审计和撤销等可证明执行的控制。 | governance | 文档模型 |
| F-042 | DPU 存在本身不构成 Phase II；audit-only 不等于阻断；不支持或不确定的证明结果不能记通过。 | governance | 验收边界 |
| F-043 | guest root 失陷后，独立管理、位于外部的执行控制才可继续作为可信依据。 | governance | 威胁模型 |
| F-044 | 网络隔离、停止进程、下游授权撤销是不同结果；已被业务系统接受的副作用不能靠撤销自动收回。 | governance | 撤销边界 |
| F-045 | 设备重新分配需核对 GPU/VRAM/本地存储清理；VM 重建不证明设备残留清除。 | tiers、governance | 回收要求 |
| F-046 | 部署层级包括 CPU VM、GPU VM/workstation、deskside workstation、team shared system、platform fleet。 | tiers | 部署模型 |
| F-047 | 团队共享物理系统仍需各用户独立 VM；很多 routed-inference coding 任务可使用 CPU VM。 | tiers | 部署模型 |
| F-048 | OpenShift Virtualization 文档给出控制、访问、工作区隔离及策略管理的参考实现映射。 | openshift | 文档参考实现 |
| F-049 | Sentry 是基于 DOCA、运行于 BlueField-4 独立信任域的安全软件框架。 | sentry、product | 官方机制 |
| F-050 | DOCA Flow 实现硅加速 L4 防火墙，拦截未授权目的地并把允许流量交给 DOCA Tower。 | sentry | 官方机制 |
| F-051 | DOCA Tower 基于 Envoy 透明代理作 L7 检查；配置检查的连接可经 TLS termination 解密。 | sentry | 检查范围限定 |
| F-052 | OPA/Rego 在本地内存评估策略，亚毫秒评估取决于策略复杂度与配置。 | sentry | 条件性厂商性能声明 |
| F-053 | DOCA Argus 在 BlueField-4 分析选定易失主机内存区域，不要求主机驻留 agent。 | sentry | 观察范围 |
| F-054 | Argus 提供进程、线程、容器、网络、库与哈希上下文；Tower 可关联 SBOM 与访问决策。 | sentry | 官方机制 |
| F-055 | Tower 支持 SPIFFE/SPIRE 与伙伴身份系统集成，并可向 XDR/SIEM 提供遥测。 | sentry | 官方集成声明 |
| F-056 | 专用模型可在本地或远程 GPU 系统分析通信；inline 分类可在送达前阻断，out-of-band 分类在检测后响应。 | sentry | 检测时序 |
| F-057 | Sentry 文档使用 attested telemetry 和 tamper-evident records 表述证据属性。 | sentry | 证据属性 |
| F-058 | Sentry 的主机独立控制叙述要求 Agent 通信经过 BlueField-4 管理的唯一路径。 | sentry | 路径前提 |
| F-059 | Sentry 深潜称 DOCA Argus、DOCA Flow、OVS-DOCA 等可作为 Sentry 计划可用之前的实验基础。 | sentry | 库与整产品交付区别 |
| F-060 | 技术博客另引 CoreWeave Terminal Bench 几何平均 1.8 倍及 sandbox 启动超过 3 倍；本次未取得 CoreWeave 原始测试报告。 | technical | NVIDIA 转述，未独立核验 |
| F-061 | Supervisor 在到期前共同续期两个 JWT；删除 sandbox 后不能续期。共享部署应设置 `gateway_jwt.ttl_secs`，未设置时 token 可持续一个 sandbox generation。 | runtime | 凭证生命周期 |
| F-062 | 发布数据分类政策是启用自主 Agent 的前置条件。 | governance | 文档要求 |
| F-063 | 高影响共享写入需人工批准，包括受保护分支合并、发送、发布、删除和共享状态变更；个人或临时目标写入按影响范围区分。 | operations | 文档要求 |
| F-064 | 撤销须声明并测量传播上界，覆盖待批准动作、排队写入、子级授权、缓存凭证和存活连接。 | governance | 文档要求 |
| F-065 | 可选 DPU 依赖须明确平台责任与安全响应分工；准入前验证失效关闭、更新、回滚与恢复，重启或迁移后复验绑定。 | operations | 文档要求 |
| F-066 | 部署层级的成本遥测与预算控制从工作区计量扩展到集中 FinOps 和预算门。 | tiers | 文档要求 |

## 阅读而非测试

本次没有部署 OpenShell、OpenShift 或 BlueField-4，没有重放绕行攻击、策略更新、凭证撤销或设备清理测试。新闻与官方机制的可溯源性不等于安全能力、时延、容量或伙伴交付已实测。
