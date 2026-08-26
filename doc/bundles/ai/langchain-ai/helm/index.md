---
type: bundle
title: Helm Chart 部署配置
okf_version: "0.2"
scope: langchain-ai
name: helm
version: "0.1.0"
source: https://github.com/langchain-ai/helm
description: LangChain-AI 官方 Kubernetes Helm Chart 集合——LangGraph Cloud、LangGraph Dataplane（Operator+CRD）、LangSmith、LangSmith Auth Proxy（Envoy）、LangSmith Observability（已废弃）五个独立 Chart 的部署结构、values 配置与 K8s 资源映射
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
verified: grep-verified
status: stable
stale_after: '2027-08-23'
tags:
- helm
- kubernetes
- langchain
- deployment
- langgraph
- langsmith
---

# Helm Chart 部署配置

本知识包是 [langchain-ai/helm](https://github.com/langchain-ai/helm)（Apache-2.0 许可证）的系统化中文参考文档。该仓库包含 LangChain-AI 官方维护的 5 个独立 Helm Chart，用于在 Kubernetes 上部署 LangGraph Cloud、LangSmith 可观测性平台及相关基础设施。所有内容均溯源至仓库源码（`external/libs/ai/langchain-ai/helm/`），遵循 [OKF v0.2 规范](../../../meta/okf-spec/index.md) 的 R→I→E 三阶段工作流生成。

## Chart 概览

| Chart | 版本 | appVersion | 定位 |
|-------|------|------------|------|
| [langgraph-cloud](/ai/langchain-ai/helm/references/chart-structure.md#chart-1langgraph-cloud) | 0.3.2 | 0.2.3 | LangGraph Cloud 全栈（API Server + Queue + PostgreSQL + Redis + MongoDB） |
| [langgraph-dataplane](/ai/langchain-ai/helm/references/chart-structure.md#chart-2langgraph-dataplane) | 0.2.22 | 0.16.36 | LangGraph 数据平面（Listener + Operator + CRD + Redis） |
| [langsmith](/ai/langchain-ai/helm/references/chart-structure.md#chart-3langsmith) | 0.17.0-rc.12 | 0.17.12rc1 | LangSmith 全栈（Backend + Frontend + ClickHouse + PG + Redis + Agent Features + Sandbox） |
| [langsmith-auth-proxy](/ai/langchain-ai/helm/references/chart-structure.md#chart-4langsmith-auth-proxy) | 0.0.11 | 1.37.0 | Envoy 认证代理（JWT 验证 + ext_authz + ext_proc） |
| [langsmith-observability](/ai/langchain-ai/helm/references/chart-structure.md#chart-5langsmith-observability已废弃) | 0.2.0 | 0.2.0 | 可观测性栈（**已废弃**，Prometheus/Grafana/Loki/Tempo） |

## 信源登记簿（references/）

* [Helm Chart 结构索引](/ai/langchain-ai/helm/references/chart-structure.md) — 仓库顶层结构、5 个 Chart 版本矩阵、镜像清单、模板文件映射、核心 values 配置段、探针模式、CI/CD 工具链、跨 Chart 共性模式（双模式有状态服务、三入口互斥、命名模板规范）。

## 事实与洞察（spec/）

* [事实清单](/ai/langchain-ai/helm/spec/facts.md) — 85 条源码事实（F-001~F-085），覆盖仓库元数据、Chart 版本、模板结构、values 配置、CI/CD、命名约定、探针模式。
* [架构洞察](/ai/langchain-ai/helm/spec/insights.md) — 4 个架构洞察：五 Chart 分层矩阵、内置/外部双模式、三入口互斥设计、文档即代码流水线。

## 关键设计模式

### 1. 有状态服务双模式

PostgreSQL、Redis、MongoDB 均支持 `external.enabled` 切换：内置模式创建 StatefulSet/Deployment，外部模式通过 `connectionUrl` 或 `existingSecretName` 连接托管服务。内置资源明确标注面向开发/CI，生产环境建议使用托管服务。

### 2. 三种入口互斥

`ingress`（传统 Ingress）、`gateway`（Gateway API HTTPRoute）、`istioGateway`（Istio VirtualService）三选一，模板层强制互斥校验。Gateway API 和 Istio 模式推荐用于生产和多 release 部署。

### 3. 统一弹性配置

所有无状态组件支持 HPA + 可选 KEDA ScaledObject、PDB、ServiceAccount 注解（IRSA/Workload Identity）、优先级类名、节点选择器/容忍度/亲和性。

## 信任与生命周期说明

* **status 判定依据**：全部内容文档（1 篇信源登记 + 1 篇事实清单 + 1 篇洞察）均 `status: stable`。内容基于对 langchain-ai/helm 仓库（5 个 Chart 的 Chart.yaml、values.yaml、templates/、ci/、tests/、hack/、.github/workflows/）的逐文件阅读与事实提取（85 条事实 F-001~F-085），经 R→I→E 三阶段流程生成。
* **stale_after 解释**：统一设置为 `2027-08-23`。Helm Chart 的核心结构（多 Chart 组织、values 双模式、三入口抽象）自仓库建立以来设计稳定；该日期作为针对未来大版本变更的保守重新评估节点。
* **核验链路**：`generated.at` 记录生成时刻，事实零推测，所有版本号、镜像 tag、文件路径均经源码验证。

本知识包为参考型 bundle，不包含 concepts/ 和 examples/ 目录。共收录 1 个信源登记文档，另含 spec/ 子目录（facts.md + insights.md）、references/index.md 与根 index.md、log.md。

```{toctree}
:hidden:
:maxdepth: 7

references/index
spec/facts
spec/insights
log
```
