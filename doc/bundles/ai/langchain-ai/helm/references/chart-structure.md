---
type: reference
title: "Helm Chart 结构索引"
description: "langchain-ai/helm 仓库 5 个 Chart 的目录结构、版本、组件、镜像与模板文件映射"
sources:
  - path: "external/libs/ai/langchain-ai/helm/"
    facts: [F-001, F-002, F-003, F-004, F-005, F-006, F-007, F-008, F-009, F-010, F-011, F-012, F-013, F-014, F-015, F-016, F-017, F-018, F-019, F-020, F-021, F-022, F-023, F-024, F-025, F-026, F-027, F-028, F-029, F-030, F-031, F-032, F-033, F-034, F-035, F-036, F-037, F-038, F-039, F-040, F-041, F-042, F-043, F-044, F-045, F-046, F-047, F-048, F-049, F-050, F-051, F-052, F-053, F-054, F-055, F-056, F-057, F-058, F-059, F-060, F-061, F-062, F-063, F-064, F-065, F-066, F-067, F-068, F-069, F-070, F-071, F-072, F-073, F-074, F-075, F-076, F-077, F-078, F-079, F-080, F-081, F-082, F-083, F-084, F-085]
---

# Helm Chart 结构索引

## 信源概述

| 信源 | 类型 | 职责 |
|------|------|------|
| `external/libs/ai/langchain-ai/helm/` | Helm Chart 仓库 | LangChain-AI 官方 Kubernetes 部署 Chart 集合 |

仓库根路径：`d:/spaces/SpecWeave/external/libs/ai/langchain-ai/helm/`
Helm 仓库地址：`https://langchain-ai.github.io/helm/`
许可证：Apache License 2.0

## 仓库顶层结构

```
helm/
├── charts/                          # 5 个独立 Chart
│   ├── langgraph-cloud/             # LangGraph Cloud 全栈部署
│   ├── langgraph-dataplane/         # LangGraph 数据平面（Operator + CRD）
│   ├── langsmith/                   # LangSmith 全栈部署
│   ├── langsmith-auth-proxy/        # LangSmith Envoy 认证代理
│   └── langsmith-observability/     # 可观测性栈（已废弃）
├── hack/                            # 本地开发脚本
│   ├── ensure-safe-kube-context.sh
│   ├── kind-create.sh
│   ├── kind-delete.sh
│   ├── install-langgraph-cloud.sh
│   ├── smoke-langgraph-cloud.sh
│   ├── port-forward-langgraph-cloud.sh
│   ├── dump-k8s-debug.sh
│   ├── lib.sh
│   └── fixtures/mongo.yaml
├── .github/workflows/
│   ├── helm_checks.yaml             # CI: lint + unittest + kind install
│   └── release_charts.yaml          # CD: chart-releaser 发布
├── Makefile                         # 本地开发 target
├── README.md
├── SECURITY.md
└── LICENSE
```

## Chart 版本矩阵

| Chart | Chart 版本 | appVersion | 类型 | 维护者 | 状态 |
|-------|-----------|------------|------|--------|------|
| langgraph-cloud | 0.3.2 | 0.2.3 | application | Ankush | 活跃 |
| langgraph-dataplane | 0.2.22 | 0.16.36 | application | Ankush | 活跃 |
| langsmith | 0.17.0-rc.12 | 0.17.12rc1 | application | Ankush | RC |
| langsmith-auth-proxy | 0.0.11 | 1.37.0 | application | Brian | 活跃 |
| langsmith-observability | 0.2.0 | 0.2.0 | application | Romain | **deprecated** |

## Chart 1：langgraph-cloud

### 定位

部署 LangGraph Cloud 应用及其全部依赖服务（PostgreSQL + Redis + MongoDB + Queue），面向自托管 LangGraph Platform。

### 镜像清单

| 配置键 | 镜像 | 默认 Tag | 用途 |
|--------|------|----------|------|
| `images.apiServerImage` | docker.io/langchain/langgraph-api | 3.11-28c1407 | API Server |
| `images.postgresImage` | pgvector/pgvector | pg16 | 向量数据库（内置） |
| `images.redisImage` | docker.io/redis | 6 | 缓存/队列（内置） |
| `images.mongoImage` | mongo | 7 | Checkpointer（内置，默认关闭） |

### 模板文件映射

```
charts/langgraph-cloud/templates/
├── _helpers.tpl                    # 命名/标签/Secret 模板
├── NOTES.txt                       # 安装后提示
├── secrets.yaml                    # 全局 Secret
├── ingress.yaml                    # 传统 Ingress
├── http_route.yaml                 # Gateway API HTTPRoute
├── virtual_service.yaml            # Istio VirtualService
├── api-server/
│   ├── deployment.yaml
│   ├── hpa.yaml
│   ├── pdb.yaml
│   ├── scaled-object.yaml          # KEDA ScaledObject
│   ├── service.yaml
│   └── service-account.yaml
├── queue/
│   ├── deployment.yaml
│   ├── hpa.yaml
│   ├── pdb.yaml
│   ├── scaled-object.yaml
│   └── service-account.yaml
├── postgres/
│   ├── stateful-set.yaml
│   ├── service.yaml
│   ├── pdb.yaml
│   ├── secrets.yaml
│   └── service-account.yaml
├── redis/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── pdb.yaml
│   ├── secrets.yaml
│   └── service-account.yaml
└── mongo/
    ├── stateful-set.yaml
    ├── service.yaml
    └── secrets.yaml
```

### 核心 values 段

| 段 | 关键配置 | 默认值 |
|----|---------|--------|
| 全局 | `namespace` / `clusterDomain` / `commonDnsConfig.ndots` | "" / "cluster.local" / "4" |
| `config` | `langGraphCloudLicenseKey` / `apiKey` / `numberOfJobsPerWorker` / `auth.enabled` | "" / "" / 10 / false |
| `ingress` | `enabled` / `hostname` / `ingressClassName` / `tls` | false |
| `gateway` | `enabled` / `name` / `namespace` / `hostname` / `basePath` | false |
| `istioGateway` | `enabled` / `name` / `namespace` / `hostname` / `basePath` | false |
| `apiServer` | `containerPort` / `deployment.replicaCount` / `service.type` | 8000 / 1 / LoadBalancer |
| `queue` | `enabled` / `containerPort` | false / 8000 |
| `postgres` | `external.enabled` / `statefulSet.persistence.size` | false / 8Gi |
| `redis` | `external.enabled` | false |
| `mongo` | `enabled` / `external.enabled` / `statefulSet.persistence.size` | false / false / 8Gi |

### 探针模式

- apiServer：`exec python /api/healthcheck.py`（startup/readiness/liveness 相同）
- queue：`HTTP GET /ok`（port 8000）
- redis：`exec redis-cli ping`
- postgres：无显式探针

### 测试

- `tests/`：mongo_test、pdb_test、priority_class_name_test、statefulset_update_strategy_test、validate_test
- `ci/`：7 个场景 values（dev-kind、lightweight、readonly、mongo-checkpointer 等）

## Chart 2：langgraph-dataplane

### 定位

部署 LangGraph 数据平面，包含 Listener（连接 LangSmith Host Backend）和 Operator（管理 LangGraph Platform Deployment CRD），是 LangGraph Platform 的 Kubernetes 控制平面。

### 镜像清单

| 配置键 | 镜像 | 默认 Tag | 用途 |
|--------|------|----------|------|
| `images.listenerImage` | docker.io/langchain/langsmith-backend | 0.16.36 | Listener 服务 |
| `images.operatorImage` | docker.io/langchain/langgraph-operator | 0.1.36 | LangGraph Operator |
| `images.redisImage` | docker.io/redis | 7 | 内置 Redis（StatefulSet） |

### 模板文件映射

```
charts/langgraph-dataplane/templates/
├── _helpers.tpl
├── secrets.yaml
├── ingress.yaml
├── listener/
│   ├── deployment.yaml
│   ├── hpa.yaml
│   ├── pdb.yaml
│   ├── rbac.yaml
│   └── service-account.yaml
├── operator/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── pdb.yaml
│   ├── rbac.yaml
│   ├── service-account.yaml
│   ├── config-map.yaml              # Operator 内嵌资源模板
│   └── crds.yaml                    # LangGraph Platform CRD
└── redis/
    ├── stateful-set.yaml
    ├── service.yaml
    ├── pdb.yaml
    ├── secrets.yaml
    └── service-account.yaml
```

### 核心 values 段

| 段 | 关键配置 | 默认值 |
|----|---------|--------|
| `config` | `hostBackendUrl` / `smithBackendUrl` / `langsmithWorkspaceId` / `hostQueue` | https://api.host.langchain.com / https://api.smith.langchain.com / "" / "host" |
| `listener` | `containerPort` / `deployment.replicas` / 命令 | 8080 / 1 / host_backend_entrypoint.sh + listener_entrypoint.sh |
| `operator` | `enabled` / `createCRDs` / `kedaEnabled` / `watchNamespaces` | true / true / true / "" |
| `operator.templates` | `deployment` / `service` / `db` / `redis` | 内嵌 YAML 模板（${name} 等占位符） |
| `redis` | `external.enabled` / `statefulSet.persistence.size` | false / 8Gi |

### Operator 内嵌模板

`operator.templates` 字段包含 4 个内嵌 YAML 模板，Operator 用它们动态创建用户 Deployment 的资源：

| 模板 |  kind | 镜像 | 关键占位符 |
|------|-------|------|-----------|
| `deployment` | Deployment | `${image}` | `${name}` / `${namespace}` / `${replicas}` |
| `service` | Service | — | `${name}` / `${namespace}` |
| `db` | StatefulSet | pgvector/pgvector:pg15 | `${service_name}` / `${secret_name}` / `${storage_gi}` 等 |
| `redis` | Deployment | redis:6 | `${service_name}` |

### 探针模式

- listener：`HTTP GET /health`（startup/readiness），`exec saq ... --check`（liveness，60s 周期）
- redis：`exec redis-cli ping`

## Chart 3：langsmith

### 定位

部署 LangSmith 可观测性平台全栈，包含 Backend、Frontend、ClickHouse、PostgreSQL、Redis、ACE Backend、Agent Gateway、Agent Features（Fleet/Insights/Polly）、Sandbox 等组件。

### 镜像清单（部分）

| 配置键 | 镜像 | 默认 Tag |
|--------|------|----------|
| `images.backendImage` | docker.io/langchain/langsmith-backend | 0.17.12rc1 |
| `images.frontendImage` | docker.io/langchain/langsmith-frontend | 0.17.12rc1 |
| `images.aceBackendImage` | docker.io/langchain/langsmith-ace-backend | 0.17.12rc1 |
| `images.engineInsightsAgentImage` | docker.io/langchain/langsmith-insights-engine | 0.17.12rc1 |
| `images.operatorImage` | docker.io/langchain/langgraph-operator | 0.1.47 |
| `images.postgresImage` | docker.io/postgres | 14.7 |
| `images.redisImage` | docker.io/redis | 7 |
| `images.clickhouseImage` | docker.io/clickhouse/clickhouse-server | 25.12 |
| `images.agentBuilderImage` | docker.io/langchain/agent-builder-deep-agent | 0.17.12rc1 |
| `images.pollyAgentImage` | docker.io/langchain/langsmith-polly | 0.17.12rc1 |
| `images.smithdbImage` | docker.io/langchain/smithdb | 0.17.12rc1 |
| `images.presidioAnalyzerImage` | mcr.microsoft.com/presidio-analyzer | 2.2.354（可选） |
| `images.sandboxHostImage` | docker.io/langchain/sandbox-host | ""（可选） |

### 模板目录结构

```
charts/langsmith/templates/
├── _helpers.tpl
├── NOTES.txt
├── ace-backend/           # deployment/hpa/pdb/scaled-object/service/service-account
├── agent-gateway/         # deployment/hpa/service/service-account
├── backend/               # deployment/hpa/pdb/scaled-object/service/service-account
│                          # + auth-bootstrap/backfill-check/clickhouse-migrations/
│                          #   postgres-migrations/e2e-test
├── clickhouse/            # config-map
└── agent-features/
    ├── fleet/
    │   ├── api-server/    # deployment/hpa/pdb/scaled-object/service/serviceaccount
    │   ├── postgres/      # statefulset/pdb/service/secrets/serviceaccount
    │   ├── queue/         # deployment/hpa/pdb/scaled-object/serviceaccount
    │   ├── redis/         # statefulset/pdb/service/secrets/serviceaccount
    │   ├── tool-server/   # deployment/hpa/pdb/service/service-account
    │   └── trigger-server/ # deployment/service/service-account
    ├── insights/
    │   ├── api-server/    # deployment/hpa/pdb/scaled-object/service/serviceaccount
    │   ├── postgres/      # statefulset/pdb/service/secrets/serviceaccount
    │   ├── queue/         # deployment/hpa/pdb/scaled-object/serviceaccount
    │   └── redis/         # statefulset/pdb/service/secrets/serviceaccount
    └── polly/
        ├── api-server/    # deployment/hpa/pdb/scaled-object/service/serviceaccount
        ├── postgres/      # statefulset/pdb/service/secrets/serviceaccount
        ├── queue/         # deployment/hpa/pdb/scaled-object/serviceaccount
        └── redis/         # statefulset/pdb/service/secrets/serviceaccount
```

### 特色配置段

| 段 | 说明 |
|----|------|
| `preInstallManifests` | pre-install/pre-upgrade hook 清单（如 ExternalSecret） |
| `sandboxes` | 沙箱配置（JuiceFS 存储、sandbox-host 特权容器、配额、CA） |
| `fleet` | Fleet 独立部署模式（OAuth 多提供商、encryptionKey、apiServer/queue） |
| `clickhouse` | ClickHouse 配置（ConfigMap） |
| `ingress` / `gateway` / `istioGateway` | 三种互斥入口 |

### 辅助资源

- `examples/`：15 个示例 values（basic、autoscaling、basic_auth、blob_storage、ingress、lightweight、medium_size、mixed_oauth、mtls、read_only、redis_cluster、smithdb_alloydb_auth_proxy、tracing）
- `docs/`：12 个运维文档（删除组织/工作区/Trace、OAuth 迁移、ClickHouse/PostgreSQL 支持查询、升级指南）
- `scripts/`：运维脚本（backfill、删除、镜像镜像、K8s 调试信息、支持查询）

## Chart 4：langsmith-auth-proxy

### 定位

基于 Envoy 的独立认证代理，验证 LangSmith 签名的 JWT，可选调用外部授权服务注入 LLM 提供商认证头，面向 LLM API 网关场景。

### 镜像

| 配置键 | 镜像 | Tag |
|--------|------|-----|
| `images.authProxyImage` | docker.io/envoyproxy/envoy | v1.37-latest |

### 模板文件映射

```
charts/langsmith-auth-proxy/templates/
├── _helpers.tpl
├── ingress.yaml
├── http_route.yaml
└── auth-proxy/
    ├── config-map.yaml            # Envoy 配置
    ├── deployment.yaml
    ├── hpa.yaml
    ├── pdb.yaml
    ├── service.yaml
    └── service-account.yaml
```

### 核心配置段

| 段 | 关键配置 | 说明 |
|----|---------|------|
| `authProxy.upstream` | URL | LLM 提供商/网关地址 |
| `authProxy.jwtIssuer` | "langsmith" | JWT issuer 声明 |
| `authProxy.jwtAudiences` | [] | **必填** JWT audience |
| `authProxy.jwksJson` | "" | 内联 JWKS（与 jwksUri 二选一） |
| `authProxy.jwksUri` | "" | 远程 JWKS 端点（优先于 jwksJson） |
| `authProxy.streamIdleTimeout` | "300s" | SSE 流式空闲超时 |
| `authProxy.httpProxy` | enabled/host/port/noProxy | HTTP CONNECT 代理 |
| `authProxy.extAuthz` | serviceUrl/timeout/headers | 外部授权（ext_authz） |
| `authProxy.transformer` | serviceUrl/processingMode | ext_proc 请求/响应变换 |
| `authProxy.rollout` | enabled | ArgoCD Rollouts |

### E2E 测试场景

| 场景 | 目录 | 测试内容 |
|------|------|---------|
| basic | `e2e/basic/` | 基础 JWT 验证 + ext-authz mock |
| http-proxy | `e2e/http-proxy/` | HTTP CONNECT 代理 + JWKS 服务 |
| oauth | `e2e/oauth/` | OAuth 外部授权 |
| transformer | `e2e/transformer/` | ext_proc gRPC 变换（含 Go 示例实现） |

## Chart 5：langsmith-observability（已废弃）

### 定位

~~部署 LangSmith 可观测性栈（Prometheus Exporters + Grafana + Loki + Tempo + Mimir + OpenTelemetry）~~。Chart.yaml 标记 `deprecated: true`，建议用户使用自己的可观测性栈。

### 依赖 Chart

| 依赖 | 版本 | 仓库 | Condition |
|------|------|------|-----------|
| prometheus-postgres-exporter | 6.10.2 | prometheus-community | postgres-exporter.enabled |
| prometheus-redis-exporter | 6.11.0 | prometheus-community | redis-exporter.enabled |
| prometheus-nginx-exporter | 1.6.0 | prometheus-community | nginx-exporter.enabled |
| kube-state-metrics | 5.37.0 | prometheus-community | kube-state-metrics.enabled |
| grafana | 9.2.6 | grafana | grafana.enabled |
| loki | 6.30.1 | grafana | loki.enabled |
| tempo | 1.23.1 | grafana | tempo.enabled |

### 模板

```
charts/langsmith-observability/templates/
├── _helpers.tpl
├── grafana/grafana-dashboards-configmap.yaml
├── mimir/{config-map,service,stateful-set}.yaml
└── otel/{gateway,logs-sidecar,rbac-gateway,rbac-sidecar}.yaml
```

### Dashboards

`dashboards/` 目录含 6 个预配置 Grafana Dashboard：clickhouse、kube-state-metrics、langsmith-services、nginx、postgres、redis。

## CI/CD 工具链

### helm_checks.yaml（CI）

| 步骤 | 工具 | 版本 |
|------|------|------|
| Helm | azure/setup-helm | v3.12.1 |
| Chart Testing | helm/chart-testing-action | v2.6.0 |
| Helm Unittest | helm-unittest plugin | 0.7.0 |
| Kind 集群 | helm/kind-action | v0.25.0（kind v0.25.0） |
| Python | actions/setup-python | 3.9 |

CI 矩阵覆盖 3 个 Chart：langgraph-cloud、langsmith、langsmith-auth-proxy。
流程：ct lint（版本检查）→ ct lint（Chart 检查）→ helm unittest → kind 创建 → 预拉镜像 → ct install（含资源缩减 set 参数）。

### release_charts.yaml（CD）

推送到 `main` 或 `*-stable` 分支时触发，使用 helm/chart-releaser-action@v1.5.0 发布到 GitHub Pages，并触发自托管 changelog bot。

### Makefile 本地开发

| Target | 脚本 | 功能 |
|--------|------|------|
| cloud-dev-check | ensure-safe-kube-context.sh | 校验 kube context 是 kind 集群 |
| cloud-dev-template | helm template | 渲染 dev values |
| cloud-dev-up | kind-create.sh + install-langgraph-cloud.sh | 创建 kind 集群并安装 |
| cloud-dev-smoke | smoke-langgraph-cloud.sh | 端口转发 + 冒烟测试 |
| cloud-dev-connect | port-forward-langgraph-cloud.sh | 端口转发到 8000 |
| cloud-dev-logs | dump-k8s-debug.sh | 导出 K8s 诊断信息 |
| cloud-dev-status | kubectl get | 查看 namespace 资源 |
| cloud-dev-down | kind-delete.sh | 删除 kind 集群 |

## 跨 Chart 共性模式

### 命名模板前缀

| Chart | 模板前缀 |
|-------|---------|
| langgraph-cloud | `langGraphCloud.*` |
| langgraph-dataplane | `langgraphDataplane.*`（推断） |
| langsmith | `langsmith.*`（推断） |
| langsmith-auth-proxy | `authProxy.*`（推断） |

### 通用 values 字段

所有 Chart 共享以下全局配置：

- `nameOverride` / `fullnameOverride` / `namespace`
- `commonAnnotations` / `commonLabels`
- `commonDnsConfig.options`（默认 `ndots: "4"`，减少 DNS 查询放大）
- `clusterDomain`（默认 `"cluster.local"`）
- `images.registry` / `images.imagePullSecrets`

### K8s 标签规范

所有资源统一使用 Kubernetes 推荐标签：
- `app.kubernetes.io/name`
- `app.kubernetes.io/instance`
- `app.kubernetes.io/version`
- `app.kubernetes.io/managed-by`
- `helm.sh/chart`

### 有状态服务双模式

所有内置有状态服务（PostgreSQL/Redis/MongoDB）均支持：

```yaml
<component>:
  external:
    enabled: false          # true 时连接外部服务
    connectionUrl: ""       # 或 host/port/user/password
    existingSecretName: ""  # 或引用已有 Secret
  statefulSet/deployment:   # 内置资源配置
    ...
  persistence:
    enabled: true
    size: 8Gi
```

### 弹性配置

所有无状态组件统一支持：
- `deployment.replicaCount`
- `autoscaling.enabled` + HPA（CPU/内存目标利用率）
- `autoscaling.keda.enabled` + KEDA ScaledObject
- `pdb.enabled` + minAvailable/maxUnavailable
- `serviceAccount.create` + annotations（IRSA/Workload Identity）
