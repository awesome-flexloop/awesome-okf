---
type: Concept
title: 部署层级与企业验收
description: CPU 到平台集群的放置取舍、隔离与控制分层、性能评测和设备回收
source: ../references/article-source.md
sources:
  - id: ledger
    resource: ../references/article-source.md
  - id: tiers
    resource: https://docs.nvidia.com/enterprise-reference-architectures/secure-agent-workspace-reference-design/latest/deployment-tiers.html
  - id: governance
    resource: https://docs.nvidia.com/enterprise-reference-architectures/secure-agent-workspace-reference-design/latest/security-and-governance-model.html
  - id: operations
    resource: https://docs.nvidia.com/enterprise-reference-architectures/secure-agent-workspace-reference-design/latest/operating-properties.html
generated: {by: "process:okf-wiki-author", at: "2026-10-27"}
status: draft
stale_after: 2026-12-31
---

# 部署与验收

参考设计把工作区隔离、治理控制和硬件放置分开。工作区需要独立 guest kernel，不表示每个用户需要独占物理服务器；共享系统仍可以为不同用户分配独立 VM（F-033、F-036、F-047）。[^tiers]

## 五种部署层级

| 官方层级 | 主要放置形态 | 教程建议的选择问题 |
|---|---|---|
| CPU VM | CPU 工作区、模型推理路由到独立服务 | 工具是否真的依赖本地 GPU |
| GPU VM / workstation | 工作区具有 GPU 能力 | 工具加速与本地推理是否争抢设备 |
| Deskside workstation | 桌边个人工作站 | 是否仍有企业身份、网络及生命周期治理 |
| Team shared system | 团队共享物理资源，各用户独立 VM | 用户边界与设备回收如何证明 |
| Platform fleet | 集中平台与多工作区编排 | 策略、镜像、审计和容量如何批量管理 |

层级名称与关键约束来自 F-046、F-047；选择问题属于作者建议。CPU VM 对 routed-inference coding 是合理起点，本地推理和 GPU 工具属于分别评估的需求（F-037）。

原稿列出的 RTX Spark、DGX Spark、DGX Station 是 NVIDIA 边缘扩展方案（F-004）。本教程没有逐机型硬件实测，也不将其型号列表转化为最低采购要求。

## 三张验收表

**上线前置门：** 先发布数据分类政策，再启用自主 Agent（F-062）。应明确哪些数据可读、哪些可进入工作区、哪些允许发送到模型服务；以下范围细化属于作者建议，应由企业数据与安全负责人确认。没有批准的数据范围时，不应仅凭隔离测试通过就放行。[^governance]

| 隔离项 | 证据目标 | 事实依据 |
|---|---|---|
| 跨用户边界 | 不共享 guest kernel，不泄漏其他工作区数据 | F-033、F-036 |
| 网络出口 | 直连被 fence 拒绝，获准请求经过可信授权路径 | F-020～F-024 |
| 失陷后控制 | 可信控制和管理权限仍在失陷域之外 | F-043、F-058 |

| 控制项 | 证据目标 | 事实依据 |
|---|---|---|
| 策略发布 | 发布、应用、实际授权结果分别可追踪 | F-039 |
| 策略证明 | 不确定/不支持的结果不当作成功 | F-025、F-042 |
| 模式选择 | audit-only 与 enforce 的结果分别记录 | F-042 |
| 业务批准 | 受保护分支合并、发送、发布、删除及共享状态变更必经人工批准；网络允许不替代批准 | F-063 |
| 撤销 | 网络隔离、进程终止、下游撤权分别确认；声明并实测传播上界，覆盖待批准动作、排队写入、子授权、缓存凭证及存活连接 | F-044、F-064 |
| 身份 | 旧 generation 凭证失效；共享部署设置有效期并验证续期、到期及删除后的拒绝 | F-027、F-061 |
| 运维准入 | 责任与响应分工明确；失效关闭、更新、回滚、恢复及重启/迁移后绑定通过验证 | F-065 |

| 放置项 | 证据目标 | 事实依据 |
|---|---|---|
| GPU 回收 | 重新分配前验证 VRAM 与设备残留清理 | F-045 |
| 存储回收 | 本地存储清理有真实证据，不能仅凭 VM 重建 | F-045 |
| 本地模型 | 单独核对模型数据访问与资源预算 | F-037 |

这些是依据文档生成的验收目标，不是已完成的测试用例结果。OpenShift Virtualization 参考实现可作为职责映射的继续阅读入口（F-048），不能代替对本机版本和真实网络路径的检查。[^governance]

## 性能和投入

采购论证不能直接用“2 倍”或“提升 20%”算收益。它们分别带关键工作负载、最高值和厂商自述限定，未取得本次独立复现（F-009、F-010、F-060）。

建议先固定任务集、并发、工具链、模型端点、硬件、策略模式和基线，再测任务完成质量、耗时、启动延迟、资源占用和撤销窗口。OPA 单次评估、硬件隔离与整个业务链的完成时延是不同指标（F-052、F-044）。该评测设计属于作者建议，未填入模拟数字。

官方部署层级要求成本遥测与预算门（F-066）。作者建议把采购折旧、模型调用、集成运维、人工复核和误阻断返工计入总成本，以真正节省的人工时间或可归因业务收益核对回报。试点前由业务负责人约定收益兑现周期、预算上限及停止投入条件；达不到质量、安全或经济性门槛时停止扩容，不用厂商最高倍数补足论证。

## 读者的起点

先画现有系统的职责表，标出终端、身份入口、VM、模型路由、企业 API 和凭证中介。再用上面的隔离、控制、放置三表列出现有证据和缺口。能定位缺口后，再进入具体平台的官方安装与版本文档；本包不提供未经实测的“一键部署”命令。

下面是作者设计的最小填写样例，不是真实部署记录：

| 对象 | 允许边界 | 证据 | 缺口与责任 |
|---|---|---|---|
| 代码仓库 | 只读检索，个人分支草稿；合并需人工批准 | 待填写批准记录与请求结果 | 仓库负责人确认受保护分支门 |
| 模型端点 | 仅允许经批准的数据分类外发 | 待填写分类政策及路由测试 | 数据负责人确认范围 |
| 工作区撤销 | 同时停止进程、网络及下游授权 | 待填写传播上界和在途动作结果 | 平台与业务方联合验证 |

第一轮完成判据是每个对象都有明确边界、责任人、证据或待验证缺口；“待填写”不能当通过。上线判据还须由责任方确认所有前置门及适用验收项通过。

[^tiers]: [Deployment Tiers](https://docs.nvidia.com/enterprise-reference-architectures/secure-agent-workspace-reference-design/latest/deployment-tiers.html)
[^governance]: [Security and Governance Model](https://docs.nvidia.com/enterprise-reference-architectures/secure-agent-workspace-reference-design/latest/security-and-governance-model.html)
