---
type: Concept
title: OpenShell 软件执行与信任边界
description: Supervisor 中介、外围网络 fence、驱动通道、策略证明与凭证生命周期
source: ../references/article-source.md
sources:
  - id: ledger
    resource: ../references/article-source.md
  - id: runtime
    resource: https://docs.nvidia.com/openshell/latest/about/architecture.html
  - id: overview
    resource: https://docs.nvidia.com/openshell/latest/about/overview.html
generated: {by: "process:okf-wiki-author", at: "2026-10-27"}
status: draft
stale_after: 2026-12-31
---

# 软件执行边界

Supervisor 与 Sandbox 位于边界两侧。Sandbox 同不可信 Agent 一起运行，只观察和转发请求；Supervisor 位于可信侧，判断访问是否获准，再打开真实连接。Compute runtime 先建立隔离边界，Supervisor 确认后才启动 Agent（F-016～F-020）。[^runtime]

## 一次网络访问

下列顺序根据官方架构归纳，未在本机重放（F-017～F-021）：

1. Agent 发起 TCP 连接或 DNS 请求。
2. Sandbox 暂挂网络操作，并识别调用程序。
3. 请求经认证 Sandbox Protocol 送至 Supervisor。
4. Supervisor 评估策略，仅在获准位置加入提供商凭证。
5. Supervisor 打开连接并转发流量；外围 fence 拒绝 Agent 的其他直连。

拒绝默认出口很关键：如果 Agent 仍能直接连公网、内部地址、DNS 或 Gateway，就有机会绕开中介。策略引擎本身不能弥补一条未治理的连接路径。

当前 Linux backend 使用非 root 身份且无 capabilities；Landlock 控制文件访问，seccomp user notification 暂挂网络操作（F-019）。这里的“当前”绑定阅读时点，不能推广为所有操作系统、所有驱动的相同内核实现。

## 驱动实现

| 驱动 | Supervisor 放置 | 通道 | 直接出口封锁 |
|---|---|---|---|
| Docker / Podman | 独立容器 | 驱动持有卷上的认证 Unix socket | Workload 关闭网络 |
| Kubernetes | 独立 pod | 私有 service 与 mTLS | NetworkPolicy 只允许 Supervisor |
| VM | 宿主进程 | 认证 vsock | Guest 无网络设备 |

这些是官方驱动边界契约（F-022～F-024）。运行环境可以不同，但授权职责仍属于 Supervisor。驱动能力与 readiness 的差异必须在具体部署版本中核对。

## 策略的生效时间

| 对象 | 官方说明 | 运维含义 |
|---|---|---|
| 文件系统、进程策略 | 创建时锁定 | 更新需求可能需要重建，而非修改文件后等待 |
| 网络策略 | 可热更新 | 需读取执行面反馈并核对新请求 |
| 提供商凭证 | 可附加、轮转、撤销 | 更新环境变量需要新进程 |

依据 F-030、F-039。声明式 YAML 表示“希望系统做到什么”；实际应用、授权结果和审计事件才表示“系统现在做到什么”。[^overview]

Policy prover 检查 Agent 提议的网络规则，也提供 `openshell-prover` 用于 CI 边界核对。新增凭证可达域、HTTP 方法、云 metadata 访问等发现会阻断自动批准（F-025、F-026）。这是特定策略性质的证明，不是对模型输出、内核、业务动作或整个系统安全的总证明。

## 身份与断连

JWT（JSON Web Token）在这里是 Gateway 签发的认证令牌，不是用户登录凭证。Gateway JWT 用于 Supervisor→Gateway 的管理调用；Sandbox JWT 用于 Supervisor→Sandbox 的调用。`generation` 指同一个 sandbox 的一次运行代际；重启 sandbox 开始新代际，换发 token 与 TLS 证书，旧凭证失效（F-027）。Agent 不直接连接 Supervisor，由 Sandbox 转发；Sandbox 不持有签名密钥、Gateway JWT 或提供商凭证（F-021、F-028）。

Supervisor 在到期前共同续期两个 token，删除 sandbox 后不能续期。共享部署（如 Kubernetes）应设置 `gateway_jwt.ttl_secs`；未设置时 token 可持续整个 generation（F-061）。因此“重启换证”不能代替有效期治理，验收还需覆盖到期拒绝、正常续期和删除后的拒绝。

认证 Sandbox 通道不意味着所有连接默认都具有同样配置：官方架构对 Supervisor→Gateway 的 TLS 描述带有 Gateway 已启用 TLS 的条件，企业部署应核对实际启用状态。[^runtime]

断连时 Sandbox 冻结 Agent，只有原 Supervisor 进程可重连恢复（F-029）。企业验收应测断连、旧凭证、错误 sandbox 身份和直连绕行；此处列出的是待验证条件，没有声称已经执行。

[^runtime]: [OpenShell Architecture](https://docs.nvidia.com/openshell/latest/about/architecture.html)
[^overview]: [OpenShell Overview](https://docs.nvidia.com/openshell/latest/about/overview.html)
