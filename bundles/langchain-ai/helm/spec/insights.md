---
type: spec
title: Helm Chart 部署架构洞察
description: langchain-ai/helm 仓库架构洞察记录
tags:
- helm
- kubernetes
- langchain
- spec
- insights
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
verified: grep-verified
status: stable
stale_after: '2027-08-23'
sources:
- id: helm-chart-structure
  resource: /langchain-ai/helm/references/chart-structure.md
  title: Helm Chart 结构索引
---

# Helm Chart 部署架构洞察

> I阶段产出。基于 85 条源码事实（F-001~F-085）提炼。

## 核心洞察

### 洞察1：五 Chart 分层矩阵——按产品边界与数据平面解耦

- **陈述**：仓库并非单一巨型 Chart，而是按产品边界（LangGraph Cloud / LangSmith / Auth Proxy / Observability / Dataplane）拆分为 5 个独立 Chart，每个 Chart 有独立的版本号、appVersion、维护者和发布周期。其中 `langgraph-dataplane` 是唯一部署 LangGraph Operator + CRD 的 Chart，构成了控制平面；`langgraph-cloud` 和 `langsmith` 是各自包含完整有状态依赖（PostgreSQL/Redis/MongoDB/ClickHouse）的应用平面；`langsmith-auth-proxy` 是独立的 Envoy 边缘代理；`langsmith-observability` 已废弃。
- **证据**：F-005（5个Chart）、F-006~F-010（各自独立版本）、F-031~F-034（dataplane 含 operator/crds.yaml）、F-014~F-019（langgraph-cloud 完整栈）、F-042~F-045（langsmith 完整栈）、F-010（observability deprecated）、F-055~F-058（auth-proxy 独立）
- **反常识**：直觉上可能认为 Helm 仓库会用一个"伞形 Chart"（umbrella chart）通过 requirements.yaml 组装所有组件，但本仓库没有这样做——5 个 Chart 之间没有任何 Chart.yaml 级别的依赖声明（唯一有 dependencies 的是已废弃的 observability，依赖的是第三方 Prometheus/Grafana 栈）。这意味着用户需要独立安装和升级每个 Chart，版本兼容性通过文档而非 Helm 依赖机制保证。
- **行动**：参考文档需要清晰呈现 5 个 Chart 的定位矩阵（哪个是控制平面、哪个是应用平面、哪个是边缘代理），帮助用户理解安装顺序和依赖关系——dataplane（Operator+CRD）应先于 langgraph-cloud 安装，auth-proxy 可独立于 langsmith 部署。

### 洞察2："内置依赖 vs 外部服务"双模式贯穿所有有状态组件

- **陈述**：所有有状态中间件（PostgreSQL、Redis、MongoDB）在 values.yaml 中都实现了统一的双模式切换：`external.enabled: false` 时 Chart 自行创建 StatefulSet/Deployment + Service + Secret；`external.enabled: true` 时通过 `connectionUrl`/`host`/`port` 或 `existingSecretName` 连接外部托管服务，同时禁用内置资源的创建。
- **证据**：F-028（postgres external 模式）、F-029（redis external 模式）、F-030（mongo external 模式）、F-041（dataplane redis external 模式）、F-050（langsmith 镜像注释明确建议生产环境使用托管 PostgreSQL/Redis）
- **反常识**：许多 Helm Chart 将"内置数据库"作为默认且唯一选项，或把外部连接配置散落在各处。本仓库的设计是：内置服务明确标注面向"本地开发/CI/快速入门"（如 F-030 描述 MongoDB 为 "bundled single-node MongoDB replica set intended for local development, CI, and quickstarts"），而生产建议直接写入 values 注释中（F-050 引用官方文档链接）。这种"开箱即用但明确不推荐生产使用内置依赖"的立场比大多数 Chart 更鲜明。
- **行动**：参考文档需要总结这个双模式配置范式，指出每个有状态组件的 external 配置字段和内置资源的资源规格（CPU/内存/PVC 大小），帮助运维人员快速决策。

### 洞察3：三种入口互斥模式——Ingress / Gateway API / Istio 三选一

- **陈述**：langgraph-cloud、langgraph-dataplane、langsmith 三个面向用户流量的 Chart 都实现了完全一致的三种入口抽象：传统 `ingress`（Kubernetes Ingress 资源）、`gateway`（Gateway API HTTPRoute）、`istioGateway`（Istio VirtualService）。三者通过 values 中的 `enabled` 布尔值控制，且在模板层强制互斥（同一时间只能启用一个）。
- **证据**：F-025（langgraph-cloud 三种入口互斥）、F-047（langgraph-dataplane ingress/gateway/istioGateway 三段配置）、F-054（langsmith 同样三段）、F-025 中注释 "Only one of ingress, gateway, or istioGateway can be enabled at the same time"
- **反常识**：多数 Helm Chart 只支持一种入口方式（通常是 Ingress），或同时创建多种入口资源导致冲突。本仓库不仅三种都支持，还在 values 注释中明确警告 `basePath` 变更会破坏已有路由（F-025 中 "WARNING: Changing basePath after deployment will break existing routes"），说明团队经历过真实的生产事故。此外，Gateway API 和 Istio 模式被注释为"推荐生产使用/多 release 同集群部署时使用"（dataplane values.yaml L65、L75），体现了从 Ingress 向更现代入口 API 的迁移导向。
- **行动**：参考文档需要对比三种入口方式的适用场景、创建的资源类型差异、basePath 限制，帮助用户根据集群基础设施选择正确的入口模式。

### 洞察4：从 values 注释到 README.gotmpl 的"文档即代码"流水线

- **陈述**：每个 Chart 的 values.yaml 中大量使用 `# --` 前缀的注释（Helm docs 注释格式），配合 `README.md.gotmpl` 模板自动生成 `README.md`。这意味着 values 的每个配置项都有内联文档，README 不是手写的而是从 values 注释派生的。
- **证据**：F-080（4个Chart有 README.md.gotmpl）、F-022~F-030（values.yaml 中每个字段都有 `# --` 注释）、F-051~F-053（langsmith values 中长篇注释说明使用场景和警告）
- **反常识**：许多 Helm Chart 的 values.yaml 缺乏注释，README 中的配置表与实际 values 不同步。本仓库通过 helm-docs 工具链将 values 注释作为单一真相源（single source of truth），README 自动生成——这在 CI 中通过 ct lint 强制版本一致性（F-069/F-070），形成了"改 values 必须改注释 → 自动生成 README → CI 检查版本"的闭环。
- **行动**：参考文档应记录这套文档生成机制，对于需要自定义 values 的运维人员，直接阅读 values.yaml 中的 `# --` 注释比读 README 更准确。

## 知识地图

### 文档清单

**references/（1篇）**
1. `chart-structure.md` — Helm Chart 结构索引：5 个 Chart 的目录结构、版本、核心组件、镜像清单、模板文件、CI/CD 工具链。覆盖 F-001~F-085。

### 适用读者

- **平台工程师/SRE**：需要在 Kubernetes 上部署 LangGraph Cloud 或 LangSmith，了解 Chart 结构、values 配置、入口选择、有状态服务部署模式。
- **Helm Chart 开发者**：学习多 Chart 仓库的组织方式、values 双模式设计、文档即代码流水线、CI/CD 集成。
